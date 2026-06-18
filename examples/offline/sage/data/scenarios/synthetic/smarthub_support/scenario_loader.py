from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .golden_examples.all import GOLDEN_EXAMPLES



def load_scenario():
    return Scenario(
            name="smarthub-support",
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            golden_examples=GOLDEN_EXAMPLES,
            description="SmartHub customer support — generic baseline vs product-specific knowledge (exec demo scenario)",
        )

def get_scenario_name():
    return "smarthub-support"
