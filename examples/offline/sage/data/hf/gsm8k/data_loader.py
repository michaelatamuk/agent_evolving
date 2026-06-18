# coding: utf-8
"""HuggingFace loader for GSM8K (Grade School Math 8K).

Dataset : openai/gsm8k  (main config, test split — 1,319 examples)
Paper   : OPRO arXiv:2309.03409, DSPy arXiv:2310.03714

Dataset fetching is delegated to ``data_loaders.gsm8k_loader.fetch_rows``
to avoid duplicating HuggingFace loading logic.

``expected_behavior`` is the chain-of-thought answer with calculator
annotations (``<<expr=N>>``) stripped, ending with ``#### <number>``.

Difficulty is derived from the number of arithmetic steps in the raw
answer (count of ``<<`` tokens before cleaning):
  0-1 steps → easy  |  2-3 → medium  |  4+ → hard
"""
from __future__ import annotations

import re
from typing import Any, Dict, List


def _clean_answer(raw: str) -> str:
    """Strip ``<<expr=N>>`` calculator annotations from a GSM8K answer."""
    return re.sub(r"<<[^>]+>>", "", raw).strip()


def _step_difficulty(raw: str) -> str:
    steps = raw.count("<<")
    if steps <= 1:
        return "easy"
    if steps <= 3:
        return "medium"
    return "hard"


def load(n: int = 50, seed: int = 42) -> List[Dict[str, Any]]:
    """Return ``n`` examples sampled from the GSM8K test split.

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
            "expected_behavior": _clean_answer(row["answer"]),
            "difficulty": _step_difficulty(row["answer"]),
            "source": "gsm8k-hf",
        }
        for row in _fetch_rows(n=n, seed=seed)
    ]


def _fetch_rows(n: int = 50, seed: int = 42) -> list[dict]:
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
