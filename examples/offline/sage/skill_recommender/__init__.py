# coding: utf-8
"""Skill Recommender — Contextual Bayesian Prompt-Skill Router.

Public API
----------
``build_recommender``   — convenience factory (recommended entry point)
``SkillRecommender``    — core recommender class
``SkillContextStore``   — Phase 3: per-skill adaptive context embeddings
``ContextualMatrix``    — Phase 3: online prompt→skill utility matrix
``Embedder``            — prompt embedder (TF-IDF or OpenAI)
``load_scores_matrix``  — load 3-D scoring matrix from oracle files
"""

from .recommender         import SkillRecommender
from .recommender_builder import build_recommender
from .recommender_similarities_computer import Embedder
from .reccmmender_scores_matrix import load_scores_matrix
from .skill_context_store import SkillContextStore
from .contextual_matrix   import ContextualMatrix

__all__ = [
    "SkillRecommender",
    "build_recommender",
    "Embedder",
    "load_scores_matrix",
    "SkillContextStore",
    "ContextualMatrix",
]
