# Heuristics Under Hardness — Design Document

*How do language models answer problems they cannot solve exactly?*

- **Status:** Draft v0.2, 2026-11-13. Revised after the literature review in [LITERATURE.md](LITERATURE.md).
- **Owner:** Andrew Keenan Richardson
- **Follows on from:** the 2025 ETR study ([arXiv 2506.11128](https://arxiv.org/abs/2506.11128), ICLR 2026). Its code stays frozen in [`Oxford-HAI-Lab/etr_case_generator`](https://github.com/Oxford-HAI-Lab/etr_case_generator) (see §6).

---

## 1. Summary

Many reasoning problems people care about are NP-hard or coNP-hard in general. A language model does a bounded amount of computation per token, and usually answers in far fewer tokens than exhaustive search would take. On instances whose search exceeds its token budget, it cannot be running an exact algorithm. Whatever it runs there is a **heuristic**: a cheap procedure that is right on many instances and wrong on others in a characteristic way.

This project asks **which heuristics**. We will:

1. Build a zoo of candidate heuristics. Each one is a precise procedure that gives a predicted answer, or a distribution over answers, on every instance.
2. Generate instances on which the candidates disagree.
3. Measure which candidates explain models' answers, especially their errors.
4. Look for the winning heuristics inside open-weight models.
5. Situate them in RASP-L.

**Where this sits (see [LITERATURE.md](LITERATURE.md)).** Several things are already established:

- **LLMs fall back on greedy-looking procedures on NP-hard problems**, inferred from accuracy or by reading traces (EHOP; GraphArena; Hazra et al. 2025; AlgoTrace).
- **Accuracy collapses beyond a size threshold**, and thinking tokens first rise and then fall (Shojaee et al. 2025 and others).
- **Zhou et al. (2024) proposed that transformers learn the shortest RASP-L program that fits the training set.**

What is missing is **identification**: deciding between *competing* heuristics from instance-level answers, using chance baselines, manipulation signatures and recovery tests, and then checking the winner mechanistically. That is the contribution. On the theory side, we extend the shortest-program idea to the regime where *no* short program fits exactly, which is where heuristics live.

The 2025 ETR study is a special case of this design: one heuristic (ETR's default inference procedure), tested on items chosen so that the heuristic errs. The idea worth keeping is **error composition**: what a model's wrong answers look like says more about its procedure than its accuracy does.

---

## 2. Objectives at a glance

| # | Objective | Kind of evidence | Role in the paper |
|---|-----------|------------------|-------------------|
| O1 | Many real-world problems are effectively NP-hard | Argument + survey; measured hardness of our items, including hardness *relative to the heuristic zoo* | Motivation |
| O2 | Bounded compute forces heuristics above a budget line | Complexity argument + compute-vs-accuracy measurements centred on the budget line | Premise (largely established; we locate the line per model) |
| O3 | Investigate many candidate heuristics and see which we find evidence for | Identification method (below) | **Core contribution** |
| O4 | Evidence from evals | Behavioural experiments on API and open models | Evidence for O3 |
| O5 | Evidence from mechanistic interpretability | Probes, interventions and circuit analysis on open models, with competing-heuristic controls | Evidence for O3 |
| O6 | Continue the RASP-L work and situate the heuristics there | Imperfect-fit MDL extension of the RASP MDL principle; toy-model training; decompilation | Theory for O3 |

---

## 3. Objectives in detail

### O1. Many real-world problems are effectively NP-hard

**Claim, stated carefully.** The computational problems underneath many everyday and professional reasoning tasks are NP-hard or coNP-hard in the worst case. Realistic instance distributions contain a tail of hard instances.

| Task | Underlying problem | Complexity |
|------|--------------------|------------|
| Timetabling, shift rostering, job-shop scheduling | Scheduling | NP-hard |
| Route planning with stops | TSP / vehicle routing | NP-hard |
| Configuring a product with constraints | Constraint satisfaction | NP-complete |
| Register allocation; rooms for clashing meetings | Graph coloring | NP-complete |
| "Does this conclusion follow from these rules?" | Propositional entailment | coNP-complete |
| Same, with properties of objects | Monadic first-order logic | NEXPTIME-complete (satisfiability) |
| Bounded-length planning | Classical planning | NP-complete (PSPACE without the bound) |
| Puzzles: Sudoku (n²×n²), Minesweeper consistency | CSP | NP-complete |

**What we'll do.**

1. Write a short survey and argument section mapping tasks to formal problems.
2. For every domain, measure each item's hardness on three axes:
   - **Solver hardness:** solver node counts and runtime, backbone size, and distance from the phase transition, with density and formula length controlled jointly.
   - **Proof hardness:** for unsatisfiable items, proof-hard versus proof-easy families at matched density.
   - **Heuristic-relative hardness:** how many zoo heuristics get the item wrong, and a greedy score.

   Then report which axis predicts model errors. Solver hardness alone may not: Verma (2026) finds no accuracy gap between proof-hard and proof-easy formulas at matched density. This result links O1 to O3.

**Caveats to state up front.**

- **NP-hardness is a worst-case statement.** Industrial SAT instances are solved every day because they have structure, such as backdoors (Williams, Gomes & Selman 2003). Most real-world graph and proof instances fall within reasoning models' current success range, with a long tail outside it (Rameshkumar et al. 2025).
- **The "heuristics don't escape intractability" objection** (van Rooij, Wright & Wareham 2012). We answer it directly. In our framing a heuristic is a *different, tractable function* that agrees with the target on many inputs, and identifying *which* function is exactly the computational-level revision they ask for.

O1 is motivation: it should take a page, not a chapter.

### O2. Bounded computation forces heuristics above a budget line

**Argument.**

1. **Per forward pass.** A fixed transformer forward pass with log-precision arithmetic is in log-space-uniform TC⁰ (Merrill & Sabharwal 2023). With constant precision and no chain of thought it is in AC⁰ (Li et al. 2024).
   - Answering directly (T = O(1) tokens, as under v1's "answer immediately" instruction) therefore rules out even some problems in P, assuming TC⁰ ≠ NC¹. Feng et al. (2023) show this for arithmetic and linear equations.
   - Padding tokens alone don't escape TC⁰ (Merrill & Sabharwal 2025), so filler isn't thinking.
2. **With chain of thought.** Polynomially many CoT steps give exactly P, under a generalized pre-norm assumption (Merrill & Sabharwal 2024). Even some problems in P need CoT length at least linear in input size (Amiri et al. 2025).
3. **The converse.** A fixed transformer *can* decide 3-SAT exactly by running backtracking search in its chain of thought, with exponentially many steps in the worst case (Pan et al. 2025).

   So the operative quantity is the **token budget relative to the size of the search** (≈ 2^Θ(n) for hard SAT instances), not "polynomial vs. exponential" in the abstract:
   - **Below the budget line**, exact search is possible and is observed: DeepSeek-R1's traces show DPLL-style search on small instances (Hazra et al. 2025).
   - **Above it**, the answer must come from an incomplete procedure.
4. **Worst case vs. our distribution.** P ≠ NP says some instance is answered wrongly, not that many items *from our distribution* are. That part is measured, not assumed.

**What's established and what we add.** O2(a), accuracy falling with size, and O2(b), thinking tokens rising and then falling, are already published several times (Shojaee et al. 2025; Estermann & Wattenhofer 2025; NPPC; Rameshkumar et al. 2025). We replicate them only where needed to locate each model's budget line. Our addition is **O2(c): errors above the budget line are structured**, and they are structured in a way the zoo can name. This is supported qualitatively already (GraphArena; Heyman & Zylberberg 2025; Hazra et al. 2025).

**Design rule.** For each model and thinking budget, estimate the instance size *n\** at which exhaustive search would exceed the budget, and centre the size sweep on *n\**.

**Rules.**

- Measure "quickly" in tokens and FLOPs, never wall-clock time.
- Disable tool use.
- Keep answer formats **small and polynomial in size**, so output-length limits can't masquerade as reasoning failure. This was the Tower-of-Hanoi lesson from Shojaee et al. vs Lawsen.
- Check every item is solvable, or keep matched SAT/UNSAT pairs (Zhang, Chen & Chen 2026).
- Treat runs that hit the budget cap as **censored** in token-vs-size models.
- Score "declared impossible / too complex" as its own category, separate from refusal and from UNSAT.
- Check small instances for memorisation.

### O3. Identify the heuristics (core)

**Definitions.**

- An instance *x* has ground truth *g(x)* from an exact solver.
- A **heuristic** *h* maps *x* to an answer *h(x)*, or to a distribution over answers, within a stated compute budget.
- Each heuristic has an **expressibility class**:
  - **C:** computable in a constant number of transformer layers, i.e. a constant-depth RASP-L program. Available in direct-answer mode.
  - **S:** sequential. It needs many steps, so it is available only with chain of thought, or in truncated form.
- *y* is a model's response.
- **Evidence that model *m* uses *h*** has two parts:
  - *y* agrees with *h* on instances where *h* is wrong, more than chance and more than competing heuristics do; and
  - under manipulations, the answer moves the way *h* predicts.

**Initial heuristic zoo.** These are candidates; adding and removing entries is expected.

| Domain | ID | Heuristic | Class | How it errs |
|--------|----|-----------|-------|-------------|
| Entailment | `ETR` | ETR default procedure (PyETR): Update filters alternatives by issue matching | S? | Commission (illusory inferences) |
| Entailment | `MM` | Mental models, principle of truth (cf. mReasoner) | S? | Commission and omission |
| Entailment | `MATCH` | Take the disjunct of an earlier premise that shares atoms with a later categorical premise | C | Commission |
| Entailment | `FIRST` | Read each "either A or B" as A | C | Commission |
| Entailment | `UP-k` | k rounds of unit propagation; report derived literals | C for small k | Omission only (sound) |
| Entailment | `FREQ` | Conclude the most frequent literals | C | Commission |
| Entailment | `ATMOSPHERE` | Mood or polarity of the premises sets the conclusion's mood | C | Commission |
| Entailment | `ECHO` / `NONE` | Restate a premise / say nothing follows | C | Uninformative but valid |
| SAT / CSP | `ALWAYS-SAT`, `DENSITY` | Answer SAT; or decide SAT/UNSAT from the clause/variable ratio or the length | C | Wrong on the minority class |
| SAT / CSP | `POLARITY`, `PURE-LITERAL`, `MOMS` | Literal-statistics assignments | C | Wrong assignment |
| SAT / CSP | `GREEDY` | Assign in mention order, maximise clauses satisfied so far, never backtrack | S | Wrong assignment, false UNSAT |
| SAT / CSP | `UP+GUESS` | Unit propagation, then a default fill | S | Wrong assignment |
| SAT / CSP | `DPLL-b` | Complete search cut off after b decisions, then a default answer | S | Wrong above budget; links exact search to heuristics |
| SAT / CSP | `WALK-k` | WalkSAT with k flips | S | Wrong assignment |
| Coloring | `FIRST-FIT`, `RANDOM-ORDER-FIRST-FIT`, `DSATUR`, `LARGEST-FIRST` | Greedy colorings | S | Too many colors / conflicts |
| Knapsack | `RATIO`, `VALUE`, `LARGEST-FIT` | Greedy selection rules | S | Suboptimal or infeasible |
| TSP | `NN-from-0`, `NN-best-start`, `INPUT-ORDER`, `GREEDY-EDGE`, `FARTHEST-INSERTION`, `2OPT-k` | Construction and local search | S | Suboptimal tours |
| Any | `PRIMACY`, `RECENCY`, `LENGTH-PRIOR` | Surface cues | C | Order and size effects |
| Any | `TEXTBOOK-TRANSFER` | Solve the textbook version of a re-themed or rule-inverted item | — | Wrong on inverted items (EHOP) |
| Any | `NOISY-EXACT` | Exact algorithm with a per-step slip probability | S | Errors grow with size |
| Any | `HALLUC-CONSTRAINT` | Adds or drops a constraint (e.g. a phantom edge), then solves | — | Answers a different instance |

`NOISY-EXACT` and `HALLUC-CONSTRAINT` are there so that execution and perception errors aren't credited to procedural heuristics. Noisy execution of an exact algorithm also predicts accuracy falling with size (Sinha et al. 2025). "Approximate retrieval" is partly captured by `TEXTBOOK-TRANSFER`; the rest shows up as unexplained mass in the mixture model.

**Identification method.**

1. **Discriminating items.**
   - Select items where the candidates disagree **with each other**, not only with *g(x)*. Prior work (e.g. EHOP) separates greedy from optimal; we separate greedy from greedy.
   - Choose items by expected information gain between heuristics: optimal design for model discrimination (Myung & Pitt 2009; Cavagnaro et al. 2010).
2. **Likelihoods, not exact matches.** LLM answers are often infeasible or near-misses (GraphArena; Hazra et al. 2025), so exact agreement `1[y = h(x)]` would leave most errors unexplained. Use a noisy-execution likelihood: P(y | h, x) ∝ exp(−λ · d(y, h(x))) with a domain-appropriate distance *d*, or "*h* executed with k random slips".
3. **Strategy classification, as in decision research** (Bröder & Schiffer 2003; Davis-Stober & Brown 2011).
   - Per model × domain, compare "single heuristic + error" against mixture specifications.
   - Report error agreement EA(h, m) = P(y ≈ h(x) | y wrong, h(x) wrong), which generalises v1's "fallacy rate", with explicit tie handling.
   - Report the lift over a permutation baseline matched on item structure.
   - The mixture is P(y | x) = Σ_h π_h · P(y | h, x) + ε · q(y | x), where *q* is the "none of the above" model. Always report the unexplained mass.
   - Cross-model claims come from one hierarchical model with item and model random effects.
4. **Process measures.** Pre-register each heuristic's predictions for reasoning-token counts and stated confidence, and use them as a second channel alongside answers. Reasoning tokens play the role decision time plays in Glöckner's (2009) multiple-measure method.
5. **Manipulation signatures.** Each heuristic predicts how answers move under:
   - premise-order reversal;
   - renaming and re-theming;
   - **rule inversion** (EHOP);
   - duplicating a premise;
   - adding an irrelevant premise;
   - changing which atoms are "at issue";
   - instance size and constraint density;
   - thinking budget.

   The signature matrix (heuristic × manipulation → predicted change) is the main test.
6. **Positive controls first.** Implement heuristics, and noisy mixtures of them, as fake models. Run them through the full pipeline and confirm the planted strategy is recovered at known rates before analysing LLM data. Recovery-analysis designs exist to borrow (Bröder & Schiffer 2003; AutoCog, Jagadish et al. 2026).

### O4. Evidence from evals

**Domains.** Start with the first two.

| Domain | Exact solver | Answer format | Why / prior work |
|--------|--------------|---------------|------------------|
| Propositional / monadic entailment ("what follows?") | PySMT + z3; PyETR | JSON literals over the item's vocabulary, or multiple choice built from heuristic outputs | Continuity with v1; cognitive heuristics. Strategy taxonomies so far come from traces (Mondorf & Plank 2024; Eisape et al. 2024; Bertolazzi et al. 2024), not from answers. |
| Random 3-SAT near ratio ≈ 4.26, with matched SAT/UNSAT pairs | PySAT | Assignment or `UNSAT` | The hardness dial. Overlaps Hazra et al. 2025 and Zhang, Chen & Chen 2026; our addition is identification. |
| Graph coloring | PySAT / OR-Tools | Coloring + structured edge-list echo (diagnoses hallucinated edges) | Heyman & Zylberberg 2025 (greedy score); EHOP |
| Knapsack | Dynamic programming / OR-Tools | Item subset | EHOP (greedy baselines, inverted variants) |
| TSP (small n), then Blocksworld planning | OR-Tools / Concorde; a planner | Tour / plan | NN-on-TSP is already shown behaviourally and mechanistically (AlgoTrace), so TSP is not our showcase. Planning at PlanBench sizes is near-solved by reasoning models (Valmeekam et al. 2024), so we'd need larger sizes. |

**Framings.** Each domain is rendered as:

- a bare textbook framing;
- natural-language "realistic" framings, reusing v1's theme system;
- an **inverted-rule** variant (EHOP).

**Answer formats.** Primary metrics must be machine-checkable without an LLM translator: structured output or multiple choice. Free-text conditions are secondary, and use a translator whose error rate is measured on a hand-labelled set.

**Models.**

- Frontier API models, with and without thinking, at explicit thinking budgets (0 / 1k / 4k / 16k) where the API supports them. Log the reasoning tokens actually used.
- The open-weight models used in O5.
- Every call records provider, exact model version, date and sampling parameters.

**Repetition.** At least 3 samples per item and condition on a fixed 20% subset.

**Pre-registration.** Commit hypotheses, metrics, exclusions and analysis scripts before the main run.

### O5. Evidence from mechanistic interpretability

**Prior work sets the bar.**

- Circuits for propositional and syllogistic inference in open LLMs are already published (Hong et al. 2025; Kim et al. 2025). "We found the logic circuit" is not a contribution. Adjudicating *between competing heuristics on the items where they disagree* is.
- Nobody has probed for a heuristic's state on NP-hard instances in pretrained LLMs, as far as the review found.
- Premise-order patching also appears to be open.

**Target models.**

- **Qwen3 (4B / 8B) is the primary model.** One checkpoint gives thinking and non-thinking modes, and circuit-tracer has transcoders for Qwen3 0.6–14B.
- Gemma 2 (Gemma Scope) and Gemma 3 (Gemma Scope 2).
- Llama-3.1-8B-Instruct (transcoders available).
- OLMo 2, for data-contamination checks only; no known transcoders.

**Questions and methods.**

| Question | Method | What would discriminate |
|----------|--------|-------------------------|
| Which candidate's answer is the model heading toward? | Tuned lens / logit lens, layer by layer, on items where the candidates disagree | Which heuristic's answer the lens favours, and at which layer. *Not* "early and independent of size": LLMs don't adapt depth to difficulty in general (Csordás et al. 2025; Hu et al. 2025), so a failing exact procedure predicts that too. |
| Is the heuristic's state represented? | Linear probes with control tasks (selectivity) and format deconfounding | For `UP-k`, the layer at which the k-th derived literal becomes decodable grows with k, up to a depth ceiling |
| Is that state used? | **Linear** interchange interventions / DAS (Geiger et al. 2023) | Interventions on *h*'s variable move answers as *h* predicts, **more than the same procedure on the best competing heuristic's variables**. The same alignment must fail on a random-init model: non-linear alignment maps make causal abstraction trivial (Sutter et al. 2025), and explanations can be non-identifiable (Méloux et al. 2025). |
| Is it one procedure or a bag of heuristics? | Neuron/feature classification and ablation by type (Nikankin et al. 2025); Sasaki et al. 2026 for cue-subspace interventions | Pre-specify the level of analysis, because neuron-level and subspace-level analyses can reach opposite verdicts on the same task |
| Which components? | Attribution graphs with transcoders (Ameisen et al. 2025; Lindsey et al. 2025) | Short, no-CoT entailment items only. Replacement models are partial, so expect many uninformative graphs. |
| (Thinking models) Is the answer committed before thinking? | Pre-CoT probes, steering with norm-matched baselines (Cox et al. 2026); thought-anchor resampling | Whether suppressing backtracking shifts mixture weight toward greedy heuristics (links to H3) |
| Where does order sensitivity enter? | Activation patching between forward and reversed premise orders on paired items | `PRIMACY` / `FIRST` / `MATCH` each predict a different locus (cf. Chen et al. 2024; Kim et al. 2025) |

**Controls before LLMs.** The pipeline must recover the known procedure in each of these before we trust it on LLMs:

- **InterpBench-style SIIT models** trained to implement zoo heuristics with realistic weights (Gupta et al. 2024). Raw Tracr weights are unrealistic.
- **ALTA** (Shaw et al. 2025) for heuristics that need loops.
- A **capacity toy** following Ye et al. (2025): small transformers trained on graphs within or beyond their depth capacity. The learned procedure, exact algorithm or degree heuristic, is then known and switchable.
- **MIB** (Mueller et al. 2025), to check that our patching and DAS implementation reproduces published numbers.

### O6. Continuing RASP-L

**Background.**

- RASP (Weiss, Goldberg & Yahav 2021) is a programming language whose primitives correspond to transformer operations.
- Zhou et al. (2024) define RASP-L, a learnable subset. Their RASP-Generalization Conjecture has three conditions: realizability, simplicity (a short RASP-L program) and diversity. They describe it as phenomenological, not mechanistic.
- Their **toy model (RASP MDL principle)** states: "Transformers tend to learn the shortest RASP-L program which fits the training set." Their forward-addition result is already a short program that fits in-distribution and fails on long carries.
- Formal follow-ups:
  - C-RASP and limit transformers (Huang et al. 2025);
  - uncomputability of length-generalisation bounds, and sample sizes exponential in the minimal program's size (Yang et al. 2026);
  - a decompiler from trained transformers to RASP (Huang et al. 2026).

**Our extension: the imperfect-fit regime.** For NP-hard tasks we expect no short RASP-L program to fit the training distribution exactly. So "the shortest program that fits" is undefined, and must become a trade-off. The hypothesis is that training selects

P\* = argmin_P |P| + λ · err_train(P),

and that P\* is a heuristic. This is a two-part MDL objective. The closest precedent is Ye et al. (2025): beyond depth capacity a node-degree heuristic is learned, and data curation restores the exact algorithm.

**Predictions.**

1. The heuristics models use lie on or near the zoo's accuracy-versus-program-length Pareto frontier. This follows from the objective above.
2. As training-set size or diversity grows, the learned heuristic moves along the frontier toward longer, more accurate programs. This follows from Yang et al. 2026 and from Ye et al.'s data switch.
3. Thinking budget moves mixture weight from class-C heuristics to class-S ones. Looping or CoT lets a short per-step program iterate: n-RASP-L (Fan et al. 2025; Li et al. 2024).
4. Models trained from scratch on NP-hard tasks decompile, at all sizes, into a short program matching a zoo heuristic. The main falsifier is Huang et al. 2026: models that don't length-generalise usually *don't* decompile to short programs.

**Things to pre-register.**

- **The length measure.** Primitive count, depth, or MDL code length. ALTA found learned behaviour follows the fewest-*layers* program, not the fewest-rules one, so H2 can pass under one measure and fail under another.
- **The input encoding.** RASP-L length depends on tokenisation and format.
- **Rival complexity measures**, so H2 is a model comparison: sensitivity, min-degree (Abbe et al.), globality, depth.

**Scope.** H2 is a claim about from-scratch toy training. For pretrained LLMs, "the training distribution" is pretraining plus post-training, so H2 is an analogy there. Some RASP-family predictions do transfer to pretrained models (Jobanputra et al. 2025).

**Other work to note.** Standard optimisers don't reliably find MDL-optimal solutions (Shaw et al. 2026). Pan et al. (2025) already combine SAT, a compiled transformer (PARAT) and training on solver traces.

---

## 4. Hypotheses and what would change our minds

| ID | Hypothesis | Falsified if |
|----|------------|--------------|
| H1 | Above the budget line, a few zoo heuristics (≤ 3 per domain, under noisy-execution likelihoods) explain most of each model's errors, well above chance | No heuristic's lift over its permutation baseline exceeds a pre-registered threshold for most models. Also report how much is absorbed by `NOISY-EXACT` and `HALLUC-CONSTRAINT`. |
| H2 | In toy models, the learned heuristic is the two-part-MDL optimum among zoo programs, under a pre-registered length measure, and beats rival complexity measures | Another complexity measure predicts mixture weights better, or trained models don't decompile to zoo programs |
| H3 | Capability and thinking budget raise the effective search budget *b* (`DPLL-b`) and shift weight from surface heuristics to structural ones. Beyond the budget line, residual errors match budget-truncated search plus its default answer | On items beyond the budget line, agreement with truncated-search predictions is no higher than with surface heuristics. Budget effects may be non-monotone (Gema et al. 2025; Ghosal et al. 2025), so this is pre-registered as allowed. |
| H4 | A model's dominant heuristic *family* is stable, first across framings within a domain, then across domains linked by reductions (SAT ↔ vertex cover ↔ coloring; cf. Zhang, Chen & Chen 2026) | Family weights are uncorrelated across framings. Prior work (EHOP; Hazra et al.) leads us to expect strong framing dependence, which would be a result in itself. |
| H5a | The identified heuristic's state is linearly decodable, with selectivity above control tasks | Probes fail where behaviour matches |
| H5b | Linear interventions on that state move answers as the heuristic predicts, more than interventions on the best competitor's state, and not in random-init models | Competitor or random-init alignments do as well |
| H5c | H5a and H5b hold on items where the heuristic is wrong | Effects appear only where the heuristic is right |
| H5-alt | Behaviour matching *h* comes from many shallow input-pattern features, with no *h*-state variable ("bag of heuristics") | — (a competing outcome, reported either way) |
| H6 | Cognitive heuristics (`ETR`, `MM`) explain errors better than surface heuristics, with a capability trend that may be **non-monotone** (an inverted U is allowed) | Surface heuristics explain as much or more, controlling for accuracy. Which heuristics count as "cognitive" (e.g. `MATCH`, `ATMOSPHERE`) is pre-registered. |

---

## 5. Methodology requirements

These are lessons from v1. Each one is cheap to follow and expensive to skip.

1. **Immutable, content-addressed item sets.** Every item has a hash of its logical content. A manipulated item (e.g. reversed premises) stores its source item's hash. Analyses join on hashes, never on row index or `doc_id`.
2. **Manipulation and control use the same items, and a script asserts it** before any analysis runs.
3. **One versioned scorer.**
   - Every scored result records the scorer git SHA and the solver and PyETR versions.
   - When the scorer changes, all runs are re-scored from raw outputs.
   - Raw outputs are kept permanently.
4. **No LLM in the scoring path for primary metrics.** If a translator is needed for secondary analyses:
   - it sees only the response and the vocabulary, never the premises;
   - its output is validated against a grammar, with whole-word name matching (no substring replacement);
   - its error rate is measured on ≥ 200 hand-labelled items.
5. **Parse failures, refusals and "declared impossible" are their own categories**, reported per model and condition. They never fall silently into "correct" or "incorrect".
6. **Every number in the paper comes from one command.** A script in `analysis/` produces it from raw data in the repo, and CI checks that it still does.
7. **Tests match the design.**
   - Paired designs get paired tests (McNemar, mixed-effects logistic regression).
   - Never test a quantity against a subset of itself.
   - Cross-model claims come from one hierarchical model, not from counting per-model significant tests.
8. **Run-to-run variance is measured and reported.** If one run per model is used, which run is fixed in advance.
9. **Capability covariates come from a checked mapping table.** Arena Elo, training compute and benchmark scores are joined through a table of provider model id → leaderboard entry, with source and date per row, checked by hand.
10. **The exact prompts are published.** Instructions that change how a model reasons (e.g. "answer immediately") are experimental factors, not hidden constants.
11. **Token limits and thinking budgets are set per call and verified** against what the API reports was used. Runs that hit the cap are analysed as censored.
12. **Positive controls (O3 step 6) pass before any LLM data is analysed.**

---

## 6. Repository layout

This repository (`reasoning_heuristics`) holds the new work. `etr_case_generator` stays as the frozen record of v1. Its entailment generator is first used as a dependency (pinned git SHA), then ported.

```
docs/
  DESIGN.md                 this document
  LITERATURE.md             literature review (summary); docs/literature/ holds the full reports
  decisions/                short decision records, one per decision
src/reasoning_heuristics/
  problems/                 instance generators + exact solvers, one subpackage per domain
    entailment/  sat/  coloring/  knapsack/  tsp/  planning/
  heuristics/               the zoo: reference implementation + metadata (domain, class C/S, budget, RASP-L program id)
  rasp/                     RASP-L interpreter, a program per heuristic, length measures, Tracr/ALTA export
  evals/                    prompt templates, runner (OpenRouter + native APIs), structured-output parsing, run manifests
  identify/                 likelihoods, baselines, mixture/strategy classification, item selection, fake-model controls
  interp/                   lenses, probes, interventions, attribution graphs (open-weight models)
analysis/                   one script per figure/table; reads data/runs, writes figures/
data/
  items/                    generated item sets, content-hashed, never edited in place
  runs/                     raw model outputs (JSONL) + manifest per run
tests/
```

### Setup steps

1. **Finish v1's record in `etr_case_generator`.**
   - Commit the remaining item sets and raw outputs. Some exist only in local copies, including the 383-item set and several result directories.
   - Add a `reproduce.py` that regenerates v1's tables from raw outputs.
2. Create the `src/` skeleton, `pyproject.toml` and CI (tests + `analysis/` smoke run).
3. Use `etr_case_generator` as a pinned dependency for entailment items. Port the generator and theme system into `problems/entailment/` once item hashing (§5.1) is in place.
4. Replace `lm_eval` with a thin runner, or Inspect AI. `lm_eval` gives no direct control over thinking budgets or structured output, and its token-limit precedence is easy to get wrong: a task's `max_gen_toks` overrides `max_tokens` in `--model_args`.

---

## 7. Plan and milestones

| Phase | Scope | Exit criterion |
|-------|-------|----------------|
| 0. Reset (1–2 wk) | Repo skeleton; freeze v1 with all raw data; one-command reproduction of v1 tables | v1's `reproduce.py` runs; CI is green |
| 1. Pilot (3–4 wk) | Entailment + 3-SAT; ~15 heuristics; fake-model and capacity-toy controls; ~8 models × 2 thinking budgets × ~300 items | Controls recover planted heuristics; go/no-go on H1, with a threshold written down before the run |
| 2. Full evals (4–6 wk) | + coloring, knapsack; all manipulations; 25–40 models; repeats | Pre-registration committed before data collection |
| 3. Interp (4–6 wk, overlaps 2) | Qwen3 first; SIIT/ALTA/MIB controls first; premise-order patching early, since it looks open | Controls pass; H5a–c and H5-alt tested |
| 4. RASP-L (4 wk, can start in 1) | Programs + class labels for the zoo; length measures; toy training with data-size sweeps; decompilation | O6 predictions 1–4 tested |
| 5. Write-up | Consider a short methods paper on identification after Phase 1, given the competition | — |

---

## 8. Risks

| Risk | Mitigation |
|------|------------|
| **Being scooped.** Close groups: EHOP; Hazra et al.; AlgoTrace; Ye et al.; the Hahn lab (decompiler + C-RASP theory); AutoCog-style automated strategy discovery | Move the identification pilot fast; claim the method (competing-heuristic identification from answers, plus signatures) early |
| Heuristics aren't identifiable: many predict the same answers | Information-gain item selection; manipulation signatures; process measures; fake-model recovery tests show where the method's resolution ends |
| Exact-match scoring leaves most errors unexplained | Noisy-execution likelihoods; `NOISY-EXACT` and `HALLUC-CONSTRAINT` components |
| Models do approximate retrieval, not a clean procedure | `TEXTBOOK-TRANSFER` + inverted-rule items; report unexplained mass |
| Long-CoT models do exact search on small items | Centre sweeps on each model's budget line *n\** |
| Interpretability methods pass with the wrong heuristic | Linear maps only; competing-heuristic and random-init controls; pre-specified level of analysis |
| API nondeterminism and silent model updates | Run manifests with exact version strings; repeats; date every run |
| O1 slides into philosophy | Keep it to a page; answer van Rooij et al. directly; let measured hardness carry the weight |
| Cost | Pilot first; size the main study by power analysis on pilot effects |

---

## 9. Open questions for Andrew

1. **Pilot domains.** Given the overlap (Hazra et al. and Zhang et al. on 3-SAT; EHOP on coloring, knapsack and TSP), do we keep entailment + 3-SAT for the pilot? Entailment has the least prior work and the most continuity with v1.
2. **Showcase for O5.** Entailment and SAT heuristics on Qwen3, instead of NN-on-TSP, which AlgoTrace has done?
3. **The length measure H2 is judged on.** Primitive count, depth, or MDL code length?
4. **Collaborators.** Do the v1 co-authors (Oxford HAI Lab) join this line of work?
5. **Runner.** A thin custom runner, or Inspect AI?

Resolved since v0.1:
- "The RASP-L paper" is Zhou et al. 2024 (confirmed).
- The repo name is `reasoning_heuristics`.

---

## 10. References

Key references only. [LITERATURE.md](LITERATURE.md) and [docs/literature/](literature/) list about 150 papers with links.

- Ameisen et al. (2025). *Circuit Tracing: Revealing Computational Graphs in Language Models.* Transformer Circuits Thread.
- Amiri Bavandpour, Huang, Rofin & Hahn (2025). *Lower Bounds for Chain-of-Thought Reasoning in Hard-Attention Transformers.* ICML. arXiv 2502.02393.
- Bertolazzi, Gatt & Bernardi (2024). *A Systematic Analysis of LLMs as Soft Reasoners: The Case of Syllogistic Inferences.* EMNLP. arXiv 2406.11341.
- Bröder & Schiffer (2003). *Bayesian strategy assessment in multi-attribute decision making.* J. Behavioral Decision Making 16(3).
- Chen et al. (2024). *Premise Order Matters in Reasoning with Large Language Models.* ICML.
- Cox, Kianersi & Garriga-Alonso (2026). *Post-Hoc Reasoning in Chain of Thought: Decoding and Steering Pre-Committed Answers.* arXiv 2603.01437.
- Csordás, Manning & Potts (2025). *Do Language Models Use Their Depth Efficiently?* NeurIPS. arXiv 2505.13898.
- Davis-Stober & Brown (2011). *A shift in strategy or "error"? Strategy classification over multiple stochastic specifications.* Judgment and Decision Making 6(8).
- Duchnowski, Pavlick & Koller (2025). *A Knapsack by Any Other Name: Presentation impacts LLM performance on NP-hard problems* (EHOP). Findings of EMNLP.
- Eisape et al. (2024). *A Systematic Comparison of Syllogistic Reasoning in Humans and Language Models.* NAACL. arXiv 2311.00445.
- Estermann & Wattenhofer (2025). *Reasoning Effort and Problem Complexity: A Scaling Analysis in LLMs.* ICLR 2025 workshop. arXiv 2503.15113.
- Fan, Du, Ramchandran & Lee (2025). *Looped Transformers for Length Generalization.* ICLR. arXiv 2409.15647.
- Feng et al. (2023). *Towards Revealing the Mystery behind Chain of Thought: A Theoretical Perspective.* NeurIPS.
- Geiger, Wu, Potts, Icard & Goodman (2023). *Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations* (DAS). arXiv 2303.02536.
- Gema et al. (2025). *Inverse Scaling in Test-Time Compute.* TMLR. arXiv 2507.14417.
- Ghosal et al. (2025). *Does Thinking More always Help? Mirage of Test-Time Scaling in Reasoning Models.* NeurIPS. arXiv 2506.04210.
- Glöckner (2009). *Investigating intuitive and deliberate processes statistically: The multiple-measure maximum likelihood strategy classification method.* Judgment and Decision Making 4(3).
- Gupta, Arcuschin, Kwa & Garriga-Alonso (2024). *InterpBench: Semi-Synthetic Transformers for Evaluating Mechanistic Interpretability Techniques.* NeurIPS Datasets & Benchmarks. arXiv 2407.14494.
- Hagendorff, Fabi & Kosinski (2023). *Human-like intuitive behavior and reasoning biases emerged in large language models but disappeared in ChatGPT.* Nature Computational Science 3.
- Hazra, Venturato, Zuidberg Dos Martires & De Raedt (2025). *Have Large Language Models Learned to Reason? A Characterization via 3-SAT Phase Transition.* COLM. arXiv 2504.03930.
- Heyman & Zylberberg (2025). *Evaluating the Systematic Reasoning Abilities of Large Language Models through Graph Coloring.* arXiv 2502.07087.
- Hong et al. (2025). *A Implies B: Circuit Analysis in LLMs for Propositional Logical Reasoning.* NeurIPS. arXiv 2411.04105.
- Hu, Zhou & Zhang (2025). *What Affects the Effective Depth of Large Language Models?* arXiv 2512.14064.
- Huang et al. (2025). *A Formal Framework for Understanding Length Generalization in Transformers.* ICLR. arXiv 2410.02140.
- Huang, Bakalova, Bhattamishra, Merrill & Hahn (2026). *Discovering Interpretable Algorithms by Decompiling Transformers to RASP.* ICML. arXiv 2602.08857.
- Jagadish et al. (2026). *Closing the Loop to Discover Psychological Theories with an Automated Cognitive Scientist* (AutoCog). arXiv 2606.26448.
- Jobanputra et al. (2025). *Born a Transformer – Always a Transformer? On the Effect of Pretraining on Architectural Abilities.* NeurIPS. arXiv 2505.21785.
- Kim, Valentino & Freitas (2025). *Reasoning Circuits in Language Models: A Mechanistic Interpretation of Syllogistic Inference.* Findings of ACL. arXiv 2408.08590.
- Koralus (2022). *Reason and Inquiry: The Erotetic Theory.* OUP (online Dec 2022; print 2023).
- Koralus & Wang-Maścianica (2023). *Humans in Humans Out: On GPT Converging Toward Common Sense in both Success and Failure.* arXiv 2303.17276.
- Lawsen (2025). *Comment on The Illusion of Thinking* (comment on Shojaee et al.; not peer-reviewed). arXiv 2506.09250.
- Li, Liu, Zhou & Ma (2024). *Chain of Thought Empowers Transformers to Solve Inherently Serial Problems.* ICLR. arXiv 2402.12875.
- Lieberum et al. (2024). *Gemma Scope: Open Sparse Autoencoders Everywhere All At Once on Gemma 2.* arXiv 2408.05147.
- Lindner et al. (2023). *Tracr: Compiled Transformers as a Laboratory for Interpretability.* NeurIPS.
- Lindsey et al. (2025). *On the Biology of a Large Language Model.* Transformer Circuits Thread.
- Lippl et al. (2025). *AlgoTrace: Algorithmic Primitives and Compositional Geometry of Reasoning in Language Models.* arXiv 2510.15987.
- McCoy et al. (2024). *Embers of autoregression show how large language models are shaped by the problem they are trained to solve.* PNAS 121(41).
- Méloux, Maniu, Portet & Peyrard (2025). *Everything, Everywhere, All at Once: Is Mechanistic Interpretability Identifiable?* ICLR. arXiv 2502.20914.
- Merrill & Sabharwal (2023). *The Parallelism Tradeoff: Limitations of Log-Precision Transformers.* TACL.
- Merrill & Sabharwal (2024). *The Expressive Power of Transformers with Chain of Thought.* ICLR.
- Merrill & Sabharwal (2025). *Exact Expressive Power of Transformers with Padding.* NeurIPS. arXiv 2505.18948.
- Mitchell, Selman & Levesque (1992). *Hard and Easy Distributions of SAT Problems.* AAAI.
- Mondorf & Plank (2024). *Comparing Inferential Strategies of Humans and Large Language Models in Deductive Reasoning.* ACL. arXiv 2402.14856.
- Mueller et al. (2025). *MIB: A Mechanistic Interpretability Benchmark.* ICML. arXiv 2504.13151.
- Myung & Pitt (2009). *Optimal Experimental Design for Model Discrimination.* Psychological Review 116(3).
- Nikankin et al. (2025). *Arithmetic Without Algorithms: Language Models Solve Math with a Bag of Heuristics.* ICLR.
- Pan, Ganesh, Abernethy, Esposo & Lee (2025). *Can Transformers Reason Logically? A Study in SAT Solving.* ICML. arXiv 2410.07432.
- Rameshkumar et al. (2025). *Reasoning Models Reason Well, Until They Don't.* arXiv 2510.22371.
- Richardson, Kearns, Moss, Wang-Maścianica & Koralus (2025). *Theory-Grounded Evaluation of Human-Like Fallacy Patterns in LLM Reasoning.* ICLR 2026. arXiv 2506.11128 (v1 title: "Stronger Language Models Produce More Human-Like Errors").
- Sasaki et al. (2026). *Language Models Compare Quantities Using Number-specific and Unit-specific Heuristics.* arXiv 2606.03982.
- Shaw et al. (2025). *ALTA: Compiler-Based Analysis of Transformers.* TMLR. arXiv 2410.18077.
- Shaw, Cohan, Eisenstein & Toutanova (2026). *Bridging Kolmogorov Complexity and Deep Learning: Asymptotically Optimal Description Length Objectives for Transformers.* ICLR. arXiv 2509.22445.
- Shojaee et al. (2025). *The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity.* NeurIPS.
- Sinha, Arun, Goel, Staab & Geiping (2025). *The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs.* ICLR 2026. arXiv 2509.09677.
- Sutter, Minder, Hofmann & Pimentel (2025). *The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability?* NeurIPS. arXiv 2507.08802.
- Tang et al. (2025). *GraphArena: Evaluating and Exploring Large Language Models on Graph Computation.* ICLR. arXiv 2407.00379.
- Valmeekam et al. (2023). *PlanBench: An Extensible Benchmark for Evaluating Large Language Models on Planning and Reasoning about Change.* NeurIPS Datasets & Benchmarks.
- van Rooij, Wright & Wareham (2012). *Intractability and the use of heuristics in psychological explanations.* Synthese 187(2).
- Verma (2026). *Solver-Hard Is Not Model-Hard: A Hardness-Controlled Diagnostic for LLM Constraint Reasoning.* arXiv 2607.17047.
- Weiss, Goldberg & Yahav (2021). *Thinking Like Transformers.* ICML.
- Williams, Gomes & Selman (2003). *Backdoors to Typical Case Complexity.* IJCAI.
- Yang, Bergsträßer, Zetzsche, Chiang & Lin (2026). *Length Generalization Bounds for Transformers.* arXiv 2603.02238.
- Ye, Fu, Jia & Sharan (2025). *Transformers Provably Learn Algorithmic Solutions for Graph Connectivity, But Only with the Right Data.* arXiv 2510.19753.
- Zhang, Chen & Chen (2026). *Satisfiability Solving with LLMs: A Matched-Pair Evaluation of Reasoning Capability.* FSE. arXiv 2605.28602.
- Zhou, Bradley, Littwin, Razin, Saremi, Susskind, Bengio & Nakkiran (2024). *What Algorithms can Transformers Learn? A Study in Length Generalization.* ICLR. arXiv 2310.16028.
