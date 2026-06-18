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

  BENCHMARK MODE  (--benchmarks [NAME ...])
  ──────────────────────────────────────────
  Builds a scoring matrix from scenario examples and shows routing accuracy.
  Works with any scenario that has an oracle_builder — both synthetic (no
  network) and HuggingFace benchmarks.

      python runner.py --benchmarks                          # all scenarios
      python runner.py --benchmarks smarthub-support code-review  # no network
      python runner.py --benchmarks gsm8k hotpotqa          # HF download
      python runner.py --benchmarks bbh --oracle-dir /tmp/bbh_oracle

  Available: any name from list_scenarios() with oracle_builder set.

Common options
──────────────
  --data-dir PATH        Scoring-matrix directory  [default: ~/.openjiuwen/oracle]
  --oracle-dir PATH      Alias for --data-dir (accepted in all modes)
  --variant              baseline | evolved | both  [default: baseline]
  --embedder             tfidf | openai  [default: tfidf]
  --sim-threshold FLOAT  [default: 0.25 / 0.08 in benchmark mode]
  --score-threshold FLOAT[default: 0.20 / 0.08 in benchmark mode]
  --top-k N              [default: 10 / 3 in benchmark mode]

Benchmark-only options
──────────────────────
  --n-examples N         Examples per benchmark to download  [default: 30]
  --overwrite            Re-download even if JSON files already exist

Query-only options
──────────────────
  --cache-embedder PATH  Cache fitted TF-IDF embedder (load if exists, save otherwise)
  --min-examples N       Min similar examples required  [default: 1]

Run as module
─────────────
  python -m skill_recommender [ARGS]
"""
from __future__ import annotations

from examples.offline.sage.skill_recommender.runner_args import args_parser, DEFAULT_ORACLE_DIR
from examples.offline.sage.skill_recommender.runner_benchmarks import _run_benchmarks
from examples.offline.sage.skill_recommender.runner_query import _run_query


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    args = args_parser()

    if args.benchmarks is not None:
        _run_benchmarks(args, DEFAULT_ORACLE_DIR)
    else:
        _run_query(args)


if __name__ == "__main__":
    main()
