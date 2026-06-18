from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .golden_examples.all import GOLDEN_EXAMPLES



def load_scenario():
    return Scenario(
            name="contract-review",
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            golden_examples=GOLDEN_EXAMPLES,
            description="Commercial contract review — penalties, force majeure, IP, non-compete",
        )

def get_scenario_name():
    return "contract-review"
