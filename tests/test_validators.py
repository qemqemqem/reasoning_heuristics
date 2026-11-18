"""Validators and solver edge cases (project review 2026-11-17, V2 and V4-V9).

- leakage: knapsack and TSP canonical forms, every instance compared, the effective (stated)
  problem, canonical CNFs, conditionals kept directed;
- the SAT menu renderer's condition count;
- solver edge cases: fixed colours outside 1..k, the empty graph, one-city TSP, inconsistent premises;
- the validator path's independence (own transforms, another SAT backend) and its readout rechecks;
- hygiene: 16-hex hash collisions, seed tiers, rng_for salts, lineage.
"""

import ast
import itertools
import random
from pathlib import Path

import numpy as np
import pytest

from reasoning_heuristics import seeds
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, KnapsackTask, SatTask, TspTask
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.render import render_menu
from reasoning_heuristics.problems.tsp.tsp import TSP, solve_bnb, solve_held_karp
from reasoning_heuristics.schema.item import Item
from reasoning_heuristics.validate import checks as C
from reasoning_heuristics.validate import independent as V
from reasoning_heuristics.validate import truth as T

NAMES10 = tuple(f"x{i:02d}" for i in range(1, 11))


def _item(task, split="dev", iid=None, base=None, source=None, prompt=None, generator="tests.synthetic",
          tier=None, seed=None, ground_truth=None, params=None) -> Item:
    content = sha(task.content_key())
    prompt = prompt or f"prompt for {content}"
    tier = tier or ("dev" if split == "dev" else "test")
    return Item(item_id=iid or f"{split}-{content}-{random.random()}", vertical="T", eval_id="E0",
                set_id=f"set-{base or content}", cell="c", domain=task.domain, framing="f", prompt=prompt,
                answer_format="a", ground_truth=ground_truth or {}, predictions={}, instance=task.to_json(),
                params=params or {}, content_hash=content, presentation_hash=sha(prompt), base_hash=base or content,
                source_hash=source, seed=seed if seed is not None else seeds.TIERS[tier].seed_lo + 7, split=split,
                tier=tier, generator=generator)


def _flagged(dev, test) -> bool:
    return bool(C.check_leakage(list(dev) + list(test)))


def _ksat(seed, n=10, m=40):
    return S.random_ksat(n, m, 3, np.random.default_rng(seed), NAMES10[:n])


# --- V4: leakage ----------------------------------------------------------------------------------


def test_leakage_knapsack_same_items_under_other_letters():
    k = Knapsack(tuple("ABCDE"), (10, 20, 30, 15, 7), (5, 9, 14, 6, 3), 20)
    perm = [3, 0, 4, 1, 2]
    relettered = Knapsack(tuple("ABCDE"), tuple(k.values[i] for i in perm), tuple(k.weights[i] for i in perm), 20)
    dev = _item(KnapsackTask(k))
    assert _flagged([dev], [_item(KnapsackTask(relettered), "test")])
    # the covering problem is the packing problem on the complement (capacity W - L)
    covering = KnapsackTask(Knapsack(k.names, k.values, k.weights, sum(k.weights) - 20), covering=True)
    assert _flagged([dev], [_item(covering, "test")])
    other = Knapsack(tuple("ABCDE"), (10, 20, 30, 15, 8), (5, 9, 14, 6, 3), 20)
    assert not _flagged([dev], [_item(KnapsackTask(other), "test")])


def test_leakage_tsp_same_distances_under_other_names():
    t = TSP(("a", "b", "c", "d", "e"), ((0, 0), (10, 3), (4, 8), (7, 7), (2, 5)))
    order = [2, 4, 0, 3, 1]
    relabelled = TSP(tuple(f"z{i}" for i in range(5)), tuple(t.coords[i] for i in order))
    moved = TSP(t.names, tuple((50 - x, y + 9) for x, y in t.coords))  # reflected and translated
    dev = _item(TspTask(t))
    assert _flagged([dev], [_item(TspTask(relabelled), "test")])
    assert _flagged([dev], [_item(TspTask(moved), "test")])
    other = TSP(t.names, ((0, 0), (10, 3), (4, 8), (7, 7), (2, 9)))
    assert not _flagged([dev], [_item(TspTask(other), "test")])


def test_leakage_compares_every_instance_not_only_one_per_base():
    x, y = _ksat(1), _ksat(2)
    x2 = x.with_clauses([tuple(-l for l in c) if i < 3 else c for i, c in enumerate(x.clauses)])
    assert not S.isomorphic(x, x2) and not S.isomorphic(x, y) and not S.isomorphic(y, x2)
    y2 = x2.renamed({v: v.replace("x", "z") for v in NAMES10})  # the test variant copies the dev variant
    bx, by = sha(SatTask(x).content_key()), sha(SatTask(y).content_key())
    dev = [_item(SatTask(x), base=bx), _item(SatTask(x2), base=bx, source=bx)]
    test = [_item(SatTask(y), "test", base=by), _item(SatTask(y2), "test", base=by, source=by)]
    out = C.check_leakage(dev + test)
    assert [f.item_id for f in out] == [test[1].item_id]


def test_leakage_compares_the_effective_graph():
    h = G.random_gnp([f"p{i}" for i in range(9)], 0.3, np.random.default_rng(2))
    vs = h.vertices
    comp = G.Graph(vs, tuple((vs[i], vs[j]) for i, j in itertools.combinations(range(len(vs)), 2) if not h.has_edge(vs[i], vs[j])))
    assert not G.isomorphic(h, comp)
    friends = _item(ColouringTask(h, 3, complement=True))  # "only friends may share": the graph lists friendships
    enemies = _item(ColouringTask(comp, 3), "test")  # the same stated problem, written as enemies
    assert _flagged([friends], [enemies])


def test_leakage_cnf_is_canonicalised():
    x = _ksat(3)
    dup_clause = x.with_clauses(list(x.clauses) + [x.clauses[0]])
    dup_literal = x.with_clauses([c + (c[0],) if i == 1 else c for i, c in enumerate(x.clauses)])
    tautology = x.with_clauses(list(x.clauses) + [(1, -1, 2)])
    dev = _item(SatTask(x))
    for variant in (dup_clause, dup_literal, tautology):
        assert _flagged([dev], [_item(SatTask(variant), "test")])


def test_leakage_still_sound_under_renaming_polarity_and_order():
    x = _ksat(4)
    rng = np.random.default_rng(9)
    perm = [int(p) + 1 for p in rng.permutation(10)]
    flip = {v: (-1 if v % 3 == 0 else 1) for v in range(1, 11)}
    clauses = [tuple(flip[abs(l)] * (perm[abs(l) - 1] if l > 0 else -perm[abs(l) - 1]) for l in reversed(c)) for c in reversed(x.clauses)]
    disguised = S.CNF(tuple(f"y{i}" for i in range(10)), tuple(clauses))
    assert _flagged([_item(SatTask(x))], [_item(SatTask(disguised), "test")])
    assert not _flagged([_item(SatTask(x))], [_item(SatTask(_ksat(5)), "test")])


def test_leakage_reads_the_stated_rule():
    x = _ksat(6)
    marked = (0, 3, 5)
    stated = x.with_clauses([[-l for l in c] if i in marked else list(c) for i, c in enumerate(x.clauses)])
    assert not S.isomorphic(x, stated)
    assert _flagged([_item(SatTask(x, inverted_clauses=marked))], [_item(SatTask(stated), "test")])
    a, b, c = F.lit("a"), F.lit("b"), F.lit("c")
    nor_read = EntailmentTask((F.disj(a, b), F.cond(b, c), F.lit("c", False)), None, "OPEN", reading="nor")
    nor_written = EntailmentTask((("nor", (a, b)), F.cond(b, c), F.lit("c", False)), None, "OPEN")
    assert _flagged([_item(nor_read)], [_item(nor_written, "test")])


def test_leakage_keeps_conditionals_directed():
    a, b, c = F.lit("a"), F.lit("b"), F.lit("c")
    forward = EntailmentTask((F.cond(a, b), F.cond(b, c), a), c)
    reversed_ = EntailmentTask((F.cond(b, a), F.cond(c, b), a), c)  # a different problem
    renamed = EntailmentTask((F.cond(F.lit("q"), F.lit("p")), F.cond(F.lit("r"), F.lit("q")), F.lit("r")), F.lit("p"))
    assert not _flagged([_item(forward)], [_item(reversed_, "test")])
    assert _flagged([_item(forward)], [_item(renamed, "test")])


# --- V5: the SAT menu renderer ----------------------------------------------------------------------


def test_menu_condition_count_is_true_for_any_clause_width():
    names = tuple(f"x{i:02d}" for i in range(1, 7))
    mixed = render_menu(S.CNF(names, ((1, -2, 3), (4,), (-5, 6))))
    assert "three conditions" not in mixed
    assert "Each guest has a request that is met if at least one of its conditions holds." in mixed
    assert "at least one of its two conditions holds." in render_menu(S.CNF(names, ((1, -2), (3, 4))))
    assert "Each guest has a request that is met if its condition holds." in render_menu(S.CNF(names, ((1,), (-3,))))
    three = render_menu(S.CNF(names, ((1, -2, 3), (4, 5, -6))))
    assert "Each guest has a request that is met if at least one of its three conditions holds." in three


# --- V6: solver edge cases -----------------------------------------------------------------------------


def test_fixed_colours_outside_1_to_k_are_rejected_on_both_paths():
    g = G.Graph(("v1", "v2"), (("v1", "v2"),))
    for bad in ({"v1": 3}, {"v1": 0}, {"v9": 1}):
        with pytest.raises(ValueError):
            G.k_colour(g, 2, bad)
    task = ColouringTask(g, 2, (("v1", 3),))
    with pytest.raises(ValueError):
        T.truth(task)
    with pytest.raises(ValueError):
        V.independent_truth(task.to_json())
    assert G.k_colour(g, 2, {"v1": 2}) == {"v1": 2, "v2": 1}
    # an item carrying such an instance fails validation instead of crashing it
    fails = C.check_item(_item(task, ground_truth={"k": 2, "colourable": True}))
    assert any(f.check == "ground_truth" and "ValueError" in f.message for f in fails)


def test_chromatic_number_of_empty_and_edgeless_graphs_agree():
    for g, chi in ((G.Graph((), ()), 0), (G.Graph(("a", "b", "c"), ()), 1)):
        task = ColouringTask(g)
        assert G.chromatic_number(g) == G.chromatic_number_sat(g) == chi
        assert T.truth(task) == V.independent_truth(task.to_json()) == {"chromatic_number": chi}


def test_tsp_with_one_city():
    t = TSP(("c0",), ((3, 4),))
    assert solve_held_karp(t) == (0, ["c0"])
    assert solve_bnb(t) == 0
    assert T.truth(TspTask(t)) == V.independent_truth(TspTask(t).to_json()) == {"optimal_length": 0}


def test_inconsistent_premises_entail_everything_on_both_paths():
    a, b = F.lit("a"), F.lit("b")
    prem = (a, F.lit("a", False))
    yn = EntailmentTask(prem, b, "YN")
    assert T.truth(yn) == V.independent_truth(yn.to_json()) == {"answer": "YES", "follows": True}
    mc = EntailmentTask(prem, None, "MC", (b, F.conj(a, b)))  # every option must be true; a∧b is the strongest
    assert T.truth(mc) == V.independent_truth(mc.to_json()) == {"answer": "B"}
    op = EntailmentTask(prem, None, "OPEN")
    assert T.truth(op) == V.independent_truth(op.to_json()) == {"answer": ["a", "not a"]}


def test_item_check_flags_inconsistent_premises():
    task = EntailmentTask((F.lit("a"), F.cond(F.lit("a"), F.lit("b")), F.lit("b", False)), F.lit("c"), "YN")
    fails = C.check_item(_item(task, ground_truth={"answer": "YES", "follows": True}))
    assert [f.check for f in fails if f.check in ("premises", "ground_truth")] == ["premises"]
    ok = EntailmentTask((F.lit("a"), F.cond(F.lit("a"), F.lit("b"))), F.lit("b"), "YN")
    assert not [f for f in C.check_item(_item(ok, ground_truth={"answer": "YES", "follows": True})) if f.check == "premises"]


# --- V7: an independent validator path ------------------------------------------------------------------


def test_validator_path_imports_nothing_from_the_generator_path():
    src = Path(V.__file__).read_text()
    mods = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
        elif isinstance(node, ast.Import):
            mods |= {a.name for a in node.names}
    banned = ("reasoning_heuristics.heuristics", "reasoning_heuristics.generators", "reasoning_heuristics.problems.coloring",
              "reasoning_heuristics.problems.sat", "reasoning_heuristics.problems.entailment", "reasoning_heuristics.problems.knapsack")
    assert not [m for m in mods if m.startswith(banned)]
    assert "Minisat" not in src and V.SAT_BACKEND != "minisat22"
    checks_src = Path(C.__file__).read_text()
    assert "independent_truth(item.instance)" in checks_src


def test_validator_does_not_follow_the_zoos_transforms(monkeypatch):
    # Break the shared transforms the generator path reads instances through: the validator must not follow.
    k3 = G.Graph(("a", "b", "c"), (("a", "b"), ("b", "c"), ("a", "c")))
    cases = [
        (ColouringTask(k3, None, complement=True), {"chromatic_number": 1}),
        (SatTask(S.CNF(("x1",), ((1,), (1,))), inverted_clauses=(1,)), {"satisfiable": False}),
        (EntailmentTask((F.disj(F.lit("a"), F.lit("b")),), F.lit("a", False), "YN", reading="nor"), {"answer": "YES", "follows": True}),
    ]
    for task, expected in cases:
        assert T.truth(task) == expected
    monkeypatch.setattr(T, "effective_graph", lambda task: task.graph)
    monkeypatch.setattr(T, "effective_cnf", lambda task: task.cnf)
    monkeypatch.setattr(T, "effective_premises", lambda task: list(task.premises))
    for task, expected in cases:
        assert T.truth(task) != expected  # the generator path is fooled ...
        assert V.independent_truth(task.to_json()) == expected  # ... the validator is not


def _brute_models(n, clauses, fixed=()):
    out = 0
    for bits in itertools.product((False, True), repeat=n):
        if any(bits[v - 1] != b for v, b in fixed):
            continue
        out += all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in clauses)
    return out


def _brute_colourings(vertices, edges, k, fixed=None):
    """(labelled proper colourings extending `fixed`, partitions into <= k independent sets)."""
    labelled, parts = 0, set()
    for cols in itertools.product(range(1, k + 1), repeat=len(vertices)):
        col = dict(zip(vertices, cols))
        if any(col[u] == col[v] for u, v in edges):
            continue
        parts.add(frozenset(frozenset(v for v in vertices if col[v] == c) for c in set(cols)))
        labelled += all(col[v] == c for v, c in (fixed or {}).items())
    return labelled, len(parts)


def test_readouts_sat_counts_are_rechecked():
    names = ("x1", "x2", "x3", "x4", "x5")  # x5 is declared and unused: counts run over every declared variable
    cnf = S.CNF(names, ((1, 2), (-1, 3), (-2, -3, 4)))
    stated = [(-1, -2), (-1, 3), (-2, -3, 4)]
    task = SatTask(cnf, inverted_clauses=(0,))
    gt = {"satisfiable": True, "n_solutions_stated": _brute_models(5, stated),
          "n_solutions_textbook": _brute_models(5, cnf.clauses)}
    assert V.recheck_readouts(task.to_json(), gt, {}) == []
    for key in ("n_solutions_stated", "n_solutions_textbook"):
        assert V.recheck_readouts(task.to_json(), {**gt, key: gt[key] + 1}, {})
    fixed = SatTask(cnf, (("x1", True),))
    gt = {"n_solutions": _brute_models(5, cnf.clauses), "n_completions": _brute_models(5, cnf.clauses, [(1, True)])}
    assert V.recheck_readouts(fixed.to_json(), gt, {}) == []
    assert V.recheck_readouts(fixed.to_json(), {**gt, "n_completions": gt["n_solutions"]}, {})


def test_readouts_colouring_counts_are_rechecked():
    vs = ("v0", "v1", "v2", "v3", "v4")
    c5 = G.Graph(vs, tuple((vs[i], vs[(i + 1) % 5]) for i in range(5)))
    _, parts3 = _brute_colourings(vs, c5.edges, 3)
    fewest = ColouringTask(c5)
    assert V.recheck_readouts(fewest.to_json(), {"chromatic_number": 3, "n_optimal_partitions": parts3}, {}) == []
    assert V.recheck_readouts(fewest.to_json(), {"chromatic_number": 3, "n_optimal_partitions": parts3 - 1}, {})
    k3 = ColouringTask(c5, 3)
    assert V.recheck_readouts(k3.to_json(), {"n_colourings_up_to_renaming": parts3}, {}) == []
    assert V.recheck_readouts(k3.to_json(), {"n_colourings_up_to_renaming": parts3 + 2}, {})
    star = G.Graph(("h", "a", "b", "c"), (("h", "a"), ("h", "b"), ("h", "c")))
    comp_edges = [("a", "b"), ("a", "c"), ("b", "c")]
    inv = ColouringTask(star, 3, complement=True)
    gt = {"n_partitions_stated": _brute_colourings(star.vertices, comp_edges, 3)[1],
          "n_partitions_textbook": _brute_colourings(star.vertices, star.edges, 3)[1]}
    assert gt["n_partitions_stated"] != gt["n_partitions_textbook"]
    assert V.recheck_readouts(inv.to_json(), gt, {}) == []
    assert V.recheck_readouts(inv.to_json(), {**gt, "n_partitions_stated": gt["n_partitions_textbook"]}, {})
    state = ColouringTask(c5, 3, (("v0", 1), ("v2", 2)))
    n_c = _brute_colourings(vs, c5.edges, 3, {"v0": 1, "v2": 2})[0]
    assert V.recheck_readouts(state.to_json(), {"n_completions": n_c}, {}) == []
    assert V.recheck_readouts(state.to_json(), {"n_completions": n_c + 1}, {})
    good = {"v0": 1, "v1": 2, "v2": 1, "v3": 2, "v4": 3}
    assert V.recheck_readouts(k3.to_json(), {"colourable": True, "example": good}, {}) == []
    assert V.recheck_readouts(k3.to_json(), {"colourable": True, "example": {**good, "v4": 1}}, {})
    assert V.recheck_readouts(k3.to_json(), {"colourable": True, "example": None}, {})
    # the C E3 asked answer: the first-fit colour of the target in listing order
    listed = ColouringTask(G.Graph(("v3", "v0", "v1", "v4", "v2"), c5.edges), None, (), ("v3", "v0", "v1", "v4", "v2"))
    # first fit in listing order: v3=1, v0=1, v1=2, v4=2 (v3, v0 are 1), v2=3 (v1=2, v3=1)
    assert V.recheck_readouts(listed.to_json(), {"answer": 3}, {"target": "v2"}) == []
    assert V.recheck_readouts(listed.to_json(), {"answer": 1}, {"target": "v2"})


def test_readouts_knapsack_and_entailment_are_rechecked():
    k = Knapsack(tuple("ABCD"), (6, 5, 4, 3), (3, 3, 2, 2), 5)
    subsets = []
    for r in range(5):
        for s in itertools.combinations(range(4), r):
            if sum(k.weights[i] for i in s) <= 5:
                subsets.append((sum(k.values[i] for i in s), sorted(k.names[i] for i in s)))
    best = max(v for v, _ in subsets)
    pack = sorted(s for v, s in subsets if v == best)
    assert len(pack) == 1
    task = KnapsackTask(k)
    assert V.recheck_readouts(task.to_json(), {"optimum": best, "optimal_set": pack[0]}, {}) == []
    assert V.recheck_readouts(task.to_json(), {"optimum": best, "optimal_set": ["A", "B"]}, {})
    assert V.recheck_readouts(task.to_json(), {"optimal_subsets": pack, "packing_optimal_subsets": pack}, {}) == []
    assert V.recheck_readouts(task.to_json(), {"optimal_subsets": pack + [["D"]], "packing_optimal_subsets": pack}, {})
    a, b, c = F.lit("a"), F.lit("b"), F.lit("c")
    prem = (F.disj(a, b), F.cond(b, c))
    yn = EntailmentTask(prem, c, "YN")
    worlds = [dict(zip("abc", bits)) for bits in itertools.product((False, True), repeat=3)]
    cm = sum(1 for w in worlds if (w["a"] or w["b"]) and (not w["b"] or w["c"]) and not w["c"])
    assert V.recheck_readouts(yn.to_json(), {"countermodels": cm}, {}) == []
    assert V.recheck_readouts(yn.to_json(), {"countermodels": cm + 1}, {})
    op = EntailmentTask((F.disj(a, b), F.lit("c")), None, "OPEN")
    gt = {"entailed_under_or": ["c"], "entailed_under_nor": ["c", "not a", "not b"]}
    assert V.recheck_readouts(op.to_json(), gt, {}) == []
    assert V.recheck_readouts(op.to_json(), {**gt, "entailed_under_nor": ["c"]}, {})


def test_both_truth_paths_agree_on_random_small_instances():
    rng = random.Random(7)
    for _ in range(60):
        n = rng.randint(1, 6)
        vs = [f"v{i}" for i in range(n)]
        edges = [e for e in itertools.combinations(vs, 2) if rng.random() < 0.5]
        g = G.Graph(tuple(vs), tuple(edges))
        compl = rng.random() < 0.3
        k = rng.randint(1, 3)
        fixed = tuple((v, rng.randint(1, k)) for v in vs if rng.random() < 0.2)
        for task in (ColouringTask(g, None, complement=compl), ColouringTask(g, k, fixed, complement=compl)):
            assert T.truth(task) == V.independent_truth(task.to_json())
    for _ in range(80):
        n = rng.randint(1, 6)
        clauses = tuple(tuple(rng.choice((-1, 1)) * rng.randint(1, n) for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(1, 3 * n)))
        cnf = S.CNF(NAMES10[:n], clauses)
        fixed = tuple((v, rng.random() < 0.5) for v in cnf.var_names if rng.random() < 0.2)
        marked = tuple(i for i in range(len(clauses)) if rng.random() < 0.3)
        for task in (SatTask(cnf, fixed), SatTask(cnf, fixed, inverted=True), SatTask(cnf, fixed, inverted_clauses=marked)):
            assert T.truth(task) == V.independent_truth(task.to_json())
    atoms = "abcd"

    def rand_f(depth=0):
        if depth >= 2 or rng.random() < 0.35:
            return F.lit(rng.choice(atoms), rng.random() < 0.5)
        op = rng.choice(["and", "or", "nand", "nor", "if", "iff"])
        if op in ("if", "iff"):
            return (op, rand_f(depth + 1), rand_f(depth + 1))
        return (op, tuple(rand_f(depth + 1) for _ in range(rng.randint(1, 3))))

    for _ in range(200):
        prem = tuple(rand_f() for _ in range(rng.randint(1, 4)))
        fmt = rng.choice(["YN", "OPEN", "MC"])
        task = EntailmentTask(prem, rand_f() if fmt == "YN" else None, fmt,
                              tuple(rand_f() for _ in range(rng.randint(1, 4))) if fmt == "MC" else (),
                              rng.choice(["standard", "nor"]))
        try:
            indep = V.independent_truth(task.to_json())
        except ValueError as exc:  # an MC item without one strongest option is flagged, not tie-broken
            assert fmt == "MC" and "strongest" in str(exc)
            continue
        assert T.truth(task) == indep
    for _ in range(40):
        n = rng.randint(1, 8)
        k = Knapsack(tuple("ABCDEFGH"[:n]), tuple(rng.randint(0, 20) for _ in range(n)),
                     tuple(rng.randint(0, 20) for _ in range(n)), 0)
        k = Knapsack(k.names, k.values, k.weights, rng.randint(0, sum(k.weights)))
        for task in (KnapsackTask(k), KnapsackTask(k, covering=True)):
            assert T.truth(task) == V.independent_truth(task.to_json())


# --- V8, V9: hashes, seeds, salts, lineage ------------------------------------------------------------


def test_hash_collisions_are_detected():
    a, b = _item(SatTask(_ksat(10)), iid="a"), _item(SatTask(_ksat(11)), iid="b")
    b.content_hash = a.content_hash  # different content under one 16-hex hash
    assert [f.check for f in C.check_hash_collisions([a, b])] == ["hash_collision"]
    c, d = _item(SatTask(_ksat(10)), iid="c", prompt="one"), _item(SatTask(_ksat(10)), iid="d", prompt="two")
    d.presentation_hash = c.presentation_hash
    assert [f.check for f in C.check_hash_collisions([c, d])] == ["hash_collision"]
    assert C.check_hash_collisions([a, c]) == []  # the same content under the same hash is not a collision
    report = C.run_checks([a, b], None)
    assert any(f["check"] == "hash_collision" for f in report["failures"])


def test_seed_must_lie_in_its_tiers_range():
    task = SatTask(_ksat(12))

    def seed_failures(tier, seed):
        return [f for f in C.check_item(_item(task, tier=tier, seed=seed)) if f.check == "seed"]

    assert seed_failures("smoke", 50) == [] and seed_failures("dev", 200_000) == []
    assert seed_failures("smoke", 200_000)  # a dev seed on a smoke item: inside the split, outside the tier
    assert seed_failures("dev", 50)
    assert seed_failures("test", 50)


def test_rng_for_streams_unchanged_and_salt_truncation_fails_fast():
    s = 1_234_567_891  # outside every tier range: no generator in this process uses it
    want = np.random.default_rng([s, int.from_bytes(b"AH-E1-SA", "little")]).integers(0, 2**31, size=4)
    assert list(seeds.rng_for(s, "AH-E1-SAT-critical").integers(0, 2**31, size=4)) == list(want)
    assert list(seeds.rng_for(s, "AH-E1-SAT-critical").integers(0, 2**31, size=4)) == list(want)  # same salt again
    with pytest.raises(AssertionError, match="first 8 bytes"):
        seeds.rng_for(s, "AH-E1-SAT-null")  # would silently share the stream above
    seeds.rng_for(s + 1, "AH-E1-SAT-null")  # another seed: another stream
    short = np.random.default_rng([s, int.from_bytes(b"C-E3-1".ljust(8, b"\0"), "little")]).integers(0, 2**31, size=2)
    assert list(seeds.rng_for(s, "C-E3-1").integers(0, 2**31, size=2)) == list(short)


def test_lineage_rules():
    x, x2, x3 = SatTask(_ksat(20)), SatTask(_ksat(21)), SatTask(_ksat(22))
    base = _item(x, iid="base")
    child = _item(x2, iid="child", base=base.base_hash, source=base.content_hash)
    assert C.check_lineage([base, child]) == ([], [])

    def rules(items):
        fails, known = C.check_lineage(items)
        assert known == []
        return sorted(f.message.split(":")[0] for f in fails)

    assert rules([base, _item(x3, iid="orphan", base=base.base_hash, source="0123456789abcdef")]) == ["source-resolves"]
    assert rules([base, _item(x3, iid="root", base=base.base_hash)]) == ["root-is-base"]
    other_base = _item(x3, iid="other", base="ffffffffffffffff", source=base.content_hash)
    assert rules([base, other_base]) == ["source-same-base"]
    moved = _item(x2, iid="moved", base=base.base_hash, source=base.content_hash, seed=base.seed + 1)
    assert rules([base, moved]) == ["base-provenance", "base-provenance"]


def test_lineage_known_gaps_are_reported_not_failed(monkeypatch):
    monkeypatch.setattr(C, "KNOWN_LINEAGE_GAPS", {("tests.known", "source-resolves")})
    base = _item(SatTask(_ksat(23)), iid="base", generator="tests.known")
    orphan = _item(SatTask(_ksat(24)), iid="orphan", base=base.base_hash, source="0123456789abcdef", generator="tests.known")
    fails, known = C.check_lineage([base, orphan])
    assert fails == [] and [f.item_id for f in known] == ["orphan"]
    report = C.run_checks([base, orphan], None)
    assert report["lineage_known_gaps"] == {"tests.known": {"source-resolves": 1}}
    assert not [f for f in report["failures"] if f["check"] == "lineage"]
    # the same violation from a generator that is not on the list fails
    stray = _item(SatTask(_ksat(25)), iid="stray", base=base.base_hash, source="0123456789abcdef", generator="tests.other")
    fails, _ = C.check_lineage([base, stray])
    assert [f.item_id for f in fails] == ["stray"]
