# Vertical: C — Constructive / priority heuristics ("greedy")

*One file per heuristic class (template: [TEMPLATE.md](TEMPLATE.md)). Example items: [C_constructive_questions.md](C_constructive_questions.md) and [`data/examples/C_constructive.jsonl`](../../data/examples/C_constructive.jsonl).*

- **Status:** designed (v0.3, 2026-11-13). Phase 1 is behavioural only. Phase 2 (interpretability) runs only if Phase 1 finds behavioural evidence.
- **Owner:** [TODO]
- **Scope of this version.**
  1. The primary condition is open-weight reasoning models at **best effort** (high reasoning effort, up to 32k thinking tokens). Direct answers, no-think runs and budget caps are diagnostic factors.
  2. Every eval has pre-registered chain-of-thought hypotheses, a trace-coding scheme and faithfulness tests (§2.4).
  3. The first model is **gpt-oss-20b at high effort**. No model below 14B is used in Phase 1.
  4. Each eval has a dev batch (§5).
  5. Every question set states how strongly each possible outcome moves weight between theories, as likelihood ratios (§2.9, and per-item blocks in the library).
  6. **The readout is scalar explanatory power, not "used / not used".** A model may use several heuristics in part. Every result is stated as a quantity with an interval:
     - the mixture weight π_h (posterior mean, 95% interval);
     - lift (the share of errors explained above chance);
     - the log-likelihood gain (log10 Bayes factor) over the null and over the nearest competitor;
     - for traces, the faithfulness-weighted share T_h of traces matching h's signature.

     Weights may depend on item features and on the model (strategy selection, family I; §2.5).

---

## 0. Summary

**The gap.** Prior work says LLMs behave "greedily" on NP-hard problems. EHOP, GraphArena, Hazra et al. 2025 and Saparov & He 2023 infer it from accuracy or from hand-read traces; AlgoTrace shows it for nearest neighbour on TSP. The claim is not *identified*. Take the standard prompt format: vertices v1…vn listed in order, answer requested in the same order. In that format the following give the same answer on every item where greedy succeeds:

- first-fit in listing order;
- first-fit in label order;
- first-fit in answer order;
- backtracking search in that same order.

This vertical separates the members of family C from each other, and from their nearest competitors.

**Six evals**:

| ID | Question | Key counterfactual |
|----|----------|--------------------|
| **E1** Order source | How much weight does each order source carry in the model's construction: listing, labels, the requested answer order, a score order, a random order, or none? | Isomorphic copies that decorrelate listing order, label order and requested answer order. Ground truth and every order-free member are constant by construction. |
| **E2** Rule discrimination | Within an order class, how is weight split among priority rules: first-fit vs DSATUR vs largest-first; GREEDY vs UC vs GUC/SC vs POLARITY; RATIO vs DIFF vs VALUE; NN vs GREEDY-EDGE vs farthest insertion? | Single edits found by search, each changing exactly one member's output (double dissociations), plus placebo and truth-only edits. Tie psychophysics for knapsack. |
| **E3** Depth stress | How much of the order-sensitive weight is sequential execution, and how much a shallow cue, as a function of dependency depth d? Const vs seq. | NOR-circuit gadgets. Swapping two adjacent lines flips first-fit's colour of a target *d* dependency levels away, on the identical labelled graph. Answer order (forward vs reversed) and budget are varied. |
| **E4** Knees and co-failure | What share of the model's failures falls on the *same items* the C member fails on, at matched density and solver hardness? | Random 3-SAT and 3-colouring sweeps; item-level co-failure at fixed α. |
| **E5** Dead ends | What share of failures has the form of no-backtracking construction: false "impossible", or a conflict at the stuck vertex that moves with the vertex order? How is completion from a controlled state split between state-blind (C0), state-counting (C1), unit-following (C2) and search? | Stuck/control pairs matched on order-free hardness; vertex order × edge order factorial; given partial assignments; greedy countermodel construction in entailment. |
| **E6** Trace faithfulness | How reliable is the trace, as a reliability r per model and per trace code, used to weight trace evidence? | Early answering: truncate the trace at fraction f and force an answer. Trace–answer consistency tests. |

**Six design principles** (they apply to every eval):

- **P1. Order-only counterfactuals.** Re-list, relabel, or change the requested answer order without changing the instance. Ground truth and every order-invariant heuristic are then constant by construction. Any systematic change in the answer is order use, and the *pattern* of change says which order.
- **P2. Solution fingerprints.** On items with many solutions, *which* solution comes back identifies the construction, even when the answer is correct. This matters because best-effort reasoning models are often correct.
- **P3. Predictions are computed, not argued.** Every member of every family is executed on every item in every cell. Cells are filled by selecting on the computed prediction vectors, and the generator asserts them.
- **P4. The output stream is a chain of thought.** An answer written in processing order lets a model run a sequential greedy at one step per token. A "direct answer" is constant-depth only for a single-value answer, or for an answer written in an order the procedure cannot follow (E3).
- **P5. The trace is a second, unreliable channel.** Answers decide. Trace codes enter with a reliability weight measured in E6, and are used mainly to split members that agree on the answer.
- **P6. Graded, feature-dependent weights.** The estimand is a mixture π_h(φ(x), m) over every family plus a "none of the above" term, not a single winner. It is fitted hierarchically across models. Item features φ include size, density, output format, framing and budget. Each set is designed to *detect* a weight (80% power at a stated π) and to *bound* the weight of absent theories (upper 95%). Recovery is validated on planted graded mixtures (§2.10).

**Scale.**

- **Full study:** 10,960 unique items per model, plus 1,000 early-answer re-prompts per open thinking model.
- **Best-effort volume:** about 159M tokens per model (146M decoded), so about 1.43B for the 9-model panel. About 1.85B with diagnostics.
- **Dev batch:** 1,042 items, about 13M tokens on gpt-oss-20b.
- **Engineering:** about 48 person-days for behaviour (8 of them hand annotation), 2 for RASP-L, and about 19 for Phase 2.

---

## 1. The class

### 1.1 Defining idea and taxonomy position

- **Defining idea.** Consider the items one at a time in some order: variables, vertices, objects, cities or edges. Give each an **irrevocable** decision that depends on the decisions so far.
- **Formal models:**
  - **Priority algorithms** (Borodin, Nielsen & Rackoff 2003). Priorities are either *fixed* (set once) or *adaptive* (re-ordered after every decision).
  - **Width-1 pBT**: no branching and no backtracking (Alekhnovich et al. 2011). Width 1 cannot approximate knapsack better than n^−1/4, while width 2 achieves 1/2 (F report).
- **Taxonomy position.** Family C of PAPER_SKELETON Table 4:
  - **C0** one-shot scoring, with no sequential dependence;
  - **C1** fixed order;
  - **C2** adaptive order;
  - **C3** random order.
- **C4** (online, bounded state) has its own vertical and appears here as a competitor. Online first-fit colouring *is* FF-LIST, so C4 and C1 differ only through memory limits (§2.9).

**Nearest competitors** (all appear in the prediction cells):

| Family | Members | Relation to C |
|---|---|---|
| D | `DPLL-σ-b` (truncated backtracking search) | With the same variable order and value order it coincides with C1 until the first dead end. |
| F | `MIN-CONFLICTS`, `WALK` | Local search. Includes the hybrid `GREEDY+REPAIR`. |
| E | `LOCAL-t` | t rounds of ID-based local greedy. With IDs = listing positions it is *exactly* depth-truncated FF-LIST (§1.3). |
| B1 | `DROP-LAST-EDGES`, `UP-k` / `UP`-fixpoint | Systematic constraint dropping. |
| B4 | `PHANTOM-EDGE` | Adds a constraint. |
| A | `DENSITY`, `ALL-T`, `ALWAYS-YES`, `PRIMACY` | Cues. |
| H | `RANDOM` | Guess. |
| Nulls | `EXACT`, `NOISY-EXACT`, `PERCEPTION-NOISE` | `EXACT` = the model solves the item with no order dependence. `PERCEPTION-NOISE` = exact on a misread instance. |

### 1.2 Conventions (fixed for all evals)

**Orders present in a prompt**:

| Symbol | Order | Notes |
|---|---|---|
| π_L | Listing order | The vertex header line; for SAT, first mention of a variable in clause order; the item or city listing. |
| λ | Label order | Ascending numeric label. Labels are random two-digit numbers 10–99 (prefix v, x, c), drawn independently of π_L. |
| π_O | Requested answer order | LIST (= π_L), LABEL (= λ), RAND, REV (reverse π_L), or FREE. Under FREE the model chooses and the emitted order ε is recorded. |
| π_C, π_E | Clause order, edge-list order | π_E only in the separate edge-list format. |

**Tie-breaks.** The primary key is earliest in π_L; the variant key is lowest label. The tie key is part of a member's identity, and the variant is fitted only on items where ties actually occur.

**Values.** Colours are 1..k. SAT values are T/F. Polarity-count ties resolve to T.

**Dead ends.** Each member runs in two conventions:

- **-ABORT:** report IMPOSSIBLE/UNSAT at the first dead end;
- **-INFEAS:** complete the assignment anyway. The stuck vertex gets the colour in 1..k with the fewest conflicts with earlier neighbours (ties to the smallest).

**Distributional members** (C3, randomised C2, F with random initialisation) predict a distribution, estimated from 10⁴ Monte-Carlo runs with add-ε smoothing.

**Likelihood.** P(y | h, x) ∝ exp(−λ_h·d(y, h(x))), as in DESIGN §3 O3. The distance d is:

- colouring: partition distance (vertices to recolour, up to renaming colours; Hungarian assignment);
- SAT: Hamming;
- knapsack: symmetric difference;
- TSP: directed sequence edit distance from the start city (comparable with AlgoTrace), plus undirected edge distance.

**Prompt formats.** The textbook framing is used for identification. A re-themed 20% subset (exams/slots, product options, packing, deliveries) tests within-domain framing invariance (H4). Neighbour lists are written in π_L order, so first mention equals π_L. Answers come after a line `ANSWER:`. Every label has the same token count in every panel tokenizer; this is asserted, and the label set is changed if it fails.

```
Graph with 16 vertices.
Vertices (in this order): v37, v12, v85, …
Neighbours (one line per vertex, same order):
v37: v12, v61, v90
…
Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v12, v90, …
```

### 1.3 Members (pseudocode)

Reference implementations go under `src/reasoning_heuristics/heuristics/constructive/` (scratch versions were used to verify the example library).

**SAT / CSP.** State: a partial assignment A.

- A clause is *satisfied* if some literal is true under A, *falsified* if all its literals are false, and *open* otherwise.
- len_A(c) is the number of unassigned literals of an open clause c.

```
POLARITY (C0):      A[v] = T iff #pos(v) >= #neg(v)
JW (C0):            A[v] = T iff Σ_{c∋v} 2^-|c| >= Σ_{c∋¬v} 2^-|c|             # ≡ POLARITY on uniform k-SAT
MOMS (C0):          POLARITY restricted to minimum-width clauses; fall back to POLARITY   # ≡ POLARITY on uniform k-SAT
PURE+DEFAULT (C0):  pure variables get their polarity; others T                  # PURE+POLARITY ≡ POLARITY, so dropped
GREEDY-σ (C1):      for v in σ: p = #open clauses ∋ v; q = #open clauses ∋ ¬v; A[v] = T iff p >= q
                    σ ∈ {MENTION = π_L, INDEX = λ, OUT = π_O or ε}; -ABORT: UNSAT if any clause ends falsified
RO-GREEDY (C3):     GREEDY with σ uniformly random
UC-DET (C2) ≡ UP+GUESS:
                    loop: if a falsified clause exists → ABORT | continue
                          elif an open clause with len_A = 1 exists → first in π_C; make its literal true
                          else first unassigned v in π_L; A[v] = T
UC-RAND (C2):       as UC-DET, but uniform unit clause; uniform free variable and value   (Achlioptas's UC)
GUC(-DET) (C2):     pick an open clause of minimum len_A (uniform | first in π_C); satisfy a uniform | first-written literal
SC(-DET) (C2):      if open clauses with len_A <= 2 exist: prefer length 1, else 2; pick one; satisfy a literal
                    else a random | first unassigned variable, random | T value
GREEDY-CM-σ (C1, entailment yes/no):
                    CNF(P1 ∧ … ∧ Pk ∧ ¬C) in premise order (¬C last; variant ¬C first); run GREEDY-MENTION;
                    satisfying assignment found → "does not follow", else "follows"   # errs only by commission
```

The SC and GUC rules follow the usual descriptions. We could not fetch the original analyses (attributed to Chao & Franco, and to Frieze & Suen), so confirm both definitions and the attributions before citing. Thresholds are simulated on our generator.

**Colouring.**

```
FF-σ (C1):          for v in σ: c(v) = smallest positive integer not used by a neighbour earlier in σ
                    σ ∈ {LIST, LABEL, OUT (π_O or ε), REV, EDGE-MENTION (first mention in π_E)}
FF-k-σ:             with k colours; all k blocked → -ABORT "impossible" | -INFEAS least-conflict colour
LF (C1, static):    σ = degree descending (ties π_L | λ), then FF            # largest-first; EHOP's baseline
DSATUR (C2):        repeat: v = argmax saturation (#distinct colours on coloured neighbours);
                    ties: max degree in the uncoloured subgraph, then π_L | λ; c(v) = smallest free colour
RO-FF (C3):         σ uniformly random, then FF                             # RANDOM-ORDER-FIRST-FIT
GREEDY+REPAIR-σ (C→F):
                    "fewest colours" format: FF-σ, then repeatedly try to empty the top colour class by moving
                    each of its vertices (in σ) to the lowest free colour
                    k-colouring format: FF-k-σ-INFEAS, then min-conflicts moves on conflicted vertices only
```

**Two lemmas used by the generators.** Both were checked in simulation.

- **(L1) Grundy.** A proper colouring is the output of FF for *some* vertex order iff every vertex coloured j has neighbours of every colour 1..j−1. ("Up to relabelling" means there is some ordering of the colour classes for which this holds.)
  - (⇐) List the vertices class by class.
  - (⇒) FF assigns j only when 1..j−1 are already blocked.
- **(L2) FF invariance.** Adding an edge between two vertices with different FF colours never changes the FF colouring. Let u come before v.
  - If c(u) < c(v), then c(u) was already blocked for v.
  - If c(u) > c(v), then c(v) stays free.
  - No other vertex's set of earlier neighbours changes.

**Entailment.** Only `GREEDY-CM` (above). Coordinate with the B4/C4 verticals, which own ETR/PyETR.

**Knapsack.** Values and weights are 10–99; W is the capacity.

```
INPUT-FIT (C1):     items in π_L, take if it fits
RATIO-SKIP (C1):    sort by v/w desc (ties π_L), take each item that fits     # S: superincreasing knapsack P-complete
RATIO-PREFIX (C1):  same sort, stop at the first item that does not fit       # C if sorting ∈ TC⁰ (unverified)
VALUE, LARGEST-FIT, DIFF* (C1): sort by v | w | v−w desc, take if it fits    # DIFF: a no-division proxy (new)
RATIO+BEST-SINGLE (pBT width 2): max(RATIO-PREFIX, best single item)
```

**TSP.** Symmetric integer distance matrix, or integer coordinates.

```
NN-FIRST (C1):      start at the first-listed city; go to the nearest unvisited city (ties π_L)   # = NN-from-0
NN-LABEL0 (C1):     the same, starting at the smallest label
NN-BEST:            the best NN tour over all start cities
INPUT-ORDER (C1):   tour = π_L
GREEDY-EDGE (C2):   edges in ascending length; add one unless it creates degree 3 or a cycle shorter than n
FARTHEST-INSERTION (C2): start {first city, farthest city}; repeatedly add the city farthest from the tour, at its cheapest insertion point
```

**Competitor members with order variants** (owned by other verticals; this vertical adds the order variants):

| Member | Family | Definition |
|---|---|---|
| `DPLL-σ-b` | D | Branch on the first unassigned variable in σ; value order T-first, or smallest colour first; b decisions; default UNSAT/IMPOSSIBLE. |
| `MIN-CONFLICTS`, `WALK-k` | F | Random or all-1 initialisation. |
| `LOCAL-t-ID` | E | Each round, every uncoloured vertex whose ID is smallest among its uncoloured neighbours takes its smallest free colour; leftovers get colour 1. With t = ∞ this is exactly FF in ID order, so `LOCAL-t-LIST` (IDs = listing positions) is the canonical *const-depth truncation* of FF-LIST. |
| `DROP-LAST-EDGES` | B1 | Ignore the last q edges in π_E, then solve exactly. |
| `UP-k` / `UP`-fixpoint | B1 | k rounds of unit propagation, or propagation to a fixpoint. |
| `PHANTOM-ADJACENT` | B4 | Adds edges between consecutively listed vertices. |
| `DENSITY`, `ALL-T`, `ALWAYS-YES` | A | Cues. |
| `RANDOM` | H | Uniform random answer. |
| `NOISY-EXACT`, `NOISY-FF-ε` | Nulls | Per-step slips. |
| `PERCEPTION-NOISE` | Null | Exact on a randomly misread instance. |

### 1.4 Identifiability map (where members coincide)

| Coincidence | Where | Consequence / where it is broken |
|---|---|---|
| FF-LIST ≡ FF-LABEL ≡ FF-OUT ≡ DPLL-LIST | The standard format (labels follow the listing, the answer is in listing order) on every item where FF succeeds | Prior "greedy" claims cannot tell these apart. E1 decorrelates the orders. |
| FF-σ ≡ DPLL-σ (smallest-colour-first) ≡ GREEDY+REPAIR-σ | Every item where FF-k-σ succeeds | Order sensitivity alone cannot separate C1 from D. They separate on FF dead ends (E5), on copies where FF-σ is suboptimal (E1; in the library's E1 set FF-LIST needs 4 colours on c1–c5 while DPLL-LIST finds 3), and through backtracking codes in the trace. |
| MOMS ≡ JW ≡ POLARITY | Uniform k-SAT | Mixed 2+3-SAT items (E2-SAT; cf. 2+p-SAT, Monasson et al. 1999) |
| PURE+DEFAULT ≈ ALL-T | α ≳ 3 (each variable occurs about 3α times, so pure literals are rare) | Identifiable only at low α or with planted pure literals |
| RATIO-PREFIX ≡ RATIO-SKIP ≡ RATIO+BEST-SINGLE | Unless an item is skipped before a later one fits | E2-KNAP PREFIX/SKIP pairs |
| LF ≈ DSATUR | Near-regular graphs, early steps (both start at the maximum degree) | E2-COL edit search; tie keys |
| UC-DET ≈ GREEDY | When no unit clauses arise early | E5-STATE s2; E1-SAT c6 |
| FF-OUT under FREE ≡ RO-FF | When the emitted order is uncorrelated with the input orders | AR self-consistency test (E1 c5) |

### 1.5 Expressibility (depth class)

| Member | Latent depth (answer with no trace) | Evidence | Executable at one step per emitted token? |
|---|---|---|---|
| POLARITY, JW, MOMS, PURE+DEFAULT | const | Counting and threshold, so TC⁰ (F report) | No sequential dependence, so not needed |
| FF-LIST / FF-LABEL (lexicographic first-fit) | seq | LF Δ+1 colouring is P-complete (Greenlaw–Hoover–Ruzzo compendium A.2.6) | Yes, if the answer order equals the processing order |
| NN-FIRST | seq | The NN-TSP heuristic is P-complete (A.2.12) | Yes (a tour is written in visiting order) |
| GREEDY-σ (SAT) | seq by analogy | F report; our E3-SAT gadget is a *reduction sketch* from NOR circuit value to GREEDY-INDEX (verified in simulation, 200/200; proof to be written) | Yes |
| UC / GUC / SC | seq | They contain unit propagation to a fixpoint, which is P-complete (unit resolution, A.6.1; Jones & Laaser 1976) | Only in FREE order (they pick the next item) |
| DSATUR, LF, GREEDY-EDGE, FARTHEST-INSERTION | seq by analogy (no citation found) | — | DSATUR and LF only in FREE order |
| RATIO-SKIP | seq | Superincreasing knapsack is P-complete (remark under A.8.5) | Yes |
| RATIO-PREFIX | const if sorting ∈ TC⁰ (unverified) | — | — |
| RO-FF | polylog (provisional) | By analogy with random-order greedy MIS (Blelloch, Fineman & Shun 2012) | Yes |

P-completeness is asymptotic. At our sizes, "seq" means *the dependency depth on this item*, and E3 measures it directly. Under best-effort thinking every member is executable, so the depth class matters only for the diagnostic conditions.

### 1.6 RASP-L sketch (pre-registered before any LLM data)

The length measure is the primitive count (`select`, `aggregate`, `selector_width`, `map`, `sequence_map`); attention-layer depth is reported too (DESIGN O6). Programs are per emitted step, so the loop is decoding or CoT. The latent versions have no fixed-depth program.

| Member | Outline per step | Prims | Layers |
|---|---|---|---|
| POLARITY | Select same-variable occurrences; aggregate polarity; map ≥ ½ | 3 | 2 |
| JW / MOMS | Adds a width-dependent weight map | 4–5 | 2 |
| AR-FF | (1) Fetch the current vertex from the requested order. (2) At each earlier output line, form the neighbour-set embedding of its vertex. (3) Select the earlier outputs whose neighbour set contains the current vertex, and aggregate their colour one-hots. (4) Map to mex. | 7 | 3 |
| AR-GREEDY | Aggregate the true-literal set from earlier outputs; select the open clauses containing ±v; aggregate a signed count; map to its sign | 7 | 3 |
| AR-LF (FREE) | Degree via `selector_width`; uncoloured flag; select-max; then the AR-FF step | 10 | 4 |
| AR-UC (FREE) | Count false literals per clause under the outputs; select the first unit clause | 10 | 3 |
| AR-DSATUR (FREE) | Distinct-colour count per vertex; select-max with a degree tie-break; then the AR-FF step | 14 | 4 |
| Latent FF / GREEDY (target query) | No fixed-depth program; unrolled, about 3 layers per dependency level | — | ≈ 3d |

**Pre-registered predictions.** These come from the two-part MDL objective with a depth cap (DESIGN O6; F report, suggestion 14):

- **R1** (no-think, answer written in processing order). C weight concentrates on the shortest adequate per-step programs: AR-FF for colouring; POLARITY, then AR-GREEDY, for SAT. DSATUR and UC get little weight.
- **R2** (best effort). With the depth cap relaxed, weight moves to longer per-step programs (DSATUR, UC/SC) and to the hybrids C→D (DPLL-σ) and C→F (GREEDY+REPAIR). *Modal prediction for reasoning models: a greedy first pass in listing order, then verification, then local repair.*
- **R3** (no-think, latent target query). π_seq(d) falls toward zero beyond a model-specific d\* ≲ layers/3, with weight moving to π_proxy and π_order-free.

---

## 2. Behavioural evidence (Phase 1)

### 2.1 Conditions, models, sizes

**Conditions.**

- **BE (primary).** Thinking on, at the highest effort.
  - Caps: 32,768 thinking tokens plus 2,048 answer tokens; model-card sampling.
  - A run that reaches the cap gets `</think>` plus answer forcing. It is marked *censored* and analysed separately (DESIGN §5.11).
- **ND (diagnostic).**
  - Qwen3 runs with thinking off (non-thinking mode, or Instruct-2507), with greedy decoding.
  - gpt-oss has no no-think mode. Its diagnostic is `reasoning_effort = low`, reported as **LOW**, never as ND.
  - R1-distills get no ND condition; an empty think block would be off-distribution.
- **T1k / T4k (experimental factor, E3 only).** Budget forcing: truncate the thinking at the cap and force the answer.

**Models (Phase 1, in run order).**

1. **gpt-oss-20b** (high effort). It runs first, and runs every dev batch.
2. gpt-oss-120b (high)
3. Qwen3-30B-A3B (thinking)
4. Qwen3-14B (thinking)
5. Qwen3-32B (thinking)
6. Qwen3-235B-A22B-Thinking-2507
7. DeepSeek-R1-0528
8. R1-Distill-Qwen-32B
9. R1-Distill-Llama-70B

The ND diagnostics run on Qwen3-14B, -32B, -30B-A3B and -235B-A22B (non-thinking or Instruct). The budget factor runs on the four Qwen3 models and the two gpt-oss models.

**Samples.**

| Condition | Samples per item |
|---|---|
| BE | 1 at model-card temperature, plus 2 more on a fixed 20% subset (≥ 3, per DESIGN §O4): 1.4 on average |
| E3 | 2 per version (flip measures need within-item noise) |
| ND | 1 at T = 0, plus 2 at T = 0.7 on the 20% subset |

**Sizes.** The dev batch of each model locates its budget line n\* per domain: the largest size at which the best-effort exact-solve rate is ≥ 80% (DESIGN §O2). Then:

- E1 and E2 use sizes near n\*. Fingerprints work on correct answers, but many solutions must exist.
- E4 and E5 span n\*, because errors are needed.
- The sizes below are the planned defaults for gpt-oss-20b-class models, re-centred per model after the dev batch.

### 2.2 Predicted error signature (template)

- **Omission or commission.**
  - In search: C-ABORT gives a false IMPOSSIBLE/UNSAT. C-INFEAS gives an infeasible answer whose violations sit at the member's stuck point.
  - In optimisation: feasible but suboptimal, with member-specific slack. RATIO-PREFIX leaves capacity unused at the first item that does not fit. FF's extra colours fall on late vertices.
  - In entailment: GREEDY-CM errs by *commission* only.
- **Hardness axis.** Each member has its own success-vs-density curve. The asymptotic anchors are UC ≈ 8/3 and optimal myopic 3.26 on 3-SAT, and greedy colouring ≈ 2χ colours on large random graphs (F report). We simulate the curves at our n (E4).
- **Order.**
  - C1 answers move with the order in a computable way.
  - C2 and C0 answers move only through ties.
  - C3 answers move only in distribution.

### 2.3 Manipulation signatures

| Manipulation | C0 | C1 | C2 | C3 | Nearest competitors |
|---|---|---|---|---|---|
| Order reversed / re-listed / relabelled (isomorphic) | Ties only | Answer changes, as computed per member and order | Ties only | Distribution unchanged | D with the same order: = C1 where C1 succeeds. F, E (listing), EXACT: invariant. B1-DROP-LATE: changes with the *edge* order. C4: changes with the update order. |
| Re-themed | = | = | = | = | A3 TEXTBOOK-TRANSFER: = on the textbook problem, ≠ on inverted ones |
| Rule inverted (colour the complement: non-adjacent items must differ) | Computed on the inverted instance | Computed | Computed | Computed | A3: answers the uninverted problem |
| Irrelevant tautological clause (x ∨ ¬x ∨ y) | Changes y's tally | GREEDY can change | UC/SC unchanged | — | D/F/EXACT: unchanged. A-DENSITY: tiny shift. |
| Isolated vertex added | = | = (no edges) | = | = | All unchanged: a placebo |
| Density ↑ (fixed n) | Knee | Member-specific knee | Knees: UC < GUC/SC < myopic | Knee | D: smooth, tracks solver nodes. F: late knee. E: BP-decimation fails early. |
| Thinking budget ↑ | = | Latent execution recovers depth (E3); per-step rule unchanged | = | = | D: budget b grows; may become non-monotone (Gema et al. 2025; Ghosal et al. 2025) |

### 2.4 Chain-of-thought hypotheses, trace coding, faithfulness, and how trace and answer evidence combine

#### 2.4.1 Trace codes

| Code | What it records | Extraction |
|---|---|---|
| K1 | Commitment sequence: the ordered (item, value) pairs at their first commitment, with token offsets | Parser |
| K2 | Explicit order statements ("in the given order", "highest degree first", "most constrained first", "start with unit clauses", "best value per kg first") | LLM coder |
| K3 | Score mentions: degree, saturation / "fewest options", clause length / "unit" / "forced", occurrence counts, ratio, value, weight, distance | LLM coder (+ lexicon) |
| K4 | Revisions: a committed item later receives a different value. Classified as *local repair* (change a conflicted item, then continue), *chronological backtracking* (undo a suffix of commitments in reverse order and try the next value), or *restart* | Parser (event) + LLM coder (type) |
| K5 | Dead-end declaration ("no colour left for v", "C7 can't be satisfied"), and what follows it: IMPOSSIBLE without revision, or a revision | Parser + LLM coder |
| K6 | A verification pass over all constraints after a full assignment | LLM coder |
| K7 | Look-ahead: reasoning about later items before committing ("if v gets 1, w will need…") | LLM coder |
| K8 | Arbitrary-choice statements ("pick any", "let's try v57") | LLM coder |
| K9 | Last complete state in the trace | Parser |
| K10 | Enumeration or case splits ("case 1: x = T…") | LLM coder |
| K11 | Quoted constraints that are not in the instance, or required ones that are missing (hallucinated edges or literals) | Parser (exact check against the instance) |
| Scalars | Thinking tokens; censoring; # commitments; # revisions; tokens to first commitment; share of the trace after the last revision | Runner / parser |

#### 2.4.2 Per-member trace signature (pre-registered)

| Member | K1 order | Per-step rule (replayed on the trace's own state) | K4 revisions | Dead end | Other |
|---|---|---|---|---|---|
| C0 POLARITY / JW / MOMS | Any (often label order) | Value = static majority; never refers to earlier commitments | 0 | — | Tallies over *all* clauses (K3) |
| C1 FF-σ / GREEDY-σ | Kendall τ(K1, σ) ≥ 0.8 | Value = mex of earlier-neighbour colours / sign of open-clause counts *given the trace's own earlier commitments* | 0 | ABORT: IMPOSSIBLE with no revision. INFEAS: a forced commit. | K2 cites the given order (LIST), or "in numerical order" (LABEL) |
| C1 FF-OUT (AR) | τ(K1, π_O) ≥ 0.8 | As FF | 0 | As FF | — |
| C1 LF / RATIO / VALUE / DIFF | τ with the static score order ≥ 0.8 | As FF / take-if-fits | 0 | Skip vs stop at a misfit (SKIP vs PREFIX) | K3 names the score (degree, value per kg, value minus weight…) |
| C2 DSATUR | Each next item = argmax saturation *given the trace state* (≥ 0.8 of steps) | mex | 0 | As FF | K3: "most constrained", "fewest options" |
| C2 UC / GUC / SC | The next commitment comes from a unit (UC) or shortest (GUC/SC) clause given the state | Forced literal | 0 | ABORT: UNSAT at the first falsified clause | K3: "forced", "unit" |
| C3 RO-FF / RO-GREEDY | \|τ\| < 0.2 with π_L, λ, π_O and score orders; the order varies across samples | As FF / GREEDY | 0 | As FF | K8 arbitrary-choice statements |
| C→F GREEDY+REPAIR | A complete C1 pass (τ ≥ 0.8), then K6 | — | ≥ 1 local repair, confined to conflicted vertices and their neighbours | Repairs at the stuck vertex | — |
| D DPLL-σ | τ(K1, σ) high | Propagation steps | Chronological backtracking (K4 type) | IMPOSSIBLE only after an exhaustive refutation | K10 case splits |
| F MIN-CONFLICTS / WALK | A full candidate before any repair | — | Many local repairs anywhere | Rarely declares impossible | K6 repeated |
| E LOCAL-t | No sequential commitments ("each vertex looks at its neighbours") | — | — | — | Rarely verbalised |
| A cues | Few or no per-item commitments before the answer | — | — | IMPOSSIBLE justified by global features ("dense", "many clauses") | — |
| B1 DROP / UP | Neighbourhoods quoted without the dropped (late) edges (K11 omissions) | — | — | — | — |
| B4 PHANTOM | Constraints quoted that are not in the instance (K11 additions) | — | — | False IMPOSSIBLE | — |
| C4 ONLINE-STATE | Premise-by-premise or line-by-line updates ("after line 7 we know…") | — | — | — | Errors with decisive information far back |
| NOISY-EXACT | Correct procedure | Sporadic violations of its own stated rule | — | — | — |
| PERCEPTION-NOISE | — | — | — | — | K11 misquotes that predict the violation location |

#### 2.4.3 Coding pipeline

1. **Automatic parsers (primary trace codes: K1, K4 events, K5, K9, K11, scalars).**
   - A regex grammar over the item vocabulary. Labels are unique strings such as v37 and x23.
   - Patterns: `v37 = 2`, `v37: 2`, `v37 → 2`, `colour v37 (with) 2`, `give v37 colour 2`, `x23 = T|True|1`, `set x23 to false`, plus negative contexts ("v37 can't be 2").
   - A **replay checker** re-runs every member from the trace's own committed state at each step. It reports per-step agreement with each member, i.e. *which rule the trace follows*, independent of whether earlier steps were right.
2. **LLM-assisted codes (secondary: K2, K3, K4 type, K6, K7, K8, K10).**
   - The coder is a pinned model with a versioned codebook.
   - It sees only the trace and the item vocabulary. It never sees ground truth, member predictions or the counterfactual cell (blind coding).
   - Long traces go in overlapping 4k-token windows, and the window codes are aggregated.
3. **Validation.**
   - Hand-label 200 traces, stratified by model, domain and length; two human coders.
   - Report human–human and LLM–human Cohen's κ per code, and parser precision and recall for K1 and K4 (targets: F1 ≥ 0.9; human κ ≥ 0.8).
   - Add 100 synthetic traces from fake models (§2.10) with known codes, 20% of them deliberately unfaithful (generated from a different member than the answer).
   - **Codes with LLM–human κ < 0.6 are dropped from inference** and reported descriptively only.
   - Codebook and parser versions are recorded like scorer versions (DESIGN §5.3), and every change triggers re-coding from the raw traces.

#### 2.4.4 Faithfulness tests (measured in E6)

| Test | Question | Pre-registered expectation (reported as a rate with a 95% interval; it sets r and is not a pass/fail gate) |
|---|---|---|
| F-T1 final-state consistency | Is the answer the last complete state in the trace (K9)? | ≥ 0.9 |
| F-T2 order faithfulness | Does the trace's commitment order agree with the order identified from the *answer* fingerprint (E1)? | κ ≥ 0.6 |
| F-T3 counterfactual covariation | Across isomorphic copies, does the trace order move with π_L, λ or π_O exactly when the answer does? | Agreement ≥ 0.7 |
| F-T4 stated-score faithfulness | When the trace says "highest degree", "most constrained" or "unit", is the chosen item the argmax under that score *given the trace state*? | ≥ 0.8 |
| F-T5 impossibility faithfulness | Is a declared dead end a real dead end of the trace state? Mismatches are classified as perception errors when K11 flags a misquote. | ≥ 0.9 |
| F-T6 early answering | Is the answer determined progressively, as commitments are made, rather than at f = 0? | Agreement at f = 0 no higher than the best order-free member's |

#### 2.4.5 Combining trace and answer evidence

1. **Answer evidence is primary.** Every weight π_h for model m on domain X comes first from the answer-only fit (r = 0). Trace evidence may narrow an interval, or split a tied pair, but it never creates weight that the answers do not support. The reporting rules are in §2.5.
2. **Trace evidence is a second channel.** It enters a joint likelihood in the style of Glöckner's (2009) multiple-measure maximum likelihood:
   - P(y, z | h) = P(y | h) · [r·P_h(z) + (1 − r)·P_0(z)], where z are the trace codes, P_0 is the pooled code distribution (a trace generated independently of the procedure), and r ∈ [0, 1] is the trace reliability.
   - r is estimated per model × domain from F-T1 to F-T4 *before* the identification model is fitted, and fixed. Every result is reported twice: with r = 0 (answers only) and with the estimated r. The gain from adding traces is reported as Δlog10 L and as the change in interval width for each π_h.
   - **Trace readout per theory:** T_h = Σ_i r_i·1[trace_i matches h's signature] / Σ_i r_i, with a bootstrap 95% interval. Here r_i is the reliability of the codes the signature uses, for that model. Under the mixture, E[T_h] ≈ π_h·r̄ + (1 − π_h·r̄)·b_h, where b_h is the base rate of the signature under the other theories. So T_h is converted into a trace-based estimate of π_h, (T_h − b_h)/(r̄·(1 − b_h)), and compared with the answer-based π_h.
3. **Licensed uses of the trace.**
   - Splitting members that agree on the answer: FF-σ vs DPLL-σ vs GREEDY+REPAIR-σ on FF-success items (backtracking vs repair vs neither).
   - Corroboration.
   - Process predictions (tokens).
4. **Disagreement rules (pre-registered).**

   | Case | Conclusion |
   |---|---|
   | Answer posterior favours h; trace posterior favours h′ (a different order or rule) | The item's responsibility is split per the joint likelihood. If GREEDY+REPAIR-h′ explains both channels better (Δlog10 L > 0), its weight rises. Otherwise r for that code falls in the next estimation round. Report the per-item posterior, not a label. |
   | Trace shows C1 commitments; the answer is valid, optimal and matches no C member | The weight goes to the C→D/F hybrids, not to C alone: "C as a first pass". |
   | No commitments in the trace (cue-style justification); the answer matches C1 | The answer-based responsibility stands. The trace term is uninformative (P_h(z) ≈ P_0(z)). Flag it as latent computation, plausible only at shallow dependency depth (see E3). |
   | Trace declares a dead end; the answer is a valid colouring | An F-T1 failure: the item gets r_i = 0 for every code, and is reported separately in E5. |
   | The answer is uninformative (unique solution, and correct) | Answer likelihoods are equal across members, so the item adds nothing to π. A trace alone never moves π; such items only enter T_h. |

### 2.5 Estimands, weight statements and power (pre-registered)

**Estimands.** Every eval reports the following for model m and domain X. They are fitted jointly in the shared identification engine (DESIGN §3 O3).

- **Mixture weight.** The model is P(y | x, m) = Σ_h π_h(φ(x), m)·P(y | h, x) + π_∅·q(y | x).
  - The sum runs over every member of every family in the cells. π_∅ is the "none of the above" mass.
  - π_h(φ, m) = softmax(w_h·φ + u_{h,m}), with model random effects. This is Rice-style strategy selection (family I).
  - Pre-registered features φ: size relative to n\*, density, answer-order format, framing, budget, and whether the item is a C dead end.
  - Each π_h is reported as a posterior mean with a 95% interval, both pooled and per feature cell. The interval is a credible interval from the hierarchical fit, cross-checked by a bootstrap over bases.
- **Lift.** The share of errors explained by h above its matched baseline: EA_h on h-wrong items minus EA under the matched permutation, i.e. the same member's prediction for another copy or edit of the same base.
- **Log-likelihood gain.** Δlog10 L (a log10 Bayes factor, held-out) of the mixture with h over the mixture without it, against two references: the null (RANDOM + NOISY-EXACT + PERCEPTION-NOISE), and h's nearest competitor in the set.
- **Trace share.** T_h, faithfulness-weighted (§2.4.5), with its trace-based estimate of π_h.

**Weight statements replace pass/fail.** Every result is written in one of three forms:

- "π_h = x [lo, hi]";
- "the evidence moves weight from h to h′ by Δπ = x [lo, hi]";
- "this set bounds π_h ≤ u (upper 95%)".

There are no supported/against verdicts. The pre-registered design targets below say what each set can resolve at full size. They are normal approximations for a weight separated from its nearest competitor:

- c is the rate at which the competitor's answers coincide with h's prediction;
- slip rate ε = 0.2;
- the detectable weight is π_det ≈ 2.8·√(c(1−c)/N)/(1−ε−c), at 80% power and two-sided α = .05;
- the upper bound when h is absent is ≈ 1.645·√(c(1−c)/N)/(1−ε−c).

They are checked against the simulated recovery in §2.10, whose widths are wider: as a rule of thumb, take about 1.5× these numbers.

| ID | Eval | Estimand(s) | N (informative) | c | Detects π_h ≥ (80%) | Bounds absent π_h ≤ (upper 95%) | Also reported |
|---|---|---|---|---|---|---|---|
| W1 | E1 (per domain) | π per order source (LIST, LABEL, OUT, score order, random order); matched-copy lift; Grundy excess | 500 copies | 0.05 | 0.04 | 0.02 | Δπ between the c1 natural format and decorrelated copies (format dependence, family I) |
| W2 | E2 (per contrast) | Δπ between the two rules of a double dissociation; π per rule | 120 pairs (720 items pooled) | 0.15 (placebo flips) | 0.14 per contrast (0.06 pooled) | 0.08 (0.03 pooled) | E2-KT psychometric weights β with 95% intervals |
| W3 | E3 (per depth / pooled) | π_seq(d) (FF-LIST executed), π_proxy(d) (LOCAL-t-LIST), π_order-free(d); d\* with interval; B(d) | 60 triples per depth (360 pooled) | 0.25 | 0.28 per depth (0.12 pooled) | 0.17 (0.07) | The ND vs BE contrast Δπ_seq(d), which measures the depth dependence |
| W4 | E4 | Share of failures co-located with a C member's failures, i.e. π_C restricted to errors; knee likelihood per member | 640 (SAT) + 480 (colouring) | 0.30 | 0.10 | 0.06 | Δlog10 L of each family's item-level success predictor |
| W5 | E5 | π_C-ABORT, π_C-INFEAS, π_B1-DROP, π_F, π_D among failures; state-dependence weights | 320 stuck / 160 control; 600 state items | 0.10–0.20 | 0.07–0.08 | 0.04–0.05 | Localisation interaction with its interval |
| W6 | E6 | Reliability r per model × code | 200 traces × 5 cuts | — | r to ±0.07 (95% half-width) | — | Pre-commitment share at f = 0 |
| W7 | Mixture (all evals) | Family weight π_C on items where C disagrees with D/F/EXACT, with its split into C0/C1/C2/C3/hybrids and per-feature curves | All | — | — | — | Unexplained mass π_∅ (always reported) |

### 2.6 The evals

#### E1. Order source (isomorphic re-orderings)

**Weight hypothesis H-C1.** For model m on domain X, the identity of the returned solution (correct or not) is a mixture over order sources. The estimand is the vector (π_LIST, π_LABEL, π_OUT, π_score-order, π_random-order, π_order-free), where order-free pools C0, C2 with order-free ties, F, EXACT, A, H and the nulls.

- **Prediction (R2).** Under BE, π_LIST is the largest order weight, with π_LIST ≥ 0.15.
- **Prediction (P4).** π_OUT rises in the ND and LOW conditions; Δπ_OUT(ND − BE) > 0.
- **Prediction (format dependence, family I).** Order weights in c1, the natural format, differ from those in c2–c6. This is reported as Δπ with an interval.
- **Bound.** The set detects any order weight ≥ 0.04 and bounds absent order sources at ≤ 0.02 (upper 95%) per domain (W1).

**Design.** For each base instance, six isomorphic copies with an identical edge (or clause) set and label multiset:

| Copy | Listing π_L | Labels λ | Answer order π_O | Isolates |
|---|---|---|---|---|
| c1 NAT | π_L | ascending along π_L | LIST | The standard format (all orders coincide) |
| c2 RELABEL | π_L | random | LIST | Labels (c1 → c2) |
| c3 ANS-LABEL | π_L | as c2 | LABEL | Answer order (c2 → c3) |
| c4 ANS-RAND | π_L | as c2 | RAND | Answer order |
| c5 ANS-FREE | π_L | as c2 | FREE (emitted order ε recorded) | Self-chosen order |
| c6 RELIST | π_L′ (new) | as c2 | LIST (= π_L′) | Listing (c2 → c6) |

**Cell predictions (answers).** "=" means the same answer as the copy to its left.

| Theory | c1 | c2 | c3 | c4 | c5 | c6 |
|---|---|---|---|---|---|---|
| FF-LIST / GREEDY-MENTION | FF(π_L) | = | = | = | = | FF(π_L′) |
| FF-LABEL / GREEDY-INDEX | FF(π_L) | FF(λ) | = | = | = | = |
| FF-OUT (AR) | FF(π_L) | = | FF(λ) | FF(π_R) | FF(ε) | FF(π_L′) |
| LF, DSATUR, POLARITY, UC-RAND, GUC, SC | one answer up to isomorphism (ties aside) | | | | | |
| UC-DET | free choices follow π_L, so as FF-LIST in pattern | | | | | |
| RO-FF / RO-GREEDY | same *distribution* in every copy; valid colourings Grundy | | | | | |
| DPLL-σ | = FF-σ where FF-σ is optimal; otherwise σ's first optimal solution (library: DPLL-LIST 3 colours vs FF-LIST 4 on c1–c5) | | | | | |
| GREEDY+REPAIR-σ | = FF-σ where FF-σ is optimal; otherwise FF-σ with the top class emptied | | | | | |
| MIN-CONFLICTS / WALK | same distribution; Grundy rate ≈ its own (low on selected items) | | | | | |
| LOCAL-t-ID (E) | λ-sensitive, π_L-invariant; often invalid | | | | | |
| DROP-LATE (B1) | follows π_L through the dropped edges; conflicts on them | | | | | |
| A, H, EXACT, NOISY-EXACT, PERCEPTION-NOISE | order-invariant (H: random; PERCEPTION: conflicts on misread edges) | | | | | |

**Cell predictions (trace).**

| Theory | Prediction |
|---|---|
| FF-LIST | τ(K1, π_L) ≥ 0.8 in every copy |
| FF-LABEL | τ(K1, λ) ≥ 0.8 |
| FF-OUT | τ(K1, π_O) ≥ 0.8; under FREE, τ(K1, ε) ≈ 1 |
| LF | τ with degree order |
| DSATUR | Replay agreement with saturation |
| RO-* | \|τ\| < 0.2 with every named order, plus K8 |
| DPLL-σ | Chronological backtracking, only on copies where FF-σ is suboptimal |
| GREEDY+REPAIR | A τ-ordered first pass, then local moves confined to the top colour class |
| MIN-CONFLICTS | Full candidate, then scattered repairs |

**Metrics.**

- **M1 matched-copy lift.** For each order member h_σ: exact-partition (or assignment) agreement with h_σ's prediction *for this copy*, minus agreement with h_σ's prediction for another copy of the same base. Same graph, same member, wrong order: a permutation baseline matched on structure. A distance-kernel version uses the likelihood.
- **M2 order-invariance index.** The mean partition distance between answers on isomorphic copies (mapped through the isomorphism), against the within-copy sampling distance from repeat samples.
- **M3 Grundy excess (colouring).** P(valid answer is Grundy up to relabelling) minus the base rate among optimal colourings of the item (enumerated), compared with each member's Grundy rate (L1).
- **M4 AR self-consistency (c5).** P(answer = FF(ε)), and τ(ε, each member's order).
- **M5 C1-vs-D split.** On copies where FF-σ is suboptimal: does the answer follow FF-σ or σ's optimal first solution?

**Confound control.**

- **Token length.** Identical across copies (same label multiset and edges); asserted per tokenizer.
- **Naming.** Two-digit labels with a fixed prefix, with equal token counts asserted per tokenizer. Numeric labels make λ a salient order, which is intended; a names variant (20%) tests alphabetical order.
- **Position vs order.** c2–c5 hold every absolute position fixed and vary only the *requested* order. c2 vs c6 moves everything. A pure position cue (e.g. "the first-listed vertex gets colour 1") is invariant to colour names under the partition readout, so it contributes nothing.
- **Answer length.** Identical across copies.
- **Neighbour-list order.** Fixed to π_L; a robustness subset uses λ.

**Weight statements reported.**

- π for each order source, with its 95% interval, and the matched-copy lift for each.
- Δlog10 L of the order-source mixture over the order-free-only mixture (null) and over the best single order (nearest competitor).
- The Grundy excess as a weight on the first-fit family in *any* order: π_FF-any = (Grundy rate − base rate)/(1 − base rate), with its interval.

If every order weight's upper bound is ≤ 0.05, the result is stated as such: "order sources carry ≤ 0.05; the weight sits with order-free members, split by E2/E4/E5".

**Power, as weights.**

- **Analytic (W1).** With 500 copies per domain and a coincidence rate c ≈ 0.05, an order weight of 0.04 is detected (80% power), and an absent one is bounded at ≤ 0.02.
- **Simulated (§2.10, n = 10 dev graphs, 480 items).** A planted 60/30/10 mixture of FF-LIST, DSATUR and DPLL-LIST is recovered at 0.62/0.28/0.09. The 95% interval widths are 0.12/0.09/0.10, so expect weights resolved to about ±0.05 at full size.
- **Grundy excess.** An excess of 0.15 over a base rate of 0.3 needs about 75 valid answers.
- **Pairwise contrasts.** Lifts are also reported as paired contrasts per member (McNemar), for readers who want them; the weights are primary.

**Threats.**

- Thinking models may find a canonical or "structural" solution that is in no member: it shows up as unexplained mass; trace codes help.
- FREE output is often written in listing order anyway (then c5 ≈ c2).
- Under BE, order dependence may reflect D's branching order. M5 and E5 handle this.
- Hallucinated edges: K11, plus an edge-echo control on 10% of items.
- Solution-aesthetic preferences (balanced classes) are not in the zoo; they are reported as unexplained mass.

#### E2. Rule discrimination (edit-search minimal pairs and tie psychophysics)

**Weight hypothesis H-C2.** Within the order class from E1 (default π_L), weight is split among the decision rules of each contrast.

- **Estimand per contrast.** Δπ(h1 − h2) = DDI/(1 − ε), with its interval, plus each rule's π from the joint mixture over all E2 items.
- **Prediction (R1/R2).** In ND, π_FF ≥ π_DSATUR and π_POLARITY ≥ π_UC. Under BE, weight moves toward DSATUR/UC/SC and toward D: Δπ(BE − ND) > 0 for the adaptive rules.
- **Bound.** The set bounds an absent rule at ≤ 0.08 per contrast (0.03 pooled; W2). It detects a weight difference of 0.14 per contrast.

**Design.** For a base x, enumerate single edits:

| Domain | Edits |
|---|---|
| Colouring | Add or delete one edge |
| SAT | Flip a literal's sign; replace a literal's variable; add or delete a clause; insert a tautological clause; swap two clauses (order only) |
| Knapsack | One value or weight ±1..6, staying two-digit |
| TSP | Move one city by 1–3 grid units |

For each x′, compute the change signature over *all* members and the ground truth, then fill the cells:

| Cell | Definition |
|---|---|
| D(h1 \| h2) | h1 changes, h2 does not, g does not |
| D(h2 \| h1) | The reverse |
| PLACEBO | Nothing changes |
| G-ONLY | g changes, the focal members do not |

Within a double dissociation, edits are balanced so that the *competitor families'* predicted flip rates are equal in the two directions. DDI then cancels them.

**Focal contrasts:**

| Domain | Contrasts |
|---|---|
| Colouring | FF-σ\* vs DSATUR; FF-σ\* vs LF; DSATUR vs LF; DSATUR tie key (π_L vs λ) |
| SAT | GREEDY vs UC-DET; GREEDY vs POLARITY; UC vs GUC/SC (distributional members: "change" = TV distance > 0.5); POLARITY vs JW/MOMS on mixed 2+3-SAT |
| Knapsack | RATIO vs DIFF; RATIO vs VALUE; PREFIX vs SKIP |
| TSP | NN-FIRST vs GREEDY-EDGE; NN-FIRST vs FI; GREEDY-EDGE vs FI |

L2 makes FF-invariant edges easy to construct.

**Knapsack tie psychophysics (E2-KT).**

- n = 25 items, built so that every sort-based member agrees on a dominant prefix and the decision reduces to two critical items A and B (both fit; not both).
- A filler item fits only with B, so the optimum is decorrelated from the gaps.
- Grid: Δlog-ratio ∈ {−.25, −.08, 0, .08, .25} × Δ(v−w) ∈ {−15, −5, 0, 5, 15}, with 8 items per cell, and the listing position of A counterbalanced.
- Fit P(A) = Φ(β_r·Δlogr + β_d·Δd + β_v·Δv + β_w·Δw + β_pos·[A first] + β_opt·[opt = A]).
- Predicted dominant coefficient: RATIO → β_r (step at Δr = 0); DIFF → β_d; VALUE → β_v; LARGEST-FIT → β_w > 0; INPUT-FIT/PRIMACY → β_pos; DP-EXACT → β_opt.

**Cell predictions.**

| Theory | D(h1 \| h2) | D(h2 \| h1) | PLACEBO | G-ONLY | Trace |
|---|---|---|---|---|---|
| h1 (e.g. FF-LIST) | flips (to h1(x′)) | stays | stays | stays | Replay agreement with h1 ≥ 0.8 of steps; the step where h1's choice changes is visible |
| h2 (e.g. DSATUR) | stays | flips | stays | stays | Replay agreement with h2 |
| D / EXACT | stays (balanced) | stays | stays | flips | Search with revisions |
| F | small TV change | small TV change | — | larger | Guess, then fix |
| A cue | equal small shift (placebo matched on cue change) | | | | — |
| NOISY-EXACT, PERCEPTION, RANDOM | equal flip rates in every cell, including PLACEBO | | | | — |

**Metrics.**

- M1 flip contrast: P(change | cell) − P(change | PLACEBO).
- DDI(h1, h2) = flip(D(h1 | h2)) − flip(D(h2 | h1)).
- M2 directional agreement: does the new answer move toward h1(x′)?
- M3 psychometric coefficients and the point of subjective equality (E2-KT).
- M4 mixture weights over all E2 items.

**Confound control.**

- An edit adds or removes two label tokens (colouring) or changes one number (knapsack). Every cell has the same edit-type mix.
- Edit location (line index) is matched between each cell and PLACEBO.
- Numbers stay two-digit. Tokenizer family is a covariate: Qwen splits digits, while gpt-oss and Llama-3 use multi-digit tokens.
- Ratio items avoid "round" ratios (exact halves or doubles).

**Power, as weights.**

- With a placebo flip rate of 0.15 and 120 pairs per contrast, Δπ ≥ 0.14 is detected and an absent rule is bounded at ≤ 0.08. Pooling the 720 items in the joint mixture gives 0.06 and 0.03. A GLMM with base random effects gains a little.
- E2-KT: 200 trials give SE(β) ≈ 0.15 on standardised predictors. The cue weights are reported as normalised |β| shares with intervals: RATIO vs DIFF vs VALUE vs position vs optimum.

**Threats.**

- One edit can change many members; selection plus covariates handle it.
- BE models may solve n = 16–20 exactly, in which case only G-ONLY flips. Sizes are re-centred per model so that exact-solve rate ≤ 50%.
- An edit may trigger a perception error on the new edge (K11).
- "Change" for distributional members needs TV thresholds, which are pre-registered.

#### E3. Depth-stress gadgets (const vs seq)

**Hypotheses.**

The estimand is the split of the order-sensitive weight as a function of depth: π_seq(d) (FF-LIST executed), π_proxy,t(d) (LOCAL-t-LIST, for each horizon t), π_noisy(d) (NOISY-FF-ε) and π_order-free(d). Each is reported per condition, with intervals, and E[A2(d)] = π_seq(d)·(1−ε)² + π_proxy(d)·[d ≤ t] + ¼·π_random.

- **H-C3a (seq execution, BE).** π_seq(d) is flat in d: its slope over d has a 95% interval that includes 0, and π_seq ≥ 0.5 wherever π_seq(1) ≥ 0.5.
- **H-C3b (const limitation, diagnostic).** In ND with a single-value or reversed-order answer, π_seq(d) drops beyond a model-specific d\*, reported with an interval. Δπ_seq(ND − BE) grows with d. Weight returns to π_seq when the answer is written in listing order, or when the budget is at least about c·|cone(d)| tokens; B(d) is reported with an interval.
- **H-C3c (shallow cue, the alternative).** π_proxy carries the order-sensitive weight under BE as well: π_seq(d) decays with d in *both* conditions, at the same rate.
- **Bound (W3).** The pooled set detects π_seq ≥ 0.12 and bounds absent components at ≤ 0.07. Per depth, the figures are 0.28 and 0.17.

**Gadget** (colouring, primary). Our construction follows the standard LFMIS reduction idea.

- **Circuits.** Two layered NOR circuits, A (holds the targets) and B (holds the placebo inputs). Width 3, depth D_max = 8. Edges run A→B only.
- **Inputs.** Each primary input x has a pendant p_x. The pair is listed as adjacent lines (x, p_x) or (p_x, x): x first makes x colour 1 under FF, i.e. "True".
- **Order.** Gates are listed in topological layer order, A and B interleaved.
- **Triangles.** Three pendant triangles on random gates, listed after all gates, make χ = 3.
- **Target.** A sink gate of A at layer d, listed last.
- **Size.** n = 68 and m = 114 for *every* item. The circuit is fixed; only the target's layer varies, so length, density and degree histogram are identical across depths.

**Lemma (gadget).** Under FF-LIST, a vertex has colour 1 iff its NOR-circuit value is True. By induction over π_L:

- input x has colour 1 iff it is listed before its pendant;
- gate g = NOR(a, b) has exactly a and b as earlier neighbours, so it has colour 1 iff neither of them does.

Simulation check (scratch): 100% agreement on 1,500 gadgets; FF uses exactly 3 = χ colours; DSATUR with an order-free tie key gives identical output across versions in 100% of cases.

**Minimal triple.**

| Version | Change | Effect under FF-LIST |
|---|---|---|
| x | Base | — |
| x_crit | Swap one sensitive A-input/pendant pair | The target flips |
| x_plac | Swap one B-input pair, outside the target's cone | The target cannot flip |

All three are the *same labelled graph*: identical edges and labels, and two adjacent lines exchanged. So g, χ and every order-invariant member are identical by construction.

- Graph distance from the swap to the target: d (critical) vs a median of d + 2 (placebo).
- Depths: d ∈ {1, 2, 3, 4, 6, 8}.
- Raw NOR circuits alternate with the parity of depth (P(True) is 0.34 at odd d and 0.64 at even d in simulation). Items are therefore selected so that P(FF-target = colour 1) = 0.5 per depth, and so that every audited shallow proxy has accuracy 0.5 ± 0.05 per depth. The proxies are LOCAL-t-LIST for t < d with both defaults, the target's degree, its position, and the parity of its number of earlier neighbours.

**Arms.**

| Arm | Prompt | Readout |
|---|---|---|
| E3-COL-U (uninstructed) | "Colour with at most 3 colours", answer in LIST order. REV order in the diagnostic conditions only. | The bit "the target shares a colour with the first-listed vertex", which is never swapped and is always colour 1 under FF. Invariant to colour names. |
| E3-COL-I (instructed capacity curve) | "Go through the vertices in the listed order; give each the smallest number not used by an earlier-listed neighbour. What colour does t get?" | A single number |
| E3-SAT-I (gated: run only if E1-SAT shows GREEDY-INDEX/MENTION weight) | The same circuits encoded as CNF for GREEDY-INDEX. Each input is a symmetric pair gadget, (x ∨ y ∨ d)×2, (x ∨ d d′), (y ∨ d d′), (¬x ∨ ¬y ∨ d)×2: whichever of x, y has the lower index becomes True. Each gate g = NOR(a, b) gets (a ∨ g ∨ d)×2 and (b ∨ g ∨ d)×2, compensation (¬a ∨ d d′)×2 per fan-out, and a bias (¬g ∨ d d′)×3. Dummies take the highest indices. The swap exchanges the indices of one input pair. About 30 variables and 216 clauses at width 3, depth 6 (verified: 200/200 circuits reproduced). | — |
| E3-NN (secondary) | n = 14 integer-coordinate cities. One city near the start moves by ≤ 2 units, so the NN-FIRST tour diverges at step 2 and its k-th city changes, while the optimal tour, NN-BEST, GREEDY-EDGE and FI are unchanged. Margin: at every NN step the nearest city is ≥ 15% closer than the runner-up (robust to distance-estimation noise). Instructed ("which city is k-th?") and uninstructed ("tour from A") arms; k ∈ {2, 4, 6, 8, 12}. AlgoTrace measured %NN paths, not this depth curve. | — |

**Cell predictions** (A2 = pair-consistent agreement with FF on both x and x_crit; the chance value is 0.25 for a random bit, and 0 for an order-invariant responder).

| Theory | BE, U-LIST | ND, U-LIST | ND, U-REV | ND, I | T1k/T4k, I | Placebo (all) |
|---|---|---|---|---|---|---|
| FF-LIST executed (C1, seq) | ≈ 1 | ≈ 1 (the answer stream carries the computation) | ≈ 1 for d ≤ d\*, then 0 | ≈ 1 for d ≤ d\*, then 0 | Recovers once the budget ≥ the tokens needed to reach t | No flips |
| FF-OUT (AR) | ≈ 1 | ≈ 1 | 0 (follows FF-REV) | — | — | No flips |
| LOCAL-t-LIST (const proxy) | 1 for d within its horizon, then 0 | same | same | same | No recovery | No flips |
| NOISY-FF-ε | ≈ (1−ε)^\|cone(d)\|: a smooth decay, *identical across conditions* | | | | | No flips |
| DSATUR, LF, C0, RO-FF, EXACT, F (random init), LOCAL-t (labels) | 0 | 0 | 0 | — | — | No flips |
| DPLL-LIST, GREEDY+REPAIR | = FF-LIST (FF never dead-ends on gadgets), so not separable here | | | | | |
| RANDOM, PERCEPTION-NOISE | 0.25; flips equally on critical and placebo | | | | | |

**Trace predictions.**

| Theory | Prediction |
|---|---|
| FF-LIST | τ(K1, π_L) ≈ 1 over all 68 vertices. Tokens to reach t ≈ the whole listing, so flat in d. |
| Goal-directed cone evaluation (a D-like backward chaining) | Commits only the target's ancestors, backwards. Tokens grow with \|cone(d)\|. This separates it from FF-LIST on process, though not on answers. |
| Shallow proxy | Talks about t's neighbourhood only (≤ d\* hops); no full pass. |
| DSATUR | Saturation order; t is coloured mid-sequence. |

**Metrics.**

- A2(d).
- Placebo consistency P(bit(x) = bit(x_plac)).
- Flip contrast Δ(d) = P(flip | crit) − P(flip | plac).
- d\* = the largest d with Δ(d) ≥ ½·Δ(1), from a logistic fit in d.
- B(d) = tokens to recover.

**Weight statements reported.** For each condition:

- π_seq(d), π_proxy(d) and π_order-free(d), each with an interval;
- d\* with an interval;
- the slope of π_seq in d;
- Δlog10 L of the seq-plus-proxy mixture over the proxy-only mixture (nearest competitor) and over the order-free null.

**Leak diagnostic.** If π_seq(8) under ND-I has a lower bound ≥ 0.5, a gadget leak is suspected. The proxy audit is then re-run, and those items carry no weight until it passes.

**Power.** 60 triples per depth per arm, 2 samples per version.

- Detecting a drop of A2 from 0.8 to 0.5 needs about 36 per depth.
- A logistic fit over 6 depths (360 triples) gives SE(d\*) ≈ 0.5 levels.
- A flip contrast of 0.2 at a given depth needs about 60.

**Threats.**

- The gadget structure is unnatural; the random labels, interleaved circuits and triangles mask it.
- BE models may 3-colour by an order-free global method. That is a legitimate non-C1 result, but it makes E3-U uninformative about depth; E3-I still gives the capacity curve.
- At d = 1, ND-I needs a 1-hop lookup on a 1.5k-token prompt. If A2(1) < 0.7 under ND, the format is too hard: shorten it in the dev batch.
- The critical and placebo pairs sit at matched list positions, counterbalanced.
- Noisy execution vs const limitation: separated by condition dependence. The per-step slip rate is estimated from instructed d = 1 items.

#### E4. Threshold knees and item-level co-failure

**Weight hypothesis H-C4.** At fixed density and fixed order-free solver hardness, the model's per-item failures are a mixture of the members' item-level failure patterns.

- **Estimand.** π_h restricted to failures, for each member and family (C members, D via solver nodes, F via WALK success, E via BP success, noise via length). It comes from a GLMM over item-level success, with each family's predictor entered. The reported quantities are each family's Δlog10 L and its share of explained deviance, with intervals.
- **Prediction.** The C share is ≥ 0.15 and exceeds D's under ND, and the C share falls under BE. As a curve-shape check, each member's simulated success-vs-α curve gets its own likelihood weight (with a fitted slip rate).
- **Bound (W4).** The set detects a C share ≥ 0.10 and bounds an absent family at ≤ 0.06.

**Design.**

- **3-SAT:** n ∈ {25, 40}; α ∈ {2.0, 2.5, 2.8, 3.1, 3.4, 3.7, 4.0, 4.26}; satisfiable items only (filtered uniform random); 40 per cell, so 640.
- **3-colouring:** filtered uniform random 3-colourable graphs (not planted, to avoid planting cues); n ∈ {30, 50}; average degree c ∈ {3.0, 3.5, 4.0, 4.3, 4.6, 4.9}; 40 per cell, so 480.
- **Task:** find an assignment or colouring, or say impossible.
- Members' item-level success is computed: deterministic for some, a probability for the randomised ones.

**Cell predictions.**

| Theory | Knee (simulated at our n) | What predicts the model's per-item success at fixed α | Trace |
|---|---|---|---|
| UC / GUC / SC / GREEDY / POLARITY | Early (UC < GUC/SC < myopic; anchors 8/3 and 3.26) | The member's own success, s_h(i) | Contradiction at the member's step; ABORT → UNSAT, INFEAS → continue |
| FF-k / DSATUR (colouring) | Earlier for FF than for DSATUR | s_h(i) | Stuck vertex |
| D (DPLL-b) | Smooth; grows with solver nodes | log nodes (matched away within cells) | Backtracking |
| F (WALK-k) | Late | WALK success probability | Flips |
| A DENSITY | Step at a density threshold | α only, so constant within a cell | Cites the ratio |
| NOISY-EXACT | Smooth in length | Length × ε | Slips |
| EXACT | None below n\* | None (solves everything) | Search |

**Metrics.**

- GLMM: logit P(success_i) = f(α) + γ_h·s_h(i) + δ·log length + η·log nodes(order-free) + (1 | base), fitted per member.
- Held-out log-likelihood comparison.
- Knee location with a bootstrap CI.

**Power, as weights.** An odds ratio of 2 with balanced s_h corresponds to a co-failure share of about 0.15. Detecting it needs about 134 items. The 640 SAT items give a detectable share of about 0.10 and an upper bound of about 0.06 for an absent family, overall. Per size the figures are about 0.14 and 0.08.

**Threats.**

- Members' success is collinear across items (UC and GUC fail on similar items), so report at family level unless the members are dissociated.
- Truncation at 32k on hard cells is analysed as censored.
- Satisfiable-only filtering changes the distribution near threshold (stated).
- "UNSAT" answers on satisfiable items go to E5.

#### E5. Dead ends, false "impossible", violation localisation, controlled states

**Weight hypothesis H-C5.** m's failures are a mixture of failure forms. Each component's weight among failures is reported with an interval: π_C-ABORT, π_C-INFEAS, π_B1-DROP, π_F, π_D (budget exhaustion), π_noise. The components' signatures:

- (a) false IMPOSSIBLE on items where the member dead-ends, at matched density and order-free hardness;
- (b) infeasible answers whose violated constraint is at the member's stuck vertex, moving with the vertex order and not with the edge order;
- (c) on controlled partial states, completions split by state dependence: C0 state-blind, C1 counting the open clauses, C2 following unit clauses, D searching. Each split is reported as π with an interval.

Prediction: the C components carry ≥ 0.15 of failures under ND, and less under BE, where π_D and π_C→F (GREEDY+REPAIR) grow. The set detects a component at ≥ 0.07–0.08 and bounds an absent one at ≤ 0.04–0.05 (W5).

**E5-COL design (2×2 plus control).**

- Filtered uniform random 3-colourable graphs, n = 24, average degree about 4.2.
- FF-3-LIST gets stuck at a vertex v\* in the middle third of π_L.
- Format: a vertex list (π_L) and a separate edge list (π_E).
- Factorial: vertex order {A, B} (B moves the stuck vertex) × edge order {A, B} (B reverses the edge list).
- Controls: FF-3-LIST succeeds; matched on n, m (±1) and **order-free hardness** (degree-order backtracking nodes).
- Listing-order DPLL nodes cannot be used for matching: FF success mechanically implies zero backtracking. We hit this while building the example library.

**Cell predictions (answers, and trace).**

| Theory | STUCK vA/eA | STUCK vB/eA | STUCK vA/eB | CONTROL | Trace |
|---|---|---|---|---|---|
| FF-3-LIST-ABORT | IMPOSSIBLE | IMPOSSIBLE (at v\*\*) | IMPOSSIBLE | valid | Reaches v\*, "no colour left", stops with no revision |
| FF-3-LIST-INFEAS | Conflict at v\* | Conflict at v\*\* | Conflict at v\* | valid | Forced colour at v\* |
| FF-3-EDGE-MENTION | (computed) | unchanged | changes with π_E | (computed) | Processes vertices in edge-mention order |
| GREEDY+REPAIR | valid; few vertices changed, near v\* | near v\*\* | near v\* | valid = FF | Pass, conflict, local recolouring |
| DPLL-LIST (D) | valid | valid | valid | valid | Chronological backtracking from v\* |
| DROP-LAST-EDGES (B1) | Conflict on late edges | same | Conflict moves with π_E | Conflict possible | Quotes omit the late edges |
| PHANTOM-ADJACENT (B4) | Possibly IMPOSSIBLE | changes with π_L | — | IMPOSSIBLE possible | Quotes extra edges |
| C4 ONLINE-STATE(k) | Conflicts with earlier neighbours listed more than k lines back | | | | "Recent" reasoning only |
| MIN-CONFLICTS (F) | Valid or near-miss; unlocalised | same | same | same | Guess, then fix |
| DENSITY (A) | identical on all four | | | | Cites density |
| EXACT | valid on all four | | | | Search |
| NOISY / PERCEPTION / RANDOM | Location uniform / on misread edges / about m/3 conflicts | | | | K11 for PERCEPTION |

**E5-SAT.** From the E4 pool, satisfiable items on which UC-DET and GREEDY dead-end, against matched non-dead-end items (same α and n, order-free DPLL nodes ±20%). Each dead-end item also gets one clause-order permuted copy (100 new items) to check that the falsified clause or false UNSAT moves as predicted.

**E5-STATE** (controlled partial states; works with thinking). The prompt fixes some values: "these values are already fixed". Colouring n = 16 with the first 6 listed vertices coloured; SAT n = 20 with 6 variables set. The states are found by search:

| State | Colouring | SAT |
|---|---|---|
| s1 | FF continuation dead-ends, but a completion exists | GREEDY's completion is valid while POLARITY's (state-blind) falsifies a clause |
| s2 | — | Unit propagation from the state forces a value against GREEDY's count, so UC is valid while GREEDY falsifies a clause |
| s3 | No completion exists | No completion exists |

100 bases × 3 states × 2 domains = 600 items. E5-P is the diagnostic twin: the same states with the answer prefix prefilled, and a single next decision read out (no-think only).

**E5-ENT.**

- Items where C does not follow, but GREEDY-CM in premise order fails to find the countermodel (so it predicts "follows"), with premise order reversed in a twin item (GREEDY-CM then finds it).
- Matched items where GREEDY-CM succeeds in both orders.
- 120 bases × 2 orders.
- ETR/C4 predictions for the same items come from PyETR (B4/C4 verticals) and must differ from GREEDY-CM's on at least half the pairs.

**Metrics.**

- False-IMPOSSIBLE difference (GLMM).
- Conflict location: P(conflict involves v\*) and P(conflict on the last-listed edges), with the 2×2 interaction contrasts.
- FF prefix agreement before v\*.
- State-dependence contrasts in E5-STATE.

**Power, as weights.**

- False IMPOSSIBLE: a C-ABORT weight of 0.2 among failures (0.1 vs 0.3 false-IMPOSSIBLE rates) needs about 59 per group; there are 160 stuck vs 160 controls. The detectable weight is about 0.07, and an absent component is bounded at about 0.04.
- Localisation: among about 130 infeasible answers, π_C-INFEAS is estimated from P(conflict at v\*) against a base rate of deg(v\*)/m ≈ 0.15. Its interval half-width is about ±0.08.

**Threats.**

- BE models rarely give infeasible answers on n = 24 (sizes re-centred).
- IMPOSSIBLE can also come from a DPLL budget exhaustion: matching on order-free hardness, plus backtracking codes.
- Partial states are an unusual framing; a no-state control is included.

#### E6. Trace faithfulness and commitment timing

**Hypotheses.**

- **Reliability.** r per model × code, with an interval (W6), estimated from F-T1 to F-T5 on all BE traces from E1–E5; no new generation is needed. The §2.4.4 expectations are reported as rates with intervals, not as gates. They set how much weight the trace channel receives: r enters the joint likelihood and the T_h weights.
- **Pre-commitment share (F-T6).** The share of items whose forced answer at f = 0 already equals the final answer, minus the share expected from the best order-free member. Reported with an interval. It enters as a down-weight on r for the order codes.

**E6-EA.** For each open model, 200 BE traces stratified across E1–E5, truncated at f ∈ {0, .1, .25, .5, .75} with the answer forced: 1,000 prompts.

**Predictions.**

| Theory | At fraction f |
|---|---|
| Faithful C1 trace | Forced answers keep every committed item's trace value. Uncommitted items follow the member's continuation from the trace state. Agreement rises in steps. |
| Post-hoc trace | A high pre-commitment share: agreement at f = 0 near 1 − ε, i.e. the answer was fixed before the trace (cf. Cox et al. 2026). |
| Latent exact solver with a narrated trace | Valid forced answers at every f that differ from FF. |

**Output.** r per model × domain × code, with intervals (§2.4.5), fixed before identification. Each trace-based weight T_h is reported next to the answer-based π_h, together with their difference.

**Threats.**

- Forced answering is off-distribution.
- Parser misses: hand-labelled audit.
- LLM-coder bias: blind coding plus κ.

### 2.7 Eval summary (template table)

The template's *Supported if* / *Against if* columns are replaced by weight statements: what the set can detect, and what it can bound (§2.5).

| ID | Item generator | Answer format | Metric (all with 95% intervals) | Detects (80% power) | Bounds an absent component at (upper 95%) |
|----|----------------|---------------|--------|--------------|------------|
| E1 | Isomorphic copies c1–c6 of graphs (n = 16) with many optimal partitions; 3-SAT (n = 20, α 3.0–3.5) with many solutions; knapsack n = 20; TSP n = 12 | Full colouring / assignment / subset / tour in the requested order | π per order source; matched-copy lift; Δlog10 L vs order-free and vs the best single order; Grundy-based π_FF-any; Δπ by format | π ≥ 0.04 | ≤ 0.02 |
| E2 | Edit-search double dissociations; knapsack psychophysics (n = 25) | As E1 | Δπ(h1 − h2) per contrast; π per rule; normalised cue weights β | Δπ ≥ 0.14 per contrast (0.06 pooled) | ≤ 0.08 (0.03 pooled) |
| E3 | NOR-circuit gadgets (n = 68), order-only triples, d ∈ {1..8}; CNF gadget (gated); NN margin pairs | Full 3-colouring (LIST / REV) or single value | π_seq(d), π_proxy(d), π_order-free(d); d\*; B(d); Δπ_seq(ND − BE) | π_seq ≥ 0.12 pooled (0.28 per depth) | ≤ 0.07 (0.17) |
| E4 | Filtered random 3-SAT / 3-colouring sweeps | Assignment / colouring / impossible | Share of failures per family; Δlog10 L of item-level predictors; knee likelihood | Share ≥ 0.10 | ≤ 0.06 |
| E5 | Stuck vs control (matched on order-free hardness), 2×2 orders; partial states; GREEDY-CM entailment | As E4; YES/NO | Failure-form weights (C-ABORT, C-INFEAS, B1, F, D, noise); state-dependence weights | ≥ 0.07–0.08 | ≤ 0.04–0.05 |
| E6 | Truncated BE traces | Forced answer | r per model × code; pre-commitment share; T_h vs π_h | r to ±0.07 | — |

### 2.8 Generator specifications

Common rules:

**Content addressing.** Every base instance has a hash of its canonical form; every variant stores its base's hash (DESIGN §5.1).

- Graphs: canonical labelling (nauty or pynauty), or a Weisfeiler–Lehman hash with an exact isomorphism check on collisions.
- CNF: canonical form under variable renaming, polarity flips and clause permutation; same check.

**Dev/test split.**

- Assigned by the *base* hash, so every copy, edit and order variant of a base lands in the same split.
- Dev bases are drawn from a disjoint seed range (seeds < 10⁶ for dev, ≥ 10⁶ for test).
- A CI assertion checks that no two bases across splits are isomorphic.
- Dev items are never reused in test.

**Surface matching** (asserted per variant).

- The label multiset is identical across variants.
- Token counts are equal per tokenizer (gpt-oss o200k, Qwen3, DeepSeek, Llama-3); edits are matched in token delta across cells.
- Edited and swapped lines occupy matched list positions in critical vs placebo variants.
- Answer lengths are equal.
- Numbers are two-digit.

**Verification.** Each generator recomputes every member's prediction on every variant and asserts the cell definition. The yields below come from the scratch builds and simulations.

| Eval | Template and parameters (sampling) | Constraints / rejection | Variant derivation | Expected yield |
|---|---|---|---|---|
| E1-COL | G(n, p): n = 16 (dev examples: 10), p tuned so that mean degree is 4.0–4.8; labels 10–99 | χ ∈ {3, 4}; ≥ 50 optimal partitions (≥ 12 at n = 10); Grundy fraction among optimal ≤ 0.4; the FF partitions for π_L, λ, π_R and π_L′ pairwise distinct; LF and DSATUR distinct from all of them; ≥ 1 order with FF using χ + 1 (the C1-vs-D split) | c1–c6 per §2.6 E1 | n = 10: 1 accepted per ~100 candidate graphs with the Grundy filter (1 per 6 without it); n = 16: estimate 1 in 100–300 (partition enumeration dominates cost; seconds per candidate) |
| E1-SAT | Uniform 3-SAT, n = 20 (dev: 8), α ∈ {3.0, 3.5} | Satisfiable; ≥ 20 solutions (dev: ≥ 6); GREEDY-MENTION, GREEDY-INDEX and GREEDY on the re-listed copy all satisfying and pairwise Hamming ≥ 4; POLARITY distinct; UC-DET distinct from GREEDY on ≥ 1 copy | c1, c2, c6 (c3–c5 as for colouring) | Dev: 1 in 9 |
| E1-KNAP / E1-TSP | Knapsack n = 20, v, w ∈ U[10, 99], W = 0.45·Σw. TSP n = 12, coordinates on a 100×100 grid, integer distances | INPUT-FIT ≠ the sorted members; ties planted in half the bases; NN-FIRST ≠ NN-LABEL0 ≠ NN-BEST | Listing, label and answer-order copies | Estimate ≥ 1 in 3 |
| E2-COL | As E1-COL | All four cells {D(FF\|DS), D(DS\|FF), PLACEBO, G-ONLY} reachable by a single edge addition; competitor flip rates balanced across directions | Enumerate all non-edges; select by change signature (L2 generates D(DS\|FF) candidates directly) | Dev (n = 10): 1 in 182 bases has all four cells; n = 16: higher (more edits). Cells can also be filled from different bases. |
| E2-SAT | Uniform 3-SAT n = 20, α ∈ {3.0, 3.5, 4.0}; mixed 2+3-SAT (p = 0.5) for POLARITY vs JW/MOMS | As above, per contrast | Literal flip / replace, clause add / delete, tautology insertion | Estimate 1 in 20–50 bases per complete set |
| E2-KNAP | n = 10 (dev) / 25; ±1..6 edits | All four cells; values stay 10–99 | Enumerate 2·n·12 edits | Dev: 1 in 49 bases |
| E2-KT | n = 25: dominant prefix (high v, low w), critical A, B, filler F, dominated items with w > residual capacity | Every sort-based member agrees on the prefix; the decision reduces to A vs B; the optimum is balanced and orthogonal to Δr and Δd | Solve for (v, w) per grid cell by integer rejection sampling | Estimate ≥ 1 in 5 per cell |
| E3-COL | Two-circuit NOR gadget: width 3, D_max = 8, A→B cross edges (p = 0.5), 3 triangles; target a sink at layer d | The target is sensitive to ≥ 1 A-input; a B-input is outside the cone; P(target True) balanced per depth; shallow-proxy audit 0.5 ± 0.05; FF uses exactly 3 colours | Swap an adjacent pair (critical / placebo); reference vertex = a never-swapped pair listed first | 80% pass sensitivity and placebo (simulation); about 55% after parity balancing |
| E3-SAT | The same circuits, CNF gadget (§2.6) | 200/200 verified | Index swap within an input pair | ≈ 100% |
| E3-NN | n = 14 cities | NN margin ≥ 15% at every step; perturbation leaves the optimum (Held–Karp), NN-BEST, GREEDY-EDGE and FI unchanged | Move one city near the start by ≤ 2 units | Estimate 1 in 20 |
| E4 | Uniform 3-SAT / 3-colourable graphs (rejection-filtered) | Satisfiable / colourable; within each (n, α) cell, balanced on UC (or FF) success and matched on order-free nodes | — | Dev (n = 12, α = 3.5): a matched pair in 4 tries |
| E5-COL | G(24, p), 3-colourable, not 2-colourable | FF-3-LIST stuck in the middle third; vertex order B moves the stuck vertex; control matched on n, m ±1 and degree-order backtracking nodes | Vertex re-listing; edge-list reversal | Dev (n = 12): 36 tries for stuck + control. About 70% of random 3-colourable graphs get stuck under a random order. |
| E5-STATE | SAT n = 20 (dev 10), α = 3.5; colouring n = 16 | States s1–s3 per §2.6 E5, with completion existence checked by enumeration | The same formula with a different fixed state | Dev: found in 1 try |
| E5-ENT | 5 atoms, 4 premises (if / or / not-both), literal conclusion | Not valid; GREEDY-CM fails in order A and succeeds in order B; ETR prediction computed | Premise reversal | Dev: 2 tries |
| E6 | BE traces from E1–E5 | Stratified by model, domain and correctness | Truncation f ∈ {0, .1, .25, .5, .75} | 100% |

### 2.9 Coverage: which sets bound which theories' weights

Key (weights, not verdicts):

- **✓** = at full size, the set can push the theory's weight toward zero. When the theory carries no weight, the set bounds it at ≤ 0.10 (upper 95%), and the theory's pattern is separated from the favoured theory by ≥ 2 log10 units on the dev set (library likelihood-ratio tables).
- **~** = the bound is weaker (≤ 0.25), or holds only conditionally, e.g. only where the relevant members disagree, or once pending predictions (PyETR) are in.
- **blank** = no leverage.

Column groups: E1 (COL, SAT, KN/TSP), E2 (COL, SAT, KN), E3 (U, I), E4, E5 (COL, STATE, ENT), E6.

| Theory | E1-COL | E1-SAT | E1-KN/TSP | E2-COL | E2-SAT | E2-KN | E3-U | E3-I | E4 | E5-COL | E5-STATE | E5-ENT | E6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 POLARITY | | ✓ | | | ✓ | | | | ✓ | | ✓ | | |
| C0 JW / MOMS | | | | | ✓ (mixed width) | | | | | | | | |
| C1 FF-LIST / GREEDY-MENTION / INPUT-FIT / NN-FIRST | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ~ | ✓ | ✓ | | ~ |
| C1 FF-LABEL / GREEDY-INDEX / NN-LABEL0 | ✓ | ✓ | ✓ | | | | ✓ (label arm, gated) | | | | | | |
| C1 FF-OUT (AR) | ✓ | | | | | | ✓ (LIST vs REV) | | | | | | |
| C1 static score (LF, RATIO, DIFF, VALUE, LARGEST-FIT) | ✓ (ties only) | | ✓ | ✓ | | ✓ | ✓ | | | | | | |
| C1 GREEDY-CM | | | | | | | | | | | | ✓ | |
| C2 DSATUR | ✓ | | | ✓ | | | ✓ | | ~ | ~ | | | |
| C2 UC / GUC / SC | | ✓ | | | ✓ | | | | ✓ | | ✓ | | |
| C2 GREEDY-EDGE / FI | | | ✓ | | | | | | | | | | |
| C3 RO-FF / RO-GREEDY | ✓ | ✓ | | ~ | ~ | | ✓ | | ✓ | | | | |
| C→F GREEDY+REPAIR | ~ | | | | | | | | | ✓ | | | ~ |
| D DPLL-σ (incl. "goal-directed cone evaluation") | ✓ (M5) | ✓ (c6) | | ✓ (BASE: 3 vs 4 colours) | ✓ | ✓ | | ~ (tokens) | ✓ | ✓ | ✓ | ✓ | |
| F MIN-CONFLICTS / WALK | ~ (vs C ✓; vs EXACT only ≤ 0.15, §2.10) | ~ | | ✓ | ✓ | | ✓ | | ✓ | ✓ | ✓ | | |
| E LOCAL-t (ID = label or listing) | ✓ | | | | | | ✓ (depth horizon) | ✓ | | | | | |
| B1 DROP-LAST-EDGES / UP | | | | | | | | | ~ | ✓ (edge-order localisation) | | ✓ (UP never says YES) | |
| B4 PHANTOM-ADJACENT | | | | | | | | | | ✓ (false IMPOSSIBLE on CONTROL) | | | |
| C4 ONLINE-STATE / ETR | | | | | | | | | | ✓ (conflicts with distant earlier neighbours) | | ✓ (once PyETR predictions are added) | |
| A cues (DENSITY, ALL-T, ALWAYS-YES, PRIMACY) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | |
| H RANDOM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| EXACT (the model solves it, order-free) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | |
| NOISY-EXACT | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (condition dependence) | ✓ | ✓ | ✓ | ✓ | ✓ | |
| PERCEPTION-NOISE | ~ | ~ | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ (K11 + location) | ✓ | | |
| Const-depth proxy (LOCAL-t-LIST) | | | | | | | ✓ | ✓ | | | | | |
| Post-hoc trace (answer pre-committed) | | | | | | | | | | | | | ✓ |

**Every theory's weight is bounded by at least one set.** The weakest coverage is for JW/MOMS (mixed-width E2-SAT only), GREEDY-EDGE/FI (TSP arms only, secondary), B4 and C4 (E5-COL, and E5-ENT once PyETR predictions are in). Some pairs are tied on every set but one: their likelihood ratio is > −0.5, so only the sum of their weights is identified there. The set that separates each pair:

| Tied pair | Separating set |
|---|---|
| FF-σ vs DPLL-σ vs GREEDY+REPAIR-σ | E5-COL (and E1 M5, E2-COL BASE) |
| LF vs DSATUR | E2-COL contrast |
| GUC vs SC | E2-SAT contrast |
| RATIO-PREFIX vs SKIP | E2-KNAP PREFIX/SKIP pairs |
| FF-LIST vs a long-horizon const proxy | E3's depth curve |

### 2.10 Fake-model recovery with graded mixtures (behavioural positive controls)

Recovery is judged on **how precisely each weight is recovered**: bias, RMSE, 95% interval width and interval coverage, plus upper bounds for absent theories. Top-1 accuracy is not the criterion. These checks run before any LLM data is analysed (DESIGN §5.12).

**Planted fake models.**

- *Single members* (π = 1): FF-LIST, FF-LABEL, FF-OUT, LF, DSATUR, RO-FF, GREEDY-σ, POLARITY, UC-DET, GUC, GREEDY+REPAIR, DPLL-LIST-b, MIN-CONFLICTS, LOCAL-3-LIST, NOISY-FF (ε ∈ {.02, .05}), PERCEPTION-NOISE.
- *Graded mixtures:*
  - 60/30/10 across three members, in every pairing that matters: a C1 rule / a C2 rule / D; C1-LIST / C1-LABEL / F; GREEDY / POLARITY / UC;
  - 45/45/10 (two near-equal components);
  - 85/10/5 (a minor component near the detection limit).
- *Feature-dependent mixtures* (family I): π_h(φ) = softmax(w_h·φ). Weights shift with density, with output format (ND vs BE), and with whether the item is a C dead end.
- *Nulls:* EXACT 100%; NOISY-EXACT; RANDOM; and a mixture of RANDOM with 20% "none of the above" (unmodelled answers), to check that π_∅ absorbs unmodelled answers instead of inflating a member.
- *Traces:* synthetic traces (templated verbalisations with paraphrase noise), with planted reliability r ∈ {1, 0.6, 0.2}. Unfaithful traces are generated from a different member.

**Pre-registered recovery targets** at full-study size, per eval:

| Quantity | Target |
|---|---|
| \|bias\| per weight | ≤ 0.03 |
| Coverage of the 95% interval for weights in (0.05, 0.95) | ≥ 0.90 |
| Upper 95% bound for planted-absent theories | ≤ the W-row bound in §2.5 |
| Feature-dependent slopes w_h | sign recovered in ≥ 0.9 of replicates; slope interval covers the truth in ≥ 0.9 |
| Estimated r | within ±0.1 of the planted r |
| Combined (answer + trace) inference | never widens the answer-only interval |
| d\* for LOCAL-t-LIST | = t |

**First run (scratch simulation, E1-style colouring copies).**

- Setup: n = 10, 80 bases × 6 copies = 480 items, i.e. dev size, about the full E1-COL size per domain.
- Fitting: EM under the library noise model, with a fitted slip of 0.2 against a true slip of 0.1, slips spread uniformly over candidate answers.
- Uncertainty: a 60-replicate bootstrap over bases; 20 replicate datasets per scenario.

| Scenario | Theory | True π | Mean π̂ | Bias | RMSE | Mean 95% width | Coverage |
|---|---|---|---|---|---|---|---|
| S1 60/30/10 | FF-LIST | 0.60 | 0.625 | +0.025 | 0.047 | 0.123 | 17/20 |
| | DSATUR | 0.30 | 0.284 | −0.016 | 0.032 | 0.087 | 14/20 |
| | DPLL-LIST | 0.10 | 0.091 | −0.009 | 0.032 | 0.101 | 17/20 |
| | absent (FF-LABEL, EXACT, …) | 0 | ≤ 0.001 | — | — | upper bound ≤ 0.003 | — |
| S2 60/30/10 | FF-LIST | 0.60 | 0.658 | +0.058 | 0.068 | 0.105 | 7/20 |
| | FF-LABEL | 0.30 | 0.315 | +0.015 | 0.040 | 0.092 | 15/20 |
| | MIN-CONFLICTS | 0.10 | 0.019 | **−0.081** | 0.084 | 0.051 | 1/20 |
| S3 feature-dependent (dense) | FF-LIST | 0.70 | 0.761 | +0.061 | 0.071 | 0.137 | 13/20 |
| | DSATUR | 0.20 | 0.220 | +0.020 | 0.038 | 0.130 | 20/20 |
| | EXACT | 0.10 | 0.009 | **−0.091** | 0.093 | 0.042 | 1/20 |
| S3 feature-dependent (sparse) | FF-LIST | 0.20 | 0.215 | +0.015 | 0.035 | 0.135 | 19/20 |
| | DSATUR | 0.60 | 0.668 | +0.068 | 0.080 | 0.155 | 14/20 |
| | EXACT | 0.20 | 0.074 | **−0.126** | 0.134 | 0.133 | 2/20 |
| S4 null (EXACT 100%) | EXACT | 1.00 | 0.960 | −0.040 | 0.066 | 0.167 | — |
| | DSATUR / DPLL-LIST / FF-LABEL | 0 | ≤ 0.005 | — | — | upper bound ≤ 0.02 | — |
| | MIN-CONFLICTS | 0 | 0.031 | — | — | upper bound ≈ 0.10 | — |

**What the first run shows.**

1. **Deterministic members are recovered well.** Bias is within ±0.03 in S1. Interval widths are 0.09–0.14 at 480 items, so the W1 analytic bound of 0.04 is optimistic by about 1.5–3×. Absent deterministic members are bounded at ≤ 0.02.
2. **Diffuse theories are not identifiable under a uniform-candidate slip model.** EXACT spreads its mass uniformly over optimal solutions; MIN-CONFLICTS spreads it widely. Both look like "a deterministic member plus slips", so their weight leaks into the deterministic members: biases of −0.08 to −0.13, and +0.06 on FF-LIST/DSATUR.
3. **Bootstrap percentile intervals under-cover.** Coverage is 7–17 out of 20 against a nominal 19. The full pipeline therefore uses posterior intervals from the hierarchical fit, plus a coverage calibration step on these simulations.

**Pre-registered remedies, which are part of the design.**

- **(a) Slips as near-misses.** Slips are modelled with the distance kernel of §1.2 (near-misses around the member's prediction), not as uniform over plausible answers. The slip rate is estimated separately, from instructed single-step items (E3-I at d = 1, E5-P) and from repeat samples.
- **(b) Diffuse weights are reported conditionally.** Weights of diffuse theories (EXACT, F, RO-FF) are always reported with their sensitivity to the slip model, and their lower bounds are not interpreted unless remedy (a) recovers them in simulation.
- **(c) Interval coverage is calibrated** on this harness before any LLM data is analysed.

The kernel-slip re-run is below.

**Second run (remedy (a)).** Slips are near-misses (one vertex recoloured; ε = 0.15), both planted and fitted with the same kernel. Otherwise identical: 480 items; 10 replicates; 40-replicate bootstrap.

| Scenario | Theory | True π | Mean π̂ | Bias | Mean 95% width | Coverage | Upper 95% if absent |
|---|---|---|---|---|---|---|---|
| K1 60/30/10 | FF-LIST / DSATUR / DPLL-LIST | .60 / .30 / .10 | .611 / .295 / .093 | +.011 / −.005 / −.007 | .10 / .09 / .08 | 10, 10, 10 of 10 | absent members ≤ .002 |
| K2 60/30/10 | FF-LIST / FF-LABEL / MIN-CONFLICTS | .60 / .30 / .10 | .598 / .297 / .092 | −.002 / −.003 / −.008 | .09 / .08 / .06 | 9, 9, 7 of 10 | EXACT ≤ .027; others ≤ .015 |
| K3 dense | FF-LIST / DSATUR / EXACT | .70 / .20 / .10 | .696 / .206 / .068 | −.004 / +.006 / −.032 | .12 / .11 / .08 | 10, 10, 7 of 10 | MIN-CONFLICTS ≤ .054 |
| K3 sparse | FF-LIST / DSATUR / EXACT | .20 / .60 / .20 | .196 / .600 / .174 | −.004 / .000 / −.026 | .10 / .10 / .13 | 10, 8, 7 of 10 | MIN-CONFLICTS ≤ .073 |
| K4 null | EXACT | 1.00 | .945 | −.055 | .15 | — | C members ≤ .017; MIN-CONFLICTS ≤ .149 |

**Conclusions** (carried into §2.5 and §2.9).

1. **The kernel slip model is required.** With it, every deterministic weight is recovered within ±0.011. Diffuse weights come back within −0.03, against −0.13 under uniform slips. The feature-dependent split, a strategy-selection curve, is recovered in both density cells.
2. **The full E1 set (500 copies per domain) resolves C-member weights to about ±0.05 (95%).** It bounds absent C members at ≤ 0.02.
3. **EXACT and MIN-CONFLICTS stay partly confounded on E1-type items** (two diffuse, order-free solvers). When the model solves exactly, up to about 0.15 of the weight can sit on F. E1 therefore bounds F against EXACT only weakly; the separation comes from E4/E5 (co-failure and failure forms) and from trace codes (repair vs search).
4. **Diffuse components under-cover** (7 of 10). Coverage calibration (remedy (c)) is mandatory before these weights are reported.

---

## 3. Phase 2 (only if behavioural evidence): mechanistic tests

**Trigger.** Run Phase 2 for member h and model m only if Phase 1 gives answer-based support for h in at least two evals (one of them E1 or E5), and E6 has measured trace reliability.

**State variables.**

1. AR state at the decision token: the forbidden-colour set F(v) (k bits) and the decision c(v); for GREEDY, sign(p − q). Competitors: POLARITY's static bit; UC's "forced + value".
2. The next-item identity under FREE order: DSATUR's argmax vs LF's vs the listing successor.
3. Gadget gate values by layer (E3-I, ND): the FF value of each gate at depth j.
4. Look-ahead variables: the colour a later neighbour will need (D competitor).

**Probes.**

- Linear (logistic) probes at pre-specified positions and layers.
- Selectivity against Hewitt & Liang control tasks.
- Competitor-state probes on dissociating items.
- Format residualisation (Sahoo et al. 2026).
- Train/test split by instance.

**Interventions.**

- Linear DAS (Geiger et al. 2023) or interchange on the F(v) subspace. The source is the same item with a different forced prefix; the prediction is next colour = mex(F_source).
- Compare the interchange-intervention accuracy (IIA) with the same procedure on: (i) competitor variables (POLARITY bit; a RECENCY forbidden set built from the last j lines; the look-ahead set); (ii) a random-init model of the same architecture (Sutter et al. 2025); (iii) a norm-matched random subspace (Cox et al. 2026).
- Guard against the Makelov et al. (2024) illusion: the subspace must be active in unpatched runs.
- H5c: effects must hold on items where FF is wrong.

**Depth staircase.**

- The layer at which a depth-j gate value becomes decodable should grow with j, with a ceiling at d\*.
- Patching a gate value at j ≤ d\* (from the critical-swap source) should flip the target as the circuit predicts.
- For thinking models, a pre-CoT probe for t's bit should be decodable only for d ≤ d\* (design as in Cox et al. 2026).

**Positive controls.**

- An InterpBench-style SIIT toy implementing AR-FF in our exact format, and a competitor SIIT toy implementing AR-DSATUR. The pipeline must recover F(v) in the first, and must *not* find it above controls in the second.
- An ALTA-compiled AR-FF / GREEDY loop.
- A Ye-et-al.-style capacity toy trained on E3-I target queries within vs beyond its depth capacity. It calibrates hops per layer for the staircase.

**Avoiding a re-run of AlgoTrace.**

- No mechanistic work on TSP.
- The variables come from a specified causal model with competitor and random-init controls, not from unsupervised primitive clusters plus steering.
- Order-only minimal pairs give interventions whose effect order-invariant competitors cannot reproduce.

**Models.** In line with "no tiny models":

- Qwen3-14B (transcoders; thinking and non-thinking in one checkpoint);
- gpt-oss-20b (the first behavioural model; circuit-tracer transcoders exist);
- Qwen3-8B as the cheap development model;
- Qwen3-32B for behaviour-linked probes only;
- R1-Distill-Qwen-14B, to ask whether reasoning distillation changes the per-step rule.

The 8–32B range gives a ladder for d\* vs layer count, and fits on one 80 GB GPU (32B at bf16 is tight).

---

## 4. Build scope

| # | Component | Person-days | Shared infrastructure? |
|---|---|---|---|
| 1 | Order-aware renderers and isomorphic-copy machinery (colouring, SAT, knapsack, TSP, entailment hook); per-tokenizer label and length assertions | 3 | **Yes** (A, B4, C4 use the same order objects) |
| 2 | C zoo: about 30 members with variants, deterministic and Monte-Carlo, ABORT/INFEAS; unit tests on hand-worked items; property tests (L1, L2, gadget lemma, isomorphism invariance of order-free members) | 5 | Zoo framework yes; members no |
| 3 | Order variants of competitor members (DPLL-σ, MIN-CONFLICTS inits, GREEDY+REPAIR, LOCAL-t, DROP-LAST, PHANTOM) | 2 | **Yes** (zoo) |
| 4 | E1 generator (partition and solution enumeration, Grundy base rates, filters) | 2 | No |
| 5 | Edit-search minimal-pair engine, E2-KT constructor, TSP pairs | 3 | **Engine yes** |
| 6 | E3 generators (two-circuit gadget, balancing, proxy audit, CNF gadget with exhaustive check, NN margin pairs). Scratch prototypes exist. | 3 | No |
| 7 | E4/E5 generators (filtered pools, order-free matching, 2×2 orders, state search, GREEDY-CM entailment hook) | 3 | Partly |
| 8 | Scorers: partition distance, canonicalisation, Grundy test, violation localisation, same-class readout, A2 | 2 | **Yes** (scorer framework) |
| 9 | Trace pipeline: commitment extractor plus replay checker plus K11 checker (4); LLM-coder codebook and chunking (2); hand-labelling of 200 traces × 2 coders (≈ 10 min per long trace ≈ 8) | 14 | **Yes** (all verticals; the C codebook is C-specific) |
| 10 | E6 early-answer harness (prefill truncation on open models) | 1.5 | **Yes** |
| 11 | Analysis scripts: lifts, DDI, psychometrics, A2/d\* fits, co-failure GLMMs, 2×2 localisation, κ, combined likelihood | 5 | Partly |
| 12 | Fake-model recovery with synthetic traces | 2.5 | **Harness yes** |
| 13 | Dev-batch pilot and per-model n\* calibration | 2 | — |
| | **Behaviour total** | **48** (of which 8 annotation) | |
| 14 | RASP-L programs for POLARITY, AR-FF, AR-GREEDY, AR-DSATUR, AR-UC | 2 | Interpreter shared |
| 15 | Phase 2, if triggered: SIIT ×2 (5), ALTA (2), capacity toy (4), LLM probes and DAS (8) | 19 | Activation tooling shared |

**Should be built once, centrally:**

- content-hashed item store and split assignment;
- runner (vLLM/SGLang, budget forcing, censoring, manifests);
- structured-output parsing;
- identification engine (likelihoods, mixtures, permutation baselines, hierarchical model);
- order objects and copies;
- edit-search engine;
- trace pipeline and coder harness;
- early-answer harness;
- fake-model harness.

---

## 5. Compute budget

Notes on the figures:

- **Thinking tokens.** BE output tokens are our estimates for gpt-oss-20b/Qwen3-class models at high effort, including the answer. They are informed by reports that thinking tokens grow with size and stay high on hard or over-constrained items (Hazra et al. 2025; Verma 2026: random-UNSAT items reach 16k). **Every figure is replaced by dev-batch measurements before the full run.**
- **Samples.** "1.4" = 1 sample plus 2 more on a 20% subset.
- **Dev rows.** They exercise every cell with about 5 items per cell, at one sample per item (E3: 2), on gpt-oss-20b (BE) and Qwen3-14B (ND).
- **Phase 2 rows** are forward passes on open models (activations).

| Eval ID | Domain | # items | Conditions (e.g. direct, CoT-1k, CoT-4k) | Samples/item | Avg prompt tokens | Avg output tokens per condition | Needs activations? (Y/N) |
|---|---|---|---|---|---|---|---|
| E1-COL | colouring n = 16 | 500 | BE; ND | 1.4 | 550 | BE 7,000 (≤ 2% at 32k); ND 100 | N |
| E1-COL dev | colouring | 50 | BE; ND | 1 | 550 | BE 7,000; ND 100 | N |
| E1-SAT | 3-SAT n = 20 | 500 | BE; ND | 1.4 | 900 | BE 10,000 (~5% at 32k); ND 100 | N |
| E1-SAT dev | 3-SAT | 50 | BE; ND | 1 | 900 | BE 10,000; ND 100 | N |
| E1-KNAP | knapsack n = 20 | 200 | BE; ND | 1.4 | 390 | BE 6,000; ND 60 | N |
| E1-KNAP dev | knapsack | 20 | BE; ND | 1 | 390 | BE 6,000; ND 60 | N |
| E1-TSP | TSP n = 12 | 200 | BE; ND | 1.4 | 550 | BE 10,000 (~3% at 32k); ND 50 | N |
| E1-TSP dev | TSP | 20 | BE; ND | 1 | 550 | BE 10,000; ND 50 | N |
| E2-COL | colouring n = 16 | 720 | BE; ND | 1.4 | 550 | BE 7,000; ND 100 | N |
| E2-COL dev | colouring | 72 | BE; ND | 1 | 550 | BE 7,000; ND 100 | N |
| E2-SAT | 3-SAT / 2+3-SAT n = 20 | 900 | BE; ND | 1.4 | 850 | BE 11,000 (~6% at 32k, mostly G-ONLY UNSAT edits); ND 100 | N |
| E2-SAT dev | 3-SAT | 90 | BE; ND | 1 | 850 | BE 11,000; ND 100 | N |
| E2-KNAP (incl. KT) | knapsack n = 25 | 400 | BE; ND | 1.4 | 450 | BE 6,000; ND 70 | N |
| E2-KNAP dev | knapsack | 65 | BE; ND | 1 | 450 | BE 6,000; ND 70 | N |
| E2-TSP | TSP n = 12 | 360 | BE; ND | 1.4 | 550 | BE 10,000; ND 50 | N |
| E2-TSP dev | TSP | 45 | BE; ND | 1 | 550 | BE 10,000; ND 50 | N |
| E3-COL-U | colouring gadget n = 68 | 2,160 (BE on 1,080 LIST items) | BE (LIST); ND (LIST, REV); T1k, T4k (LIST, REV); LOW (gpt-oss) | 2 | 1,480 | BE 14,000 (~10% at 32k); ND 450; T1k 1,450; T4k 4,400; LOW ~2,500 | N |
| E3-COL-U dev | colouring gadget | 180 (BE on 90) | as above | 2 | 1,480 | as above | N |
| E3-COL-I | colouring gadget n = 68 | 1,080 | BE; ND; T1k; T4k; LOW | 2 | 1,250 | BE 6,000 (~1% at 32k); ND 8; T1k 1,010; T4k 3,600; LOW ~1,500 | N |
| E3-COL-I dev | colouring gadget | 90 | as above | 2 | 1,250 | as above | N |
| E3-SAT-I (gated) | CNF gadget | 900 | BE; ND; T1k; T4k | 2 | 2,400 | BE 12,000 (~5% at 32k); ND 8; T1k 1,010; T4k 3,900 | N |
| E3-SAT-I dev (gated) | CNF gadget | 75 | as above | 2 | 2,400 | as above | N |
| E3-NN | TSP n = 14 | 800 | BE; ND | 2 | 330 | BE 8,500 (instructed ~5k, tour ~12k); ND 35 | N |
| E3-NN dev | TSP | 100 | BE; ND | 2 | 330 | as above | N |
| E4-SAT | 3-SAT n = 25/40 | 640 | BE; ND | 1.4 | 1,360 | BE 18,000 (~20% at 32k overall; n = 40 with α ≥ 3.7: 40–60%); ND 160 | N |
| E4-SAT dev | 3-SAT | 80 | BE; ND | 1 | 1,360 | as above | N |
| E4-COL | 3-colouring n = 30/50 | 480 | BE; ND | 1.4 | 950 | BE 16,000 (~20% at 32k; n = 50 with c ≥ 4.3: 30–50%); ND 250 | N |
| E4-COL dev | 3-colouring | 60 | BE; ND | 1 | 950 | as above | N |
| E5-COL | 3-colouring n = 24 | 480 | BE; ND | 1.4 | 600 | BE 10,000 (~5% at 32k); ND 150 | N |
| E5-COL dev | 3-colouring | 30 | BE; ND | 1 | 600 | as above | N |
| E5-SAT | 3-SAT n = 25–40 (+ E4 reuse) | 100 | BE; ND | 1.4 | 1,360 | BE 18,000 (~20% at 32k); ND 160 | N |
| E5-SAT dev | 3-SAT | 10 | BE; ND | 1 | 1,360 | as above | N |
| E5-STATE | SAT n = 20 / colouring n = 16 | 600 | BE; ND | 1.4 | 800 | BE 7,000 (~2% at 32k); ND 100 | N |
| E5-STATE dev | SAT / colouring | 30 | BE; ND | 1 | 800 | as above | N |
| E5-ENT | entailment | 240 | BE; ND | 1.4 | 300 | BE 3,000; ND 5 | N |
| E5-ENT dev | entailment | 20 | BE; ND | 1 | 300 | as above | N |
| E5-P | SAT / colouring (prefilled single step) | 600 | ND only | 1 | 800 | ND 5 | N |
| E5-P dev | SAT / colouring | 30 | ND only | 1 | 800 | ND 5 | N |
| E6-EA | re-prompts of BE traces | 1,000 per open thinking model | forced answer after truncation (f ∈ {0, .1, .25, .5, .75}) | 1 | 5,500 (prompt + partial trace) | 30 | N |
| E6-EA dev | re-prompts | 100 | as above | 1 | 5,500 | 30 | N |
| M1 (Phase 2) AR-state probes | E5-P / E1-COL LIST items | 900 | ND (teacher-forced prefixes) | 1 | 800 | 0 (forward only) | Y |
| M2 (Phase 2) depth staircase | E3-COL-I | 1,080 | ND; BE pre-CoT position | 1 | 1,250 | 1 | Y |
| M3 (Phase 2) DAS / interchange | base–source pairs from E5-P | 600 pairs | ND | 2 forward passes | 800 | 0 | Y |
| M4 (Phase 2) look-ahead probes | E5-STATE / E5-P subset | 300 | ND | 1 | 800 | 0 | Y |

**Totals.**

| Item | Figure |
|---|---|
| Full study, unique items per model | 10,960 (E3-SAT-I excluded while gated) |
| Best-effort volume per model | ≈ 159M tokens (146M decoded) |
| Best-effort volume, 9-model panel | ≈ 1.43B tokens |
| ND diagnostics (4 Qwen3 models) | ≈ 65M |
| Budget factor (6 models, E3 only) | ≈ 321M |
| Early answering (7 open thinking models) | ≈ 39M |
| **Total** | **≈ 1.85B tokens** |
| If E3-SAT-I is released | +26M per model (BE) and +17M per model (budgets) |
| Dev batch | 1,042 items + 100 early-answer re-prompts ≈ 13M tokens on gpt-oss-20b at BE (E3 accounts for about 45%) |

**Truncation at 32k (expected; censored).**

| Items | Expected share at 32k |
|---|---|
| E4-SAT, n = 40, α ≥ 3.7 | 40–60% |
| E4-COL, n = 50, c ≥ 4.3 | 30–50% |
| E5-SAT (dead-end items from the high-α cells) | ~20% |
| E3-COL-U at n = 68 | ~10% (more on REV under budgets, by design) |
| E2-SAT G-ONLY edits that make the formula UNSAT | ~15% |
| Everything else | ≤ 5% |

Qwen3-235B-A22B-Thinking and R1 think longest, so expect their truncation at the upper end. If a cell exceeds 50% censoring for a model, its size is reduced for that model, as part of n\* re-centring.

---

## 6. What would bound family C's role toward zero

Family C's role is graded, so "falsified" means bounded: C's weight is pushed toward zero with a stated upper bound. For model m, C's role is **bounded to negligible** if the hierarchical fit gives all of the following. Each is reported with its interval.

1. **E1.** Every order source has π ≤ 0.05 (upper 95%) on every domain. The Grundy-based first-fit weight (any order), π_FF-any, has upper 95% ≤ 0.05.
2. **E2 and E5-STATE.** Every C rule has π ≤ 0.08 per contrast (upper 95%) against its D/F/EXACT competitor. The C state-dependence weights have upper 95% ≤ 0.05.
3. **E4/E5.** The C share of failures is ≤ 0.06 (upper 95%). The C-ABORT and C-INFEAS components are each ≤ 0.05. The localisation interaction's interval includes 0.
4. **Mixture.** The family weight π_C on items where C disagrees with D/F/EXACT has upper 95% ≤ 0.05, and Δlog10 L(with C − without C) is ≤ 0 on held-out items.

**Partial outcomes.** These are reported as weight *shifts*, which narrow the claim rather than reject it:

- **Shallow cue (H-C3c).** π_seq(d) decays with d under BE as well as under ND, while π_proxy holds. The order-sensitive weight is then a shallow cue, and FF-LIST's weight beyond depth d\* is bounded ≤ u(d). "The model runs first-fit" is then false beyond d\*, even where the answers match it.
- **Answer-writing, not reasoning.** π_OUT carries the order weight only when the requested answer order equals the processing order, and Δπ_OUT(ND − BE) is large. The "greedy" weight then belongs to autoregressive answer-writing, not to the reasoning procedure.
- **Unfaithful traces.** T_h is high for C1 signatures, but r ≈ 0 (upper 95% ≤ 0.2) for the order codes. Trace-based reports of greedy strategies (Hazra et al.'s reading of GPT-4o traces, for example) then get no behavioural confirmation: the answer-based π_C1 is the number to cite.
- **Strategy selection (family I).** π_C depends strongly on features, e.g. high under ND or near n\* and low under BE. The result is then a strategy-selection curve π_C(φ), with intervals, not a single number.

---

## 7. Evidence-table row

| Behavioural lift over baseline | Mixture weight | Signatures matched | Process match | Probe selectivity | Intervention vs competitor | Control recovered | RASP-L length / class |
|---|---|---|---|---|---|---|---|
| [lift per member, with intervals; Δlog10 L vs null and vs nearest competitor] | [π_C with 95% interval, split into C0/C1/C2/C3/hybrid; π_C(φ) curves by condition] | [x / 7 rows of §2.3, each as an estimated effect with an interval] | [T_h vs π_h, with r per code] | Phase 2 | Phase 2 | [§2.10: bias and interval coverage for planted graded mixtures] | AR-FF 7 / 3 layers (per step; seq latent); POLARITY 3 / 2 (const) |

---

## 8. Open questions

1. **Tie-break defaults.** Is "earliest listed" the right primary key, or should "lowest label" be primary for numeric labels? The dev batch decides; pre-register the choice before the full run.
2. **Thresholds for SC and GUC at k = 3**, and the exact SC rule: confirm with the original papers (Chao & Franco; Frieze & Suen) or drop the attributions.
3. **A proof** that the E3-SAT gadget is a log-space reduction from NOR-CVP to GREEDY-INDEX, which would make GREEDY P-complete. Is this result already known?
4. **Whether sorting ∈ TC⁰** (for RATIO-PREFIX's const label). F report, unverified.
5. **The ETR/PyETR predictions for E5-ENT** and the colouring analogue of C4 (premise-at-a-time with memory k). Coordinate with the B4/C4 owners.
6. **Whether LOW effort on gpt-oss** should count as a "low-budget" level in E3's budget factor, or be reported separately.
7. **Whether the trace coder may be a panel model** (circularity), or should be from outside the panel.

---

## References

Only papers from the repo's literature reports. The tag is the report and its check level ([R] read, [A] abstract, [S] secondary, [M] metadata). Details marked [S]/[M] are to be confirmed before citing in the paper.

- Alekhnovich, Borodin, Buresh-Oppenheim, Impagliazzo, Magen & Pitassi (2011). *Toward a Model for Backtracking and Dynamic Programming.* Computational Complexity 20. [F, R]
- Achlioptas (2001). *Lower bounds for random 3-SAT via differential equations.* TCS. [F, S] · Achlioptas & Sorkin (2000). *Optimal myopic algorithms for random 3-SAT.* FOCS. [F, A] · Achlioptas & Coja-Oghlan (2008). *Algorithmic Barriers from Phase Transitions.* FOCS, arXiv 0803.2122. [F, A]
- Blelloch, Fineman & Shun (2012). *Greedy Sequential Maximal Independent Set and Matching are Parallel on Average.* SPAA, arXiv 1202.3205. [F, A]
- Borodin, Nielsen & Rackoff (2003). *(Incremental) Priority Algorithms.* Algorithmica 37. [F, S]
- Bröder & Schiffer (2003); Glöckner (2009); Davis-Stober & Brown (2011); Myung & Pitt (2009). Strategy classification and optimal design. [B]
- Chen, Chi, Wang & Zhou (2024). *Premise Order Matters in Reasoning with LLMs.* ICML, arXiv 2402.08939. [B]
- Cook (1985). *A taxonomy of problems with fast parallel algorithms.* Information and Control 64. [F, via compendium]
- Cox, Kianersi & Garriga-Alonso (2026). *Post-Hoc Reasoning in Chain of Thought.* arXiv 2603.01437. [C]
- Csordás, Manning & Potts (2025), arXiv 2505.13898; Hu, Zhou & Zhang (2025), arXiv 2512.14064; Yao et al. (2025), arXiv 2505.17923. Depth limits. [C]
- Duchnowski, Pavlick & Koller (2025). *A Knapsack by Any Other Name* (EHOP). Findings of EMNLP, arXiv 2502.13776. [B, R]
- Fan, Du, Ramchandran & Lee (2025). *Looped Transformers for Length Generalization* (n-RASP-L). ICLR, arXiv 2409.15647. [D]
- Geiger, Wu, Potts, Icard & Goodman (2023). DAS. arXiv 2303.02536. [C]
- Gema et al. (2025), arXiv 2507.14417; Ghosal et al. (2025), arXiv 2506.04210. Non-monotone budget effects. [A]
- Greenlaw, Hoover & Ruzzo (1991/1995). *A Compendium of Problems Complete for P.* TR91-11 / *Limits to Parallel Computation.* Entries A.2.6, A.2.12, A.6.1, A.8.5 remark. [F, R; entry numbers to confirm]
- Gupta, Arcuschin, Kwa & Garriga-Alonso (2024). *InterpBench.* arXiv 2407.14494. [C]
- Hazra, Venturato, Zuidberg Dos Martires & De Raedt (2025). *Have LLMs Learned to Reason? A Characterization via 3-SAT Phase Transition.* COLM, arXiv 2504.03930. [A/B]
- Hewitt & Liang (2019). *Designing and Interpreting Probes with Control Tasks.* arXiv 1909.03368. [C]
- Heyman & Zylberberg (2025a, b). arXiv 2502.07087; 2505.12151. [A]
- Jones & Laaser (1976). *Complete problems for deterministic polynomial time.* TCS. [F, S]
- Lippl et al. (2025/26). *AlgoTrace.* arXiv 2510.15987. [B, C]
- Makelov, Lange & Nanda (2024). *Is This the Subspace You Are Looking for?* arXiv 2311.17030. [C]
- Monasson et al. (1999). 2+p-SAT. Nature. [F, M]
- Saparov & He (2023). *Language Models Are Greedy Reasoners.* ICLR, arXiv 2210.01240. [B]
- Sahoo, Jain, Chadha & Chaudhary (2026). *Linear Probes Detect Task Format, Not Reasoning Mode.* arXiv 2606.02907. [C]
- Shaw et al. (2025). *ALTA.* TMLR, arXiv 2410.18077. [C/D]
- Sutter, Minder, Hofmann & Pimentel (2025). *The Non-Linear Representation Dilemma.* arXiv 2507.08802. [C]
- Tang et al. (2025). *GraphArena.* ICLR, arXiv 2407.00379. [A/B]
- Verma (2026). *Solver-Hard Is Not Model-Hard.* arXiv 2607.17047. [A]
- Ye, Fu, Jia & Sharan (2025/26). *Transformers Provably Learn Algorithmic Solutions for Graph Connectivity, But Only with the Right Data.* arXiv 2510.19753. [C]
- Zhang, Chen & Chen (2026). *Satisfiability Solving with LLMs: A Matched-Pair Evaluation.* FSE, arXiv 2605.28602. [A]
- Zhou et al. (2024). *What Algorithms can Transformers Learn?* (RASP-L). ICLR, arXiv 2310.16028. [D]
