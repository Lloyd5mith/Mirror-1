from typing import List, Dict, Any
import time
import sys
from collections import Counter


META_PREFIX = "__meta__"


class MemEvent:
    def __init__(self, event_type: str, content: Any, timestamp: float = None):
        self.event_type = event_type
        self.content = content
        self.timestamp = timestamp if timestamp else time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.event_type,
            "content": self.content,
            "timestamp": self.timestamp
        }

    def to_log(self) -> str:
        ts = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        emoji = {
            "interpretation": "🧠",
            "input": "⌨️",
            "observer_feedback": "🪞",
            "memory_update": "📘",
            "goal": "🎯"
        }.get(self.event_type, "📍")
        return f"{emoji} [{ts}] {self.event_type.upper()}: {str(self.content)}"


class Memory:
    """
    Stores symbolic trace AND computes memory pressure.
    Pressure biases future interpretation and response.

    HARD RULE:
    - Meta tokens (starting with "__meta__") NEVER contribute to pressure,
      even if they slip through upstream.
    """

    def __init__(self, verbose: bool = True):
        self.trace: List[MemEvent] = []
        self.verbose = verbose
        self.symbol_counter: Counter[str] = Counter()

    def _filter_tokens(self, tokens: List[Any]) -> List[str]:
        out: List[str] = []
        for t in tokens or []:
            if not isinstance(t, str):
                continue
            if t.startswith(META_PREFIX):
                continue
            out.append(t)
        return out

    # --------------------------------------------------
    # STORE EVENTS
    # --------------------------------------------------

    def store(self, event_type: str, content: Any):
        event = MemEvent(event_type, content)
        self.trace.append(event)

        # Track symbolic pressure from interpretations (meta-filtered)
        if event_type == "interpretation" and isinstance(content, dict):
            tokens = self._filter_tokens(content.get("tokens", []))
            self.symbol_counter.update(tokens)

        if self.verbose:
            print(event.to_log(), file=sys.stdout)

    # --------------------------------------------------
    # PRESSURE MODEL
    # --------------------------------------------------

    def pressure_profile(self, window: int = 10) -> Dict[str, Any]:
        """
        Computes symbolic pressure from recent memory.
        Meta tokens are excluded.
        """
        recent = self.trace[-window:]
        recent_tokens: List[str] = []

        for e in recent:
            if e.event_type == "interpretation" and isinstance(e.content, dict):
                recent_tokens.extend(self._filter_tokens(e.content.get("tokens", [])))

        freq = Counter(recent_tokens)

        dominant = [
            sym for sym, count in freq.items()
            if count >= 3 and len(freq) > 1
        ]

        return {
            "recent_frequency": dict(freq),
            "dominant_symbols": dominant,
            "global_frequency": dict(self.symbol_counter),
        }

    # --------------------------------------------------
    # SUMMARY (SAFE)
    # --------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        for event in reversed(self.trace):
            if event.event_type == "interpretation" and isinstance(event.content, dict):
                return {
                    "input": event.content.get("input"),
                    "tokens": self._filter_tokens(event.content.get("tokens", [])),
                    "goals": event.content.get("goals", []),
                }
        return {}

    # --------------------------------------------------
    # RESET
    # --------------------------------------------------

    def reset(self):
        self.trace.clear()
        self.symbol_counter.clear()