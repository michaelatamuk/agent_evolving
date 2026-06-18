from __future__ import annotations

import argparse
import contextlib
import tempfile
from pathlib import Path

from .oracle_builder import build_oracle_from_examples
from .results_printer import _print_benchmark_results
from ..recommender_builder import build_recommender
from ...data import list_scenarios


def _run_self_test(args: argparse.Namespace, DEFAULT_ORACLE_DIR: Path) -> None:
    """Build per-scenario oracles from load_examples(), then verify routing accuracy."""
    scenarios       = [s for s in list_scenarios() if s.sample_query is not None]
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

        print(f"\nBuilding self-test oracles → {oracle_dir}")
        for s in scenarios:
            if s.name not in requested:
                continue
            examples = s.load_examples(n=n_examples, seed=42)
            if not examples:
                print(f"  skip  {s.name}  (no examples)")
                continue
            build_oracle_from_examples(oracle_dir, s.name, examples, overwrite)

        print("\nBuilding recommender …")
        rec = build_recommender(oracle_dir=oracle_dir, variant="baseline",
                                embedder_method="tfidf")
        print(f"  Rows    : {rec.n_examples}")
        print(f"  Skills  : {rec.skills}")
        print(f"  Metrics : {rec.metrics}")

        correct = total = 0

        for s in scenarios:
            if s.name not in requested or s.name not in set(rec.skills):
                continue
            results = rec.recommend(query=s.sample_query, sim_threshold=sim_threshold,
                                    score_threshold=score_threshold, top_k=top_k)
            _print_benchmark_results(results, s.sample_query, s.name)
            is_hit = bool(results and results[0]["skill"] == s.name)
            if is_hit:
                correct += 1
            total += 1

        if total:
            print(f"\n  Routing accuracy: {correct}/{total} queries routed to expected skill")
