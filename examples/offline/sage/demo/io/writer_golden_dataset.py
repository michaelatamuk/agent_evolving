import json
import random as _random
from pathlib import Path


def write_golden_dataset(skills_root: Path, name: str, examples: list, seed: int = 42) -> Path:
    """Write examples to the golden_dataset path that eval_source='golden' reads.

    Parameters
    ----------
    skills_root:
        Root directory containing skill sub-directories.
    name:
        Skill name (used as sub-directory key).
    examples:
        List of example dicts with ``task_input``, ``expected_behavior``,
        ``difficulty``, and ``source`` keys.
    seed:
        Random seed for reproducible shuffling (default: 42).
    """
    out = skills_root / name / "golden_dataset"
    out.mkdir(parents=True, exist_ok=True)

    shuffled = list(examples)
    _random.Random(seed).shuffle(shuffled)
    n          = len(shuffled)
    train_end  = int(n * 0.50)
    val_end    = train_end + int(n * 0.25)
    splits     = {"train": shuffled[:train_end],
                  "val":   shuffled[train_end:val_end],
                  "holdout": shuffled[val_end:]}

    for split_name, rows in splits.items():
        path = out / f"{split_name}.jsonl"
        with open(path, "w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    return out
