# coding: utf-8
"""Scenario dataclass and registry for the Thompson Sampling vs baseline GEPA demo.

A Scenario bundles a skill definition with its golden benchmark examples
so the runner can select any pair by name.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


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
    golden_examples:
        Static list of golden example dicts (always available, no network needed).
        Each dict must have ``task_input``, ``expected_behavior``, ``difficulty``,
        and ``source``.
    description:
        One-line human-readable description shown in the runner banner.
    loader:
        Optional callable ``(n: int, seed: int) -> List[Dict]`` that fetches
        examples from the original HuggingFace benchmark dataset.  Only present
        for benchmark scenarios (gsm8k, hotpotqa, pubmedqa, aquarat).
        Call ``load_examples(n, seed)`` rather than invoking this directly.
    """

    name: str
    skill_body: str
    skill_frontmatter: str
    golden_examples: List[Dict[str, Any]]
    description: str = ""
    loader: Optional[Callable[..., List[Dict[str, Any]]]] = field(default=None, repr=False)

    # ── Derived helpers ────────────────────────────────────────────────────────

    def load_examples(self, n: int = 50, seed: int = 42) -> List[Dict[str, Any]]:
        """Return examples for this scenario.

        For benchmark scenarios (gsm8k, hotpotqa, etc.) this fetches ``n``
        examples from the HuggingFace dataset when a ``loader`` is registered.
        Falls back to the static ``golden_examples`` list when the loader is
        absent or raises (e.g. no network access).

        Parameters
        ----------
        n:
            Number of examples to load from HuggingFace.  Ignored when no
            loader is registered.
        seed:
            Random seed for reproducible sampling.
        """
        if self.loader is None:
            return self.golden_examples
        try:
            return self.loader(n=n, seed=seed)
        except Exception as exc:
            print(
                f"  [WARN] HuggingFace loader for '{self.name}' failed "
                f"({exc}); falling back to {len(self.golden_examples)} "
                "static examples."
            )
            return self.golden_examples

    def example_counts(self) -> Dict[str, int]:
        """Return a dict mapping difficulty label → count."""
        counts: Dict[str, int] = {}
        for ex in self.golden_examples:
            d = ex.get("difficulty", "unknown")
            counts[d] = counts.get(d, 0) + 1
        return counts

    def summary_line(self) -> str:
        counts = self.example_counts()
        parts = " / ".join(
            f"{counts.get(d, 0)} {d}"
            for d in ("easy", "medium", "hard")
            if counts.get(d, 0)
        )
        return f"{self.name}  —  {len(self.golden_examples)} examples ({parts})"
