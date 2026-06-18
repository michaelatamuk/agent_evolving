from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .golden_examples.all import GOLDEN_EXAMPLES


def load_scenario():
    return Scenario(
            name=get_scenario_name(),
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            description="ML/data-science code review — data leakage, CV strategy, metrics",
            loader=lambda n, seed: GOLDEN_EXAMPLES,
            sample_query=GOLDEN_EXAMPLES[0]["task_input"],
        )


def get_scenario_name():
    return "ml-review"
