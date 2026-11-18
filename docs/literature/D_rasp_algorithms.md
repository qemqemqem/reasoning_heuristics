> Research-agent report written 2026-11-13 for the literature review in [../LITERATURE.md](../LITERATURE.md). Every paper was found by web search or fetch during the review; the most decision-relevant claims were then spot-checked against the source (see LITERATURE.md, "How this review was done"). Treat other details as leads to confirm before citing.

# Lit review slice D: RASP, RASP-L, and what algorithms transformers learn

*Covers O6 (§3) and H2 (§4) of `heuristics-under-hardness/docs/DESIGN.md`. Searched and fetched 2026-11-13.*

**Scope note.** The session's shared web-search budget ran out partway through. All of §1–§5 below rests on papers I searched for or fetched in this session. Two planned searches did not run: one on from-scratch transformers trained on random 3-SAT and learning statistical shortcuts, and one final sweep for "RASP + SAT". Those gaps are listed under Unverified.

Where I read the paper itself (PDF text extracted), I say so. These are Zhou et al. 2024, ALTA, Huang et al. 2025, Huang et al. 2026 (decompiling) and Cheng 2025. For the rest I read only the abstract page or HTML.

---

## Summary

- **"The RASP-L paper" is confirmed.** It is Zhou, Bradley, Littwin, Razin, Saremi, Susskind, Bengio & Nakkiran, *What Algorithms can Transformers Learn? A Study in Length Generalization*, ICLR 2024 (arXiv 2310.16028). The arXiv listing still says "Preprint", but the ICLR 2024 proceedings list it. A reference NumPy implementation exists: `apple-aiml-research/ml-np-rasp`.
- **The core of the "heuristic RASP-L hypothesis" is already in Zhou et al.** Their *Toy Model (RASP MDL Principle)* reads: "Transformers tend to learn the shortest RASP-L program which fits the training set." Their forward-addition experiment is already a case of a short shortcut program that fits in-distribution (short carry chains) and fails on hard carries. What is new in our version:
  - applying it to NP-hard tasks;
  - the imperfect-fit regime, where no short program fits the training set, so we need an accuracy-versus-length trade-off;
  - identifying the heuristic from its error signatures;
  - extending it to pretrained LLMs.
- **The formal successor is C-RASP plus Limit Transformers.** Huang et al. (ICLR 2025, with Zhou and Nakkiran as co-authors) "formalize the RASP-L Conjecture": idealized norm-regularized learning length-generalizes on functions expressible by a Limit Transformer, and C-RASP programs give lower bounds. Work from 2026 shows three things:
  - length-generalization bounds are **uncomputable** for full C-RASP;
  - they are exponential and optimal for C-RASP+ (equivalent to fixed-precision transformers);
  - sample size scales **exponentially in the size of the smallest formula**. For example, PARITY_k is definable in C-RASP yet fails in practice.
- **The strongest direct support for H2's mechanism comes from Ye et al. (2025, graph connectivity).** When training graphs exceed the depth capacity of an L-layer model (diameter > 3^L), transformers learn a simple **node-degree heuristic**. When graphs stay within capacity, they learn the exact algorithm. Training data decides which is learned.
- **The strongest evidence against naive "shortest program" comes from two papers:**
  - **ALTA** (Shaw et al., TMLR 2025): end-to-end training matched a 31-rule program over a 7-rule one. The authors conclude there is no simplicity bias aligned with rule count, and that learned behaviour tracks the program needing the **fewest layers**.
  - **Huang et al. (ICML 2026, decompiling):** transformers that fail to length-generalize usually **cannot** be decompiled into short programs. The authors suggest that such models implement "heuristic … solutions, for which no short D-RASP program exists". That is the opposite of our framing. Even so, 3 of their 6 non-generalizing models did decompile when matched only on training lengths.
- **The program-length measure decides H2's outcome and is unsettled.** Candidates include RASP-L line count (Zhou), layer depth (ALTA's finding), C-RASP formula size (bounds papers), and pruned D-RASP lines (decompiler). Zhou et al. themselves say minimum RASP-L length is "likely intractable" to compute and does not map one-to-one onto transformer complexity.
- **Prediction 3 (CoT iterates a short program) has strong theoretical backing and mixed empirical results.**
  - Theory: CoT with T steps buys circuit size T (Li et al. 2024). Looped models iterate RASP-L steps and length-generalize (Fan et al. 2025, "n-RASP-L"). Turing-programme CoT is RASP-implementable (Hou et al. 2025). Length-generalizable softmax CoT C-RASP is Turing-complete (Jiang et al. 2025).
  - Against: Saparov et al. (ICLR 2025) report that in-context search (CoT) does **not** fix transformers' failure to learn search on larger graphs. Pan et al. (ICML 2025) report that DPLL-trace-trained SAT transformers generalize within trained sizes but degrade sharply beyond them.
- **Many zoo heuristics are not constant-depth RASP-L programs at all.** GREEDY, NN, DSATUR, WALK-k and UP-k for large k are inherently sequential. Under RASP-L's no-loops rule they need either depth that grows with k or n, or CoT. This affects which heuristics the direct-answer and thinking conditions can even express.
- **Reusable tools exist for every step of the O6 pipeline:**
  - ml-np-rasp: RASP-L interpreter;
  - Tracr (supports `causal=True`): compiler;
  - ALTA: loops and Universal Transformers;
  - D-RASP decompiler (lacoco-lab): extracts programs from trained models;
  - Learning Transformer Programs: programs that are interpretable by design;
  - InterpBench/SIIT: realistic known-circuit models;
  - ULTK-based RASP-L program enumeration (Cheng 2025);
  - C-RASP synthesis and verification via Kind2 (Jiang et al. IJCAI 2026).

---

## Key papers

| Citation | Link | Finding (what the paper claims) | Relevance | S / C / O |
|---|---|---|---|---|
| Weiss, Goldberg & Yahav 2021, *Thinking Like Transformers*, ICML 2021 | https://arxiv.org/abs/2106.06981 | Introduces RASP. Programs for histograms, sorting and Dyck. RASP analysis bounds the heads and layers needed. Transformers can be trained to mimic RASP solutions. | Base language for O6 | Background |
| **Zhou et al. 2024**, *What Algorithms can Transformers Learn? A Study in Length Generalization*, ICLR 2024 (read closely) | https://arxiv.org/abs/2310.16028 | RASP-Generalization Conjecture: length generalization is likely if (1) realizability, (2) simplicity (short RASP-L), (3) diversity (no *shorter* RASP-L program agrees in-distribution but not out-of-distribution). Toy model: "Transformers tend to learn the shortest RASP-L program which fits the training set." RASP-L is straight-line (no loops or branches), int8 values, restricted index ops (IndexInt). Explicitly "phenomenological, as opposed to mechanistic". Minimum program "likely intractable" to find. Forward addition learns a shortcut that fails on long carry chains. | Direct antecedent of H2 and of predictions 1–2 | **Overlaps** (strongly) / Supports |
| Huang, Yang, Bhattamishra, Sarrof, Krebs, Zhou, Nakkiran & Hahn 2025, *A Formal Framework for Understanding Length Generalization in Transformers*, ICLR 2025 (read intro) | https://arxiv.org/abs/2410.02140 | Limit Transformers. Idealized inference (fit up to length n while minimizing a norm-based regularizer over depth, heads, width and precision) provably length-generalizes on functions expressible by a Limit Transformer with PERIODIC/LOCAL positional terms. C-RASP gives lower bounds, communication complexity gives upper bounds. "Our results formalize the RASP-L Conjecture." Code: lacoco-lab/length_generalization. | Gives H2 a formal regularizer-based version of "shortest program" | Supports (formal) |
| Yang & Chiang 2024, *Counting Like Transformers: Compiling Temporal Counting Logic Into Softmax Transformers*, COLM 2024 | https://arxiv.org/abs/2404.04393 | Introduces C-RASP, equivalent to the counting logic K_t[#]. Compiles into future-masked softmax transformers with no length restriction. | Alternative, formally grounded dialect for zoo programs | Background |
| Yang, Bergsträßer, Zetzsche, Chiang & Lin 2026, *Length Generalization Bounds for Transformers*, arXiv (v2 May 2026) | https://arxiv.org/abs/2603.02238 | No computable length-generalization bounds exist for C-RASP, even with two layers. Computable, optimal, exponential bounds exist for positive C-RASP, which is equivalent to fixed-precision transformers. | Limits on how sharply program length can predict behaviour | Complicates |
| Zetzsche, Jiang, Yang, Bergsträßer, Sälzer, Chiang & Lin 2026, *Length Generalization for Transformers via Compression*, arXiv Sep 2026 | https://arxiv.org/abs/2609.08851 | Calls the C-RASP hypothesis "a formalized version of the RASP-l conjecture". Seemingly contradicting experiments: PARITY_k is C-RASP-definable but fails. Resolution: sample size is exponential in the smallest C-RASP+/C-RASP1 formula size, an exponential improvement on the prior doubly-exponential bound. COUNT_k and MAJ_k have O(log k) formulas, so polynomial sample size. | Program size sets the **data needed**, not only what is learnable. Implies a dataset-size sweep for H2. | Supports (refined) / Complicates |
| **Shaw et al. 2025, *ALTA: Compiler-Based Analysis of Transformers*, TMLR 2025** (read closely) | https://arxiv.org/abs/2410.18077 | RASP/Tracr-like language with loops, compiles to Universal Transformers. A "minimal program w.r.t. training set" criterion (Theorems 1–2: a minimal rule set gives a strict coordinate-wise local optimum). Minimal-program generalization predicts trace-supervised generalization. **But** end-to-end training on parity matches the 31-rule Sum+Modulo program, not the 7-rule Sequential one. "Transformers … do not have an inherent simplicity bias that aligns with the number of transition rules". Behaviour tracks "the algorithm that requires the fewest layers". Code: google-deepmind/alta. | Program-length measure for H2; depth versus count | **Contradicts** naive H2 (under a count measure) / Supports a depth version |
| **Huang, Bakalova, Bhattamishra, Merrill & Hahn 2026, *Discovering Interpretable Algorithms by Decompiling Transformers to RASP*, ICML 2026** (read closely) | https://arxiv.org/abs/2602.08857 | Re-parameterizes trained transformers as D-RASP (a rounded fragment is equivalent to C-RASP), then prunes causally to a minimal sufficient sub-program. Recovers short programs for 9 of 14 length-generalizing formal languages. Fails on non-generalizing ones, and suggests these "may internally implement heuristic, non-length-generalizable solutions, for which no short D-RASP program exists". Matching only on training lengths, 3 of 6 non-generalizing models become decompilable and 3 stay dense. Pareto frontier of lines of code against match accuracy. Code: lacoco-lab/decompiling_transformers. | The ideal test tool for O6 toy models. Their view of heuristics is the **opposite** of H2's. | **Overlaps** (tools) / Contradicts (framing) / Mixed |
| Cheng 2025, *Beyond Memorization: Evaluating Length-Generalization in Transformer-based Language Models*, MS thesis, Univ. of Washington (read abstract and methods) | https://digital.lib.washington.edu/server/api/core/bitstreams/47d8692d-3df9-460a-b3ba-e122f8bc1d82/content | Enumerates hundreds of binary tasks with *shortest* RASP-L programs (via ULTK, built on ml-np-rasp). "Our investigation does not support the conjecture." Some failures come from the model not knowing when to stop, and are fixed with oracle length. | Only direct empirical counter-test of the RASP-L conjecture found. Also a program-enumeration tool. | **Contradicts** (non-peer-reviewed) |
| **Ye, Fu, Jia & Sharan 2025, *Transformers Provably Learn Algorithmic Solutions for Graph Connectivity, But Only with the Right Data*** (v1 title: *When Do Transformers Learn Heuristics for Graph Connectivity?*), arXiv | https://arxiv.org/abs/2510.19753 | An L-layer disentangled transformer can solve connectivity up to diameter 3^L (adjacency powering). Training dynamics: within-capacity graphs promote the algorithm, while beyond-capacity connected pairs promote a degree-product **heuristic**. Capacity-aware data curation makes standard transformers learn the algorithm. RASP is mentioned only in related work. | The closest prior statement of "capacity-limited means heuristic, and training data picks which". Template for the O6 toy study. | **Supports** / **Overlaps** |
| Liu, Ash, Goel, Krishnamurthy & Zhang 2023, *Transformers Learn Shortcuts to Automata*, ICLR 2023 | https://arxiv.org/abs/2210.10749 | o(T)-layer transformers can simulate automata. O(log T)-depth solutions always exist and O(1)-depth ones are common (Krohn–Rhodes). Standard training finds shortcuts, and the authors study how brittle they are. | Precedent for "shallow programs fitting the distribution" being what gets learned | Supports |
| Kawata et al. 2025, *From Shortcut to Induction Head: How Data Diversity Shapes Algorithm Selection in Transformers*, NeurIPS 2025 | https://arxiv.org/abs/2512.18634 | Proves that a max-sum distance ratio in the training data decides between a positional shortcut and an induction head in one-layer transformers. | Data diversity decides which "program" is selected, as in Zhou's condition 3 | Supports |
| **Fan, Du, Ramchandran & Lee 2025, *Looped Transformers for Length Generalization*, ICLR 2025** | https://arxiv.org/abs/2409.15647 | Defines n-RASP-L: tasks solved by iterating a RASP-L step a number of times that depends on length. Looped transformers with adaptive step counts length-generalize on copy, parity and addition without intermediate supervision. | Formal home for prediction 3: propagation loops are n-RASP-L | Supports / Overlaps (prediction 3) |
| Saunshi, Dikkala, Li, Kumar & Reddi 2025, *Reasoning with Latent Thoughts: On the Power of Looped Transformers*, ICLR 2025 | https://arxiv.org/abs/2502.17416 | A k-layer model looped L times about matches a kL-layer model on reasoning tasks. Looped models can simulate T CoT steps with T loops. | Links CoT and loops for prediction 3 | Supports |
| Li, Liu, Zhou & Ma 2024, *Chain of Thought Empowers Transformers to Solve Inherently Serial Problems*, ICLR 2024 | https://arxiv.org/abs/2402.12875 | Constant-depth transformers without CoT are limited to TC0 (AC0 at constant bit precision). With T CoT steps they solve any problem with a circuit of size T. | Theory for prediction 3 | Supports |
| Hou, Brandfonbrener, Kakade, Jelassi & Malach 2025, *Universal Length Generalization with Turing Programs*, ICML 2025 | https://arxiv.org/abs/2407.03310 | A CoT that imitates Turing-machine steps (copy the tape, modify it once) length-generalizes on addition, multiplication and in-context SGD. Gives a RASP program that simulates any TM. | Prediction 3: a short per-step program, iterated | Supports |
| Jiang, Hahn, Zetzsche & Lin 2025, *Softmax Transformers are Turing-Complete*, arXiv | https://arxiv.org/abs/2511.20038 | Length-generalizable softmax CoT transformers (CoT C-RASP) are Turing-complete (unary/letter-bounded case; general case with relative PE). Includes experiments. | Prediction 3, formal | Supports |
| Amiri Bavandpour, Huang, Rofin & Hahn 2025, *Lower Bounds for Chain-of-Thought Reasoning in Hard-Attention Transformers*, ICML 2025 | https://arxiv.org/abs/2502.02393 | CoT length must grow at least linearly with input size for parity, multiplication, median and reachability (UHAT, tight up to log factors). | Gives a floor on the thinking tokens an exact procedure needs (O2/H3) | Supports O2 |
| Saparov et al. 2025, *Transformers Struggle to Learn to Search*, ICLR 2025 | https://arxiv.org/abs/2412.04703 | Small transformers learn parallel reachable-set expansion (exponential in layers). They fail on larger graphs regardless of parameter count, and in-context search (CoT) does not fix this. Code: asaparov/learning_to_search. | Counter-evidence for prediction 3. Mechanistic template. | **Contradicts** prediction 3 (partially) |
| Pan, Ganesh, Abernethy, Esposo & Lee 2025, *Can Transformers Reason Logically? A Study in SAT Solving*, ICML 2025 | https://arxiv.org/abs/2410.07432 | Constructs a decoder-only transformer that decides 3-SAT via DPLL-equivalent CoT (non-uniform). PARAT compiles NumPy-subset specifications to PyTorch transformers. LLaMA-style models trained on traces reach about 98.5–99.99% within trained variable ranges, and performance "degrades drastically" beyond them. | Closest existing "SAT + compiled transformer + trained on traces" work. PARAT is an alternative to Tracr. | **Overlaps** (O5/O6 SAT controls) |
| Shah, Dikkala, Wang & Panigrahy 2024, *Causal Language Modeling Can Elicit Search and Reasoning Capabilities on Logic Puzzles*, NeurIPS 2024 | https://arxiv.org/abs/2409.10502 | Trained on solver-step sequences, transformers solve 94.21% of Sudokus. Step order is necessary. Candidate sets per cell are linearly decodable. | Prediction 3: a propagation-like state in CoT models. Probe template for O5. | Supports |
| Duan et al. 2026, *Interpreting Neural Combinatorial Optimization via Evolving Programmatic Bottlenecks*, NeurIPS 2026 | https://arxiv.org/abs/2606.19741 | Distills NCO policies (e.g. POMO, LEHD) into an LLM-evolved bank of readable heuristic programs mixed by a state-dependent router. Finds recurring decision patterns, e.g. "phase-adaptive" heuristics for TSP. | Like O3's mixture over heuristic programs, but for neural solvers | **Overlaps** (method) |
| Zhang, Ma, Cao & Lau 2025, *Probing Neural Combinatorial Optimization Models*, NeurIPS 2025 (spotlight) | https://arxiv.org/abs/2510.22131 | Probing (CS-Probing) shows NCO models encode low-level construction information plus higher-level decision knowledge. A search snippet says they test whether models avoid myopic nearest-node choices; not confirmed on the abstract page. | Learned NCO policies are not plain NN-greedy | Context |
| Narad, Boussioux & Wagner 2025, *Mechanistic Interpretability for Neural TSP Solvers*, arXiv | https://arxiv.org/abs/2510.21693 | SAEs on an RL-trained pointer-network TSP solver find convex-hull, cluster and separator features. | O5 tools on NP-hard neural solvers | Context |
| Zhang, Li, Meng, Chang & Van den Broeck 2023, *On the Paradox of Learning to Reason from Data*, IJCAI 2023 | https://arxiv.org/abs/2205.11502 | BERT trained on propositional reasoning fits in-distribution through statistical features, not the reasoning function. Such features are inherent and hard to remove. | From-scratch models learn shortcuts on logic tasks. A "statistical feature" is a heuristic that may not be a short program. | Supports O2 / Complicates H2 |
| Selsam et al. 2019, *Learning a SAT Solver from Single-Bit Supervision*, ICLR 2019 | https://arxiv.org/abs/1802.03685 | NeuroSAT (MPNN) trained only on SAT/UNSAT bits. Assignments can be decoded when it predicts SAT. Generalizes to other NP-complete encodings, but is not competitive. | Iterated message passing is a looped short program | Context |
| Friedman, Wettig & Chen 2023, *Learning Transformer Programs*, NeurIPS 2023 (oral) | https://arxiv.org/abs/2306.01128 | Trains constrained transformers that convert to discrete RASP-like Python programs, on par with standard transformers of similar size. Code: princeton-nlp/TransformerPrograms. | A way to get a learned program directly and measure its length | Tool |
| Lindner et al. 2023, *Tracr: Compiled Transformers as a Laboratory for Interpretability*, NeurIPS 2023 (spotlight) | https://arxiv.org/abs/2301.05062 | Compiles RASP to decoder-only transformers with known structure. The repo's compiler has `causal: bool = False`. | O5 controls | Tool |
| Gupta, Arcuschin, Kwa & Garriga-Alonso 2024, *InterpBench*, NeurIPS 2024 D&B | https://arxiv.org/abs/2407.14494 | Tracr weights are unrealistic. Strict IIT trains realistic models that keep a known circuit (86 models). Code: FlyingPumba/InterpBench. | More realistic O5 controls | Tool |
| Thurnherr & Riesen 2024, *Neural Decompiling of Tracr Transformers*, arXiv | https://arxiv.org/abs/2410.00061 | A learned decompiler recovers RASP from Tracr weights: over 30% exact, the rest mostly near-correct. | Alternative decompiler (Tracr-only) | Tool |
| Jiang, Hague, Rümmer & Lin 2026, *Synthesis and Verification of Transformer Programs*, IJCAI 2026 | https://ijcai.org/proceedings/2026/434 | C-RASP to Lustre/Kind2 for equivalence and inclusion checking. Simulated-annealing synthesis of C-RASP programs from examples. Program minimization. | Tooling to *find* the shortest program fitting data, the core operation behind H2 | Tool / Overlaps (partly) |
| Shaw, Cohan, Eisenstein & Toutanova 2026, *Bridging Kolmogorov Complexity and Deep Learning: Asymptotically Optimal Description Length Objectives for Transformers*, ICLR 2026 | https://arxiv.org/abs/2509.22445 | Asymptotically optimal MDL objectives exist for transformers. A variational objective favours low-complexity, well-generalizing solutions, **but standard optimizers fail to find them from random init**. | SGD does not reliably find the shortest program | Complicates H2 |
| Varma, Shah, Kenton, Kramár & Kumar 2023, *Explaining grokking through circuit efficiency*, arXiv | https://arxiv.org/abs/2309.02390 | Generalizing and memorizing circuits trade off efficiency (logit per parameter norm). There is a critical dataset size. Also ungrokking and semi-grokking. | Dataset size shifts which "program" wins: a predicted sweep for H2 | Supports (analogous) |
| Bhattamishra, Patel, Kanade & Blunsom 2023, *Simplicity Bias in Transformers and their Ability to Learn Sparse Boolean Functions*, ACL 2023 | https://arxiv.org/abs/2211.12316 | Transformers are biased towards low-sensitivity functions, more so than LSTMs. They learn k-sparse functions robustly. | Rival simplicity measure (sensitivity) | Alternative |
| Hahn & Rofin 2024, *Why are Sensitive Functions Hard for Transformers?*, ACL 2024 | https://arxiv.org/abs/2402.09963 | High-sensitivity solutions sit in isolated, sharp minima, which gives a low-sensitivity bias and explains PARITY's failure to length-generalize. | Rival measure. Low-sensitivity heuristics (FREQ, POLARITY) should be favoured. | Alternative / Supports a variant |
| Abbe, Bengio, Lotfi & Rizk 2023, *Generalization on the Unseen, Logic Reasoning and Degree Curriculum*, ICML 2023 | https://arxiv.org/abs/2301.13105 | Min-degree interpolator bias on unseen inputs. Zhou et al. give a counterexample that RASP-L predicts and min-degree does not. | Rival measure | Alternative |
| Abbe, Bengio, Lotfi, Sandon & Saremi 2024, *How Far Can Transformers Reason? The Globality Barrier and Inductive Scratchpad*, NeurIPS 2024 | https://arxiv.org/abs/2406.06467 | "Globality degree" predicts efficient learnability. High-globality tasks such as long syllogism chains are hard. Inductive scratchpads help. | Rival measure. Relevant to entailment chains. | Alternative |
| Goldblum, Finzi, Rowan & Wilson 2024, *The No Free Lunch Theorem, Kolmogorov Complexity, and the Role of Inductive Biases in Machine Learning*, ICML 2024 (position) | https://arxiv.org/abs/2304.05366 | Neural nets, including random and pretrained LMs, prefer low-Kolmogorov-complexity outputs. | General Occam backdrop | Supports (general) |
| Mingard, Rees, Valle-Pérez & Louis 2025, *Deep neural networks have an inbuilt Occam's razor*, Nature Communications 16:220 | https://arxiv.org/abs/2304.06670 | A Bayesian prior over functions is exponentially biased towards simple functions, cancelling their exponential growth in number. | General Occam backdrop | Supports (general) |
| Jobanputra et al. 2025, *Born a Transformer – Always a Transformer? On the Effect of Pretraining on Architectural Abilities*, NeurIPS 2025 | https://arxiv.org/abs/2505.21785 | Predictions from Huang et al.'s framework (an induction versus anti-induction asymmetry) carry over to pretrained LLMs. Pretraining does not remove fundamental length-generalization limits. | Evidence that from-scratch RASP-family predictions transfer to LLMs, which H2 needs | Supports (transfer) |
| Konda 2026, *Transformers Learn the Mestre-Nagao Heuristic*, arXiv | https://arxiv.org/abs/2606.15036 | A two-layer transformer trained on elliptic-curve rank learns a known number-theory heuristic. Learned neuron weights correlate with Mestre–Nagao weights at Spearman 0.997. | Precedent: a from-scratch model converges on a known compact heuristic, identified by matching against a candidate | Supports (analogous) |

---

## Novelty risks (blunt)

1. **The hypothesis itself is Zhou et al.'s toy model.** "Training finds the shortest RASP-L program that fits the training distribution" is a near-verbatim restatement of their RASP MDL Principle. Their condition 3 (diversity) and their forward-addition shortcut result already cover "a short program fits in-distribution and is wrong elsewhere". A reviewer will say H2 is the RASP MDL principle applied to new tasks.
   - **Defensible novelty:**
     - (a) the **imperfect-fit regime**, where no short program fits the training set and the claim becomes an accuracy-versus-length Pareto/MDL trade-off;
     - (b) NP-hard tasks, where the "correct" program provably cannot exist at constant depth;
     - (c) identifying the heuristic from **error signatures** rather than from OOD accuracy;
     - (d) the CoT/loop prediction for heuristics.
   - State this framing explicitly and cite Zhou et al. as the source.
2. **The Hahn lab (Saarland) has the whole toolchain and is publishing fast:** the C-RASP length-generalization theory, the D-RASP decompiler (ICML 2026), CoT lower bounds, and pretrained-LLM transfer. Their decompilation paper already raises the question of what non-generalizing models implement, and answers it the opposite way ("heuristic … no short program"). Pointing their decompiler at a model trained on random 3-SAT is an obvious next paper for them. **Highest scoop risk for O6's toy-model study.**
3. **Ye et al. 2025 already showed "beyond capacity means a simple heuristic; data curation means the algorithm"** for graph connectivity, with a training-dynamics proof. O6's toy-model study is the NP-hard, multi-heuristic generalization of this. We must cite it and position against it. Our difference is that for NP-hard tasks no depth is enough, so curation cannot rescue the exact algorithm, and the question is *which* heuristic.
4. **The Lin, Zetzsche and Chiang group (Kaiserslautern/Notre Dame) is building program-synthesis-from-data tools for C-RASP** (IJCAI 2026) and sample-size theory tied to formula size. "Learn the shortest C-RASP program fitting SAT data and compare it with what transformers learn" is within their reach.
5. **Mixture over heuristic programs for neural solvers is already done for NCO (EPB, NeurIPS 2026).** It uses LLM-evolved rule banks plus a router fitted to a teacher policy. That is close to O3's identification method, applied to trained solvers instead of LLMs. O3 still differs in its fixed, pre-registered zoo, error-conditioned agreement and manipulation signatures. Cite it.
6. **Pan et al. (ICML 2025) cover "SAT + compiled transformer + trained-on-traces"**, including a NumPy-subset compiler (PARAT). Our Tracr controls for SAT heuristics are incremental relative to this. Their open question (what trained models do beyond trained sizes) is something we can answer.
7. **No paper found that tests whether RASP-L (or C-RASP/D-RASP) program length predicts *which heuristic* a model uses on NP-hard reasoning, in toy models or LLMs.** I found no prior statement of the "heuristic RASP-L hypothesis" for NP-hard tasks. This is the claim to stake. Caveat: two planned searches were lost to the search budget (see top).

---

## Methods & resources to reuse

**RASP-family interpreters and compilers**
- **RASP-L reference (NumPy):** https://github.com/apple-aiml-research/ml-np-rasp (redirects from `apple/ml-np-rasp`). Contents:
  - `src/np_rasp/core.py` and `lib.py`, which hold the core ops plus the "standard library" (induction head, etc.);
  - `examples/add.py`.
  - Apple custom sample-code licence ("for reference and research purposes only"), so check it before vendoring.
  - The README points to **raskell** (Haskell RASP-L): https://github.com/charlesfrye/raskell (not inspected).
- **Original RASP interpreter:** https://github.com/tech-srl/RASP. **RASPy** (Python-embedded, by Sasha Rush): https://github.com/srush/raspy.
- **Tracr:** https://github.com/google-deepmind/tracr.
  - `compile_rasp_to_model(..., causal=False)` supports causal masking, which is required for RASP-L's causal semantics.
  - Tracr's RASP dialect is **not** RASP-L: there is no IndexInt type system or sel_width typing. Write zoo programs in one canonical dialect and translate.
- **ALTA** (loops, Universal Transformers, minimality analysis, trace supervision): https://github.com/google-deepmind/alta. Best fit for n-RASP-L heuristics (UP-k, WALK-k) and for ALTA's "minimal program w.r.t. training set" test.
- **PARAT** (Pan et al.) compiles NumPy-subset specs to PyTorch transformers and already implements DPLL/unit propagation. Code location not confirmed.

**Getting programs out of trained models**
- **D-RASP decompiler:** https://github.com/lacoco-lab/decompiling_transformers (blog: https://lacoco-lab.github.io/home/decompiling_transformers).
  - Its output is a Pareto frontier of lines of code against match accuracy, with success at ≥ 0.9 match. That is exactly the program-length measure prediction 1 needs, *measured on the trained model*.
  - Use it on O6 toy models: train on SAT/entailment, decompile, and compare the recovered program with the zoo.
- **Learning Transformer Programs:** https://github.com/princeton-nlp/TransformerPrograms. Learned programs come out discrete and their length is directly measurable.
- **Length-generalization framework code:** https://github.com/lacoco-lab/length_generalization.

**Finding or enumerating short programs**
- **ULTK** (used by Cheng 2025 to enumerate shortest RASP-L programs by semantic deduplication): https://github.com/CLMBRs/ultk. This can estimate the *shortest* program for a zoo heuristic, not just the one we happen to write.
- **C-RASP synthesis and verification** (Jiang et al., IJCAI 2026): simulated annealing over C-RASP plus Kind2 equivalence and minimization. Can search for the shortest C-RASP program that best fits a training set. Code location not confirmed.

**Realistic known-circuit models**
- **InterpBench / SIIT:** https://github.com/FlyingPumba/InterpBench. Train realistic models carrying a known heuristic circuit, which makes a better O5 control than raw Tracr weights.

**Experimental templates**
- **Capacity-controlled toy training:** Ye et al. 2025 (vary depth L against instance "reach"; show heuristic switching under data curation). Saparov et al. graph-search code: https://github.com/asaparov/learning_to_search.
- **Candidate matching by weights:** Konda 2026, which correlates neuron weights with a candidate heuristic's weights.
- **Program-length measures to pre-register** (report all of them; treat which one predicts as a result):
  1. RASP-L line count (Zhou);
  2. RASP-L "parallel depth" or layers (suggested by Zhou; ALTA's finding);
  3. number of attention ops (kqv/select) and MLP transition rules (ALTA);
  4. C-RASP formula size (bounds papers);
  5. pruned D-RASP lines at ≥ 0.9 match (decompiler);
  6. a two-part MDL code, L(program) + bits for the errors given the program, for the imperfect-fit regime.

---

## Suggested changes to DESIGN.md

1. **O6 background: state the conjecture's three conditions and cite the toy model.** The conjecture is "realizability + simplicity + diversity", and it is explicitly phenomenological. Cite the RASP MDL principle as the direct antecedent: "Transformers tend to learn the shortest RASP-L program which fits the training set." Rewrite the "heuristic RASP-L hypothesis" as an extension of it to the **imperfect-fit regime**. Claim novelty there, not on "shortest program".
2. **Formalize "fits the training distribution well" as a two-part MDL objective.** Choose P to minimize |P| + λ·err_train(P), or |P| + Σ code-length of errors. Then prediction 1 (Pareto frontier) follows from the objective rather than sitting beside it. Without this, H2 is underdetermined whenever no short program fits exactly.
3. **Add a dataset-size and diversity prediction.**
   - The prediction: as training-set size or diversity grows, the learned heuristic should move along the frontier towards longer, more accurate programs.
   - Why: Zetzsche et al. 2026 show sample size grows exponentially in the minimal program size, and Varma et al. show a critical dataset size.
   - Kawata et al. and Ye et al. show that data composition switches the learned mechanism.
   - This is a sharp test that is cheap to run in O6's toy study.
4. **Classify every zoo heuristic by expressibility.**
   - (a) Constant-depth RASP-L, for example FREQ, POLARITY, FIRST, MATCH, PRIMACY/RECENCY, and UP-k for small fixed k with O(k) layers.
   - (b) n-RASP-L, needing loops or CoT, for example GREEDY in mention order, NN tour construction, DSATUR, WALK-k, and plausibly the ETR update sequence.
   - RASP-L forbids loops, so class (b) is unavailable in the direct-answer condition except as truncated versions.
   - This makes prediction 3 concrete: thinking budget should move mixture weight from (a) to (b). Add the class as a column in the §3 zoo table and the heuristics metadata.
5. **Pre-register the program-length measures** (list above) and say which one H2's falsification criterion uses. ALTA found that learned behaviour follows the fewest-layers program, not the fewest-rules one. Under a count measure H2 could fail while holding under a depth measure. Decide in advance.
6. **Pin the input encoding.** RASP-L length depends heavily on tokenization and format (Zhou: reversed versus forward addition, index hints). Fix the CNF and entailment serialization before writing programs, and report sensitivity to one alternative encoding.
7. **Make the decompiler the main O6 test on toy models, beside the behavioural test.**
   - Prediction 2 ("short heuristics length-generalize their errors") becomes: models trained on NP-hard tasks are decompilable at *all* sizes into a short program matching a zoo heuristic.
   - Huang et al. 2026's finding that non-generalizing models are usually *not* decompilable is the main falsifier. Name it in §4.
8. **Separate toy-model claims from LLM claims.** The RASP conjecture concerns from-scratch training "to completion". For pretrained LLMs, "the training distribution" is pretraining plus post-training, so "shortest program fitting it" is not well-defined. State H2 strongly for toy models and as an analogy for LLMs. Cite Jobanputra et al. 2025 for evidence that RASP-family predictions transfer.
9. **O5 Tracr controls:**
   - compile with `causal=True`;
   - translate RASP-L to Tracr-RASP explicitly;
   - use ALTA for looped heuristics;
   - consider SIIT (InterpBench) so the control circuits sit in realistic weights.
10. **Add rival complexity measures to H2 as model comparison:** sensitivity (Bhattamishra et al.; Hahn & Rofin), min-degree (Abbe et al. 2023), globality (Abbe et al. 2024), depth (ALTA). The H2 result is then "RASP-L length predicts mixture weights better than X", which is stronger than "short wins".
11. **Add the citations above to §10**, at minimum Huang et al. 2025, Ye et al. 2025, ALTA, Huang et al. 2026, Fan et al. 2025, Zetzsche et al. 2026, Pan et al. 2025 and Saparov et al. 2025.

---

## Citation corrections (DESIGN.md §10, this slice)

| §10 entry | Status | Correction |
|---|---|---|
| Weiss, Goldberg & Yahav (2021). *Thinking Like Transformers.* ICML. | **Correct** | Optionally add arXiv 2106.06981 and PMLR 139:11080–11090. |
| Zhou et al. (2024). *What Algorithms can Transformers Learn? A Study in Length Generalization.* ICLR. | **Correct** (confirms §9 Q1) | Authors: Hattie Zhou, Arwen Bradley, Etai Littwin, Noam Razin, Omid Saremi, Josh Susskind, Samy Bengio, Preetum Nakkiran (Apple); arXiv 2310.16028. An earlier version appeared at the NeurIPS 2023 MATH-AI workshop. **Disambiguate:** a separate Zhou et al. 2024, *Transformers Can Achieve Length Generalization But Not Robustly* (arXiv 2402.09371, ICLR 2024 workshop), is cited in this literature as "Zhou et al. 2024b". Cite ours as Zhou, Bradley et al. 2024 or "2024a". |
| Lindner et al. (2023). *Tracr: Compiled Transformers as a Laboratory for Interpretability.* NeurIPS. | **Correct** | Authors: Lindner, Kramár, Farquhar, Rahtz, McGrath, Mikulik. NeurIPS 2023 Spotlight. arXiv 2301.05062. |
| Liu et al. (2023). *Transformers Learn Shortcuts to Automata.* ICLR. | **Correct** | Authors: Bingbin Liu, Jordan T. Ash, Surbhi Goel, Akshay Krishnamurthy, Cyril Zhang. ICLR 2023. arXiv 2210.10749. |
| §3 O6 text: "They conjecture that transformers length-generalise on a task when the task has a short RASP-L program." | **Incomplete** | The conjecture has three conditions (realizability, simplicity, diversity) and is "phenomenological, as opposed to mechanistic". The separate *Toy Model (RASP MDL Principle)* is what H2 extends, so cite it. |
| §3 O6 "starting from the Zhou et al. reference implementation" | **Exists** | https://github.com/apple-aiml-research/ml-np-rasp (Apple custom licence). |

No §10 entry in this slice is wrong on year, venue or title.

---

## Unverified / leads

These came up in this session only as citations inside fetched papers or as search snippets, or are recalled from memory. None is verified.

- **Chen et al. 2025, "non-asymptotic length generalization"** (partial computable bounds for one- and two-layer C-RASP). Cited by Yang et al. 2026 and Zetzsche et al. 2026; not fetched.
- **Butoi et al. 2025.** Cited by Zetzsche et al. as showing PARITY failures; not fetched.
- **C\*-RASP** (March 2026, growing alphabets; arXiv 2603.19954 per a search snippet). Not fetched.
- **Venue of Yang et al. 2026.** ICML 2026 slides for *Length Generalization Bounds for Transformers* appeared in search results (icml.cc/media/icml-2026/Slides/63411.pdf). The arXiv page lists no venue.
- **TracrBench** (Thurnherr & Scheurer): 121 RASP programs, some LLM-generated. Search snippet only; venue unknown.
- **Other Tracr decompilers:** Baker 2023 and Langosco et al. 2024, cited by Huang et al. 2026. Not fetched.
- **Michaud et al. 2024, *Opening the AI black box: program synthesis via mechanistic interpretability*** (arXiv 2402.05110; Entropy, Dec 2024). Found by search, abstract only. It distils RNNs to code (MIPS solved 32 of 62 tasks) and is a possible template for extracting heuristic programs.
- **Raju & Netrapalli 2026, *A model of errors in transformers*** (arXiv 2601.14175, ICML 2026). Offers a noise-accumulation account of LLM errors as an alternative to "the model uses a heuristic". Worth adding to O3's rival explanations. The abstract does not mention RASP-L, although a search snippet claimed the text frames the model as a RASP-L program.
- **Hong et al., *A Implies B: Circuit Analysis in LLMs for Propositional Logical Reasoning*** (arXiv 2411.04105, formerly *How Transformers Solve Propositional Logic Problems*). Circuits in Mistral and Gemma for a minimal propositional task. Relevant to O5's entailment work, but not read in depth.
- **Grokking as compression.** DeMoss et al., *The Complexity Dynamics of Grokking* (arXiv 2412.09810), and Liu, Zhong & Tegmark, *Grokking as Compression* (arXiv 2310.05918). Snippets only.
- **Rende et al. 2024, *A distributional simplicity bias in the learning dynamics of transformers*** (NeurIPS 2024, arXiv 2410.19637). Transformers learn low-order token interactions first. Abstract fetched; marginal relevance.
- **Redman et al. 2026, *Shortcut Solutions Learned by Transformers Impair Continual Compositional Reasoning*** (arXiv 2605.05495). BERT learns shortcuts while ALBERT, the looped version, learns a "for-loop-esque" solution. Weak support for prediction 3; abstract only.
- ***Learning How to Cube*** (arXiv 2605.16632). A 4B model post-trained to choose cubes for Cube-and-Conquer, analysed against CDCL heuristics. Snippet only.
- **ScienceDirect 2025, *Neural approaches to SAT solving: Design choices and interpretability*.** Suggests GNN SAT solvers resemble continuous MaxSAT relaxations. Snippet only.
- **Not searched (budget), from memory only:**
  - B-RASP / masked hard-attention, Yang, Chiang & Angluin (NeurIPS 2024);
  - Strobl et al., the TACL survey on transformer expressivity;
  - Giannou et al. 2023, *Looped Transformers as Programmable Computers*;
  - Malach 2023, *Auto-regressive next-token predictors are universal learners* (cited by Zhou et al. for the autoregressive "outer loop");
  - Nanda et al. 2023, progress measures for grokking;
  - Valle-Pérez et al. 2019, parameter-function-map simplicity bias;
  - Bachmann & Nagarajan 2024, *The Pitfalls of Next-Token Prediction*;
  - neural algorithmic reasoning, e.g. CLRS and Georgiev et al. on combinatorial optimisation.
- **Searches still to run:**
  1. from-scratch transformers on random 3-SAT near the phase transition and what statistical shortcut they learn;
  2. "RASP" with "SAT" or "graph coloring";
  3. 2026 workshop papers (ICML/NeurIPS 2026 MI and theory workshops) on heuristics and RASP.
