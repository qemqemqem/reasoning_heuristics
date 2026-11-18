"""ETR members are deterministic: answers and trace text do not depend on PYTHONHASHSEED.

PyETR stores a view's states as frozensets, so anything read off a view must be put in a
canonical order before it is rendered; otherwise the MC `output` trace feature (and so the
validators' recomputation) changes with the interpreter's hash seed.
"""

import json
import os
import subprocess
import sys

SCRIPT = r"""
import json
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import EntailmentTask
from reasoning_heuristics.problems.entailment import formula as F

L = F.lit
aA, aB, bC, bD, cE = "box:red", "box:heavy", "jar:blue", "jar:cold", "cup:green"
out = []
for T in "MUV":
    for P in (1, 2):
        for O in ("DC", "CD"):
            d1, d2 = F.conj(L(aA), L(aB)), F.conj(L(bC), L(bD))
            pd = F.disj(d1, d2) if P == 1 else F.disj(d2, d1)
            second = {"M": L(aA), "U": L(cE), "V": F.disj(L(aA), L(cE))}[T]
            prem = (pd, second) if O == "DC" else (second, pd)
            options = (L(aB), L(bD), F.disj(L(aB), F.conj(L(bC), L(bD))), L(aB, False))
            task = EntailmentTask(prem, None, "MC", options)
            for name in ("ETR-default", "ETR-1p"):
                for rendering in ("R1", "R2"):
                    p = run("entailment", name, task, {"rendering": rendering})
                    out.append([T, P, O, name, rendering, p.answer, p.trace_features])
print(json.dumps(out, sort_keys=True))
"""


def _run(seed: str) -> list:
    env = {**os.environ, "PYTHONHASHSEED": seed}
    res = subprocess.run([sys.executable, "-c", SCRIPT], capture_output=True, text=True, env=env, timeout=300)
    assert res.returncode == 0, res.stderr
    return json.loads(res.stdout)


def test_etr_mc_output_is_canonical_across_hash_seeds():
    runs = [_run(seed) for seed in ("0", "1", "2", "123")]
    assert all(r == runs[0] for r in runs[1:])
    assert len({row[6]["output"] for row in runs[0]}) > 1  # real formulas, not one constant
