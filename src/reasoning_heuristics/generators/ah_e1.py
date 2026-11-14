"""A/H E1: structure-blindness minimal pairs (g flips; every cue in an invariance class fixed).

Each set is one pair (x, x') -- cells ".../x" and ".../x-prime" -- built by an edit from an invariance group (A/H §2.3 P1, §2.6 E1,
§2.8 E1), so every function of the preserved statistics is equal on the pair:

- SAT (n in {16, 24, 36}, alpha in {4.0, 4.26, 4.5}; cycled across pairs): choose a variable v
  positive in clause i and negative in clause j with neg(j) = neg(i) + 1, and flip both
  occurrences. Preserved: n, m, alpha, per-variable polarity counts (so POLARITY, FREQ, MOMS,
  PURE-LITERAL), the clause negation-count multiset, positions, and the proxy-token multiset.
  Critical pairs: g(x) = SAT, g(x') = UNSAT. Null pairs: the same kind of edit with g fixed,
  alternating SAT->SAT and UNSAT->UNSAT across pairs. CNF and menu framings alternate between
  bases (a between-base factor, balanced against the null pairs' SAT/UNSAT alternation). B1 stratum: 2 unit clauses ("facts") and 15% binary
  clauses, where UP-3 refutes x' (and x is SAT).
- COL (n in {15, 20, 30}, k = 3, mean degree U[4.2, 4.6]): a double-edge swap
  (a,b),(c,d) -> (a,d),(c,b) made in place in the pair list. Preserved: every person's degree,
  |E|, the people-list order (so FIRST-FIT order), mention counts, tokens. Critical: G
  3-colourable, G' not; null: colourability unchanged. The tercile of the first edited pair's
  list position is cycled across pairs, crossed with size.
- ENT (atoms in {6, 8, 10}; 4-7 premises: one categorical conjunction of 1-2 literals at a
  random position, the rest "either ... or" with 2-3 disjuncts of 1-2 literals; a literal
  conclusion C that is not a stated fact): a negation moves between two occurrences of an
  atom v not in C, in two premises with neg(j) = neg(i) + 1. Critical: P |= C, P' |/= C; null:
  entailment unchanged. C's propagation depth in P (UP rounds beyond the facts: 1, 2, >=3, or
  none) is targeted round-robin and recorded with rho' (the counter-model fraction in P').

At most one pair per base. Every member in A/H §1.5's table that the zoo implements is run on
both members of every pair; the pair is rejected unless every A1/A2 cue and C0 POLARITY give
identical predictions on x and x' (recipe step 5).

Readings of the doc (also in docs/GENERATORS.md):
- The ENT depth strata are targets, not hard cells: a target stratum is tried for up to
  `stratum_tries` premise sets, then any stratum is accepted and the achieved stratum is
  recorded in params (the summary reports the distribution).
- SAT swaps are restricted to clauses of equal width (in pure 3-SAT this is automatic; in the
  B1 stratum it keeps the all-true / all-false validity unchanged, as the doc intends).
- A2 thresholds are illustrative: DENSITY theta = 4.26 (SAT) / 4.69 (COL mean degree), LENGTH
  theta = 100 clauses / 2.3n pairs; the study fits them per model on the E3 sweep.
- ETR (PyETR) is run on ENT items with at most `etr_max_atoms` atoms used (default 8); larger
  items record no ETR row (PyETR's update is exponential in the disjunctions).
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from reasoning_heuristics import tokens
from reasoning_heuristics.counterfactual import surface
from reasoning_heuristics.generators import ah_common as A
from reasoning_heuristics.generators.common import GenStats, make_item, set_hash
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.entailment import _flip_nth, is_categorical
from reasoning_heuristics.heuristics.sat import unit_propagate
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, SatTask, load_task
from reasoning_heuristics.lexicon import DEVICES, PEOPLE, fixed_width_names
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.coloring.render import render_rooms
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.cnf import CNF
from reasoning_heuristics.problems.sat.render import render_menu, render_textbook
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.truth import truth

VERTICAL, EVAL_ID = "A/H", "E1"
LEXICON_PARTITIONED = False
DOMAINS = ("SAT", "COL", "ENT")
CUE_LABELS = {
    "SAT": ["A1 ALWAYS-SAT", "A1 ALWAYS-UNSAT", "A2 DENSITY-U", "A2 DENSITY-D", "A2 LENGTH-M", "C0 POLARITY"],
    "COL": ["A1 ALWAYS-POSSIBLE", "A1 ALWAYS-IMPOSSIBLE", "A2 DENSITY-U", "A2 DENSITY-D", "A2 LENGTH-M"],
    "ENT": ["A1 ALWAYS-YES", "A1 NONE", "A2 FREQ", "A2 ATMOSPHERE", "A2 PRIMACY", "A2 RECENCY", "A2 DENSITY"],
}
DEPTH_STRATA = ("1", "2", ">=3", "none")


def _kinds(domain: str, params: dict[str, Any]) -> list[str]:
    if domain == "SAT":
        return ["critical", "null"] + (["B1"] if params.get("b1_stratum", True) else [])
    return ["critical", "null"]


def cells(params: dict[str, Any]) -> list[str]:
    out = []
    for d in params.get("domains", DOMAINS):
        for kind in _kinds(d, params):
            out += [f"{d}/{kind}/x", f"{d}/{kind}/x-prime"]
    return out


# --- SAT -------------------------------------------------------------------------------------


def neg_count(c: tuple[int, ...]) -> int:
    return sum(1 for l in c if l < 0)


def sat_swaps(cnf: CNF) -> list[tuple[int, int, int]]:
    """(v, i, j): v positive in clause i, negative in clause j, |C_i| = |C_j|, neg(j) = neg(i) + 1."""
    out = []
    for v in range(1, cnf.n + 1):
        pos = [i for i, c in enumerate(cnf.clauses) if v in c]
        neg = [j for j, c in enumerate(cnf.clauses) if -v in c]
        for i in pos:
            for j in neg:
                if i != j and len(cnf.clauses[i]) == len(cnf.clauses[j]) and neg_count(cnf.clauses[j]) == neg_count(cnf.clauses[i]) + 1:
                    out.append((v, i, j))
    return out


def apply_swap(cnf: CNF, v: int, i: int, j: int) -> CNF:
    clauses = list(cnf.clauses)
    clauses[i] = tuple(-v if l == v else l for l in clauses[i])
    clauses[j] = tuple(v if l == -v else l for l in clauses[j])
    return cnf.with_clauses(clauses)


def b1_formula(n: int, m: int, rng: np.random.Generator, names: tuple[str, ...]) -> CNF:
    """2 unit clauses, round(0.15 m) binary clauses, the rest ternary, at random positions."""
    n_bin = round(0.15 * m)
    widths = [1, 1] + [2] * n_bin + [3] * (m - 2 - n_bin)
    widths = [widths[i] for i in rng.permutation(len(widths))]
    clauses = []
    for w in widths:
        vs = rng.choice(n, size=w, replace=False) + 1
        signs = rng.integers(0, 2, size=w) * 2 - 1
        clauses.append(tuple(int(a * s) for a, s in zip(vs, signs)))
    return CNF(names, tuple(clauses))


def sat_pair(rng: np.random.Generator, kind: str, n: int, alpha: float, want_sat_base: bool, max_bases: int = 400):
    names = tuple(fixed_width_names("x", n))
    m = round(alpha * n)
    for _ in range(max_bases):
        cnf = b1_formula(n, m, rng, names) if kind == "B1" else S.random_ksat(n, m, 3, rng, names)
        g = S.solve(cnf) is not None
        if kind in ("critical", "B1") and not g:
            continue
        if kind == "null" and g != want_sat_base:
            continue
        swaps = sat_swaps(cnf)
        for idx in rng.permutation(len(swaps)):
            v, i, j = swaps[idx]
            x2 = apply_swap(cnf, v, i, j)
            g2 = S.solve(x2) is not None
            if kind == "null" and g2 == g:
                return cnf, x2, (v, i, j)
            if kind == "critical" and not g2:
                return cnf, x2, (v, i, j)
            if kind == "B1" and not g2 and unit_propagate(x2, {}, 3)[1] and not unit_propagate(cnf, {}, 3)[1]:
                return cnf, x2, (v, i, j)
    return None


def sat_params(cnf: CNF, framing: str) -> dict[str, Any]:
    n_used = len(cnf.used_vars())
    out = {"n_decl": cnf.n, "n_used": n_used, "m": cnf.m, "alpha_U": round(cnf.m / n_used, 3),
           "alpha_D": round(cnf.m / cnf.n, 3), "framing": framing,
           "polarity_counts": {cnf.var_names[v - 1]: [sum(1 for c in cnf.clauses if v in c), sum(1 for c in cnf.clauses if -v in c)]
                               for v in range(1, cnf.n + 1)},
           "clause_negation_multiset": sorted(Counter((len(c), neg_count(c)) for c in cnf.clauses).items())}
    if cnf.n <= 24:
        out["n_solutions"] = S.count_solutions(cnf, limit=100_000)
    return out


# --- COL -------------------------------------------------------------------------------------


def col_base(rng: np.random.Generator, n: int) -> Graph:
    names = [PEOPLE[i] for i in sorted(rng.choice(len(PEOPLE), size=n, replace=False))]
    names = [names[i] for i in rng.permutation(n)]  # random list order
    deg = rng.uniform(4.2, 4.6)
    g = G.random_gnm(names, round(deg * n / 2), rng)
    edges = [g.edges[i] for i in rng.permutation(g.m)]
    edges = [(u, v) if rng.random() < 0.5 else (v, u) for u, v in edges]
    return Graph(tuple(names), tuple(edges))


def double_edge_swap(g: Graph, p: int, q: int) -> Graph | None:
    (a, b), (c, d) = g.edges[p], g.edges[q]
    if len({a, b, c, d}) < 4 or g.has_edge(a, d) or g.has_edge(c, b):
        return None
    edges = list(g.edges)
    edges[p], edges[q] = (a, d), (c, b)
    return Graph(g.vertices, tuple(edges))


def col_pair(rng: np.random.Generator, kind: str, n: int, tercile: int, want_colourable: bool,
             max_bases: int = 200, swaps_per_base: int = 300):
    for _ in range(max_bases):
        g = col_base(rng, n)
        col = G.k_colour(g, 3) is not None
        if kind == "critical" and not col:
            continue
        if kind == "null" and col != want_colourable:
            continue
        third = g.m // 3
        lo, hi = tercile * third, (g.m if tercile == 2 else (tercile + 1) * third)
        for _ in range(swaps_per_base):
            p = int(rng.integers(lo, hi))
            q = int(rng.integers(g.m))
            if p == q:
                continue
            g2 = double_edge_swap(g, p, q)
            if g2 is None:
                continue
            col2 = G.k_colour(g2, 3) is not None
            if (kind == "critical" and not col2) or (kind == "null" and col2 == col):
                return g, g2, (p, q)
    return None


# --- ENT -------------------------------------------------------------------------------------


def random_premises(rng: np.random.Generator, atoms: list[str], n_prem: int) -> tuple:
    cat_pos = int(rng.integers(n_prem))
    prem = []
    for i in range(n_prem):
        if i == cat_pos:
            k = int(rng.integers(1, 3))
            chosen = rng.choice(len(atoms), size=k, replace=False)
            prem.append(F.conj(*[F.lit(atoms[a], bool(rng.integers(2))) for a in chosen]))
            continue
        nd = int(rng.integers(2, 4))
        sizes = [int(rng.integers(1, 3)) for _ in range(nd)]
        chosen = list(rng.choice(len(atoms), size=sum(sizes), replace=False)) if sum(sizes) <= len(atoms) else None
        if chosen is None:
            sizes = [1] * nd
            chosen = list(rng.choice(len(atoms), size=nd, replace=False))
        ds, pos = [], 0
        for s in sizes:
            ds.append(F.conj(*[F.lit(atoms[a], bool(rng.integers(2))) for a in chosen[pos:pos + s]]))
            pos += s
        prem.append(F.disj(*ds))
    return tuple(prem)


def premise_neg(p) -> int:
    return sum(1 for _, s in F.literals(p) if not s)


def ent_edits(premises: tuple) -> list[tuple[str, int, int, int, int]]:
    """(v, i, li, j, lj): v positive at literal li of premise i, negative at literal lj of premise j,
    neg(P_j) = neg(P_i) + 1."""
    occ: dict[str, list[tuple[int, int, bool]]] = {}
    for i, p in enumerate(premises):
        for li, (a, s) in enumerate(F.literals(p)):
            occ.setdefault(a, []).append((i, li, s))
    out = []
    for v, os_ in occ.items():
        for i, li, si in os_:
            for j, lj, sj in os_:
                if si and not sj and i != j and premise_neg(premises[j]) == premise_neg(premises[i]) + 1:
                    out.append((v, i, li, j, lj))
    return out


def apply_ent_edit(premises: tuple, i: int, li: int, j: int, lj: int) -> tuple:
    prem = list(premises)
    prem[i] = _flip_nth(prem[i], li)
    prem[j] = _flip_nth(prem[j], lj)
    return tuple(prem)


def depth_stratum(d: int | None) -> str:
    if d is None:
        return "none"
    return ">=3" if d >= 3 else str(d)


def ent_pair(rng: np.random.Generator, kind: str, n_atoms: int, target: str | None, want_follows: bool,
             tries: int):
    devices = list(DEVICES)
    for _ in range(tries):
        atoms = [f"{d}:{DEVICES[d]}" for d in (devices[i] for i in rng.choice(len(devices), size=n_atoms, replace=False))]
        prem = random_premises(rng, atoms, int(rng.integers(4, 8)))
        used = F.atoms_of(prem)
        ms = F.models(list(prem), used)
        if not ms:
            continue
        facts = {l for p in prem if is_categorical(p) for l in F.literals(p)}
        concl = [(a, s) for a in used for s in (True, False) if (a, s) not in facts]
        follows = {c: all(w[c[0]] == c[1] for w in ms) for c in concl}
        edits = ent_edits(prem)
        order = rng.permutation(len(edits))
        for e in order:
            v, i, li, j, lj = edits[e]
            p2 = apply_ent_edit(prem, i, li, j, lj)
            ms2 = F.models(list(p2), used)
            if not ms2:
                continue
            cands = []
            for c in concl:
                if c[0] == v:
                    continue
                f2 = all(w[c[0]] == c[1] for w in ms2)
                if kind == "critical" and follows[c] and not f2:
                    cands.append(c)
                if kind == "null" and follows[c] == f2 == want_follows:
                    cands.append(c)
            if not cands:
                continue
            if kind == "critical" and target is not None:
                hits = [c for c in cands if depth_stratum(A.up_depth(EntailmentTask(prem, F.lit(*c), "YN"))) == target]
                if not hits:
                    continue
                cands = hits
            c = cands[int(rng.integers(len(cands)))]
            return prem, p2, F.lit(*c), (v, i, li, j, lj), atoms
    return None


# --- generation ------------------------------------------------------------------------------


def generate(tier: str, seed: int, per_cell: int | None = None, domains: list[str] | None = None,
             sat_sizes: list[int] = (16, 24, 36), sat_alphas: list[float] = (4.0, 4.26, 4.5),
             col_sizes: list[int] = (15, 20, 30), ent_atoms: list[int] = (6, 8, 10), b1_stratum: bool = True,
             b1_n: int = 16, b1_alpha: float = 3.6, stratum_tries: int = 60, etr_max_atoms: int = 8,
             walk_runs: int = 30, max_attempts: int = 300) -> tuple[list, dict]:
    per_cell = per_cell or TIERS[tier].default_per_cell
    params = {"b1_stratum": b1_stratum}
    stats = GenStats()
    items: list = []
    attempt = 0
    for domain in (domains or DOMAINS):
        for kind in _kinds(domain, params):
            made = tried = 0
            while made < per_cell:
                tried += 1
                if tried > max_attempts:
                    raise RuntimeError(f"A/H E1 {domain}/{kind}: {made}/{per_cell} pairs after {max_attempts} attempts; stats {stats.to_json()}")
                bseed = base_seed(tier, seed, attempt)
                attempt += 1
                stats.attempts += 1
                rng = rng_for(bseed, f"AH-E1-{domain}-{kind}")
                if domain == "SAT":
                    pair_items = _sat_items(rng, kind, made, bseed, tier, sat_sizes, sat_alphas, b1_n, b1_alpha, walk_runs)
                elif domain == "COL":
                    pair_items = _col_items(rng, kind, made, bseed, tier, col_sizes)
                else:
                    pair_items = _ent_items(rng, kind, made, bseed, tier, ent_atoms, stratum_tries, etr_max_atoms)
                if pair_items is None:
                    stats.reject(f"{domain}/{kind}: no pair found from this seed")
                    continue
                problems = check_set(pair_items) + [f"{it.cell} does not discriminate" for it in pair_items if not A.discriminates(it)]
                if problems:
                    stats.reject(f"{domain}/{kind}: " + problems[0][:70])
                    continue
                items += pair_items
                made += 1
                stats.accepted += 1
    return items, stats.to_json()


def _pair_items(*, domain: str, kind: str, tasks: tuple, prompts: tuple, framing: str, specs, channel,
                answer_format: str, bseed: int, tier: str, params: tuple[dict, dict], notes: str) -> list:
    set_id = f"{set_hash(bseed, domain, kind)}-{domain}-{kind}"
    base_hash = sha(tasks[0].content_key())
    out = []
    for member, task, prompt, extra in zip(("x", "x-prime"), tasks, prompts, params):
        gt = truth(task)
        it = make_item(vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=f"{domain}/{kind}/{member}", domain=domain,
                       framing=framing, prompt=prompt, answer_format=answer_format, task=task, ground_truth=gt,
                       specs=specs, channel=channel, seed=bseed, tier=tier, generator=__name__, base_hash=base_hash,
                       source_hash=None if member == "x" else out[0].content_hash, pair_id=set_id,
                       params={**extra, "pair_kind": kind, "member": member, "prompt_tokens": tokens.count(prompt),
                               "tokenizer_proxy": tokens.PROXY_NAME},
                       notes=notes, cell_note=f"Pair kind {kind}; this member's ground truth: {gt}.")
        out.append(it)
    return out


def _sat_items(rng, kind, made, bseed, tier, sizes, alphas, b1_n, b1_alpha, walk_runs):
    if kind == "B1":
        n, alpha = b1_n, b1_alpha
    else:
        n, alpha = sizes[made % len(sizes)], alphas[(made // len(sizes)) % len(alphas)]
    found = sat_pair(rng, kind, n, alpha, want_sat_base=(made % 2 == 0))
    if found is None:
        return None
    x, x2, (v, i, j) = found
    # made % 4 in (0, 3) -> CNF: framing is balanced against the SAT/UNSAT alternation of null bases.
    framing = "CNF textbook" if made % 4 in (0, 3) else "natural-language menu"
    render = render_textbook if framing == "CNF textbook" else render_menu
    edit = f"swap the signs of {x.var_names[v - 1]} in C{i + 1:02d} (+ -> ¬) and C{j + 1:02d} (¬ -> +)"
    p1, p2 = sat_params(x, framing), sat_params(x2, framing)
    common = {"edit": edit, "swap": [x.var_names[v - 1], i, j], "alpha_target": alpha,
              "controlled": "n, m, alpha, tokens, every variable's polarity counts, the clause negation-count multiset, positions, names, framing",
              "varied": "the signs of two occurrences of one variable"}
    return _pair_items(domain="SAT", kind=kind, tasks=(SatTask(x), SatTask(x2)), prompts=(render(x), render(x2)),
                       framing=framing, specs=A.sat_members(100, walk_runs=walk_runs), channel=A.SAT_CHANNEL,
                       answer_format=A.SAT_FORMAT, bseed=bseed, tier=tier, params=({**p1, **common}, {**p2, **common}),
                       notes="Invariance pair: polarity-preserving sign swap. A1/A2 cues and C0 POLARITY are equal on x and x′ by construction (asserted).")


def _col_items(rng, kind, made, bseed, tier, sizes):
    n = sizes[made % len(sizes)]
    tercile = (made + made // 3) % 3  # not confounded with size (which cycles with made % 3)
    found = col_pair(rng, kind, n, tercile, want_colourable=(made % 2 == 0))
    if found is None:
        return None
    g, g2, (p, q) = found
    (a, b), (c, d) = g.edges[p], g.edges[q]
    rule = "No two enemies may share a room."
    prompts = (render_rooms(g, 3, "enemies", rule), render_rooms(g2, 3, "enemies", rule))
    common = {"n": g.n, "m": g.m, "k": 3, "mean_degree": round(2 * g.m / g.n, 3), "edit": f"{a}–{b}, {c}–{d} -> {a}–{d}, {c}–{b}",
              "edited_positions": [p, q], "tercile_of_first": tercile,
              "controlled": "degree of every person, |E|, people-list order (FIRST-FIT order), mention counts, tokens",
              "varied": "a double-edge swap in place"}
    specs = A.col_members(3, round(2.3 * g.n))
    return _pair_items(domain="COL", kind=kind, tasks=(ColouringTask(g, 3), ColouringTask(g2, 3)), prompts=prompts,
                       framing="rooms (themed)", specs=specs, channel=A.COL_CHANNEL, answer_format=A.COL_FORMAT,
                       bseed=bseed, tier=tier, params=(common, common),
                       notes="Invariance pair: double-edge swap preserving every degree.")


def _ent_items(rng, kind, made, bseed, tier, atom_sizes, stratum_tries, etr_max_atoms):
    n_atoms = atom_sizes[made % len(atom_sizes)]
    target = DEPTH_STRATA[made % len(DEPTH_STRATA)] if kind == "critical" else None
    found = ent_pair(rng, kind, n_atoms, target, want_follows=(made % 2 == 0), tries=stratum_tries)
    stratum_fallback = False
    if found is None and target is not None:
        found = ent_pair(rng, kind, n_atoms, None, want_follows=True, tries=stratum_tries)
        stratum_fallback = True
    if found is None:
        return None
    p, p2, c, (v, i, li, j, lj), atoms = found
    t1, t2 = EntailmentTask(p, c, "YN"), EntailmentTask(p2, c, "YN")
    used = F.atoms_of(p)
    depth = A.up_depth(t1)
    rho2 = F.rho(list(p2), c)
    common = {"atoms_drawn": n_atoms, "atoms_used": len(used), "premises": len(p), "conclusion": F.render(c, False),
              "edit": f"the negation on {F.render_lit(v, True)!r} moves from premise {j + 1} to premise {i + 1}",
              "up_depth_in_P": depth, "depth_stratum": depth_stratum(depth), "depth_target": target,
              "depth_target_missed": stratum_fallback, "rho_P": F.rho(list(p), c), "rho_P′": rho2,
              "controlled": "signed-literal FREQ, total and per-premise negation counts, connectives, premise positions, C's overlap with every premise",
              "varied": "which premise carries the negation of an atom that is not in C"}
    specs = A.ent_members(with_etr=len(used) <= etr_max_atoms)
    return _pair_items(domain="ENT", kind=kind, tasks=(t1, t2), prompts=(A.render_machine_facts(t1), A.render_machine_facts(t2)),
                       framing="machine facts", specs=specs, channel=A.ENT_CHANNEL, answer_format=A.ENT_YN_FORMAT,
                       bseed=bseed, tier=tier, params=(common, common),
                       notes="Invariance pair: a negation moves between two occurrences of an atom not in C.")


# --- set invariants ----------------------------------------------------------------------------


def check_set(items: list) -> list[str]:
    errs: list[str] = []
    if len(items) != 2:
        return [f"expected a pair, got {len(items)} items"]
    x, x2 = sorted(items, key=lambda it: it.params["member"] != "x")
    domain, kind = x.domain, x.params["pair_kind"]
    t1, t2 = load_task(x.instance), load_task(x2.instance)
    for label in CUE_LABELS[domain]:
        if label in x.predictions and x.predictions[label]["answer"] != x2.predictions[label]["answer"]:
            errs.append(f"cue {label} differs within the pair")
    errs += surface.equal_token_multisets({"x": x.prompt, "x-prime": x2.prompt})
    if domain == "SAT":
        a, b = t1.cnf, t2.cnf
        diff = [k for k in range(a.m) if a.clauses[k] != b.clauses[k]]
        if len(diff) != 2:
            errs.append(f"{len(diff)} clauses differ (expected 2)")
        if x.params["polarity_counts"] != x2.params["polarity_counts"]:
            errs.append("per-variable polarity counts differ")
        if x.params["clause_negation_multiset"] != x2.params["clause_negation_multiset"]:
            errs.append("clause negation multiset differs")
        g1, g2 = x.ground_truth["satisfiable"], x2.ground_truth["satisfiable"]
        if kind in ("critical", "B1") and not (g1 and not g2):
            errs.append(f"{kind} pair is not SAT -> UNSAT")
        if kind == "null" and g1 != g2:
            errs.append("null pair flips g")
        if kind == "B1" and (x2.predictions["B1 UP-3"]["answer"] != "UNSAT" or x.predictions["B1 UP-3"]["answer"] != "SAT"):
            errs.append("B1 pair: UP-3 does not refute x′ only")
    elif domain == "COL":
        g1, g2 = t1.graph, t2.graph
        if g1.vertices != g2.vertices or g1.m != g2.m:
            errs.append("people list or pair count differs")
        if any(g1.degree(v) != g2.degree(v) for v in g1.vertices):
            errs.append("degree sequence differs")
        if sum(1 for e1, e2 in zip(g1.edges, g2.edges) if e1 != e2) != 2:
            errs.append("edit is not a two-position in-place swap")
        c1, c2 = x.ground_truth["colourable"], x2.ground_truth["colourable"]
        if kind == "critical" and not (c1 and not c2):
            errs.append("critical pair is not colourable -> not")
        if kind == "null" and c1 != c2:
            errs.append("null pair flips g")
    else:
        if Counter(l for p in t1.premises for l in F.literals(p)) != Counter(l for p in t2.premises for l in F.literals(p)):
            errs.append("signed-literal FREQ differs")
        if sorted(premise_neg(p) for p in t1.premises) != sorted(premise_neg(p) for p in t2.premises):
            errs.append("per-premise negation multiset differs")
        if [p[0] for p in t1.premises] != [p[0] for p in t2.premises]:
            errs.append("premise forms differ")
        if t1.probe != t2.probe:
            errs.append("conclusion differs")
        facts = {l for p in t1.premises if is_categorical(p) for l in F.literals(p)}
        if F.literals(t1.probe)[0] in facts:
            errs.append("C is a stated fact")
        f1, f2 = x.ground_truth["follows"], x2.ground_truth["follows"]
        if kind == "critical" and not (f1 and not f2):
            errs.append("critical pair is not follows -> does not")
        if kind == "null" and f1 != f2:
            errs.append("null pair flips g")
    return errs
