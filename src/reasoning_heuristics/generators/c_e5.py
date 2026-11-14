"""C E5: dead ends, false "impossible", violation localisation, controlled states
(C §2.6 E5, §2.8 E5-COL / E5-STATE / E5-ENT; E5-SAT from the E4-style pool).

E5-COL (study default n = 24, mean degree about 4.2, k = 3; vertex list plus a separate
edge list). Stuck graph: 3-colourable, not 2-colourable, and FF-3 in listing order gets
stuck at a vertex v* in the middle third of π_L. Factorial vertex order {A, B} x edge order
{A, B}: B-vertex is a re-listing in which FF-3 is still stuck but at a different vertex
v**; B-edge reverses the edge list. CONTROL: a different graph on which FF-3-LIST succeeds,
matched on n, m (+-1) and order-free hardness = decision nodes of degree-order
backtracking (within 25%, or 2 nodes). Cells STUCK/vA/eA, vB/eA, vA/eB, vB/eB, CONTROL/vA/eA.

E5-SAT (default n = 25, α = 3.5, satisfiable items only). DEAD: UC-DET and GREEDY-MENTION
both dead-end. DEAD-PERM: the same formula with the clause order permuted so that
GREEDY's dead end (variable or falsified clause) moves. CONTROL: a formula on which both
succeed, same n and α, order-free DPLL nodes (MOMS order, polarity values) within 20%.

E5-STATE (controlled partial states; same formula, different fixed values). SAT (default
n = 20, α = 3.5, the first 6 variables in mention order fixed): s1 GREEDY's completion is
valid while state-blind POLARITY falsifies a clause; s2 UC's completion is valid while
GREEDY falsifies a clause; s3 no completion exists. Colouring (n = 16, k = 3, the first 6
listed vertices coloured): s1 the FF continuation dead-ends but a completion exists;
s3 no completion exists (the doc has no colouring s2).

E5-ENT (5 atoms A-E, 4 premises from {if, or, not-both} over positive literals, a literal
conclusion; the library's wording). FAIL pair: the conclusion does not follow, GREEDY-CM
in premise order fails to find the countermodel (predicts YES) and finds it with the
premises reversed. MATCHED pair: GREEDY-CM finds it in both orders. ETR predictions come
from the PyETR members; the generator keeps the share of pairs on which ETR-default and
GREEDY-CM differ at >= 1/2 (doc: "must differ on at least half the pairs").

Readings of the doc (also in docs/GENERATORS.md):
- The colouring factorial includes vB/eB (the doc's prose says 2 x 2 and asks for the
  2 x 2 interaction; its cell table lists three stuck cells).
- B1 DROP-LAST drops the last q = 3 edges (q is not given in the doc; parameter `drop_q`).
- MIN-CONFLICTS (F) is not in the zoo; C4 is ONLINE-FF (edge-list order, never recolours).
- E5-P (the prefilled single-decision twin) is a runner condition, not a new item set.
- The SAT control uses "both members succeed" for "non-dead-end".
"""

from __future__ import annotations

from typing import Any

from reasoning_heuristics import tokens
from reasoning_heuristics.counterfactual.reorder import permutation, reorder_clauses
from reasoning_heuristics.generators import c_common as CC
from reasoning_heuristics.generators.common import GenStats, decision_channel, make_item, set_hash, witness_channel
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, SatTask, load_task
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.coloring.render import render_neighbours
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.render import render_c
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.truth import truth

VERTICAL, EVAL_ID = "C", "E5"
LEXICON_PARTITIONED = False
COL_CELLS = ["STUCK/vA/eA", "STUCK/vB/eA", "STUCK/vA/eB", "STUCK/vB/eB", "CONTROL/vA/eA"]
SAT_CELLS = ["DEAD", "DEAD-PERM", "CONTROL"]
STATE_CELLS = {"SAT": ["s1", "s2", "s3"], "COL": ["s1", "s3"]}
ENT_CELLS = ["FAIL/ORDER-A", "FAIL/ORDER-B", "MATCHED/ORDER-A", "MATCHED/ORDER-B"]
DEFAULTS = {"parts": ["COL", "SAT", "STATE", "ENT"], "n_col": 24, "col_mean_degree": 4.2, "drop_q": 3,
            "n_sat": 25, "alpha_sat": 3.5, "n_state_sat": 20, "alpha_state": 3.5, "n_fixed": 6,
            "n_state_col": 16, "n_atoms": 5, "n_premises": 4, "max_attempts": 50_000, "max_partitions": 500_000}


def cells(params: dict[str, Any]) -> list[str]:
    parts = params.get("parts", DEFAULTS["parts"])
    out = []
    if "COL" in parts:
        out += [f"COL/{c}" for c in COL_CELLS]
    if "SAT" in parts:
        out += [f"SAT/{c}" for c in SAT_CELLS]
    if "STATE" in parts:
        out += [f"STATE/{d}/{s}" for d in ("SAT", "COL") for s in STATE_CELLS[d]]
    if "ENT" in parts:
        out += [f"ENT/{c}" for c in ENT_CELLS]
    return out


# --- renderers (library wording) --------------------------------------------------------------------


def col_edge_prompt(g: Graph) -> str:
    return "\n".join([
        f"Graph with {g.n} vertices and {g.m} edges.",
        "Vertices (in this order): " + ", ".join(g.vertices),
        "Edges: " + ", ".join(f"{u}-{v}" for u, v in g.edges),
        "",
        "Colour every vertex with one of the colours 1, 2, ..., 3 so that the two ends of every edge get different "
        "colours. If this is impossible, answer IMPOSSIBLE.",
        "After the line ANSWER:, write IMPOSSIBLE or one line `vertex: colour` per vertex, in this order: "
        + ", ".join(g.vertices) + ".",
    ])


def col_state_prompt(g: Graph, fixed: list[tuple[str, int]]) -> str:
    text = render_neighbours(g, "k", list(g.vertices), 3)
    head, tail = text.split("\n\nColour every vertex", 1)
    vals = ", ".join(f"{v}: {c}" for v, c in fixed)
    return (head + f"\n\nThese vertices are already coloured and must not be changed: {vals}.\n\nColour every vertex"
            + tail.replace("If this is impossible, say IMPOSSIBLE.", "If this is impossible (keeping the fixed colours), say IMPOSSIBLE."))


def ent_prompt(task: EntailmentTask) -> str:
    def sent(p):
        if p[0] == "or":
            return " or ".join(F.render(d, False) for d in p[1]) + " (or both)."
        if p[0] == "nand":
            return "Not both " + " and ".join(F.render(d, False) for d in p[1]) + "."
        if p[0] == "if":
            return f"If {F.render(p[1], False)}, then {F.render(p[2], False)}."
        return F.sentence(p)

    lines = ["Premises:"] + [f"{i}. {sent(p)}" for i, p in enumerate(task.premises, 1)]
    concl = F.render(task.probe, False)
    lines += ["", f"Conclusion: {concl[0].upper() + concl[1:]}.", "",
              "After the line ANSWER:, write YES if the conclusion must be true whenever all premises are true, otherwise NO."]
    return "\n".join(lines)


# --- E5-COL ---------------------------------------------------------------------------------------------


def col_members(q: int) -> list:
    return [
        ("FF-3-LIST-ABORT (C1)", "FF", {"order": "LIST", "k": 3, "mode": "ABORT"}),
        ("FF-3-LIST-INFEAS (C1)", "FF", {"order": "LIST", "k": 3, "mode": "INFEAS"}),
        ("FF-3-EDGE-MENTION-ABORT (C1 variant)", "FF", {"order": "EDGE", "k": 3, "mode": "ABORT"}),
        ("DSATUR-3 (C2)", "DSATUR", {"k": 3, "mode": "ABORT"}),
        ("GREEDY+REPAIR-LIST (C->F)", "GREEDY+REPAIR", {"order": "LIST", "k": 3}),
        ("DPLL-LIST (D)", "SEARCH", {"order": "LIST"}),
        (f"DROP-LAST-{q}-EDGES + exact (B1)", "DROP-LAST", {"q": q, "k": 3}),
        ("PHANTOM-ADJACENT (B4)", "PHANTOM", {"pairs": "adjacent-listed", "k": 3}),
        ("ONLINE-FF (C4)", "ONLINE-FF", {"k": 3}),
        ("EXACT", "EXACT", {}),
        ("RANDOM (H)", "RANDOM", {}),
        ("NOISY-EXACT", "NOISY-EXACT", {"p": 0.01}),
    ]


def ff3(g: Graph) -> Any:
    return run("coloring", "FF", ColouringTask(g, 3), {"order": "LIST", "k": 3, "mode": "ABORT"})


def order_free_nodes(g: Graph) -> int:
    return run("coloring", "SEARCH", ColouringTask(g, 3), {"order": "DEGREE", "tie": "LABEL"}).trace_features["decisions"]


def col_graph(rng, n: int, deg: float) -> Graph | None:
    m = int(round(deg * n / 2)) + int(rng.integers(-2, 3))
    g = G.random_gnm(CC.labels_for(n, "v", rng), m, rng)
    g = g.relisted(permutation(list(g.vertices), rng))
    g = Graph(g.vertices, tuple(permutation(list(g.edges), rng)))
    if G.k_colour(g, 3) is None or G.k_colour(g, 2) is not None:
        return None
    return g


def generate_col(tier, seed, per_cell, p, stats, attempt0) -> tuple[list, int]:
    items, attempt, accepted = [], attempt0, 0
    n = p["n_col"]
    while accepted < per_cell:
        bseed = base_seed(tier, seed, attempt)
        attempt += 1
        stats.attempts += 1
        CC.guard(attempt - attempt0, p, stats, "E5-COL")
        rng = rng_for(bseed, "C-E5-COL")
        g = col_graph(rng, n, p["col_mean_degree"])
        if g is None:
            stats.reject("COL: not exactly 3-chromatic")
            continue
        pred = ff3(g)
        stuck = pred.trace_features.get("stuck_vertex")
        if pred.answer != "IMPOSSIBLE" or not n // 3 <= g.position[stuck] < 2 * n // 3:
            stats.reject("COL: FF-3-LIST not stuck in the middle third")
            continue
        vB = None
        for _ in range(200):
            g2 = g.relisted(permutation(list(g.vertices), rng))
            pr2 = ff3(g2)
            if pr2.answer == "IMPOSSIBLE" and pr2.trace_features["stuck_vertex"] != stuck:
                vB = g2
                break
        if vB is None:
            stats.reject("COL: no re-listing moves the stuck vertex")
            continue
        hard = order_free_nodes(g)
        control = None
        for _ in range(400):
            c = col_graph(rng, n, p["col_mean_degree"])
            if c is None or abs(c.m - g.m) > 1 or ff3(c).answer == "IMPOSSIBLE":
                continue
            hc = order_free_nodes(c)
            if abs(hc - hard) <= max(2, 0.25 * hard):
                control = c
                break
        if control is None:
            stats.reject("COL: no matched control found")
            continue
        variants = {
            "STUCK/vA/eA": g, "STUCK/vB/eA": vB,
            "STUCK/vA/eB": Graph(g.vertices, tuple(reversed(g.edges))),
            "STUCK/vB/eB": Graph(vB.vertices, tuple(reversed(vB.edges))),
            "CONTROL/vA/eA": control,
        }
        sid = set_hash(bseed, "COL")
        set_items = []
        for cell, gg in variants.items():
            task = ColouringTask(gg, 3, (), tuple(gg.vertices))
            masks = G.enumerate_partitions(gg, 3, p["max_partitions"])
            if masks is None:
                break
            gt = {**truth(task), "n_colourings_up_to_renaming": len(masks),
                  "example": G.k_colour(gg, 3)}
            ch = CC.colouring_channel(gg, 3, len(masks))
            stuck_v = ff3(gg).trace_features.get("stuck_vertex")
            prompt = col_edge_prompt(gg)
            base_hash = sha((control if cell.startswith("CONTROL") else g).content_key())
            set_items.append(make_item(
                vertical=VERTICAL, eval_id=EVAL_ID, set_id=sid, cell=f"COL/{cell}", domain="colouring (k=3)",
                framing="textbook", prompt=prompt, answer_format=CC.COLOUR_K_FORMAT, task=task, ground_truth=gt,
                specs=col_members(p["drop_q"]), channel=ch, seed=bseed, tier=tier, generator=__name__,
                base_hash=base_hash, source_hash=None if cell in ("STUCK/vA/eA", "CONTROL/vA/eA") else base_hash,
                pair_id=f"E5-COL-{sid}",
                params={"n": gg.n, "m": gg.m, "design_cell": cell, "stuck_vertex": stuck_v,
                        "stuck_position": gg.position[stuck_v] if stuck_v else None,
                        "order_free_hardness_nodes": order_free_nodes(gg),
                        "listing_dpll_nodes": run("coloring", "SEARCH", task, {"order": "LIST"}).trace_features["decisions"],
                        "prompt_tokens": tokens.count(prompt), "tokenizer_proxy": tokens.PROXY_NAME},
                notes="Stuck-vs-control items are matched on n, m and order-free backtracking nodes; within the stuck "
                      "graph, vertex order and edge order are crossed.",
                cell_note=f"Cell {cell}.",
            ))
        if len(set_items) != len(variants):
            stats.reject("COL: colouring enumeration cap")
            continue
        problems = check_set(set_items)
        if problems:
            stats.reject("COL: set invariant failed: " + problems[0][:50])
            continue
        items += set_items
        accepted += 1
        stats.accepted += 1
    return items, attempt


# --- E5-SAT ---------------------------------------------------------------------------------------------


def sat_members() -> list:
    return [
        ("GREEDY-MENTION-ABORT (C1)", "GREEDY", {"order": "MENTION", "mode": "ABORT"}),
        ("GREEDY-MENTION-INFEAS (C1)", "GREEDY", {"order": "MENTION", "mode": "INFEAS"}),
        ("UC-DET (C2)", "UC", {}), ("GUC-DET (C2)", "GUC", {}), ("SC-DET (C2)", "SC", {}),
        ("POLARITY (C0)", "POLARITY", {}),
        ("DPLL-MENTION (D)", "SEARCH", {"order": "MENTION", "value": "TRUE"}),
        ("DPLL-MOMS-POLARITY (D)", "SEARCH", {"order": "MOMS", "value": "POLARITY"}),
        ("RO-GREEDY (C3)", "RO-GREEDY", {"samples": 200, "seed": 0}),
        ("EXACT", "EXACT", {}), ("RANDOM (H)", "RANDOM", {}),
    ]


def sat_nodes(cnf: S.CNF) -> int:
    return run("sat", "SEARCH", SatTask(cnf), {"order": "MOMS", "value": "POLARITY"}).trace_features["decisions"]


def labelled_cnf(rng, n: int, alpha: float) -> S.CNF:
    base = S.random_ksat(n, int(round(alpha * n)), 3, rng, tuple(f"u{i}" for i in range(n)))
    labels = CC.labels_for(n, "x", rng)
    mo = base.mention_order() + [v for v in range(1, n + 1) if v not in base.mention_order()]
    return base.renamed({base.var_names[v - 1]: labels[i] for i, v in enumerate(mo)})


def sat_dead_end(cnf: S.CNF) -> tuple[bool, dict]:
    t = SatTask(cnf)
    g = run("sat", "GREEDY", t, {"order": "MENTION"})
    u = run("sat", "UC", t)
    return g.answer == "UNSAT" and u.answer == "UNSAT", {"greedy": g.trace_features.get("dead_end"), "uc": u.trace_features.get("dead_end")}


def generate_sat(tier, seed, per_cell, p, stats, attempt0) -> tuple[list, int]:
    items, attempt, accepted = [], attempt0, 0
    n, alpha = p["n_sat"], p["alpha_sat"]
    while accepted < per_cell:
        bseed = base_seed(tier, seed, attempt)
        attempt += 1
        stats.attempts += 1
        CC.guard(attempt - attempt0, p, stats, "E5-SAT")
        rng = rng_for(bseed, "C-E5-SAT")
        cnf = labelled_cnf(rng, n, alpha)
        if S.solve(cnf) is None:
            stats.reject("SAT: unsatisfiable")
            continue
        dead, where = sat_dead_end(cnf)
        if not dead:
            stats.reject("SAT: GREEDY and UC do not both dead-end")
            continue
        perm = None
        for _ in range(50):
            c2 = reorder_clauses(cnf, [int(i) for i in rng.permutation(cnf.m)])
            d2, w2 = sat_dead_end(c2)
            if not d2:
                continue
            gc1 = cnf.clauses[int(where["greedy"]["clause"][1:]) - 1]
            gc2 = c2.clauses[int(w2["greedy"]["clause"][1:]) - 1]
            if w2["greedy"]["variable"] != where["greedy"]["variable"] or sorted(gc1) != sorted(gc2):
                perm = c2
                break
        if perm is None:
            stats.reject("SAT: no clause order moves GREEDY's dead end")
            continue
        hard = sat_nodes(cnf)
        control = None
        for _ in range(3000):
            c = labelled_cnf(rng, n, alpha)
            t = SatTask(c)
            if run("sat", "GREEDY", t, {"order": "MENTION"}).answer == "UNSAT" or run("sat", "UC", t).answer == "UNSAT":
                continue
            if abs(sat_nodes(c) - hard) <= max(1, 0.2 * hard):
                control = c
                break
        if control is None:
            stats.reject("SAT: no matched control found")
            continue
        sid = set_hash(bseed, "SAT")
        set_items = []
        for cell, c in (("DEAD", cnf), ("DEAD-PERM", perm), ("CONTROL", control)):
            order = sorted(c.var_names, key=G.label_key)
            task = SatTask(c, (), tuple(order))
            n_sol = CC.count_models(c)
            prompt = render_c(c, order)
            base_hash = sha((control if cell == "CONTROL" else cnf).content_key())
            set_items.append(make_item(
                vertical=VERTICAL, eval_id=EVAL_ID, set_id=sid, cell=f"SAT/{cell}", domain="3-SAT", framing="textbook",
                prompt=prompt, answer_format=CC.SAT_FORMAT, task=task,
                ground_truth={**truth(task), "n_solutions": n_sol}, specs=sat_members(),
                channel=CC.sat_channel(c, n_sol), seed=bseed, tier=tier, generator=__name__, base_hash=base_hash,
                source_hash=base_hash if cell == "DEAD-PERM" else None, pair_id=f"E5-SAT-{sid}",
                params={"n": n, "m": c.m, "alpha": alpha, "design_cell": cell, "order_free_dpll_nodes": sat_nodes(c),
                        "greedy_dead_end": sat_dead_end(c)[1]["greedy"], "uc_dead_end": sat_dead_end(c)[1]["uc"],
                        "prompt_tokens": tokens.count(prompt), "tokenizer_proxy": tokens.PROXY_NAME},
                notes="Dead-end items (UC-DET and GREEDY both get stuck) against a matched control; the permuted copy "
                      "moves GREEDY's dead end.",
                cell_note=f"Cell {cell}.",
            ))
        problems = check_set(set_items)
        if problems:
            stats.reject("SAT: set invariant failed: " + problems[0][:50])
            continue
        items += set_items
        accepted += 1
        stats.accepted += 1
    return items, attempt


# --- E5-STATE ---------------------------------------------------------------------------------------------


def state_sat_members() -> list:
    return [
        ("GREEDY-MENTION from state (C1)", "GREEDY", {"order": "MENTION", "mode": "INFEAS"}),
        ("GREEDY-MENTION-ABORT from state (C1)", "GREEDY", {"order": "MENTION", "mode": "ABORT"}),
        ("POLARITY (C0, ignores state)", "POLARITY", {}),
        ("UC-DET from state (C2)", "UC", {}), ("GUC-DET from state (C2)", "GUC", {}), ("SC-DET from state (C2)", "SC", {}),
        ("DPLL from state (D)", "SEARCH", {"order": "MENTION"}),
        ("EXACT", "EXACT", {}), ("RANDOM (H)", "RANDOM", {}),
    ]


def state_col_members() -> list:
    return [
        ("FF-3-LIST from state (C1, ABORT)", "FF", {"order": "LIST", "k": 3, "mode": "ABORT"}),
        ("FF-3-LIST from state (C1, INFEAS)", "FF", {"order": "LIST", "k": 3, "mode": "INFEAS"}),
        ("DSATUR-3 from state (C2)", "DSATUR", {"k": 3, "mode": "ABORT"}),
        ("GREEDY+REPAIR-LIST (C->F)", "GREEDY+REPAIR", {"order": "LIST", "k": 3}),
        ("DPLL-LIST from state (D)", "SEARCH", {"order": "LIST"}),
        ("EXACT", "EXACT", {}), ("RANDOM (H)", "RANDOM", {}),
    ]


def sat_state_classes(cnf: S.CNF, fixed: dict[str, bool]) -> str | None:
    t = SatTask(cnf, tuple(fixed.items()))
    if S.solve(cnf, fixed) is None:
        return "s3"
    g = run("sat", "GREEDY", t, {"order": "MENTION", "mode": "INFEAS"})
    pol = run("sat", "POLARITY", t)
    uc = run("sat", "UC", t)
    g_ok = not g.trace_features["falsified"]
    if g_ok and pol.trace_features["falsified"]:
        return "s1"
    if not g_ok and uc.answer != "UNSAT" and not uc.trace_features["falsified"]:
        return "s2"
    return None


def count_completions(g: Graph, k: int, fixed: dict[str, int]) -> int:
    col = dict(fixed)
    free = [v for v in g.vertices if v not in col]

    def rec(i: int) -> int:
        if i == len(free):
            return 1
        v = free[i]
        used = {col[u] for u in g.adj[v] if u in col}
        total = 0
        for c in range(1, k + 1):
            if c not in used:
                col[v] = c
                total += rec(i + 1)
                del col[v]
        return total

    return rec(0)


def completion_test(g: Graph, fixed: dict[str, int]):
    def test(key: str) -> bool:
        classes = CC.parse_partition_key(key)
        if classes is None or len(classes) > 3:
            return False
        if any(g.has_edge(u, v) for c in classes for i, u in enumerate(c) for v in c[i + 1:]):
            return False
        # consistent with the fixed colours up to renaming
        cls_of = {v: i for i, c in enumerate(classes) for v in c}
        pairs = {}
        for v, c in fixed.items():
            if pairs.setdefault(cls_of[v], c) != c:
                return False
        return len(set(pairs.values())) == len(pairs)

    return test


def generate_state(tier, seed, per_cell, p, stats, attempt0) -> tuple[list, int]:
    items, attempt = [], attempt0
    for domain in ("SAT", "COL"):
        accepted = 0
        while accepted < per_cell:
            bseed = base_seed(tier, seed, attempt)
            attempt += 1
            stats.attempts += 1
            CC.guard(attempt - attempt0, p, stats, f"E5-STATE-{domain}")
            rng = rng_for(bseed, f"C-E5-STATE-{domain}")
            found: dict[str, Any] = {}
            if domain == "SAT":
                cnf = labelled_cnf(rng, p["n_state_sat"], p["alpha_state"])
                mo = cnf.mention_order()
                fixed_vars = [cnf.var_names[v - 1] for v in mo[: p["n_fixed"]]]
                for bits in range(2 ** len(fixed_vars)):
                    fixed = {x: bool(bits >> i & 1) for i, x in enumerate(fixed_vars)}
                    cls = sat_state_classes(cnf, fixed)
                    if cls and cls not in found:
                        found[cls] = fixed
            else:
                n = p["n_state_col"]
                lo, hi = int(round(4.0 * n / 2)), int(round(4.8 * n / 2))
                g = G.random_gnm(CC.labels_for(n, "v", rng), int(rng.integers(lo, hi + 1)), rng)
                g = g.relisted(permutation(list(g.vertices), rng))
                if G.k_colour(g, 3) is None:
                    stats.reject("STATE-COL: not 3-colourable")
                    continue
                head = list(g.vertices[: p["n_fixed"]])
                order = [int(i) for i in rng.permutation(3 ** len(head))]
                for code in order:
                    fixed = {v: code // 3 ** i % 3 + 1 for i, v in enumerate(head)}
                    if any(fixed[u] == fixed[v] for u in head for v in head if u < v and g.has_edge(u, v)):
                        continue
                    t = ColouringTask(g, 3, tuple(fixed.items()))
                    exists = G.k_colour(g, 3, fixed) is not None
                    ff = run("coloring", "FF", t, {"order": "LIST", "k": 3, "mode": "ABORT"}).answer
                    cls = "s3" if not exists else ("s1" if ff == "IMPOSSIBLE" else None)
                    if cls and cls not in found:
                        found[cls] = fixed
                    if len(found) == 2:
                        break
            if sorted(found) != STATE_CELLS[domain]:
                stats.reject(f"STATE-{domain}: not every state reachable")
                continue
            sid = set_hash(bseed, "STATE", domain)
            set_items = []
            for cell in STATE_CELLS[domain]:
                fixed = found[cell]
                if domain == "SAT":
                    order = [cnf.var_names[v - 1] for v in cnf.mention_order()] + [x for x in cnf.var_names if cnf.index(x) not in cnf.mention_order()]
                    task = SatTask(cnf, tuple(fixed.items()), tuple(order))
                    prompt = render_c(cnf, order, fixed)
                    n_sol = CC.count_models(cnf, fixed)
                    gt = {**truth(task), "n_completions": n_sol}
                    ch = CC.sat_channel(cnf, n_sol, fixed)
                    specs, base_hash, dom = state_sat_members(), sha(cnf.content_key()), "3-SAT (partial assignment given)"
                    fmt = CC.SAT_FORMAT
                else:
                    fx = list(fixed.items())
                    task = ColouringTask(g, 3, tuple(fx), tuple(g.vertices))
                    prompt = col_state_prompt(g, fx)
                    n_c = count_completions(g, 3, fixed)
                    gt = {**truth(task), "n_completions": n_c}
                    sv = {"RANDOM": (lambda key: False, 1)}
                    if n_c:
                        sv["EXACT"] = (completion_test(g, fixed), n_c)
                    ch = witness_channel("coloring", sv)
                    specs, base_hash, dom = state_col_members(), sha(g.content_key()), "colouring (k=3, partial colouring given)"
                    fmt = CC.COLOUR_K_FORMAT
                set_items.append(make_item(
                    vertical=VERTICAL, eval_id=EVAL_ID, set_id=sid, cell=f"STATE/{domain}/{cell}", domain=dom,
                    framing="textbook", prompt=prompt, answer_format=fmt, task=task, ground_truth=gt, specs=specs,
                    channel=ch, seed=bseed, tier=tier, generator=__name__, base_hash=base_hash,
                    source_hash=None if cell == "s1" else base_hash, pair_id=f"E5-STATE-{sid}",
                    params={"design_cell": cell, "fixed": fixed, "prompt_tokens": tokens.count(prompt),
                            "tokenizer_proxy": tokens.PROXY_NAME},
                    notes="Same instance in every state; only the fixed values differ. C0 ignores them, C1 counts only "
                          "the clauses they leave open, C2 follows the clauses they make unit.",
                    cell_note=f"State {cell}.",
                ))
            problems = check_set(set_items)
            if problems:
                stats.reject(f"STATE-{domain}: set invariant failed: " + problems[0][:40])
                continue
            items += set_items
            accepted += 1
            stats.accepted += 1
    return items, attempt


# --- E5-ENT ---------------------------------------------------------------------------------------------


def ent_members() -> list:
    return [
        ("GREEDY-CM-MENTION (C1)", "GREEDY-CM", {}),
        ("GREEDY-CM (not-C first) (C1)", "GREEDY-CM", {"neg_first": True}),
        ("TRUTH TABLE (exact)", "EXACT", {}),
        ("UP-fixpoint (B1, sound)", "UP-k", {"k": 10}),
        ("ALWAYS-YES (A1)", "ALWAYS-YES", {}),
        ("ETR-default (R1)", "ETR-default", {"rendering": "R1"}),
        ("ETR-1p (R1)", "ETR-1p", {"rendering": "R1"}),
        ("ONL(1) (C4)", "ONL", {"k": 1}), ("ONL(2) (C4)", "ONL", {"k": 2}),
        ("MM-S1 (B4)", "MM-S1", {"variant": "open"}), ("FIRST (B4)", "FIRST", {}),
        ("SAMPLE-3 (H)", "SAMPLE-m", {"m": 3}), ("RANDOM (H)", "RANDOM", {}),
        ("NOISY-EXACT", "NOISY-EXACT", {"p": 0.01}),
    ]


def random_premises(rng, atoms: list[str], k: int) -> tuple:
    out = []
    for _ in range(k):
        a, b = (atoms[int(i)] for i in rng.choice(len(atoms), 2, replace=False))
        kind = ["if", "or", "nand"][int(rng.integers(3))]
        la, lb = F.lit(a), F.lit(b)
        out.append({"if": ("if", la, lb), "or": ("or", (la, lb)), "nand": ("nand", (la, lb))}[kind])
    return tuple(out)


def greedy_cm(task: EntailmentTask) -> str:
    return run("entailment", "GREEDY-CM", task, {}).answer


def generate_ent(tier, seed, per_cell, p, stats, attempt0) -> tuple[list, int]:
    items, attempt, accepted = [], attempt0, 0
    atoms = [chr(ord("A") + i) for i in range(p["n_atoms"])]
    differ = total = 0
    pending: dict[str, tuple] = {}
    while accepted < per_cell:
        bseed = base_seed(tier, seed, attempt)
        attempt += 1
        stats.attempts += 1
        CC.guard(attempt - attempt0, p, stats, "E5-ENT")
        rng = rng_for(bseed, "C-E5-ENT")
        prem = random_premises(rng, atoms, p["n_premises"])
        concl = F.lit(atoms[int(rng.integers(len(atoms)))], bool(rng.integers(2)))
        a = EntailmentTask(prem, concl, "YN")
        b = EntailmentTask(tuple(reversed(prem)), concl, "YN")
        if not F.models(list(prem), atoms) or F.entails(list(prem), concl):
            stats.reject("ENT: inconsistent premises or the conclusion follows")
            continue
        ga, gb = greedy_cm(a), greedy_cm(b)
        kind = "FAIL" if (ga, gb) == ("YES", "NO") else "MATCHED" if (ga, gb) == ("NO", "NO") else None
        if kind is None or kind in pending:
            stats.reject("ENT: GREEDY-CM pattern not needed")
            continue
        etr = [run("entailment", "ETR-default", t, {"rendering": "R1"}).answer for t in (a, b)]
        d = int(etr[0] != ga or etr[1] != gb)
        if not d and (differ + sum(x[2] for x in pending.values())) < 0.5 * (total + len(pending) + 1):
            stats.reject("ENT: ETR agrees with GREEDY-CM (keeping the differ share >= 1/2)")
            continue
        pending[kind] = (a, b, d, bseed)
        if len(pending) < 2:
            continue
        sid = set_hash(pending["FAIL"][3], pending["MATCHED"][3], "ENT")
        set_items = []
        for kind in ("FAIL", "MATCHED"):
            ta, tb, _, kseed = pending[kind]
            base_hash = sha(ta.content_key())
            for order, t in (("ORDER-A", ta), ("ORDER-B", tb)):
                prompt = ent_prompt(t)
                gt = {**truth(t), "countermodels": len(F.countermodels(list(t.premises), t.probe))}
                set_items.append(make_item(
                    vertical=VERTICAL, eval_id=EVAL_ID, set_id=sid, cell=f"ENT/{kind}/{order}",
                    domain="propositional entailment", framing="textbook", prompt=prompt,
                    answer_format='After the line ANSWER:, YES or NO', task=t, ground_truth=gt, specs=ent_members(),
                    channel=decision_channel("YES", "NO"), seed=kseed, tier=tier, generator=__name__,
                    base_hash=base_hash, source_hash=base_hash if order == "ORDER-B" else None,
                    pair_id=f"E5-ENT-{base_hash[:10]}",
                    params={"design_cell": f"{kind}/{order}", "atoms": len(atoms), "premises": len(t.premises),
                            "premises_reversed": order == "ORDER-B", "prompt_tokens": tokens.count(prompt),
                            "tokenizer_proxy": tokens.PROXY_NAME},
                    notes="GREEDY-CM errs only by commission (YES when a countermodel exists) and its error depends on "
                          "premise order. ETR and C4 predictions are computed with the B4/C4 members.",
                    cell_note=f"Cell {kind}/{order}.",
                ))
        problems = check_set(set_items)
        if problems:
            stats.reject("ENT: set invariant failed: " + problems[0][:50])
            pending = {}
            continue
        differ += sum(x[2] for x in pending.values())
        total += len(pending)
        pending = {}
        items += set_items
        accepted += 1
        stats.accepted += 1
    stats_extra = {"pairs": total, "pairs_where_ETR_differs_from_GREEDY_CM": differ}
    return items, attempt, stats_extra


# --- entry points -----------------------------------------------------------------------------------------


def generate(tier: str, seed: int, per_cell: int | None = None, **params) -> tuple[list, dict]:
    p = {**DEFAULTS, **params}
    per_cell = per_cell or TIERS[tier].default_per_cell
    stats = GenStats()
    items: list = []
    attempt = 0
    extra: dict[str, Any] = {}
    if "COL" in p["parts"]:
        got, attempt = generate_col(tier, seed, per_cell, p, stats, attempt)
        items += got
    if "SAT" in p["parts"]:
        got, attempt = generate_sat(tier, seed, per_cell, p, stats, attempt)
        items += got
    if "STATE" in p["parts"]:
        got, attempt = generate_state(tier, seed, per_cell, p, stats, attempt)
        items += got
    if "ENT" in p["parts"]:
        got, attempt, extra = generate_ent(tier, seed, per_cell, p, stats, attempt)
        items += got
    out = stats.to_json()
    out["ent"] = extra
    return items, out


def check_set(items: list) -> list[str]:
    errs: list[str] = []
    part = items[0].cell.split("/")[0]
    by = {it.cell.split("/", 1)[1]: it for it in items}
    tasks = {c: load_task(it.instance) for c, it in by.items()}
    P = {c: it.predictions for c, it in by.items()}
    if part == "COL":
        if sorted(by) != sorted(COL_CELLS):
            return [f"COL set has cells {sorted(by)}"]
        stuck = [c for c in COL_CELLS if c.startswith("STUCK")]
        if len({frozenset(frozenset(e) for e in tasks[c].graph.edges) for c in stuck}) != 1:
            errs.append("stuck variants are not the same graph")
        for c in stuck:
            if P[c]["FF-3-LIST-ABORT (C1)"]["answer"] != "IMPOSSIBLE":
                errs.append(f"{c}: FF-3-LIST does not get stuck")
            if not by[c].ground_truth["colourable"]:
                errs.append(f"{c}: not 3-colourable")
        sv = {c: by[c].params["stuck_vertex"] for c in stuck}
        if sv["STUCK/vA/eA"] == sv["STUCK/vB/eA"]:
            errs.append("vertex order B does not move the stuck vertex")
        n = tasks["STUCK/vA/eA"].graph.n
        if not n // 3 <= by["STUCK/vA/eA"].params["stuck_position"] < 2 * n // 3:
            errs.append("the stuck vertex is not in the middle third")
        if list(tasks["STUCK/vA/eB"].graph.edges) != list(reversed(tasks["STUCK/vA/eA"].graph.edges)):
            errs.append("edge order B is not the reversed edge list")
        if tasks["STUCK/vA/eB"].graph.vertices != tasks["STUCK/vA/eA"].graph.vertices:
            errs.append("edge-order variant changed the vertex list")
        ctl = "CONTROL/vA/eA"
        if P[ctl]["FF-3-LIST-ABORT (C1)"]["answer"] == "IMPOSSIBLE" or not by[ctl].ground_truth["colourable"]:
            errs.append("control: FF-3-LIST fails or the graph is not 3-colourable")
        if abs(tasks[ctl].graph.m - tasks["STUCK/vA/eA"].graph.m) > 1 or tasks[ctl].graph.n != n:
            errs.append("control not matched on n, m")
        h, hc = by["STUCK/vA/eA"].params["order_free_hardness_nodes"], by[ctl].params["order_free_hardness_nodes"]
        if abs(h - hc) > max(2, 0.25 * h):
            errs.append("control not matched on order-free hardness")
    elif part == "SAT":
        if sorted(by) != sorted(SAT_CELLS):
            return [f"SAT set has cells {sorted(by)}"]
        for c in ("DEAD", "DEAD-PERM"):
            if P[c]["GREEDY-MENTION-ABORT (C1)"]["answer"] != "UNSAT" or P[c]["UC-DET (C2)"]["answer"] != "UNSAT":
                errs.append(f"{c}: GREEDY and UC do not both dead-end")
        if any(isinstance(P["CONTROL"][m]["answer"], str) for m in ("GREEDY-MENTION-ABORT (C1)", "UC-DET (C2)")):
            errs.append("CONTROL: a member dead-ends")
        if not all(by[c].ground_truth["satisfiable"] for c in SAT_CELLS):
            errs.append("an item is unsatisfiable")
        d, pm = tasks["DEAD"].cnf, tasks["DEAD-PERM"].cnf
        if sorted(map(sorted, d.clauses)) != sorted(map(sorted, pm.clauses)) or d.var_names != pm.var_names:
            errs.append("the permuted copy is not the same formula")
        if by["DEAD"].params["greedy_dead_end"] == by["DEAD-PERM"].params["greedy_dead_end"]:
            errs.append("the permutation does not move GREEDY's dead end")
        c = tasks["CONTROL"].cnf
        if c.n != d.n or c.m != d.m:
            errs.append("control not matched on n, m")
        h, hc = by["DEAD"].params["order_free_dpll_nodes"], by["CONTROL"].params["order_free_dpll_nodes"]
        if abs(h - hc) > max(1, 0.2 * h):
            errs.append("control not matched on order-free DPLL nodes")
    elif part == "STATE":
        domain = items[0].cell.split("/")[1]
        sub = {c.split("/")[1]: it for c, it in by.items()}
        if sorted(sub) != STATE_CELLS[domain]:
            return [f"STATE set has states {sorted(sub)}"]
        ts = {s: load_task(it.instance) for s, it in sub.items()}
        inst = {repr((t.cnf if domain == "SAT" else t.graph).content_key()) for t in ts.values()}
        if len(inst) != 1:
            errs.append("states are not on the same instance")
        for s, it in sub.items():
            exists = it.ground_truth["satisfiable" if domain == "SAT" else "colourable"]
            if (s == "s3") == exists:
                errs.append(f"{s}: completion existence contradicts the state")
            pr = it.predictions
            if domain == "SAT":
                g_bad = bool(pr["GREEDY-MENTION from state (C1)"]["trace_features"]["falsified"])
                if s == "s1" and (g_bad or not pr["POLARITY (C0, ignores state)"]["trace_features"]["falsified"]):
                    errs.append("s1: GREEDY not valid or POLARITY valid")
                if s == "s2" and (not g_bad or isinstance(pr["UC-DET from state (C2)"]["answer"], str)
                                  or pr["UC-DET from state (C2)"]["trace_features"]["falsified"]):
                    errs.append("s2: GREEDY valid or UC invalid")
            elif s == "s1" and pr["FF-3-LIST from state (C1, ABORT)"]["answer"] != "IMPOSSIBLE":
                errs.append("COL s1: the FF continuation does not dead-end")
    elif part == "ENT":
        if sorted(by) != sorted(ENT_CELLS):
            return [f"ENT set has cells {sorted(by)}"]
        want = {"FAIL/ORDER-A": "YES", "FAIL/ORDER-B": "NO", "MATCHED/ORDER-A": "NO", "MATCHED/ORDER-B": "NO"}
        for c, w in want.items():
            if P[c]["GREEDY-CM-MENTION (C1)"]["answer"] != w:
                errs.append(f"{c}: GREEDY-CM gives {P[c]['GREEDY-CM-MENTION (C1)']['answer']}, design {w}")
            if by[c].ground_truth["answer"] != "NO":
                errs.append(f"{c}: the conclusion follows")
        for kind in ("FAIL", "MATCHED"):
            ta, tb = tasks[f"{kind}/ORDER-A"], tasks[f"{kind}/ORDER-B"]
            if tuple(reversed(ta.premises)) != tb.premises or ta.probe != tb.probe:
                errs.append(f"{kind}: ORDER-B is not ORDER-A with the premises reversed")
    else:
        errs.append(f"unknown part {part}")
    return errs
