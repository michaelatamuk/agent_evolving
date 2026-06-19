from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .recommender_similarities_computer import Embedder, Backend
from .reccmmender_scores_matrix import norm_columns, metric_columns


class SkillRecommender:
    """Fit once on the matrix, then call recommend() for any query.

    Scoring is a weighted fusion of up to five components, each in [0, 1].
    Components are enabled incrementally as their dependencies are provided:

    Phase 1 — Bayesian fusion (ts_state_path):
        collaborative_score  (existing similarity×matrix weighted avg)
        bayesian_confidence  α/(α+β) — exploitation signal
        uncertainty_sample   Beta(α,β) draw — exploration signal

    Phase 2 — Freshness (freshness_lambda > 0, requires ts_state_path):
        freshness            exp(−λ × days_since_last_success)

    Phase 3 — Adaptive context (context_store / contextual_matrix):
        context_match        cosine(query_vec, per-skill running embedding)
        online_collaborative similarity-weighted online reward from ContextualMatrix

    Active components are normalised so their weights always sum to 1.0 —
    disabling a component does not shrink the score range.
    """

    def __init__(
        self,
        matrix_df: pd.DataFrame,
        embedder_method: Backend = "tfidf",
        # ── Phase 1: Bayesian arm state ──────────────────────────────────────
        ts_state_path: Optional[Path] = None,
        w_collaborative: float = 0.35,
        w_bayesian_conf: float = 0.20,
        w_uncertainty: float = 0.15,
        # ── Phase 2: Freshness ───────────────────────────────────────────────
        freshness_lambda: float = 0.0,   # 0.0 = disabled; try 0.05 to enable
        w_freshness: float = 0.10,
        # ── Phase 3: Adaptive context ────────────────────────────────────────
        context_store=None,       # SkillContextStore | None
        contextual_matrix=None,   # ContextualMatrix  | None
        w_context_match: float = 0.15,
        w_online_collab: float = 0.05,
    ) -> None:
        """
        Parameters
        ----------
        matrix_df : pd.DataFrame
            Output of ``load_scores_matrix()``.  Must have columns
            ``example_input``, ``skill_name``, ``norm_<metric>``, …
        embedder_method : str
            ``"tfidf"`` (default, offline) or ``"openai"``.
        ts_state_path : Path, optional
            Path to ``ts_skill_scheduler.json`` produced by
            ``ThompsonSkillScheduler``.  When provided, Bayesian arm state
            is loaded and blended into recommendation scores (Phase 1).
        w_collaborative, w_bayesian_conf, w_uncertainty : float
            Component weights for Phase 1.  Active components are
            re-normalised, so these are relative not absolute.
        freshness_lambda : float
            Exponential decay rate (per day) for the freshness component.
            Set > 0 to enable Phase 2; requires ``ts_state_path``.
        w_freshness : float
            Weight for the freshness component.
        context_store : SkillContextStore, optional
            Phase 3 adaptive per-skill context embeddings.
        contextual_matrix : ContextualMatrix, optional
            Phase 3 online prompt→skill utility matrix.
        w_context_match, w_online_collab : float
            Weights for Phase 3 components.
        """
        self._df        = matrix_df.copy().reset_index(drop=True)
        self._metrics   = metric_columns(matrix_df)
        self._norm_cols = norm_columns(matrix_df)

        if not self._metrics:
            raise ValueError("No score_* columns found in matrix_df.  Check your oracle data.")

        # Build and fit embedder on all known example prompts
        texts = self._df["example_input"].fillna("").tolist()
        self._embedder = Embedder(method=embedder_method)
        self._embedder.fit(texts)

        # ── Phase 1: load Thompson arm state ─────────────────────────────────
        self._ts_arms: dict = {}
        if ts_state_path is not None:
            p = Path(ts_state_path)
            if p.exists():
                try:
                    self._ts_arms = json.loads(p.read_text())
                except Exception:
                    pass

        # ── Weights ──────────────────────────────────────────────────────────
        self._w_collaborative  = w_collaborative
        self._w_bayesian_conf  = w_bayesian_conf
        self._w_uncertainty    = w_uncertainty
        self._freshness_lambda = freshness_lambda
        self._w_freshness      = w_freshness
        self._w_context_match  = w_context_match
        self._w_online_collab  = w_online_collab

        # ── Phase 3 objects ──────────────────────────────────────────────────
        self._context_store     = context_store
        self._contextual_matrix = contextual_matrix

    # ── Public: recommend ────────────────────────────────────────────────────

    def recommend(
        self,
        query: str,
        sim_threshold: float = 0.25,
        score_threshold: float = 0.20,
        min_examples: int = 1,
        top_k: int = 10,
    ) -> list[dict]:
        """Return skill recommendations for *query*.

        Parameters
        ----------
        query : str
            The prompt to find matching skills for.
        sim_threshold : float
            Minimum cosine similarity to include an example row  [0, 1].
        score_threshold : float
            Minimum weighted normalised score for a result to be returned.
        min_examples : int
            Minimum number of similar examples required to recommend a skill.
        top_k : int
            Maximum number of results returned.

        Returns
        -------
        list[dict], sorted by score descending::

            [
              {
                "skill":    "smarthub-support",
                "metric":   "bag_of_words",
                "score":    0.61,          # final blended score
                "collaborative_score": 0.58,
                "bayesian_confidence": 0.72,   # present if ts_state_path set
                "uncertainty_sample":  0.65,   # present if ts_state_path set
                "freshness":           0.91,   # present if freshness enabled
                "context_match":       0.43,   # present if context_store set
                "n_examples": 3,
                "similar_examples": [...],
              },
              ...
            ]
        """
        similarities = self._embedder.similarities(query)   # shape (n_rows,)

        # Phase 3: dense query vector for context store / online matrix
        query_vec: Optional[np.ndarray] = None
        if self._context_store is not None or self._contextual_matrix is not None:
            query_vec = self._embedder.dense_embed(query)

        # ── Filter to rows above sim_threshold ──────────────────────────────
        mask = similarities >= sim_threshold
        if not mask.any():
            return []

        sim_vals = similarities[mask]
        sub_df   = self._df[mask].copy()
        sub_df["_sim"] = sim_vals

        # ── Aggregate per (skill_name, metric) ──────────────────────────────
        results: list[dict] = []

        for skill_name, skill_df in sub_df.groupby("skill_name"):
            skill_str   = str(skill_name)
            sim_weights = skill_df["_sim"].values
            total_sim   = sim_weights.sum()

            # Top-3 example snippets (shared across all metrics for this skill)
            skill_df_sorted = skill_df.sort_values("_sim", ascending=False)
            top_examples = []
            for _, row in skill_df_sorted.head(3).iterrows():
                top_examples.append({
                    "input":      str(row.get("example_input",    "") or "")[:160],
                    "expected":   str(row.get("example_expected", "") or "")[:120],
                    "output":     str(row.get("candidate_output", "") or "")[:160],
                    "similarity": round(float(row["_sim"]), 4),
                })

            # ── Phase 1: Bayesian components ─────────────────────────────────
            arm        = self._ts_arms.get(skill_str, {})
            alpha      = float(arm.get("alpha", 1.0))
            beta_v     = float(arm.get("beta",  1.0))
            bayes_conf = alpha / (alpha + beta_v)
            unc_sample = random.betavariate(alpha, beta_v)

            # ── Phase 2: Freshness ────────────────────────────────────────────
            freshness = 1.0  # neutral default (does not penalise unexplored skills)
            if self._freshness_lambda > 0 and self._ts_arms:
                last_success_at = arm.get("last_success_at")
                if last_success_at is not None:
                    age_days = (time.time() - float(last_success_at)) / 86_400.0
                    freshness = math.exp(-self._freshness_lambda * age_days)

            # ── Phase 3: Context match + online collaborative ──────────────────
            context_match  = 0.5   # neutral prior (halfway between bad and good)
            online_collab  = None
            if query_vec is not None:
                if self._context_store is not None:
                    context_match = self._context_store.context_match(skill_str, query_vec)
                if self._contextual_matrix is not None:
                    online_collab = self._contextual_matrix.collaborative_score(
                        query_vec, skill_str
                    )

            for metric in self._metrics:
                norm_col = f"norm_{metric}"
                if norm_col not in skill_df.columns:
                    continue
                raw_norm = skill_df[norm_col]
                if raw_norm.isna().all():
                    continue
                norm_vals = raw_norm.fillna(0).values
                if total_sim == 0:
                    continue

                collaborative_score = float((sim_weights * norm_vals).sum() / total_sim)

                # ── Weighted fusion ──────────────────────────────────────────
                # Collect (weight, value) for every active component.
                # Active weights are re-normalised so the final score stays
                # in the same range regardless of which phases are enabled.
                components: dict[str, tuple[float, float]] = {
                    "collaborative": (self._w_collaborative, collaborative_score),
                }
                if self._ts_arms:  # Phase 1
                    components["bayesian_confidence"] = (self._w_bayesian_conf, bayes_conf)
                    components["uncertainty_sample"]  = (self._w_uncertainty,   unc_sample)
                if self._freshness_lambda > 0 and self._ts_arms:  # Phase 2
                    components["freshness"] = (self._w_freshness, freshness)
                if self._context_store is not None:  # Phase 3
                    components["context_match"] = (self._w_context_match, context_match)
                if online_collab is not None:  # Phase 3
                    # Blend static + online collaborative: online replaces 30 % of static
                    blended_collab = 0.7 * collaborative_score + 0.3 * online_collab
                    components["collaborative"] = (self._w_collaborative, blended_collab)
                    components["online_collaborative"] = (self._w_online_collab, online_collab)

                total_w = sum(w for w, _ in components.values())
                if total_w == 0:
                    final_score = collaborative_score
                else:
                    final_score = sum(w * v for w, v in components.values()) / total_w

                if final_score < score_threshold:
                    continue
                if len(skill_df) < min_examples:
                    continue

                result: dict = {
                    "skill":                skill_str,
                    "metric":               metric,
                    "score":                round(final_score, 4),
                    "collaborative_score":  round(collaborative_score, 4),
                    "n_examples":           int(len(skill_df)),
                    "mean_similarity":      round(float(sim_weights.mean()), 4),
                    "similar_examples":     top_examples,
                }
                if self._ts_arms:
                    result["bayesian_confidence"] = round(bayes_conf, 4)
                    result["uncertainty_sample"]  = round(unc_sample, 4)
                if self._freshness_lambda > 0 and self._ts_arms:
                    result["freshness"] = round(freshness, 4)
                if self._context_store is not None:
                    result["context_match"] = round(context_match, 4)

                results.append(result)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    # ── Public: record (online update) ───────────────────────────────────────

    def record(
        self,
        query: str,
        skill_name: str,
        reward: float,
    ) -> None:
        """Update online state after executing *skill_name* on *query*.

        Updates the Phase 3 SkillContextStore and ContextualMatrix when
        they are present.  Thompson arm state (Phase 1/2) is controlled by
        the offline evolver and is NOT updated here.

        Parameters
        ----------
        query : str
            The prompt that was routed to *skill_name*.
        skill_name : str
            The skill that was executed.
        reward : float
            Soft reward in [0, 1].  Use ``clamp(improvement, 0, 1)`` from
            the holdout evaluation, or any composite reward signal.
        """
        if self._context_store is None and self._contextual_matrix is None:
            return
        query_vec = self._embedder.dense_embed(query)
        if self._context_store is not None:
            self._context_store.update(skill_name, query_vec, reward)
        if self._contextual_matrix is not None:
            self._contextual_matrix.update(query_vec, skill_name, reward)

    @property
    def n_examples(self) -> int:
        """Total number of (skill, example) pairs in the matrix."""
        return len(self._df)

    @property
    def skills(self) -> list[str]:
        """All unique skill names in the matrix."""
        return sorted(self._df["skill_name"].unique().tolist())

    @property
    def metrics(self) -> list[str]:
        """All metric names found in the matrix."""
        return list(self._metrics)
