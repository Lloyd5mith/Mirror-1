from __future__ import annotations

import yaml
import json
import random
from typing import Dict, Any

from memory import Memory
from observer import Observer
from meaning_store import MeaningStore
from integrity import Integrity
from interpreter import Interpreter
from goal_loop import GoalLoop
from self_model import SelfModel
from integrity_filter import IntegrityFilter

from symbol_graph import SymbolGraph
from contradiction_engine import ContradictionEngine


TOKENS = [
    "self",
    "mirror",
    "loop",
    "origin",
    "integrity",
    "observer",
    "recursion",
    "structure",
    "symbolic",
]

COMPETITOR_SYMBOLS = ("self", "mirror", "loop", "observer", "origin")


def auto_stimulus(turn: int) -> str:
    """
    Generate a more competitive symbolic field.
    """

    patterns = [
        ["mirror", "reflects", "loop"],
        ["loop", "returns", "origin"],
        ["observer", "tracks", "structure"],
        ["recursion", "builds", "symbolic", "structure"],
        ["integrity", "stabilizes", "loop"],
        ["symbolic", "structure", "emerges"],
        ["observer", "reflects", "mirror"],
        ["origin", "anchors", "loop"],
        ["mirror", "contains", "observer"],
        ["loop", "organizes", "structure"],
        ["origin", "precedes", "mirror"],
        ["observer", "interprets", "symbolic", "structure"],
        ["self", "reflects", "mirror"],
        ["self", "binds", "observer"],
        ["origin", "defines", "self"],
    ]

    if turn < 1000:
        weighted_pool = patterns[:12] + patterns[:12] + patterns[12:15]
    elif turn < 2500:
        weighted_pool = patterns[:12] + patterns[12:15]
    else:
        weighted_pool = patterns

    noise = random.sample(TOKENS, k=random.randint(2, 4))

    if random.random() < 0.8:
        chosen = random.choice(weighted_pool)
    else:
        chosen = noise

    return " ".join(chosen)


class Mirror1:

    def __init__(self, cfg: Dict[str, Any]):
        print("Initializing Mirror-1 (Repo 1)")

        self.cfg = cfg
        self.memory = Memory(verbose=False)
        self.observer = Observer(identity="observer", anchor="Mirror-1", verbose=False)

        self.meaning_store = MeaningStore()
        self.integrity = Integrity()
        self.goal_loop = GoalLoop(cfg)
        self.goal_loop.ensure_self_goal()
        self.self_model = SelfModel()
        self.integrity_filter = IntegrityFilter()

        self.interpreter = Interpreter(
            cfg=cfg,
            memory=self.memory,
            meaning_store=self.meaning_store,
            integrity=self.integrity,
        )

        self.symbol_graph = SymbolGraph()
        self.contradiction_engine = ContradictionEngine(self.symbol_graph)

        self.turn = 0
        print("Mirror-1 initialized\n")

    def step(self, stimulus: str):
        self.turn += 1
        self.memory.store("input", stimulus)

        interpretation = self.interpreter.interpret(stimulus)
        tokens = interpretation.get("tokens", []) or []
        relations = interpretation.get("relations", []) or []

        self.memory.store("interpretation", interpretation)

        for t in tokens:
            self.symbol_graph.add_symbol(t)

        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                self.symbol_graph.relate(tokens[i], "co_occurs", tokens[j])

        for rel in relations:
            if isinstance(rel, (list, tuple)) and len(rel) == 3:
                a, relation, b = rel
                self.symbol_graph.relate(a, relation, b)

        for t in tokens:
            inferred = self.symbol_graph.infer_transitive(t)
            for inf in inferred:
                self.symbol_graph.add_symbol(inf)

        self.meaning_store.extract(tokens)

        if self.self_model.locked_invariant is None:
            present_competitors = [s for s in COMPETITOR_SYMBOLS if s in tokens]
            for sym in present_competitors:
                self.meaning_store.reinforce_token(
                    sym,
                    amount=0.06,
                    reason="competitive_field_presence",
                )

        self.meaning_store.decay()

        # ----------------------------------------------
        # 🔥 CONVERGENCE PRESSURE
        # ----------------------------------------------
        if self.turn > 2000:
            for sym, strength in list(self.meaning_store.reinforcement_strength.items()):
                if sym != "self":
                    self.meaning_store.reinforcement_strength[sym] *= 0.992

        # slight late-phase self bias (SAFE VERSION)
        if self.turn > 3000 and self.self_model.locked_invariant is None:
            if "self" in self.meaning_store.reinforcement_strength:
                self.meaning_store.reinforcement_strength["self"] *= 1.001
        # ----------------------------------------------

        self.goal_loop.update_from_interpretation(interpretation)

        events = self.goal_loop.consume_events()
        for achieved_goal in events.get("achieved", []):
            self.meaning_store.reinforce_from_goal(achieved_goal, tokens)

        dominant = self.meaning_store.dominant_symbols()

        self_alignment = "self" in tokens
        self.self_model.update_binding(self_alignment)

        loop_score = self.goal_loop.coherence_score()
        meaning_pressure = 1.0 if dominant else 0.5
        coherence = loop_score * meaning_pressure

        contradictions = self.contradiction_engine.detect()

        structural_coherence = min(
            1.0,
            coherence + 0.45 * self.self_model.binding_strength
        )

        integrity_score = self.integrity.reflect(
            stimulus=stimulus,
            coherence=structural_coherence,
            binding_strength=self.self_model.binding_strength,
            contradiction_count=len(contradictions),
        )

        self.self_model.update(
            active_goals=self.goal_loop.evaluate(),
            dominant_symbols=dominant,
            reinforced_symbols=list(self.meaning_store.reinforcement_strength.keys()),
            integrity_score=integrity_score,
        )

        self.integrity_filter.observe(
            integrity_score=integrity_score,
            mode=self.self_model.state.get("mode"),
            active_goals=self.goal_loop.evaluate(),
            dominant_symbols=dominant,
        )

        intervention = self.integrity_filter.evaluate()

        leader, leader_strength = self.meaning_store.leading_symbol(
            candidates=COMPETITOR_SYMBOLS
        )
        runner_up_strength = self.meaning_store.runner_up_strength_among(
            candidates=COMPETITOR_SYMBOLS,
            exclude=leader,
        )
        leader_context_diversity = self.meaning_store.context_diversity(leader)

        candidate = leader if leader == "self" else None

        gate = self.self_model.observe_commit_gate(
            candidate_symbol=candidate,
            integrity_score=integrity_score,
            intervention_action=intervention.get("action", "none"),
            turn=self.turn,
            candidate_strength=leader_strength if leader == "self" else 0.0,
            runner_up_strength=runner_up_strength if leader == "self" else 0.0,
            context_diversity=leader_context_diversity if leader == "self" else 0,
            leader_symbol=leader,
        )

        if gate.get("action") == "lock_invariant":
            symbol = gate.get("symbol")
            self.observer.bind_invariant(symbol)
            self.meaning_store.lock_invariant(symbol)
            print(f"Invariant locked: '{symbol}' at turn {self.turn}")

        return {
            "turn": self.turn,
            "integrity": integrity_score,
            "binding": self.self_model.binding_strength,
            "dominant": dominant,
            "contradictions": contradictions,
            "leader": leader,
            "leader_strength": round(leader_strength, 3),
            "runner_up_strength": round(runner_up_strength, 3),
            "context_diversity": leader_context_diversity,
            "invariant": self.self_model.locked_invariant,
        }

    def run(self, steps: int = 5000):
        print(f"Running for {steps} steps\n")

        for i in range(steps):
            stim = auto_stimulus(i)
            state = self.step(stim)

            if i % 100 == 0:
                print(
                    f"[{i:05d}] "
                    f"binding={state['binding']:.3f} | "
                    f"integrity={state['integrity']:.3f} | "
                    f"leader={state['leader']} | "
                    f"leader_strength={state['leader_strength']:.3f} | "
                    f"runner_up={state['runner_up_strength']:.3f} | "
                    f"contexts={state['context_diversity']} | "
                    f"dominant={state['dominant']} | "
                    f"contradictions={len(state['contradictions'])} | "
                    f"invariant={state['invariant']}"
                )

        self.export_summary()

    def export_summary(self, path: str = "summary.json"):
        leader, leader_strength = self.meaning_store.leading_symbol(
            candidates=COMPETITOR_SYMBOLS
        )

        summary = {
            "steps": self.turn,
            "locked_invariant": self.self_model.locked_invariant,
            "final_binding": round(self.self_model.binding_strength, 4),
            "competitive_leader": leader,
            "competitive_leader_strength": round(leader_strength, 4),
            "meaning_summary": self.meaning_store.summary(),
            "graph_summary": self.symbol_graph.summary(),
            "self_model_state": self.self_model.state,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"Summary written to {path}")


def main():
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    except FileNotFoundError:
        cfg = {}

    engine = Mirror1(cfg)
    engine.run()


if __name__ == "__main__":
    main()