# coding: utf-8
"""HuggingFace loader for HotPotQA (distractor setting).

Dataset : hotpotqa/hotpot_qa  (distractor config, validation split)
Paper   : DSPy arXiv:2310.03714

Dataset fetching is delegated to ``skill_recommender.hotpotqa_loader.fetch_rows``
to avoid duplicating HuggingFace loading logic.

The dataset's ``level`` field (easy / medium / hard) is mapped directly to
``difficulty``.
"""
from __future__ import annotations

from typing import Any, Dict, List


def load(n: int = 50, seed: int = 42) -> List[Dict[str, Any]]:
    """Return ``n`` examples sampled from the HotPotQA validation split.

    Parameters
    ----------
    n:
        Number of examples to return.
    seed:
        Random seed for reproducible sampling.
    """
    return [
        {
            "task_input": row["question"],
            "expected_behavior": row["answer"],
            "difficulty": row.get("level", "unknown"),
            "source": "hotpotqa-hf",
        }
        for row in _fetch_rows(n=n, seed=seed)
    ]


_DEFAULT_BUFFER = 500  # streaming buffer size for random sampling


def _fetch_rows(n: int = 50, seed: int = 42, buffer_size: int = _DEFAULT_BUFFER) -> list[dict]:
    """Return *n* randomly-sampled HotPotQA validation rows (streaming).

    Each row is a dict with keys ``question``, ``answer``, and ``level``
    (``"easy"`` / ``"medium"`` / ``"hard"``).

    Uses streaming to avoid downloading the full ~500 MB split.  A buffer
    of ``buffer_size`` examples is fetched first, then ``n`` are sampled.

    Parameters
    ----------
    n:
        Number of examples to return.
    seed:
        Random seed for reproducible sampling.
    buffer_size:
        How many streaming examples to buffer before sampling ``n``.
    """
    import itertools
    import random

    try:
        from datasets import load_dataset  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "The 'datasets' package is required.\n"
            "Install it with:  pip install datasets"
        ) from exc

    ds = load_dataset(
        "hotpotqa/hotpot_qa", "distractor", split="validation", streaming=True
    )
    buffer = list(itertools.islice(ds, buffer_size))
    rng = random.Random(seed)
    sample = rng.sample(buffer, min(n, len(buffer)))
    return [
        {
            "question": r["question"],
            "answer": r["answer"],
            "level": r.get("level", "unknown"),
        }
        for r in sample
    ]
