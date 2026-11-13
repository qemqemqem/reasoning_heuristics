# [TODO Title] — working: *Greedy by Default? Identifying the Heuristics Language Models Use on NP-Hard Problems*

> **Skeleton.** Every number below is a stand-in (`XX`, `+XX pp`, `0.XX`) showing the *kind* of metric we will report. `[TODO …]` marks text to write.
>
> - The heuristic classes are provisional until the taxonomy in Step 2 is final; see [DESIGN.md](DESIGN.md) and [LITERATURE.md](LITERATURE.md).
> - Section ↔ plan: §3 = Step 1 (real problems are NP-hard), §5 = Step 2 (heuristic classes), §7 = Step 3 (evals), §8 = Step 4 (interpretability), §9 = Step 5 (the table), §10 = Step 6 (RASP-L explanation).

**Authors:** [TODO]

---

## Abstract

[TODO 150–200 words.] Draft shape:

> Many reasoning problems people bring to language models are NP-hard, yet models answer them with bounded computation, so on hard instances they must rely on heuristics. We ask *which* heuristics. We model real-world tasks as [TODO chosen problem models] and enumerate [XX] classes of heuristics for NP-hard problems. For each class we design discriminating evaluations and mechanistic tests. Across [XX] models and [XX,XXX] instances, [TODO standout heuristic class] explains [XX]% of errors above the budget line ([+XX] pp over chance), and its internal state is linearly decodable and causally used in [TODO open models]. We explain this with a RASP-L account: [TODO one-sentence explanation, e.g. "it is the shortest program on the accuracy–length frontier available within a single forward pass"].

---

## 1. Introduction

**Opening.** [TODO Real problems are hard: scheduling, planning, configuring, checking whether a conclusion follows.]

**The puzzle.** [TODO Models answer in a bounded number of tokens, far less than exhaustive search would need. On instances beyond that budget, they must be using an incomplete procedure. Which one?]

**Why it matters.** [TODO Predicting failures; designing benchmarks; deciding when to give a model tools or more thinking budget. Error composition matters more than error rate.]

**What we do.** [TODO One paragraph on the pipeline: model real problems → enumerate heuristic classes → evals per class → interpretability per class → evidence table → RASP-L explanation.]

**Contributions.**

1. [TODO] A comparison of formal models of real-world reasoning problems, and the case for [TODO chosen models].
2. [TODO] A taxonomy of [XX] heuristic classes for NP-hard problems, each with a reference implementation, a predicted error signature, and an expressibility class: one forward pass (C) or sequential (S).
3. [TODO] An identification method that tells competing heuristics apart from instance-level answers, validated by recovering planted heuristics.
4. [TODO] Behavioural and mechanistic evidence for each class across [XX] models. The standout is [TODO class].
5. [TODO] A RASP-L account of why that class wins, with predictions written down before the evals.

**Figure 1** — [TODO The evidence table as a heatmap: heuristic classes × evidence types, with the standout row highlighted.]

---

## 2. Related work

[TODO One paragraph each.]

- **LLMs on NP-hard and combinatorial problems:** [TODO EHOP, GraphArena, Hazra et al. 2025, NPPC, Zhang et al. 2026.]
- **Scaling of reasoning effort with problem complexity:** [TODO Shojaee et al. 2025 and replies, Rameshkumar et al. 2025.]
- **Heuristics and biases in LLMs; comparison with human reasoning:** [TODO Koralus & Wang-Maścianica 2023, Richardson et al. 2025, Hagendorff et al. 2023, Eisape et al. 2024.]
- **Strategy identification in cognitive science and decision research:** [TODO Bröder & Schiffer 2003, Glöckner 2009, Davis-Stober & Brown 2011, Myung & Pitt 2009.]
- **Interpretability of reasoning and search:** [TODO Hong et al. 2025, Nikankin et al. 2025, AlgoTrace, Ye et al. 2025, Sutter et al. 2025.]
- **RASP, RASP-L and what transformers learn:** [TODO Weiss et al. 2021, Zhou et al. 2024, Huang et al. 2025/2026, ALTA.]

---

## 3. Real-world problems are well modelled by NP-hard problems  *(Step 1)*

### 3.1 Candidate models

[TODO Introduce the candidate formal models and the criteria for comparing them.]

**Table 1. Candidate formal models of real-world reasoning problems.** Coverage = share of a sample of real tasks (§3.2) that the model expresses faithfully.

| Model | Example real-world tasks | Complexity (decision) | Coverage of task sample | Instance fidelity | Generator / solver available | Chosen |
|-------|--------------------------|-----------------------|-------------------------|-------------------|------------------------------|--------|
| Propositional / monadic logic (entailment) | Policy and rule checking, "does this follow?" | coNP-complete | XX% | High / Med / Low | ✓ | [TODO] |
| Boolean satisfiability / CSP | Configuration, puzzles, verification | NP-complete | XX% | — | ✓ | [TODO] |
| Graph coloring | Timetabling, allocation | NP-complete | XX% | — | ✓ | [TODO] |
| Knapsack / subset selection | Budgeting, packing | NP-hard (weakly) | XX% | — | ✓ | [TODO] |
| TSP / routing | Errands, delivery | NP-hard | XX% | — | ✓ | [TODO] |
| Scheduling | Shifts, project plans | NP-hard | XX% | — | ✓ | [TODO] |
| Classical planning | Multi-step tasks, agents | NP-complete (bounded) / PSPACE | XX% | — | ✓ | [TODO] |
| Probabilistic inference / abduction | Diagnosis, explanation | #P-hard / NP-hard | XX% | — | partial | [TODO] |

### 3.2 How we chose

[TODO Describe the task sample (e.g. XX tasks drawn from [TODO source: user requests, benchmarks, occupational task lists]). Explain how each task was mapped to a model, with inter-rater agreement κ = 0.XX.]

### 3.3 Our instances are hard, and hard in the right way

[TODO Hardness on three axes: solver effort; proof hardness; heuristic-relative hardness (how many zoo heuristics fail on the item).]

**Table 2. Hardness of the item sets.**

| Domain | n (vars / nodes / items) | Solver nodes (median) | % proof-hard | % items where ≥1 heuristic fails | % items where heuristics disagree |
|--------|--------------------------|-----------------------|--------------|----------------------------------|-----------------------------------|
| Entailment | XX–XX | XX | XX% | XX% | XX% |
| 3-SAT (α ≈ 4.26) | XX–XX | XX | XX% | XX% | XX% |
| Coloring | XX–XX | XX | — | XX% | XX% |
| [TODO] | | | | | |

---

## 4. From hardness to heuristics: the budget line

[TODO The argument. A forward pass is in TC⁰. Chain of thought with T tokens buys at most T sequential steps. Exact search needs on the order of 2^Θ(n) steps on hard instances, and Pan et al. 2025 show exact search *is* expressible given enough tokens. So for each model and budget there is a size n\* above which the answer must come from an incomplete procedure.]

**Figure 2** — [TODO Accuracy vs instance size per model, with n\* marked. Below n\*: near-exact; above n\*: falls to heuristic level.]

**Table 3. Budget line per model.**

| Model | Thinking budget | Estimated n\* | Accuracy below n\* | Accuracy above n\* | Median tokens used above n\* | % runs hitting the cap |
|-------|-----------------|---------------|--------------------|--------------------|------------------------------|------------------------|
| [TODO model A] | 0 | XX | XX% | XX% | XX | XX% |
| [TODO model A] | 4k | XX | XX% | XX% | XX | XX% |
| [TODO model B] | 0 | XX | XX% | XX% | XX | XX% |

---

## 5. A taxonomy of heuristics for NP-hard problems  *(Step 2)*

[TODO Introduce the taxonomy and where it comes from: e.g. Pearl's view of heuristics as exact solutions to relaxed problems, plus the classical algorithmic families. Explain the expressibility split: **C** = possible in one forward pass; **S** = needs sequential steps, i.e. chain of thought.]

**Table 4. Heuristic classes (provisional).** RASP-L length is measured under the pre-registered measure.

| # | Class | Defining idea | Example members (per domain) | Predicted error signature | C / S | RASP-L length |
|---|-------|---------------|------------------------------|---------------------------|-------|---------------|
| H1 | Surface / statistical cues | Answer from global statistics of the input, not its structure | `DENSITY`, `ALWAYS-SAT`, `FREQ`, `PRIMACY` | Commission; wrong on the minority class; insensitive to structure | C | XX |
| H2 | Constructive greedy | One pass, commit to the locally best choice, never revise | `GREEDY`, `FIRST-FIT`, `NN`, `RATIO` | Feasible but suboptimal, or false "impossible"; order-sensitive | S | XX |
| H3 | Propagation (sound, incomplete) | Derive only what follows locally, k steps deep | `UP-k`, `UP+GUESS` | Omission only; never a false conclusion | C (small k) / S | XX |
| H4 | Truncated exact search | Complete search with a step budget, then a default | `DPLL-b` | Exact below budget; default answer above | S | XX |
| H5 | Local search / repair | Start from a candidate, fix violations | `WALK-k`, `2OPT-k` | Near-feasible; stuck in local optima | S | XX |
| H6 | Relaxation | Solve an easier problem with a constraint dropped | `HALLUC-CONSTRAINT`, [TODO] | Answers a different instance; infeasible | C / S | XX |
| H7 | Alternative filtering (cognitive) | Keep a few alternatives; filter by matching new information | `ETR`, `MM`, `MATCH` | Illusory inferences; order effects | S? | XX |
| H8 | Retrieval / template transfer | Map to a familiar problem and use its standard solution | `TEXTBOOK-TRANSFER` | Fails on inverted or novel variants | — | — |
| H0 | Noisy exact (control) | The exact algorithm with random slips | `NOISY-EXACT` | Errors grow smoothly with size; no structure | S | XX |

### 5.1–5.9 The classes

For each class, one subsection:

- **H1 Surface / statistical cues:** [TODO explain heuristic] · [TODO formal definition] · [TODO members per domain] · [TODO why C/S]
- **H2 Constructive greedy:** [TODO explain heuristic] · …
- **H3 Propagation:** [TODO explain heuristic] · …
- **H4 Truncated exact search:** [TODO explain heuristic] · …
- **H5 Local search / repair:** [TODO explain heuristic] · …
- **H6 Relaxation:** [TODO explain heuristic] · …
- **H7 Alternative filtering:** [TODO explain heuristic; connect to ETR and mental models] · …
- **H8 Retrieval / template transfer:** [TODO explain heuristic] · …
- **H0 Noisy exact:** [TODO explain why it is the null] · …

---

## 6. Method: identifying heuristics from answers

### 6.1 Discriminating items

[TODO Generate a pool, then keep the items where the heuristics disagree with each other and with ground truth. Choose them by expected information gain.]

**Table 5. How often classes disagree on the selected items** (share of items where the row and column classes give different answers).

| | H1 | H2 | H3 | H4 | H5 | H6 | H7 |
|---|---|---|---|---|---|---|---|
| **H1** | — | XX% | XX% | XX% | XX% | XX% | XX% |
| **H2** | | — | XX% | XX% | XX% | XX% | XX% |
| **H3** | | | — | XX% | XX% | XX% | XX% |
| [TODO] | | | | | | | |

### 6.2 Likelihood model

[TODO The noisy-execution likelihood P(y | h, x) ∝ exp(−λ · d(y, h(x))) and the mixture over classes plus a "none of the above" term. Error agreement EA, the permutation baseline, lift, and the hierarchical model over items and models.]

### 6.3 Manipulation signatures

[TODO The manipulations: order reversal, re-theming, rule inversion, an irrelevant constraint, size, density, thinking budget. Give the predicted direction of change for each class.]

### 6.4 Validation: recovering planted heuristics

**Table 6. Recovery of planted heuristics from simulated models.**

| Planted class | Planted noise | Recovered as top class | Mean posterior on true class | Most-confused-with |
|---------------|---------------|------------------------|------------------------------|--------------------|
| H1 | 10% slips | XX% | 0.XX | H[TODO] |
| H2 | 10% slips | XX% | 0.XX | H[TODO] |
| H2 + H3 mixture (50/50) | 10% slips | XX% (both) | 0.XX / 0.XX | — |
| [TODO] | | | | |

### 6.5 Models and setup

**Table 7. Models evaluated.**

| Model | Provider / version | Open weights | Thinking budgets | Capability covariate (Elo / compute) |
|-------|--------------------|--------------|------------------|--------------------------------------|
| [TODO] | | ✓ / ✗ | 0 / 1k / 4k / 16k | XXXX |

[TODO Prompts (Appendix C), answer formats, number of samples, pre-registration link.]

---

## 7. Behavioural evidence  *(Step 3)*

### 7.1 Which classes explain the errors?

**Table 8. Error explanation by heuristic class** (pooled over models, items above n\*).

| Class | Error agreement EA | Chance baseline | Lift | Mixture weight π | 95% CI on π |
|-------|--------------------|-----------------|------|------------------|-------------|
| H1 Surface cues | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H2 Constructive greedy | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H3 Propagation | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H4 Truncated search | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H5 Local search | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H6 Relaxation | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H7 Alternative filtering | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H8 Retrieval | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| H0 Noisy exact | XX% | XX% | +XX pp | 0.XX | [0.XX, 0.XX] |
| *Unexplained* | — | — | — | 0.XX | |

### 7.2 Manipulation signatures

**Table 9. Predicted vs observed change under each manipulation.** ↑ / ↓ / = is the predicted direction; the observed change is in pp.

| Manipulation | H1 pred. | H2 pred. | H3 pred. | H7 pred. | Observed (pooled) | Best-matching class |
|--------------|----------|----------|----------|----------|-------------------|---------------------|
| Order reversed | = | ↓ | = | ↓ | −XX pp | H[TODO] |
| Re-themed | = | = | = | = | ±XX pp | H[TODO] |
| Rule inverted | = | = | = | = | −XX pp | H[TODO] |
| Irrelevant constraint added | ↓ | = | = | ↓ | −XX pp | H[TODO] |
| Density ↑ (at fixed n) | ↓↓ | ↓ | ↓ | ↓ | −XX pp | H[TODO] |
| Thinking budget ×4 | = | = | ↑ | ↑ | +XX pp | H[TODO] |

### 7.3 Capability and thinking budget

**Table 10. How mixture weight shifts with capability and thinking budget.**

| Class | Slope of π vs capability (per 100 Elo) | Δπ, budget 0 → 16k | Direction predicted (H3, H6) | Matches? |
|-------|-----------------------------------------|---------------------|------------------------------|----------|
| H1 | −0.XX | −0.XX | ↓ | ✓ / ✗ |
| H2 | +0.XX | ±0.XX | [TODO] | |
| H4 | +0.XX | +0.XX | ↑ | |
| H7 | +0.XX → −0.XX (inverted U?) | ±0.XX | [TODO] | |

### 7.4 Per-class results (one subsection per vertical)

For each class (template in [verticals/TEMPLATE.md](verticals/TEMPLATE.md)):

#### 7.4.x H[N] [class name]

- **The heuristic:** [TODO explain heuristic]
- **Eval design:** [TODO eval: items that separate it from its nearest competitor; answer format; metric]
- **Result:** EA = XX% (lift +XX pp); signatures matched XX/XX; process measures [TODO]
- **Takeaway:** [TODO one sentence]

---

## 8. Mechanistic evidence  *(Step 4)*

### 8.1 Setup

[TODO Open models (Qwen3 4B/8B primary; Gemma; Llama), tools (transcoders, tuned lens, linear probes, linear interchange interventions), and the level of analysis chosen in advance.]

### 8.2 Controls: can the pipeline find a known heuristic?

**Table 11. Recovery on models with a known procedure.**

| Control model | True procedure | Probe recovers state? | Intervention moves answer as predicted? | Random-init passes? (should be ✗) |
|---------------|----------------|-----------------------|-----------------------------------------|-----------------------------------|
| SIIT model (InterpBench-style) | H2 greedy | ✓ / ✗ (selectivity 0.XX) | ✓ / ✗ (XX% IIA) | ✗ |
| ALTA-compiled | H3 propagation | | | |
| Capacity toy (in-capacity) | exact algorithm | | | |
| Capacity toy (beyond capacity) | degree heuristic | | | |

### 8.3 Is the heuristic's state represented?

**Table 12. Linear probes for class-specific state.**

| Class | Variable probed | Best layer / position | Probe accuracy | Control-task accuracy | Selectivity |
|-------|-----------------|-----------------------|----------------|-----------------------|-------------|
| H2 | Current partial assignment | L XX / last token | XX% | XX% | +XX pp |
| H3 | k-th derived literal | L XX (grows with k?) | XX% | XX% | +XX pp |
| H7 | Surviving alternatives | L XX | XX% | XX% | +XX pp |
| [TODO] | | | | | |

### 8.4 Is the state used?

**Table 13. Interventions: target class vs nearest competitor vs random init.**

| Class | Intervention | Answer change toward class prediction | Same intervention, competitor's variable | Random-init model | Holds on items where the class is wrong? |
|-------|--------------|----------------------------------------|------------------------------------------|-------------------|------------------------------------------|
| H2 | Patch partial assignment | +XX pp | +XX pp | +XX pp | ✓ / ✗ |
| H7 | Steer surviving alternative | +XX pp | +XX pp | +XX pp | ✓ / ✗ |
| [TODO] | | | | | |

### 8.5 One procedure or a bag of heuristics?

[TODO Results of feature classification and ablation by type. Does behaviour matching class H come from a single state variable, or from many shallow cue features?]

### 8.6 Thinking models: is the answer decided before thinking?

[TODO Pre-chain-of-thought probes: AUC 0.XX. Steering effect: +XX pp. What happens to the mixture weights when backtracking is suppressed.]

---

## 9. Evidence summary  *(Step 5)*

**Table 14. The evidence table.** ✓ = supported, ~ = mixed, ✗ = against, — = not tested. The thresholds for each mark are pre-registered (Appendix E).

| Class | Behavioural lift | Mixture weight | Signatures matched | Process measures | Probe selectivity | Intervention > competitor | Control recovered | Verdict |
|-------|------------------|----------------|--------------------|------------------|-------------------|---------------------------|-------------------|---------|
| H1 Surface cues | +XX pp ✓ | 0.XX ~ | X/6 | ~ | +XX pp ✗ | ✗ | ✓ | [TODO] |
| H2 Constructive greedy | +XX pp | 0.XX | X/6 | | +XX pp | | | [TODO] |
| H3 Propagation | +XX pp | 0.XX | X/6 | | +XX pp | | | [TODO] |
| H4 Truncated search | +XX pp | 0.XX | X/6 | | — | — | | [TODO] |
| H5 Local search | +XX pp | 0.XX | X/6 | | — | — | | [TODO] |
| H6 Relaxation | +XX pp | 0.XX | X/6 | | | | | [TODO] |
| H7 Alternative filtering | +XX pp | 0.XX | X/6 | | +XX pp | | | [TODO] |
| H8 Retrieval | +XX pp | 0.XX | X/6 | | — | — | — | [TODO] |
| H0 Noisy exact | +XX pp | 0.XX | X/6 | | — | — | — | [TODO] |

**The standout.** [TODO Which class stands out, how strongly, and how consistently across models, domains and framings.]

---

## 10. Why this heuristic? A RASP-L account  *(Step 6)*

[TODO The RASP MDL principle (Zhou et al. 2024): transformers learn the shortest RASP-L program that fits the training set. For NP-hard tasks no short program fits exactly, so the learned program balances length against training error (a two-part MDL objective). Class-C programs are available in a single forward pass; class-S programs only with chain of thought.]

**Table 15. RASP-L programs for each class.** Lengths and the prediction were written down before the evals.

| Class | Program length (primitives) | Depth (layers) | C / S | Accuracy on a training-like distribution | On the accuracy–length frontier? | Predicted rank | Observed rank (Table 14) |
|-------|-----------------------------|----------------|-------|------------------------------------------|----------------------------------|----------------|--------------------------|
| H1 | XX | X | C | XX% | ✓ / ✗ | X | X |
| H2 | XX | X | S | XX% | | X | X |
| H3 (k = 2) | XX | X | C | XX% | | X | X |
| H7 | XX | X | S | XX% | | X | X |
| [TODO] | | | | | | | |

**Figure 3** — [TODO Accuracy vs program length for all classes, showing the frontier. The standout should sit on the frontier at the budget the model has.]

### 10.1 Toy-model test

**Table 16. Small transformers trained from scratch: which program do they learn?**

| Training set (size / diversity) | Depth | Decompiles to | Matches class | Accuracy in / out of distribution |
|---------------------------------|-------|---------------|---------------|-----------------------------------|
| XXk items / low | X | [TODO] | H[TODO] | XX% / XX% |
| XXk items / high | X | [TODO] | H[TODO] | XX% / XX% |
| XXk items / low, with CoT | X | [TODO] | H[TODO] | XX% / XX% |

[TODO Does the learned program move along the frontier as data grows (prediction 2), and toward class S with chain of thought (prediction 3)?]

---

## 11. Discussion

- **What it means:** [TODO what the standout class implies about how models reason under hardness.]
- **Human-likeness:** [TODO connection to v1 (ETR). Does H7 behave like human reasoning, and does that change with capability (an inverted U)?]
- **Practical implications:** [TODO where to expect failures; when to add thinking budget or tools; benchmark design.]
- **Limitations:**
  - [TODO open-model interpretability may not transfer to closed models];
  - [TODO the taxonomy may be incomplete; unexplained mass XX%];
  - [TODO API drift].

## 12. Conclusion

[TODO One paragraph.]

---

## Appendices

- **A. Item generators and hardness measures:** [TODO]
- **B. The heuristic zoo: definitions and reference implementations:** [TODO]
- **C. Prompts (exact text):** [TODO]
- **D. Full per-model, per-domain results:** [TODO]
- **E. Pre-registration: hypotheses, thresholds, exclusions:** [TODO]
- **F. RASP-L programs:** [TODO]
- **G. Reproducibility: one command per table and figure:** [TODO]
