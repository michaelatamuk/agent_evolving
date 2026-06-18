from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .golden_examples.all import GOLDEN_EXAMPLES


def load_scenario():
    return Scenario(
            name="blades-in-the-dark",
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            golden_examples=GOLDEN_EXAMPLES,
            description="Blades in the Dark GM facilitation — D&D baseline primes systematically wrong answers for BitD mechanics",
        )

def get_scenario_name():
    return "blades-in-the-dark"
