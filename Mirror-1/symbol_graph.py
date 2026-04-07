# symbol_graph.py

from typing import Dict, List, Tuple, Set


class SymbolGraph:
    """
    Directed typed symbol graph with:

    - Multi-hop implication inference
    - Cycle detection
    - Structural closure computation
    """

    def __init__(self):
        self.edges: Dict[str, List[Tuple[str, str]]] = {}

    # --------------------------------------------------
    # Basic graph ops
    # --------------------------------------------------

    def add_symbol(self, symbol: str):
        self.edges.setdefault(symbol, [])

    def relate(self, a: str, relation: str, b: str):
        self.add_symbol(a)
        self.add_symbol(b)
        self.edges[a].append((relation, b))

    def neighbors(self, symbol: str) -> List[Tuple[str, str]]:
        return self.edges.get(symbol, [])

    # --------------------------------------------------
    # Multi-hop implication closure
    # --------------------------------------------------

    def infer_transitive(self, start: str) -> Set[str]:
        visited = set()
        stack = [(start, 0)]  # (symbol, depth)

        while stack:
            current, depth = stack.pop()

            for rel, target in self.neighbors(current):
                if rel == "implies" and target not in visited:
                    visited.add(target)
                    stack.append((target, depth + 1))

        return visited

    # --------------------------------------------------
    # Full closure map
    # --------------------------------------------------

    def full_closure(self) -> Dict[str, Set[str]]:
        closure = {}
        for symbol in self.edges:
            closure[symbol] = self.infer_transitive(symbol)
        return closure

    # --------------------------------------------------
    # Cycle detection
    # --------------------------------------------------

    def detect_cycles(self) -> List[str]:
        visited = set()
        stack = set()
        cycles = []

        def dfs(node):
            if node in stack:
                cycles.append(node)
                return
            if node in visited:
                return

            visited.add(node)
            stack.add(node)

            for rel, target in self.neighbors(node):
                if rel == "implies":
                    dfs(target)

            stack.remove(node)

        for symbol in self.edges:
            dfs(symbol)

        return cycles

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    def summary(self):
        return {
            "symbol_count": len(self.edges),
            "edge_count": sum(len(v) for v in self.edges.values()),
        }