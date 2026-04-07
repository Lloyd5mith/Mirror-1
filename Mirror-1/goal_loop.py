# goal_loop.py
from typing import List, Dict, Any, Optional
import time


class GoalLoop:

    SELF_GOAL = "Maintain coherent self-model across time"

    def __init__(self, cfg: Optional[Dict[str, Any]] = None):
        self.cfg = cfg or {}
        self.goals: List[Dict[str, Any]] = []

        self._events = {
            "achieved": [],
            "abandoned": [],
        }

        self._achieve_after = 3
        self._abandon_after = 6

    # --------------------------------------------------

    def set_goal(self, goal: str, priority: int = 1, source: str = "inferred"):
        if self._goal_exists(goal):
            return

        self.goals.append({
            "goal": goal,
            "priority": priority,
            "state": "pending",
            "source": source,
            "created_at": time.time(),
            "resolved_at": None,
            "attempts": 0,
        })

    def ensure_self_goal(self):
        self.set_goal(
            goal=self.SELF_GOAL,
            priority=10,
            source="self-loop",
        )

    # --------------------------------------------------

    def evaluate(self) -> List[str]:
        active = [g for g in self.goals if g["state"] == "pending"]
        active.sort(key=lambda g: g["priority"], reverse=True)
        return [g["goal"] for g in active]

    # --------------------------------------------------

    def update_from_interpretation(self, interpretation: Dict[str, Any]):
        detected = interpretation.get("goals", []) or []

        for g in self.goals:
            if g["state"] != "pending":
                continue

            if g["goal"] == self.SELF_GOAL:
                g["attempts"] += 1
                continue

            if g["goal"] in detected:
                g["attempts"] += 1
                if g["attempts"] >= self._achieve_after:
                    self._mark_achieved(g)
            else:
                g["attempts"] += 1
                if g["attempts"] >= self._abandon_after:
                    self._mark_abandoned(g)

    # --------------------------------------------------

    def coherence_score(self) -> float:
        for g in self.goals:
            if g["goal"] == self.SELF_GOAL and g["state"] == "pending":
                # Soft asymptotic rise instead of hard plateau
                return round(1 - (1 / (1 + g["attempts"])), 3)
        return 0.0

    # --------------------------------------------------

    def consume_events(self):
        out = {
            "achieved": self._events["achieved"][:],
            "abandoned": self._events["abandoned"][:],
        }
        self._events["achieved"].clear()
        self._events["abandoned"].clear()
        return out

    # --------------------------------------------------

    def _mark_achieved(self, goal_obj):
        goal_obj["state"] = "achieved"
        goal_obj["resolved_at"] = time.time()
        self._events["achieved"].append(goal_obj["goal"])

    def _mark_abandoned(self, goal_obj):
        goal_obj["state"] = "abandoned"
        goal_obj["resolved_at"] = time.time()
        self._events["abandoned"].append(goal_obj["goal"])

    def _goal_exists(self, goal: str) -> bool:
        return any(g["goal"] == goal for g in self.goals)
