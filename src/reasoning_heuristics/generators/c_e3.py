"""C E3: depth-stress gadgets, const vs seq (C §2.6 E3, §2.8 E3-COL).

Construction (two layered NOR circuits; the standard LFMIS-reduction idea):
- circuits A (holds the target) and B (holds the placebo inputs), width W = 3, layers
  1..D_max (default 8); every gate is NOR of two gates (or inputs) of the previous layer;
  B gates take each input from A's previous layer with probability `cross_p` = 0.5, so
  edges run A -> B only;
- every primary input x has a pendant p_x; the pair is listed as adjacent lines (x, p_x)
  ("x True") or (p_x, x) ("x False");
- listing: the reference pair (a B input pair, never swapped) first, then the other input
  pairs, then the gates layer by layer with A and B interleaved, then three pendant
  triangles on random gates (so χ = 3), then the target, listed last;
- the target is an extra sink gate of A at layer d: NOR of two A gates of layer d - 1.
  The circuit is the same size for every depth, so n and m do not depend on d.

Lemma (checked on every item): under FF-LIST a circuit vertex gets colour 1 iff its NOR
value is True (a gate's earlier neighbours are exactly its two inputs).

Versions (the *same labelled graph*, two adjacent lines exchanged):
BASE; CRITICAL = swap a sensitive A input/pendant pair (the target flips under FF-LIST);
PLACEBO = swap a B input pair (outside the target's cone, so it cannot flip).
Arms: U-LIST (3-colouring, answer in listing order), U-REV (answer in reversed order),
I (instructed first-fit: "what colour does t get?"). The U readout is the bit "the
target shares a colour with the first-listed vertex" (always colour 1 under FF).

Depth, two ways. `target_depth` d counts gate layers (the cell label; the critical swap is
d levels below the target). LOCAL-t-LIST counts rounds: it colours a vertex in the round
equal to its first-fit dependency depth (1 + the depth of its deepest earlier-listed
neighbour), and gives it the default colour 1 otherwise. The inputs take a round, and an
input listed after its pendant ("False") a second, so the target's first-fit depth is
D = d + 2 (d + 1 when every input in its cone is "True"). Gadgets are kept only if D = d + 2
in all three versions (filter `target_ff_depth = d + 2`, recorded in params), so LOCAL-t-LIST
reaches the target iff t >= D and the doc's recovery gate "d* for LOCAL-t-LIST = t" holds with
depth measured as `target_ff_depth` (in gate layers, d* = t - 2). The listed proxies are
LOCAL-(D-1) (one round short: the default colour) and LOCAL-D (= FF-LIST on the target).

Balancing: within each depth the BASE target value alternates True / False, so
P(FF target = colour 1) = 0.5 up to parity. The proxy audit enforces |acc - 0.5| <= 0.05 + 1/N_d
for every LOCAL-t-LIST proxy that cannot see the target or its inputs: t < D with leftovers
coloured 1, and t < D - 2 with leftovers given their smallest free colour (the target's inputs
sit at first-fit depth D - 2 or D - 1, and that default reads the target off whichever inputs
are already coloured, so it reaches the target at t = D - 1). These proxies are constant on the
target by construction, so the audit checks the balance; the target's degree, position and
earlier-neighbour parity are constant here too. LOCAL-(D-2)-LIST with the free default is
reported in the stats, not enforced: it sees the inputs whose cones are all "True", and at
d = 1 it decodes the target exactly (a True input is coloured in round 1, a False one is not).

Likelihoods. U arms score the bit (same / different; an IMPOSSIBLE answer is class other).
EXACT is set-valued over the proper 3-colourings; its share of "same" is counted exactly
(variable elimination; the counts are the same for all versions of a triple). The I arm
scores the colour number; the instructed procedure *is* FF-LIST, so EXACT (an optimal
colouring with arbitrary colour names) is not listed there. The I arm's question (the
listing order and the target) is part of its task and content hash.

Readings of the doc (also in docs/GENERATORS.md):
- Size: W = 3, D_max = 8 gives n = 67, m = 113 (the doc quotes 68 / 114; its construction
  has one more vertex and edge than the one described, which we could not identify).
  D_max > 11 needs more than 90 vertices, so labels become three-digit (still equal width).
- E3-SAT (gated on E1-SAT showing GREEDY weight) and E3-NN are not built.
- NOISY-FF-ε is not in the zoo; RO-FF is left out of these items (its bit probabilities need a
  channel-aware Monte Carlo). RANDOM (H) is listed: its channel probabilities are exact.
- Lineage: BASE/U-LIST is the set's base; BASE/U-REV and BASE/I are derived from it, and each
  CRITICAL / PLACEBO item from the BASE item of the same arm.
"""

from __future__ import annotations

import itertools
from typing import Any

import networkx as nx

from reasoning_heuristics import tokens
from reasoning_heuristics.counterfactual import surface
from reasoning_heuristics.counterfactual.reorder import permutation
from reasoning_heuristics.generators import c_common as CC
from reasoning_heuristics.generators.common import (OTHER, Channel, GenStats, SetSpec, content_hash, make_item,
                                                     set_hash, target_bit_channel, target_colour_channel)
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.tasks import ColouringTask, load_task
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.coloring.render import render_neighbours
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.independent import recheck_readouts
from reasoning_heuristics.validate.truth import truth

VERTICAL, EVAL_ID = "C", "E3"
LEXICON_PARTITIONED = False
VERSIONS = ("BASE", "CRITICAL", "PLACEBO")
ARMS = ("U-LIST", "U-REV", "I")
DEFAULTS = {"width": 3, "D_max": 8, "depths": [1, 2, 3, 4, 6, 8], "cross_p": 0.5, "n_triangles": 3,
            "max_attempts": 5000, "repeat_prompt": False}


def cells(params: dict[str, Any]) -> list[str]:
    depths = params.get("depths", DEFAULTS["depths"])
    return [f"d={d}/{v}/{a}" for d in depths for v in VERSIONS for a in ARMS]


# --- the gadget -------------------------------------------------------------------------------------


def build_gadget(rng, W: int, D_max: int, depth: int, cross_p: float, n_tri: int) -> dict[str, Any]:
    """Internal names: A0_i / B0_i inputs, A0_i_p pendants, A{L}_j / B{L}_j gates, T target."""
    gates: dict[str, tuple[str, str]] = {}
    layers = {c: [[f"{c}0_{i}" for i in range(W)]] for c in "AB"}
    for L in range(1, D_max + 1):
        for c in "AB":
            row = []
            for j in range(W):
                name = f"{c}{L}_{j}"
                if c == "A":
                    a, b = (layers["A"][L - 1][int(x)] for x in rng.choice(W, 2, replace=False))
                else:
                    pool = [(layers["A"] if rng.random() < cross_p else layers["B"])[L - 1][int(rng.integers(W))] for _ in range(2)]
                    while pool[0] == pool[1]:
                        pool[1] = (layers["A"] if rng.random() < cross_p else layers["B"])[L - 1][int(rng.integers(W))]
                    a, b = pool
                gates[name] = (a, b)
                row.append(name)
            layers[c].append(row)
    t_inputs = [layers["A"][depth - 1][int(x)] for x in rng.choice(W, 2, replace=False)]
    gates["T"] = (t_inputs[0], t_inputs[1])
    inputs = [f"{c}0_{i}" for c in "AB" for i in range(W)]
    pendant = {x: x + "_p" for x in inputs}
    gate_list = [g for g in gates if g != "T"]
    tri_hosts = [gate_list[int(i)] for i in rng.choice(len(gate_list), n_tri, replace=False)]
    tri = [(f"t{k}a", f"t{k}b", h) for k, h in enumerate(tri_hosts)]
    edges = [(x, pendant[x]) for x in inputs]
    for g, (a, b) in gates.items():
        edges += [(a, g), (b, g)]
    for ta, tb, h in tri:
        edges += [(h, ta), (h, tb), (ta, tb)]
    # listing
    orient = {x: bool(rng.integers(2)) for x in inputs}  # True: x before its pendant ("x True")
    ref = "B0_0"
    others = permutation([x for x in inputs if x != ref], rng)
    listing: list[str] = []
    for x in [ref] + others:
        listing += [x, pendant[x]] if orient[x] else [pendant[x], x]
    for L in range(1, D_max + 1):
        listing += permutation(layers["A"][L] + layers["B"][L], rng)
    for ta, tb, _ in permutation(tri, rng):
        listing += [ta, tb]
    listing.append("T")
    return {"gates": gates, "inputs": inputs, "pendant": pendant, "orient": orient, "listing": listing,
            "edges": edges, "ref": ref, "depth": depth}


def nor_values(gadget: dict[str, Any], orient: dict[str, bool]) -> dict[str, bool]:
    vals = dict(orient)
    for g, (a, b) in gadget["gates"].items():  # gates are created in topological order
        vals[g] = not (vals[a] or vals[b])
    return vals


def swap_pair(listing: list[str], x: str, p: str) -> list[str]:
    i, j = listing.index(x), listing.index(p)
    assert abs(i - j) == 1, "an input and its pendant must be adjacent lines"
    out = list(listing)
    out[i], out[j] = out[j], out[i]
    return out


# --- items ---------------------------------------------------------------------------------------------


def u_prompt(g: Graph, order: list[str], repeat: bool = False, style: str | None = None) -> str:
    """The library's uninstructed wording: 3-colouring, IMPOSSIBLE allowed in the question,
    the answer line asks for the colouring (`style`: the renderer's answer-line wording)."""
    return render_neighbours(g, "k", order, 3, repeat, style).replace("write IMPOSSIBLE or one line", "write one line")


def i_prompt(g: Graph, target: str) -> str:
    head = render_neighbours(g, "fewest", list(g.vertices)).split("\n\nColour every vertex")[0]
    return (head + "\n\nGo through the vertices one at a time in the listed order. Give each vertex the smallest "
            "positive integer not already used by one of its neighbours that come earlier in the list. "
            f"What colour does {target} get?\nAfter the line ANSWER:, write only the colour number of {target}.")


def members(arm: str, D: int) -> list:
    """D = the target's first-fit dependency depth (= d + 2 on every item)."""
    k = None if arm == "I" else 3
    specs = [
        ("FF-LIST (C1 seq)", "FF", {"order": "LIST", "k": k}),
        ("DSATUR (C2, label ties)", "DSATUR", {"tie": "LABEL", "k": k}),
        ("LF (C1 static, label ties)", "LF", {"tie": "LABEL", "k": k}),
        (f"LOCAL-{D - 1}-LIST (const proxy, one round short)", "LOCAL-t", {"t": D - 1, "ids": "LIST", "default": "one"}),
        (f"LOCAL-{D}-LIST (const proxy, reaches the target)", "LOCAL-t", {"t": D, "ids": "LIST", "default": "one"}),
        ("DPLL-LIST (D, k=3)", "SEARCH", {"order": "LIST"}),
    ]
    if arm != "I":
        specs.insert(1, ("FF-OUT (AR, answer order)", "FF", {"order": "OUT", "k": 3}))
        specs.append(("EXACT", "EXACT", {}))
    else:
        specs.append(("ANSWER-1 (A1 default; = LOCAL-0)", "LOCAL-t", {"t": 0, "ids": "LIST", "default": "one"}))
    specs.append(("RANDOM (H)", "RANDOM", {}))
    return specs


def random_spec(arm: str, n: int) -> SetSpec:
    """RANDOM (H) is uniform over the colourings with colours 1..k (k = 3 on the U arms, k = n
    on the fewest-colours I arm), so on the channel: the target matches the reference with
    probability 1/3, or the target's colour is uniform on 1..n."""
    if arm == "I":
        return SetSpec("fill", {}, n, f"uniform over the {n}^{n} colourings with colours 1..{n}: the target's colour "
                       f"is uniform on 1..{n}", class_counts={"1": 1, "2": 1, "3": 1, OTHER: n - 3})
    return SetSpec("fill", {}, 3, "uniform over the 3^n colourings with colours 1..3: the target shares the reference "
                   "vertex's colour with probability 1/3", class_counts={"same": 1, "different": 2})


def bit_channel(target: str, ref: str, set_valued: dict | None = None) -> Channel:
    """The U-arm readout: does the target share the reference vertex's colour? (common.target_bit_channel)"""
    return target_bit_channel(target, ref, set_valued)


def colour_channel(target: str, set_valued: dict | None = None) -> Channel:
    """The I-arm readout: the target's colour number (common.target_colour_channel)."""
    return target_colour_channel(target, set_valued)


def count_colourings(g: Graph, k: int, same: tuple[str, str] | None = None) -> int:
    """Exact number of proper colourings with colours 1..k, by variable elimination in
    min-degree order (the gadgets have small treewidth). `same=(a, b)` counts only the
    colourings with c(a) = c(b)."""
    rep = {v: v for v in g.vertices}
    if same is not None:
        rep[same[1]] = same[0]
    edges = set()
    for u, v in g.edges:
        u, v = rep[u], rep[v]
        if u == v:
            return 0
        edges.add((min(u, v), max(u, v)))
    neq = {(x, y): 1 for x in range(k) for y in range(k) if x != y}
    factors: list[tuple[tuple[str, ...], dict]] = [((u, v), neq) for u, v in sorted(edges)]
    adj: dict[str, set[str]] = {v: set() for v in set(rep.values())}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    total = 1
    while adj:
        v = min(adj, key=lambda x: (len(adj[x]), x))
        mine = [f for f in factors if v in f[0]]
        factors = [f for f in factors if v not in f[0]]
        scope = sorted({x for f in mine for x in f[0]} - {v})
        new = {}
        for assign in itertools.product(range(k), repeat=len(scope)):
            a = dict(zip(scope, assign))
            s = 0
            for c in range(k):
                a[v] = c
                prod = 1
                for vars_, tab in mine:
                    prod *= tab.get(tuple(a[x] for x in vars_), 0)
                    if not prod:
                        break
                s += prod
            if s:
                new[assign] = s
        if scope:
            factors.append((tuple(scope), new))
        else:
            total *= new.get((), 0)
        for x in scope:
            adj[x] |= set(scope) - {x}
            adj[x].discard(v)
        del adj[v]
    return total


def exact_bit_spec(g: Graph, target: str, ref: str) -> SetSpec:
    """EXACT on the bit channel: uniform over the proper 3-colourings (as partitions; every one
    uses all 3 colours, because of the triangles, so each is 3! labelled colourings)."""
    n_all, n_same = count_colourings(g, 3), count_colourings(g, 3, (target, ref))
    if n_all % 6 or n_same % 6:
        raise ValueError("a proper 3-colouring of the gadget uses fewer than 3 colours")
    return SetSpec("colouring", {"graph": "stated", "colours": 3}, n_all // 6, "proper 3-colouring",
                   class_counts={"same": n_same // 6, "different": (n_all - n_same) // 6})


def ff_depth(g: Graph, v: str) -> int:
    """First-fit dependency depth in listing order: 1 + the depth of the deepest earlier-listed
    neighbour. LOCAL-t-LIST colours v (with FF's colour) iff t >= this."""
    depth: dict[str, int] = {}
    for x in g.vertices:
        depth[x] = 1 + max((depth[u] for u in g.adj[x] if g.position[u] < g.position[x]), default=0)
        if x == v:
            return depth[x]
    raise KeyError(v)


def make_triple(gadget: dict[str, Any], rng, tier: str, bseed: int, triple: int, params: dict[str, Any]) -> list | None:
    """The nine items of one gadget, or None if the target's first-fit depth is not d + 2 in
    every version (the depth-accounting filter)."""
    d = gadget["depth"]
    names = gadget["listing"]
    labels = CC.labels_for(len(names), "v", rng)
    lab = dict(zip(names, permutation(labels, rng)))  # labels independent of the listing
    vals = nor_values(gadget, gadget["orient"])
    sens = []
    for x in gadget["inputs"]:
        if x.startswith("A"):
            flipped = dict(gadget["orient"])
            flipped[x] = not flipped[x]
            if nor_values(gadget, flipped)["T"] != vals["T"]:
                sens.append(x)
    crit = sens[int(rng.integers(len(sens)))]
    plac_pool = [x for x in gadget["inputs"] if x.startswith("B") and x != gadget["ref"]]
    plac = plac_pool[int(rng.integers(len(plac_pool)))]
    listings = {
        "BASE": names,
        "CRITICAL": swap_pair(names, crit, gadget["pendant"][crit]),
        "PLACEBO": swap_pair(names, plac, gadget["pendant"][plac]),
    }
    edges = tuple((lab[u], lab[v]) for u, v in gadget["edges"])
    graphs = {version: Graph(tuple(lab[v] for v in order), edges) for version, order in listings.items()}
    target, ref_v = lab["T"], lab[names[0]]
    D = d + 2
    if any(ff_depth(g, target) != D for g in graphs.values()):
        return None
    graph_nx = nx.Graph(list(edges))
    circuit = {"gates": [[lab[g], lab[a], lab[b]] for g, (a, b) in gadget["gates"].items()],  # topological order
               "input_pairs": [[lab[x], lab[gadget["pendant"][x]]] for x in gadget["inputs"]]}
    exact = exact_bit_spec(graphs["BASE"], target, ref_v)  # one labelled graph: the same for every version
    sid = set_hash(bseed, d, triple)

    def u_task(g: Graph, arm: str) -> ColouringTask:
        listing = list(g.vertices)
        return ColouringTask(g, 3, (), tuple(listing if arm == "U-LIST" else listing[::-1]))

    def i_task(g: Graph) -> ColouringTask:
        return ColouringTask(g, None, (), tuple(g.vertices), target=target)

    base_hash = content_hash(u_task(graphs["BASE"], "U-LIST"))
    base_of_arm = {"U-LIST": base_hash, "U-REV": content_hash(u_task(graphs["BASE"], "U-REV")),
                   "I": content_hash(i_task(graphs["BASE"]))}
    items = []
    for version, g in graphs.items():
        swapped = {"BASE": None, "CRITICAL": crit, "PLACEBO": plac}[version]
        dist = None
        if swapped and nx.has_path(graph_nx, lab[swapped], target):
            dist = nx.shortest_path_length(graph_nx, lab[swapped], target)
        for arm in ARMS:
            if arm == "I":
                task = i_task(g)
                prompt = i_prompt(g, target)
                gt = {**truth(task), "check": "unique: first-fit colour of the target in listing order"}
                channel = colour_channel(target, {"RANDOM (H)": random_spec(arm, g.n)})
                fmt = f"After the line ANSWER:, only the colour number of {target}"
            else:
                task = u_task(g, arm)
                prompt = u_prompt(g, list(task.answer_order), params["repeat_prompt"])
                gt = {**truth(task), "readout": f"bit = {target} has the same colour as {ref_v} (first-listed vertex)",
                      "check": "any proper 3-colouring is correct; the bit is a fingerprint, not a correctness criterion"}
                channel = bit_channel(target, ref_v, {"EXACT": exact, "RANDOM (H)": random_spec(arm, g.n)})
                fmt = CC.COLOUR_K_FORMAT
            if version == "BASE":
                source = None if arm == "U-LIST" else base_hash
            else:
                source = base_of_arm[arm]
            items.append(make_item(
                vertical=VERTICAL, eval_id=EVAL_ID, set_id=sid, cell=f"d={d}/{version}/{arm}", domain="colouring (gadget)",
                framing="textbook", prompt=prompt, answer_format=fmt, task=task, ground_truth=gt,
                specs=members(arm, D), channel=channel, seed=bseed, tier=tier, generator=__name__,
                base_hash=base_hash, source_hash=source, pair_id=f"E3-{sid}",
                params={"width": params["width"], "D_max": params["D_max"], "target_depth": d, "target_ff_depth": D,
                        "n": g.n, "m": g.m, "version": version, "arm": arm, "target": target, "reference_vertex": ref_v,
                        "swap": None if swapped is None else {"input": lab[swapped], "pendant": lab[gadget["pendant"][swapped]],
                                                              "kind": "critical (in the target's cone)" if version == "CRITICAL" else "placebo (circuit B)"},
                        "swap_to_target_distance": dist, "base_target_true": vals["T"], "circuit": circuit,
                        "filters": ["target_ff_depth = target_depth + 2 in every version",
                                    "at least one A input is sensitive for the target"],
                        "prompt_tokens": tokens.count(prompt), "tokenizer_proxy": tokens.PROXY_NAME,
                        "repeat_prompt": params["repeat_prompt"]},
                notes="All three versions are the identical labelled graph; only two adjacent vertices swap places "
                      "in the listing, so ground truth, chromatic number and every order-invariant member are unchanged.",
                cell_note=f"Depth {d} (first-fit depth {D}), version {version}, arm {arm}.",
            ))
    return items


def proxy_bits(task: ColouringTask, target: str, ref: str, D: int) -> dict[str, bool]:
    """The bit of every LOCAL-t-LIST proxy whose horizon stops short of the target (first-fit
    depth D): t < D with leftovers coloured 1, t < D - 1 with leftovers given their smallest
    free colour (that default reaches the target one round early). `enforced` says which of
    them the audit enforces."""
    out = {}
    for default, horizon in (("one", D), ("free", D - 1)):
        for t in range(1, horizon):
            col = run("coloring", "LOCAL-t", task, {"t": t, "ids": "LIST", "default": default}).answer
            out[f"LOCAL-{t}-LIST/{default}"] = col[target] == col[ref]
    return out


def enforced(proxy: str, D: int) -> bool:
    """LOCAL-(D-2)-LIST/free sees the target's already-coloured inputs: reported, not enforced."""
    return proxy != f"LOCAL-{D - 2}-LIST/free"


def generate(tier: str, seed: int, per_cell: int | None = None, **params) -> tuple[list, dict]:
    p = {**DEFAULTS, **params}
    per_cell = per_cell or TIERS[tier].default_per_cell
    if max(p["depths"]) > p["D_max"]:
        raise ValueError("every depth must be <= D_max")
    stats = GenStats()
    items: list = []
    audit: dict[str, Any] = {}
    attempt = 0
    for di, d in enumerate(p["depths"]):
        accepted, truths, proxy_hits = 0, [], {}
        while accepted < per_cell:
            want_true = (accepted + di) % 2 == 0  # alternate within a depth (and across depths for smoke)
            bseed = base_seed(tier, seed, attempt)
            attempt += 1
            stats.attempts += 1
            CC.guard(attempt, p, stats, f"E3 d={d}")
            rng = rng_for(bseed, f"C-E3-{d}")
            gadget = build_gadget(rng, p["width"], p["D_max"], d, p["cross_p"], p["n_triangles"])
            vals = nor_values(gadget, gadget["orient"])
            if vals["T"] != want_true:
                stats.reject("target value does not match the balancing target")
                continue
            triple = make_triple_or_none(gadget, rng, tier, bseed, accepted, p, stats)
            if triple is None:
                continue
            base_u = next(it for it in triple if it.params["version"] == "BASE" and it.params["arm"] == "U-LIST")
            bits = proxy_bits(load_task(base_u.instance), base_u.params["target"], base_u.params["reference_vertex"],
                              base_u.params["target_ff_depth"])
            for k, b in bits.items():
                proxy_hits[k] = proxy_hits.get(k, 0) + (b == vals["T"])
            truths.append(vals["T"])
            items += triple
            accepted += 1
            stats.accepted += 1
        N = len(truths)
        acc = {k: v / N for k, v in proxy_hits.items()}
        audit[f"d={d}"] = {"N": N, "target_ff_depth": d + 2, "P(target colour 1)": sum(truths) / N, "proxy_accuracy": acc,
                           "reported_not_enforced": [k for k in acc if not enforced(k, d + 2)]}
        if N >= 2:
            tol = 0.05 + 1 / N
            bad = {k: a for k, a in acc.items() if enforced(k, d + 2) and abs(a - 0.5) > tol}
            if abs(sum(truths) / N - 0.5) > tol or bad:
                raise RuntimeError(f"E3 d={d}: balance / proxy audit failed (tolerance {tol:.2f}): {bad}")
    out = stats.to_json()
    out["audit"] = audit
    return items, out


def make_triple_or_none(gadget, rng, tier, bseed, triple, p, stats):
    if not any(x.startswith("A") for x in gadget["inputs"]):
        return None
    vals = nor_values(gadget, gadget["orient"])
    sens = []
    for x in gadget["inputs"]:
        if x.startswith("A"):
            flipped = dict(gadget["orient"])
            flipped[x] = not flipped[x]
            if nor_values(gadget, flipped)["T"] != vals["T"]:
                sens.append(x)
    if not sens:
        stats.reject("no A input is sensitive for the target")
        return None
    items = make_triple(gadget, rng, tier, bseed, triple, p)
    if items is None:
        stats.reject("target's first-fit depth is not d + 2 in every version")
        return None
    problems = check_set(items)
    if problems:
        stats.reject("set invariant failed: " + problems[0][:60])
        return None
    return items


def check_set(items: list) -> list[str]:
    errs: list[str] = []
    by = {(it.params["version"], it.params["arm"]): it for it in items}
    if sorted(by) != sorted((v, a) for v in VERSIONS for a in ARMS):
        return ["set does not have every version x arm"]
    tasks = {k: load_task(it.instance) for k, it in by.items()}
    graphs = {k: t.graph for k, t in tasks.items()}
    edge_sets = {frozenset(frozenset(e) for e in g.edges) for g in graphs.values()}
    if len(edge_sets) != 1 or len({frozenset(g.vertices) for g in graphs.values()}) != 1:
        errs.append("versions are not the same labelled graph")
    base = list(graphs[("BASE", "U-LIST")].vertices)
    for v in ("CRITICAL", "PLACEBO"):
        other = list(graphs[(v, "U-LIST")].vertices)
        diff = [i for i in range(len(base)) if base[i] != other[i]]
        if len(diff) != 2 or diff[1] - diff[0] != 1:
            errs.append(f"{v} listing is not one adjacent swap of BASE")
    p0 = items[0].params
    target, ref = p0["target"], p0["reference_vertex"]
    circuit = p0["circuit"]
    bits = {}
    for v in VERSIONS:
        g = graphs[(v, "U-LIST")]
        if g.vertices[0] != ref:
            errs.append(f"{v}: the reference vertex is not listed first")
        pos = g.position
        vals = {x: pos[x] < pos[pnd] for x, pnd in circuit["input_pairs"]}
        for gate, a, b in circuit["gates"]:  # stored in topological order
            vals[gate] = not (vals[a] or vals[b])
        ff = by[(v, "U-LIST")].predictions["FF-LIST (C1 seq)"]["answer"]
        if isinstance(ff, str) or len(set(ff.values())) != 3:
            errs.append(f"{v}: FF-LIST does not 3-colour the gadget")
            continue
        if any((ff[x] == 1) != val for x, val in vals.items()):
            errs.append(f"{v}: gadget lemma fails (FF colour 1 iff NOR value True)")
        bits[v] = ff[target] == ff[ref]
        i_item = by[(v, "I")]
        errs += [f"{v} (I): {m}" for m in recheck_readouts(i_item.instance, i_item.ground_truth, i_item.params)]
        if (i_item.ground_truth["answer"] == 1) != vals[target]:
            errs.append(f"{v}: the instructed answer disagrees with the target's NOR value (colour 1 iff True)")
    if any(tasks[(v, "I")].target != target for v in VERSIONS):
        errs.append("an I-arm task does not carry the asked target")
    if len({by[(v, "I")].content_hash for v in VERSIONS}) != len(VERSIONS):
        errs.append("I-arm versions with different questions share a content hash")
    if any(ff_depth(graphs[(v, "U-LIST")], target) != p0["target_ff_depth"] for v in VERSIONS):
        errs.append("the target's first-fit depth differs from params.target_ff_depth")
    if bits and bits.get("BASE") == bits.get("CRITICAL"):
        errs.append("the critical swap does not flip the target under FF-LIST")
    if bits and bits.get("BASE") != bits.get("PLACEBO"):
        errs.append("the placebo swap flips the target")
    ds = {repr(by[(v, "U-LIST")].predictions["DSATUR (C2, label ties)"]["answer"]) for v in VERSIONS}
    if len(ds) != 1:
        errs.append("DSATUR with label ties differs across versions")
    if len({repr(it.ground_truth.get("colourable", it.ground_truth.get("chromatic_number"))) for it in items}) > 2:
        errs.append("ground truth differs across versions")
    for arm in ARMS:
        errs += surface.equal_token_multisets({v: by[(v, arm)].prompt for v in VERSIONS})
    return errs
