# coding: utf-8
"""HuggingFace loader for PubMedQA (expert-labeled subset).

Dataset : qiaojin/PubMedQA  (pqa_labeled config, train split — 1,000 examples)
Paper   : SkillGen arXiv:2605.10999

Dataset fetching is delegated to ``data_loaders.pubmedqa_loader.fetch_rows``
to avoid duplicating HuggingFace loading logic.

``task_input`` is the abstract sentences followed by the research question.
``expected_behavior`` is the verdict (yes/no/maybe) followed by the expert
long answer.

Difficulty is assigned by tertile of ``long_answer`` length across the
fetched batch: shorter evidence → easy, longer → hard.
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
    """Return ``n`` examples sampled from PubMedQA pqa_labeled train split.

    Parameters
    ----------
    n:
        Number of examples to return.
    seed:
        Random seed for reproducible sampling.
    """
    from examples.offline.sage.data.scenarios.hf.pubmedqa.pubmedqa_loader import fetch_rows

    raw_rows = fetch_rows(n=n, seed=seed)
    examples: List[Dict[str, Any]] = []
    long_answer_lengths: List[int] = []

    for row in raw_rows:
        context_text = "\n".join(row["context"]["contexts"])
        task_input = f"Context:\n{context_text}\n\nQuestion: {row['question']}"
        verdict = row["final_decision"]
        long_answer = row.get("long_answer", "").strip()
        expected = f"{verdict}\n{long_answer}" if long_answer else verdict
        examples.append({
            "task_input": task_input,
            "expected_behavior": expected,
            "difficulty": "unknown",
            "source": "pubmedqa-hf",
        })
        long_answer_lengths.append(len(long_answer))

    difficulties = _tertile_difficulties(long_answer_lengths)
    for ex, diff in zip(examples, difficulties):
        ex["difficulty"] = diff

    return examples
