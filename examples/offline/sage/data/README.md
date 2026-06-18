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

| Name | Domain | Oracle? |
|------|--------|---------|
| `paper-review` | Research paper peer review ★ recommended | |
| `contract-review` | Commercial contract review ★ recommended | |
| `rtos-review` | Embedded C / FreeRTOS ★ recommended | |
| `smarthub-support` | Customer support (exec demo) ★ recommended | |
| `ml-review` | ML/data-science code review | |
| `api-security` | REST API security review | |
| `code-review` | Python code review | |
| `pokemon-player` | Game domain (Pokemon) | |
| `blades-in-the-dark` | TTRPG GM facilitation | |
| `gsm8k` | Grade-school math | ✓ |
| `hotpotqa` | Multi-hop QA | ✓ |
| `pubmedqa` | Biomedical QA | ✓ |
| `aquarat` | Algebra word problems | ✓ |
| `bbh` | Big-Bench Hard (multi-task) | ✓ |

---

## Loading examples

Same call for every scenario — client does not know or care whether data is
local or from HuggingFace:

```python
# local scenario: returns static golden_examples, no network needed
scenario = get_scenario("paper-review")
examples = scenario.load_examples()

# HF benchmark scenario: fetches from HuggingFace, falls back to static on failure
scenario = get_scenario("gsm8k")
examples = scenario.load_examples(n=100, seed=42)
```

Each example dict:

```python
{
    "task_input":        str,   # the question / code to evaluate
    "expected_behavior": str,   # gold answer
    "difficulty":        str,   # "easy" | "medium" | "hard"
    "source":            str,   # e.g. "gsm8k-hf"
}
```

Static examples are always available at `scenario.golden_examples` with no
network call.

---

## Building oracle files (skill_recommender)

Only benchmark scenarios (those with ✓ above) support `build_oracle`.
The call is identical regardless of which benchmark:

```python
from pathlib import Path

oracle_dir = Path("/tmp/oracle")

get_scenario("gsm8k").build_oracle(oracle_dir, n_examples=50, overwrite=False)
get_scenario("hotpotqa").build_oracle(oracle_dir, n_examples=50)
get_scenario("bbh").build_oracle(oracle_dir, n_examples=50)

# calling on a local-only scenario raises NotImplementedError
get_scenario("paper-review").build_oracle(oracle_dir)  # ← raises
```

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
> with no single skill, so it is only useful for `build_oracle`.

---

## Scoring utilities

Available directly from the scoring module (not re-exported via `data`):

```python
from examples.offline.sage.data._scoring import compute_scores, FITNESS_METRICS

print(FITNESS_METRICS)   # ["exact_match", "f1", "bag_of_words"]

scores = compute_scores(output="The answer is 18.", expected="18")
# {"exact_match": 0.0, "f1": 0.4, "bag_of_words": 0.25}
```

| Metric | Description |
|--------|-------------|
| `exact_match` | 1.0 if strings match after strip/lower, else 0.0 |
| `f1` | Token-level F1 (punctuation removed) |
| `bag_of_words` | Jaccard over token sets |

---

## Package layout

```
data/
├── __init__.py              # Scenario, get_scenario, list_scenarios only
├── _scoring.py              # compute_scores, FITNESS_METRICS
├── _benchmarks.py           # oracle builder implementations (internal)
├── io/
│   ├── writer_skill.py      # write SKILL.md to disk
│   ├── writer_golden_dataset.py   # write golden dataset splits to disk
│   └── reader_latest_evolved.py   # read latest evolved skill from output dir
├── data_loaders/            # per-benchmark HuggingFace loaders (internal)
└── scenarios/
    ├── scenario.py          # Scenario dataclass  (load_examples, build_oracle)
    ├── scenario_getter.py   # registry: get_scenario, list_scenarios
    └── <name>/
        ├── skill/body.py + frontmatter.py
        └── golden_examples/all.py  (+ easy/medium/hard + hf_loader.py for HF benchmarks)
```
