from ...scenario import Scenario
from .bbh_loader import load_bbh_to_oracle, DEFAULT_TASKS


def load_scenario():
    return Scenario(
            name="bbh",
            skill_body="",
            skill_frontmatter="",
            golden_examples=[],
            description="Big-Bench Hard — diverse reasoning tasks (multi-task oracle benchmark, no single skill)",
            oracle_builder=lambda d, n, ow: load_bbh_to_oracle(d, tasks=DEFAULT_TASKS, n_examples=n, overwrite=ow),
            oracle_skill_name=None,  # multi-task: any loaded bbh skill counts as a hit
            sample_query="Sort the following words in alphabetical order: zebra mango apple pineapple cherry",
        )

def get_scenario_name():
    return "bbh"
