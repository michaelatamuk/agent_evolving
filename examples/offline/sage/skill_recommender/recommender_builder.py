# coding: utf-8
"""Core skill recommender.

Given a query prompt, finds the most similar training examples in the
3-D scoring matrix and returns the skills (and associated fitness metrics)
that performed best on those similar examples.

Algorithm
---------
1. Embed all known ``example_input`` texts from the matrix (TF-IDF or OpenAI).
2. For the query, compute cosine similarity against every corpus text.
3. Keep only rows with similarity >= ``sim_threshold``  (default 0.25).
4. For each (skill_name, metric) pair, compute a weighted score:

       weighted_score = Σ sim_i × norm_score_i  /  Σ sim_i

   where the sum is over all matching rows for that pair.
5. Keep only (skill, metric) results with weighted_score >= ``score_threshold``
   (default 0.2) AND supported by at least ``min_examples`` similar examples.
6. Return the top-k results sorted by weighted_score, each annotated with the
   similar example snippets that drove the recommendation.

Usage
-----
    from skill_recommender.recommender import SkillRecommender
    from skill_recommender.matrix_store import load_matrix

    df = load_matrix("~/.openjiuwen/oracle", variant="baseline")
    rec = SkillRecommender(df)
    results = rec.recommend("How do I cancel my subscription?")
    for r in results:
        print(r["skill"], r["metric"], f"{r['score']:.2f}", r["n_examples"])
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from .recommender_similarities_computer import Backend
from .reccmmender_scores_matrix import load_scores_matrix
from .recommender import SkillRecommender


# ── Convenience factory ───────────────────────────────────────────────────────

def build_recommender(
    oracle_dir: Path | str,
    variant: Literal["baseline", "evolved", "both"] = "baseline",
    embedder_method: Backend = "tfidf",
    # Phase 1 — Bayesian arm state
    ts_state_path: Optional[Path] = None,
    w_collaborative: float = 0.35,
    w_bayesian_conf: float = 0.20,
    w_uncertainty: float = 0.15,
    # Phase 2 — Freshness
    freshness_lambda: float = 0.0,
    w_freshness: float = 0.10,
    # Phase 3 — Adaptive context
    context_store=None,
    contextual_matrix=None,
    w_context_match: float = 0.15,
    w_online_collab: float = 0.05,
) -> SkillRecommender:
    """Load matrix from *oracle_dir* and return a ready-to-use SkillRecommender.

    Parameters
    ----------
    oracle_dir : Path | str
        Directory with ``scoring_matrix_*.json`` files.
    variant : str
        Which layer of the 3-D matrix to use: ``"baseline"``, ``"evolved"``,
        or ``"both"``.
    embedder_method : str
        ``"tfidf"`` (default) or ``"openai"``.
    ts_state_path : Path, optional
        Path to ``ts_skill_scheduler.json`` for Phase 1 Bayesian blending.
        Typically ``<skills_root>/ts_skill_scheduler.json``.
    freshness_lambda : float
        Exponential decay rate (per day) for Phase 2 freshness.  Set > 0
        to enable (e.g. ``0.05``).  Requires *ts_state_path*.
    context_store : SkillContextStore, optional
        Phase 3 per-skill adaptive context embeddings.
    contextual_matrix : ContextualMatrix, optional
        Phase 3 online prompt→skill utility matrix.
    """
    df = load_scores_matrix(Path(oracle_dir).expanduser(), variant=variant)
    return SkillRecommender(
        df,
        embedder_method=embedder_method,
        ts_state_path=ts_state_path,
        w_collaborative=w_collaborative,
        w_bayesian_conf=w_bayesian_conf,
        w_uncertainty=w_uncertainty,
        freshness_lambda=freshness_lambda,
        w_freshness=w_freshness,
        context_store=context_store,
        contextual_matrix=contextual_matrix,
        w_context_match=w_context_match,
        w_online_collab=w_online_collab,
    )
