"""A/H E2: hardness-neutral cue moves (the cue moves; g and structural competitors fixed).

Design (A/H §2.6 E2, §2.8 E2). One set = one base and its padded variants:

- SAT: core n = 24, m = 101 (alpha = 4.21), rejection-sampled to the target g (alternating SAT
  and UNSAT bases). Levels:
    base  the core;
    K     +28 padding clauses (fresh literal, two core literals from distinct core variables,
          random signs) at 28 uniformly chosen slots of 129; fresh literals from 3 fresh pure
          variables (x25-x27, 8-10 occurrences each): alpha_U = 129/27 = 4.78;
    J     the same 28 clauses, the same core literals and slots, the same negated slots; fresh
          literals from 10 fresh pure variables (x25-x34, 2-3 occurrences each): alpha_U = 3.79;
    U     the core plus 8 declared but unused variables: alpha_U = 4.21, alpha_D = 3.16.
  Asserted: fresh variables are pure; the padded formula is satisfiable iff the core is;
  pure-literal elimination returns the core exactly (so cores with a pure literal are
  rejected); POLARITY gives the same assignment to the core variables at every level; K and J
  prompts differ only in fresh-variable names and the declaration line.
- COL: base n = 20, |E| = 44, k = 3, target colourability alternating; the base is connected
  (not in the doc; it keeps exact search on the padded graphs inside the base). K: + K_{3,3,3} on 9 new
  people (27 pairs). J: + a random 27-edge tree on 28 new people, people listed in BFS order.
  U: + 8 isolated people. New pairs sit at the same list slots in K and J; new people are
  inserted at the same anchors (K and U use a prefix of J's anchors and names). Asserted:
  colourability unchanged; FIRST-FIT and DSATUR colour the added component with <= 3
  colours in the presented order.
- ENT: matched conclusions. For a premise set (6-8 atoms, 4-6 premises: one categorical, the
  rest "either ... or"), 8 two-literal conclusions in a 2 (g) x 2 (FREQ hi: f(C) >= 3 / lo:
  f(C) <= 1; f = min over a conjunction's literals, max over a disjunction's) x 2 (ATMOSPHERE
  match / mismatch) design, matched within the tuple on: word count (range <= 2, i.e. +-1),
  atom overlap with the first, last and categorical premises (identical), UP depth for the
  entailed four (identical), counter-model fraction rho for the non-entailed four (range <= 1/16).

Readings of the doc (also in docs/GENERATORS.md):
- "14 of the 28 fresh literals are negated" cannot hold in K: 3 pure variables with 8-10
  occurrences each can negate 8-10 or 16-20 slots, never 14. K keeps 3 variables (the alpha_U
  the design is about) with occurrences (10, 9, 9) and one variable negated, so 10 of 28 slots
  are negated; J negates exactly the same 10 slots (4 negative variables of 3, 3, 2, 2
  occurrences and 6 positive variables of 3 each).
- The fresh literal's position inside a padding clause is random (the same in K and J), not
  always first, so position does not mark padding.
- ENT matching omits two of the doc's constraints: the perception-fragility kappa (+-0.05) and
  the PyETR counterbalancing across sets (PyETR's prediction is recorded on every item as the
  "B4 ETR" row, so it can be balanced at selection time later). Conclusions are two-literal
  only (so word counts can match); 50% of premise sets are flagged as the A2 calibration split.
- A2 thresholds are illustrative (DENSITY 4.26 / 4.69, LENGTH-M 115 clauses / 58 pairs, LENGTH-T
  the midpoint of the base and K prompts' proxy-token counts).
"""

from __future__ import annotations

import itertools
from collections import Counter

import networkx as nx
from typing import Any

import numpy as np

from reasoning_heuristics import tokens
from reasoning_heuristics.generators import ah_common as A
from reasoning_heuristics.generators.common import GenStats, make_item, set_hash
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.base import run
from reasoning_heuristics.heuristics.entailment import atmosphere_of, cat_lits, freq_score, is_categorical, mood_of
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, SatTask, load_task
from reasoning_heuristics.lexicon import DEVICES, PEOPLE, fixed_width_names
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.coloring.render import render_rooms
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.cnf import CNF
from reasoning_heuristics.problems.sat.render import render_textbook
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.truth import truth
from reasoning_heuristics.generators.ah_e1 import random_premises

VERTICAL, EVAL_ID = "A/H", "E2"
LEXICON_PARTITIONED = False
DOMAINS = ("SAT", "COL", "ENT")
LEVELS = ("base", "K", "J", "U")
ENT_CELLS = [f"{g}-{f}-{a}" for g in ("E", "N") for f in ("hi", "lo") for a in ("match", "mis")]


def cells(params: dict[str, Any]) -> list[str]:
    out = []
    for d in params.get("domains", DOMAINS):
        if d == "SAT":
            out += [f"SAT/{lv}/g={g}" for g in ("SAT", "UNSAT") for lv in LEVELS]
        elif d == "COL":
            out += [f"COL/{lv}/g={g}" for g in ("possible", "impossible") for lv in LEVELS]
        else:
            out += [f"ENT/{c}" for c in ENT_CELLS]
    return out


# --- SAT -------------------------------------------------------------------------------------


def pure_literal_elimination(clauses: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    clauses = list(clauses)
    while True:
        signs: dict[int, set[bool]] = {}
        for c in clauses:
            for l in c:
                signs.setdefault(abs(l), set()).add(l > 0)
        pure = {v for v, s in signs.items() if len(s) == 1}
        kept = [c for c in clauses if not any(abs(l) in pure for l in c)]
        if len(kept) == len(clauses):
            return kept
        clauses = kept


def sat_core(rng, n: int, m: int, want_sat: bool, tries: int = 500) -> CNF | None:
    names = tuple(fixed_width_names("x", n))
    for _ in range(tries):
        cnf = S.random_ksat(n, m, 3, rng, names)
        if len(cnf.used_vars()) != n or pure_literal_elimination(list(cnf.clauses)) != list(cnf.clauses):
            continue
        if (S.solve(cnf) is not None) == want_sat:
            return cnf
    return None


def _groups(rng, idx: list[int], sizes: list[int]) -> list[list[int]]:
    perm = [idx[i] for i in rng.permutation(len(idx))]
    out, pos = [], 0
    for s in sizes:
        out.append(sorted(perm[pos:pos + s]))
        pos += s
    assert pos == len(idx)
    return out


def sat_padding(rng, core: CNF, n_pad: int = 28):
    """Returns (K, J, design dict). Fresh variable names are assigned at random to occurrence groups."""
    n, m = core.n, core.m
    slots = sorted(int(s) for s in rng.choice(m + n_pad, size=n_pad, replace=False))
    pads = []
    for _ in range(n_pad):
        vs = rng.choice(n, size=2, replace=False) + 1
        signs = rng.integers(0, 2, size=2) * 2 - 1
        pads.append(([int(v * s) for v, s in zip(vs, signs)], int(rng.integers(3))))
    neg_pads = sorted(int(i) for i in rng.choice(n_pad, size=10, replace=False))
    pos_pads = [i for i in range(n_pad) if i not in neg_pads]
    k_groups = [(g, False) for g in _groups(rng, neg_pads, [10])] + [(g, True) for g in _groups(rng, pos_pads, [9, 9])]
    j_groups = [(g, False) for g in _groups(rng, neg_pads, [3, 3, 2, 2])] + [(g, True) for g in _groups(rng, pos_pads, [3] * 6)]

    def build(groups):
        names = list(core.var_names) + fixed_width_names("x", n + len(groups))[n:]
        fresh_of = {}
        order = rng.permutation(len(groups))
        for slot_name, gi in enumerate(order):
            members, positive = groups[gi]
            for p in members:
                fresh_of[p] = (n + 1 + slot_name) * (1 if positive else -1)
        clauses, it_core, pad_at = [], iter(core.clauses), {s: i for i, s in enumerate(slots)}
        for pos in range(m + n_pad):
            if pos in pad_at:
                i = pad_at[pos]
                core_lits, fpos = pads[i]
                lits = list(core_lits)
                lits.insert(fpos, fresh_of[i])
                clauses.append(tuple(lits))
            else:
                clauses.append(next(it_core))
        return CNF(tuple(names), tuple(clauses))

    K, J = build(k_groups), build(j_groups)
    return K, J, {"slots": slots, "negated_pads": neg_pads}


def core_polarity(task: SatTask, core_names) -> dict[str, bool]:
    ans = run("sat", "POLARITY", task).answer
    return {k: ans[k] for k in core_names}


def _sat_set(rng, made: int, bseed: int, tier: str, n: int, m: int, walk_runs: int):
    want_sat = made % 2 == 0
    core = sat_core(rng, n, m, want_sat)
    if core is None:
        return None, "no core with the target g"
    for _ in range(50):
        K, J, design = sat_padding(rng, core)
        pol = core_polarity(SatTask(core), core.var_names)
        if core_polarity(SatTask(K), core.var_names) == pol == core_polarity(SatTask(J), core.var_names):
            break
    else:
        return None, "padding changes POLARITY on the core"
    U = CNF(tuple(fixed_width_names("x", n + 8)), core.clauses)
    cnfs = {"base": core, "K": K, "J": J, "U": U}
    prompts = {lv: render_textbook(c) for lv, c in cnfs.items()}
    theta_t = (tokens.count(prompts["base"]) + tokens.count(prompts["K"])) // 2
    g = "SAT" if want_sat else "UNSAT"
    set_id = f"{set_hash(bseed, 'SAT')}-SAT-{g}"
    base_hash = sha(SatTask(core).content_key())
    items = []
    for lv in LEVELS:
        cnf = cnfs[lv]
        task = SatTask(cnf)
        tok = tokens.count(prompts[lv])
        specs = A.sat_members(115, walk_runs=walk_runs) + [
            ("A2 LENGTH-T", "LENGTH", {"variant": "T", "tokens": tok, "theta": theta_t}),
            ("D DPLL-b+PL", "SEARCH", {"b": 8, "order": "MENTION", "value": "TRUE", "default": "UNSAT", "pure": True}),
        ]
        n_used = len(cnf.used_vars())
        params = {"level": lv, "n_used": n_used, "n_decl": cnf.n, "m": cnf.m, "alpha_U": round(cnf.m / n_used, 3),
                  "alpha_D": round(cnf.m / cnf.n, 3), "prompt_tokens": tok, "tokenizer_proxy": tokens.PROXY_NAME,
                  "padding_slots": design["slots"] if lv in ("K", "J") else None,
                  "negated_padding": design["negated_pads"] if lv in ("K", "J") else None,
                  "fresh_occurrences": _fresh_occurrences(cnf, n) if lv in ("K", "J") else None,
                  "controlled": "core clauses and positions; padding core literals, slots and negated slots identical in K and J",
                  "varied": {"base": "none", "K": "+28 clauses on 3 fresh pure variables", "J": "+28 clauses on 10 fresh pure variables",
                             "U": "+8 declared, unused variables"}[lv]}
        items.append(make_item(vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=f"SAT/{lv}/g={g}", domain="SAT",
                               framing="CNF textbook", prompt=prompts[lv], answer_format=A.SAT_FORMAT, task=task,
                               ground_truth=truth(task), specs=specs, channel=A.SAT_CHANNEL, seed=bseed, tier=tier,
                               generator=__name__, base_hash=base_hash,
                               source_hash=None if lv == "base" else base_hash, pair_id=set_id, params=params,
                               notes="Satisfiability-neutral padding: every padded formula reduces to the core by pure-literal elimination.",
                               cell_note=f"Level {lv}; g = {g} at every level."))
    return items, None


def _fresh_occurrences(cnf: CNF, n_core: int) -> dict[str, int]:
    c = Counter(cnf.var_names[abs(l) - 1] for cl in cnf.clauses for l in cl if abs(l) > n_core)
    return dict(sorted(c.items()))


# --- COL -------------------------------------------------------------------------------------


def random_tree_bfs(rng, names: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """A random recursive tree on `names`; returns (names in BFS order, edges in BFS order)."""
    order = [names[i] for i in rng.permutation(len(names))]
    parent = {order[i]: order[int(rng.integers(i))] for i in range(1, len(order))}
    children: dict[str, list[str]] = {}
    for c, p in parent.items():
        children.setdefault(p, []).append(c)
    bfs, edges, queue = [order[0]], [], [order[0]]
    while queue:
        v = queue.pop(0)
        for c in children.get(v, []):
            bfs.append(c)
            edges.append((v, c))
            queue.append(c)
    return bfs, edges


def _col_set(rng, made: int, bseed: int, tier: str, n: int, m: int):
    want = made % 2 == 0
    pool = [PEOPLE[i] for i in rng.permutation(len(PEOPLE))]
    base_names, new = pool[:n], pool[n:n + 28]
    for _ in range(200):
        g = G.random_gnm(base_names, m, rng)
        # A connected base keeps DSATUR-ordered exact search inside the base when refuting.
        if nx.is_connected(g.nx()) and G.k_colourable_sat(g, 3) == want:
            break
    else:
        return None, "no base with the target colourability"
    base_edges = [g.edges[i] for i in rng.permutation(m)]
    base = Graph(tuple(base_names), tuple(base_edges))
    tree_names, tree_edges = random_tree_bfs(rng, new)
    anchors = sorted(int(a) for a in rng.integers(0, n + 1, size=28))
    k_names = tree_names[:9]
    parts = [k_names[0:3], k_names[3:6], k_names[6:9]]
    k_edges = [(u, v) for a, b in itertools.combinations(range(3), 2) for u in parts[a] for v in parts[b]]
    k_edges = [k_edges[i] for i in rng.permutation(len(k_edges))]
    slots = sorted(int(s) for s in rng.choice(m + 27, size=27, replace=False))

    def people(extra: list[str], used_anchors: list[int]) -> tuple[str, ...]:
        out, j = [], 0
        for pos in range(n + 1):
            while j < len(extra) and used_anchors[j] == pos:
                out.append(extra[j])
                j += 1
            if pos < n:
                out.append(base_names[pos])
        return tuple(out)

    def edges_with(new_edges: list[tuple[str, str]]) -> tuple:
        out, it_b, it_n = [], iter(base_edges), iter(new_edges)
        for pos in range(m + 27):
            out.append(next(it_n) if pos in slots else next(it_b))
        return tuple(out)

    graphs = {
        "base": base,
        "K": Graph(people(k_names, anchors[:9]), edges_with(k_edges)),
        "J": Graph(people(tree_names, anchors), edges_with(tree_edges)),
        "U": Graph(people(tree_names[:8], anchors[:8]), tuple(base_edges)),
    }
    for lv in ("K", "J"):
        added = set(graphs[lv].vertices) - set(base_names)
        for name, params in (("FF", {"order": "LIST"}), ("DSATUR", {})):
            col = run("coloring", name, ColouringTask(graphs[lv]), params).answer
            if len({col[v] for v in added}) > 3:
                return None, f"{name} uses more than 3 colours on the added component ({lv})"
    rule = "No two enemies may share a room."
    g_label = "possible" if want else "impossible"
    set_id = f"{set_hash(bseed, 'COL')}-COL-{g_label}"
    base_hash = sha(ColouringTask(base, 3).content_key())
    items = []
    for lv in LEVELS:
        gr = graphs[lv]
        task = ColouringTask(gr, 3)
        prompt = render_rooms(gr, 3, "enemies", rule)
        used = sum(1 for v in gr.vertices if gr.degree(v) > 0)
        params = {"level": lv, "n_decl": gr.n, "n_used": used, "m": gr.m, "mean_degree_U": round(2 * gr.m / used, 3),
                  "mean_degree_D": round(2 * gr.m / gr.n, 3), "new_pair_slots": slots if lv in ("K", "J") else None,
                  "insert_anchors": {"K": anchors[:9], "J": anchors, "U": anchors[:8]}.get(lv),
                  "prompt_tokens": tokens.count(prompt), "tokenizer_proxy": tokens.PROXY_NAME,
                  "varied": {"base": "none", "K": "+K_{3,3,3} on 9 new people", "J": "+a 27-edge tree on 28 new people (BFS order)",
                             "U": "+8 isolated people"}[lv]}
        items.append(make_item(vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=f"COL/{lv}/g={g_label}", domain="COL",
                               framing="rooms (themed)", prompt=prompt, answer_format=A.COL_FORMAT, task=task,
                               ground_truth=truth(task), specs=A.col_members(3, 58), channel=A.COL_CHANNEL, seed=bseed,
                               tier=tier, generator=__name__, base_hash=base_hash,
                               source_hash=None if lv == "base" else base_hash, pair_id=set_id, params=params,
                               notes="Colourability-neutral padding with a disconnected, 3-colourable component.",
                               cell_note=f"Level {lv}; colourability {g_label} at every level."))
    return items, None


# --- ENT -------------------------------------------------------------------------------------


def up_depth_any(premises: tuple, c, max_k: int = 8) -> int | None:
    """Rounds of unit propagation (beyond the stated facts) after which C holds on the known literals."""
    from reasoning_heuristics.heuristics.entailment import holds_in_state

    clauses = [cl for p in premises for cl in F.clauses_of(p)]
    known: dict[str, bool] = {}
    for cl in clauses:
        if len(cl) == 1:
            (a, s), = cl
            known[a] = s
    for k in range(max_k + 1):
        if holds_in_state(c, frozenset(known.items())):
            return k
        new = {}
        for cl in clauses:
            if any(known.get(a) == s for a, s in cl):
                continue
            open_l = [(a, s) for a, s in cl if a not in known]
            if len(open_l) == 1:
                new[open_l[0][0]] = open_l[0][1]
        if not new:
            return None
        known.update(new)
    return None


def _overlap(c, p) -> int:
    return len({a for a, _ in F.literals(c)} & set(F.atoms(p)))


def _ent_set(rng, made: int, bseed: int, tier: str, atom_range: tuple[int, int], prem_range: tuple[int, int],
             tries: int, etr_max_atoms: int):
    devices = list(DEVICES)
    for _ in range(tries):
        n_atoms = int(rng.integers(atom_range[0], atom_range[1] + 1))
        atoms = [f"{d}:{DEVICES[d]}" for d in (devices[i] for i in rng.choice(len(devices), size=n_atoms, replace=False))]
        prem = random_premises(rng, atoms, int(rng.integers(prem_range[0], prem_range[1] + 1)))
        used = F.atoms_of(prem)
        ms = F.models(list(prem), used)
        if not ms:
            continue
        cat = next(p for p in prem if is_categorical(p))
        base_task = EntailmentTask(prem, F.lit(used[0]), "YN")
        atm = atmosphere_of(base_task)
        cands = []
        for a, b in itertools.combinations(used, 2):
            for sa, sb in itertools.product((True, False), repeat=2):
                for op in ("and", "or"):
                    c = (op, (F.lit(a, sa), F.lit(b, sb)))
                    if any(F.canonical(c) == F.canonical(p) for p in prem):
                        continue
                    f = freq_score(base_task, c)
                    fcell = "hi" if f >= 3 else ("lo" if f <= 1 else None)
                    if fcell is None:
                        continue
                    follows = all(F.evaluate(c, w) for w in ms)
                    cands.append({
                        "c": c, "g": "E" if follows else "N", "f": fcell, "atm": "match" if mood_of(c) == atm else "mis",
                        "words": len(F.render(c, False).split()),
                        "overlap": (_overlap(c, prem[0]), _overlap(c, prem[-1]), _overlap(c, cat)),
                        "depth": up_depth_any(prem, c) if follows else None,
                        "rho": None if follows else sum(1 for w in ms if not F.evaluate(c, w)) / len(ms),
                    })
        tuple_ = _match_tuple(cands, rng)
        if tuple_ is None:
            continue
        return prem, tuple_, atoms, atm
    return None


def _match_tuple(cands: list[dict], rng) -> dict[str, dict] | None:
    by_sig: dict[tuple, list[dict]] = {}
    for c in cands:
        by_sig.setdefault(c["overlap"], []).append(c)
    sigs = list(by_sig)
    for si in rng.permutation(len(sigs)):
        group = by_sig[sigs[si]]
        cell = {name: [c for c in group if f"{c['g']}-{c['f']}-{c['atm']}" == name] for name in ENT_CELLS}
        if any(not v for v in cell.values()):
            continue
        for w0 in sorted({c["words"] for c in group}):
            band = {name: [c for c in v if w0 <= c["words"] <= w0 + 2] for name, v in cell.items()}
            if any(not v for v in band.values()):
                continue
            ent = [band[n] for n in ENT_CELLS[:4]]
            depths = set.intersection(*[{repr(c["depth"]) for c in v} for v in ent])
            if not depths:
                continue
            d = sorted(depths)[0]
            chosen = {n: next(c for c in band[n] if repr(c["depth"]) == d) for n in ENT_CELLS[:4]}
            non = [band[n] for n in ENT_CELLS[4:]]
            # Among rho-matched combinations prefer the lowest mean rho: conclusions with rare
            # counter-models are more informative than ones the premises flatly contradict.
            best = None
            for combo in itertools.islice(itertools.product(*non), 20000):
                rhos = [c["rho"] for c in combo]
                if max(rhos) - min(rhos) <= 1 / 16 + 1e-12 and (best is None or sum(rhos) < best[0]):
                    best = (sum(rhos), combo)
            if best is not None:
                chosen.update(dict(zip(ENT_CELLS[4:], best[1])))
                return chosen
    return None


def _ent_items(rng, made, bseed, tier, atom_range, prem_range, tries, etr_max_atoms):
    found = _ent_set(rng, made, bseed, tier, atom_range, prem_range, tries, etr_max_atoms)
    if found is None:
        return None, "no premise set with a matched 8-tuple"
    prem, chosen, atoms, atm = found
    set_id = f"{set_hash(bseed, 'ENT')}-ENT"
    base_hash = sha({"premises": sorted((F.canonical(p) for p in prem), key=repr)})
    items = []
    with_etr = len(F.atoms_of(prem)) <= etr_max_atoms
    for name in ENT_CELLS:
        c = chosen[name]
        task = EntailmentTask(prem, c["c"], "YN")
        prompt = A.render_machine_facts(task)
        params = {"g_cell": c["g"], "freq_cell": c["f"], "atmosphere_match": c["atm"] == "match",
                  "freq_stat": freq_score(task, c["c"]), "atmosphere": list(atm), "mood": list(mood_of(c["c"])),
                  "words": c["words"], "overlap_first_last_categorical": list(c["overlap"]),
                  "up_depth": c["depth"], "rho": c["rho"], "atoms_drawn": len(atoms), "premises": len(prem),
                  "calibration_split": made % 2 == 1, "prompt_tokens": tokens.count(prompt),
                  "matched": "words (range <= 2), overlap with first/last/categorical premise, UP depth (entailed), rho within 1/16 (non-entailed)",
                  "not_matched": "perception fragility kappa; PyETR counterbalancing"}
        items.append(make_item(vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=f"ENT/{name}", domain="ENT",
                               framing="machine facts", prompt=prompt, answer_format=A.ENT_YN_FORMAT, task=task,
                               ground_truth=truth(task), specs=A.ent_members(with_etr), channel=A.ENT_CHANNEL,
                               seed=bseed, tier=tier, generator=__name__, base_hash=base_hash, source_hash=None,
                               pair_id=set_id, params=params,
                               notes="Matched conclusions: the cues (FREQ, ATMOSPHERE) vary within one premise set.",
                               cell_note=f"Cell {name}."))
    return items, None


# --- generation ------------------------------------------------------------------------------


def generate(tier: str, seed: int, per_cell: int | None = None, domains: list[str] | None = None,
             sat_n: int = 24, sat_m: int = 101, col_n: int = 20, col_m: int = 44, ent_atoms: list[int] = (6, 8),
             ent_premises: list[int] = (4, 6), ent_tries: int = 400, etr_max_atoms: int = 8,
             walk_runs: int = 30, max_attempts: int = 300) -> tuple[list, dict]:
    """per_cell counts items per cell: SAT and COL cells are split by g, so each g level gets
    per_cell bases; ENT gets per_cell premise sets."""
    per_cell = per_cell or TIERS[tier].default_per_cell
    stats = GenStats()
    items: list = []
    attempt = 0
    for domain in (domains or DOMAINS):
        target = 2 * per_cell if domain in ("SAT", "COL") else per_cell
        made = tried = 0
        while made < target:
            tried += 1
            if tried > max_attempts:
                raise RuntimeError(f"A/H E2 {domain}: {made}/{target} sets after {max_attempts} attempts; stats {stats.to_json()}")
            bseed = base_seed(tier, seed, attempt)
            attempt += 1
            stats.attempts += 1
            rng = rng_for(bseed, f"AH-E2-{domain}")
            if domain == "SAT":
                set_items, why = _sat_set(rng, made, bseed, tier, sat_n, sat_m, walk_runs)
            elif domain == "COL":
                set_items, why = _col_set(rng, made, bseed, tier, col_n, col_m)
            else:
                set_items, why = _ent_items(rng, made, bseed, tier, tuple(ent_atoms), tuple(ent_premises), ent_tries, etr_max_atoms)
            if set_items is None:
                stats.reject(f"{domain}: {why}")
                continue
            problems = check_set(set_items) + [f"{it.cell} does not discriminate" for it in set_items if not A.discriminates(it)]
            if problems:
                stats.reject(f"{domain}: {problems[0][:70]}")
                continue
            items += set_items
            made += 1
            stats.accepted += 1
    return items, stats.to_json()


# --- set invariants ----------------------------------------------------------------------------


def check_set(items: list) -> list[str]:
    errs: list[str] = []
    domain = items[0].domain
    if domain == "SAT":
        by = {it.params["level"]: it for it in items}
        if set(by) != set(LEVELS):
            return [f"levels present: {sorted(by)}"]
        tasks = {lv: load_task(by[lv].instance) for lv in LEVELS}
        core = tasks["base"].cnf
        gs = {lv: by[lv].ground_truth["satisfiable"] for lv in LEVELS}
        if len(set(gs.values())) != 1:
            errs.append(f"g differs across levels: {gs}")
        n = core.n
        for lv in ("K", "J"):
            cnf = tasks[lv].cnf
            signs: dict[int, set[bool]] = {}
            for c in cnf.clauses:
                for l in c:
                    signs.setdefault(abs(l), set()).add(l > 0)
            if any(len(signs[v]) != 1 for v in range(n + 1, cnf.n + 1)):
                errs.append(f"{lv}: a fresh variable is not pure")
            if sorted(pure_literal_elimination(list(cnf.clauses))) != sorted(core.clauses):
                errs.append(f"{lv}: pure-literal elimination does not return the core")
            occ = by[lv].params["fresh_occurrences"]
            lo, hi = (8, 10) if lv == "K" else (2, 3)
            if any(not lo <= v <= hi for v in occ.values()):
                errs.append(f"{lv}: fresh occurrence counts {occ} outside [{lo}, {hi}]")
        K, J = tasks["K"].cnf, tasks["J"].cnf
        for ck, cj in zip(K.clauses, J.clauses):
            core_k = [l for l in ck if abs(l) <= n]
            core_j = [l for l in cj if abs(l) <= n]
            if core_k != core_j or [i for i, l in enumerate(ck) if abs(l) > n] != [i for i, l in enumerate(cj) if abs(l) > n]:
                errs.append("K and J differ outside the fresh-variable names")
                break
            if [l < 0 for l in ck] != [l < 0 for l in cj]:
                errs.append("K and J negate different slots")
                break
        if tasks["U"].cnf.clauses != core.clauses:
            errs.append("U changes the clauses")
        strip = {lv: "\n".join(l for l in by[lv].prompt.splitlines() if not l.startswith("Variables:")) for lv in ("K", "J")}
        if tokens.count(strip["K"]) != tokens.count(strip["J"]):
            errs.append("K and J prompts differ beyond names and the declaration line")
        pol = {lv: {k: v for k, v in by[lv].predictions["C0 POLARITY"]["answer"].items() if k in core.var_names} for lv in LEVELS}
        if any(pol[lv] != pol["base"] for lv in LEVELS):
            errs.append("POLARITY's core assignment changes across levels")
    elif domain == "COL":
        by = {it.params["level"]: it for it in items}
        if set(by) != set(LEVELS):
            return [f"levels present: {sorted(by)}"]
        tasks = {lv: load_task(by[lv].instance) for lv in LEVELS}
        base = tasks["base"].graph
        gs = {lv: by[lv].ground_truth["colourable"] for lv in LEVELS}
        if len(set(gs.values())) != 1:
            errs.append(f"colourability differs across levels: {gs}")
        base_edges = set(base.edges)
        for lv in ("K", "J", "U"):
            gr = tasks[lv].graph
            if [e for e in gr.edges if e in base_edges] != list(base.edges):
                errs.append(f"{lv}: base pairs not kept in order")
            if [v for v in gr.vertices if v in set(base.vertices)] != list(base.vertices):
                errs.append(f"{lv}: base people not kept in order")
        for lv in ("K", "J"):
            gr = tasks[lv].graph
            added = set(gr.vertices) - set(base.vertices)
            for name, params in (("FF", {"order": "LIST"}), ("DSATUR", {})):
                col = run("coloring", name, ColouringTask(gr), params).answer
                if len({col[v] for v in added}) > 3:
                    errs.append(f"{lv}: {name} uses more than 3 colours on the added component")
        sk = [i for i, e in enumerate(tasks["K"].graph.edges) if e not in base_edges]
        sj = [i for i, e in enumerate(tasks["J"].graph.edges) if e not in base_edges]
        if sk != sj or len(sk) != 27:
            errs.append("new pairs are not at the same 27 slots in K and J")
    else:
        if len(items) != 8:
            return [f"expected 8 matched conclusions, got {len(items)}"]
        tasks = [load_task(it.instance) for it in items]
        if len({repr(t.premises) for t in tasks}) != 1:
            errs.append("conclusions do not share one premise set")
        for it in items:
            want = it.params["g_cell"] == "E"
            if it.ground_truth["follows"] != want:
                errs.append(f"{it.cell}: g mismatch")
        words = [it.params["words"] for it in items]
        if max(words) - min(words) > 2:
            errs.append("conclusion word counts not within +-1")
        if len({tuple(it.params["overlap_first_last_categorical"]) for it in items}) != 1:
            errs.append("premise overlaps differ")
        ent = [it for it in items if it.params["g_cell"] == "E"]
        if len({repr(it.params["up_depth"]) for it in ent}) != 1:
            errs.append("UP depths differ among entailed conclusions")
        rhos = [it.params["rho"] for it in items if it.params["g_cell"] == "N"]
        if max(rhos) - min(rhos) > 1 / 16 + 1e-12:
            errs.append("rho differs by more than 1/16 among non-entailed conclusions")
        for it in items:
            t = load_task(it.instance)
            if (freq_score(t, t.probe) >= 3) != (it.params["freq_cell"] == "hi"):
                errs.append(f"{it.cell}: FREQ cell wrong")
    return errs
