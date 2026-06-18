# coding: utf-8
"""HotPotQA row fetcher — returns raw HuggingFace rows for use by hf_loader.py."""
from __future__ import annotations

_DEFAULT_BUFFER = 500  # streaming buffer size for random sampling


def fetch_rows(n: int = 50, seed: int = 42, buffer_size: int = _DEFAULT_BUFFER) -> list[dict]:
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
