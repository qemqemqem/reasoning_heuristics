# [TODO Title] — working: *Greedy by Default? Identifying the Heuristics Language Models Use on NP-Hard Problems*

> **Skeleton, written for us.**
>
> - Every number is a stand-in (`XX`, `+XX pp`, `0.XX`) showing the *kind* of metric we will report. `[TODO …]` marks text to write.
> - The frameworks (§3) and heuristic families (§5) are filled in briefly from literature reports E and F ([LITERATURE.md](LITERATURE.md), [literature/](literature/)).
> - Section ↔ plan:
>   - §3 = Step 1 (real problems are NP-hard)
>   - §5 = Step 2 (heuristic families)
>   - §7 = Step 3 (evals)
>   - §8 = Step 4 (interpretability)
>   - §9 = Step 5 (the table)
>   - §10 = Step 6 (RASP-L explanation)
>
> **Labels:** heuristic *families* are **A–I**. *Depth* is **const** (O(1) rounds: possible in one forward pass), **polylog** (polylog rounds), or **seq** (inherently sequential: P-complete or exponential, so it needs chain of thought).

**Authors:** [TODO]

---

## Abstract

[TODO 150–200 words.] Draft shape:

> Many reasoning problems people bring to language models are NP-hard, yet models answer them with bounded computation, so on hard instances they must rely on heuristics. We ask *which* heuristics. We model real-world tasks as [TODO chosen problem models] and organise heuristics for NP-hard problems into [XX] families. For each family we design discriminating evaluations and mechanistic tests. Across [XX] models and [XX,XXX] instances, [TODO standout family] explains [XX]% of errors above the budget line ([+XX] pp over chance), and its internal state is linearly decodable and causally used in [TODO open models]. A RASP-L account explains why: [TODO one sentence].

---

## 1. Introduction

- **Opening:** [TODO real problems are hard: scheduling, planning, configuring, checking whether a conclusion follows. Andrew's earlier statement of this: Richardson 2025, "Many Common Problems are NP-Hard", Mechanistic Mind.]
- **The puzzle:** [TODO models answer in far fewer tokens than exhaustive search needs. Beyond that budget they must use an incomplete procedure. Which one?]
- **Why it matters:** [TODO predicting failures; benchmark design; when to add thinking budget or tools. Error composition, not error rate.]
- **What we do:** [TODO model real problems → enumerate heuristic families → evals per family → interpretability per family → evidence table → RASP-L explanation.]

**Contributions.**

1. [TODO] A comparison of formal models of real-world reasoning problems, and the case for [TODO chosen models].
2. [TODO] A taxonomy of heuristics for NP-hard problems in [XX] families, each with a reference implementation, a predicted error signature and a depth class.
3. [TODO] A method that identifies heuristics from instance-level answers, validated by recovering planted heuristics.
4. [TODO] Behavioural and mechanistic evidence per family across [XX] models. The standout is [TODO].
5. [TODO] A RASP-L account of the standout, with predictions written down before the evals.

**Figure 1** — [TODO The evidence table (Table 14) as a heatmap, with the standout row highlighted.]

---

## 2. Related work

[TODO One paragraph each.]

- **LLMs on NP-hard problems:** EHOP, GraphArena, Hazra et al. 2025, NPPC, Zhang et al. 2026.
- **Reasoning effort vs complexity:** Shojaee et al. 2025 and replies; Rameshkumar et al. 2025.
- **Heuristics and biases in LLMs, and human comparisons:** Koralus & Wang-Maścianica 2023; Richardson et al. 2025; Hagendorff et al. 2023; Eisape et al. 2024.
- **Strategy identification:** Bröder & Schiffer 2003; Glöckner 2009; Davis-Stober & Brown 2011; Myung & Pitt 2009.
- **Interpretability of reasoning and search:** Hong et al. 2025; Nikankin et al. 2025; AlgoTrace; Ye et al. 2025; Sutter et al. 2025.
- **RASP and what transformers learn:** Weiss et al. 2021; Zhou et al. 2024; Huang et al. 2025/2026; ALTA.
- **Intractability in cognitive science:** van Rooij et al. 2019; Kwisthout et al. 2011.

---

## 3. Real-world problems are well modelled by NP-hard problems  *(Step 1)*

### 3.0 How we argue it: the frameworks

**The claim, in three layers.**

1. **Hard cores.** Real tasks contain NP-hard (or harder) problems, often already at the *feasibility* level. Satisficing doesn't escape: timetabling, configuration and Sudoku feasibility are NP-complete.
2. **Generality.** Any *general* capacity, stated in full, comes out NP-hard. van Rooij 2015 calls this a natural consequence of domain generality.
3. **Budget.** On our instance distributions, some measured share XX% of items is beyond what any known procedure solves within the model's token budget.

**Frameworks we draw on.** One line each:

| # | Framework | Claim we use | Key sources |
|---|-----------|--------------|-------------|
| F1 | **Computational-level intractability** (tractable-cognition thesis) | General cognitive capacities, stated fully, are NP-hard, so a finite agent must compute something else | van Rooij 2008; van Rooij, Blokpoel, Kwisthout & Wareham 2019; Kwisthout et al. 2011 |
| F2 | **Catalogues by reduction** | Real tasks contain hard cores; hardness often holds for feasibility or approximation | Garey & Johnson 1979; Even, Itai & Shamir 1976; Table 1 |
| F3 | **Bounded rationality / resource rationality** | Heuristics are the rational response to intractability. Humans show accuracy falling with instance hardness. Choosing heuristics by adaptation is itself intractable, and for LLMs training is that adaptation (links to §10). | Simon; Gigerenzer; Russell & Subramanian 1995; Lieder & Griffiths 2020; Murawski & Bossaerts 2016; Rich et al. 2019 |
| F4 | **Parameterized complexity** | Names *which* parameter makes a task hard, which gives us hardness dials | Downey & Fellows; van Rooij & Wareham 2008 |
| F5 | **Beyond worst-case** | Hardness that matters is on the instance distribution and relative to the solver's budget, so we measure it | Roughgarden 2019; Bogdanov & Trevisan 2006 |

**Counterargument to answer:** real instances have exploitable structure (industrial SAT; backdoors).

- **Reply 1:** structure isn't sufficient (Mull et al. 2016).
- **Reply 2:** "easy for a solver taking millions of steps" isn't "easy in a few thousand tokens".

[TODO one paragraph.]

### 3.1 Candidate formal models

**Table 1. Candidate formal models of real-world reasoning problems.** Coverage = share of a sample of real tasks (§3.2) that the model expresses faithfully. "Use" = role in our study.

| Model | Real-world tasks (catalogue examples) | Complexity | Coverage | Ground truth & checkable answer | Use |
|-------|----------------------------------------|------------|----------|---------------------------------|-----|
| **Logic: entailment** (propositional / monadic) | Rule and policy checking; regulatory compliance (coNP-complete; Colombo Tosatto et al. 2015); "does this follow?" | coNP-complete | XX% | ✓ SMT; small answer | **Primary** (continuity with v1; cognitive heuristics exist) |
| **SAT / CSP (feasibility)** | Product configuration (Sinz et al. 2003); timetabling (Even et al. 1976); residency matching with couples; Sudoku, Minesweeper | NP-complete | XX% | ✓ SAT solver; assignment | **Primary** (hardness dial: clause/variable ratio) |
| **Graph coloring / independent set** | Exam scheduling, room allocation, seating, groups without conflicts (EHOP) | NP-complete | XX% | ✓; coloring | **Primary** (rich greedy family) |
| **Packing / selection** (knapsack, set cover, bin packing) | Budgeting, sightseeing in limited time, procurement and auctions (Sandholm 2002) | NP-hard | XX% | ✓ DP; subset | Secondary |
| **Sequencing / routing** (TSP, VRP, job-shop) | Errands, delivery routes, factory scheduling (Lenstra et al. 1977), crew rostering | NP-hard | XX% | ✓; tour or schedule | Secondary (TSP is not our showcase, given AlgoTrace) |
| **Abduction / diagnosis** | Medical diagnosis with multiple disorders (Bylander et al. 1991); explaining symptoms (Eiter & Gottlob 1995) | NP-hard to Σ₂ᵖ ("harder than deduction") | XX% | ✓ for small cases | Secondary (natural extension of entailment) |
| **Probabilistic inference / MPE** | Prediction with causal models; "best explanation" (Cooper 1990; Kwisthout et al. 2011) | NP-hard, also to approximate | XX% | partial | Later |
| **Planning** (STRIPS) | Multi-step tasks, agents (Bylander 1994) | PSPACE-complete (NP-complete when bounded) | XX% | ✓ planner; plan | Later (near-solved at benchmark sizes) |
| **Similarity / structure** (analogy, clustering, coherence) | Analogy (structure mapping), categorising, judging coherence | NP-hard | XX% | weak (answers are graded) | Out of scope |
| **Strategic** (Nash equilibria, mechanism design) | Markets, bargaining, voting rules | PPAD-complete / various | XX% | weak | Out of scope |

### 3.2 How we chose

[TODO Describe the task sample: XX tasks from [TODO source: user requests, occupational task lists, agent benchmarks such as TravelPlanner and NATURAL PLAN]. Map each to a model; inter-rater κ = 0.XX. Selection criteria:

1. coverage;
2. computable ground truth;
3. small, checkable answers;
4. well-defined heuristics;
5. a hardness dial;
6. natural rendering in language.]

### 3.3 Our instances are hard, and hard in the right way

[TODO Three hardness axes: solver effort; proof hardness; heuristic-relative hardness (how many zoo heuristics fail on the item). Plus the parameter that drives hardness, from F4.]

**Table 2. Hardness of the item sets.**

| Domain | n | Hardness parameter (F4) | Solver nodes (median) | % proof-hard | % items where ≥1 heuristic fails | % items where heuristics disagree |
|--------|---|-------------------------|-----------------------|--------------|----------------------------------|-----------------------------------|
| Entailment | XX–XX | # disjunctive premises | XX | XX% | XX% | XX% |
| 3-SAT | XX–XX | α = clauses / vars (≈ 4.26) | XX | XX% | XX% | XX% |
| Coloring | XX–XX | edge density / χ | XX | — | XX% | XX% |
| [TODO] | | | | | | |

---

## 4. From hardness to heuristics: the budget line

[TODO A forward pass is in TC⁰. Chain of thought with T tokens gives at most T sequential steps. Exact search needs on the order of 2^Θ(n) steps on hard instances, and is *expressible* given enough tokens (Pan et al. 2025). So each model and budget has a size n\* above which the answer must come from an incomplete procedure.]

**Figure 2** — [TODO Accuracy vs n per model, with n\* marked.]

**Table 3. Budget line per model.**

| Model | Thinking budget | Estimated n\* | Accuracy below n\* | Accuracy above n\* | Median tokens above n\* | % runs at the cap |
|-------|-----------------|---------------|--------------------|--------------------|-------------------------|-------------------|
| [TODO model A] | 0 | XX | XX% | XX% | XX | XX% |
| [TODO model A] | 4k | XX | XX% | XX% | XX | XX% |
| [TODO model B] | 0 | XX | XX% | XX% | XX | XX% |

---

## 5. A taxonomy of heuristics for NP-hard problems  *(Step 2)*

**Organising principle.** Classify each heuristic by *what it manipulates* and *how it commits*. Several properties are cross-cutting axes, not families:

- approximation guarantee;
- soundness;
- feasibility;
- randomness;
- depth.

Most families have a formal model with known lower bounds:

- priority algorithms for C;
- priority branching trees for D;
- the LOCAL model, low-degree polynomials and GNNs for E;
- PLS for F.

We derive candidate members with **Pearl's simplified-model view**: a heuristic is the exact solution of a simplified problem.

- **Relax** (drop constraints) → errs by *omission*; family B1.
- **Restrict** (add constraints) → errs by *commission*; family B4.
- **Probabilistic model** (replace with an expectation) → family B5.

(Bogdanov & Trevisan 2006 for the formal definition of a heuristic; Pearl 1983.)

**Table 4. Heuristic families.** `*` = new relative to DESIGN v0.2. Signatures are brief and partly our interpretation. Random-instance thresholds are from the literature where given.

| Family | Idea (one line) | Members we'll implement | Depth | Error signature |
|--------|-----------------|-------------------------|-------|-----------------|
| **A. Cue / substitution** | Answer from an easy feature of the input, not its structure (Kahneman & Frederick's attribute substitution) | **A1** constant: `ALWAYS-SAT`, `NONE`, `ECHO` · **A2** feature thresholds: `DENSITY`, `LENGTH-PRIOR`, `FREQ`, `ATMOSPHERE`, `PRIMACY`, `RECENCY` · **A3** problem substitution: `TEXTBOOK-TRANSFER` | const | Wrong on the minority class; blind to structure; moves only when the cue moves |
| **B1. Relax** | Drop some constraints, solve the rest exactly | `UP-k` (k rounds of unit propagation), `RES-w`\* (bounded-width resolution), `PREMISE-SUBSET`\* (use only some premises), `2SAT-CORE`\*, `MST-TOUR`\*, `DROP-CONSTRAINT`\* (systematic, e.g. drop long-range edges) | const for fixed k / w; fixpoint is seq | **Omission** (sound) in entailment; in search, violates exactly the dropped constraint type; biased toward SAT |
| **B3. Convex relax + round** | LP/SDP relaxation, then round | `LP-ROUND`\* | seq (exact LP is P-complete) | Low priority for LLMs |
| **B4. Restrict** | Add constraints or consider only some models of the premises | `FIRST` ("A or B" read as A), `MATCH`, `MM` (principle of truth), `ETR`, `CLOSED-WORLD`\*, `BICONDITIONAL`\* ("if" read as "iff"), `ADD-CONSTRAINT`\* (systematic, e.g. a phantom edge between co-mentioned nodes) | const for a local rewrite; seq for sequential updates | **Commission** (illusory inferences); false "impossible"; feasible but suboptimal |
| **B5. Probabilistic model** | Replace the exact cost with an expectation | `EXPECTED-COST`\* | const | Neither sound nor complete; low priority |
| **C. Constructive / priority** | Consider items in an order; irrevocable decisions (greedy) | **C0** one-shot scoring: `POLARITY`, `MOMS`, `PURE-LITERAL` · **C1** fixed order: `GREEDY`, `FIRST-FIT`, `NN-from-0`, `RATIO`, `VALUE`, `LARGEST-FIT`, `INPUT-ORDER` · **C2** adaptive order: `DSATUR`, `UC`/`GUC`/`SC`\* (unit-clause and shortest-clause rules), `GREEDY-EDGE`, `FARTHEST-INSERTION` · **C3** random order: `RANDOM-ORDER-FIRST-FIT` · **C4** online with bounded state: `ONLINE-STATE(k)`\* (premise-at-a-time update; ETR is one instance) | C0 const; C1/C2 **seq** (first-fit coloring and the NN tour are P-complete); C3 polylog; C4 seq in # premises | Feasible but suboptimal, or dead ends; **order-sensitive**. Thresholds: UC ≈ 8/3, optimal myopic 3.26 on 3-SAT; ≈ 2χ colours |
| **D. Systematic search, truncated** | Backtracking with propagation, cut off at a budget | `DPLL-b` (b decisions then a default answer), `BEAM-w`\*, `BACKDOOR-k`\* (branch only on a few variables) | seq | Exact below budget, default answer above; errors track solver hardness |
| **E. Iterated message passing** | Each variable updates from its neighbours for t rounds, then decides (≈ an L-layer GNN) | `BP-t`\*, `WP-t`\* (warning propagation), `SP-t`\*, `LOCAL-t` coloring\*; decimation `BP-DEC`\* | const for fixed t; decimation seq | Fails beyond algorithmic thresholds (BP-decimation ≈ 2^k/k); never better than simple greedy without extra features (Sato et al. 2019) |
| **F. Local search / repair** | Start from a full candidate and fix violations | `MIN-CONFLICTS`\*, `WALK-k`, `2OPT-k`, `SA`\* | seq (depth ≈ k) | **Infeasible near-misses** (few violated constraints); never certifies UNSAT; depends on initialisation |
| **G. Decompose / DP** | Split into parts and solve each, ignoring or tracking the links | `DP-EXACT` (knapsack DP), `IGNORE-CROSSLINKS`\* (decompose, drop interactions) | seq | Exact when the structure holds; misses cross-component interactions |
| **H. Guess / sample** | Sample from a simple distribution, optionally check | `RANDOM`\* (uniform answer: 7/8 of clauses satisfied), `SAMPLE-m`\* (entailment: check the conclusion in m sampled models) | const (one sample) | Chance level; `SAMPLE-m` commits on items with rare counter-models |
| **I. Strategy selection** (meta) | Choose a heuristic from item features (Rice's algorithm-selection problem; Lieder & Griffiths) | Not a vertical: modelled as feature-dependent mixture weights π_h(φ(x)) | const (the selector) | Errors correlated with features; tests H4 |
| *Nuisance (not heuristics)* | Execution or perception noise | `NOISY-EXACT`, `PERCEPTION-NOISE` (random constraint errors) | — | Smooth error growth with size; unstructured violations |

**Verticals for the pilot:** A, B1, B4, C, D, F, H (plus E if `BP-t` is cheap to implement), with nuisance models always included. [TODO confirm.]

### 5.1 Families, briefly

- **A. Cue / substitution.** [TODO explain heuristic] The model answers a proxy question ("is this long or dense?") instead of the real one. It is the natural null for "no reasoning".
- **B1. Relax.** [TODO explain heuristic] Draw only conclusions you can reach cheaply, e.g. a few propagation steps. Never wrong when it concludes; it just concludes too little.
- **B4. Restrict.** [TODO explain heuristic] Commit early to a reading: one disjunct, "if" as "iff", only the true cases. This is where ETR and mental models live, and the main source of illusory inferences.
- **C. Constructive / priority.** [TODO explain heuristic] Build the answer piece by piece in some order, never revisiting. The prior work's "LLMs are greedy" claim is about this family. We distinguish its members by order type (fixed / adaptive / random / online).
- **D. Truncated search.** [TODO explain heuristic] Real search, but with a budget, then a default. It bridges exact solving and heuristics, and the budget b should grow with thinking tokens.
- **E. Message passing.** [TODO explain heuristic] Local rounds of "my neighbours say…". It is the closest family to what a fixed-depth network computes, so it is a strong candidate for direct-answer mode.
- **F. Local search / repair.** [TODO explain heuristic] Guess a full answer, then patch violations. Look for near-miss answers with a few broken constraints.
- **G. Decompose.** [TODO explain heuristic] Solve the parts separately; misses interactions.
- **H. Guess / sample.** [TODO explain heuristic] Chance baseline; `SAMPLE-m` is "check a few cases" reasoning.
- **I. Strategy selection.** [TODO explain] Different items get different heuristics. This is modelled, not tested as a single heuristic.

---

## 6. Method: identifying heuristics from answers

### 6.1 Discriminating items

[TODO Keep items where families (and members within a family) disagree with each other and with ground truth. Choose by expected information gain.]

**Table 5. How often families disagree on the selected items.**

| | A | B1 | B4 | C | D | E | F | H |
|---|---|---|---|---|---|---|---|---|
| **A** | — | XX% | XX% | XX% | XX% | XX% | XX% | XX% |
| **B1** | | — | XX% | XX% | XX% | XX% | XX% | XX% |
| **B4** | | | — | XX% | XX% | XX% | XX% | XX% |
| [TODO] | | | | | | | | |

### 6.2 Likelihood model

**The readout is graded.** A model can partly use several heuristics, so every result is an estimated weight π_h with an interval, plus likelihood gains over the null and over the nearest competitor. None of it is a used / not-used verdict. "Disconfirming" a competitor means bounding its weight (e.g. π ≤ 0.05, upper 95%).

[TODO The noisy-execution likelihood P(y | h, x) ∝ exp(−λ · d(y, h(x))). A violation-profile term for infeasible answers: *which* constraints are broken. The mixture over members, plus a "none of the above" term, with feature-dependent weights π_h(φ(x)). EA, permutation baseline, lift, and the hierarchical model.]

### 6.3 Manipulation signatures and special item types

[TODO The manipulations: order reversal, re-theming, rule inversion, an irrelevant constraint, size, density, thinking budget, environment shifts (e.g. a planted polarity bias). Two special item types:]

- **Threshold knees:** [TODO compare the knee of the model's error-vs-density curve with each heuristic's simulated curve.]
- **Depth-stress items:** [TODO P-completeness gadgets force a seq heuristic to evaluate a circuit of chosen depth. Prediction: in direct-answer mode, agreement with seq heuristics falls with gadget depth, and recovers with CoT. This is a direct test of const vs seq.]

### 6.4 Validation: recovering planted heuristics

**Table 6. Recovery of planted mixtures from simulated models.** Simulated "models" mix heuristics with known weights. We report how precisely each weight is recovered, since the real readout is graded.

| Planted mixture | Noise | Recovered weights (mean) | Bias (max over components) | 95% CI width | Most confused pair |
|-----------------|-------|--------------------------|----------------------------|--------------|--------------------|
| 100% C1 `FIRST-FIT` | 10% slips | 0.XX / … | ±0.XX | 0.XX | C1 vs C2 `DSATUR` |
| 60% B4 `FIRST` · 30% B1 `UP-2` · 10% A `DENSITY` | 10% slips | 0.XX / 0.XX / 0.XX | ±0.XX | 0.XX | B4 `FIRST` vs `MATCH` |
| 50% C1 · 50% D `DPLL-b` | 10% slips | 0.XX / 0.XX | ±0.XX | 0.XX | — |
| Feature-dependent: C1 on dense items, B1 on sparse | 10% slips | π(φ) curve recovered? R² = 0.XX | ±0.XX | 0.XX | — |
| 20% each of five families | 10% slips | 0.XX each | ±0.XX | 0.XX | [TODO] |

### 6.5 Models and setup

**Table 7. Models evaluated.**

| Model | Provider / version | Open weights | Thinking budgets | Capability covariate |
|-------|--------------------|--------------|------------------|----------------------|
| [TODO] | | ✓ / ✗ | 0 / 1k / 4k / 16k | XXXX |

[TODO Prompts (Appendix C), answer formats, samples, pre-registration link.]

---

## 7. Behavioural evidence  *(Step 3)*

### 7.1 Which families explain the errors?

**Table 8. Error explanation by family** (pooled; items above n\*). For each family, the best-fitting member is shown.

| Family (best member) | EA | Chance baseline | Lift | Mixture weight π | 95% CI |
|----------------------|----|-----------------|------|------------------|--------|
| A Cue (`DENSITY`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| B1 Relax (`UP-k`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| B4 Restrict (`FIRST`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| C Constructive (`FIRST-FIT`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| D Truncated search (`DPLL-b`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| E Message passing (`BP-t`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| F Local search (`WALK-k`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H Guess (`SAMPLE-m`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| Nuisance (`NOISY-EXACT`) | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| *Unexplained* | — | — | — | 0.XX | |

### 7.2 Manipulation signatures

**Table 9. Predicted vs observed change.** ↑ / ↓ / = is the predicted direction for the model's error rate; observed is in pp.

| Manipulation | A | B1 | B4 | C1 | C4 | D | F | Observed | Best match |
|--------------|---|----|----|----|----|---|---|----------|------------|
| Order reversed | = | = | ↕ | ↕ | ↕↕ | = | = | ±XX pp | [TODO] |
| Re-themed | = | = | = | = | = | = | = | ±XX pp | [TODO] |
| Rule inverted | ↑ (A3) | = | = | = | = | = | = | +XX pp | [TODO] |
| Irrelevant constraint | ↑ | = | ↑ | ↑ | ↑ | = | = | +XX pp | [TODO] |
| Density ↑ (fixed n) | knee at cue | knee | — | knee ≈ 8/3 | — | ↑ smooth | knee | knee at XX | [TODO] |
| Depth-stress gadget depth ↑ | = | = | = | ↑ (no CoT) | ↑ | ↑ | ↑ | +XX pp | [TODO] |
| Thinking budget ×4 | = | ↓ (k grows) | = | = | = | ↓ (b grows) | ↓ | −XX pp | [TODO] |

### 7.3 Capability and thinking budget

**Table 10. How mixture weight shifts.**

| Family | Slope of π per 100 Elo | Δπ, budget 0 → 16k | Predicted | Matches? |
|--------|------------------------|---------------------|-----------|----------|
| A | −0.XX | −0.XX | ↓ | ✓ / ✗ |
| C | +0.XX | ±0.XX | [TODO] | |
| D | +0.XX | +0.XX | ↑ | |
| B4 | inverted U? | ±0.XX | [TODO] | |

### 7.4 Per-family results (one subsection per vertical; template in [verticals/TEMPLATE.md](verticals/TEMPLATE.md))

#### 7.4.x [Family letter + name]

- **The heuristic:** [TODO explain heuristic]
- **Eval design:** [TODO items that separate it from its nearest competitor; answer format; metric]
- **Result:** EA = XX% (lift +XX pp); signatures matched XX/XX; process measures [TODO]
- **Takeaway:** [TODO one sentence]

---

## 8. Mechanistic evidence  *(Step 4)*

### 8.1 Setup

[TODO Qwen3 4B/8B as primary model; Gemma; Llama. Transcoders, tuned lens, linear probes, linear interchange interventions. Level of analysis fixed in advance.]

### 8.2 Controls

**Table 11. Recovery on models with a known procedure.**

| Control | True procedure | Probe recovers state? | Intervention as predicted? | Random-init passes? (should be ✗) |
|---------|----------------|-----------------------|----------------------------|-----------------------------------|
| SIIT model | C1 `FIRST-FIT` | ✓ / ✗ (0.XX) | ✓ / ✗ (XX% IIA) | ✗ |
| ALTA-compiled | B1 `UP-k` | | | |
| Capacity toy, in capacity | exact | | | |
| Capacity toy, beyond capacity | degree cue (A2-like) | | | |

### 8.3 Is the family's state represented?

**Table 12. Linear probes.**

| Family | Variable probed | Layer / position | Probe acc. | Control acc. | Selectivity |
|--------|-----------------|------------------|------------|--------------|-------------|
| C | Current partial assignment / colour so far | L XX | XX% | XX% | +XX pp |
| B1 | k-th derived literal (layer grows with k?) | L XX | XX% | XX% | +XX pp |
| B4 / C4 | Surviving alternatives after each premise | L XX | XX% | XX% | +XX pp |
| E | Per-variable marginals after t rounds | L XX | XX% | XX% | +XX pp |

### 8.4 Is the state used?

**Table 13. Interventions: target vs nearest competitor vs random init.**

| Family | Intervention | Answer change toward prediction | Competitor's variable | Random init | Holds where the family is wrong? |
|--------|--------------|----------------------------------|-----------------------|-------------|----------------------------------|
| C | Patch partial assignment | +XX pp | +XX pp | +XX pp | ✓ / ✗ |
| B4 | Steer surviving alternative | +XX pp | +XX pp | +XX pp | ✓ / ✗ |
| [TODO] | | | | | |

### 8.5 One procedure or a bag of heuristics?

[TODO Feature classification and ablation by type.]

### 8.6 Thinking models: is the answer decided before thinking?

[TODO Pre-CoT probes: AUC 0.XX. Steering: +XX pp. Effect of suppressing backtracking on D vs C weights.]

---

## 9. Evidence summary  *(Step 5)*

**Table 14. The evidence table.** Every entry is a **scalar with an interval**. Heuristics can be partly used, so the readout is explanatory power, not a verdict. Weights sum to 1 with the unexplained mass. Phase 2 columns (interpretability) are filled only for families with behavioural weight. Model-level detail is in Appendix D.

| Family | Depth | Mixture weight π (95% CI) | ΔlogL vs null (per item) | ΔlogL vs nearest competitor | Lift on errors | Signature fit (weighted) | Trace-match share (faithfulness-weighted) | *Phase 2:* probe selectivity | *Phase 2:* intervention effect vs competitor |
|--------|-------|---------------------------|--------------------------|-----------------------------|----------------|--------------------------|-------------------------------------------|------------------------------|----------------------------------------------|
| A Cue | const | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | +XX pp | +XX pp |
| B1 Relax | const / seq | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | | |
| B4 Restrict | const / seq | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | | |
| C Constructive | const–seq | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | | |
| D Truncated search | seq | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | | |
| E Message passing | const | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | | |
| F Local search | seq | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | | |
| G Decompose | seq | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | | |
| H Guess / sample | const | 0.XX [0.XX, 0.XX] | +0.XX | +0.XX | +XX pp | 0.XX | XX% | | |
| Nuisance (noisy exact, perception) | — | 0.XX [0.XX, 0.XX] | +0.XX | — | +XX pp | 0.XX | — | — | — |
| *Unexplained* | — | 0.XX [0.XX, 0.XX] | — | — | — | — | — | — | — |

**Figure 4** — [TODO Stacked bars of π per model, ordered by capability, for direct-answer vs best-effort thinking. This shows how the weight shifts between families rather than a single winner.]

**What stands out.** [TODO Which families carry the most weight, how concentrated the weight is (e.g. the top family's π and the entropy of π), and how stable it is across models, domains, framings and thinking budget. Hopefully one family dominates; if the weight is spread, say so.]

---

## 10. Why this heuristic? A RASP-L account  *(Step 6)*

[TODO The RASP MDL principle (Zhou et al. 2024): transformers learn the shortest RASP-L program that fits the training set. For NP-hard tasks no short program fits exactly, so the learned program trades length against error (two-part MDL), under a depth constraint (bounded optimality, Russell & Subramanian). const-depth programs are available in one forward pass; seq ones need CoT.

Training-as-adaptation (F3): choosing heuristics by adaptation is intractable in general (Rich et al. 2019). SGD settles for a short program. Rival complexity measures with lower-bound theory: pBT width, LOCAL rounds, polynomial degree.]

**Table 15. Programs per family.** Lengths and the prediction were written down before the evals.

| Family (member) | RASP-L length | Depth (layers) | Depth class | Accuracy on a training-like distribution | On the frontier? | Predicted rank | Observed rank |
|-----------------|---------------|----------------|-------------|------------------------------------------|------------------|----------------|---------------|
| A (`DENSITY`) | XX | X | const | XX% | ✓ / ✗ | X | X |
| B1 (`UP-2`) | XX | X | const | XX% | | X | X |
| B4 (`FIRST`) | XX | X | const | XX% | | X | X |
| C (`FIRST-FIT`) | XX | X | seq | XX% | | X | X |
| E (`BP-2`) | XX | X | const | XX% | | X | X |
| [TODO] | | | | | | | |

**Figure 3** — [TODO Accuracy vs program length, with the frontier and the standout marked.]

### 10.1 Toy-model test

**Table 16. Small transformers trained from scratch: which program do they learn?**

| Training set (size / diversity) | Depth | Decompiles to | Matches family | Accuracy in / out of distribution |
|---------------------------------|-------|---------------|----------------|-----------------------------------|
| XXk / low | X | [TODO] | [TODO] | XX% / XX% |
| XXk / high | X | [TODO] | [TODO] | XX% / XX% |
| XXk / low, with CoT | X | [TODO] | [TODO] | XX% / XX% |

---

## 11. Discussion

- **What it means:** [TODO]
- **Human-likeness:** [TODO connection to v1 (ETR is family B4/C4). Inverted U with capability?]
- **Practical implications:** [TODO]
- **Limitations:**
  - [TODO open-model interpretability transfer];
  - [TODO taxonomy completeness; unexplained mass XX%];
  - [TODO API drift].

## 12. Conclusion

[TODO]

---

## Appendices

- **A. Item generators and hardness measures:** [TODO]
- **B. The heuristic zoo: definitions, reference implementations, depth arguments (P-completeness citations):** [TODO]
- **C. Prompts:** [TODO]
- **D. Full results:** [TODO]
- **E. Pre-registration:** [TODO]
- **F. RASP-L programs:** [TODO]
- **G. Reproducibility:** [TODO]
