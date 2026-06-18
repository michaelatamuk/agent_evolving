# coding: utf-8
"""Generic oracle builder for the skill_recommender self-test.

Converts any list of GEPA-format examples (task_input / expected_behavior)
into a scoring_matrix_<skill_name>.json file that the Recommender can load.

The baseline candidate output is always empty string — scores are 0.0 across
all metrics.  This is intentional: the self-test checks *routing accuracy*
(TF-IDF similarity of the query to example_input text), not fitness scores.
Fitness scores only matter in query mode where real GEPA outputs are present.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from examples.offline.sage.data._scoring import FITNESS_METRICS, compute_scores


def build_oracle_from_examples(
    oracle_dir: Path,
    skill_name: str,
    examples: List[Dict[str, Any]],
    overwrite: bool = False,
) -> Path:
    """Write a scoring-matrix oracle JSON for one skill.

    Parameters
    ----------
    oracle_dir : Path   Destination directory (created if absent).
    skill_name : str    Skill name used as the key in the recommender
                        (typically ``scenario.name``).
    examples   : list   GEPA-format dicts with ``task_input`` and
                        ``expected_behavior`` keys.
    overwrite  : bool   Replace existing file if True (default False).

    Returns
    -------
    Path  of the written JSON file.
    """
    oracle_dir = Path(oracle_dir).expanduser()
    oracle_dir.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^\w-]", "_", skill_name)
    dest = oracle_dir / f"scoring_matrix_{safe_name}.json"

    if dest.exists() and not overwrite:
        print(f"  skip  {skill_name}  (file exists, use --overwrite to replace)")
        return dest

    print(f"  build {skill_name} …", end=" ", flush=True)
    cross_eval = []
    for i, ex in enumerate(examples):
        task_input = ex.get("task_input", "")
        expected   = ex.get("expected_behavior", "")
        output     = ""  # deterministic empty baseline — scores are 0.0
        cross_eval.append({
            "example_id":       f"{safe_name}_{i:04d}",
            "example_input":    task_input,
            "example_expected": expected,
            "candidate_output": output,
            "scores":           compute_scores(output, expected),
        })

    payload = {
        "run_id":              f"{safe_name}_self_test",
        "skill_name":          skill_name,
        "fitness_metrics":     FITNESS_METRICS,
        "baseline_cross_eval": cross_eval,
        "evolved_cross_eval":  [],
    }
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(f"{len(cross_eval)} examples → {dest.name}")
    return dest
