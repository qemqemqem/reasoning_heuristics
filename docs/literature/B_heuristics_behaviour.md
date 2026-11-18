> Research-agent report written 2026-11-13 for the literature review in [../LITERATURE.md](../LITERATURE.md). Every paper was found by web search or fetch during the review; the most decision-relevant claims were then spot-checked against the source (see LITERATURE.md, "How this review was done"). Treat other details as leads to confirm before citing.

# Lit review slice B: behavioural evidence about which heuristics LLMs use

*Scope: DESIGN.md §3 O3 and O4, and §4 H1, H4 and H6. Compiled 2026-11-13.*

**Coverage caveat.** The session's shared web-search budget ran out after about 45 searches in this slice. After that, I only fetched specific arXiv or ACL pages for papers I had already surfaced, or recalled and then verified by fetching. Two areas are under-searched as a result: (a) 2026 work on cognitive biases in reasoning models, and (b) optimal design or strategy classification applied to LLMs. Treat "I found nothing" in those two areas as moderate-confidence, not a confirmed gap.

Convention: **Claim** is what the paper says. **Read** is my interpretation for this project.

---

## Summary

- **The headline "LLMs act greedily on NP-hard problems" is already published, more than once.**
  - GraphArena (ICLR 2025) on graph NP-complete tasks.
  - EHOP / "A Knapsack by Any Other Name" (Findings of EMNLP 2025) on graph coloring, knapsack and TSP.
  - Saparov & He (ICLR 2023) for proof planning ("Language Models Are Greedy Reasoners").
  - Hazra et al. (COLM 2025): GPT-4o does "greedy search without backtracking" on 3-SAT.

  None of them measures instance-level agreement with competing heuristics, chance baselines or manipulation signatures. That is the gap we can own.
- **EHOP is the closest overlap with O4 domains 3–5.** It has the same three problems and the same classic greedy baselines (largest-degree-first first-fit, density ratio, nearest neighbour). It renders textbook, real-life ("costumed") and inverted framings, and has a "HARD" split of items the greedy baseline gets wrong. Its claim that LLMs "primarily follow a greedy strategy" rests only on aggregate accuracy on that split.
- **AlgoTrace (arXiv 2510.15987, v3 Aug 2026) already identifies nearest neighbour in LLM TSP outputs.** It counts the share of paths that are NN paths, measured by edit distance. It also steers the behaviour causally with a "nearest_neighbor" primitive vector (Phi-4, Qwen, Llama), and has 3-SAT strategy clusters. This pre-empts NN-on-TSP as a flagship demonstration for O5/H5.
- **Cognitive-science strategy identification has been applied to LLM deduction, but at the process level, not with outcome-based likelihood.**
  - Mondorf & Plank (ACL 2024) hand-annotated chain-of-thought (CoT) traces against human propositional-reasoning strategies (Van der Henst et al. 2002).
  - Eisape et al. (NAACL 2024) projected LLM syllogism responses into the parameter space of mReasoner, the mental-models program.
  - Bertolazzi et al. (EMNLP 2024) explained LLM syllogism errors with cognitive heuristics.

  I found nobody applying Bröder-style strategy classification, mixture models or Myung–Pitt optimal design to LLMs as subjects.
- **H1 (a few heuristics explain most errors) has qualitative support, and one structural threat.**
  - Support: greedy (EHOP, GraphArena, Hazra), NN (AlgoTrace) and atmosphere-like heuristics (Bertolazzi).
  - Threat: many LLM answers are *infeasible*. GraphArena counts these as "hallucinatory". Classic heuristics always return feasible solutions. Exact-match agreement `1[y = h(x)]` will therefore leave most error mass "unexplained" even when a model is basically running a heuristic. We need graded (noisy-execution) likelihoods.
- **H4 (the same heuristic family across domains) has weak priors and mostly contrary evidence.**
  - Against: strategy and accuracy depend on presentation within a single problem (EHOP costumes and inversions; Hazra's SAT-CNF vs SAT-Menu framings; Wu et al.'s counterfactual tasks). Bias expression is prompt-sensitive and inconsistent (Macmillan-Scott & Musolesi 2024; Knipper et al. 2025).
  - For: AlgoTrace's cross-task transfer of primitive vectors is the main evidence.
- **H6 (cognitive heuristics beat surface ones, increasingly with capability) has precedents on both sides.**
  - For: Koralus & Wang-Maścianica 2023 (ETR-predicted answers rise from GPT-3 to GPT-4); Eisape et al. 2024 (larger PaLM 2 models' errors look more like deliberative mental-model reasoning); content-effect parallels (Lampinen/Dasgupta et al. 2024).
  - Against:
    - Hagendorff et al. 2023: human-like intuitive errors appear and then *disappear* in ChatGPT/GPT-4.
    - Macmillan-Scott & Musolesi 2024: LLM errors differ from human biases.
    - Eisape et al.: the Llama 2 scale effect vanishes once accuracy is controlled.
    - McCoy et al. 2024: probability (surface) sensitivity persists in o1.

  Expect a non-monotone relationship, and pre-register which zoo heuristics count as "cognitive" and which as "surface".
- **The v1 ETR paper (arXiv 2506.11128, ICLR 2026) has almost no external uptake.** Semantic Scholar lists two citing papers: NeuReasoner, which uses ETR as a prompting "lens" (COLM 2026 workshop), and an unrelated retrieval paper. I found no critiques and no follow-ups.
- **Reusable method stack from judgement and decision-making research:**
  - Bröder & Schiffer 2003: outcome-based Bayesian strategy classification with a per-strategy error rate.
  - Glöckner 2009: multiple-measure maximum likelihood, adding times and confidence. For LLMs, the analogues are reasoning tokens and log-probabilities.
  - Davis-Stober & Brown 2011: "one strategy plus error" vs "mixture" stochastic specifications, compared with normalised maximum likelihood.
  - Myung & Pitt 2009: optimal design for model discrimination.
  - AutoCog (Jagadish et al. 2026): closed-loop recovery of strategies from simulated behaviour, a precedent for our positive controls.
- **Citations in my slice are essentially correct.** Fixes are minor: the full PNAS title for McCoy et al.; "& the ABC Research Group" for Gigerenzer & Todd; the Koralus print year; and ICLR 2026 for our own v1 paper.

---

## Key papers

S = supports, C = contradicts, O = overlaps our plan (novelty risk), R = resource or method.

### A. Heuristics on combinatorial and NP-hard problems

| Citation | Link | Claim (what the paper says) | Relevance (my read) | S/C/O |
|---|---|---|---|---|
| Duchnowski, Pavlick & Koller (2025). *A Knapsack by Any Other Name: Presentation impacts LLM performance on NP-hard problems* (EHOP). Findings of EMNLP 2025. (v1 title: "EHOP: A Dataset of Everyday NP-Hard Optimization Problems".) | https://arxiv.org/abs/2502.13776 · https://aclanthology.org/2025.findings-emnlp.352/ | **Setup:** graph coloring, knapsack and TSP, each as textbook, real-life "costumed" and inverted variants. Models: GPT-4o, Llama 3.1 70B, Qwen3-32B, DeepSeek R1.<br>**Presentation effect:** textbook versions are solved optimally more often than inverted or costumed ones, "often by more than 20 percentage points". R1 and Qwen3 in thinking mode show no systematic drop but large fluctuations.<br>**Greedy baselines:** largest-degree-first first-fit coloring, density-greedy knapsack, nearest-neighbour TSP. Greedy is near-optimal on coloring, beats CoT on knapsack, and matches it on TSP.<br>**EHOP-HARD** (items the greedy baselines don't solve optimally): LLM-only approaches drop and are beaten even by *weak* greedy baselines (random-order coloring, value-first knapsack). The authors call this "further evidence … that they primarily follow a greedy strategy". | Same domains, same baselines and same framing manipulation as our O4 domains 3–5. The greedy claim is inferred from accuracy, not from instance-level agreement. The inverted variants make "approximate retrieval" operational: solve the textbook version and report it. | **O** (strong), S (H1), C (H4) |
| Tang et al. (2025). *GraphArena: Evaluating and Exploring LLMs on Graph Computation.* ICLR 2025. | https://arxiv.org/abs/2407.00379 | **Scope:** 4 polynomial-time and 6 NP-complete graph tasks.<br>**Claim:** on NP tasks LLMs "typically default to greedy algorithms", sometimes using better approximations.<br>**Output categories:** correct, suboptimal, hallucinatory (well-formed but infeasible), missing.<br>**GPT-4o vs greedy (win/tie/lose %):** TSP small 23.6/49.0/27.4, TSP large 18.8/4.2/77.0, MIS large 0/5.4/94.6. | The paper never says how "defaults to greedy" was established; its evidence is win/tie/lose comparisons. The "hallucinatory" category shows infeasible outputs are common, so exact-match heuristic agreement will under-explain errors. | O, S (H1, weak) |
| Lippl, McGee, … Eberle & Momennejad (2025; v3 Aug 2026). *AlgoTrace: Algorithmic Primitives and Compositional Geometry of Reasoning in Language Models.* arXiv preprint, no venue listed. | https://arxiv.org/abs/2510.15987 | **Method:** clusters activations on TSP, 3-SAT, AIME and graph navigation, labels the clusters from trace tokens, and extracts "primitive vectors".<br>**Steering:** injecting `nearest_neighbor` raises the share of NN paths by +56.1%.<br>**Behaviour:** Phi-4-Reasoning "begins with the NN heuristic much more frequently than Phi-4-Base, especially when >8 cities". NN is detected by edit distance to the NN tour starting from city 0, within the first five generated paths.<br>**3-SAT:** clause-based (`if_clause_true`) vs variable-assignment brute-force (`if_variable_true`) clusters.<br>**Transfer:** primitives transfer across tasks. | Behavioural *and* causal identification of a named heuristic (NN) in open models: direct overlap with O3+O5/H5 for TSP. The graded-agreement method (edit distance, first k paths) is worth copying. Cross-task transfer of primitives is the best evidence I found *for* H4. | **O** (strong), S (H1, H3, H4) |
| Hazra, Venturato, Zuidberg Dos Martires & De Raedt (2025). *Have Large Language Models Learned to Reason? A Characterization via 3-SAT Phase Transition.* COLM 2025. | https://arxiv.org/abs/2504.03930 | **Phase transition:** all models show an "inverted phase transition" on random 3-SAT, with accuracy dropping near αc≈4.27, "where statistical features are largely absent".<br>**R1's traces:** unit-clause and pure-literal elimination, MOMS, lookahead, unit propagation, backtracking and backjumping. Failures: incompleteness (stops early) and limited soundness (overlooks clauses).<br>**GPT-4o:** "performs a greedy search without backtracking".<br>**Format:** R1 is worse on the natural-language SAT-Menu framing than on CNF. | Ready-made SAT zoo candidates (PURE-LITERAL, MOMS, truncated DPLL). Trace coding is qualitative, not answer-based identification. Format dependence argues against H4. | O (partial), S (H1, H3), C (H4) |
| Saparov & He (2023). *Language Models Are Greedy Reasoners: A Systematic Formal Analysis of Chain-of-Thought.* ICLR 2023. | https://arxiv.org/abs/2210.01240 | PrOntoQA. InstructGPT and GPT-3 make correct individual deduction steps but struggle with "proof planning" and don't systematically explore the alternatives when several valid steps are available. | Prior art for "greedy, no backtracking" in deduction. Cite it under GREEDY. | S (H1), O (terminology) |
| Fan et al. (2024). *NPHardEval: Dynamic Benchmark on Reasoning Ability of LLMs via Complexity Classes.* ACL 2024. | https://arxiv.org/abs/2312.14890 | 900 algorithmic questions across P, NP-complete and NP-hard, regenerated monthly. | Accuracy-only; useful as a source of instance generators and as a contrast ("we measure *which* procedure, not *whether* correct"). | R |

### B. Shortcuts, surface cues, frequency and retrieval

| Citation | Link | Claim | Relevance | S/C/O |
|---|---|---|---|---|
| Chen, Chi, Wang & Zhou (2024). *Premise Order Matters in Reasoning with Large Language Models.* ICML 2024. | https://arxiv.org/abs/2402.08939 | Permuting premises drops accuracy by more than 30%. Models do best when premise order follows the order of the proof's steps. Introduces the R-GSM benchmark. | A ready manipulation: the PRIMACY / INPUT-ORDER signature. Note the effect is measured relative to *proof order*, not to surface position, which matters for which heuristic each order effect diagnoses. | S, R |
| McCoy, Yao, Friedman, Hardy & Griffiths (2024). *Embers of autoregression show how large language models are shaped by the problem they are trained to solve.* PNAS 121(41): e2322420121. | https://arxiv.org/abs/2309.13638 | Accuracy depends on the probability of the task, the output and the input. GPT-4 on a cipher: 51% for high-probability outputs vs 13% for low-probability ones. | Basis for the FREQ / LENGTH-PRIOR heuristics. The method (vary output probability with the task fixed) is directly reusable as a manipulation. | S (surface heuristics), R |
| McCoy et al. (2024). *When a language model is optimized for reasoning, does it still show embers of autoregression? An analysis of OpenAI o1.* arXiv. | https://arxiv.org/abs/2410.01792 | o1 is still sensitive to output probability and uses more tokens on low-probability examples. Reasoning optimisation "can mitigate but might not fully overcome" the effect. | Surface sensitivity persists in reasoning models, which argues against a clean H3/H6 shift. Token count works as a process measure, analogous to Glöckner's decision times. | C (H6, partly), R |
| Wu et al. (2024). *Reasoning or Reciting? Exploring the Capabilities and Limitations of LMs Through Counterfactual Tasks.* NAACL 2024. | https://arxiv.org/abs/2307.02477 | Consistent degradation on counterfactual variants across 11 tasks. LMs "often also rely on narrow, non-transferable procedures". | Supports domain- and format-specific procedures, against H4. Template for the "inverted" manipulations. | C (H4), R |
| Ruis et al. (2025). *Procedural Knowledge in Pretraining Drives Reasoning in Large Language Models.* ICLR 2025. | https://arxiv.org/abs/2411.12580 | For reasoning queries, influential pretraining documents carry procedures (formulas, code) rather than answers. The same documents influence different queries of the same task type. | "Retrieval" means retrieving procedures, which favours a heuristic-zoo framing over pure answer lookup. Evidence is from math tasks only. | S (O3 framing) |
| Aoki et al. (2024). *First Heuristic Then Rational: Dynamic Use of Heuristics in Language Model Reasoning.* EMNLP 2024. | https://arxiv.org/abs/2406.16078 | Early in multi-step reasoning, LMs rely more on shallow heuristics such as lexical overlap. That reliance falls as they approach the answer, and they "dynamically combine heuristic strategies with rational ones". | Suggests the heuristic in use varies *within* an item, by step. Our per-item mixture assumption may be too coarse for CoT models. | S (H1, surface), C (single-strategy assumption) |
| Zhang, Li, Meng, Chang & Van den Broeck (2023). *On the Paradox of Learning to Reason from Data.* IJCAI 2023. | https://arxiv.org/abs/2205.11502 | BERT (and T5) trained on SimpleLogic reach near-perfect in-distribution accuracy but fail on other distributions over the same problem space, by exploiting statistical features. Jointly removing all such features is computationally infeasible. | Warns that **our own generators** will carry exploitable statistics. The zoo needs generator-specific "statistical feature" heuristics (e.g. predict from clause/variable ratio), and items should be checked against them. | S, R |
| Kambhampati et al. (2024). *Position: LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks.* ICML 2024. | https://arxiv.org/abs/2402.01817 | Autoregressive LLMs can't plan or self-verify by themselves; treat them as "approximate knowledge sources". | The "approximate retrieval" account. EHOP's inverted variants and our TEXTBOOK-TRANSFER proposal (below) make it testable rather than residual. | context |

### C. LLMs vs human biases and theories of reasoning

| Citation | Link | Claim | Relevance | S/C/O |
|---|---|---|---|---|
| Koralus & Wang-Maścianica (2023). *Humans in Humans Out: On GPT Converging Toward Common Sense in both Success and Failure.* arXiv. | https://arxiv.org/abs/2303.17276 | On 61 ETR problems (ETR61): ETR-predicted answers rise 59% (GPT-3) → 77% (GPT-3.5) → 75% (GPT-4). Human-like fallacious answers rise 18% → 33% → 34%. | Direct precursor of v1 and H6 (same group). Single-theory design: no competitors. | S (H6) |
| Richardson, Kearns, Moss, Wang-Maścianica & Koralus (2025). *Theory-Grounded Evaluation of Human-Like Fallacy Patterns in LLM Reasoning.* ICLR 2026. (v1 title: "Stronger Language Models Produce More Human-Like Errors".) | https://arxiv.org/abs/2506.11128 | 383 PyETR items, 38 models. The share of errors that are ETR-predicted fallacies correlates with Arena Elo (ρ=0.360, p=0.0265). Premise reversal reduces fallacies. | **Citations:** Semantic Scholar lists two: NeuReasoner (arXiv 2606.29971, COLM 2026 Workshop on Agent Behavior), which uses ETR as a prompting "Cognitive Lens", and an unrelated retrieval paper (arXiv 2602.23906). OpenAlex lists one. I found no critiques or replications. | own prior work |
| Eisape, Tessler, Dasgupta, Sha, van Steenkiste & Linzen (2024). *A Systematic Comparison of Syllogistic Reasoning in Humans and Language Models.* NAACL 2024. | https://arxiv.org/abs/2311.00445 | **Method:** instantiates 923 mReasoner (mental-models) parameter settings, runs PCA, and projects humans and PaLM 2 models into that space.<br>**Scale:** larger PaLM 2 models score higher on the deliberation component, "even the models' errors become more consistent with deliberative reasoning". For Llama 2 the size effect disappears once accuracy is controlled.<br>**Biases:** ordering effects run in the same direction as humans', with no clear trend in magnitude with size. Strong aversion to "nothing follows". | The closest precedent to H6 using the MM theory. Its method (place an LLM in a cognitive model's parameter space) is an alternative to our discrete zoo. The mixed scale result (PaLM 2 yes, Llama 2 no) is a warning for H6. | O, S/C (H6 mixed), R |
| Bertolazzi, Gatt & Bernardi (2024). *A Systematic Analysis of LLMs as Soft Reasoners: The Case of Syllogistic Inferences.* EMNLP 2024. | https://arxiv.org/abs/2406.11341 | Pretrained models' behaviour "can be explained by heuristics" from cognitive science. Content effects and avoidance of "nothing follows". In-context learning improves valid inferences, but only supervised fine-tuning removes most biases. (The atmosphere-heuristic fit for LLaMA-3 8B comes from a slide-deck summary; I didn't confirm it in the paper.) | A small heuristic-comparison study on LLM syllogisms. The atmosphere heuristic is a cognitive-science heuristic that is *surface* in kind (mood matching), so H6's cognitive-vs-surface split needs care. | O, C/S (H6) |
| Mondorf & Plank (2024). *Comparing Inferential Strategies of Humans and Large Language Models in Deductive Reasoning.* ACL 2024. | https://arxiv.org/abs/2402.14856 | **Method:** manual annotation of 300 CoT responses (Llama-2 7B/13B/70B, Mistral-7B, Zephyr-7B) on propositional problems, against Van der Henst et al. (2002) strategies; κ=0.98.<br>**Scale (Llama 2):** chain construction 20% → 36.7% → 50%; supposition following 20% → 28.3% → 45%; sound reasoning 0% → 31.7%.<br>**Reasoning vs answer:** correct answers often come from flawed reasoning (r=0.45 between correctness and soundness). LLMs never used the incremental-diagram strategy, which humans used 34% of the time. | Strategy identification for LLMs in our entailment domain, at the *process* level. Our outcome-based, competitor-controlled identification is still distinct. Supports H3 (strategy shifts with scale). | **O**, S (H3) |
| Lampinen, Dasgupta et al. (2024). *Language models show human-like content effects on reasoning tasks.* PNAS Nexus 3(7): pgae233. (The arXiv record lists Dasgupta first.) | https://arxiv.org/abs/2207.07051 | On natural language inference, syllogisms and the Wason task, LMs are more accurate when content supports the logic, as humans are. Model answer distributions also relate to human response times. | Supports our content/re-theming manipulation; human-like content effects. | S (H6 broadly), R |
| Hagendorff, Fabi & Kosinski (2023). *Human-like intuitive behavior and reasoning biases emerged in large language models but disappeared in ChatGPT.* Nature Computational Science 3: 833–838. | https://www.nature.com/articles/s43588-023-00527-x | On cognitive-reflection tests and semantic illusions, earlier GPT models make human-like intuitive errors and ChatGPT/GPT-4 largely avoid them. | Capability eventually *removes* human-like errors. That argues against a monotone "increasingly" in H6; expect an inverted U. | **C** (H6) |
| Macmillan-Scott & Musolesi (2024). *(Ir)rationality and cognitive biases in large language models.* Royal Society Open Science 11(6). | https://arxiv.org/abs/2402.09193 | Seven LLMs on 12 classic tasks. When they are wrong, it is "often … in ways that differ from human-like biases", and their responses are significantly inconsistent. | Against H6 (errors not human-like) and against H4 (inconsistent). | **C** (H6, H4) |
| Yax, Anlló & Palminteri (2024). *Studying and improving reasoning in humans and machines.* Communications Psychology. | https://arxiv.org/abs/2309.12485 | Most models make errors "akin to … heuristic-based human reasoning". The GPT-3/3.5 family shows bounded reasoning. Humans and LLMs respond differently to the same prompting schemes. | Mixed: heuristic-like errors, but different sensitivity to interventions. | S/C (H6) |
| Knipper et al. (2025). *The Bias is in the Details: An Assessment of Cognitive Bias in LLMs.* arXiv. | https://arxiv.org/abs/2509.22856 | 45 LLMs, 8 biases, 2.8M responses. Bias-consistent answers in 17.8–57.3% of instances. Models above 32B reduce bias in 39.5% of cases. Prompt detail changes biases by up to ±15%. | Bias expression is prompt-sensitive and only partly reduced by scale. Caution for H4/H6, and a reason for §5.10 (prompts as factors). | C (H4), mixed (H6) |
| Binz & Schulz (2023). *Using cognitive psychology to understand GPT-3.* PNAS 120(6). | https://arxiv.org/abs/2206.14576 | Treats GPT-3 as an experimental participant. It shows the conjunction fallacy, near-human decision-making, and is fragile to vignette changes. | Methodological ancestor of "machine psychology". | R |

### D. Identifying a strategy from answers

| Citation | Link | Claim | Relevance | S/C/O |
|---|---|---|---|---|
| Bröder & Schiffer (2003). *Bayesian strategy assessment in multi-attribute decision making.* J. Behavioral Decision Making 16(3): 193–213. | https://www.bohrium.com/paper-details/bayesian-strategy-assessment-in-multi-attribute-decision-making/812396875347918848-8940 | Outcome-based classification. Each candidate strategy predicts a choice vector and has a constant error rate; strategies are compared by likelihood or Bayes factors. Later work notes that simple "accordance rates" are biased when strategies tie or predict guessing. | This is O3's identification problem. Our EA metric is an accordance rate and inherits the bias; adopt their likelihood formulation. | **R** |
| Glöckner (2009). *Investigating intuitive and deliberate processes statistically: The multiple-measure maximum likelihood strategy classification method.* Judgment and Decision Making 4(3): 186–199. | https://www.cambridge.org/core/journals/judgment-and-decision-making/article/investigating-intuitive-and-deliberate-processes-statistically-the-multiplemeasure-maximum-likelihood-strategy-classification-method/FB063EDF9DF0756F359833F022025E95 | Adds decision times and confidence to choices in a joint maximum-likelihood fit. Simulations show it is unbiased and separates strategies when the time/confidence effects are large. | LLM analogues: reasoning tokens used (cf. McCoy-o1 token effects) and answer log-probability. Each heuristic predicts a cost profile (UP-k ∝ k; NN ∝ n²). | **R** |
| Davis-Stober & Brown (2011). *A shift in strategy or "error"? Strategy classification over multiple stochastic specifications.* Judgment and Decision Making 6(8): 800–813. | https://www.cambridge.org/core/product/E2FA1D4CCFF1E22C59A1C55CF989C39E/core-reader | Classifies each decision maker by strategy *and* stochastic specification: one strategy with low or high error, or a mixture over strategies. Uses normalised maximum likelihood for non-nested comparison. Some people are best fit by one strategy plus error, others by a mixture. | Answers "is the model one noisy heuristic or a mixture?", the core of our mixture model, with a principled complexity penalty. | **R** |
| Myung & Pitt (2009). *Optimal experimental design for model discrimination.* Psychological Review 116(3): 499–518. | https://pmc.ncbi.nlm.nih.gov/articles/PMC3755632 (tutorial that cites it) · DOI 10.1037/a0016104 | Sampling-based search for designs that best discriminate competing models. Later adaptive version: Cavagnaro et al. (2010), see Unverified. | O3 step 1. With deterministic heuristics, expected information gain reduces to choosing items where candidate predictions disagree, weighted by the posterior. | **R** |
| Jagadish, Strittmatter, … Schulz, Daw, Chandramouli & Griffiths (2026). *Closing the Loop to Discover Psychological Theories with an Automated Cognitive Scientist* (AutoCog). arXiv. | https://arxiv.org/abs/2606.26448 | LLM agents propose competing executable cognitive models, design experiments "that best discriminate" them, collect data, score, diagnose and revise. It recovered known decision strategies, including unconventional ones, from simulated behaviour. With humans, it found a new multi-cue theory confirmed in a pre-registered study. | Precedent for our positive controls and for growing the zoo from residuals. Not applied to LLM subjects, as far as the abstract shows, but trivially could be. A reviewer will ask "why not AutoCog?" | O (method), **R** |

---

## Novelty risks (blunt)

1. **"LLMs use greedy heuristics on NP-hard problems" is taken.** GraphArena (ICLR 2025), EHOP (Findings of EMNLP 2025), Saparov & He (ICLR 2023) and Hazra et al. (COLM 2025) all say it.
   - EHOP in particular already has our domains 3–5, our baselines (first-fit by degree, density ratio, nearest neighbour), a realistic-framing manipulation (costumes), an inversion manipulation, and a "greedy-hard" item split.
   - If the paper's pitch is "we show LLMs are greedy", it is not novel.
   - **What is still open:** instance-level agreement on items where *heuristics disagree with each other* (EHOP only separates greedy from optimal), permutation baselines, mixture weights with unexplained mass, and manipulation signatures. Say this explicitly.
2. **AlgoTrace pre-empts NN-on-TSP, behaviourally and mechanistically.**
   - It measures how often outputs are NN paths, shows reasoning fine-tuning increases NN use, and causally induces NN behaviour with a steering vector. It also has 3-SAT strategy clusters.
   - For O5/H5, don't make TSP-NN the showcase. Entailment (ETR state, UP-k derived literals) or SAT POLARITY / unit propagation are less crowded.
3. **Strategy identification for LLM deduction exists at the process level.**
   - Mondorf & Plank (ACL 2024) did human-strategy classification on propositional problems.
   - Eisape et al. (NAACL 2024) projected LLMs into mReasoner's parameter space.
   - Bertolazzi et al. (EMNLP 2024) tested cognitive heuristics on syllogisms.

   "Apply cognitive-science strategy identification to LLMs" is not a new framing. What I did *not* find is outcome-based, likelihood-based classification (Bröder / Glöckner / Davis-Stober) with designed discriminating items and a chance baseline applied to LLMs. That looks open, at moderate confidence given the search-budget cutoff.
4. **A heuristic zoo as such.** I found no paper that builds a cross-domain zoo of executable heuristics and fits mixture weights to LLM answers. The closest are EHOP (two greedy baselines per problem), AlgoTrace (trace-derived primitives, not a predefined zoo) and Hazra (trace coding). AutoCog's closed loop is the method most likely to scoop the *identification engine* if someone points it at LLMs. Watch 2026–27 arXiv for "AutoCog" plus "LLM".
5. **H6 as a question is not new.** Koralus & Wang-Maścianica 2023, v1, and Eisape et al. 2024 each report human-like error patterns rising with capability. Hagendorff et al. 2023 and Macmillan-Scott & Musolesi 2024 report the opposite. Our novelty is the competitor-controlled test, not the question.
6. **v1 has little external engagement**, so there is little risk of being scooped on ETR-with-competitors. The motivation can't lean on v1 being influential, and the v1 correlation itself is fragile (internal re-analysis).

---

## Methods and resources to reuse

- **Likelihood-based strategy classification** (Bröder & Schiffer 2003; Davis-Stober & Brown 2011).
  - Per model (or per model × domain), fit {strategy, error rate}, plus mixture alternatives.
  - Select with held-out log-likelihood or normalised maximum likelihood.
  - Handle ties: when two heuristics give the same answer, the item carries no discriminating information, and raw accordance rates are biased. This directly affects our EA metric.
- **Multiple measures** (Glöckner 2009). Add `reasoning_tokens_used` and answer log-probability, where available, as process measures with heuristic-specific predictions. McCoy et al.'s o1 paper shows token use varies systematically with input properties.
- **Optimal design** (Myung & Pitt 2009; adaptive follow-up by Cavagnaro et al. 2010, see Unverified). With deterministic heuristics, "information gain" is cheap to compute from prediction disagreement plus the current posterior over the zoo.
- **Graded agreement** (from AlgoTrace).
  - Tours: edit distance to the heuristic's tour; also accept a match "within the first k paths".
  - Colorings and assignments: Hamming distance.
  - Knapsack: Jaccard distance on item sets.
- **Output taxonomy** (GraphArena): correct / suboptimal / hallucinatory (infeasible) / missing. Use it alongside §5.5's parse-failure and refusal categories.
- **EHOP dataset and design**: textbook / costumed / inverted variants of coloring, knapsack and TSP, plus EHOP-HARD (greedy-not-optimal items) and weak-greedy baselines. It can seed domains 3–5 and a cross-check. I didn't verify where the code and data are hosted.
- **Hazra et al. 3-SAT setup.** Phase-transition sweep around αc≈4.267, CNF vs "Menu" natural-language framing, plus their trace-coding categories (unit clause, pure literal, MOMS, lookahead, backtracking/backjumping, unit-propagation mistakes) for a secondary trace analysis.
- **mReasoner parameter-space projection** (Eisape et al. 2024). An existing executable mental-models implementation, plus human syllogism data. It could stand in for our MM heuristic, or validate it, on the syllogistic fragment.
- **Human strategy taxonomy for propositional reasoning** (Van der Henst et al. 2002, via Mondorf & Plank 2024): incremental diagram, supposition following, chain construction, compound, concatenation. Useful for mapping zoo entries to human strategies, and for a CoT secondary analysis.
- **Manipulations with precedent:**
  - premise order relative to proof order (Chen et al. 2024; R-GSM);
  - output and input probability (McCoy et al. 2024);
  - counterfactual or inverted rules (Wu et al. 2024; EHOP);
  - belief-congruent vs incongruent content (Lampinen/Dasgupta et al. 2024; Bertolazzi et al. 2024).
- **Centaur** (Binz et al., Nature 2025; Llama-3.1-70B fine-tuned on Psych-101). Possibly a "human-like responder" baseline: does a model's error pattern look more like Centaur's than like any zoo heuristic? I verified only the bibliographic record, not its fit for this use.

---

## Suggested changes to DESIGN.md

1. **Add a Related Work section and reposition the contribution.**
   - Name EHOP, GraphArena, AlgoTrace, Hazra et al., Saparov & He, Mondorf & Plank, Eisape et al., Bertolazzi et al. and Koralus & Wang-Maścianica 2023.
   - Say plainly that "LLMs are greedy / heuristic on NP-hard problems" is known qualitatively. Our contribution is *discriminating among competing heuristics* with instance-level likelihoods, chance baselines and manipulation signatures.
2. **Replace exact-match agreement with noisy-execution likelihoods (O3 §2).**
   - Today the mixture uses `1[y = h(x)]`. LLM outputs are often infeasible or near-misses (GraphArena "hallucinatory"; R1 "limited soundness" in Hazra et al.).
   - Use a kernel `P(y | h(x)) ∝ exp(−λ · d(y, h(x)))` with a domain-appropriate distance d, or "h executed with k random slips".
   - Otherwise most error mass will be "unexplained", and H1 will fail for the wrong reason.
3. **Adopt the Bröder / Davis-Stober framework explicitly.**
   - Per model × domain, compare "single heuristic + error" vs "mixture" stochastic specifications.
   - Report how EA handles ties: drop items where h ties with other candidates from that h's EA, or move to the likelihood.
4. **Add process measures (Glöckner MM-ML).** Pre-register heuristic-specific predictions for reasoning-token counts and answer confidence, and use them as a second identification channel alongside answers.
5. **Zoo additions with literature support:**
   - SAT: `PURE-LITERAL`, `MOMS`, `DPLL-trunc-b` (complete search cut off at budget b; R1's "incomplete" failure), and a generator-statistics heuristic, e.g. predict SAT/UNSAT from clause/variable ratio (Zhang et al. 2023; Hazra "statistical features").
   - Coloring: `RANDOM-ORDER-FIRST-FIT` (EHOP weak greedy).
   - Knapsack: `VALUE` (already listed).
   - TSP: `NN-from-0` as distinct from `NN-from-best-start` (AlgoTrace saw starts at city 0), and `FARTHEST-INSERTION` (the OPRO baseline; snippet only).
   - Syllogistic fragment, if added: `ATMOSPHERE` and mReasoner.
   - Cross-domain: `TEXTBOOK-TRANSFER` (solve the uninverted or textbook version of an inverted item). This turns approximate retrieval from residual mass into a testable procedure (EHOP inverted variants).
6. **Discriminating items: greedy vs greedy, not only greedy vs optimal.** EHOP-HARD only removes items where greedy is optimal. Our value comes from items where `FIRST-FIT`, `DSATUR` and `LARGEST-FIRST` (or `RATIO`, `VALUE` and `LARGEST-FIT`) disagree with each other. State this as the design difference.
7. **H4 needs a pre-registered family map and a within-domain test first.**
   - Define families before data. Examples: "one-pass constructive, no revision" = {GREEDY, FIRST-FIT, RATIO, NN, FIRST}; "local propagation" = {UP-k, UP+GUESS}; "surface" = {PRIMACY, RECENCY, FREQ, LENGTH-PRIOR}; "search" = {DPLL-trunc, WALK-k, 2OPT-k}.
   - Test across-framing consistency within a domain (textbook vs costumed) before cross-domain consistency. EHOP, Hazra and Wu all show strong framing dependence, so H4 may fail at the within-domain level already. That would be informative, not a null.
8. **H6: pre-register which heuristics are "cognitive" and which are "surface", and allow an inverted U.**
   - MATCH and ATMOSPHERE are ambiguous: cognitive-science heuristics that are surface-like in mechanism.
   - Change the falsification criterion to allow non-monotone capability trends (Hagendorff et al. 2023; Eisape's Llama 2 null), and include accuracy as a covariate, as Eisape et al. did.
9. **Positive controls: cite precedent.** AutoCog recovered strategies from simulated behaviour; Bröder & Schiffer validated against process tracing. Their recovery-analysis designs can be borrowed.
10. **Consider Centaur as a "human-likeness" reference model** for H6, alongside ETR and MM.

---

## Citation corrections (DESIGN.md §10, my slice)

| Entry in DESIGN.md | Status | Correction |
|---|---|---|
| Chen et al. (2024). *Premise Order Matters in Reasoning with Large Language Models.* ICML. | Correct | Authors: Xinyun Chen, Ryan A. Chi, Xuezhi Wang, Denny Zhou. arXiv 2402.08939. |
| McCoy et al. (2024). *Embers of Autoregression.* PNAS. | Short title only | Full title: *Embers of autoregression show how large language models are shaped by the problem they are trained to solve.* PNAS 121(41): e2322420121 (Oct 2024). Authors: McCoy, Yao, Friedman, Hardy, Griffiths. The 2023 arXiv title differs ("…: Understanding Large Language Models Through the Problem They are Trained to Solve", arXiv 2309.13638). Consider also citing the o1 follow-up (arXiv 2410.01792). |
| Myung & Pitt (2009). *Optimal Experimental Design for Model Discrimination.* Psychological Review. | Correct | 116(3): 499–518, doi 10.1037/a0016104. The adaptive, mutual-information version we actually want is Cavagnaro, Myung, Pitt & Kujala (2010); I didn't verify its venue. |
| Gigerenzer, Todd et al. (1999). *Simple Heuristics That Make Us Smart.* | Minor | Edited volume: Gigerenzer, G., Todd, P. M., & the ABC Research Group (1999). Oxford University Press (Evolution and Cognition series). |
| Johnson-Laird (2006). *How We Reason.* | Correct | Oxford University Press, 2006. |
| Koralus (2022). *Reason and Inquiry: The Erotetic Theory.* OUP. | Correct, with a date nuance | Online on OUP Academic on 29 Dec 2022; print listed by retailers as 2023 (ISBN 978-0-19-882376-6). Either year is defensible; "2022/2023" or "2023 (online 2022)" avoids reviewer nitpicks. |
| Zhang et al. (2023). *On the Paradox of Learning to Reason from Data.* IJCAI. | Correct | Authors: Honghua Zhang, Liunian Harold Li, Tao Meng, Kai-Wei Chang, Guy Van den Broeck. IJCAI 2023, pp. 3365–3373. Note it studies BERT and T5 on SimpleLogic, not modern LLMs. |
| Richardson et al. (2025). arXiv 2506.11128. | Incomplete | Add **ICLR 2026** (proceedings listing found). v1 was titled "Stronger Language Models Produce More Human-Like Errors". |
| Fan et al. (2024). *NPHardEval.* ACL. | Correct | Full title: *NPHardEval: Dynamic Benchmark on Reasoning Ability of Large Language Models via Complexity Classes.* ACL 2024 (Long), pp. 4092–4114. |

None of the checked entries is fabricated. All exist with the stated year and venue.

---

## Unverified / leads

**Found in searches, but not read or not fully verified:**
- **Cavagnaro, Myung, Pitt & Kujala (2010).** *Adaptive Design Optimization: A Mutual Information-Based Approach to Model Discrimination in Cognitive Science.* Title seen at https://cir.nii.ac.jp/crid/1360017289167683072. Venue (I believe Neural Computation) not verified.
- **Imannezhad, Pothos & Wills (2026).** *Divergent patterns of probabilistic reasoning in humans and GPT-5.* Frontiers in Psychology. Seen only in Semantic Scholar's list of papers citing Koralus & Wang-Maścianica 2023; not read. Potentially important for H6 at frontier scale.
- **Bessis et al. (2026).** *Legal Decision Biases in GPT: A Comparison with Human Judgment.* Behavioral Science. Same source, not read.
- **Erata et al. (2026).** *Learning How to Cube.* NeurIPS 2026 (arXiv 2605.16632).
  - A search snippet claimed 388 Qwen3-4B SAT traces were classified, with "variable frequency analysis" the default strategy in about 73.5% and unit-propagation potential in about 2.3%.
  - The abstract page doesn't mention this. Check the full text: if true, it supports FREQ/POLARITY-type SAT heuristics.
- **Stechly, Marquez & Kambhampati (2023).** *GPT-4 Doesn't Know It's Wrong: An Analysis of Iterative Prompting for Reasoning Problems.* arXiv 2310.12397, listed on neurips.cc (probably a 2023 workshop; unverified).
  - Graph coloring: GPT-4 is poor at both solving and verifying.
  - Follow-up: Stechly, Valmeekam et al., *On the Self-Verification Limitations of LLMs on Reasoning and Planning Tasks*, ICLR 2025.
- **Yang et al. (2023).** *Large Language Models as Optimizers* (OPRO), arXiv 2309.03409. Per a snippet, TSP with NN and farthest-insertion baselines: LLMs find the optimum at n=10, and farthest insertion beats all LLMs as n grows. Not read closely.
- **Wang et al. (2026).** *Formalize, Don't Optimize: The Heuristic Trap in LLM-Generated Combinatorial Solvers.* arXiv 2605.12421. LLM-written solvers replace complete search with approximations when asked to optimise. Tangential support for O2.
- **Jiang et al. (2025).** *Large Language Models as End-to-end Combinatorial Optimization Solvers.* NeurIPS 2025, arXiv 2509.16865. Fine-tuned 7B models beat classic heuristics, so "LLM output = classic heuristic" need not hold for task-trained models.
- **Backtracking benchmarks** (snippets only):
  - FineReason (ACL 2025, arXiv 2502.20238): "backtracking failure" reported in snippets, not confirmed on the abstract page.
  - ZebraLogic (arXiv 2502.01100).
  - LR²Bench (arXiv 2502.17848).
- **Lin et al. (2025).** *Implicit Reasoning in Transformers is Reasoning through Shortcuts.* Findings of ACL 2025, arXiv 2503.07604.
- **Mondorf & Plank (2024).** *Beyond Accuracy: Evaluating the Reasoning Behavior of LLMs — A Survey.* COLM 2024, arXiv 2404.01869. A good map of process-level evaluation.
- **Hagendorff (2023–24).** *Machine Psychology.* arXiv 2303.13988. Methodology and caveats.
- **Binz et al. (2025).** *A foundation model to predict and capture human cognition* (Centaur). Nature 644: 1002–1009.
- **Order-sensitivity follow-ups to Chen et al.:** *Order Doesn't Matter, But Reasoning Does: Training LLMs with Order-Centric Augmentation* (EMNLP 2025, arXiv 2502.19907).
- **"Think Again! The Effect of Test-Time Compute on Preferences, Opinions, and Beliefs of LLMs"** (arXiv 2505.19621). Relevant to thinking-budget effects on bias; not read.
- **Pan et al. (2024).** *Can Transformers Reason Logically? A Study in SAT Solving* (arXiv 2410.07432). A transformer constructed to be trace-equivalent to DPLL. Belongs in the O5/O6 slices.
- **Olsson, Chalmers MSc thesis.** LLM-generated TSP/VRP algorithms vs nearest neighbour (odr.chalmers.se). Not read.

**Recalled, but not searched (search budget ran out):**
- Evans's matching bias.
- Khemlani & Johnson-Laird (2012) meta-analysis of syllogistic theories. Useful: it compares 12 theories of syllogistic reasoning on the same data, a "theory zoo" precedent from cognitive science.
- Van der Henst, Yang & Johnson-Laird (2002), *Strategies in sentential reasoning* (Cognitive Science). Cited via Mondorf & Plank, not fetched.
- Valmeekam et al. on o1 and PlanBench.
- Shortcut-learning reviews (Geirhos et al. 2020).
