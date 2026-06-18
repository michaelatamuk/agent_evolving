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

from data.scenarios.hf.aquarat.scenario_loader import load_scenario as load_scenario_aquarat
from data.scenarios.hf.aquarat.scenario_loader import get_scenario_name as get_scenario_name_aquarat
from data.scenarios.hf.bbh.scenario_loader import load_scenario as load_scenario_bbh
from data.scenarios.hf.bbh.scenario_loader import get_scenario_name as get_scenario_name_bbh
from data.scenarios.hf.pubmedqa.scenario_loader import load_scenario as load_scenario_pubmedqa
from data.scenarios.hf.pubmedqa.scenario_loader import get_scenario_name as get_scenario_name_pubmedqa
from data.scenarios.hf.hotpotqa.scenario_loader import load_scenario as load_scenario_hotpotqa
from data.scenarios.hf.hotpotqa.scenario_loader import get_scenario_name as get_scenario_name_hotpotqa
from data.scenarios.hf.gsm8k.scenario_loader import load_scenario as load_scenario_gsm8k
from data.scenarios.hf.gsm8k.scenario_loader import get_scenario_name as get_scenario_name_gsm8k
from examples.offline.sage.data import Scenario

from examples.offline.sage.data.scenarios.synthetic.code_review.skill.body import \
    SKILL_BODY as _CR_BODY
from examples.offline.sage.data.scenarios.synthetic.code_review.skill.frontmatter import \
    SKILL_FRONTMATTER as _CR_FM
from examples.offline.sage.data.scenarios.synthetic.code_review.golden_examples.all import \
    GOLDEN_EXAMPLES as _CR_EXAMPLES
from examples.offline.sage.data.scenarios.synthetic.api_security.skill.body import \
    SKILL_BODY as _AS_BODY
from examples.offline.sage.data.scenarios.synthetic.api_security.skill.frontmatter import \
    SKILL_FRONTMATTER as _AS_FM
from examples.offline.sage.data.scenarios.synthetic.api_security.golden_examples.all import \
    GOLDEN_EXAMPLES as _AS_EXAMPLES
from examples.offline.sage.data.scenarios.synthetic.ml_review.skill.body import \
    SKILL_BODY as _ML_BODY
from examples.offline.sage.data.scenarios.synthetic.ml_review.skill.frontmatter import \
    SKILL_FRONTMATTER as _ML_FM
from examples.offline.sage.data.scenarios.synthetic.ml_review.golden_examples.all import \
    GOLDEN_EXAMPLES as _ML_EXAMPLES
from examples.offline.sage.data.scenarios.synthetic.rtos_review.skill.body import \
    SKILL_BODY as _RT_BODY
from examples.offline.sage.data.scenarios.synthetic.rtos_review.skill.frontmatter import \
    SKILL_FRONTMATTER as _RT_FM
from examples.offline.sage.data.scenarios.synthetic.rtos_review.golden_examples.all import \
    GOLDEN_EXAMPLES as _RT_EXAMPLES
from examples.offline.sage.data.scenarios.synthetic.paper_review.skill.body import \
    SKILL_BODY as _PR_BODY
from examples.offline.sage.data.scenarios.synthetic.paper_review.skill.frontmatter import \
    SKILL_FRONTMATTER as _PR_FM
from examples.offline.sage.data.scenarios.synthetic.paper_review.golden_examples.all import \
    GOLDEN_EXAMPLES as _PR_EXAMPLES
from examples.offline.sage.data.scenarios.synthetic.contract_review.skill.body import \
    SKILL_BODY as _CT_BODY
from examples.offline.sage.data.scenarios.synthetic.contract_review.skill.frontmatter import \
    SKILL_FRONTMATTER as _CT_FM
from examples.offline.sage.data.scenarios.synthetic.contract_review.golden_examples.all import \
    GOLDEN_EXAMPLES as _CT_EXAMPLES
from examples.offline.sage.data.scenarios.synthetic.pokemon_player.skill.body import \
    SKILL_BODY as _PK_BODY
from examples.offline.sage.data.scenarios.synthetic.pokemon_player.skill.frontmatter import \
    SKILL_FRONTMATTER as _PK_FM
from examples.offline.sage.data.scenarios.synthetic.pokemon_player.golden_examples.all import \
    GOLDEN_EXAMPLES as _PK_EXAMPLES
from examples.offline.sage.data.scenarios.synthetic.blades_in_the_dark.skill.body import \
    SKILL_BODY as _BD_BODY
from examples.offline.sage.data.scenarios.synthetic.blades_in_the_dark.skill.frontmatter import \
    SKILL_FRONTMATTER as _BD_FM
from examples.offline.sage.data.scenarios.synthetic.blades_in_the_dark.golden_examples.all import \
    GOLDEN_EXAMPLES as _BD_EXAMPLES
from examples.offline.sage.data.scenarios.synthetic.smarthub_support.skill.body import \
    SKILL_BODY as _SH_BODY
from examples.offline.sage.data.scenarios.synthetic.smarthub_support.skill.frontmatter import \
    SKILL_FRONTMATTER as _SH_FM
from examples.offline.sage.data.scenarios.synthetic.smarthub_support.golden_examples.all import \
    GOLDEN_EXAMPLES as _SH_EXAMPLES


def _load_scenarios() -> Dict[str, Scenario]:
    return {
        "code-review": Scenario(
            name="code-review",
            skill_body=_CR_BODY,
            skill_frontmatter=_CR_FM,
            golden_examples=_CR_EXAMPLES,
            description="Python code review — bugs, style, performance, security",
        ),
        "api-security": Scenario(
            name="api-security",
            skill_body=_AS_BODY,
            skill_frontmatter=_AS_FM,
            golden_examples=_AS_EXAMPLES,
            description="REST API security review — auth, injection, SSRF, crypto",
        ),
        "ml-review": Scenario(
            name="ml-review",
            skill_body=_ML_BODY,
            skill_frontmatter=_ML_FM,
            golden_examples=_ML_EXAMPLES,
            description="ML/data-science code review — data leakage, CV strategy, metrics",
        ),
        "rtos-review": Scenario(
            name="rtos-review",
            skill_body=_RT_BODY,
            skill_frontmatter=_RT_FM,
            golden_examples=_RT_EXAMPLES,
            description="Embedded C / FreeRTOS review — ISR safety, volatile, stack, barriers",
        ),
        "paper-review": Scenario(
            name="paper-review",
            skill_body=_PR_BODY,
            skill_frontmatter=_PR_FM,
            golden_examples=_PR_EXAMPLES,
            description="Research paper peer review — HARKing, p-hacking, power, effect size",
        ),
        "contract-review": Scenario(
            name="contract-review",
            skill_body=_CT_BODY,
            skill_frontmatter=_CT_FM,
            golden_examples=_CT_EXAMPLES,
            description="Commercial contract review — penalties, force majeure, IP, non-compete",
        ),
        "pokemon-player": Scenario(
            name="pokemon-player",
            skill_body=_PK_BODY,
            skill_frontmatter=_PK_FM,
            golden_examples=_PK_EXAMPLES,
            description="Pokemon Red/Blue/Yellow gameplay — operational procedure recall (API, actions, paths, prefixes)",
        ),
        "blades-in-the-dark": Scenario(
            name="blades-in-the-dark",
            skill_body=_BD_BODY,
            skill_frontmatter=_BD_FM,
            golden_examples=_BD_EXAMPLES,
            description="Blades in the Dark GM facilitation — D&D baseline primes systematically wrong answers for BitD mechanics",
        ),
        "smarthub-support": Scenario(
            name="smarthub-support",
            skill_body=_SH_BODY,
            skill_frontmatter=_SH_FM,
            golden_examples=_SH_EXAMPLES,
            description="SmartHub customer support — generic baseline vs product-specific knowledge (exec demo scenario)",
        ),
        get_scenario_name_gsm8k(): load_scenario_gsm8k(),
        get_scenario_name_hotpotqa(): load_scenario_hotpotqa(),
        get_scenario_name_pubmedqa():load_scenario_pubmedqa(),
        get_scenario_name_aquarat():load_scenario_aquarat(),
        get_scenario_name_bbh(): load_scenario_bbh(),
    }
