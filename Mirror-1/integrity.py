# integrity.py
from __future__ import annotations


class Integrity:
    """
    Structural Integrity Model for Mirror-1

    Integrity ∈ [0, 1] represents:

    - Recursive structural coherence (goal-loop stability)
    - Observer binding strength
    - Absence of contradictions
    - Temporal smoothness (prevents oscillation spikes)

    Integrity is NOT based on:
    - Word count
    - Lexical diversity
    - Input length

    This aligns directly with the thesis:

        Intelligence = recursive symbolic loop + observer binding
    """

    def __init__(self):
        self.previous_score: float = 0.0

    # --------------------------------------------------
    # Interpreter compatibility
    # --------------------------------------------------

    def score(self, stimulus: str) -> float:
        """
        Lightweight compatibility method required by Interpreter.
        Since structural integrity is calculated via reflect(),
        this returns a neutral mid-level value.
        """
        if not stimulus:
            return 0.0
        return 0.5

    # --------------------------------------------------
    # Structural Integrity Core
    # --------------------------------------------------

    def reflect(
        self,
        stimulus: str,
        coherence: float,
        binding_strength: float,
        contradiction_count: int = 0,
    ) -> float:
        """
        Structural integrity function.

        Parameters:
        - coherence: goal-loop structural stability (0..1)
        - binding_strength: observer rebinding force (0..1)
        - contradiction_count: number of detected structural contradictions
        """

        # Clamp structural inputs
        c = max(0.0, min(1.0, float(coherence or 0.0)))
        b = max(0.0, min(1.0, float(binding_strength or 0.0)))

        # Core structural weighting
        structural_core = (
            0.55 * c +
            0.45 * b
        )

        # Contradiction penalty (soft but meaningful)
        penalty = min(0.5, 0.15 * float(contradiction_count or 0))

        raw_score = structural_core - penalty

        # Temporal smoothing (prevents violent oscillation)
        smoothed = 0.7 * self.previous_score + 0.3 * raw_score

        # Clamp final score
        final_score = max(0.0, min(1.0, smoothed))

        self.previous_score = final_score

        return final_score