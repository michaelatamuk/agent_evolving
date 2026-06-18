# `sage/data` — unified data interface

`Scenario` is the single data contract.  Every client — demo, skill_recommender,
or any future client — calls `get_scenario(name)` and works with the same object,
regardless of whether the data is local/static or fetched from HuggingFace.

```python
from examples.offline.sage.data import get_scenario, list_scenarios, Scenario
```

---

## Getting a scenario

```python
from examples.offline.sage.data import get_scenario, list_scenarios

scenario = get_scenario("paper-review")

print(scenario.name)                    # "paper-review"
print(scenario.description)
print(scenario.example_counts())        # {"easy": 4, "medium": 4, "hard": 4}
print(scenario.summary_line())

for s in list_scenarios():
    print(s.summary_line())
```

**All 14 scenario names:**

| Name | Type | Domain |
|------|------|--------|
| `paper-review` | synthetic | Research paper peer review ★ recommended |
| `contract-review` | synthetic | Commercial contract review ★ recommended |
| `rtos-review` | synthetic | Embedded C / FreeRTOS ★ recommended |
| `smarthub-support` | synthetic | Customer support (exec demo) ★ recommended |
| `ml-review` | synthetic | ML/data-science code review |
| `api-security` | synthetic | REST API security review |
| `code-review` | synthetic | Python code review |
| `pokemon-player` | synthetic | Game domain (Pokemon) |
| `blades-in-the-dark` | synthetic | TTRPG GM facilitation |
| `gsm8k` | HF benchmark | Grade-school math |
| `hotpotqa` | HF benchmark | Multi-hop QA |
| `pubmedqa` | HF benchmark | Biomedical QA |
| `aquarat` | HF benchmark | Algebra word problems |
| `bbh` | HF benchmark | Big-Bench Hard (multi-task, no single skill) |

---

## Loading examples

Same call for every scenario — client does not know or care whether data is
local or from HuggingFace:

```python
# synthetic scenario: returns static golden_examples, no network needed
scenario = get_scenario("paper-review")
examples = scenario.load_examples()

# HF benchmark scenario: fetches from HuggingFace
scenario = get_scenario("gsm8k")
examples = scenario.load_examples(n=100, seed=42)
```

Each example dict:

```python
{
    "task_input":        str,   # the question / code to evaluate
    "expected_behavior": str,   # gold answer
    "difficulty":        str,   # "easy" | "medium" | "hard"
    "source":            str,   # e.g. "gsm8k-hf" or "synthetic"
}
```

> `bbh` has no loader and returns `[]` — it is a meta-benchmark with no single
> skill or unified example format.

---

## Train / val split

```python
scenario = get_scenario("paper-review")
trainset, valset = scenario.split(n=50, seed=42, train_ratio=0.8)
```

`split()` loads examples, shuffles with the given seed, and cuts at `train_ratio`.
Works identically for synthetic and HF scenarios.

---

## Skill text

The baseline skill body and frontmatter are carried on the `Scenario` and are
used to write `SKILL.md` before GEPA evolution:

```python
scenario = get_scenario("api-security")

print(scenario.skill_body)
print(scenario.skill_frontmatter)
```

> `bbh` has empty `skill_body` / `skill_frontmatter` — it is a meta-benchmark
> with no single skill.

---

## Package layout

```
data/
├── __init__.py              # re-exports Scenario, get_scenario, list_scenarios
├── scenario.py              # Scenario dataclass: load_examples, split, example_counts
├── scenario_getter.py       # get_scenario(name), list_scenarios()
├── scenarios_loader.py      # internal registry — loads all scenario modules
├── tester.py                # standalone inspector script
├── hf/                      # HuggingFace benchmark scenarios
│   ├── gsm8k/               # openai/gsm8k — grade-school math
│   ├── hotpotqa/            # hotpotqa/hotpot_qa — multi-hop QA
│   ├── pubmedqa/            # qiaojin/PubMedQA — biomedical yes/no/maybe
│   ├── aquarat/             # deepmind/aqua_rat — algebra word problems
│   └── bbh/                 # Big-Bench Hard (no loader, placeholder only)
└── synthetic/               # Hand-crafted golden example scenarios
    ├── api_security/
    ├── blades_in_the_dark/
    ├── code_review/
    ├── contract_review/
    ├── ml_review/
    ├── paper_review/
    ├── pokemon_player/
    ├── rtos_review/
    └── smarthub_support/

Each scenario directory contains:
    scenario_loader.py       load_scenario() → Scenario, get_scenario_name() → str
    skill/body.py            SKILL_BODY string
    skill/frontmatter.py     SKILL_FRONTMATTER string
    golden_examples/all.py   GOLDEN_EXAMPLES list  (synthetic only)
    data_loader.py           load(n, seed) → examples  (HF only)
```
