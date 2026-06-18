from __future__ import annotations

import pandas as pd

from .recommender_similarities_computer import Embedder, Backend
from .scores_matrix import norm_columns, metric_columns


class SkillRecommender:
    """Fit once on the matrix, then call recommend() for any query."""

    def __init__(
        self,
        matrix_df: pd.DataFrame,
        embedder_method: Backend = "tfidf",
    ) -> None:
        """
        Parameters
        ----------
        matrix_df : pd.DataFrame
            Output of ``matrix_store.load_matrix()``.  Must have columns
            ``example_input``, ``skill_name``, ``norm_<metric>``, …
        embedder_method : str
            ``"tfidf"`` (default, offline) or ``"openai"``.
        """
        self._df      = matrix_df.copy().reset_index(drop=True)
        self._metrics = metric_columns(matrix_df)
        self._norm_cols = norm_columns(matrix_df)

        if not self._metrics:
            raise ValueError("No score_* columns found in matrix_df.  Check your oracle data.")

        # Build and fit embedder on all known example prompts
        texts = self._df["example_input"].fillna("").tolist()
        self._embedder = Embedder(method=embedder_method)
        self._embedder.fit(texts)

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
                "score":    0.61,          # weighted normalised score
                "n_examples": 3,           # similar examples supporting this
                "similar_examples": [      # up to 3 snippets
                    {
                        "input":      "...",   # training example prompt
                        "expected":   "...",   # ground-truth expected output
                        "output":     "...",   # what the skill actually produced
                        "similarity": 0.72,
                    },
                    ...
                ],
              },
              ...
            ]
        """
        similarities = self._embedder.similarities(query)  # shape (n_rows,)

        # ── Filter to rows above sim_threshold ──────────────────────────────
        mask = similarities >= sim_threshold
        if not mask.any():
            return []

        sim_vals = similarities[mask]                  # 1-D array
        sub_df   = self._df[mask].copy()
        sub_df["_sim"] = sim_vals

        # ── Aggregate per (skill_name, metric) ──────────────────────────────
        results: list[dict] = []

        for skill_name, skill_df in sub_df.groupby("skill_name"):
            sim_weights = skill_df["_sim"].values
            total_sim   = sim_weights.sum()

            # Top-3 example snippets (shared across all metrics for this skill)
            skill_df_sorted = skill_df.sort_values("_sim", ascending=False)
            top_examples = []
            for _, row in skill_df_sorted.head(3).iterrows():
                entry = {
                    "input":      str(row.get("example_input",    "") or "")[:160],
                    "expected":   str(row.get("example_expected", "") or "")[:120],
                    "output":     str(row.get("candidate_output", "") or "")[:160],
                    "similarity": round(float(row["_sim"]), 4),
                }
                top_examples.append(entry)

            for metric in self._metrics:
                norm_col = f"norm_{metric}"
                if norm_col not in skill_df.columns:
                    continue
                raw_norm = skill_df[norm_col]
                if raw_norm.isna().all():
                    # All scores were 0 or None for this metric — skip silently
                    continue
                norm_vals = raw_norm.fillna(0).values
                if total_sim == 0:
                    continue
                weighted_score = float((sim_weights * norm_vals).sum() / total_sim)

                if weighted_score < score_threshold:
                    continue
                if len(skill_df) < min_examples:
                    continue

                results.append({
                    "skill":            str(skill_name),
                    "metric":           metric,
                    "score":            round(weighted_score, 4),
                    "n_examples":       int(len(skill_df)),
                    "mean_similarity":  round(float(sim_weights.mean()), 4),
                    "similar_examples": top_examples,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

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
