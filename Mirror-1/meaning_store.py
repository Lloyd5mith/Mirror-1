from __future__ import annotations

from typing import List, Dict, Any, Optional, Iterable, Tuple


class MeaningStore:
    """
    Stores and evolves symbolic meaning.

    Features:
    - Usage-based emergence
    - Goal → meaning reinforcement
    - Soft stabilization (strength-based, reversible)
    - Continuous decay (entropy)
    - Dominance query
    - Competitive leader queries
    - Invariant locking (exactly one invariant)
    - Deterministic behavior
    """

    META_PREFIX = "__meta__"

    def __init__(self, decay_rate: float = 0.02):
        self.definitions: Dict[str, str] = {
            "loop": "A process that repeats based on previous state.",
            "mirror": "A reflective structure that interprets and updates meaning.",
            "integrity": "The internal consistency and ethical alignment of meaning.",
        }

        self.usage_count: Dict[str, int] = {}
        self.context_map: Dict[str, List[List[str]]] = {}

        self.stable_strength: Dict[str, float] = {}
        self.reinforcement_strength: Dict[str, float] = {}

        self.invariant_symbol: Optional[str] = None
        self.invariants: Dict[str, str] = {}

        self.decay_rate = float(decay_rate)
        self.stabilize_threshold = 3
        self.commit_threshold = 0.8

        self.goal_symbol_map: Dict[str, str] = {
            "Define reflection logic": "mirror",
            "Trace previous meaning loops": "recursion",
            "Bind observer to current interpretation": "observer",
            "Determine first symbolic state": "origin",
            "Evaluate symbolic recursion": "loop",
        }

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def _is_meta(self, token: str) -> bool:
        return isinstance(token, str) and token.startswith(self.META_PREFIX)

    def _filtered_tokens(self, tokens: List[str]) -> List[str]:
        return [t for t in tokens if t and not self._is_meta(t)]

    # --------------------------------------------------
    # EXTRACTION
    # --------------------------------------------------

    def extract(self, tokens: List[str], memory_trace: Any = None) -> Dict[str, Any]:
        found: Dict[str, str] = {}
        tokens = self._filtered_tokens(tokens)

        for t in tokens:
            self._observe_usage(t, tokens)
            if t in self.invariants:
                found[t] = self.invariants[t]
            elif t in self.definitions:
                found[t] = self.definitions[t]

        stabilized = [
            s for s, strength in self.stable_strength.items()
            if strength >= self.commit_threshold
        ]

        return {
            "definitions": found,
            "stabilized": stabilized,
        }

    # --------------------------------------------------
    # USAGE-BASED MEANING EMERGENCE
    # --------------------------------------------------

    def _observe_usage(self, token: str, context: List[str]):
        if self._is_meta(token):
            return

        self.usage_count[token] = self.usage_count.get(token, 0) + 1
        self.context_map.setdefault(token, []).append(context)

        if self.usage_count[token] == self.stabilize_threshold:
            self._stabilize(token, base_strength=1.0)

    def _stabilize(self, token: str, base_strength: float = 1.0):
        if self._is_meta(token):
            return

        if token not in self.definitions and token not in self.invariants:
            contexts = self.context_map.get(token, [])
            flattened = set(
                x for ctx in contexts for x in ctx
                if x != token and not self._is_meta(x)
            )
            inferred = (
                f"{token} emerges as a symbolic node related to: {', '.join(sorted(flattened))}"
                if flattened else
                f"{token} emerges as a recurrent symbolic element."
            )
            self.definitions[token] = inferred

        self.stable_strength[token] = self.stable_strength.get(token, 0.0) + float(base_strength)

    # --------------------------------------------------
    # GOAL → MEANING REINFORCEMENT
    # --------------------------------------------------

    def reinforce_from_goal(self, achieved_goal: str, tokens: List[str]) -> Dict[str, Any]:
        """
        Strengthen meaning when a goal is achieved.
        After invariant lock, the invariant itself is no longer further amplified.
        """
        tokens = self._filtered_tokens(tokens)
        anchor = self.goal_symbol_map.get(achieved_goal)
        symbol: Optional[str] = None

        if anchor and anchor in tokens:
            symbol = anchor
        else:
            freq: Dict[str, int] = {}
            for t in tokens:
                freq[t] = freq.get(t, 0) + 1
            if freq:
                max_count = max(freq.values())
                for t in tokens:
                    if freq.get(t, 0) == max_count:
                        symbol = t
                        break

        if not symbol or self._is_meta(symbol):
            return {"reinforced": None, "definition": None}

        if self.invariant_symbol is not None and symbol == self.invariant_symbol:
            return {
                "reinforced": None,
                "definition": self.invariants.get(symbol),
                "reason": "locked_invariant_no_growth",
            }

        self.reinforcement_strength[symbol] = self.reinforcement_strength.get(symbol, 0.0) + 1.0
        self.stable_strength[symbol] = self.stable_strength.get(symbol, 0.0) + 0.5

        base = (
            self.invariants.get(symbol)
            or self.definitions.get(symbol)
            or f"{symbol} is an emerging symbolic construct."
        )
        strengthened = f"{base} (reinforced via achieved goal: '{achieved_goal}')"

        if symbol in self.invariants:
            strengthened = self.invariants[symbol]
        else:
            self.definitions[symbol] = strengthened

        return {"reinforced": symbol, "definition": strengthened}

    # --------------------------------------------------
    # STRUCTURAL REINFORCEMENT
    # --------------------------------------------------

    def reinforce_token(self, token: str, amount: float = 0.6, reason: str = "structural") -> Dict[str, Any]:
        if not token or self._is_meta(token):
            return {"reinforced": None, "reason": "invalid_token"}

        token = str(token)

        if self.invariant_symbol is not None and token == self.invariant_symbol:
            return {"reinforced": None, "reason": "locked_invariant_no_growth"}

        self.reinforcement_strength[token] = self.reinforcement_strength.get(token, 0.0) + float(amount)
        self.stable_strength[token] = self.stable_strength.get(token, 0.0) + (0.25 * float(amount))

        if token not in self.definitions and token not in self.invariants:
            self.definitions[token] = f"{token} emerges as a recurrent symbolic element."

        return {"reinforced": token, "amount": float(amount), "reason": reason}

    # --------------------------------------------------
    # DECAY / FORGETTING
    # --------------------------------------------------

    def decay(self):
        for sym in list(self.stable_strength.keys()):
            if sym in self.invariants:
                continue
            self.stable_strength[sym] *= (1.0 - self.decay_rate)
            if self.stable_strength[sym] < 0.05:
                del self.stable_strength[sym]

        for sym in list(self.reinforcement_strength.keys()):
            if sym in self.invariants:
                continue
            self.reinforcement_strength[sym] *= (1.0 - self.decay_rate)
            if self.reinforcement_strength[sym] < 0.05:
                del self.reinforcement_strength[sym]

    # --------------------------------------------------
    # DOMINANCE / COMPETITION HELPERS
    # --------------------------------------------------

    def dominant_symbols(self) -> List[str]:
        out = [
            sym for sym, strength in self.reinforcement_strength.items()
            if strength >= self.commit_threshold and not self._is_meta(sym)
        ]
        return sorted(out)

    def symbol_strength(self, symbol: str) -> float:
        if not symbol or self._is_meta(symbol):
            return 0.0
        return float(self.reinforcement_strength.get(symbol, 0.0))

    def leading_symbol(self, candidates: Optional[Iterable[str]] = None) -> Tuple[Optional[str], float]:
        if candidates is None:
            items = [
                (sym, float(strength))
                for sym, strength in self.reinforcement_strength.items()
                if not self._is_meta(sym)
            ]
        else:
            allowed = set(candidates)
            items = [
                (sym, float(self.reinforcement_strength.get(sym, 0.0)))
                for sym in allowed
                if not self._is_meta(sym)
            ]

        if not items:
            return None, 0.0

        items.sort(key=lambda x: (-x[1], x[0]))
        return items[0]

    def runner_up_strength(self, exclude: Optional[str] = None) -> float:
        strengths = []
        for sym, strength in self.reinforcement_strength.items():
            if self._is_meta(sym):
                continue
            if exclude is not None and sym == exclude:
                continue
            strengths.append(float(strength))
        return max(strengths) if strengths else 0.0

    def runner_up_strength_among(
        self,
        candidates: Iterable[str],
        exclude: Optional[str] = None,
    ) -> float:
        strengths = []
        for sym in candidates:
            if self._is_meta(sym):
                continue
            if exclude is not None and sym == exclude:
                continue
            strengths.append(float(self.reinforcement_strength.get(sym, 0.0)))
        return max(strengths) if strengths else 0.0

    def context_diversity(self, symbol: str) -> int:
        if not symbol or self._is_meta(symbol):
            return 0

        contexts = self.context_map.get(symbol, [])
        unique_contexts = set()

        for ctx in contexts:
            filtered = tuple(sorted(set(self._filtered_tokens(ctx))))
            if filtered:
                unique_contexts.add(filtered)

        return len(unique_contexts)

    # --------------------------------------------------
    # INVARIANT LOCKING
    # --------------------------------------------------

    def lock_invariant(self, symbol: str) -> Dict[str, Any]:
        if not symbol or self._is_meta(symbol):
            return {"locked": None, "reason": "invalid_symbol"}

        if self.invariant_symbol is not None:
            return {
                "locked": None,
                "reason": "already_locked",
                "invariant": self.invariant_symbol,
            }

        definition = self.definitions.get(symbol) or f"{symbol} is a fixed invariant."

        self.invariant_symbol = symbol
        self.invariants[symbol] = definition

        self.stable_strength[symbol] = max(
            self.stable_strength.get(symbol, 0.0),
            self.commit_threshold,
        )
        self.reinforcement_strength[symbol] = max(
            self.reinforcement_strength.get(symbol, 0.0),
            self.commit_threshold,
        )

        return {"locked": symbol, "definition": definition}

    # --------------------------------------------------
    # EXPLICIT EXTENSION
    # --------------------------------------------------

    def extend(self, keyword: str, definition: str):
        if not keyword or self._is_meta(keyword):
            return
        self.definitions[keyword] = definition
        self.stable_strength[keyword] = max(
            self.stable_strength.get(keyword, 0.0),
            self.commit_threshold,
        )

    # --------------------------------------------------
    # INTROSPECTION
    # --------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        return {
            "known_definitions": list(self.definitions.keys()),
            "invariant_symbol": self.invariant_symbol,
            "invariants": dict(self.invariants),
            "stable_symbols": {k: round(v, 3) for k, v in self.stable_strength.items()},
            "reinforcement_strength": {k: round(v, 3) for k, v in self.reinforcement_strength.items()},
            "usage_counts": dict(self.usage_count),
            "context_diversity": {k: self.context_diversity(k) for k in self.context_map.keys()},
        }
