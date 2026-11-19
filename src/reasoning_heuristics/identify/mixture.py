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

**Noise-model options** (`noise.py`, docs/NOISE_MODEL.md): when the tensors carry a non-default
`NoiseModel`, `em` and `fit` hand over to `_GeneralStepper`, the same EM with a per-member slip
rate, a free kernel over the tensors' cells, and the strata q's probabilities and special-token
mass as further M-steps (all closed form). The default model never reaches it, so its results are
unchanged.

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
from reasoning_heuristics.identify.noise import NoiseModel, NoiseParams
from reasoning_heuristics.identify.spaces import AD_CELLS, DMAX, trunc_geom

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
    state: dict[str, np.ndarray] | None = None  # non-default noise models: every parameter, batched


def _mixture_terms(T: Tensors, pi: np.ndarray, eps: np.ndarray, rho: np.ndarray, rho_free: bool):
    """Per-replicate likelihood pieces: L (B,N,G), S (slip part), num (B,N,G), numq (B,N), tot, Savail."""
    G = T.A.shape[1]
    if rho_free:
        S = T.B0[None]
    else:
        g = trunc_geom(rho)  # (B, D+1)
        S = T.B0[None] + np.einsum("ngd,bd->bng", T.C, g)
    L = (1 - eps)[:, None, None] * T.A[None] + eps[:, None, None] * S
    w = pi[:, None, :G] * T.avail[None]
    num = w * L
    numq = pi[:, None, G] * T.Q[None]
    tot = num.sum(-1) + numq
    savail = np.maximum(w.sum(-1) + pi[:, None, G], TINY)
    return L, S, num, numq, tot, savail


class _Stepper:
    """One EM (MM) update of (pi, eps, rho) for a batch of replicates; returns the log-likelihood at its input."""

    def __init__(self, T: Tensors, W: np.ndarray, fix_eps: float | None, fix_rho: float | None, eps_max: float):
        self.T, self.W = T, W
        self.fix_eps, self.fix_rho, self.eps_max = fix_eps, fix_rho, eps_max
        self.rho_free = T.rho_free
        self.slip_cols = T.slips.astype(float)
        self.avail = T.avail.astype(float)
        self.log_g_grid = np.log(np.maximum(trunc_geom(RHO_GRID), TINY))  # (grid, D+1)
        self.G = T.A.shape[1]

    def loglik(self, pi: np.ndarray, eps: np.ndarray, rho: np.ndarray) -> np.ndarray:
        _, _, _, _, tot, savail = _mixture_terms(self.T, pi, eps, rho, self.rho_free)
        return (self.W * (np.log(np.maximum(tot, TINY)) - np.log(savail) + self.T.log_scale[None])).sum(1)

    def __call__(self, pi: np.ndarray, eps: np.ndarray, rho: np.ndarray):
        T, W, G = self.T, self.W, self.G
        L, S, num, numq, tot, savail = _mixture_terms(T, pi, eps, rho, self.rho_free)
        tot_safe = np.maximum(tot, TINY)
        ll = (W * (np.log(tot_safe) - np.log(savail) + T.log_scale[None])).sum(1)
        R = num / tot_safe[..., None]
        Rq = numq / tot_safe
        # weights: Luce MM step
        numer = np.einsum("bn,bng->bg", W, R)
        numer_q = (W * Rq).sum(1)
        Wd = W / savail
        denom = Wd @ self.avail
        denom_q = Wd.sum(1)
        new = np.empty_like(pi)
        with np.errstate(invalid="ignore", divide="ignore"):
            new[:, :G] = np.where(denom > 0, numer / np.maximum(denom, TINY), pi[:, :G])
            new[:, G] = numer_q / np.maximum(denom_q, TINY)
        new = np.maximum(new, 0.0)
        new /= new.sum(1, keepdims=True)
        eps_new, rho_new = eps, rho
        if self.fix_eps is None:  # slip rate
            with np.errstate(invalid="ignore", divide="ignore"):
                share = np.where(L > 0, eps[:, None, None] * S / np.maximum(L, TINY), 0.0)
            Rs = R * self.slip_cols[None, None, :]
            top = np.einsum("bn,bng->b", W, Rs * share)
            bot = np.einsum("bn,bng->b", W, Rs)
            eps_new = np.where(bot > 0, np.minimum(top / np.maximum(bot, TINY), self.eps_max), eps)
        if self.fix_rho is None and not self.rho_free:  # slip shape: expected slips by distance, grid M-step
            g = trunc_geom(rho)
            with np.errstate(invalid="ignore", divide="ignore"):
                inv_L = np.where(L > 0, 1.0 / np.maximum(L, TINY), 0.0)
            Ed = np.einsum("bn,bng,ngd->bd", W, R * inv_L * self.slip_cols[None, None, :], T.C) * g * eps[:, None]
            has = Ed.sum(1) > 0
            if has.any():
                rho_new = np.where(has, RHO_GRID[np.argmax(Ed @ self.log_g_grid.T, 1)], rho)
        return new, eps_new, rho_new, ll


def em(T: Tensors, W: np.ndarray | None = None, pi0: np.ndarray | None = None, eps0: Any = 0.1, rho0: Any = 0.3,
       fix_eps: float | None = None, fix_rho: float | None = None, eps_max: float = EPS_MAX,
       max_iter: int = 3000, tol: float = 1e-8, accelerate: bool = True) -> EMResult:
    """EM for (pi, eps, rho), batched over the rows of W (bootstrap weights; default one all-ones row).

    With `accelerate`, SQUAREM (Varadhan & Roland 2008): two EM steps give a direction, the step is
    extrapolated, projected back onto the simplex, stabilised with one more EM step, and kept only
    when it does not lower the likelihood (otherwise the plain second EM step is kept). tol is the
    largest log-likelihood gain per unit weight at which a replicate counts as converged; max_iter
    counts EM steps."""
    N, G = T.A.shape
    if fix_eps is None and not T.slip_identified:
        fix_eps = 0.0
    if not T.noise.is_default:
        if fix_rho is not None:
            raise ValueError("fix_rho applies to the default (geometric) noise model only")
        return em_general(T, W, pi0, eps0=eps0, fix_eps=fix_eps, max_iter=max_iter, tol=tol, accelerate=accelerate)
    W = np.ones((1, N)) if W is None else np.asarray(W, dtype=float)
    B = W.shape[0]
    if pi0 is None:
        pi = np.full((B, G + 1), 1.0 / (G + 1))
    else:
        pi = np.array(np.broadcast_to(pi0, (B, G + 1)), dtype=float)
    eps = np.full(B, float(fix_eps)) if fix_eps is not None else np.array(np.broadcast_to(np.asarray(eps0, dtype=float), (B,)))
    rho = np.array(np.broadcast_to(np.asarray(fix_rho if fix_rho is not None else rho0, dtype=float), (B,)))
    step = _Stepper(T, W, fix_eps, fix_rho, eps_max)
    wsum = W.sum(1)
    prev = np.full(B, -np.inf)
    converged = np.zeros(B, dtype=bool)
    steps = 0
    while steps < max_iter:
        p1, e1, r1, ll0 = step(pi, eps, rho)
        steps += 1
        converged = np.abs(ll0 - prev) / wsum < tol
        prev = ll0
        if converged.all():
            break
        if not accelerate:
            pi, eps, rho = p1, e1, r1
            continue
        p2, e2, r2, ll1 = step(p1, e1, r1)
        rp, vp = p1 - pi, p2 - 2 * p1 + pi
        re, ve = e1 - eps, e2 - 2 * e1 + eps
        nr = np.sqrt((rp ** 2).sum(1) + re ** 2)
        nv = np.sqrt((vp ** 2).sum(1) + ve ** 2)
        with np.errstate(invalid="ignore", divide="ignore"):
            alpha = np.where(nv > 0, -nr / np.maximum(nv, TINY), -1.0)
        alpha = np.clip(alpha, -64.0, -1.0)
        # project back onto the simplex with a floor: an exact zero could leave an item with no
        # available weight at all (and EM can never revive a zero)
        pe = np.maximum(pi - 2 * alpha[:, None] * rp + alpha[:, None] ** 2 * vp, 1e-12)
        pe /= pe.sum(1, keepdims=True)
        ee = np.clip(eps - 2 * alpha * re + alpha ** 2 * ve, 0.0, eps_max) if fix_eps is None else eps
        p3, e3, r3, ll_ext = step(pe, ee, r2)
        steps += 2
        ok = ll_ext >= ll1
        pi = np.where(ok[:, None], p3, p2)
        eps = np.where(ok, e3, e2)
        rho = np.where(ok, r3, r2)
    ll = step.loglik(pi, eps, rho)
    return EMResult(pi, eps, rho, ll, steps, converged)


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
    jack: np.ndarray | None = field(default=None, repr=False)  # (clusters, G + 1) leave-one-cluster-out fits

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
        fix_eps: float | None = None, fix_rho: float | None = None, max_iter: int = 3000, tol: float = 1e-8,
        q_label: str = UNEXPLAINED, jackknife: bool = False) -> FitResult:
    """Point estimate plus cluster-bootstrap percentile intervals. With `jackknife`, also the
    leave-one-cluster-out fits that BCa intervals need (`bca_interval`)."""
    rng = rng or np.random.default_rng(0)
    if fix_eps is None and not T.slip_identified:
        fix_eps = 0.0
    if not T.noise.is_default:
        return _fit_general(T, n_boot, rng, chunk, fix_eps, max_iter, tol, q_label, jackknife)
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
               max_iter=min(max_iter, 1500), tol=tol)
        pis.append(r.pi)
        epss.append(r.eps)
        rhos.append(r.rho)
    boot = np.concatenate(pis)
    eb, rb = np.concatenate(epss), np.concatenate(rhos)
    lo, hi = np.percentile(boot, 2.5, 0), np.percentile(boot, 97.5, 0)
    jack = None
    if jackknife:
        ids, inv = np.unique(T.cluster, return_inverse=True)
        Wj = np.ones((len(ids), T.n))
        Wj[inv, np.arange(T.n)] = 0.0  # replicate k drops cluster k
        js = []
        for start in range(0, len(ids), chunk):
            r = em(T, Wj[start:start + chunk], pi0=pi_hat, eps0=eps_hat, rho0=rho_hat, fix_eps=fix_eps, fix_rho=fix_rho,
                   max_iter=min(max_iter, 1500), tol=tol)
            js.append(r.pi)
        jack = np.concatenate(js)
    return FitResult(labels, pi_hat, lo, hi, eps_hat, (float(np.percentile(eb, 2.5)), float(np.percentile(eb, 97.5))),
                     rho_hat, (float(np.percentile(rb, 2.5)), float(np.percentile(rb, 97.5))), float(point.loglik[0]),
                     T.n, len(np.unique(T.cluster)), boot, point.iters, bool(point.converged[0]),
                     {"data_ties": data_ties(T), "slip_identified": T.slip_identified}, jack)


def bca_interval(boot: np.ndarray, est: np.ndarray, jack: np.ndarray, alpha: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    """Bias-corrected and accelerated bootstrap interval (Efron 1987), per column: the bias correction
    z0 from the share of bootstrap values below the estimate, the acceleration from the
    leave-one-cluster-out jackknife. Works on any linear combination of weights (pass transformed
    boot / est / jack). Columns with no bootstrap spread get the degenerate interval [est, est]."""
    from scipy.stats import norm

    boot, est, jack = np.asarray(boot), np.asarray(est), np.asarray(jack)
    B = boot.shape[0]
    frac = ((boot < est[None, :]).sum(0) + 0.5 * (boot == est[None, :]).sum(0)) / B
    z0 = norm.ppf(np.clip(frac, 0.5 / B, 1 - 0.5 / B))
    d = jack.mean(0)[None, :] - jack
    den = 6.0 * np.power((d ** 2).sum(0), 1.5)
    a = np.where(den > 0, (d ** 3).sum(0) / np.where(den > 0, den, 1.0), 0.0)
    lo, hi = np.empty(boot.shape[1]), np.empty(boot.shape[1])
    for j in range(boot.shape[1]):
        qs = []
        for z in (norm.ppf(alpha / 2), norm.ppf(1 - alpha / 2)):
            adj = norm.cdf(z0[j] + (z0[j] + z) / (1 - a[j] * (z0[j] + z)))
            qs.append(float(np.quantile(boot[:, j], np.clip(adj, 0.0, 1.0))))
        lo[j], hi[j] = qs
    return lo, hi


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
# Non-default noise models (noise.py)
# =============================================================================================


def default_kernel(cells: str, rho: float = 0.3, reach: int = DMAX) -> np.ndarray:
    """The geometric kernel g(rho) over a noise model's cells (adds-drops: g_d split evenly over the
    d + 1 cells with adds + drops = d), cut at `reach` and renormalised."""
    g = trunc_geom(rho)
    if cells != "distance":
        g = np.array([0.0] + [g[a + r] / (a + r + 1) for a, r in AD_CELLS[1:]])
    dist = np.arange(DMAX + 1) if cells == "distance" else np.array([a + r for a, r in AD_CELLS])
    g = np.where(dist <= reach, g, 0.0)
    return g / g.sum()


class _GeneralStepper:
    """One EM (MM) update of every parameter of a non-default noise model, batched over replicates.

    State (each batched over B): pi (B, G + 1); eps (B, G) per member or (B, 1) shared; g (B, K) the
    kernel over the tensors' cells (geometric: a grid M-step on rho as in the default; free and swap:
    expected slips per cell, normalised); P (B, S) the strata q's probabilities and tau (B,) its
    special-token mass (closed-form M-steps: q's responsibility per stratum, normalised within each
    group, and q's responsibility on special tokens over its responsibility on rows whose space has
    them)."""

    def __init__(self, T: Tensors, W: np.ndarray, fix_eps: float | None):
        self.T, self.W = T, W
        self.noise: NoiseModel = T.noise
        self.fix_eps = fix_eps
        self.eps_max = self.noise.eps_max
        self.G = T.A.shape[1]
        self.slip_cols = T.slips.astype(float)
        self.avail = T.avail.astype(float)
        self.log_g_grid = np.log(np.maximum(trunc_geom(RHO_GRID), TINY))
        self.qs = T.qs
        if self.qs is not None:
            q = self.qs
            self.structured = q.row >= 0
            self.row_idx = np.where(self.structured, q.row, 0)
            S = len(q.p0)
            self.onehot = np.zeros((T.n, S))
            self.onehot[np.arange(T.n)[self.structured], q.row[self.structured]] = 1.0
            ng = int(q.group.max()) + 1 if S else 0
            self.group_mat = np.zeros((S, ng))
            self.group_mat[np.arange(S), q.group] = 1.0

    def init(self, B: int, pi0: np.ndarray | None, eps0: Any) -> dict[str, np.ndarray]:
        G = self.G
        pi = np.full((B, G + 1), 1.0 / (G + 1)) if pi0 is None else np.array(np.broadcast_to(pi0, (B, G + 1)), dtype=float)
        Ge = G if self.noise.eps == "member" else 1
        eps = np.full((B, Ge), float(self.fix_eps if self.fix_eps is not None else np.mean(eps0)))
        g = np.tile(default_kernel(self.noise.cells, reach=self.T.reach), (B, 1))
        st = {"pi": pi, "eps": eps, "g": g, "rho": np.full(B, 0.3)}
        if self.qs is not None:
            st["P"] = np.tile(self.qs.p0, (B, 1))
            st["tau"] = np.full(B, self.qs.tau0)
        return st

    def q_rows(self, st: dict[str, np.ndarray]) -> np.ndarray:
        """(B, N) q at the state, on the tensors' row scale."""
        T = self.T
        if self.qs is None:
            return np.broadcast_to(T.Q[None], (st["pi"].shape[0], T.n))
        q = self.qs
        tau = st["tau"][:, None]
        with np.errstate(divide="ignore"):
            logP = np.log(np.maximum(st["P"], 0.0))
            log_tau, log_1mtau = np.log(tau), np.log1p(-tau)
        lq = np.broadcast_to(q.log_q_fixed[None], (len(tau), T.n)).copy()
        s_rows = self.structured
        lq[:, s_rows] = logP[:, self.row_idx[s_rows]] - q.logsize[None, s_rows] + np.where(
            q.has_special[None, s_rows], log_1mtau, 0.0)
        sp = q.special
        lq[:, sp] = log_tau - q.log_nspecial[None, sp]
        return np.exp(lq - T.log_scale[None])

    def terms(self, st):
        T, G = self.T, self.G
        S = T.B0[None] + np.einsum("ngk,bk->bng", T.C, st["g"])
        e = st["eps"][:, None, :]
        L = (1 - e) * T.A[None] + e * S
        w = st["pi"][:, None, :G] * T.avail[None]
        num = w * L
        Q = self.q_rows(st)
        numq = st["pi"][:, None, G] * Q
        tot = num.sum(-1) + numq
        savail = np.maximum(w.sum(-1) + st["pi"][:, None, G], TINY)
        return S, L, num, numq, tot, savail

    def loglik(self, st) -> np.ndarray:
        *_, tot, savail = self.terms(st)
        return (self.W * (np.log(np.maximum(tot, TINY)) - np.log(savail) + self.T.log_scale[None])).sum(1)

    def __call__(self, st):
        T, W, G = self.T, self.W, self.G
        S, L, num, numq, tot, savail = self.terms(st)
        tot_safe = np.maximum(tot, TINY)
        ll = (W * (np.log(tot_safe) - np.log(savail) + T.log_scale[None])).sum(1)
        R = num / tot_safe[..., None]
        Rq = numq / tot_safe
        pi = st["pi"]
        numer = np.einsum("bn,bng->bg", W, R)
        numer_q = (W * Rq).sum(1)
        Wd = W / savail
        denom = Wd @ self.avail
        denom_q = Wd.sum(1)
        new_pi = np.empty_like(pi)
        with np.errstate(invalid="ignore", divide="ignore"):
            new_pi[:, :G] = np.where(denom > 0, numer / np.maximum(denom, TINY), pi[:, :G])
            new_pi[:, G] = numer_q / np.maximum(denom_q, TINY)
        new_pi = np.maximum(new_pi, 0.0)
        new_pi /= new_pi.sum(1, keepdims=True)
        new = dict(st)
        new["pi"] = new_pi
        e = st["eps"][:, None, :]
        Rs = R * self.slip_cols[None, None, :]
        if self.fix_eps is None:
            with np.errstate(invalid="ignore", divide="ignore"):
                share = np.where(L > 0, e * S / np.maximum(L, TINY), 0.0)
            top = np.einsum("bn,bng->bg", W, Rs * share)
            bot = np.einsum("bn,bng->bg", W, Rs)
            if self.noise.eps == "shared":
                top, bot = top.sum(1, keepdims=True), bot.sum(1, keepdims=True)
            new["eps"] = np.where(bot > 1e-12, np.minimum(top / np.maximum(bot, TINY), self.eps_max), st["eps"])
        # kernel: expected slips per cell
        with np.errstate(invalid="ignore", divide="ignore"):
            inv_L = np.where(L > 0, 1.0 / np.maximum(L, TINY), 0.0)
        Ed = np.einsum("bn,bng,ngk->bk", W, Rs * inv_L * e, T.C) * st["g"]
        has = Ed.sum(1) > 0
        if has.any():
            if self.noise.kernel == "geometric":
                rho = np.where(has, RHO_GRID[np.argmax(Ed @ self.log_g_grid.T, 1)], st["rho"])
                new["rho"] = rho
                new["g"] = np.where(has[:, None], trunc_geom(rho), st["g"])
            else:
                new["g"] = np.where(has[:, None], Ed / np.maximum(Ed.sum(1, keepdims=True), TINY), st["g"])
        # the strata q
        if self.qs is not None:
            WRq = W * Rq
            c = WRq @ self.onehot  # (B, S)
            gs = c @ self.group_mat  # (B, groups)
            per = gs @ self.group_mat.T  # (B, S): each stratum's group total
            new["P"] = np.where(per > 0, c / np.maximum(per, TINY), st["P"])
            if self.qs.tau_free:
                sp = (WRq * self.qs.special[None]).sum(1)
                den = (WRq * self.qs.has_special[None]).sum(1)
                new["tau"] = np.where(den > 0, sp / np.maximum(den, TINY), st["tau"])
        return new, ll


def em_general(T: Tensors, W: np.ndarray | None = None, pi0: np.ndarray | None = None, eps0: Any = 0.1,
               fix_eps: float | None = None, init: dict[str, np.ndarray] | None = None, max_iter: int = 3000,
               tol: float = 1e-8, accelerate: bool = True) -> EMResult:
    """`em` for a non-default noise model: the same batched EM with SQUAREM on (pi, eps); the kernel and
    q parameters take the plain EM step. `init` warm-starts every parameter (each (B, ...) or one row)."""
    N, G = T.A.shape
    if fix_eps is None and not T.slip_identified:
        fix_eps = 0.0
    W = np.ones((1, N)) if W is None else np.asarray(W, dtype=float)
    B = W.shape[0]
    step = _GeneralStepper(T, W, fix_eps)
    st = step.init(B, pi0, eps0)
    if init is not None:
        for k, v in init.items():
            if k in st and not (k == "eps" and fix_eps is not None):
                st[k] = np.array(np.broadcast_to(v, st[k].shape), dtype=float)
        if pi0 is not None:
            st["pi"] = np.array(np.broadcast_to(pi0, st["pi"].shape), dtype=float)
    wsum = W.sum(1)
    prev = np.full(B, -np.inf)
    converged = np.zeros(B, dtype=bool)
    steps = 0
    em_max = step.eps_max
    while steps < max_iter:
        s1, ll0 = step(st)
        steps += 1
        converged = np.abs(ll0 - prev) / wsum < tol
        prev = ll0
        if converged.all():
            break
        if not accelerate:
            st = s1
            continue
        s2, ll1 = step(s1)
        # SQUAREM over every simplex-valued parameter (pi, the free kernel, the strata q) and eps, tau;
        # the geometric kernel's rho is a grid M-step and takes the plain step
        keys = ["pi", "eps"] + (["g"] if T.noise.kernel != "geometric" else []) + (["P", "tau"] if "P" in st else [])
        if fix_eps is not None:
            keys.remove("eps")
        r1 = {k: (s1[k] - st[k]).reshape(B, -1) for k in keys}
        v1 = {k: (s2[k] - 2 * s1[k] + st[k]).reshape(B, -1) for k in keys}
        nr = np.sqrt(sum((r1[k] ** 2).sum(1) for k in keys))
        nv = np.sqrt(sum((v1[k] ** 2).sum(1) for k in keys))
        with np.errstate(invalid="ignore", divide="ignore"):
            alpha = np.where(nv > 0, -nr / np.maximum(nv, TINY), -1.0)
        alpha = np.clip(alpha, -64.0, -1.0)
        ext = dict(s2)
        for k in keys:
            x = st[k].reshape(B, -1) - 2 * alpha[:, None] * r1[k] + alpha[:, None] ** 2 * v1[k]
            if k == "pi":
                x = np.maximum(x, 1e-12)
                x /= x.sum(1, keepdims=True)
            elif k == "eps":
                x = np.clip(x, 0.0, em_max)
            elif k == "tau":
                x = np.clip(x, 0.0, 1.0) if step.qs.tau_free else st[k].reshape(B, -1)
            elif k == "g":  # cells that are empty (0, or beyond the reach) stay empty
                x = np.where(s2[k] > 0, np.maximum(x, 1e-12), 0.0)
                x /= np.maximum(x.sum(1, keepdims=True), TINY)
            elif k == "P":  # renormalise within each group; strata with no mass stay empty
                x = np.where(s2[k] > 0, np.maximum(x, 1e-12), 0.0)
                tot = (x @ step.group_mat) @ step.group_mat.T
                x = np.where(tot > 0, x / np.maximum(tot, TINY), s2[k])
            ext[k] = x.reshape(st[k].shape)
        s3, ll_ext = step(ext)
        steps += 2
        ok = ll_ext >= ll1
        st = {k: np.where(ok.reshape((-1,) + (1,) * (s3[k].ndim - 1)), s3[k], s2[k]) for k in s3}
    ll = step.loglik(st)
    eps_out = _eps_summary(st, T)
    return EMResult(st["pi"], eps_out, st["rho"] if T.noise.kernel == "geometric" else np.full(B, np.nan), ll, steps,
                    converged, st)


def _eps_summary(st: dict[str, np.ndarray], T: Tensors) -> np.ndarray:
    """One slip rate per replicate: the shared rate, or the per-member rates averaged with the weights
    of the slipping columns (a member that never slips does not count)."""
    eps = st["eps"]
    if eps.shape[1] == 1:
        return eps[:, 0]
    G = T.A.shape[1]
    w = st["pi"][:, :G] * T.slips[None, :]
    tot = w.sum(1)
    return np.where(tot > 0, (w * eps).sum(1) / np.maximum(tot, TINY), eps.mean(1))


def _fit_general(T: Tensors, n_boot: int, rng: np.random.Generator, chunk: int, fix_eps: float | None, max_iter: int,
                 tol: float, q_label: str, jackknife: bool) -> FitResult:
    """`fit` for a non-default noise model: point estimate, cluster bootstrap with every parameter
    warm-started at the estimate (pi as in `fit`), optional jackknife. The kernel, the per-member slip
    rates and the q parameters are in `extra`, with bootstrap intervals."""
    point = em_general(T, fix_eps=fix_eps, max_iter=max_iter, tol=tol)
    st = {k: v[:1] for k, v in point.state.items()}
    pi_hat, eps_hat = point.pi[0], float(point.eps[0])
    labels = list(T.labels) + [q_label]
    extra = {"data_ties": data_ties(T), "slip_identified": T.slip_identified, "noise": T.noise.to_json(),
             "state": {k: v[0].tolist() for k, v in st.items()}}
    if n_boot <= 0:
        z = np.full(len(labels), np.nan)
        return FitResult(labels, pi_hat, z, z, eps_hat, (np.nan, np.nan), float(point.rho[0]), (np.nan, np.nan),
                         float(point.loglik[0]), T.n, len(np.unique(T.cluster)), None, point.iters,
                         bool(point.converged[0]), extra)
    Wall = cluster_bootstrap(T.cluster, n_boot, rng)
    starts = 0.5 * pi_hat[None, :] + 0.5 * rng.dirichlet(np.ones(len(pi_hat)), size=n_boot)
    pis, epss, states = [], [], []
    for start in range(0, n_boot, chunk):
        Wb = Wall[start:start + chunk]
        r = em_general(T, Wb, pi0=starts[start:start + chunk], fix_eps=fix_eps, init=st, max_iter=min(max_iter, 1500), tol=tol)
        pis.append(r.pi)
        epss.append(r.eps)
        states.append(r.state)
    boot = np.concatenate(pis)
    eb = np.concatenate(epss)
    bst = {k: np.concatenate([s[k] for s in states]) for k in states[0]}
    lo, hi = np.percentile(boot, 2.5, 0), np.percentile(boot, 97.5, 0)
    extra["state_ci"] = {k: [np.percentile(v, 2.5, 0).tolist(), np.percentile(v, 97.5, 0).tolist()] for k, v in bst.items()}
    jack = None
    if jackknife:
        ids, inv = np.unique(T.cluster, return_inverse=True)
        Wj = np.ones((len(ids), T.n))
        Wj[inv, np.arange(T.n)] = 0.0
        js = []
        for start in range(0, len(ids), chunk):
            r = em_general(T, Wj[start:start + chunk], pi0=pi_hat, fix_eps=fix_eps, init=st, max_iter=min(max_iter, 1500),
                           tol=tol)
            js.append(r.pi)
        jack = np.concatenate(js)
    rho_hat = float(point.rho[0])
    rho_ci = (np.nan, np.nan) if np.isnan(rho_hat) else (float(np.percentile(bst["rho"], 2.5)), float(np.percentile(bst["rho"], 97.5)))
    return FitResult(labels, pi_hat, lo, hi, eps_hat, (float(np.percentile(eb, 2.5)), float(np.percentile(eb, 97.5))),
                     rho_hat, rho_ci, float(point.loglik[0]), T.n, len(np.unique(T.cluster)), boot, point.iters,
                     bool(point.converged[0]), extra, jack)


def noise_params(state: dict[str, Any], noise: NoiseModel, keys_by_column: list[str],
                 strata_keys: list[tuple[str, int, int]] | None = None) -> NoiseParams:
    """A fitted state (one replicate, e.g. `FitResult.extra['state']`) as `NoiseParams` for the fake
    models. Per-member rates are keyed by `keys_by_column` (e.g. each group's first member); the strata
    q's probabilities by `strata_keys` (`UnitModel.strata_index()[0]`)."""
    eps = np.asarray(state["eps"], dtype=float).ravel()
    e: float | dict[str, float] = float(eps[0]) if len(eps) == 1 else {c: float(x) for c, x in zip(keys_by_column, eps)}
    strata = None
    tau = None
    if "P" in state:
        P = np.asarray(state["P"], dtype=float).ravel()
        strata = {}
        for (kind, n, size), p in zip(strata_keys, P):
            strata.setdefault((kind, n), np.zeros(n + 1))[size] = p
        tau = float(np.asarray(state["tau"]).ravel()[0])
    return NoiseParams(e, np.asarray(state["g"], dtype=float).ravel(), tau, strata, cells=noise.cells)


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
