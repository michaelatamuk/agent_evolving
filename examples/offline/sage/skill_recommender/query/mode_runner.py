from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..recommender_builder import build_recommender
from ..skill_context_store import SkillContextStore
from ..contextual_matrix import ContextualMatrix
from .results_printer import _print_query_results, _print_skills


def _run_query(args: argparse.Namespace) -> None:
    """Production query mode — requires real GEPA scoring matrix files."""
    oracle_dir = (args.oracle_dir or args.data_dir).expanduser()
    cache_path = Path(args.cache_embedder).expanduser() if args.cache_embedder else None

    # ── Phase 1 / 2 — Bayesian + freshness ───────────────────────────────
    ts_state_path: Optional[Path] = None
    if getattr(args, "ts_state_path", None):
        ts_state_path = Path(args.ts_state_path).expanduser()

    freshness_lambda: float = getattr(args, "freshness_lambda", 0.0) or 0.0

    # ── Phase 3 — Adaptive context embeddings + online matrix ─────────────
    context_store: Optional[SkillContextStore] = None
    contextual_matrix: Optional[ContextualMatrix] = None
    ctx_dir_arg = getattr(args, "context_state_dir", None)
    if ctx_dir_arg:
        ctx_dir = Path(ctx_dir_arg).expanduser()
        ctx_dir.mkdir(parents=True, exist_ok=True)
        context_store    = SkillContextStore(state_path=ctx_dir / "context_store.json")
        contextual_matrix = ContextualMatrix(state_path=ctx_dir / "contextual_matrix.json")

    try:
        recommender = build_recommender(
            oracle_dir=oracle_dir,
            variant=args.variant,
            embedder_method=args.embedder,
            ts_state_path=ts_state_path,
            freshness_lambda=freshness_lambda,
            context_store=context_store,
            contextual_matrix=contextual_matrix,
        )
    except FileNotFoundError as exc:
        sys.exit(
            f"[ERROR] {exc}\n\n"
            "Run gepa_scoring_matrix mode first with oracle_data_dir configured."
        )
    except ValueError as exc:
        sys.exit(
            f"[ERROR] {exc}\n\n"
            "The scoring_matrix_*.json files may predate baseline_cross_eval support.\n"
            "Re-run gepa_scoring_matrix to regenerate them."
        )

    if cache_path is not None:
        from ..recommender_similarities_computer import Embedder
        if cache_path.exists():
            try:
                recommender._embedder = Embedder.load(cache_path)
                print(f"  Embedder cache   : loaded from {cache_path}")
            except Exception as exc:
                print(f"  [WARN] Could not load embedder cache ({exc}); using fresh model.")
        else:
            recommender._embedder.save(cache_path)
            print(f"  Embedder cache   : saved to {cache_path}")

    print(f"  Loaded matrix: {recommender.n_examples} rows · {len(recommender.skills)} skill(s) · "
          f"{len(recommender.metrics)} metric(s)")

    active_phases = ["Phase 0: collaborative"]
    if ts_state_path and ts_state_path.exists():
        active_phases.append("Phase 1: Bayesian")
        if freshness_lambda > 0:
            active_phases.append("Phase 2: freshness")
    if context_store is not None:
        active_phases.append("Phase 3: context")
    print(f"  Active phases: {' + '.join(active_phases)}")

    if args.list_skills:
        _print_skills(recommender)
        return

    if args.from_file is not None:
        fp = Path(args.from_file).expanduser()
        if not fp.exists():
            sys.exit(f"[ERROR] File not found: {fp}")
        queries = [l.strip() for l in fp.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not queries:
            sys.exit(f"[ERROR] File is empty: {fp}")
    elif args.query is None or args.query == "-":
        print("Enter your query (press Enter to submit):")
        try:
            # Try reading a single line first (works for live keyboard & IDEs)
            raw = sys.stdin.readline().strip()
        except Exception:
            # Fallback if standard input is completely redirected
            raw = sys.stdin.read().strip()

        if not raw:
            sys.exit("Query is empty. Provide a prompt as argument, via --from-file, or stdin.")
        queries = [raw]
    else:
        queries = [args.query.strip()]

    for query in queries:
        if not query:
            continue
        results = recommender.recommend(query=query,
                                        sim_threshold=args.sim_threshold,
                                        score_threshold=args.score_threshold,
                                        min_examples=args.min_examples,
                                        top_k=args.top_k)
        _print_query_results(results, query, args.variant)
