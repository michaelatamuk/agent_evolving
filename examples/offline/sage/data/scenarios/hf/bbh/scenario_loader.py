from ...scenario import Scenario


def load_scenario():
    return Scenario(
            name=get_scenario_name(),
            skill_body="",
            skill_frontmatter="",
            golden_examples=[],
            description="Big-Bench Hard — diverse reasoning tasks (multi-task benchmark, no single skill)",
        )

def get_scenario_name():
    return "bbh"
