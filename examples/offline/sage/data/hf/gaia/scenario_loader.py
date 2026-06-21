from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .data_loader import load


def load_scenario() -> Scenario:
    return Scenario(
        name=get_scenario_name(),
        skill_body=SKILL_BODY,
        skill_frontmatter=SKILL_FRONTMATTER,
        description=(
            "GAIA real-world QA — multi-step reasoning to exact short answer "
            "(text-only subset; Level 1=easy, 2=medium, 3=hard)"
        ),
        loader=load,
    )


def get_scenario_name() -> str:
    return "gaia"
