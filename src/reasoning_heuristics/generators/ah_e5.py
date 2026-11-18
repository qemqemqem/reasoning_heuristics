"""A/H E5: rule inversion with length-matched preamble controls (A3 TEXTBOOK-TRANSFER).

Design (A/H §2.6 E5, §2.8 E5). One set = one base instance shown in each framing:

    T     textbook rule, no preamble                     correct answer Sol(x)
    N     T + a neutral preamble restating the standard  Sol(x)
          meaning (length-matched to I's preamble)
    I     the same constraint list + an inverting        Sol(x_inv); TT answers Sol(x)
          rule and preamble
    I+R   I + a one-line reminder before the question    Sol(x_inv)
    P     (SAT only) half the clauses, marked ★, use     Sol(x_P); TT's violations fall on ★
          the inverted meaning

- SAT (n in {12, 16}, alpha in [3.8, 4.3]): "a clause is satisfied when at least one of its
  literals is FALSE", so x_inv = F-bar (every literal flipped). Kept only if F is SAT and
  F and F-bar are jointly UNSAT (no textbook solution is valid under inversion). Half the bases
  have a unique textbook solution (crossed with size).
- COL (n in {10, 14}, k = 4): "the listed pairs are friends; only friends may share a room",
  a proper colouring of the complement graph. G is planted as k friend groups (cliques, sizes
  as equal as possible) plus cross-group pairs with p = 0.2, in shuffled order. Required: G
  k-colourable, the complement k-colourable (true by planting), FIRST-FIT on G within k rooms.
  The two solution sets are disjoint for n > k (asserted).
- KNAP (n = 10, weights 1-20, values 1-30, L = half the total weight): I = "total weight at
  least L, minimising total value". Required: the packing optimum is infeasible for the
  covering problem (its weight is below L), so the TT answer is wrong by construction.
- ENT (5-6 atoms, 2-3 "either ... or" premises, two disjuncts of 1-2 literals): I reads
  "either A, or B" as "neither A nor B" (NOR); the answer is the set of entailed literals.
  Required: the entailed-literal sets under the OR and NOR readings differ and are both
  non-empty.

N and I preambles have equal word counts and proxy-token counts within 3 (asserted; the
proxy is tokens.PROXY_NAME). Scoring is on the witness channel (which solution comes back):
EXACT and TT are set-valued over their solution sets in the likelihood table.

Readings of the doc (also in docs/GENERATORS.md):
- COL uses k = 4 for both sizes: with k planted friend cliques of sizes ceil(n/k), the
  textbook graph G contains a clique larger than 3 for k = 3 at n in {10, 14}, so "G
  k-colourable" fails; the doc's k in {3, 4} is infeasible at k = 3 under its own planting.
- P (partial inversion) is built for SAT only. The library's COL P ("★ partners must share
  a room") is an equality constraint the colouring task cannot express, and per-premise
  NOR marking is not expressible in the entailment task; both are left for later.
- The library's N/I colouring preambles differ by two words; the doc asks for word count +-0,
  so the N preamble here adds "who are" to match I exactly.
- Decision-level cues (A1/A2) and H RANDOM are not listed on E5 items: the doc predicts the
  decision unchanged by inversion, so they carry no witness-channel information here.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from reasoning_heuristics import tokens
from reasoning_heuristics.generators import ah_common as A
from reasoning_heuristics.generators.common import GenStats, make_item, set_hash, witness_channel
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.coloring import effective_graph
from reasoning_heuristics.heuristics.entailment import effective_premises, entailed_literals
from reasoning_heuristics.heuristics.sat import effective_cnf
from reasoning_heuristics.heuristics.tasks import ColouringTask, EntailmentTask, KnapsackTask, SatTask, load_task
from reasoning_heuristics.lexicon import DEVICES, PEOPLE, fixed_width_names
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.coloring.graph import Graph
from reasoning_heuristics.problems.coloring.render import render_rooms
from reasoning_heuristics.problems.entailment import formula as F
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack, solve_brute
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.cnf import CNF
from reasoning_heuristics.problems.sat.render import render_textbook
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.truth import truth

VERTICAL, EVAL_ID = "A/H", "E5"
LEXICON_PARTITIONED = False
DOMAINS = ("SAT", "COL", "KNAP", "ENT")
FRAMINGS = {"SAT": ("T", "N", "I", "I+R", "P"), "COL": ("T", "N", "I", "I+R"), "KNAP": ("T", "N", "I", "I+R"),
            "ENT": ("T", "N", "I", "I+R")}

SAT_DESC = 'Each clause is a disjunction of three literals ("¬" means NOT); a clause is satisfied when at least one of its literals is true. The formula is the conjunction of all clauses.'
SAT_DESC_INV = 'Each clause lists three literals ("¬" means NOT). In this puzzle a clause is satisfied when at least one of its literals is FALSE. The formula is the conjunction of all clauses.'
SAT_DESC_P = ('Each clause lists three literals ("¬" means NOT). A clause without a ★ is satisfied when at least one of its literals is true; '
              'a clause marked ★ is satisfied when at least one of its literals is FALSE. The formula is the conjunction of all clauses.')
PREAMBLE = {
    "SAT": ("Note on the rule: this is the standard reading; a clause fails only when every one of its three literals is false.",
            "Note on the rule: this is a reversed reading; a clause fails only when every one of its three literals is true."),
    "COL": ("Note on the rule: the two people in each listed pair must be put in different rooms; people who are not listed together may share or not.",
            "Note on the rule: people in each listed pair may share or not; any two people who are not listed together must be put in different rooms."),
    "KNAP": ("Note on the rule: the weight limit is a maximum; the chosen items must weigh no more than {L} in total.",
             "Note on the rule: the weight limit is a minimum; the chosen items must weigh no less than {L} in total."),
    "ENT": ("Note on the wording: here 'either A, or B' means that at least one of A and B is true.",
            "Note on the wording: here 'either A, or B' means that not even one of A and B is true."),
}
REMINDER = {
    "SAT": "Reminder: in this puzzle a clause is satisfied when at least one of its literals is false.",
    "COL": "Reminder: only listed friends may share a room; everyone else must be split up.",
    "KNAP": "Reminder: reach at least {L} in total weight, as cheaply as possible.",
    "ENT": "Reminder: in these facts, 'either ..., or ...' means that none of the listed options holds.",
}


def cells(params: dict[str, Any]) -> list[str]:
    return [f"{d}/{f}" for d in params.get("domains", DOMAINS) for f in FRAMINGS[d]]


# --- SAT -------------------------------------------------------------------------------------


def sat_prompt(cnf: CNF, framing: str, marked: tuple[int, ...] = ()) -> str:
    text = render_textbook(cnf)
    lines = text.splitlines()
    desc_idx = lines.index(SAT_DESC)
    if framing in ("I", "I+R"):
        lines[desc_idx] = SAT_DESC_INV
    if framing == "P":
        lines[desc_idx] = SAT_DESC_P
        for i in marked:
            j = desc_idx + 2 + i
            head, rest = lines[j].split(":", 1)
            lines[j] = f"{head}★:{rest}"
    if framing in ("N", "I", "I+R"):
        lines.insert(desc_idx + 1, PREAMBLE["SAT"][0 if framing == "N" else 1])
    if framing == "I+R":
        q = lines.index("Is there an assignment of truth values to the variables that satisfies every clause?")
        lines.insert(q, REMINDER["SAT"])
    return "\n".join(lines)


def sat_base(rng, n: int, want_unique: bool, tries: int = 4000):
    names = tuple(fixed_width_names("x", n))
    for _ in range(tries):
        alpha = rng.uniform(3.8, 4.3)
        cnf = S.random_ksat(n, round(alpha * n), 3, rng, names)
        if len(cnf.used_vars()) != n or S.solve(cnf) is None:
            continue
        both = cnf.with_clauses(list(cnf.clauses) + [tuple(-l for l in c) for c in cnf.clauses])
        if S.solve(both) is not None:
            continue
        if want_unique and S.count_solutions(cnf, limit=2) != 1:
            continue
        return cnf, alpha
    return None


def sat_marks(rng, cnf: CNF, tries: int = 200) -> tuple[int, ...] | None:
    """Half the clauses marked ★ so that the partially inverted formula is satisfiable and the
    textbook solution violates at least one ★ clause under the stated reading."""
    for _ in range(tries):
        marked = tuple(sorted(int(i) for i in rng.choice(cnf.m, size=cnf.m // 2, replace=False)))
        task = SatTask(cnf, inverted_clauses=marked)
        eff = effective_cnf(task)
        if S.solve(eff) is None:
            continue
        tt = S.solve(cnf)
        if any(i in marked for i in S.falsified_clauses(eff, tt)):
            return marked
    return None


def _assignment_valid(cnf: CNF):
    def check(key: str) -> bool:
        if "=" not in key:
            return False
        a = {kv.split("=")[0]: kv.split("=")[1] == "T" for kv in key.split(",")}
        return set(a) == set(cnf.var_names) and S.satisfies(cnf, a)
    return check


def _sat_set(rng, made, bseed, tier, sizes):
    n = sizes[made % len(sizes)]
    found = sat_base(rng, n, want_unique=((made // 2) % 2 == 0))  # crossed with size (made % 2)
    if found is None:
        return None, "no SAT base with F and F-bar jointly UNSAT"
    cnf, alpha = found
    marked = sat_marks(rng, cnf)
    if marked is None:
        return None, "no partial inversion with a satisfiable formula"
    n_text = S.count_solutions(cnf)
    tasks = {"T": SatTask(cnf), "N": SatTask(cnf), "I": SatTask(cnf, inverted=True), "I+R": SatTask(cnf, inverted=True),
             "P": SatTask(cnf, inverted_clauses=marked)}
    items = []
    set_id = f"{set_hash(bseed, 'SAT')}-SAT"
    base_hash = sha(tasks["T"].content_key())
    for fr in FRAMINGS["SAT"]:
        task = tasks[fr]
        eff = effective_cnf(task)
        n_stated = S.count_solutions(eff)
        channel = witness_channel("sat", {"exact": (_assignment_valid(eff), n_stated),
                                          "A3 TT[exact]": (_assignment_valid(cnf), n_text)})
        specs = [("exact", "EXACT", {}), ("A3 TT[exact]", "TT", {}), ("C0 POLARITY", "POLARITY", {}),
                 ("C1 GREEDY", "GREEDY", {"order": "MENTION", "mode": "INFEAS"}),
                 ("D DPLL (first solution)", "SEARCH", {"order": "MENTION", "value": "TRUE"})]
        prompt = sat_prompt(cnf, fr, marked if fr == "P" else ())
        tt = S.solve(cnf)
        gt = {**truth(task), "n_solutions_stated": n_stated, "n_solutions_textbook": n_text,
              "tt_answer_violations_under_stated": len(S.falsified_clauses(eff, tt))}
        items.append(make_item(
            vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=f"SAT/{fr}", domain="SAT", framing=f"CNF {fr}",
            prompt=prompt, answer_format=A.SAT_FORMAT, task=task, ground_truth=gt, specs=specs, channel=channel,
            seed=bseed, tier=tier, generator=__name__, base_hash=base_hash, source_hash=None if fr == "T" else base_hash,
            pair_id=set_id, params={"framing": fr, "n": n, "m": cnf.m, "alpha": round(alpha, 3), "marked_clauses": list(marked) if fr == "P" else None,
                                    "preamble": _preamble_of("SAT", fr), "prompt_tokens": tokens.count(prompt),
                                    "controlled": "clause list and order; preamble word count", "varied": _varied(fr)},
            notes="Rule inversion: F-bar = every literal flipped; F and F-bar are jointly unsatisfiable, so no textbook solution is valid under inversion.",
            cell_note=f"Framing {fr}."))
    return items, None


# --- COL -------------------------------------------------------------------------------------


def planted_friends(rng, n: int, k: int, p: float = 0.2):
    names = sorted(PEOPLE[i] for i in rng.choice(len(PEOPLE), size=n, replace=False))
    perm = [names[i] for i in rng.permutation(n)]
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    groups, pos = [], 0
    for s in sizes:
        groups.append(perm[pos:pos + s])
        pos += s
    group_of = {v: gi for gi, gr in enumerate(groups) for v in gr}
    edges = []
    for i, u in enumerate(names):
        for v in names[i + 1:]:
            if group_of[u] == group_of[v] or rng.random() < p:
                edges.append((u, v) if rng.random() < 0.5 else (v, u))
    edges = [edges[i] for i in rng.permutation(len(edges))]
    return Graph(tuple(names), tuple(edges)), groups


def _partition_member(g: Graph):
    def check(key: str) -> bool:
        if key == "IMPOSSIBLE":
            return False
        classes = [c.split(",") for c in key.split("|")]
        col = {v: i for i, c in enumerate(classes) for v in c}
        return set(col) == set(g.vertices) and G.is_proper(g, col)
    return check


def _col_set(rng, made, bseed, tier, sizes, k):
    n = sizes[made % len(sizes)]
    for _ in range(200):
        g, groups = planted_friends(rng, n, k)
        if G.k_colour(g, k) is None:
            continue
        if run_ff(g, k) == "IMPOSSIBLE":
            continue
        break
    else:
        return None, "no planted graph with G k-colourable and FIRST-FIT within k"
    comp = effective_graph(ColouringTask(g, k, complement=True))
    parts_text, parts_inv = G.enumerate_partitions(g, k, 10**6), G.enumerate_partitions(comp, k, 10**6)
    if parts_text is None or parts_inv is None:
        return None, "more than 10^6 partitions: solution-set sizes not computed"
    n_text, n_inv = len(parts_text), len(parts_inv)
    items = []
    set_id = f"{set_hash(bseed, 'COL')}-COL"
    base_hash = sha(ColouringTask(g, k).content_key())
    for fr in FRAMINGS["COL"]:
        inverted = fr in ("I", "I+R")
        task = ColouringTask(g, k, complement=inverted)
        eff = effective_graph(task)
        prompt = render_rooms(g, k, "friends" if inverted else "enemies",
                              "Only friends may share a room." if inverted else "No two enemies may share a room.",
                              preamble=_preamble_of("COL", fr), reminder=REMINDER["COL"] if fr == "I+R" else None)
        channel = witness_channel("coloring", {"exact": (_partition_member(eff), n_inv if inverted else n_text),
                                               "A3 TT[exact]": (_partition_member(g), n_text)})
        specs = [("exact", "EXACT", {}), ("A3 TT[exact]", "TT", {"inner": "EXACT"}), ("A3 TT[FIRST-FIT]", "TT", {"inner": "FF"}),
                 ("C1 FIRST-FIT (stated rule)", "FF", {"order": "LIST", "mode": "ABORT"}),
                 ("C2 DSATUR (stated rule)", "DSATUR", {"mode": "ABORT"}),
                 ("D DPLL (first solution)", "SEARCH", {"order": "LIST"}),
                 ("B1 DROP-CONSTRAINT(last 3)", "DROP-LAST", {"q": 3})]
        tt = G.k_colour(g, k)
        gt = {**truth(task), "n_partitions_stated": n_inv if inverted else n_text, "n_partitions_textbook": n_text,
              "tt_answer_violations_under_stated": len(G.conflicts(eff, tt))}
        items.append(make_item(
            vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=f"COL/{fr}", domain="COL", framing=f"rooms {fr}",
            prompt=prompt, answer_format=A.COL_FORMAT, task=task, ground_truth=gt, specs=specs, channel=channel,
            seed=bseed, tier=tier, generator=__name__, base_hash=base_hash, source_hash=None if fr == "T" else base_hash,
            pair_id=set_id, params={"framing": fr, "n": n, "k": k, "pairs": g.m, "friend_groups_planted": groups,
                                    "preamble": _preamble_of("COL", fr), "prompt_tokens": tokens.count(prompt),
                                    "controlled": "people, pair list and its order, room count, answer format; preamble word count",
                                    "varied": _varied(fr)},
            notes="Rule inversion: under 'only friends may share', the answer is a proper colouring of the complement graph; the solution sets are disjoint for n > k.",
            cell_note=f"Framing {fr}."))
    return items, None


def run_ff(g: Graph, k: int):
    from reasoning_heuristics.heuristics.base import run

    return run("coloring", "FF", ColouringTask(g, k), {"order": "LIST", "mode": "ABORT"}).answer


# --- KNAP ------------------------------------------------------------------------------------


def knap_prompt(k: Knapsack, framing: str) -> str:
    lines = [f"Ten items ({k.names[0]}–{k.names[-1]}) are available. Their weights and values are:"]
    lines += [f"{nm}: weight {w}, value {v}" for nm, v, w in zip(k.names, k.values, k.weights)]
    if framing in ("I", "I+R"):
        lines.append(f"Choose items so that the total weight is at least {k.capacity} and the total value is as small as possible.")
    else:
        lines.append(f"Choose items so that the total weight is at most {k.capacity} and the total value is as large as possible.")
    pre = _preamble_of("KNAP", framing)
    if pre:
        lines.append(pre.format(L=k.capacity))
    if framing == "I+R":
        lines.append(REMINDER["KNAP"].format(L=k.capacity))
    lines.append('Think as carefully as you need. Then end your reply with your final answer as JSON on its own line: {"items": ["<letter>", ...]}')
    return "\n".join(lines)


def _subset_member(optima: list[list[str]]):
    keys = {",".join(sorted(s)) for s in optima}
    return lambda key: key in keys


def _knap_set(rng, made, bseed, tier):
    for _ in range(200):
        w = [int(x) for x in rng.integers(1, 21, size=10)]
        v = [int(x) for x in rng.integers(1, 31, size=10)]
        k = Knapsack(tuple("ABCDEFGHIJ"), tuple(v), tuple(w), sum(w) // 2)
        _, pack = solve_brute(k)
        _, cover = solve_brute(k, covering=True)
        if all(k.weight_of(s) < k.capacity for s in pack) and not ({",".join(sorted(s)) for s in pack} & {",".join(sorted(s)) for s in cover}):
            break
    else:
        return None, "no instance with the packing optimum infeasible for covering"
    items = []
    set_id = f"{set_hash(bseed, 'KNAP')}-KNAP"
    base_hash = sha(KnapsackTask(k).content_key())
    for fr in FRAMINGS["KNAP"]:
        covering = fr in ("I", "I+R")
        task = KnapsackTask(k, covering=covering)
        channel = witness_channel("knapsack", {"exact": (_subset_member(cover if covering else pack), len(cover if covering else pack)),
                                               "A3 TT[exact]": (_subset_member(pack), len(pack))})
        specs = [("exact", "EXACT", {}), ("A3 TT[exact]", "TT", {})]
        if not covering:
            specs += [("C1 INPUT-FIT", "INPUT-FIT", {}), ("C1 RATIO-SKIP", "RATIO-SKIP", {}),
                      ("C1 VALUE", "VALUE", {}), ("C1 LARGEST-FIT", "LARGEST-FIT", {})]
        prompt = knap_prompt(k, fr)
        gt = {**truth(task), "optimal_subsets": [sorted(s) for s in (cover if covering else pack)],
              "packing_optimal_subsets": [sorted(s) for s in pack]}
        items.append(make_item(
            vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=f"KNAP/{fr}", domain="KNAP", framing=f"packing {fr}",
            prompt=prompt, answer_format='JSON {"items": [...]}', task=task, ground_truth=gt, specs=specs, channel=channel,
            seed=bseed, tier=tier, generator=__name__, base_hash=base_hash, source_hash=None if fr == "T" else base_hash,
            pair_id=set_id, params={"framing": fr, "capacity": k.capacity, "preamble": _preamble_of("KNAP", fr),
                                    "prompt_tokens": tokens.count(prompt), "varied": _varied(fr)},
            notes="Rule inversion (EHOP-style): covering instead of packing; the textbook optimum weighs less than L, so it is infeasible here.",
            cell_note=f"Framing {fr}."))
    return items, None


# --- ENT -------------------------------------------------------------------------------------


def _ent_set(rng, made, bseed, tier, tries: int = 3000):
    devices = list(DEVICES)
    for _ in range(tries):
        n_atoms = int(rng.integers(5, 7))
        atoms = [f"{d}:{DEVICES[d]}" for d in (devices[i] for i in rng.choice(len(devices), size=n_atoms, replace=False))]
        prem = []
        for _ in range(int(rng.integers(2, 4))):
            sizes = [int(rng.integers(1, 3)) for _ in range(2)]
            chosen = rng.choice(n_atoms, size=sum(sizes), replace=False)
            d1 = F.conj(*[F.lit(atoms[a], bool(rng.integers(2))) for a in chosen[:sizes[0]]])
            d2 = F.conj(*[F.lit(atoms[a], bool(rng.integers(2))) for a in chosen[sizes[0]:]])
            prem.append(F.disj(d1, d2))
        prem = tuple(prem)
        std, nor = EntailmentTask(prem, None, "OPEN"), EntailmentTask(prem, None, "OPEN", reading="nor")
        used = F.atoms_of(prem)
        if not F.models(effective_premises(std), used) or not F.models(effective_premises(nor), used):
            continue
        e_std = entailed_literals(effective_premises(std), used)
        e_nor = entailed_literals(effective_premises(nor), used)
        if e_std and e_nor and e_std != e_nor:
            break
    else:
        return None, "no premise set whose OR and NOR readings entail different non-empty literal sets"
    items = []
    set_id = f"{set_hash(bseed, 'ENT')}-ENT"
    base_hash = sha({"premises": [F.canonical(p) for p in prem]})
    for fr in FRAMINGS["ENT"]:
        task = EntailmentTask(prem, None, "OPEN", reading="nor" if fr in ("I", "I+R") else "standard")
        prompt = A.render_machine_facts(task, preamble=_preamble_of("ENT", fr), reminder=REMINDER["ENT"] if fr == "I+R" else None)
        specs = [("exact", "EXACT", {}), ("A3 TT[exact]", "TT", {}), ("B4 FIRST", "FIRST", {}), ("A1 NONE", "NONE", {})]
        gt = {**truth(task), "entailed_under_or": e_std, "entailed_under_nor": e_nor}
        items.append(make_item(
            vertical=VERTICAL, eval_id=EVAL_ID, set_id=set_id, cell=f"ENT/{fr}", domain="ENT", framing=f"machine facts {fr}",
            prompt=prompt, answer_format=A.ENT_OPEN_FORMAT, task=task, ground_truth=gt, specs=specs,
            channel=witness_channel("entailment"), seed=bseed, tier=tier, generator=__name__, base_hash=base_hash,
            source_hash=None if fr == "T" else base_hash, pair_id=set_id,
            params={"framing": fr, "atoms": len(atoms), "premises": len(prem), "preamble": _preamble_of("ENT", fr),
                    "prompt_tokens": tokens.count(prompt), "varied": _varied(fr)},
            notes="Rule inversion: 'either A, or B' redefined as NOR; the answer is the set of entailed literals.",
            cell_note=f"Framing {fr}."))
    return items, None


# --- shared ------------------------------------------------------------------------------------


def _preamble_of(domain: str, framing: str) -> str | None:
    if framing == "N":
        return PREAMBLE[domain][0]
    if framing in ("I", "I+R"):
        return PREAMBLE[domain][1]
    return None


def _varied(framing: str) -> str:
    return {"T": "textbook rule, no preamble", "N": "textbook rule + length-matched neutral preamble",
            "I": "inverted rule + inverting preamble", "I+R": "I + reminder just before the question",
            "P": "only the ★ constraints carry the inverted meaning"}[framing]


def generate(tier: str, seed: int, per_cell: int | None = None, domains: list[str] | None = None,
             sat_sizes: list[int] = (12, 16), col_sizes: list[int] = (10, 14), col_k: int = 4,
             max_attempts: int = 300) -> tuple[list, dict]:
    per_cell = per_cell or TIERS[tier].default_per_cell
    stats = GenStats()
    items: list = []
    attempt = 0
    for domain in (domains or DOMAINS):
        made = tried = 0
        while made < per_cell:
            tried += 1
            if tried > max_attempts:
                raise RuntimeError(f"A/H E5 {domain}: {made}/{per_cell} sets after {max_attempts} attempts; stats {stats.to_json()}")
            bseed = base_seed(tier, seed, attempt)
            attempt += 1
            stats.attempts += 1
            rng = rng_for(bseed, f"AH-E5-{domain}")
            if domain == "SAT":
                set_items, why = _sat_set(rng, made, bseed, tier, sat_sizes)
            elif domain == "COL":
                set_items, why = _col_set(rng, made, bseed, tier, col_sizes, col_k)
            elif domain == "KNAP":
                set_items, why = _knap_set(rng, made, bseed, tier)
            else:
                set_items, why = _ent_set(rng, made, bseed, tier)
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


def check_set(items: list) -> list[str]:
    errs: list[str] = []
    domain = items[0].domain
    by = {it.params["framing"]: it for it in items}
    if set(by) != set(FRAMINGS[domain]):
        return [f"framings present: {sorted(by)}"]
    tasks = {fr: load_task(it.instance) for fr, it in by.items()}
    # identical constraint lists across framings
    if domain == "SAT":
        if len({t.cnf for t in tasks.values()}) != 1:
            errs.append("clause lists differ across framings")
    elif domain == "COL":
        if len({t.graph for t in tasks.values()}) != 1:
            errs.append("pair lists differ across framings")
    elif domain == "KNAP":
        if len({t.knapsack for t in tasks.values()}) != 1:
            errs.append("item lists differ across framings")
    else:
        if len({t.premises for t in tasks.values()}) != 1:
            errs.append("premises differ across framings")
    # length-matched preambles
    pn, pi = by["N"].params["preamble"], by["I"].params["preamble"]
    if len(pn.split()) != len(pi.split()):
        errs.append(f"N and I preambles differ in word count ({len(pn.split())} vs {len(pi.split())})")
    if abs(tokens.count(pn) - tokens.count(pi)) > 3:
        errs.append("N and I preambles differ by more than 3 proxy tokens")
    # the textbook answer is invalid under inversion, and correct answers differ
    for fr in ("I", "I+R"):
        it = by[fr]
        tt = it.predictions["A3 TT[exact]"]["answer"]
        if domain == "SAT":
            eff = effective_cnf(tasks[fr])
            if S.satisfies(eff, tt):
                errs.append(f"{fr}: the textbook solution is valid under inversion")
        elif domain == "COL":
            if G.is_proper(effective_graph(tasks[fr]), tt):
                errs.append(f"{fr}: the textbook colouring is valid under inversion")
        elif domain == "KNAP":
            if tasks[fr].knapsack.feasible(tt, covering=True):
                errs.append(f"{fr}: the packing optimum is feasible for covering")
        else:
            if it.ground_truth["answer"] == by["T"].ground_truth["answer"]:
                errs.append(f"{fr}: OR and NOR readings entail the same literals")
    if domain == "SAT":
        p = by["P"]
        if not p.ground_truth["satisfiable"]:
            errs.append("P: the partially inverted formula is unsatisfiable")
        if len(p.params["marked_clauses"]) != tasks["T"].cnf.m // 2:
            errs.append("P: not half the clauses are marked")
    return errs
