from __future__ import annotations

# NOTE: GAIA is a gated dataset.  Before first use, accept the terms of access
# at https://huggingface.co/datasets/gaia-benchmark/GAIA and authenticate once
# with ``huggingface-cli login``.
#
# SAGE limitation: GAIA questions that reference file attachments (PDFs, images,
# audio, spreadsheets) are filtered out here because SAGE evaluates text-in /
# text-out skills without tool-use or file access.  On the 2023 validation split
# ~60-65% of rows are text-only; Level 1 has the highest text-only fraction.

import random
from typing import Any, Dict, List

from datasets import load_dataset


_LEVEL_TO_DIFFICULTY: Dict[int, str] = {1: "easy", 2: "medium", 3: "hard"}


def load(n: int = 50, seed: int = 42) -> List[Dict[str, Any]]:
    """Return up to *n* text-only examples from the GAIA 2023 validation split.

    Rows with non-empty ``file_name`` are skipped (they require file access).
    If fewer than *n* text-only rows are available the full text-only pool is
    returned without truncation.
    """
    rows = _fetch_rows(n=n, seed=seed)
    return [
        {
            "task_input": row["Question"],
            "expected_behavior": row["Final answer"],
            "difficulty": _LEVEL_TO_DIFFICULTY.get(row["Level"], "unknown"),
            "source": "gaia-hf",
        }
        for row in rows
    ]


def _fetch_rows(n: int = 50, seed: int = 42) -> List[Dict[str, Any]]:
    """Fetch *n* randomly-sampled text-only GAIA validation rows."""
    ds = load_dataset(
        "gaia-benchmark/GAIA",
        "2023_all",
        split="validation",
        trust_remote_code=True,
    )
    text_only = [r for r in ds if not r.get("file_name", "")]
    rng = random.Random(seed)
    sample = rng.sample(text_only, min(n, len(text_only)))
    return [
        {
            "Question": r["Question"],
            "Final answer": r["Final answer"],
            "Level": r["Level"],
        }
        for r in sample
    ]
