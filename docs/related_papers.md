# Related Papers

Reference document covering the skill-evolution research family this project
belongs to, and the academic benchmarks used in `data/hf/`.

---

## Skill Evolution Papers

Papers whose ideas directly motivate the architecture of this project
(GEPA optimizer, skill-as-parametric-asset, score-guided mutation, Thompson
Sampling scheduling).

---

### SkillOpt — Executive Strategy for Self-Evolving Agent Skills

**arXiv:** https://arxiv.org/abs/2605.23904
**Authors:** Yifan Yang, Ziyang Gong, Weiquan Huang, Qihao Yang, Ziwei Zhou,
Zisu Huang, Yan Li, Xuemei Gao, Qi Dai, Bei Liu, Kai Qiu, Yuqing Yang,
Dongdong Chen, Xue Yang, Chong Luo

**Core idea:** First systematic, controllable text-space optimizer for agent
skills.  Treats skill documents as parametric assets — trained like neural
network weights via scored rollouts.  An optimizer model converts scored
rollouts into targeted edits to the skill text; changes are accepted only when
validation scores improve.  Adds no inference-time cost after training.

**Evaluation:** Six benchmarks across direct-chat, Codex, and Claude Code
execution environments.

**Relevance to this project:** Direct inspiration for treating skills as
evolving text assets scored against held-out examples.

---

### SkillEvolver — Skill Learning as a Meta-Skill

**arXiv:** https://arxiv.org/abs/2605.10500
**Authors:** Genrui Zhang, Erle Zhu, Jinfeng Zhou, Caiyan Jia, Hongning Wang

**Core idea:** Autonomous improvement of agent skills through an iterative
cycle of authoring → deployment → refinement, without modifying model weights.
A *meta-skill* governs the refinement loop by monitoring deployment failures.
Includes safeguards against overfitting and skills that appear functional but
never fire.

**Evaluation:** SkillsBench (83 tasks, 15+ domains) — 56.8 % vs 43.6 % for
human-curated skills and 29.9 % baseline; KernelBench (GPU kernel optimization,
3 tasks) — 1.51× mean speedup.

**Relevance to this project:** Refinement-through-failure loop and meta-skill
governance are analogous to GEPA's score-guided candidate selection.

---

### EvoSkill — Automated Skill Discovery for Multi-Agent Systems

**arXiv:** https://arxiv.org/abs/2603.02766
**Authors:** Salaheddin Alzubi, Noah Provenzano, Jaydon Bingham, Weiyuan Chen,
Tu Vu

**Core idea:** Iterative failure analysis to automatically discover and refine
reusable agent skills (workflows).  Maintains a Pareto frontier of agent
programs while keeping the underlying model frozen.  Optimization targets the
skill level, not the model weights.

**Evaluation:** OfficeQA (U.S. Treasury grounded reasoning, +7.3 %),
SealQA (search-augmented QA with noisy retrieval, +12.1 %),
BrowseComp (zero-shot transfer, +5.3 %).

**Relevance to this project:** Pareto-frontier search and failure-driven
discovery mirror the population-based evolutionary search in GEPA.

---

### SkillMAS — Skill Co-Evolution with LLM-based Multi-Agent System

**arXiv:** https://arxiv.org/abs/2605.09341
**Authors:** Shuai Pan, Yixiang Liu, Jiaye Gao, Te Gao, Weiwen Liu,
Jianghao Lin, Zhihui Fu, Jun Wang, Weinan Zhang, Yong Yu

**Core idea:** Jointly evolves individual skills and the multi-agent system
topology post-deployment.  Three mechanisms: (1) Utility Learning for credit
assignment from execution traces, (2) bounded skill evolution to manage
procedure refinement without unchecked library expansion, (3) evidence-gated
MAS restructuring triggered by persistent failures.

**Evaluation:** Embodied manipulation, command-line execution, and retail
workflow domains.

**Relevance to this project:** Utility learning and evidence-gated acceptance
are closely related to Thompson Sampling skill scheduling and the Bayesian
acceptance gate in SAGE/GEPA.

---

### Skill-MAS — Evolving Meta-Skill for Automatic Multi-Agent Systems

**arXiv:** https://arxiv.org/abs/2606.18837
**Authors:** Hehai Lin (HKUST Guangzhou), Qi Yang (Ant Group),
Chengwei Qin (HKUST Guangzhou)
**Published:** June 17, 2026

**Core idea:** Proposes a "third path" between inference-time MAS (powerful
but no experience retention) and training-time MAS (internalises experience
but constrained by smaller model capacity).  Decouples orchestration
experience from parametric updates by treating multi-agent orchestration
itself as an *evolvable Meta-Skill* — a structured three-module document that
is rewritten, not retrained.

**Meta-Skill three-module structure:**
1. **Task Decomposition** ("What") — analyses queries, identifies macro
   objectives, decomposes into sub-tasks, specifies success criteria.
2. **Agent Engineering** ("Who") — instantiates specialised sub-agents with
   distinct roles and contextual inputs.
3. **Workflow Orchestration** ("How") — selects architectural topology and
   defines precise input-output mappings across agents.

**Two-phase evolutionary loop:**
- *Phase 1 — Multi-Trajectory Rollout:* Samples K independent trajectories
  per validation task.  Computes two statistics per task: **uncertainty**
  (std-dev of trajectory scores = inconsistency) and **difficulty** (negated
  mean score = hardness).
- *Phase 2 — Selective Reflection:* Priority-driven selection combines
  normalised uncertainty + difficulty via weighted scoring, applies elbow
  detection on the priority curve to select high-impact tasks.  Then runs
  **hierarchical contrastive analysis**: within-task (high vs. low-scoring
  trajectories) followed by cross-task synthesis to extract systemic
  patterns.  Skill Optimization updates the three-module Meta-Skill while
  preserving its scaffold structure.

**Evolution hyperparameters:** R=10 optimization rounds, K=5 trajectories per
task, temperature=1.0, max 32 768 output tokens.

**Evaluation:** Four benchmarks, four LLM backbones
(Gemini-3.1-Flash, GPT-5.4-Nano, Qwen3.5-Plus, DeepSeek-V4-Flash):
- **DeepResearchBench (DRB):** 44.71–51.69 % (research comprehensiveness,
  insight, instruction-following).
- **Humanity's Last Exam – Math (HLE):** 18.45–29.76 % (expert-level math).
- **BrowseComp-Plus (BCP):** 23.21–27.38 % (multi-hop QA accuracy).
- **VitaBench (VITA):** 15.48–63.10 % (real-world interactive task success).

Baselines: EvoAgent, AOrchestra, AFlow (inference-time); MAS2, MAS-Orchestra
(training-time).  Skill-MAS achieves highest average across nearly all
backbone/benchmark combinations.

**Ablations:** Performance scales with trajectory count (K=3→5→7, diminishing
returns).  Full-validation and half-validation variants both degrade without
adaptive priority selection.  Framework currently requires ground-truth labels
for priority scoring (identified as future work).

**Transferability:** Evolved Meta-Skills generalise to unseen tasks and
different LLM backbones; strongest transfer on same-task, different-LLM.

**Evolved skill trajectory (qualitative):** The paper reports a consistent
cross-benchmark pattern across all four LLM backbones: evolution proceeds in
three recognisable phases, each corresponding roughly to which Meta-Skill
module is being refined most heavily.

- *Early rounds (Task Decomposition — "What"):* The optimizer sharpens
  objective identification and success-criteria specification.  Initial
  Meta-Skills tend to state objectives vaguely; evolved versions decompose
  queries into discrete, verifiable sub-goals with explicit completion
  conditions.  This is the lowest-hanging fruit: clearer decomposition
  directly reduces agent coordination failures.

- *Middle rounds (Agent Engineering — "Who"):* The optimizer shifts to
  epistemic control — agents acquire more precisely scoped roles, more
  targeted contextual inputs, and explicit uncertainty signalling.  Brittle
  binary checks ("did this step succeed: yes/no?") are progressively replaced
  by calibrated evaluation instructions ("assess confidence on a 0–1 scale
  and flag ambiguity before proceeding").  Agent specialisation increases,
  reducing redundant work and improving credit assignment.

- *Late rounds (Workflow Orchestration — "How"):* The optimizer introduces
  system-level resilience mechanisms — constraint-aware reasoning rules,
  verification gates between pipeline stages, and fallback routing for
  high-uncertainty sub-tasks.  The architectural topology stabilises; the
  optimizer fine-tunes handoff semantics and error propagation boundaries
  rather than restructuring agents.

Overall direction: "From decomposition design through agent-level epistemic
control to system-level resilience."  The scaffold structure of the three
modules is preserved throughout; the optimizer rewrites content within each
module without collapsing or merging modules.  Evolved Meta-Skills are
substantially longer and more specific than their initial versions, with the
largest growth occurring in the Agent Engineering module.

**Relevance to this project:** Hierarchical contrastive analysis of
successful vs. failing rollouts is directly analogous to GEPA's
scored-candidate mutation strategy.  The three-module Meta-Skill concept
(what / who / how) mirrors the skill-as-parametric-asset design.  Priority
scoring via uncertainty × difficulty is a concrete implementation of the
Thompson Sampling intuition used in SAGE's batch scheduler.

---

### SkillGen — Verified Inference-Time Agent Skill Synthesis

**arXiv:** https://arxiv.org/abs/2605.10999
**Authors:** Yuchen Ma, Yue Huang, Han Bao, Haomin Zhuang, Swadheen Shukla,
Michel Galley, Xiangliang Zhang, Stefan Feuerriegel

**Core idea:** Auto-generates reusable skills by analysing both successful and
failed agent trajectories via contrastive learning.  Treats skills as
interventions and measures true impact by comparing performance with vs.
without the skill on identical tasks (including potential regressions).

**Evaluation:** Includes the PubMedQA biomedical dataset (see below).

**Relevance to this project:** PubMedQA benchmark in `data/hf/pubmedqa/` is
used in this paper.  Contrastive evaluation of skill presence/absence mirrors
the baseline vs. evolved holdout split in GEPA.

---

## June 2026 — New Papers (Skill Evolution Wave)

29 additional papers published June 1–16, 2026, discovered via arXiv search.
Grouped loosely by mechanism: co-evolution / RL, statistical gates, contrastive
extraction, infrastructure / lifecycle, domain-specific, and survey.

---

### ReSkill — Assertion-Driven Skill Creation Co-Evolved with Policy

**arXiv:** https://arxiv.org/abs/2606.01619
**Authors:** Zelin He, Haotian Lin, Boran Han, Wei Zhu, Haoyang Fang, Bernie
Wang, Xuan Zhu, Runze Li, Matthew Reimherr
**Published:** June 1, 2026

**Core idea:** Integrates skill development directly into policy learning in a
co-evolution loop.  An assertion-driven skill creator diagnoses failures from
past experience and proposes conditional, trigger-based skill revisions.
Skills undergo automatic creation, testing, refinement, and pruning as policies
improve.  Thompson Sampling balances exploration-exploitation in skill
selection.

**Relevance to this project:** Explicit Thompson Sampling for skill selection
at Level 1, identical in formulation to SAGE's skill scheduler arm.
Assertion-driven diagnosis maps to GEPA's contrastive failure reflection.

---

### UCE — Unified Context Evolution for LLM Agents

**arXiv:** https://arxiv.org/abs/2606.02304
**Authors:** Zixuan Zhu, Yitong Hu, Yong Dai, Junfeng Fang, Chunyang Jiang,
Senkang Hu, Yuzhi Zhao
**Published:** June 1, 2026

**Core idea:** Organises agent experience into four co-evolving Evolvable
Context Unit types: Memory, Strategy, Workflow, and Skill.  Units are generated
from task trajectories, retrieved during decisions, evaluated through usage
outcomes, and pruned when no longer beneficial.  ALFWorld 75.4 % → 96.3 %;
WebShop 45.1 % → 61.3 %.  Library transfers across model architectures without
retraining.

**Relevance to this project:** Skill treated as one of four co-evolving context
types; pruning and value-based retention mirrors SAGE's Beta-Bernoulli skill
scheduler deprecation logic.

---

### MetaForge — Self-Evolving Multimodal Agent via Forge-Recycle Loop

**arXiv:** https://arxiv.org/abs/2606.01801
**Authors:** Shouang Wei, Houcheng Min, Xinpeng Dong, Xin Lin, Sen Cui,
Bo Jiang, Zhongxiang Dai, Kun Kuang, Guandong Xu, Fei Wu, Min Zhang
**Published:** June 1, 2026

**Core idea:** Closed decide-retrieve-adapt-forge-recycle loop for a multimodal
agent.  Determines tool necessity, selects/contextualises tools, creates novel
skills for library integration.  RL optimises across multiple objectives while
penalising unnecessary invocations.  Outperforms 16 baselines across 12
benchmarks.

**Relevance to this project:** Forge-recycle loop evolves the skill/tool
library on demand; skill value scoring mirrors SAGE's Level 2 trace
discrimination for identifying high-signal operations.

---

### Adaptive Auto-Harness — Sustained Skill Self-Improvement on Task Streams

**arXiv:** https://arxiv.org/abs/2606.01770
**Authors:** Zewen Liu, Zhan Shi, Yisi Sang, Bing He, Minhua Lin, Tianxin Wei,
Dakuo Wang, Benoit Dumoulin, Wei Jin, Hanqing Lu
**Published:** June 1, 2026 (revised June 3, 2026)

**Core idea:** Addresses auto-harness/skill system limitations on open-ended
continuous task streams.  Decomposes performance gaps into *evolution loss* and
*adaptation loss*.  Framework includes a multi-agent evolver, adaptive harness
routing, and human feedback mechanisms.

**Relevance to this project:** Evolution loss / adaptation loss decomposition is
a useful diagnostic lens for evaluating SAGE runs across skill lifecycle stages.

---

### FederatedSkill — Federated Learning for Agentic Skill Evolution

**arXiv:** https://arxiv.org/abs/2606.03143
**Authors:** Jingbo Yang, Guanyu Yao, Yang Zhang, Ramana Rao Kompella,
Gaowen Liu, Shiyu Chang
**Published:** June 2, 2026

**Core idea:** Privacy-preserving collaborative skill evolution.  Agents
exchange "semantic skill diffs" — structured patches over local skill libraries
— rather than raw trajectories.  A server-side evolution agent processes patches
to recognise individual capability boundaries.  Up to 44.4 % success rate
increase and 37.5 % computational cost reduction vs. self-improving baselines
across 20 agent task families.

**Relevance to this project:** Semantic skill diffs are structurally analogous
to SAGE's candidate mutations; the federated setting surfaces questions about
cross-skill knowledge transfer (see SAGE §8.9).

---

### SkillPyramid — Hierarchical Skill Consolidation for Self-Evolving Agents

**arXiv:** https://arxiv.org/abs/2606.03692
**Authors:** Yuan Xiong, Ziqi Miao, Qian Chen, Lijun Li, Yequan Wang,
Shizhu He, Jun Zhao, Kang Liu
**Published:** June 2, 2026

**Core idea:** Reuses existing skills and enables agents to compose/validate new
ones during execution rather than redundantly building similar capabilities per
task.  Transforms skill collection into a continuously evolving hierarchical
system.  ALFWorld / WebShop / ScienceWorld: average reward +38.0 %,
execution steps −27.7 %.

**Relevance to this project:** Hierarchical composition with reuse addresses the
skill portfolio management problem implicit in SAGE's Level 1 scheduler across
large enterprise skill catalogs.

---

### EvoDS — Self-Evolving Autonomous Data Science Agent

**arXiv:** https://arxiv.org/abs/2606.03841
**Authors:** Zherui Yang, Fan Liu, Yansong Ning, Hao Liu
**Published:** June 2, 2026 (accepted KDD 2026)

**Core idea:** Two innovations: (1) Autonomous Skill Acquisition synthesises,
validates, and reuses executable skills; (2) Adaptive Context Compression treats
context management as a learned control problem.  Dual-stage multi-agent
training with theoretical guarantees on error reduction.  ~29 % improvement
over comparable open-source agents.

**Relevance to this project:** Skill acquisition + validation loop is analogous
to SAGE's evolutionary search + holdout gate for domain-specific (data science)
skills.

---

### Parthenon Law — Self-Evolving Legal-Agent Framework

**arXiv:** https://arxiv.org/abs/2606.04602
**Authors:** Hejia Geng, Leo Liu
**Published:** June 3, 2026 (revised June 11, 2026)

**Core idea:** Empirically tested on 12,510 agent trajectories; frontier models
fail to complete legal matters autonomously.  Separates Model, Harness, Agent,
Knowledge, Tools, and Skills into auditable components.  An anti-leakage
learning loop converts scored failures into task-agnostic edits to skills,
tools, and knowledge — continuous improvement without weight modification.

**Relevance to this project:** Anti-leakage loop (score → skill edit) is
architecturally identical to GEPA's mutation loop.  Legal domain mirrors
contract-review synthetic scenario; demonstrates SAGE applicability to regulated
domains.

---

### LifeSkill — Skill-Enhanced Test-Time Co-Evolution for Lifelong Learning

**arXiv:** https://arxiv.org/abs/2606.04815
**Authors:** Bo Mao, Jie Zhou, Yutao Yang, Xin Li, Xian Wei, Qin Chen,
Xingjiao Wu, Liang He
**Published:** June 3, 2026

**Core idea:** Two-stage RL framework.  Stage 1 — Verifier-Guided Skill
Learning rewards skills based on verifier success across multiple rollouts
(practical usefulness, not textual plausibility).  Stage 2 — Online Skill
Internalization converts skill-conditioned trajectories into reward signals for
real-time policy improvement.  +7 pts on LifelongAgentBench.

**Relevance to this project:** Stage 1 verifier-guided reward is a RL analogue
of SAGE's holdout gate.  Stage 2 internalization maps to SAGE's Thompson
Sampling posterior update from live deployment telemetry (§4.5 online routing).

---

### SePO — Self-Evolving Prompt Agent for System Prompt Optimization

**arXiv:** https://arxiv.org/abs/2606.04465
**Authors:** Wangcheng Tao, Han Wu, Weng-Fai Wong
**Published:** June 3, 2026

**Core idea:** Self-referential design where the prompt agent treats its own
system prompt as an optimization target through evolutionary search while
simultaneously optimising task-specific prompts.  Two-stage training:
pre-training across tasks then fine-tuning for objectives.  ~4.5 pts over
baselines with out-of-distribution task transfer.

**Relevance to this project:** Self-referential skill-as-optimization-target is
the same architectural move as GEPA.  Pre-training → fine-tuning analogy maps
to SAGE's burn-in phase before Thompson Sampling pressure engages.

---

### VASO — Formally Verifiable Self-Evolving Skills for Physical AI

**arXiv:** https://arxiv.org/abs/2606.05395
**Authors:** Yunhao Yang, Neel P. Bhatt, Kevin Wang, Samuel Tetteh,
Zhangyang Wang, Ufuk Topcu
**Published:** June 3, 2026

**Core idea:** Couples formal verification with skill evolution for robot
agents.  Each skill has a semantic contract with formal and planner-facing
interfaces.  Model checking filters inconsistent contracts; when verification
fails, counterexample traces are translated into textual gradients that update
skill contracts (no weight changes).  97.2 % specification compliance with
< 100 optimization samples.

**Relevance to this project:** Formal verification as acceptance gate is the
strongest analogue to SAGE's hard per-dimension no-regression constraint (§4.4);
counterexample-as-textual-gradient is a formal version of SAGE's contrastive
mutation reflection.

---

### RHO — Retrospective Harness Optimization via Self-Preference

**arXiv:** https://arxiv.org/abs/2606.05922
**Authors:** Wenbo Pan, Shujie Liu, Chin-Yew Lin, Jingying Zeng, Xianfeng
Tang, Xiangyang Zhou, Yan Lu, Xiaohua Jia
**Published:** June 4, 2026 (revised June 10, 2026)

**Core idea:** Self-supervised harness/skill optimization using only past
trajectories, without labeled validation data.  Selects a diverse coreset of
challenging tasks from past trajectories and re-solves them in parallel, using
the agent's own preference judgment to evaluate improvements.  SWE-Bench Pro
59 % → 78 % with no external grading.

**Relevance to this project:** Self-preference evaluation without labeled data
is the LLM-judge analogue of SAGE's LLM-as-judge holdout modes; coreset
selection mirrors SAGE's Level 2 trace discrimination (top-quartile selection).

---

### OpenSkill — Open-World Self-Evolution for LLM Agents

**arXiv:** https://arxiv.org/abs/2606.06741
**Authors:** Zhiling Yan, Dingjie Song, Hanrong Zhang, Wei Liang, Yuxuan
Zhang, Yutong Dai, Lifang He, Philip S. Yu, Ran Xu, Xiang Li, Lichao Sun
**Published:** June 4, 2026

**Core idea:** Enables LLM agents to improve independently in open-world
settings without supervised training data or target-task supervision.  Acquires
knowledge from documentation and web resources, develops transferable
capabilities, creates self-generated practice tasks, and builds self-verification
signals autonomously.

**Relevance to this project:** Self-generated practice tasks are analogous to
SAGE's synthetic scenario generation mode (Proxy 1 in §5.1).  Cross-backbone
transfer mirrors SAGE §8.9 cross-task transfer research direction.

---

### Socratic-SWE — Trace-Derived Skill Evolution for Coding Agents

**arXiv:** https://arxiv.org/abs/2606.07412
**Authors:** Chuan Xiao, Zhengbo Jiao, Shaobo Wang, Wei Wang, Bing Zhao,
Hu Wei, Linfeng Zhang, Lin Qu
**Published:** June 5, 2026

**Core idea:** Closed-loop self-evolution for software engineering agents.
Distils agent execution traces into structured skills summarising recurring
failures and effective repair patterns.  Skills guide generation of targeted
repair tasks, validated through execution and scored with alignment-based
rewards.  50.40 % on SWE-bench Verified after three iterations.

**Relevance to this project:** Trace → skill distillation is the core SAGE
trajectory mode; alignment-based reward scoring maps to SAGE's fitness metric
family applied to code generation tasks.

---

### PACE — Anytime-Valid Acceptance Tests for Self-Evolving Agents

**arXiv:** https://arxiv.org/abs/2606.08106
**Author:** Zayx Shawn
**Published:** June 6, 2026

**Core idea:** Identifies that "keep if better" acceptance in agent self-evolution
amounts to repeated testing against the same noisy evaluation set, causing false
improvements and drift.  PACE (Paired Anytime-valid Commit Evaluation) treats
acceptance as a formal hypothesis test using e-process testing-by-betting to
accumulate decisive evidence before committing.  Greedy acceptance commits
30–42 % false and 10–33 % harmful edits; PACE maintains baseline performance
when no genuine gains exist.

**Relevance to this project:** PACE is the closest formal analogue to SAGE's
Bayesian Acceptance Gate (§4.5) — both replace the naive "higher score → deploy"
heuristic with a calibrated statistical test.  PACE's e-process testing-by-betting
and SAGE's Monte Carlo P ≥ 0.75 address the same structural problem from
different statistical frameworks (frequentist anytime vs. Bayesian posterior).

---

### Bayesian-Agent — Posterior-Guided Skill Evolution

**arXiv:** https://arxiv.org/abs/2606.08348
**Authors:** Xiaojun Wu, Cehao Yang, Honghao Liu, Xueyuan Lin, Wenjie Zhang,
Zhichao Shi, Xuhui Jiang, Chengjin Xu, Jia Li, Jian Guo
**Published:** June 6, 2026

**Core idea:** Treats reusable skills and SOPs as probabilistic hypotheses about
agent success.  Maintains a feature-conditioned categorical posterior over each
skill and converts posterior information into actionable responses —
"posterior-guided harness optimisation rather than uncalibrated prompt
accumulation."  DeepSeek-v4-Flash gains 15–20 pp on SOP-Bench, Lifelong
AgentBench, and RealFin-Bench.

**Relevance to this project:** Feature-conditioned categorical posterior over
each skill is a generalisation of SAGE's Beta-Bernoulli conjugate arms.
"Posterior-guided" optimisation is the same philosophical move as SAGE's
Thompson Sampling resource allocation.

---

### Co-Evolving Skill Generation and Policy Optimization

**arXiv:** https://arxiv.org/abs/2606.08755
**Authors:** Zhiwei Zhang, Yudi Lin, Nikki Lijing Kuang, Linlin Wu,
Xiaomin Li, Songtao Liu, Fenglong Ma
**Published:** June 7, 2026

**Core idea:** Addresses newly generated skills lacking validation before
storage.  Uses matched rollout groups to measure whether candidate skills provide
marginal value beyond already-retrieved capabilities.  The policy is trained as
a skill generator, reducing dependence on external LLMs; context-dependent
scores handle retrieval and pruning of outdated skills.

**Relevance to this project:** Marginal-value validation before storage is a RL
analogue of SAGE's holdout gate; pruning via context-dependent scores mirrors
SAGE's Level 1 arm deprecation for stagnant skills.

---

### SkillHone — Continual Skill Evolution via Persistent Decision History

**arXiv:** https://arxiv.org/abs/2606.08671
**Authors:** Zhiwei Li, Yong Hu
**Published:** June 7, 2026

**Core idea:** Enables cross-session skill refinement by pairing skill revisions
with evaluation-side evidence and recording structured histories of diagnoses,
revisions, and outcomes — without discarding decision rationale between
sessions.  Specialised subagents test candidates and propose improvements based
on prior decisions.  +15.8 pts on GAIA, +3.2 pts on WebWalkerQA-EN using
Qwen3.6-35B-A3B.

**Relevance to this project:** Persistent decision history across sessions is
the same motivation as SAGE's provenance log (§5.5) and inter-run adaptive
dimension weighting.  GAIA improvement numbers are a useful baseline for any
future GAIA integration.

---

### SkeMex — Self-Evolving Skill Memory for Medical Agents

**arXiv:** https://arxiv.org/abs/2606.09365
**Authors:** Haoran Sun, Wenjie Li, Yujie Zhang, Zekai Lin, Fanrui Zhang,
Kaitao Chen, Xingqi He, Yichen Li, Mianxin Liu, Lei Liu, Yankai Jiang
**Published:** June 8, 2026 (revised June 15, 2026)

**Core idea:** Post-deployment framework for medical agents that distils
clinical interaction trajectories into structured skills organised across
general, task-specific, and action-level repositories.  Uses environment
feedback via a read-write-assess-govern cycle.  Consistent improvements across
clinical tasks; cross-model skill transfer demonstrated.

**Relevance to this project:** Three-tier skill repository maps naturally to
SAGE's population-based search across skill specificity levels.  Medical domain
extends naturally from the existing `data/hf/pubmedqa/` scenario.

---

### SkillAxe — Evaluation-Guided Self-Refinement of LLM-Authored Skills

**arXiv:** https://arxiv.org/abs/2606.10546
**Authors:** Srishti Gautam, Arjun Radhakrishna, Sumit Gulwani
**Published:** June 9, 2026

**Core idea:** Unsupervised framework enabling LLMs to self-diagnose and refine
their own authored skills across four dimensions: quality impact, trigger
precision, instruction compliance, and solution-path coverage.  +28 % relative
over unimproved skills.  Closes 47–67 % of the gap to human-authored skills on
SkillsBench; SpreadsheetBench 16 % → 52 %.

**Relevance to this project:** Four-dimension self-diagnosis maps directly to
SAGE's rubrics evaluation mode (§4.4) measuring correctness / procedure-following
/ format-adherence / completeness.  SkillsBench results provide a comparison
point for any future SkillsBench integration.

---

### Agent Skill Evaluation and Evolution: Frameworks and Benchmarks (Survey)

**arXiv:** https://arxiv.org/abs/2606.11435
**Authors:** Kexin Ding, Yang Zhou, Can Jin, Feng Tong, Mu Zhou,
Dimitris N. Metaxas
**Published:** June 9, 2026

**Core idea:** Comprehensive survey identifying four paradigms for agent skill
enhancement: (1) execution feedback, (2) trajectory distillation, (3)
compression, and (4) reinforcement learning.  Analyses six benchmark categories
to highlight coverage gaps and missing metrics.

**Relevance to this project:** Reference map of the full field as of June 2026.
The four paradigms map to SAGE's Layer 1 (execution feedback), Layer 2
(trajectory distillation), and Layer 3 (RL / macro evolutionary).  Coverage gap
analysis is relevant to SAGE §6 evaluation methodology.

---

### SkillCAT — Contrastive Assessment and Topology-Aware Skill Self-Evolution

**arXiv:** https://arxiv.org/abs/2606.13317
**Authors:** Kunfeng Chen, Qihuang Zhong, Juhua Liu, Bo Du
**Published:** June 11, 2026

**Core idea:** Training-free skill evolution in three phases: (1) Contrastive
Causal Extraction (CCE) compares same-task execution trajectories to isolate
differentiating factors; (2) assessment-augmented refinement replays candidates
on task variants before merging; (3) topology-aware execution organises evolved
capabilities into a navigable network so only task-relevant components are
loaded at inference.  Up to 40.40 % improvement on spreadsheet, table-question,
and document-analysis benchmarks.

**Relevance to this project:** CCE is a training-free variant of GEPA's
contrastive candidate reflection.  Assessment-augmented refinement on task
variants is analogous to SAGE's consistency evaluation mode (§4.4).

---

### EvoArena / EvoMem — Memory Evolution Benchmark for Dynamic Environments

**arXiv:** https://arxiv.org/abs/2606.13681
**Authors:** Jundong Xu, Qingchuan Li, Jiaying Wu, Yihuai Lan, Shuyue Stella
Li, Huichi Zhou, Bowen Jiang, Lei Wang, Jun Wang, Anh Tuan Luu, Caiming Xiong,
Hae Won Park, Bryan Hooi, Zhiyuan Hu
**Published:** June 11, 2026 (revised June 17, 2026)

**Core idea:** EvoArena evaluates agents in environments that change
progressively across terminal, software, and social domains.  EvoMem tracks
knowledge updates via structured histories.  Current agents achieve only 39.6 %
on evolving tasks; EvoMem improves by 1.5 % on EvoArena and 6.1 % on GAIA.

**Relevance to this project:** EvoArena is a direct benchmark for agents whose
skills must adapt over time.  GAIA improvement numbers are a useful baseline
reference for any future GAIA integration.

---

### SkillAudit — Ground-Truth-Free Skill Evolution via Paired Trajectory Auditing

**arXiv:** https://arxiv.org/abs/2606.14239
**Authors:** Haowen Gao, Haoran Chen, Can Wang, Shasha Guo, Liang Pang,
Zhaoyang Liu, Huawei Shen, Xueqi Cheng
**Published:** June 12, 2026

**Core idea:** Evolves agent skills without any external validation signals or
ground-truth labels.  At each iteration, the same task is executed with and
without the candidate skill; Process-Aligned Contrastive Evaluation maps
trajectory differences to actionable edits, and a structural verifier enforces
task constraints.  73.9 % average task reward vs. 40.9 % (no skill) and 56.7 %
(static expert skill) across 89 containerised tasks, 8 professional domains.

**Relevance to this project:** Ground-truth-free evolution directly addresses
the limitation Skill-MAS flagged (requires ground-truth labels for priority
scoring).  With-vs-without-skill paired execution mirrors SAGE's trajectory mode
baseline comparison.  Structural verifier is analogous to SAGE's no-regression
constraint without requiring labeled reference outputs.

---

### ASSAY — Not All Skills Help: Measuring and Repairing Agent Knowledge

**arXiv:** https://arxiv.org/abs/2606.15390
**Authors:** Yixuan Wang, Yiyang Zhou, Yiming Liang, Congyu Zhang, Fuxiao
Liu, Jiawei Zhou, Huaxiu Yao
**Published:** June 13, 2026

**Core idea:** Identifies "pervasive causal heterogeneity" — individual skills
help some tasks while harming others, and collective evaluation masks this.
ASSAY uses randomised masking to measure per-skill causal attribution on dev
sets and suppresses unhelpful skills at test time.  DeepSeek-V3 gains 47.4 %
relative improvement on AppWorld's hardest split; GPT-4.1 gains 8.7 % on
tau-bench retail.

**Relevance to this project:** Causal heterogeneity is the exact failure mode
SAGE's per-dimension no-regression constraint is designed to catch: a skill
that helps on metric A while hurting metric B should not deploy.  ASSAY's
randomised masking is a complementary diagnostic to SAGE's rubric-based
regression gate.

---

### VisualClaw — Real-Time Skill Evolution via Retrieval-Conditioned Memory

**arXiv:** https://arxiv.org/abs/2606.16295
**Authors:** Haoqin Tu, Jianwen Chen, Zijun Wang, Siwei Han, Juncheng Wu,
Hardy Chen, Haonian Ji, Kaiwen Xiong, Jiaqi Liu, Peng Xia, Jieru Mei,
Hongliang Fei, Jason Eshraghian, Zeyu Zheng, Yuyin Zhou, Huaxiu Yao, Cihang Xie
**Published:** June 15, 2026

**Core idea:** Multimodal agent combining hybrid encoding (filtering
uninformative frames, compressing skill databases) with skill evolution via
retrieved-memory conditioning.  The agent learns from mistakes and updates its
skill repository in real time.  ~98 % API cost reduction vs. full-frame upload.
Introduces VisualClawArena (200-scenario benchmark).

**Relevance to this project:** Skill database compression and cost-reduction
techniques are directly applicable to SAGE's computational overhead problem
(§5.4).  Real-time skill update maps to SAGE's Level 1 online routing posteriors.

---

### daVinci-kernel — Co-Evolving Skill Library for GPU Kernel Optimization

**arXiv:** https://arxiv.org/abs/2606.16497
**Authors:** Dayuan Fu, Mohan Jiang, Tongyu Wang, Dian Yang, Jiarui Hu,
Liming Liu, Jinlong Hou, Pengfei Li
**Published:** June 15, 2026

**Core idea:** RL framework with three coordinated agents (retriever, generator,
distiller) sharing a model backbone.  The distiller validates successful
CUDA/Triton kernel optimizations and adds them to a dynamically evolving skill
library.  37.2 % / 70.6 % / 32.2 % on KernelBench L1/L2/L3.

**Relevance to this project:** Validation-before-storage is the same principle
as SAGE's holdout gate; the three-agent (retrieve / generate / distil) topology
maps to SAGE's (trace selection / mutation / evaluation) pipeline.  KernelBench
results are the strongest published baseline for the KernelBench scenario
investigated in this project.

---

### SkillWiki — A Living Knowledge Infrastructure for Agent Skills

**arXiv:** https://arxiv.org/abs/2606.16523
**Authors:** Dingcheng Huang, Yuda Ding, Bingshuo Liu, Qingbin Liu, Xi Chen,
Jiang Bian, Hongliang Sun, Zhiying Tu, Dianhui Chu, Xiaoyan Yu, Dianbo Sui
**Published:** June 15, 2026

**Core idea:** Observes that while knowledge has Wikipedia and software has
GitHub, agent skills lack infrastructure for large-scale production, governance,
and evolution.  Converts heterogeneous knowledge into reusable, evidence-linked
skill assets and manages the complete skill lifecycle: importing, developing,
exploring with source tracking, oversight, and refinement from execution
outcomes.

**Relevance to this project:** SkillWiki is the infrastructure layer SAGE
assumes exists but does not itself provide.  Evidence-linked skill assets and
source tracking map to SAGE's provenance log design (§5.5).  The governance
lifecycle mirrors the SAGE deployment cadence (§5.4).

---

### OPD-Evolver — Holistic Agent Evolver via On-Policy Distillation

**arXiv:** https://arxiv.org/abs/2606.17628
**Authors:** Guibin Zhang, Xun Xu, Yanwei Yue, Zikun Su, Wangchunshu Zhou,
Xiaobin Hu, Shuicheng Yan
**Published:** June 16, 2026

**Core idea:** Combines fast and slow evolutionary loops with outcome-calibrated
memory attribution and on-policy distillation.  Agents build hierarchical
memory and learn to "read, use, write, and maintain experience for rapid
test-time evolution."  OPD-Evolver-9B achieves up to 11.5 % performance gains
over comparable memory-augmented systems.

**Relevance to this project:** Fast/slow evolutionary loop split maps directly
to SAGE's Layer 2 (per-epoch directed maintenance) + Layer 3 (periodic macro
rewrite) architecture.  Outcome-calibrated memory attribution is a finer-grained
version of SAGE's Level 2 Beta-Bernoulli trace arm tracking.

---

## HuggingFace Benchmark Datasets

Datasets available under `data/hf/` and their origin papers.  These are used
in this project as routing-test benchmarks for the skill recommender self-test
(`--self-test`) — not as GEPA training data.

---

### GSM8K — Grade School Math 8K

**HuggingFace dataset:** `openai/gsm8k`
**Origin paper:** "Training Verifiers to Solve Math Word Problems" — Cobbe et al., 2021
**Used as benchmark in:**
- **OPRO** (arXiv:2309.03409) — "Large Language Models as Optimizers" (Yang et al., 2023) — prompt meta-optimization
- **DSPy** (arXiv:2310.03714) — "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines" (Khattab et al., 2023) — few-shot compilation

**Dataset:** 8,500 grade-school math word problems requiring multi-step
arithmetic.  Answers are chain-of-thought strings ending with `#### <number>`.
Split: 7,473 train / 1,319 test.

**In this project (`data/hf/gsm8k/`):** Skill = step-by-step math reasoning.
Difficulty derived from number of arithmetic steps (0–1 easy, 2–3 medium, 4+ hard).

---

### HotPotQA — Multi-hop Question Answering

**HuggingFace dataset:** `hotpotqa/hotpot_qa` (distractor config)
**Origin paper:** "HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering" — Yang et al., 2018
**Used as benchmark in:**
- **DSPy** (arXiv:2310.03714) — multi-hop chain-of-thought compilation

**Dataset:** ~113K crowd-sourced multi-hop QA questions requiring two
Wikipedia paragraphs to answer (bridge and comparison types).  We use the
`distractor` config (10 candidate paragraphs) for fast download.

**In this project (`data/hf/hotpotqa/`):** Skill = multi-hop QA with
chain-of-thought over two supporting facts.
Difficulty derived from question level field (`easy` / `medium` / `hard`).

---

### PubMedQA — Biomedical Research Question Answering

**HuggingFace dataset:** `qiaojin/PubMedQA` (pqa_labeled config)
**Origin paper:** "PubMedQA: A Dataset for Biomedical Research Question Answering" — Jin et al., 2019
**Used as benchmark in:**
- **SkillGen** (arXiv:2605.10999) — verified inference-time agent skill synthesis

**Dataset:** 1,000 expert-labelled biomedical yes/no/maybe questions derived
from PubMed abstracts.  Label distribution: ~55 % yes / 34 % no / 11 % maybe.

**In this project (`data/hf/pubmedqa/`):** Skill = biomedical QA with a
one-sentence verdict plus supporting evidence.
Difficulty derived from tertile of answer length.

---

### AQuA-RAT — Algebra with Rationale

**HuggingFace dataset:** `deepmind/aqua_rat` (raw config, test split)
**Origin paper:** "Program Induction by Rationale Generation: Learning to Solve and Explain Algebraic Word Problems" — Ling et al., 2017
**Used as benchmark in:**
- **OPRO** (arXiv:2309.03409) — used as a GSM8K transfer benchmark for algebraic reasoning

**Dataset:** 254 algebra word problems (test split) with five lettered answer
choices (A–E), a full step-by-step rationale, and the correct option letter.

**In this project (`data/hf/aquarat/`):** Skill = algebra reasoning with full
working and the correct option letter.
Difficulty derived from tertile of rationale length.

---

### BBH — Big-Bench Hard

**Origin paper:** "Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them" — Suzgun et al., 2022
**Used as benchmark in:**
- **DSPy** (arXiv:2310.03714) — multi-task chain-of-thought evaluation

**Dataset:** 23 diverse reasoning tasks (algorithmic, logical, symbolic,
commonsense) selected from Big-Bench for being hard enough to require
chain-of-thought prompting to exceed random performance.

**In this project (`data/hf/bbh/`):** Placeholder scenario — no loader, no
single skill, returns `[]`.  BBH is multi-task with heterogeneous formats;
it cannot be expressed as a single skill for GEPA evolution.  Excluded from
skill recommender self-test.

---

## Benchmarks Evaluated for Integration

Benchmarks from skill-evolution papers that were investigated for addition
as new scenarios in `data/`.  Neither is currently integrated — reasons
documented below.

---

### SkillsBench — Agent Skill Benchmark (83 tasks, 15+ domains)

**Origin paper:** "SkillsBench: Benchmarking How Well Agent Skills Work Across
Diverse Tasks" — Li et al., 2026 (arXiv:2602.12670)
**Used in:** SkillEvolver (arXiv:2605.10500)
**GitHub:** https://github.com/benchflow-ai/skillsbench
**HuggingFace:** `benchflow/skillsbench` (viewer broken; `benchflow/skillsbench-data`
is a different, unrelated artifact — 94k Claude skill YAML files)

**Data format:** Each task is a self-contained Docker module:
```
tasks/<id>/
  task.md           # YAML frontmatter (difficulty, category, …) + instruction body
  environment/Dockerfile
  oracle/solve.sh   # reference solution (must hit 100% on verifier)
  verifier/test_outputs.py
```
The instruction body of `task.md` can serve as `task_input`.  There is **no
stored `expected_output` text** — correctness is verified by running pytest
assertions inside a Docker container against a live environment.

**Difficulty field:** present directly in YAML frontmatter (`easy/medium/hard`).

**8 taxonomy domains:** software-engineering, cybersecurity, natural-science,
finance-economics, office-white-collar, media-content-production,
industrial-physical-systems, mathematics-or-formal-reasoning.

**Why not integrated:** Evaluation requires Docker container execution.
`task_input` is extractable as a plain string; `expected_output` is not — the
oracle is a shell script + pytest, not a text answer.  LLM-as-judge rubric
scoring could substitute, but the evaluation infrastructure is non-trivial.

**Integration path if needed:** Clone the repo, parse each `task.md` YAML
frontmatter and instruction body, generate `expected_behavior` as prose from
`oracle/solve.sh`, use rubric-based fitness metrics.

---

### KernelBench — GPU Kernel Optimization (270 tasks, 4 levels)

**Origin paper:** "KernelBench: Can LLMs Write Efficient GPU Kernels?" —
Ouyang et al., 2025 (ScalingIntelligence / Stanford)
**Used in:** SkillEvolver (arXiv:2605.10500) — 3 Level-3 tasks only
**GitHub:** https://github.com/ScalingIntelligence/KernelBench
**HuggingFace:** `ScalingIntelligence/KernelBench` — public, clean, 4 columns

**Data format (HuggingFace):**

| Column | Type | Description |
|--------|------|-------------|
| `problem_id` | int64 | 1-indexed within level |
| `name` | string | e.g. `"1_Square_matrix_multiplication_"` |
| `level` | int64 | 1, 2, 3, or 4 |
| `code` | string | Complete self-contained PyTorch reference file |

The `code` column is the task: a PyTorch `Model` class plus `get_inputs()`.
Expected output = a functionally equivalent CUDA/Triton kernel class named
`ModelNew` that achieves measurable speedup on a GPU.  **No golden
`expected_output` string exists** — any correct, faster kernel is valid.

**Dataset size:** 100 (L1) + 100 (L2) + 50 (L3) + 20 (L4) = 270 tasks.
**Difficulty mapping:** level 1 → easy, level 2 → medium, level 3/4 → hard.

**Why not integrated:** Evaluation requires a GPU (NVIDIA H100 used in paper)
to verify correctness and measure speedup.  Without GPU execution the only
signal is LLM-as-judge code review, which gives weak signal for kernel quality.
Data loading from HuggingFace is straightforward and dependency-free; the
blocker is entirely on the evaluation side.

**Integration path if needed:**
```python
from datasets import load_dataset
def load(n: int = 50, seed: int = 42):
    ds = load_dataset("ScalingIntelligence/KernelBench",
                      split="level_1+level_2+level_3")
    ds = ds.shuffle(seed=seed).select(range(min(n, len(ds))))
    return [{
        "task_input": "Optimize this PyTorch model with a CUDA/Triton kernel:\n\n"
                      + row["code"],
        "difficulty": {1:"easy",2:"medium",3:"hard",4:"hard"}[row["level"]],
    } for row in ds]
```

---

## Benchmark → Paper Quick-Reference

| Dataset | Origin | Used in skill paper |
|---------|--------|---------------------|
| GSM8K | Cobbe et al., 2021 | OPRO (2309.03409), DSPy (2310.03714) |
| HotPotQA | Yang et al., 2018 | DSPy (2310.03714) |
| PubMedQA | Jin et al., 2019 | SkillGen (2605.10999) |
| AQuA-RAT | Ling et al., 2017 | OPRO (2309.03409) |
| BBH | Suzgun et al., 2022 | DSPy (2310.03714) |

| Skill paper | arXiv | Benchmarks |
|-------------|-------|------------|
| SkillOpt | 2605.23904 | 6 internal benchmarks |
| SkillEvolver | 2605.10500 | SkillsBench (arXiv:2602.12670), KernelBench |
| EvoSkill | 2603.02766 | OfficeQA, SealQA, BrowseComp |
| SkillMAS | 2605.09341 | Embodied / CLI / retail domains |
| Skill-MAS | 2606.18837 | DeepResearchBench, HLE-Math, BrowseComp-Plus, VitaBench |
| SkillGen | 2605.10999 | Includes PubMedQA |
| ReSkill | 2606.01619 | — (RL policy tasks, not named) |
| UCE | 2606.02304 | ALFWorld, WebShop |
| MetaForge | 2606.01801 | 12 benchmarks (multimodal) |
| Adaptive Auto-Harness | 2606.01770 | Prediction markets, security competitions, forecasting |
| FederatedSkill | 2606.03143 | 20 agent task families |
| SkillPyramid | 2606.03692 | ALFWorld, WebShop, ScienceWorld |
| EvoDS | 2606.03841 | Data science tasks (KDD 2026) |
| Parthenon Law | 2606.04602 | 12,510 legal agent trajectories |
| LifeSkill | 2606.04815 | LifelongAgentBench |
| SePO | 2606.04465 | Math, reasoning, science, code, logic |
| VASO | 2606.05395 | Robot task specification benchmarks |
| RHO | 2606.05922 | SWE-Bench Pro |
| OpenSkill | 2606.06741 | Open-world tasks (multiple) |
| Socratic-SWE | 2606.07412 | SWE-bench Verified |
| PACE | 2606.08106 | Agent self-evolution benchmarks |
| Bayesian-Agent | 2606.08348 | SOP-Bench, Lifelong AgentBench, RealFin-Bench |
| Co-Evolving Skill Gen | 2606.08755 | RL policy tasks |
| SkillHone | 2606.08671 | GAIA, WebWalkerQA-EN |
| SkeMex | 2606.09365 | Clinical tasks (medical) |
| SkillAxe | 2606.10546 | SkillsBench, SpreadsheetBench |
| Survey (Ding et al.) | 2606.11435 | — (survey; 6 benchmark categories reviewed) |
| SkillCAT | 2606.13317 | Spreadsheet, table-QA, document-analysis |
| EvoArena / EvoMem | 2606.13681 | EvoArena, GAIA |
| SkillAudit | 2606.14239 | 89 containerised tasks, 8 domains |
| ASSAY | 2606.15390 | AppWorld, tau-bench retail |
| VisualClaw | 2606.16295 | VisualClawArena (200 scenarios) |
| daVinci-kernel | 2606.16497 | KernelBench L1/L2/L3 |
| SkillWiki | 2606.16523 | Skill lifecycle evaluation |
| OPD-Evolver | 2606.17628 | Memory-augmented agent benchmarks |

| Benchmark | Integration status | Blocker |
|-----------|-------------------|---------|
| SkillsBench | Not integrated | Docker execution required for evaluation |
| KernelBench | Not integrated | GPU required for evaluation |

---

## Paper Analysis — Relevance, Importance, and Benchmark Comparisons

Reference section for positioning SAGE against the field.  Covers all 36
papers across three dimensions.

**Caveat on importance ratings:** All papers in this file are from 2025–2026
and mostly fall outside the knowledge cutoff (Jan 2025).  Citation counts
are unavailable.  Importance is estimated from proxy signals: institutional
affiliation, peer-reviewed venue acceptance, and known authors.

---

### Rating scales

**Relevance to SAGE** (1–5) — specifically *improving an existing skill
document*, not creating skills from scratch:

- 5 = Core focus is iteratively improving an existing skill text
- 4 = Substantial improvement loop, mixed with other concerns
- 3 = Relevant but also covers creation, memory, or unrelated scope
- 2 = Loosely related (infrastructure, benchmarks, tangential)
- 1 = Survey or benchmark only

**Importance signals** (★ / ★★ / ★★★):

- ★★★ = Top institution + peer-reviewed venue, or very well-known senior
  author (e.g. Gulwani, Chin-Yew Lin, Caiming Xiong, Kang Liu)
- ★★ = Good institution, preprint, reasonable scope
- ★ = Single author, unknown affiliation, or niche scope

---

### Master analysis table — original 7 papers

| Paper | arXiv | Relevance | Importance | Benchmarks used | Compares against |
|---|---|---|---|---|---|
| **SkillOpt** | 2605.23904 | 5/5 | ★★ | 6 internal benchmarks (direct-chat, Codex, Claude Code) | Not stated explicitly |
| **SkillEvolver** | 2605.10500 | 5/5 | ★★ (Renmin Univ., UVA) | **SkillsBench** (83 tasks), **KernelBench** | Human-curated skills, no-skill baseline |
| **EvoSkill** | 2603.02766 | 4/5 | ★★ (UMass Amherst) | **OfficeQA**, **SealQA**, **BrowseComp** | Static skill, no-skill baseline |
| **SkillMAS** | 2605.09341 | 5/5 | ★★ (Shanghai Jiao Tong + industry) | Embodied, CLI, retail workflow | Ablations of each module; utility learning variants |
| **Skill-MAS** | 2606.18837 | 4/5 | ★★★ (HKUST GZ + Ant Group) | **DeepResearchBench**, **HLE-Math**, **BrowseComp-Plus**, **VitaBench** | EvoAgent, AOrchestra, AFlow, MAS2, MAS-Orchestra |
| **SkillGen** | 2605.10999 | 3/5 | ★★★ (UNC + Microsoft Research; Xiangliang Zhang well-known) | **PubMedQA** + others | Baseline (no skill), static skill |
| **MUSE-Autoskill** | 2605.27366 | 2/5 | ★★ | Not documented | Not documented |

---

### Master analysis table — June 2026 wave (29 papers)

| Paper | arXiv | Relevance | Importance | Benchmarks used | Compares against |
|---|---|---|---|---|---|
| **ReSkill** | 2606.01619 | 5/5 | ★★ (Penn State + industry) | RL policy tasks (unnamed) | Policy-only, skill-only, no-skill baselines |
| **UCE** | 2606.02304 | 3/5 | ★★ (multiple Chinese universities) | **ALFWorld**, **WebShop** | Ablations of each context unit type |
| **MetaForge** | 2606.01801 | 3/5 | ★★ (Zhejiang Univ + others) | 12 multimodal benchmarks | 16 baselines (unnamed in summary) |
| **Adaptive Auto-Harness** | 2606.01770 | 3/5 | ★★★ (Michigan State + Huawei; Dakuo Wang / IBM Research well-known) | Prediction markets, security comps, forecasting | 5 baseline harness approaches |
| **FederatedSkill** | 2606.03143 | 4/5 | ★★★ (USC + Cisco Research; Shiyu Chang well-known) | 20 agent task families | Self-improving baselines, non-federated skill evolution |
| **SkillPyramid** | 2606.03692 | 4/5 | ★★★ (CAS + CASIA; Kang Liu very well-known) | **ALFWorld**, **WebShop**, **ScienceWorld** | Flat skill collection, no-reuse baseline |
| **EvoDS** | 2606.03841 | 4/5 | ★★★ (Peking Univ; **KDD 2026 accepted** — only peer-reviewed paper in the set) | Data science tasks (KDD benchmark suite) | AIDE, OpenHands, open-source data science agents |
| **Parthenon Law** | 2606.04602 | 4/5 | ★★ (independent / early-stage) | 12,510 legal trajectories | Frontier models w/o evolution (GPT-4o, Claude 3.5) |
| **LifeSkill** | 2606.04815 | 4/5 | ★★ (ECNU + others) | **LifelongAgentBench** | Static skill, no-skill, RL-only baselines |
| **SePO** | 2606.04465 | 3/5 | ★★ (NUS) | Math, reasoning, science, code, logic tasks | Fixed prompt, DSPy, OPRO, APE |
| **VASO** | 2606.05395 | 4/5 | ★★★ (UT Austin; Ufuk Topcu very well-known in formal methods) | Robot task specification benchmarks | Unverified skill evolution, no-skill robot baselines |
| **RHO** | 2606.05922 | 4/5 | ★★★ (Microsoft Research Asia; **Chin-Yew Lin** very well-known NLP researcher) | **SWE-Bench Pro** | Standard harness (no retro opt.), human-graded baselines |
| **OpenSkill** | 2606.06741 | 3/5 | ★★★ (UIC; Lichao Sun well-known) | Open-world task suites | No-skill, static skill, retrieval-only baselines |
| **Socratic-SWE** | 2606.07412 | 4/5 | ★★ (Alibaba DAMO) | **SWE-bench Verified** | SWE-agent, Agentless, Moatless, CodeAct |
| **PACE** | 2606.08106 | 4/5 | ★ (single author "Zayx Shawn", no affiliation listed) | Agent self-evolution suites | Greedy acceptance, hold-out splitting, cross-validation |
| **Bayesian-Agent** | 2606.08348 | 5/5 | ★★ (ICT CAS + others) | **SOP-Bench**, **Lifelong AgentBench**, **RealFin-Bench** | Non-Bayesian harness evolution, DSPy, PromptAgent |
| **Co-Evolving Skill Gen** | 2606.08755 | 3/5 | ★★ (Penn State + others) | RL policy task benchmarks | Separate skill gen, separate policy opt., combined static |
| **SkillHone** | 2606.08671 | 5/5 | ★★ (independent / small team) | **GAIA**, **WebWalkerQA-EN** | Commercial deep-research agent, static skill baselines |
| **SkeMex** | 2606.09365 | 4/5 | ★★ (Shanghai Jiao Tong med school) | Clinical task suites | Static expert skill, no-skill, retrieval-augmented |
| **SkillAxe** | 2606.10546 | 5/5 | ★★★ (**Sumit Gulwani** at Microsoft — inventor of FlashFill, extremely well-known) | **SkillsBench**, **SpreadsheetBench** | Human-authored skills, LLM-authored w/o self-refinement, SkillEvolver |
| **Survey (Ding et al.)** | 2606.11435 | 3/5 (survey) | ★★★ (Rutgers; Dimitris Metaxas well-known in vision/AI) | — reviews 6 benchmark categories | Survey: no direct comparison, reviews all methods |
| **SkillCAT** | 2606.13317 | 5/5 | ★★ (Wuhan Univ) | Spreadsheet, table-QA, document-analysis | CCE ablation, non-topology variants, SkillGen, SkillEvolver |
| **EvoArena / EvoMem** | 2606.13681 | 2/5 | ★★★ (NUS + Salesforce; **Caiming Xiong** very well-known; MIT) | **EvoArena** (novel benchmark), **GAIA** | Static memory, retrieval-only, no-adaptation baselines |
| **SkillAudit** | 2606.14239 | 5/5 | ★★★ (CAS + ICT; **Huawei Shen**, **Xueqi Cheng** very well-known in IR) | 89 containerised tasks, 8 professional domains | Static expert skill, no-skill, SkillOpt, SkillEvolver |
| **ASSAY** | 2606.15390 | 4/5 | ★★★ (UNC + Stanford; Huaxiu Yao well-known) | **AppWorld**, **tau-bench retail** | Full skill set (unfiltered), random selection baselines |
| **VisualClaw** | 2606.16295 | 3/5 | ★★★ (UCSC; Huaxiu Yao, Yuyin Zhou, Cihang Xie all well-known) | **VisualClawArena** (200 scenarios, novel benchmark) | Full-frame baselines, static skill databases |
| **daVinci-kernel** | 2606.16497 | 3/5 | ★★ (mid-tier Chinese institutions) | **KernelBench L1/L2/L3** | SkillEvolver, LLM-direct baselines |
| **SkillWiki** | 2606.16523 | 2/5 | ★★★ (Microsoft Research Asia; Jiang Bian well-known) | Skill lifecycle evaluation | No direct benchmark — infrastructure paper |
| **OPD-Evolver** | 2606.17628 | 4/5 | ★★★ (NUS; Wangchunshu Zhou, **Shuicheng Yan** / Sea AI Lab very well-known) | Memory-augmented agent benchmarks | Static memory, fast-loop-only, slow-loop-only ablations |

---

### Relevance ranking (top tier for SAGE positioning)

Papers with relevance 5/5 — all directly improve an existing skill document:

| Paper | arXiv | Key differentiator vs. SAGE |
|---|---|---|
| SkillOpt | 2605.23904 | Text-space optimizer; closest ancestor of GEPA |
| SkillEvolver | 2605.10500 | Meta-skill governs the refinement loop; SkillsBench baseline |
| SkillMAS | 2605.09341 | Co-evolves skill + topology jointly; utility-learning credit assignment |
| ReSkill | 2606.01619 | Explicit Thompson Sampling in an RL co-evolution loop |
| Bayesian-Agent | 2606.08348 | Feature-conditioned categorical posterior — generalises Beta-Bernoulli arms |
| SkillHone | 2606.08671 | Persistent decision history across sessions; GAIA results |
| SkillAxe | 2606.10546 | Four-dimension self-diagnosis; SkillsBench+SpreadsheetBench; **Gulwani** |
| SkillCAT | 2606.13317 | Training-free; contrastive causal extraction; topology-aware loading |
| SkillAudit | 2606.14239 | Ground-truth-free; solves Skill-MAS stated limitation; compares to SkillOpt+SkillEvolver |

---

### Benchmark connectivity — how to anchor SAGE comparisons

The following chain of papers share benchmarks, allowing SAGE to be
positioned transitively even without running every benchmark:

**SkillsBench chain:**
SkillEvolver (56.8 %) → SkillAxe (closes 47–67 % gap to human) →
daVinci-kernel → SAGE (if integrated)

**KernelBench chain:**
SkillEvolver (1.51× speedup, 3 tasks) → daVinci-kernel (37.2/70.6/32.2 %
on L1/L2/L3) → SAGE (if GPU available)

**SWE-bench chain:**
Socratic-SWE (50.40 % SWE-bench Verified, 3 iterations) →
RHO (SWE-Bench Pro 59 % → 78 %) → SAGE (if code scenario added)

**GAIA chain:**
SkillHone (+15.8 pts over commercial deep-research) →
EvoArena/EvoMem (+6.1 % on GAIA) → SAGE (recommended for integration)

**ALFWorld / WebShop chain:**
UCE (ALFWorld 75→96 %, WebShop 45→61 %) →
SkillPyramid (+38 % avg reward, −27.7 % steps) → SAGE (if env available)

**Closed comparison pairs** (papers that explicitly compare to each other):
- SkillAudit directly compares to SkillOpt and SkillEvolver
- SkillCAT directly compares to SkillGen and SkillEvolver
- SkillAxe directly compares to SkillEvolver
- daVinci-kernel directly compares to SkillEvolver

These four papers provide the tightest baseline chain for SAGE:
SkillEvolver is the common reference, and any SAGE result on SkillsBench,
KernelBench, or the held-out domain tasks can be directly positioned
against all four.

---

### Top 5 papers to read in depth for SAGE positioning

| Priority | Paper | arXiv | Why |
|---|---|---|---|
| 1 | **SkillAudit** | 2606.14239 | Ground-truth-free; solves Skill-MAS's stated limitation; closest methodological competitor; compares directly to SkillOpt + SkillEvolver |
| 2 | **SkillAxe** | 2606.10546 | Gulwani (Microsoft); SkillsBench + SpreadsheetBench; four-dimension self-diagnosis is most comparable to SAGE's rubrics mode |
| 3 | **Bayesian-Agent** | 2606.08348 | Parallel design to SAGE's Thompson Sampling; if community picks this up, SAGE's scheduler needs clear differentiation |
| 4 | **PACE** | 2606.08106 | Directly attacks the acceptance gate problem — SAGE's Bayesian gate is the alternative answer from a different statistical family |
| 5 | **SkillCAT** | 2606.13317 | Training-free, up to 40 %; explicitly compares to SkillGen and SkillEvolver, the same chain SAGE sits in |

---

### Papers not worth prioritising for SAGE comparison

| Paper | Reason |
|---|---|
| MUSE-Autoskill | Insufficient documentation; benchmarks unknown |
| MetaForge | Skill creation / tool forging, not improvement of existing text skill |
| Adaptive Auto-Harness | Diagnostic framework; no comparable benchmark to SAGE's scenarios |
| OpenSkill | Creation from scratch in open world; minimal improvement loop |
| EvoArena / EvoMem | Benchmark + memory evolution; not skill improvement |
| SkillWiki | Infrastructure paper; no performance comparison |
| VASO | Robotics + formal verification; different domain and evaluation stack |
| UCE | Skill is one of four context types; improvement is incidental |


