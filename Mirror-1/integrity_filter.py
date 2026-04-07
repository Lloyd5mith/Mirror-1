# integrity_filter.py
from typing import Dict, Any, List
import time


class IntegrityFilter:
    """
    Mirror-1′
    Hard constraint layer governing structural safety.
    """

    def __init__(self):
        self.last_intervention: float = 0.0
        self.cooldown_seconds: float = 5.0

        self.integrity_history: List[float] = []
        self.mode_history: List[str] = []
        self.goal_history: List[str] = []

    # --------------------------------------------------
    # UPDATE OBSERVATIONS
    # --------------------------------------------------

    def observe(
        self,
        integrity_score: float,
        mode: str,
        active_goals: List[str],
        dominant_symbols: List[str],
    ):
        self.integrity_history.append(integrity_score)
        self.mode_history.append(mode)
        self.goal_history.extend(active_goals)

        self.integrity_history = self.integrity_history[-10:]
        self.mode_history = self.mode_history[-10:]
        self.goal_history = self.goal_history[-10:]

    # --------------------------------------------------
    # CONSECUTIVE CHECK HELPER
    # --------------------------------------------------

    def _last_n_all(self, seq: List[str], value: str, n: int) -> bool:
        if len(seq) < n:
            return False
        return all(x == value for x in seq[-n:])

    # --------------------------------------------------
    # SAFETY EVALUATION
    # --------------------------------------------------

    def evaluate(self) -> Dict[str, Any]:
        now = time.time()
        if now - self.last_intervention < self.cooldown_seconds:
            return {"action": "none"}

        # 1️⃣ Integrity decay (3 consecutive drops)
        if len(self.integrity_history) >= 3:
            if (
                self.integrity_history[-1]
                < self.integrity_history[-2]
                < self.integrity_history[-3]
            ):
                return self._intervene("integrity_decay")

        # 2️⃣ Runaway narrowing (3 consecutive narrowing)
        if self._last_n_all(self.mode_history, "narrowing", 3):
            return self._intervene("runaway_narrowing")

        # 3️⃣ Goal fixation (no diversity)
        if len(set(self.goal_history)) <= 1 and len(self.goal_history) >= 4:
            return self._intervene("goal_fixation")

        # 4️⃣ Over-stabilization (3 consecutive stabilized)
        if self._last_n_all(self.mode_history, "stabilized", 3):
            return self._intervene("symbolic_lock")

        return {"action": "none"}

    # --------------------------------------------------
    # INTERVENTION
    # --------------------------------------------------

    def _intervene(self, reason: str) -> Dict[str, Any]:
        self.last_intervention = time.time()

        if reason in ("runaway_narrowing", "symbolic_lock"):
            return {
                "action": "downgrade_mode",
                "target_mode": "exploratory",
                "reason": reason,
            }

        if reason == "goal_fixation":
            return {
                "action": "inject_goal",
                "goal": "Re-open interpretive space",
                "reason": reason,
            }

        if reason == "integrity_decay":
            return {
                "action": "block_reinforcement",
                "duration": self.cooldown_seconds,
                "reason": reason,
            }

        return {"action": "none"}
