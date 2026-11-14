> Research-agent report written 2026-11-13 for the literature review in [../LITERATURE.md](../LITERATURE.md). Every paper was found by web search or fetch during the review; the most decision-relevant claims were then spot-checked against the source (see LITERATURE.md, "How this review was done"). Treat other details as leads to confirm before citing.

# Lit review slice A: hardness and compute (O1, O2, H3)

*Heuristics Under Hardness, DESIGN.md v0.1. Compiled 2026-11-13.*

Scope: typical-case hardness; theoretical limits of transformers with and without CoT; empirical scaling of reasoning models with size and hardness; LLM benchmarks on NP-hard problems.

How this was done: ~70 web searches and ~45 page fetches. Close reads were of Hazra et al. 2025, Shojaee et al. 2025, Zhang et al. 2026 (FSE), Verma 2026, Pan et al. 2025 (theorem checked in the PDF), Heyman & Zylberberg 2025a, GraphArena, AlgoTrace, NPPC and Valmeekam et al. 2024. The session's shared web-search budget ran out near the end, so a few leads stay unverified (last section).

Convention: **Claim** = what the paper says. **Interp.** = my reading of what it means for us.

---

## Summary

- **O2's theory is settled, and two citations carry it.**
  - Merrill & Sabharwal (TACL 2023): a log-precision transformer is in *log-space-uniform* TC⁰.
  - Merrill & Sabharwal (ICLR 2024): polynomially many CoT steps, with "generalized pre-norm", give exactly P.
  - Feng et al. 2023 is cited for the wrong step. It proves that models can't answer *without* CoT; it doesn't put CoT inside P.
  - Newer results sharpen the argument: linear CoT lower bounds (Amiri et al., ICML 2025), padding = TC⁰ and looping = TCᵈ (Merrill & Sabharwal, NeurIPS 2025).
- **The converse matters as much and is missing from the design.** Pan et al. (ICML 2025) build a fixed transformer that decides 3-SAT with ≤ p·2^(p+1) CoT steps by running DPLL with unit propagation. Exact search is therefore *expressible*. The real dividing line is the token budget against roughly 2^Θ(n), so "LLMs must use heuristics" holds only above that line.
- **O2(a) and O2(b) are already well documented and won't count as contributions.** Accuracy collapses past a size threshold, and thinking tokens rise and then *fall* before the budget runs out. Papers showing this: Shojaee et al. (NeurIPS 2025), Estermann & Wattenhofer 2025, NPPC 2025, Hazra et al. 2025, Rameshkumar et al. 2025, NLCO 2026, Utsho et al. 2026. Token growth is roughly linear or polynomial in size, never exponential. That supports O2(b), but much of the evidence comes from puzzles in P (Tents, Hanoi).
- **3-SAT near α≈4.26 has already been used on LLMs, including R1.**
  - Hazra et al. 2025 report an easy-hard-easy accuracy curve. R1's traces show DPLL, unit propagation and backtracking. GPT-4o searches greedily without backtracking. Models give "lazy" answers of the form "UNSAT because complex".
  - Zhang et al. (FSE 2026) show most models are biased toward SAT and don't reproduce the transition. Their matched SAT/UNSAT pairs separate "heuristic" from "reasoning-oriented" models.
- **Solver hardness ≠ model hardness (Verma 2026).** At matched clause density, proof-hard and proof-easy UNSAT families gave no pooled accuracy gap. Token spend didn't track solver hardness once formula length was controlled. *Interp.:* O1's plan to make hardness "a measured property" with solver nodes and backbones is necessary but not enough. Hardness should also be measured *relative to the heuristics in the zoo*, which ties O1 to O3.
- **The errors are structured.** That supports O2(c):
  - a bias toward answering SAT (SATBench; Zhang et al. 2026);
  - hallucinated graph edges as the main cause of coloring errors (Heyman & Zylberberg 2025b);
  - GraphArena's "default to greedy", with hallucination (infeasible answers) rising from about 20% to 44% as graphs grow;
  - ~~reasoning models' coloring errors spiking when a randomized greedy colorer rarely succeeds (Heyman & Zylberberg 2025a)~~ — **withdrawn by its authors**: 2505.12151 v3 (§1, App. A.1) reports the correlation is "not causally significant"; it tracked edge count. Don't cite 2025a as evidence of greedy behaviour (see [theory/T3](../theory/T3_llm_precedent.md) §5);
  - o1 producing plans for unsolvable instances.
- **H3 has partial qualitative support, plus two real threats.**
  - Support: R1 uses unit propagation and DPLL where GPT-4o uses greedy search (Hazra). Phi-4-Reasoning opens TSP with nearest neighbour where Phi-4 brute-forces or guesses (AlgoTrace).
  - Threat 1: at small n, reasoning models *do* run exact search (Hazra, n ≤ 10). Frontier LLMs now match classical planners on fresh IPC tasks (Corrêa et al. 2025/26).
  - Threat 2: more thinking can *lower* accuracy (Gema et al., TMLR 2025; Ghosal et al., NeurIPS 2025). Budget effects need not be monotone.
- **Typical-case caveat for O1.**
  - Rameshkumar et al. 2025: most *real-world* graph and proof instances fall inside reasoning models' success range, with a long tail outside it.
  - Cognitive science has argued for years that appealing to "heuristics" doesn't escape intractability (van Rooij, Wright & Wareham, Synthese 2012). O1/O2 should engage with that argument rather than be ambushed by it.

---

## Key papers

S = supports, C = contradicts or complicates, O = overlaps with our plan (novelty risk).

| # | Citation | Link | Finding (claim) | Relevance | S / C / O |
|---|----------|------|-----------------|-----------|-----------|
| 1 | Merrill & Sabharwal (2023). *The Parallelism Tradeoff: Limitations of Log-Precision Transformers.* TACL 11:531–545 | https://arxiv.org/abs/2207.00729 | Log-precision transformers can be simulated by constant-depth **logspace-uniform** threshold circuits | O2 step 1 | S |
| 2 | Merrill & Sabharwal (2024). *The Expressive Power of Transformers with Chain of Thought.* ICLR 2024 | https://arxiv.org/abs/2310.07923 | Log steps add little. Linear steps (projected pre-norm) give all regular languages and stay within context-sensitive. Poly steps with generalized pre-norm give **exactly P** | O2 steps 1–2 | S |
| 3 | Feng, Zhang, Gu, Ye, He & Wang (2023). *Towards Revealing the Mystery behind Chain of Thought: A Theoretical Perspective.* NeurIPS 2023 (oral) | https://arxiv.org/abs/2305.15408 | Bounded-depth transformers can't directly output answers to arithmetic or linear equations unless size grows super-polynomially. Constant-size models with CoT can, and can do a class of DP problems | O2 direct-answer bullet (not the P upper bound) | S |
| 4 | Li, Liu, Zhou & Ma (2024). *Chain of Thought Empowers Transformers to Solve Inherently Serial Problems.* ICLR 2024 | https://arxiv.org/abs/2402.12875 | Without CoT, constant-precision constant-depth transformers are in AC⁰. T CoT steps simulate size-T circuits | O2. Stronger no-CoT bound under constant precision | S |
| 5 | Amiri (Bavandpour), Huang, Rofin & Hahn (2025). *Lower Bounds for Chain-of-Thought Reasoning in Hard-Attention Transformers.* ICML 2025 | https://arxiv.org/abs/2502.02393 | Parity, multiplication, median and reachability need CoT length at least linear in input size, tight up to log factors. Pause or "dot" tokens can't do parity at polynomial length | O2: a bounded-token model *must* fail, even on problems in P | S |
| 6 | Merrill & Sabharwal (2025). *Exact Expressive Power of Transformers with Padding.* NeurIPS 2025 | https://arxiv.org/abs/2505.18948 | Polynomial padding gives exactly TC⁰. Padding plus O(logᵈ n) looping gives TCᵈ. Polylog looping gives NC | O2: "filler" thinking buys no serial power. O6: looped models | S |
| 7 | Saunshi, Dikkala, Li, Kumar & Reddi (2025). *Reasoning with Latent Thoughts: On the Power of Looped Transformers.* ICLR 2025 | https://arxiv.org/abs/2502.17416 | A k-layer model looped L times nearly matches a kL-layer model. T loops can simulate T CoT steps | O2/O6: latent compute counts as "tokens" | S |
| 8 | Pan, Ganesh, Abernethy, Esposo & Lee (2025). *Can Transformers Reason Logically? A Study in SAT Solving.* ICML 2025 | https://arxiv.org/abs/2410.07432 | Thm 4.5 (read in PDF): a 7-layer, 5-head transformer with O(p²) params decides 3-SAT with ≤ p vars in ≤ p·2^(p+1) CoT steps. It is trace-equivalent to DPLL with unit propagation. The construction is non-uniform. "Exponentially many CoT steps in the worst case"; far fewer on typical formulas. PARAT compiles NumPy-style specs to weights. Trained models generalise within sizes seen, but not to larger sizes | O2's converse. O5/O6 tooling | C (to "must use heuristics" at small n); resource |
| 9 | Yang, Srebro, McAllester & Li (2025). *PENCIL: Long Thoughts with Short Memory.* ICML 2025 | https://arxiv.org/abs/2503.14337 | Generate-then-erase CoT simulates Turing machines with optimal time and space. A 25M model solves Einstein's puzzle | O2: exponential-time search fits in poly context. O6 prediction 3 | C / resource |
| 10 | Shojaee, Mirzadeh, Alizadeh, Horton, Bengio & Farajtabar (2025). *The Illusion of Thinking: …via the Lens of Problem Complexity.* NeurIPS 2025 | https://arxiv.org/abs/2506.06941 | Puzzles: Hanoi, Checker Jumping, River Crossing, Blocks World. Three regimes. Thinking tokens rise, then fall near collapse though the budget isn't used up. Supplying the algorithm doesn't help. "Overthinking" on easy items. The v3 appendix answers critics: first failures come well before context limits; River Crossing limited to N<6 | O2(a)(b) | O / S |
| 11 | Lawsen (2025). *Comment on The Illusion of Thinking…* (PDF title "The Illusion of the Illusion of Thinking"). arXiv | https://arxiv.org/abs/2506.09250 | The collapse is partly an artefact: outputs hit token limits, the grader can't tell truncation from error, and River Crossing N≥6 is unsolvable. Hanoi's per-move decision is O(1), so move count isn't reasoning complexity. Asking for a generating function restores accuracy (preliminary) | O2 rules | C (to Shojaee); methodology |
| 12 | Dellibarda Varela, Romero-Sorozabal, Rocon & Cebrian (2025). *Rethinking the Illusion of Thinking.* arXiv | https://arxiv.org/abs/2507.01231 | Replication. River Crossing failures come from unsolvable configurations. Hanoi still degrades at about 8 disks, even with stepwise prompting | O2 | Mixed |
| 13 | Khan, Madhavan & Natarajan (2025). *A Comment On "The Illusion of Thinking": Reframing the Reasoning Cliff as an Agentic Gap.* arXiv | https://arxiv.org/abs/2506.18957 | With tools, models solve variants well past the cliff | O2's "disable tools" rule is right; scope the claim | C (scope) |
| 14 | Estermann & Wattenhofer (2025). *Reasoning Effort and Problem Complexity: A Scaling Analysis in LLMs.* ICLR 2025 Workshop on Reasoning and Planning for LLMs | https://arxiv.org/abs/2503.15113 | Tents puzzle (linear-time solvable). Token count grows roughly linearly with size for R1 and o3-mini. o3-mini's effort peaks near size 100 and then falls. Higher effort settings solve larger puzzles but spend more tokens on small ones | O2(b) | S / O |
| 15 | Yang, Wang, Wang et al. (2025). *Nondeterministic Polynomial-time Problem Challenge (NPPC): An Ever-Scaling Reasoning Benchmark for LLMs.* arXiv | https://arxiv.org/abs/2504.11239 | npgym has 25 NP-complete generators, 10 levels each, with verifiers. Accuracy can be pushed below 10%. Tokens for Claude 3.7 and R1 rise, then fall. Wrong answers use more tokens. Failures include R1 guessing on unjustified assumptions and looping, Claude claiming checks it didn't do, and JSON breaking at truncation | O2(a)(b), resources | O / S |
| 16 | Hazra, Venturato, Zuidberg Dos Martires & De Raedt (2025). *Have Large Language Models Learned to Reason? A Characterization via 3-SAT Phase Transition.* arXiv (updates arXiv 2408.07215) | https://arxiv.org/abs/2504.03930 | Random 3-SAT, n = 3–10, α ≈ 1–11, CNF and NL "Menu" framings. LLM accuracy on search drops to about 10% near α_c. R1 is far better; its tokens grow polynomially and stay high on over-constrained items. R1's traces show DPLL, unit propagation, pure-literal elimination, MOMS and backjumping. It fails by incompleteness (stopping early) and unsoundness (missed clauses). GPT-4o does "greedy search without backtracking". Others give lazy answers ("UNSAT because complex") | O1, O2, H3, zoo | **O (high)**; S (H3 partly); C (exact search at small n) |
| 17 | Zhang, Chen & Chen (2026). *Satisfiability Solving with LLMs: A Matched-Pair Evaluation of Reasoning Capability.* FSE 2026 | https://arxiv.org/abs/2605.28602 | Accuracy and F1 mislead because models over-predict SAT. Most models show no easy-hard-easy pattern; GPT-5 partly does. Minimal SAT/UNSAT pairs and ADR (both members right) separate "heuristic" from "reasoning-oriented" models (GPT-5, o1, o3-mini, deepseek-reasoner). ADR decays with N; most models sit near chance by N ≥ 25. Predictions agree across reductions to Vertex Cover and 3D packing on about 75–80% of instances | O2(c), H3, **H4** | **O (high)**; S |
| 18 | Verma (2026). *Solver-Hard Is Not Model-Hard: A Hardness-Controlled Diagnostic for LLM Constraint Reasoning.* arXiv | https://arxiv.org/abs/2607.17047 | At matched density, expander-Tseitin (proof-hard) and ladder-Tseitin (proof-easy) gave a pooled accuracy gap of +1.7 pts (p = .74), with r(correct, conflicts) = +0.15. Reasoning-model tokens didn't track hardness once length was controlled. Random-UNSAT, the *solver-easiest* family, capped the 16k budget. Proof-preserving relabeling changed verdicts for some models. The paper recommends treating capped runs as censored | **O1 item 2**, O2(b), H3 | C (to "solver hardness ⇒ model error") |
| 19 | Wei, Wu, Wan, Suresh, Tan, Zhou, Koyejo, Wang & Aiken (2025). *SATBench: Benchmarking LLMs' Logical Reasoning via Automated Puzzle Generation from SAT Formulas.* NeurIPS 2025 (per NeurIPS listing) | https://arxiv.org/abs/2505.14615 | 2,100 NL puzzles generated from SAT formulas, with difficulty set by clause count. o4-mini gets 65% on hard UNSAT, against a 50% baseline. Error types: satisfiability bias, context inconsistency, condition omission | O2(c), zoo (`SAT-BIAS`) | S / O |
| 20 | Heyman & Zylberberg (2025a). *Evaluating the Systematic Reasoning Abilities of Large Language Models through Graph Coloring.* arXiv | https://arxiv.org/abs/2502.07087 | Sizes 4v2c to 8v4c. Difficulty is a **greedy score** (randomized greedy success over 10k trials). Errors of o1-mini and R1 spike at greedy score < 0.5. Framings: Math vs Friends. Errors split into invalid coloring vs falsely claiming "uncolorable" | O1 (heuristic-relative hardness), O2(c), coloring zoo | S / resource |
| 21 | Heyman & Zylberberg (2025b). *Reasoning Large Language Model Errors Arise from Hallucinating Critical Problem Features.* arXiv | https://arxiv.org/abs/2505.12151 | Six reasoning models (o1-mini, o3-mini, R1, Claude 3.7, Gemini 2.5 Pro, Grok 3 mini) on coloring. Hallucinated edges explain a large share of errors, nearly all for some models, at every complexity and framing | O2(c); a confound for heuristic identification | S (structured errors) / C (not a *procedure*) |
| 22 | Tang, Zhang, Li, Chen & Li (2025). *GraphArena: Evaluating and Exploring Large Language Models on Graph Computation.* ICLR 2025 | https://arxiv.org/abs/2407.00379 | Four P tasks and six NP-complete tasks. Outputs are classed correct / suboptimal / hallucinatory / missing. On NP-complete tasks GPT-4o goes from small to large graphs as accuracy 47→6%, hallucination 20→44%. "Models typically default to greedy algorithms." On large TSP, GPT-4o loses to greedy 77% of the time. Scaling test-time compute (GPT-4o-mini) cuts hallucination but barely helps on hard tasks | O2(c), H3, TSP zoo | S / O |
| 23 | Lippl, McGee, Lopez, Pan, Zhang, Ziadi, Eberle & Momennejad (2025, v3 2026). *AlgoTrace: Algorithmic Primitives and Compositional Geometry of Reasoning in Language Models.* arXiv | https://arxiv.org/abs/2510.15987 | Activations are clustered and labelled by trace tokens on TSP, 3SAT, AIME and graph navigation. Primitives found include nearest_neighbor, compare_verify and if_clause_true. Phi-4-Reasoning starts with NN far more than Phi-4, which brute-forces or guesses. Injecting a primitive vector elicits the operation | **H3, O3, O5** | **O (high, for O5)** / S (H3) |
| 24 | Duchnowski, Pavlick & Koller (2025). *A Knapsack by Any Other Name: Presentation impacts LLM performance on NP-hard problems.* EMNLP 2025 (Findings) | https://arxiv.org/abs/2502.13776 | The EHOP dataset has textbook, real-life and inverted-rule framings of NP-hard problems. Textbook framings score best. Reasoning models are better but vary across framings. Greedy baselines are competitive (per search snippet; not confirmed on the abstract page) | O4 framings (content effects) | O |
| 25 | Rameshkumar, Huang, Sun, Xia & Saparov (2025). *Reasoning Models Reason Well, Until They Don't.* arXiv | https://arxiv.org/abs/2510.22371 | DeepRD controls lookahead and branching. R1 and o3-mini collapse abruptly, and not because of token limits. Most real-world graph and proof instances fall inside the success range; the long tail doesn't | **O1 typical-case claim**, O2(a) | C (O1's strong form) / S (weak form) |
| 26 | Valmeekam, Stechly & Kambhampati (2024). *LLMs Still Can't Plan; Can LRMs? A Preliminary Evaluation of OpenAI's o1 on PlanBench.* arXiv | https://arxiv.org/abs/2409.13373 | o1-preview scores 97.8% on Blocksworld, 52.8% on Mystery and 37.3% on Randomized Mystery. On 6–20 blocks it scores 23.6% and degrades quickly with length. It flags only 27% of unsolvable goals and calls 11.5% of solvable ones unsolvable. Reasoning tokens didn't track difficulty | O2, planning domain | S |
| 27 | Corrêa, Pereira & Seipp (2025, v2 2026). *Frontier Large Language Models Rival State-of-the-Art Planners* (v1 title: "The 2025 Planning Performance of Frontier Large Language Models"). arXiv | https://arxiv.org/abs/2511.09378 | 360 freshly generated IPC tasks. Gemini 3.1 Pro solves 245 against the best planner's 234; GPT-5 is comparable. Obfuscation hurts but Gemini stays competitive | Planning domain, H3 | C (to "LLMs can't plan"; supports near-exact search at these sizes) |
| 28 | Gema, Hägele, Chen, Arditi, … Perez (2025). *Inverse Scaling in Test-Time Compute.* TMLR 12/2025 | https://arxiv.org/abs/2507.14417 | Longer reasoning lowers accuracy on several task families, including "deduction with constraint tracking". Five failure modes: distraction, framing overfit, spurious correlations, loss of focus on deduction, amplified concerning behaviours | **H3 budget arm** | C (to a monotone budget effect) |
| 29 | Ghosal et al. (2025). *Does Thinking More always Help? Mirage of Test-Time Scaling in Reasoning Models* (earlier title: "…Understanding Test-Time Scaling…"). NeurIPS 2025 | https://arxiv.org/abs/2506.04210 | Forcing more thinking ("Wait") helps at first, then hurts. Parallel sampling beats sequential extension at a matched budget | H3 | C |
| 30 | Sinha, Arun, Goel, Staab & Geiping (2025). *The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs.* ICLR 2026 | https://arxiv.org/abs/2509.09677 | Even with the plan supplied, long tasks fail through execution errors that compound. "Self-conditioning": past errors in context cause more. Thinking reduces this | H3 / O3 confound: decay with size can be noisy *exact* execution | C (alternative explanation) |
| 31 | Jiang et al. (2026). *Reasoning in a Combinatorial and Constrained World: Benchmarking LLMs on Natural-Language Combinatorial Optimization (NLCO).* arXiv | https://arxiv.org/abs/2602.02188 | 43 problems. Performance falls with instance size even when more reasoning tokens are used. Graph problems and bottleneck objectives are hardest | O2(a)(b) | S / O |
| 32 | Utsho, Ameen, Islam, Rashed & Das (2026). *Empirical Evidence of Complexity-Induced Limits in LLMs on Finite Discrete State-Space Problems with Explicit Validity Constraints.* arXiv | https://arxiv.org/abs/2604.13371 | Nine puzzles with strict validators. "Reasoning collapse" past task-specific thresholds: constraint violations, lost state tracking, confident wrong answers. Longer reasoning doesn't reliably help | O2 | O |
| 33 | Fan, Hua, Li, Ling & Zhang (2024). *NPHardEval: Dynamic Benchmark on Reasoning Ability of LLMs via Complexity Classes.* ACL 2024, pp. 4092–4114 | https://arxiv.org/abs/2312.14890 | 900 questions in 9 tasks across P, NP-complete and NP-hard, 10 levels each, refreshed monthly. Accuracy falls with complexity, sharply at NP-hard. No reasoning-model follow-up found | Precedent | O (low) |
| 34 | Valmeekam, Marquez, Olmo, Sreedharan & Kambhampati (2023). *PlanBench: An Extensible Benchmark for Evaluating LLMs on Planning and Reasoning about Change.* NeurIPS 2023 D&B | https://arxiv.org/abs/2206.10498 | IPC-style domains: plan generation, cost-optimal planning, verification. Mystery obfuscation | Planning domain | Resource |
| 35 | Stojanovski et al. (2025). *Reasoning Gym: Reasoning Environments for RL with Verifiable Rewards.* NeurIPS 2025 D&B (spotlight) | https://arxiv.org/abs/2505.24760 | 100+ generators and verifiers with difficulty knobs. Sharp drops from easy to hard, especially on graph and algorithmic tasks | Resource; contamination risk for future models | Resource |
| 36 | Mitchell, Selman & Levesque (1992). *Hard and Easy Distributions of SAT Problems.* AAAI-92, pp. 459–465 | https://mlanthology.org/aaai/1992/mitchell1992aaai-hard | Hard random SAT distributions exist at the right parameters | O1, 3-SAT dial | S |
| 37 | Cheeseman, Kanefsky & Taylor (1991). *Where the Really Hard Problems Are.* IJCAI-91 | https://ijcai.org/proceedings/1991/50 | NP-complete problems have an order parameter, and hard instances sit at its critical value (k-colorability by connectivity) | O1, coloring dial | S |
| 38 | Williams, Gomes & Selman (2003). *Backdoors To Typical Case Complexity.* IJCAI-03 | https://ijcai.org/proceedings/2003/167 | Small backdoor sets explain why solvers scale on real-world instances | O1 caveat | S (caveat) |
| 39 | Monasson, Zecchina, Kirkpatrick, Selman & Troyansky (1999). *Determining computational complexity from characteristic 'phase transitions'.* Nature 400:133–137 | https://arxiv.org/abs/cond-mat/9910080 | Exponential vs polynomial cost matches a discontinuous vs continuous transition (2+p-SAT). Backbones are in the companion RSA paper | O1 hardness measures (backbone) | S |
| 40 | Pisinger (2005). *Where are the hard knapsack problems?* Computers & OR 32(9):2271–2284 | https://www.dcs.gla.ac.uk/~pat/cpM/jchoco/knapsack/papers/hardInstances.pdf | Instance classes hard for DP and for branch-and-bound | Knapsack generator | Resource |
| 41 | van Rooij, Wright & Wareham (2012). *Intractability and the use of heuristics in psychological explanations.* Synthese 187(2):471–487 | https://link.springer.com/article/10.1007/s11229-010-9847-7 | Explaining an intractable computational-level theory by "the mind uses heuristics" doesn't work. The fix is to revise the computational-level theory | **O2 framing**: a direct conceptual challenge | C (to naive framing) |
| 42 | van Rooij, Guest, Adolfi, de Haan, Kolokolova & Rich (2024). *Reclaiming AI as a Theoretical Tool for Cognitive Science.* Computational Brain & Behavior 7:616–636 | https://research-information.bris.ac.uk/en/publications/reclaiming-ai-as-a-theoretical-tool-for-cognitive-science/ | Learning human-like cognition from data is intractable (they reduce it to an NP-hard problem) | O1 context | Context |
| 43 | Fan, Cheng, Li, Liang, Zhou & Feizi (2026). *Thinking Hard, Not Smart: Reasoning Models Fail to Ration Test-Time Compute Across Questions.* arXiv | https://arxiv.org/abs/2608.07968 | Given a shared budget, models allocate compute greedily by presentation order and ignore value | `PRIMACY`/greedy at the meta level; H4 | S (H4-ish) |

---

## Novelty risks

Ranked by how much each threatens the paper's claims.

1. **3-SAT phase-transition evaluation of LLMs is taken (high).**
   - Hazra et al. 2024/2025 did it, with R1 trace analysis that names our zoo entries: unit propagation, DPLL, and greedy without backtracking for GPT-4o.
   - Zhang et al. (FSE 2026) add matched pairs, a SAT-bias diagnosis, and a "heuristic vs reasoning-oriented" split.
   - Verma 2026 shows the α-dial is confounded with length and doesn't transfer to model hardness.
   - "LLMs on random 3-SAT near 4.26" can't be pitched as new. *Our only defensible novelty in that domain is formal heuristic identification:* discriminating items, lift over a permutation baseline, a mixture model, and manipulation signatures. None of these papers does that.
2. **O2(a)/(b) measurements are already published many times (high, but O2 is only framing).**
   - Accuracy versus size, and thinking tokens rising then falling: Shojaee, Estermann & Wattenhofer, NPPC, NLCO, DeepRD, Utsho, Reasoning Gym.
   - Treat O2 as replication on our own domains. Don't claim it as a finding.
3. **"LLMs default to greedy heuristics on NP-hard problems" has been asserted, qualitatively (medium-high).**
   - GraphArena says it in its intro. Hazra says it of GPT-4o. AlgoTrace shows nearest neighbour on TSP, with *latent primitive vectors*, which also overlaps O5.
   - Reviewers will say "known". The answer is that it was asserted from traces or tour lengths, never identified against competing heuristics with a chance baseline. That point has to be made explicitly, with these papers cited.
4. **AlgoTrace overlaps O5 directly (medium-high).**
   - It finds algorithmic primitives (NN, verify, clause-check) in activations on TSP and 3SAT, and steers with them. O5 needs to distinguish itself: it tests *causal abstraction of a specified heuristic* (DAS, interchange interventions) and checks it against behavioural identification. AlgoTrace only clusters and labels.
5. **Content effects under re-theming are already published (medium).**
   - EHOP (Duchnowski, Pavlick & Koller, EMNLP 2025) uses textbook, real-life and inverted framings of NP-hard problems. Heyman & Zylberberg use Math vs Friends.
   - Our bare vs realistic framing contrast is not new. The inverted-rule manipulation from EHOP is worth adopting.
6. **Cross-domain consistency of decision rules (H4) has a first result (medium).**
   - Zhang et al. 2026 report 75–80% agreement across SAT, Vertex Cover and 3D-packing reductions. H4 should cite this and go further: identify the *same named heuristic* across domains, not just matching verdicts.
7. **O1's "measure hardness with solvers" is now known to be insufficient (medium, and an opportunity).** Verma 2026 makes exactly this point. Our answer is to define model-relevant hardness *relative to the zoo*, which strengthens the whole paper.

---

## Results bearing on O2(a)–(c) and H3

**O2(a): accuracy falls with size and hardness.**

- *Supported almost everywhere:* Shojaee; Hazra; Zhang 2026 (ADR decays with N); GraphArena; NLCO; NPPC; DeepRD; Valmeekam 2024 (o1 at 6–20 blocks).
- *Complication:* Verma 2026. At fixed size and matched density, *proof hardness* didn't predict accuracy. Size seems to matter more than solver-measured hardness.
- *Complication:* Corrêa et al. Frontier models now plan at planner level on IPC-sized tasks. The collapse point moves with each model generation.

**O2(b): thinking tokens grow sub-exponentially.**

- *Supported:*
  - Estermann & Wattenhofer: roughly linear growth for R1 and o3-mini.
  - Hazra: R1's output grows polynomially with input length.
  - Shojaee and NPPC: rise, then *decline*.
- *Caveats:*
  - Several of these tasks are in P. Tents is linear-time. Hanoi is trivial per move, and its exponential *output* confounds the measure (Lawsen).
  - Verma: tokens don't track solver hardness once length is controlled. Budget caps censor the data and must be modelled as censoring.
- *Interp.:* the drop after the peak ("giving up") is a behaviour in its own right. It needs a zoo entry: terminate early, then emit a default.

**O2(c): errors are structured, not random.**

- *Supported:*
  - SAT bias (SATBench; Zhang 2026).
  - "Too complex, so UNSAT" lazy answers (Hazra).
  - Hallucinated edges (Heyman & Zylberberg 2025b).
  - ~~Errors concentrated where greedy coloring fails (Heyman & Zylberberg 2025a).~~ Withdrawn by the authors (confounded with edge count; 2505.12151 v3, App. A.1).
  - Greedy-level suboptimality, plus hallucinated infeasible answers that rise with size (GraphArena).
  - o1 producing plans for unsolvable problems (Valmeekam 2024).
- *Caveat:* some structure is *misperception* (hallucinated constraints), not a decision procedure. A heuristic zoo with no perception-error component will misattribute these errors.

**H3: capability and budget shift weight to structural heuristics, not exact search; accuracy still decays with size.**

- *Support:*
  - R1 vs GPT-4o: DPLL and unit propagation vs greedy without backtracking (Hazra).
  - Phi-4-Reasoning vs Phi-4: NN vs brute force or random guessing (AlgoTrace).
  - Reasoning models are less SAT-biased (Zhang 2026).
  - Accuracy still decays with N in all of these.
- *Contradiction 1, exact search at small n:* R1 runs backtracking DPLL at n ≤ 10 (Hazra). Pan et al. prove the construction exists. *Interp.:* H3's "not to exact search" is false below the budget threshold. It should be restated as *exact search within budget, then budget-truncated search with a default answer beyond it*.
- *Contradiction 2, budget non-monotonicity:* more thinking can hurt (Gema et al.; Ghosal et al.). Estermann: higher effort solves larger puzzles. The budget arm of H3 may show an inverted U. Pre-register that possibility.
- *Alternative explanation:* errors in executing a correct plan compound with length (Sinha et al.). Decay with size is predicted by noisy *exact* execution too, so H3's falsifier ("accuracy flat with size") can't tell heuristics from noisy search. The size-decay half of H3 is therefore weak evidence. Weight the claim on *which* wrong answers appear.

---

## Methods and resources to reuse

**Instance generators and hardness measures**

- *Random 3-SAT:*
  - Hazra et al.'s protocol: n = 3–10, α ≈ 1–11, MiniSAT labels, CNF vs "Menu" NL framing.
  - Zhang et al. 2026's **matched SAT/UNSAT minimal pairs** and **ADR**. These cancel SAT bias by construction and should be adopted.
- *Proof-hardness dissociation (Verma 2026):* expander-Tseitin vs ladder-Tseitin at matched density and clause width, pigeonhole anchors, proof-preserving relabeling controls, budget-censoring analysis. Code is on GitHub (linked from the paper).
- *Heuristic-relative hardness:* Heyman & Zylberberg's **greedy score** (randomized greedy success rate). Generalise it to "fraction of the zoo that errs on the item" or "success rate of `WALK-k`, `UP+GUESS`". This puts O1's hardness measure and O3's discrimination on one footing.
- *Classical dials:* clause/variable ratio (Mitchell et al. 1992); graph connectivity for coloring (Cheeseman et al. 1991); backbone (Monasson et al. 1999, plus the 2+p-SAT companion paper); backdoor size (Williams et al. 2003); Pisinger's (2005) hard knapsack classes. Smith-Miles et al. 2021 instance space analysis is a lead.
- *Lookahead and branching:* the DeepRD generator (Rameshkumar et al. 2025). Its method for measuring the real-world complexity distribution is a template for O1's claim that realistic distributions contain hard cores.

**Benchmarks and generators to borrow or compare against**

- NPPC `npgym`: 25 NP-complete problems × 10 levels, with verifiers (github.com/SMU-DIGA/nppc).
- NPHardEval: 9 tasks × 10 levels.
- Reasoning Gym: 100+ generators.
- SATBench (github.com/Anjiang-Wei/SATBench).
- EHOP: textbook / real-life / inverted framings.
- GraphArena: TSP and other NP-complete graph tasks.
- PlanBench with Mystery Blocksworld.
- Corrêa et al.'s freshly generated IPC tasks.

**Scoring taxonomies**

- GraphArena's classes: correct / suboptimal / hallucinatory (infeasible) / missing.
- Heyman's split: invalid coloring vs false "uncolorable".
- Lawsen and Varela's lesson: verify that every item is solvable.
- Valmeekam's unsolvable-instance probes.

**Theory and tooling for O5/O6**

- Pan et al.'s **PARAT** compiles NumPy-style specs to transformer weights. It already implements DPLL. Use it alongside Tracr as a positive control, and to compile `UP-k` and `DPLL-b`.
- PENCIL: erasable CoT, relevant to O6 prediction 3.
- Saunshi et al. and Merrill & Sabharwal 2025: theory for looped models.

**Cross-domain construction for H4:** use polynomial reductions to make isomorphic items, as Zhang et al. 2026 do with SAT→Vertex Cover and SAT→3D packing. A heuristic stated on SAT predicts answers on the reduced instance.

---

## Suggested changes to DESIGN.md

1. **O2 step 1, precision.**
   - Change it to: "A fixed transformer forward pass with log precision is in *log-space-uniform* TC⁰ (Merrill & Sabharwal 2023). With constant precision and no CoT, it is in AC⁰ (Li et al. 2024)."
   - Attribute "poly steps ⇒ exactly P" to Merrill & Sabharwal 2024 only, and note its generalized pre-norm assumption.
   - Move **Feng et al. 2023** to the direct-answer sub-bullet. Its result is that arithmetic and linear equations can't be answered directly by bounded-depth transformers under TC⁰ ≠ NC¹.
   - Add Amiri et al. 2025: linear CoT lower bounds even for problems in P. Add Merrill & Sabharwal 2025: padding alone stays in TC⁰, so filler tokens don't count as thinking.
2. **O2 step 2, add the converse.**
   - Pan et al. 2025: a fixed transformer decides 3-SAT with ≤ p·2^(p+1) CoT steps by running DPLL. The operative quantity is *budget relative to 2^Θ(n)*, not the bare fact of a polynomial budget.
   - Make this explicit: below budget, exact search is possible and observed (R1 at n ≤ 10, per Hazra). Above it, heuristics take over. The §8 mitigation (size sweeps past the budget) should become a stated design rule: for each model and budget, find the n where exhaustive DPLL would exceed the budget, and centre the size sweep on it.
3. **O2 steps 2–3, worst-case vs distribution.**
   - P ≠ NP says some instance is wrong. It doesn't say the model is wrong on many items *from our distribution*. Average-case hardness of random 3-SAT near threshold is a separate conjecture (see Unverified: Feige's hypothesis).
   - Rephrase step 3 as "on some instances". Leave the distributional claim to measurement.
4. **O1 item 2, hardness measurement.** Keep the solver metrics, but:
   - (a) control density and formula length jointly;
   - (b) add proof-hard vs proof-easy families at matched density (Verma 2026);
   - (c) add **heuristic-relative hardness**: the number of zoo heuristics that err on the item, and a greedy score.
   - Then report which hardness axis predicts model errors. That result is itself a contribution and ties O1 to O3.
5. **O1 framing.**
   - Cite Rameshkumar et al. 2025 (real-world instances mostly within the success range; long tail outside) as the honest version of "realistic distributions contain hard cores".
   - Engage van Rooij, Wright & Wareham (2012). In our framing a heuristic is a *different, tractable function* that agrees with the target on many inputs. Identifying *which* function is exactly the computational-level revision they ask for. That turns a likely reviewer objection into motivation.
6. **O2 rules.** Add:
   - (a) answer formats with **small, polynomial output size**, so length limits don't masquerade as reasoning failure (the Hanoi lesson);
   - (b) a solvability check on every item;
   - (c) budget-capped runs analysed as **censored** in token-vs-size models;
   - (d) a separate "declared impossible / too complex" category, distinct from refusal and from UNSAT;
   - (e) matched SAT/UNSAT pairs for decision tasks.
7. **Zoo additions.**
   - `SAT-BIAS` / `ALWAYS-SAT`.
   - `DENSITY` (UNSAT above an α or length cutoff).
   - `GIVE-UP→default` (stop early, answer UNSAT or "impossible").
   - `DPLL-b` (DPLL with a decision budget b, then a default). This links exact search to heuristics, and H3 becomes "b grows with capability and budget".
   - `NOISY-EXACT` (exact algorithm with per-step slip probability).
   - `HALLUC-CONSTRAINT` (adds or drops a constraint, e.g. a phantom edge).
   - Without the last two, the mixture model will credit perception and execution errors to procedural heuristics.
8. **Restate H3.** For example: "Capability and budget raise the effective search budget b and shift weight from surface to structural heuristics. On instances whose exhaustive search exceeds the budget, residual errors match budget-truncated search plus its default answer, not random noise."
   - Change the falsifier to: on items beyond budget, error agreement with truncated-search predictions is no higher than with surface heuristics.
   - Pre-register that budget effects may be non-monotone (Gema; Ghosal).
9. **H4 method.** Build cross-domain item pairs by polynomial reduction (SAT ↔ Vertex Cover ↔ coloring), following Zhang et al. 2026, and cite them as the first cross-representation consistency result.
10. **Domain table.**
    - Planning: cite Valmeekam et al. 2024 for o1 and Corrêa et al. for frontier models rivalling planners. Expect near-exact search at PlanBench sizes and choose sizes to match.
    - Graph coloring: cite Heyman & Zylberberg ×2. The hallucinated-edge effect makes structured JSON *graph restatement* a useful diagnostic. For example, ask the model to echo the edge list as a parsed side output (secondary analysis).
11. **Content effects.** Cite EHOP and add its *inverted-rule* manipulation. It cleanly separates "retrieves the textbook problem" from "runs a procedure on the stated constraints".

---

## Citation corrections (DESIGN.md §10, my slice)

| Entry in DESIGN.md | Status | Correction |
|---|---|---|
| Merrill & Sabharwal (2023). *The Parallelism Tradeoff: Limitations of Log-Precision Transformers.* TACL | Correct | TACL vol. 11, pp. 531–545; arXiv 2207.00729, formerly titled "Log-Precision Transformers are Constant-Depth Threshold Circuits". **§3 text:** the class is *log-space-uniform* TC⁰, under log precision and with feedforward nets computable in linear space. Not just "uniform TC⁰". |
| Merrill & Sabharwal (2024). *The Expressive Power of Transformers with Chain of Thought.* ICLR | Correct | arXiv 2310.07923. **§3 text:** the exact-P result needs polynomial steps *and generalized pre-norm*. Linear steps need projected pre-norm. |
| Feng et al. (2023). *Towards Revealing the Mystery behind Chain of Thought: A Theoretical Perspective.* NeurIPS | Title, venue and year correct (NeurIPS 2023 oral; Feng, Zhang, Gu, Ye, He, Wang; arXiv 2305.15408) | **Miscited in §3 O2 step 1.** It doesn't show that poly-token generation stays in P. It shows the *no-CoT impossibility* for arithmetic and equations, plus CoT constructions for DP. Cite it for the direct-answer bullet. |
| Shojaee et al. (2025). *The Illusion of Thinking.* | Incomplete | Full title: *The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity.* NeurIPS 2025. arXiv 2506.06941 (v3 is the camera-ready, with an appendix answering critiques). Authors: Shojaee, Mirzadeh, Alizadeh, Horton, Bengio, Farajtabar. |
| Lawsen (2025). *The Illusion of the Illusion of Thinking* (comment on Shojaee et al.) | Title differs by source | arXiv 2506.09250. The **arXiv listing title** is *"Comment on The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity"*; the PDF's title is "The Illusion of the Illusion of Thinking". v1 (10 Jun 2025) listed C. Opus (Claude) as co-author. v2 (16 Jun 2025) removed it under arXiv policy and fixed errors in §§4 and 6. Not peer-reviewed. **§3 text:** the dispute was about truncation and unsolvable River Crossing instances, *and also* about whether Hanoi's exponential move count measures reasoning complexity. Add Dellibarda Varela et al. 2025 as an independent replication. |
| Mitchell, Selman & Levesque (1992). *Hard and Easy Distributions of SAT Problems.* AAAI | Correct | AAAI-92, pp. 459–465 (AAAI-92 Best Written Paper). |
| Williams, Gomes & Selman (2003). *Backdoors to Typical Case Complexity.* IJCAI | Correct | IJCAI-03, pp. 1173–1177 (some indexes give 1173–1178). Official capitalisation: "Backdoors To Typical Case Complexity". **§3 text:** this paper supports "backdoors", not "low treewidth". Cite a treewidth source separately, or drop it. |
| Fan et al. (2024). *NPHardEval.* ACL | Title incomplete | Fan, Hua, Li, Ling & Zhang (2024). *NPHardEval: Dynamic Benchmark on Reasoning Ability of Large Language Models via Complexity Classes.* ACL 2024 (Vol. 1: Long Papers), pp. 4092–4114. doi:10.18653/v1/2024.acl-long.225. arXiv 2312.14890. |
| Valmeekam et al. (2023). *PlanBench.* NeurIPS Datasets & Benchmarks | Title incomplete | Valmeekam, Marquez, Olmo, Sreedharan & Kambhampati (2023). *PlanBench: An Extensible Benchmark for Evaluating Large Language Models on Planning and Reasoning about Change.* NeurIPS 2023 Datasets & Benchmarks Track. arXiv 2206.10498 (first posted 2022). Suggest adding Valmeekam, Stechly & Kambhampati (2024), arXiv 2409.13373, for o1 results. |

References to add (all verified this session): Li et al. 2024; Amiri et al. 2025; Merrill & Sabharwal 2025 (padding); Pan et al. 2025; Hazra et al. 2025; Zhang et al. 2026 (FSE); Verma 2026; Heyman & Zylberberg 2025a,b; GraphArena (Tang et al. 2025); EHOP (Duchnowski et al. 2025); AlgoTrace (Lippl et al.); Rameshkumar et al. 2025; Gema et al. 2025; Sinha et al. 2026; van Rooij, Wright & Wareham 2012; Cheeseman et al. 1991.

---

## Unverified / leads

Not checked, or seen only in search snippets. Don't cite these without checking.

- **Feige's average-case hardness hypothesis for random 3-SAT** (Feige 2002, STOC?). This is the standard citation for "random 3-SAT near threshold is hard on average", which O2's distributional claim needs. Not searched; the budget ran out.
- **Merrill & Sabharwal 2025, "A Little Depth Goes a Long Way"** (on looped and deeper transformers). Seen only as a cited key inside the padding paper. Title, venue and claims not verified.
- **Monadic FO satisfiability "NEXPTIME-complete"** and **bounded-length planning "NP-complete (PSPACE without the bound)"** in the §3 O1 table. These are standard results (Lewis 1980; Bylander 1994, from memory) but were not verified this session. Note that bounded planning is NP-complete only when the bound is polynomial (e.g. given in unary).
- **Hazra et al. 2024, arXiv 2408.07215**, "Can Large Language Models Reason? A Characterization via 3-SAT". The earlier version of #16. A search snippet says GPT-4 spends more tokens in the hard region while accuracy drops.
- **NPG-Muse** (arXiv 2508.20373): RL on NP-hard graph problems to scale long CoT. A 7B model is reported to beat QwQ-32B. Seen in search results only. *Interp.:* future models may be trained on exactly our domains, a contamination and drift risk.
- **OPT-Engine** (arXiv 2601.19924): a case study in which DeepSeek-V3.2's text-only TSP trace starts with nearest neighbour and then refines. Snippet only.
- **"To Backtrack or Not to Backtrack: When Sequential Search Limits Model Reasoning"** (arXiv 2504.07052, COLM 2025 per PDF header). Explicit backtracking traces help on Sudoku and hurt on CountDown. Relevant to H3. Authors not retrieved.
- **"How Much Backtracking is Enough?"** (arXiv 2505.24273) and **"Wait, Wait, Wait… Why Do Reasoning Models Loop?"** (arXiv 2512.12895). Looping is more frequent on harder problems, relevant to the give-up / loop failure category. Snippets only.
- **OpenXOR / "Reasoning: From Reflection to Solution"** (arXiv 2511.11712). Claims an NP-hardness result for a simple-looking task where greedy fails and backtracking succeeds. The snippet was garbled.
- **"Natural Language Satisfiability: Exploring the Problem Distribution…"** (ACL 2024 long 815). A snippet says GPT accuracy falls as the variable count grows, and the hard band narrows. Full title and authors not retrieved.
- **LogicPhase** (OpenReview q47jRIeaZl) and **"Logical Phase Transitions"** (Zhang et al., ACL 2026, arXiv 2601.02902, verified abstract). Collapse beyond a critical "logical depth". Relevant to the entailment domain, but the formalism and models weren't stated on the abstract page.
- **FrontierCO** (arXiv 2505.16952; ICLR 2026 per search) and **HeuriGym** (arXiv 2506.07972; NeurIPS 2025). These are about LLMs *writing* heuristic code, not answering directly. Low overlap, but reviewers may conflate them with this project, so cite to distinguish.
- **"Formalize, Don't Optimize: The Heuristic Trap in LLM-Generated Combinatorial Solvers"** (arXiv 2605.12421; NeurIPS 2026 listing). Code-generation setting; low overlap.
- **Smith-Miles, Christiansen & Muñoz (2021)**, "Revisiting where are the hard knapsack problems? via Instance Space Analysis", C&OR 128:105184. Seen in search results; a good source of hardness features for knapsack.
- Not searched (budget): Kambhampati's LLM-Modulo position papers; Stechly et al. "Chain of Thoughtlessness" (NeurIPS 2024); NLGraph (Wang et al. 2023); Sudoku-Bench; Strobl et al.'s TACL survey of transformer expressivity; Chiang's "Transformers in uniform TC⁰". All are worth a check by whoever owns the adjacent slices.
