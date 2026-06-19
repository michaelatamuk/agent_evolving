from __future__ import annotations

import json
import math
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ── Shared Beta arm ───────────────────────────────────────────────────────────

@dataclass
class _BetaArm:
    skill_name: str
    alpha: float = 1.0   # prior + weighted successes
    beta: float = 1.0    # prior + weighted failures
    n_runs: int = 0
    # Phase 2: timestamp of the last successful run (unix seconds), or None
    last_success_at: Optional[float] = field(default=None)

    # ── Binary update (original behaviour) ───────────────────────────────────

    def update(self, improvement: float) -> None:
        """Binary update: α += 1 if improvement > 0, else β += 1."""
        self.n_runs += 1
        if improvement > 0.0:
            self.alpha += 1.0
            self.last_success_at = time.time()
        else:
            self.beta += 1.0

    # ── Soft update (Phase 2) ─────────────────────────────────────────────────

    def soft_update(self, reward: float) -> None:
        """Soft update: α += reward, β += (1 − reward).

        *reward* should be in [0, 1].  A value of 1.0 is a perfect success;
        0.0 is a total failure; anything in between gives a fractional update.
        This preserves more information than the binary update and prevents
        a single large improvement from dominating the posterior.

        Compatible with the six-component reward signal from the algorithm::

            reward = clamp(
                a1*objective_success + a2*metric_improvement + … − a5*recurrence,
                0, 1
            )
        """
        reward = max(0.0, min(1.0, reward))
        self.n_runs += 1
        self.alpha += reward
        self.beta  += 1.0 - reward
        if reward > 0.5:
            self.last_success_at = time.time()

    # ── Decay toward prior (Phase 3) ──────────────────────────────────────────

    def decay(self, rate: float = 0.99) -> None:
        """Shrink α and β back toward the uninformative prior Beta(1, 1).

        ``rate`` is the retention fraction: 1.0 = no decay, 0.0 = full reset.
        Calling this once per batch run with rate=0.99 ensures that very old
        evidence is gradually forgotten without a hard reset.

        Formula: α ← 1 + rate × (α − 1), and analogously for β.
        The surplus above the prior (the evidence mass) is multiplied by
        *rate* at each call.
        """
        self.alpha = 1.0 + rate * (self.alpha - 1.0)
        self.beta  = 1.0 + rate * (self.beta  - 1.0)

    # ── Sampling and statistics ───────────────────────────────────────────────

    def sample(self) -> float:
        """Draw θ ~ Beta(α, β)."""
        return random.betavariate(self.alpha, self.beta)

    @property
    def mean(self) -> float:
        """Posterior mean E[θ] = α / (α + β)."""
        return self.alpha / (self.alpha + self.beta)

    def freshness(self, lambda_: float = 0.05) -> float:
        """Exponential freshness: exp(−λ × days_since_last_success).

        Returns 1.0 for skills that have never succeeded (neutral — we do not
        penalise unexplored skills).  Returns values in (0, 1] otherwise.

        Parameters
        ----------
        lambda_ : float
            Decay rate per day.  Suggested range: 0.01 (slow) – 0.1 (fast).
            0.05 ≈ half-life of ~14 days.
        """
        if self.last_success_at is None:
            return 1.0
        age_days = (time.time() - self.last_success_at) / 86_400.0
        return math.exp(-lambda_ * age_days)


# ── Thompson Sampling scheduler ───────────────────────────────────────────────

class ThompsonSkillScheduler:
    """Prioritise skills by Thompson Sampling over Beta(α, β) distributions.

    Each skill has an arm.  ``schedule()`` draws one Beta sample per arm and
    returns skills sorted by their sample (highest first).  This means skills
    that have historically improved most are likely to be scheduled first,
    while under-explored skills still occasionally bubble to the top.

    State is persisted to ``<state_dir>/ts_skill_scheduler.json`` so arm
    history survives between CLI invocations.
    """

    _STATE_FILE = "ts_skill_scheduler.json"

    def __init__(
        self,
        skills_root: Path,
        state_dir: Optional[Path] = None,
    ) -> None:
        self._skills_root = Path(skills_root)
        self._state_dir = Path(state_dir) if state_dir else self._skills_root
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._arms: Dict[str, _BetaArm] = {}
        self._load()
        self._bootstrap_from_metrics()

    # ── Persistence ──────────────────────────────────────────────────────────

    def _state_path(self) -> Path:
        return self._state_dir / self._STATE_FILE

    def _load(self) -> None:
        path = self._state_path()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text())
            for name, d in data.items():
                self._arms[name] = _BetaArm(
                    skill_name=name,
                    alpha=float(d.get("alpha", 1.0)),
                    beta=float(d.get("beta", 1.0)),
                    n_runs=int(d.get("n_runs", 0)),
                    last_success_at=d.get("last_success_at"),  # Phase 2
                )
        except Exception:
            pass

    def save(self) -> None:
        """Atomically persist arm state to disk."""
        path = self._state_path()
        tmp = path.with_suffix(".tmp")
        data: dict = {}
        for name, arm in self._arms.items():
            entry: dict = {
                "alpha":  arm.alpha,
                "beta":   arm.beta,
                "n_runs": arm.n_runs,
            }
            if arm.last_success_at is not None:      # Phase 2
                entry["last_success_at"] = arm.last_success_at
            data[name] = entry
        tmp.write_text(json.dumps(data, indent=2))
        tmp.rename(path)

    def _bootstrap_from_metrics(self) -> None:
        """Seed arm params from existing stage11 metrics.json files.

        Expected layout: ``<skills_root>/<skill_name>/<timestamp>/metrics.json``
        Allows the scheduler to start informed even on the very first batch run
        after Thompson Sampling is introduced (avoids a cold-start penalty for
        skills that already have evolution history).
        """
        if not self._skills_root.exists():
            return
        for metrics_file in self._skills_root.rglob("metrics.json"):
            try:
                # …/<skill_name>/<timestamp>/metrics.json  → parent.parent.name
                skill_name = metrics_file.parent.parent.name
            except Exception:
                continue
            if skill_name in self._arms:
                continue  # already loaded from state file
            try:
                m = json.loads(metrics_file.read_text())
                improvement = float(m.get("improvement", 0.0))
                arm = self._arms.setdefault(skill_name, _BetaArm(skill_name=skill_name))
                arm.update(improvement)
            except Exception:
                pass

    # ── Public interface ──────────────────────────────────────────────────────

    def register(self, skill_names: List[str]) -> None:
        """Ensure every skill has an arm (cold-start = Beta(1, 1))."""
        for name in skill_names:
            self._arms.setdefault(name, _BetaArm(skill_name=name))

    def schedule(self, skill_names: List[str]) -> List[str]:
        """Return *skill_names* sorted by a single Beta sample (highest first).

        Skills with a strong improvement track-record are likely to appear
        early; unexplored skills retain a chance to be prioritised.
        """
        self.register(skill_names)
        return sorted(
            skill_names,
            key=lambda n: self._arms[n].sample(),
            reverse=True,
        )

    def record(self, skill_name: str, improvement: float) -> None:
        """Binary update: improvement > 0 → α += 1, else β += 1."""
        arm = self._arms.setdefault(skill_name, _BetaArm(skill_name=skill_name))
        arm.update(improvement)
        self.save()

    def record_soft(self, skill_name: str, reward: float) -> None:
        """Soft update (Phase 2): α += reward, β += (1 − reward).

        *reward* should be in [0, 1].  Preserves more information than the
        binary ``record()`` because the fractional improvement magnitude is
        reflected in the posterior rather than being thresholded at 0.

        Use this in place of ``record()`` when you have a continuous reward
        signal from the six-component reward formula::

            reward = clamp(
                a1*objective_success + a2*metric_improvement + …,
                0, 1,
            )
        """
        arm = self._arms.setdefault(skill_name, _BetaArm(skill_name=skill_name))
        arm.soft_update(reward)
        self.save()

    def apply_decay(self, rate: float = 0.99) -> None:
        """Decay all arm evidence toward the uninformative prior (Phase 3).

        Call once per batch run to prevent historical evidence from dominating
        forever.  ``rate=0.99`` loses ~1 % of evidence per call; after 100
        batch runs the arm is at ~37 % of its original evidence mass.

        Parameters
        ----------
        rate : float
            Retention fraction in (0, 1].  1.0 = no decay, 0.99 = slow,
            0.90 = fast (≈ half-life of 7 calls).
        """
        for arm in self._arms.values():
            arm.decay(rate)
        self.save()

    def rankings(self) -> List[Tuple[str, float]]:
        """Return (skill_name, posterior_mean) sorted best-first."""
        return sorted(
            [(name, arm.mean) for name, arm in self._arms.items()],
            key=lambda x: x[1],
            reverse=True,
        )
