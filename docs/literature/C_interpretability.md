> Research-agent report written 2026-11-13 for the literature review in [../LITERATURE.md](../LITERATURE.md). Every paper was found by web search or fetch during the review; the most decision-relevant claims were then spot-checked against the source (see LITERATURE.md, "How this review was done"). Treat other details as leads to confirm before citing.

# Lit review slice C: mechanistic interpretability of reasoning, search and heuristics (O5, H5)

*Prepared 2026-11-13 for `heuristics-under-hardness/docs/DESIGN.md` §3 O5 and §4 H5. Every paper below was found by search or fetched in this session. Where I give my own reading rather than the paper's claim, it is marked **[interp]**. The session's web-search budget ran out near the end, so a few venue checks are listed under "Unverified" instead of being confirmed.*

---

## Summary

- **Pretrained LLMs on small logic problems already have published circuits.** Hong et al. (NeurIPS 2025) found a sparse, four-part circuit for "A or B implies C"-style propositional queries in Mistral-7B and Gemma-2-9B/27B. Kim et al. (Findings ACL 2025) found a syllogism circuit ("middle-term suppression") that world-knowledge heads contaminate, which they call belief bias. "Is there an entailment circuit?" is therefore not new. What is new is asking *which competing heuristic* that circuit implements on items where heuristics disagree, and especially on errors.
- **"Bag of heuristics" is an established finding with an established method.** Nikankin et al. (ICLR 2025) worked at neuron level. They classified ~91% of the top 3,200 circuit neurons in Llama3-8B into heuristic types (range, modulo, pattern…), ran ablations by heuristic type, and found that errors come from weak promotion of the correct logit, not from missing heuristics. A 2026 preprint (Sasaki et al.) did almost exactly our O3→O5 pipeline in a small domain: a linear surrogate over heuristic cues predicts the LM's choices, and DAS-style interventions on those cue subspaces shift its output.
- **Models trained on search tasks usually learn parallel or shortcut procedures, not textbook search.** Examples: parallel reachable-set expansion with exponential path merging (Saparov et al., ICLR 2025); a spectral rather than DP shortest-path method (Cohen et al. 2025); depth-limited backward chaining (Brinkmann et al. 2024). Ye et al. (2025/26) show a transformer learns the exact connectivity algorithm when training graphs fit its depth capacity, and a **node-degree heuristic** when they don't. That is a direct small-scale analogue of our "heuristics under hardness" thesis and of O6.
- **Learned look-ahead or planning does exist and is shown causally**, with probes plus patching. Examples: Leela chess with a 92% probe for the move two plies ahead (Jenner et al., NeurIPS 2024); a Sokoban RNN; rhyme planning in Claude 3.5 Haiku (Lindsey et al. 2025); latent planning that grows with scale in Qwen3 0.6B–14B (Hanna & Ameisen, ICLR 2026). In every case the evidence is position- or item-specific, an "existence proof", not proof of general search.
- **Per-forward-pass depth is a hard limit that LLMs don't adapt.** In Llama 3.1, Qwen 3 and OLMo 2, the second half of the layers mostly refines, and there is no evidence that extra depth composes more hops (Csordás et al., NeurIPS 2025). Long-CoT models don't raise effective depth, and depth doesn't grow with difficulty (Hu et al. 2025). Implicit k-hop needs layers linear in k and data exponential in k (Yao et al., EMNLP 2025). **[interp]** Our logit-lens prediction ("shallow heuristics: early, size-independent") will not discriminate on its own, because almost everything is size-independent in depth.
- **Causal abstraction and DAS need guard rails.** With unrestricted (non-linear) alignment maps, any network can be mapped to any algorithm, and random-init models score 100% on IOI (Sutter et al., NeurIPS 2025). Explanations are non-identifiable: several algorithms align with one network (Méloux et al., ICLR 2025). Subspace patching can activate dormant pathways (Makelov et al., ICLR 2024). Probes can read task format instead of computation (Sahoo et al. 2026). H5 as written ("decodable and causally used") can be satisfied by the wrong heuristic.
- **In reasoning models, the trace and the activations come apart.** Hints are verbalised only about 25% of the time for Claude 3.7 Sonnet and 39% for R1 (Chen et al. 2025). Answers are often linearly decodable *before* the CoT, with AUC > 0.9, and steering along that direction flips answers; the steered CoT then confabulates (Cox et al. 2026). Resampling-based "thought anchors" find that planning and backtracking sentences dominate (Bogdan et al. 2025). Backtracking is linearly steerable in R1-distills (Venhoff et al. 2025) and reuses a base-model direction (Ward et al. 2025).
- **Tooling for open models is now good.** circuit-tracer ships transcoders for:
  - Qwen3 0.6B / 1.7B / 4B / 8B / 14B;
  - Gemma-3 270M–27B, PT and IT, via Gemma Scope 2;
  - Gemma-2-2B, with both per-layer transcoders (PLTs) and cross-layer transcoders (CLTs);
  - Llama-3.2-1B and Llama-3.1-8B-Instruct;
  - GPT-OSS-20B.

  Qwen3 has thinking and non-thinking modes in one checkpoint plus transcoders, which makes it the best single target for O5/H5.
- **Ground-truth testbeds exist beyond Tracr.** InterpBench (NeurIPS 2024 D&B) has 86+ SIIT-trained models with known circuits and realistic weights. TracrBench has 121 compiled programs. ALTA (TMLR 2025) compiles programs with loops, which suits `UP-k`. MIB (ICML 2025) is a standard method benchmark: supervised DAS was best for causal-variable localisation, and SAE features were no better than neurons.
- **No prior work found that** (a) patches *premise-order* effects mechanistically, or (b) probes a pretrained LLM for SAT/coloring/knapsack heuristic state. Both look open, but both are cheap for others to do, so the scoop risk is real.

---

## Key papers

Legend for the last column: **S** supports H5, **C** contradicts or complicates H5, **O** overlaps our plan (novelty risk), **M** method or resource.

### A. Multi-step and logical reasoning inside one forward pass

| Citation | Link | Finding (paper's claim) | Relevance | S/C/O |
|---|---|---|---|---|
| Hong, Dikkala, Luo, Rashtchian, Wang, Panigrahy (2025). *A Implies B: Circuit Analysis in LLMs for Propositional Logical Reasoning.* NeurIPS 2025 (earlier arXiv title: "How Transformers Solve Propositional Logic Problems: A Mechanistic Analysis") | https://arxiv.org/abs/2411.04105 | Minimal propositional problem (rule like "A or B implies C" plus facts, query the truth of C). Causal mediation in Mistral-7B, Gemma-2-9B and 27B finds a sparse circuit with four modular sub-circuits; mechanisms are "analogous but not identical" across models. v1–v3 also had a 3-layer from-scratch model with linear probes plus interventions. | Same domain as our entailment pilot, no CoT, open models. The closest prior art to O5 on entailment. | **O**, **S** |
| Kim, Valentino, Freitas (2025). *Reasoning Circuits in Language Models: A Mechanistic Interpretation of Syllogistic Inference.* Findings of ACL 2025 | https://arxiv.org/abs/2408.08590 | Circuit discovery on symbolic syllogisms. A necessary and sufficient circuit with "middle-term suppression"; extra heads that encode world knowledge contaminate it (belief bias); the circuit is shared across sizes and families for schemes above 60% accuracy. Methods: activation patching, logit lens. Code public. | Content effects are a mechanism, not just behaviour. Directly relevant to our re-theming manipulation. **[interp]** Earlier versions described a first stage of "naive recitation of the first premise", which is a candidate substrate for `PRIMACY`/`FIRST`. | **O**, **S** |
| Brinkmann, Sheshadri, Levoso, Swoboda, Bartelt (2024). *A Mechanistic Analysis of a Transformer Trained on a Symbolic Multi-Step Reasoning Task.* Findings of ACL 2024 | https://arxiv.org/abs/2402.11917 | 6-layer transformer finding paths in 16-node trees. Backward chaining reaches about one step per layer, plus a "depth-bounded recurrent mechanism" in parallel that stores intermediate results at chosen positions. Correlational and causal evidence. | Template for "procedure state is stored at token positions". Shows layer count bounds the number of steps, which bears on `UP-k`. | **S**, **M** |
| Yang, Gribovskaya, Kassner, Geva, Riedel (2024). *Do Large Language Models Latently Perform Multi-Hop Reasoning?* ACL 2024 | https://aclanthology.org/2024.acl-long.550 | Strong evidence for the first hop (recall of the bridge entity) for some relation types; second-hop and full traversal evidence is "moderate"; highly context-dependent. | Even two latent steps are unreliable. | **C** (for deep heuristics) |
| Biran, Gottesman, Yang, Geva, Globerson (2024). *Hopping Too Late.* EMNLP 2024 | https://arxiv.org/abs/2406.12775 | The bridge entity is resolved early and the answer late. "Back-patching" a later state into an earlier layer fixes up to 66% of errors. | Errors from running out of layers. A patching design we can copy for "heuristic ran out of depth" errors. | **S**, **M** |
| Balesni, Korbak, Evans (2024, rev. 2025). *Lessons from Studying Two-Hop Latent Reasoning* (v2 title "The Two-Hop Curse") | https://arxiv.org/abs/2411.16353 | Fine-tuned Llama 3 8B and GPT-4o fail to compose two *synthetic* facts latently, but succeed when facts co-occur in training or prompt, or when one fact is natural. | Latent composition depends on co-occurrence. Relevant to the "approximate retrieval" residual. | **C** |
| Yao, Du, Zhu, Hahn, Koller (2025). *Language models can learn implicit multi-hop reasoning, but only if they have lots of training data.* EMNLP 2025 | https://arxiv.org/abs/2505.17923 | GPT-2-style models trained on k-hop (k = 2, 3, 4) need layers linear in k and data exponential in k. Curriculum helps but doesn't remove the growth. | Quantitative per-pass step budget, useful for predicting the maximum k of `UP-k` in no-CoT mode. | **C** (limits), **M** |
| Csordás, Manning, Potts (2025). *Do Language Models Use Their Depth Efficiently?* NeurIPS 2025 | https://arxiv.org/abs/2505.13898 | In Llama 3.1, Qwen 3 and OLMo 2, second-half layers contribute much less. Skipping them has a small effect. "Unable to find evidence that models are using increased depth to compose subresults" on multi-hop. | Directly undercuts the "decodable layer depends on size" contrast in O5's logit-lens row. Uses our candidate models. | **C** |
| Hu, Zhou, Zhang (2025). *What Affects the Effective Depth of Large Language Models?* arXiv | https://arxiv.org/abs/2512.14064 | In Qwen-2.5 1.5B–32B, effective depth ratio is stable. Long-CoT models show no increase in effective depth over their base models. Models don't use more layers for harder problems. | Supports the O6 prediction 3 framing (CoT iterates across tokens, not depth). | **C** for depth-based tests |
| Lin, Xie, Yuan, Yang (2025). *Implicit Reasoning in Transformers is Reasoning through Shortcuts.* Findings of ACL 2025 | https://arxiv.org/abs/2503.07604 | GPT-2 trained from scratch on multi-step math. Stepwise implicit reasoning appears only with fixed-pattern data; otherwise shortcuts. Activation patching. | Shortcut vs procedure, decided by the training distribution. | **S** (heuristics exist), **C** (not clean procedures) |

### B. Search and planning representations

| Citation | Link | Finding | Relevance | S/C/O |
|---|---|---|---|---|
| Saparov, Pawar, Pimpalgaonkar, Joshi, Pang, Padmakumar, Kazemi, Kim, He (2025). *Transformers Struggle to Learn to Search.* ICLR 2025 | https://arxiv.org/abs/2412.04703 | With the right data, small transformers learn graph connectivity by computing reachable sets for all vertices in parallel, each layer expanding them (exponential in layers). Found with a new computation-graph extraction method. Fails on larger graphs; more parameters and in-context CoT search don't fix it. | "Search" in transformers is parallel set-expansion, not DFS or BFS. A heuristic zoo should include parallel procedures. | **O**, **S** |
| Ye, Fu, Jia, Sharan (2025, rev. 2026). *Transformers Provably Learn Algorithmic Solutions for Graph Connectivity, But Only with the Right Data* (v1 title: "When Do Transformers Learn Heuristics for Graph Connectivity?") | https://arxiv.org/abs/2510.19753 | An L-layer (Disentangled) transformer can decide connectivity up to diameter 3^L by computing adjacency powers. Training graphs within that capacity yield the algorithm; graphs beyond it drive a **node-degree heuristic**. Proven through training dynamics and confirmed empirically. | **Very close to our core thesis and to O6 (heuristic RASP-L).** Also a ready-made positive and negative control: we can choose whether the toy learns the algorithm or the heuristic. | **O** (high), **S**, **M** |
| Cohen, Gromov, Yang, Tian (2025). *Spectral Journey: How Transformers Predict the Shortest Path.* ICLR 2025 workshop | https://arxiv.org/abs/2502.08794 | Two-layer transformers on shortest paths (≤ 10 nodes). No evidence of DP (Dijkstra or Bellman-Ford). Edge embeddings track line-graph Laplacian eigenvectors, followed by greedy navigation in that space ("Spectral Line Navigation"). Failures happen where many paths are near-optimal. | A learned heuristic nobody would have put in a zoo a priori. **[interp]** The zoo must allow "other". | **C** for zoo completeness, **S** for heuristics |
| Shah, Dikkala, Wang, Panigrahy (2024). *Causal Language Modeling Can Elicit Search and Reasoning Capabilities on Logic Puzzles.* NeurIPS 2024 | https://arxiv.org/abs/2409.10502 | A transformer trained on solver-step sequences solves 94.21% of Sudokus and 92.04% of Zebra puzzles. Without step traces it fails. Linear probes decode each cell's **candidate set**. | The direct precedent for "probe the heuristic's intermediate state" (candidate sets are constraint-propagation state). But the model was *trained on the solver's steps*, so the algorithm was supplied. | **O**, **S** |
| Jenner, Kapur, Georgiev, Allen, Emmons, Russell (2024). *Evidence of Learned Look-Ahead in a Chess-Playing Neural Network.* NeurIPS 2024 | https://arxiv.org/abs/2406.00877 | Leela represents future optimal moves, which are causally important in some positions. Evidence: activation patching on future-move squares, heads that move information "forward and backward in time", a probe predicting the move 2 plies ahead at 92% (where there is a single best line). Framed as an "existence proof", not general search. | The methodological model for "search vs heuristics": three converging lines, scoped claims. | **S**, **M** |
| Cruz (2025). *Understanding the learned look-ahead behavior of chess neural networks.* arXiv; MLAnthology lists TMLR 2025 | https://arxiv.org/abs/2505.21552 | Look-ahead is highly position-dependent, reaching up to 7 moves. Several candidate lines are considered. | Partial search, varying by instance. | **S** |
| Taufeeque et al. (2024); Taufeeque et al. (2025/26). *Planning in a recurrent neural network that plays Sokoban*; *Path Channels and Plan Extension Kernels* (ICLR 2026) | https://arxiv.org/abs/2407.15421 ; https://arxiv.org/abs/2506.10138 | Causal plan representation predicting actions about 50 steps ahead. The network "paces" to buy compute. Plan channels plus convolutional kernels extend plans forward from boxes and backward from goals, with pruning at obstacles. | A full mechanistic search-like account, in an RNN that has recurrence. **[interp]** Contrast case: transformers without CoT lack this recurrence. | **S** (in RNNs) |
| Spies, Edwards, Ivanitskiy, Skapars, Räuker, Inoue, Russo, Shanahan (2024). *Transformers Use Causal World Models in Maze-Solving Tasks.* arXiv | https://arxiv.org/abs/2412.11867 | SAE features and attention circuits agree on a maze world model. Feature interventions are causal; activation is easier than suppression. | SAE-plus-circuit agreement as cross-validation. | **M** |
| Men, Cao, Jin, Chen, Liu, Zhao (2024). *Unlocking the Future: Exploring Look-Ahead Planning Mechanistic Interpretability in LLMs.* EMNLP 2024 | https://arxiv.org/abs/2406.16033 | Llama-2-7B-chat and Vicuna-7B on Blocksworld. Middle-layer attention output at the last token decodes the decision. Middle and upper layers encode a few short-term future decisions, only when planning succeeds. | Pretrained-LLM probe for planning state in a classical planning domain. | **O**, **S** (weak) |
| Lindsey, Gurnee, Ameisen, Chen, Pearce, Turner, Citro, … Batson (2025). *On the Biology of a Large Language Model.* Transformer Circuits Thread, 27 Mar 2025 | https://transformer-circuits.pub/2025/attribution-graphs/biology.html | Claude 3.5 Haiku findings:<br>• Dallas→Texas→Austin two-hop, with swap interventions plus a parallel shortcut path.<br>• Rhyme planning: injecting the planned word makes it end the line 70% of the time (25 poems).<br>• Addition: a rough-magnitude path in parallel with an exact ones-digit path; the model's own explanation doesn't match.<br>• CoT: faithful (√0.64) vs "bullshitting" vs motivated backward reasoning (cos(23423) with a hint).<br>Limits: "satisfying insight" on about a quarter of prompts; attention-pattern formation is not explained; prompts up to about 100 tokens. | Shows parallel heuristic paths and mismatches between internals and the CoT. The model is closed, so it's not reusable directly. | **S**, **M** |
| Hanna & Ameisen (2026). *Latent Planning Emerges with Scale.* ICLR 2026 | https://arxiv.org/abs/2604.12493 | Across Qwen-3 0.6B–14B, latent planning grows with size. Features for a planned word (e.g., "accountant") cause "an" instead of "a". 4B–8B show nascent mechanisms. Rhymes are planned, but seldom far ahead. | Same model family and tools we would use. Shows capability scaling is measurable mechanistically, relevant to H3. | **S**, **M** |

### C. "Bag of heuristics" results and methods

| Citation | Link | Finding | Relevance | S/C/O |
|---|---|---|---|---|
| Nikankin, Reusch, Mueller, Belinkov (2025). *Arithmetic Without Algorithms: Language Models Solve Math With a Bag of Heuristics.* ICLR 2025 | https://arxiv.org/abs/2410.21272 ; project https://technion-cs-nlp.github.io/llm-arithmetic-heuristics | Models: Llama3-8B and 70B, Pythia-6.9B, GPT-J.<br>• Patching finds a circuit (faithfulness ≈ 0.96) of mostly late MLPs, with the answer probe-decodable from layer 16 of 32.<br>• About 200 neurons per layer suffice. Neurons are classified by activation pattern over operand pairs plus logit lens on their value vectors; ~91% of the 3,200 top neurons fall into types such as range, modulo, pattern and identical-operands.<br>• Ablating a heuristic type hurts its associated prompts more (average −29% from ~95%).<br>• Errors don't come from missing heuristics; incorrect prompts actually have *more* associated neurons. They come from weak total promotion of the correct logit.<br>• Heuristics emerge early in training (Pythia checkpoints). | The method for "many shallow heuristics vs one algorithm". **[interp]** Its error analysis is the mechanistic analogue of our error-composition idea, and it predicts that a model matching zoo heuristic *h* behaviourally may implement *h* as a union of pattern detectors, with no "h-state" variable to probe. | **S** (heuristics), **C** (for single-variable probes), **M** |
| Kantamneni & Tegmark (2025). *Language Models Use Trigonometry to Do Addition.* arXiv / ICLR 2025 listing | https://arxiv.org/abs/2502.00873 | Numbers form a helix. GPT-J, Pythia-6.9B and Llama3.1-8B build helix(a+b) by a "Clock" procedure, shown by patching plus helix fits. | **Same task, opposite verdict to Nikankin.** "Algorithm vs heuristics" depends on the level of analysis (representation geometry vs neuron level). **[interp]** We must pre-specify the level at which H5 is judged. | **C** (identifiability) |
| Sasaki, Kamoda, Takahashi, Sato, Inui, Sakaguchi, Heinzerling (2026). *Language Models Compare Quantities Using Number-specific and Unit-specific Heuristics.* arXiv | https://arxiv.org/abs/2606.03982 | Comparisons like "110 cm vs 1.2 m". Accuracy drops near the boundary. A linear surrogate on "numerical-difference" and "unit-scale-difference" cues predicts LM preferences, and interventions on subspaces aligned with those cues shift outputs. Conclusion: a collection of heuristics, not conversion to a common scale. | **The closest methodological overlap with O3 plus O5 combined** (behavioural surrogate → subspace interventions on heuristic variables), in a non-NP-hard domain. | **O**, **S** |
| jylin04 (2024). *OthelloGPT learned a bag of heuristics.* LessWrong / AF (MATS interim report) | https://www.lesswrong.com/posts/gcpNuEZnxAPayaKBY/othellogpt-learned-a-bag-of-heuristics-1 | Board state and legal moves are computed by many local, non-generalising neuron rules; a succinct algorithm can't be ruled out. | The same phenomenon in a world-model setting. Not peer-reviewed. | **S** |

### D. Tools and their critiques

| Citation | Link | Finding | Relevance | S/C/O |
|---|---|---|---|---|
| Ameisen et al. (2025). *Circuit Tracing: Revealing Computational Graphs in Language Models.* Transformer Circuits Thread | https://transformer-circuits.pub/2025/attribution-graphs/methods.html | The method paper: cross-layer transcoders (CLTs), a replacement model, attribution graphs with error nodes, pruning. The CLT matches model outputs in about 50% of cases. Attention patterns are frozen. | The correct citation for the method that DESIGN.md attributes to Lindsey et al. | **M** |
| circuit-tracer (Anthropic Fellows + Decode Research, 2025; library by M. Hanna & M. Piotrowski) | https://github.com/safety-research/circuit-tracer ; https://www.anthropic.com/research/open-source-circuit-tracing | Attribution graphs for open models. Transcoder sets (HF):<br>• Gemma-2-2B: PLT `mntss/gemma-scope-transcoders`, CLTs `mntss/clt-gemma-2-2b-426k` and `-2.5M`<br>• Llama-3.2-1B: PLT and CLT<br>• Qwen-3 0.6B / 1.7B / 4B / 8B / 14B: PLTs `mwhanna/qwen3-*-transcoders`<br>• Gemma-3 270M–27B, PT and IT: GemmaScope-2 PLTs, needs the nnsight backend<br>• Llama-3.1-8B-Instruct: TopK PLT `facebook/crv-8b-instruct-transcoders`<br>• GPT-OSS-20B: CLT<br>Interventions run in scripts; on Neuronpedia only for Gemma-2-2B. | The main resource for O5's "which components" row. | **M** |
| Dunefsky, Chlenski, Nanda (2024). *Transcoders Find Interpretable LLM Feature Circuits.* NeurIPS 2024 | https://arxiv.org/abs/2406.11944 | Transcoders as sparse MLP replacements match or beat SAEs; weights-based circuit analysis through MLPs. | Background for the transcoder choice. | **M** |
| Geiger, Lu, Icard, Potts (2021). *Causal Abstractions of Neural Networks.* NeurIPS 2021 | https://arxiv.org/abs/2106.02997 | Interchange interventions align network representations with variables of a causal model (MQNLI natural-logic task). | Cited in DESIGN.md; correct. | **M** |
| Geiger, Wu, Potts, Icard, Goodman (2023/24). *Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations.* arXiv | https://arxiv.org/abs/2303.02536 | Introduces **DAS** (learned rotations). | The paper to cite for "distributed alignment search". DESIGN.md currently implies it is Geiger 2021 or Wu 2023. | **M** |
| Wu, Geiger, Icard, Potts, Goodman (2023). *Interpretability at Scale: Identifying Causal Mechanisms in Alpaca.* NeurIPS 2023 | https://arxiv.org/abs/2305.08809 | **Boundless DAS** (learned subspace size). Alpaca-7B uses two boolean variables on a numerical task; tooling through pyvene. | Cited; correct. Closest precedent for "causal model with boolean intermediate variables in an LLM". | **M**, **S** |
| Geiger, Ibeling, Zur, … Potts, Icard (2025). *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability.* JMLR 26(83) | https://jmlr.org/papers/v26/23-0058.html | Unifies patching, causal scrubbing, SAEs, DAS and steering under causal abstraction. | Theory reference for O5. | **M** |
| Sutter, Minder, Hofmann, Pimentel (2025). *The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability?* NeurIPS 2025 (spotlight) | https://arxiv.org/abs/2507.08802 | Under mild assumptions, with unrestricted maps any network can be mapped to any algorithm. Random-init LMs reach 100% IIA on IOI. With non-linear maps there is no principled complexity/accuracy trade-off. | **The critique the task brief asked about.** H5's DAS test needs linear maps plus a random-init or untrained baseline. | **C** |
| Méloux, Maniu, Portet, Peyrard (2025). *Everything, Everywhere, All at Once: Is Mechanistic Interpretability Identifiable?* ICLR 2025 | https://arxiv.org/abs/2502.20914 | On small MLPs computing Boolean functions, where all explanations can be enumerated: many circuits fit, many interpretations per circuit, several algorithms align causally, and one algorithm aligns with several subspaces. | **Directly threatens H5's identification logic.** Two zoo heuristics could both "pass". We need comparative scoring, not pass/fail. | **C** |
| Makelov, Lange, Nanda (2024). *Is This the Subspace You Are Looking for? An Interpretability Illusion for Subspace Activation Patching.* ICLR 2024 | https://arxiv.org/abs/2311.17030 | Subspace patching can change behaviour through a dormant parallel pathway that is causally disconnected in normal operation. | Guard rail for DAS/patching claims. | **C** |
| Belrose, Ostrovsky, McKinney, Furman, Smith, Halawi, Biderman, Steinhardt (2023). *Eliciting Latent Predictions from Transformers with the Tuned Lens.* arXiv:2303.08112 (no venue listed) | https://arxiv.org/abs/2303.08112 | Per-layer affine translators. More reliable than the logit lens, which fails on some models (e.g., BLOOM, OPT-125M); validated with causal basis extraction. | Cited; preprint only. | **M** |
| Hewitt & Liang (2019). *Designing and Interpreting Probes with Control Tasks.* EMNLP-IJCNLP 2019 | https://arxiv.org/abs/1909.03368 | Selectivity = task accuracy − control-task accuracy. MLP probes have low selectivity; linear probes are more selective. | Required control for H5's probes. | **M** |
| Sahoo, Jain, Chadha, Chaudhary (2026). *Linear Probes Detect Task Format, Not Reasoning Mode in Language Model Hidden States.* ACL 2026 TrustNLP workshop | https://arxiv.org/abs/2606.02907 | On Qwen3-14B, 100% probe accuracy for reasoning type falls to chance after residualising source, option count and length. Steering vs random controls shows no effect. | Our heuristic-state probes must deconfound surface format (premise count, length, theme). | **C**, **M** |
| Mueller et al. (2025). *MIB: A Mechanistic Interpretability Benchmark.* ICML 2025 | https://arxiv.org/abs/2504.13151 | Two tracks. Circuit localisation: attribution and mask-optimisation methods are best. Causal-variable localisation: supervised DAS is best, and SAE features are no better than neurons. | Choose DAS over SAE features for H5's "variable" test. | **M** |
| Feng & Steinhardt (2024). *How do Language Models Bind Entities in Context?* ICLR 2024 | https://arxiv.org/abs/2310.17191 | Binding-ID vectors in a continuous subspace; causal interventions; IDs transfer across tasks. | **[interp]** A plausible substrate for representing ETR "alternatives" or mental-model possibilities (which atoms co-occur in which alternative). | **M** |

### E. Reasoning models and chain of thought

| Citation | Link | Finding | Relevance | S/C/O |
|---|---|---|---|---|
| Chen et al. (Anthropic Alignment Science) (2025). *Reasoning Models Don't Always Say What They Think.* arXiv | https://arxiv.org/abs/2505.05410 | Hint-verbalisation faithfulness: about 25% (Claude 3.7 Sonnet) and 39% (R1) on average. Outcome RL plateaus. | The trace isn't a reliable readout of the heuristic. Supports activation-level evidence. | **M** |
| Arcuschin et al. (2025). *Chain-of-Thought Reasoning In The Wild Is Not Always Faithful.* ICLR 2025 workshop | https://arxiv.org/abs/2503.08679 | Implicit post-hoc rationalisation (Yes to both "X > Y?" and "Y > X?"); illogical shortcuts on hard maths. v4 rates are much lower for thinking models. | Paired-item design similar to our manipulations. | **M** |
| Lanham et al. (2023). *Measuring Faithfulness in Chain-of-Thought Reasoning.* arXiv | https://arxiv.org/abs/2307.13702 | Early-answering, mistake-insertion, paraphrase and filler tests. Faithfulness varies by task. | Behavioural CoT-ablation protocol for the thinking-budget manipulation. | **M** |
| Bogdan, Macar, Nanda, Conmy (2025). *Thought Anchors: Which LLM Reasoning Steps Matter?* arXiv | https://arxiv.org/abs/2506.19143 | Sentence-level counterfactual resampling plus attention "broadcasting" analysis; anchors are mostly planning and backtracking sentences. Tool at thought-anchors.com. | A method to find *which trace step* commits to the heuristic's answer in thinking models. | **M** |
| Venhoff, Arcuschin, Torr, Conmy, Nanda (2025). *Understanding Reasoning in Thinking Language Models via Steering Vectors.* arXiv / ICLR 2025 workshop | https://arxiv.org/abs/2506.18167 | Uncertainty, backtracking and example-testing are linear directions in R1-distills; steering changes how often each happens. | Lets us manipulate "backtracking" causally. **[interp]** Prediction: suppressing backtracking should shift a thinking model's weight from search-like to greedy heuristics (H3). | **M** |
| Ward, Lin, Venhoff, Nanda (2025). *Reasoning-Finetuning Repurposes Latent Representations in Base Models.* arXiv | https://arxiv.org/abs/2507.12638 | A backtracking direction from base Llama-3.1-8B steers backtracking in R1-Distill-Llama-8B but not in the base model. | Reasoning-tuned models reuse base representations, so a base-model probe can transfer. | **M** |
| Galichin et al. (2025). *I Have Covered All the Bases Here: Interpreting Reasoning Features in Large Language Models via Sparse Autoencoders.* arXiv | https://arxiv.org/abs/2503.18878 | SAE "reasoning features" in R1-series models; steering them changes reasoning. | SAE route for thinking models. | **M** |
| Zhang et al. (2025). *Reasoning Models Know When They're Right: Probing Hidden States for Self-Verification.* arXiv | https://arxiv.org/abs/2504.05419 | Linear probes on hidden states predict whether intermediate answers are correct, before the answer is finished; probe-based early exit saves 24% of tokens. | Correctness is linearly decodable; a confound for heuristic-state probes, since "h is wrong here" correlates with "the model will be wrong". | **C**, **M** |
| Cox, Kianersi, Garriga-Alonso (2026). *Post-Hoc Reasoning in Chain of Thought: Decoding and Steering Pre-Committed Answers.* arXiv | https://arxiv.org/abs/2603.01437 | Pre-CoT residual probes predict the final answer (AUC > 0.9 on most tasks). Steering along the probe direction flips answers far more than norm-matched orthogonal baselines; steered CoTs confabulate or don't entail the answer. Search snippets say reasoning models were less steerable (not confirmed on the abstract page). | **Overlaps a natural O5 experiment** (is the heuristic answer committed before thinking?). Gives a baseline design: norm-matched orthogonal steering. | **O**, **S** |
| Mehrafarin, Parekh, Konstas (2026). *When Chain-of-Thought Fails, the Solution Hides in the Hidden States.* Findings of EMNLP 2026 | https://arxiv.org/abs/2604.23351 | Patching single CoT-token states into direct-answer runs on GSM8K beats both direct prompting and the original CoT; information is concentrated in mid-to-late layers. | Activations hold more than the trace. A patching design for thinking vs non-thinking modes. | **M** |
| Zhao, Koishekenov, Yang, Murray, Cancedda (2026). *Verifying Chain-of-Thought Reasoning via Its Computational Graph (CRV).* ICLR 2026 oral | https://arxiv.org/abs/2510.09312 | Structural features of per-step attribution graphs (transcoders) predict reasoning errors; signatures are domain-specific; targeted feature interventions fix errors. Released Llama-3.1-8B-Instruct transcoders. | **Overlaps "error composition from internals."** It classifies errors as correct or incorrect, not by which heuristic. | **O**, **M** |
| Pfau, Merrill, Bowman (2024). *Let's Think Dot by Dot: Hidden Computation in Transformer Language Models.* arXiv | https://arxiv.org/abs/2404.15758 | Filler tokens can stand in for CoT on 3SUM and 2SUM-Transform (100% and 94% accuracy) but need dense supervision; expressivity likely stays in TC⁰. | Control condition: does a heuristic's accuracy grow with filler tokens vs real thinking? | **M** |

### F. Ground-truth validation testbeds

| Citation | Link | Finding | Relevance | S/C/O |
|---|---|---|---|---|
| Lindner, Kramár, Farquhar, Rahtz, McGrath, Mikulik (2023). *Tracr: Compiled Transformers as a Laboratory for Interpretability.* NeurIPS 2023 (spotlight) | https://arxiv.org/abs/2301.05062 | RASP → transformer weights with known structure. | Cited; correct. | **M** |
| Gupta, Arcuschin, Kwa, Garriga-Alonso (2024). *InterpBench: Semi-Synthetic Transformers for Evaluating Mechanistic Interpretability Techniques.* NeurIPS 2024 Datasets & Benchmarks | https://arxiv.org/abs/2407.14494 | 86 models (85 Tracr circuits plus IOI), later extended by 69, trained with **Strict IIT**. Weights look realistic, unlike raw Tracr. Benchmarks ACDC, SP, EAP and EAP-IG. Code MIT, models CC-BY on HF. | A better positive control than raw Tracr. SIIT can plant *our* heuristics' RASP programs into realistic weights. | **M** |
| TracrBench (2024). *TracrBench: Generating Interpretability Testbeds with Large Language Models.* arXiv | https://arxiv.org/abs/2409.13714 | 121 RASP programs plus compiled TransformerLens models. | More ground-truth programs. | **M** |
| Shaw, Cohan, Eisenstein, Lee, Berant, Toutanova (2024/25). *ALTA: Compiler-Based Analysis of Transformers.* TMLR 2025 | https://arxiv.org/abs/2410.18077 | RASP-like language with **loops**, compiling to Universal Transformers. | **[interp]** The right compiler for iterative heuristics (`UP-k`, `WALK-k`, propagation loops), which Tracr can't express directly. | **M** |
| Palumbo, Mangal, Wang, Vijayakumar, Păsăreanu, Jha (2024/25). *Validating Mechanistic Interpretations: An Axiomatic Approach* (v1: "Mechanistically Interpreting a Transformer-based 2-SAT Solver") | https://arxiv.org/abs/2407.13594 | Axioms for a valid mechanistic interpretation (abstract-interpretation style). 2-SAT transformer: layer 1 parses clauses, layer 2 evaluates. | The only SAT-specific mechanistic interpretation found. A validation framework. | **O** (small), **M** |

---

## Novelty risks

1. **Entailment circuits in open LLMs are taken (high risk for a "we found the logic circuit" framing).** Hong et al. (NeurIPS 2025) already did causal mediation on propositional rule-plus-fact problems in Mistral-7B and Gemma-2-9B/27B, and Kim et al. (Findings ACL 2025) did syllogisms, including content (belief-bias) contamination. Our O5 on entailment must be framed as *adjudicating between competing heuristics* (ETR vs MM vs MATCH vs UP-k…) on discriminating items and errors. Neither paper does that; both study items models get right.
2. **Probing a heuristic's intermediate state has close precedents (medium-high risk).** Closest prior work:
   - Sudoku candidate sets: Shah et al., NeurIPS 2024.
   - Reachable sets: Saparov et al., ICLR 2025.
   - Future moves: Jenner et al., NeurIPS 2024.
   - Blocksworld future decisions: Men et al., EMNLP 2024.
   - Backward-chaining registers: Brinkmann et al. 2024.
   - Cue variables plus subspace interventions for a heuristic in a *pretrained* LM: Sasaki et al. 2026.

   The open piece I found no prior for is probing **pretrained LLMs on NP-hard instances** (SAT, coloring, knapsack, TSP) for state belonging to a *named competing heuristic*, and showing it on *errors*. Methodologically this is standard. Reviewers will credit the question and the item design, not the method.
3. **Ye et al. (arXiv 2510.19753, rev. Feb 2026) is a near-scoop of the thesis in miniature (high risk for O6/H2; flag to the RASP-L slice).** Their result: a transformer learns the exact algorithm when the data is within its depth capacity, and a degree heuristic beyond it, with proofs. Our "heuristic RASP-L" hypothesis must cite this paper and go beyond it: multiple competing heuristics, NP-hard tasks, pretrained LLMs.
4. **"Bag of heuristics" is an established framing (medium risk).** It appears in Nikankin et al. 2025, OthelloGPT, Sasaki et al. 2026, and the Lindsey et al. addition section. Our novelty must come from (a) NP-hard domains and (b) *competing explicit procedures with discriminating items*, not from the claim "LLMs use heuristics".
5. **Error signatures from internals are partly done (medium risk).** CRV (ICLR 2026 oral) predicts and fixes reasoning errors from attribution-graph structure. Nikankin analysed why arithmetic errors occur. We need to say that we classify errors *by procedure*, not as correct vs incorrect.
6. **Premise-order patching seems open (low prior-art risk, high scoop risk).** I found no mechanistic study of premise-order effects. Chen et al. 2024 explicitly leave the mechanism to future work. The experiment is cheap (clean = forward order, corrupt = reversed), so others may be running it. If it matters to the paper, do it early. The "first-premise recitation" stage in Kim et al. is related prior evidence.
7. **The pre-CoT commitment experiment for thinking models is done generically (medium risk).** Cox et al. 2026 decode answers before the CoT and steer them. Our version (is the *heuristic's* answer committed pre-CoT, and does thinking budget move it?) is a specialisation, not a new method.

---

## Methods and resources to reuse

**Models (recommended order for O5)**
1. **Qwen3-4B / 8B (thinking and non-thinking in one checkpoint).**
   - circuit-tracer PLTs: `mwhanna/qwen3-{0.6b,1.7b,4b,8b,14b}-transcoders*` (https://github.com/safety-research/circuit-tracer).
   - Qwen-Scope SAEs (official) for Qwen3-1.7B, 8B and 30B-A3B: https://arxiv.org/abs/2605.11887 (hook points and widths not verified).
   - BluelightAI CLTs for Qwen3-0.6B and 1.7B: https://www.bluelightai.com/blog/clts-for-qwen3/ (seen in a search result only).
   - Hanna & Ameisen (ICLR 2026) and Csordás et al. (NeurIPS 2025) already use this family, so the baselines are comparable.
2. **Gemma-3 (270M–27B, PT and IT).** Gemma Scope 2 (Dec 2025) has SAEs and transcoders on every layer of both PT and IT, CLTs on 270M and 1B, and 4-layer crosscoders (https://www.alignmentforum.org/posts/YQro5LyYjDzZrBCdb/announcing-gemma-scope-2). circuit-tracer supports it via the nnsight backend.
3. **Gemma-2-2B / 9B.** Gemma Scope (https://arxiv.org/abs/2408.05147) plus circuit-tracer PLTs and CLTs. Neuronpedia supports interventions for Gemma-2-2B. Hong et al. used Gemma-2-9B, which gives a direct comparison point.
4. **Llama-3.1-8B (base and Instruct).**
   - Llama Scope SAEs and transcoders (https://arxiv.org/abs/2410.20526, HF `fnlp/Llama-Scope`).
   - CRV TopK transcoders (`facebook/crv-8b-instruct-transcoders`).
   - Goodfire SAEs for Llama 3.1 8B and 3.3 70B (https://www.goodfire.ai/blog/sae-open-source-announcement).
   - Pair with DeepSeek-R1-Distill-Llama-8B to compare reasoning-tuned and base (Ward et al.).
5. **DeepSeek R1 (671B).** Goodfire SAEs (https://www.goodfire.ai/blog/under-the-hood-of-a-reasoning-model). Only if compute allows.
6. **OLMo 2.** I found no public SAEs or transcoders (not searched exhaustively). Keep it for contamination checks and behaviour, not as the main interp target.

**Libraries**
- `circuit-tracer` (attribution graphs; TransformerLens or nnsight backends).
- `pyvene` (DAS / Boundless DAS / interchange interventions; Wu et al. 2023 release).
- `nnsight` + NDIF (https://arxiv.org/abs/2407.14561), for remote access to large models.
- TransformerLens.
- `tuned-lens` (EleutherAI).
- Tracr (https://github.com/google-deepmind/tracr), ALTA, InterpBench (GitHub FlyingPumba/InterpBench; HF models), TracrBench.
- MIB (GitHub aaronmueller/MIB) for checking our DAS / patching pipeline on a public benchmark.
- Thought-anchors resampling code (thought-anchors.com).
- Code from relevant papers:
  - Nikankin: technion-cs-nlp.github.io/llm-arithmetic-heuristics
  - Kim et al.: github.com/neuro-symbolic-ai/Mechanistic-Interpretation-Syllogism
  - Palumbo: github.com/nilspalumbo/sat-mi
  - Biran: github.com/edenbiran/HoppingTooLate
  - Feng & Steinhardt: github.com/jiahai-feng/binding-iclr

**Method recipes to copy**
- **Heuristic-neuron classification (Nikankin).** For each zoo heuristic *h*, define the set of prompts where *h*'s rule fires. Assign a neuron or feature to *h* when its top-activating prompts overlap that set (they used a 0.6 threshold). Ablate by heuristic type and compare against random-neuron ablations matched in size.
- **Surrogate then subspace intervention (Sasaki 2026).** Fit a behavioural surrogate over heuristic cue variables, then run DAS on those variables. This is the cleanest bridge from O3's mixture model to O5.
- **Three converging lines (Jenner 2024):**
  1. patching that localises *h*'s state at predicted positions;
  2. attention that moves it as *h* predicts;
  3. a probe for it, with the claim scoped to items where *h* is unambiguous.
- **Back-patching (Biran 2024).** Tests whether errors come from running out of depth: patch later-layer states into earlier layers and see whether `UP-k` errors at large k disappear.
- **Guard rails, to adopt all together:**
  - control-task selectivity (Hewitt & Liang);
  - format deconfounding by residualising premise count, length and theme (Sahoo 2026);
  - **linear** alignment maps only, plus an untrained or random-init baseline that must fail (Sutter 2025);
  - score *all* competing heuristics' variables and report the comparison, not one pass/fail (Méloux 2025);
  - check for dormant-pathway illusions, e.g. that the subspace also matters in clean runs (Makelov 2024);
  - norm-matched orthogonal steering baselines (Cox 2026);
  - prefer supervised DAS over SAE features for variable localisation (MIB).
- **Thinking models:**
  - a pre-CoT probe for the heuristic's answer (Cox 2026);
  - thought-anchor resampling to find the committing sentence (Bogdan 2025);
  - a backtracking steering vector as a causal manipulation of "search effort" (Venhoff 2025);
  - token-state patching from CoT into a direct answer (Mehrafarin 2026).

---

## Suggested changes to DESIGN.md

1. **O5 "Target models".** Replace "Gemma 2 / 3, which have the Gemma Scope SAEs" with something precise. Gemma Scope covers *Gemma 2*; *Gemma 3* is covered by **Gemma Scope 2** (Dec 2025, SAEs plus transcoders plus CLTs). Add **Qwen3 0.6B–14B transcoders (circuit-tracer)** and **Llama-3.1-8B-Instruct transcoders (CRV)**. Make Qwen3-4B/8B the primary H5 model, because one checkpoint gives thinking vs non-thinking. Note that OLMo 2 has no known transcoders.
2. **O5 logit/tuned-lens row: replace the prediction.** "Shallow heuristics: early, and independent of instance size" won't discriminate. Csordás et al. 2025 and Hu et al. 2025 show LLMs generally don't adapt depth to difficulty, so an exact-but-failing procedure predicts the same thing. Better predictions:
   - (a) for `UP-k`, the layer at which the k-th derived literal becomes decodable grows with k, up to a ceiling set by depth (Brinkmann; Yao);
   - (b) on items where heuristics disagree, track **which candidate heuristic's answer** the tuned lens favours layer by layer.
3. **Rewrite H5 into testable parts with stricter falsifiers.**
   - H5a (decodable): a linear probe for *h*'s state has selectivity above a control task and survives format deconfounding.
   - H5b (used): linear interchange interventions on *h*'s variable move answers as *h* predicts, and do so **more than the same procedure applied to the best competing heuristic's variables**. The same alignment must fail on a random-init model.
   - H5c (errors): the effect holds on items where *h* is wrong.
   - Add the competing hypothesis **H5-alt (bag of heuristics)**: behaviour matching *h* is produced by many shallow input-pattern features with no *h*-state variable. Test it with Nikankin-style feature classification and ablation by type. If H5-alt wins, that is a reportable result, not a failure.
4. **Pre-specify the level of analysis.** Nikankin (neurons → bag of heuristics) and Kantamneni & Tegmark (representation geometry → helix algorithm) reach opposite verdicts on the *same task*. State in advance whether H5 is judged at variable or subspace level (DAS) or at feature or neuron level.
5. **Controls before LLMs: add three.**
   - (i) **InterpBench-style SIIT** models trained to implement our zoo heuristics' RASP programs, with realistic weights. Raw Tracr weights are unrealistic, as Gupta et al. note.
   - (ii) **ALTA** for iterative heuristics that need loops.
   - (iii) A **Ye et al.-style capacity toy**: train small transformers on graphs within or beyond their depth capacity, so the learned procedure (algorithm vs degree heuristic) is known and *switchable*. This is the cleanest positive-and-negative control for the whole O3 + O5 pipeline, and it ties to O6.

   Also run the pipeline on **MIB** to show our DAS/patching implementation reproduces published numbers.
6. **Attribution-graph scope.** CLT replacement models match outputs only about 50% of the time, ignore how attention patterns form, and have been used on prompts of about 100 tokens. They gave "satisfying insight" on about a quarter of prompts (Lindsey et al.). Restrict the "which components" row to short, no-CoT entailment items, and expect many failures.
7. **Thinking models (new O5 sub-question).** Is the heuristic's answer committed before thinking? Use a pre-CoT probe, steering against norm-matched baselines, and thought-anchor resampling. Does suppressing the backtracking direction shift the mixture weights toward greedy heuristics? This links O5 to H3.
8. **Premise-order patching.** Add it explicitly as an O5 experiment: patch forward-order and reversed runs on paired items, with `PRIMACY` / `FIRST` / `MATCH` predictions about *where* order sensitivity enters. Cite Chen et al. 2024 (behaviour, mechanism left open) and Kim et al. 2025 (first-premise stage).
9. **References.** Add Ameisen et al. 2025 (method), Geiger et al. 2023/24 (DAS), Geiger et al. 2025 JMLR, Sutter et al. 2025, Méloux et al. 2025, Makelov et al. 2024, Hewitt & Liang 2019, Gupta et al. 2024 (InterpBench), Hong et al. 2025, Ye et al. 2025, Saparov et al. 2025, Shah et al. 2024, Jenner et al. 2024, Csordás et al. 2025, Cox et al. 2026 and Zhao et al. 2026 (CRV).

---

## Citation corrections (DESIGN.md §10, this slice)

| Entry as written | Status | Correction |
|---|---|---|
| Nikankin et al. (2025). *Arithmetic Without Algorithms: Language Models Solve Math with a Bag of Heuristics.* ICLR. | **Correct.** | Authors: Nikankin, Reusch, Mueller, Belinkov. arXiv 2410.21272 (Oct 2024; v2 May 2025). The official title capitalises "With". |
| Lindsey et al. (2025). *On the Biology of a Large Language Model.* Transformer Circuits. | **Correct** (27 Mar 2025, Claude 3.5 Haiku). | DESIGN.md cites it for "attribution graphs with transcoders". The *method* paper is **Ameisen et al. (2025), "Circuit Tracing: Revealing Computational Graphs in Language Models"**, Transformer Circuits Thread. Cite both. For open models, cite the circuit-tracer library (2025). |
| Geiger et al. (2021). *Causal Abstractions of Neural Networks.* NeurIPS. | **Correct.** | Geiger, Lu, Icard, Potts; arXiv 2106.02997. **But** O5 attributes "distributed alignment search" to "Geiger et al.". DAS was introduced in **Geiger, Wu, Potts, Icard, Goodman, "Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations"** (arXiv 2303.02536; venue not verified this session). Add it, plus the theory paper Geiger et al. 2025, JMLR 26(83). |
| Wu et al. (2023). *Interpretability at Scale: Identifying Causal Mechanisms in Alpaca.* NeurIPS. | **Correct.** | Wu, Geiger, Icard, Potts, Goodman; arXiv 2305.08809. It introduces *Boundless* DAS, not DAS. |
| Belrose et al. (2023). *Eliciting Latent Predictions from Transformers with the Tuned Lens.* | **Correct** as an arXiv preprint. | arXiv 2303.08112; no venue on the arXiv page (latest revision v6, Nov 2025). Don't add a conference. |
| Lieberum et al. (2024). *Gemma Scope.* | **Incomplete title.** | Full title: *Gemma Scope: Open Sparse Autoencoders Everywhere All At Once on Gemma 2*. arXiv 2408.05147. A search snippet from an ACL Anthology author page lists it in BlackboxNLP 2024, but the arXiv page shows no venue, so this is moderately verified. It covers **Gemma 2 only**. For Gemma 3, cite Gemma Scope 2 (Google DeepMind, Dec 2025). |
| Lindner et al. (2023). *Tracr: Compiled Transformers as a Laboratory for Interpretability.* NeurIPS. | **Correct.** | Lindner, Kramár, Farquhar, Rahtz, McGrath, Mikulik; arXiv 2301.05062; NeurIPS 2023 spotlight. |
| Dziri et al. (2023). *Faith and Fate: Limits of Transformers on Compositionality.* NeurIPS. | **Correct.** | arXiv 2305.18654; NeurIPS 2023. |

No entry in this slice is fabricated or has the wrong year. The real fixes are: add Ameisen et al. for the method, add the DAS paper, and expand the Gemma Scope title and scope.

---

## Unverified / leads

**Venues not confirmed this session** (the search budget ran out):
- DAS paper (arXiv 2303.02536): I believe CLeaR 2024, but the arXiv page lists none.
- Wang et al., *Grokked Transformers are Implicit Reasoners* (https://arxiv.org/abs/2405.15071): probably NeurIPS 2024. Content confirmed: composition fails OOD, comparison succeeds, grokking is required.
- pyvene: NAACL 2024 demo?
- NNsight/NDIF: ICLR 2025, per a third-party listing only.
- Cruz 2025: TMLR, per MLAnthology only.
- Zhang et al. 2025 (probing correctness).
- TracrBench authors.

**Resources seen only in search snippets:**
- Qwen-Scope hook points, widths and licence.
- BluelightAI Qwen3 CLTs.
- ByteDance-Seed Qwen3-30B-A3B MoE SAEs.
- Goodfire R1 SAE hosting and licence.
- The 2026 Qwen3-Instruct SAE suite (https://arxiv.org/abs/2606.26620), whose weights may not be released yet.

**Leads worth a follow-up read:**
- **Da Ros, Di Gaspero, Roitero (2025/26).** *Behavior and Representation in Open-Weight LLMs for Combinatorial Optimization.* Computers & Operations Research (https://arxiv.org/abs/2512.13374). Probes hidden states of 3B–120B open models for combinatorial-optimisation instance features and per-instance algorithm selection. Finds a consistent gap between implicit encoding and explicit retrieval. **Possible overlap with probing on NP-hard instances.** It probes instance features, not heuristic state, but it should be read.
- "Mechanistic Interpretability for Neural TSP Solvers" (https://arxiv.org/abs/2510.21693): SAEs on a dedicated TSP transformer, not an LLM.
- GraphGhost (https://arxiv.org/abs/2510.08613): circuit tracing on path reasoning, with a Qwen3-0.6B case study.
- "Knowing Before Saying" (https://arxiv.org/abs/2505.24362): CoT success is predictable before generation.
- "Mechanistic Evidence for Faithfulness Decay in CoT" (https://arxiv.org/abs/2602.11201).
- "Dissecting Logical Reasoning in LLMs" (https://arxiv.org/abs/2506.04810).
- Sequential activation patching of CoT (Dura et al. 2026, https://arxiv.org/abs/2608.22332).
- "Are Arithmetic Heuristic Neurons Form-Invariant?" (https://arxiv.org/abs/2607.16693).
- Du et al., "Fine-Grained Manipulation of Arithmetic Neurons" (BlackboxNLP 2025): steers via heuristic neurons.
- Sanford, Hsu, Telgarsky, log-depth k-hop constructions: theory for per-pass step limits.
- Ivanitskiy et al. 2023, maze transformers (https://arxiv.org/abs/2312.02566).

**Recalled but not searched this session** (do not cite until checked):
- Patchscopes (Ghandeharioun et al. 2024).
- Marks et al., *Sparse Feature Circuits* (2024).
- Prakash et al. on "lookback" belief tracking (2025).
- Nanda et al. 2023 (modular addition Clock), cited only through Kantamneni & Tegmark.
- Zhong et al. 2023 ("Pizza"), cited only through Kantamneni & Tegmark.
- Conmy et al. 2023 (ACDC), cited only through InterpBench.
- Chen et al. 2024, *Premise Order Matters*: confirmed via its arXiv PDF in a search result (https://arxiv.org/abs/2402.08939). It belongs to another slice.
