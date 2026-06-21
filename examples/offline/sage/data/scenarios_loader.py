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
    gaia              — Real-world QA requiring multi-step reasoning to exact short answer
                        ★ Low baseline: ~0.10-0.25  (text-only subset; gated HF dataset —
                          accept terms at huggingface.co/datasets/gaia-benchmark/GAIA and
                          run ``huggingface-cli login`` before first use)
"""
from __future__ import annotations

from typing import Dict, List

from .hf.aquarat import load_scenario as load_scenario_aquarat
from .hf.aquarat import get_scenario_name as get_scenario_name_aquarat
from .hf.bbh import load_scenario as load_scenario_bbh
from .hf.bbh import get_scenario_name as get_scenario_name_bbh
from .hf.pubmedqa import load_scenario as load_scenario_pubmedqa
from .hf.pubmedqa import get_scenario_name as get_scenario_name_pubmedqa
from .hf.hotpotqa import load_scenario as load_scenario_hotpotqa
from .hf.hotpotqa import get_scenario_name as get_scenario_name_hotpotqa
from .hf.gsm8k import load_scenario as load_scenario_gsm8k
from .hf.gsm8k import get_scenario_name as get_scenario_name_gsm8k
from .hf.gaia import load_scenario as load_scenario_gaia
from .hf.gaia import get_scenario_name as get_scenario_name_gaia
from .synthetic.smarthub_support import load_scenario as load_scenario_smarthub_support
from .synthetic.smarthub_support import get_scenario_name as get_scenario_name_smarthub_support
from .synthetic.blades_in_the_dark import load_scenario as load_scenario_blades_in_the_dark
from .synthetic.blades_in_the_dark import get_scenario_name as get_scenario_name_blades_in_the_dark
from .synthetic.pokemon_player import load_scenario as load_scenario_pokemon_player
from .synthetic.pokemon_player import get_scenario_name as get_scenario_name_pokemon_player
from .synthetic.contract_review import load_scenario as load_scenario_contract_review
from .synthetic.contract_review import get_scenario_name as get_scenario_name_contract_review
from .synthetic.paper_review import load_scenario as load_scenario_paper_review
from .synthetic.paper_review import get_scenario_name as get_scenario_name_paper_review
from .synthetic.rtos_review import load_scenario as load_scenario_rtos_review
from .synthetic.rtos_review import get_scenario_name as get_scenario_name_rtos_review
from .synthetic.ml_review import load_scenario as load_scenario_ml_review
from .synthetic.ml_review import get_scenario_name as get_scenario_name_ml_review
from .synthetic.api_security import load_scenario as load_scenario_api_security
from .synthetic.api_security import get_scenario_name as get_scenario_name_api_security
from .synthetic.code_review import load_scenario as load_scenario_code_review
from .synthetic.code_review import get_scenario_name as get_scenario_name_code_review

from .scenario import Scenario


def _load_scenarios() -> Dict[str, Scenario]:
    return {
        get_scenario_name_code_review(): load_scenario_code_review(),
        get_scenario_name_api_security(): load_scenario_api_security(),
        get_scenario_name_ml_review(): load_scenario_ml_review(),
        get_scenario_name_rtos_review(): load_scenario_rtos_review(),
        get_scenario_name_paper_review(): load_scenario_paper_review(),
        get_scenario_name_contract_review(): load_scenario_contract_review(),
        get_scenario_name_pokemon_player(): load_scenario_pokemon_player(),
        get_scenario_name_blades_in_the_dark(): load_scenario_blades_in_the_dark(),
        get_scenario_name_smarthub_support(): load_scenario_smarthub_support(),
        get_scenario_name_gsm8k(): load_scenario_gsm8k(),
        get_scenario_name_hotpotqa(): load_scenario_hotpotqa(),
        get_scenario_name_pubmedqa():load_scenario_pubmedqa(),
        get_scenario_name_aquarat():load_scenario_aquarat(),
        get_scenario_name_gaia(): load_scenario_gaia(),
        get_scenario_name_bbh(): load_scenario_bbh(),
    }
