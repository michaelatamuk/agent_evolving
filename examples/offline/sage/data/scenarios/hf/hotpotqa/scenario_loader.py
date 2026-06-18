from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .hf_loader import load
from .hotpotqa_loader import load_hotpotqa_to_oracle, SKILL_NAME


def load_scenario():
    return Scenario(
            name="hotpotqa",
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            golden_examples=[],
            description="HotPotQA multi-hop QA — chain-of-thought over two supporting facts (DSPy benchmark)",
            loader=load,
            oracle_builder=lambda d, n, ow: load_hotpotqa_to_oracle(d, n_examples=n, overwrite=ow),
            oracle_skill_name=SKILL_NAME,
            sample_query=(
                "Who was the lead singer of the band that performed the theme song "
                "for the 1995 James Bond film?"
            ),
        )

def get_scenario_name():
    return "hotpotqa"
