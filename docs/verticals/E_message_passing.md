# Vertical E: iterated local message passing

*One file per heuristic class; structure from [TEMPLATE.md](TEMPLATE.md). Citations come from the repo's literature reports (written "report A–F", meaning [docs/literature/](../literature/)) or were checked this session on their arXiv abstract pages (marked "checked"). Statements marked **[ours]** are our own derivations or design choices, to be asserted by unit tests rather than cited.*

- **Status:** designed (v0.2, 2026-11-13). Revised for the Phase-1 scope update.
- **Owner:** [TODO]
- **Phase-1 scope:** behavioural only.
  - **Primary condition:** open-weight reasoning models at best effort (high effort, 32k-token thinking cap).
  - **Diagnostic conditions:** direct-answer and low-budget runs. They stay because family E is the leading candidate for what a *single forward pass* computes.
  - **Interpretability (§3):** Phase 2, run only if the behavioural evidence warrants it.
- **Example library:** [E\_message\_passing\_questions.md](E_message_passing_questions.md) and [`data/examples/E_message_passing.jsonl`](../../data/examples/E_message_passing.jsonl). It holds 163 computationally verified items, with hypotheses, likelihood-ratio tables and the coverage matrix (§2.14).

---

## 0. Summary

**The claim.** On some items, the model's answer about a variable or node is what t rounds of "update from your neighbours" would give.

**Three contrasts define the family.** Everything below is built on them.

1. **Locality.** The answer about v depends on the formula only through the clauses within radius t of v. *Every* local family shares this: C0 is radius 0, B1 `UP-k` is radius k−1.
2. **Soft vs hard.** E members other than WP pass graded marginals. B1 passes only forced literals, and C0 uses only v's own literal counts.
3. **Computation tree vs ball.** Message passing sees only the *unrolled* neighbourhood (the computation tree). So it is blind to cycles and identical on a formula and its covers. A general local procedure that reads the whole ball, names included, is not.

**Two forms of E matter for thinking models.**

- **E-explicit:** the trace itself runs rounds: per-variable votes, sweeps, graded beliefs.
- **E-implicit:** E runs inside forward passes and shows up as the *value heuristic* inside a search-like trace. Examples are which value is tried first, or the guess given when the budget runs out. The hybrid member `E-in-D` (§1.3) models this.

**The readout is graded, not binary.** A model may use E on some items and other procedures on others. So every result is a *quantity with an interval*, never a used / not-used verdict:

- **mixture weight π\_E** (and π for each member and competitor): posterior mean and 95% interval, from the shared mixture model (DESIGN O3);
- **lift:** the share of errors that E explains above its permutation baseline;
- **ΔLL / Bayes factor** of the mixture including E over (i) the null mixture and (ii) the mixture with E replaced by its nearest competitor;
- **trace share:** the fraction of traces matching E's signature, weighted by the model's measured faithfulness w (§2.6).

Weights may depend on item features and on the model: π\_h(φ(x), m) = softmax(w\_h · φ(x) + b\_{h,m}). Examples of φ are radius d, α, framing, budget and n relative to n\*. This is family I's strategy selection, and every eval reports whether the feature terms are needed (ΔLL with and without them).

"Disconfirming" a competitor means pushing its weight toward zero with a stated upper bound, e.g. π\_C0 ≤ 0.1 (upper 95%). It never means eliminating it.

**Evals.** Primary = run at best effort in thinking mode. Diagnostic = mainly direct and low-budget runs.

| ID | Question (one line) | Key counterfactual | Role |
|----|---------------------|--------------------|------|
| **E1** LOC | Does the answer depend only on a finite radius r\*? How large is r\*, in one pass and at best effort? | Edits at controlled graph distance d, each against a matched *semantic no-op* null edit. Two channels (hard forcing / soft bias). Crossed with token placement and chain order. | E1-S (sparse) diagnostic; E1-C (periphery–core) primary |
| **E2** SOFT | Does v's answer follow its neighbours' *tendencies* (the BP-1 marginal) rather than v's own polarity, processing order, or the truth? | 3 × 2 × 2 × 2 factorial: own polarity A × second-order evidence B × truth D × first-mention order O | Primary |
| **E3** COVER | Can the model tell apart structures that every radius-r procedure sees identically? | Two odd cycles vs one even cycle (same counts and degrees). Cycle length m swept, with and without anchors. | Diagnostic |
| **E4** KNEE | Above the budget line, which procedure's success curve and failure profile fits? | α sweep on random 3-SAT at n around n\*. Simulated reference curves for every family on the same items. | Primary |
| **E5** CALIB | When choosing values of unforced variables, does the model follow BP marginals, own polarity, or the true solution marginals? | Per-variable regression on tree-like vs loopy formulas, plus 2-lift pairs (BP-identical, exact-different) | Primary |
| **E6** DEC | When committing variables one at a time, does an early commitment influence later ones the way decimation predicts? | Flip one early commitment (forced output prefix in direct mode; edited trace prefix in thinking mode). Read later choices by distance and by whether the path is "open" or "blocked". | E6a diagnostic; E6b primary (doubles as faithfulness test FT4) |

**Rigour decisions that shape everything else.**

- **Random 3-SAT can't measure radius at prompt sizes.** At α ≈ 4.26 a variable shares clauses with ≈ 25 others, so the formula's diameter is ≈ 2 for n ≤ 60. Radius tests therefore use constructed sparse neighbourhoods.
- **Hard items with controlled neighbourhoods.** Thinking models at best effort solve small sparse items. To make them fall back on a heuristic while we still control v's neighbourhood, we use a **periphery–core** design: a hard random core joined to v only by a short equivalence link, plus a controlled periphery around v.
- **Every effective edit has a matched null.** The null flips literals of variables that occur only once. That is a renaming of the solution space, so it is invisible to every procedure that reads the semantics, and it is matched in tokens.
- **Token distance is decorrelated from graph distance**, and placement is a designed factor. A causal transformer predicts placement effects of its own (§1.7 P2).
- **Single-token answers are the only true one-pass probes.** Emitting a full assignment gives the model n sequential steps even with thinking off, so it can decimate.

---

## 1. The class

### 1.1 Defining idea and taxonomy position

- **Defining idea.** Each variable (or node) keeps a local state. For t rounds it recomputes that state from the states of its factor-graph neighbours, then it decides. Formally this is a t-round LOCAL algorithm. An L-layer GNN equals an L-round distributed algorithm, and the solvable problem classes coincide (Sato, Yamada & Kashima 2019, report F).
- **Taxonomy position.** Family E in PAPER_SKELETON Table 4 and report F's tree:
  - **E1:** t rounds plus rounding;
  - **E2:** decimation.
- **Overlaps with other families.** C0 is E's zero-round member. B1 `UP-k` is its hard-decision member.

### 1.2 Notation and conventions (all members)

**Formulas.**

- A CNF F has variables V and clauses C.
- s\_{a,i} ∈ {+1, −1} is +1 if variable i occurs un-negated in clause a.
- σ\_i = +1 means True.

**Graphs and distances.**

- G\_F is the factor graph.
- In the interaction graph H\_F, i ~ j if the two variables share a clause. dist(i, j) is the shortest-path distance in H\_F.
- C\_r(v) is the set of clauses that contain a variable within distance r of v.

**Radius** (one scale for every family).

- rad\_h is the least r such that h's output at v is a function of C\_r(v) alone, for every F.
- With the round indexing below:
  - `BP-t`, `WP-t`, `SP-t`: rad = t;
  - C0 `POLARITY`: rad = 0;
  - B1 `UP-k`: rad = k − 1 (keeping B1's own round count).
- r\* always means radius on this scale.

**Edit distance.**

- An edit changes literals in a clause a. Its distance is d = min over variables w in a of dist(v, w).
- On tree-like neighbourhoods, a radius-r member changes its output at v only if d ≤ r. This is asserted for every item (§2.4).

**Computation tree.** T\_t(v) is the depth-t non-backtracking unrolling of G\_F rooted at v.

**Message schedule.**

- Synchronous ("flooding"): every variable→clause message, then every clause→variable message.
- Serial schedules are excluded from the reference members, because one serial sweep can carry information across the whole graph and destroy the meaning of t. A serial variant exists only as a simulation option in E4.

**Colouring.**

- G = (N, E) with q named colours. Each node i has a list L\_i of allowed colours; a precoloured node has |L\_i| = 1.
- Distances are graph hops.

### 1.3 Members (pseudocode)

#### SAT / CSP

**`BP-t`** (sum-product for the uniform measure on satisfying assignments):

```
BP-t(F, t, δ = 0):
  μ[i→a] ← (½, ½)                          for every edge            # round-0 init: uninformative
  for r = 1 .. t+1:
     η[a→i] ← Π_{j∈∂a\i} μ[j→a](−s_{a,j})                            # P(all other literals of a are false)
     if r == t+1: break
     μ'[i→a](σ) ∝ Π_{b∈∂i\a} (1 − η[b→i]·1[σ ≠ s_{b,i}])
     μ[i→a] ← (1 − δ)·μ' + δ·μ[i→a]                                   # damping (δ = 0 by default)
  M_i(σ) ∝ Π_{b∈∂i} (1 − η[b→i]·1[σ ≠ s_{b,i}])
  if Σ_σ M_i(σ) = 0: CONFLICT(i)                                      # hard zeros (unit-forced contradiction)
  β_i ← M_i(+1) − M_i(−1)
```

- **BP-0 is weighted `POLARITY`.** log M\_v(+)/M\_v(−) = Σ\_{b ∋ ¬v} log(1 − 2^{1−|b|}) − Σ\_{b ∋ v} log(1 − 2^{1−|b|}). This is exactly `POLARITY` on 3-clauses, Jeroslow–Wang-like weights on mixed clause lengths, and unit clauses are decisive **[ours]**.
- **`BP-∞`:** iterate until max-change < 1e−6 or 200 rounds. If it hasn't converged at δ = 0, retry with δ = 0.5 and flag the run. Loopy BP can oscillate; when it converges it is often accurate (Murphy, Weiss & Jordan 1999, checked).

**Decision rules** (fixed before data):

- **R-assign:**
  - True if β > ε, False if β < −ε, with ε = 1e−9.
  - Ties go to a seeded coin and are scored as ½ likelihood each way. Variant: tie → False.
- **R-3way** (entailment, and "must" questions with a "can't tell" option):
  - "ℓ follows" if M(ℓ) ≥ 1 − τ;
  - "¬ℓ follows" if M(ℓ) ≤ τ;
  - otherwise "neither".
  - τ is chosen per model by maximum likelihood from {0.05, 0.1, 0.2, 0.3}; confirmatory analyses use τ = 0.2.
- **R-sat:** UNSAT iff a CONFLICT appears within the rounds; otherwise SAT with the R-assign assignment. A variant using the Bethe-entropy sign is secondary.

**`WP-t`** (warning propagation: the hard-decision limit, on the boundary with B1):

```
WP-t(F, t):
  u[a→i] ← 0
  for r = 1 .. t+1:
     h[j→a] ← Σ_{b∈∂j\a} s_{b,j}·u[b→j]                               # net cavity field
     u[a→i] ← Π_{j∈∂a\i} 1[h[j→a]·s_{a,j} < 0]                         # warn iff every other literal is pushed false
                                                                       #   (empty product = 1: unit clauses warn)
  H_i ← Σ_b s_{b,i}·u[b→i]
  contradiction(i) iff warnings arrive in both directions
  output: True if H_i > 0; False if H_i < 0; unforced if H_i = 0 (→ default rule)
  R-sat: UNSAT iff any contradiction
```

How WP-t relates to `UP-k`:

- WP sums warnings and does not stop at a conflict; UP reports the conflict.
- On conflict-free items, WP-t should derive exactly the literals UP-(t+1) derives. This is a unit test, not a citation **[ours]**.

**`SP-t`** (survey propagation; Braunstein, Mézard & Zecchina 2005, checked; equations as we implement them):

```
SP-t(F, t, K = 16 seeds):
  η[a→i] ~ U(0,1)                                                      # SP needs non-trivial init; η ≡ 0 is a fixed point
  repeat t rounds:
     for each edge (j, a):
        S = {b ∋ j, b ≠ a : s_{b,j} = s_{a,j}}      U = {b ∋ j, b ≠ a : s_{b,j} ≠ s_{a,j}}
        P_S = Π_{b∈S}(1 − η[b→j])                   P_U = Π_{b∈U}(1 − η[b→j])
        Π^u = (1 − P_U)·P_S        Π^s = (1 − P_S)·P_U        Π^0 = P_S·P_U
     η[a→i] ← Π_{j∈∂a\i} Π^u_{j→a} / (Π^u_{j→a} + Π^s_{j→a} + Π^0_{j→a})
  per variable:
     P+ = Π_{b: s_{b,i}=+1}(1 − η[b→i])             P− = Π_{b: s_{b,i}=−1}(1 − η[b→i])
     W+ ∝ (1 − P+)·P−        W− ∝ (1 − P−)·P+        W0 ∝ P+·P−        (normalised)
  per seed: True if W+ − W− > 0.1; False if < −0.1; else "unfrozen" (→ default)
  aggregate over seeds by majority
```

At our sizes, and at α below the clustering region, SP mostly converges to the trivial fixed point, so it outputs "unfrozen". SP matters only near threshold, in E4.

**Decimation** (seq):

```
BP-DEC-MAX(F, t_dec ∈ {1, 2, ∞}, UP = on):
  while unfixed variables remain:
     run BP-t_dec on F | fixed;   if CONFLICT: return FAIL
     i* ← argmax |β_i| over unfixed variables (ties: name order)
     fix x_{i*} ← sign(β_{i*}) (tie → True)
     if UP: unit-propagate to fixpoint;   if contradiction: return FAIL      # no backtracking
  return assignment

BP-DEC-OUT: identical, except i* = the next unfixed variable in the answer's output order    # "autoregressive decimation"
SP-DEC:     BP-DEC-MAX with SP biases. When SP reaches the trivial fixed point (all η < 1e−3), hand over to BP-DEC-MAX.
            (BMZ's handover to WalkSAT would be an E∘F hybrid; it is simulated only as a variant.)
FAIL → answer "UNSAT" (pre-registered).   Variant: FAIL → complete the partial assignment by R-assign.
```

**`BP-t-CAUSAL`** (transformer-specific variant: "prefix BP") **[ours]**:

- Order clauses by prompt position π(a).
- Run BP-t, but let the message μ[j→a] use only clauses b ∋ j with π(b) < π(a).
- The readout for target v (at the question, after the formula) uses all of v's clauses.
- Why: in a decoder-only model a clause's tokens attend only to earlier tokens. Evidence therefore reaches the answer only along position-increasing paths, plus whatever the answer position integrates itself. This is the abstract counterpart of the §1.7 program.

#### Graph colouring

```
BP-t colouring (q colours, lists L_i):
  ψ[i→j](c) ← 1/q for all nodes (including precoloured) at round 0
  repeat t rounds:
     ψ'[i→j](c) ∝ 1[c ∈ L_i]·Π_{k∈∂i\j}(1 − ψ[k→i](c))
     ψ ← (1 − δ)ψ' + δψ
  marginal ψ_i(c) ∝ 1[c ∈ L_i]·Π_{k∈∂i}(1 − ψ[k→i](c));   all zero → CONFLICT
  decision: argmax_c ψ_i(c); ties uniform (likelihood split)

WP-t colouring (singleton propagation = forward checking to depth t; B1 boundary):
  L^0 = L
  round r: L_i^r = L_i^{r−1} \ {c : some k ∈ ∂i has L_k^{r−1} = {c}};   empty list → CONFLICT

LOCAL-t colouring (Jones–Plassmann with fixed priorities ρ, truncated):
  ρ(i) = first-mention position (variant: degree descending, then first mention)
  repeat t rounds:
     every uncoloured i whose uncoloured neighbours all have larger ρ takes the first colour
     (in the prompt's colour order) in L_i not used by a coloured neighbour
  after t rounds: all remaining nodes simultaneously take the first colour unused by *coloured*
     neighbours (so adjacent late nodes may clash)
```

Two facts about `LOCAL-t` **[ours]**:

- **Limit.** As t → ∞ it outputs C1 `FIRST-FIT` in order ρ. A node fires only after all its higher-priority neighbours have, and it takes the colour sequential greedy would give it.
- **Failure profile.** At finite t it fails by *clashes* between adjacent nodes at the ends of long decreasing-priority chains. `FIRST-FIT` never clashes, so the violation profile separates the two.

#### Entailment as SAT

- The premises P are rendered from a CNF; the question is "Does ℓ follow?". Run BP-t, WP-t or SP-t on P and answer by R-3way.
- **E-specific error signatures:**
  - **Commission:** concluding something *probable but not entailed* (M(ℓ) ≥ 1 − τ). This separates E from B1, which errs only by omission.
  - **Omission:** answering "neither" for an entailed ℓ whose support lies beyond radius t.

#### Reference envelope and hybrids (zoo additions proposed here)

- **`LOCAL-EXACT-r`** (envelope; not message passing):
  - Solve the subformula C\_r(v) exactly by enumeration (≤ 30 variables).
  - Answer v's backbone value in C\_r(v) if it has one; else the majority value; UNSAT if C\_r(v) is UNSAT.
  - On tree-like balls it equals BP-r. On loopy balls it doesn't, and that difference separates "local" from "message passing".
- **`E-in-D`** (hybrid):
  - DPLL with BP-t value ordering: try sign(β) first. The variable choice is by |β|, or by the D vertical's rule.
  - Budget b. When the budget runs out, answer from the current BP-guided partial assignment.
  - This is how E would appear inside a search trace.
- **`EQ-CONTRACT+POL`** (B1∘C0 hybrid; a competitor we add):
  - Merge variables linked by 2-clause equivalences, then apply `POLARITY` to the merged variable.
  - Unlimited radius along equivalence chains; radius 0 elsewhere.

**Unit tests** (part of the build):

- BP-t equals brute-force marginals on trees.
- BP output is identical on a formula and its 2-lifts, at every t.
- BP-0 equals weighted `POLARITY`.
- WP-t equals UP-(t+1) on conflict-free items.
- `LOCAL-∞` equals `FIRST-FIT`.

| Problem model | Member | Reference implementation |
|---|---|---|
| SAT / entailment | `BP-t`, `BP-∞`, `WP-t`, `SP-t`, `BP-t-CAUSAL` | `src/reasoning_heuristics/heuristics/message_passing/sat_bp.py`, `sat_wp.py`, `sat_sp.py` |
| SAT | `BP-DEC-MAX`, `BP-DEC-OUT`, `SP-DEC` | `.../message_passing/decimation.py` |
| SAT | `LOCAL-EXACT-r`, `E-in-D`, `EQ-CONTRACT+POL` | `.../message_passing/envelope.py` (E-in-D calls D's `dpll.py`) |
| Colouring | `BP-t`, `WP-t`, `LOCAL-t`, `BP-DEC` | `.../message_passing/coloring.py` |
| Entailment | R-3way readout over the SAT members | `.../message_passing/entailment.py` |

### 1.4 Facts the designs rely on

1. **Locality.** rad(BP-t) = rad(WP-t) = rad(SP-t) = t. This follows directly from the update equations **[ours]**.
2. **Computation-tree (cover) invariance.**
   - BP-t, WP-t and SP-t outputs at v are functions of T\_t(v). So they are identical at corresponding variables of F and of any finite cover (lift) of F, for every t, including fixed points reached from lifted initialisations **[ours; standard]**.
   - Vontobel (2013, checked) makes the Bethe approximation exact as a statement about counting in graph covers.
   - LOCAL algorithms that use node identities can see cycles inside the ball, which is why `LOCAL-EXACT-r` is the envelope.
3. **Exactness on trees.** If C\_t(v) is a tree factor graph, BP-t's marginal at v is the exact marginal of v in C\_t(v), with distance-(t+1) variables free. Loops make BP double-count evidence.
4. **Nesting** **[ours]**:
   - BP-0 = weighted C0 `POLARITY`.
   - WP = UP without conflict detection.
   - Literals UP derives become hard zeros in BP.
   - `LOCAL-∞` = C1 `FIRST-FIT`.

   So the claims that are specific to E are **t ≥ 1 and soft**.
5. **Thresholds** (asymptotic in k):
   - BP-guided decimation fails on random k-SAT at density c·2^k ln 2 / k, below the 2^k ln k / k barrier (Coja-Oghlan 2011, arXiv 1007.1328, checked; report F cites the JACM version).
   - Low-degree polynomials fail above ≈ 4.911·2^k log k / k (Bresler & Huang 2021, report F).
   - Local algorithms find at most a 1/2 + 1/(2√2) fraction of the maximum independent set (Gamarnik & Sudan 2017; Rahman & Virág 2017; report F).
   - GNN/LOCAL approximation ratios are no better than simple greedy without extra features (Sato et al. 2019, report F).

   None of these gives a k = 3 number. The decimation-analysis papers checked (Montanari, Ricci-Tersenghi & Semerjian 2007; Ricci-Tersenghi & Semerjian 2009) state none in their abstracts either. **Every knee used here is simulated on our generator at our n.**

### 1.5 Expressibility

- **const:** `BP-t`, `WP-t`, `SP-t`, `LOCAL-t` for constant t.
  - Basis: Sato et al. 2019.
  - The transformer version is the §1.7 sketch: about 2 attention layers per round. It is not a theorem yet; report F lists it as a lead.
- **seq:** `BP-DEC`, `SP-DEC`, `BP-DEC-OUT`, `BP-∞`, `WP-∞`. Each fixing is followed by UP to fixpoint, and unit resolution is P-complete (Greenlaw–Hoover–Ruzzo compendium A.6.1, report F).
- **Caveat 1: output-as-decimation.** A full-assignment answer gives n sequential steps even with thinking off, so `BP-DEC-OUT` is available in "direct" mode. Only single-token target questions probe one pass.
- **Caveat 2: doubling.** Along chains (each variable in exactly two chain clauses), information can be composed by pointer-doubling. So fixed depth could reach radius ~2^{L/c} on chains.
  - Precedents: Ye et al. 2025 (adjacency powering to diameter 3^L) and Saparov et al. 2025 (exponential reachable-set growth), reports C and D.
  - We know of no such shortcut for soft BP on *branching* trees.
  - So the hard (chain) radius and the soft radius may scale differently with depth. E1 reports them separately.

### 1.6 What E looks like in a thinking trace

**E-explicit.** The trace shows:

- (a) per-variable tallies or "votes" from clauses;
- (b) **second-order votes**: a clause's vote for v weighted by its other literals' tendencies;
- (c) **sweeps** that update many variables before any commitment, then a later sweep that revises them;
- (d) graded language ("lamp leans True", "probably");
- (e) commitments only after the sweeps. In BP-DEC form: fix the most-biased variable, simplify, re-tally, never backtrack.

An example of the BP-1 pattern: *"Clause 7 is (lamp or cat or not door). Cat is negated in 3 of its other 4 clauses and door is mostly un-negated, so both literals are probably false here. Clause 7 hinges on lamp, which pushes lamp towards True."*

**E-implicit.** The trace is search-like or greedy, but its value choices and its guess at the cap follow E's marginals.

**Competitor trace signatures** (used in every eval's per-cell trace predictions):

| Family | Characteristic trace |
|---|---|
| B1 `UP-k` | Chains of "clause becomes unit → forced" from unit clauses. Categorical; no tallies. |
| B1∘C0 `EQ-CONTRACT` | "a = b = c = …" substitutions (code T10, §2.5), then a tally of the merged variable |
| C0 `POLARITY` / `MOMS` | One tally of each variable's own occurrences, then an assignment. No second-order reasoning. |
| C1 `GREEDY` / `FIRST-FIT` | Variables in mention order, each fixed once, no backtracking ("satisfies the most clauses so far") |
| C2 `UC` / `GUC` / `DSATUR` | Adaptive choice ("shortest clause", "most constrained") |
| D `DPLL-b` | Tentative decisions ("try x = T"), propagation, conflicts, backtracking. The answer comes from a finished search, or a default at the cap. |
| F `WALK-k` | A complete assignment, a clause check, flips of variables in violated clauses |
| H `SAMPLE-m` | Several complete candidate models, each checked against the conclusion |
| E-explicit | Sweeps, soft votes, second-order votes (above) |

### 1.7 RASP-L sketch (pre-registered before any LLM data)

**Pinned encoding.**

- A clause is rendered as `( l1 or l2 or l3 )`.
- A literal is ` name` or ` not name`.
- Names are single tokens in every tokenizer used.

**Program** (causal, one pass, t rounds unrolled):

```
open     = tokens == "("
cid      = numerical(aggregate(select(indices, indices, <=), open)) · width   # clause index = prefix count of "("
                                                                                #   (needs selector width: dialect-dependent)
negated  = shift(tokens == "not", 1)                                            # sign of the next literal
vid      = tokens                                                               # single-token names: identity = token
same_var = select(vid, vid, ==)                                                 # earlier mentions of the same variable
same_cl  = select(cid, cid, ==)                                                 # earlier tokens of the same clause
s_0      = numerical(aggregate(same_var, sign(negated)))                        # BP-0 / POLARITY state
for r in 1..t:                                                                  # per round: 2 selects + 2 maps
    pf   = numerical(map(log_p_false, s_{r−1}, negated))                        # log P(this literal false), int8 log-odds
    clm  = numerical(aggregate(same_cl, pf))                                    # at clause end: sum over earlier literals
    msg  = numerical(map(log1m_exp, clm − pf))                                  # log(1 − η) toward this literal's variable
    s_r  = numerical(aggregate(same_var, msg · sign))                           # accumulated at later mentions
answer   = map(threshold, s_t at the question token naming v)
```

**Size.** About 7 + 4t primitive lines; depth about 1 + 2t attention layers. `WP-t` has the same skeleton with boolean maps, which fit int8 natively. `BP-t` needs quantised log-odds lookup maps: same depth, larger maps.

**Predictions committed to now:**

- **P1: radius in one pass.**
  - Round by round, r\* ≤ (L − 1)/2. Given that later layers mostly refine (Csordás et al. 2025, report C), we expect r\* ≲ L/4.
  - Layer counts are from the HF `config.json` files, fetched this session: Qwen3-4B and 8B have 36 layers, 14B 40, 32B 64; gpt-oss-20b 24, gpt-oss-120b 36.
  - That gives upper bounds of about 9 (4B / 8B), 10 (14B), 16 (32B), 6 (gpt-oss-20b) and 9 (gpt-oss-120b).
  - **If r\* is set by depth, Qwen3-4B ≈ 8B (equal depth, different width) and gpt-oss-120b ≈ Qwen3-8B (both 36 layers).** This is a cheap behavioural test in the `direct-ladder` condition. Tiny models are excluded, so the 0.6B-vs-1.7B pair is not used.
- **P2: causal mask.** Evidence travels along position-increasing paths (`BP-t-CAUSAL`), so chain order and edit placement matter (E1).
- **P3: hard vs soft.**
  - WP-t is no deeper than BP-t, and it is shorter under any precision-weighted length measure.
  - The RASP MDL principle (Zhou et al. 2024, report D) therefore predicts *hard* messages unless soft marginals buy accuracy on the training distribution. E2 decides this.
- **P4: thinking.**
  - Iterating the round program in CoT is n-RASP-L (Fan et al. 2025, report D). E-explicit predicts r\* growing roughly linearly with thinking tokens.
  - Decimation iterates a short per-step program. DPLL also needs a stack for backtracking, so its per-step program is longer.

---

## 2. Behavioural evidence (Phase 1)

### 2.1 Models and conditions

**Primary models.** All are open-weight with raw traces visible.

- **Run order:** gpt-oss-20b at reasoning effort "high" is the **first model**. It runs the pilot (n\* calibration, token use, truncation rates) and every dev batch (§5). The others follow once the dev batches pass.
- **No tiny models** (Andrew's instruction). Qwen3-0.6B and 1.7B are dropped everywhere, including the diagnostic ladder.
- Qwen3-14B, Qwen3-32B, Qwen3-30B-A3B (thinking mode) and Qwen3-235B-A22B-Thinking-2507: 40, 64, 48 and 94 layers.
- gpt-oss-20b and gpt-oss-120b at reasoning effort "high": 24 and 36 layers.
- DeepSeek-R1.
- DeepSeek-R1-Distill-Qwen-14B (48 layers) and R1-Distill-Qwen-32B.

Layer counts are from HF `config.json`, fetched this session; R1's and R1-Distill-Qwen-32B's were not checked.

| Code | Condition | Role |
|---|---|---|
| `think-hi` | Thinking on, highest effort, thinking cap 32,768 tokens, answer cap 1,024. Each model's recommended sampling (e.g. Qwen3 thinking T = 0.6, top-p 0.95; gpt-oss T = 1.0). | **Primary** |
| `think-B` | Budget forcing at B ∈ {512, 2k, 8k}: stop thinking at B tokens, close the thinking block, force the answer | Diagnostic: radius vs budget (P4) |
| `direct` | Thinking off, greedy decoding, with logprobs: Qwen3 `enable_thinking=False`; R1 and R1-distills with an empty thinking block prefilled; gpt-oss at "low" effort, reported separately because it still thinks briefly | Diagnostic: one forward pass |
| `direct-ladder` | Qwen3-4B / 8B / 14B / 32B, thinking off. 4B is the smallest kept; drop it if Andrew counts it as tiny, at the cost of the 4B-vs-8B equal-depth contrast. | Diagnostic: radius vs depth (P1) |

**Rules** (DESIGN §5):

- Runs that hit the 32k cap are censored. The answer forced after the cap is analysed as its own stratum.
- 3 samples per item on a fixed 20% subset.
- Manifests record exact model versions.
- **n\* (the budget line) is measured in a pilot per model family.** It is the core size at which `think-hi` accuracy on core-only backbone questions is 50%. Priors: 32–48 variables at α = 4.1.

### 2.2 Predicted error signature

**Omission or commission? Both, by a stated rule.**

- **Commission** when the local marginal is confident and wrong: soft evidence opposes the backbone, or loops double-count.
- **Omission** ("neither") when the decisive constraint lies beyond radius t.
- In entailment, E commits to probable-but-not-entailed conclusions. B1 never does.

**Infeasible, or feasible but suboptimal?**

- `BP-t` plus rounding: infeasible assignments with violations scattered over the formula.
- `BP-DEC` with UP: a satisfying assignment or FAIL (→ false UNSAT), with no near-misses.
- `LOCAL-t` colouring: clashes between adjacent late-priority nodes.

**Thresholds.** Simulated success-vs-α curves (E4).

**Size invariance** (a signature of E that doesn't depend on n). With the local structure fixed, E's answer about v doesn't change as the rest of the formula grows. `NOISY-EXACT` and truncated search predict errors rising with n (E1-S growth arm).

### 2.3 What separates E from each competitor

| Competitor | What it shares with E | Separating contrast | Eval |
|---|---|---|---|
| C0 `POLARITY` / `MOMS` (= BP-0) | Locality | Second-order evidence (radius ≥ 1) | E2 (A vs B), E1 (d ≥ 1), E5 (t = 0 vs t ≥ 1) |
| B1 `UP-k`, `WP-t` | Locality; hard forcing | Soft evidence with no unit clauses anywhere | E1 soft channel, E2 |
| B1∘C0 `EQ-CONTRACT+POL` | Soft evidence along chains | No radius step | E1 |
| A2 `DENSITY` / `LENGTH` / `RECENCY` / negation counting | — | Surface-balanced cells; semantic no-op nulls; placement factor; growth arm | E1, E2 |
| C1 `GREEDY` / `FIRST-FIT` | Order-driven cascades can mimic a radius | First-mention order (E2-O); chain order (E1-C); open vs blocked paths (E6); false "impossible" on even cycles (E3) | E1-C, E2, E3, E6 |
| C2 `UC` / `GUC` | Adaptive choice | Decision-sequence likelihood in traces; knee | E4, E6b |
| D `DPLL-b` | E may be its value heuristic (`E-in-D`) | Soft effects only on unfinished runs; retraction after a flipped commitment; peaked token-vs-α curve | E1-C, E2, E4, E6b |
| F `WALK-k` | Local and soft-ish | Complete-assignment traces; near-miss violation profile; never certifies UNSAT | E3, E4 |
| H `SAMPLE-m` / exact sampler | Tracks marginals | Loops and lifts (exact ≠ BP); no radius | E5b, E1 |
| `LOCAL-EXACT-r` (envelope) | Locality | Computation tree vs ball (cycles; unanchored covers) | E3, E5a loopy |
| `NOISY-EXACT` | — | Errors rising with n at fixed local structure | E1-S growth |

### 2.4 Shared item machinery and confound control

1. **Sparse vs dense.**
   - At α ≈ 4.26 a random 3-SAT variable appears in about 3α ≈ 12.8 clauses, each with 2 other variables. So it has about 25 neighbours, and nearly every pair of variables is within 2 hops at n ≤ 60.
   - Radius therefore needs **constructed** sparse, tree-like neighbourhoods (E1, E2 periphery, E3).
   - Threshold signatures (E4) use random 3-SAT.
   - Items that must be *above budget* and also *locally controlled* use the **periphery–core** design (E1-C, E2):
     - a random core K at n\* and α = 4.1, satisfiable;
     - a backbone variable c\* chosen to be as BP-uninformative as possible: the least max\_t |β\_t| over backbone variables, required < 0.3 for t ≤ 8 and at the fixed point. A stricter bound of 0.1 found no core in 5,000 seeds at n = 10. BP-1 at v cannot see the core at all (c\* is 2 hops away), and periphery dominance at t ≥ 2 is verified per item;
     - the link v ≡ u ≡ c\* (2-clause equivalences, one positive and one negative occurrence of v), so truth(v) = backbone(c\*);
     - a controlled tree-like periphery around v.
2. **Semantic no-op nulls.**
   - Flipping a literal of a variable that occurs only once is the renaming x ↦ ¬x. That is an isomorphism of the solution space, so every procedure that reads the semantics is invariant, and only surface procedures can react.
   - Each null is matched to its effective edit in the number of literals flipped, in token count, and in distance.
   - For colouring, the null is renaming a free pendant node.
3. **Surface balancing.** Residual count differences between cells (negations, occurrences per variable, clause lengths) are cancelled by further degree-1 flips at least 8 hops from v, or in a disconnected filler. These are also semantic no-ops.
4. **Token distance vs graph distance.**
   - Clause and literal order are shuffled uniformly; then edited clauses are placed by design (E1-S: early vs late; E1-C: chain order).
   - The token distance from each edit to v's mentions and to the question is a covariate in every analysis, and a crossed factor in E1-S.
5. **Names.**
   - A pool of 256 words, each a single token with its leading space in the Qwen3, gpt-oss (o200k) and DeepSeek tokenizers (checked by script).
   - A fresh random mapping per item. No numbering along chains, so names never encode position.
   - NL renderings use v1's theme templates.
6. **Tokens and length.**
   - Negation is rendered as the word ` not` (one token everywhere), not "¬".
   - Every minimal pair or triple is asserted equal in token count under each tokenizer; failures are regenerated.
7. **Verification.** An item enters the set only if every family's prediction in its cell matches the design tables below. The cell predictions in this document are therefore *checked properties of the items*. Each item gets:
   - satisfiability and backbone (PySAT), and exact marginals by model counting (E5);
   - `BP` / `WP` / `SP`-t for t = 0..8 and ∞, `UP-k`, `LOCAL-EXACT-r`;
   - every competitor's prediction from the other verticals' reference code: C0, C1, C2, D with b ∈ {0, 16, 256}, F with k ∈ {50, 500}, H.
8. **Hashing.** Items are content-hashed, and minimal pairs store their source hash (DESIGN §5.1–5.2).

### 2.5 Trace-coding scheme (shared across evals)

**Step 1: segment.** Split the thinking text at line breaks and sentence boundaries, and number the steps.

**Step 2: automatic parser** (deterministic, no LLM; whole-word matching on the item's names). It extracts:

- **value statements** (variable, value, modality), where modality is one of:
  - *commit:* "set X to True", "X = T", "X must be";
  - *tentative:* "try X", "suppose";
  - *soft:* "likely", "probably", "leans", "tends";
  - *retract:* "undo", "can't be".
- **tallies:** "appears 3 times positively", "two clauses want X true";
- **clause references and propagation:** "becomes unit", "forced", "implies";
- **conflict and backtrack cues:** "contradiction", "backtrack", "try the other value";
- **complete-assignment listings** (≥ 80% of variables valued in one step) and **clause checks**.

**Step 3: LLM-assisted coder.**

- It is blind to cell, model and ground truth. It sees the numbered steps, the name list and the formula.
- It labels each step as one of: tally, second-order vote, soft belief, tentative assignment, commitment, propagation, conflict, backtrack, sweep start, complete assignment, verification, equivalence contraction, other.
- It also marks **dependency links**: which earlier steps a step relies on.
- Coding runs in 4k-token windows with 512 tokens of overlap.
- The coder is an open model (e.g. Qwen3-235B-A22B, non-thinking) so the pipeline is reproducible. A second coder model on a 20% subset estimates how much results depend on the choice of coder.

**Step 4: validation.**

- Two human coders, also blind, independently label 3,000 steps from 120 traces, stratified by model × eval × cell.
- Report Cohen's κ per category for human–human and human–LLM agreement, and precision and recall for the parser's extractions.
- A category is used in confirmatory analyses only if human–LLM κ ≥ 0.70 *and* ≥ 0.9 × the human–human κ. Otherwise it is exploratory.
- All κ values go in the paper.

**Step 5: synthetic-trace positive control** (run before any real trace is coded).

- Scripted generators emit paraphrase-varied natural-language traces of BP-1 sweeps, BP-DEC, UP chains, DPLL with backtracking, GREEDY and WalkSAT.
- The parser and coder together must recover the generating procedure with accuracy ≥ 0.85.

**Derived measures per trace** (definitions pre-registered):

| Code | Measure | Definition |
|---|---|---|
| T1 | Sweep index | Number of windows in which ≥ 60% of the variables within 2 hops of v get a tally, soft or second-order statement with no commitment in between. A window counts only if a later window revisits ≥ 60% of the same variables and changes at least one belief. |
| T2 | Soft rate | Soft value statements / all value statements |
| T3 | Second-order rate | Second-order votes / all statements justifying v's value |
| T4 | Trace radius | TR\_v = max graph distance from v among variables in steps linked (by coded dependency) to the final statement about v. TR\_all = max distance of any variable mentioned. |
| T5 | Edit mention | Whether the edited clause or variable is mentioned, and whether it is in v's dependency set |
| T6 | Commitment sequentiality | Fraction of commitments followed by propagation from that commitment before the next commitment |
| T7 / T8 / T9 / T10 | Counts | Backtracks; decisions; complete-assignment checks; equivalence contractions |
| T11 | Decision-sequence likelihood (DSL) | Each parsed commitment's log-probability, given the trace's *own* current simplified formula, under each family's selection rule (softmax with a fitted temperature per family): `BP-DEC-MAX` (most biased, sign value), `GUC` / `SC` (shortest clause), MOMS-DPLL, `POLARITY` order, `INPUT-ORDER` (C1). Forced (unit) moves are counted separately, because every UP-using family makes them. |
| T12 | Budget | Thinking tokens used; truncation flag |

**Trace classification.** A multinomial model over T1–T11 with each family's predicted profile (§1.6), fitted by maximum likelihood per trace.

### 2.6 Faithfulness tests (does the trace match the answer?)

| Code | Test | Procedure | What it licenses |
|---|---|---|---|
| FT1 | Final-statement consistency | P(final answer = last trace statement about v) | Sanity baseline |
| FT2 | Counterfactual verbalisation | On minimal pairs whose answers differ: P(trace mentions the edit), P(edit in v's dependency set). On pairs whose trace uses the edit: P(answer changes). | Whether the trace carries what drives the answer. Hints are verbalised in only ~25–39% of cases (Chen et al. 2025, report C). |
| FT3 | Early answering | Truncate the trace at 0 / 10 / 25 / 50 / 75 / 100% and force an answer (Lanham et al. 2023, report C). The 0% point is a pre-commitment check (cf. Cox et al. 2026, report C). | If the answer is fixed near 0%, the procedure the trace describes is post hoc |
| FT4 | Trace-state intervention | E6b: flip one committed value in the trace text and continue | Whether the states written in the trace are used |
| FT5 | Channel agreement | Per item, κ between the family that best explains the answer and the family assigned to the trace | The headline faithfulness number |

**Trace reliability weight per model:** w = min(FT2 verbalisation rate, 1 − FT3 pre-commitment).

- FT3 pre-commitment is the agreement at 10% truncation minus the agreement of a no-information baseline.
- Both quantities lie in [0, 1].

### 2.7 How trace and answer evidence combine

- **Answers are the confirmatory channel.** They are scored with no LLM in the path (DESIGN §5.4).
- **The trace is a second, unreliable channel,** handled like Glöckner's (2009) process measures (report B).
- **Joint likelihood per model:** log L(h) = log L\_ans(h) + w · log L\_trace(h). Report w = 0 (confirmatory) and w = ŵ (exploratory).

**Trace quantity.** s\_E^trace = (traces classified E-explicit) / (all traces), reported raw and multiplied by w, with a bootstrap interval over items.

**How the two channels combine** (pre-registered; every entry is a quantity, not a verdict):

| Answer channel: π\_E (95% interval) | Trace channel: w · s\_E^trace | Reported reading |
|---|---|---|
| Lower bound > 0 | High | E used explicitly, with weight π\_E |
| Lower bound > 0 | Low | E used *implicitly* (as a value heuristic) with weight π\_E, provided FT3 shows the answer is not fixed before the trace. Otherwise the weight is attributed to pre-committed E-like answers. |
| Upper bound small (≤ 0.1) | High | Message passing verbalised but not used. This moves weight away from E, and lowers w for the model. |
| Upper bound small (≤ 0.1) | Low | π\_E bounded near zero in this condition |

**The trace never moves π\_E on its own.** Through w it can only re-apportion weight among families the answers cannot separate (e.g. `E-in-D` vs D-POLARITY on unfinished runs), and only for models with w ≥ 0.5.

### 2.8 Evals

---

#### E1. Locality and radius (LOC)

**Hypothesis H-E1.** The answer about v depends on the formula only through C\_r(v), for a finite effective radius r\*.

- Edits at d ≤ r\* move the answer in E's predicted direction.
- Edits at d > r\* move it no more than the matched no-op nulls do.
- **One pass (diagnostic):** E requires r̂\_soft ≥ 1. Otherwise the behaviour is C0, or B1 if only the hard channel responds.
- **Best effort (primary):** on items above the budget line, does the fallback answer depend on *local soft* evidence, and over what distance?

##### E1-S (sparse; diagnostic)

**SAT skeleton.**

- **v and its chain.** The target v is the root of the test branch, an equivalence chain v = c\_0 ≡ c\_1 ≡ … ≡ c\_8. Each link is the pair (c\_i or not c\_{i+1}), (not c\_i or c\_{i+1}).
- **Pendants.** Each c\_i carries a balanced pendant pair of 2-clauses (c\_i or l), (not c\_i or l′) with fresh degree-1 leaves. The pair adds zero net bias.
- **Cycles.** Each 2-clause equivalence pair is a 4-cycle in the factor graph (two clauses on the same two variables). So within C\_9(v) the only cycles are the designed equivalence pairs. Consequences, verified on the example items:
  - the exact marginal passes along the chain unattenuated;
  - BP *over-amplifies* it, double-counting around each pair (e.g. exact 0.89 vs BP-3 1.00);
  - locality is unaffected: BP-t still responds only to edits at d ≤ t.
- **v's own polarity.** v carries two more balanced pendant pairs, so its own polarity is tied.
- **Filler.** A satisfiable filler (20 variables, α = 2, tree-like) is attached at least 10 hops from v. Decoy equivalence pairs inside the filler keep equivalences from flagging the test branch.
- **Size.** n ≈ 50 variables, m ≈ 80 clauses.

**Channels.**

- **Hard channel.**
  - The hub at c\_d is the unit clause (c\_d) or (not c\_d).
  - Effective edit: flip the unit's sign. Truth(v) flips.
  - Question (single token): "Every satisfying assignment gives v the same value. Which value?"
- **Soft channel.**
  - The hub is c\_d in 3 extra pendant 2-clauses (c\_d or h\_k), all with the same sign, where the h\_k are fresh degree-1 leaves. The exact P(c\_d) is 1/(1 + (1/2)³) ≈ 0.89; v's exact marginal is 0.89 in the example item.
  - Effective edit: flip c\_d's sign in those 3 clauses (0.89 → 0.11).
  - v is free, so the question is a preference: "Give v's value in a satisfying assignment of your choice."
- **Null edit.**
  - Soft channel: flip the *leaf* literal h\_k in the same 3 clauses. The clauses and token counts are identical; only which word carries `not` differs.
  - Hard channel: flip the leaf literal of the pendant (c\_d or l) placed next to the unit clause.

**Factors.**

- channel {hard, soft} × d ∈ {1, 2, 3, 4, 6} × placement (edited clauses in the first 15% of the clause list or the last 15%) × version {base, effective, null};
- edit direction balanced;
- **growth arm** (at d = 2): add 40 clauses on 20 fresh, disconnected variables (~45% more tokens).

**Colouring analogue.**

- **Diamond chains.** A diamond is u–a, u–b, a–b, a–w, b–w; in 3-colouring it forces col(u) = col(w). d is counted in hops: 2, 4, 6, 8 or 12, i.e. 1–6 diamonds.
- **Hard channel:** the hub is precoloured, and the edit swaps Red ↔ Blue.
- **Soft channel:** the hub's two free neighbours are each adjacent to a node precoloured X. BP gives P(hub = X) ≈ 0.67. The edit changes X from Red to Blue for both.
- **Null:** rename a free pendant node.
- Diamonds contain triangles, so BP is loopy here. Radius semantics still hold, but `LOCAL-EXACT` ≠ BP on these balls; both are simulated per item.

**Predicted effect: (effective − null) shift toward the edit's direction.**

| Family | Hard, d ≤ r | Hard, d > r | Soft, d ≤ r | Soft, d > r | Placement | Growth |
|---|---|---|---|---|---|---|
| Truth / exact | + at every d | + | n/a (free) | n/a | none | none |
| E `BP-t` | + | 0 | + | 0 | none | none |
| E `WP-t` | + | 0 | 0 | 0 | none | none |
| E `BP-t-CAUSAL` | + | 0 | + | 0 | late placement shrinks the step | none |
| E-explicit (thinking) | + with r growing in budget | | + | | none | none |
| `E-in-D` (DPLL with BP-2 values) | + at every d | + | + at every d (sequential conditioning extends its reach: no step) | + | order-dependent | none |
| B1 `UP-k` (rad k−1) | + | 0 | 0 | 0 | none | none |
| B1∘C0 `EQ-CONTRACT+POL` | + at every d | + | + at every d | + | none | none |
| C0 `POLARITY` / `MOMS` | 0 | 0 | 0 | 0 | none | none |
| C1 `GREEDY` | + iff the chain is mentioned hub→v (any d) | same | same | same | strong | none |
| D (thinking, finishes) | + at every d | + | via value order only | | none | none |
| F `WALK-k` (k = 60) | + **decaying** with d (example: 0.95 → 0.27) | | + without a step (0.34–0.45 for d ≤ 4, 0.10 at d = 6) | | none | small |
| H exact sampler | + | + | + at every d (0.78 in the example) | + | none | none |
| A2 cues (`RECENCY`, negation counts) | 0 vs null (matched) | 0 | 0 | 0 | late > early at every d | `LENGTH-PRIOR`: ± |
| `NOISY-EXACT` | +, slips growing with d | | | | none | errors ↑ |
| `PERCEPTION-NOISE` (one misread literal) | + decaying slowly (0.85 → 0.65) | | + decaying slowly (0.60 → 0.50) | | none | none |
| `RANDOM` | 0 | 0 | 0 | 0 | none | none |

**Only one-shot E members predict a step in d.**

- BP-t steps at the same r on both channels; WP steps on the hard channel only.
- The step is placement-free in the abstract form and placement-dependent in the causal form. In the example, BP-2-CAUSAL's d = 1 soft effect is 1.00 with early placement and 0 with late placement (sign readout; the graded marginal shift is 0.81).
- `WALK-k` and `PERCEPTION-NOISE` *decay* gradually. The sampler, `EQ-CONTRACT` and UP-to-fixpoint are flat in d.
- The step-vs-decay model comparison therefore separates E from F and from the noise nulls.
- All numbers in this table that are not ± signs were computed on the example items in [E\_message\_passing\_questions.md](E_message_passing_questions.md).

**Trace predictions** (thinking subset, hard channel).

- Every UP-using family predicts the same trace here: a chain of forced steps, with T6 high and TR\_v = d.
- So this arm is a **sanity check, not a discriminator.** We expect thinking models to propagate globally.

##### E1-C (periphery–core; primary for thinking)

**Item.**

- **Core and link.** Core K at n\*, with a BP-uninformative backbone variable c\* and the link v ≡ u ≡ c\*.
- **Periphery.** The equivalence chain v ≡ p\_1 ≡ … ≡ p\_6 with a hub slot at p\_d, d ∈ {1, 2, 4, 6}, plus balanced pendants.
- **Hub evidence S** ∈ {toward truth, neutral (2:2), against truth}, set by p\_d's sign in 4 pendant 2-clauses (p\_d or h\_k) with fresh leaves. In isolation this is P ≈ 1/(1 + (1/2)⁴) ≈ 0.94 toward S; neutral gives 0.5.
  - p\_d is forced too, via v ≡ c\*, but "against" leaves remain satisfiable through their leaves.
  - Truth never changes across S.
- **Chain order O** ∈ {the chain's clauses appear hub→v; v→hub}. Positions are otherwise random.
- **Question:** "Every satisfying assignment gives v the same value. Which?" A 10% calibration subset adds a "can't tell" option.

**Primary contrast:** accuracy(toward) − accuracy(against), per d and O.

| Family | d ≤ r | d > r | Order effect |
|---|---|---|---|
| Truth; D that finishes | 0 | 0 | none |
| E `BP-t`; E-explicit (unfinished runs) | large + | 0 | none (abstract); hub→v larger (causal) |
| `E-in-D` | + on unfinished runs | 0 | none |
| D-POLARITY, truncated | 0 (v's own polarity is fixed) | 0 | none |
| C0 | 0 | 0 | none |
| B1 `UP-k` | 0 (no unit clauses) | 0 | none |
| `EQ-CONTRACT+POL` | + | + | none |
| C1 `GREEDY` | + if hub→v, at any d | same | hub→v only |
| F `WALK-k` | small +, falling with d | | none |
| H; `NOISY-EXACT` | 0 | 0 | none |

**Trace predictions per cell** (toward vs against).

| Family | Trace |
|---|---|
| E-explicit | Tallies the hub's leaf clauses and passes the tendency along ("p\_4 leans False and p\_4 = … = v, so v leans False"). Soft language; the answer follows S for d ≤ TR\_v. |
| `E-in-D` | Search on the core. v's value (or the chain's) is guessed with a justification citing the hub. On unfinished runs the guess survives to the answer. |
| D | Search on the core. The periphery is touched only through propagation; S is never given as a reason. |
| `EQ-CONTRACT` | "v, p\_1, …, p\_d are all equal" (T10), then the merged variable's polarity |
| C1 | Assignments in mention order. Under hub→v order, the hub's value is set first and copied along the chain. |
| C0 | Tally of v's own occurrences |

**Pre-registered CoT hypotheses (E1).**

- **CH1a (E-explicit):** T1 ≥ 2 and T3 > 0 in ≥ 20% of E1-C `think-hi` traces. Within those traces, the answer follows S for d ≤ TR\_v.
- **CH1b (E-implicit):** the S-effect is present on runs that don't finish the core search and absent on runs that do.
- **CH1c (reach):** the edit-mention rate (T5) falls with d under E, and is flat in d under D (where mentions follow search order).
- **CH1d (budget):** under `think-B`, the hard-channel r̂ on E1-S grows with B. E-explicit and UP predict roughly linear growth; D predicts a jump to global once B covers the cost of propagating along the chain.

**Confounds.**

- Semantic no-op nulls; placement and chain-order factors; token-distance covariate; surface balancing; random names; the growth arm tests length directly.
- **Conditioning on run completion is post-treatment** (the edit can change whether a run finishes). The primary analysis is unconditional; CH1b is exploratory.

**Generator recipe.**

- **E1-S:**
  1. build the chain and pendants;
  2. attach the hub gadget at c\_d;
  3. add filler and decoys;
  4. shuffle clauses and literals, then place the edited clauses by the placement level;
  5. render;
  6. derive the effective and null variants;
  7. verify:
     - within C\_9(v) the only cycles are the designed equivalence pairs;
     - the BP-t step falls at t = d;
     - the UP-k step falls at k = d + 1 (hard channel);
     - v is backbone in the hard channel and free in the soft channel;
     - token counts are equal.
- **E1-C:**
  1. sample cores at n\* until satisfiable with ≥ 30% backbone;
  2. pick the backbone variable with the least max\_t |β\_t| (< 0.3), and log the rejection rate in the pilot;
  3. attach the link and periphery;
  4. impose the order;
  5. verify:
     - truth(v) = backbone(c\*);
     - BP-t at v follows S iff t ≥ d;
     - UP is silent;
     - C0 is constant across S;
     - C1 behaves per order;
     - D-POL and WALK predictions are simulated.

**Answer format and metric.**

- Single word (True/False, or a colour).
- **E1-S, direct:** Δlogit of the effective edit vs base and of the null vs base.
  - r̂ = the largest d with (effective − null) > δ\_min, where δ\_min = 0.25 logit or 8pp. Tested one-sided with Holm correction.
  - Also a segmented logistic fit with bootstrap CI, compared against a geometric-decay model. A step favours E; decay favours noisy propagation (slips per hop).
- **E1-C:** mixed logistic regression of accuracy on S × d × O, with random intercepts for core and skeleton.

**Weight statements** (what E1 estimates, and how precisely).

- **The model.** The observed effect vector over cells (d, channel, placement or order) is modelled as Σ\_h π\_h δ\_h + ε. Here δ\_h is family h's *computed* effect vector, as tabulated in the question library, and ε is noise with the design's per-cell SE. A least-squares or Bayesian fit gives π for every family, including `BP-t` at each t, which yields a posterior over r\*.
- **Resolution between two families h and h′** is se(π̂) ≈ SE\_cell / ‖δ\_h − δ\_h′‖. Computed on the E1-S example items:
  - BP-1 vs C0, vs `UP-k` and vs exact: ‖Δ‖ = 1.0;
  - BP-1 vs the flat sampler: 1.57;
  - BP-3 vs `EQ-CONTRACT`: 1.41.
  - At SE\_cell ≈ 0.05 (full study) that means π ≥ 0.09–0.15 is detectable, and an absent competitor is bounded at π ≤ 0.05–0.09 (upper 95%).
  - At dev-batch size (SE\_cell ≈ 0.19) only π ≳ 0.35–0.55 is detectable.
- **The question library gives these per pair** (resolution tables in each set).
- **What moves weight:**
  - a step at d ≤ r̂ and flat nulls → weight onto `BP-t` with t ≈ r̂ and away from C0, B1, the sampler and `EQ-CONTRACT`;
  - decay instead of a step → weight onto F and `PERCEPTION-NOISE`;
  - an O main effect without a d-step → weight onto C1.
- **Feature terms.** Whether π\_E depends on placement or order (i.e. `BP-t-CAUSAL` vs abstract BP) is reported as ΔLL for the interaction term.
- **Power at full size** (computed):
  - E1-S: π\_BP-t ≥ 0.15 (80%) against each listed competitor.
  - E1-C (SE\_cell ≈ 0.085): BP-2 vs C0 / `UP-k` / exact / `EQ-CONTRACT` gives ‖Δ‖ = 2.0, so π ≥ 0.12 is detectable and absent competitors are bounded at ≤ 0.07. BP-2 vs C1 or vs BP-2-CAUSAL gives ‖Δ‖ = 1.41, so π ≥ 0.17 is detectable and the bound is ≤ 0.10.

**Sample size and power.**

- **E1-S:** 80 skeletons per channel per domain, giving 160 effective/null triples per (channel, d) cell.
  - With an assumed paired SD of Δlogit ≈ 1.0, the minimal detectable effect is MDE = 2.8/√160 ≈ 0.22 logit (α = .05, power .8).
  - With binary flips under `think-2k` (null-flip rate ≈ 0.15), 160 triples detect 0.15 → 0.30 with power ≈ 0.88.
- **E1-C:** 48 skeletons × 2 orders = 96 toward/against pairs per d.
  - McNemar test with discordance ≈ 0.35: a 20pp difference is detected with power ≈ 0.90; 15pp with ≈ 0.68. The pooled d-trend model does better.
  - The O effect pools d ≥ 2 (144 pairs per level): MDE ≈ 13pp.

**Threats to validity.**

1. **Attenuation vs radius.**
   - Equivalence pairs avoid attenuation: transmission is exact for the exact marginal.
   - BP over-amplifies them through the 4-cycle each pair forms, which sharpens rather than blurs its step.
   - The step-vs-decay comparison guards against slips accumulating per hop. `WALK-k` and `PERCEPTION-NOISE` produce decay on the example items.
2. **The contraction shortcut.** Covered by the `EQ-CONTRACT` competitor and code T10.
3. **Salient structure.** Equivalence pairs stand out; decoys in the filler counter this.
4. **BP-uninformative backbone variables may be rare at α = 4.1.** Fallback: a parity-forced anchor, which is BP-invisible but easy for thinking models. It changes whether the item is above budget, and is flagged when used.
5. **Cores differ across model families** because n\* differs. Compare models through effect sizes relative to their own n\*.
6. **Preference questions invite default answers.** The base/effective/null contrast removes main effects of the default.

---

#### E2. Soft vs hard: second-order evidence (SOFT)

**Hypothesis H-E2.** When v isn't forced locally, the answer follows v's BP-1 marginal, i.e. its neighbours' tendencies. It does so beyond v's own polarity (C0), regardless of processing order (C1), and when it opposes the truth.

**Design** (periphery–core, same core machinery as E1-C).

- **Local clauses and satellites.** v has 4 local 3-clauses, each with two fresh satellite variables. Each satellite has 3 pendant 2-clauses (s or l) with a common sign and fresh leaves, so its cavity marginal is 1/(1 + 1/8) ≈ 0.89 toward that sign. v is also linked to the core by v ≡ u ≡ c\*.
- **Why 3 pendants.** With 2 pendants (tendency 0.80), the verifier rejected the first example core in 4 of 24 cells. BP-2 and BP-4 double-counted c\*'s weak bias (0.27) through the link's equivalence 4-cycles and overrode B in the A-opposed cells. Three pendants plus c\* bias < 0.2 pass in all 24 cells.
- **Factors:**
  - **A (own polarity)** of the 4 local clauses: (3+, 1−), (2+, 2−), (1+, 3−).
  - **B (second-order evidence):**
    - pro-T: v's positive local clauses are *critical* (both satellite literals likely false) and its negative ones *slack* (both likely true);
    - pro-F: the reverse.
  - **D (truth):** set by the link's sign (v ≡ c\* or v ≡ ¬c\*). Both forms give v one positive and one negative occurrence.
  - **O (order):**
    - sat-first: every satellite is first mentioned before v;
    - v-first: v's local clauses come first.
    - v's link clauses (its last mentions) come last in both levels.
    - The intent was that only C1's first-mention processing would differ. **Verification showed otherwise:** in v-first order the satellite evidence arrives after v's clauses, so `BP-t-CAUSAL` loses it too. The computed B×O interaction is 0.66 for BP-2-CAUSAL, against 1.0 for C1 and 0 for abstract BP.
    - So O separates *abstract* E from {C1, causal E}. **C1 vs causal E is separated by E1-C's chain-order profiles** (C1 [+++000+0] vs BP-2-CAUSAL [+0+00000] in the example items).
- **Cells:** 24 per skeleton.

**BP check** (from §1.3, verified per item).

- Critical clause: η = 0.89² ≈ 0.79. Slack clause: η = 0.11² ≈ 0.012.
- BP-1 P(T) for B = pro-T, from the gadget alone:
  - A agrees (3+, 1−): 0.988 / (0.988 + 0.21³) ≈ 0.99;
  - A tied: 0.976 / (0.976 + 0.21²) ≈ 0.96;
  - A opposes (1+, 3−): 0.964 / (0.964 + 0.21) ≈ 0.82, matching the computed 0.82 in the example cell.
  - pro-F mirrors these.
- BP-0 follows A.
- BP-1 cannot see the core: c\* is 2 hops from v, so its messages are still uniform at round 1.
- From t = 2 the core contributes |β| < 0.3 (odds factor ≤ 1.86), below the gadget's weakest (A-opposed) odds of 2.45. So sign(BP-t) = B for t ≥ 1 in every cell; this is verified per item.
- The link pairs are 4-cycles, so BP-t at t ≥ 2 is somewhat more confident than these values. The computed per-cell values are in the question library.
- **BP run to convergence (BP-∞) sees the whole core.** In the 4 A-opposed cells it ends on the truth D instead of B (computed). So E predicts that more rounds, e.g. more budget for E-explicit, move answers from B toward D *exactly in the cells where local evidence is weakest*. This is a graded, feature-dependent prediction (family I).

**Predicted P(answer = True) per cell.** D, A and B are coded as their directions (1 = True).

| Family | Prediction |
|---|---|
| Truth; D that finishes; `NOISY-EXACT` | D |
| E `BP-t` (t ≥ 1); E-explicit; `E-in-D` on unfinished runs | **B** |
| `E-in-D` overall (completion probability q) | q·D + (1 − q)·B |
| C0 `POLARITY` (= BP-0), JW | A (tie → 0.5) |
| C0 `MOMS` | Simulated (≈ A) |
| B1 `UP-k`, `WP-t` | Silent → default rule (UP+POL gives A; UP+False gives 0) |
| D-POLARITY, truncated | q·D + (1 − q)·A |
| C1 `GREEDY` (first-mention order) | sat-first: B; v-first: A |
| E `BP-t-CAUSAL` (prefix BP) | sat-first: B; v-first: B lost (the satellite evidence comes after v's clauses). The computed B×O interaction for BP-2-CAUSAL is 0.66, so it resembles C1 here. |
| C2 `GUC` / `SC` | Simulated. The link 2-clauses are the shortest, so roughly 0.5 or order-driven. |
| F `WALK-k` | Simulated (between A and B) |
| H `SAMPLE-m` (entailment) | D |
| A1 / A2 | Constant (surface-balanced) |

**Entailment rendering.** Same skeletons rendered as NL premises. Question: "Does it follow that [v]?" with options {follows, its negation follows, neither}.

- E with τ = 0.2 predicts "follows" in B's direction in every A cell (M ≈ 0.99 / 0.96 / 0.82; the A-opposed cell is borderline). With τ fitted per model, the A-opposed cells are where "neither" appears first. The computed values are in the library.
- C0 predicts A's direction, or "neither" when A is tied.
- Truth and `SAMPLE-m` predict D.

**Pre-registered CoT hypotheses.**

- **CH2a:** in the A-opposed cells, traces whose answer follows B justify v by citing the satellites' external occurrences (T3 > 0) more often than traces whose answer follows A. The latter tally only v's own occurrences.
- **CH2b:** E-classified traces have a higher soft rate (T2).
- **CH2c:** C1-classified traces (mention-order assignment, no backtracking) follow B only under sat-first. Causal E predicts the same answer pattern, but its traces (if explicit) tally satellites only when they were read before v's clauses.
- **CH2d:** on truncated runs, the answer is the last tentative value, and its coded justification (polarity vs second-order) predicts whether it follows A or B.

**Trace predictions per family**, for an A-opposed cell (e.g. A = (1+, 3−), B = pro-T, D = F):

| Family | Trace | Answer |
|---|---|---|
| E-explicit | Satellites' tendencies → "clause 3 depends on v" → v leans True | T |
| C0 | "v is negated 3 times, un-negated once" → False | F |
| C1 (sat-first / v-first) | Satellites set from their externals, then v satisfies the remaining clauses / v set first by its own count | T / F |
| D | Branches in the core; finds c\* → v = F; at the cap: last tentative value | F / default |
| F | Complete assignment, flips inside violated clauses | Simulated |

**Generator recipe.**

1. Build the core and c\* (as in E1-C).
2. Build the local gadget: 4 clauses, 8 satellites, 24 pendant 2-clauses.
3. Apply the cell's signs.
4. Surface-balance.
5. Add decoy satellites elsewhere, unrelated to v, so the "satellite with 3 same-sign leaves" pattern doesn't mark v.
6. Impose the order constraints.
7. Render as CNF and as NL.
8. Verify.

**Answer format and metric.**

- Single word for SAT; three options for entailment.
- Per model, a mixed logistic regression: answer ~ A + B + D + O + B×O + A×B + (1 | skeleton) + (1 | core).
- Also the per-family error agreement (EA) in cells where truth ≠ family, and mixture weights from the shared likelihood (DESIGN O3).

**Weight statements.**

- **The model.** Each family's 24-cell prediction vector (computed; question library §6) enters the mixture, P(answer | cell) = Σ\_h π\_h P\_h(answer | cell) + ε·q. The cells separate the families along four nearly orthogonal directions:
  - β\_B for E;
  - β\_A for C0 and D-POL;
  - β\_D for exact solving and H;
  - β\_{B×O} for C1.
- **Resolution** (computed over the 24-cell answer vectors, SE\_cell ≈ 0.09 at 30 skeletons per cell):
  - BP-1 vs C0, `UP-k`, exact, D-POL-truncated or the sampler: ‖Δ‖ = 3.2–3.5, so π ≥ 0.07–0.08 is detectable and absent competitors are bounded at ≤ 0.04–0.05;
  - BP-1 vs C1 or BP-2-CAUSAL: ‖Δ‖ = 2.45, so π ≥ 0.10 is detectable and the bound is ≤ 0.06;
  - C1 vs BP-2-CAUSAL: ‖Δ‖ = 2.0, bound ≤ 0.07;
  - BP-1 vs WALK: ‖Δ‖ = 1.8, bound ≤ 0.08.
  - BP-1 vs `E-in-D(b=0)` is **not separated** (identical); E1-C truncation and E6b separate them.
- **What moves weight:**
  - β\_B > 0 in the A-opposed cells moves weight from C0 and UP+POL onto E;
  - β\_D > 0 moves weight onto exact solving and H, weighted by the share of runs that finish;
  - β\_{B×O} moves weight onto C1.
- **Feature dependence.** π\_E may differ between finished and unfinished runs (`E-in-D`). That is fitted as a feature term on the observed truncation flag, and reported as exploratory because the flag is post-treatment.

**Sample size and power.**

- SAT: 30 skeletons × 24 cells = 720 items. Entailment: 20 × 24 = 480.
- The B main effect uses 360 pairs (SAT), giving MDE ≈ 8.7pp (binary, p ≈ 0.5, within-pair ρ ≈ 0.3, α = .05, power .8). Entailment: 240 pairs, MDE ≈ 10.7pp. Pooled: 600 pairs, MDE ≈ 6.8pp.
- B×O: 180 pairs per O level (SAT), MDE ≈ 12pp; pooled ≈ 9.5pp.
- Direct mode with logits is far more sensitive.

**Threats to validity.**

- **Moderate marginals** (0.60–0.87). A noisy BP-like model would show an attenuated β\_B; the power calculation assumes 8pp.
- **Core difficulty varies,** so q varies: modelled by the core random effect.
- **NL length** (~4.7k prompt tokens) may push models toward shortcuts. Comparing SAT and entailment is a within-E test of H4.

---

#### E3. Computation tree vs ball: cycle-parity covers (COVER) [diagnostic]

**Hypothesis H-E3.**

- **(a) Anchored:** in one pass and at small budgets, discrimination is limited to cycles of length m ≤ 2r̂ + 1, with r̂ matching E1's.
- **(b) Unanchored:** anonymous message passing (BP or WP, which ignore names) never discriminates. Local procedures that use names (`LOCAL-EXACT-r`) discriminate short cycles. So the unanchored arm separates E-MP from E-LOCAL-ID.

**Design.**

- **Pairs (U, S):**
  - U = two disjoint odd cycles C\_m ∪ C\_m (not 2-colourable);
  - S = one even cycle C\_{2m} (2-colourable).
  - Both have 2m nodes and 2m edges, every node has degree 2, and every radius-r ball is a path for r < (m − 1)/2 **[ours]**.
- **Cycle length** m ∈ {3, 5, 7, 9, 11, 13, 15}.
- **Anchoring:**
  - none; or
  - anchored: "Ann is in group A, Bo is in group B", one anchor per cycle in U and antipodal in S.
  - Identical anchor strings in both members.
- **Distractor:** a bipartite sparse graph of 20 nodes and ~24 edges, the same within each pair.
- **Domains:**
  - **COL:** "Can everyone be split into two groups so that no two people who clash are in the same group?"
  - **SAT:** ≠-constraints as 2-clause pairs, plus a satisfiable 3-SAT filler of 20 variables at α = 2.
- **Answer:** yes / no.

**Predicted discrimination Δ(m) = P(no | U) − P(no | S).**

| Family | Anchored | Unanchored |
|---|---|---|
| Global (BFS/DFS 2-colouring, D, exact) | 1 at every m (seq; needs budget) | 1 |
| E-MP `BP-t` / `WP-t` | 1 for m ≤ 2t + 1, else 0 | 0 at every m |
| E `LOCAL-EXACT-r` (names usable) | 1 for m ≤ 2r + 1 | Same |
| E-explicit (thinking) | Knee m\* grows with budget | 0, unless the trace breaks the symmetry (which is a D/C1 move) |
| B1 `UP-k` | As E-MP, with k − 1 | 0 |
| C0, A2 | 0 | 0 |
| C1 `FIRST-FIT` (2 colours, mention order) | U: "no". S: false "no" whenever a node meets two differently coloured neighbours, rising with m. So Δ is small. | Same |
| F `WALK-k` | S: "yes" when found. U: never certified, so "yes" by default; Δ can be < 0. | Same |
| H `RANDOM` | 0 | 0 |

The off-by-one (does a radius-r procedure see the edge closing a (2r+1)-cycle?) is fixed by the reference implementations' convention, and the knee is read on that convention.

**Pre-registered CoT hypotheses.**

- **CH3a:** WP-round traces expand fronts from both anchors in lockstep ("Ann: A ⇒ her neighbours B; Bo: B ⇒ his neighbours A; next ring…"), so T1 is high. They find the contradiction where the fronts meet, at the antipode. DFS-style traces walk in one direction and find it when the walk closes.
- **CH3b:** under budget forcing, m\* grows roughly linearly with B (fixed tokens per ring).
- **CH3c:** unanchored traces break symmetry by an explicit choice ("put Ann in A"). That is a D/C1 step, not E-MP.

**Confounds.**

- Equal counts, degrees and tokens.
- Cycle edges are interleaved with distractor edges in random order, so a cycle is never contiguous text.
- Names are random.

**Generator recipe.**

1. Build the cycles and the distractor.
2. Randomise edge orientation in the rendering.
3. Shuffle; add anchors.
4. Verify: U is not 2-colourable, S is, balls are paths for r < (m−1)/2, and counts and tokens are equal.

**Metric.**

- Δ(m) per model × condition × anchoring, and a logistic knee m\*.
- r̂\_E3 = (m\* − 1)/2, checked against r̂\_E1-hard (CIs must overlap).

**Weight statements.**

- **The model.** The discrimination profile Δ(m) under each anchoring is modelled as a mixture of the computed profiles. Their shapes:
  - E-MP: a step at 2t − 1 anchored, and 0 unanchored;
  - `LOCAL-EXACT-r`: a step at 2r + 1 under both anchorings;
  - exact and DSATUR: 1 everywhere;
  - C0, A and RANDOM: 0.
- **Resolution** (computed over the 14 cells Δ(m), SE\_cell ≈ 0.079):
  - WP/BP-4 vs `LOCAL-EXACT-3`: ‖Δ‖ = 1.73, so the bound is ≤ 0.08;
  - vs exact or DSATUR: 3.32, bound ≤ 0.04;
  - vs C0 / A: 1.73, bound ≤ 0.08;
  - vs FIRST-FIT: 2.0, bound ≤ 0.06;
  - WP/BP-2 vs WP/BP-4: 1.41, bound ≤ 0.09, which locates t.
  - E-MP vs `UP-k` is **not separated** here.
- **What moves weight:**
  - an anchored knee with an unanchored zero moves weight to E-MP (and B1, which E3 cannot separate);
  - equal knees move weight to `LOCAL-EXACT`;
  - flat Δ ≈ 1 moves weight to global procedures.
- **Cross-check.** The implied r̂\_E3 must agree with r̂\_E1 within its interval. Disagreement means the two evals' E weights refer to different procedures, and both are reported.

**Sample size and power.**

- 40 pairs per (m, anchoring, domain) cell, giving 2,240 items.
- Per m, pooled over domains: 80 pairs, MDE ≈ 18pp.
- The pooled logistic regression over 7 m values (560 pairs per anchoring level) puts m\* within about one step (prior from simulation).

**Threats to validity.**

- **Triangles and short cycles are familiar from pretraining** (A3), so m = 3 is uninformative; the analysis uses m ≥ 5.
- **2-colouring is in P.** E3 is a locality probe, like PAPER\_SKELETON §6.3's depth-stress items, not a hardness claim.
- **`think-hi` would be at ceiling,** so thinking runs use only `think-B` (512 / 2k / 8k).

---

#### E4. Threshold knees on random 3-SAT (KNEE) [primary for thinking]

**Hypothesis H-E4.** Above the budget line, an E member (`BP-DEC-MAX`, `BP-DEC-OUT`, `SP-DEC`, `BP-t`+round) fits the model's success curve over α *and* its failure profile better than D, F, C1 or C2.

**Design.**

- Random 3-SAT with n ∈ {n\* − 12, n\*, n\* + 12} (calibrated per family; priors 24 / 36 / 48).
- α ∈ {3.0, 3.5, 3.8, 4.0, 4.2, 4.4, 4.7, 5.0}; 30 items per cell.
- Labels from the solver. At α ≥ 4.2, use matched SAT/UNSAT pairs one clause apart (Zhang, Chen & Chen 2026, report A).
- Answer: a JSON assignment or "UNSAT".
- **This α sweep is shared infrastructure with verticals C, D and F:** one item set, several analyses.

**Reference curves**, simulated on the same items (50 seeds where stochastic):

- `BP-t`+round (t = 0..5);
- `BP-DEC-MAX` (t\_dec ∈ {2, ∞}), `BP-DEC-OUT`, `SP-DEC`;
- `UC`, `GUC`, `SC`, `GREEDY`;
- `DPLL-b` and `WALK-k`, with b and k matched to the model's tokens (tokens ÷ the median tokens per decision or flip in its own traces);
- `RANDOM`, `NOISY-EXACT`.

**Predicted shapes** (not asymptotic numbers):

| Family | Success on SAT items vs α | False UNSAT | Profile of wrong assignments |
|---|---|---|---|
| `BP-t`+round | Low already at moderate α | Only via CONFLICT | Many violated clauses, scattered |
| `BP-DEC` (FAIL → UNSAT) | High up to its knee, then drops | Rises after the knee | None |
| `SP-DEC` | Knee later than BP-DEC (simulated) | Rises near α\_c | None |
| `DPLL-b` | High below budget; depends on n more than α | At the cap: the D vertical's default | Default only |
| `WALK-k` | High until near α\_c at small n | Never | 1–3 violated clauses, scattered (near-misses) |
| C1 / C2 | Early knees (simulated; report F's 8/3 and ≈ 3.26 are asymptotic) | Dead ends | Violations among late-assigned variables |

**Process signature:** thinking tokens vs α. BP-DEC has no backtracking, so tokens are roughly flat in α. D's tokens peak near α\_c.

**Pre-registered CoT hypotheses.**

- **CH4a:** DSL (T11) favours `BP-DEC-MAX` if the model fixes the most-biased variable, re-tallies, and never backtracks. It favours D if T7 (backtracks) is high, and F if T9 (complete-assignment checks) is high.
- **CH4b:** the simulated knee of the family assigned to the traces lies within the CI of the model's knee.

**Metric.** Per model and n:

- logistic fits of success on α;
- a joint likelihood against each reference over success, false-UNSAT and violation-count distributions;
- the item-level mixture from DESIGN O3.

**Weight statements.**

- **The model.** The item-level mixture over the reference procedures (DESIGN O3) gives π for BP-DEC, SP-DEC, BP+round, C2, C1, D-b, F-k, `NOISY-EXACT`, `PERCEPTION-NOISE` and `RANDOM`, with α and n as feature terms. This is family I: e.g. π\_BP-DEC falling and π\_F rising with α.
- **Reported per weight:** posterior mean and 95% interval; ΔLL of the full mixture vs the mixture without E members; and the same for the nearest competitor.
- **Trace channel.** The DSL estimates the same weights from commitment sequences. Its estimates are reported beside the answer-based ones, scaled by w.
- **Resolution** (computed on the n = 12 illustration sweep, one-hot failure categories, SE\_cell ≈ 0.09):
  - BP-DEC-MAX vs GUC, BP-2+round, GREEDY or RANDOM: ‖Δ‖ = 3.5–4.0, bound ≤ 0.04;
  - vs WALK-500 and BP-DEC-OUT: ‖Δ‖ = 1.41, bound ≤ 0.10.
  - **At n = 12, BP-DEC-MAX is not separated from exact search or DPLL-16:** all are correct on every item. Separation comes only from the full sweep at n\* ± 12, where BP-DEC's false UNSATs appear (to verify in simulation at full n before the run).

**Sample size and power.** 720 items, 240 per n. The SE of α50 is ≈ 0.1–0.15 (prior), so curves whose α50 differ by ≥ 0.4 are separated with power > 0.9.

**Threats to validity.**

- At n ≤ 48 the curves are broad and overlap, so identification rests on joint profiles, not knee position alone.
- Most UNSAT items at α ≥ 4.7 will hit the 32k cap and are censored.
- The D vertical's default rule matters for interpreting capped runs.

---

#### E5. Per-variable preference calibration: BP vs exact marginals (CALIB) [primary, below budget]

**Hypothesis H-E5.** When the model picks values for unforced variables in the solutions it finds at best effort, the picks follow BP-t marginals (t ≥ 1). They follow them better than own polarity (t = 0), better than the exact solution marginals, and better than other solvers' solution biases. On lifts, the picks ignore global solution counts, as BP must.

**E5a.**

- 96 satisfiable formulas: n ∈ {24, 30}, α ∈ {2.5, 3.0, 3.5}.
- Half are **tree-like**: factor-graph girth ≥ 8 around ≥ 80% of variables, bounded degree.
- Half are **loopy**: on average ≥ 3 cycles of length 4–6 per variable.
- They are below the budget line, so thinking models mostly solve them.
- **`think-hi`:** 8 sampled solutions per formula. Measure the per-variable frequency f(i) among valid solutions.
- **`direct`:** single-token preference queries with logprobs, 8 variables per formula.

**E5b.**

- 48 lift pairs:
  - F (n = 20, loopy, α ≈ 3) ∪ G (a disjoint filler, n = 20); vs
  - F̃, a random connected 2-lift of F (n = 40).
- Token counts within 2%.
- In each pair, 4 targets with |exact marginal in F − exact marginal of v₁ in F̃| ≥ 0.15.
- BP is identical on v, v₁ and v₂ at every t (fact 2).

**Candidate scores.**

- Exact marginals (by model counting).
- `BP-t` (t = 0..6, ∞), `WP-∞`, `SP-∞`, `POLARITY`, JW, `MOMS`.
- Simulated solution frequencies of:
  - DPLL with each value order: {`POLARITY`, BP (`E-in-D`), always-True, first-mention};
  - `WALK-k` from random starts, `GREEDY`, `BP-DEC-MAX` / `-OUT`.

**Predictions.**

| Family | E5a best-fitting score | E5a loopy: BP vs exact | E5b slope of Δf on Δexact |
|---|---|---|---|
| E (`BP-t`, `E-in-D`, `BP-DEC`) | `BP-t`, t ≥ 1 | BP fits better | ≈ 0 |
| C0 `POLARITY`; D-POL | t = 0 | Polarity | ≈ 0 |
| H uniform / exact sampler | Exact marginals | Exact fits better | ≈ 1 × the E5a calibration slope |
| C1; D with first-mention order | Order-based scores | — | ≈ 0 to partial (simulated) |
| F `WALK-k` | WALK frequencies (simulated; partly marginal-like) | Simulated | Partial |

**Pre-registered CoT hypothesis (CH5).** E-classified traces justify free choices with second-order votes, C0-classified traces with own tallies, and H-classified traces by enumerating candidate solutions.

**Metric.**

- A hierarchical logistic regression of the sampled values on one score at a time, per model. Log-likelihoods are compared with a formula-clustered bootstrap. Report the best t.
- The E5b regression slope.

**Weight statements.**

- **The model.** Value frequencies are modelled as a mixture over the candidate scores: f(i) = Σ\_h π\_h · σ(a\_h + b\_h · score\_h(i)).
- **Reported:** π per score with a 95% interval, and ΔLL vs the best single score.
- **The lift slope** estimates the H/exact share directly: slope ≈ π\_H × calibration, with SE ≈ 0.10. So a zero H weight is bounded at π\_H ≤ ≈ 0.2 (upper 95%) from E5b alone, and tighter when combined with E5a's loopy items.
- **What moves weight:**
  - the tree-like item moves weight between BP-0 (C0) and BP-t (t ≥ 1), where they disagree;
  - the loopy and lift items move weight between BP and exact.

**Sample size and power.**

- **E5a:** 96 × 8 × ~27 ≈ 20,700 variable observations in thinking mode, plus 768 direct queries. A partial correlation of 0.1 is easily detected under formula clustering (ICC 0.3).
- **E5b:** 192 pair-observations. The slope's SE is ≈ 0.10, so power ≈ 0.98 to separate a slope of 0 from 0.4.

**Threats to validity.**

- **Frequencies mix preference and constraint.** The exact marginal is the baseline that absorbs the constraint.
- **8 samples per formula give coarse per-variable frequencies,** so the analysis pools variables.
- **Sampling temperature changes diversity.** Use each model's recommended T and report it.

---

#### E6. Decimation: does an early commitment shape later ones as BP-DEC predicts? (DEC)

**Hypothesis H-E6.** When an assignment is built one variable at a time, flipping an early commitment changes later choices the way BP-guided decimation predicts:

- soft influence passes through neighbours that are not yet committed;
- committed neighbours block it;
- the influence is radius-limited.

It does not change them the way greedy predicts (only through committed values, distance 1), nor the way search does (propagation, conflict, retraction).

**E6a (direct; open models).**

- 200 tree-like formulas (n = 30, α = 2.5). Output order is alphabetical by name, which is random with respect to the graph.
- Run free first. Then teacher-force the first emitted value, flipped, keep the model's own later prefix fixed, and read the logit for every later variable j.
- Classify each j by dist(x₍₁₎, j) ∈ {1, 2, 3, ≥ 4} and by path status:
  - **open:** every intermediate variable on the tree path is emitted after j;
  - **blocked:** some intermediate is emitted before j, and is held at its free-run value.

**Predicted shift Δ\_j toward the BP-conditional direction.**

| Family | Distance 1 | Distance ≥ 2, open | Distance ≥ 2, blocked |
|---|---|---|---|
| `BP-DEC-OUT-t` | ≠ 0 | ≠ 0 for dist ≤ t | 0 (on a tree, conditioning on the intermediate separates) |
| `BP-t`+round (no conditioning) | 0 | 0 | 0 |
| C1 `GREEDY` | ≠ 0 | 0 | 0 |
| `UP+GUESS` | ≠ 0 only where the flip makes a clause containing j unit | 0 | 0 |
| Exact conditional sampler | ≠ 0 | ≠ 0 at every distance, ∝ the exact conditional shift | 0 |

On trees, `BP-DEC-OUT-∞` equals exact conditioning. The two separate by Δ\_obs / Δ\_exact as a function of distance: flat for exact, dropping to 0 beyond t for `BP-t`.

**E6b (thinking; open models; this is also FT4).**

- 120 satisfiable formulas (n = 30, α = 3.3).
- Generate a base trace and locate its first commitment of a free variable, one where both values extend to solutions.
- Build two prefixes ending at that commitment, one with the value as written and one flipped (a minimal text edit). Continue each twice.
- **Measures:**
  - whether the flipped commitment is retracted;
  - shifts in later commitments of variables at distance 1–4;
  - the trace's own later tallies;
  - the final answer.

**Predictions (E6b).**

| Family | Retraction | Later commitments at distance 2–4 | Final answer |
|---|---|---|---|
| E-explicit / `BP-DEC` | No | Shift through uncommitted neighbours; re-tallies cite the flipped value | Consistent with the flip |
| C1 | No | Only adjacent variables shift | Consistent with the flip; conflicts possible |
| D | Only if the flip leads to a conflict (rare here: both values extend) | Via propagation | Consistent |
| F | The flip may be undone by later repair flips | Diffuse | Varies |
| Trace decorative (unfaithful) | — | Trace changes but later commitments and the answer don't | Unchanged |

**Sample size and power.**

- **E6a:** ~5,800 observations, ≥ 300 per class; MDE ≈ 0.15 logit.
- **E6b:** 240 continuations per arm detect a 15pp difference in retraction rate (0.45 vs 0.60) with power ≈ 0.85.

**Threats to validity.**

- **Off-distribution prefixes.** A flipped prefix is off-distribution and may trigger generic self-correction. The unflipped control absorbs resampling noise but not that effect. Choosing commitments where both values extend to solutions keeps retraction from being forced by logic.
- **Inconsistent prefixes (found by verification).** Teacher-forcing the free-run values *after* a flipped first value can leave no satisfying extension. In the first example formula, 5 of 9 later variables were in that state. E6a therefore chooses a first variable whose flip leaves the rest of the free-run assignment valid, and logs any inconsistent prefix as its own category.
- **Small effects at distance ≥ 2.** Influence through open paths is small on sparse trees: in the example, 0.04–0.08 at distance 2 vs 0.22 at distance 1. The full study should use tighter couplings (2-clause links) on the paths of interest, so that open-vs-blocked differences exceed the 0.1 detection threshold.

---

### 2.9 Manipulation signatures

| Manipulation | E (abstract) | E-causal (`BP-t-CAUSAL`) | E-explicit (trace) | Nearest competitors |
|---|---|---|---|---|
| Premise/clause order reversed | = | Changes when it reverses the forward paths from decisive clauses | = | C1: ± (order-driven); A2 `PRIMACY` / `RECENCY`: ± |
| Re-themed / renamed | = | = | = | A3 `TEXTBOOK-TRANSFER`: may change |
| Rule inverted (e.g. "same group" instead of "different groups") | Follows the stated rule | Same | Same | A3: answers the textbook version |
| Irrelevant constraint added | = if d > r; ± if within r and it shifts marginals | Same | = | A2: ±; C1: ± if early in order |
| Size increased, local structure fixed | = (size invariance) | = | Tokens ↑ only if sweeps are global | `NOISY-EXACT`, D: errors ↑ |
| Density increased | Knee as simulated (E4) | — | — | C2 / D / F: their own simulated knees |
| Thinking budget ×4 | r\* ↑ (E-explicit) or a switch to D | — | Sweeps ↑ | D: b ↑; B1: k ↑ |

### 2.10 Process measures

- **Thinking tokens.**
  - E-explicit predicts tokens ∝ rounds × variables touched per round.
  - On E4, BP-DEC predicts a token count roughly flat in α. D predicts a peak near α\_c.
  - On E1-S chains, UP and E both predict tokens linear in d, so tokens don't discriminate there.
- **Confidence.**
  - E predicts *confident* errors where BP is confidently wrong: E2 cells where A and B agree but D opposes, and E5 loopy items.
  - Measure stated confidence (0–100) or answer logprob against |β\_BP|, controlling for accuracy.

### 2.11 Eval designs (template table)

The template's "Supported if / Against if" columns become weight statements (Andrew's correction: the readout is graded).

| ID | Item generator | Answer format | Metric (quantity, 95% interval) | Moves weight toward E when | Bounds π\_E (or a competitor) when |
|----|----------------|---------------|--------|--------------|------------|
| E1-S | Sparse equivalence chain + hub (unit / soft) at d; semantic no-op nulls; placement; growth arm | Single word | π per family from the cell-effect mixture; posterior on r\*; ΔLL vs null and vs nearest competitor | A step at d ≤ r̂ with null edits flat (weight to BP-t, away from C0 / B1 / sampler) | A flat zero profile bounds π\_E,soft (upper 95% ≈ 1.645·SE/‖Δ‖ ≈ 0.1); decay moves weight to F / PERCEPTION-NOISE |
| E1-C | Periphery–core; hub S at d; chain order | Single word | Same, on Δacc (toward − against) by d and O | Δacc > 0 for d ≤ r̂ only | Δacc ≈ 0 at every d bounds π\_E at best effort; an O-only effect moves weight to C1 |
| E2 | Periphery–core; A × B × D × O | Word / 3-way | π per family from the 24-cell mixture; contrasts β\_B, β\_A, β\_D, β\_{B×O} | β\_B > 0, including the A-opposed cells | β\_B ≈ 0 bounds π\_E (≈ 0.06 upper 95%); β\_A, β\_D, β\_{B×O} move weight to C0 / exact / C1 |
| E3 | 2 × C\_m vs C\_{2m}; anchors; distractor | yes / no | π over the Δ(m) profiles; r̂\_E3 vs r̂\_E1 | Anchored knee + unanchored zero (E-MP); equal knees (E-LOCAL-ID) | Flat Δ ≈ 1 moves weight to global procedures; flat 0 moves it to C0 / A / RANDOM |
| E4 | Random 3-SAT, α × n around n\* | Assignment / UNSAT | Item-level mixture with α and n features; DSL weights × w | False UNSAT past a knee with no near-misses (BP-DEC) | Near-misses bound π\_BP-DEC and move weight to F; no errors below budget moves weight to exact |
| E5 | Tree-like vs loopy SAT; 2-lift pairs | Assignment ×8 / preference | π over scores; lift slope (≈ π\_H × calibration) | BP-t (t ≥ 1) out-fits BP-0 and exact; slope ≈ 0 | Slope bounds π\_H ≤ ≈ 0.2 alone; POLARITY winning moves weight to C0 |
| E6 | Tree-like SAT; forced prefix / edited trace | Assignment / continued trace | π over the Δ\_j class profiles; retraction rate | Open-path shifts, blocked = 0, radius-limited (BP-DEC) | Distance-1-only moves weight to C1; no shifts move it to one-pass E or RANDOM |

### 2.12 Positive controls before any LLM data (DESIGN O3.6, §5.12)

- **Fake models with graded mixtures.** Each fake model samples its procedure per item from planted weights, then applies 10% slips. The analyses of E1, E2, E4, E5 and E6 must recover every weight. The planted mixtures are:
  - **pure:** `BP-1`, `BP-2`, `BP-DEC-OUT`, C0, C1, D-POL-truncated, `EQ-CONTRACT`, `NOISY-EXACT`, each at π = 1;
  - **three-way partial:** 60/30/10 over (BP-2, C0, D-truncated) and over (BP-DEC, F, exact);
  - **close competitors:** 50/50 BP-2 vs UP-3, and 70/30 BP-1 vs `EQ-CONTRACT`. These are the hardest pairs;
  - **feature-dependent (family I):**
    - π\_E = σ(1.5 − 1.0·[d ≥ 3]) in E1;
    - π\_BP-DEC falling linearly from 0.7 at α = 3.0 to 0.1 at α = 5.0, with F taking the rest, in E4;
    - π\_E higher on unfinished runs (0.6) than on finished ones (0.1), in E1-C and E2.
  - **null-heavy:** 80% `PERCEPTION-NOISE` + 20% BP-2.
- **Reported for each planted weight:** bias of the posterior mean, 95% interval width, and coverage over 200 simulated replicates, at both dev-batch and full-study sizes.
- **Pre-registered acceptance at full size:** |bias| ≤ 0.05, coverage within [0.90, 0.98], and interval width ≤ 0.20 for every weight ≥ 0.1.
  - Feature-term slopes are recovered within ±0.5 on the logit scale.
  - r\* is recovered within ±1 in ≥ 80% of replicates.
- **Dev-batch sizes are expected to fail these widths.** They are for plumbing; the recovery report says so.
- **Synthetic traces** for the trace pipeline (§2.5, step 5).

### 2.13 Generator specifications

Concrete instances of every template below are in [E\_message\_passing\_questions.md](E_message_passing_questions.md), with machine-readable copies in [`data/examples/E_message_passing.jsonl`](../../data/examples/E_message_passing.jsonl). Ground truths and every heuristic's prediction there were computed by a throwaway verifier (exact model counting plus reference implementations), not by hand. The sizes there are illustration scale.

**Rules shared by every template.**

- **Splits.**
  - Each skeleton or core is generated from an integer seed. split = SHA-256(eval ‖ seed) mod 10: 0 → dev, 1–9 → test.
  - Minimal pairs and triples inherit their skeleton's split, so variants of one skeleton never straddle splits.
  - A core's clause multiset is content-hashed. A hash seen in one split is rejected in the other.
  - Dev uses a disjoint 64-name sub-pool of the 256 names; test uses the other 192.
  - Dev items are for iteration only and never enter confirmatory analyses.
- **Surface matching inside a pair or triple.**
  - Edits only flip literal signs in place, so clause count, clause order, literal order and lengths are identical.
  - Negation counts are equalised by degree-1 flips (§2.4).
  - Names are the same, except the colouring null, which swaps in a different single-token name.
  - Token counts are asserted equal under every tokenizer used.
- **Rejection rules shared by every template.**
  - Token mismatch → regenerate.
  - Some family's prediction differs from the cell's design table → reject (§2.4.7).
  - For backbone questions: satisfiable, and the target must be backbone.
  - For preference questions: satisfiable, and both values of the target must extend to solutions.
- **Yields.** Measured at illustration scale by running each acceptance test on fresh seeds; reported per template below as "yield". The pilot re-measures them at full scale.

**E1-S (sparse chain).**

- **Parameters:**
  - chain length L\_c = 8 (illustration: 6);
  - d ∈ {1, 2, 3, 4, 6};
  - channel ∈ {hard, soft};
  - hub strength k\_h = 3 pendant 2-clauses (range 2–4);
  - one balanced pendant pair per chain variable;
  - filler: 20 variables at α\_f ∼ U[1.2, 2.0], 3-clauses, attached ≥ 10 hops away or disconnected (illustration: 5 variables, 7 clauses);
  - 4 decoy equivalence pairs in the filler;
  - placement ∈ {first 15%, last 15%};
  - edit direction balanced.
- **Variants** (same skeleton and order):
  - effective = flip the hub literal in the hub clauses;
  - null = flip the leaf literal in the same clauses (soft), or in the adjacent pendant (hard);
  - growth = append a disconnected block (+40 clauses on 20 variables; illustration +10 on 8).
- **Rejection:** filler UNSAT; any cycle within C\_9(v) other than the designed equivalence pairs; the BP-t step not at t = d; the UP-k step not at k = d + 1 (hard channel).
- **Expected yield:** ≈ 95% (filler satisfiability is the only random step).

**E1-S colouring.**

- **Parameters:** diamonds per chain ∈ {1, …, 6} (d = 2 hops per diamond); 3 colours; hub precoloured; 1–2 free pendants per diamond tip; a filler triangle.
- **Variants:** effective = recolour the hub; null = rename a free pendant.
- **Rejection:** v not backbone; a pendant constrains v.
- **Yield:** ≈ 100% (deterministic).

**E1-C (periphery–core).**

- **Core:** random 3-SAT with n\_K = n\*(model family) (prior 32–48; illustration 10) and α\_K ∼ U[4.0, 4.2]. Accept if satisfiable, the backbone covers ≥ 30% of variables, and some backbone variable c\* has max\_t |2·BP\_t(c\*) − 1| < 0.3 over t = 0..8 and the fixed point. Take the least-biased one.
- **Periphery:** link v ≡ u ≡ c\*; chain v ≡ p\_1 ≡ … ≡ p\_6; hub at p\_d, d ∈ {1, 2, 4, 6}, with 4 pendant 2-clauses whose signs give S ∈ {toward, neutral, against}; 4 balancing clauses.
- **Variants:**
  - S changes the hub signs;
  - O re-orders the chain links (relative order hub→v vs v→hub; random absolute positions);
  - the hub pendants sit next to the hub's link.
- **Rejection:** truth(v) ≠ backbone(c\*); the BP-t sign at v doesn't follow S for t ≥ d + 1; UP derives v; C0 not constant across S.
- **Yield:** dominated by core acceptance. Measured at n\_K = 10 (§2.13 table below); to re-measure at n\*.

**E2 (soft vs hard).**

- **Core:** as in E1-C.
- **Gadget:**
  - 4 local 3-clauses on v, each with 2 fresh satellites;
  - satellite tendency set by 3 pendant 2-clauses, sign σ\_s ∼ Bernoulli(½);
  - A, B, D, O as in §2.8;
  - 12 balancing clauses on fresh degree-1 pairs;
  - 6 decoy satellites elsewhere.
- **Variants:**
  - A sets v's signs in the local clauses;
  - B sets the satellite literal signs (critical = −σ, slack = σ);
  - D sets the link sign (v ≡ u or v ≡ ¬u);
  - O moves the gadget blocks relative to each other, with the link clauses last in both levels.
- **Rejection:**
  - backbone(v) ≠ D;
  - sign(BP-1(v)) ≠ B, or sign(BP-0(v)) ≠ A (tie where A is tied), in any cell;
  - C1 GREEDY not following B in sat-first and A in v-first.
- **Yield:** core acceptance × ≈ 0.9 (gadget checks).

**E3 (cover pairs).**

- **Parameters:**
  - m ∈ {3, 5, …, 15};
  - anchored ∈ {yes, no};
  - distractor: a bipartite graph with 6 nodes (illustration) to 20 nodes (full), even cycles only;
  - names drawn without replacement; edge order and orientation random.
- **Variants:** U vs S re-wire the same node names (two m-cycles vs one 2m-cycle); anchors are identical strings in both.
- **Rejection:** none (deterministic), except the token check.
- **Yield:** 100%.

**E4 (α sweep).**

- **Parameters:** n ∈ {n\* − 12, n\*, n\* + 12}; α on the 8-point grid; clauses of 3 distinct variables with uniform signs.
- **Matched pairs** at α ≥ 4.2: flip single literals of a SAT instance until it is UNSAT, and keep the pair.
- **Rejection:** none beyond matched-pair search.
- **Yield:** a matched pair (some single-literal flip makes it UNSAT) is found among 50 random flips in 44% of satisfiable instances (measured at n = 12, α = 4.2).

**E5 (calibration).**

- **Tree-like:** grow a factor-graph tree with clause lengths ∼ {2, 3}. Accept if ≥ 2 variables have `POLARITY` ≠ sign(exact marginal).
- **Loopy:** n = 10, m = 22, clause lengths {2, 3, 3}. Accept if ≥ 3 variables have |BP-∞ − exact| > 0.12 and at least one disagrees in sign.
- **Lifts:** F has n = 6 and m = 11 (illustration; full study n = 20). Its random 2-lift must be connected, with ≥ 2 variables whose exact marginal moves by ≥ 0.15 between F and F̃. G is a disjoint filler of equal size.
- **Yield:** measured (table below): tree 0.7%, loopy 23%, lift 12% of seeds.

**E6 (decimation).**

- **Parameters:** a tree factor graph with n = 10 (full study 30) and α ≈ 2.5; the first variable in output order is chosen with degree ≥ 3; alphabetical output order is set by assigning names.
- **Variants:** a flipped forced prefix (E6a); flipped vs as-written committed value in a thinking prefix (E6b).
- **Yield:** ≈ 100% for E6a; E6b needs a first commitment of a *free* variable (≈ 70%, to measure in the pilot).


**Measured acceptance rates** (illustration scale: fresh seeds, the throwaway verifier; the pilot re-measures at full scale):

| Template / acceptance test | Seeds | Accepted | Main rejection reasons |
|---|---|---|---|
| Core, n\_K = 10, α ∼ U[4.0, 4.2]: satisfiable, backbone ≥ 30%, some backbone c\* with max\_t \|BP bias\| < 0.3 | 300 | **5.0%** | no BP-uninformative backbone variable 61%; UNSAT 16%; small backbone 18% |
| Core, n\_K = 16 (same test) | 120 | **8.3%** | no BP-uninformative variable 53%; UNSAT 23%; small backbone 16% |
| Core with c\* bias < 0.1 (the original rule) | 5,000 | **0%** at n = 10 | (rule relaxed; see §2.4) |
| E5 tree-like (≥ 2 variables with POLARITY ≠ exact sign) | 300 | 0.7% | trees rarely make polarity misleading; cheap to oversample |
| E5 loopy (≥ 3 variables with \|BP-∞ − exact\| > 0.12, one sign flip) | 300 | 23% | |
| E5 lift (connected 2-lift, ≥ 2 marginal shifts ≥ 0.15) | 1,000 | 11.7% | |
| E4 matched SAT/UNSAT pair (n = 12, α = 4.2) | 100 | 44% of SAT instances | |

Core acceptance (5–8%) is the binding cost for E1-C and E2: about 15–20 core draws per accepted core. Each draw costs one SAT call plus n backbone checks and BP runs, which is cheap.

### 2.14 Coverage: which question sets can bound which theories

Every row must have a ✓ somewhere: some set must be able to push that theory's weight toward zero with an upper-95% bound ≤ 0.10 at full-study size. The matrix below was **computed** from the example items in [E\_message\_passing\_questions.md](E_message_passing_questions.md), so it is regenerated whenever the items change.

- **What each cell is.** The best upper-95% bound on that theory's weight the set delivers when the theory is absent, computed as 1.645·SE\_cell / ‖δ\_h − δ\_nearest‖.
- **The reference it is measured against.**
  - For a competitor: the nearest main E member (BP-t with t ≥ 1; BP-0 counts as C0).
  - For an E member: the nearest non-E theory.
- **Symbols:** ✓ = bound ≤ 0.10; ~ = bound ≤ 0.30; — = not separated (identical predictions) or no prediction.

| Theory | E1-S soft | E1-S hard | E1-S colouring | E1-C | E2 | E3 | E4 | E5 | E6a | Best bound |
|---|---|---|---|---|---|---|---|---|---|---|
| E: BP-t (t ≥ 1) | ✓ 0.08 | ~ 0.12 | ✓ 0.04 | ✓ 0.10 | ✓ 0.08 | — (identical) | — | ✓ 0.05 | — | ✓ 0.04 |
| E: BP-t-CAUSAL | ✓ 0.09 | ~ 0.16 | — | ✓ 0.10 | ✓ 0.07 | — | — | — | — | ✓ 0.07 |
| E: LOCAL-EXACT-r | ✓ 0.08 | — (identical) | — | ✓ 0.10 | ✓ 0.08 | ✓ 0.09 | — | — | — | ✓ 0.08 |
| E: LOCAL-t colouring | — | — | ✓ 0.04 | — | — | — | — | — | — | ✓ 0.04 |
| E: E-in-D | — (identical) | — (identical) | — | ✓ 0.10 | ✓ 0.08 | — | — | ✓ 0.01 | — | ✓ 0.01 |
| E: BP-DEC / BP+round | — | — | — | — | — | — | ✓ 0.05 | ✓ 0.02 | — 0.83 | ✓ 0.02 |
| B1: UP-k / WP-t | ✓ 0.08 | — (identical) | ~ 0.14 | — (identical) | ✓ 0.06 | — (identical) | — | — | — | ✓ 0.06 |
| B1∘C0: EQ-CONTRACT | — (identical) | — (identical) | — | — (identical) | ✓ 0.05 | — | — | — | — | ✓ 0.05 |
| C0: POLARITY (= BP-0) | ✓ 0.08 | ✓ 0.08 | ~ 0.14 | — (identical) | ✓ 0.06 | ~ 0.13 | — | ✓ 0.02 | — | ✓ 0.02 |
| C1: GREEDY / FIRST-FIT | — (identical) | ✓ 0.08 | — (identical) | ✓ 0.10 | ✓ 0.07 | ✓ 0.08 | ✓ 0.06 | ✓ 0.01 | — (identical) | ✓ 0.01 |
| C2: UC / GUC / DSATUR | — | — | — (identical) | — | — | ✓ 0.06 | ✓ 0.04 | — | — | ✓ 0.04 |
| D: DPLL-b | ✓ 0.08 | — (identical) | — | — (identical) | ✓ 0.05 | — | ✓ 0.06 | ✓ 0.01 | — | ✓ 0.01 |
| F: WALK / MIN-CONFLICTS | ✓ 0.09 | ~ 0.13 | — | ~ 0.19 | ~ 0.11 | ~ 0.11 | ~ 0.10 | ✓ 0.06 | — | ✓ 0.06 |
| H: sampler / exact conditioning | ~ 0.17 | — (identical) | — | — (identical) | — (identical) | — | — | ✓ 0.08 | — (identical) | ✓ 0.08 |
| A1: constant | ✓ 0.08 | ✓ 0.08 | — | — (identical) | ✓ 0.04 | ~ 0.13 | — | — | — | ✓ 0.04 |
| A2: cues | ✓ 0.08 | ✓ 0.08 | — | — (identical) | ✓ 0.04 | ~ 0.13 | — | — | — | ✓ 0.04 |
| NULL: solves exactly | ✓ 0.08 | — (identical) | — (identical) | — (identical) | — (identical) | ✓ 0.06 | — (identical) | — | — | ✓ 0.06 |
| NULL: NOISY-EXACT | ✓ 0.08 | — 0.37 | — (identical) | — (identical) | — 0.60 | ✓ 0.07 | — | — | — | ✓ 0.07 |
| NULL: PERCEPTION-NOISE | ✓ 0.08 | ~ 0.15 | — | — (identical) | — 0.41 | ✓ 0.08 | — | — | — | ✓ 0.08 |
| NULL: RANDOM | ✓ 0.08 | ✓ 0.08 | ✓ 0.06 | — (identical) | ✓ 0.06 | ~ 0.13 | ✓ 0.04 | ✓ 0.03 | — (identical) | ✓ 0.03 |

**Reading it.**

- **MP vs `UP-k`:** separated only by sets with soft evidence and no unit clauses (E1-S soft, E2). Every hard-propagation set (E1-S hard, E1-S colouring, E1-C, E3) predicts the same for both.
- **MP vs C0:** separated by E1-S (both channels), E2 and E5.
- **MP vs exact solving:**
  - E1-S soft: exact solving implies no preference effect.
  - E3: exact solving is global.
  - E1-C and E2 under the noise nulls: `NULL:EXACT` ties with search that finishes (D, E-in-D on finished runs). That tie is broken by E6b and by the truncation feature term.
- **Nulls:**
  - `PERCEPTION-NOISE` (decay without a step in E1-S; parity-preserving misreads in E3);
  - `NOISY-EXACT` (E1-S soft, E3);
  - `RANDOM` (E2, E4, E5);
  - all bounded by at least one set.
- **Weakest rows:**
  - F (WALK / min-conflicts) is best bounded by E5 (0.06); it is only ~ elsewhere.
  - H (sampler) is bounded only by E5 (0.08), which makes the E5b lift pairs essential rather than optional.
- **Not in the matrix** (qualitative here): E1-S placement / growth / framing, E2 entailment, and E6b. B4 `FIRST` is covered only by the E2 entailment rendering, where it is predicted per item.

---

## 3. Phase 2 (only if behavioural evidence): mechanistic tests

Run only if Phase 1 gives E an "explicit" or "implicit" verdict for some model and condition.

**State variables.** For each variable: its prefix-BP-t marginal (the `BP-t-CAUSAL` state) at each of its mentions, t = 0..6. For the target, the answer-position readout.

| ID | Model | Method | Prediction | Moves weight toward E when | Bounds π\_E when |
|---|---|---|---|---|---|
| M1 | Qwen3-4B / 8B / 14B (direct); Qwen3-14B thinking and gpt-oss-20b (pre-CoT position) | Linear ridge probes for **residualised** round-t targets (BP-t minus its projection on BP-(t−1) and on surface covariates: occurrence count, position, distance to the question, negation). Splits by formula and by halves of the name pool. | The layer where the round-t residual becomes decodable rises with t (≈ 2 layers per round, §1.7) up to a ceiling | Rising layer profile; selectivity over every control ≥ pre-set margin | Only t = 0 is decodable, or no layer ordering |
| M1-ctrl | Same | Controls: (i) **future-BP** (full-formula BP at early positions, causally unavailable: must be at chance, which catches leakage via generator statistics); (ii) degree-preserving rewired-formula BP (selectivity; Hewitt & Liang 2019, report C); (iii) random-init model; (iv) competitor states (UP flags, exact prefix marginals, GREEDY's state, `POLARITY`) | E's targets beat all of them | — | A competitor state or the future-BP control decodes as well |
| M2 | Same | Head-level attention mass from a mention to same-variable mentions, same-clause literals, and clause ends containing the variable, vs a token-distance-matched null. Path patching on E1-S pairs. | An edit's effect at distance d flows through mentions of intermediate variables, not straight to the answer | Path through intermediates carries ≥ 50% of the effect | Direct edit→answer path dominates |
| M3 | Qwen3-4B / 8B | Linear DAS (Geiger et al. 2023, report C) for "j's marginal" at j's last mention, layer ℓ. Interchange from items where j's marginal is opposite; read queries about v at distances 1–6 (prefix-cached). | Effect ∝ BP sensitivity ∂M\_v/∂M\_j. Zero beyond the radius left after layer ℓ. Zero along paths running backwards in token order. | Locality curve matches and beats competitor subspaces | Effect independent of distance, or no better than random-init or norm-matched random directions (Cox et al. 2026); fails the dormant-pathway check (Makelov et al. 2024) |
| M4 | Qwen3-8B | Tuned lens on E2 A-opposed items | The favoured answer flips from A to B at a layer (we report *which heuristic* the lens favours, not when; Csordás et al. 2025) | A → B flip | B never favoured |
| M5 | Qwen3-14B thinking; R1-Distill-Qwen-14B | Pre-CoT probe for the BP-t answer vs the final answer (Cox et al. 2026 design) | E-implicit: BP answer decodable before thinking and predicts unfinished runs' answers | AUC ≥ 0.7 on unfinished runs | Chance |

**Positive controls.**

- Small decoder-only transformers (L ∈ {4, 6, 8, 12}) trained on the same encoding to output BP-t, t ∈ {0..4}. The pipeline must recover r\* = t both behaviourally (E1-S) and mechanistically (M1–M3).
- WP-2 compiled with ALTA (report D).
- Negative controls: a `POLARITY` emulator (r\* = 0) and a toy trained on exact labels within its capacity.
- Linear maps only, because non-linear causal abstraction is trivially satisfiable (Sutter et al. 2025, report C). Every competitor's variables are scored (Méloux et al. 2025, report C).

**Why these model sizes.**

- Qwen3-4B and 8B share 36 layers, and so does gpt-oss-120b. So depth and width vary separately, which is a direct test of P1. Tiny models are excluded.
- circuit-tracer transcoders exist for Qwen3 up to 14B and for GPT-OSS-20B (report C).
- Qwen3-14B thinking vs R1-Distill-Qwen-14B (48 layers) gives two reasoning post-trainings of the same base family.

---

## 4. Build scope

| Component | Person-days | Shared? |
|---|---|---|
| E zoo: SAT `BP` / `WP` / `SP`-t, `BP-DEC-MAX` / `OUT`, `SP-DEC`, `BP-t-CAUSAL`, `LOCAL-EXACT-r`, `E-in-D`, `EQ-CONTRACT`; colouring `BP` / `WP` / `LOCAL-t` / `BP-DEC`; entailment readout; unit tests (§1.3) | 6 | E-specific (`E-in-D` reuses D's DPLL) |
| Factor-graph library: distances, balls, computation trees, girth and cycles, random 2-lifts, hashing | 3 | **Shared** |
| Solver wrappers: SAT, backbone, model counting, colouring CSP | 2 | **Shared** |
| Sparse-skeleton builder: chains, hubs, pendants, diamonds, no-op nulls, surface balancing, decoys | 4 | E (B1 can reuse chains) |
| Periphery–core builder: cores at n\*, BP-uninformative backbone search, link, periphery, order control | 4 | **Shared** with B1, C, D (any family that needs above-budget items with controlled local structure) |
| E2 factorial + NL rendering | 2 | E |
| E3 cover pairs | 1 | E |
| E5 lifts + marginal-gap search | 2 | E |
| Renderers; name pools checked per tokenizer; token-count assertions | 3 | **Shared** |
| Item verification (every family's prediction per cell) | 3 | E glue over the shared zoo |
| Runner for open reasoning models (vLLM; effort; budget forcing; logprobs; prefix cache; teacher forcing; trace prefill) | 5 | **Shared** |
| Trace pipeline: segmenter, parser, LLM-coder harness, DSL, synthetic traces | 8 + 2 (E measures T1, T3, T4) | **Shared** (+2 E) |
| Human trace coding (2 coders × 3 days) | 6 | **Shared** |
| Analysis: radius/knee estimators, step-vs-decay, mixed models, calibration comparison, faithfulness, combination rule | 6 | E (the likelihood core is shared, DESIGN O3) |
| Fake-model positive controls | 2 | E (framework shared) |
| Pilot: n\* calibration, token use, truncation rates | 3 | **Shared** |
| **Phase 1 total** | **≈ 32 E-specific + ≈ 32 shared** | |
| Phase 2 (only if): activation caching and span alignment (3, shared), probes + controls (4), attention–adjacency (3), DAS with locality readout (5), BP-t emulator toys (4), ALTA WP-2 (4), random-init and competitor controls (2) | ≈ 25 | |

The shared pieces worth building first, because every vertical needs them:

- the periphery–core builder;
- the semantic no-op null and surface-balancing utilities;
- the tokenizer-checked renderers;
- the trace pipeline.

---

## 5. Compute budget

Output tokens are priors, to be recalibrated in the pilot. "Truncated" means the run hit the 32k thinking cap.

| Eval ID | Domain | # items | Conditions (e.g. direct, CoT-1k, CoT-4k) | Samples/item | Avg prompt tokens | Avg output tokens per condition | Needs activations? (Y/N) |
|---|---|---|---|---|---|---|---|
| E1-S | SAT-CNF (hard + soft) | 4,960 (thinking subset: 300, hard channel) | direct (all); think-2k, think-hi (subset) | direct 1 (greedy + logprobs); think 1 (3 on 20%) | 900 | direct 3; think-2k 1,800; think-hi 6,000 (≈1% truncated) | N |
| E1-S | Colouring (hard + soft) | 4,960 (thinking subset: 300) | direct (all); think-2k, think-hi (subset) | same | 520 | direct 3; think-2k 1,800; think-hi 5,000 (≈1%) | N |
| E1-C | SAT-CNF, periphery–core | 1,152 | think-hi; direct | think 1 (3 on 20%); direct 1 | 2,150 | think-hi 22,000 (≈35% truncated); direct 3 | N |
| E2 | SAT-CNF, periphery–core | 720 | think-hi; direct | same | 2,200 | think-hi 22,000 (≈35%); direct 3 | N |
| E2 | Entailment-NL | 480 | think-hi; direct | same | 4,700 | think-hi 24,000 (≈40%); direct 3 | N |
| E3 | Colouring (two groups) | 1,120 | direct; think-512; think-2k; think-8k | 1 | 360 | direct 3; think-512 500 (mostly capped, by design); think-2k 1,500 (≈30% capped at m ≥ 11); think-8k 2,500 (≈2%) | N |
| E3 | SAT (≠-cycles + filler) | 1,120 | direct | 1 | 880 | direct 3 | N |
| E4 | Random 3-SAT | 720 (think-8k subset: 240) | think-hi; think-8k (subset); direct | 1 (3 on 20%) | 1,680 | think-hi 21,000 (≈38% truncated; ≈65% at α ≥ 4.7 and n ≥ 36); think-8k 7,500 (≈80% capped); direct 180 | N |
| E5 | SAT (E5a: 96 formulas; E5b: 48 pairs = 96 formulas) | 192 formulas (1,536 direct queries) | think-hi; direct | think 8; direct 1 (logprobs) | 1,130 | think-hi 8,000 (≈5% truncated); direct 3 | N |
| E6a | SAT, tree-like | 200 | direct (free run + 2 teacher-forced scoring passes) | 1 + 2 passes | 950 | 150 (free run); 0 (scoring passes) | N (logits only) |
| E6b | SAT | 120 | think-hi + trace-prefill continuations | 1 base + 2 × 2 continuations | 1,200 (continuations: + ≈ 4,000 trace prefix) | base 8,000; continuation 6,000 | N |
| **Dev batches** (dev split only; gpt-oss-20b high effort first; every cell covered, 5 skeletons per cell) | | | | | | | |
| E1-S dev | SAT-CNF | 310 (5 skeletons × 60 cells + 10 growth); thinking subset: 30 (hard channel, 2 skeletons × 5 d × 3) | direct (all); think-2k, think-hi (subset) | 1 | 900 | as full study | N |
| E1-S dev | Colouring | 310 (thinking subset: 30) | same | 1 | 520 | as full study | N |
| E1-C dev | SAT-CNF | 120 (5 skeletons × 24 cells) | think-hi; direct | 1 | 2,150 | think-hi 22,000; direct 3 | N |
| E2 dev | SAT-CNF | 120 (5 × 24) | think-hi; direct | 1 | 2,200 | think-hi 22,000; direct 3 | N |
| E2 dev | Entailment-NL | 120 (5 × 24) | think-hi; direct | 1 | 4,700 | think-hi 24,000; direct 3 | N |
| E3 dev | Colouring | 140 (5 × 28 cells) | direct; think-512; think-2k; think-8k | 1 | 360 | as full study | N |
| E3 dev | SAT | 140 (5 × 28) | direct | 1 | 880 | direct 3 | N |
| E4 dev | Random 3-SAT | 120 (5 × 8 α × 3 n) | think-hi; direct | 1 | 1,680 | think-hi 21,000; direct 180 | N |
| E5 dev | SAT | 20 formulas (5 tree, 5 loopy, 5 lift pairs) | think-hi; direct | think 8; direct 1 | 1,130 | think-hi 8,000; direct 3 | N |
| E6a dev | SAT | 20 | direct | 1 + 2 passes | 950 | 150 | N (logits only) |
| E6b dev | SAT | 10 | think-hi + prefill continuations | 1 + 2 × 2 | 1,200 (+ ≈ 4,000) | base 8,000; continuation 6,000 | N |
| P2-M1/M4/M5 (Phase 2) | SAT (E2 + E5a + 2,000 probe formulas) | 2,000 (+ reuse) | direct; think-hi (pre-CoT position only) | 1 | 1,000 | 0 (forward pass only) | Y |
| P2-M2/M3 (Phase 2) | SAT-CNF (E1-S subset) | 1,000 | direct | 1 | 900 | 3 | Y |

**Dev-batch totals.**

- **Items:** ≈ 1,430 distinct items: every cell of every eval, 5 skeletons per cell.
- **Tokens on gpt-oss-20b at high effort:** ≈ 13M output, of which E2 (5.5M), E1-C (2.6M) and E4 (2.5M) are most; ≈ 3.5M prompt.
- **Time:** about 1–2 H100-hours at the throughput assumed below.
- **This is the first run.** It calibrates n\*, the truncation rates and the per-item token priors used in this table.

**Totals (Phase 1, full study).**

- **Items:** 15,744 distinct items (E5 counted as formulas).
- **Per primary model:**
  - ≈ 95M thinking-output tokens, plus ≈ 28M for the 3-sample 20% subsets: **≈ 125M output tokens**;
  - ≈ 36M prompt tokens.
  - E1-C, E2 and E4 account for ≈ 70% of the output.
- **Direct conditions are cheap:** < 0.3M output tokens per model. So the 6-model `direct-ladder` costs ≈ 18M prompt tokens per model and almost no output.
- **Large models.** Run R1 and Qwen3-235B on a core subset only (E1-C, E2-SAT, E4, E5): ≈ 93M output tokens each.
- **Overall:** ≈ 1.05B output tokens.
- **GPU time** (rough priors, factor-2 uncertainty):
  - the seven smaller models, assuming ≈ 2.5k tokens/s per H100 for ≤ 32B dense or small-active MoE at 32k context: ≈ 100 H100-hours;
  - R1 and Qwen3-235B, assuming ≈ 4k tokens/s per 8×H100 node: ≈ 100 H100-hours (or R1 via an API);
  - **total ≈ 200 H100-hours.**

**Which items will be truncated at 32k.**

- **E1-C and E2:** items whose core is at or above n\*. Since cores are centred on n\*, about half are unsolved by design and many of those run to the cap. Entailment-NL slightly more often.
- **E4:** items at α ≥ 4.2 with n ≥ n\*. Nearly all UNSAT items at α ≥ 4.7 with n ≥ 36, since random UNSAT needs long refutations. Verma 2026 (report A) reports random UNSAT exhausting a 16k budget.
- **E1-S, E3, E5 and E6:** rarely.
- **Treatment:** truncated runs get a forced answer, and are analysed as a censored stratum and in sensitivity analyses. They are never silently counted as wrong.

---

## 6. What would falsify E's role, and the link to Step 6

### What would bound E's role (pre-registered; graded)

E's role is the weight π\_E per model × condition, with feature terms. "Falsifying" it means an upper bound near zero, or weight that moves to a named competitor.

**Single pass** (direct and low-budget). The soft-radius part of E (BP-t, t ≥ 1) is bounded if:

- the E1-S soft-channel mixture gives π\_BP-t≥1 ≤ 0.1 (upper 95%); and
- E2 gives π\_E ≤ 0.06 (upper 95%).

Its weight then goes to C0 (radius 0), or to B1 if the hard channel carries weight. The *local* class as a whole is bounded by:

- far edits (d ≥ 6) carrying as much weight as near ones after token controls; or
- E3's Δ ≈ 1 at every m, which moves weight to global procedures.

**Best effort** (primary). The bound is π\_E ≤ 0.1 (upper 95%) jointly across:

- E1-C (the Δacc mixture);
- E2 under `think-hi`;
- E6b (the BP-DEC pattern's share).

This covers E-explicit and E-in-D together. The feature term on unfinished runs is reported even when the main weight is bounded. A small E weight concentrated on unfinished runs is a finding, not a null.

**Marginals.** E5 bounds BP's share of free-choice preferences, π\_BP-t≥1 ≤ 0.1, when POLARITY or the exact marginals absorb the weight. The lift slope bounds π\_H directly.

**Knee.** E4's mixture bounds π\_E-members against D, F and C2 using answers, and gives an independent estimate from DSL scaled by w.

**Traces alone never bound or raise π\_E.** MP-style traces without answer weight lower the model's faithfulness weight w (§2.7).

**Reported per model × condition:**

- π\_E with a 95% interval, split into members (BP-t by t, WP, BP-DEC, E-in-D);
- the posterior over r\*;
- lift;
- ΔLL vs the null mixture and vs the mixture with E replaced by its nearest competitor;
- the trace share × w;
- feature terms (d, α, n/n\*, budget, framing, run completion).

### Link to the Step-6 RASP-L account (PAPER_SKELETON §10)

**The §1.7 sketch makes four predictions before data.** Each Phase-1 outcome maps onto them:

1. **P1** (depth bounds the one-pass radius). Tested by `direct-ladder`.
   - If r̂ tracks depth (0.6B ≈ 1.7B; 4B ≈ 8B) and stays ≤ L/4, round-by-round MP is a depth-bounded short program. That is the shape the RASP MDL account (Zhou et al. 2024, report D) needs for a class-C heuristic.
   - If r̂ tracks capability rather than depth, the program isn't round-by-round, or depth isn't the binding cost. That is evidence for ALTA's "fewest layers" measure being wrong here (report D).
2. **P2** (causal mask). Order and placement effects of the `BP-t-CAUSAL` kind tie the heuristic to its transformer implementation. An abstract, order-free radius would favour a representation that integrates at late positions.
3. **P3** (hard vs soft). The E2 outcome is a direct test of the MDL prediction that WP is preferred unless soft marginals pay off. Soft (BP) behaviour would mean the length measure must charge less for numeric precision than a primitive count does. Hard (WP / UP) behaviour favours precision-weighted measures.
4. **P4** (thinking). If r̂ grows linearly with budget (E1-S `think-B`, E3) and E6b shows the decimation pattern, CoT is iterating a short per-round or per-fixing program (n-RASP-L; Fan et al. 2025, report D). If thinking switches to D (global search with backtracking), the account must say why a longer stack-based program wins once depth is relaxed. That is DESIGN §3 O6's "relaxing d moves weight from C to S".

**Program lengths** (pre-registered, length measure as DESIGN O6 fixes it):

| Member | Length | Depth |
|---|---|---|
| `BP-t` / `WP-t` | ≈ 7 + 4t lines | 1 + 2t layers |
| `BP-DEC` | Per-fixing step ≈ 7 + 4t\_dec lines; seq | — |
| `POLARITY` (= BP-0) | ≈ 6 lines | 1 layer |

These rows go into PAPER_SKELETON Table 15.

---

## 7. Evidence-table row

| Behavioural lift over baseline | Mixture weight | Signatures matched | Process match | Probe selectivity | Intervention vs competitor | Control recovered | RASP-L length / class |
|---|---|---|---|---|---|---|---|
| [lift (95% interval); ΔLL vs null and vs nearest competitor] | [π\_E mean (95% interval) per model × condition, split by member; feature terms] | [/7: §2.9 rows] | [trace share × w; FT5 κ] | [Phase 2: M1] | [Phase 2: M3] | [weight recovery: bias / width / coverage on graded and feature-dependent mixtures; Phase 2 toys] | ≈ 7 + 4t / const (`BP-t`); seq (`BP-DEC`) |

---

## 8. Open questions

1. **n\* calibration:** one core size per model family, or per model? Per model is fairer but makes cross-model comparison harder.
2. **Equivalence chains may be too salient.** The alternative is 3-clause soft links, which attenuate under BP and bring back the attenuation-vs-radius confound. Pilot both on one model?
3. **Should E1-C get an entailment rendering,** as E2 has? It would cost ≈ 25M output tokens per model.
4. **Name pool:** real single-token words (priors attach to meaning) or meaningless single tokens (rare, possibly multi-token in some tokenizers)?
5. **Trace coder:** an open model (reproducible) or a frontier API model (likely more accurate)? The κ validation decides, but the choice affects cost.
6. **Budget forcing for gpt-oss's harmony format,** and the empty-think trick for R1: confirm that both produce valid "direct" conditions. Otherwise report those models' direct runs as "low effort" only.

---

## References and provenance

**From the repo's literature reports.**

- **Report F:** Sato, Yamada & Kashima 2019; Bresler & Huang 2021; Gamarnik & Sudan 2017; Rahman & Virág 2017; Wein 2022; Krzakala et al. 2007; Kuhn, Moscibroda & Wattenhofer 2016; Mézard, Parisi & Zecchina 2002; Selsam et al. 2019 (NeuroSAT); Greenlaw, Hoover & Ruzzo 1991 (compendium); Achlioptas & Coja-Oghlan 2008; Coja-Oghlan 2017 (JACM).
- **Report C:** Csordás, Manning & Potts 2025; Hu, Zhou & Zhang 2025; Ye, Fu, Jia & Sharan 2025; Saparov et al. 2025; Hewitt & Liang 2019; Sahoo et al. 2026; Sutter et al. 2025; Méloux et al. 2025; Makelov, Lange & Nanda 2024; Geiger et al. 2023 (DAS); Gupta et al. 2024 (InterpBench); Chen et al. 2025 (faithfulness); Lanham et al. 2023; Cox, Kianersi & Garriga-Alonso 2026; Bogdan et al. 2025.
- **Report D:** Zhou et al. 2024; Fan et al. 2025; Shaw et al. 2025 (ALTA); Li et al. 2024.
- **Report A:** Zhang, Chen & Chen 2026; Verma 2026; Hazra et al. 2025.
- **Report B:** Glöckner 2009.

**Checked this session (arXiv abstract pages).**

- Braunstein, Mézard & Zecchina (2005). *Survey propagation: an algorithm for satisfiability.* Random Structures & Algorithms 27. arXiv cs/0212002.
- Coja-Oghlan (2011). *On belief propagation guided decimation for random k-SAT.* SODA. arXiv 1007.1328. Failure at c·r(k)/k with r(k) ≈ 2^k ln 2.
- Montanari, Ricci-Tersenghi & Semerjian (2007). *Solving constraint satisfaction problems through belief propagation-guided decimation.* Allerton. arXiv 0709.1667. No k = 3 threshold in the abstract.
- Ricci-Tersenghi & Semerjian (2009). *On the cavity method for decimated random constraint satisfaction problems and the analysis of belief propagation guided decimation algorithms.* J. Stat. Mech. P09001. arXiv 0904.3395. No numbers in the abstract.
- Vontobel (2013). *Counting in graph covers: a combinatorial characterization of the Bethe entropy function.* IEEE Trans. IT 59. arXiv 1012.0065.
- Murphy, Weiss & Jordan (1999). *Loopy belief propagation for approximate inference: an empirical study.* UAI. arXiv 1301.6725.
- Model layer counts: Hugging Face `config.json` for Qwen3-0.6B / 1.7B / 4B / 8B / 14B / 32B / 30B-A3B / 235B-A22B-Thinking-2507, gpt-oss-20b / 120b, and DeepSeek-R1-Distill-Qwen-14B, fetched 2026-11-13.

**Not cited (leads only).**

- Jones & Plassmann's parallel colouring: the `LOCAL-∞ = FIRST-FIT` equivalence is stated as our derivation.
- Weiss on loopy BP correctness.
- Mulet et al. on colouring BP.
- s1-style budget forcing: described operationally, not cited.
