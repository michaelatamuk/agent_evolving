# coding: utf-8
"""Phase 3 — Per-skill adaptive context embeddings.

Each skill maintains a running *context embedding* — an exponentially
weighted average (EWA) of the query embeddings for prompts on which the
skill was executed, weighted by the reward received.

High-reward executions pull the skill's context toward the current query
more strongly than low-reward ones.  Over time the embedding converges to
the centroid of the input distribution where the skill performs well.

At recommendation time, ``context_match(skill, query_vec)`` returns the
cosine similarity between the query and the skill's context embedding.
A high value means the query is in the zone where the skill has
historically worked well.

Persistence
-----------
State is stored as a JSON file::

    {
      "smarthub-support": [0.12, -0.04, 0.87, ...],   # 1-D float list
      "contract-review":  [...],
      ...
    }

Each list is the L2-normalised running context embedding for that skill.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import numpy as np


class SkillContextStore:
    """Maintains a per-skill running embedding updated from online executions.

    Parameters
    ----------
    state_path : Path
        File to persist the embeddings.  Created automatically if absent.
    ewa_base_rate : float
        Base EWA learning rate.  The effective update rate is
        ``ewa_base_rate × reward`` so high-reward executions update more
        aggressively.  Suggested range: 0.05 – 0.20.
    """

    def __init__(
        self,
        state_path: Path,
        ewa_base_rate: float = 0.10,
    ) -> None:
        self._state_path  = Path(state_path)
        self._ewa_rate    = ewa_base_rate
        self._embeddings: Dict[str, np.ndarray] = {}
        self._load()

    # ── Online update ─────────────────────────────────────────────────────────

    def update(
        self,
        skill_name: str,
        query_vec: np.ndarray,
        reward: float,
    ) -> None:
        """Update the context embedding for *skill_name* after an execution.

        Parameters
        ----------
        skill_name : str
            Name of the skill that was executed.
        query_vec : np.ndarray
            Dense, L2-normalised embedding of the prompt (from
            ``Embedder.dense_embed()``).
        reward : float
            Soft reward in [0, 1].  Low reward → small update; high reward →
            large update.
        """
        reward = max(0.0, min(1.0, float(reward)))
        rate   = self._ewa_rate * reward          # scale by reward magnitude

        if skill_name in self._embeddings:
            existing = self._embeddings[skill_name]
            updated  = (1.0 - rate) * existing + rate * query_vec
        else:
            # Initialise directly from the first query embedding
            updated = query_vec.copy().astype(np.float32)

        # Re-normalise so cosine similarity stays meaningful
        norm = np.linalg.norm(updated)
        if norm > 0:
            updated = updated / norm

        self._embeddings[skill_name] = updated.astype(np.float32)
        self._save()

    # ── Query ─────────────────────────────────────────────────────────────────

    def context_match(self, skill_name: str, query_vec: np.ndarray) -> float:
        """Return cosine similarity between *query_vec* and *skill_name*'s
        context embedding.

        Returns 0.5 (neutral) for skills with no recorded executions, so
        unknown skills are neither promoted nor penalised.

        Values are clipped to [0, 1] because both embeddings are
        L2-normalised and cosine similarity can be slightly negative for
        TF-IDF vectors.
        """
        if skill_name not in self._embeddings:
            return 0.5

        emb = self._embeddings[skill_name]
        dot = float(np.dot(emb, query_vec))
        # Both vectors are L2-normalised → dot product == cosine similarity
        return float(np.clip(dot, 0.0, 1.0))

    def known_skills(self) -> list[str]:
        """Return skill names that have at least one recorded execution."""
        return list(self._embeddings.keys())

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save(self) -> None:
        data = {name: vec.tolist() for name, vec in self._embeddings.items()}
        tmp  = self._state_path.with_suffix(".tmp")
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(data))
        tmp.rename(self._state_path)

    def _load(self) -> None:
        if not self._state_path.exists():
            return
        try:
            data = json.loads(self._state_path.read_text())
            self._embeddings = {
                k: np.array(v, dtype=np.float32)
                for k, v in data.items()
            }
        except Exception:
            pass
