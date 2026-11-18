# Literature Review

*For [DESIGN.md](DESIGN.md). Written 2026-11-13. The full reports are in [literature/](literature/).*

## How this review was done

Six research agents each took one slice of the design. A–D came first; E and F were added for Steps 1 and 2 of the plan:

| Slice | Objectives | Report | Papers |
|-------|-----------|--------|--------|
| A. Hardness and compute | O1, O2, H3 | [A_hardness_compute.md](literature/A_hardness_compute.md) | ~43 |
| B. Heuristics in LLM behaviour | O3, O4, H1, H4, H6 | [B_heuristics_behaviour.md](literature/B_heuristics_behaviour.md) | ~35 |
| C. Interpretability of reasoning and search | O5, H5 | [C_interpretability.md](literature/C_interpretability.md) | ~50 |
| D. RASP / RASP-L and algorithm learning | O6, H2 | [D_rasp_algorithms.md](literature/D_rasp_algorithms.md) | ~40 |
| E. Modelling the world as NP-hard | Step 1 (O1) | [E_world_as_np_hard.md](literature/E_world_as_np_hard.md) | ~45, plus a 42-row catalogue of real task → formal problem → complexity |
| F. Classes of heuristics for NP-hard problems | Step 2 (O3 zoo, O6) | [F_heuristic_classes.md](literature/F_heuristic_classes.md) | ~90 |

**How far to trust it.**

- **Provenance.** Each agent was told to cite only papers it actually found by search or fetch.
- **Coverage.** All four ran out of web-search budget near the end. The thinnest areas are 2026 work on biases in reasoning models, and optimal design or strategy classification applied to LLMs.
- **Spot-checks.** The claims that most affect novelty were checked against the source:

| Claim | Checked against | Result |
|-------|-----------------|--------|
| Zhou et al. 2024 state a "RASP MDL principle" | PDF | **Confirmed verbatim:** "Transformers tend to learn the shortest RASP-L program which fits the training set." |
| EHOP covers coloring, knapsack and TSP with greedy baselines and inverted variants | PDF | **Confirmed.** Its §5.3 is titled "LLMs rarely beat greedy heuristics". |
| AlgoTrace finds and steers a nearest-neighbour primitive on TSP | HTML full text | **Confirmed.** It measures "%NN paths"; injecting the NN vector raises them by 56%. |
| Ye et al. 2025: within depth capacity → exact algorithm; beyond → node-degree heuristic | Abstract | **Confirmed** |
| Sutter et al. 2025: non-linear causal abstraction is trivial (100% on IOI with random-init models) | Abstract | **Confirmed** (NeurIPS 2025 Spotlight) |
| Hazra et al. 2025: DeepSeek-R1 differs from other LLMs on 3-SAT, which rely on statistical features | Abstract | **Confirmed.** The details about DPLL traces and GPT-4o greedy search are in the agent's reading of the full text and were not re-checked. |
| Pan et al. 2025: a transformer decides 3-SAT via backtracking in CoT | Abstract | **Confirmed.** Agent A read the step bound (p·2^(p+1)) in the PDF; I did not re-check it. arXiv lists the paper as a preprint; the ICML 2025 venue is per the agent. |

Treat any other detail in the full reports as a lead to confirm before citing it in a paper.

---

## 1. Bottom line

**Already known.**

- **LLMs fall back on greedy-looking procedures on NP-hard problems.** EHOP shows this on coloring, knapsack and TSP; GraphArena on graph problems; Hazra et al. 2025 on 3-SAT; Saparov & He 2023 on proof search. All of these infer it from accuracy, or from reading traces.
- **Accuracy collapses past a size threshold.** Thinking tokens rise, then fall before the budget runs out (Shojaee et al. 2025; Estermann & Wattenhofer 2025; NPPC; Rameshkumar et al. 2025).
- **The complexity theory behind O2 is settled.** Without chain of thought, a transformer is limited to TC⁰. With polynomially many CoT steps it can do exactly P. With exponentially many it can decide 3-SAT by search (Pan et al. 2025).
- **"Transformers learn the shortest RASP-L program that fits the training set"** is Zhou et al.'s own toy model. Ye et al. 2025 show the "beyond capacity → heuristic" case for graph connectivity.
- **Circuits for propositional and syllogistic inference in open LLMs are published** (Hong et al. 2025; Kim et al. 2025).

**Still open, and the project's contribution.**

1. **Identification.** Deciding between *competing* heuristics from instance-level *answers*, with noisy-execution likelihoods, chance baselines, information-gain item selection, manipulation signatures and recovery tests.
   - Strategy taxonomies for LLM deduction so far come from reading traces (Mondorf & Plank 2024) or from fitting one cognitive model (Eisape et al. 2024).
   - The answer-based strategy-classification methods from decision research (Bröder & Schiffer 2003; Glöckner 2009; Davis-Stober & Brown 2011) were not found applied to LLMs.
2. **The imperfect-fit regime of the RASP MDL principle.** NP-hard tasks, where no short program fits exactly, and the two-part-MDL trade-off that decides which heuristic is learned.
3. **Mechanistic tests that adjudicate between heuristics.** Probing for a heuristic's state on NP-hard instances in pretrained LLMs, and premise-order patching. Neither was found in prior work.

---

## 2. Novelty map

| Planned element | Closest prior work | Status | What remains ours |
|-----------------|--------------------|--------|-------------------|
| LLMs on random 3-SAT near the phase transition | Hazra et al. 2025 (COLM); Zhang, Chen & Chen 2026 (FSE; matched SAT/UNSAT pairs) | Taken | Identification against competing heuristics; signatures; `DPLL-b` |
| "LLMs default to greedy" on NP-hard problems | GraphArena (ICLR 2025); EHOP; Hazra et al.; Saparov & He | Claimed qualitatively | Discriminating *between greedy variants*, item by item |
| Coloring / knapsack / TSP with greedy baselines, realistic framings, inverted rules | EHOP (Findings of EMNLP 2025) | Largely taken | Greedy-vs-greedy items; mixture weights; signatures |
| Nearest neighbour on TSP: behaviour and steering | AlgoTrace (Lippl et al. 2025) | Taken | Not our showcase |
| Accuracy and token use vs. size | Shojaee et al.; Estermann & Wattenhofer; NPPC; Rameshkumar et al. | Taken | Centring sweeps on each model's budget line |
| Cross-representation consistency via reductions | Zhang, Chen & Chen 2026 (75–80% agreement across reductions) | First result exists | Consistency of *heuristic family*, not just of answers |
| Strategy identification for LLM deduction | Mondorf & Plank 2024; Eisape et al. 2024; Bertolazzi et al. 2024 | Partly (traces / single model) | Answer-based likelihood strategy classification with competitors |
| Human-likeness of LLM errors | Koralus & Wang-Maścianica 2023; v1; Hagendorff et al. 2023 (biases disappear in GPT-4) | Mixed evidence | Competitors; allow an inverted U |
| Logic circuits in open LLMs | Hong et al. 2025; Kim et al. 2025 | Taken | Adjudicating competing heuristics on disagreement items |
| Probing a heuristic's internal state | Sudoku candidate sets, reachability, chess look-ahead, Blocksworld probes; Sasaki et al. 2026 (cue heuristics in a pretrained LM) | Precedents in other domains | NP-hard instances in pretrained LLMs: none found |
| Premise-order mechanism | Chen et al. 2024 (behaviour only); Kim et al. 2025 (first-premise stage) | Open | Patching forward vs. reversed premises; run early |
| Shortest-program hypothesis | Zhou et al. 2024 (RASP MDL toy model) | Taken | Imperfect-fit / two-part MDL; identification from errors |
| Beyond capacity → heuristic | Ye et al. 2025 (graph connectivity) | Taken for connectivity | NP-hard tasks; frontier across a zoo |
| SAT + compiled transformer + training on traces | Pan et al. 2025 (PARAT) | Taken | What trained models do beyond trained sizes |
| Decompiling trained transformers to RASP | Huang et al. 2026 (ICML) | Tool exists | Apply it to NP-hard toy tasks; their null is our falsifier |
| Mixtures of readable heuristic programs fitted to neural combinatorial-optimisation solvers | "EPB" (NeurIPS 2026, per agent D; no link captured, unverified) | Close, if confirmed | LLMs; RASP-L length; fixed theory-driven zoo |
| Automated strategy discovery | AutoCog (Jagadish et al. 2026) | Adjacent | Could become a competing engine; borrow its recovery tests |

**Who is closest:** EHOP (Brown/Saarland), Hazra et al. (KU Leuven), AlgoTrace (Microsoft Research et al.), Ye et al. (USC), and the Hahn lab (Saarland: decompiler, C-RASP theory, CoT lower bounds). Moving the identification pilot quickly is the main defence.

---

## 3. Findings by objective

### O1: real-world hardness
- Most real-world graph and proof instances fall within reasoning models' success range, with a long tail outside it (Rameshkumar et al. 2025).
- Solver hardness doesn't predict model errors: there is no pooled accuracy gap between proof-hard and proof-easy UNSAT formulas at matched density (Verma 2026). So measure hardness relative to the heuristic zoo as well.
- Answer the van Rooij, Wright & Wareham (2012) objection directly; see DESIGN §3 O1.
- Frameworks and a 42-row catalogue of real task → formal problem are in report E (§6).

### O2: bounded compute
- The theory is settled: Merrill & Sabharwal 2023 (log-space-uniform TC⁰), 2024 (CoT → P, under generalized pre-norm) and 2025 (padding alone stays in TC⁰); Li et al. 2024 (AC⁰ at constant precision); Amiri et al. 2025 (linear CoT lower bounds).
- The converse is the important correction: Pan et al. 2025 show exact search is expressible with exponential CoT. The operative quantity is the token budget relative to the size of the search.
- R1 does near-exact search on small instances. Several threats bear on H3:
  - more thinking can *hurt* (Gema et al. 2025; Ghosal et al. 2025);
  - noisy execution of an exact algorithm also predicts accuracy falling with size (Sinha et al. 2025).
- Structured errors are documented qualitatively:
  - over-predicting SAT (Zhang, Chen & Chen 2026);
  - hallucinated edges (GraphArena; Heyman & Zylberberg 2025);
  - "UNSAT because complex" (Hazra et al.);
  - plans produced for unsolvable instances (Valmeekam et al. 2024).

### O3 / O4: identifying heuristics from behaviour
- LLM answers are often infeasible or near-misses, so exact-match agreement with a heuristic would leave most errors unexplained. Use noisy-execution likelihoods.
- The decision-research toolkit transfers directly:
  - Bayesian strategy classification (Bröder & Schiffer 2003);
  - multiple-measure strategy classification with process measures (Glöckner 2009);
  - multiple stochastic specifications (Davis-Stober & Brown 2011);
  - optimal design for model discrimination (Myung & Pitt 2009).
- H4 (consistent heuristic family across domains) faces contrary evidence: strategy depends strongly on presentation (EHOP; Hazra et al.). Test consistency within a domain across framings first.
- H6 (human-likeness) has evidence both ways:
  - for: Koralus & Wang-Maścianica 2023; Eisape et al. on PaLM 2;
  - against: Hagendorff et al. 2023; Eisape et al.'s null on Llama 2.

  Allow a non-monotone capability trend.

### O5: interpretability
- LLMs don't adapt depth to difficulty (Csordás et al. 2025; Hu et al. 2025). So "the answer is decodable early, regardless of size" doesn't separate a heuristic from a failing exact procedure.
- Causal abstraction with non-linear maps is trivially satisfiable (Sutter et al. 2025), and explanations can be non-identifiable (Méloux et al. 2025). Use linear interventions, competing-heuristic controls and random-init controls.
- Neuron-level and representation-level analyses can reach opposite verdicts on the same task (Nikankin et al.'s bag of heuristics vs. helix-style accounts). Pre-specify the level of analysis.
- Tooling is good: circuit-tracer transcoders exist for Qwen3 0.6–14B, Gemma-2-2B, Gemma 3 (Gemma Scope 2), Llama-3.2-1B and Llama-3.1-8B-Instruct. Qwen3 is the best primary model, because one checkpoint has thinking and non-thinking modes.
- Better positive controls than raw Tracr: InterpBench (SIIT), ALTA (loops), MIB (benchmark), and a Ye-style capacity toy.
- In reasoning models, answers are often decodable before the chain of thought and can be steered (Cox et al. 2026). Written traces are often unfaithful.

### O6: RASP-L
- The RASP-Generalization Conjecture has three conditions (realizability, simplicity, diversity) and is explicitly phenomenological.
- Formal follow-ups: C-RASP and limit transformers (Huang et al. 2025); length-generalisation bounds are uncomputable and sample size grows exponentially in the minimal program's size (Yang et al. 2026); a decompiler (Huang et al. 2026).
- Contrary results:
  - ALTA: learned behaviour follows the fewest-*layers* program, not the fewest-rules one.
  - Huang et al. 2026: models that don't length-generalise usually aren't short programs.
  - Shaw et al. 2026: standard optimisers don't find MDL-optimal solutions.
- Many zoo heuristics (greedy, nearest neighbour, DSATUR, WalkSAT) are sequential, i.e. not constant-depth RASP-L. They are available only with CoT or looping (n-RASP-L, Fan et al. 2025). That is why the zoo has a C/S class column.

---

## 4. What changed in DESIGN.md (v0.1 → v0.2)

1. **§1 positioning.** Prior work is named and the contribution is stated as identification. The RASP-L extension is stated as the imperfect-fit regime.
2. **O2.**
   - Precise complexity statements: log-space-uniform TC⁰; AC⁰; padding; generalized pre-norm.
   - Feng et al. moved to the direct-answer case it actually supports.
   - Added the Pan et al. converse and the **budget line** *n\**.
   - Separated worst case from our distribution.
   - New rules: small outputs, solvability checks, censoring, a "declared impossible" category, matched SAT/UNSAT pairs.
3. **O1.** Three hardness axes, including heuristic-relative hardness. Rameshkumar et al. and van Rooij et al. addressed.
4. **O3.**
   - C/S expressibility class column.
   - Zoo additions: `ALWAYS-SAT`, `DENSITY`, `PURE-LITERAL`, `MOMS`, `DPLL-b`, `NOISY-EXACT`, `HALLUC-CONSTRAINT`, `ATMOSPHERE`, `TEXTBOOK-TRANSFER`, `RANDOM-ORDER-FIRST-FIT`, `NN-from-0`, `FARTHEST-INSERTION`.
   - Noisy-execution likelihoods.
   - Decision-research strategy classification.
   - Process measures.
   - Greedy-vs-greedy item selection.
   - Rule inversion as a manipulation.
5. **O4.** Prior work per domain; TSP demoted as a showcase; planning sizes adjusted.
6. **O5.**
   - Qwen3 as primary model; corrected Gemma Scope coverage.
   - Replaced the logit-lens prediction.
   - Linear-only interventions with competing-heuristic and random-init controls.
   - Bag-of-heuristics alternative.
   - Thinking-model pre-commitment.
   - Premise-order patching.
   - SIIT, ALTA, MIB and capacity-toy controls.
7. **O6.**
   - Conjecture conditions and the RASP MDL toy model credited.
   - Two-part MDL objective.
   - Data-size prediction and decompiler test.
   - Pre-registered length measure and encoding.
   - Rival complexity measures.
   - Toy-model vs. LLM scope.
8. **§4 hypotheses.**
   - H1 uses likelihoods.
   - H2 restated for the imperfect-fit regime.
   - H3 restated around search budget *b*, with non-monotone effects allowed.
   - H4 within-domain first.
   - H5 split into a, b, c and an alternative.
   - H6 allows an inverted U.
9. **§7–§9.** Scooping risk; Qwen3-first interpretability; open questions updated (RASP-L paper confirmed; repo named).

## 5. Citation corrections applied

| Entry | Fix |
|-------|-----|
| Feng et al. 2023 | Was cited for "CoT stays in P"; it actually shows bounded-depth transformers can't answer arithmetic directly. Moved. |
| Merrill & Sabharwal 2023 / 2024 | Log-space-uniform TC⁰; the exact-P result needs generalized pre-norm |
| Shojaee et al. 2025 | Full title; NeurIPS 2025 |
| Lawsen 2025 | Listed as "Comment on The Illusion of Thinking" (arXiv 2506.09250); not peer-reviewed |
| NPHardEval, PlanBench, McCoy et al. | Full titles |
| Williams, Gomes & Selman 2003 | Supports backdoors only, not "low treewidth" |
| Geiger et al. / Wu et al. | DAS comes from Geiger, Wu, Potts, Icard & Goodman 2023 (arXiv 2303.02536); Wu et al. 2023 introduced *Boundless* DAS |
| Lindsey et al. 2025 | Add Ameisen et al. 2025 for the attribution-graph method |
| Gemma Scope | Full title; covers Gemma 2 only (Gemma 3 is covered by Gemma Scope 2) |
| Belrose et al. 2023 | arXiv only |
| Gigerenzer & Todd | "Gigerenzer, Todd & the ABC Research Group (1999)" |
| Koralus | Online Dec 2022, print 2023 |
| Richardson et al. 2025 | ICLR 2026; v1 had a different title |
| Zhou et al. 2024 | Disambiguate from a separate Zhou et al. 2024 (arXiv 2402.09371) |

## 6. Steps 1 and 2: reports E and F

These two are summarised briefly here. Their content is worked into [PAPER_SKELETON.md](PAPER_SKELETON.md) §3 (frameworks and formal models) and §5 (heuristic families).

**E. Modelling the world as NP-hard.**

- **Lead with generality.** General capacities across perception, reasoning, categorisation, decision-making and planning come out NP-hard when stated in full (van Rooij 2015).
- **Deduction is the mildest case.**
  - Abduction is "harder than deduction" (Eiter & Gottlob 1995).
  - Bayesian inference and MPE are NP-hard even to approximate (Cooper 1990; Dagum & Luby 1993; Kwisthout et al. 2011).
  - Planning is PSPACE-complete; Nash equilibrium is PPAD-complete.
- **Satisficing doesn't escape.** *Feasibility* alone is NP-complete for timetabling, configuration, Minesweeper and Latin-square completion.
- **Humans show the same pattern:** accuracy falls with instance hardness (Murawski & Bossaerts 2016; Franco et al. 2022).
- **Five frameworks:** computational-level intractability; reduction catalogues; bounded and resource rationality; parameterized complexity; beyond-worst-case.
- **Counterargument:** "real instances have structure". Replies: structure isn't sufficient (Mull et al. 2016), and solver-easy isn't budget-easy.
- **Recent LLM papers assert the premise without defending it** (EHOP, NPHardEval, NPPC, NATURAL PLAN, TravelPlanner).
- **Two O1-table rows in DESIGN v0.2 need a source or should be dropped:** monadic first-order logic (NEXPTIME) and register allocation.

**F. Classes of heuristics.**

- **Families by mechanism:** A cue/substitution; B simplified model (relax / abstract / convex / restrict / probabilistic); C constructive/priority; D systematic search; E message passing; F local search; G decomposition/DP; H guess/sample; I meta-level.
- **Formal models with lower bounds:** priority algorithms, pBT, the LOCAL model (equivalent to GNNs; Sato et al. 2019), low-degree polynomials, PLS.
- **Pearl (1983):** heuristics come from relaxed, restricted (over-constrained) or probabilistic simplified models. On the report's reading, relaxations err by omission and restrictions by commission, so ETR, MM, FIRST and MATCH are restrictions.
- **Citable depth labels** come from the P-completeness compendium (Greenlaw, Hoover & Ruzzo).
  - P-complete: lexicographically-first greedy colouring (`FIRST-FIT`), the nearest-neighbour TSP tour, first-fit-decreasing bin packing, unbounded unit/Horn resolution, exact LP.
  - Random-order greedy is polylog depth (Blelloch et al. 2012).
  - Hence a three-way depth split, const / polylog / seq.
  - *Not re-checked by me; these are standard results, but confirm the compendium entry numbers before citing.*
- **Random-instance thresholds give signatures:** unit clause ≈ 8/3 and optimal myopic 3.26 on 3-SAT; greedy colouring ≈ 2χ; BP-decimation ≈ 2^k/k.
- **New item types:** depth-stress items built from P-completeness gadgets (a direct const-vs-seq test); threshold knees; violation profiles; feature-dependent mixture weights (Rice).

## 7. Still to check

- **Confirm before citing in a paper:**
  - Pan et al.'s step bound and venue;
  - Hazra et al.'s trace-level claims;
  - "EPB" (NeurIPS 2026);
  - AutoCog's details;
  - any numbers quoted only in the agent reports.
