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

from examples.offline.sage.data import Scenario
from examples.offline.sage.data.scenarios.hf.gsm8k.gsm8k_loader import (
    load_gsm8k_to_oracle as _gsm8k_oracle,
    SKILL_NAME as _GSIM8K_SKILL_NAME,
)
from examples.offline.sage.data.scenarios.hf.hotpotqa.hotpotqa_loader import (
    load_hotpotqa_to_oracle as _hp_oracle,
    SKILL_NAME as _HP_SKILL_NAME,
)
from examples.offline.sage.data.scenarios.hf.pubmedqa.pubmedqa_loader import (
    load_pubmedqa_to_oracle as _pm_oracle,
    SKILL_NAME as _PM_SKILL_NAME,
)
from examples.offline.sage.data.scenarios.hf.aquarat.aquarat_loader import (
    load_aquarat_to_oracle as _aq_oracle,
    SKILL_NAME as _AQ_SKILL_NAME,
)
from examples.offline.sage.data.scenarios.hf.bbh.bbh_loader import (
    load_bbh_to_oracle as _bbh_oracle,
    DEFAULT_TASKS as _BBH_DEFAULT_TASKS,
)


def _load_scenarios() -> Dict[str, Scenario]:
    """Import each scenario lazily so missing dependencies don't break others."""
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
    from examples.offline.sage.data.scenarios.hf.gsm8k.skill.body import \
        SKILL_BODY as _GS_BODY
    from examples.offline.sage.data.scenarios.hf.gsm8k.skill.frontmatter import \
        SKILL_FRONTMATTER as _GS_FM
    from examples.offline.sage.data.scenarios.hf.hotpotqa.skill.body import \
        SKILL_BODY as _HP_BODY
    from examples.offline.sage.data.scenarios.hf.hotpotqa.skill.frontmatter import \
        SKILL_FRONTMATTER as _HP_FM
    from examples.offline.sage.data.scenarios.hf.pubmedqa.skill.body import \
        SKILL_BODY as _PM_BODY
    from examples.offline.sage.data.scenarios.hf.pubmedqa.skill.frontmatter import \
        SKILL_FRONTMATTER as _PM_FM
    from examples.offline.sage.data.scenarios.hf.aquarat.skill.body import \
        SKILL_BODY as _AQ_BODY
    from examples.offline.sage.data.scenarios.hf.aquarat.skill.frontmatter import \
        SKILL_FRONTMATTER as _AQ_FM
    from examples.offline.sage.data.scenarios.hf.gsm8k.golden_examples.hf_loader import \
        load as _GS_LOADER
    from examples.offline.sage.data.scenarios.hf.hotpotqa.golden_examples.hf_loader import \
        load as _HP_LOADER
    from examples.offline.sage.data.scenarios.hf.pubmedqa.golden_examples.hf_loader import \
        load as _PM_LOADER
    from examples.offline.sage.data.scenarios.hf.aquarat.golden_examples.hf_loader import \
        load as _AQ_LOADER

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
        "gsm8k": Scenario(
            name="gsm8k",
            skill_body=_GS_BODY,
            skill_frontmatter=_GS_FM,
            golden_examples=[],
            description="GSM8K grade-school math — step-by-step reasoning chain (OPRO, DSPy benchmark)",
            loader=_GS_LOADER,
            oracle_builder=lambda d, n, ow: _gsm8k_oracle(d, n_examples=n, overwrite=ow),
            oracle_skill_name=_GSIM8K_SKILL_NAME,
            sample_query=(
                "A baker made 48 cookies and packed them into boxes of 6. "
                "He sold 5 boxes. How many cookies does he have left?"
            ),
        ),
        "hotpotqa": Scenario(
            name="hotpotqa",
            skill_body=_HP_BODY,
            skill_frontmatter=_HP_FM,
            golden_examples=[],
            description="HotPotQA multi-hop QA — chain-of-thought over two supporting facts (DSPy benchmark)",
            loader=_HP_LOADER,
            oracle_builder=lambda d, n, ow: _hp_oracle(d, n_examples=n, overwrite=ow),
            oracle_skill_name=_HP_SKILL_NAME,
            sample_query=(
                "Who was the lead singer of the band that performed the theme song "
                "for the 1995 James Bond film?"
            ),
        ),
        "pubmedqa": Scenario(
            name="pubmedqa",
            skill_body=_PM_BODY,
            skill_frontmatter=_PM_FM,
            golden_examples=[],
            description="PubMedQA biomedical QA — yes/no/maybe verdict with evidence (SkillGen benchmark)",
            loader=_PM_LOADER,
            oracle_builder=lambda d, n, ow: _pm_oracle(d, n_examples=n, overwrite=ow),
            oracle_skill_name=_PM_SKILL_NAME,
            sample_query=(
                "Does regular physical exercise reduce the risk of type 2 diabetes "
                "in adults with pre-diabetic conditions?"
            ),
        ),
        "aquarat": Scenario(
            name="aquarat",
            skill_body=_AQ_BODY,
            skill_frontmatter=_AQ_FM,
            golden_examples=[],
            description="AQuA-RAT algebra word problems — full working + correct option letter (OPRO benchmark)",
            loader=_AQ_LOADER,
            oracle_builder=lambda d, n, ow: _aq_oracle(d, n_examples=n, overwrite=ow),
            oracle_skill_name=_AQ_SKILL_NAME,
            sample_query=(
                "If the price of a book is increased by 20% and then decreased by 10%, "
                "what is the net percentage change in the price? "
                "Options:\nA) 8% increase\nB) 10% decrease\nC) 8% decrease\nD) 10% increase\nE) No change"
            ),
        ),
        "bbh": Scenario(
            name="bbh",
            skill_body="",
            skill_frontmatter="",
            golden_examples=[],
            description="Big-Bench Hard — diverse reasoning tasks (multi-task oracle benchmark, no single skill)",
            oracle_builder=lambda d, n, ow: _bbh_oracle(d, tasks=_BBH_DEFAULT_TASKS, n_examples=n, overwrite=ow),
            oracle_skill_name=None,  # multi-task: any loaded bbh skill counts as a hit
            sample_query="Sort the following words in alphabetical order: zebra mango apple pineapple cherry",
        ),
    }


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
