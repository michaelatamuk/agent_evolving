from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .hf_loader import load


def load_scenario():
    return Scenario(
            name=get_scenario_name(),
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            description="HotPotQA multi-hop QA — chain-of-thought over two supporting facts (DSPy benchmark)",
            loader=load,
            sample_query=(
                "Who was the lead singer of the band that performed the theme song "
                "for the 1995 James Bond film?"
            ),
        )

def get_scenario_name():
    return "hotpotqa"
