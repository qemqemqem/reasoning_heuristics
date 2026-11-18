"""One call from responses to weight statements: fit every (model, condition, eval, domain).

    from reasoning_heuristics.identify.engine import fit_all
    results = fit_all(items, responses)          # {(model, condition, eval, domain): report}

Each report has the weights with 95% cluster-bootstrap intervals (tie groups merged; the
unexplained mass last), the slip rate and shape, the excluded responses per cell and category,
error agreement with its within-cell permutation lift, the weight lift over the permutation
baseline, and identifiability diagnostics (tie groups, members folded into q, items that
separate each pair of groups, data ties). Responses are joined to items on item_id with the
content hash checked (`records.join`).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

import numpy as np

from reasoning_heuristics.identify import agreement
from reasoning_heuristics.identify.likelihood import NEAR_MISS, TokenModel, UnitModel
from reasoning_heuristics.identify.mixture import fit
from reasoning_heuristics.identify.records import Response, fit_key, join
from reasoning_heuristics.identify.units import Unit, eval_name, is_answer_item


def separations(um: UnitModel) -> dict[str, dict[str, int]]:
    """Items on which each pair of column groups predicts differently (or only one is available)."""
    cols = um.columns
    sig = [[um.signature(i, g.members[0]) for i in range(len(um.items))] for g in cols]
    out: dict[str, dict[str, int]] = {}
    for a in range(len(cols)):
        row = {}
        for b in range(len(cols)):
            if a != b:
                row[cols[b].name] = sum(1 for x, y in zip(sig[a], sig[b]) if x != y)
        out[cols[a].name] = row
    return out


def design_rank(um: UnitModel) -> dict[str, Any] | None:
    """For units whose items are all on finite channels: the (item, value) x (groups + q) matrix of
    no-slip probabilities, its rank and sigma_min / sigma_max after scaling columns to unit norm
    (A/H §5.3 pre-registers >= 0.05), and the columns of the weakest direction. A rank below the
    number of columns means some weights are not identified by any amount of data on these items
    (e.g. q = 1/2 ALWAYS-SAT + 1/2 ALWAYS-UNSAT on a two-valued channel)."""
    from reasoning_heuristics.identify.spaces import FiniteSpace

    if not all(isinstance(im.space, FiniteSpace) for im in um.items):
        return None
    cols = um.columns
    rows = []
    for i, im in enumerate(um.items):
        V = im.space.values
        block = np.zeros((len(V), len(cols) + 1))
        for j, g in enumerate(cols):
            p = um.pred(i, g.members[0])
            if p.kind == "det":
                block[V.index(p.key), j] = 1.0
            elif p.kind == "dist":
                for k, v in p.dist.items():
                    block[V.index(k), j] += v
            elif p.kind in ("uniform",):
                block[:, j] = 1.0 / len(V)
        block[:, -1] = 1.0 / len(V)
        rows.append(block)
    M = np.vstack(rows)
    norms = np.linalg.norm(M, axis=0)
    M = M / np.where(norms > 0, norms, 1.0)
    _, s, vt = np.linalg.svd(M, full_matrices=False)
    tol = s.max() * 1e-9
    rank = int((s > tol).sum())
    weak = vt[-1]
    labels = [g.name for g in cols] + ["q"]
    involved = [labels[j] for j in np.argsort(-np.abs(weak)) if abs(weak[j]) > 0.1]
    return {"columns": len(labels), "rank": rank, "sigma_ratio": round(float(s.min() / s.max()), 4),
            "weakest_direction": involved[:8]}


def design_matrix(um: UnitModel, eps: float = 0.1, rho: float = 0.3, samples: int = 6,
                  rng: np.random.Generator | None = None) -> np.ndarray:
    """Rows: (item, outcome); columns: the unit's column groups, then q; entries P(outcome | component, item).

    Finite channels: every value, without slips (eps is held at 0 there). Witness channels: the
    answer space is too large to list, so the rows are the candidate answers plus `samples` draws
    from every component (slips at eps, rho), with the components' likelihoods at those points; a
    linear dependency among the full distributions holds on any such rows, and with enough draws
    an independent column shows up as full rank. Unavailable members are 0 on an item (the Luce
    renormalisation is ignored here)."""
    from reasoning_heuristics.identify.spaces import FiniteSpace, trunc_geom

    rng = rng or np.random.default_rng(0)
    cols = um.columns
    G = len(cols)
    g = trunc_geom(rho)
    rows = []
    for i, im in enumerate(um.items):
        if isinstance(im.space, FiniteSpace):
            V = im.space.values
            block = np.zeros((len(V), G + 1))
            for j, grp in enumerate(cols):
                p = um.pred(i, grp.members[0])
                if p.kind == "det":
                    block[V.index(p.key), j] = 1.0
                elif p.kind == "dist":
                    for k, v in p.dist.items():
                        block[V.index(k), j] += v
                elif p.kind == "uniform":
                    block[:, j] = 1.0 / len(V)
            block[:, G] = 1.0 / len(V)
            rows.append(block)
            continue
        ys = set(im.candidates)
        for grp in cols:
            if um.pred(i, grp.members[0]).available:
                ys.update(um.sample(i, grp.members[0], eps, rho, rng) for _ in range(samples))
        ys.update(um.sample_q(i, rng) for _ in range(samples))
        block = np.zeros((len(ys), G + 1))
        for r, y in enumerate(sorted(ys)):
            A, B0, C, Q, avail = um.row(i, y)
            block[r, :G] = np.where(avail, (1 - eps) * A + eps * (B0 + C @ g), 0.0)
            block[r, G] = Q
        # Scale every row by its largest entry: that leaves the null space unchanged and keeps the
        # tiny probabilities (q on a random colouring, ~1e-15) visible to the SVD.
        rows.append(block / np.maximum(block.max(1, keepdims=True), 1e-300))
    return np.vstack(rows)


_PIVOT_ORDER = {"q": 0, "dist": 1, "uniform": 2, "set": 3, "det": 4, "na": 5}


def identifiability(um: UnitModel, tol: float = 1e-7, rng: np.random.Generator | None = None, **kw: Any) -> dict[str, Any]:
    """Numerical rank and null space of `design_matrix`, generalising pairwise ties to linear
    dependencies (on a two-valued channel q = 1/2 ALWAYS-pos + 1/2 ALWAYS-neg, which no pairwise
    test can see).

    For k null directions, k columns are chosen as **pivots** (q first, then noise models, then
    procedures) and are *not identified*. Every other column c has an identified quantity
    theta_c = pi_c - sum_j R[j, c] pi_{pivot_j}: its weight plus the share of the pivots' mass the
    design cannot tell apart from it (e.g. pi_ALWAYS-SAT + 0.5 pi_0). `transform` maps
    (columns + q) weights to those quantities; with full rank it is the identity."""
    M = design_matrix(um, rng=rng, **kw)
    labels = [g.name for g in um.columns] + ["q"]
    C = M.shape[1]
    norms = np.linalg.norm(M, axis=0)
    norms = np.where(norms > 0, norms, 1.0)
    _, s, vt = np.linalg.svd(M / norms, full_matrices=False)
    rank = int((s > tol * s[0]).sum())
    U = vt[rank:].copy() if rank < C else np.zeros((0, C))  # null basis in column-scaled coordinates
    kinds = []
    for j, g in enumerate(um.columns):
        ks = {um.pred(i, g.members[0]).kind for i in range(len(um.items))} - {"na"}
        kinds.append(min(ks, key=lambda k: _PIVOT_ORDER[k]) if ks else "na")
    kinds.append("q")
    order = sorted(range(C), key=lambda c: (_PIVOT_ORDER[kinds[c]], -c))
    # Reduce the null basis (Gauss-Jordan in the scaled coordinates, where entries are O(1)), taking
    # pivots in preference order: q, then noise models, then procedures.
    pivots: list[int] = []
    piv_row: dict[int, int] = {}  # pivot column -> its row of the reduced null basis
    for c in order:
        if len(pivots) == len(U):
            break
        free = [j for j in range(len(U)) if j not in piv_row.values()]
        cand = [j for j in free if abs(U[j, c]) > 1e-3 * np.abs(U[j]).max()]
        if not cand:
            continue
        j = max(cand, key=lambda r: abs(U[r, c]))
        U[j] /= U[j, c]
        for r in range(len(U)):
            if r != j:
                U[r] -= U[r, c] * U[j]
        piv_row[c] = j
        pivots.append(c)
    # back to weight coordinates (M v = 0 for v = u / norms), scaled so v[pivot] = 1
    R = U / norms[None, :]
    for c, j in piv_row.items():
        R[j] /= R[j, c]
    R[np.abs(R) < 1e-4] = 0.0  # numerical residue (e.g. a 1e-7 probability that is 0 in all but name)
    transform, id_labels = [], []
    for c in range(C):
        if c in pivots:
            continue
        a = np.zeros(C)
        a[c] = 1.0
        terms = []
        for p, j in piv_row.items():
            if R[j, c] != 0:
                a[p] -= R[j, c]
                terms.append(f"{-R[j, c]:.3g} × {labels[p]}")
        transform.append(a)
        id_labels.append(labels[c] if not terms else f"{labels[c]} + " + " + ".join(terms))
    directions = []
    for p, j in piv_row.items():
        rhs = [f"{-R[j, c]:.3g} × {labels[c]}" for c in range(C) if c != p and R[j, c] != 0]
        directions.append(f"{labels[p]} = " + (" + ".join(rhs) if rhs else "0"))
    return {"columns": labels, "rank": rank, "deficiency": C - rank, "sigma_ratio": float(s[-1] / s[0]),
            "null_directions": directions, "not_identified": [labels[p] for p in pivots],
            "identified": id_labels, "transform": np.array(transform).reshape(len(transform), C)}


def diagnostics(um: UnitModel) -> dict[str, Any]:
    sep = separations(um)
    weakest = sorted(((min(v.values()) if v else 0, k, min(v, key=v.get) if v else None) for k, v in sep.items()))[:5]
    return {"groups": [g.members for g in um.columns], "folded_into_q": um.q_members,
            "n_items": len(um.items), "n_clusters": um.unit.n_clusters,
            "least_separated": [{"group": k, "nearest": n, "separating_items": s} for s, k, n in weakest],
            "design": design_rank(um)}


def fit_unit(um: UnitModel, responses: list[Response], n_boot: int = 200, seed: int = 0,
             token_model: TokenModel | None = None, declared_impossible: str = "exclude",
             n_perm: int = 100, ea_ties: str = "include") -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    obs, exc = um.observations(responses, token_model, declared_impossible)
    report: dict[str, Any] = {"unit": um.unit.name, "likelihood": um.model, "n_responses": len(responses),
                              "n_rows": len(obs), "excluded": exc.to_json(), "diagnostics": diagnostics(um)}
    if not obs:
        report["fit"] = None
        return report
    T = um.tensors(obs, token_model)
    res = fit(T, n_boot=n_boot, rng=rng)
    report["fit"] = res.to_json()
    report["fit"]["q_members"] = um.q_members
    ident = identifiability(um, rng=rng)
    report["identifiability"] = {k: v for k, v in ident.items() if k != "transform"}
    if ident["deficiency"]:
        # weights the design cannot see are not numbers; their identified combinations are
        names = [g.name for g in um.columns] + [res.labels[-1]]
        for p in ident["not_identified"]:
            report["fit"]["weights"][names[ident["columns"].index(p)]] = "not identified"
        Tid = ident["transform"]
        est = Tid @ res.pi
        if res.boot is not None:
            tb = res.boot @ Tid.T
            lo, hi = np.percentile(tb, 2.5, 0), np.percentile(tb, 97.5, 0)
        else:
            lo = hi = np.full(len(est), np.nan)
        report["fit"]["identified"] = {l: {"est": round(float(e), 4), "lo": round(float(a), 4), "hi": round(float(b), 4)}
                                       for l, e, a, b in zip(ident["identified"], est, lo, hi)}
    ea, exch = agreement.ea_lift(um, obs, n_perm=n_perm, rng=rng, ties=ea_ties, stat="ea")
    co, _ = agreement.ea_lift(um, obs, n_perm=n_perm, rng=rng, ties=ea_ties, stat="co_error")
    report["error_agreement"] = {"ties": ea_ties, "exchangeable": round(exch, 3),
                                 "ea": {k: vars(v) for k, v in ea.items()},
                                 "co_error": {k: vars(v) for k, v in co.items()}}
    if n_perm:
        lifts, exch_w = agreement.permutation_weights(um, obs, res.pi, n_perm=n_perm, rng=rng)
        report["weight_lift"] = {"exchangeable": round(exch_w, 3), "by_group": {k: vars(v) for k, v in lifts.items()}}
    return report


def fit_all(items: Iterable[dict[str, Any]], responses: Iterable[Response], model: str = NEAR_MISS,
            **kw: Any) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    items = [it for it in items if is_answer_item(it)]
    pairs = join(list(responses), items)
    by_key: dict[tuple, list[Response]] = defaultdict(list)
    for r, it in pairs:
        by_key[fit_key(r, it)].append(r)
    units: dict[tuple[str, str], Unit] = {}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for it in items:
        groups[(eval_name(it), it["domain"])].append(it)
    out = {}
    models: dict[tuple[str, str], UnitModel] = {}
    for key, rs in sorted(by_key.items()):
        ud = (key[2], key[3])
        if ud not in units:
            units[ud] = Unit(ud[0], ud[1], groups[ud])
            models[ud] = UnitModel(units[ud], model)
        rep = fit_unit(models[ud], rs, **kw)
        rep["model"], rep["condition"] = key[0], key[1]
        out[key] = rep
    return out
