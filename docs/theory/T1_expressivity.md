# T1. Expressivity and compute: which heuristics can a thinking LLM actually run?

*Theory-crafting note, written 2026-11-13, before any project data. One of three: T2 covers RASP-L program length, learnability and simplicity bias; T3 covers LLM precedent and training pressure. Overlaps are marked [→T2] and [→T3] and are not argued here. This note builds on [literature/A_hardness_compute.md](../literature/A_hardness_compute.md), [literature/D_rasp_algorithms.md](../literature/D_rasp_algorithms.md) and [literature/F_heuristic_classes.md](../literature/F_heuristic_classes.md) and does not repeat them. Family labels follow [PAPER_SKELETON.md](../PAPER_SKELETON.md) Table 4.*

**Citation status.**

- ✓ = verified in this session by search or fetch: title, authors, year, venue where given, and the specific claim used.
- [A] / [D] / [F] = verified in literature slice A, D or F. Taken from that slice, not re-checked here.
- [V:x] = taken from vertical document x in [verticals/](../verticals/) (its own construction or check).
- [?] = not verified; a lead or a textbook fact I did not re-check.
- **Sim** = a result of this note's own simulations. Code: [`scripts/theory/expressivity/`](../../scripts/theory/expressivity/) (pure Python, fixed seeds, each part runs in minutes).

**Regimes** (the same labels as T3):

- **1P:** one forward pass. A single-token direct answer, or the computation inside one chain-of-thought step.
- **DS:** a direct answer with a structured multi-token output (assignment, colouring, tour) and thinking off. The output stream works as a scratchpad, one sequential step per emitted token ([C_constructive.md](../verticals/C_constructive.md) P4).
- **TH:** thinking at best effort (gpt-oss high, Qwen3 thinking), with about 32k tokens.

**Support types in the score table:** **Thm** = theorem; **Con** = explicit construction (a transformer or RASP-style program exists); **Sim** = our simulation; **Emp** = empirical result in the literature; **Arg** = argument or back-of-envelope.

---

## 0. Summary

1. **Every step function in the zoo is constant depth** (≈ 2–6 layers). Families differ in how many *dependent* steps they need, whether a step needs a *global* aggregate, and how much text a step writes. In **1P** the natural members are A, C0, B4 rewrites, H and a few rounds of B1/E. In **TH** everything except B3, SA and *explicit* E is cheap at our sizes.
2. **P-completeness overstates 1P difficulty at our sizes.** First-fit colouring on random graphs (n ≤ 40, listing order unrelated to structure) has only **4–10 dependency levels**; SAT mention-order GREEDY has **16–28** at n = 20–60; the NN tour has n − 1 (Sim).
3. **"L layers ≈ L rounds of message passing" is an upper bound for decoders on text.** About 2 layers per round, forward-in-text paths only (causal mask), half the layers mostly refine, and gpt-oss has only **12 / 18 full-attention layers**. Realistic radius: ≈ 3–9 rounds (gpt-oss) to ≈ 10–16 (Qwen3-14B/32B).
4. **The 32k budget line depends more on the ordering rule than on verbosity** (Sim). Exact DPLL on UNSAT random 3-SAT: n\* ≈ 30 with listing-order branching vs ≈ 50 most-constrained-first (verbose); terse traces add 13–30; the SAT side lies near 70–80. Each ×4 of budget adds only 11–31 variables.
5. **Colouring (≤ 40 nodes) and entailment (3–12 premises) sit below the line** for any sensible exact method: DSATUR-ordered search needs ≈ n node visits, and truth tables fit to ≈ 9 atoms. So **errors there at best effort are not compute-forced** (noise, or a chosen shortcut [→T2, →T3]). Heuristics are forced only on SAT above n ≈ 30–50, TSP (10–14 cities) and large-capacity knapsack.
6. **E is cheap inside a pass and expensive as text** (one explicit BP round at n = 40 ≈ 9–22k tokens), so in TH expect *implicit* E: the value heuristic inside search.

---

## 1. Score table

Scores run from **−2** (theory says the member is hard or implausible to compute in this regime) to **+2** (natural and cheap). They rate *computability and cost at our sizes*, not whether the model uses the member. A +2 means "available", and choice among available members is T2's and T3's question.

- **1P** = one forward pass, for a single-token answer or within one CoT step.
- **TH** = thinking at best effort with about 32k tokens, at our sizes: SAT n ≈ 10–60, colouring 8–40 nodes, entailment 3–12 premises, TSP 10–14, knapsack about 20 items.
- **Conf** = confidence in the 1P / TH score.

| Family · member | 1P | TH | Conf | Support | Key citations | Note |
|---|---|---|---|---|---|---|
| **A1** `ALWAYS-SAT`, `NONE`, `ECHO` | +2 | +2 | high / high | Thm (trivial), Con | MS 2023 [A] | Constant map or copy |
| **A2** counts and thresholds: `DENSITY`, `LENGTH-PRIOR`, `FREQ`, `ATMOSPHERE` | +2 | +2 | high / high | Thm, Con | Counting is TC⁰; Yehudai et al. ✓; C-RASP [D] | Name vocabulary ≤ 60 ≪ width, so histogram counting works |
| **A2** positional: `PRIMACY`, `RECENCY` | +2 | +2 | high / high | Con | Weiss et al. 2021 [D] | Positional select |
| **A3** `TEXTBOOK-TRANSFER` | +1 | +1 | low / low | Arg | — | The rewrite is constant depth; the solve inherits the substituted procedure's score |
| **B1** `UP-k`, small k | +1 | +2 | med / high | Con, Thm (LOCAL = GNN) | Sato et al. 2019 [F]; Sanford, Hsu & Telgarsky 2024 ✓; [V:B1] | About 2 layers per round. Chains can use doubling; branching cones cannot (§2.2) |
| **B1** `UP` to fixpoint | −1 | +2 | high / high | Thm (P-complete), Sim | Jones & Laaser 1976 [F]; GHR A.6.1 [F] | −2 asymptotically. At our sizes propagation depth per decision has median 1–2, p90 4–7 (Sim) |
| **B1** `RES-w` (bounded-width resolution) | −1 | 0 | low / med | Arg | [V:B1] | Closure needs many levels; the number of resolvents grows like n^O(w) |
| **B1** `PREMISE-SUBSET`, `DROP-CONSTRAINT` | +2 | +2 | med / high | Arg | — | The selector is constant depth; the solve inherits |
| **B1** `2SAT-CORE` | 0 | +1 | med / med | Thm (NL; log depth suffices) | MS 2025b ✓; Sanford et al. 2024b ✓ | Implication-graph reachability |
| **B1** `MST-TOUR` | −1 | +1 | med / med | Arg | — | MST is in NC (Borůvka) [?]; Prim needs n steps in CoT |
| **B3** `LP-ROUND` | −2 | −1 | med / low | Thm (LP P-complete), Arg | GHR A.4.3 [F] | On knapsack its output equals RATIO plus one fractional item: an identification problem, not an expressivity one |
| **B4** local rewrites: `FIRST`, `MATCH`, `BICONDITIONAL`, `CLOSED-WORLD`, `ADD-CONSTRAINT` | +2 | +2 | high / high | Con | [V:B4] sketches (depth 2–3) | Downstream inference is costed separately |
| **B4/C4** sequential updates: `MM`, `ETR`, `ONLINE-STATE(k)` | +1 / 0 | +2 | med / high | Arg, Con | Liu et al. 2023 [D]; Li et al. 2024 [A] | About 3 layers per premise. +1 up to about 5 premises, 0 at 12 |
| **B5** `EXPECTED-COST` | +1 | +1 | low / low | Thm, Arg | Hesse, Allender & Barrington 2002 ✓ | Iterated multiplication is in TC⁰; practical numeric precision is a separate issue [→T3] |
| **C0** `POLARITY`, `MOMS`, `PURE-LITERAL` | +2 | +2 | high / high | Con | [V:C] (2 layers) | Counts plus a sign |
| **C1** `FIRST-FIT` colouring, single target query | −1 | +2 | med / high | Thm (P-complete), Sim | GHR A.2.6 [F]; §3.5 | 4–10 levels on our random graphs (Sim): 0 for Qwen3-32B, −2 on gadgets with d > 10 |
| **C1** any member, answer written in processing order (DS) | +2 | +2 | high / high | Thm | Li et al. 2024 [A] | The output is the chain of thought |
| **C1** `GREEDY` (SAT, mention order) | −2 | +2 | med / high | Sim, Arg | §3.5 | 16–28 dependency levels at n = 20–60 |
| **C1** `NN-from-0` (TSP) | −2 | +2 | high / high | Thm | GHR A.2.12 [F] | n − 1 dependent steps |
| **C1** `RATIO` / `VALUE` (knapsack) | +1 (prefix) / −1 (skip) | +2 | med / high | Arg; Thm | GHR remark under A.8.5 [F] | `RATIO-PREFIX` = rank by counting, then a prefix sum: constant depth. `RATIO-SKIP` is P-complete |
| **C2** `DSATUR`, `UC` / `GUC` / `SC`, `GREEDY-EDGE`, `FARTHEST-INSERTION` | −2 | +2 | med / high | Arg; Thm for UC | GHR A.6.1 [F] | n steps, each a global argmax (about 4–5 layers). UC contains UP to fixpoint |
| **C3** `RANDOM-ORDER-FIRST-FIT` | 0 | +1 | med / med | Thm, Sim | Blelloch et al. 2012 [F]; Fischer & Noever 2018 ✓ | Polylog dependency depth. A pass has no randomness of its own; an arbitrary fixed order is just C1 |
| **D** `DPLL-b` | −2 | +2 below n\*; truncated above | high / high (n\*: med) | Con, Sim | Pan et al. 2025 [A]; §3 | 1P can run only the b = 0 member (the default or the first value choice) |
| **D** `BEAM-w` | −2 | 0 | med / low | Thm (pBT width), Arg | Alekhnovich et al. 2011 [F] | w trails per level in a linear trace |
| **D** `BACKDOOR-k` | −1 | +1 | low / low | Arg | Williams et al. 2003 [A] | 2^k branches × UP. The set must be guessed |
| **E** `WP-t`, `UP`-style hard messages, t ≤ 3 | +1 | −1 explicit / +2 implicit | med / med | Thm (GNN), Con, Arg | Sato 2019 [F]; Kim et al. 2022 ✓; Sanford et al. 2024a ✓ | §2.2: about 2 layers per round, causal paths only |
| **E** `BP-t` (soft) | +1 | −1 explicit / +2 implicit | med / med | Con, Arg | as above | Needs log-odds arithmetic; same depth as WP |
| **E** `SP-t` | 0 | −2 explicit / +1 implicit | low / low | Arg | — | Three-component messages |
| **E** decimation: `BP-DEC`, `SP-DEC` | −2 | −2 explicit / +1 inside C or D | med / med | Thm (UP fixpoint), Arg | GHR A.6.1 [F] | Explicit cost is n × rounds × 3m messages |
| **E** `LOCAL-t` colouring | +1 | −1 | med / med | Thm | Linial 1992 ✓ | Local rounds can't make a long cycle or chain globally consistent |
| **F** `WALK-k`, `MIN-CONFLICTS` | −2 | +1 | high / med | Thm (PLS), Sim | Schäffer & Yannakakis 1991 [F] | SAT side only. Viable only if the violation check happens inside the pass (§3.4) |
| **F** `2OPT-k` (TSP n ≤ 14) | −2 | +1 | high / med | Arg | — | One pass over candidate moves ≈ 2.5k tokens |
| **F** `SA` | −2 | −1 | high / low | Arg | — | Needs calibrated randomness and acceptance probabilities |
| **G** `DP-EXACT` (knapsack) | −1 | +1 / −1 | med / med | Con, Arg | Feng et al. 2023 [A] | +1 while reachable sums per stage are ≲ 300; −1 above |
| **G** `IGNORE-CROSSLINKS` | +1 | +2 | med / med | Arg, Thm | Sanford et al. 2024b ✓ | Splitting by section is constant depth; by component it needs log depth |
| **H** `RANDOM` | +2 | +2 | high / high | trivial | — | The randomness comes from decoding, not from the computation |
| **H** `SAMPLE-m` (`FIXED-PROBE-m` in 1P) | +1 | +2 | med / high | Arg | — | m parallel AND-of-OR checks |
| **I** strategy selector | +2 | +2 | med / med | Arg | — | Cue features are constant depth. Whether the selector chooses well is [→T2] |
| *Nuisance* `NOISY-EXACT` | n/a | n/a | — | Arg, Emp | Sinha et al. 2025 [A] | Predicts error that grows with *work*, not with work ÷ budget (§3.6) |
| *Nuisance* `PERCEPTION-NOISE` / `HALLUC-CONSTRAINT` | n/a | n/a | — | Thm (retrieval is 1 layer) | Sanford et al. 2024b ✓ | Not an expressivity limit; empirical [→T3] |

Abbreviations: MS 2023 = Merrill & Sabharwal (TACL 2023). MS 2025b = Merrill & Sabharwal, "A Little Depth Goes a Long Way" (NeurIPS 2025). Sanford et al. 2024a = Sanford, Hsu & Telgarsky (ICML 2024). Sanford et al. 2024b = Sanford et al., graph algorithms (NeurIPS 2024). GHR = Greenlaw, Hoover & Ruzzo compendium of P-complete problems.

---

## 2. Reasoning

### 2.0 Terms

- **Forward pass / depth.** One forward pass computes each new token with a fixed number of layers L. Its *depth* is the length of the longest chain of dependent operations it can compose: at most L attention-plus-MLP blocks.
- **TC⁰ / AC⁰ / NC.** Problems solved by polynomial-size circuits of constant depth:
  - **TC⁰** allows threshold (majority) gates;
  - **AC⁰** allows only AND/OR gates;
  - **NC** allows polylogarithmic depth.
- **P-complete.** As hard as anything solvable in polynomial time, under reductions that run in logspace or NC. Unless TC⁰ = P (and in fact unless NC = P), no constant- or polylog-depth circuit family computes a P-complete function.
- **Log precision.** Activations carry O(log n) bits.
- **Dependency depth** of a procedure on an instance: the longest chain of steps in which each step needs the result of the previous one. A sequential procedure can still have small dependency depth on a given instance.
- **Round.** One synchronous update in which every node reads its neighbours' current state (the LOCAL model of distributed computing).
- **Budget line n\*.** The instance size at which a procedure's typical CoT trace exceeds the token budget (DESIGN O2).

### 2.1 Shared facts the scores rest on

| # | Fact | Status |
|---|------|--------|
| F1 | A log-precision transformer forward pass is in log-space-uniform TC⁰ (Merrill & Sabharwal 2023). With constant precision and no CoT it is in AC⁰ (Li et al. 2024). So, unless TC⁰ = P, no fixed-depth model computes first-fit colouring, the NN tour, UP to fixpoint, arc consistency or LP outputs *on all inputs at all sizes*. | Thm [A]. Asymptotic and conditional: it constrains *trends in n*, not behaviour at n = 20 |
| F2 | T CoT steps buy circuits of size T (Li et al. 2024). Polynomially many steps give exactly P (Merrill & Sabharwal 2024, generalized pre-norm). Filler tokens alone stay in TC⁰ (Merrill & Sabharwal 2025, padding). Parity and reachability need CoT of length at least linear in n (Amiri et al. 2025). | Thm [A] |
| F3 | Exact search is expressible: a fixed 7-layer transformer decides 3-SAT on p variables by DPLL with UP in at most p·2^(p+1) CoT steps (Pan et al. 2025). | Con [A] |
| F4 | Depth buys composition. Log depth suffices for graph connectivity and regular languages, which fixed depth cannot express under standard conjectures (MS 2025b ✓). Log depth is necessary and sufficient for connectivity in Sanford et al. 2024b ✓. k-hop induction heads need about log₂k + 2 layers, with a conditional Ω(log k) lower bound (Sanford, Hsu & Telgarsky 2024 ✓). An L-layer decoder needs n^Ω(1) width to compose L functions in sequence, and L vs L+1 layers is an exponential separation (Chen, Peng & Wu 2024 ✓, preprint). One attention layer cannot reliably compose two functions over large domains (Peng, Narayanan & Papadimitriou 2024 ✓). | Thm |
| F5 | Graph-side equivalences. L-layer GNNs are exactly L-round LOCAL algorithms (Sato et al. 2019 [F]). For some problems GNNs need depth × width ≥ Ω̃(n^δ), with δ ∈ [½, 2] (Loukas 2020 ✓). A plain transformer over node and edge tokens with node identifiers is at least as expressive as 2-IGN, which exceeds all message-passing GNNs (Kim et al. 2022 ✓). A constant number of attention layers simulates, and is simulated by, a constant number of MPC rounds (Sanford, Hsu & Telgarsky 2024 ✓). Looped transformers simulate BFS, DFS, Dijkstra and SCC from an adjacency-matrix input (Back de Luca & Fountoulakis 2024 ✓). | Thm / Con |
| F6 | Our models' depth (HF `config.json`, fetched this session ✓). Global attention means every layer can attend to the whole context. All four models have far more width than our state needs (n ≤ 60 variables × a few bits), so **depth and causality, not width, bind in 1P at our sizes**. | Fact. Table below |
| F7 | In Llama 3.1 and Qwen 3, second-half layers contribute much less to later computation. There is no evidence that deeper models use the extra depth to compose more sub-results on multi-hop tasks (Csordás, Manning & Potts 2025 ✓). We use "effective depth ≈ half of L" as a working discount. | Emp |
| F8 | Causal masking. A decoder position sees only earlier positions, so multi-step computation over a prompt runs only along position-increasing paths, except at the final positions. Supporting evidence: permuting premises out of proof order costs over 30% accuracy (Chen et al. 2024 ✓); repeating the prompt improves *non-reasoning* models and is neutral with reasoning on (Leviathan, Kalman & Matias 2025 ✓); Chen, Peng & Wu prove an encoder–decoder separation ✓. | Arg (elementary) + Emp |
| F9 | Every per-step program in the zoo's RASP sketches is constant depth: about 2–3 layers (C0, C1 steps, B4 rewrites), about 5 (a DPLL step), 5–6 (a WalkSAT flip), about 2 per BP round ([V:C], [V:D_F], [V:E], [V:B1]). These are construction estimates, not measurements of trained models. | Con (sketch) |

F6, model depth:

| Model | Layers L | Full-attention layers | Sliding-window layers (128 tokens) | Width |
|---|---|---|---|---|
| gpt-oss-20b | 24 | 12 | 12 | 2880 |
| gpt-oss-120b | 36 | 18 | 18 | 2880 |
| Qwen3-14B | 40 | 40 | 0 | 5120 |
| Qwen3-32B | 64 | 64 | 0 | 5120 |

### 2.2 Message passing ↔ attention (task item 4)

**The claim:** L layers implement about L rounds of message passing on a constraint graph serialised as text.

**What is proven.**

- For GNNs, L layers are exactly L LOCAL rounds (F5, Sato).
- For transformers, constructions show one or a few layers per round when the graph is presented as node and edge tokens with identifiers and attention is **bidirectional** (TokenGT; the MPC simulation).
- Looping can stand in for depth (F5; Saunshi et al. 2025 [A]; Giannou et al. 2023 ✓).
- None of these is about a causal decoder reading CNF or prose.

**What changes for a decoder reading text.**

1. **About two layers per round, not one.** On a factor graph a round has two hops:
   - literal → clause: aggregate the clause's other literals;
   - clause → variable: aggregate over all mentions of the variable.

   The B1 and E sketches both cost about 2 attention layers per round ([V:B1] 2k + 3 layers for `UP-k`; [V:E] 1 + 2t for `BP-t`). So L layers give at most about L/2 rounds, and about L/4 after the effective-depth discount (F7).
2. **Causal paths only.** Variable v's state at position i depends only on tokens before i. A round can bring in neighbour u's previous-round state only if that state already sits at an earlier position.
   - Over the prompt, the computation is therefore a *causal* variant of BP: messages flow forward in text order (the E vertical's `BP-t-CAUSAL`).
   - The final positions (the question, or the first answer token) see everything, so they add one global gathering step. Further rounds over the whole graph would have to happen *inside* those few positions. Their width is ample, but attention cannot route between sub-states of a single position, so this is not message passing in the usual sense.
   - Consequence: **one-pass radius depends on the order of the text**, not only on the graph.
3. **Doubling beats one round per layer only on chains.** Pointer-doubling gives radius about 2^(L/c) along chains (k-hop heads, F4; Ye et al. 2025's 3^L diameter [D]). No such shortcut is known for soft messages on branching trees. Evaluating branching Horn cones is monotone circuit value, which is P-complete. So chains and trees should behave differently (P5).
4. **Sliding windows.** gpt-oss alternates full and 128-token sliding layers. A hop that stays within 128 tokens can use a sliding layer; a hop between distant mentions needs a full layer.
   - In CNF, the literal → clause hop is local (a clause is about 10–13 tokens), so a round costs one full layer: at most 12 (20b) / 18 (120b) rounds nominally.
   - In a shuffled edge list both hops are global, so a round costs two full layers: at most 6 / 9.
   - Qwen3 pays about 2 layers per round either way.

**How serialisation matters.**

| Format | Same-constraint hop | Same-entity hop | Cost per round | Notes |
|---|---|---|---|---|
| CNF, single-token names | Local (inside the parentheses) | Token identity: one content-match head | ≈ 2 layers; 1 full layer for gpt-oss | Cheapest for E/B1 |
| Edge list `u–v` (shuffled) | Adjacent tokens | Token identity | ≈ 2 global layers | Both hops global for gpt-oss |
| Adjacency lists `v: u1, u2, …` | Local (a node's neighbours sit together) | Look up u's line by name | ≈ 2 layers, one of them local | Best for neighbourhood aggregation |
| Natural language (multi-token names, paraphrase) | Within a sentence | Must first build entity representations | + a constant number of layers before round 1; more tokens per constraint (19 vs 10–13 for a clause, measured), so longer distances | Fewer rounds; more perception errors [→T3] |

**Verdict.**

- The claim holds up to a constant factor for bidirectional models over graph-structured tokens (Con, Thm).
- For our decoder LLMs on text it is an **upper bound**: at most about (L_global − 1)/2 rounds, along causal paths, with about L/4 a more realistic ceiling.
- Width is not the constraint at our sizes (F6). Loukas's depth × width bounds concern tasks that need information from far across the graph; with n ≤ 60 and width ≥ 2880 the width side of that product is not what binds. Depth is. A globally consistent colouring of a long cycle is such a task: 2-colouring it is parity (Hahn 2020 ✓), and even 3-colouring needs Ω(log\* n) rounds (Linial ✓).

**Score:** +1 for E and B1 with t ≲ 3 in 1P; confidence medium.

**Round ceilings implied for 1P** (nominal, then roughly halved for effective depth):

| Model | CNF-like (one hop local) | Both hops global | Sequential levels at ≈ 3 layers each (C1, B4 updates) |
|---|---|---|---|
| gpt-oss-20b | ≤ 12 → ≈ 6 | ≤ 6 → ≈ 3 | ≤ 4–8 → ≈ 2–4 |
| gpt-oss-120b | ≤ 18 → ≈ 9 | ≤ 9 → ≈ 4–5 | ≤ 6–12 → ≈ 3–6 |
| Qwen3-14B | ≤ 19 → ≈ 10 | ≤ 19 → ≈ 10 | ≤ 13 → ≈ 6–7 |
| Qwen3-32B | ≤ 31 → ≈ 16 | ≤ 31 → ≈ 16 | ≤ 21 → ≈ 10 |

The ranges for gpt-oss depend on whether each level's lookups are local (≤ 128 tokens) or global.

### 2.3 Per-step simplicity (task item 3)

Every step is constant depth (F9). What matters is whether the step needs **global** information, and how it reads the current state back from the trace.

| Step | Members | Information needed | Layers per step (sketch) | Tokens per step (terse–verbose, measured on sample lines, o200k) |
|---|---|---|---|---|
| Assign the next item in a given order (mex of neighbour colours; sign of a clause count) | C1 FF, GREEDY | Local (neighbours) | ≈ 3 | 4–30 |
| Pick the next item by a global score, then assign | C2 DSATUR, UC; MOMS branching in D | Global argmax over n items (or m clauses) | ≈ 4–5 | 10–40, plus ≈ 8n if the scores are written out |
| One unit propagation | B1, D | Local once the unit clause is found; *finding* one is global | ≈ 3 | 7–37 |
| Decision with backtrack bookkeeping | D | Global: the last unflipped decision on the trail | ≈ 5 | 9–57 per decision or conflict |
| One flip | F WALK | Global (find a violated clause), then local break counts | 5–6 | 16–47, plus ≈ 30m if every clause is re-checked |
| One message | E | Local | ≈ 1 (about 2 per round) | 18 (hard) – 44 (soft); 3m messages per round |
| One premise update | B4/C4 ETR, ONL(k) | Global over the current model set | ≈ 3 | ≈ 37 |
| Check a full candidate | H SAMPLE, verification | Global AND over all constraints | ≈ 2–3 | ≈ 30 per clause if written; ≈ 0 if internal |

Two consequences.

**(i) Global steps are constant depth but fragile.** Finding the one violated clause among 170, or the one maximum-saturation vertex among 40, is a single attention selection in principle (TC⁰). Whether trained models do it reliably is empirical. We expect slip rates to grow with the number of candidates (P12). This is Arg, not Thm.

**(ii) The trace format trades tokens against per-step depth.**

- If each step writes only a delta (`x5=T`), reading the current value of a variable means selecting its latest write that no later backtrack has undone. That is constant depth, but harder.
- If each step rewrites the full state line, reading is a 1-hop copy, at about 3n tokens per step.
- This is the trade-off behind Turing-program and PENCIL-style CoT [D], [A].

### 2.4 Per-family notes

**A. Cue / substitution.**

- *1P.* Counting, ratios and thresholds are majority-type operations, so TC⁰ (Thm). Softmax attention computes averages, and C-RASP counts natively [D]. Histogram counting works when width ≥ vocabulary (Yehudai et al. ✓). Our name vocabularies (≤ 60) are far below 2880–5120. `DENSITY` needs a distinct-variable count: first-occurrence detection, one attention plus an aggregate, about 3 layers [V:A_H].
- *Caveat.* The AC⁰ bound for constant precision (Li et al.) would forbid majority. At our lengths (≤ a few hundred clauses), bf16 activations hold the needed counts. **Score +2 / +2, high.**
- *TH.* Nothing to add: A needs no steps. Expressivity cannot say why a thinking model would ever choose it [→T3].

**B1. Relax.**

- `UP-k` costs about 2k + 3 layers [V:B1], so in 1P k ≲ 3 (gpt-oss) to ≲ 16 (Qwen3-32B) at the nominal ceilings of §2.2.
- Fan-in-1 chains (a → b → c …) are pointer-chasing, and doubling gives log-depth (F4). Branching Horn cones are monotone circuit value, P-complete with no known shortcut. UP to fixpoint is P-complete (Jones & Laaser [F]).
- At our sizes propagation is shallow: per DPLL decision on random 3-SAT, UP depth has median 1–2, p90 4–7, maximum 10–17 at n = 20–60 (Sim). Entailment derivations are at most about #premises ≤ 12 deep.
- In TH, UP to fixpoint costs at most n propagations × 7–37 tokens ≤ 2.2k at n = 60, so it is never budget-bound.
- `2SAT-CORE` is implication-graph reachability (NL-complete [?, textbook]). Log depth suffices (F4); at our n the implication graphs have small diameter.
- `RES-w` closure is many levels deep and generates many resolvents. It is TH-feasible only on small formulas (0).
- `MST-TOUR`: MST is in NC by Borůvka (Arg [?]); in TH, Prim takes n steps for n ≤ 14.

**B3. Convex relax + round.**

- Exact LP is P-complete [F]: −2 in 1P.
- In TH, a by-hand simplex on a knapsack-sized LP is token-feasible (a tableau rewrite per pivot), but there is no reason to expect it [→T3].
- On knapsack the LP optimum is the ratio-greedy prefix plus one fractional item, so LP-ROUND's output coincides with `RATIO`'s. This is an identification problem, not an expressivity one. **−2 / −1.**

**B4. Restrict.**

- *Local rewrites* (`FIRST`, `MATCH`, `BICONDITIONAL`, `CLOSED-WORLD`, `ADD-CONSTRAINT`) are one or two attention operations ([V:B4]: ≈ 3–6 primitives, depth 2–3): **+2 / +2.** The downstream inference on the rewritten problem has its own cost: `FIRST` turns disjunctions into atoms, which leaves Horn-like chains costed as B1.
- *Sequential updates* (`ETR`, `MM`, and C4 `ONLINE-STATE(k)`) cost about 3 layers per premise.
  - In 1P that allows about 2–4 premises (gpt-oss) to about 10 (Qwen3-32B, effective).
  - A parallel-prefix shortcut exists in principle when the update is a fixed finite-state map (Liu et al. 2023 [D]). But the state here is a set of partial models over all atoms, so the shortcut would need impractical width (Arg, low confidence).
  - In TH each update is about 37 tokens over at most 2^(#disjunctions) models: cheap.

**B5. Probabilistic model.** Expected costs are sums and products, and iterated multiplication is in uniform TC⁰ (Hesse, Allender & Barrington 2002 ✓). Expressible, but transformer arithmetic is unreliable in practice [→T3]. **+1 / +1, low.**

**C. Constructive / priority.**

- **C0** is a count and a sign: +2 / +2.
- **C1, as a single target query (1P).**
  - The first-fit colour of vertex v depends on the colours of its earlier neighbours, recursively. This is P-complete for adversarial orders (GHR A.2.6 [F]).
  - But on random graphs whose listing order is unrelated to structure, the dependency depth is small. The longest dependency path (an upper bound) is 4–10 at n = 8–40, and an optimistic witness-based bound is 3–6 (Sim, §3.5).
  - At about 3 layers per level, that sits inside Qwen3-32B's nominal range and outside gpt-oss-20b's. So the "seq" label is about order and gadgets, and the C vertical's E3 NOR gadgets are exactly the right test.
  - SAT mention-order `GREEDY` is different. Each variable shares clauses with about 25 others at α ≈ 4.26, and the dependency depth is about n/2: 16 at n = 20, 28 at n = 60 (Sim). NN-TSP has n − 1 levels by construction.
- **C1 in DS or TH.** One step per token (Li et al.): +2. All C1 members cost n steps × 4–30 tokens, under 2k tokens.
- **C2** (DSATUR, UC, GUC, SC, greedy-edge, farthest insertion) chooses each next item by a global score that depends on every earlier choice. Dependency depth is n, and UC contains UP to fixpoint. **−2** in 1P; available in DS only when the model controls the output order. In TH each step is a constant-depth global argmax: **+2** (§3.2 shows why this ordering rule matters so much).
- **C3.** Random-order greedy has O(log n) (MIS: Fischer & Noever ✓) or polylog (Blelloch et al. [F]) dependency depth. Two caveats:
  - a pass has no randomness, so in 1P "random order" just means some fixed arbitrary order, i.e. C1;
  - our generators' listing orders *are* random relative to structure, so on random items C1 and C3 have the same depth.
- **C1 knapsack.**
  - `RATIO-PREFIX` is a rank (rank(i) = #{j : key_j < key_i}, one count) followed by a prefix sum of weights in rank order (one aggregate). That is constant depth (Arg; this answers report F's "sorting ∈ TC⁰" open item by the standard counting argument).
  - `RATIO-SKIP` is P-complete (superincreasing knapsack [F]).

**D. Truncated systematic search.**

- *1P* can hold only the degenerate member: the default answer, the fill rule, or the value chosen at the first decision. That value choice is where E-implicit enters.
- *TH* is the Pan et al. construction: exact below n\*, truncated with a default above it (§3).
- `BEAM-w` multiplies tokens per level by w and has no natural linear serialisation. pBT width lower bounds rule out polynomial-width beams on hard 3-SAT [F].
- `BACKDOOR-k` costs 2^k × a UP pass, which fits 32k for k ≤ 4. But the model has to *guess* the set (Arg).

**E. Message passing.**

- *1P* is the natural home of E: §2.2, +1 for t ≲ 3, which includes `WP-1/2` and `BP-1/2`.
- *TH explicit* is expensive. One round costs 3m messages × 18–44 tokens. With m = 4.26n, that is about 4.6–11k tokens at n = 20, 9–22k at n = 40 and 14–34k at n = 60. So at most 1–3 explicit rounds fit at n = 40, and explicit decimation (n × rounds) does not fit at all for n ≳ 10.
- *TH implicit* means a one-pass BP-1/2 marginal computed inside each CoT step and used as the value or branching heuristic. That costs nothing in tokens: +2.
- `SP` messages have three components and an explicit SP round is far beyond budget: −2 explicit.
- `LOCAL-t` colouring cannot make long cycles or chains globally consistent. 2-colouring a cycle needs parity, which self-attention cannot do at fixed depth as length grows (Hahn 2020 ✓), and 3-colouring cycles needs Ω(log\* n) rounds (Linial ✓). On our graphs the relevant fact is finite radius, not log\*.

**F. Local search / repair.**

- *1P:* the trajectory is sequential, and predicting the endpoint of standard local search is PSPACE-complete in general (Schäffer & Yannakakis [F]). Only the initialisation member is available: −2.
- *TH:* a flip is constant depth (F9). WalkSAT on satisfiable near-threshold instances needs median 27–330 flips at n = 20–60, with p90 up to about 1.6k (Sim). At 16–47 tokens per flip the median fits in 32k and the tail does not.
- If the trace re-checks all m clauses after each flip (≈ 30 tokens per clause, 2.5–7.7k per check at n = 20–60), only about 4–12 flips fit. So F in TH works **only with internal checking**. F never certifies UNSAT.
- `2OPT-k` on TSP with n ≤ 14: a pass over 77–100 candidate moves costs about 2.5k tokens, so several passes fit.
- `SA` needs calibrated randomness, and LLM sampling is a poor random-number generator: −1.

**G. Decompose / DP.**

- `DP-EXACT` in TH: Feng et al. 2023 give constant-size CoT transformers for a class of DP problems [A], and message-passing architectures align with DP (Xu et al. 2020 ✓). Tokens ≈ n × R × 5, where R is the number of reachable sums (or Pareto pairs) per stage. With n = 20 this fits 32k for R ≲ 300.
- In 1P the state is set-valued over n stages: −1. Unary subset-sum may be in TC⁰ [?], but no practical one-pass circuit is in sight.
- `IGNORE-CROSSLINKS`: splitting by text section is constant depth; splitting by connected component needs log depth (F4).

**H. Guess / sample.**

- `RANDOM` is a constant map plus decoding noise.
- In 1P, `SAMPLE-m` becomes `FIXED-PROBE-m`: m fixed assignments checked in parallel, constant depth.
- In TH, m candidates × a check of about 12 premises at roughly 5 tokens each: m = 20 costs about 1.2k tokens.

**I. Strategy selection.** The selector reads constant-depth cue features: +2 / +2. Whether it selects well is a learning question [→T2].

**Nuisance.** Expressivity says nothing about slip rates. Perceiving a single stated constraint is a one-layer retrieval task (Sanford et al. 2024b ✓), so hallucinated edges (Heyman & Zylberberg 2025b [A]) are not an expressivity failure. They may be an attention-dilution failure on long inputs (Arg).

---

## 3. Budget lines and one-pass depth on our instances

### 3.1 Method

All numbers are medians over 30–40 random instances per cell (Sim; `scripts/theory/expressivity/search_costs.py`).

- **SAT instances:** random 3-SAT, α = 4.26, 3 distinct variables per clause.
- **Colouring instances:** G(n, c/n) with c ∈ {3.0, 4.7, 6.0}, listing order a random permutation.
- **DPLL:** unit propagation plus chronological backtracking, with two branching rules:
  - **INDEX:** the first unassigned variable in listing order, True first. This is C1 order inside D.
  - **JW:** Jeroslow–Wang, a most-constrained-first rule like MOMS. This is C2 order inside D.

  Work is counted as decisions (each value tried), propagated literals, and conflicts.

**Token costs** are o200k_base counts (`trace_tokens.py`) of sample trace lines:

| Event | Terse | Verbose |
|---|---|---|
| Decision | 4 (`x14=T;`) | 9 ("Let's try setting x14 = True.") |
| Propagated literal | 7 (`c23→x3=T;`) | 37 (cites the clause and the reason) |
| Conflict and backtrack | 12 | 57 |
| One clause, restated | 13 (CNF) / 10 (plain) / 19 (natural language) | — |
| One clause, checked | — | 30 |
| BP message | — | 44 |
| WP message | — | 18 |
| WalkSAT flip | 16 | 47 |

Three trace styles are compared: **terse**, **verbose**, and **verbose ×2**. The last doubles the verbose costs to allow for re-checking and hesitation. Every trace also restates the CNF (13 tokens per clause), and a SAT answer is verified (30 tokens per clause).

These per-event costs are the **largest source of uncertainty**: real traces could differ by ×2–×5. The D vertical's plan to measure τ_W on dev traces ([V:D_F] E1) is the right fix.

### 3.2 Exact search on 3-SAT

DPLL work (median):

| n | JW decisions (UNSAT) | JW props (UNSAT) | INDEX decisions (UNSAT) | INDEX props (UNSAT) | JW decisions (SAT) | INDEX decisions (SAT) |
|---|---|---|---|---|---|---|
| 20 | 16 | 77 | 38 | 165 | 10 | 18 |
| 30 | 28 | 188 | 122 | 641 | 12 | 30 |
| 40 | 40 | 312 | 284 | 1,753 | 19 | 78 |
| 50 | 86 | 723 | 1,152 | 8,359 | 26 | 239 |
| 60 | 140 | 1,415 | 2,052 | 16,204 | 27 | 704 |

Work doubles about every **12 variables** under JW and every **6** under INDEX (UNSAT, n = 40–60).

**Estimated budget line n\*** is the n at which the median trace, including restatement and verification, reaches the budget. The UNSAT side needs the whole tree; the SAT side stops at the first solution.

| Branching · style | n\* at 2k | n\* at 8k | n\* at 32k | Share of UNSAT items over 32k at n = 40 / 50 / 60 |
|---|---|---|---|---|
| JW · terse | ≈ 21 | ≈ 49 | ≈ 80 | 0 / 0 / 0 |
| JW · verbose | ≈ 11 | ≈ 27 | **≈ 50** | 0 / 0.52 / 0.92 |
| JW · verbose ×2 | < 10 | ≈ 20 | ≈ 42 | 0.33 / 1.0 / 1.0 |
| INDEX · terse | ≈ 17 | ≈ 31 | ≈ 44 | 0.13 / 0.90 / 1.0 |
| INDEX · verbose | < 10 | ≈ 19 | **≈ 31** | 1.0 / 1.0 / 1.0 |
| INDEX · verbose ×2 | < 10 | ≈ 15 | ≈ 22 | 1.0 / 1.0 / 1.0 |
| SAT side, JW · verbose | < 10 | ≈ 33 | ≈ 70–80 (share over 32k: 0.15 at n = 60, 0.46 at 70) | — |

**Readings.**

- **The ordering rule is worth about three doublings (×8) of budget.** At 32k with verbose traces, n\* is about 31 with INDEX and about 50 with JW. Per-step global scoring, a constant-depth computation (§2.3), buys an exponential saving in search.
- **Budget elasticity.** At these sizes, ×4 of budget adds about +11 to +31 variables to n\*: about +12 under listing-order branching, +16 to +31 under most-constrained-first.
- **SAT/UNSAT asymmetry.** On satisfiable items n\* is roughly 20–30 higher. Above the UNSAT line, an incomplete D answers SAT items correctly while UNSAT items hit the cap and fall to the default, which is the D vertical's E1-H2 prediction.
- Our planned range n ≈ 10–60 brackets most of these values. JW-terse and the SAT side lie above 60, which is why the D vertical's grid needs to run to 72 ({8, …, 72}).

### 3.3 Other domains

- **Colouring (8–40 nodes).**
  - *DSATUR order (C2 inside D):* finding a χ-colouring visits about n nodes with essentially no backtracking (p90 ≤ 1.3n). Proving that χ − 1 colours fail needs a median of 2–9 node visits, p90 ≤ 22 (Sim). With about 30 tokens per node plus an edge check (about 9 tokens per edge), n = 40 costs about 2–3k tokens. **This is far below any budget line.**
  - *Listing order (C1 inside D):* finding a colouring needs a median of 1.1–2.5k nodes at n = 30 and 1.8–2.1·10⁴ at n = 40, with p90 hitting our 10⁶ cap. Refutation needs a median of 0.4–12k nodes at n = 30. At about 30 tokens per node, **n\* ≈ 20–25.**
  - *Caveat:* random G(n, p) graphs at these sizes are easy; small dense subgraphs settle χ. Filtered "hard" items (low greedy score, no small obstructions) will be harder. Re-run `search_costs.py colour` on the actual generator.
- **Entailment (3–12 premises).**
  - A truth table over a atoms costs 2^a rows × (≈ 3a + 3p + 2) tokens (29 tokens measured for a = 6, p = 3). With p ≈ a that is about 2k tokens at a = 6, 13k at a = 8, 29k at a = 9 and 63k at a = 10.
  - Case splitting or DPLL on premises ∧ ¬conclusion costs far less.
  - **For every item type in [V:B4] and [V:B1] except possibly E1L's 20-atom loaded items, exact solving fits 32k.**
- **Knapsack (about 20 items).** DP fits when there are fewer than about 300 reachable sums per stage. With large integer weights it does not, and greedy is forced.
- **TSP (10–14 cities).** Held–Karp needs about n²·2ⁿ ≈ 10⁵–3·10⁶ steps, and brute force is worse [? textbook], so exact search is out of reach. NN costs about n² ≈ 200 distance reads, and each 2-opt pass about 2.5k tokens. **Heuristics are forced**, consistent with the NN openings seen in AlgoTrace [A].

### 3.4 Budget line per family (32k, our sizes)

| Family · member | Dominant cost | Where it crosses 32k |
|---|---|---|
| A, C0, B4 rewrites, I | ≈ 0 steps | Never |
| B1 `UP` to fixpoint | ≤ n propagations × 7–37 | Never (≤ 2.2k at n = 60) |
| B4/C4 `ETR`, `ONL(k)` | premises × 37 × (number of models) | Never at 3–12 premises with few disjunctions |
| C1 / C2 constructive | n steps × 4–40 (+ 8n per step if scores are written) | Never (≤ 15k at n = 40) |
| D `DPLL` (JW order) | §3.2 | UNSAT n ≈ 42–80 (style); SAT ≈ 70–80+ |
| D `DPLL` (listing order) | §3.2 | UNSAT n ≈ 22–44; colouring n ≈ 20–25 |
| F `WALK-k` | flips × 16–47 | SAT median never at n ≤ 60; the p90 tail crosses at n ≈ 40–50. Never answers UNSAT |
| F `WALK-k` writing full re-checks | flips × (47 + 30m) | Already at n ≈ 20 |
| E explicit `WP-t` / `BP-t` | t × 3m × 18–44 (m = 4.26n) | BP-3 at n ≈ 19; BP-2 at n ≈ 28; WP-2 at n ≈ 70; decimation (n steps × one round) at n ≈ 8–12 |
| G `DP-EXACT` | n × R × 5 | R ≈ 300 at n = 20 |
| H `SAMPLE-m` | m × (check cost) | m ≈ 300–500 at 12 premises; m ≈ 6 for SAT at n = 40 if every clause check is written |
| Truth table (entailment) | 2^a × (3a + 3p + 2) | a ≈ 9 atoms |

### 3.5 One-pass dependency depth on our instances (Sim)

**First-fit colouring**, random listing order, median (p90). The longest path is an upper bound; the witness bound is optimistic.

| n | c = 3.0: longest path / witness | c = 4.7 | c = 6.0 |
|---|---|---|---|
| 8 | 4 (5) / 3 | 6 (6) / 4 | 6 (8) / 5 |
| 20 | 5 (7) / 4 | 8 (10) / 4 | 8 (10) / 5 |
| 40 | 6 (8) / 4 | 9 (10) / 5 | 10 (12) / 5 |

**SAT mention-order GREEDY** (α = 4.26), longest path, median (p90): 10 (10) at n = 10; 16 (18) at n = 20; 20 (21) at n = 30; 23 (26) at n = 40; 28 (31) at n = 60.

**Against the level budgets of §2.2** (about 3 layers per level):

- 1P first-fit on random graphs (4–10 levels) is within Qwen3-32B's nominal range (≈ 21 levels; ≈ 10 effective) and Qwen3-14B's (≈ 13; ≈ 6–7).
- It is outside gpt-oss-20b's (≈ 4–8; ≈ 2–4).
- 1P `GREEDY` on SAT (16 levels at n = 20) exceeds every model's effective range beyond n ≈ 10–15, and even Qwen3-32B's nominal range beyond n ≈ 30.
- C vertical E3's gadget depths d ∈ {1..8} will find d\* for gpt-oss but may not reach Qwen3-32B's (P2).

### 3.6 Truncation vs noisy execution

Two accounts of failure predict different things.

- **Noisy execution.** With a per-event slip probability ε, P(correct) ≈ (1 − ε)^E, where E is decisions plus propagations: about 350 events for JW at n = 40 (UNSAT) and about 1,550 at n = 60. ε = 10⁻³ then gives about 70% → 21%: a smooth decline that **does not depend on budget**.
- **Truncation** predicts a threshold that moves with budget (§3.2).

The D vertical's data-collapse test z = log W − β·log T separates the two (β ≈ 1 for truncation, β ≈ 0 for slips). Expressivity theory gives no prior on ε.

---

## 4. Predictions

Each prediction says what theory expects, what would falsify it, and which eval checks it (IDs from [verticals/](../verticals/)). "1P items" means single-token answers with thinking off.

| # | Prediction | Falsified if | Evals |
|---|---|---|---|
| **P1** | **1P composition.** On 1P items, mixture weight concentrates on A, C0, B4 rewrites, `FIXED-PROBE-m` and B1/E with ≤ r\* rounds. C2, D with b > 0, F with k > 0, and latent C1 beyond d\* each get π ≲ 0.05. | Any of C2, D (b > 0) or F (k > 0) gets π > 0.1 on 1P items where it disagrees with every constant-depth member | A_H E1, E2 (direct arms); C E3; D/F E4 DIR arm (in-pass lookahead); B1 E1; E E1-S |
| **P2** | **One-pass ceilings track global attention depth, not capability.** Predicted order of r\*, k\* and d\*: Qwen3-32B > Qwen3-14B > gpt-oss-120b ≥ gpt-oss-20b, with r\*(32B)/r\*(14B) ≈ 1.6 (same width). **On items whose hops are both global (> 128 tokens apart), gpt-oss-120b sits below Qwen3-14B in 1P radius** (≤ 9 vs ≤ 19 rounds), though it may beat it at best effort; on CNF-like items they are about equal (≤ 18 vs ≤ 19). Effective d\* for latent first-fit ≈ 2–4 (gpt-oss-20b), 3–6 (120b), 6–7 (14B), about 10 (32B). | The ceilings order by general capability (e.g. gpt-oss-120b ≥ Qwen3-32B), or show no 14B/32B depth effect | B1 E1 direct-ladder; E E1; C E3. **Design note:** extend C E3 to d ≈ 12–16 and B1/E radii to about 16, or Qwen3-32B's ceiling will be censored |
| **P3** | **gpt-oss is more sensitive to serialisation distance.** When a round's "local" hop spans more than 128 tokens (both hops global), gpt-oss's 1P radius roughly halves; Qwen3's changes much less. | Equal sensitivity across families, or none | E E1 (token placement is already a factor); B1 E1. A cheap added arm: adjacency lists vs shuffled edge lists for colouring |
| **P4** | **Causal-order asymmetry in 1P.** Premises in derivation order reach deeper k\* than reversed order. Giving the prompt twice narrows the gap (Leviathan et al.). In TH the gap shrinks to the order effects of C1/C4 processing. | No forward/reverse difference in 1P, or no effect of repetition | B1 E3 (position × proof order); E E1 (chain order); B4 E1, E3. A cheap added arm: prompt ×2 |
| **P5** | **Chains vs branching in 1P.** On fan-in-1 chains, accuracy decays slowly with depth d (doubling, log-depth). On ladders and trees (fan-in ≥ 2) it falls off at d ≈ k\*. So k\*_chain > k\*_tree. | k\*_chain ≈ k\*_tree | B1 E1 (chain / ladder / tree × d) |
| **P6** | **The budget line fingerprints the branching rule.** At 32k, a model whose D-coded traces branch in listing order has n\*_obs (UNSAT members) ≈ 22–44, and one that branches most-constrained-first ≈ 42–80. Within the band, the coded branching order predicts n\*_obs better than the coded verbosity does. | n\*_obs is unrelated to the coded branching order | D E1 (sweep; τ_W); D E3 (branching by text position) |
| **P7** | **Budget elasticity.** Each ×4 of budget (2k → 8k → 32k) raises n\* by about 11–31 variables: about +12 under listing-order branching, +16 to +31 under most-constrained-first. `NOISY-EXACT`, C and A each predict no shift. | n\* doesn't move with budget (β ≈ 0), or moves in proportion to budget rather than its log | D E1 (β in the data collapse) |
| **P8** | **Colouring at n ≤ 40 is below the line.** At best effort, if traces order vertices most-constrained-first, accuracy is high and nearly flat in n, and the remaining errors are perception or slips (`HALLUC-CONSTRAINT`, `NOISY-EXACT`), not cap hits. If traces use listing order with backtracking, accuracy falls from n ≈ 20–25 and cap hits rise. | Errors at n ≤ 40 at best effort show truncation signatures (cap hits, a default "impossible") although the traces are DSATUR-ordered | C E1, E2, E4, E5; D E6 (colouring arm, edge echo) |
| **P9** | **Entailment at 3–12 premises is below the line, so restriction errors there are not compute-forced.** Moving the budget from 8k to 32k should not change π for B4 or C4 on items with ≤ 8 atoms. Any commission errors at best effort are a learned default [→T2, →T3]. | π_B4 falls substantially with budget on small items. That would be interesting in itself: resource-rational trading of tokens for accuracy | B4 E1, E2, E3 (× budget); B1 E2 |
| **P10** | **In TH, E is implicit.** Explicit sweeps of two or more rounds over all clauses are rare at n ≥ 20. E's weight in TH comes through value choices and guesses at the cap that follow BP-1 marginals rather than `POLARITY`. Where explicit sweeps do occur, rounds per trace scale as 1/m. | Explicit multi-round sweeps are common at n ≥ 40; or value choices follow `POLARITY` as well as BP-1 on the 2-lift and second-order items | E E2, E5, E6; D E1 (answers at the cap) |
| **P11** | **F traces must check internally.** F-coded traces at n ≥ 40 that write full clause checks after each flip hit the cap within about 4–12 flips. Successful F traces don't write full checks, and they produce false "all satisfied" claims at a rate that grows with m. | Successful F traces routinely write full checks at n ≥ 40 | D E6 (verification probe); D E7 |
| **P12** | **Global steps slip more (Arg).** Step-level errors are more frequent for steps that need a global argmax (DSATUR's choice, UC's unit clause, MOMS branching, WalkSAT's violated-clause search) than for local steps (first-fit in a given order, an ETR update), and they grow with n or m. | Slip rates equal across step types | C E2 (DSATUR vs first-fit edits); D E6 |
| **P13** | **DS vs 1P on the same item.** With a full answer written in processing order (DS), C1 weight is high at every n. For the same item asked as a single-token target query (1P), C1 weight falls beyond d\*. | C1 weight equal in DS and 1P at depths beyond d\* | C E3 (LIST vs REV, single value); E E1 (single-token vs full assignment) |
| **P14** | **TSP heuristics are forced.** At n = 10–14 under best effort, tour quality matches NN followed by a few 2-opt passes, not optimal. Optimal tours appear only when NN plus 2-opt is itself optimal. | Optimal tours at a rate well above NN + 2-opt's optimality rate | D/F E7 (TSP seeds); C E1, E2 (TSP arms) |

---

## 5. Open questions and weakest links

**Weakest links, in order.**

1. **Layers per round or level** (≈ 2–3) **and the effective-depth discount** (×½) come from RASP sketches and one measurement study (Csordás et al.). Trained models may be far less efficient. Or they may beat the estimate, by doubling or by superposition: continuous-thought models search a whole frontier at once (Zhu et al. 2025 ✓). Every 1P ceiling in §2.2 inherits this uncertainty, perhaps ×2.
2. **Token cost per search event** (×2–×5 uncertain) shifts n\* by one or two doublings: ±12–24 variables under JW, ±6–12 under INDEX. The ordering-rule effect is robust to this, because it holds at every style in §3.2. Absolute n\* values are not.
3. **Simulated DPLL is not LLM DPLL.** LLMs re-check, restart, give up early, skip propagation or propagate wrongly. Their branching may be smarter than INDEX or dumber than JW, and they don't learn clauses.
4. **Random G(n, p) graphs may be easier** than the project's filtered colouring items. The DSATUR conclusion (P8) needs a re-run on the real generator.
5. **The complexity separations used (F1, F4) are asymptotic and mostly conditional.** At n ≤ 60 they predict *trends* (ceilings that move with depth), not failures at a given n. The only unconditional lower bounds on multi-layer decoders (Chen, Peng & Wu) are a preprint about a specific composition task.
6. **Expressivity is not learnability or choice.** A score of +2 means the member is available. Which available member a model uses is T2's and T3's question.

**Open questions.**

- **Where does real 1P computation happen in our models?** In prompt positions (causal message passing) or at the answer positions (wide-state gathering)? Probes for the k-th derived literal by position and layer would tell ([V:B1] probe plan; [V:E] P2).
- **Do thinking models compute E-implicit marginals inside each step?** Theory allows it, and no evidence exists either way [→T3].
- **Is effective depth the same in thinking mode?** Csordás et al. measured Llama 3.1 and Qwen 3 residual streams on general tasks, not long reasoning traces.
- **Precision of soft messages.** Do bf16 log-odds survive two BP rounds? E E2 (SOFT) tests the behavioural consequence.
- **A theory of per-step slips** (NOISY-EXACT's ε as a function of context length and step globality). Raju & Netrapalli 2026 is a lead [D, ?].
- **Does training make most-constrained-first branching the default?** P6 makes this measurable; the reason is [→T2, →T3].

---

## 6. References

**Verified in this session (✓).**

- Back de Luca, A. & Fountoulakis, K. (2024). *Simulation of Graph Algorithms with Looped Transformers.* ICML 2024, PMLR 235:2319–2363. arXiv 2402.01107. Looped transformers simulate BFS, DFS, Dijkstra and Kosaraju SCC from an adjacency-matrix input, at constant width.
- Chen, L., Peng, B. & Wu, H. (2024). *Theoretical Limitations of Multi-layer Transformer.* arXiv 2412.02975 (preprint; venue not confirmed). An L-layer decoder needs n^Ω(1) width for L-step sequential composition; L vs L+1 layers is an exponential separation; an encoder–decoder separation; a task that CoT makes exponentially easier.
- Chen, X., Chi, R. A., Wang, X. & Zhou, D. (2024). *Premise Order Matters in Reasoning with Large Language Models.* ICML 2024. arXiv 2402.08939. Permuting premises costs over 30%; accuracy is best when premise order follows the proof.
- Csordás, R., Manning, C. D. & Potts, C. (2025). *Do Language Models Use Their Depth Efficiently?* NeurIPS 2025. arXiv 2505.13898. Second-half layers contribute much less; no evidence that deeper models compose more sub-results on multi-hop tasks (Llama 3.1, Qwen 3).
- Fischer, M. & Noever, A. (2018). *Tight Analysis of Parallel Randomized Greedy MIS.* SODA 2018. arXiv 1707.05124. Random-order greedy MIS finishes in O(log n) rounds w.h.p. on any graph.
- Giannou, A., Rajput, S., Sohn, J., Lee, K., Lee, J. D. & Papailiopoulos, D. (2023). *Looped Transformers as Programmable Computers.* ICML 2023, PMLR 202. arXiv 2301.13196.
- Hahn, M. (2020). *Theoretical Limitations of Self-Attention in Neural Sequence Models.* TACL 8:156–171. Self-attention cannot model periodic finite-state languages (e.g. parity) or hierarchical structure unless layers, heads or parameters grow with length. Unconditional for hard attention; under smoothness assumptions for soft attention.
- Hesse, W., Allender, E. & Barrington, D. A. M. (2002). *Uniform constant-depth threshold circuits for division and iterated multiplication.* JCSS 65(4):695–716 (corrigendum 2014). Bibliographic details verified; the theorem is used by its title.
- Kim, J., Nguyen, T. D., Min, S., Cho, S., Lee, M., Lee, H. & Hong, S. (2022). *Pure Transformers are Powerful Graph Learners* (TokenGT). NeurIPS 2022. arXiv 2207.02505. Node and edge tokens with identifiers are at least as expressive as 2-IGN, which exceeds message-passing GNNs.
- Leviathan, Y., Kalman, M. & Matias, Y. (2025). *Prompt Repetition Improves Non-Reasoning LLMs.* arXiv 2512.14982. Gains without reasoning; neutral to slightly positive with reasoning; motivated by causal attention.
- Linial, N. (1992). *Locality in Distributed Graph Algorithms.* SIAM J. Comput. 21(1):193–201. 3-colouring an n-cycle needs Ω(log\* n) rounds.
- Loukas, A. (2020). *What Graph Neural Networks Cannot Learn: Depth vs Width.* ICLR 2020. arXiv 1907.03199. Some problems need depth × width ≥ Ω̃(n^δ), δ ∈ [½, 2].
- Merrill, W. & Sabharwal, A. (2025b). *A Little Depth Goes a Long Way: The Expressive Power of Log-Depth Transformers.* NeurIPS 2025. arXiv 2503.03961. Log-depth uniform transformers express regular-language recognition and graph connectivity, which fixed depth cannot under standard conjectures. Depth scaling is more efficient than width or CoT. (Report A listed this paper as unverified; it is now verified.)
- Peng, B., Narayanan, S. & Papadimitriou, C. (2024). *On Limitations of the Transformer Architecture.* COLM 2024. arXiv 2402.08164. One attention layer cannot reliably compose functions over large domains (communication complexity).
- Sanford, C., Hsu, D. & Telgarsky, M. (2024a). *Transformers, Parallel Computation, and Logarithmic Depth.* ICML 2024, PMLR 235:43276–43327. arXiv 2402.09268. Constant attention layers ↔ constant MPC rounds; k-hop induction heads in about log₂k + 2 layers, with a conditional Ω(log k) lower bound.
- Sanford, C., Fatemi, B., Hall, E., Tsitsulin, A., Kazemi, M., Halcrow, J., Perozzi, B. & Mirrokni, V. (2024b). *Understanding Transformer Reasoning Capabilities via Graph Algorithms.* NeurIPS 2024. arXiv 2405.18512. Hierarchy of retrieval / parallelizable / search tasks. Log depth is necessary and sufficient for connectivity; single-layer, small-width models do retrieval; search tasks need larger width at log depth.
- Strobl, L., Merrill, W., Weiss, G., Chiang, D. & Angluin, D. (2024). *What Formal Languages Can Transformers Express? A Survey.* TACL 12:543–561. Background.
- Xu, K., Li, J., Zhang, M., Du, S. S., Kawarabayashi, K. & Jegelka, S. (2020). *What Can Neural Networks Reason About?* ICLR 2020. Algorithmic alignment; GNNs align with DP. Background for G.
- Yehudai, G., Kaplan, H., Ghandeharioun, A., Geva, M. & Globerson, A. (2024). *When Can Transformers Count to n?* arXiv 2407.15160. Proceedings version UAI 2026 (PMLR 337), with Dar and Rassin added. Counting works by histogram when width ≥ vocabulary.
- Zhu, H., Hao, S., Hu, Z., Jiao, J., Russell, S. & Tian, Y. (2025). *Reasoning by Superposition: A Theoretical Perspective on Chain of Continuous Thought.* NeurIPS 2025 (per mlanthology). arXiv 2505.12514. Continuous thoughts solve reachability in diameter-many steps; the best known discrete-CoT bound is O(n²).
- Model configs: `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `Qwen/Qwen3-14B`, `Qwen/Qwen3-32B` `config.json` on Hugging Face (layer counts, layer types, widths).

**Verified in earlier literature slices** ([A], [D], [F]; claims as stated there): Merrill & Sabharwal 2023 (TACL), 2024 (ICLR), 2025 (padding, NeurIPS); Li, Liu, Zhou & Ma 2024 (ICLR); Feng et al. 2023 (NeurIPS; the no-CoT impossibility and DP with CoT, **not** "CoT stays in P"); Amiri, Huang, Rofin & Hahn 2025 (ICML); Pan, Ganesh, Abernethy, Esposo & Lee 2025 (ICML); Saunshi et al. 2025 (ICLR); Yang et al. 2025 (PENCIL, ICML); Fan, Du, Ramchandran & Lee 2025 (ICLR); Liu, Ash, Goel, Krishnamurthy & Zhang 2023 (ICLR); Ye, Fu, Jia & Sharan 2025; Saparov et al. 2025 (ICLR); Weiss, Goldberg & Yahav 2021; Yang & Chiang 2024 (C-RASP); Zhou, Bradley et al. 2024a (RASP-L, ICLR); Sato, Yamada & Kashima 2019 (NeurIPS); Greenlaw, Hoover & Ruzzo 1991/1995 (compendium); Jones & Laaser 1976; Kasif 1990; Blelloch, Fineman & Shun 2012; Schäffer & Yannakakis 1991; Alekhnovich et al. 2011; Bresler & Huang 2021; Coja-Oghlan 2011; Williams, Gomes & Selman 2003 (backdoors only); Hazra et al. 2025; Heyman & Zylberberg 2025a, b; Sinha et al. 2025/26; Lippl et al. (AlgoTrace).

**Not verified ([?]).**

- 2-SAT is NL-complete; MST is in NC (Borůvka); the Held–Karp DP costs O(n²2ⁿ). Textbook facts, not re-checked.
- Unary subset-sum in TC⁰ (possibly Elberfeld, Jakoby & Tantau).
- Ben-Sasson & Wigderson resolution width (cited via [V:B1]).
- Raju & Netrapalli 2026 (a model of errors in transformers; lead from [D]).
