# T2. RASP-L length, learnability and simplicity bias: which heuristics would training *select*?

*Theory-crafting note, written 2026-11-13, before any project data. One of three. T1 covers expressivity, circuit complexity and the budget line; T3 covers LLM precedent and training pressure. Overlaps are marked [→T1] and [→T3] and are not argued here. This note builds on [literature/D_rasp_algorithms.md](../literature/D_rasp_algorithms.md) and does not repeat it. It is the first draft of [PAPER_SKELETON.md](../PAPER_SKELETON.md) Table 15.*

**Code.** Everything marked **Code** runs from [`scripts/theory/rasp/`](../../scripts/theory/rasp/) (numpy + matplotlib, fixed seeds; the full run takes about 30 s):

- `rasp.py`: an instrumented RASP-L interpreter. It counts primitives, tracks attention depth and flags rule-bending.
- `programs_sat.py`, `programs_ent.py`, `programs_col.py`: the programs, with reference implementations and equivalence tests.
- `search_refs.py`: the sequential members.
- `frontier.py`: writes `results.json`, [T2_frontier.png](T2_frontier.png) and [T2_perstep.png](T2_perstep.png).
- `ood.py`: writes `ood.json`.

**Citation status.**

- ✓ = verified this session: title, authors, year, venue, and the specific claim. Zhou et al. was checked against the PDF text; the rest by a verification pass over primary sources.
- [D] / [C] / [F] = verified in that literature slice, not re-checked here.
- [?] = not verified.

**Regimes**, the same labels as T1 and T3:

- **1P:** one forward pass, single-token answer.
- **DS:** direct answer with a structured output (colouring, assignment). The output stream is itself a sequence of steps.
- **TH:** thinking, ≈ 32k tokens.

"Direct" below means 1P, or DS where stated.

**Support types:**

- **Thm** = theorem.
- **Code** = construction tested in code: the program runs, it matches a reference implementation, and its accuracy is measured.
- **Est** = pseudo-RASP-L length estimated from measured components.
- **Emp** = empirical result in the literature.
- **Arg** = argument.

---

## 0. Summary

1. **The direct-answer frontier is short cues plus shallow causal propagation** (Code).
   - On random 3-SAT, `DENSITY` (8 primitives, 2 layers) is the only short program above base rate (0.787 vs 0.728). Unit propagation is inert on pure 3-SAT, because it has no unit clauses.
   - On puzzle-like CNF and on entailment, `UP-k` is on the frontier (puzzle CNF 0.865 at k = 2; entailment 0.958–0.967), with `ALWAYS-*` and `ECHO` below it.
   - `POLARITY` (9 primitives) is the frontier for single-variable value choice. Causal `BP-2` (81) adds nothing on a training-like distribution.
2. **Restriction (B4) members cost no extra length.** `FIRST∘UP-k` and `BICOND∘UP-k` are the B1 skeleton with a different lookup table: same length, same depth (Code).
   - Under validity labels they are strictly dominated.
   - They overtake `UP-k` only if ≈ 50% (`FIRST`) or ≈ 70–80% (`BICOND`) of training labels on the discriminating items endorse the restricted reading.
   - So RASP-L simplicity cannot explain B4. If models use it, the data put it there [→T3].
3. **Greedy with state is not RASP-L in terse form.** A terse `FIRST-FIT` step must join prompt structure (edges) with generated state (colours). We found no int8 program for that join. It takes 25 primitives with set-valued state, which is non-RASP-L and needs width ≥ n (Code + Arg).
   - With a *verbose* trace that restates each neighbour's colour, every token is a strict RASP-L step (53 primitives, 3 layers; it reproduces FIRST-FIT exactly; Code).
   - The account therefore predicts the **style** of thinking traces (copy, then evaluate), not only the heuristic.
4. **In TH the ranking flips toward exact search.**
   - Per-step programs for C, D and F share about 40–50 primitives of trace machinery (copy, lookup, dispatch). They differ by roughly 10–40 primitives.
   - Iterated accuracy on training-size instances differs a great deal: `DPLL-b` 1.00, `WALK` 0.88, `UC` 0.43 on random 3-SAT, n = 20 (Code for accuracy, Est for lengths).
   - So two-part MDL favours D (truncated exact search) below the budget line. Above it, it favours D's default answer.
5. **Surprise.** With a small, fixed atom vocabulary, the MDL-optimal *direct* entailment program for N ≳ 10⁴ examples is a parallel truth table (`PROBE-16`).
   - It has 147 primitives but only **3 layers**, and it is exact in-distribution.
   - Out of distribution it becomes a fixed-probe sampler with 56% commission (Code).
   - So a "heuristic" seen on hard items can be the out-of-distribution shadow of a program that was exact on training items.
6. **Simplicity measures mostly agree.**
   - Average sensitivity ranks the members as length does on SAT, and penalises B4 and `MM` more than B1 on entailment (Code).
   - They disagree on `MATCH`: short, but the most sensitive member. Both measures put it off the frontier.
7. **Weakest links.**
   - Length conventions: maps, n-ary maps, set-valued state.
   - Our programs are upper bounds, not minima.
   - Linear MDL makes length irrelevant at LLM-scale N.
   - From-scratch theory may not transfer to pretrained LLMs.

---

## 1. Score table

Scores run from −2 (long, off the frontier, high sensitivity) to +2 (short, on the frontier).

- **1P/DS** = a single forward pass, or a terse structured answer.
- **TH** = a per-step program iterated over about 32k tokens.

The training-distribution assumptions are in §4.1. "Frontier" means non-dominated on (length, accuracy).

| Family | Key member | 1P/DS | TH | Conf. (1P / TH) | Support | One-line reason |
|---|---|---|---|---|---|---|
| A1 constant | `ALWAYS-SAT`, `ALWAYS-NO` | +1 | −1 | high / med | Code | Always the frontier's left endpoint, and MDL-optimal only for N ≲ 10³. In TH it reappears as D's default at the cap. |
| A2 cue | `DENSITY` | **+2** random k-SAT; 0 puzzle CNF | −1 | high / med | Code | 8 primitives, 2 layers, sensitivity 0. The only short program above base rate on 3-SAT. Barely above base on mixed-width CNF. |
| A2 cue | `PRIMACY` | −1 | −1 | med | Code | 20 primitives at `ALWAYS-NO`'s accuracy (0.703 vs 0.698): dominated |
| A2/B4 cue | `MATCH` | −2 | −1 | med | Code | Dominated by `ALWAYS-NO` (0.61 vs 0.70). The most sensitive member (0.20). |
| B1 relax | `UP-k` (k ≤ 3, causal) | **+2** | +1 | high / med | Code | On the frontier on entailment and puzzle CNF; sound. About 1 layer per round (2-literal clauses) or 2 (3-literal). In TH it is absorbed into D's propagation. |
| B3 convex | `LP-ROUND` | −2 | −1 | low | Arg | Needs iterated real arithmetic. No int8 RASP-L program, and exact LP is P-complete [F]. |
| B4 restrict | `FIRST`, `BICOND` | −1 | −1 | med / low | Code | Same length as `UP-k` (Δ = 0) but less accurate under validity labels. Selected only when labels endorse the reading (q\* ≈ 0.5 / 0.7–0.8). |
| B4/C4 | `MM`, `ETR` (simplified) | −1 | −1 | low | Code (acc.) + Arg | 0.76 accuracy. Model sets are set-valued, so there is no int8 constant-depth program for unbounded disjunctions, and the per-step form needs verbose model lists. |
| B5 | `EXPECTED-COST` | 0 | 0 | low | — | Not analysed |
| C0 one-shot | `POLARITY` | **+2** | 0 | high / med | Code | 9 primitives, 2 layers, 0.960 on single-variable value choice. `BP-1c`/`BP-2c` add nothing. In TH it serves as D's value ordering. |
| C1 fixed order | `FIRST-FIT` | 0 | +1 | low / med | Code | Terse: not strict RASP-L (25 primitives with set-valued state). Verbose: a 53-primitive strict step, 0.82 on n ≤ 12. At N ≳ 10³ it loses to DSATUR or repair *if* their estimated lengths hold. |
| C1 | `NN` (TSP) | −1 | +1 | low | Est + Arg | Terse needs the visited set (set-valued). Verbose scan ≈ 45 ± 10. Accuracy not computed. |
| C2 adaptive | `DSATUR` | −2 | +1 | med / low | Code (acc.) + Est | An argmax over candidates whose scores depend on generated state cannot be done in one step. 0.998 on n ≤ 12 at ≈ 90 ± 20 per step. |
| C2 adaptive | `UC` (decision use) | −2 | −1 | med | Code (acc.) + Est | Below base rate as a decision procedure (0.43 at n = 20, α = 4.26) |
| C3 random order | `RO-FIRST-FIT` | −1 | 0 | med | Arg | RASP-L is deterministic, so randomness exists only through sampling |
| C4 online | `ONLINE-STATE(k)` | −1 | 0 | low | Arg | A sequential state update: k slots, about 7 primitives per premise [V: B4] |
| D truncated search | `DPLL-b` | −2 | **+2** | high / med | Code (acc.) + Est | No constant-depth program. Per step ≈ 75 ± 20, within 1.5× of greedy, and exact on training sizes. |
| E message passing | `BP-2`, `LOCAL-t` | −1 | −1 | med / low | Code | `BP-2c`: 81 primitives, 0.958 vs `POLARITY` 0.960. `LOCAL-3`: 0.73 vs FIRST-FIT 0.82. As text it is Θ(m) tokens per round [→T1]. |
| F local search | `WALK` | −2 | 0 | med / low | Code (acc.) + Est | 0.875 at n = 20 vs `DPLL-b` 1.0 at a similar estimated length: dominated |
| F local search | `MIN-CONFLICTS` | −2 | +1 | med / low | Code (acc.) + Est | 0.968 (20 repairs after FIRST-FIT) at ≈ 80 ± 20 |
| G decompose | `IGNORE-CROSSLINKS` | 0 | 0 | low | Arg | The base solver + 2 primitives (a part id conjoined into each selector). Nearly free, so the data decide, as for B4. |
| H sample | `SAMPLE-m` / `PROBE-m` | −1 SAT; +1 ENT (fixed vocab) | 0 | med | Code | `PROBE-2`/`-4` dominated on SAT. `PROBE-16` is exact in-distribution on ≤ 4 atoms and has the fewest layers, but is SAMPLE-like out of distribution. |
| I selection | mixture | 0 | 0 | low | Arg | Pays for the selector plus every member. Favoured only where members are complementary on the training distribution. |
| nuisance | `NOISY-EXACT` | −2 | **+2** | med / low | Arg | No uniform exact 1P program. In TH, exact search with slips is what MDL predicts below the budget line (same evidence as D). |

**Reading the TH column.**

- In TH the length differences shrink to about 10–40 primitives on a shared base of about 50.
- Accuracy therefore dominates, and the scores are weaker evidence than in 1P.
- If one generic "copy, look up, evaluate, decide" interpreter executes procedures described in the trace, per-step length stops discriminating at all. The choice then comes from reward and pretraining text [→T3]. See §5.3.

---

## 2. Conventions

### 2.1 What RASP-L allows

Checked against Zhou et al. 2024, §3.2 and Appendix E, PDF text ✓.

- Programs are straight-line: no loops or branches.
- Every operation is causal.
- Values are int8.
- Indices admit only order comparisons and successor or predecessor.
- `aggregate` reduces with mean, max or min.
- "Every call to `sel_width` … returns a new type which inherits from IndexInt", and the outputs of two `sel_width` calls are "incomparable".
- Each line "compiles into at most one Transformer layer".

**Two observations.**

- **(i) Zhou et al. break their own width rule.** Their Listing 5 (`binary_mode`) compares the outputs of two different `sel_width` calls with `gt`, which their App. E forbids. The rule is not applied consistently in their own listings, so `rasp.py` records such comparisons as a flag (`cross_width_compare`) rather than an error. None of our SAT, ENT or COL programs needed it: we count with mean-aggregation (int8 fractions) or with max/min-of-index tricks instead.
- **(ii) int8 mean aggregation is coarse.** It truncates, so `DENSITY` can place its threshold only on a coarse grid (127·n/T ∈ {5, 6} brackets α ≈ 4.2). That is an artefact of the language, not of transformers.

### 2.2 Length and depth

**Length.** One unit per call of `select`, `aggregate`, `sel_width`, `tok_map` or `seq_map`, counted by running the program (`rasp.measure`). `tokens`, `indices` and `full` are free.

Two conventions inflate or deflate counts, and we report them:

- **(a)** A select whose predicate conjoins two comparisons counts as **1**. One head can add the two score terms; Tracr has `SelectorAnd`.
- **(b)** An n-ary elementwise map counts as **n − 1** binary maps. It is flagged `nary_map` because the binary tree needs int8 intermediate codes, which exist only for small joint domains.

**Other measures.** We also report **heads** (the number of `aggregate` + `sel_width` calls) and **layers** (the longest chain of attention operations; maps are fused into the following MLP).

- ALTA found learned behaviour tracks the fewest-layers program, not the fewest-rules one ✓ (Shaw et al. 2025), so layers is a rival length measure.
- Frontiers by primitives and by heads coincide in every task except entailment (§4.2).

**Depth classes**, as in PAPER_SKELETON §5:

- **const** = fixed depth.
- **seq** = needs chain of thought, or depth that grows with the instance.

**Set-valued extension.** `aggregate_set` returns the *set* of selected values. It is not RASP-L: per-position state of size up to n means width ≥ n, which is non-uniform. It is flagged `set_valued`, and used only to show what a wide-residual transformer could do that RASP-L cannot.

**All programs are upper bounds on the minimal length.** Zhou et al. call the minimum "likely intractable" to compute ✓.

### 2.3 Serialisations

From `instances.py`:

- **CNF:** `BOS ( l l l ) ( l l l ) … Q [v]`. A literal is ±v.
- **Entailment:** `BOS` *premises* `? L END`. The grammar:
  - `L .`
  - `L and L .`
  - `either L or L .`
  - `if L then L .`
  - L = atom (1–6) | `not` atom

  Connectives come first, so a literal's role is known causally.
- **Colouring:** `BOS a b , a b , … ;`. Then either the terse answer `v c v c …` or the verbose answer `v : u₁ c₁ u₂ c₂ … -> c |`.

---

## 3. Programs

Each entry gives the program idea, its measured length (primitives / heads / layers), and its test.

### 3.1 Direct (1P) programs, tested

**`ALWAYS-SAT` / `ALWAYS-NO` / `CONST-TRUE`** (1 / 0 / 0). One constant map.

**`DENSITY`** (8 / 2 / 2; `programs_sat.density`). Equivalence-tested against `ref_density` on 200 instances, 0 failures.

```
var      = tok_map(tok, |lit|)                                   # 0 off literals
first    = seq_map(aggregate(select(var,var,==), indices, min), indices, ==)   # first occurrence
new_var  = seq_map(first, var, 127·[first ∧ var>0])
frac     = aggregate(select_all, new_var, mean)                   # 127·(#distinct vars)/T
answer   = tok_map(frac, ≥ θ)                                     # θ tuned on train
```

**`UP-k` causal, SAT** (`up_causal`; k = 1, 2, 3: 31/7/3, 51/12/5, 71/17/7). Equivalence-tested against `ref_up_causal` on 200 instances × 3 values of k, 0 failures.

- Derived literals sit at clause-close positions.
- Each round:
  - a literal looks up its variable among *earlier* derived literals (one head, max and min of the sign);
  - each clause aggregates `sat`, `max` and `min` of its non-false literal tokens;
  - `max == min` means unit, and `max = −128` means conflict.
- About 20 primitives and 2 layers per round, plus 11 primitives of setup and readout.
- The causal mask means a unit can only fire clauses that come **after** it.

**`POLARITY`** (9 / 2 / 2; equivalence-tested). The sign of the mean polarity of the target variable's occurrences in the prompt (+4 primitives to mask the query token).

**`BP-t` causal, int8 mean-field** (`bp_causal`; t = 1, 2: 62/19/4, 81/25/6).

- A clause, at its close token, sends each of its 3 literal slots the product of the other two literals' P(false). One select per slot reaches back 1–3 positions.
- A later literal position, or the query, averages the incoming signed messages per slot (3 heads per round).
- Mean, not sum, aggregation makes this a normalised BP.
- The program *is* the member, so its accuracy is measured by running it. Non-causal float BP-t (`ref_bp`) is the comparison.
- The E vertical's sketch (7 + 4t) is shorter because it leaves out slot routing and causality. Even at 15 primitives for BP-2, the conclusion in §4 stands: BP is not more accurate than `POLARITY` on the training distribution.

**Entailment members**, sharing a 13–17 primitive parse (shifts for `not`, role table, query literal):

- **`MATCH`** (17/3/2): the conclusion literal occurs anywhere.
- **`PRIMACY`** (20/4/2): it occurs in the first premise.
- **`UP-0` = `ECHO`** (17/3/2): it is a stated fact.
- **`UP-k`** (54/14/4, 93/25/5, 141/38/6 for k = 1, 2, 3): each round adds about one layer.
  - (i) Forward: a 2-literal clause, stored at its second literal, derives the other literal from an earlier fact on the same variable. This is a *sign-carrying* lookup, so the decision table can be swapped.
  - (ii) Backward: a fact derives from an earlier clause on its variable, into a fresh slot per round.
- **`FIRST∘UP-k`**: the role table maps "either A or B" to fact A and drops B. **+0 primitives.**
- **`BICOND∘UP-k`**: the decision table also licenses b⇒a and ¬a⇒¬b. **+0 primitives.**
- Tested on 9 hand-checked schemas: MP and MT in both orders, DS, illusory "A or B ⊢ A", AC, DA, and forward and backward chains. 0 failures.

**`PROBE-m`, entailment** (`probe`; m = 4, 16: 51/8/3, 147/20/3).

- Probe i makes atom a true iff bit (a − 1) of i is set.
- It looks for a probe that satisfies every premise and falsifies the conclusion.
- `PROBE-16` equals `EXACT` on 300 random items with ≤ 4 atoms (0 mismatches).

**`PROBE-m`, SAT** (m = 2, 4: 19/5/3, 29/9/3). SAT iff a fixed assignment (all-true, all-false, odd-true, even-true) satisfies every clause. Equivalence-tested.

### 3.2 Per-step programs, tested (DS and TH)

**`FIRST-FIT`, terse** (25 / 6 / 3, flags `set_valued`, `nary_map`; `programs_col.ff_terse_step`).

```
N(u)   = aggregate_set over edges with endpoint u  (two directions)      # set-valued
used   = aggregate_set(select(colour-token's vertex ∈ N(v)), colour)      # set-valued
next   = SEMI→1 | colour→prev+1 or STOP | vertex v→mex(used)
```

**`FIRST-FIT`, verbose** (53 / 14 / 3, strict apart from `nary_map`; `ff_verbose_step`). It emits `v : u₁ c₁ … -> c |` and relies on fixed order: "already coloured" ⟺ u < v, so no state lookup is needed to find the candidates.

- The next listed neighbour is min{w ∈ N(v) : u_last < w < v}. It takes two conjunctive selects over the edge list, one per direction.
- A listed neighbour's colour is fetched from that vertex's own line (`-> c` carries the line owner).
- The final colour is the mex over the k = 3 colour-presence heads in the current line.
- Run autoregressively, both programs reproduce Python FIRST-FIT on 30 + 40 random planted graphs (0 mismatches, empty graphs excluded).

### 3.3 Why the terse greedy step resists RASP-L

Status: an argument with a counting bound, not a proof.

A terse FIRST-FIT step at the token for vertex v must decide "∃ an earlier output position j with colour c and an edge (u_j, v)".

- **Prompt positions can't see the output.** Edge positions precede the output, so they cannot carry colours (causality).
- **The query must test adjacency directly.** The query position must attend to output positions j with a predicate pred(key_j, query_v) that equals adjacency. Adjacency differs per instance, while `pred` is fixed, so key_j and query_v must *encode* the graph.
- **Counting bound.** With c int8 sequences per position, one fixed predicate can represent at most 2^(16cn) of the 2^(n(n−1)/2) graphs on n vertices. A single join therefore fails for n > 32c, and program length must grow with n, which is non-uniform.
- **What we haven't ruled out.** Multi-hop routes through intermediate positions. A communication-complexity proof in the style of Huang et al. 2025 ✓ is open (§7).

**What wide models can do instead.** A real transformer with d_model ≫ n can put a neighbourhood indicator in superposition in the key (the 25-primitive set-valued program). Retrieval noise would then grow with degree and n.

### 3.4 Per-step programs: estimates (Est)

These are built from components measured in §3.1–3.2:

| Component | Primitives |
|---|---|
| Parse or setup | 7 (CNF) – 15 (entailment) |
| Same-variable lookup | 2 |
| Line bookkeeping (line start, line owner) | about 6 |
| Next-token dispatcher (n-ary map) | about 7 |
| Copy-and-evaluate one 3-literal clause against trail values | about 10 |
| Running argmin over a scan | about 4 |

A verbose format is assumed throughout: decisions, a propagated trail and clause checks are written out (the "state-line" format of the D/F vertical).

| Member (TH step) | What one step must do | Est. length (heads) | Tokens per decision |
|---|---|---|---|
| `UC` / `GUC` | Scan clauses (copy-evaluate); first unit or shortest open clause; assign; propagate | 65 ± 15 (≈ 18) | Θ(m) |
| `DPLL-b` | UC step + find the last unflipped decision (1 lookup) + copy the trail prefix (2–3) + budget counter (`sel_width`) + conflict branch | 75 ± 20 (≈ 22) | Θ(m) |
| `WALK` | Scan for a falsified clause; break counts of its 3 variables (a sole-true-literal flag per clause + 3 counts); argmin; copy with flip | 85 ± 20 (≈ 25) | Θ(m) first pass, then Θ(deg) |
| `DSATUR` (colouring) | FIRST-FIT verbose + a saturation entry per neighbour after each colouring + a scan over uncoloured vertices with running argmax (degree tie-break) | 90 ± 20 (≈ 25) | Θ(n + deg) |
| `MIN-CONFLICTS` | Per-vertex conflict scan + k colour-conflict counts + argmin | 80 ± 20 | Θ(n + k·deg) |
| `NN` (TSP, distance matrix) | Scan unvisited w (successor + visited check), pair-key distance lookup, running min | 45 ± 10 (≈ 12); terse with a set-valued visited set ≈ 15 | Θ(n) |
| `LOCAL-t` (in-prompt, 1P) | Per round: neighbour's current colour via the edge partner (2), k presence heads, mex | ≈ 3 + 2k per round, ≈ 35 at t = 3, 2 layers per round | — |
| `IGNORE-CROSSLINKS` | Solver S with a part id conjoined into every selector | len(S) + 2 [V: B1] | as S |
| `MM` / `ETR` (premise update) | Copy the model list, product with the premise's alternatives, drop inconsistent models, (ETR) issue-matching filter | 50–70; model list Θ(2^#disjunctions) tokens | Θ(models × atoms) |
| `SAMPLE-m` (TH) | Write a candidate, check each premise, check the conclusion | ≈ 40 (copy-evaluate) | Θ(m·|premises|) |
| `NOISY-EXACT` (TH, truth table) | Increment an assignment (reverse-order addition style, Zhou Listing 9 ✓) + evaluate premises | 60–80 | Θ(2^atoms · |premises|) |

**Not expressible in 1P under RASP-L** (no constant-depth, uniform, int8 program; Arg): `DPLL-b`, `WALK`, `MIN-CONFLICTS`, `DSATUR`, `UC` to fixpoint, `NN`, `MM`/`ETR` with unbounded disjunctions, exact SAT and entailment, and `LP-ROUND`.

- **Partial exception: truncations.** These are expressible at the cost of length growing with their depth: `UP-k`, `LOCAL-t`, `BP-t`, and the parallel `PROBE-2^a`, whose length grows exponentially in the number of atoms.
- **Implication.** In 1P these members can appear only through such truncations, or (DS) through the output stream. Their 1P error signatures are those of the truncation, not of the full heuristic.

---

## 4. Length vs accuracy: the frontier

### 4.1 Training-distribution assumptions

These are stated so that they can be argued with. The intent is "textbook puzzles and RL on small verifiable instances" [→T3 for whether that is right].

| Task | Distribution | Base rate |
|---|---|---|
| SAT-DEC/puzzle | Mixed-width CNF (15% units, 35% binary, 50% ternary), n 4–10, m/n 0.5–3 | 72% SAT |
| SAT-DEC/bench | Random 3-SAT, n 8–14, α 3.0–5.5 | 73% SAT |
| SAT-VAL | Satisfiable random 3-SAT, n 6–12, α 1.5–4.2. Answer: a value for a named variable shared by some model | 92% "true" is OK |
| ENT | 2–4 consistent premises over 3–4 atoms; the conclusion's atom is mentioned | 30% "follows" |
| COL | Planted 3-colourable G(n, p), n 6–12, p 0.3–0.6. Success = proper colouring with ≤ 3 colours | — |

Each task has N = 600 items, seed 0.

### 4.2 Results

Code: `frontier.py`. The figure is [T2_frontier.png](T2_frontier.png). ★ = on the (length, accuracy) frontier.

| Task | Member | Length / heads / layers | Accuracy |
|---|---|---|---|
| SAT-DEC/puzzle | `ALWAYS-SAT` ★ | 1 / 0 / 0 | 0.718 |
| | `DENSITY` ★ | 8 / 2 / 2 | 0.727 |
| | `UP-1c` | 31 / 7 / 3 | 0.718 |
| | `UP-2c` ★ | 51 / 12 / 5 | 0.865 |
| | `UP-3c` ★ | 71 / 17 / 7 | 0.893 |
| | `PROBE-2` / `-4` | 19 / 29 | 0.473 / 0.593 |
| | *UP to fixpoint, non-causal (seq)* | — | 0.997 |
| SAT-DEC/bench | `ALWAYS-SAT` ★ | 1 | 0.728 |
| | `DENSITY` ★ | 8 / 2 / 2 | **0.787** |
| | `UP-kc`, `UP-fix` | 31–71 | 0.728 (inert: no unit clauses) |
| | `PROBE-2` / `-4` | 19 / 29 | 0.28 / 0.29 |
| SAT-VAL | `CONST-TRUE` ★ | 1 | 0.917 |
| | `POLARITY` ★ | 9 / 2 / 2 | **0.960** |
| | `BP-1c` / `BP-2c` | 62 / 81 | 0.960 / 0.958 |
| | *BP-1 / 2 / 5, non-causal float* | — | 0.968 / 0.978 / 0.985 |
| ENT | `ALWAYS-NO` ★ | 1 | 0.698 |
| | `MATCH` | 17 / 3 / 2 | 0.610 |
| | `PRIMACY` | 20 / 4 / 2 | 0.703 |
| | `ECHO` (UP-0) ★ | 17 / 3 / 2 | 0.897 |
| | `FIRST-0` | 17 / 3 / 2 | 0.848 |
| | `UP-1` ★ | 54 / 14 / 4 | 0.958 |
| | `FIRST∘UP-1` / `BICOND∘UP-1` | 54 / 14 / 4 | 0.870 / 0.935 |
| | `UP-2` ★ (by length only) | 93 / 25 / 5 | 0.967 |
| | `FIRST∘UP-2` / `BICOND∘UP-2` | 93 / 25 / 5 | 0.875 / 0.928 |
| | `PROBE-4` | 51 / 8 / 3 | 0.637 |
| | `PROBE-16` ★ | 147 / 20 / **3** | **1.000** |
| | *Python: `MM` (initial models)* | — | 0.758 |
| | *Python: `SAMPLE-1/2/4/8`* | — | 0.45 / 0.54 / 0.73 / 0.83 |
| | *Python: `FIRST∘EXACT` / `BICOND∘EXACT` / `NOISY-EXACT` (2%/row)* | — | 0.870 / 0.951 / 0.975 |
| COL (per step, DS/TH) | `FIRST-FIT` (verbose 53 / terse 25 set-ext.) | 53 / 14 / 3 | 0.818 |
| | *Python: `RO-FF`* | — | 0.837 |
| | *Python: `DSATUR`* | — | 0.998 |
| | *Python: `LOCAL-1/2/3`* | — | 0.12 / 0.53 / 0.73 |
| | *Python: `MIN-CONFLICTS-20` / `-100`* | — | 0.968 / 0.985 |
| | *Python: `RANDOM`* | — | 0.055 |

**Frontier members.** These are the direct-answer candidates the account predicts:

- SAT-DEC/puzzle: {`ALWAYS-SAT`, `DENSITY`, `UP-2c`, `UP-3c`}.
- SAT-DEC/bench: {`ALWAYS-SAT`, `DENSITY`}.
- SAT-VAL: {`CONST-TRUE`, `POLARITY`}.
- ENT: {`ALWAYS-NO`, `ECHO`, `UP-1`, `UP-2`, `PROBE-16`}.
  - By heads, `UP-2` drops out: `PROBE-16` has fewer heads (20 vs 25) and fewer layers (3 vs 5) and is exact.
  - **Never on the frontier:** `MATCH`, `PRIMACY`, `FIRST`, `BICOND`, `PROBE-4`, causal `BP-t`.

### 4.3 Two-part MDL

The objective is

total(P) = 16 bits × |P| + N · H₂(err_train(P))

where 16 bits per primitive covers the op type, two argument references and a predicate or table index. It is crude; vary it and the crossover N scales proportionally.

The MDL winner as training-set size N grows, with the transitions:

| Task | N ≤ 10³ | N ≈ 3·10³ | N ≥ 10⁴ |
|---|---|---|---|
| SAT-DEC/puzzle | `ALWAYS-SAT` | `UP-2c` | `UP-3c` |
| SAT-DEC/bench | `ALWAYS-SAT` | `DENSITY` | `DENSITY` |
| SAT-VAL | `CONST-TRUE` | `POLARITY` (from N ≈ 10³) | `POLARITY` |
| ENT | `ALWAYS-NO` → `ECHO` (N ≈ 10³) | `UP-1` | **`PROBE-16`** |

**Capacity reading.** A rival reading takes sample complexity to be exponential in program size, after Zetzsche et al. 2026 ✓. Note that this is only a proven *upper* bound, and only for the C-RASP⁺/C-RASP₁ fragments. Under it, a member is learnable iff β^heads ≤ N, and we pick the most accurate learnable member.

- With β = 2, entailment stays at `ECHO` up to N = 10⁴, moves to `UP-1` at 10⁵–10⁶, and reaches `PROBE-16` only at 10⁸.
- SAT/puzzle moves `DENSITY` → `UP-2c` (10⁴) → `UP-3c` (10⁶).

**The general point.** In linear MDL every crossover lies at N ≈ 10³–10⁴. That is far below the puzzle-like data an LLM sees. **At LLM scale linear MDL makes length nearly irrelevant: the selection is "the most accurate *expressible* program".** The bite comes from four places:

- (i) Expressibility: depth, causality, uniformity (§3.3–3.4).
- (ii) Capacity-type sample complexity, if the exponential bounds are anywhere near tight.
- (iii) Optimisation not finding the MDL optimum: Shaw et al. 2026 [D].
- (iv) The *training* distribution, on which cheap programs are nearly exact (`UP-fix` 0.997 on puzzle CNF, `DSATUR` 0.998 on n ≤ 12). Their failures appear only out of distribution, which is Zhou's diversity condition ✓.

### 4.4 Restrictions are a data effect, not a simplicity effect

Code: `label_mixture`. Suppose a share q of training labels follows a restricted reading R instead of validity, as human-written text might [→T3].

- Since `FIRST∘UP-2`, `BICOND∘UP-2` and `UP-2` have *identical* length, the winner is decided by majority on the items where they disagree.
- `FIRST∘UP-2` overtakes `UP-2` at **q ≈ 0.5**.
- `BICOND∘UP-2` overtakes it at **q ≈ 0.7–0.8**.
- `MM` labels never make a B4 member win; at q = 1, `ECHO` wins.

### 4.5 Sensitivity as a rival simplicity measure

Code. Sensitivity is the mean fraction of single local edits that flip the answer: literal sign flips (SAT) or negation toggles in premises (ENT).

**SAT/puzzle:**

| Member | Sensitivity |
|---|---|
| `ALWAYS-SAT`, `DENSITY`, `UP-1c` | 0 |
| `UP-2c` | 0.016 |
| `UP-3c` | 0.023 |
| `UP-fix` | 0.047 |
| `EXACT` | 0.053 |
| `PROBE-2` / `-4` | 0.079 / 0.090 |

**ENT:**

| Member | Sensitivity |
|---|---|
| `ALWAYS-NO` | 0 |
| `ECHO` | 0.071 |
| `FIRST-0` | 0.107 |
| `PRIMACY` | 0.118 |
| `UP-1` / `UP-2` | 0.128 / 0.135 |
| `BICOND∘UP-1` | 0.163 |
| `EXACT`, `PROBE-16` | 0.173 |
| `FIRST∘UP-2` / `BICOND∘UP-2` | 0.182 / 0.184 |
| `MATCH` | **0.201** |
| `MM` | **0.233** |

**Agreement with the RASP-L ranking:**

- On SAT, the two orderings match.
- On ENT both favour B1 over B4 and `MM`. Restricted readings are *more* sensitive than validity: they add commission dependencies.
- **Disagreement:** `MATCH` is among the shortest members but the most sensitive.

**Other simplicity results:**

- **Sensitivity bias.** Transformers prefer low-sensitivity functions: Bhattamishra et al. 2023 ✓ (empirical); Vasudeva et al. 2025 ✓. Hahn & Rofin 2024 ✓ show sensitive functions need large weight norm or LayerNorm blow-up and sit in sharp, isolated minima. This predicts that exact SAT near threshold is hard to learn in 1P while `DENSITY`, `POLARITY` and shallow `UP` are easy. That agrees with the frontier.
- **Parity and min-degree.** Parity-like structure is the extreme case. Gradients carry exponentially little information about the target (Shalev-Shwartz et al. 2017 ✓). SGD needs about n^O(k) steps for sparse parity (Barak et al. 2022 ✓). A min-degree interpolator is learned on unseen inputs (Abbe et al. 2023 ✓, for sparse targets and a class of models). Hence XOR-SAT items should be answered only by A1/A2 cues in 1P.
- **Globality** (Abbe et al. 2024 ✓; the positive direction is a conjecture). Long derivation chains are not weakly learnable without a scratchpad. This agrees with UP-k's depth limit, and with TH helping.
- **Shortcut learning** (Geirhos et al. 2020 ✓) and the statistical-feature results on logic (Zhang et al. 2023 ✓). These predict cue members in 1P, and agree.
- **Grokking and circuit efficiency** (Power et al. 2022 ✓; Nanda et al. 2023 ✓; Varma et al. 2023 ✓). These predict movement along the frontier with dataset size and training time, toward the efficient general circuit. This is our MDL path, with a critical-N twist: semi-grokking near crossover points.
- **Where they disagree with RASP-L:** `MATCH`, and the `PROBE-16` case. `PROBE-16` has exact-level sensitivity, so a sensitivity bias would not favour it over UP-2 (0.135). RASP-L under the heads or layers measure does favour it.

---

## 5. Direct vs per-step: does the distinction change the ranking?

Yes, in three ways.

### 5.1 Different objects

In 1P the program computes the answer, and its length must cover the whole computation within fixed depth. In TH the program is the next-token function, and the heuristic is its iteration (Zhou et al.'s scratchpad argument ✓: a scratchpad "unroll[s] a loop"; n-RASP-L, Fan et al. 2025 ✓, empirical).

**Two consequences:**

- **(a) Depth stops binding.** UP to fixpoint (0.997 on puzzle CNF), DSATUR (0.998) and DPLL (exact) are all available.
- **(b) The cost moves from program length to token count.**

### 5.2 Per-step programs mostly share their bulk

FIRST-FIT verbose (measured) is 53 primitives. About 30 of them are trace machinery:

- line bookkeeping;
- the dispatcher;
- edge lookups;
- the colour fetch.

The heuristic-specific delta between members of C, D and F is about 10–40 primitives (§3.4, Est). Meanwhile, iterated accuracy on training-size items spans 0.43 (`UC`) → 0.875 (`WALK`) → 1.0 (`DPLL-b`) on SAT at n = 20, and 0.82 (`FIRST-FIT`) → 0.97 (`MIN-CONFLICTS`) → 0.998 (`DSATUR`) on colouring ([T2_perstep.png](T2_perstep.png)).

So the per-step frontier is accuracy-dominated, and MDL selects **truncated exact search (D)** on SAT and **DSATUR/repair** on colouring as soon as N ≳ 10³.

**The 1P/TH ranking flips:**

| Regime | Favoured | Off the frontier |
|---|---|---|
| 1P | A2, C0, B1 truncations, H-parallel | D and F (inexpressible) |
| TH | D (and the nuisance "noisy exact") | A and C1 |

Under our token-cost assumptions (6 tokens per clause check, 32k budget), DPLL-b is exact at n ≤ 20 and drops toward its default answer at n ≈ 30–40. That matches T1's budget-line estimate (n\* ≈ 30 with listing-order branching) [→T1].

**Above the line, the account predicts D's default** (A1-like answers, or a greedy completion of the partial trail). It does not predict a switch to a different heuristic family.

### 5.3 A shared interpreter would remove length from TH

If a model learns one generic per-step program ("copy a constraint, look up the values it mentions, evaluate it, choose the next action as the trace says"), then *which* heuristic it runs is written in the trace, not in the weights. Per-step length is then the same for every member, and RASP-L says nothing about the TH choice beyond expressibility and format. That choice is set by reward and by pretraining text [→T3].

We cannot settle from theory whether LLM thinking is "one interpreter running described procedures" or "a per-heuristic step". This is the main reason the TH column carries lower confidence.

### 5.4 The account predicts trace format

Per-step RASP-L programs cannot join prompt structure with generated state unless the trace puts both near each other (§3.3). So the account predicts:

- **(i) Copy-then-evaluate traces.** The constraint is restated, the values it needs are copied next to it, and only then is a judgment emitted.
- **(ii) Token cost.** Θ(deg) tokens per decision for fixed-order greedy; Θ(m) for D and F.
- **(iii) Errors on terse outputs.** Where outputs are terse (DS, thinking off), FIRST-FIT-like answers should show adjacency-retrieval errors that grow with degree and n. These look like phantom or missed constraints rather than procedure errors (conjecture; the wide-residual superposition story of §3.3).

---

## 6. Predictions

Each prediction names the eval it maps to. **Embarrassing results for the account are in bold.**

**P1. 1P on random 3-SAT is `DENSITY` + `ALWAYS-SAT`.**

- The mixture weight on B1 should be ≈ 0, because UP is inert on pure 3-SAT.
- Maps to: A/H E2 (K/J padding), E3 (α × n sweep), the D/F E1 density arm.
- Prediction: the knee in 1P error vs α sits at the model's tuned density threshold, and is flat in n at fixed α. DENSITY is size-invariant.
- **Wrong if:** 1P answers on pure 3-SAT at n ≥ 20 track exact satisfiability or UP-refutability beyond what density explains. That would mean a short structural shortcut we have not found.

**P2. 1P entailment and puzzle CNF behave like causal UP-k.**

- Sound, with omission errors and an accuracy step in derivation depth d.
- d\* is at most 1 round per layer for 2-literal clauses and 1 round per 2 layers for 3-literal clauses (our constructions). Expect about half that, since later layers mostly refine (Csordás et al. 2025 [C]).
- An order effect: in our simulation, UP-3c on puzzle CNF is 0.94 with units first, 0.895 as drawn, and 0.848 with units last (`ood.py`). UP to fixpoint is order-invariant (0.995).
- Maps to: B1 E1 (depth ladder), B1 E3 (premise position × proof order).
- **Wrong if:** 1P accuracy is invariant to the order of supporting facts at depth ≥ 2, or errors include frequent commissions on catch items.

**P3. Depth, not width, sets d\* for UP-k and the BP radius.**

- Qwen3-32B (64 layers) vs 14B (40 layers) at equal width: d\* ratio ≈ 1.6.
- Maps to: B1 E1, E E1-S.
- **Wrong if:** d\* is equal across the depth contrast but varies with width or parameter count.

**P4. B4 weight follows label statistics, not hardness.**

- FIRST and BICOND weights should be higher for natural-language framings than for formal notation, where pretraining labels endorse "or ⇒ first" and conditional perfection less.
- They should not grow with derivation depth or premise count at fixed framing.
- RL-on-verified-answers models should show lower B4 weight than base or SFT models trained on human text.
- Maps to: B4 E1 (format), E2 (5 forms + instruction), H6.
- **Wrong if:** B4 commission grows with instance size or depth at fixed framing, as a capacity shortcut would. That would mean a length advantage for restrictions that our programs don't see.

**P5. In 1P, single-variable value choices track `POLARITY`, not `BP-t`.**

- Maps to: E E5 (BP vs exact marginals), E E1-S.
- A within-pass radius > 1 requires a causal, slot-routed program of at least 60 primitives that our simulation finds no more accurate on training-like data.
- **Wrong if:** 1P preferences show second-order (BP-1) evidence on tree-like items. Then the training distribution rewards BP more than ours does, or a much shorter BP program exists.

**P6. In TH, below the budget line, behaviour is truncated exact search.**

- D, plus the noisy-exact nuisance, not C1 or F.
- Above the line: D-b's default, or a greedy completion of the trail. Not WALK-like near-misses.
- Maps to: D/F E1 (β and termination type), E2 (b̂(T)), E4 (trap pairs), C E5.
- **Wrong if:** F-style infeasible near-misses dominate TH errors above n\*. F's per-step length is not shorter than D's, so the account has no reason to pick F.

**P7. Traces are copy-then-evaluate (§5.4).**

- Judgments are preceded within a short window by restated constraints and copied values.
- Trace tokens scale with Σdeg (FIRST-FIT) or with m per decision (D).
- Maps to: C §2.4 trace codes, D/F §2.6, A/H §2.5.
- **Wrong if:** correct answers at n ≈ 30–50 come with terse traces that never restate the constraints they use. That would mean wide or set-valued state is used freely, and the int8 RASP-L abstraction is the wrong level.

**P8. Terse DS greedy outputs show retrieval-type violations.**

- Violations concentrate on edges with high-degree endpoints, and grow with n at fixed density.
- Maps to: C E5, B4 E6, D/F E6 violation profiles.
- **Wrong if:** violations are uniform over edges, or track processing order and not degree.

**P9. Toy models (Table 16).**

- **(a)** Trained on fixed-vocabulary entailment with ≤ 4 atoms and N ≳ 10⁴, models learn the parallel truth table: exact in-distribution, and about 50% commission at 5–6 atoms. The OOD blind spot is counter-models that need a high-index atom to be true.
- **(b)** With fresh atom names per item, the probe table cannot be a fixed map. Rank-based probes need comparisons on `sel_width` outputs, so they are lenient-only. Models should then learn UP-k, with omission-only OOD errors.
- **(c)** On random 3-SAT decision, models decompile to an 8-primitive density program.
- **(d)** The learned member moves ALWAYS → ECHO → UP-1 → UP-2/PROBE as N grows from 10² to 10⁵.
- **Wrong if:** (a) and (b) give the same OOD error type, or decompiled programs are dense (Huang et al. 2026 ✓) even when the toy fits in-distribution.

**P10. H signatures out of distribution.**

- If an LLM's 1P entailment is PROBE-like, its commission errors should be predicted by *which* atoms a counter-model needs true (late-mentioned atoms), not by counter-model rarity alone, as SAMPLE-m would predict.
- Maps to: A/H E6 (ρ-graded), B4 E1L (blind-spot regression).

**Results that would embarrass the account as a whole:**

- **(i)** 1P mixture weight on a long or off-frontier member (MATCH, PRIMACY, causal BP-2) exceeds the weight on the frontier member at the same accuracy.
- **(ii)** TH errors below n\* are greedy-shaped (C1) on items where D is exact within budget.
- **(iii)** The mixture weights of 1P members fail to fall with length or rise with frontier membership, *after* controlling for accuracy on a matched training-like set.

---

## 7. Open questions

1. **Prove or refute §3.3.** Is there a uniform int8 RASP-L program for one terse FIRST-FIT step? A communication-complexity argument, as in Huang et al. 2025 ✓, is the natural route.
2. **Find shorter programs.** Our UP, BP and PROBE programs are hand-written upper bounds. Enumerating programs (ULTK, Cheng 2025 [D]) or synthesising them (Jiang et al. 2026 [D]) could find shorter ones and move members on or off the frontier, especially `BP-2` and `BICOND`.
3. **Pin the length measure.** Which measure (primitives, heads, layers, bits) do trained models track? ALTA ✓ says layers. Under layers, `PROBE-16` (3 layers) beats `UP-2` (5) outright. Pre-register all three.
4. **Set the bits per primitive and the effective N.** Linear MDL crossovers sit at N ≈ 10³–10⁴, so for LLMs the length term is nearly inert unless the capacity reading holds. Which reading applies is an empirical question for the toy study (Table 16).
5. **Interpreter or per-heuristic step (§5.3)?** A test: does an in-context description of an unfamiliar procedure (e.g. "colour by largest degree first") get executed as faithfully as familiar ones at matched per-step complexity [→T3]?
6. **Test the training-distribution assumptions.** Our distributions are guesses at "textbook plus small RL". The frontier for ENT moves if yes-rates or premise forms differ. We should rerun `frontier.py` on samples of real textbook items.
7. **Fold in nuisance noise.** `NOISY-EXACT` is outside RASP-L. Should per-step slip rates enter the MDL accounting, for example through the precision of attention over long traces?

---

## 8. Table 15, first draft

| Family (member) | RASP-L length (primitives / heads) | Depth (layers) | Depth class | Accuracy, training-like | On the frontier? | Predicted rank (1P, in task) |
|---|---|---|---|---|---|---|
| A (`DENSITY`) | 8 / 2 | 2 | const | 0.787 random 3-SAT (base 0.728); 0.727 puzzle CNF (base 0.718) | ✓ (both) | 1 on random 3-SAT; 3 on puzzle CNF |
| B1 (`UP-2`) | 51 / 12 (SAT, causal); 93 / 25 (ENT) | 5 / 5 | const (fixed k) | 0.865 puzzle CNF; 0.728 random 3-SAT (inert); 0.967 ENT | ✓ puzzle CNF, ENT (length); ✗ ENT by heads/layers (vs `PROBE-16`) | 1 on ENT (open names) and on puzzle CNF |
| B4 (`FIRST`) | 17 / 3 (alone) = `ECHO`; 93 / 25 with UP-2 (= UP-2) | 2 / 5 | const | 0.848 / 0.875 | ✗ (dominated at equal length) | Below `UP-k` and `ECHO` unless ≥ 50% of labels endorse it |
| C (`FIRST-FIT`) | per step 53 / 14 verbose; 25 / 6 terse with set-valued state (not RASP-L) | 3 per step | seq (const per step) | 0.818 (n 6–12, ≤ 3 colours) | ✓ at its length (per step); dominated by DSATUR/repair if N ≳ 10³ (Est) | 1 for DS colouring with thinking off; 2–3 in TH |
| E (`BP-2`) | 81 / 25 (causal, int8) | 6 | const | 0.958 (POLARITY 0.960) | ✗ | Below `POLARITY` |
| C0 (`POLARITY`) | 9 / 2 | 2 | const | 0.960 | ✓ | 1 on single-variable value choice |
| H (`PROBE-16`) | 147 / 20 | 3 | const (non-uniform in #atoms) | 1.000 in-distribution; 0.61 OOD | ✓ | 1 for fixed-vocab ENT at N ≳ 10⁴ (toy) |
| D (`DPLL-b`) | per step ≈ 75 ± 20 (Est) | ≈ 5 per step | seq | 1.0 (n ≤ 20 at 32k) | ✓ (TH) | 1 in TH below n\* |

The "Observed rank" column stays empty until the evals run.

---

## References

✓ = verified this session (PDF text for Zhou et al.; abstract and full-text checks for the rest). [D], [C], [F] = from that literature slice, not re-checked.

- Abbe, E., Bengio, S., Lotfi, A., Rizk, K. (2023). Generalization on the Unseen, Logic Reasoning and Degree Curriculum. *ICML 2023*. arXiv:2301.13105. ✓ (min-degree interpolator for sparse targets and a class of models).
- Abbe, E., Bengio, S., Lotfi, A., Sandon, C., Saremi, O. (2024). How Far Can Transformers Reason? The Globality Barrier and Inductive Scratchpad. *NeurIPS 2024*. arXiv:2406.06467. ✓ (the learnability claim is a conjecture; the negative direction is proved for one task).
- Barak, B., Edelman, B. L., Goel, S., Kakade, S., Malach, E., Zhang, C. (2022). Hidden Progress in Deep Learning: SGD Learns Parities Near the Computational Limit. *NeurIPS 2022*. arXiv:2207.08799. ✓
- Bhattamishra, S., Patel, A., Kanade, V., Blunsom, P. (2023). Simplicity Bias in Transformers and their Ability to Learn Sparse Boolean Functions. *ACL 2023*. arXiv:2211.12316. ✓ (empirical).
- Cheng (2025). *Beyond Memorization: Evaluating Length-Generalization in Transformer-based Language Models*. MS thesis, Univ. of Washington. [D]
- Csordás, R., Manning, C. D., Potts, C. (2025). Do Language Models Use Their Depth Efficiently? *NeurIPS 2025*. arXiv:2505.13898. [C]
- Fan, Y., Du, Y., Ramchandran, K., Lee, K. (2025). Looped Transformers for Length Generalization. *ICLR 2025*. arXiv:2409.15647. ✓ (n-RASP-L definition; length generalisation shown empirically).
- Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., Wichmann, F. A. (2020). Shortcut learning in deep neural networks. *Nature Machine Intelligence* 2:665–673. ✓
- Greenlaw, R., Hoover, H. J., Ruzzo, W. L. (1995). *Limits to Parallel Computation: P-Completeness Theory*. Oxford University Press. [F] (entry numbers not re-checked).
- Grünwald, P. D. (2007). *The Minimum Description Length Principle*. MIT Press. ✓ (crude two-part MDL, ch. 5).
- Hahn, M. (2020). Theoretical Limitations of Self-Attention in Neural Sequence Models. *TACL* 8:156–171. ✓ (the soft-attention result assumes Lipschitz components).
- Hahn, M., Rofin, M. (2024). Why are Sensitive Functions Hard for Transformers? *ACL 2024*. arXiv:2402.09963. ✓
- Huang, X., Yang, A., Bhattamishra, S., Sarrof, Y., Krebs, A., Zhou, H., Nakkiran, P., Hahn, M. (2025). A Formal Framework for Understanding Length Generalization in Transformers. *ICLR 2025*. arXiv:2410.02140. ✓ ("in the limit"; a composite regulariser).
- Huang, X., Bakalova, A., Bhattamishra, S., Merrill, W., Hahn, M. (2026). Discovering Interpretable Algorithms by Decompiling Transformers to RASP. *ICML 2026*. arXiv:2602.08857. ✓
- Jiang, Hague, Rümmer, Lin (2026). Synthesis and Verification of Transformer Programs. *IJCAI 2026*. [D]
- Li, Z., Liu, H., Zhou, D., Ma, T. (2024). Chain of Thought Empowers Transformers to Solve Inherently Serial Problems. *ICLR 2024*. arXiv:2402.12875. ✓
- Lindner, D., Kramár, J., Farquhar, S., Rahtz, M., McGrath, T., Mikulik, V. (2023). Tracr: Compiled Transformers as a Laboratory for Interpretability. *NeurIPS 2023*. [D]
- Liu, B., Ash, J. T., Goel, S., Krishnamurthy, A., Zhang, C. (2023). Transformers Learn Shortcuts to Automata. *ICLR 2023*. ✓
- Nanda, N., Chan, L., Lieberum, T., Smith, J., Steinhardt, J. (2023). Progress measures for grokking via mechanistic interpretability. *ICLR 2023*. ✓
- Pan, L., Ganesh, V., Abernethy, J., Esposo, C., Lee, W. (2025). Can Transformers Reason Logically? A Study in SAT Solving. *ICML 2025*, PMLR 267. arXiv:2410.07432. ✓ (non-uniform construction; generalisation limited to trained sizes).
- Power, A., Burda, Y., Edwards, H., Babuschkin, I., Misra, V. (2022). Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets. arXiv:2201.02177 (earlier version at the MATH-AI workshop, ICLR 2021). ✓
- Rende, R., Gerace, F., Laio, A., Goldt, S. (2024). A distributional simplicity bias in the learning dynamics of transformers. *NeurIPS 2024*. ✓ (not used in scoring).
- Saparov, A., et al. (2025). Transformers Struggle to Learn to Search. *ICLR 2025*. arXiv:2412.04703. ✓
- Sato, R., Yamada, M., Kashima, H. (2019). Approximation Ratios of Graph Neural Networks for Combinatorial Problems. *NeurIPS 2019*. ✓ (GNNs ↔ constant-round port-numbering models SB(1)/MB(1)/VV_C(1), *not* LOCAL with IDs).
- Shalev-Shwartz, S., Shamir, O., Shammah, S. (2017). Failures of Gradient-Based Deep Learning. *ICML 2017*, PMLR 70. ✓
- Shaw, P., Cohan, J., Eisenstein, J., Lee, K., Berant, J., Toutanova, K. (2025). ALTA: Compiler-Based Analysis of Transformers. *TMLR*. arXiv:2410.18077. ✓
- Shaw, P., Cohan, J., Eisenstein, J., Toutanova, K. (2026). Bridging Kolmogorov Complexity and Deep Learning: Asymptotically Optimal Description Length Objectives for Transformers. *ICLR 2026*. [D]
- Varma, V., Shah, R., Kenton, Z., Kramár, J., Kumar, R. (2023). Explaining grokking through circuit efficiency. arXiv:2309.02390 (preprint). ✓
- Vasudeva, B., Fu, D., Zhou, T., Kau, E., Huang, Y., Sharan, V. (2025). Transformers Learn Low Sensitivity Functions: Investigations and Implications. *ICLR 2025*. arXiv:2403.06925. ✓ (the v1 title differs).
- Weiss, G., Goldberg, Y., Yahav, E. (2021). Thinking Like Transformers. *ICML 2021*. [D]
- Ye, Q., Fu, D., Jia, R., Sharan, V. (2026). Transformers Provably Learn Algorithmic Solutions for Graph Connectivity, But Only with the Right Data. *ICML 2026*. arXiv:2510.19753. ✓ (the 3^L result is for a disentangled transformer).
- Zetzsche, G., Jiang, H., Yang, A., Bergsträßer, P., Sälzer, M., Chiang, D., Lin, A. W. (2026). Length Generalization for Transformers via Compression. arXiv:2609.08851. ✓ (exponential sample size is an **upper** bound, for C-RASP⁺/C-RASP₁ only).
- Zhang, H., Li, L. H., Meng, T., Chang, K.-W., Van den Broeck, G. (2023). On the Paradox of Learning to Reason from Data. *IJCAI 2023*. ✓
- Zhou, H., Bradley, A., Littwin, E., Razin, N., Saremi, O., Susskind, J., Bengio, S., Nakkiran, P. (2024). What Algorithms can Transformers Learn? A Study in Length Generalization. *ICLR 2024*. arXiv:2310.16028. ✓ (PDF: the RASP MDL principle, App. E types, Listing 5 `binary_mode`, the scratchpad argument, "likely intractable").
