# coding: utf-8
"""Example 5 — Thompson Sampling vs baseline GEPA: a side-by-side comparison.

Goal
----
Show concretely what each Thompson Sampling level adds to GEPA by running
the *same* skill through up to four independent evolution passes and printing
a comparison table.  The baseline skill is always evaluated on holdout first
(before any training), so the gap is unambiguous.

    ⓪ Baseline holdout eval (no training)
    ──► GEPA-Uniform  ──► L2 only  ──► L3 only  ──► GEPA-Full

  GEPA-Uniform  : plain GEPA, all training examples, threshold acceptance gate
  L2 only: TS Example Selector — focuses budget on hard/discriminating examples
  L3 only: TS Acceptance Gate  — requires P(candidate > deployed) ≥ 0.75
  GEPA-Full  : both TS levels active simultaneously

Configuration
-------------
All settings live in ``config.json`` next to this file.  Edit it to change
scenarios, model, API key, GEPA iterations, or run modes — no code changes needed.

  "scenarios"    — list of scenario names to run back-to-back
  "run_modes"    — which passes to run: any subset of
                   ["gepa_plain_holistic", "gepa_plain_rubrics", "gepa_focused_on_difficulty", "gepa_gated", "gepa_full"], or [] for
                   baseline eval only (no GEPA training)
  "model"        — DSPy model string (e.g. "deepseek/deepseek-chat")
  "api_key"      — overridden by DEEPSEEK_API_KEY env var if set
  "api_base"     — provider base URL
  "iterations"   — GEPA iterations per training pass
  "ts_batch_size"— TS example-selector batch size
  "verbose"      — true / false
  "print_skill_diff" — true / false (default false)
                   After the comparison table, print the baseline skill and the
                   winner skill side by side so GEPA's changes are easy to read.

Available scenarios
-------------------
  "paper-review"    ★ RECOMMENDED (non-software) — Research paper methodology review
                    Baseline skill: generic writing/clarity check
                    Hard examples: HARKing, p-hacking, optional stopping, measurement
                    invariance, common method variance, equivalence testing errors
                    Expected baseline: ~0.10–0.20  →  evolved: ~0.55–0.75

  "contract-review" ★ RECOMMENDED (non-software, non-technical) — Commercial contract review
                    Baseline skill: structural/completeness checker only
                    Hard examples: liquidated damages as penalty, force majeure ejusdem
                    generis trap, uncapped IP indemnification, anti-assignment without
                    change-of-control carve-out, auto-renewal trap, UCC warranty
                    disclaimer gap, overbroad non-compete, one-sided indemnification
                    Expected baseline: ~0.05–0.15  →  evolved: ~0.50–0.70

  "rtos-review"     ★ RECOMMENDED (software) — Embedded C / FreeRTOS code review
                    Baseline skill: generic C review (null checks, buffer overflows)
                    Hard examples: malloc in ISR, volatile-missing MMIO, mutex in ISR,
                    xQueueSend portMAX_DELAY in ISR, 64-bit torn MMIO read, DSB barrier
                    Expected baseline: ~0.10–0.20  →  evolved: ~0.60–0.75

  "ml-review"       ML / data-science code review (data leakage, CV strategy)
                    Expected baseline: ~0.25–0.35  →  evolved: ~0.65–0.80

  "api-security"    REST API security review (auth, injection, SSRF, crypto)
                    Note: LLM already knows this domain; baseline is ~0.78

  "code-review"     Python code review (bugs, style, performance, security)
                    Note: baseline is already high; limited training improvement

Model
-----
Uses DeepSeek-Chat (https://api.deepseek.com) by default.  Set your key in
``config.json`` or via the environment:

    export DEEPSEEK_API_KEY=sk-...

Usage
-----
    python -m examples.offline.sage.runner
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from examples.offline.sage.config_loader import load_config
from examples.offline.sage.demo.demo import Demo
from examples.offline.sage.demo.demo_params import DemoParams
from examples.offline.sage.data import Scenario, get_scenario

if __name__ == "__main__":
    # ── Load config from config.json ──────────────────────────────────────────
    config = load_config()

    demo = Demo(config)

    # ── Print run summary ─────────────────────────────────────────────────────
    modes_str = ", ".join(config.run_modes) if config.run_modes else "baseline eval only (no training)"
    # print(f"\nRun modes         : {modes_str}")
    # print("\nAvailable scenarios:")
    # for s in list_scenarios():
    #     marker = "→" if s.name in config.scenario_names else " "
    #     print(f"  {marker} {s.summary_line()}")
    # print()

    # ── Run each scenario ─────────────────────────────────────────────────────
    for scenario_name in config.scenario_names:
        scenario: Scenario = get_scenario(scenario_name)
        counts = scenario.example_counts()
        workdir = Path(tempfile.mkdtemp(prefix=f"gepa_ts_{scenario.name}_"))

        params = DemoParams(
            skill_name=scenario.name,
            skill_body=scenario.skill_body,
            skill_frontmatter=scenario.skill_frontmatter,
            golden_examples=scenario.golden_examples,
            workdir=workdir,
        )

        print(f"{'═' * 70}")
        print(f"Scenario          : {scenario.name}  —  {scenario.description}")
        print(f"Working directory : {workdir}")
        print(f"Golden examples   : {len(scenario.golden_examples)}  "
              f"({counts.get('easy', 0)} easy / "
              f"{counts.get('medium', 0)} medium / "
              f"{counts.get('hard', 0)} hard)")
        print()

        demo.run(params)
        print()
