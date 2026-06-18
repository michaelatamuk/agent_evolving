# `sage/data` — unified data interface

Single import point for all data operations in `sage`.
Both `demo/` and `skill_recommender/` load everything from here.

```python
from examples.offline.sage.data import (
    # scenarios
    get_scenario, list_scenarios, Scenario,
    # skill + dataset I/O
    write_skill, write_golden_dataset, read_latest_evolved,
    # scoring
    compute_scores, FITNESS_METRICS,
    # HuggingFace benchmarks
    build_oracle, fetch_benchmark_rows, fetch_benchmark_examples,
)
```

---

## Scenarios

13 built-in scenarios, each bundling a baseline skill and golden examples.

```python
from examples.offline.sage.data import get_scenario, list_scenarios

# load one scenario by name
scenario = get_scenario("paper-review")

print(scenario.name)             # "paper-review"
print(scenario.description)
print(len(scenario.golden_examples))   # static list, always available
print(scenario.example_counts())       # {"easy": 4, "medium": 4, "hard": 4}

# skill text (used to write SKILL.md)
print(scenario.skill_body)
print(scenario.skill_frontmatter)

# list all scenarios
for s in list_scenarios():
    print(s.summary_line())
```

**Available scenario names:**

| Name | Domain |
|------|--------|
| `paper-review` | Research paper peer review ★ recommended |
| `contract-review` | Commercial contract review ★ recommended |
| `rtos-review` | Embedded C / FreeRTOS ★ recommended |
| `smarthub-support` | Customer support (exec demo) ★ recommended |
| `ml-review` | ML/data-science code review |
| `api-security` | REST API security review |
| `code-review` | Python code review |
| `pokemon-player` | Game domain (Pokemon) |
| `blades-in-the-dark` | TTRPG GM facilitation |
| `gsm8k` | Grade-school math (HF benchmark) |
| `hotpotqa` | Multi-hop QA (HF benchmark) |
| `pubmedqa` | Biomedical QA (HF benchmark) |
| `aquarat` | Algebra word problems (HF benchmark) |

Benchmark scenarios (`gsm8k`, `hotpotqa`, `pubmedqa`, `aquarat`) can also
fetch examples from HuggingFace:

```python
scenario = get_scenario("gsm8k")

# uses HuggingFace (requires network); falls back to static golden_examples on failure
examples = scenario.load_examples(n=100, seed=42)
```

Each example dict has:

```python
{
    "task_input":          str,   # the question / code to evaluate
    "expected_behavior":   str,   # gold answer
    "difficulty":          str,   # "easy" | "medium" | "hard"
    "source":              str,   # e.g. "gsm8k-hf"
}
```

---

## Skill and dataset I/O

```python
from pathlib import Path
from examples.offline.sage.data import write_skill, write_golden_dataset, read_latest_evolved

skills_root = Path("/tmp/skills")

# write SKILL.md → skills_root/<name>/SKILL.md
skill_path = write_skill(skills_root, scenario.name,
                         scenario.skill_frontmatter, scenario.skill_body)

# write golden dataset → skills_root/<name>/golden_dataset/{train,val,holdout}.jsonl
# examples are shuffled and split 50 / 25 / 25
golden_dir = write_golden_dataset(skills_root, scenario.name, scenario.golden_examples)

# read the latest evolved skill produced by GEPA in output_dir
text = read_latest_evolved(output_dir, scenario.name)  # str | None
```

---

## Scoring

Three metrics available for comparing model output against expected text.

```python
from examples.offline.sage.data import compute_scores, FITNESS_METRICS

print(FITNESS_METRICS)   # ["exact_match", "f1", "bag_of_words"]

scores = compute_scores(output="The answer is 18.", expected="18")
# {"exact_match": 0.0, "f1": 0.4, "bag_of_words": 0.25}

# pick a single metric
score = compute_scores(output, expected)["f1"]
```

| Metric | Description |
|--------|-------------|
| `exact_match` | 1.0 if strings match after strip/lower, else 0.0 |
| `f1` | Token-level F1 (punctuation removed) |
| `bag_of_words` | Jaccard over token sets |

`f1` is the recommended default for most scenarios.

---

## HuggingFace benchmark oracles

Used by `skill_recommender` to build scoring-matrix oracle files.

```python
from pathlib import Path
from examples.offline.sage.data import build_oracle, fetch_benchmark_rows, fetch_benchmark_examples

oracle_dir = Path("/tmp/oracle")

# download benchmark and write oracle JSONL into oracle_dir
# supported: "gsm8k", "hotpotqa", "pubmedqa", "aquarat", "bbh"
build_oracle("gsm8k", oracle_dir, n_examples=50, overwrite=False)

# raw HuggingFace rows (field names vary per dataset)
# supported: "gsm8k", "hotpotqa", "pubmedqa", "aquarat"
rows = fetch_benchmark_rows("gsm8k", n=50, seed=42)

# GEPA-shaped dicts: task_input / expected_behavior / difficulty / source
# supported: "gsm8k", "hotpotqa", "pubmedqa", "aquarat"
examples = fetch_benchmark_examples("gsm8k", n=50, seed=42)
```

---

## Package layout

```
data/
├── __init__.py              # re-exports only — no logic
├── _scoring.py              # compute_scores, FITNESS_METRICS
├── _benchmarks.py           # build_oracle, fetch_benchmark_rows, fetch_benchmark_examples
├── io/
│   ├── writer_skill.py      # write_skill
│   ├── writer_golden_dataset.py   # write_golden_dataset
│   └── reader_latest_evolved.py   # read_latest_evolved
├── data_loaders/            # per-benchmark HuggingFace loaders (gsm8k, hotpotqa, …)
└── scenarios/
    ├── scenario.py          # Scenario dataclass + registry
    └── <name>/
        ├── skill/body.py + frontmatter.py
        └── golden_examples/all.py  (+ easy/medium/hard + hf_loader.py for benchmarks)
```
