# contradiction_engine.py

from typing import List, Tuple
from symbol_graph import SymbolGraph


class ContradictionEngine:
    """
    Multi-hop contradiction detection.

    Detects:

    - Direct contradictions
    - Transitive contradictions
    - Implied contradictions
    """

    def __init__(self, graph: SymbolGraph):
        self.graph = graph

    def detect(self) -> List[Tuple[str, str]]:
        contradictions = []

        closure = self.graph.full_closure()

        for symbol, edges in self.graph.edges.items():

            implied = closure.get(symbol, set())
            negated = set()

            # Direct contradict edges
            for rel, target in edges:
                if rel == "contradicts":
                    negated.add(target)

            # Multi-hop contradiction:
            # if symbol implies X AND contradicts X
            for target in implied:
                if target in negated:
                    contradictions.append((symbol, target))

            # Reverse case:
            # if symbol contradicts something it implies indirectly
            for neg in negated:
                if neg in implied:
                    contradictions.append((symbol, neg))

        return contradictions