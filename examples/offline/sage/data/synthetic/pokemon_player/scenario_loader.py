from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .golden_examples.all import GOLDEN_EXAMPLES


def load_scenario():
    return Scenario(
            name=get_scenario_name(),
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            description="Pokemon Red/Blue/Yellow gameplay — operational procedure recall (API, actions, paths, prefixes)",
            loader=lambda n, seed: GOLDEN_EXAMPLES,
        )


def get_scenario_name():
    return "pokemon-player"
