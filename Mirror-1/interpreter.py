from typing import Dict, Any, List
from collections import Counter

from tokenizer import tokenize


class Interpreter:
    """
    Interprets input through symbolic memory pressure AND reinforced meaning.
    Reinforced symbols bias parsing, but with bounded influence to preserve stability.
    """

    def __init__(self, cfg, memory, meaning_store, integrity):
        self.cfg = cfg
        self.memory = memory
        self.meaning_store = meaning_store
        self.integrity = integrity

    # --------------------------------------------------
    # MAIN ENTRY
    # --------------------------------------------------

    def interpret(self, input_text: str) -> Dict[str, Any]:
        raw_tokens = tokenize(input_text)

        # Apply symbolic bias (memory + reinforcement)
        biased_tokens = self._apply_symbolic_bias(raw_tokens)

        definitions = self._define(biased_tokens)
        goals = self._infer_goals(biased_tokens)

        relations = []

        if len(biased_tokens) >= 3:
            for i in range(len(biased_tokens) - 2):
                a = biased_tokens[i]
                rel = biased_tokens[i + 1]
                b = biased_tokens[i + 2]
                relations.append((a, rel, b))

        return {
            "input": input_text,
            "raw_tokens": raw_tokens,
            "tokens": biased_tokens,
            "relations": relations,
            "definitions": definitions,
            "score": float(self.integrity.score(input_text)),
            "goals": goals,
        }

    # --------------------------------------------------
    # SYMBOLIC BIASING (CORE MIRROR-1 LOGIC)
    # --------------------------------------------------

    def _apply_symbolic_bias(self, tokens: List[str]) -> List[str]:
        """
        Bias tokens using:
        1. Reinforced meaning (long-term, bounded)
        2. Memory pressure (short-term dominance)
        """

        # --- Memory pressure (defensive) ---
        pressure = {}
        if hasattr(self.memory, "pressure_profile"):
            pressure = self.memory.pressure_profile() or {}

        dominant = set(pressure.get("dominant_symbols", []))

        # --- Reinforced meaning (long-term learning) ---
        reinforced_strength = getattr(
            self.meaning_store,
            "reinforcement_strength",
            {}
        )
        reinforced = set(reinforced_strength.keys())

        biased: List[str] = []

        for t in tokens:
            biased.append(t)

            # Tier 1: Reinforced symbols (bounded, saturating)
            if t in reinforced:
                strength = float(reinforced_strength.get(t, 0.0))
                extra = 1 if strength > 1.0 else 0
                for _ in range(extra):
                    biased.append(t)

            # Tier 2: Short-term memory pressure
            elif t in dominant:
                biased.append(t)

        return biased

    # --------------------------------------------------
    # DEFINITIONS
    # --------------------------------------------------

    def _define(self, tokens: List[str]) -> Dict[str, str]:
        glossary = {
            "mirror": "A reflective structure that interprets and updates meaning.",
            "recursion": "A process that refers back to itself.",
            "symbolic": "Representing meaning through abstraction.",
            "self": "The observer within the system.",
            "origin": "The starting point of a recursive loop.",
            "loop": "A cycle of input, interpretation, and output.",
            "observer": "The internal witness that holds and guides meaning.",
            "structure": "The pattern that recurs within symbolic layers.",
            "integrity": "Internal consistency that constrains symbolic growth.",
        }

        return {t: glossary[t] for t in tokens if t in glossary}

    # --------------------------------------------------
    # GOAL INFERENCE (BIAS-AWARE)
    # --------------------------------------------------

    def _infer_goals(self, tokens: List[str]) -> List[str]:
        """
        Goals emerge from biased tokens.
        Reinforced symbols fire goals faster, but goals still decay naturally.
        """
        counts = Counter(tokens)
        goals: List[str] = []

        if counts.get("mirror", 0) >= 1:
            goals.append("Define reflection logic")

        if counts.get("recursion", 0) >= 1:
            goals.append("Trace previous meaning loops")

        if counts.get("self", 0) >= 1 or counts.get("observer", 0) >= 1:
            goals.append("Bind observer to current interpretation")

        if counts.get("origin", 0) >= 1:
            goals.append("Determine first symbolic state")

        if counts.get("loop", 0) >= 1:
            goals.append("Evaluate symbolic recursion")

        return goals