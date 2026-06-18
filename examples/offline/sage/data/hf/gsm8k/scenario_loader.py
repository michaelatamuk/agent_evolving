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
            description="GSM8K grade-school math — step-by-step reasoning chain (OPRO, DSPy benchmark)",
            loader=load,
            sample_query=(
                "A baker made 48 cookies and packed them into boxes of 6. "
                "He sold 5 boxes. How many cookies does he have left?"
            ),
        )

def get_scenario_name():
    return "gsm8k"
