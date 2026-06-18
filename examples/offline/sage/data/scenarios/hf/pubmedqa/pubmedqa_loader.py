# coding: utf-8
"""PubMedQA row fetcher — returns raw HuggingFace rows for use by hf_loader.py."""
from __future__ import annotations


def fetch_rows(n: int = 50, seed: int = 42) -> list[dict]:
    """Return *n* randomly-sampled PubMedQA pqa_labeled rows.

    Each row is a dict with keys ``question``, ``context``,
    ``final_decision`` (``"yes"`` / ``"no"`` / ``"maybe"``), and
    ``long_answer``.

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

    ds = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train")
    ds = ds.shuffle(seed=seed).select(range(min(n, len(ds))))
    return [
        {
            "question": r["question"],
            "context": r["context"],
            "final_decision": r["final_decision"],
            "long_answer": r.get("long_answer", ""),
        }
        for r in ds
    ]
