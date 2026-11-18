"""C E1: order source, by isomorphic copies (C §2.6 E1, §2.8 E1-COL / E1-SAT).

For each base instance, six copies with an identical edge (clause) set and label multiset:

    c1 NAT        listing π_L, labels ascending along π_L, answer in LIST order
    c2 RELABEL    listing π_L, labels randomly permuted, answer LIST
    c3 ANS-LABEL  as c2, answer in LABEL order
    c4 ANS-RAND   as c2, answer in a random order π_R
    c5 ANS-FREE   as c2, answer in any order (FREE)
    c6 RELIST     new listing π_L' (labels as c2), answer LIST (= π_L')

Ground truth and every order-free member are constant by construction; FF-LIST changes
only at c6, FF-LABEL between c1 and c2, FF-OUT follows the requested answer order.

COL (study default n = 16, from G(n, m) with mean degree 4.0-4.8). Filters (§2.8):
χ in {3, 4}; >= 50 optimal partitions; Grundy fraction among optimal partitions <= 0.4;
the FF partitions for π_L, λ, π_R and π_L' pairwise distinct; LF and DSATUR distinct
from all four; FF uses χ + 1 colours in at least one of those orders.

SAT (study default n = 20, α alternating 3.0 / 3.5, uniform 3-SAT). Filters (§2.8):
satisfiable; >= 20 solutions; GREEDY-MENTION, GREEDY-INDEX and GREEDY on the re-listed copy
all satisfying and pairwise Hamming >= 4; POLARITY distinct from them; UC-DET distinct from
GREEDY on at least one copy. For SAT, "listing" is first mention in clause order, so c6
shuffles the clause order.

Readings of the doc (also in docs/GENERATORS.md):
- FF-OUT / GREEDY-OUT are omitted on c5: under FREE their prediction is FF over the
  model's own emitted order, which only exists after the run (scored by the runner).
- Partition enumeration is capped (`max_partitions`, default 200,000); bases with more
  optimal partitions are rejected (none of the doc's other filters needs the exact count).
- E1-KNAP / E1-TSP copies, the 20% re-themed subset and the names variant are not built.
- MIN-CONFLICTS / WALK (F) are not in the zoo for colouring; NOISY-EXACT is included for
  colouring (slip mass spread like EXACT's optimal set) but not for SAT witnesses.
- The theory §5 arms are parameters: `serialisation` ("adjacency" | "edge_list_shuffled";
  the edge order is shuffled once per base and kept across copies) and `repeat_prompt`.
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics import tokens
from reasoning_heuristics.counterfactual import surface
from reasoning_heuristics.counterfactual.reorder import permutation, reorder_clauses
from reasoning_heuristics.generators import c_common as CC
from reasoning_heuristics.generators.common import GenStats, make_item, set_hash
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import ColouringTask, SatTask, load_task
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.render import render_c
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.truth import truth

VERTICAL, EVAL_ID = "C", "E1"
LEXICON_PARTITIONED = False
COPIES = ["c1-NAT", "c2-RELABEL", "c3-ANS-LABEL", "c4-ANS-RAND", "c5-ANS-FREE", "c6-RELIST"]


def cells(params: dict[str, Any]) -> list[str]:
    return [f"{d}/{c}" for d in params.get("domains", ["COL", "SAT"]) for c in COPIES]


# --- colouring -------------------------------------------------------------------------------------


def col_members(copy: str) -> list:
    specs = [
        ("FF-LIST", "FF", {"order": "LIST"}),
        ("FF-LABEL", "FF", {"order": "LABEL"}),
        ("FF-OUT (AR)", "FF", {"order": "OUT"}),
        ("LF", "LF", {"tie": "LIST"}),
        ("DSATUR", "DSATUR", {"tie": "LIST"}),
        ("DSATUR-LABEL", "DSATUR", {"tie": "LABEL"}),
        ("DPLL-LIST (D)", "SEARCH", {"order": "LIST"}),
        ("DPLL-LABEL (D)", "SEARCH", {"order": "LABEL"}),
        ("GREEDY+REPAIR-LIST (C->F)", "GREEDY+REPAIR", {"order": "LIST"}),
        ("RO-FF (C3)", "RO-FF", {"samples": 2000, "seed": 0}),
        ("LOCAL-2-ID (E)", "LOCAL-t", {"t": 2, "ids": "LABEL", "default": "one"}),
        ("EXACT", "EXACT", {}),
        ("RANDOM (H)", "RANDOM", {}),
        ("NOISY-EXACT", "NOISY-EXACT", {"p": 0.01}),
    ]
    if copy == "c5-ANS-FREE":
        specs = [s for s in specs if s[0] != "FF-OUT (AR)"]
    return specs


def _ff_partition(g: Graph, order: list[str], structure: dict[str, int]):
    col = run("coloring", "FF", ColouringTask(g), {"order": "EXPLICIT", "sequence": order}).answer
    return CC.structural_partition(col, structure), len(set(col.values()))


def build_col_copies(base: Graph, rng, params: dict[str, Any]) -> dict[str, Any] | None:
    """Six copies of `base` (internal names u0..). Returns None (with a reason) on rejection."""
    n = base.n
    labels = CC.labels_for(n, "v", rng)
    edge_order = permutation(list(base.edges), rng) if params["serialisation"] == "edge_list_shuffled" else list(base.edges)
    base = Graph(base.vertices, tuple(edge_order))
    to_c1 = dict(zip(base.vertices, labels))  # labels ascend along π_L
    c1 = base.renamed(to_c1)
    sigma = dict(zip(labels, permutation(labels, rng)))  # c1 label -> c2 label
    c2 = c1.renamed(sigma)
    struct_c1 = {to_c1[u]: i for i, u in enumerate(base.vertices)}
    struct_c2 = {sigma[l]: i for l, i in struct_c1.items()}
    pi_R = permutation(list(c2.vertices), rng)
    pi_L2 = permutation(list(c2.vertices), rng)
    c6 = c2.relisted(pi_L2)
    copies = {
        "c1-NAT": (c1, list(c1.vertices), struct_c1),
        "c2-RELABEL": (c2, list(c2.vertices), struct_c2),
        "c3-ANS-LABEL": (c2, c2.label_order(), struct_c2),
        "c4-ANS-RAND": (c2, pi_R, struct_c2),
        "c5-ANS-FREE": (c2, None, struct_c2),
        "c6-RELIST": (c6, list(c6.vertices), struct_c2),
    }
    return {"copies": copies, "pi_R": pi_R, "pi_L2": pi_L2, "c2": c2, "c6": c6, "struct": struct_c2}


def col_filters(c: dict[str, Any], params: dict[str, Any], stats: GenStats) -> dict[str, Any] | None:
    c2, c6, st = c["c2"], c["c6"], c["struct"]
    chi = G.chromatic_number(c2)
    if chi not in (3, 4):
        stats.reject("chromatic number not in {3, 4}")
        return None
    fps = {
        "LIST": _ff_partition(c2, list(c2.vertices), st),
        "LABEL": _ff_partition(c2, c2.label_order(), st),
        "RAND": _ff_partition(c2, c["pi_R"], st),
        "RELIST": _ff_partition(c6, list(c6.vertices), st),
    }
    parts = [p for p, _ in fps.values()]
    if len(set(parts)) != 4:
        stats.reject("FF partitions for the four orders not pairwise distinct")
        return None
    lf = CC.structural_partition(run("coloring", "LF", ColouringTask(c2)).answer, st)
    ds = CC.structural_partition(run("coloring", "DSATUR", ColouringTask(c2)).answer, st)
    if lf in parts or ds in parts:
        stats.reject("LF or DSATUR equals an FF partition")
        return None
    if not any(k == chi + 1 for _, k in fps.values()):
        stats.reject("FF optimal in every order (no C1-vs-D split)")
        return None
    masks = G.enumerate_partitions(c2, chi, params["max_partitions"])
    if masks is None:
        stats.reject("more optimal partitions than the enumeration cap")
        return None
    if len(masks) < params["min_optimal"]:
        stats.reject("too few optimal partitions")
        return None
    grundy = sum(G.is_grundy_masks(c2, m) for m in masks) / len(masks)
    if grundy > params["max_grundy"]:
        stats.reject("Grundy fraction among optimal partitions too high")
        return None
    return {"chi": chi, "n_optimal": len(masks), "grundy_fraction": round(grundy, 4),
            "fingerprints": {k: sorted(sorted(c) for c in p) for k, (p, _) in fps.items()},
            "ff_colours": {k: v for k, (_, v) in fps.items()}}


def generate_col(tier: str, seed: int, per_cell: int, params: dict[str, Any], stats: GenStats) -> list:
    items = []
    attempt = 0
    accepted = 0
    n = params["n_col"]
    while accepted < per_cell:
        bseed = base_seed(tier, seed, attempt)
        attempt += 1
        stats.attempts += 1
        CC.guard(attempt, params, stats, "E1-COL")
        rng = rng_for(bseed, "C-E1-COL")
        lo, hi = int(round(params["mean_degree"][0] * n / 2)), int(round(params["mean_degree"][1] * n / 2))
        m = int(rng.integers(lo, hi + 1))
        base = G.random_gnm([f"u{i}" for i in range(n)], m, rng)
        c = build_col_copies(base, rng, params)
        info = col_filters(c, params, stats)
        if info is None:
            continue
        set_items = []
        base_hash = sha(c["c2"].content_key())
        sid = set_hash(bseed, "COL")
        for copy, (g, order, struct) in c["copies"].items():
            task = ColouringTask(g, None, (), tuple(order) if order is not None else None)
            prompt = CC.render_colouring(g, "fewest", order, None, params["serialisation"], params["repeat_prompt"])
            gt = {**truth(task), "n_optimal_partitions": info["n_optimal"],
                  "grundy_fraction_among_optimal": info["grundy_fraction"],
                  "check": f"any proper colouring; optimal iff it uses {info['chi']} colours"}
            set_items.append(make_item(
                vertical=VERTICAL, eval_id=EVAL_ID, set_id=sid, cell=f"COL/{copy}", domain="colouring",
                framing="textbook", prompt=prompt, answer_format=CC.COLOUR_FEWEST_FORMAT, task=task,
                ground_truth=gt, specs=col_members(copy), channel=CC.colouring_channel(g, info["chi"], info["n_optimal"]),
                seed=bseed, tier=tier, generator=__name__, base_hash=base_hash,
                source_hash=None if copy == "c2-RELABEL" else base_hash, pair_id=f"E1-COL-{sid}",
                params={"n": n, "m": g.m, "copy": copy, "structure": struct, "ff_fingerprints": info["fingerprints"],
                        "ff_colours_by_order": info["ff_colours"], "serialisation": params["serialisation"],
                        "repeat_prompt": params["repeat_prompt"], "prompt_tokens": tokens.count(prompt),
                        "tokenizer_proxy": tokens.PROXY_NAME},
                notes="Isomorphic copies: identical edge set and label multiset. FF-LIST changes only at c6; "
                      "FF-LABEL between c1 and c2; FF-OUT follows the requested answer order.",
                cell_note=f"Copy {copy}.",
            ))
        problems = check_set(set_items)
        if problems:
            stats.reject("set invariant failed: " + problems[0][:60])
            continue
        items += set_items
        accepted += 1
        stats.accepted += 1
    return items


# --- SAT ----------------------------------------------------------------------------------------------


def sat_members(copy: str) -> list:
    specs = [
        ("GREEDY-MENTION", "GREEDY", {"order": "MENTION"}),
        ("GREEDY-INDEX", "GREEDY", {"order": "INDEX"}),
        ("GREEDY-OUT (AR)", "GREEDY", {"order": "OUT"}),
        ("POLARITY (C0)", "POLARITY", {}),
        ("UC-DET (C2)", "UC", {}),
        ("GUC-DET (C2)", "GUC", {}),
        ("DPLL-MENTION (D, T first)", "SEARCH", {"order": "MENTION", "value": "TRUE"}),
        ("DPLL-INDEX (D, T first)", "SEARCH", {"order": "INDEX", "value": "TRUE"}),
        ("RO-GREEDY (C3)", "RO-GREEDY", {"samples": 300, "seed": 0}),
        ("EXACT", "EXACT", {}),
        ("RANDOM (H)", "RANDOM", {}),
    ]
    if copy == "c5-ANS-FREE":
        specs = [s for s in specs if s[0] != "GREEDY-OUT (AR)"]
    return specs


def build_sat_copies(base: S.CNF, rng) -> dict[str, Any]:
    n = base.n
    labels = CC.labels_for(n, "x", rng)
    mention = base.mention_order() + [v for v in range(1, n + 1) if v not in base.mention_order()]
    to_c1 = {base.var_names[v - 1]: labels[i] for i, v in enumerate(mention)}
    c1 = base.renamed(to_c1)
    sigma = dict(zip(labels, permutation(labels, rng)))
    c2 = c1.renamed(sigma)
    struct_c1 = {to_c1[u]: i for i, u in enumerate(base.var_names)}
    struct_c2 = {sigma[l]: i for l, i in struct_c1.items()}
    clause_order = [int(i) for i in rng.permutation(base.m)]
    c6 = reorder_clauses(c2, clause_order)

    def mention_names(cnf: S.CNF) -> list[str]:
        mo = cnf.mention_order() + [v for v in range(1, cnf.n + 1) if v not in cnf.mention_order()]
        return [cnf.var_names[v - 1] for v in mo]

    pi_R = permutation(list(c2.var_names), rng)
    copies = {
        "c1-NAT": (c1, mention_names(c1), struct_c1),
        "c2-RELABEL": (c2, mention_names(c2), struct_c2),
        "c3-ANS-LABEL": (c2, sorted(c2.var_names, key=G.label_key), struct_c2),
        "c4-ANS-RAND": (c2, pi_R, struct_c2),
        "c5-ANS-FREE": (c2, None, struct_c2),
        "c6-RELIST": (c6, mention_names(c6), struct_c2),
    }
    return {"copies": copies, "c2": c2, "c6": c6, "struct": struct_c2, "clause_order": clause_order}


def sat_filters(c: dict[str, Any], params: dict[str, Any], stats: GenStats) -> dict[str, Any] | None:
    c2, c6, st = c["c2"], c["c6"], c["struct"]
    if S.solve(c2) is None:
        stats.reject("unsatisfiable")
        return None
    t2, t6 = SatTask(c2), SatTask(c6)
    gm = run("sat", "GREEDY", t2, {"order": "MENTION"}).answer
    gi = run("sat", "GREEDY", t2, {"order": "INDEX"}).answer
    g6 = run("sat", "GREEDY", t6, {"order": "MENTION"}).answer
    if any(isinstance(a, str) or not S.satisfies(c2, a) for a in (gm, gi, g6)):
        stats.reject("a GREEDY order does not reach a satisfying assignment")
        return None
    if min(CC.hamming(gm, gi), CC.hamming(gm, g6), CC.hamming(gi, g6)) < params["min_hamming"]:
        stats.reject("GREEDY assignments closer than the Hamming threshold")
        return None
    pol = run("sat", "POLARITY", t2).answer
    if pol in (gm, gi, g6):
        stats.reject("POLARITY equals a GREEDY assignment")
        return None
    uc_differs = any(run("sat", "UC", t).answer != run("sat", "GREEDY", t, {"order": "MENTION"}).answer for t in (t2, t6))
    if not uc_differs:
        stats.reject("UC-DET equals GREEDY on every copy")
        return None
    n_sol = CC.count_models(c2)
    if n_sol < params["min_solutions"]:
        stats.reject("too few solutions")
        return None
    return {"n_solutions": n_sol}


def generate_sat(tier: str, seed: int, per_cell: int, params: dict[str, Any], stats: GenStats) -> list:
    items = []
    attempt = 0
    accepted = 0
    n = params["n_sat"]
    while accepted < per_cell:
        bseed = base_seed(tier, seed, attempt)
        attempt += 1
        stats.attempts += 1
        CC.guard(attempt, params, stats, "E1-SAT")
        rng = rng_for(bseed, "C-E1-SAT")
        alpha = params["alphas"][accepted % len(params["alphas"])]
        base = S.random_ksat(n, int(round(alpha * n)), 3, rng, tuple(f"u{i}" for i in range(n)))
        c = build_sat_copies(base, rng)
        info = sat_filters(c, params, stats)
        if info is None:
            continue
        set_items = []
        base_hash = sha(c["c2"].content_key())
        sid = set_hash(bseed, "SAT")
        for copy, (cnf, order, struct) in c["copies"].items():
            task = SatTask(cnf, (), tuple(order) if order is not None else None)
            prompt = render_c(cnf, order)
            if params["repeat_prompt"]:
                prompt = prompt + "\n\nHere is the same problem again, repeated verbatim:\n\n" + prompt
            gt = {**truth(task), "n_solutions": info["n_solutions"], "check": "any satisfying assignment"}
            set_items.append(make_item(
                vertical=VERTICAL, eval_id=EVAL_ID, set_id=sid, cell=f"SAT/{copy}", domain="3-SAT",
                framing="textbook", prompt=prompt, answer_format=CC.SAT_FORMAT, task=task, ground_truth=gt,
                specs=sat_members(copy), channel=CC.sat_channel(cnf, info["n_solutions"]), seed=bseed, tier=tier,
                generator=__name__, base_hash=base_hash, source_hash=None if copy == "c2-RELABEL" else base_hash,
                pair_id=f"E1-SAT-{sid}",
                params={"n": n, "m": cnf.m, "alpha": alpha, "copy": copy, "structure": struct,
                        "clause_order_c6": c["clause_order"] if copy == "c6-RELIST" else None,
                        "repeat_prompt": params["repeat_prompt"], "prompt_tokens": tokens.count(prompt),
                        "tokenizer_proxy": tokens.PROXY_NAME},
                notes="GREEDY-MENTION's prediction moves with clause order (c6); GREEDY-INDEX's with labels "
                      "(c1 vs c2); POLARITY and UC's unit steps do not.",
                cell_note=f"Copy {copy}.",
            ))
        problems = check_set(set_items)
        if problems:
            stats.reject("set invariant failed: " + problems[0][:60])
            continue
        items += set_items
        accepted += 1
        stats.accepted += 1
    return items


# --- entry points --------------------------------------------------------------------------------------

DEFAULTS = {
    "domains": ["COL", "SAT"], "n_col": 16, "mean_degree": [4.0, 4.8], "min_optimal": 50, "max_grundy": 0.4,
    "max_partitions": 200_000, "serialisation": "adjacency", "repeat_prompt": False,
    "max_attempts": 50_000, "n_sat": 20, "alphas": [3.0, 3.5], "min_solutions": 20, "min_hamming": 4,
}


def generate(tier: str, seed: int, per_cell: int | None = None, **params) -> tuple[list, dict]:
    p = {**DEFAULTS, **params}
    per_cell = per_cell or TIERS[tier].default_per_cell
    stats = GenStats()
    items = []
    if "COL" in p["domains"]:
        items += generate_col(tier, seed, per_cell, p, stats)
    if "SAT" in p["domains"]:
        items += generate_sat(tier, seed, per_cell, p, stats)
    return items, stats.to_json()


def _before_answer(prompt: str) -> str:
    return prompt.split("After the line ANSWER:")[0]


def check_set(items: list) -> list[str]:
    errs: list[str] = []
    by = {it.cell.split("/", 1)[1]: it for it in items}
    if sorted(by) != sorted(COPIES):
        return [f"set has copies {sorted(by)}"]
    dom = "coloring" if items[0].cell.startswith("COL") else "sat"
    tasks = {c: load_task(it.instance) for c, it in by.items()}
    structs = {c: {k: int(v) for k, v in it.params["structure"].items()} for c, it in by.items()}
    # identical content up to the copy maps, and identical label multisets
    if dom == "coloring":
        shapes = {c: CC.structural_edges(t.graph, structs[c]) for c, t in tasks.items()}
        labels = {c: sorted(t.graph.vertices) for c, t in tasks.items()}
    else:
        shapes = {c: frozenset(frozenset((structs[c][t.cnf.name(l)], l > 0) for l in cl) for cl in t.cnf.clauses)
                  for c, t in tasks.items()}
        labels = {c: sorted(t.cnf.var_names) for c, t in tasks.items()}
    if len(set(shapes.values())) != 1:
        errs.append("copies are not isomorphic through their structure maps")
    if len({tuple(v) for v in labels.values()}) != 1:
        errs.append("label multisets differ")
    if len({repr(it.ground_truth) for it in items}) != 1:
        errs.append("ground truth differs across copies")
    # surface: equal token counts (relabelling changes which label repeats, so multisets differ)
    errs += surface.equal_token_counts({c: by[c].prompt for c in COPIES if c != "c5-ANS-FREE"})
    errs += surface.equal_token_counts({c: _before_answer(by[c].prompt) for c in COPIES})

    def sp(copy: str, label: str):
        ans = by[copy].predictions[label]["answer"]
        return CC.structural_partition(ans, structs[copy]) if dom == "coloring" else CC.structural_assignment(ans, structs[copy])

    lst, lab, out = ("FF-LIST", "FF-LABEL", "FF-OUT (AR)") if dom == "coloring" else ("GREEDY-MENTION", "GREEDY-INDEX", "GREEDY-OUT (AR)")
    first5 = [c for c in COPIES if c != "c6-RELIST"]
    if len({sp(c, lst) for c in first5}) != 1:
        errs.append(f"{lst} changes before c6")
    if sp("c6-RELIST", lst) == sp("c1-NAT", lst):
        errs.append(f"{lst} does not change at c6")
    if sp("c1-NAT", lab) != sp("c1-NAT", lst):
        errs.append(f"{lab} != {lst} in the natural format")
    if len({sp(c, lab) for c in COPIES[1:]}) != 1:
        errs.append(f"{lab} changes after c2")
    if sp("c2-RELABEL", lab) == sp("c1-NAT", lab):
        errs.append(f"{lab} does not change at c2")
    if sp("c3-ANS-LABEL", out) != sp("c3-ANS-LABEL", lab):
        errs.append(f"{out} does not follow the label order at c3")
    for c in ("c1-NAT", "c2-RELABEL", "c6-RELIST"):
        if sp(c, out) != sp(c, lst):
            errs.append(f"{out} does not follow the listing at {c}")
    if "FF-OUT (AR)" in by["c5-ANS-FREE"].predictions or "GREEDY-OUT (AR)" in by["c5-ANS-FREE"].predictions:
        errs.append("an OUT member is predicted on the FREE copy")
    return errs
