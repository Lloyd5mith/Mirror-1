from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CommitGateConfig:
    consecutive_required: int = 25
    min_integrity: float = 0.78
    allowed_modes: tuple[str, ...] = ("stabilized",)
    block_if_intervening: bool = True
    min_turns_before_lock: int = 1200
    min_candidate_strength: float = 0.65
    min_strength_margin: float = 0.05
    min_context_diversity: int = 8
    require_leader_to_be_self: bool = True


class SelfModel:

    ALLOWED_INVARIANTS = ("self",)

    def __init__(self):
        self.state: Dict[str, Any] = {
            "mode": "exploratory",
            "active_goals": [],
            "dominant_symbols": [],
            "reinforced_symbols": [],
            "integrity_score": 0.0,
        }

        self.cfg = CommitGateConfig()

        self.locked_invariant: Optional[str] = None
        self.binding_strength: float = 0.0
        self.binding_decay: float = 0.95

        self._candidate: Optional[str] = None
        self._candidate_streak: int = 0

    # ==================================================
    # MODE UPDATE
    # ==================================================

    def update(
        self,
        active_goals: List[str],
        dominant_symbols: List[str],
        reinforced_symbols: List[str],
        integrity_score: float,
    ):
        integrity_score = float(integrity_score or 0.0)

        mode = "exploratory"
        if dominant_symbols:
            mode = "narrowing"
        if integrity_score >= 0.6 and dominant_symbols:
            mode = "stabilized"

        self.state = {
            "mode": mode,
            "active_goals": active_goals,
            "dominant_symbols": dominant_symbols,
            "reinforced_symbols": reinforced_symbols,
            "integrity_score": integrity_score,
        }

    # ==================================================
    # BINDING DYNAMICS
    # ==================================================

    def update_binding(self, reinforced_this_turn: bool):
        if reinforced_this_turn:
            self.binding_strength = min(1.0, self.binding_strength + 0.15)
        else:
            self.binding_strength *= self.binding_decay

        self.binding_strength = max(0.0, min(1.0, self.binding_strength))

    # ==================================================
    # COMMIT GATE
    # ==================================================

    def observe_commit_gate(
        self,
        candidate_symbol: Optional[str],
        integrity_score: float,
        intervention_action: str = "none",
        turn: int = 0,
        candidate_strength: float = 0.0,
        runner_up_strength: float = 0.0,
        context_diversity: int = 0,
        leader_symbol: Optional[str] = None,
    ) -> Dict[str, Any]:

        if self.locked_invariant is not None:
            return {"action": "none", "reason": "already_locked"}

        mode = self.state.get("mode", "unknown")
        integrity_score = float(integrity_score or 0.0)
        candidate_strength = float(candidate_strength or 0.0)
        runner_up_strength = float(runner_up_strength or 0.0)
        margin = candidate_strength - runner_up_strength
        turn = int(turn or 0)
        context_diversity = int(context_diversity or 0)

        if self.cfg.block_if_intervening and intervention_action != "none":
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "intervention_block"}

        if turn < self.cfg.min_turns_before_lock:
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "turn_floor"}

        if self.cfg.require_leader_to_be_self and leader_symbol != "self":
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "self_not_leader"}

        if (
            not candidate_symbol
            or candidate_symbol not in self.ALLOWED_INVARIANTS
        ):
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "invalid_candidate"}

        if integrity_score < self.cfg.min_integrity:
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "integrity_low"}

        if mode not in self.cfg.allowed_modes:
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "mode_not_allowed"}

        if candidate_strength < self.cfg.min_candidate_strength:
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "candidate_strength_low"}

        if margin < self.cfg.min_strength_margin:
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "margin_too_small"}

        if context_diversity < self.cfg.min_context_diversity:
            self._candidate = None
            self._candidate_streak = 0
            return {"action": "none", "reason": "context_diversity_low"}

        if self._candidate == candidate_symbol:
            self._candidate_streak += 1
        else:
            self._candidate = candidate_symbol
            self._candidate_streak = 1

        if self._candidate_streak >= self.cfg.consecutive_required:
            self.locked_invariant = candidate_symbol
            return {
                "action": "lock_invariant",
                "symbol": candidate_symbol,
                "streak": self._candidate_streak,
                "margin": round(margin, 4),
                "candidate_strength": round(candidate_strength, 4),
                "runner_up_strength": round(runner_up_strength, 4),
                "context_diversity": context_diversity,
                "leader_symbol": leader_symbol,
            }

        return {
            "action": "none",
            "streak": self._candidate_streak,
            "margin": round(margin, 4),
            "candidate_strength": round(candidate_strength, 4),
            "runner_up_strength": round(runner_up_strength, 4),
            "context_diversity": context_diversity,
            "leader_symbol": leader_symbol,
        }