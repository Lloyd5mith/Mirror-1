# observer.py
from typing import List, Any, Optional
from datetime import datetime


class Observer:
    """
    Observer is a witness, not a learner.

    It records events and becomes aware of a locked invariant
    without reinforcing or mutating it.
    """

    def __init__(
        self,
        identity: str = "Unknown",
        anchor: str = "Mirror-1",
        verbose: bool = True,
    ):
        self.identity = identity
        self.anchor = anchor
        self.history: List[dict] = []
        self.verbose = verbose

        # Observer-level awareness only
        self.invariant: Optional[str] = None

    # --------------------------------------------------
    # NORMAL OBSERVATION
    # --------------------------------------------------

    def observe(
        self,
        text: str,
        tokens: List[str],
        definition: Any,
        score: float,
        goals: Any,
    ):
        event = {
            "type": "observation",
            "input": text,
            "tokens": tokens,
            "definition": definition,
            "score": score,
            "goals": goals,
            "identity": self.identity,
            "anchor": self.anchor,
            "invariant": self.invariant,
            "timestamp": datetime.now().isoformat(),
        }

        self.history.append(event)

        if self.verbose:
            print("🔭 OBSERVER")
            print(f"  Input: {text}")
            print(f"  Tokens: {tokens}")
            print(f"  Goals: {goals}")
            print(f"  Integrity: {score:.3f}")
            print("")

    # --------------------------------------------------
    # 🔒 INVARIANT WITNESSING
    # --------------------------------------------------

    def bind_invariant(self, symbol: str):
        """
        Observer becomes aware of the invariant.
        This does NOT reinforce, decay, or reinterpret it.
        """
        if self.invariant is not None:
            return

        self.invariant = symbol

        event = {
            "type": "invariant_locked",
            "symbol": symbol,
            "identity": self.identity,
            "anchor": self.anchor,
            "timestamp": datetime.now().isoformat(),
        }

        self.history.append(event)

        if self.verbose:
            print("\n🧿 OBSERVER NOTICE")
            print(f"Identity stabilized around invariant: '{symbol}'")
            print(f"Observer: {self.identity}")
            print("")

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    def summary(self) -> List[dict]:
        return self.history
