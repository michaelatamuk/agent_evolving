from __future__ import annotations

from agent_evolving.offline.evolvers.skill_evolver_config import EvolverConfig
from agent_evolving.offline.dataset_builder import SyntheticDatasetBuilder


def build(skill_raw: str, dataset_dir, config: EvolverConfig, console):
    console.print("[bold]Building synthetic dataset…[/bold]")
    builder = SyntheticDatasetBuilder(config)
    dataset = builder.generate(skill_raw, artifact_type="skill")
    dataset.save(dataset_dir)

    return dataset

