from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .hf_loader import load


def load_scenario():
    return Scenario(
            name=get_scenario_name(),
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            description="PubMedQA biomedical QA — yes/no/maybe verdict with evidence (SkillGen benchmark)",
            loader=load,
            sample_query=(
                "Does regular physical exercise reduce the risk of type 2 diabetes "
                "in adults with pre-diabetic conditions?"
            ),
        )

def get_scenario_name():
    return "pubmedqa"
