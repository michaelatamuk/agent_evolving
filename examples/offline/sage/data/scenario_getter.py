# coding: utf-8
"""
Usage
-----
    from scenarios.scenario import get_scenario

    scenario = get_scenario("api-security")
    run_demo(..., scenario=scenario)

Available scenarios
-------------------
    code-review       — Python code review (bugs, style, performance, security)
    api-security      — REST API security review (auth, injection, SSRF, crypto)
    ml-review         — ML/data-science code review (data leakage, CV strategy, metrics)
    rtos-review       — Embedded C / FreeRTOS review (ISR safety, volatile, stack, barriers)
                        ★ Low baseline: ~0.10-0.20
    paper-review      — Research paper peer review (HARKing, p-hacking, power, effect size)
                        ★ Low baseline: ~0.10-0.20 (non-software, recommended for demos)
    contract-review   — Commercial contract review (penalties, force majeure, IP, non-compete)
                        ★ Low baseline: ~0.05-0.15 (non-software, non-technical)
    pokemon-player    — Pokemon Red/Blue/Yellow gameplay decisions (non-code, game domain)
                        ★ Low baseline: ~0.10-0.25 (hard examples test exact operational
                          values only in the skill: API endpoints, action names, port 9876,
                          screenshot path, PKM memory prefixes, tunnel setup, batch size)
    blades-in-the-dark — BitD TTRPG GM facilitation; D&D 5e baseline primes wrong answers
                        ★ Low baseline: ~0.05-0.15 (Flashback, Engagement Roll, Devil's
                          Bargain, Harm levels, Heat/Entanglements, Fortune Roll, Vice,
                          Trauma — all incompatible with D&D d20/HP/Long-Rest framework)
    smarthub-support  — Customer support for SmartHub networking device; generic baseline
                        ★ Low baseline: ~0.05-0.20 (hard examples require exact invented
                          product facts: firmware 3.2.1 MAC bug, error E-7734, serial
                          prefix SH2-B escalation, LED 3-red-blink overtemp, rollback path,
                          ports 8443/8080, XR-500 DMZ fix, Gen 2/3 cross-flash risk)
                        ★ EXECUTIVE DEMO SCENARIO — before/after answer delta is immediately
                          readable by non-technical audiences; no domain expertise required

Benchmark scenarios (from skill-improvement papers)
----------------------------------------------------
    gsm8k             — Grade-school math word problems with step-by-step reasoning chain
                        ★ Low baseline: ~0.10-0.20  (OPRO arXiv:2309.03409, DSPy arXiv:2310.03714)
    hotpotqa          — Multi-hop QA requiring two supporting facts to answer correctly
                        ★ Low baseline: ~0.10-0.25  (DSPy arXiv:2310.03714)
    pubmedqa          — Biomedical yes/no/maybe with concise evidence sentence
                        ★ Low baseline: ~0.10-0.25  (SkillGen arXiv:2605.10999)
    aquarat           — Algebra word problems with full working + lettered option selection
                        ★ Low baseline: ~0.05-0.15  (OPRO arXiv:2309.03409)
"""
from __future__ import annotations

from typing import Dict, List

from .scenario import Scenario
from .scenarios_loader import _load_scenarios


def get_scenario(name: str) -> Scenario:
    """Return the Scenario for *name*, raising ValueError if unknown."""
    registry = _load_scenarios()
    if name not in registry:
        available = ", ".join(f'"{k}"' for k in sorted(registry))
        raise ValueError(
            f"Unknown scenario {name!r}. Available scenarios: {available}"
        )
    return registry[name]


def list_scenarios() -> List[Scenario]:
    """Return all registered scenarios sorted by name."""
    return sorted(_load_scenarios().values(), key=lambda s: s.name)
