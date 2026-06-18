
from __future__ import annotations

from examples.offline.sage.demo.helpers.printer_skill import _print_skill
from examples.offline.sage.demo.io.writer_golden_dataset import write_golden_dataset
from examples.offline.sage.demo.io.writer_skill import write_skill


def run_step(skills_root, skill_name, skill_body, skill_frontmatter, examples, verbose: bool = False, console = None):

    # ── Step 1: Write baseline skill + golden dataset ─────────────────────────
    console.print(f"\n[bold cyan]*** Demo Step 00: Write Demo Scenarios Started ***[/bold cyan]")
    skill_path = write_skill(skills_root, skill_name, skill_frontmatter, skill_body)
    golden_dir = write_golden_dataset(skills_root, skill_name, examples)
    console.print(f"Pre-training skill: {skill_path}")
    console.print(f"Golden dataset : {golden_dir}")

    if verbose:
        baseline_text = skill_path.read_text()
        _print_skill("① BASELINE SKILL — before any evolution", baseline_text, console)

    console.print(f"[bold cyan]*** Demo Step 00: Write Demo Scenarios Finished ***[/bold cyan]")
