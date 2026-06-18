from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .hf_loader import load
from .pubmedqa_loader import load_pubmedqa_to_oracle, SKILL_NAME


def load_scenario():
    return Scenario(
            name=get_scenario_name(),
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            golden_examples=[],
            description="PubMedQA biomedical QA — yes/no/maybe verdict with evidence (SkillGen benchmark)",
            loader=load,
            oracle_builder=lambda d, n, ow: load_pubmedqa_to_oracle(d, n_examples=n, overwrite=ow),
            oracle_skill_name=SKILL_NAME,
            sample_query=(
                "Does regular physical exercise reduce the risk of type 2 diabetes "
                "in adults with pre-diabetic conditions?"
            ),
        )

def get_scenario_name():
    return "pubmedqa"
