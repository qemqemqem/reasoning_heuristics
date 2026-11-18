# T3. LLM precedent: what we already know about how LLMs reason, family by family

*Theory-crafting note, written 2026-11-13, before any project data. One of three: T1 covers expressivity, circuit complexity and CoT compute; T2 covers RASP-L program length and learnability. Overlaps are marked [→T1] and [→T2] and are not argued here. This note builds on [literature/B_heuristics_behaviour.md](../literature/B_heuristics_behaviour.md) and [literature/C_interpretability.md](../literature/C_interpretability.md) and does not repeat them. Family labels follow [PAPER_SKELETON.md](../PAPER_SKELETON.md) Table 4.*

**Citation status.**

- ✓ = verified in this session by search or fetch: title, authors, year and the specific claim used.
- [A] / [B] / [C] = verified in literature slice A, B or C. The claim is taken from that slice and was not re-checked here.
- [?] = not verified; a lead only.

**Evidence types.**

- **M** = mechanistic (internals).
- **B** = behavioural (answers or traces).
- **T** = training argument.
- **An** = analogy, e.g. to models trained from scratch.

**Regimes.** Precedent maps differently onto three regimes, so the note keeps them apart:

- **1P:** a single-token direct answer. One forward pass, constant depth.
- **DS:** a direct answer with structured output (assignment, colouring, tour) and thinking off. The output stream works as a sequential scratchpad (see [C_constructive.md](../verticals/C_constructive.md) P4).
- **TH:** thinking at best effort (gpt-oss high, Qwen3 thinking, ≤ 32k tokens). It splits into items below and above the model's budget line n\*.

---

## Summary

1. **Mechanistic evidence in pretrained LLMs covers only single forward passes on short, easy items.** It shows shallow, parallel, feature-gated computation: position and cue heuristics (A), one- or two-step propagation (B1, small k), bags of heuristics (I in miniature). Nothing yet looks inside a thinking model on an NP-hard item.
2. **Search-like internals** (parallel set expansion, adjacency powers, candidate sets, look-ahead) **are documented only in models trained from scratch on one task.** For our models they are analogies, not evidence.
3. **Behaviour splits by regime.** DS models act like fixed-order greedy without backtracking (C1). Thinking models search with unit propagation and backtracking (D), but unsystematically and with a self-chosen early stop, and they open with named greedy constructions (NN) *more* often than their base models.
4. **The best-documented reasoning-model errors on constraint problems are misreading the instance and slipping during long execution** (hallucinated edges, overlooked clauses, compounding errors). So the nuisance terms may outweigh any heuristic family above n\*. The one published link between such errors and greedy difficulty was later judged non-causal by its authors.
5. **Training.** Pretraining supplies the repertoire (textbook procedures, human pragmatic readings, frequency priors). RLVR mostly *reweights* it toward verifying and backtracking, and gives no signal above budget beyond "commit to some answer". Expect shifting mixture weights, not new families.
6. **Order and position sensitivity is weakened by thinking, not removed.** It shrinks as an accuracy effect, grows with trace length, and should survive as order-dependent solution fingerprints.
7. **Best supported:** A (direct), C1 (DS), the D family (TH), `NOISY-EXACT` and `PERCEPTION-NOISE` (TH). **Least supported:** B3, B5, explicit E, F, G; none has direct LLM precedent.
8. **Most likely to fail to transfer:** greedy-without-backtracking and premise-order accuracy findings from non-thinking models, and human-likeness trends measured on them.

---

## 1. Score table

The score runs from −2 (existing evidence argues against LLMs doing this) to +2 (strong existing evidence that they do); 0 means no evidence, or evidence that cancels.

- **Direct** means 1P unless "DS" is written.
- **Thinking** means TH at best effort, mainly below n\*. Above-n\* evidence is thin everywhere, and §2 says so where it matters.
- **Conf.** is the confidence in the direct score and in the thinking score.

| Family · member | Direct | Thinking | Conf. (D / T) | Type | Main precedent (↑ for, ↓ against) |
|---|---|---|---|---|---|
| **A1** constant default (`ALWAYS-SAT`, "yes", aversion to "nothing follows") | +2 | +1 | med / med | B | ↑ SAT bias (Zhang, Chen & Chen 2026 [A]); aversion to "nothing follows" (Eisape 2024 [B]; Bertolazzi 2024 [B]); "UNSAT because complex" (Hazra 2025 ✓). ↓ R1 "always attempts to solve" (Hazra ✓) |
| **A2** position (`PRIMACY`, `RECENCY`, `LABEL-A`) | +2 | +1 | high / med | M, B | ↑ causal-mask position bias (Wu, Wang, Jegelka & Jadbabaie 2025 ✓); U-shaped use of context (Liu et al. 2024 ✓); option-ID priors (Zheng 2024 ✓); premise order (Chen 2024 [B]); position bias grows with trace length in reasoning models (Wang 2026 ✓) |
| **A2** statistical features (`DENSITY`, `FREQ`, `LENGTH-PRIOR`) | +1 | 0 | med / low | B, An | ↑ Zhang et al. 2023 [B]; Hazra ✓ ("statistical features"); degree heuristic beyond depth capacity (Ye 2025 [C], toy); McCoy 2024a [B]. ↓ R1 is the exception in Hazra ✓ |
| **A3** `TEXTBOOK-TRANSFER` | +2 | +1 | med / med | B, T | ↑ EHOP ✓; Wu 2024 [B]; o1 still probability-sensitive (McCoy 2024b [B]); procedures drive reasoning (Ruis 2025 [B]) |
| **B1** `UP-k`, small k (bounded forward chaining) | +1 | 0 | med / low | M, B | ↑ hop limits per pass (Yang 2024 [C]; Biran 2024 [C]; Yao 2025 [C]; Csordás 2025 [C]); one-rule circuit (Hong 2025 [C]); proof by cases fails without demonstrations (Saparov et al. 2023 ✓). In TH, UP is a *subroutine* of search (Hazra ✓), not the final answer |
| **B1** `PREMISE-SUBSET` / `DROP-CONSTRAINT` | +1 | 0 | low / low | B | ↑ middle-of-context omissions (Liu 2024 ✓); R1 "overlooking clauses" (Hazra ✓). Not shown to be *systematic*, so not yet separable from `PERCEPTION-NOISE` |
| **B3** `LP-ROUND` | 0 | 0 | low / low | — | No precedent. On knapsack, LP rounding ≡ `RATIO` greedy, so B3 and C1 are confounded there |
| **B4** surface restriction (`FIRST`, `MATCH`) | +1 | 0 | med / low | B, M | ↑ share of errors that are ETR fallacies rises with Elo (Richardson 2025 ✓); Koralus & Wang-Maścianica 2023 [B]; atmosphere/matching (Bertolazzi [B]); induction/copy circuits make matching cheap (Olsson 2022 ✓, An). ↓ zero-shot CoT reduces conditional fallacies (Holliday 2024 ✓); intuitive errors fade with capability (Hagendorff 2023 [B]) |
| **B4** model-based (`MM`, `ETR`) | +1 | 0 | med / low | B | ↑ deliberative mReasoner component grows with PaLM 2 size (Eisape [B]); premise reversal reduces fallacies (Richardson ✓). ↓ the Llama 2 size effect vanishes once accuracy is controlled (Eisape [B]) |
| **B4** interpretive (`BICOND`, `CLOSED-WORLD`) | +1 | 0 | low / low | B, T | ↑ basic conditional fallacies in all 29 models tested (Holliday ✓). TH: training pulls both ways (§3.3) |
| **B4** `ADD-CONSTRAINT` (phantom constraint) | +1 | +1 | low / med | B | ↑ hallucinated edges in all six reasoning models tested (Heyman & Zylberberg 2025b ✓); GraphArena "hallucinatory" outputs [B]. Whether they are *structured* (B4) or random (nuisance) is unknown |
| **B5** `EXPECTED-COST` | 0 | 0 | low / low | — | No precedent |
| **C0** one-shot scoring (`POLARITY`, `MOMS`, `PURE-LITERAL`) | +1 | +1 | low / low | An, B | ↑ constant-depth count features are what bag-of-heuristics circuits compute (Nikankin 2025 [C], An); R1 "actively applies classical SAT-solving heuristics" (Hazra ✓) |
| **C1** fixed-order greedy (`FIRST-FIT`, `NN`, `GREEDY`, `INPUT-ORDER`) | 1P −1 · DS +2 | +1 | med / med | B, M | ↑ DS: Saparov & He 2023 [B]; EHOP ✓; GraphArena [B]; GPT-4o "greedy search without backtracking" (Hazra ✓). TH: NN is a "hallmark of Phi-4-Reasoning responses" (AlgoTrace ✓). ↓ 1P: sequential, beyond the per-pass hop budget [→T1] |
| **C2** adaptive order (`DSATUR`, `UC` / `GUC`) | 0 | +1 | low / low | B, T | ↑ R1 uses unit propagation (Hazra ✓); most-constrained-first rules are standard textbook CSP advice (T) |
| **C3** random order | −1 | −1 | low / low | B | ↓ order following is strong and systematic (Chen 2024 [B]; Zheng 2024 ✓) |
| **C4** `ONL(k)` online, bounded state | +1 | 0 | med / low | M, B | ↑ causal processing; accuracy best when premise order matches proof order (Chen 2024 [B]); state tracking over updates is fragile (Kim & Schuster 2023 ✓; Li, Guo & Andreas 2025 ✓); ETR reversal effect (Richardson ✓) |
| **D** family: search with backtracking | −2 | +2 | high / med | M, B | ↓ 1P: no search found inside a pass (Saparov et al. 2025 [C], toy; Csordás [C]). ↓ DS: no backtracking (Saparov & He [B]; Hazra ✓). ↑ TH: R1 builds and navigates a search tree and backtracks (Hazra ✓); output length tracks solver conflicts (Lin 2025 ✓; Yang et al. 2026 ✓); reflection emerges under RL (DeepSeek-AI 2025 ✓); backtracking is a linear direction (Venhoff 2025 [C]) |
| **D** `DPLL-b` (systematic; truncated at b; default answer) | −2 | +1 | high / med | B | ↓ TH: "wanderers rather than systematic explorers" (Lu et al. 2025 ✓); thought switching in wrong answers (Wang et al. 2025 ✓); R1 "terminates prematurely" (Hazra ✓); effort falls before the budget runs out (Shojaee 2025 [A]) |
| **D** `BEAM-w`, `BACKDOOR-k` | −1 | 0 | med / low | — | No precedent for either |
| **E** `BP-t`, `WP-t` (soft local message passing) | +1 | 0 | low / low | An, M | ↑ layer-wise parallel set expansion and adjacency powers in from-scratch models (Saparov 2025 [C]; Ye 2025 [C]; Brinkmann 2024 [C]; Wang et al. 2024 ALPINE ✓). No evidence of graded marginals in pretrained LLMs. TH-explicit: no textbook source (T) |
| **F** local search (`MIN-CONFLICTS`, `WALK-k`, `2OPT-k`) | −1 | +1 | med / low | T, B (weak) | ↑ TH: verification habit (Gandhi et al. 2025 ✓). ↓ self-critique without a sound verifier *hurts* on colouring (Stechly et al. 2025 ✓); models condition on their own errors (Sinha 2025 ✓). No quantified repair study found |
| **G** `DP-EXACT` | −1 | +1 | med / low | T, B | ↑ TH: DP is the textbook knapsack method (T). ↓ DP accuracy collapses with size (Dziri 2023 ✓); greedy beats CoT on knapsack in non-thinking models (EHOP [B]) |
| **G** `IGNORE-CROSSLINKS` | 0 | +1 | low / low | B (weak), T | ↑ subgoal-setting habit (Gandhi 2025 ✓); "linearized subgraph matching" (Dziri ✓, interpretive) |
| **H** `RANDOM` | +1 | 0 | low / low | B | Near-chance accuracy at the threshold (Hazra ✓). Not separable from A1 on accuracy alone |
| **H** `SAMPLE-m` ("check a few cases") | 0 | +1 | low / med | M, B | ↑ "example testing" is a steerable direction in R1 distills (Venhoff [C]); verification habit (Gandhi ✓) |
| **I** strategy selection | +1 | +1 | med / med | M, B | ↑ bag of heuristics (Nikankin [C]); heuristic first, then rational (Aoki 2024 [B]); presentation changes the procedure (Hazra ✓; EHOP ✓); effort allocation miscalibrated both ways (Chen et al. 2024 ✓; Wang et al. 2025 ✓) |
| **`NOISY-EXACT`** | +1 | +2 | low / med | B | ↑ long-horizon execution errors and self-conditioning (Sinha 2025 ✓); supplying the algorithm doesn't help (Shojaee [A]); errors compound (Dziri ✓) |
| **`PERCEPTION-NOISE`** | +1 | +2 | med / med | B, M | ↑ hallucinated edges (Heyman 2025b ✓); overlooked clauses (Hazra ✓); U-shaped context use (Liu 2024 ✓) |

**How to read the table.** Rows with "B" only rest on what models *wrote*, either answers or traces. Trace-based rows (Hazra, AlgoTrace, Gandhi) inherit the faithfulness problem: hints are verbalised about 25–39% of the time (Chen et al. 2025 [C]), and biasing features go unmentioned (Turpin et al. 2023 ✓). The scores on output-only evidence are sturdier: token counts against solver conflicts, accuracy against presentation, and violation types.

---

## 2. Evidence by family

Each family has the same layout: **M**echanistic, **B**ehavioural, **T**raining, then the **net** verdict.

### A. Cue / substitution

- **M.**
  - Position bias has an architectural cause. Under causal masking, deeper layers increasingly favour early positions; with rotary or decay positional encodings, this trades off against a recency effect (Wu et al. 2025 ✓).
  - Option-ID tokens carry a prior before the options are read (Zheng et al. 2024 ✓).
  - Induction and copy heads make "repeat or match what you saw" cheap and early (Olsson et al. 2022 ✓). That is a substrate for `ECHO` and for matching heuristics.
  - The cleanest "A under hardness" analogue comes from a toy model. A transformer trained on graphs beyond its depth capacity learns a node-degree cue instead of the connectivity algorithm (Ye et al. 2025 [C]) [→T2].
- **B, direct.**
  - Accuracy depends on output and input probability (McCoy 2024a [B]).
  - Models fit statistical features of the generator (Zhang et al. 2023 [B]).
  - Models other than R1 "fit on statistical features" on 3-SAT (Hazra ✓).
  - Bias toward answering SAT (Zhang, Chen & Chen 2026 [A]).
  - Answer-position cues change answers without being mentioned (Turpin 2023 ✓).
  - One irrelevant but plausible clause cuts accuracy by up to 65 points (Mirzadeh et al. 2025 ✓; cf. Shi et al. 2023 ✓).
  - Textbook versions beat costumed and inverted ones (EHOP ✓).
- **B, thinking.** Cue effects shrink but don't vanish:
  - o1 is still sensitive to output probability (McCoy 2024b [B]);
  - o1-preview loses 17.5 points on GSM-NoOp (Mirzadeh ✓);
  - reasoning models use hints without saying so (Chen et al. 2025 [C]);
  - reasoning models "show high variance across problem presentations" (EHOP ✓);
  - in 12 of 13 reasoning configurations, position bias rises with trajectory length after controlling for accuracy (Wang 2026 ✓; single-author preprint).
- **T.**
  - Next-token prediction rewards exactly these priors (McCoy's "problem they are trained to solve").
  - RL with verifiable rewards (RLVR) rewards any cue that predicts the verifier's answer on its training distribution. Nothing in RLVR penalises a cue that is valid there.
- **Net.** A is the best-supported family for direct answers. In thinking mode, expect it (i) as the *default* when search stops, and (ii) as a slow drift that grows with trace length.

### B1. Relax

- **M.**
  - Composition within one pass is shallow. The first hop is reliable; the second is "moderate" (Yang et al. 2024 [C]).
  - Bridge entities are resolved too late in the layer stack (Biran et al. 2024 [C]).
  - k hops need layers linear in k (Yao et al. 2025 [C]).
  - Later layers don't compose more (Csordás et al. 2025 [C]).

  Together this is a bounded-k forward-chaining profile, i.e. `UP-k` with k ≈ 1–2 in 1P [→T1]. A sparse circuit handles one "A or B implies C" rule (Hong et al. 2025 [C]).
- **B.**
  - With one-step rules, models generalise to compositional proofs. But proof by cases and proof by contradiction need explicit demonstrations (Saparov et al. 2023 ✓). That is B1's signature: sound but incomplete, failing exactly where a case split is needed.
  - In thinking mode, R1 runs unit propagation inside search (Hazra ✓), so UP is a subroutine of D, not the final answer.
- **Caveat.** The same depth profile is predicted by an exact procedure that runs out of layers (slice C). B1 separates from `NOISY-EXACT` only through omission-vs-commission and a dependence on depth alone ([B1_G](../verticals/B1_G_relax_decompose.md) E1, E2).
- **Net.** +1 direct, 0 thinking as a final heuristic.

### B3, B5

No precedent in LLMs, and the training argument is weak: LP relaxation and expected-cost models are rare in puzzle-solving text. One identifiability note: on knapsack, the LP relaxation rounds to the `RATIO` greedy, so "B3" there is C1.

### B4. Restrict

- **B, direct.**
  - **Erotetic theory (ETR).** Koralus & Wang-Maścianica 2023 [B] report it first. Richardson et al. 2025 ✓ test 383 PyETR items on 38 models:
    - the share of incorrect answers that are ETR-predicted fallacies rises with Chatbot Arena Elo (ρ = 0.360, p = 0.0265);
    - overall correctness does not rise with Elo;
    - reversing premise order significantly reduces fallacies for many models.
  - **Mental models.** Projecting into mReasoner's parameter space: larger PaLM 2 models look more deliberative (Eisape 2024 [B]).
  - **Conditionals.** All 29 models tested make basic conditional and modal fallacies, reduced by zero-shot CoT (Holliday, Mandelkern & Zhang 2024 ✓).
  - **Syllogisms.** Atmosphere and matching (Bertolazzi 2024 [B]).
  - **Content effects.** In behaviour (Lampinen/Dasgupta 2024 [B]) and as belief-bias heads (Kim, Valentino & Freitas 2025 [C]).
- **Against.**
  - Intuitive human-like errors disappear in stronger models (Hagendorff 2023 [B]).
  - Errors are often unlike human biases (Macmillan-Scott & Musolesi 2024 [B]).
  - LLMs never used the incremental-diagram strategy that humans used 34% of the time (Mondorf & Plank 2024 [B]).
- **M.** None for restriction as such. Two candidate substrates:
  - Binding-ID vectors (Feng & Steinhardt 2024 [C]) could hold a few alternatives.
  - Kim et al.'s first-premise recitation stage could support `FIRST` / `PRIMACY` (an interpretation, as slice C notes).
- **Thinking.** There is no direct evidence on thinking models at best effort. The one exception is phantom constraints:
  - Hallucinated edges (Heyman & Zylberberg 2025b ✓) are B4 `ADD-CONSTRAINT` if they fall on structured pairs, and nuisance if they don't.
  - In R1, 33 of 39 false "uncolourable" answers on one framing would have been correct had the hallucinated edges existed (Heyman 2025b ✓).
- **T.** See §3.3: pretraining favours interpretive readings, and RL on maths and code has little reason to correct them.
- **Net.** +1 direct, 0 thinking. The interpretive members and `ADD-CONSTRAINT` are the B4 members most likely to survive thinking.

### C. Constructive / priority

- **DS.**
  - "Greedy" is the most-replicated description: Saparov & He 2023 [B]; EHOP ✓; GraphArena [B]; Hazra's GPT-4o ✓.
  - None of these identifies *which* greedy (slice B; [C_constructive.md](../verticals/C_constructive.md) §0).
  - In 1P, C1 and C2 are sequential and so unavailable [→T1]; C0 is available.
- **TH.** AlgoTrace (✓, full text):
  - "distinct heuristic approaches arise more commonly in Phi-4-Reasoning than Phi-4 (nearest_neighbor and if_clause_true)";
  - base Phi-4 responses split into "a brute-force search and a random guess without further refinement".

  So reasoning training *raised* named greedy construction relative to both exhaustive search and guessing. R1 also starts from classical SAT heuristics (Hazra ✓). Below n\*, C therefore most plausibly appears as the *proposal step inside D*, not as the final answer.
- **C3.** No precedent. LLMs follow the given order.
- **C4.**
  - Causal transformers build each position from its prefix.
  - Accuracy is best when premise order follows proof order (Chen et al. 2024 [B]).
  - Entity tracking through sequential updates is fragile and, in GPT-3.5, linked to code in pretraining (Kim & Schuster 2023 ✓).
  - Models trained on permutation tracking learn one of two procedures (Li, Guo & Andreas 2025 ✓): an associative scan, or a parity heuristic followed by a scan. The second is harder to run robustly.
  - The ETR reversal effect (Richardson ✓) is a behavioural order effect of the C4 kind.
- **Net.**
  - DS: C1 is the expected default.
  - TH: C supplies the first candidate.
  - Above n\*, C's weight in the *final* answer should rise.

### D. Truncated search

- **1P.**
  - Look-ahead inside a pass is position-specific: chess (Jenner 2024 [C]), rhyme planning (Lindsey 2025 [C]; Hanna & Ameisen 2026 [C]).
  - Small transformers trained on graphs learn parallel set expansion, not DFS, and don't scale (Saparov et al. 2025 [C]).
- **DS.** No backtracking in the output (Saparov & He [B]; Hazra GPT-4o ✓).
- **TH.**
  - R1 "constructs and logically navigates a search tree", applies unit propagation, and "identifies the source of the inconsistency and backtracks" (Hazra ✓).
  - Two output-level results that don't rely on reading traces:
    - hidden reasoning tokens scale with Z3 conflicts on logic-grid puzzles (Lin et al. 2025, ZebraLogic ✓; shown in a figure, numbers not checked here);
    - SMT conflict counts predict output length well enough to build denial-of-service attacks on seven frontier models (Yang et al. 2026, SMTrap ✓).
  - Training on search traces does teach search: Gandhi et al. 2024 (Stream of Search) ✓; Lehnert et al. 2024 (Searchformer) ✓.
- **Truncation and defaults.** The search isn't systematic, and the model decides when to stop:
  - R1 "often terminates prematurely without fully exploring the search tree" (Hazra ✓);
  - reasoning effort falls near the collapse point even though budget remains (Shojaee [A]);
  - wrong answers show 418% more thought switching (Wang et al. 2025 ✓);
  - reasoning LLMs are "wanderer[s] rather than systematic explorers" (Lu, Xu & Kankanhalli 2025 ✓).

  So in `DPLL-b`, b is an effort level the model chooses, and the search has restarts. The best-matching member may be **"unsystematic search with self-chosen stop"**, which sits between D and H.
- **Net.** D as a family: +2 for thinking. `DPLL-b` as specified: +1.

### E. Iterated message passing

- **M (analogy only).** All from models trained from scratch:
  - synchronous layer-wise set expansion (Saparov 2025 [C]);
  - adjacency powers reaching diameter 3^L (Ye 2025 [C]);
  - adjacency stored in the MLP while attention captures partial reachability, but not transitive reachability (ALPINE, Wang et al. 2024 ✓);
  - several search frontiers in superposition, i.e. BFS, in *continuous* thought only (Zhu et al. 2025 ✓).

  Log depth is necessary and sufficient for connectivity (Sanford et al. 2024 ✓) [→T1]. Attention is message passing on the token graph; that is an analogy, not evidence.
- **B.** No study shows graded, BP-like marginals in pretrained LLMs on SAT or colouring, and no trace study reports explicit rounds.
- **T.** BP and SP are absent from puzzle text. Sudoku "candidate elimination" guides teach hard-message, WP/UP-like updates, so the explicit E members pretraining could supply overlap B1.
- **Net.**
  - "E-implicit" is a reasonable conjecture: E inside the forward pass, acting as the value heuristic.
  - "E-explicit" is unlikely: rounds written out in the trace.

### F. Local search / repair

- **B.** One targeted search found no quantified study of repair behaviour in LLM reasoning traces.
- **Indirect, for.** Verification is one of four habits that predict RL gains (Gandhi 2025 ✓).
- **Indirect, against.**
  - GPT-4's self-critique on colouring lowers accuracy, while a sound external verifier raises it (Stechly, Valmeekam & Kambhampati 2025 ✓).
  - Models become more error-prone when their own errors are in context (Sinha 2025 ✓), which works against repair.
- **Ambiguous.** GraphArena's infeasible outputs grow with size [B]. That fits F near-misses and noise equally well.
- **Net.** −1 direct, +1 thinking (low confidence).

### G. Decompose / DP

- **DP.**
  - CoT can express DP (Feng et al. 2023 [A]) [→T1].
  - Measured DP accuracy collapses with size, and early errors compound (Dziri et al. 2023 ✓).
  - Knapsack → DP is the textbook route, so thinking models may write DP tables (T).
- **`IGNORE-CROSSLINKS`.**
  - Dziri's finding that models reduce compositional tasks to "linearized subgraph matching" is decomposition without reconciliation, in spirit (interpretive).
  - Subgoal setting is a trained habit (Gandhi ✓).
- **Net.** Weak in both directions.

### H. Guess / sample

- **`RANDOM`.** Cannot be told apart from A1 on accuracy. The only precedent is near-chance accuracy at the threshold.
- **`SAMPLE-m`.**
  - "Example testing" is a steerable direction in R1 distills (Venhoff 2025 [C]).
  - Verification is a trained habit (Gandhi ✓).
  - "Try a few cases" is common in human mathematical text (T).
- **Net.** `SAMPLE-m` scores +1 in thinking mode.

### I. Strategy selection

- **Within a pass.** Many feature-gated heuristics are combined, which is I in miniature (Nikankin 2025 [C]).
- **Within a chain.** Shallow heuristics come early and rational steps later (Aoki 2024 [B]).
- **Across presentations.**
  - R1's search is "noticeably more unstructured" on SAT-Menu than on CNF, and it "struggles to map SAT-Menu inputs into structured CNF-like representations" (Hazra ✓).
  - EHOP ✓ shows the same kind of presentation dependence.
- **Effort allocation is miscalibrated in both directions.** Models spend too much effort on easy items (Chen et al. 2024 ✓) and too little on hard ones (Wang et al. 2025 ✓).
- **Net.** I is the expected *shape* of every result.

### Nuisance terms

- **`NOISY-EXACT`.** Sinha et al. 2025 ✓:
  - per-step accuracy degrades over long horizons;
  - scale fixes long-context degradation but not self-conditioning;
  - thinking mitigates self-conditioning. The wording varies across arXiv versions; v3 says "mitigates".

  Supplying the algorithm doesn't rescue accuracy (Shojaee [A]).
- **`PERCEPTION-NOISE`.**
  - Hallucinated edges account for "at least a significant fraction" of errors in every model tested and "the vast majority" for some (Heyman 2025b ✓).
  - R1 overlooks clauses (Hazra ✓).
- **Net.** Both score +2 in thinking mode. Together they are the main threat to H1 (that a few heuristics explain most errors).

---

## 3. Training pressure

### 3.1 What each stage supplies

| Stage | What it rewards | Families it should push up | Evidence |
|---|---|---|---|
| **Pretraining** (next token on text and code) | Imitating procedures and human argument; output frequency | A (priors), A3 (recognise, then retrieve the textbook procedure), B4 interpretive readings, C1/C2 (taught greedy algorithms), D as code (N-queens and Sudoku backtracking), G-DP (knapsack), WP/UP-like elimination (Sudoku guides) | Procedures in documents drive reasoning (Ruis 2025 [B]). Human-like content effects (Lampinen [B]). Qwen-2.5-3B *base* already verifies and backtracks; Llama-3.2-3B doesn't until continued pretraining on behaviour-filtered OpenWebMath (Gandhi 2025 ✓). Self-reflection appears in almost all base models before RL (Liu et al. 2025 ✓). Entity tracking comes from code (Kim & Schuster ✓) |
| **Long-CoT SFT / distillation** | Copying a teacher's traces | The teacher's procedure, including its heuristics | Qwen3-0.6B–14B are trained by strong-to-weak distillation from Qwen3-32B / 235B-A22B; Qwen3-32B runs the full four-stage pipeline (Qwen3 report ✓). Distillation can add patterns that RLVR doesn't (Yue 2025 ✓) |
| **RLVR** (final-answer reward) | Answers correct on the *training* distribution | Verification and backtracking (D) where present; cues valid in-distribution (A); confident answers over "unknown" | Qwen3's reasoning RL uses maths and coding, 3,995 query–verifier pairs ✓, with logical reasoning only in cold-start data ✓. gpt-oss uses CoT RL "similar to o3" (model card ✓; data not disclosed). R1-Zero's reflection emerges under pure RL (DeepSeek-AI 2025 ✓) |

### 3.2 What RLVR on mostly small problems implies for NP-hard items

1. **Sharpening, not invention (contested).**
   - RL concentrates output on a distribution already present in pretraining (Zhao et al. 2025, "Echo Chamber" ✓).
   - RL wins at small pass@k but base models win at large k (Yue et al. 2025 ✓).
   - **Against:** prolonged RL reaches strategies base models never sample (ProRL, Liu et al. 2025 ✓).

   For us, the thinking model's repertoire of families should be the base model's, *reweighted*. ProRL warns this may not hold for heavily RL-trained models such as gpt-oss.
2. **Search below budget.** Training items are mostly solvable within the budget, so RL rewards exact search plus checking. That predicts D with `NOISY-EXACT` and `PERCEPTION-NOISE` errors below n\*.
3. **No gradient for graceful failure.** Above n\*, nothing in training says *which* fallback to use. Two things remain:
   - the training-distribution prior on answers (A1);
   - whatever the pretrained proposal step produces (C).

   Predicted composite: **search, stop at a self-chosen effort, then answer with the current candidate or a default**, i.e. D∘(C | A1). On a decision answer, "no model found yet" reads naturally as "UNSAT" or "impossible", so this composite predicts **false impossibility** (P1).
4. **Backtracking is amplified only if present.**
   - Backtracking models gain from RL; models without it gain little (Qin et al. 2025 ✓).
   - Sequential backtracking helps on Sudoku and hurts on CountDown at equal compute (Qin ✓). So D's weight should depend on the domain.
5. **Length and faithfulness.**
   - GRPO's length normalisation makes wrong answers longer (Liu et al. 2025 ✓).
   - Outcome RL raises CoT faithfulness, then plateaus (Chen et al. 2025 [C]).

   Expect long wrong traces, and traces that understate the cues a model used.

### 3.3 Where pretraining and RL pull in opposite directions

| Tension | Pretraining pulls toward | RL pulls toward | Predicted compromise |
|---|---|---|---|
| Commit or revise | One-pass construction (taught greedy; human prose written once) | Verify, backtrack | **Greedy proposal → check → backtrack or patch.** C is high in the *first* candidate and low in the final answer below n\*, and rises above n\* (P4) |
| Everyday connectives | Pragmatic readings: exclusive "or", "if" read as "iff", closed world | Literal semantics, *where the rewarded tasks use them*. Qwen3's RL is maths and code, so connectives in natural language are barely trained | **Interpretive B4 survives thinking better than surface B4** (`FIRST`, `MATCH`), and does so more in costumed / natural renderings than in formal / CNF ones (P7) |
| Recognise or read the instance | Retrieve the textbook procedure for the recognised problem (A3) | Check this instance's constraints | A3 shrinks but persists under rule inversion (P13; EHOP ✓) |
| Statistical cues | Frequency priors | Any cue valid in-distribution is *reinforced* | No conflict, so A survives as the default answer (P1, P3) |

### 3.4 Base vs thinking; small vs large

- **"Direct" here is not a base model.** Qwen3's no-think mode is the same checkpoint after thinking-mode fusion (Qwen3 report ✓). gpt-oss offers low, medium and high effort; whether a true no-reasoning mode exists is unverified [?]. Direct-mode answers may therefore carry RL-shaped proposal habits without the search.
- **Base → thinking.** A and B4 weights should fall, and D and nuisance weights rise. C moves from the final answer to the first proposal.
- **Small vs large within a family.**
  - Size should mainly move n\* and the slip rate, not the mixture:
    - scale fixes long-context degradation (Sinha ✓);
    - in non-thinking models, more deliberate strategies come with size (Eisape [B]; Mondorf & Plank [B]);
    - latent planning grows with scale (Hanna & Ameisen [C]).
  - **Prediction (P14):** compared at matched n/n\*, the mixtures of gpt-oss-20b and 120b, and of Qwen3-14B and 32B, look alike.
  - Distilled Qwen3-14B should look like its teachers with more slips.

---

## 4. Predictions

Each prediction names the evals in [verticals/](../verticals/) that test it and states what would falsify it. Confidence reflects how directly the precedent bears on our regime.

| ID | Prediction | Evals | Precedent | Falsified if | Conf. |
|---|---|---|---|---|---|
| **P1** | **The direction of the default flips with mode.** In TH above n\*, errors on satisfiable items are mostly false "UNSAT / IMPOSSIBLE" (truncated search, plus phantom constraints). In direct mode, errors on UNSAT items are mostly false "SAT / feasible" | D_F E1 (termination type), E5 (certificates); C E5 (false impossible); A_H E1, E2 | SAT bias (Zhang, Chen & Chen 2026 [A]); "UNSAT because complex" (Hazra ✓); R1 false "uncolourable" from phantom edges (Heyman ✓) | TH errors on SAT items are mostly infeasible assignments, or direct mode shows no SAT-side bias | med |
| **P2** | **Effort tracks search difficulty, not just size.** At fixed n and formula length, log reasoning tokens rise with DPLL decisions and conflicts in TH, with no such relation in direct mode | D_F E1, E2 (process measures); B1 E6 | ZebraLogic ✓; SMTrap ✓. **In tension with** Verma 2026 [A] (token spend didn't track proof hardness once length was controlled) | Slope ≈ 0 at matched length. That would side with Verma, and push weight from D to `NOISY-EXACT` | med |
| **P3** | **Position effects survive thinking as a function of trace length.** In TH, `PRIMACY` / `RECENCY` / `LABEL-A` weights rise with trace length (controlling for accuracy and item), even though order effects on accuracy are much smaller than in direct mode | A_H E4 × budget; C E1; B4 E1 (O factor) | Wang 2026 ✓; Chen 2024 [B]; Wu et al. 2025 ✓ | Position weight flat or falling with trace length | med |
| **P4** | **Greedy first, exact last (below n\*).** In TH traces, the first complete candidate matches a C1/C2 member above the permutation baseline in most traces. Final answers below n\* are mostly correct. On trap pairs, π_C ≤ 0.1 below n\* and rises above it | C E6, E1; D_F E4 | AlgoTrace ✓; Hazra ✓; Gandhi ✓ | First candidates match no C member above baseline, or trap failure doesn't rise above n\* | med |
| **P5** | **Order fingerprints on correct answers.** On many-solution items, *which* correct solution a TH model returns depends on listing or answer order | C E1 (P2 fingerprints) | Order following (Chen 2024 [B]); NN started from city 0 (AlgoTrace, per slice B [B]) | Returned solutions are order-invariant | med |
| **P6** | **No sequential execution in a single token.** In C E3 depth-stress gadgets, π_seq(d) falls to its bound by d ≈ 3–4 in 1P, and recovers in DS (answer in processing order) and in TH | C E3 | Hop limits (Yang [C]; Biran [C]; Yao [C]; Csordás [C]) [→T1] | 1P answers track first-fit at d ≥ 4 | high |
| **P7** | **B4 falls with thinking; interpretive members fall least.** The direct-mode π for `FIRST` / `MATCH` / `ETR` is detectable and drops ≥ 50% (relative) in TH. `BICOND` / `CW` drop less, and stay higher in natural / costumed renderings than in formal ones | B4 E1, E2, E5 | Holliday ✓ (CoT reduces fallacies); Hagendorff [B]; Richardson ✓ (non-thinking) | TH B4 weight ≥ direct, or interpretive members fall as much as surface ones | low–med |
| **P8** | **Premise reversal acts on order-sensitive members.** A reversal effect in *yes/no* format in direct mode loads onto `ETR-1p` / `MATCH-L` / `ONL(k)` / `PRIMACY`, not onto PyETR's default procedure, which predicts none there ([B4_C4](../verticals/B4_C4_restrict_online.md) §0) | B4 E1 (F × O), E3 | Reversal reduces fallacies (Richardson ✓); Chen 2024 [B] | No reversal effect in yes/no format | med |
| **P9** | **Phantom constraints are structured.** Hallucinated colouring edges concentrate on pairs that are co-mentioned or textually adjacent (B4 `ADD-CONSTRAINT`), not spread uniformly over non-edges (`PERCEPTION-NOISE`) | B4 E6a; D_F E6 (edge echo); A_H E7 | Existence: Heyman ✓. Structure: conjecture, from attention locality and copying | Phantom edges uniform over non-edges | low |
| **P10** | **Nuisance mass is large above n\*.** In TH, `NOISY-EXACT` + `PERCEPTION-NOISE` weight ≥ the largest single heuristic family's weight | All mixture fits; A_H E7; D_F E6 | Heyman ✓; Sinha ✓; Hazra ✓ | A heuristic family exceeds the nuisance total with separated intervals | med |
| **P11** | **Seeds anchor rather than get repaired.** Answers move toward a provided seed (`ECHO`, anchoring) more than F's simulated repair curve predicts | D_F E7 | Hint following (Turpin ✓; Chen 2025 [C]); self-critique weak (Stechly ✓) | The seed-distance slope matches the `MIN-CONFLICTS` simulation | low–med |
| **P12** | **No soft messages at best effort.** E E2 gives β_B ≈ 0 in TH (π_E,soft ≤ 0.1). Any E signal sits in direct mode, at radius ≤ 2 | E E1-S, E2 | Absence of evidence, plus the training argument; hop limits for the radius | β_B > 0 in the cells where A opposes it, in TH | low |
| **P13** | **`TEXTBOOK-TRANSFER` persists.** π_TT > 0 on inverted knapsack / colouring in direct mode; smaller but non-zero in TH | A_H E5 | EHOP ✓; McCoy 2024b [B] | π_TT ≈ 0 in direct mode | med |
| **P14** | **Size moves n\*, not the mixture.** Within gpt-oss and within Qwen3, mixtures differ less at matched n/n\* than at matched n. Distilled Qwen3-14B is closer to Qwen3-32B than gpt-oss-20b is | Hierarchical fit across verticals | Qwen3 report ✓; Yue ✓; Sinha ✓ | Size effects on π persist at matched n/n\* | low–med |
| **P15** | **The trace carries search state but not cues.** Corrupting written search state is followed (high corruption-following). Order and position cues that move answers are rarely verbalised | A_H E8; C E6; D_F E8; B4 E7 | Turpin ✓; Chen 2025 [C]; thought anchors are planning and backtracking sentences (Bogdan 2025 [C]) | Low corruption-following (post-hoc traces), or cues verbalised at rates close to their effect sizes | med |
| **P16** | **Underthinking above n\*.** Wrong TH answers above n\* show more strategy switches than right ones. The fitted `DPLL-b` b is well below what the token cap allows | D_F E1, E2; trace codes | Wang et al. 2025 ✓; Shojaee [A]; Hazra ✓ | Wrong answers use about the full cap on deep single-branch traces | med |

### 4.1 Findings most likely to fail to transfer to thinking models at best effort on NP-hard items

| Finding | Where it was measured | Transfer | Why |
|---|---|---|---|
| "Greedy reasoners": no backtracking in proof planning (Saparov & He 2023) | InstructGPT / GPT-3, few-shot CoT | **Low** (DS only) | Reasoning models backtrack (Hazra ✓; DeepSeek-AI 2025 ✓). It may reappear above n\* (P4) |
| GPT-4o "greedy search without backtracking" on 3-SAT (Hazra) | Non-thinking | **Low** | Same reason; R1 in the same paper behaves differently |
| Premise order drops accuracy by > 30% (Chen et al. 2024) | Non-thinking; deduction and R-GSM | **Low as accuracy; medium as fingerprints and length drift** | Thinking re-reads the premises. Order effects move to *which* answer is returned and to long traces (P3, P5) |
| Lost in the middle (Liu et al. 2024) | Long multi-document inputs | **Low for our short prompts; medium for the model's own 32k trace** | The long context that matters is self-generated, where self-conditioning applies (Sinha ✓) |
| Single-pass mechanisms: hop limits, bag of heuristics, logic circuits (Yang, Biran, Nikankin, Hong, Kim) | One forward pass, easy items | **Low at the procedure level; high at the step level** | CoT externalises the hops. These findings describe how *each step* is computed, so expect them in the structure of `NOISY-EXACT` slips |
| Human-like errors rise with capability (Koralus 2023; Richardson 2025; Eisape 2024) | Mostly non-thinking models; short items | **Uncertain below n\*; open above** | CoT reduces conditional fallacies (Holliday ✓). Intuitive errors fade (Hagendorff [B]) |
| Search mechanisms in toy models (Saparov 2025; Ye 2025; SoS; Searchformer; Shah 2024) | Trained from scratch on one task | **Analogy only** | Different training data, scale and objective [→T2] |
| Greedy difficulty predicts reasoning-model colouring errors (Heyman & Zylberberg 2025a) | Reasoning models | **None** | Its authors later found the correlation "not causally significant": it was confounded with edge count, and reversed once edge count was fixed (2025b ✓, App. A) |
| Hallucinated edges (Heyman 2025b) | Six reasoning models on colouring | **High** | Same model class and task |
| NN as the opening move (AlgoTrace) | Phi-4-Reasoning, TSP up to 13 cities | **Medium–high, for the first candidate** | Same regime; final answers may differ |
| Distractor clauses (GSM-NoOp, Mirzadeh 2025) | Maths word problems, including o1-preview (−17.5 points) | **Medium** | Supports an effect of the "irrelevant constraint" manipulation in TH |

---

## 5. Contradictions and corrections found

1. **Slice A cites a withdrawn correlation.** [A_hardness_compute.md](../literature/A_hardness_compute.md) says reasoning models' colouring errors spike when a randomized greedy colorer rarely succeeds (Heyman & Zylberberg 2025a). The authors' later paper says "later validation experiments that we conducted yielded evidence that this correlation is not causally significant". The correlation tracked edge count, and at fixed edge count error was *lower* on low-greedy-score problems (2505.12151 v3, App. A ✓). **Do not use 2025a as support for greedy behaviour.**
2. **Which way the default goes.**
   - Zhang, Chen & Chen 2026 [A]: models are biased toward SAT.
   - Hazra ✓: LLMs answer "UNSAT" because the problem looks complex.
   - Heyman ✓: R1 claims "uncolourable" falsely because of phantom edges.

   P1 reconciles these by mode. Treat it as a hypothesis, not a settled finding.
3. **Does effort track hardness?** ZebraLogic ✓ and SMTrap ✓ find output length tracks solver conflicts. Verma 2026 [A] finds token spend doesn't track proof hardness once length is controlled. The hardness measures differ (search conflicts vs resolution proof size); P2 is designed to adjudicate.
4. **What RL adds.** Yue et al. 2025 ✓ (bounded by the base model) vs ProRL ✓ (prolonged RL expands it).
5. **Version-sensitive wording.** Sinha et al. 2025 say in some versions that thinking models are "not affected" by self-conditioning; v3 says thinking "mitigates" it. Cite the version.
6. **Not contradictions, but scoped:**
   - Saparov et al. 2025 (in-context search CoT doesn't fix learning to search) vs SoS / Searchformer (training on search traces works). The tasks and training setups differ.
   - Qin et al. 2025: backtracking helps on Sudoku and hurts on CountDown.
   - Nikankin vs Kantamneni & Tegmark on the level of analysis is already flagged in slice C.
7. **Venues not confirmed:**
   - Stream of Search is often cited as COLM 2024, but only arXiv was confirmed.
   - Searchformer was confirmed only as arXiv plus the ICLR 2024 LLMAgents workshop.
   - Gandhi et al. 2025 and Liu et al. 2025 (R1-Zero): arXiv only.
   - Richardson et al.'s arXiv page lists no venue. ICLR 2026 is kept per [LITERATURE.md](../LITERATURE.md) §5.
   - Hazra et al.'s arXiv page lists no venue. COLM 2025 is per slice B.
8. **Detail not found.** Slice B's AlgoTrace detail "especially when > 8 cities" was not found in the part of the full text checked here (the first 100k characters). The directional claim, NN more common in Phi-4-Reasoning, is confirmed.

---

## 6. Open questions

1. **Are phantom constraints structured?** This decides whether the largest documented reasoning-model error source is a B4 heuristic or a nuisance term (P9). Answering it needs the edge-echo and co-mention designs, not accuracy.
2. **What is the stopping rule above n\*?** Is b set by the token cap, by an estimate of difficulty, or by a learned prior on trace length? Underthinking and Shojaee's falling effort suggest the model's own estimate. If so, `DPLL-b` should be fitted with b as a function of item features (family I), not of budget.
3. **What is the direct mode of a thinking-trained model?** Is it base-like, or compressed thinking? Qwen3's no-think mode was trained by SFT after reasoning RL. If it carries RL-shaped proposal habits, "direct" is not the "no reasoning" null that the A family assumes.
4. **Does length-driven position bias extend from multiple-choice to premise and constraint order in long traces?** Wang 2026 measured MCQ options only.
5. **No mechanistic precedent exists for any family in a thinking model mid-trace on an NP-hard item.** The tools exist: pre-CoT probes (Cox 2026 [C]), backtracking steering (Venhoff [C]), thought anchors (Bogdan [C]). No one has pointed them at heuristic state.
6. **Does maths/code RL transfer to puzzle search?** Qwen3's reasoning RL contained no puzzles. gpt-oss's data is undisclosed. AlgoTrace's Phi-4-Reasoning result suggests reasoning training *adds* greedy construction on TSP. Whether that generalises to colouring and SAT is untested.
7. **Is E testable at best effort at all?** If E exists only inside forward passes, as the value heuristic, it may be identifiable only through E-in-D value choices (E vertical E5, E6), with low power.

---

## References

Status marks as above. Links are arXiv or the publisher's page.

**Verified in this session (✓)**

- Chen, X., et al. (2024). *Do NOT Think That Much for 2+3=? On the Overthinking of o1-Like LLMs.* arXiv 2412.21187.
- DeepSeek-AI (Guo, D., et al.) (2025). *DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning.* Nature 645: 633–638. arXiv 2501.12948. The R1-Zero passage on learning to "allocate more thinking time … by reevaluating its initial approach" was confirmed via secondary quotation only.
- Duchnowski, A., Pavlick, E., & Koller, A. (2025). *A Knapsack by Any Other Name: Presentation impacts LLM performance on NP-hard problems* (EHOP). EMNLP 2025 (Findings per slice B). arXiv 2502.13776. Abstract only.
- Dziri, N., et al. (2023). *Faith and Fate: Limits of Transformers on Compositionality.* NeurIPS 2023. arXiv 2305.18654.
- Gandhi, K., Lee, D., Grand, G., Liu, M., Cheng, W., Sharma, A., & Goodman, N. D. (2024). *Stream of Search (SoS): Learning to Search in Language.* arXiv 2404.03683.
- Gandhi, K., Chakravarthy, A., Singh, A., Lile, N., & Goodman, N. D. (2025). *Cognitive Behaviors that Enable Self-Improving Reasoners, or, Four Habits of Highly Effective STaRs.* arXiv 2503.01307.
- Hazra, R., Venturato, G., Zuidberg Dos Martires, P., & De Raedt, L. (2025). *Have Large Language Models Learned to Reason? A Characterization via 3-SAT Phase Transition.* arXiv 2504.03930. Full text v1 checked for the quoted sentences.
- Heyman, A., & Zylberberg, J. (2025a). *Evaluating the Systematic Reasoning Abilities of Large Language Models through Graph Coloring.* arXiv 2502.07087. Its greedy-score correlation is superseded by 2025b.
- Heyman, A., & Zylberberg, J. (2025b). *Reasoning Large Language Model Errors Arise from Hallucinating Critical Problem Features.* arXiv 2505.12151 (v3). Main text and App. A checked.
- Holliday, W. H., Mandelkern, M., & Zhang, C. E. (2024). *Conditional and Modal Reasoning in Large Language Models.* EMNLP 2024, 3800–3821.
- Kim, N., & Schuster, S. (2023). *Entity Tracking in Language Models.* ACL 2023, 3835–3855.
- Lehnert, L., et al. (2024). *Beyond A\*: Better Planning with Transformers via Search Dynamics Bootstrapping* (Searchformer). arXiv 2402.14083; ICLR 2024 LLMAgents workshop.
- Li, B. Z., Guo, Z. C., & Andreas, J. (2025). *(How) Do Language Models Track State?* ICML 2025. arXiv 2503.02854.
- Li, K., Hopkins, A. K., Bau, D., Viégas, F., Pfister, H., & Wattenberg, M. (2023). *Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task.* ICLR 2023. arXiv 2210.13382.
- Lin, B. Y., et al. (2025). *ZebraLogic: On the Scaling Limits of LLMs for Logical Reasoning.* ICML 2025. arXiv 2502.01100.
- Lippl, S., McGee, T., Lopez, K., Pan, Z., Zhang, P., Ziadi, S., Eberle, O., & Momennejad, I. (2025). *AlgoTrace: Algorithmic Primitives and Compositional Geometry of Reasoning in Language Models.* arXiv 2510.15987. Full text partly checked.
- Liu, M., Diao, S., Lu, X., Hu, J., Dong, X., Choi, Y., Kautz, J., & Dong, Y. (2025). *ProRL: Prolonged Reinforcement Learning Expands Reasoning Boundaries in Large Language Models.* NeurIPS 2025. arXiv 2505.24864.
- Liu, N. F., et al. (2024). *Lost in the Middle: How Language Models Use Long Contexts.* TACL 12: 157–173.
- Liu, Z., et al. (2025). *Understanding R1-Zero-Like Training: A Critical Perspective.* arXiv 2503.20783.
- Lu, J., Xu, Z., & Kankanhalli, M. (2025). *Reasoning LLMs are Wandering Solution Explorers.* arXiv 2505.20296.
- Mirzadeh, I., Alizadeh, K., Shahrokhi, H., Tuzel, O., Bengio, S., & Farajtabar, M. (2025). *GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in Large Language Models.* ICLR 2025. arXiv 2410.05229.
- Nanda, N., Lee, A., & Wattenberg, M. (2023). *Emergent Linear Representations in World Models of Self-Supervised Sequence Models.* BlackboxNLP 2023. arXiv 2309.00941.
- Olsson, C., et al. (2022). *In-context Learning and Induction Heads.* Transformer Circuits Thread. arXiv 2209.11895.
- OpenAI (2025). *gpt-oss-120b & gpt-oss-20b Model Card.* arXiv 2508.10925.
- Qin, T., Alvarez-Melis, D., Jelassi, S., & Malach, E. (2025). *To Backtrack or Not to Backtrack: When Sequential Search Limits Model Reasoning.* COLM 2025. arXiv 2504.07052.
- Qwen Team (2025). *Qwen3 Technical Report.* arXiv 2505.09388. Pipeline, distillation and RL-data claims checked in the full text.
- Richardson, A. K., Kearns, R. O., Moss, S., Wang-Maścianica, V., & Koralus, P. (2025). *Theory-Grounded Evaluation of Human-Like Fallacy Patterns in LLM Reasoning.* ICLR 2026 (per LITERATURE.md §5). arXiv 2506.11128. Abstract checked.
- Sanford, C., Fatemi, B., Hall, E., Tsitsulin, A., Kazemi, M., Halcrow, J., Perozzi, B., & Mirrokni, V. (2024). *Understanding Transformer Reasoning Capabilities via Graph Algorithms.* NeurIPS 2024. arXiv 2405.18512.
- Saparov, A., Pang, R. Y., Padmakumar, V., Joshi, N., Kazemi, M., Kim, N., & He, H. (2023). *Testing the General Deductive Reasoning Capacity of Large Language Models Using OOD Examples.* NeurIPS 2023. arXiv 2305.15269.
- Shi, F., Chen, X., et al. (2023). *Large Language Models Can Be Easily Distracted by Irrelevant Context.* ICML 2023. arXiv 2302.00093.
- Sinha, A., Arun, A., Goel, S., Staab, S., & Geiping, J. (2025). *The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs.* arXiv 2509.09677; ICLR 2026 poster.
- Stechly, K., Valmeekam, K., & Kambhampati, S. (2025). *On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks.* ICLR 2025. arXiv 2402.08115.
- Turpin, M., Michael, J., Perez, E., & Bowman, S. R. (2023). *Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting.* NeurIPS 2023. arXiv 2305.04388.
- Wang, S., et al. (2024). *ALPINE: Unveiling the Planning Capability of Autoregressive Learning in Language Models.* arXiv 2405.09220.
- Wang, X. (2026). *More Thinking, More Bias: Length-Driven Position Bias in Reasoning Models.* arXiv 2605.06672.
- Wang, Y., et al. (2025). *Thoughts Are All Over the Place: On the Underthinking of o1-Like LLMs.* arXiv 2501.18585.
- Wu, X., Wang, Y., Jegelka, S., & Jadbabaie, A. (2025). *On the Emergence of Position Bias in Transformers.* ICML 2025. arXiv 2502.01951.
- Xie, T., et al. (2025). *Logic-RL: Unleashing LLM Reasoning with Rule-Based Reinforcement Learning.* arXiv 2502.14768. Setup checked; its AIME-transfer claim was not.
- Yang, J., et al. (2026). *SMTrap: Cost-Effective DoS Attacks Against Large Reasoning Models via SMT Conflict Guidance.* arXiv 2608.18921.
- Yue, Y., et al. (2025). *Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?* NeurIPS 2025 (oral). arXiv 2504.13837.
- Zhao, R., Meterez, A., Kakade, S., Pehlevan, C., Jelassi, S., & Malach, E. (2025). *Echo Chamber: RL Post-training Amplifies Behaviors Learned in Pretraining.* COLM 2025 (per arXiv). arXiv 2504.07912.
- Zheng, C., Zhou, H., Meng, F., Zhou, J., & Huang, M. (2024). *Large Language Models Are Not Robust Multiple Choice Selectors.* ICLR 2024. arXiv 2309.03882.
- Zhu, H., et al. (2025). *Reasoning by Superposition: A Theoretical Perspective on Chain of Continuous Thought.* NeurIPS 2025. arXiv 2505.12514. The full author list was not checked.

**Verified in earlier slices** (claims as reported there; full entries in [B](../literature/B_heuristics_behaviour.md), [C](../literature/C_interpretability.md), [A](../literature/A_hardness_compute.md))

- [B]:
  - Aoki et al. 2024;
  - Bertolazzi, Gatt & Bernardi 2024;
  - Chen, Chi, Wang & Zhou 2024 (*Premise Order Matters*);
  - Eisape et al. 2024;
  - Hagendorff, Fabi & Kosinski 2023;
  - Kambhampati et al. 2024;
  - Koralus & Wang-Maścianica 2023;
  - Lampinen, Dasgupta et al. 2024 (PNAS Nexus);
  - Macmillan-Scott & Musolesi 2024;
  - McCoy et al. 2024a (PNAS, *Embers of autoregression show how large language models are shaped by the problem they are trained to solve*);
  - McCoy et al. 2024b (o1);
  - Mondorf & Plank 2024;
  - Ruis et al. 2025;
  - Saparov & He 2023;
  - Tang et al. 2025 (GraphArena);
  - Wu et al. 2024 (*Reasoning or Reciting?*);
  - Zhang, Li, Meng, Chang & Van den Broeck 2023.
- [C]:
  - Biran et al. 2024;
  - Bogdan et al. 2025;
  - Brinkmann et al. 2024;
  - Chen et al. 2025 (*Reasoning Models Don't Always Say What They Think*);
  - Cox, Kianersi & Garriga-Alonso 2026;
  - Csordás, Manning & Potts 2025;
  - Feng & Steinhardt 2024;
  - Hanna & Ameisen 2026;
  - Hong et al. 2025;
  - Hu, Zhou & Zhang 2025;
  - Jenner et al. 2024;
  - Kantamneni & Tegmark 2025;
  - Kim, Valentino & Freitas 2025;
  - Lindsey et al. 2025 (*On the Biology of a Large Language Model*; method in Ameisen et al. 2025);
  - Nikankin, Reusch, Mueller & Belinkov 2025;
  - Saparov et al. 2025 (*Transformers Struggle to Learn to Search*);
  - Shah et al. 2024;
  - Venhoff et al. 2025;
  - Ward et al. 2025;
  - Yang, Gribovskaya, Kassner, Geva & Riedel 2024;
  - Yao, Du, Zhu, Hahn & Koller 2025;
  - Ye, Fu, Jia & Sharan 2025.
- [A]:
  - Feng et al. 2023;
  - Pan et al. 2025;
  - Shojaee et al. 2025;
  - Verma 2026;
  - Zhang, Chen & Chen 2026 (FSE).

**Unverified leads [?]**

- *Assessing judging bias in large reasoning models* (arXiv 2504.09946). The search snippet said LRMs prefer later positions in judging. Not read.
- arXiv 2512.12620, *Understanding Syllogistic Reasoning in LLMs from Formal and Natural Language Perspectives*. The snippet said belief bias falls as reasoning ability rises. Not read; would bear on P7.
- The gpt-oss reasoning modes: whether there is a true no-reasoning setting.
