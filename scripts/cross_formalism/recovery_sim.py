"""Planted-mixture recovery for the cross-formalism vertical (E1-type FIND sets).

    python recovery_sim.py OUT.json [n_reps]

Fake "models" answer every base in four encodings (G, S, C, L) by drawing a member from an
encoding-specific weight vector pi_e, then slipping to a near-miss (one vertex recoloured) with rate eps_e.
We refit by EM and report, per planted weight: bias, 95% interval width and coverage (base bootstrap,
paired across encodings), plus the power / false-positive rate of
  (a) the home-advantage contrast HAI = sum over C/L-home members of [pi_{C,L} - pi_{G,S}]  (Wald, bootstrap SE)
  (b) the omnibus shared-pi vs encoding-specific-pi likelihood-ratio test (parametric-bootstrap null).
Members: LIST family, LABEL family, DSATUR, LF (graph-home), GUC-DET, DPLL-OCC (CNF-home), COLLAPSE
(IMPOSSIBLE; POLARITY / GREEDY / FIRST / BICOND / ONL, logic- and CNF-home), EXACT (uniform over valid
partitions), plus a 'none of the above' term q (uniform over all colourings).
"""
from __future__ import annotations

import json
import random
import sys

import numpy as np

from cf_core import K, random_instance, colourings, canon, cnf_encode
import cf_members as M

MEMBERS = ['LIST', 'LABEL', 'DSATUR', 'LF', 'GUC', 'OCC', 'COLLAPSE', 'EXACT', 'NONE']
CNF_HOME = ['GUC', 'OCC', 'COLLAPSE']
GRAPH_HOME = ['DSATUR', 'LF']
ENCS = ['G', 'S', 'C', 'L']


def make_bases(count, n=10, m=15, seed0=300000):
    bases, seed = [], seed0
    while len(bases) < count:
        seed += 1
        inst = random_instance(n, m, seed)
        sols = colourings(inst)
        if not sols:
            continue
        cnf = cnf_encode(inst)
        def dec(a):
            if a[0] == 'IMP':
                return None
            from cf_core import decode, is_proper
            col = a[1] if a[0] == 'COL' else decode(cnf, inst, a[1])[0]
            return canon(col) if is_proper(inst, col) else None
        fp = {'LIST': dec(M.dpll_graph(inst, 'list')[0]), 'LABEL': dec(M.dpll_cnf(cnf, 'INDEX')[0]),
              'DSATUR': dec(M.dsatur(inst)), 'LF': dec(M.ff(inst, M.lf_order(inst))), 'GUC': dec(M.guc_det(cnf)),
              'OCC': dec(M.dpll_cnf(cnf, 'OCC')[0])}
        if any(v is None for v in fp.values()):
            continue
        if len({fp['LIST'], fp['LABEL'], fp['DSATUR'], fp['GUC']}) < 4:
            continue
        parts = sorted({canon(s) for s in sols})
        rep = {}
        for s in sols:
            rep.setdefault(canon(s), s)
        bases.append(Base(inst, fp, parts, rep))
    return bases


class Base:
    def __init__(self, inst, fp, parts, rep):
        self.n, self.fp, self.parts, self.rep = inst.n, fp, parts, rep
        self.pidx = {p: i for i, p in enumerate(parts)}
        self.nb = {}

    def exact_slip(self):
        """Near-miss distribution of EXACT: average of the kernels of all valid partitions (cached)."""
        if not hasattr(self, '_es'):
            es = {}
            for pp in self.parts:
                for k2, v in self.neighbours(pp).items():
                    es[k2] = es.get(k2, 0.0) + v / len(self.parts)
            self._es = es
        return self._es

    def neighbours(self, part):
        if part not in self.nb:
            col = self.rep.get(part, part)
            out = {}
            tot = self.n * (K - 1)
            for v in range(self.n):
                for c in range(1, K + 1):
                    if c != col[v]:
                        new = list(col)
                        new[v] = c
                        key = canon(tuple(new))
                        out[key] = out.get(key, 0) + 1 / tot
            self.nb[part] = out
        return self.nb[part]


def draw(base, member, eps, rng):
    if member == 'NONE':
        return canon(tuple(rng.randint(1, K) for _ in range(base.n)))
    if member == 'COLLAPSE':
        return 'IMP' if rng.random() >= eps else rng.choice(base.parts)
    part = rng.choice(base.parts) if member == 'EXACT' else base.fp[member]
    if rng.random() < eps:
        nb = base.neighbours(part)
        keys = list(nb)
        return rng.choices(keys, weights=[nb[k] for k in keys])[0]
    return part


def lik_vector(base, y, eps):
    """P(y | member) for every member (same order as MEMBERS)."""
    out = np.zeros(len(MEMBERS))
    npart = len(base.parts)
    q = 1.0 / (3 ** base.n) * 6
    for j, h in enumerate(MEMBERS):
        if h == 'NONE':
            out[j] = q if y != 'IMP' else 1e-12
        elif h == 'COLLAPSE':
            out[j] = (1 - eps) if y == 'IMP' else (eps / npart if y in base.pidx else 1e-12)
        elif y == 'IMP':
            out[j] = 1e-12
        elif h == 'EXACT':
            p = (1 - eps) / npart if y in base.pidx else 0.0
            # slip mass: average over valid partitions of their near-miss kernels
            p += eps * base.exact_slip().get(y, 0.0)
            out[j] = max(p, 1e-12)
        else:
            part = base.fp[h]
            p = (1 - eps) * (y == part) + eps * base.neighbours(part).get(y, 0.0)
            out[j] = max(p, 1e-12)
    return out


def em(L, iters=300, tol=1e-8):
    """L: (items, members) likelihood matrix -> MLE of mixture weights."""
    pi = np.full(L.shape[1], 1 / L.shape[1])
    prev = -np.inf
    for _ in range(iters):
        w = L * pi
        s = w.sum(1, keepdims=True)
        pi = (w / s).mean(0)
        ll = np.log(s).sum()
        if ll - prev < tol:
            break
        prev = ll
    return pi, float(np.log((L * pi).sum(1)).sum())


def simulate(bases, pis, epss, rng):
    data = {}
    for e in ENCS:
        rows = []
        for b in bases:
            h = rng.choices(MEMBERS, weights=[pis[e].get(m, 0) for m in MEMBERS])[0]
            rows.append(draw(b, h, epss[e], rng))
        data[e] = rows
    return data


def fit_all(bases, data, eps_fit, idx=None):
    idx = list(range(len(bases))) if idx is None else idx
    Ls = {e: np.array([lik_vector(bases[i], data[e][i], eps_fit[e]) for i in idx]) for e in ENCS}
    sep = {e: em(Ls[e]) for e in ENCS}
    shared_pi, _ = em(np.vstack([Ls[e] for e in ENCS]))
    ll_shared = sum(float(np.log((Ls[e] * shared_pi).sum(1)).sum()) for e in ENCS)
    ll_sep = sum(sep[e][1] for e in ENCS)
    return {e: sep[e][0] for e in ENCS}, shared_pi, 2 * (ll_sep - ll_shared), Ls


def hai(pis):
    """Home-advantage index: CNF-home weight on C/L minus on G/S, plus graph-home weight on G/S minus on C/L, halved."""
    j = {m: i for i, m in enumerate(MEMBERS)}
    cnf = sum((pis['C'][j[m]] + pis['L'][j[m]] - pis['G'][j[m]] - pis['S'][j[m]]) / 2 for m in CNF_HOME)
    gr = sum((pis['G'][j[m]] + pis['S'][j[m]] - pis['C'][j[m]] - pis['L'][j[m]]) / 2 for m in GRAPH_HOME)
    return (cnf + gr) / 2


BASE_PI = {'LIST': .30, 'LABEL': .05, 'DSATUR': .15, 'LF': .05, 'GUC': .03, 'OCC': .02, 'COLLAPSE': .02, 'EXACT': .33, 'NONE': .05}


def shifted(delta):
    """H-formalism: move `delta` of weight from graph-home to CNF-home members on C and L (HAI = delta)."""
    p = dict(BASE_PI)
    p['DSATUR'] -= delta * 0.7
    p['LF'] -= delta * 0.3
    p['GUC'] += delta * 0.5
    p['OCC'] += delta * 0.2
    p['COLLAPSE'] += delta * 0.3
    return p


SCENARIOS = {
    'S0 H-structure (no shift)': ({e: BASE_PI for e in ENCS}, {e: .1 for e in ENCS}, 0.0),
    'S1 H-formalism, HAI = 0.10': ({'G': BASE_PI, 'S': BASE_PI, 'C': shifted(.10), 'L': shifted(.10)}, {e: .1 for e in ENCS}, 0.10),
    'S2 H-formalism, HAI = 0.05': ({'G': BASE_PI, 'S': BASE_PI, 'C': shifted(.05), 'L': shifted(.05)}, {e: .1 for e in ENCS}, 0.05),
    'S3 H-length (no shift; slips 0.25 on C/L)': ({e: BASE_PI for e in ENCS}, {'G': .1, 'S': .1, 'C': .25, 'L': .25}, 0.0),
}


def run(n_bases_list=(100, 200, 300), reps=20, boots=100, lrt_boots=40, seed=1):
    rng = random.Random(seed)
    bank = make_bases(max(n_bases_list))
    results = []
    for N in n_bases_list:
        bases = bank[:N]
        for name, (pis, epss, true_hai) in SCENARIOS.items():
            rec = {'N_bases_per_encoding': N, 'scenario': name, 'true_HAI': true_hai}
            bias, width, cover, hai_hat, hai_lo, hai_hi, lrt_p = [], [], [], [], [], [], []
            for r in range(reps):
                data = simulate(bases, pis, epss, rng)
                eps_fit = {e: epss[e] for e in ENCS}         # slip rate per encoding estimated separately (here: known)
                pi_sep, pi_sh, lr, Ls = fit_all(bases, data, eps_fit)
                # bootstrap over bases (paired across encodings)
                bs = []
                for _ in range(boots):
                    idx = [rng.randrange(N) for _ in range(N)]
                    sep_b = {e: em(Ls[e][idx])[0] for e in ENCS}
                    bs.append(sep_b)
                truth = np.array([[pis[e][m] for m in MEMBERS] for e in ENCS])
                est = np.array([pi_sep[e] for e in ENCS])
                arr = np.array([[b[e] for e in ENCS] for b in bs])          # boots x enc x members
                lo, hi = np.percentile(arr, 2.5, 0), np.percentile(arr, 97.5, 0)
                bias.append(est - truth)
                width.append(hi - lo)
                cover.append((lo <= truth) & (truth <= hi))
                h = hai(pi_sep)
                hb = np.array([hai(b) for b in bs])
                se = hb.std()
                hai_hat.append(h)
                hai_lo.append(h - 1.96 * se)
                hai_hi.append(h + 1.96 * se)
                if r < (8 if N != 300 else 20) and lrt_boots:
                    null = []
                    pis_null = {e: dict(zip(MEMBERS, pi_sh)) for e in ENCS}
                    for _ in range(lrt_boots):
                        d0 = simulate(bases, pis_null, epss, rng)
                        null.append(fit_all(bases, d0, eps_fit)[2])
                    lrt_p.append(float(np.mean(np.array(null) >= lr)))
            bias, width, cover = np.array(bias), np.array(width), np.array(cover)
            present = np.array([[pis[e][m] for m in MEMBERS] for e in ENCS]) >= 0.05
            rec['max_abs_bias_present'] = round(float(np.abs(bias.mean(0))[present].max()), 3)
            rec['mean_95_width_present'] = round(float(width.mean(0)[present].mean()), 3)
            rec['coverage_present'] = round(float(cover.mean(0)[present].mean()), 3)
            rec['coverage_min_present'] = round(float(cover.mean(0)[present].min()), 3)
            rec['HAI_mean'] = round(float(np.mean(hai_hat)), 3)
            rec['HAI_mean_95_halfwidth'] = round(float(np.mean(np.array(hai_hi) - np.array(hai_hat))), 3)
            rec['HAI_detect_rate (lower 95% > 0)'] = round(float(np.mean(np.array(hai_lo) > 0)), 2)
            rec['HAI_equivalence_rate (95% CI within ±0.05)'] = round(float(np.mean((np.array(hai_lo) > -0.05) & (np.array(hai_hi) < 0.05))), 2)
            if lrt_p:
                rec['LRT_reject_rate (p < .05)'] = round(float(np.mean(np.array(lrt_p) < 0.05)), 2)
                rec['LRT_reps'] = len(lrt_p)
            results.append(rec)
            print(json.dumps(rec), flush=True)
    return results




# ============================================================================================
# Extra scenarios: (a) slip misspecification; (b) planted translation latent with noisy trace codes
# ============================================================================================

def run_misspecified(N=300, reps=20, seed=7):
    """H-length data (slip 0.25 on C/L, 0.10 on G/S, no weight shift), fitted with one common slip of 0.10.
    Shows whether length-driven noise masquerades as a home advantage when slips are not modelled per encoding."""
    rng = random.Random(seed)
    bases = make_bases(N)
    pis, epss, _ = SCENARIOS['S3 H-length (no shift; slips 0.25 on C/L)']
    out = {'misspecified (common slip 0.10)': [], 'per-encoding slip': []}
    for _ in range(reps):
        data = simulate(bases, pis, epss, rng)
        for label, eps_fit in (('misspecified (common slip 0.10)', {e: .1 for e in ENCS}), ('per-encoding slip', epss)):
            pi_sep = fit_all(bases, data, eps_fit)[0]
            out[label].append(hai(pi_sep))
    return {k: {'HAI_mean': round(float(np.mean(v)), 3), 'HAI_sd': round(float(np.std(v)), 3)} for k, v in out.items()}


def run_translation(N=300, reps=20, tau=0.6, sens=0.85, fpr=0.10, seed=11):
    """H-translate: on C and L each response is produced in a latent working representation r:
    r = graph with prob tau (weights BASE_PI) or r = native (weights NATIVE). A trace code T ('translated')
    is observed with sensitivity `sens` and false-positive rate `fpr` (as measured in hand-label validation).
    Fit: two-state latent model with known (sens, fpr); estimate tau and pi_native. Compare with the
    answer-only fit, which can recover only the blend tau*BASE + (1-tau)*NATIVE."""
    NATIVE = {'LIST': .20, 'LABEL': .05, 'DSATUR': .02, 'LF': .01, 'GUC': .25, 'OCC': .10, 'COLLAPSE': .10, 'EXACT': .22, 'NONE': .05}
    rng = random.Random(seed)
    bases = make_bases(N)
    jG = np.array([BASE_PI[m] for m in MEMBERS])
    res = {'tau_hat': [], 'native_GUC_hat': [], 'native_DSATUR_hat': [], 'assoc_logOR': []}
    for _ in range(reps):
        ys, Ts = [], []
        for b in bases:
            for e in ('C', 'L'):
                r = 'G' if rng.random() < tau else 'N'
                pw = BASE_PI if r == 'G' else NATIVE
                h = rng.choices(MEMBERS, weights=[pw[m] for m in MEMBERS])[0]
                ys.append((b, draw(b, h, .1, rng)))
                Ts.append(1 if rng.random() < (sens if r == 'G' else fpr) else 0)
        L = np.array([lik_vector(b, y, .1) for b, y in ys])
        T = np.array(Ts)
        # graph-state weights fixed from the G/S fit (here: the truth, as estimated on G/S at large N)
        lG = L @ jG
        pT_G = np.where(T == 1, sens, 1 - sens)
        pT_N = np.where(T == 1, fpr, 1 - fpr)
        t_hat, pN = 0.5, np.full(len(MEMBERS), 1 / len(MEMBERS))
        for _it in range(400):
            a = t_hat * pT_G * lG
            wN = L * pN
            bN = (1 - t_hat) * pT_N * wN.sum(1)
            z = a + bN
            rG = a / z
            t_hat = rG.mean()
            resp = (1 - rG)[:, None] * wN / wN.sum(1, keepdims=True)
            pN = resp.sum(0) / resp.sum()
        res['tau_hat'].append(t_hat)
        res['native_GUC_hat'].append(pN[MEMBERS.index('GUC')])
        res['native_DSATUR_hat'].append(pN[MEMBERS.index('DSATUR')])
        # model-free check: answers matching a CNF-home fingerprint, by trace code
        def is_cnf_home(b, y):
            return y == 'IMP' or y in (b.fp['GUC'], b.fp['OCC'])
        m = np.array([is_cnf_home(b, y) for b, y in ys])
        a1, b1 = (m & (T == 1)).sum() + .5, (~m & (T == 1)).sum() + .5
        a0, b0 = (m & (T == 0)).sum() + .5, (~m & (T == 0)).sum() + .5
        res['assoc_logOR'].append(float(np.log((a0 / b0) / (a1 / b1))))
    return {'planted': {'tau': tau, 'native_GUC': NATIVE['GUC'], 'native_DSATUR': NATIVE['DSATUR'], 'trace_sens': sens, 'trace_fpr': fpr},
            'recovered_mean': {k: round(float(np.mean(v)), 3) for k, v in res.items()},
            'recovered_sd': {k: round(float(np.std(v)), 3) for k, v in res.items()}}


if __name__ == '__main__':
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    if len(sys.argv) > 3 and sys.argv[3] == 'extra':
        res = {'misspecified_slip': run_misspecified(reps=reps), 'translation_latent': run_translation(reps=reps)}
        print(json.dumps(res, indent=1))
    else:
        res = run(reps=reps)
    with open(sys.argv[1], 'w') as f:
        json.dump(res, f, indent=1)
