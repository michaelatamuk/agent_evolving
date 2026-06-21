# coding: utf-8
"""Scenario dataclass and registry for the Thompson Sampling vs baseline GEPA demo.

A Scenario bundles a skill definition with its golden benchmark examples
so the runner can select any pair by name.
"""
from __future__ import annotations

import random as _random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class Scenario:
    """A complete evolution scenario: baseline skill + golden benchmark examples.

    Attributes
    ----------
    name:
        Identifier used as the skill directory key (e.g. ``"api-security"``).
        Must be a valid filesystem directory component.
    skill_body:
        Body text of the SKILL.md file (the part after the ``---`` frontmatter).
    skill_frontmatter:
        Frontmatter content between the ``---`` delimiters (YAML key-value pairs).
    description:
        One-line human-readable description shown in the runner banner.
    loader:
        Optional callable ``(n: int, seed: int) -> List[Dict]`` that fetches
        examples.  Synthetic scenarios use ``lambda n, seed: GOLDEN_EXAMPLES``.
        HF scenarios call the HuggingFace dataset.
        Call ``load_examples(n, seed)`` rather than invoking this directly.
    oracle_skill_name:
        Optional identifier used when the scenario has a pre-built oracle skill
        (e.g. a BBH task name).  ``None`` for most scenarios.
    sample_query:
        Optional representative query string shown in the tester banner.
        ``None`` when not provided.
    """

    name: str
    skill_body: str
    skill_frontmatter: str
    description: str = ""
    loader: Optional[Callable[..., List[Dict[str, Any]]]] = field(default=None, repr=False)
    oracle_skill_name: Optional[str] = field(default=None)
    sample_query: Optional[str] = field(default=None)

    # ── Derived helpers ────────────────────────────────────────────────────────

    def load_examples(self, n: int = 50, seed: int = 42) -> List[Dict[str, Any]]:
        """Return examples for this scenario.

        For HF benchmark scenarios this fetches ``n`` examples from HuggingFace.
        For synthetic scenarios the loader returns the full static list
        (``n`` and ``seed`` are accepted but ignored).
        Returns ``[]`` when no loader is registered (e.g. bbh).

        Parameters
        ----------
        n:
            Number of examples to load from HuggingFace.
        seed:
            Random seed for reproducible sampling.
        """
        if self.loader:
            return self.loader(n=n, seed=seed)
        else:
            return []

    def split(
        self,
        n: int = 50,
        seed: int = 42,
        train_ratio: float = 0.8,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Load examples and split into (trainset, valset).

        Parameters
        ----------
        n:
            Number of examples to load (passed to ``load_examples``).
        seed:
            Random seed used both for loading and for the shuffle.
        train_ratio:
            Fraction of examples to place in the training set.
            The remainder goes to the validation set.

        Returns
        -------
        (trainset, valset)  — both are lists of example dicts.
        """
        examples = self.load_examples(n=n, seed=seed)
        shuffled = list(examples)
        _random.Random(seed).shuffle(shuffled)
        cut = max(1, int(len(shuffled) * train_ratio))
        return shuffled[:cut], shuffled[cut:]

    def example_counts(self, n: int = 50, seed: int = 42) -> Dict[str, int]:
        """Return a dict mapping difficulty label → count."""
        counts: Dict[str, int] = {}
        for ex in self.load_examples(n=n, seed=seed):
            d = ex.get("difficulty", "unknown")
            counts[d] = counts.get(d, 0) + 1
        return counts

    def summary_line(self, n: int = 50, seed: int = 42) -> str:
        examples = self.load_examples(n=n, seed=seed)
        counts = {}
        for ex in examples:
            d = ex.get("difficulty", "unknown")
            counts[d] = counts.get(d, 0) + 1
        parts = " / ".join(
            f"{counts.get(d, 0)} {d}"
            for d in ("easy", "medium", "hard")
            if counts.get(d, 0)
        )
        return f"{self.name}  —  {len(examples)} examples ({parts})"
