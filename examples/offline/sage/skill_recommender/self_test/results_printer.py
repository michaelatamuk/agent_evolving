from __future__ import annotations


SEP  = "─" * 72
SEP2 = "═" * 72

def _print_benchmark_results(
    results: list[dict],
    query: str,
    expected_skill: str,
    is_hit: bool | None = None,
) -> None:
    """Compact output for benchmark mode — shows top-1 routing hit/miss."""
    short = query if len(query) <= 78 else query[:75] + "…"
    print(f"\n{SEP2}")
    print(f"  Query    : {short}")
    print(f"  Expected : {expected_skill}")
    print(SEP2)
    if not results:
        print("  No recommendations above the thresholds.")
        print(SEP)
        return
    top = results[0]
    if is_hit is None:
        is_hit = (top["skill"] == expected_skill)
    hit = "✓" if is_hit else "✗"
    for i, r in enumerate(results, 1):
        marker = "→" if i == 1 else " "
        print(f"  {marker} [{i}] skill={r['skill']}  "
              f"metric={r['metric']}  score={r['score']:.3f}  "
              f"sim={r['mean_similarity']:.3f}  n={r['n_examples']}")
    print(f"\n  Top-1: {hit}  ({top['skill']})")
    print(f"\n{SEP}")
