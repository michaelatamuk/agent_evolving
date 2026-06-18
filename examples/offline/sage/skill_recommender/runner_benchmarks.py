from __future__ import annotations

import argparse
import contextlib
import tempfile
from pathlib import Path

from .recommender import build_recommender
from .runner_printer import _print_benchmark_results


def _benchmark_scenarios():
    """Return all scenarios that support oracle building, sorted by name."""
    from ..data import list_scenarios
    return [s for s in list_scenarios() if s.oracle_builder is not None]


def _run_benchmarks(args: argparse.Namespace, DEFAULT_ORACLE_DIR) -> None:
    """Download benchmarks, build recommender, show routing accuracy."""
    scenarios       = _benchmark_scenarios()
    all_names       = [s.name for s in scenarios]
    benchmarks      = args.benchmarks if args.benchmarks else all_names
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
        ctx = tempfile.TemporaryDirectory(prefix="benchmarks_oracle_")  # type: ignore[assignment]

    with ctx as tmpdir:
        oracle_dir = Path(tmpdir)

        print(f"\nLoading benchmarks → {oracle_dir}")
        for s in scenarios:
            if s.name not in benchmarks:
                continue
            s.build_oracle(oracle_dir, n_examples, overwrite)

        print("\nBuilding recommender …")
        rec = build_recommender(oracle_dir=oracle_dir, variant="baseline",
                                embedder_method="tfidf")
        print(f"  Rows    : {rec.n_examples}")
        print(f"  Skills  : {rec.skills}")
        print(f"  Metrics : {rec.metrics}")

        loaded_skills = set(rec.skills)
        correct = total = 0

        for s in scenarios:
            if s.name not in benchmarks or s.sample_query is None:
                continue
            results = rec.recommend(query=s.sample_query, sim_threshold=sim_threshold,
                                    score_threshold=score_threshold, top_k=top_k)
            if s.oracle_skill_name is None:
                # multi-task benchmark (bbh): any loaded skill counts as a hit
                is_hit = bool(results and results[0]["skill"] in loaded_skills)
                _print_benchmark_results(results, s.sample_query, "<any bbh task>",
                                         is_hit=is_hit)
            else:
                if s.oracle_skill_name not in loaded_skills:
                    continue
                _print_benchmark_results(results, s.sample_query, s.oracle_skill_name)
                is_hit = bool(results and results[0]["skill"] == s.oracle_skill_name)
            if is_hit:
                correct += 1
            total += 1

        if total:
            print(f"\n  Routing accuracy: {correct}/{total} queries routed to expected skill")
