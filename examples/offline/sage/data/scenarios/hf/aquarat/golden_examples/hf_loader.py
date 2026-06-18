# coding: utf-8
"""HuggingFace loader for AQuA-RAT (Algebra Question Answering with Rationales).

Dataset : deepmind/aqua_rat  (raw config, test split — 254 examples)
Paper   : OPRO arXiv:2309.03409

Dataset fetching is delegated to ``data_loaders.aquarat_loader.fetch_rows``
to avoid duplicating HuggingFace loading logic.

``task_input`` formats the question together with the five lettered options.
``expected_behavior`` is the full rationale followed by ``Answer: <letter>``.

Difficulty is assigned by tertile of rationale length across the fetched
batch: shorter solution → easy, longer multi-step solution → hard.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _tertile_difficulties(lengths: List[int]) -> List[str]:
    n = len(lengths)
    if n == 0:
        return []
    s = sorted(lengths)
    t1, t2 = s[n // 3], s[2 * n // 3]
    return [
        "easy" if l <= t1 else ("hard" if l > t2 else "medium")
        for l in lengths
    ]


def load(n: int = 50, seed: int = 42) -> List[Dict[str, Any]]:
    """Return ``n`` examples sampled from the AQuA-RAT test split.

    Parameters
    ----------
    n:
        Number of examples to return.
    seed:
        Random seed for reproducible sampling.
    """
    from examples.offline.sage.data.scenarios.hf.aquarat.aquarat_loader import fetch_rows

    raw_rows = fetch_rows(n=n, seed=seed)
    examples: List[Dict[str, Any]] = []
    rationale_lengths: List[int] = []

    for row in raw_rows:
        options_text = "\n".join(row["options"])
        task_input = f"{row['question']}\nOptions:\n{options_text}"
        rationale = row.get("rationale", "").strip()
        correct = row.get("correct", "").strip()
        expected = f"{rationale}\nAnswer: {correct}" if rationale else f"Answer: {correct}"
        examples.append({
            "task_input": task_input,
            "expected_behavior": expected,
            "difficulty": "unknown",
            "source": "aquarat-hf",
        })
        rationale_lengths.append(len(rationale))

    difficulties = _tertile_difficulties(rationale_lengths)
    for ex, diff in zip(examples, difficulties):
        ex["difficulty"] = diff

    return examples
