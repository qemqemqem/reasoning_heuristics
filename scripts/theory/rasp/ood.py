"""(1) Order effects of causal one-pass propagation; (2) length generalisation of the entailment members: training-size items (3-4 atoms,
2-4 premises) vs larger items (5-6 atoms, 4-6 premises).  Shows what each in-distribution
fit turns into out of distribution (e.g. the parallel truth table PROBE-16 becomes a
SAMPLE-like heuristic).  Writes ood.json.
"""
import json
import os
import random

import numpy as np

import instances as I
import programs_ent as PE
from rasp import last, measure

HERE = os.path.dirname(os.path.abspath(__file__))
MEMBERS = {
    "ALWAYS-NO": PE.always_no, "MATCH": PE.match, "PRIMACY": PE.primacy,
    "UP-1": lambda s: PE.up(s, 1), "UP-2": lambda s: PE.up(s, 2), "UP-3": lambda s: PE.up(s, 3),
    "FIRST.UP-2": lambda s: PE.up(s, 2, first=True), "BICOND.UP-2": lambda s: PE.up(s, 2, bicond=True),
    "PROBE-4": lambda s: PE.probe(s, 4), "PROBE-8": lambda s: PE.probe(s, 8),
    "PROBE-16": lambda s: PE.probe(s, 16),
}


def items(rng, n, atoms, prem):
    out = []
    while len(out) < n:
        p, c, na = I.random_entailment_item(rng, atoms, prem)
        out.append((p, c, na, int(I.entails(p, c, na))))
    return out


def order_effect(rng, n=400):
    """Causal UP-kc on puzzle CNF: same clauses, three orders (units first / as drawn / units last)."""
    import programs_sat as PS
    rows = {"units first": [], "as drawn": [], "units last": []}
    for _ in range(n):
        nv = rng.randint(4, 10)
        cl = PS.mixed_cnf(nv, max(1, round(rng.uniform(0.5, 3.0) * nv)), rng)
        y = int(I.satisfiable(cl, nv))
        orders = {"units first": sorted(cl, key=len), "as drawn": cl,
                  "units last": sorted(cl, key=lambda c: -len(c))}
        for name, o in orders.items():
            rows[name].append([PS.ref_up_causal(o, k) == y for k in (2, 3, 4)] + [PS.ref_up_full(o, nv) == y])
    return {name: dict(zip(["UP-2c", "UP-3c", "UP-4c", "UP-fix"], np.mean(v, axis=0).round(3).tolist()))
            for name, v in rows.items()}


def main(n=400, seed=0):
    rng = random.Random(seed)
    oe = order_effect(rng)
    print("order effect:", oe)
    dist = {"train (3-4 atoms, 2-4 premises)": items(rng, n, (3, 4), (2, 4)),
            "OOD (5-6 atoms, 4-6 premises)": items(rng, n, (5, 6), (4, 6))}
    ex = I.entailment_tokens([("or", (1, -2)), ("if", (1, 3)), ("fact", (-3,))], 2)
    res = {"order_effect_SAT_puzzle": oe, "yes_rate": {k: float(np.mean([y for *_, y in v])) for k, v in dist.items()}, "members": {}}
    for name, prog in MEMBERS.items():
        r = measure(name, prog, ex)
        row = {"length": r.length, "heads": r.heads, "layers": r.layers}
        for k, data in dist.items():
            row[k] = float(np.mean([last(prog(I.entailment_tokens(p, c))) == y for p, c, na, y in data]))
            fp = [last(prog(I.entailment_tokens(p, c))) for p, c, na, y in data if y == 0]
            row[k + " commission"] = float(np.mean(fp)) if fp else None
        res["members"][name] = row
        print(name, row)
    with open(os.path.join(HERE, "ood.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
