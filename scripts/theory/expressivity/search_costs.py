"""Search-cost and dependency-depth simulations for the T1 expressivity note.

Pure Python, no dependencies. Measures, on the project's instance families:
  1. DPLL (unit propagation + chronological backtracking) work on random 3-SAT, alpha = 4.26,
     with two branching rules: INDEX (first unassigned var, True first) and JW (Jeroslow-Wang).
  2. WalkSAT (p = 0.5) flips to solve satisfiable random 3-SAT near threshold.
  3. Exact k-colouring by DSATUR backtracking on G(n, c/n) near the 3-COL threshold.
  4. Dependency depth (longest path in the order DAG) of first-fit colouring and of
     mention-order GREEDY on 3-SAT: the number of sequential levels a one-pass
     implementation must compose.
  5. Exact colouring by naive listing-order backtracking (no adaptive ordering).
  6. Token-cost estimates for DPLL traces under three per-event token costs.
  7. Unit-propagation depth (rounds to fixpoint) per DPLL decision.

Usage: python3 search_costs.py {dpll|walksat|colour|colour_naive|satdepth|budget|uprounds}
Each part prints CSV to stdout and runs in under a few minutes. Written for
docs/theory/T1_expressivity.md (section 3); run from this folder; seeds are fixed.
"""
import random
import statistics
import sys

sys.setrecursionlimit(10000)


# ---------------------------------------------------------------- 3-SAT
def random_3sat(n, alpha, rng):
    m = round(alpha * n)
    clauses = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        clauses.append(tuple(v if rng.random() < 0.5 else -v for v in vs))
    return clauses


class DPLL:
    def __init__(self, n, clauses, rule, node_cap):
        self.n, self.clauses, self.rule, self.cap = n, clauses, rule, node_cap
        self.occ = {l: [] for v in range(1, n + 1) for l in (v, -v)}
        for ci, c in enumerate(clauses):
            for l in c:
                self.occ[l].append(ci)
        self.val = [0] * (n + 1)
        self.decisions = 0
        self.props = 0
        self.conflicts = 0
        self.aborted = False

    def lit_val(self, l):
        v = self.val[abs(l)]
        return 0 if v == 0 else (v if l > 0 else -v)

    def propagate(self, trail):
        """Assign literals queued on trail tail until fixpoint. Returns False on conflict."""
        i = 0
        queue = list(trail)
        while i < len(queue):
            l = queue[i]
            i += 1
            for ci in self.occ[-l]:  # clauses where -l is now false
                c = self.clauses[ci]
                unassigned = None
                n_un = 0
                sat = False
                for x in c:
                    xv = self.lit_val(x)
                    if xv == 1:
                        sat = True
                        break
                    if xv == 0:
                        n_un += 1
                        unassigned = x
                if sat:
                    continue
                if n_un == 0:
                    return False, queue
                if n_un == 1:
                    self.val[abs(unassigned)] = 1 if unassigned > 0 else -1
                    self.props += 1
                    queue.append(unassigned)
        return True, queue

    def choose(self):
        if self.rule == "INDEX":
            for v in range(1, self.n + 1):
                if self.val[v] == 0:
                    return v
            return None
        # Jeroslow-Wang on unsatisfied clauses
        score = {}
        for c in self.clauses:
            if any(self.lit_val(x) == 1 for x in c):
                continue
            free = [x for x in c if self.lit_val(x) == 0]
            w = 2.0 ** (-len(free))
            for x in free:
                score[x] = score.get(x, 0.0) + w
        if not score:
            for v in range(1, self.n + 1):
                if self.val[v] == 0:
                    return v
            return None
        best = max(score, key=lambda x: (score[x] + score.get(-x, 0.0), score[x]))
        return best

    def solve(self):
        return self._rec([])

    def _assign(self, lits):
        for l in lits:
            self.val[abs(l)] = 1 if l > 0 else -1

    def _undo(self, lits):
        for l in lits:
            self.val[abs(l)] = 0

    def _rec(self, _):
        if self.decisions >= self.cap:
            self.aborted = True
            return None
        d = self.choose()
        if d is None:
            return True
        if self.rule == "INDEX":
            order = (d, -d)
        else:
            order = (d, -d)  # JW already picked the heavier literal
        for lit in order:
            self.decisions += 1
            self.val[abs(lit)] = 1 if lit > 0 else -1
            ok, queue = self.propagate([lit])
            if ok:
                r = self._rec(None)
                if r is True:
                    return True
                if r is None:
                    return None
            else:
                self.conflicts += 1
            self._undo(queue)
        return False


# ---------------------------------------------------------------- WalkSAT
def walksat(n, clauses, rng, p=0.5, max_flips=200000):
    val = [False] + [rng.random() < 0.5 for _ in range(n)]
    occ = {v: [] for v in range(1, n + 1)}
    for ci, c in enumerate(clauses):
        for l in c:
            occ[abs(l)].append(ci)

    def true_lit(l):
        return val[abs(l)] if l > 0 else not val[abs(l)]

    ntrue = [sum(true_lit(l) for l in c) for c in clauses]
    unsat = set(i for i, k in enumerate(ntrue) if k == 0)
    for flip in range(max_flips):
        if not unsat:
            return flip
        ci = rng.choice(tuple(unsat))
        c = clauses[ci]

        def breakcount(v):
            b = 0
            for cj in occ[v]:
                if ntrue[cj] == 1:
                    # is v the sole true literal?
                    for l in clauses[cj]:
                        if abs(l) == v and true_lit(l):
                            b += 1
            return b

        bc = [(breakcount(abs(l)), abs(l)) for l in c]
        zero = [v for b, v in bc if b == 0]
        if zero:
            v = rng.choice(zero)
        elif rng.random() < p:
            v = abs(rng.choice(c))
        else:
            mb = min(b for b, _ in bc)
            v = rng.choice([v for b, v in bc if b == mb])
        # flip v
        for cj in occ[v]:
            for l in clauses[cj]:
                if abs(l) == v:
                    if true_lit(l):
                        ntrue[cj] -= 1
                    else:
                        ntrue[cj] += 1
            if ntrue[cj] == 0:
                unsat.add(cj)
            else:
                unsat.discard(cj)
        val[v] = not val[v]
    return None


# ---------------------------------------------------------------- colouring
def gnp(n, c, rng):
    p = c / n
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].add(j)
                adj[j].add(i)
    return adj


def dsatur_bt(adj, k, cap=10**6):
    n = len(adj)
    col = [-1] * n
    nodes = [0]

    def pick():
        best, bkey = None, None
        for v in range(n):
            if col[v] >= 0:
                continue
            sat = len({col[u] for u in adj[v] if col[u] >= 0})
            key = (sat, len(adj[v]), -v)
            if bkey is None or key > bkey:
                best, bkey = v, key
        return best

    def rec():
        if nodes[0] > cap:
            return None
        v = pick()
        if v is None:
            return True
        used = {col[u] for u in adj[v] if col[u] >= 0}
        maxc = max(col) + 1  # symmetry breaking: at most one new colour
        for c in range(min(k, maxc + 1)):
            if c in used:
                continue
            nodes[0] += 1
            col[v] = c
            r = rec()
            if r is True:
                return True
            if r is None:
                return None
            col[v] = -1
        return False

    r = rec()
    return r, nodes[0]


def chromatic(adj):
    for k in range(1, len(adj) + 1):
        r, nodes = dsatur_bt(adj, k)
        if r:
            return k
    return len(adj)


def ff_depth(adj, order):
    """Longest path in the DAG 'u -> v if u adjacent to v and u earlier': JP rounds."""
    pos = {v: i for i, v in enumerate(order)}
    depth = {}
    for v in order:
        d = 1
        for u in adj[v]:
            if pos[u] < pos[v]:
                d = max(d, depth[u] + 1)
        depth[v] = d
    return max(depth.values()) if depth else 0


def ff_effective_depth(adj, order):
    """Optimistic (lower-bound-style) dependency depth of first-fit: v depends only on one
    witness earlier neighbour per colour j < col(v). The JP longest path (ff_depth) is the
    upper bound; the truth lies between."""
    pos = {v: i for i, v in enumerate(order)}
    col = {}
    for v in order:
        used = {col[u] for u in adj[v] if pos[u] < pos[v]}
        c = 0
        while c in used:
            c += 1
        col[v] = c
    lb = {}
    for v in order:
        earlier = [u for u in adj[v] if pos[u] < pos[v]]
        # witness for each colour j < col[v]: cheapest-depth earlier nbr with colour j
        d = 1
        for j in range(col[v]):
            w = min(lb[u] for u in earlier if col[u] == j)
            d = max(d, w + 1)
        lb[v] = d
    return max(lb.values()) if lb else 0


def sat_greedy_depth(n, clauses, order):
    pos = {v: i for i, v in enumerate(order)}
    nb = {v: set() for v in range(1, n + 1)}
    for c in clauses:
        vs = [abs(l) for l in c]
        for a in vs:
            for b in vs:
                if a != b:
                    nb[a].add(b)
    depth = {}
    for v in order:
        d = 1
        for u in nb[v]:
            if pos[u] < pos[v]:
                d = max(d, depth[u] + 1)
        depth[v] = d
    return max(depth.values())


def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))
    return xs[k]



def naive_bt(adj, k, order, cap=10**6):
    """Backtracking k-colouring in a fixed vertex order (no adaptive ordering, no lookahead)."""
    n = len(adj)
    col = [-1] * n
    nodes = [0]

    def rec(i):
        if nodes[0] > cap:
            return None
        if i == n:
            return True
        v = order[i]
        used = {col[u] for u in adj[v] if col[u] >= 0}
        maxc = max(col) + 1
        for c in range(min(k, maxc + 1)):
            if c in used:
                continue
            nodes[0] += 1
            col[v] = c
            r = rec(i + 1)
            if r:
                return True
            if r is None:
                return None
            col[v] = -1
        return False

    return rec(0), nodes[0]


class DPLLRounds(DPLL):
    """DPLL that records, per decision, the BFS depth of the unit-propagation cascade."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.rounds = []

    def propagate(self, trail):
        depth = {trail[0]: 0}
        queue = list(trail)
        i = 0
        while i < len(queue):
            l = queue[i]
            i += 1
            for ci in self.occ[-l]:
                c = self.clauses[ci]
                un, nun, sat = None, 0, False
                for x in c:
                    xv = self.lit_val(x)
                    if xv == 1:
                        sat = True
                        break
                    if xv == 0:
                        nun += 1
                        un = x
                if sat:
                    continue
                if nun == 0:
                    self.rounds.append(max(depth.values()))
                    return False, queue
                if nun == 1:
                    self.val[abs(un)] = 1 if un > 0 else -1
                    self.props += 1
                    queue.append(un)
                    depth[un] = depth.get(l, 0) + 1
        self.rounds.append(max(depth.values()))
        return True, queue


# Tokens per decision, per propagated literal, per conflict (o200k_base counts of sample
# trace lines; "verbose_x2" doubles them for re-checking and hesitation).
TOKEN_STYLES = {"terse": (4, 7, 12), "verbose": (9, 37, 57), "verbose_x2": (18, 74, 114)}
BUDGET = 32000

def main(part):
    rng = random.Random(12345)
    if part == "dpll":
        print("n,rule,status,count,med_dec,p90_dec,med_prop,p90_prop,med_confl,aborted")
        for n in (10, 15, 20, 25, 30, 40, 50, 60):
            for rule in ("INDEX", "JW"):
                res = {"SAT": [], "UNSAT": []}
                aborted = 0
                for t in range(40):
                    cl = random_3sat(n, 4.26, random.Random(1000 * n + t))
                    s = DPLL(n, cl, rule, node_cap=300000)
                    r = s.solve()
                    if r is None:
                        aborted += 1
                        continue
                    res["SAT" if r else "UNSAT"].append((s.decisions, s.props, s.conflicts))
                for st, rows in res.items():
                    if not rows:
                        continue
                    dec = [r[0] for r in rows]
                    pr = [r[1] for r in rows]
                    cf = [r[2] for r in rows]
                    print(f"{n},{rule},{st},{len(rows)},{statistics.median(dec)},{q(dec,0.9)},"
                          f"{statistics.median(pr)},{q(pr,0.9)},{statistics.median(cf)},{aborted}",
                          flush=True)
    elif part == "walksat":
        print("n,alpha,solved,med_flips,p90_flips")
        for n in (20, 30, 40, 50, 60):
            for alpha in (3.5, 4.0, 4.26):
                flips = []
                tried = 0
                while len(flips) < 30 and tried < 400:
                    tried += 1
                    cl = random_3sat(n, alpha, random.Random(7 * n + 13 * tried + int(alpha * 100)))
                    s = DPLL(n, cl, "JW", node_cap=200000)
                    if s.solve() is not True:
                        continue
                    f = walksat(n, cl, random.Random(tried), max_flips=200000)
                    flips.append(f if f is not None else 200000)
                print(f"{n},{alpha},{len(flips)},{statistics.median(flips)},{q(flips,0.9)}", flush=True)
    elif part == "colour":
        print("n,c,count,chi_dist,med_bt_nodes,p90_bt_nodes,med_refute_nodes,p90_refute_nodes,med_ff_depth_JP,p90_ff_depth_JP,med_ff_depth_LB,p90_ff_depth_LB,med_maxdeg")
        for n in (8, 12, 16, 20, 25, 30, 40):
            for c in (3.0, 4.7, 6.0):
                nodes, ref, djp, dlb, chis, degs = [], [], [], [], [], []
                for t in range(40):
                    adj = gnp(n, c, random.Random(100 * n + t + int(10 * c)))
                    k = chromatic(adj)
                    chis.append(k)
                    _, nd = dsatur_bt(adj, k)
                    nodes.append(nd)
                    _, nr = dsatur_bt(adj, k - 1)
                    ref.append(nr)
                    order = list(range(n))
                    random.Random(t).shuffle(order)
                    djp.append(ff_depth(adj, order))
                    dlb.append(ff_effective_depth(adj, order))
                    degs.append(max(len(a) for a in adj))
                chid = {k: chis.count(k) for k in sorted(set(chis))}
                print(f"{n},{c},{len(nodes)},\"{chid}\",{statistics.median(nodes)},{q(nodes,0.9)},"
                      f"{statistics.median(ref)},{q(ref,0.9)},"
                      f"{statistics.median(djp)},{q(djp,0.9)},{statistics.median(dlb)},{q(dlb,0.9)},{statistics.median(degs)}",
                      flush=True)
    elif part == "satdepth":
        print("n,alpha,med_greedy_depth,p90_greedy_depth")
        for n in (10, 20, 30, 40, 60):
            for alpha in (3.0, 4.26):
                ds = []
                for t in range(40):
                    cl = random_3sat(n, alpha, random.Random(55 * n + t))
                    order = list(range(1, n + 1))
                    ds.append(sat_greedy_depth(n, cl, order))
                print(f"{n},{alpha},{statistics.median(ds)},{q(ds,0.9)}", flush=True)
    elif part == "colour_naive":
        print("n,c,med_find,p90_find,med_refute,p90_refute,max_refute")
        for n in (8, 12, 16, 20, 25, 30, 40):
            for c in (3.0, 4.7, 6.0):
                F, R = [], []
                for t in range(40):
                    adj = gnp(n, c, random.Random(100 * n + t + int(10 * c)))
                    k = chromatic(adj)
                    order = list(range(n))
                    random.Random(t).shuffle(order)
                    _, nf = naive_bt(adj, k, order)
                    r, nr = naive_bt(adj, k - 1, order)
                    F.append(nf)
                    R.append(nr if r is not None else 10**6)
                print(f"{n},{c},{statistics.median(F)},{q(F,0.9)},{statistics.median(R)},{q(R,0.9)},{max(R)}",
                      flush=True)
    elif part == "budget":
        print("n,rule,status,cnt,style,med_tok,p90_tok,frac_over_32k,med_tok_with_parse_verify")
        for n in (10, 15, 20, 25, 30, 40, 50, 60, 70, 80):
            m = round(4.26 * n)
            for rule in ("INDEX", "JW"):
                if rule == "INDEX" and n > 60:
                    continue
                recs = {"SAT": [], "UNSAT": []}
                for t in range(40):
                    cl = random_3sat(n, 4.26, random.Random(1000 * n + t))
                    s = DPLL(n, cl, rule, node_cap=300000)
                    r = s.solve()
                    if r is None:
                        continue
                    recs["SAT" if r else "UNSAT"].append((s.decisions, s.props, s.conflicts))
                for st, rows in recs.items():
                    if not rows:
                        continue
                    for sty, (td, tp, tc) in TOKEN_STYLES.items():
                        tok = [td * d + tp * p + tc * c for d, p, c in rows]
                        over = m * 13 + (m * 30 if st == "SAT" else 0)  # restate CNF; verify a SAT answer
                        tok2 = [x + over for x in tok]
                        print(f"{n},{rule},{st},{len(rows)},{sty},{statistics.median(tok):.0f},{q(tok,0.9):.0f},"
                              f"{sum(x > BUDGET for x in tok2)/len(tok2):.2f},{statistics.median(tok2):.0f}",
                              flush=True)
    elif part == "uprounds":
        print("n,med_rounds,p90_rounds,max_rounds")
        for n in (20, 40, 60):
            R = []
            for t in range(30):
                cl = random_3sat(n, 4.26, random.Random(1000 * n + t))
                s = DPLLRounds(n, cl, "JW", node_cap=300000)
                s.solve()
                R += s.rounds
            print(f"{n},{statistics.median(R)},{q(R,0.9)},{max(R)}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
