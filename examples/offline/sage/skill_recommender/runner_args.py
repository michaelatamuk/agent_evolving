from __future__ import annotations

import argparse
from pathlib import Path

from ..data import list_scenarios

# ── Persistent-state defaults (must match demo/config.json paths) ─────────────
# All three paths are safe defaults even when the files/dirs don't exist yet:
# the recommender activates each phase only if the corresponding file is present.
_DEFAULT_TS_STATE_PATH    = Path("~/.openjiuwen/ts_router_state/ts_skill_scheduler.json")
_DEFAULT_CONTEXT_DIR      = Path("~/.openjiuwen/context_state")
_DEFAULT_FRESHNESS_LAMBDA = 0.05   # exp decay per day; ~14-day half-life

# ── CLI ───────────────────────────────────────────────────────────────────────

def args_parser(DEFAULT_ORACLE_DIR):
    parser = argparse.ArgumentParser(prog="runner.py",
                                     description="Skill Recommender — query or self-test mode.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=__doc__,)

    # ── Mode flags ────────────────────────────────────────────────────────
    mode_group = parser.add_mutually_exclusive_group()
    _AVAILABLE = [s.name for s in list_scenarios() if s.loader is not None]
    mode_group.add_argument("--self-test",
                            nargs="*",
                            metavar="NAME",
                            default=None,
                            help=f"Build oracles from scenario examples and show routing accuracy. "
                                 f"Pass names to select a subset, or omit names for all. "
                                 f"Available: {', '.join(_AVAILABLE)}",)

    # ── Query input (query mode only) ─────────────────────────────────────
    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument("query",
                             nargs="?",
                             default=None,
                             help="Prompt to find skills for (query mode).  Pass '-' to read from stdin.",)
    query_group.add_argument("--from-file",
                             metavar="PATH",
                             type=Path,
                             default=None,
                             help="File with one query per line (query mode).")
    query_group.add_argument("--list-skills",
                             action="store_true",
                             default=False,
                             help="List all skills in the matrix and exit (query mode).",)

    # ── Shared settings ───────────────────────────────────────────────────
    parser.add_argument("--data-dir",
                        metavar="PATH",
                        type=Path,
                        default=DEFAULT_ORACLE_DIR,
                        help="Directory with scoring_matrix_*.json files  [default: ~/.openjiuwen/oracle]",)
    parser.add_argument("--oracle-dir",
                        metavar="PATH",
                        type=Path,
                        default=None,
                        help="Alias for --data-dir (accepted in all modes).",)
    parser.add_argument("--variant",
                        choices=["baseline", "evolved", "both"],
                        default="baseline",
                        help="Matrix layer to use  [default: baseline]",)
    parser.add_argument("--embedder",
                        choices=["tfidf", "openai"],
                        default="tfidf",
                        help="Embedding backend  [default: tfidf]",)
    parser.add_argument("--sim-threshold",
                        type=float,
                        default=None,
                        metavar="FLOAT",
                        help="Min cosine similarity  [default: 0.25 for query, 0.08 for self-test]",)
    parser.add_argument("--score-threshold",
                        type=float,
                        default=None,
                        metavar="FLOAT",
                        help="Min weighted score  [default: 0.20 for query, 0.08 for self-test]",)
    parser.add_argument("--top-k",
                        type=int,
                        default=None,
                        metavar="N",
                        help="Max results per query  [default: 10 for query, 3 for self-test]",)

    # ── Query-only settings ───────────────────────────────────────────────
    parser.add_argument("--min-examples",
                        type=int,
                        default=1,
                        metavar="N",
                        help="Min similar examples required (query mode)  [default: 1]",)
    parser.add_argument("--cache-embedder",
                        metavar="PATH",
                        type=Path,
                        default=None,
                        help="Cache fitted embedder path (query mode).")

    # ── Self-test-only settings ───────────────────────────────────────────
    parser.add_argument("--n-examples",
                        type=int,
                        default=30,
                        metavar="N",
                        help="Examples per scenario to load  [default: 30]",)
    parser.add_argument("--overwrite",
                        action="store_true",
                        help="Re-build even if JSON files already exist (self-test mode).",)

    # ── Contextual Bayesian Router (Phase 1 / 2 / 3) ─────────────────────
    parser.add_argument("--ts-state-path",
                        metavar="PATH",
                        type=Path,
                        default=_DEFAULT_TS_STATE_PATH,
                        help="Path to ts_skill_scheduler.json produced by the demo or offline runner. "
                             "Enables Phase 1 (Bayesian confidence) and Phase 2 (freshness) blending "
                             "when the file exists; silently ignored otherwise.  "
                             f"[default: {_DEFAULT_TS_STATE_PATH}]",)
    parser.add_argument("--freshness-lambda",
                        type=float,
                        default=_DEFAULT_FRESHNESS_LAMBDA,
                        metavar="FLOAT",
                        help="Freshness decay rate λ per day (Phase 2). "
                             "0 = disabled.  "
                             f"[default: {_DEFAULT_FRESHNESS_LAMBDA} — ~14-day half-life]",)
    parser.add_argument("--context-state-dir",
                        metavar="PATH",
                        type=Path,
                        default=_DEFAULT_CONTEXT_DIR,
                        help="Directory for context_store.json and contextual_matrix.json (Phase 3). "
                             "Created automatically on first query; starts empty if it does not exist.  "
                             f"[default: {_DEFAULT_CONTEXT_DIR}]",)

    args = parser.parse_args()

    # Apply mode-specific defaults for thresholds / top-k
    if args.self_test is not None:
        args.sim_threshold   = args.sim_threshold   or 0.08
        args.score_threshold = args.score_threshold or 0.08
        args.top_k           = args.top_k           or 3
    else:
        args.sim_threshold   = args.sim_threshold   or 0.25
        args.score_threshold = args.score_threshold or 0.20
        args.top_k           = args.top_k           or 10

    return args
