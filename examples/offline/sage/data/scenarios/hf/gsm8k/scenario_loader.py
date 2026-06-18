from ...scenario import Scenario
from .skill.body import SKILL_BODY
from .skill.frontmatter import SKILL_FRONTMATTER
from .hf_loader import load
from .gsm8k_loader import load_gsm8k_to_oracle, SKILL_NAME


def load_scenario():
    return Scenario(
            name="gsm8k",
            skill_body=SKILL_BODY,
            skill_frontmatter=SKILL_FRONTMATTER,
            golden_examples=[],
            description="GSM8K grade-school math — step-by-step reasoning chain (OPRO, DSPy benchmark)",
            loader=load,
            oracle_builder=lambda d, n, ow: load_gsm8k_to_oracle(d, n_examples=n, overwrite=ow),
            oracle_skill_name=SKILL_NAME,
            sample_query=(
                "A baker made 48 cookies and packed them into boxes of 6. "
                "He sold 5 boxes. How many cookies does he have left?"
            ),
        )

def get_scenario_name():
    return "gsm8k"
