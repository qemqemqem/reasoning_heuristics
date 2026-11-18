"""The mixture fit: P(y | x) = sum_h pi_h P(y | h, x) + pi_0 q(y | x), per (model, condition, eval, domain).

**Estimator.** Maximum likelihood by EM over the weights pi (one per tie group, plus pi_0 for q),
the slip rate eps (capped at `EPS_MAX`, so slips cannot absorb everything; A/H §5.3) and, under the
near-miss model, the slip shape rho (a grid M-step). Members unavailable on an item (no
prediction on its channel) drop out there and the other weights are renormalised (a Luce choice
model: pi_h(x) = pi_h 1[h available on x] / sum over the available members); the M-step is
Hunter's (2004) MM update, which reduces to the usual EM update when every member is available.
Many bootstrap replicates are fitted at once as a batch.

**Intervals respect clustering.** Items that share a base or a counterfactual set are not
independent, so the 95% intervals are percentile intervals of a cluster bootstrap: clusters
(`units.clusters`) are resampled with replacement, the whole model (pi, eps, rho) is refitted on
each replicate (warm-started at the point estimate).

**Feature-dependent weights** (family I, strategy selection): `fit_softmax` fits
pi_h(x) = softmax_h(beta_h . phi(x)) over the available members and q (q is the reference, beta_0 = 0),
with a small ridge on beta, by L-BFGS on the marginal likelihood; the constant model is the special
case phi = 1. Its bootstrap refits each replicate in turn.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.optimize import minimize

from reasoning_heuristics.identify.likelihood import Tensors
from reasoning_heuristics.identify.spaces import DMAX, trunc_geom

EPS_MAX = 0.5
RHO_GRID = np.round(np.linspace(0.02, 0.9, 45), 4)
TINY = 1e-300


@dataclass
class EMResult:
    pi: np.ndarray  # (B, G + 1); last column is q
    eps: np.ndarray  # (B,)
    rho: np.ndarray  # (B,)
    loglik: np.ndarray  # (B,)
    iters: int
    converged: np.ndarray  # (B,)


def _mixture_terms(T: Tensors, pi: np.ndarray, eps: np.ndarray, rho: np.ndarray):
    """Per-replicate likelihood pieces: L (B,N,G), S (slip part), num (B,N,G), numq (B,N), tot, Savail."""
    G = T.A.shape[1]
    if T.rho_free:
        S = np.broadcast_to(T.B0[None], (len(eps),) + T.B0.shape)
    else:
        g = trunc_geom(rho)  # (B, D+1)
        S = T.B0[None] + np.einsum("ngd,bd->bng", T.C, g)
    L = (1 - eps)[:, None, None] * T.A[None] + eps[:, None, None] * S
    w = pi[:, None, :G] * T.avail[None]
    num = w * L
    numq = pi[:, None, G] * T.Q[None]
    tot = num.sum(-1) + numq
    savail = w.sum(-1) + pi[:, None, G]
    return L, S, num, numq, tot, savail


def em(T: Tensors, W: np.ndarray | None = None, pi0: np.ndarray | None = None, eps0: Any = 0.1, rho0: Any = 0.3,
       fix_eps: float | None = None, fix_rho: float | None = None, eps_max: float = EPS_MAX,
       max_iter: int = 5000, tol: float = 1e-8) -> EMResult:
    """EM for (pi, eps, rho), batched over the rows of W (bootstrap weights; default one all-ones row).

    tol is the largest log-likelihood gain per unit weight at which a replicate counts as converged."""
    N, G = T.A.shape
    if fix_eps is None and not T.slip_identified:
        fix_eps = 0.0
    W = np.ones((1, N)) if W is None else np.asarray(W, dtype=float)
    B = W.shape[0]
    if pi0 is None:
        pi = np.full((B, G + 1), 1.0 / (G + 1))
    else:
        pi = np.array(np.broadcast_to(pi0, (B, G + 1)), dtype=float)
    eps = np.full(B, float(fix_eps)) if fix_eps is not None else np.array(np.broadcast_to(np.asarray(eps0, dtype=float), (B,)))
    rho = np.array(np.broadcast_to(np.asarray(fix_rho if fix_rho is not None else rho0, dtype=float), (B,)))
    slip_cols = T.slips.astype(float)
    wsum = W.sum(1)
    prev = np.full(B, -np.inf)
    converged = np.zeros(B, dtype=bool)
    log_g_grid = np.log(np.maximum(trunc_geom(RHO_GRID), TINY))  # (grid, D+1)
    it = 0
    for it in range(1, max_iter + 1):
        L, S, num, numq, tot, savail = _mixture_terms(T, pi, eps, rho)
        tot_safe = np.maximum(tot, TINY)
        ll = (W * (np.log(tot_safe) - np.log(savail) + T.log_scale[None])).sum(1)
        R = num / tot_safe[..., None]
        Rq = numq / tot_safe
        # weights: Luce MM step
        numer = np.einsum("bn,bng->bg", W, R)
        numer_q = (W * Rq).sum(1)
        Wd = W / savail
        denom = Wd @ T.avail.astype(float)
        denom_q = Wd.sum(1)
        new = np.empty_like(pi)
        with np.errstate(invalid="ignore", divide="ignore"):
            new[:, :G] = np.where(denom > 0, numer / np.maximum(denom, TINY), pi[:, :G])
            new[:, G] = numer_q / np.maximum(denom_q, TINY)
        new = np.maximum(new, 0.0)
        new /= new.sum(1, keepdims=True)
        # slip rate
        if fix_eps is None:
            with np.errstate(invalid="ignore", divide="ignore"):
                share = np.where(L > 0, eps[:, None, None] * S / np.maximum(L, TINY), 0.0)
            Rs = R * slip_cols[None, None, :]
            top = np.einsum("bn,bng->b", W, Rs * share)
            bot = np.einsum("bn,bng->b", W, Rs)
            eps = np.where(bot > 0, np.minimum(top / np.maximum(bot, TINY), eps_max), eps)
        # slip shape
        if fix_rho is None and not T.rho_free:
            g = trunc_geom(rho)
            with np.errstate(invalid="ignore", divide="ignore"):
                inv_L = np.where(L > 0, 1.0 / np.maximum(L, TINY), 0.0)
            # expected slip counts by distance: sum_n W R eps C_ngd g_bd / L
            Ed = np.einsum("bn,bng,ngd->bd", W, R * inv_L * slip_cols[None, None, :], T.C) * g * eps[:, None]
            if Ed.sum() > 0:
                score = Ed @ log_g_grid.T  # (B, grid)
                has = Ed.sum(1) > 0
                rho = np.where(has, RHO_GRID[np.argmax(score, 1)], rho)
        pi = new
        gain = (ll - prev) / wsum
        converged = np.abs(gain) < tol
        prev = ll
        if converged.all():
            break
    L, S, num, numq, tot, savail = _mixture_terms(T, pi, eps, rho)
    ll = (W * (np.log(np.maximum(tot, TINY)) - np.log(savail) + T.log_scale[None])).sum(1)
    return EMResult(pi, eps, rho, ll, it, converged)


def cluster_bootstrap(cluster: np.ndarray, n_boot: int, rng: np.random.Generator) -> np.ndarray:
    """(n_boot, N) row weights: each replicate resamples the clusters with replacement."""
    ids, inv = np.unique(cluster, return_inverse=True)
    k = len(ids)
    draws = rng.integers(k, size=(n_boot, k))
    counts = np.stack([np.bincount(d, minlength=k) for d in draws])  # (B, k)
    return counts[:, inv].astype(float)


@dataclass
class FitResult:
    labels: list[str]  # column groups, then the unexplained mass
    pi: np.ndarray  # (G + 1,)
    lo: np.ndarray
    hi: np.ndarray
    eps: float
    eps_ci: tuple[float, float]
    rho: float
    rho_ci: tuple[float, float]
    loglik: float
    n_rows: int
    n_clusters: int
    boot: np.ndarray | None = field(default=None, repr=False)  # (B, G + 1)
    iters: int = 0
    converged: bool = True
    extra: dict[str, Any] = field(default_factory=dict)

    def weight(self, label: str) -> float:
        return float(self.pi[self.labels.index(label)])

    def to_json(self) -> dict[str, Any]:
        return {"weights": {l: {"pi": round(float(p), 4), "lo": round(float(a), 4), "hi": round(float(b), 4)}
                            for l, p, a, b in zip(self.labels, self.pi, self.lo, self.hi)},
                "eps": round(self.eps, 4), "eps_ci": [round(x, 4) for x in self.eps_ci],
                "rho": round(self.rho, 4), "rho_ci": [round(x, 4) for x in self.rho_ci],
                "loglik": round(self.loglik, 3), "n_rows": self.n_rows, "n_clusters": self.n_clusters,
                "iters": self.iters, "converged": self.converged, **self.extra}


UNEXPLAINED = "unexplained (q)"


def fit(T: Tensors, n_boot: int = 200, rng: np.random.Generator | None = None, chunk: int = 50,
        fix_eps: float | None = None, fix_rho: float | None = None, max_iter: int = 5000, tol: float = 1e-8,
        q_label: str = UNEXPLAINED) -> FitResult:
    """Point estimate plus cluster-bootstrap percentile intervals."""
    rng = rng or np.random.default_rng(0)
    if fix_eps is None and not T.slip_identified:
        fix_eps = 0.0
    point = em(T, fix_eps=fix_eps, fix_rho=fix_rho, max_iter=max_iter, tol=tol)
    pi_hat, eps_hat, rho_hat = point.pi[0], float(point.eps[0]), float(point.rho[0])
    labels = list(T.labels) + [q_label]
    if n_boot <= 0:
        z = np.full(len(labels), np.nan)
        return FitResult(labels, pi_hat, z, z, eps_hat, (np.nan, np.nan), rho_hat, (np.nan, np.nan),
                         float(point.loglik[0]), T.n, len(np.unique(T.cluster)), None, point.iters, bool(point.converged[0]))
    Wall = cluster_bootstrap(T.cluster, n_boot, rng)
    # Each replicate starts halfway between the point estimate and a random Dirichlet(1) draw: in
    # identified directions EM converges to the replicate's own MLE either way, while along a flat
    # ridge (members the data cannot separate) the split stays wherever it starts, so the interval
    # shows the ridge instead of the point estimate's arbitrary split.
    starts = 0.5 * pi_hat[None, :] + 0.5 * rng.dirichlet(np.ones(len(pi_hat)), size=n_boot)
    pis, epss, rhos = [], [], []
    for start in range(0, n_boot, chunk):
        Wb = Wall[start:start + chunk]
        r = em(T, Wb, pi0=starts[start:start + chunk], eps0=eps_hat, rho0=rho_hat, fix_eps=fix_eps, fix_rho=fix_rho,
               max_iter=max_iter, tol=tol)
        pis.append(r.pi)
        epss.append(r.eps)
        rhos.append(r.rho)
    boot = np.concatenate(pis)
    eb, rb = np.concatenate(epss), np.concatenate(rhos)
    lo, hi = np.percentile(boot, 2.5, 0), np.percentile(boot, 97.5, 0)
    return FitResult(labels, pi_hat, lo, hi, eps_hat, (float(np.percentile(eb, 2.5)), float(np.percentile(eb, 97.5))),
                     rho_hat, (float(np.percentile(rb, 2.5)), float(np.percentile(rb, 97.5))), float(point.loglik[0]),
                     T.n, len(np.unique(T.cluster)), boot, point.iters, bool(point.converged[0]),
                     {"data_ties": data_ties(T), "slip_identified": T.slip_identified})


def data_ties(T: Tensors) -> list[list[str]]:
    """Groups of columns with identical likelihood on every observed row: these data cannot split
    their weight, so only their sum is estimated (their split is wherever EM started)."""
    N, G = T.A.shape
    sig: dict[bytes, list[str]] = {}
    for g in range(G):
        key = np.concatenate([T.A[:, g], T.B0[:, g], T.C[:, g].ravel(), T.avail[:, g].astype(float)]).round(12).tobytes()
        sig.setdefault(key, []).append(T.labels[g])
    return [v for v in sig.values() if len(v) > 1]


# =============================================================================================
# Feature-dependent weights
# =============================================================================================


def _rho_of(v: float) -> float:
    return 0.01 + 0.94 / (1 + np.exp(-v))


@dataclass
class SoftmaxFit:
    beta: np.ndarray  # (G, F); q is the reference (beta = 0)
    eps: float
    rho: float
    loglik: float
    success: bool

    def weights(self, X: np.ndarray, avail: np.ndarray | None = None) -> np.ndarray:
        """(rows, G + 1) weights at feature rows X; with avail, renormalised over available members."""
        eta = np.asarray(X, dtype=float) @ self.beta.T
        e = np.exp(eta - np.maximum(eta.max(1, keepdims=True), 0))
        eq = np.exp(-np.maximum(eta.max(1, keepdims=True), 0))
        if avail is not None:
            e = e * avail
        tot = e.sum(1, keepdims=True) + eq
        return np.concatenate([e / tot, eq / tot], 1)


def fit_softmax(T: Tensors, X: np.ndarray, w: np.ndarray | None = None, ridge: float = 1e-3,
                init: SoftmaxFit | None = None, fix_eps: float | None = None, fix_rho: float | None = None,
                eps_max: float = EPS_MAX, maxiter: int = 2000) -> SoftmaxFit:
    """pi_h(x) = softmax over available members and q of beta_h . X[x] (q's beta = 0), by L-BFGS."""
    X = np.asarray(X, dtype=float)
    N, G = T.A.shape
    F = X.shape[1]
    if fix_eps is None and not T.slip_identified:
        fix_eps = 0.0
    w = np.ones(N) if w is None else np.asarray(w, dtype=float)
    avail = T.avail.astype(float)
    slip_cols = T.slips.astype(float)
    free_eps, free_rho = fix_eps is None, (fix_rho is None and not T.rho_free)
    d = np.arange(DMAX + 1)

    def unpack(theta):
        beta = theta[:G * F].reshape(G, F)
        j = G * F
        if free_eps:
            u = theta[j]
            j += 1
            eps = eps_max / (1 + np.exp(-u))
        else:
            u, eps = None, fix_eps
        if free_rho:
            v = theta[j]
            rho = _rho_of(v)
        else:
            v, rho = None, (fix_rho if fix_rho is not None else 0.3)
        return beta, u, eps, v, rho

    def objective(theta):
        beta, u, eps, v, rho = unpack(theta)
        eta = X @ beta.T  # (N, G)
        m = np.maximum(eta.max(1, keepdims=True), 0.0)
        e = np.exp(eta - m) * avail
        eq = np.exp(-m)[:, 0]
        Z = e.sum(1) + eq
        p = e / Z[:, None]
        pq = eq / Z
        if T.rho_free:
            S = T.B0
            dS = None
        else:
            g = trunc_geom(rho)
            S = T.B0 + T.C @ g
            # d g_d / d rho
            with np.errstate(divide="ignore", invalid="ignore"):
                dlog = np.where(d >= 1, -1 / (1 - rho) + (d - 1) / rho + DMAX * rho ** (DMAX - 1) / (1 - rho ** DMAX), 0.0)
            dS = T.C @ (g * dlog)
        L = (1 - eps) * T.A + eps * S
        mix = (p * L).sum(1) + pq * T.Q
        mix = np.maximum(mix, TINY)
        ll = float((w * np.log(mix)).sum()) - ridge * float((beta ** 2).sum())
        r = p * L / mix[:, None]
        grad_beta = ((w[:, None] * (r - p)).T @ X) - 2 * ridge * beta
        grads = [grad_beta.ravel()]
        if free_eps:
            dl_deps = (w * ((p * (S - T.A) * slip_cols).sum(1) / mix)).sum()
            sig = 1 / (1 + np.exp(-u))
            grads.append(np.array([dl_deps * eps_max * sig * (1 - sig)]))
        if free_rho:
            dl_drho = (w * ((p * eps * dS * slip_cols).sum(1) / mix)).sum()
            sig = 1 / (1 + np.exp(-v))
            grads.append(np.array([dl_drho * 0.94 * sig * (1 - sig)]))
        return -ll, -np.concatenate(grads)

    theta0 = [np.zeros(G * F) if init is None else init.beta.ravel()]
    if free_eps:
        e0 = 0.1 if init is None else min(max(init.eps, 1e-4), eps_max - 1e-4)
        theta0.append(np.array([np.log(e0 / (eps_max - e0))]))
    if free_rho:
        r0 = 0.3 if init is None else min(max(init.rho, 0.0101), 0.9499)
        theta0.append(np.array([np.log((r0 - 0.01) / (0.95 - r0))]))
    theta0 = np.concatenate(theta0)
    res = minimize(objective, theta0, jac=True, method="L-BFGS-B", options={"maxiter": maxiter})
    beta, u, eps, v, rho = unpack(res.x)
    return SoftmaxFit(beta, float(eps), float(rho), float(-res.fun), bool(res.success))


def fit_features(T: Tensors, X: np.ndarray, points: np.ndarray, n_boot: int = 100, rng: np.random.Generator | None = None,
                 ridge: float = 1e-3, q_label: str = UNEXPLAINED) -> dict[str, Any]:
    """Feature-dependent fit with cluster-bootstrap intervals for the weights at feature rows `points`."""
    rng = rng or np.random.default_rng(0)
    point = fit_softmax(T, X, ridge=ridge)
    pts = np.asarray(points, dtype=float)
    est = point.weights(pts)
    boots = []
    if n_boot > 0:
        Wall = cluster_bootstrap(T.cluster, n_boot, rng)
        for b in range(n_boot):
            fb = fit_softmax(T, X, w=Wall[b], ridge=ridge, init=point)
            boots.append(fb.weights(pts))
    boots = np.array(boots) if boots else None
    labels = list(T.labels) + [q_label]
    out = {"labels": labels, "points": pts.tolist(), "pi": est, "beta": point.beta, "eps": point.eps, "rho": point.rho,
           "loglik": point.loglik, "success": point.success}
    if boots is not None:
        out["lo"] = np.percentile(boots, 2.5, 0)
        out["hi"] = np.percentile(boots, 97.5, 0)
        out["boot"] = boots
    return out
