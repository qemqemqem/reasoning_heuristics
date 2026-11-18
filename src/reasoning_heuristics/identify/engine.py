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
