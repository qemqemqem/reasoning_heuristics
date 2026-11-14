"""C E2: rule discrimination by single-edit minimal pairs (C §2.6 E2, §2.8 E2-COL / SAT / KNAP).

For a base x, every single edit x' is enumerated with the edit engine
(counterfactual/edits.py) and its *change signature* (which members' outputs change, and
whether the ground truth g changes) is computed. For a contrast (h1, h2) the cells are:

    BASE        the unedited instance
    D(h1|h2)    h1 changes, h2 does not, g does not
    D(h2|h1)    the reverse
    PLACEBO     no signature member and not g changes
    G-ONLY      g changes, the focal members h1 and h2 do not

Contrasts: COL FF vs DSATUR, FF vs LF, DSATUR vs LF (edits: add one edge; FF = first-fit in
listing order, ties to π_L); SAT GREEDY vs UC-DET, GREEDY vs POLARITY (edits: flip one
literal's sign); KNAP RATIO vs DIFF, RATIO vs VALUE, RATIO-PREFIX vs RATIO-SKIP (edits: one
value or weight +-1..6, staying two-digit). A set is one base x one contrast (5 items).

Selection rules from the doc, as implemented:
- every cell of a set uses the same edit type (all additions / all sign flips / all
  "one number changed by +-1..6", value or weight), and the four edited items have the same token delta from BASE
  (asserted);
- the D(h1|h2) and D(h2|h1) edits are chosen so the *competitors'* change vectors (the
  other signature members) are as equal as possible; whether they are exactly balanced is
  recorded (`params.balance`) and counted in the stats;
- the PLACEBO and G-ONLY edits are chosen closest in location (listing position / clause
  index / item index) to the D edits.

Readings of the doc (also in docs/GENERATORS.md):
- G-ONLY is "g changes, the *focal* members do not" (the doc's cell table), not "no member
  changes"; with all members fixed it is nearly unreachable.
- Colouring edits are edge additions only, so all cells share one edit type (the library
  set does the same); deletions are available in the engine.
- SAT bases default to α in {3.5, 4.0}: at α = 3.0 no single sign flip gave a G-ONLY cell in
  30 of 30 measured bases (GREEDY-ABORT must already dead-end for g to flip without it
  changing). `alphas` is a parameter.
- KNAP uses the doc's dev size n = 10 by default (`n_knap`, up to 22: the independent
  validator enumerates subsets). Bases need a unique optimum and no round ratios (v/w in
  {1/2, 1, 2}). The knapsack tie psychophysics set (E2-KT), E2-TSP, and the POLARITY vs
  JW/MOMS mixed 2+3-SAT contrast are not built; UC vs GUC/SC is not a focal contrast
  (GUC/SC are still predicted on every SAT item).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from reasoning_heuristics import tokens
from reasoning_heuristics.counterfactual import edits as E
from reasoning_heuristics.generators import c_common as CC
from reasoning_heuristics.generators.common import Channel, GenStats, make_item, set_hash, witness_channel
from reasoning_heuristics.hashing import sha
from reasoning_heuristics.heuristics.answers import answer_key
from reasoning_heuristics.heuristics.tasks import ColouringTask, KnapsackTask, SatTask, load_task
from reasoning_heuristics.problems.coloring import graph as G
from reasoning_heuristics.problems.knapsack.knapsack import Knapsack, solve_brute
from reasoning_heuristics.problems.sat import cnf as S
from reasoning_heuristics.problems.sat.render import render_c
from reasoning_heuristics.seeds import TIERS, base_seed, rng_for
from reasoning_heuristics.validate.truth import truth

VERTICAL, EVAL_ID = "C", "E2"
LEXICON_PARTITIONED = False
CELL_NAMES = ("BASE", "D(h1|h2)", "D(h2|h1)", "PLACEBO", "G-ONLY")

SIGNATURE = {
    "COL": [("FF", "FF", {"order": "LIST"}), ("DSATUR", "DSATUR", {"tie": "LIST"}), ("LF", "LF", {"tie": "LIST"})],
    "SAT": [("GREEDY", "GREEDY", {"order": "MENTION"}), ("UC", "UC", {}), ("POLARITY", "POLARITY", {})],
    "KNAP": [("RATIO", "RATIO-SKIP", {}), ("PREFIX", "RATIO-PREFIX", {}), ("DIFF", "DIFF", {}), ("VALUE", "VALUE", {})],
}
CONTRASTS = {
    "COL": [("FF", "DSATUR"), ("FF", "LF"), ("DSATUR", "LF")],
    "SAT": [("GREEDY", "UC"), ("GREEDY", "POLARITY")],
    "KNAP": [("RATIO", "DIFF"), ("RATIO", "VALUE"), ("PREFIX", "RATIO")],
}
DEFAULTS = {"domains": ["COL", "SAT", "KNAP"], "n_col": 16, "mean_degree": [4.0, 4.8], "max_partitions": 500_000,
            "n_sat": 20, "alphas": [3.5, 4.0], "n_knap": 10, "max_attempts": 20_000, "repeat_prompt": False}


def cell_name(h1: str, h2: str, cell: str) -> str:
    return cell.replace("h1", h1).replace("h2", h2)


def cells(params: dict[str, Any]) -> list[str]:
    out = []
    for d in params.get("domains", DEFAULTS["domains"]):
        for h1, h2 in CONTRASTS[d]:
            out += [f"{d}/{h1}-vs-{h2}/{cell_name(h1, h2, c)}" for c in CELL_NAMES]
    return out


# --- domain plumbing -----------------------------------------------------------------------------------


def knap_prompt(k: Knapsack) -> str:
    lines = [f"You can carry at most {k.capacity} kg. Choose items to maximise total value without exceeding the limit.",
             "Items (value, weight in kg):"]
    lines += [f"{nm}: value {v}, weight {w}" for nm, v, w in zip(k.names, k.values, k.weights)]
    lines += ["", "After the line ANSWER:, write the letters of the chosen items in alphabetical order, separated by commas."]
    return "\n".join(lines)


def round_ratio(k: Knapsack) -> bool:
    return any(v == w or v == 2 * w or 2 * v == w for v, w in zip(k.values, k.weights))


def g_of(domain: str, task) -> Any:
    if domain == "COL":
        return G.chromatic_number(task.graph)
    if domain == "SAT":
        return S.solve(task.cnf) is not None
    opt, subsets = solve_brute(task.knapsack)
    return ",".join(sorted(subsets[0])) if len(subsets) == 1 else "TIE"


def edit_location(domain: str, task, edit: E.Edit) -> float:
    if domain == "COL":
        return (task.graph.position[edit.args[0]] + task.graph.position[edit.args[1]]) / 2
    if domain == "SAT":
        return float(edit.args[0])
    return float(task.knapsack.names.index(edit.args[0]))


def edits_for(domain: str, task):
    if domain == "COL":
        g = task.graph
        for e, t in E.colouring_edits(task, ("add_edge",)):
            if g.degree(e.args[0]) and g.degree(e.args[1]):  # keep neighbour lines non-empty: equal token deltas
                yield e, t
    elif domain == "SAT":
        yield from E.sat_edits(task, ("flip_sign",))
    else:
        for e, t in E.knapsack_edits(task):
            if not round_ratio(t.knapsack):
                yield e, t


def prompt_of(domain: str, task, repeat: bool) -> str:
    if domain == "COL":
        p = CC.render_colouring(task.graph, "fewest", list(task.graph.vertices), None, "adjacency", repeat)
    elif domain == "SAT":
        p = render_c(task.cnf, list(task.answer_order))
        if repeat:
            p = p + "\n\nHere is the same problem again, repeated verbatim:\n\n" + p
    else:
        p = knap_prompt(task.knapsack)
    return p


def item_members(domain: str) -> list:
    if domain == "COL":
        return [("FF-LIST", "FF", {"order": "LIST"}), ("FF-LABEL", "FF", {"order": "LABEL"}),
                ("DSATUR", "DSATUR", {"tie": "LIST"}), ("DSATUR-LABEL", "DSATUR", {"tie": "LABEL"}),
                ("LF", "LF", {"tie": "LIST"}), ("DPLL-LIST (D)", "SEARCH", {"order": "LIST"}),
                ("GREEDY+REPAIR-LIST (C->F)", "GREEDY+REPAIR", {"order": "LIST"}),
                ("RO-FF (C3)", "RO-FF", {"samples": 1000, "seed": 0}), ("EXACT", "EXACT", {}),
                ("RANDOM (H)", "RANDOM", {}), ("NOISY-EXACT", "NOISY-EXACT", {"p": 0.01})]
    if domain == "SAT":
        return [("GREEDY-MENTION", "GREEDY", {"order": "MENTION"}), ("GREEDY-INDEX", "GREEDY", {"order": "INDEX"}),
                ("UC-DET (C2)", "UC", {}), ("GUC-DET (C2)", "GUC", {}), ("SC-DET (C2)", "SC", {}),
                ("POLARITY (C0)", "POLARITY", {}), ("DPLL-MENTION (D, T first)", "SEARCH", {"order": "MENTION"}),
                ("RO-GREEDY (C3)", "RO-GREEDY", {"samples": 200, "seed": 0}), ("EXACT", "EXACT", {}),
                ("RANDOM (H)", "RANDOM", {})]
    return [(n, n, {}) for n in ("INPUT-FIT", "RATIO-SKIP", "RATIO-PREFIX", "VALUE", "LARGEST-FIT", "DIFF",
                                 "RATIO+BEST-SINGLE", "EXACT")]


def channel_of(domain: str, task, gt: dict[str, Any]) -> Channel:
    if domain == "COL":
        return CC.colouring_channel(task.graph, gt["chromatic_number"], gt["n_optimal_partitions"])
    if domain == "SAT":
        return CC.sat_channel(task.cnf, gt["n_solutions"])
    return witness_channel("knapsack")


def ground_truth(domain: str, task, params) -> dict[str, Any] | None:
    gt = truth(task)
    if domain == "COL":
        masks = G.enumerate_partitions(task.graph, gt["chromatic_number"], params["max_partitions"])
        if masks is None:
            return None
        gt["n_optimal_partitions"] = len(masks)
    elif domain == "SAT":
        gt["n_solutions"] = CC.count_models(task.cnf)
    else:
        opt, subsets = solve_brute(task.knapsack)
        if len(subsets) != 1:
            return None
        gt["optimal_set"] = sorted(subsets[0])
    return gt


def draw_base(domain: str, rng, params, index: int):
    if domain == "COL":
        n = params["n_col"]
        lo, hi = (int(round(x * n / 2)) for x in params["mean_degree"])
        g = G.random_gnm(CC.labels_for(n, "v", rng), int(rng.integers(lo, hi + 1)), rng)
        order = [g.vertices[int(i)] for i in rng.permutation(n)]  # labels independent of the listing
        g = g.relisted(order)
        return ColouringTask(g, None, (), tuple(g.vertices)), {"n": n, "m": g.m}
    if domain == "SAT":
        n = params["n_sat"]
        alpha = params["alphas"][index % len(params["alphas"])]
        base = S.random_ksat(n, int(round(alpha * n)), 3, rng, tuple(f"u{i}" for i in range(n)))
        labels = CC.labels_for(n, "x", rng)
        mention = base.mention_order() + [v for v in range(1, n + 1) if v not in base.mention_order()]
        cnf = base.renamed({base.var_names[v - 1]: labels[i] for i, v in enumerate(mention)})
        mo = cnf.mention_order() + [v for v in range(1, n + 1) if v not in cnf.mention_order()]
        return SatTask(cnf, (), tuple(cnf.var_names[v - 1] for v in mo)), {"n": n, "m": cnf.m, "alpha": alpha}
    n = params["n_knap"]
    w = [int(x) for x in rng.integers(10, 100, size=n)]
    v = [int(x) for x in rng.integers(10, 100, size=n)]
    k = Knapsack(tuple(chr(ord("A") + i) for i in range(n)), tuple(v), tuple(w), int(0.45 * sum(w)))
    return KnapsackTask(k), {"n": n, "capacity": k.capacity}


# --- selection ------------------------------------------------------------------------------------------


def select_cells(domain: str, task, sigs, h1: str, h2: str, rng, base_tokens: int, repeat: bool):
    others = [lbl for lbl, _, _ in SIGNATURE[domain] if lbl not in (h1, h2)]
    allm = [lbl for lbl, _, _ in SIGNATURE[domain]]
    d1 = [x for x in sigs if x[2][h1] and not x[2][h2] and not x[2]["TRUTH"]]
    d2 = [x for x in sigs if x[2][h2] and not x[2][h1] and not x[2]["TRUTH"]]
    pl = [x for x in sigs if not any(x[2][k] for k in allm) and not x[2]["TRUTH"]]
    go = [x for x in sigs if x[2]["TRUTH"] and not x[2][h1] and not x[2][h2]]
    if not (d1 and d2 and pl and go):
        return None

    cache: dict[int, int] = {}

    def delta(x):
        if id(x) not in cache:
            cache[id(x)] = tokens.count(prompt_of(domain, x[1], repeat)) - base_tokens
        return cache[id(x)]

    pairs = []
    for a in d1:
        for b in d2:
            if delta(a) != delta(b):
                continue
            mismatch = sum(a[2][o] != b[2][o] for o in others)
            pairs.append((mismatch, float(rng.random()), a, b))
    if not pairs:
        return None
    mismatch, _, a, b = min(pairs, key=lambda t: (t[0], t[1]))
    target_delta = delta(a)
    loc = (edit_location(domain, task, a[0]) + edit_location(domain, task, b[0])) / 2
    pl = [x for x in pl if delta(x) == target_delta]
    go = [x for x in go if delta(x) == target_delta]
    if not pl or not go:
        return None
    p = min(pl, key=lambda x: (abs(edit_location(domain, task, x[0]) - loc), x[0].text))
    g = min(go, key=lambda x: (abs(edit_location(domain, task, x[0]) - loc), x[0].text))
    balance = {"competitors": others, "D(h1|h2)": {o: a[2][o] for o in others}, "D(h2|h1)": {o: b[2][o] for o in others},
               "balanced": mismatch == 0}
    return {"D(h1|h2)": a, "D(h2|h1)": b, "PLACEBO": p, "G-ONLY": g}, balance


def generate(tier: str, seed: int, per_cell: int | None = None, **params) -> tuple[list, dict]:
    p = {**DEFAULTS, **params}
    per_cell = per_cell or TIERS[tier].default_per_cell
    stats = GenStats()
    balance_counts = {"balanced": 0, "unbalanced": 0}
    items: list = []
    attempt = 0
    for domain in p["domains"]:
        done = {c: 0 for c in CONTRASTS[domain]}
        index = 0
        while min(done.values()) < per_cell:
            bseed = base_seed(tier, seed, attempt)
            attempt += 1
            stats.attempts += 1
            CC.guard(attempt, p, stats, f"E2-{domain}")
            rng = rng_for(bseed, f"C-E2-{domain}")
            task, base_info = draw_base(domain, rng, p, index)
            if domain == "KNAP" and round_ratio(task.knapsack):
                stats.reject("round ratio in the base")
                continue
            base_gt = ground_truth(domain, task, p)
            if base_gt is None:
                stats.reject("base ground truth not unique / enumeration cap")
                continue
            sigs = E.search(task, SIGNATURE[domain], lambda t: g_of(domain, t), lambda s: True, edits=edits_for(domain, task))
            base_tokens = tokens.count(prompt_of(domain, task, p["repeat_prompt"]))
            open_contrasts = sorted((c for c in CONTRASTS[domain] if done[c] < per_cell), key=lambda c: done[c])
            chosen = None
            for h1, h2 in open_contrasts:
                sel = select_cells(domain, task, sigs, h1, h2, rng, base_tokens, p["repeat_prompt"])
                if sel is not None:
                    chosen = (h1, h2, sel)
                    break
            if chosen is None:
                stats.reject("not every cell reachable for an open contrast")
                continue
            h1, h2, (picked, balance) = chosen
            set_items = build_set(domain, task, base_gt, base_info, h1, h2, picked, balance, bseed, tier, p)
            if set_items is None:
                stats.reject("edited ground truth not unique / enumeration cap")
                continue
            problems = check_set(set_items)
            if problems:
                stats.reject("set invariant failed: " + problems[0][:60])
                continue
            items += set_items
            done[(h1, h2)] += 1
            index += 1
            stats.accepted += 1
            balance_counts["balanced" if balance["balanced"] else "unbalanced"] += 1
    out = stats.to_json()
    out["competitor_balance"] = balance_counts
    return items, out


def build_set(domain, base_task, base_gt, base_info, h1, h2, picked, balance, bseed, tier, p) -> list | None:
    base_hash = sha(base_task.content_key())
    sid = set_hash(bseed, domain, h1, h2)
    contrast = f"{h1}-vs-{h2}"
    variants = [("BASE", None, base_task, base_gt)]
    for cell in CELL_NAMES[1:]:
        edit, t, sig = picked[cell]
        gt = ground_truth(domain, t, p)
        if gt is None:
            return None
        variants.append((cell, (edit, sig), t, gt))
    framing = "realistic: packing" if domain == "KNAP" else "textbook"
    dom_name = {"COL": "colouring", "SAT": "3-SAT", "KNAP": "knapsack"}[domain]
    fmt = {"COL": CC.COLOUR_FEWEST_FORMAT, "SAT": CC.SAT_FORMAT,
           "KNAP": "After the line ANSWER:, the letters of the chosen items in alphabetical order"}[domain]
    out = []
    for cell, ed, t, gt in variants:
        prompt = prompt_of(domain, t, p["repeat_prompt"])
        out.append(make_item(
            vertical=VERTICAL, eval_id=EVAL_ID, set_id=sid, cell=f"{domain}/{contrast}/{cell_name(h1, h2, cell)}",
            domain=dom_name, framing=framing, prompt=prompt, answer_format=fmt, task=t, ground_truth=gt,
            specs=item_members(domain), channel=channel_of(domain, t, gt), seed=bseed, tier=tier, generator=__name__,
            base_hash=base_hash, source_hash=None if ed is None else base_hash, pair_id=f"E2-{domain}-{sid}",
            params={**base_info, "contrast": [h1, h2], "design_cell": cell,
                    "edit": "none" if ed is None else ed[0].to_json(),
                    "signature": None if ed is None else ed[1], "balance": balance,
                    "prompt_tokens": tokens.count(prompt), "tokenizer_proxy": tokens.PROXY_NAME,
                    "repeat_prompt": p["repeat_prompt"]},
            notes="Single edits of the base. Cell = which members' outputs change (computed over all single edits). "
                  "An edge between differently coloured FF vertices never changes FF (lemma L2)." if domain == "COL" else
                  "Single edits of the base. Cell = which members' outputs change (computed over all single edits).",
            cell_note=f"Contrast {h1} vs {h2}, cell {cell_name(h1, h2, cell)}.",
        ))
    return out


def check_set(items: list) -> list[str]:
    errs: list[str] = []
    by = {it.params["design_cell"]: it for it in items}
    if sorted(by) != sorted(CELL_NAMES):
        return [f"set has cells {sorted(by)}"]
    domain = items[0].cell.split("/")[0]
    h1, h2 = items[0].params["contrast"]
    tasks = {c: load_task(it.instance) for c, it in by.items()}
    sig_members = SIGNATURE[domain]
    from reasoning_heuristics.heuristics.base import run

    def out(c, lbl):
        _, name, prm = next(s for s in sig_members if s[0] == lbl)
        t = tasks[c]
        return answer_key(t.domain, run(t.domain, name, t, prm).answer)

    g = {c: g_of(domain, t) for c, t in tasks.items()}
    changed = {c: {lbl: out(c, lbl) != out("BASE", lbl) for lbl, _, _ in sig_members} for c in CELL_NAMES[1:]}
    for c in CELL_NAMES[1:]:
        changed[c]["TRUTH"] = g[c] != g["BASE"]
    want = {
        "D(h1|h2)": changed["D(h1|h2)"][h1] and not changed["D(h1|h2)"][h2] and not changed["D(h1|h2)"]["TRUTH"],
        "D(h2|h1)": changed["D(h2|h1)"][h2] and not changed["D(h2|h1)"][h1] and not changed["D(h2|h1)"]["TRUTH"],
        "PLACEBO": not any(changed["PLACEBO"].values()),
        "G-ONLY": changed["G-ONLY"]["TRUTH"] and not changed["G-ONLY"][h1] and not changed["G-ONLY"][h2],
    }
    errs += [f"cell {c} does not have its defining change signature" for c, ok in want.items() if not ok]
    family = {"value_delta": "number_delta", "weight_delta": "number_delta"}  # knapsack: "one number changed"
    kinds = {family.get(by[c].params["edit"]["kind"], by[c].params["edit"]["kind"]) for c in CELL_NAMES[1:]}
    if len(kinds) != 1:
        errs.append(f"edit types differ across cells: {kinds}")
    counts = {tokens.count(by[c].prompt) for c in CELL_NAMES[1:]}
    if len(counts) != 1:
        errs.append(f"edited items differ in token count: {sorted(counts)}")
    if domain == "COL":
        if len({t.graph.vertices for t in tasks.values()}) != 1:
            errs.append("listing or labels differ across the set")
    return errs
