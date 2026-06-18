# coding: utf-8
"""Benchmark dispatch layer.

Single entry point for all HuggingFace benchmark operations.
Clients call build_oracle / fetch_benchmark_rows / fetch_benchmark_examples
without knowing which loader module handles each benchmark.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from examples.offline.sage.data.scenarios.hf.data_loaders.gsm8k_loader import fetch_rows as _gsm8k_rows, load_gsm8k_to_oracle
from examples.offline.sage.data.scenarios.hf.data_loaders import fetch_rows as _hotpotqa_rows, load_hotpotqa_to_oracle
from examples.offline.sage.data.scenarios.hf.data_loaders import fetch_rows as _pubmedqa_rows, load_pubmedqa_to_oracle
from examples.offline.sage.data.scenarios.hf.data_loaders.aquarat_loader import fetch_rows as _aquarat_rows, load_aquarat_to_oracle
from examples.offline.sage.data.scenarios.hf.data_loaders import load_bbh_to_oracle, DEFAULT_TASKS as _BBH_DEFAULT_TASKS
from examples.offline.sage.data.scenarios.hf.gsm8k.golden_examples.hf_loader import load as _gsm8k_examples
from examples.offline.sage.data.scenarios.hf.hotpotqa import load as _hotpotqa_examples
from examples.offline.sage.data.scenarios.hf.pubmedqa import load as _pubmedqa_examples
from examples.offline.sage.data.scenarios.hf.aquarat import load as _aquarat_examples


_ORACLE_BUILDERS: Dict[str, Any] = {
    "gsm8k":    lambda d, n, ow: load_gsm8k_to_oracle(d, n_examples=n, overwrite=ow),
    "hotpotqa": lambda d, n, ow: load_hotpotqa_to_oracle(d, n_examples=n, overwrite=ow),
    "pubmedqa": lambda d, n, ow: load_pubmedqa_to_oracle(d, n_examples=n, overwrite=ow),
    "aquarat":  lambda d, n, ow: load_aquarat_to_oracle(d, n_examples=n, overwrite=ow),
    "bbh":      lambda d, n, ow: load_bbh_to_oracle(d, tasks=_BBH_DEFAULT_TASKS, n_examples=n, overwrite=ow),
}

_ROW_FETCHERS: Dict[str, Any] = {
    "gsm8k":    _gsm8k_rows,
    "hotpotqa": _hotpotqa_rows,
    "pubmedqa": _pubmedqa_rows,
    "aquarat":  _aquarat_rows,
}

_EXAMPLE_FETCHERS: Dict[str, Any] = {
    "gsm8k":    _gsm8k_examples,
    "hotpotqa": _hotpotqa_examples,
    "pubmedqa": _pubmedqa_examples,
    "aquarat":  _aquarat_examples,
}


def build_oracle(
    benchmark: str,
    oracle_dir: Path,
    n_examples: int = 50,
    overwrite: bool = False,
) -> Path:
    """Write a scoring-matrix oracle file for *benchmark* into *oracle_dir*."""
    if benchmark not in _ORACLE_BUILDERS:
        raise ValueError(
            f"Unknown benchmark {benchmark!r}. Available: {sorted(_ORACLE_BUILDERS)}"
        )
    return _ORACLE_BUILDERS[benchmark](oracle_dir, n_examples, overwrite)


def fetch_benchmark_rows(
    benchmark: str,
    n: int = 50,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """Return raw HuggingFace rows for *benchmark* (field names vary per dataset)."""
    if benchmark not in _ROW_FETCHERS:
        raise ValueError(
            f"fetch_benchmark_rows not supported for {benchmark!r}. "
            f"Available: {sorted(_ROW_FETCHERS)}"
        )
    return _ROW_FETCHERS[benchmark](n=n, seed=seed)


def fetch_benchmark_examples(
    benchmark: str,
    n: int = 50,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """Return GEPA-shaped examples for *benchmark*.

    Each dict has keys: task_input, expected_behavior, difficulty, source.
    """
    if benchmark not in _EXAMPLE_FETCHERS:
        raise ValueError(
            f"fetch_benchmark_examples not supported for {benchmark!r}. "
            f"Available: {sorted(_EXAMPLE_FETCHERS)}"
        )
    return _EXAMPLE_FETCHERS[benchmark](n=n, seed=seed)
