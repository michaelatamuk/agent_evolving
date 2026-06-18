# coding: utf-8
"""AQuA-RAT row fetcher — returns raw HuggingFace rows for use by hf_loader.py."""
from __future__ import annotations


def fetch_rows(n: int = 50, seed: int = 42) -> list[dict]:
    """Return *n* randomly-sampled AQuA-RAT test rows.

    Each row is a dict with keys ``question``, ``options`` (list of strings
    like ``"A)120"``), ``rationale`` (step-by-step solution), and ``correct``
    (option letter string, e.g. ``"B"``).

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

    ds = load_dataset("deepmind/aqua_rat", "raw", split="test")
    ds = ds.shuffle(seed=seed).select(range(min(n, len(ds))))
    return [
        {
            "question": r["question"],
            "options": r["options"],
            "rationale": r.get("rationale", ""),
            "correct": r["correct"],
        }
        for r in ds
    ]
