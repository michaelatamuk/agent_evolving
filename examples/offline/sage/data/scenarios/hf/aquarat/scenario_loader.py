from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .hf_loader import load


def load_scenario():
    return Scenario(
            name=get_scenario_name(),
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            golden_examples=[],
            description="AQuA-RAT algebra word problems — full working + correct option letter (OPRO benchmark)",
            loader=load,
            sample_query=(
                "If the price of a book is increased by 20% and then decreased by 10%, "
                "what is the net percentage change in the price? "
                "Options:\nA) 8% increase\nB) 10% decrease\nC) 8% decrease\nD) 10% increase\nE) No change"
            ),
        )

def get_scenario_name():
    return "aquarat"
