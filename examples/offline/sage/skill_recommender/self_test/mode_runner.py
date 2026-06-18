from __future__ import annotations

import argparse
import contextlib
import tempfile
from pathlib import Path

from .oracle_builder import build_oracle_from_examples
from .results_printer import _print_benchmark_results
from ..recommender_builder import build_recommender
from ...data import list_scenarios


def _self_test_scenarios():
    """Return scenarios with a loader (excludes bbh which has no data)."""
    return [s for s in list_scenarios() if s.loader is not None]


def _run_self_test(args: argparse.Namespace, DEFAULT_ORACLE_DIR: Path) -> None:
    """Build per-scenario oracles from load_examples(), then verify routing accuracy.

    Uses examples[0] as the routing query and examples[1:] for the oracle,
    so the query example is never present in the oracle (no self-match).
    """
    scenarios       = _self_test_scenarios()
    all_names       = [s.name for s in scenarios]
    requested       = args.self_test if args.self_test else all_names
    n_examples      = args.n_examples
    overwrite       = args.overwrite
    sim_threshold   = args.sim_threshold
    score_threshold = args.score_threshold
    top_k           = args.top_k

    oracle_dir_arg = (args.oracle_dir or args.data_dir).expanduser()

    ctx: contextlib.AbstractContextManager
    if oracle_dir_arg != DEFAULT_ORACLE_DIR:
        oracle_dir_arg.mkdir(parents=True, exist_ok=True)
        ctx = contextlib.nullcontext(oracle_dir_arg)
    else:
        ctx = tempfile.TemporaryDirectory(prefix="self_test_oracle_")  # type: ignore[assignment]

    with ctx as tmpdir:
        oracle_dir = Path(tmpdir)

        # Phase 1 — build oracles, capture per-scenario query from examples[0]
        print(f"\nBuilding self-test oracles → {oracle_dir}")
        queries: dict[str, str] = {}
        for s in scenarios:
            if s.name not in requested:
                continue
            examples = s.load_examples(n=n_examples, seed=42)
            if len(examples) < 2:
                print(f"  skip  {s.name}  (need ≥ 2 examples, got {len(examples)})")
                continue
            queries[s.name] = examples[0]["task_input"]
            build_oracle_from_examples(oracle_dir, s.name, examples[1:], overwrite)

        # Phase 2 — build recommender and route each query
        print("\nBuilding recommender …")
        rec = build_recommender(oracle_dir=oracle_dir, variant="baseline",
                                embedder_method="tfidf")
        print(f"  Rows    : {rec.n_examples}")
        print(f"  Skills  : {rec.skills}")
        print(f"  Metrics : {rec.metrics}")

        correct = total = 0
        loaded_skills = set(rec.skills)

        for s in scenarios:
            query = queries.get(s.name)
            if query is None or s.name not in loaded_skills:
                continue
            results = rec.recommend(query=query, sim_threshold=sim_threshold,
                                    score_threshold=score_threshold, top_k=top_k)
            _print_benchmark_results(results, query, s.name)
            is_hit = bool(results and results[0]["skill"] == s.name)
            if is_hit:
                correct += 1
            total += 1

        if total:
            print(f"\n  Routing accuracy: {correct}/{total} queries routed to expected skill")
