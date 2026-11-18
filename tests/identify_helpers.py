"""Synthetic items and responses for the identification tests (no generator needed)."""

from __future__ import annotations

import numpy as np

from reasoning_heuristics.identify.likelihood import Observation, UnitModel
from reasoning_heuristics.identify.records import Response


def decision_item(i: int, answers: dict[str, str], dists: dict[str, dict[str, float]] | None = None,
                  cell: str = "c0", set_id: str | None = None, base: str | None = None, exact: str | None = None) -> dict:
    """A SAT decision item. `answers`: label -> SAT/UNSAT; `exact`: EXACT's answer (default SAT)."""
    preds = {lbl: {"member": lbl, "family": "F", "params": {}, "answer": a, "distribution": None, "trace_features": {}}
             for lbl, a in answers.items()}
    for lbl, d in (dists or {}).items():
        preds[lbl] = {"member": lbl, "family": "H", "params": {}, "answer": None, "distribution": d, "trace_features": {}}
    preds["EXACT"] = {"member": "EXACT", "family": "null", "params": {}, "answer": exact or "SAT",
                      "distribution": None, "trace_features": {}}
    return {"item_id": f"T-{i}", "vertical": "T", "eval_id": "E0", "set_id": set_id or f"s{i}", "base_hash": base or f"b{i}",
            "cell": cell, "domain": "SAT", "generator": "tests.synthetic", "content_hash": f"h{i}",
            "presentation_hash": f"p{i}", "instance": {"kind": "sat_task"}, "extra": {"channel": "decision"},
            "predictions": preds, "ground_truth": {"satisfiable": (exact or "SAT") == "SAT"}}


def patterned_items(n: int, rng: np.random.Generator, cells: int = 4) -> list[dict]:
    """Members with distinct answer patterns: A always SAT, B alternates, C random, D random."""
    items = []
    for i in range(n):
        ans = {"A": "SAT", "B": "SAT" if i % 2 else "UNSAT", "C": "SAT" if rng.random() < 0.5 else "UNSAT",
               "D": "SAT" if rng.random() < 0.5 else "UNSAT"}
        items.append(decision_item(i, ans, cell=f"c{i % cells}", base=f"b{i // 2}"))
    return items


def plant(um: UnitModel, weights: dict[str, float], eps: float, rho: float, rng: np.random.Generator,
          q: float = 0.0, reps: int = 1) -> list[Observation]:
    """Responses from a planted constant mixture (members renormalised over the available ones)."""
    obs = []
    labels = list(weights)
    for _ in range(reps):
        for i in range(len(um.items)):
            avail = [l for l in labels if um.pred(i, l).available]
            w = np.array([weights[l] for l in avail] + [q])
            j = int(rng.choice(len(w), p=w / w.sum()))
            y = um.sample_q(i, rng) if j == len(avail) else um.sample(i, avail[j], eps, rho, rng)
            obs.append(Observation(i, y))
    return obs


def responses_from(um: UnitModel, obs: list[Observation], model: str = "m", condition: str = "thinking") -> list[Response]:
    out = []
    for k, ob in enumerate(obs):
        it = um.unit.items[ob.item]
        out.append(Response(it["item_id"], it["content_hash"], model, "ok", answer=ob.key, condition=condition, sample=k))
    return out
