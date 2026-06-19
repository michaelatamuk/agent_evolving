# coding: utf-8
"""Phase 3 — Online prompt→skill utility matrix (M[prompt, skill]).

Stores a rolling buffer of observed (query_embedding, skill_name, reward)
triples.  For a new query, the matrix computes a similarity-weighted
average reward across the top-k most similar past observations for each
skill — exactly step 3a of the Contextual Bayesian Prompt-Skill Router
algorithm::

    collaborative_score(Si, P) =
        Σ  similarity(P, p) × reward(p, Si)
        / Σ  similarity(P, p)
        for p in top_k_similar_prompts(P)

This complements the static 3-D scoring matrix loaded from oracle files:
the static matrix captures *offline evolution quality*, while this matrix
captures *live deployment utility* observed at inference time.

Persistence
-----------
State is stored as a JSON file with at most ``max_entries`` entries (oldest
evicted first when the buffer fills)::

    {
      "entries": [
        {"vec": [...], "skill": "contract-review", "reward": 0.82},
        ...
      ]
    }

The embedding vectors are stored as float lists.  With TF-IDF (10 k dims)
and 1 000 entries the file is ≈ 80 MB; with OpenAI embeddings (1 536 dims)
it is ≈ 12 MB.  Set ``max_entries`` lower if disk space is a concern.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


class ContextualMatrix:
    """Online-updated M[prompt_embedding, skill] = utility score.

    Parameters
    ----------
    state_path : Path
        File to persist the rolling buffer.  Created automatically.
    top_k : int
        Number of most-similar past observations to use when computing the
        collaborative score.  Higher values are more stable but slower.
    max_entries : int
        Maximum buffer size.  Oldest entries are evicted when full.
    """

    def __init__(
        self,
        state_path: Path,
        top_k: int = 10,
        max_entries: int = 1_000,
    ) -> None:
        self._state_path  = Path(state_path)
        self._top_k       = top_k
        self._max_entries = max_entries

        # List of {"vec": np.ndarray, "skill": str, "reward": float}
        self._entries: List[Dict] = []
        # Pre-computed numpy matrix of vecs (rebuilt lazily)
        self._vec_matrix: Optional[np.ndarray] = None
        self._dirty = False

        self._load()

    # ── Online update ─────────────────────────────────────────────────────────

    def update(
        self,
        query_vec: np.ndarray,
        skill_name: str,
        reward: float,
    ) -> None:
        """Record an observed (prompt, skill, reward) triple.

        Parameters
        ----------
        query_vec : np.ndarray
            Dense, L2-normalised embedding from ``Embedder.dense_embed()``.
        skill_name : str
            The skill that was executed on this prompt.
        reward : float
            Soft reward in [0, 1].
        """
        self._entries.append({
            "vec":    query_vec.astype(np.float32),
            "skill":  str(skill_name),
            "reward": float(max(0.0, min(1.0, reward))),
        })
        # Evict oldest entries beyond cap
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        self._vec_matrix = None   # invalidate cached matrix
        self._dirty = True
        self._save()

    # ── Query ─────────────────────────────────────────────────────────────────

    def collaborative_score(
        self,
        query_vec: np.ndarray,
        skill_name: str,
    ) -> float:
        """Similarity-weighted average reward for *skill_name* given *query_vec*.

        Returns 0.5 (neutral prior) when no observations exist for the skill.

        Algorithm
        ---------
        1. Compute cosine similarity between *query_vec* and all stored vecs.
        2. Keep only entries where skill == skill_name.
        3. Take top-k by similarity.
        4. Return similarity-weighted average reward.
        """
        skill_entries = [e for e in self._entries if e["skill"] == skill_name]
        if not skill_entries:
            return 0.5  # no evidence → neutral

        vecs    = np.stack([e["vec"] for e in skill_entries])    # (n, dim)
        rewards = np.array([e["reward"] for e in skill_entries]) # (n,)

        # Cosine similarity: both query and stored vecs are L2-normalised
        sims = (vecs @ query_vec).astype(float)  # (n,)

        # Take top-k by similarity (clip k to available entries)
        k = min(self._top_k, len(skill_entries))
        top_idx  = np.argpartition(sims, -k)[-k:]
        top_sims = sims[top_idx]
        top_rew  = rewards[top_idx]

        total_sim = top_sims.sum()
        if total_sim <= 0:
            return float(top_rew.mean())  # fall back to simple average

        return float((top_sims * top_rew).sum() / total_sim)

    def known_skills(self) -> list[str]:
        """Return all skill names that have at least one recorded entry."""
        return list({e["skill"] for e in self._entries})

    def __len__(self) -> int:
        return len(self._entries)

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save(self) -> None:
        payload = {
            "entries": [
                {
                    "vec":    e["vec"].tolist(),
                    "skill":  e["skill"],
                    "reward": e["reward"],
                }
                for e in self._entries
            ]
        }
        tmp = self._state_path.with_suffix(".tmp")
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(payload))
        tmp.rename(self._state_path)

    def _load(self) -> None:
        if not self._state_path.exists():
            return
        try:
            data = json.loads(self._state_path.read_text())
            self._entries = [
                {
                    "vec":    np.array(e["vec"], dtype=np.float32),
                    "skill":  e["skill"],
                    "reward": float(e["reward"]),
                }
                for e in data.get("entries", [])
            ]
        except Exception:
            pass
