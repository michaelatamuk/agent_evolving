from __future__ import annotations

from ..recommender import SkillRecommender


SEP  = "─" * 72
SEP2 = "═" * 72


def _print_query_results(results: list[dict], query: str, variant: str) -> None:
    """Detailed output for query mode — shows similar examples."""
    print(f"\n{SEP2}")
    print(f"  Skill Recommender  [{variant}]")
    print(f"  Query  : {query[:120]}")
    print(SEP2)
    if not results:
        print("  No recommendations above the configured thresholds.")
        print(SEP2)
        return
    for i, r in enumerate(results, 1):
        print(f"\n  [{i}] Skill  : {r['skill']}")
        print(f"       Metric : {r['metric']}")
        print(f"       Score  : {r['score']:.3f}  "
              f"(mean_sim={r['mean_similarity']:.3f}, "
              f"{r['n_examples']} similar example(s))")
        for ex in r["similar_examples"]:
            inp = ex.get("input", "")
            exp = ex.get("expected", "")
            out = ex.get("output", "")
            print(f"       ↳ [{ex['similarity']:.3f}] prompt   : {inp}")
            if exp:
                print(f"                 expected : {exp}")
            if out:
                print(f"                 output   : {out}")
    print(f"\n{SEP}")


def _print_skills(rec: SkillRecommender) -> None:
    print(f"\n{SEP2}")
    print("  Skills in the matrix")
    print(SEP2)
    print(f"  Total rows : {rec.n_examples}")
    print(f"  Metrics    : {rec.metrics}")
    print()
    for skill in rec.skills:
        n = int((rec._df["skill_name"] == skill).sum())
        print(f"  {skill:<40s}  {n:>4} example(s)")
    print(SEP)
