#!/usr/bin/env python3
# coding: utf-8
"""
runner.py — Skill Recommender  (single entry point)

Two modes selected by flags:

  QUERY MODE  (default — no mode flag)
  ─────────────────────────────────────
  Given a prompt, finds similar examples in the scoring matrix and recommends
  skills and their best-performing fitness metrics.

      python runner.py "How do I reset my SmartHub?"
      echo "Explain invoice terms" | python runner.py -
      python runner.py --from-file queries.txt
      python runner.py --list-skills
      python runner.py "some prompt" --cache-embedder /tmp/emb.pkl

  SELF-TEST MODE  (--self-test [NAME ...])
  ─────────────────────────────────────────
  Builds a scoring matrix from scenario examples and shows routing accuracy.
  Works with any scenario that has a loader (all except bbh).

      python runner.py --self-test                               # all scenarios
      python runner.py --self-test smarthub-support code-review  # synthetic only
      python runner.py --self-test gsm8k hotpotqa               # HF download

  Available: any name from list_scenarios() with a loader (all except bbh).

Common options
──────────────
  --data-dir PATH        Scoring-matrix directory  [default: ~/.openjiuwen/oracle]
  --oracle-dir PATH      Alias for --data-dir (accepted in all modes)
  --variant              baseline | evolved | both  [default: baseline]
  --embedder             tfidf | openai  [default: tfidf]
  --sim-threshold FLOAT  [default: 0.25 / 0.08 in self-test mode]
  --score-threshold FLOAT[default: 0.20 / 0.08 in self-test mode]
  --top-k N              [default: 10 / 3 in self-test mode]

Self-test-only options
──────────────────────
  --n-examples N         Examples per scenario to load  [default: 30]
  --overwrite            Re-build even if JSON files already exist

Query-only options
──────────────────
  --cache-embedder PATH  Cache fitted TF-IDF embedder (load if exists, save otherwise)
  --min-examples N       Min similar examples required  [default: 1]

Run as module
─────────────
  python -m skill_recommender [ARGS]
"""
from __future__ import annotations

from pathlib import Path

from examples.offline.sage.skill_recommender.runner_args import args_parser
from examples.offline.sage.skill_recommender.self_test.mode_runner import _run_self_test
from examples.offline.sage.skill_recommender.query.mode_runner import _run_query

DEFAULT_ORACLE_DIR  = Path("~/.openjiuwen/oracle").expanduser()

# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = args_parser(DEFAULT_ORACLE_DIR)

    if args.self_test is not None:
        _run_self_test(args, DEFAULT_ORACLE_DIR)
    else:
        _run_query(args)
