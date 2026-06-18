# coding: utf-8
"""GSM8K row fetcher — returns raw HuggingFace rows for use by hf_loader.py."""
from __future__ import annotations


def fetch_rows(n: int = 50, seed: int = 42) -> list[dict]:
    """Return *n* randomly-sampled GSM8K test rows.

    Each row is a dict with keys ``question`` and ``answer`` (the full
    chain-of-thought string ending with ``#### <number>``).

    Parameters
    ----------
    n:
        Number of examples to return.
    seed:
        Random seed for reproducible sampling.
    """
    try:
        from datasets import load_dataset  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "The 'datasets' package is required.\n"
            "Install it with:  pip install datasets"
        ) from exc

    ds = load_dataset("openai/gsm8k", "main", split="test")
    ds = ds.shuffle(seed=seed).select(range(min(n, len(ds))))
    return [{"question": r["question"], "answer": r["answer"]} for r in ds]
