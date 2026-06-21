# coding: utf-8
"""Quick data inspector — edit the CONFIG block and run with `python -m examples.offline.sage.data.tester`.

CONFIG OPTIONS
--------------
SCENARIO   : any name from list_scenarios(), e.g. "smarthub-support", "gsm8k", "pubmedqa"
N_EXAMPLES : how many examples to load (only matters for HF-backed scenarios)
SEED       : random seed for reproducible HF sampling
SHOW_SKILL : print skill frontmatter + body
MAX_EXAMPLES_SHOWN : how many examples to print in full (0 = none, None = all)
TRUNCATE   : max chars per field before truncating (None = no truncation)
"""

# ── CONFIG ─────────────────────────────────────────────────────────────────────

SCENARIO           = "gaia"   # ← change this
N_EXAMPLES         = 10000
SEED               = 42
SHOW_SKILL         = True
MAX_EXAMPLES_SHOWN = 3
TRUNCATE           = 400

# Other scenarios to try:
#   synthetic (static examples, no network):
#     "code-review"  "api-security"  "ml-review"  "rtos-review"
#     "paper-review"  "contract-review"  "pokemon-player"
#     "blades-in-the-dark"  "smarthub-support"
#
#   HF benchmark (downloads from HuggingFace, needs `pip install datasets`):
#     "gsm8k"  "hotpotqa"  "pubmedqa"  "aquarat"
#
#   Multi-task oracle only (no skill body or examples):
#     "bbh"

# ── MAIN ──────────────────────────────────────────────────────────────────────

def _trunc(text: str, limit) -> str:
    if limit is None or len(text) <= limit:
        return text
    return text[:limit] + f"  … [{len(text) - limit} more chars]"


def main():
    from examples.offline.sage.data import get_scenario, list_scenarios

    # ── Available scenarios ────────────────────────────────────────────────────
    all_names = [s.name for s in list_scenarios()]
    print(f"Available scenarios ({len(all_names)}): {', '.join(all_names)}\n")

    # ── Load scenario ──────────────────────────────────────────────────────────
    scenario = get_scenario(SCENARIO)

    print("=" * 70)
    print(f"  Scenario : {scenario.name}")
    print(f"  Desc     : {scenario.description}")
    hf_backed = scenario.loader is not None
    print(f"  Type     : {'HF benchmark' if hf_backed else 'synthetic (static)'}")
    if scenario.oracle_skill_name:
        print(f"  Skill ID : {scenario.oracle_skill_name}")
    if scenario.sample_query:
        print(f"  Sample Q : {_trunc(scenario.sample_query, 120)}")
    print("=" * 70)

    # ── Skill text ─────────────────────────────────────────────────────────────
    if SHOW_SKILL:
        print("\n── SKILL FRONTMATTER ──────────────────────────────────────────────")
        if scenario.skill_frontmatter:
            print(_trunc(scenario.skill_frontmatter.strip(), TRUNCATE))
        else:
            print("(none)")

        print("\n── SKILL BODY ─────────────────────────────────────────────────────")
        if scenario.skill_body:
            print(_trunc(scenario.skill_body.strip(), TRUNCATE))
        else:
            print("(none — multi-task oracle scenario)")

    # ── Examples ───────────────────────────────────────────────────────────────
    print(f"\n── EXAMPLES  (loading n={N_EXAMPLES}, seed={SEED}) ────────────────────")
    examples = scenario.load_examples(n=N_EXAMPLES, seed=SEED)

    if not examples:
        print("(no examples loaded)")
    else:
        # Difficulty distribution
        diff_counts: dict = {}
        for ex in examples:
            d = ex.get("difficulty", "unknown")
            diff_counts[d] = diff_counts.get(d, 0) + 1
        dist = "  ".join(f"{d}: {c}" for d, c in sorted(diff_counts.items()))
        source = examples[0].get("source", "?")
        print(f"Loaded {len(examples)} examples  |  source: {source}  |  {dist}\n")

        limit = len(examples) if MAX_EXAMPLES_SHOWN is None else MAX_EXAMPLES_SHOWN
        for i, ex in enumerate(examples[:limit]):
            print(f"  [{i+1}] difficulty={ex.get('difficulty','?')}")
            print(f"      INPUT    : {_trunc(ex.get('task_input',''), TRUNCATE)}")
            print(f"      EXPECTED : {_trunc(ex.get('expected_behavior',''), TRUNCATE)}")
            print()

        if limit < len(examples):
            print(f"  … {len(examples) - limit} more examples not shown "
                  f"(increase MAX_EXAMPLES_SHOWN to see them)")


if __name__ == "__main__":
    main()
