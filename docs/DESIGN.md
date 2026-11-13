# Heuristics Under Hardness — Design Document

*How do language models answer problems they cannot solve exactly?*

- **Status:** Draft v0.1, 2026-11-13
- **Owner:** Andrew Keenan Richardson
- **Follows on from:** the 2025 ETR study ([arXiv 2506.11128](https://arxiv.org/abs/2506.11128), ICLR 2026), whose code stays frozen in [`Oxford-HAI-Lab/etr_case_generator`](https://github.com/Oxford-HAI-Lab/etr_case_generator) (see §6).

---

## 1. Summary

Many reasoning problems people care about are NP-hard or coNP-hard in general. A language model does a bounded amount of computation per token and usually answers in far fewer tokens than exact search would take. So on hard instances it cannot be running an exact algorithm. Whatever it runs is a **heuristic**: a cheap procedure that is right on many instances and wrong on others in a characteristic way.

This project asks **which heuristics**. We will:

1. Build a zoo of candidate heuristics. Each one is a precise procedure that gives a predicted answer on every instance.
2. Generate instances on which the candidates disagree.
3. Measure which candidates explain models' answers, and especially their errors.
4. Look for the same heuristics inside open-weight models with interpretability tools.
5. Situate them in RASP-L. The hypothesis is that the heuristics models adopt are the short RASP-L programs that fit their training distribution.

The 2025 ETR study is one special case of this. It tested a single heuristic, the ETR default inference procedure, on items chosen so that this heuristic gets them wrong.

The idea worth keeping is **error composition**: what a model's wrong answers look like says more about its procedure than its accuracy does. What the study lacked was competing explanations. With only one candidate, a match with ETR cannot be told apart from a match with any other procedure that happens to give the same wrong answer.

---

## 2. Objectives at a glance

| # | Objective | Kind of evidence | Role in the paper |
|---|-----------|------------------|-------------------|
| O1 | Many real-world problems are effectively NP-hard | Argument + survey; measured hardness of our own items | Motivation |
| O2 | These problems can't be solved quickly, yet LLMs answer quickly, so they must use heuristics | Complexity argument + compute-vs-accuracy measurements | Premise |
| O3 | Investigate many candidate heuristics and see which ones we find evidence for | Identification method (below) | **Core contribution** |
| O4 | Evidence from evals | Behavioural experiments on API and open models | Evidence for O3 |
| O5 | Evidence from mechanistic interpretability | Probes, patching, causal abstraction on open models | Evidence for O3 |
| O6 | Continue the RASP-L work and situate the heuristics there | RASP-L programs, description length, toy-model training | Theory for O3 |

---

## 3. Objectives in detail

### O1. Many real-world problems are effectively NP-hard

**Claim, stated carefully.** The computational problems underneath many everyday and professional reasoning tasks are NP-hard or coNP-hard in the worst case, and realistic instance distributions contain hard instances.

Examples:

| Task | Underlying problem | Complexity |
|------|--------------------|------------|
| Timetabling, shift rostering, job-shop scheduling | Scheduling | NP-hard |
| Route planning with stops | TSP / vehicle routing | NP-hard |
| Configuring a product with constraints | Constraint satisfaction | NP-complete |
| Register allocation; assigning rooms to clashing meetings | Graph coloring | NP-complete |
| "Does this conclusion follow from these rules?" | Propositional entailment | coNP-complete |
| Same, with properties of objects | Monadic first-order logic | NEXPTIME-complete (satisfiability) |
| Bounded-length planning | Classical planning | NP-complete (PSPACE without the bound) |
| Puzzles: Sudoku (n²×n²), Minesweeper consistency | CSP | NP-complete |

The 2025 study's items ("what, if anything, follows?") already sit in the coNP-hard row.

**What we'll do.**

1. A short survey and argument section that maps tasks to formal problems, with reductions cited.
2. For every domain we study, measure each item's hardness with exact solvers: solver node counts and runtime, backbone size, and distance from the satisfiability phase transition. "Hard" then becomes a measured property of our items, not an assumption.

**Caveat to state up front.** NP-hardness is a worst-case statement. Industrial SAT instances with millions of variables are solved every day because they have exploitable structure (backdoors, low treewidth; Williams, Gomes & Selman 2003). The defensible claim is that the problem classes are intractable in general and realistic distributions contain hard cores. That is all O2 needs. O1 is motivation: it should take a page, not a chapter.

### O2. Bounded computation forces heuristics

**Argument.**

1. A fixed transformer forward pass with log-precision arithmetic is a uniform TC⁰ circuit (Merrill & Sabharwal 2023). Generating T tokens is T sequential passes. With T polynomial in the input size, the whole computation stays inside P (Merrill & Sabharwal 2024; Feng et al. 2023).
2. Assuming P ≠ NP, no fixed model that emits polynomially many tokens decides an NP-hard family correctly on every instance.
   - With a direct answer (T = O(1), as under v1's "answer immediately" instruction), the model is limited to TC⁰. Assuming TC⁰ ≠ NC¹, that rules out exact answers even for some problems in P.
3. Therefore, on hard instances the answer comes from an incomplete procedure.

**What makes this an objective rather than a remark.** Step 3 is close to a tautology under standard assumptions. The content is in measuring it:

- (a) How accuracy falls with instance size and hardness at a fixed token budget.
- (b) How thinking-token use scales with size. We expect sub-exponential growth, with accuracy decaying as size grows.
- (c) Whether errors are **structured** rather than random. This is what O3 measures.

**Rules.**

- Measure "quickly" in tokens and FLOPs, never wall-clock time.
- Disable tool use.
- Separate three kinds of failure: ran out of budget (truncated), wrong answer, and unsolvable item. The dispute between Shojaee et al. 2025 and Lawsen 2025 turned on exactly this.
- Check small instances for memorisation.

### O3. Identify the heuristics (core)

**Definitions.**

- An instance *x* has a ground truth *g(x)* from an exact solver.
- A **heuristic** *h* is a deterministic (or explicitly stochastic) procedure that maps *x* to an answer *h(x)* within a stated compute budget (for example, a bounded number of passes over the input).
- *y* is a model's response.
- **Evidence that model *m* uses *h*** has two parts:
  - *y* agrees with *h* on instances where *h* is wrong, more often than chance; and
  - when we manipulate the input, the model's answer moves the way *h* predicts.

**Initial heuristic zoo.** These are candidates. Adding and removing entries is expected.

| Domain | ID | Heuristic | How it errs |
|--------|----|-----------|-------------|
| Entailment | `ETR` | ETR default procedure (PyETR): Update filters alternatives by issue matching | Commission (illusory inferences) |
| Entailment | `MM` | Mental models, principle of truth: represent only what is true in each possibility | Commission and omission |
| Entailment | `MATCH` | Take the disjunct of an earlier premise that shares atoms with a later categorical premise | Commission |
| Entailment | `FIRST` | Read each "either A or B" as A | Commission |
| Entailment | `UP-k` | k rounds of unit propagation; report derived literals | Omission only (sound) |
| Entailment | `FREQ` | Conclude the most frequent literals | Commission |
| Entailment | `ECHO` / `NONE` | Restate a premise / say nothing follows | Uninformative but valid |
| SAT / CSP | `GREEDY` | Assign variables in mention order, maximise clauses satisfied so far, never backtrack | Wrong assignment, false UNSAT |
| SAT / CSP | `POLARITY` | Give each variable its majority polarity | Wrong assignment |
| SAT / CSP | `UP+GUESS` | Unit propagation, then fill the rest with a default value | Wrong assignment |
| SAT / CSP | `WALK-k` | WalkSAT with k flips | Wrong assignment |
| Coloring | `FIRST-FIT`, `DSATUR`, `LARGEST-FIRST` | Classic greedy colorings | Too many colors / conflicts |
| Knapsack / subset sum | `RATIO`, `VALUE`, `LARGEST-FIT` | Greedy selection rules | Suboptimal or infeasible |
| TSP | `NN`, `INPUT-ORDER`, `GREEDY-EDGE`, `2OPT-k` | Construction and local search | Suboptimal tours |
| Any | `PRIMACY`, `RECENCY`, `LENGTH-PRIOR` | Surface cues | Order and size effects |

"Approximate retrieval" (pattern-matching to familiar problems) is hard to state as a procedure. It shows up instead as the unexplained mass in the mixture model, and as content effects under re-theming.

**Identification method.**

1. **Discriminating items.** Generate a large pool, then select items where the candidates disagree with each other and with *g(x)*. Choose items by expected information gain between heuristics: optimal design for model discrimination, as in cognitive modelling (Myung & Pitt 2009).
2. **Metrics.**
   - *Error agreement*: EA(h, m) = P(y = h(x) | y ≠ g(x), h(x) ≠ g(x)). This is v1's "fallacy rate" generalised to any *h*.
   - *Chance baseline* for each *h*: permute *h*'s outputs across structurally matched items. Report the lift over this baseline, not raw agreement.
   - *Mixture model*: P(y | x) = Σ_h π_h · 1[y = h(x)] · (1 − ε) + ε · q(y | x), where *q* is a "none of the above" model. Fit π per model and compare heuristic sets by held-out log-likelihood. Always report the unexplained mass.
   - Cross-model claims come from one hierarchical model with item and model random effects.
3. **Manipulation signatures.** Each heuristic predicts how answers move under each manipulation:
   - reversing premise order;
   - renaming and re-theming;
   - duplicating a premise;
   - adding an irrelevant premise;
   - changing which atoms are "at issue";
   - instance size and constraint density;
   - thinking budget.

   The signature matrix (heuristic × manipulation → predicted change) is the main test. Agreement on a static item set alone is weak evidence.
4. **Positive controls first.** Implement each heuristic, and noisy mixtures of them, as a fake model. Run it through the full pipeline (prompt rendering → model → answer parsing → identification) and confirm the pipeline recovers what was planted, with known error rates. No LLM data is analysed until this passes.

### O4. Evidence from evals

**Domains.** Start with the first two and grow to five.

| Domain | Exact solver | Answer format | Why |
|--------|--------------|---------------|-----|
| Propositional / monadic entailment ("what follows?") | PySMT + z3; PyETR for `ETR` | JSON list of literals over the item's vocabulary, or multiple choice built from heuristic outputs | Continuity with v1; ready-made cognitive heuristics; coNP-hard |
| Random 3-SAT near clause/variable ratio ≈ 4.26 | PySAT | Assignment or `UNSAT` (checkable) | Canonical hardness dial (Mitchell, Selman & Levesque 1992) |
| Graph coloring | PySAT / OR-Tools | Coloring (checkable) | Well-known greedy heuristics |
| Knapsack / subset sum | Dynamic programming / OR-Tools | Item subset | Greedy rules with distinct signatures |
| TSP (small n), then Blocksworld planning | OR-Tools / Concorde; a planner | Tour / plan | Realistic framing; PlanBench precedent |

Each domain is rendered two ways: a bare formal framing, and natural-language "realistic" framings that reuse v1's theme system. The difference measures content effects.

**Answer formats.** Primary metrics must be machine-checkable without an LLM translator.

- Use structured output (a JSON schema over the item's own vocabulary) or multiple choice.
- Free-text conditions are a secondary analysis. A translator may be used there, but its error rate must be measured on a hand-labelled set.

**Models.**

- Frontier API models, with and without thinking. Set explicit thinking budgets (0 / 1k / 4k / 16k) wherever the API supports them, and log the reasoning tokens actually used.
- The open-weight models used in O5.
- Every call records provider, exact model version string, date and sampling parameters.

**Repetition.** At least 3 samples per item and condition on a fixed 20% subset, to estimate within-model variance.

**Pre-registration.** Primary hypotheses, metrics, exclusion rules and analysis scripts are committed before the main run.

### O5. Evidence from mechanistic interpretability

**Target models.** Open-weight models whose behaviour matches a zoo heuristic in O4. Candidates:

- Llama 3.x 8B / 70B
- Qwen 3, thinking and non-thinking
- Gemma 2 / 3, which have the Gemma Scope SAEs
- OLMo 2, whose open training data lets us check contamination

**Questions and methods.**

| Question | Method | What a heuristic predicts |
|----------|--------|---------------------------|
| How deep is the computation? | Logit lens / tuned lens (Belrose et al. 2023): the layer at which the answer becomes decodable | Shallow heuristics: early, and independent of instance size |
| Is the heuristic's state represented? | Linear probes, with control tasks, for heuristic-specific variables (ETR: surviving alternatives; `UP-k`: derived literals; `FIRST-FIT`: colors assigned so far) | The variable is decodable at the predicted layer and position |
| Is that state used? | Activation patching and interchange interventions between item pairs that differ in one heuristic-relevant feature; distributed alignment search (Geiger et al.; Wu et al. 2023) to test a causal abstraction of the heuristic | Interventions move the answer as the heuristic's computation graph says |
| Which components? | Attribution graphs with transcoders (Lindsey et al. 2025); "bag of heuristics" analysis (Nikankin et al. 2025) | A small set of features and paths per heuristic |

**Controls before LLMs.**

- Compile heuristics into transformers with Tracr (Lindner et al. 2023), using their RASP programs from O6.
- Train small transformers from scratch on our tasks.

The interpretability pipeline must recover the known algorithm in both before we trust it on LLMs.

### O6. Continuing RASP-L

**Background.**

- RASP (Weiss, Goldberg & Yahav 2021) is a programming language whose primitives correspond to transformer operations.
- Zhou et al. (2024) define RASP-L, a restricted, learnable subset. They conjecture that transformers length-generalise on a task when the task has a short RASP-L program.

**Extension: the heuristic RASP-L hypothesis.** We expect NP-hard tasks to have no short RASP-L program for the exact algorithm, since a fixed RASP-L program runs in constant depth. On such a task, training finds the shortest RASP-L program that fits the training distribution well. That program is a heuristic.

**Predictions.**

1. The heuristics models use lie on or near the zoo's accuracy-versus-program-length Pareto frontier.
2. Heuristics with short RASP-L programs keep the same error signature as instance size grows: they "length-generalise their errors". Longer ones don't.
3. Chain of thought lets a RASP-L program iterate across tokens. So thinking models should move to heuristics whose per-step program is short but which run for many steps, such as propagation loops.

**Work.**

- Write each zoo heuristic in RASP-L, starting from the Zhou et al. reference implementation.
- Fix a program-length measure: primitive count, or an MDL code length.
- Compile the programs with Tracr for O5's controls.
- Train small transformers on each domain with controlled training data, and test predictions 1–3 directly.

**Assumption to confirm:** "the RASP-L paper" means Zhou et al. 2024.

---

## 4. Hypotheses and what would change our minds

| ID | Hypothesis | Falsified if |
|----|------------|--------------|
| H1 | On hard items, a few zoo heuristics (≤ 3 per domain) explain most of each model's errors, well above chance | No heuristic's lift over its permutation baseline exceeds a pre-registered threshold for most models. This also undercuts O2(c), and is itself reportable. |
| H2 | The heuristics that explain errors are the shortest RASP-L programs among candidates of similar accuracy on easy items | Longer programs systematically win the mixture weights |
| H3 | More capable models and bigger thinking budgets shift weight from surface heuristics (`PRIMACY`, `FIRST`, `FREQ`) to structural ones (`UP-k`, `DSATUR`, `NN`, `ETR`), not to exact search; accuracy on hard items still decays with size | Accuracy on hard items stays flat as size grows at a sub-exponential token budget |
| H4 | A model's dominant heuristic family is consistent across domains (e.g. "greedy, never backtrack") | Weights are uncorrelated across domains |
| H5 | In open models, the identified heuristic's intermediate state is linearly decodable and causally used | Probes and interventions fail where behaviour matches |
| H6 | v1's question, now tested against competitors: cognitive heuristics (`ETR`, `MM`) explain errors better than surface heuristics, increasingly so with capability | Surface heuristics explain as much or more |

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
5. **Parse failures and refusals are their own categories**, reported per model and condition. They never fall silently into "correct" or "incorrect".
6. **Every number in the paper comes from one command.** A script in `analysis/` produces it from raw data in the repo, and CI checks that it still does.
7. **Tests match the design.**
   - Paired designs get paired tests (McNemar, mixed-effects logistic regression).
   - Never test a quantity against a subset of itself.
   - Cross-model claims come from one hierarchical model, not from counting per-model significant tests.
8. **Run-to-run variance is measured and reported.** If one run per model is used, which run is fixed in advance.
9. **Capability covariates come from a checked mapping table.** Arena Elo, training compute and benchmark scores are joined through a table of provider model id → leaderboard entry, with source and date per row, checked by hand.
10. **The exact prompts are published.** Instructions that change how a model reasons (e.g. "answer immediately") are experimental factors, not hidden constants.
11. **Token limits and thinking budgets are set per call and verified** against what the API reports was used.
12. **Positive controls (O3 step 4) pass before any LLM data is analysed.**

---

## 6. Repository layout

The new work lives in a new repository. `etr_case_generator` stays as the frozen record of v1, and its entailment generator is first used as a dependency (pinned git SHA), then ported.

### Proposed layout

```
docs/
  DESIGN.md                 this document
  decisions/                short decision records, one per decision
src/<package>/              working name TBD (e.g. hardreason)
  problems/                 instance generators + exact solvers, one subpackage per domain
    entailment/             ported from etr_case_generator (PyETR views, mutations, themes, NL rendering)
    sat/  coloring/  knapsack/  tsp/  planning/
  heuristics/               the zoo: reference implementation + metadata (domain, budget, RASP-L program id)
  rasp/                     RASP-L interpreter, a program per heuristic, length measure, Tracr export
  evals/                    prompt templates, runner (OpenRouter + native APIs), structured-output parsing, run manifests
  identify/                 agreement metrics, baselines, mixture model, item selection, fake-model controls
  interp/                   lenses, probes, patching, causal abstraction (open-weight models)
analysis/                   one script per figure/table; reads data/runs, writes figures/
data/
  items/                    generated item sets, content-hashed, never edited in place
  runs/                     raw model outputs (JSONL) + manifest per run
tests/
```

### Setup steps

1. **Finish v1's record in `etr_case_generator`.**
   - Commit the remaining item sets and raw outputs. Some exist only in local copies, including the 383-item set and several result directories. They are the only record behind the published numbers. Large files go to Git LFS or a release asset.
   - Add a `reproduce.py` that regenerates v1's tables from raw outputs.
2. **In the new repo,** create the `src/` skeleton, `pyproject.toml` and CI (tests + `analysis/` smoke run).
3. Use `etr_case_generator` as a pinned dependency for entailment items. Port the generator and theme system into `problems/entailment/` once the item-hashing requirement (§5.1) is in place.
4. Replace `lm_eval` with a thin runner, or Inspect AI. `lm_eval` gives no direct control over thinking budgets or structured output, and its token-limit precedence is easy to get wrong: a task's `max_gen_toks` overrides `max_tokens` in `--model_args`.

---

## 7. Plan and milestones

| Phase | Scope | Exit criterion |
|-------|-------|----------------|
| 0. Reset (1–2 wk) | New repo skeleton; freeze v1 in `etr_case_generator` with all raw data; one-command reproduction of v1 tables | v1's `reproduce.py` runs; new repo CI is green |
| 1. Pilot (3–4 wk) | Entailment + 3-SAT; ~10 heuristics; fake-model controls; ~8 models × 2 thinking budgets × ~300 items | Controls recover planted heuristics; a go/no-go on H1, using a threshold written down before the run |
| 2. Full evals (4–6 wk) | + coloring, knapsack, TSP; all manipulations; 25–40 models; repeats | Pre-registration committed before data collection |
| 3. Interp (4–6 wk, overlaps 2) | 2–3 open models; Tracr and toy-model controls first | Controls pass; H5 tested on the best-matching model |
| 4. RASP-L (4 wk, can start in 1) | RASP-L programs for the zoo; length measure; toy training study | Predictions 1–3 of O6 tested |
| 5. Write-up | O1 + O2 as framing; O3–O6 as results | — |

---

## 8. Risks

| Risk | Mitigation |
|------|------------|
| Heuristics aren't identifiable: many predict the same answers | Information-gain item selection; manipulation signatures; fake-model recovery tests show where the method's resolution ends |
| Models do approximate retrieval, not a clean procedure | The mixture model's "other" component; report unexplained mass; content-effect manipulations |
| Long-CoT models effectively search on small items | Size sweeps beyond what the token budget can cover; report tokens used |
| API nondeterminism and silent model updates | Run manifests with exact version strings; repeats; date every run |
| O1 slides into philosophy | Keep it to a page; let measured item hardness carry the weight |
| Interp findings on open models may not transfer to frontier models | State the scope; look for behavioural signatures shared by open and closed models |
| Cost | Pilot first; item counts set by power analysis on pilot effect sizes |

---

## 9. Open questions for Andrew

1. Is "the RASP-L paper" Zhou et al. 2024, *What Algorithms can Transformers Learn?*
2. Which two domains for the pilot? Proposed: entailment and 3-SAT.
3. Who is on this? Do the v1 co-authors (Oxford HAI Lab) stay involved? The repo is public.
4. Names for the new repo and the Python package.
5. Runner: a thin custom runner, or Inspect AI?

---

## 10. References

- Belrose et al. (2023). *Eliciting Latent Predictions from Transformers with the Tuned Lens.*
- Chen et al. (2024). *Premise Order Matters in Reasoning with Large Language Models.* ICML.
- Dziri et al. (2023). *Faith and Fate: Limits of Transformers on Compositionality.* NeurIPS.
- Fan et al. (2024). *NPHardEval.* ACL.
- Feng et al. (2023). *Towards Revealing the Mystery behind Chain of Thought: A Theoretical Perspective.* NeurIPS.
- Garey & Johnson (1979). *Computers and Intractability.*
- Geiger et al. (2021). *Causal Abstractions of Neural Networks.* NeurIPS.
- Gigerenzer, Todd et al. (1999). *Simple Heuristics That Make Us Smart.*
- Johnson-Laird (2006). *How We Reason.*
- Koralus (2022). *Reason and Inquiry: The Erotetic Theory.* OUP.
- Lawsen (2025). *The Illusion of the Illusion of Thinking* (comment on Shojaee et al.).
- Lieberum et al. (2024). *Gemma Scope.*
- Lindner et al. (2023). *Tracr: Compiled Transformers as a Laboratory for Interpretability.* NeurIPS.
- Lindsey et al. (2025). *On the Biology of a Large Language Model.* Transformer Circuits.
- Liu et al. (2023). *Transformers Learn Shortcuts to Automata.* ICLR.
- McCoy et al. (2024). *Embers of Autoregression.* PNAS.
- Merrill & Sabharwal (2023). *The Parallelism Tradeoff: Limitations of Log-Precision Transformers.* TACL.
- Merrill & Sabharwal (2024). *The Expressive Power of Transformers with Chain of Thought.* ICLR.
- Mitchell, Selman & Levesque (1992). *Hard and Easy Distributions of SAT Problems.* AAAI.
- Myung & Pitt (2009). *Optimal Experimental Design for Model Discrimination.* Psychological Review.
- Nikankin et al. (2025). *Arithmetic Without Algorithms: Language Models Solve Math with a Bag of Heuristics.* ICLR.
- Richardson, Kearns, Moss, Wang-Maścianica & Koralus (2025). *Theory-Grounded Evaluation of Human-Like Fallacy Patterns in LLM Reasoning.* arXiv 2506.11128.
- Shojaee et al. (2025). *The Illusion of Thinking.*
- Valmeekam et al. (2023). *PlanBench.* NeurIPS Datasets & Benchmarks.
- Weiss, Goldberg & Yahav (2021). *Thinking Like Transformers.* ICML.
- Williams, Gomes & Selman (2003). *Backdoors to Typical Case Complexity.* IJCAI.
- Wu et al. (2023). *Interpretability at Scale: Identifying Causal Mechanisms in Alpaca.* NeurIPS.
- Zhang et al. (2023). *On the Paradox of Learning to Reason from Data.* IJCAI.
- Zhou et al. (2024). *What Algorithms can Transformers Learn? A Study in Length Generalization.* ICLR.
