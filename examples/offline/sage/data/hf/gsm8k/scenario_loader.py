from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .data_loader import load


def load_scenario():
    return Scenario(
            name=get_scenario_name(),
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            description="GSM8K grade-school math — step-by-step reasoning chain (OPRO, DSPy benchmark)",
            loader=load,
        )

def get_scenario_name():
    return "gsm8k"
