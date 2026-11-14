# Vertical: I — Cross-formalism re-encoding (does the formalism select the heuristic?)

*One instance, one ground truth, several formalisms. This vertical asks whether the heuristic mix a model uses follows the problem's structure or the formalism it is written in. It owns no heuristic of its own. It owns one feature of the family-I selector π_h(φ): the formalism of the input. It follows [TEMPLATE.md](TEMPLATE.md), expanded like the other verticals.*

- **Status:** designed, v0.1 (2026-11-13). No LLM data. Every prediction, coincidence and yield below was computed by the scripts in [`scripts/cross_formalism/`](../../scripts/cross_formalism/); nothing was worked out by hand.
- **Owner:** [TODO]
- **Companion files:**
  - [I_cross_formalism_questions.md](I_cross_formalism_questions.md): the question library, 81 items in 8 sets, with every member's prediction on every encoding, hypothesis blocks, and item- and set-level likelihood ratios.
  - [`data/examples/I_cross_formalism.jsonl`](../../data/examples/I_cross_formalism.jsonl): the machine-readable copy. It has the fields of the other libraries plus `set_id` (links the encodings of one instance), `encoding`, and `set_disconfirms` (set-level evidence).
  - [`scripts/cross_formalism/`](../../scripts/cross_formalism/): `cf_core.py` (instances, solvers, encodings), `cf_members.py` (member implementations), `cf_other_bases.py` (SAT-native and gadget bases), `build_library.py`, `render_questions_md.py`, `recovery_sim.py`.
- **Phase 1 scope:** behavioural only, open-weight thinking models at best effort (high reasoning effort, 32k-token thinking cap). The first model is gpt-oss-20b, then gpt-oss-120b (both batch, via OpenRouter); Qwen3-14B and Qwen3-32B if those look good. Phase 2 (interpretability) only if Phase 1 finds a formalism effect or translation.
- **Readout: graded.** Every result is a mixture weight π_{h,e} (member h on encoding e; posterior mean and 95% interval), a weight *shift* Δπ_h(e, e′) with its interval, an aggregated home-advantage index (HAI, §2.3) with its interval, a likelihood-ratio test of shared-π against encoding-specific-π, and a faithfulness-weighted trace share. Nothing is a used / not-used verdict. "Disconfirming" a hypothesis means bounding the quantity it predicts (for example, HAI ≤ 0.05, upper 95%).
- **Sign convention (all likelihood ratios in this file and its library):** a **positive log10 likelihood ratio is evidence against that theory**, relative to the theory that predicts the observation best.

---

## 0. Summary

### 0.1 The gap

Each heuristic family has members native to different formalisms. ETR, mental models, `FIRST` and `BICONDITIONAL` live in logic; `DSATUR` and first-fit in graph colouring; unit propagation, DPLL, WalkSAT and belief propagation in CNF. Every existing vertical uses two or more formalisms, but each has a home formalism that carries most items, and framing varies only *within* a formalism (CNF vs English; textbook vs re-themed). No eval presents the *same* instance in several formalisms with the ground truth fixed.

So we cannot yet tell two readings of the project's results apart:

- **Representation-bound heuristics:** the formalism selects the heuristic. Logic invites restriction (B4), graphs invite greedy colouring (C).
- **Structure-bound heuristics:** the heuristic mix follows the problem's structure, whatever it is written in.

DESIGN H4 already states the second reading ("a model's dominant heuristic family is stable across domains linked by reductions"). Zhang, Chen & Chen (2026) report that answers agree on about 75–80% of instances across SAT, vertex-cover and 3D-packing reductions. That is agreement of verdicts. This vertical asks for agreement of *procedure*, measured as mixture weights, with the confounds (length, statement count, order, transparency of the reduction) controlled.

### 0.2 What computing the members showed (read first)

These facts change the design. Each was checked by code (`cf_members.py`, scratch runs recorded in the library build).

1. **On success, the "listing-order" members of three families give the same answer in every formalism.** On 209 colourable random graphs (n = 10, m = 17, k = 3), DPLL in listing order on the graph and DPLL in mention order on the CNF returned the lexicographically first colouring every time. First-fit (C1) succeeded on 90 graphs and equalled it every time. UC-DET (C2: unit clauses first, else the next variable set true) succeeded on 151 and equalled it every time; it rescued 61 of the 119 first-fit dead ends. So "graphs → first-fit, CNF → unit propagation, logic → case-by-case search" are **answer-identical wherever they succeed**. They separate only on dead ends (E4) and in traces.
2. **The classical logic-native restrictions collapse on colouring-derived logic.** `FIRST`, `BICOND` and `ONL(k)` (k ≤ 64, strict) return "the statements are inconsistent" on all 209 colourable graphs; so do the CNF-native `POLARITY` and `GREEDY-MENTION` (they set almost every variable false). In this instance class, "B4 weight rises in the logic encoding" can only show as **excess false IMPOSSIBLE** on colourable items, and at the answer level it is identified only jointly with A1 `ALWAYS-NO` (trace codes split them). B4's non-degenerate members are tested on a logic-native base (E8).
3. **Propagation depth is counted differently.** On 163 precoloured graphs, UP-2t on the CNF derives exactly what WP-t (singleton propagation, the E/B1 boundary member) derives on the graph, for t = 1, 2, 3 (163/163 each); UP-(2t−1) does not (it differs on 93, 62 and 42 of 163). One graph hop costs two clause rounds. A propagation budget fixed in "rounds over statements" reaches half as far in CNF or logic as one fixed in graph hops. This gives E5 a step-accounting test.
4. **Some members are representation-bound: same procedure, same logical content, different answer.** On the B4/C4 E1 disjunction gadget written as a disjunction of conjunctions vs as four clauses (same models, checked):
   - `MATCH-L`, `MATCH-A` and `PRIMACY` endorse the illusory inference in the M cell only in the disjunctive form;
   - **ETR (PyETR 1.0.0) changes in both directions:** on the clausal forms it misses the valid inference in the N cell (omission) and endorses an illusory one in the U cell (commission), neither of which it does on the disjunctive form;
   - `ONL(2)` flips in M, N and U;
   - `FIRST` gives the same answers in all three forms.

   So answers can change across formalisms with the weights fixed. Every member must be computed on every encoding (§1.5), and "the weights moved" must be separated from "the members' own predictions moved".
5. **PyETR does not scale to colouring-derived logic.** n = 5 (40 premises) took 18 s; n = 6, 8 and 10 timed out at 120 s. ETR is `n/c` on the colouring sets and is tested on E8 only.
6. **Equal perception noise is not equal across encodings.** With each statement dropped with probability 0.03, an uncolourable instance gets a false "possible" with probability 0.086 as a graph (22 statements) and 0.343 as CNF or English premises (114 statements). Length effects have a computable, encoding-specific signature.
7. **Lengths (o200k tokens) on the library's E1 bases (n = 12, m = 18):** G ≈ 280, S ≈ 280–295, C ≈ 1,214 (4.3×), L ≈ 2,460–2,540 (8.8–9.1×). Statements: 18 for G and S, 102 for C and L. The padded graph G-PAD matches C within −3.8% / +2.8%; DIMACS is 0.70× C; the named-atom CNF X is 1.40× C. In the reverse-direction set (E7) the graph rendering is the longest (3.2–3.7× C).

### 0.3 Hypotheses

Notation: x is the canonical instance, e an encoding, x_e its rendering. π_{h,e} is the weight of member h on encoding e. A member's prediction on x_e is computed natively if the member is defined on that surface, otherwise by translating through the reduction ("transported"; §1.5). HAI is the home-advantage index (§2.3): the weight that members gain in their home formalism, averaged over identifiable components.

| Hypothesis | Claim | Quantitative prediction (pre-registered) | Nearest competitor and what separates them |
|---|---|---|---|
| **H-structure** | π_{h,e} = π_h for every member and encoding: the mix follows the canonical instance. | Every Δπ_h(e, e′) 90% interval within ±0.05; \|HAI\| ≤ 0.05 (TOST); shared-π model not rejected (bootstrap LRT p > .05; ΔELPD < 2 SE); cross-encoding agreement / retest agreement R ≥ 0.9; no dial effect in E3. | H-translate with τ ≈ 1 makes the same answer-level predictions. Separated by the E3 dial (scrambling should lower τ and shift π under H-translate only) and by trace codes. |
| **H-formalism** | π_{h,e} depends on the input formalism: members gain weight in their home formalism (B4/C4 in logic, C in graphs, UP/DPLL/GUC in CNF). No translation. | HAI ≥ 0.10 with lower 95% > 0.05, also at matched tokens (G-PAD vs C); collapse rate ≥ 0.10 on C/L and ≤ 0.03 on G/S in E4 cell b; τ < 0.2 in traces; legend (HINT) changes π by ≤ 0.05; R ≤ 0.8. | H-length-sel (weights follow length) — separated by G-PAD, DIMACS and the reversed-length set E7. H-surface — separated by the 2 × 2 (formalism × surface) in E1, E4 and E5. |
| **H-translate** | The model re-encodes the input into a working representation (graph, for colouring bases) with probability τ_e, then uses that representation's mix. | τ_C, τ_L ≥ 0.5 (κ-corrected trace codes TR1/TR2 within the first 1,500 thinking tokens); answer–trace association: graph-home responsibility higher in translated traces (odds ratio ≥ 2); π on C/L lies on the segment between the C/L-home and G profiles; E3 dial monotone, Δπ_G-home(HINT − SCRAMBLE) ≥ 0.10. | H-formalism (τ ≈ 0) — separated by traces, the dial, and the transparent-atom encoding X. H-structure — see above. |
| **H-length** (execution) | Encodings differ in accuracy only because longer inputs are executed less reliably: slips and perception errors scale with tokens or statements; π is invariant. | Valid-answer fingerprint distributions equal across encodings (total-variation distance ≤ 0.05); the G → G-PAD accuracy drop ≥ 80% of the G → C drop; error types near-misses and misquotes, not member-specific; in E7 the graph rendering (longest) is least accurate. | H-formalism — separated by fingerprints among *valid* answers (difficulty-free) and by G-PAD. A variant, **H-length-sel**, lets π itself follow length (resource-rational selection); it predicts π(G-PAD) ≈ π(C). |
| **H-surface** | π depends on natural language vs symbols, not on the formalism. | Δπ(S − G) ≈ Δπ(L − C) (difference within ±0.05), each ≥ 0.10; Δπ(C − G) and Δπ(L − S) within ±0.05. | H-formalism — separated by the 2 × 2 in E1, E4 and E5 (S vs L differ in formalism only; G vs S and C vs L in surface only). Not separated by E8, where the two make the same prediction. |

H-structure is the special case of H-length with no length effect on π. H-structure and H-length can both hold: one is about weights, the other about why accuracy differs.

### 0.4 The evals

| ID | Question | Key counterfactual |
|---|---|---|
| **E1** Witness fingerprints | Does *which* valid colouring comes back (the procedure's fingerprint) stay the same across G, S, C and L? | One instance in four encodings, orders matched; six members with pairwise-distinct valid fingerprints. Read among valid answers, so independent of accuracy. |
| **E2** Length ladder | Is the G → C shift (if any) tokens, statement count, or formalism? | G-PAD (tokens only), X (statements of C, labels of G), C-DIMACS (fewer tokens, same clauses). |
| **E3** Translation dial | Does making the reduction visible move π toward the graph profile? | C-SCRAMBLE < C-NEUTRAL < C-HINT; L-NEUTRAL < L-HINT. Headers token-matched. |
| **E4** Dead ends and collapse | Where do false IMPOSSIBLE answers come from in each formalism? | Cells a1 (first-fit dead end that unit propagation rescues), a2 (both dead-end), b (no constructive member fails; only collapse members say IMPOSSIBLE), c / c-twin (uncolourable, and its one-edge colourable twin). |
| **E5** Backbone entailment | Omission (propagation only) vs commission (one-model reading) — does the split depend on formalism? Is propagation depth counted in graph hops or statement rounds? | Cells F-UP, F-CASE, F-CASE-twin (truth flips, encodings fixed), NF-READ. |
| **E6** Crossed order | Is E1's cross-encoding agreement produced by order matching alone? | C and L list vertices in a different order from G; agreement must drop by the computed amount. |
| **E7** Reverse direction | With a SAT-native base, where the graph rendering is longest, do the weights follow formalism or length? | Random 3-SAT as CNF, English switch rules, and a "one vertex per group" graph. Cells r1 / r2 split variable-driven from group-driven construction. |
| **E8** Logic-native gadget | Does B4 weight fall outside logic, beyond what representation-bound members predict? | The B4/C4 E1 gadget as a disjunction of conjunctions, as four English clauses, and as symbolic CNF. English clauses vs symbolic CNF have identical member predictions, so that contrast is a pure weight shift. |

### 0.5 Design principles

- **P1. Ground truth fixed, encoding varied.** Every set is one canonical instance rendered several ways. Ground truth is computed once and checked twice (enumeration and a SAT solver).
- **P2. Predictions computed in every encoding.** Each member's answer is computed natively on each surface where it is defined, and by translating through the reduction elsewhere ("transported"), with the cell flagged. Representation-bound members (fact 4) are therefore handled by the likelihood, not mistaken for weight shifts.
- **P3. A canonical answer space.** Every response is mapped to a colouring of the underlying graph (or IMPOSSIBLE, or YES/NO), so likelihoods are comparable across encodings. The CNF uses the exactly-one direct encoding, so satisfying assignments and colourings are in one-to-one correspondence.
- **P4. Difficulty-free readouts first.** On items with many solutions, *which* valid answer comes back identifies the procedure even when the model is right (the C vertical's P2). Accuracy-based contrasts are secondary and always paired with a length control.
- **P5. Orders matched by default, crossed by design.** Listing order, label order and colour order are the same in every encoding (§1.4); E6 crosses them on purpose.
- **P6. Length decomposed, not ignored.** Tokens (G-PAD, DIMACS), statement count (X) and formalism (X → C) are moved one at a time (E2), and the length direction is reversed with a different base type (E7).
- **P7. Translation measured two ways.** Causally, by a prompt-level dial (E3); observationally, by validated trace codes whose association with the answer is part of the likelihood (§2.5).

### 0.6 Scale and cost

- **Library:** 81 computed items (G 12, S 12, C 18, L 12, plus 27 items in 14 control encodings).
- **Core tier per model:** 5,744 generations, about 52M output tokens and 6.5M input tokens: **$6.00 on gpt-oss-20b (batch), $7.29 on gpt-oss-120b (batch)**. The full tier (twice the bases) is $12.00 / $14.58.
- **Dev batch:** 298 generations, about 2.8M tokens: **$0.29 / $0.35**.
- **Smallest detectable shift at the core tier** (300 bases per encoding in E1; planted-mixture simulation, §2.11): HAI = 0.05 with 85% power, HAI = 0.10 with 100%; about 0.07 for a single member pooled over G+S vs C+L, about 0.10 for a single member between two single encodings. Equivalence at ±0.05 (TOST) has about 0.77 power at this N.
- **Engineering:** about 19 person-days, most of it shared with the C, B1 and B4/C4 verticals (§4).

---

## 1. The class

### 1.1 Defining idea and taxonomy position

- **Family I (strategy selection)** in PAPER_SKELETON Table 4: weights π_h(φ(x)) depend on item features. This vertical makes the *formalism* of the input one of those features and tests whether it carries weight.
- **What "same instance" means.** Two prompts render the same instance if a fixed, size-preserving reduction maps the solutions of one onto the solutions of the other, one to one, and the ground truth is equal. Here: a 3-colouring instance, its exactly-one direct CNF encoding (one Boolean variable per vertex–colour pair; at-least-one, at-most-one and conflict clauses), the same clauses in English, and an exam-timetabling story.
- **Two things can change across encodings, and the design separates them:**
  1. **the member's own prediction** (representation-bound members, fact 4; order-bound members, E6), handled by computing predictions per encoding;
  2. **the selection weights** π_{h,e}, which is what the hypotheses are about.
- **Members are reused, not invented.** The definitions are those of C (`FF-σ`, `LF`, `DSATUR`, `POLARITY`, `GREEDY-σ`, `UC-DET`, `GUC-DET`, `RO-FF`, `GREEDY-CM`), D/F (`DPLL-b`, `MIN-CONFLICTS`, `WALK-k`), B1 (`UP-k`, `DROP-CONSTRAINT`), E (`WP-t` colouring), B4/C4 (`FIRST`, `BICOND`, `MATCH-L/A`, `ETR`, `ONL(k)`), A/H (`ALWAYS-NO`, `ALWAYS-YES`, `PRIMACY`, `RECENCY`, `SAMPLE-m`, `RANDOM`) and the nuisance models. Three group-native members are added for the reverse-direction set E7 (§1.5), as the group-graph forms of C1 and C2.

### 1.2 Encodings

| Code | Formalism | Surface | What it is | Statements (E1 base) | Tokens vs G | What it isolates |
|---|---|---|---|---|---|---|
| **G** | graph (relational) | symbolic | Vertices v10–v99 listed, edge list, "colour with 1, 2, 3" | 18 | 1.0 | Reference |
| **S** | graph (relational) | English | Exams and three slots; clashing pairs listed | 18 | ≈ 1.0 | Surface only (vs G) |
| **C** | CNF (clausal) | symbolic | Direct encoding over opaque x01–x36 | 102 | 4.3 | Formalism + opacity (vs G) |
| **L** | propositional premises | English | C clause for clause: "The Botany exam is in slot 1, slot 2 or slot 3." / "If the Botany exam is in slot 1, then the Chess exam is not in slot 1." | 102 | 8.8–9.1 | Formalism only (vs S: same exams, same slots) |
| G-PAD | graph | symbolic | G with long labels (`v37-amber-cedar-…`) | 18 | ≈ 4.3 (= C ± 4%) | Tokens only |
| X | CNF | symbolic | C with named atoms `v37.1` ("v37 has colour 1") | 102 | 6.1 | Statements of C with G's labels: relational → clausal at fixed vocabulary; X → C is opacity only |
| C-DIMACS | CNF | symbolic | C in DIMACS numbers | 102 | 3.1 | Fewer tokens, same clauses |
| C-SCRAMBLE | CNF | symbolic | C with variable numbers permuted (triples no longer adjacent) | 102 | 4.3 | Harder to see the reduction |
| C-NEUTRAL / C-HINT | CNF | symbolic | C plus a neutral header / a legend naming the reduction (tokens within 1.3%) | 102 | 4.6 | Reduction made explicit |
| L-NEUTRAL / L-HINT | premises | English | L plus a neutral header / a legend ("each 'if A in slot c then B not in slot c' means A and B clash") | 102 | 9.0 | Relational reading made explicit |
| C-XORD / L-XORD | CNF / premises | as C / L | Vertices listed in a different order π′ | 102 | as C / L | Order crossed (E6) |
| L-SW, G-GROUP | premises / graph | English / symbolic | E7: SAT-native base as switch rules / one vertex per group | 24–28 / 236–308 (3m vertices plus the edges) | (vs C) 1.8 / 3.2–3.7 | Reverse length direction |
| L-DNF, L-CNF | premises | English | E8: the gadget as a disjunction of conjunctions / as four clauses | 2 / 5 | ≈ 1 | Form within logic |

**The 2 × 2.** {G, S} × {C, L} crosses formalism (relational vs clausal) with surface (symbols vs English). S and L share their vocabulary exactly (same exam names, "slot 1–3"), so **S vs L is the clean formalism contrast**. G vs C also changes transparency (C's variables are opaque), so the symbolic-row formalism contrast is G vs X (E2) or G vs C-HINT (E3).

**Statement count is part of what the clausal formalism is.** A relational constraint "u ≠ v" over three colours *is* three clauses. Within colouring bases, statement count cannot be separated from the relational → clausal change. It is crossed instead by E7, where the clausal rendering is the short one. E7 uses a different base type, so this crossing is not within-instance (§8).

### 1.3 Why these reductions, and why not knapsack or TSP

- **Colouring ↔ CNF (direct encoding).** Size-preserving (n·k variables, n + n·C(k,2) + m·k clauses), natural (it is the textbook encoding), and solution-preserving one to one with the at-most-one clauses. Without at-most-one clauses the CNF is shorter but a satisfying assignment can give a vertex two colours; `UC-DET` then grabs several colours per vertex and fails. We keep at-most-one in the primary encoding so the canonical answer is unique.
- **CNF ↔ English premises.** One premise per clause, in the same order. The at-least-one clause is rendered as a disjunction, binary negative clauses as conditionals with the earlier-mentioned atom as antecedent. Conditionals give the B4 members (`BICOND`) a surface to act on, matching the B4/C4 vertical's SAT rendering (its E6c). A "not both" rendering is a generator option.
- **Colouring ↔ story.** Exams that share a student need different slots (EHOP's framing). Re-theming within the relational formalism.
- **SAT ↔ group graph (E7).** Karp's SAT → independent-set reduction without the triangle edges: one group of three vertices per clause, an edge between complementary literal occurrences, "pick exactly one vertex per group, no two adjacent". Natural and polynomial, but the graph has 3m vertices and many edges, so it is the longest rendering. That is why it is useful.
- **Knapsack: no size-preserving re-encoding into our formalisms.** Its constraint is arithmetic (Σ w_i x_i ≤ W). CNF needs a pseudo-Boolean encoding (adders or sequential counters, O(n log W) to O(n·W) auxiliary variables and clauses), which is neither small nor natural. English logic cannot state the sum without arithmetic. There is no natural graph form. Knapsack's natural variation is re-theming within one formalism (EHOP), already covered by the C and A/H verticals.
- **TSP: no size-preserving re-encoding either.** As SAT it needs n² position variables and O(n³) clauses for the tour, plus a pseudo-Boolean cost bound. As logic it has no natural rendering. Excluded.

### 1.4 Orders across encodings: matched by default, crossed in E6

**Decision: matched, in every primary set.** In every encoding of an instance:

- the vertex **listing order** π_L equals the **first-mention order** of its atoms (the CNF's at-least-one block and the premises follow π_L);
- the **label order** λ equals the CNF **variable-index order** (variable index = rank of the vertex's label × 3 + colour) and the **alphabetical order** of exam names (names are assigned so that this holds); λ is drawn independently of π_L, as in the C vertical, so listing and label order are decorrelated within every encoding;
- edges and their conflict clauses appear in the same order; colours appear as 1, 2, 3 everywhere.

**Why matched.** Under H-structure, an order-sensitive member (first-fit in listing order, say) should then return the *same canonical answer* in every encoding. Any cross-encoding change in the answer is then a change of member, not a change of order. Matched orders also make each order-source weight (π_LIST vs π_LABEL) comparable across encodings, a structural parameter whose invariance H-structure predicts.

**Why also crossed (E6).** Matching could manufacture agreement: two encodings could agree because both expose the same order, not because the model runs the same procedure. E6 gives C and L a different vertex order π′ on the same instance. Order-dependent members then predict different canonical answers from G's, order-free ones do not, and the expected drop in cross-encoding agreement is computable from the fitted weights (§2.6, E6). Matched order is primary because it is the condition under which invariance of π is testable from answers; crossing is the check that it was not produced by matching.

### 1.5 Members, and how each is predicted on each encoding

"Native" = the member is defined on that surface and computed there. "Transported" (ᵗ in the library) = the member is not defined on that surface; its prediction is computed by translating the input to its home formalism, applying it there with the encoding's own orders, and mapping the answer back. A transported prediction is exactly what H-translate says the model produces.

| Member (family) | Home | G, S, G-PAD | C, X, C-DIMACS, C-SCRAMBLE, C-NEUTRAL, C-HINT | L, L-NEUTRAL, L-HINT | Notes |
|---|---|---|---|---|---|
| `FF-LIST`, `FF-LIST-INFEAS`, `FF-LABEL`, `LF` (C1); `DSATUR` (C2); `RO-FF` (C3) | graph | native | transported (vertex order = first mention; label order = index order) | transported (label order = alphabetical) | Under C-SCRAMBLE, "label order" in the CNF is the scrambled index order; `FF-LABEL` transported is then undefined (n.a.) and the native INDEX members carry the label-order hypothesis. |
| `DPLL-LIST`, `DPLL-DSATUR`, `DPLL-LIST-b12` (D) | graph | native (forward checking) | transported | transported | |
| `DROP-LAST-1` (B1) | graph | native | transported | transported | Dropping the last *statement* in C/L removes one colour of the last edge. With no precolouring this gives the same answer as dropping the edge (colour symmetry); not separable here. |
| `MIN-CONFLICTS` (F) | graph | native | transported | transported | Distributional (Monte Carlo). |
| `WP-t` colouring (E/B1) | graph | native | transported | transported | WP-t ≡ UP-2t on C/L (fact 3). |
| `FF-LIST-READ`, `DSATUR-READ`, `FF-CM` (C1/C2, entailment) | graph | native | transported | transported | READ: build one colouring and read the query off it. CM: try to build a counter-example greedily; answer YES if that fails. |
| `POLARITY` (C0), `GREEDY-MENTION` (C1), `UC-DET`, `UC-DET-INDEX`, `GUC-DET` (C2) | CNF | transported (via the canonical CNF) | native | native (the premises are the clauses in English) | `POLARITY` and `GREEDY` collapse to IMPOSSIBLE on these CNFs. |
| `DPLL-MENTION`, `DPLL-INDEX`, `DPLL-OCC`, `DPLL-MENTION-b24` (D) | CNF | transported | native | native | Budget units differ: b counts Boolean decisions in CNF and vertex decisions on the graph. |
| `UP-k` (B1), `UC-READ`, `UC-CM`, `GREEDY-CM` (entailment) | CNF | transported | native | native | `GREEDY-CM` answers YES on every E5 item (its greedy never finds a model of these CNFs). |
| `WALK-k` (F) | CNF | transported | native | native | Distributional. |
| `FIRST` (B4) | logic | transported via L | native, clause form (every clause is a disjunction) | native (only the at-least-one premises are disjunctions) | Collapses on colouring sets; non-degenerate on E8. |
| `BICOND` (B4) | logic | transported via L | transported via L (clauses have no direction) | native | Collapses on colouring sets (the at-most-one conditionals alone become contradictory). |
| `ONL(k)` (C4) | logic | transported via L | native, clause form (alternatives = literals) | native (alternatives of "if a then not b" = {a, not b} and {not a}) | Representation-bound: on E5's F-UP item `ONL(1)` says NO on C and YES on L. |
| `MATCH-L`, `MATCH-A` (B4), `PRIMACY`, `RECENCY` (A2) | logic | n.a. | native (E8) | native (E8) | Representation-bound on E8 (fact 4). |
| `ETR` (B4/C4) | logic | n.a. | native (E8) | native (E8) | PyETR 1.0.0; `n/c` on colouring sets (fact 5). |
| `EXACT`, `ALWAYS-NO`, `ALWAYS-YES`, `RANDOM`, `SAMPLE-m`, `PERCEPTION-NOISE` | any | native | native | native | `PERCEPTION-NOISE` drops each *statement* with a fixed rate, so its prediction differs by encoding (fact 6). |
| **Added for E7:** `PICK-FIRST` (C1), `PICK-MINDEG` (C1, static score), `MCG` (C2, most-constrained group) | group graph | native on G-GROUP | transported (clause-order forms) | transported | `PICK-FIRST` in clause terms: for each clause in order, make true its first literal not contradicting earlier choices. `MCG` coincides with `GUC-DET` on both E7 cells. |

**How "n.a." and "n/c" cells enter the likelihood.** A member with an n.a. or n/c cell on encoding e is not a component of e's mixture (π_{h,e} ≡ 0 by construction). The shared-π model (H-structure) is defined on the members available in every compared encoding; members available only on some surfaces are tested separately (their total weight must be ≤ 0.05 everywhere under H-structure, since a structure-driven procedure cannot depend on a surface that other encodings lack). Transported cells are full components: under H-structure and H-translate they carry weight; under H-formalism they should not.

### 1.6 Coincidences, collapses and what each set can identify

| Coincidence (computed) | Where | Consequence | Broken by |
|---|---|---|---|
| `FF-LIST` ≡ `UC-DET` ≡ `DPLL-LIST` ≡ `DPLL-MENTION` ≡ lexicographically first colouring ("LIST family") | Every item where they succeed | Their weights are identified only jointly on E1 | E4 cells a1 (FF dead end, UC rescues) and a2; traces (backtracking, forced moves) |
| `FF-LABEL` ≡ `UC-DET-INDEX` ≡ `DPLL-INDEX` ("LABEL family") | Success items, natural numbering | Label-order weight is one component | C-SCRAMBLE (index order no longer = label order) |
| `DSATUR` ≡ `DPLL-DSATUR` | Whenever DSATUR succeeds (304/304) | One component | Dead-end items for DSATUR (rare at our sizes) |
| `POLARITY` ≡ `GREEDY-MENTION` ≡ `FIRST` ≡ `BICOND` ≡ `ONL(k ≤ 64)` ≡ `ALWAYS-NO` ("collapse") | Every colourable colouring item | One "collapse" component at the answer level | Trace codes (K3 COMMIT, K5 CONVERSE, polarity counting); E8 for B4 proper |
| `UP-2t` ≡ `WP-t` | Every precoloured item | Propagation depth has two scales | Fitting the depth on both scales (E5) |
| `MCG` ≡ `GUC-DET`; on the two E7 cells also ≡ `PICK-FIRST` | E7 cells r1, r2 | E7 separates clause/group-driven from variable-driven construction, not the members within each | More E7 cells (generator option) |
| `DROP-LAST-1` by edge ≡ by statement | No precolouring | Not separable here | Precoloured items (colour symmetry broken) |
| `GREEDY-CM` ≡ `ALWAYS-YES` | All E5 items | One component | E8 (GREEDY-CM is non-degenerate there) |

### 1.7 Expressibility and RASP-L sketch (written before data)

- **The selector feature is cheap.** Recognising the formalism (clause brackets and "∨"/"¬" vs "vertex"/"edge" vs English connectives) is a bag-of-tokens feature: about 2 primitives, 1 layer. So formalism *can* drive selection at no depth cost.
- **Translation of the direct encoding is constant-depth at fixed format.** A RASP-L outline from C to a graph: (1) for each variable occurrence, select the at-least-one clause containing that variable and aggregate its index → vertex identity (2 primitives, 1 layer); (2) colour = position within that clause (`selector_width` over earlier literals; 1 primitive); (3) for each binary clause, map both literals to vertex identities and emit the pair as an edge (2–3 primitives, 1–2 layers). About 6 primitives, 3 layers. It does not need index adjacency, so **scrambling the variable numbers should not change translatability for this program**.
- **Pre-registered predictions (R-I1, R-I2).**
  - R-I1: if the model does not translate (τ ≈ 0), it is not because translation is deep; the cheap program exists.
  - R-I2: if C-SCRAMBLE lowers τ, the model relies on the surface cue of adjacent variable numbers, not on clause membership.
- Member programs are as in their own verticals (AR-FF 7 primitives; POLARITY 3; UC 10).

---

## 2. Behavioural evidence (Phase 1)

### 2.1 Conditions, models, sizes

- **BE (primary).** Thinking on at the highest effort; 32,768 thinking tokens plus 2,048 answer tokens; model-card sampling. A run that reaches the cap gets the end-of-thinking token and `ANSWER:`; it is marked censored and analysed as censored (SCOPE rule 2).
- **Models, in run order:** gpt-oss-20b (high), gpt-oss-120b (high), both batch; then Qwen3-14B and Qwen3-32B (thinking) if the first two look informative. Check that each provider returns reasoning text before any run (SCOPE §1); traces are required for H-translate.
- **Samples.** One per item, plus a second on a fixed 20% subset of E1 (the retest agreement for R).
- **Sizes.** The library uses n = 12 (E1, E4), n = 10 (E5), n = 8 variables (E7). The dev batch calibrates n so that gpt-oss-20b scores 40–80% on the hardest cell, which will be C or L (SCOPE rule 1). The same n is then used for every encoding of a set: the instance is fixed, and only the encoding varies. If C or L truncates in more than 50% of runs at the calibrated n, n is lowered for the whole set, never for one encoding.
- **Diagnostic only:** gpt-oss LOW effort and Qwen3 non-thinking on E1 and E3, to ask whether translation needs thinking (R-I1). Not budgeted in the core tier.

### 2.2 The model: encoding → working representation → member

Each response on encoding e is generated in two stages.

1. **Working representation** r ∈ {graph, clausal, premise-by-premise}. P(r = own(e) | e) = 1 − τ_e; P(r = graph | e) = τ_e for e ≠ G, S. (The target is estimated, not assumed: for colouring bases graph is the expected target; E7 asks whether a SAT-native base is translated the other way.)
2. **Member choice** given r: π_h(r, φ), with φ the pre-registered item features (n, density, solution count, log tokens, log statements, cell).

The response likelihood is

P(ȳ | x_e) = Σ_r P(r | e) · Σ_h π_h(r, φ) · P(ȳ | h, x_e^{(r)}) + π_∅ · q(ȳ | x_e),

where ȳ is the response mapped to the canonical space, x_e^{(r)} means "the encoding itself" if r = own(e) and "the translated instance with the encoding's own orders" otherwise, q is the none-of-the-above term, and P(ȳ | h, ·) uses a near-miss slip kernel with a slip rate ε_e estimated **per encoding** (SCOPE rule 3).

A trace code T ("translated": TR1 or TR2 within the first 1,500 thinking tokens; §2.5) is a noisy indicator of r: P(T = 1 | r ≠ own) = sensitivity, P(T = 1 | r = own) = false-positive rate, both fixed from hand-label validation. The joint likelihood multiplies in P(T | r), tempered by the model's measured trace faithfulness (as in the other verticals).

**The hypotheses as constraints on this model:**

| Hypothesis | Constraint |
|---|---|
| H-structure | π_h(r, φ) does not depend on r, and φ has no formalism, token or statement terms. Then π_{h,e} is the same for every e, and τ_e is unidentified from answers (identified only from traces). |
| H-formalism | τ_e = 0 for every e; π_h(r, φ) depends on r. |
| H-translate | τ_e > 0 for e ≠ G, S; π_h(r, φ) depends on r. π on e is the τ-mixture of the native and graph profiles, so it lies on the segment between them. |
| H-length (execution) | π independent of r and e; ε_e (and the perception-noise rate) a function of tokens / statements only. |
| H-length-sel | π depends on e only through log tokens and log statements. |
| H-surface | π depends on e only through a surface indicator (English vs symbolic). |

### 2.3 Estimands, tests and weight statements (pre-registered)

| Estimand | Definition | Reported as |
|---|---|---|
| π_{h,e} | Mixture weight of h on encoding e (hierarchical fit, base random effects, model random effects) | Posterior mean, 95% interval |
| Δπ_h(e, e′) | π_{h,e} − π_{h,e′}, paired over bases | Mean, 95% interval; TOST at ±0.05 for equivalence |
| **HAI** | ½ [ Σ_{h ∈ C/L-home} (π̄_{h,CL} − π̄_{h,GS}) + Σ_{h ∈ G-home} (π̄_{h,GS} − π̄_{h,CL}) ], with π̄ the mean over the two encodings named. Only components identifiable on the item set enter (on E1: G-home = {DSATUR, LF}; C/L-home = {GUC-DET, DPLL-OCC, collapse}). | Mean, 95% interval (base bootstrap; posterior in the full fit) |
| Omnibus invariance test | 2 Δlog L between encoding-specific π and shared π; null distribution by parametric bootstrap from the shared fit (the χ² reference is invalid at weight boundaries) | p-value; ΔELPD (K-fold by base) with SE |
| Agreement ratio R | A_cross(e, e′) / √(A_retest(e)·A_retest(e′)); A = probability two canonical answers on the same base are identical | Mean, 95% interval. R = 1 in expectation under H-structure whether the strategy is drawn per response or fixed per instance (Davis-Stober & Brown's S2 and S1) |
| Fingerprint distance | Total-variation distance between encodings' distributions over fingerprint classes {LIST, LABEL, DSATUR, LF, GUC, OCC, other valid}, among valid answers | Mean, 95% interval |
| τ_e | Translation rate, κ-corrected (§2.5) | Rate, 95% interval |
| Answer–trace association | Log odds ratio of a graph-home answer given T = 1 vs T = 0 | Mean, 95% interval |
| Cell contrasts (E4, E5) | Differences of response rates between cells, per encoding, and their encoding differences | Δ with 95% interval |

**Weight statements replace pass/fail**, as in the other verticals: "π_h = x [lo, hi]", "the evidence moves weight from G-home to C-home members by HAI = x [lo, hi]", "this set bounds |HAI| ≤ u".

**Multiplicity.** Three primary quantities per model: HAI (E1), the dial slope (E3), and the collapse-rate contrast (E4 cell b). Everything else is secondary and reported with its interval.

### 2.4 Predicted signatures and manipulation table

**Predicted error signatures per hypothesis.**

- H-structure: the same mix of failure forms on every encoding (FF dead ends, collapse, near-misses), after each member's native prediction is applied.
- H-formalism: excess false IMPOSSIBLE (collapse) on C/L only; FF dead ends on G/S only; on E5, more omission on L/C and more commission on G/S.
- H-translate: failure forms on C/L are a τ-mixture of the G/S forms and the C/L-home forms, and the mixture component is predicted by the trace code.
- H-length: errors are near-misses and misquotes whose rate grows with tokens at the same per-statement rate in every encoding; fingerprints among valid answers unchanged.

| Manipulation | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| Re-encoded (G → S → C → L), orders matched | π unchanged | π moves to home members | π moves by τ·(G profile − home profile) | accuracy falls with tokens; π unchanged | moves only between symbolic and English |
| Tokens added (G → G-PAD) | = | = | = | accuracy falls as for G → C | = |
| Statements expanded, labels kept (G → X) | = | moves to CNF-home | ≈ G (atoms transparent, τ_X high) | falls with tokens | = |
| Notation compressed (C → C-DIMACS) | = | = | = | accuracy rises | = |
| Reduction named (C-NEUTRAL → C-HINT) | = | = (≤ 0.05) | moves to G profile | = | = |
| Variable numbers scrambled (C → C-SCRAMBLE) | = (INDEX members' predictions change, computed) | = | moves away from G profile if τ falls | = | = |
| Vertex order crossed (E6) | agreement drops by the computed amount | same | translated traces use the encoding's own order | = | = |
| Thinking budget lowered (diagnostic) | — | — | τ falls if translation needs thinking (R-I1 predicts not) | accuracy falls | — |

**Process measures.** Thinking tokens per encoding (expected C, L > G, S); token offset of the first translation event; share of trace content words from each formalism's lexicon over trace windows (§2.5); the truncation rate per cell.

### 2.5 Chain-of-thought hypotheses, trace coding, faithfulness, and how trace and answer evidence combine

**Translation codes (new, this vertical).**

| Code | What it records | Extraction |
|---|---|---|
| TR1 RECOGNISE | The trace names the reduction or the target formalism ("this is graph 3-colouring", "each exam is a vertex", "x01–x03 are the three colours of one vertex") | LLM coder + pattern list |
| TR2 REBUILD | The trace writes out the target structure: a neighbour list, an edge list, a per-vertex table of colours | Parser (edge pairs checked against the instance) + LLM coder |
| TR3 LEXICON SHARE | Share of coded content words from the graph lexicon {vertex, node, neighbour, adjacent, edge, colour, degree}, the clause lexicon {clause, literal, variable, unit, satisfied, propagate, assignment} and the premise lexicon {statement, premise, follows, suppose, case}, per 500-token window | Automatic (whole-word counts; encoding-native words such as "slot" in S/L are excluded from all lexicons) |
| TR4 BACK-MAP | The answer is mapped back from the working representation to the encoding's own terms | LLM coder |

The "translated" indicator T = 1 iff TR1 or TR2 occurs within the first 1,500 thinking tokens. The translation rate is reported κ-corrected: τ̂ = (share of traces with T = 1 − f) / (s − f), where s and f are the coder's sensitivity and false-positive rate for T on the hand labels. Member codes (commitment order, revisions, dead ends, forced moves, case splits, K3 COMMIT, K5 CONVERSE, K11 misquotes) are those of the C, B1, D/F and B4/C4 verticals.

**Pre-registered CoT predictions (also in every item's hypothesis block).**

- H-translate: T = 1 on ≥ 50% of C and L traces; graph-lexicon share ≥ 0.6 after the translation event; TR4 before the answer.
- H-formalism: T = 1 on < 20%; TR3 dominated by the encoding's own lexicon; member codes are those of the home formalism (forced moves and clause references on C; "suppose" and premise numbers on L; neighbour colours on G/S).
- H-structure: no requirement on vocabulary; the commitment pattern mapped to the canonical instance is the same member's across the encodings of a set.
- H-length: K11 misquote rate per statement equal across encodings at matched tokens.
- E8: under H-translate, C traces rewrite the clauses as cases ("either the box is red and heavy, or …") before answering.

**Coding pipeline and validation.** As in the other verticals: an automatic parser for TR2 and TR3, a pinned LLM coder outside the evaluated panel for TR1 and TR4 (blind to encoding, cell, ground truth and predictions; it sees the trace with encoding-identifying words masked where possible), 200 hand-labelled traces stratified by encoding and model, two human coders. **Codes with LLM–human κ < 0.7 are dropped from inference** and reported descriptively. The coder's sensitivity and false-positive rate for T, measured on the hand labels, enter the likelihood as P(T | r).

**Faithfulness.** Measured per model as elsewhere (final-state consistency; early answering on 100 traces per model by truncating at 25/50/75% of the trace). The trace term is tempered by the measured faithfulness. Every result is reported twice: answers only, and answers plus traces.

**Combination rules (pre-registered).**

1. Answers are primary. π_{h,e} comes from the answer-only fit; traces can split τ from π and narrow intervals, never create weight answers do not support.
2. τ is reported from traces alone (κ-corrected), and also from the joint model. If they disagree by more than 0.15, report both and do not use the joint estimate.
3. If T = 1 traces show graph-home answers no more often than T = 0 traces (log OR interval includes 0), translation is reported as "verbal only": the trace names the reduction without changing the procedure.
4. Post-treatment caution: T is observed after the encoding, so "π given T" is a description of the latent-state model, not a causal estimate. The causal estimate of translation's effect is the E3 dial.

### 2.5a Confounds and how each is controlled

| Confound | Why it matters | Control |
|---|---|---|
| **Token length** (C ≈ 4.3× G, L ≈ 9× G) | Longer inputs fail more and may shift selection (resource-rational) | G-PAD (tokens matched to C within ±4%, same statements); C-DIMACS (0.70× C, same clauses); log tokens in the selector; E7 reverses the direction |
| **Statement count** (102 vs 18) | Inherent to the clausal formalism (one relational constraint = k clauses) | X keeps statements and changes vocabulary; E7 reverses it; reported as non-separable within colouring bases (§8) |
| **Transparency of the reduction** | Opaque C hides the structure; L's atoms show it | X (named atoms), C-HINT (legend), C-SCRAMBLE (hidden grouping); S vs L as the clean formalism contrast |
| **Listing / label / colour order** | Order-dependent members follow surface order | Matched in every primary set; λ decorrelated from π_L; crossed in E6 |
| **Answer format** | G/S/L request one line per vertex in listing order; C requests the set of true variables | Matched where the formalism allows; C's free-order answer means C1's "answer-order" member (FF-OUT) is undefined on C; FF-OUT is only a diagnostic member here |
| **Difficulty-driven strategy shift** | A harder-looking encoding may change the strategy for reasons other than formalism | Fingerprints among valid answers; G-PAD; per-encoding slips; H-length-sel as an explicit competitor |
| **Differential truncation** | C/L truncate more; completed C/L answers then come from easier instances | Censoring model; truncation rate per cell; sizes calibrated on C/L and shared across encodings; sensitivity analysis on bases complete in all four encodings |
| **Vocabulary leak** | "slot" and exam names in S and L, "vertex" in X and C-HINT, can cue the reduction | Lexicons for TR3 exclude encoding-native words; S vs L share vocabulary exactly |
| **Perception noise differs by encoding** (fact 6) | More statements → more misreads → errors that look like members | `PERCEPTION-NOISE` computed per encoding as a component; K11 misquote codes |
| **Tokenizer** | Token counts differ by model family | o200k for gpt-oss (measured); Qwen3 counts measured at run time and logged; label token counts equal within each encoding (asserted, as in C) |
| **Memorisation of the direct encoding** | Models may know "this pattern is colouring" | That is what H-translate is about; C-SCRAMBLE and X probe it |

### 2.6 The evals

Every set below exists in the library with every member's prediction on every encoding, item-level likelihood ratios and set-level likelihood ratios. The numbers in the "set-level evidence" lines are log10 LRs under the library's illustrative reference profiles (`build_library.py`), per instance set, positive = against; they show the direction and rough size of what one set contributes, not results.

#### E1. Witness fingerprints across four formalisms (primary)

- **Question.** Among valid answers, does the distribution over fingerprints (LIST, LABEL, DSATUR, LF, GUC, OCC, other valid) stay the same across G, S, C and L?
- **Design.** Bases: 3-colourable graphs, n = 12, m = 18 in the library (study n calibrated, 12–16). Filter: ≥ 20 colour partitions; the six fingerprints valid and pairwise distinct; `FF-LIST`, `FF-LABEL` and `UC-DET` all succeed (so each family's fingerprint is one valid answer). Each base in G, S, C, L, orders matched. Same answer format family (a witness or IMPOSSIBLE).
- **Computed cell predictions (all three library bases):** LIST family (`FF-LIST`, `UC-DET`, `DPLL-LIST`, `DPLL-MENTION`, `DROP-LAST-1`) one fingerprint; LABEL family (`FF-LABEL`, `UC-DET-INDEX`, `DPLL-INDEX`) another; `DSATUR` (= `DPLL-DSATUR`), `LF`, `GUC-DET`, `DPLL-OCC` one each; collapse members IMPOSSIBLE; `EXACT` uniform over 38–92 partitions; `MIN-CONFLICTS`, `WALK`, `RO-FF` distributions. The canonical prediction of every member is the same in all four encodings (matched orders): any change in the answer distribution is a change of weights.
- **Hypotheses and thresholds.** H-structure: every Δπ within ±0.05, |HAI| ≤ 0.05, R ≥ 0.9, fingerprint distance ≤ 0.05. H-formalism: HAI ≥ 0.10 (lower 95% > 0.05), R ≤ 0.8. H-translate: π on C/L on the segment toward G, answer–trace association OR ≥ 2. H-length: fingerprint distance ≤ 0.05 even where accuracy differs. H-surface: Δπ(S − G) ≈ Δπ(L − C), each ≥ 0.10.
- **CoT.** Per member as in C (commitment order τ with listing order ≥ 0.8 for LIST; "most constrained" mentions for DSATUR; "shortest clause" choices for GUC); per hypothesis as in §2.5.
- **Set-level evidence (one base, four responses).** "DSATUR in G and S, GUC-DET in C and L" is 1.1–1.2 log10 against H-structure and 1.5 against H-length; "DSATUR in all four" is 1.2–1.3 against H-formalism; "valid in G and S, IMPOSSIBLE in C and L" is 1.2 against H-structure.
- **Evidence for / against.** Supports H-formalism and disconfirms H-structure and H-length when fingerprints shift toward home members; supports H-structure (and bounds HAI) when they do not. Cannot separate H-structure from H-translate with τ ≈ 1 (E3 does).
- **Power (§2.11).** 300 bases per encoding: HAI 95% half-width ≈ 0.035; detects HAI = 0.05 with 85% power.

#### E2. Length ladder

- **Question.** Is any G → C difference a token effect, a statement-count effect, or a formalism effect?
- **Design.** On E1 bases: G-PAD (long labels, tokens matched to C: 1,168 and 1,248 vs 1,214), X (C's 102 clauses with atoms `v37.1`; 1,699 tokens), C-DIMACS (855 tokens). G and C come from E1 (same bases).
- **Computed predictions.** Every member's canonical prediction is identical across G, G-PAD, X, C-DIMACS and C on these bases (no representation-bound member changes); the ladder moves only length, statements and notation.
- **Hypotheses and thresholds.**
  - H-length (execution): accuracy drop G → G-PAD ≥ 80% of G → C; π equal on all five.
  - H-length-sel: π(G-PAD) ≈ π(C) (within ±0.05) and ≠ π(G).
  - H-formalism: π(G-PAD) ≈ π(G); π(X) ≈ π(C) ≈ π(C-DIMACS); the shift happens at G → X.
  - H-translate: π(X) ≈ π(G) (named atoms make translation easy: τ_X ≥ 0.8); π(C-DIMACS) ≈ π(C).
- **Evidence for / against.** The G-PAD arm is the main disconfirmer of H-length and H-length-sel against H-formalism; X separates H-formalism from H-translate (same formalism as C, transparent like G).

#### E3. Translation dial

- **Question.** Does making the reduction visible (or hiding it) move π, and does the measured translation rate predict the move?
- **Design.** On E1 bases: C-SCRAMBLE (variable numbers permuted; clause order kept), C-NEUTRAL (neutral header), C-HINT (legend, tokens +1.3% vs neutral), L-NEUTRAL, L-HINT (+0.6%). E1's C and L are the no-header baselines.
- **Computed predictions.** Under C-SCRAMBLE, the INDEX-order members (`UC-DET-INDEX`, `DPLL-INDEX`) get a new fingerprint (index order is no longer label order); all mention-order and order-free members are unchanged.
- **Hypotheses and thresholds.** H-translate: graph-home weight monotone SCRAMBLE < NEUTRAL < HINT, Δπ_G-home(HINT − SCRAMBLE) ≥ 0.10, and the change in τ predicts the change in π (fitted slope within 0.5–2× of the latent model's prediction). H-formalism: no dial effect (|Δ| ≤ 0.05) while C/L still differ from G. H-structure: no dial effect and no difference from G. H-length: HINT = NEUTRAL (token-matched).
- **Evidence for / against.** The only *causal* test of translation. Disconfirms H-translate if the dial does nothing while traces show translation (then translation is verbal only). Disconfirms H-formalism if HINT moves π. R-I2 (§1.7) is tested by SCRAMBLE.

#### E4. Feasibility near the threshold: dead ends and collapse

- **Question.** Which members produce false IMPOSSIBLE (and false "possible") in each formalism?
- **Design.** n = 12, m ∈ {22, 24, 26}. Cells selected on computed member signatures (yields per 3,000 draws: a1 405, a2 349, b 241, c 275):

| Cell | Truth | Computed false-IMPOSSIBLE sources | Other signatures |
|---|---|---|---|
| a1 | colourable | `FF-LIST`, `FF-LABEL`, `UC-DET-INDEX`, collapse, A1 | `UC-DET` and `DSATUR` succeed (unit propagation rescues the first-fit dead end) |
| a2 | colourable (unique partition) | `FF-LIST`, `FF-LABEL`, `LF`, `UC-DET`, collapse, A1 | `DSATUR`, DPLL, `GUC-DET` succeed |
| b | colourable | collapse, A1 only | every constructive member succeeds |
| c | not colourable | every member except `DROP-LAST-1` and `FF-LIST-INFEAS` (both "possible" with an invalid witness) | `PERCEPTION-NOISE` (3% per statement): false "possible" 0.086 on G/S, 0.343 on C/L |
| c-twin | colourable (c minus its last edge) | `FF-LABEL`, collapse, A1 | truth flips with one edge, encoding fixed |

- **Contrasts.** Cell b isolates the collapse rate (B4/C0 restriction plus A1) per encoding. (a1 − b) isolates the first-fit dead-end weight; (a2 − a1) the unit-propagation and LF dead-end weight. Each contrast is compared across encodings.
- **Hypotheses and thresholds.** H-formalism: collapse ≥ 0.10 on C/L and ≤ 0.03 on G/S; (a1 − b) larger on G/S than C/L by ≥ 0.10. H-structure: every contrast equal across encodings (±0.05). H-translate: the C/L pattern is the τ-mixture, collapse answers concentrated in untranslated traces. H-length: no cell × encoding interaction beyond `PERCEPTION-NOISE`'s computed one.
- **CoT.** Collapse members: K3 COMMIT to slot 1 / "first option" (FIRST), K5 CONVERSE (BICOND), polarity counting (POLARITY), contradiction at the first conflict rule (ONL). First-fit: dead-end declaration without revision. D: chronological backtracking.
- **Set-level evidence.** On cell b, "valid in G and S, IMPOSSIBLE in C and L" is 1.2 log10 against H-structure and 1.3 against H-length; "invalid colouring in all four" is 0.9–1.3 against every hypothesis except H-length.
- **Evidence for / against.** The set where "B4 weight rises in logic" can show for colouring bases (as collapse on L), separated from A1 by traces only (§8).

#### E5. Backbone entailment: omission vs commission

- **Question.** "In every valid colouring that keeps the fixed colours, does w have colour c?" (G); "Is x23 true in every satisfying assignment?" (C); "Does it follow that the Botany exam is in slot 3?" (L). Does the split between propagation-only reasoning (omission) and one-model reading (commission) depend on the formalism? Is propagation depth counted in graph hops or in statement rounds?
- **Design.** n = 10, m ∈ {14, 15, 16}, two precoloured vertices (colours 1 and 2), query (w, c). Cells (yields per 3,000 draws, as query candidates: F-UP 5,096; F-CASE 1,717; NF-READ 12,034):

| Cell | Truth | YES | NO |
|---|---|---|---|
| F-UP (two graph hops) | YES | EXACT, `WP-2`, `WP-inf`, `UP-4`, `UP-inf`, READ and CM members, `ALWAYS-YES`; `ONL(1)`/`ONL(8)` on G, S, L (premise form) | `WP-1` = `UP-2`, `UP-3`, collapse, `ALWAYS-NO`; `ONL(1)`/`ONL(8)` on C (clause form: representation-bound) |
| F-CASE (forced only by case analysis) | YES | EXACT, `DSATUR-READ`, `FF-CM`, `UC-READ`, `UC-CM`, `GREEDY-CM`, `SAMPLE-3` (1.0) | every propagation member (`WP-*`, `UP-*`): **omission**; `FF-LIST-READ`; ONL; collapse |
| F-CASE-twin (one edge removed) | NO | `FF-CM`, `UC-READ`, `GREEDY-CM`, `ALWAYS-YES`: **commission**; `SAMPLE-3` 0.30 | EXACT, propagation, `FF-LIST-READ`, `DSATUR-READ`, `UC-CM` |
| NF-READ | NO | `FF-LIST-READ`, `UC-READ`, `GREEDY-CM`: **commission**; `SAMPLE-3` 0.13 | EXACT, propagation, `DSATUR-READ`, `FF-CM`, `UC-CM` |

- **Hypotheses and thresholds.** H-formalism: omission share higher on L/C than G/S by ≥ 0.10; commission share higher on G/S by ≥ 0.10; depth equal in statement rounds (k on C/L ≈ t on G/S). H-structure: shares equal (±0.05); depth equal in graph hops (k ≈ 2t). The step-accounting test fits the depth parameter separately on each scale and compares likelihoods.
- **Set-level evidence.** On F-CASE-twin, "NO in G and S, YES in C and L" is 0.7 log10 against H-structure; on NF-READ, "YES in all four" is 0.5 against H-structure.
- **Evidence for / against.** Omission and commission shares moving in opposite directions across encodings support H-formalism and disconfirm H-structure. H-length predicts symmetric slips, so a directional shift also disconfirms it. The depth fit separates H-structure (hops) from H-formalism (rounds) even when the shares agree, provided some items are depth-limited; at best effort most may not be, in which case the F-UP cell only bounds the depth from below.

#### E6. Crossed order

- **Question.** Is E1's agreement across encodings an artefact of matched orders?
- **Design.** E1 bases; C-XORD and L-XORD list vertices (at-least-one block, at-most-one block, conflict groups) in a different order π′, chosen so the LIST fingerprint under π′ differs from G's. G comes from E1.
- **Computed predictions.** LIST-family and `DROP-LAST-1` predictions follow π′ (new fingerprint); LABEL, DSATUR, LF, OCC unchanged; `GUC-DET` follows the clause order (on one library base it coincides with the new LIST fingerprint).
- **Prediction (all hypotheses that hold weights fixed).** The cross-encoding agreement drops from its E1 level by Σ_{h order-dependent} π_h·(1 − a_h), where a_h is the agreement of h's predictions across the two orders (0 here, by construction). The observed − predicted drop has a 95% interval including 0 under H-structure. A larger drop means weight moves between members as well.
- **Translated traces.** Under H-translate, the rebuilt graph lists vertices in π′ (the encoding's own first-mention order), and fingerprints follow π′.
- **Evidence for / against.** An observed drop equal to the predicted one confirms that E1's agreement reflects shared procedures read off each encoding's own order. Agreement that does *not* drop would mean the model ignores listing order (order-free members carry the weight). A larger drop means weights move as well, which counts for H-formalism.

#### E7. Reverse direction: a SAT-native base

- **Question.** With a SAT-native instance, where the graph rendering is longest (3.2–3.7× C), do the weights follow formalism or length?
- **Design.** Random 3-SAT, n = 8 variables, m ∈ {24, 26, 28}, satisfiable. Encodings: C, L-SW ("At least one of these is true: switch 3 is on, switch 5 is off, switch 7 is on."), G-GROUP. Cells by computed signature: r1 (group/clause-driven members `PICK-FIRST`, `MCG`, `GUC-DET` dead-end; variable-driven `UC-DET`, `GREEDY-MENTION`, `POLARITY` succeed) and r2 (the reverse).
- **Hypotheses and thresholds.** H-formalism: false NO in r1 higher on G-GROUP, in r2 higher on C/L-SW, each by ≥ 0.10. H-length: G-GROUP least accurate in both cells (no cell × encoding interaction). H-structure: equal weights. H-translate: if the canonical target is graph, C/L-SW are not translated to G-GROUP (no TR events); if it is clausal, G-GROUP traces rewrite groups as clauses (TR1 "one literal per clause") and G-GROUP's pattern moves to C's.
- **Limit.** The two library cells separate clause/group-driven from variable-driven construction, not the members inside each group (`PICK-FIRST` ≡ `MCG` ≡ `GUC-DET` on both). More cells are a generator option.
- **Evidence for / against.** A cell × encoding interaction in the formalism direction, with G-GROUP not uniformly worst, supports H-formalism and disconfirms H-length. G-GROUP worst in both cells with no interaction supports H-length and disconfirms H-formalism. Because the length direction is the reverse of E1's, the two sets together separate formalism from length.

#### E8. A logic-native gadget in three logical forms

- **Question.** Does B4 weight fall outside logic, beyond what representation-bound members already predict?
- **Design.** The B4/C4 E1 gadget, cells M, N, U, V in DC order, rendered as L-DNF ("Either the box is red and the box is heavy, or the jar is blue and the jar is cold."), L-CNF (four English clauses) and C (symbolic CNF). The three forms have the same models (checked).
- **Computed predictions (YES = endorse):**

| Member | M: L-DNF / L-CNF / C | N | U | V |
|---|---|---|---|---|
| EXACT | NO / NO / NO | YES / YES / YES | NO / NO / NO | NO / NO / NO |
| `FIRST` | YES / YES / YES | NO / NO / NO | YES / YES / YES | YES / YES / YES |
| `MATCH-L`, `MATCH-A` | YES / NO / NO | YES / YES / YES | NO / NO / NO | NO / NO / NO |
| `ETR` (PyETR) | YES / YES / YES | YES / **NO** / **NO** | NO / **YES** / **YES** | YES / YES / YES |
| `ONL(1)` | YES / YES / YES | NO / NO / NO | YES / YES / YES | YES / YES / YES |
| `ONL(2)` | NO / YES / YES | YES / NO / NO | NO / YES / YES | YES / YES / YES |
| `PRIMACY` | YES / NO / NO | YES / NO / NO | YES / NO / NO | YES / NO / NO |
| `UP-1` | NO / NO / NO | YES / YES / YES | NO / NO / NO | NO / NO / NO |

- **Two contrasts.**
  - **L-CNF → C (same clauses; English vs symbols).** Every member's prediction is identical on the two (computed), so any change in answers is a pure weight shift. H-structure: none (±0.05 per cell). H-formalism (logic vs CNF): B4 weights (FIRST, MATCH, ETR, ONL) lower on C by ≥ 0.10. H-surface predicts the same as H-formalism here: E8 does not separate those two.
  - **L-DNF → L-CNF (same surface; disjunctive vs clausal form).** Both are English logic, so H-structure and H-formalism both hold the weights fixed and predict the change Σ_h π_h·Δ_h from the computed member changes. In particular, if ETR has weight, U-cell endorsement should *rise* on L-CNF (ETR now commits there) and N-cell accuracy should *fall*: an illusion that appears only in the clausal form. A finer, form-bound variant of H-formalism (the logical form, not the formalism family, selects) instead predicts a drop in the FIRST pattern (YES on M, U, V; NO on N), whose own prediction does not change with the form.
- **Thresholds.** H-structure: L-CNF = C within ±0.05 per cell; the L-DNF → L-CNF change equals the computed Σ_h π_h·Δ_h within ±0.05. H-formalism / H-surface: π_FIRST + π_MATCH + π_ETR + π_ONL lower on C than on L-CNF by ≥ 0.10. Form-bound variant: FIRST-pattern share lower on L-CNF than L-DNF by ≥ 0.10.
- **Set-level evidence.** On N, "YES in L-DNF only" and "NO in all three" are each 0.27 log10 against H-formalism (and identically against H-surface) per set: small per set, so E8 relies on frames (32 in the core tier) as the B4 vertical's E1 does.
- **Evidence for / against.** A change between L-CNF and C disconfirms H-structure and supports H-formalism or H-surface (the E1 2 × 2 decides between them). A U-cell rise from L-DNF to L-CNF supports the fixed-weight reading of ETR and disconfirms the form-bound variant.

### 2.7 Eval summary (template table)

| ID | Item generator | Answer format | Metric (all with 95% intervals) | Supported if | Against if |
|----|----------------|---------------|--------|--------------|------------|
| E1 | 3-colourable G(n, m), six distinct valid fingerprints, × {G, S, C, L} | Witness or IMPOSSIBLE | π_{h,e}; HAI; omnibus LRT; R; fingerprint distance | H-formalism: HAI ≥ 0.10 (lower > 0.05). H-structure: \|HAI\| ≤ 0.05 and R ≥ 0.9 | The other's threshold met |
| E2 | E1 bases × {G-PAD, X, C-DIMACS} | Witness | Δπ along the ladder; accuracy | H-length: G-PAD ≈ C in accuracy; H-formalism: shift at G → X only | Shift at G → G-PAD (against H-formalism); none anywhere with accuracy gap (for H-length) |
| E3 | E1 bases × dial | Witness | π_G-home by arm; τ by arm; slope of Δπ on Δτ | H-translate: monotone, Δπ ≥ 0.10 | No dial effect with τ moving (against H-translate); HINT effect (against H-formalism) |
| E4 | Near-threshold cells a1, a2, b, c, c-twin × {G, S, C, L} | Witness or IMPOSSIBLE | Cell contrasts by encoding; collapse rate | H-formalism: collapse ≥ 0.10 on C/L, ≤ 0.03 on G/S | Collapse equal across encodings |
| E5 | Precoloured backbone cells × {G, S, C, L} | YES / NO | Omission and commission shares; depth on both scales | H-formalism: shares differ ≥ 0.10 | Shares equal (±0.05) |
| E6 | E1 bases × {C-XORD, L-XORD} | Witness | Agreement drop vs predicted | Observed = predicted (weights fixed) | Larger drop (weights move) |
| E7 | SAT-native r1, r2 × {C, L-SW, G-GROUP} | Assignment / picks or NO | False NO by cell × encoding | Formalism: interaction ≥ 0.10. Length: G-GROUP worst in both | — |
| E8 | B4 gadget M, N, U, V × {L-DNF, L-CNF, C} | YES / NO | Endorsement by cell × form; π_FIRST, π_ETR, π_MATCH by form | Formalism: B4 weights lower on C by ≥ 0.10 | Changes fully explained by members' computed predictions |

### 2.8 Generator specifications

**Common rules (as in the other verticals).** Content hashes for the canonical instance (graph canonical form; CNF canonical form under renaming); every encoding stores its base's hash, and `set_id` is derived from it; dev and test bases from disjoint seed ranges, split by base so every encoding of a base lands in the same split; every member recomputed on every encoding, and the cell definition asserted; ground truth computed by enumeration and by PySAT and asserted equal; tokens counted per tokenizer and logged.

| Eval | Template and parameters | Constraints / rejection | Variant derivation | Surface matching | Yield (measured) |
|---|---|---|---|---|---|
| E1 | G(n, m), n = 12, m = 18 (library); labels 10–99; k = 3 | ≥ 20 partitions; six fingerprints (LIST, LABEL, DSATUR, LF, GUC, OCC) valid and pairwise distinct; `FF-LIST`, `FF-LABEL`, `UC-DET` succeed | Render G, S, C, L with matched orders | Label token counts equal; exam names alphabetical = λ | 3 bases in 247 draws (≈ 1 in 80; milliseconds each). Without the success filter, six distinct fingerprints in 5 of 136 colourable graphs; four distinct (LIST, LABEL, DSATUR, GUC) in 56 of 136 |
| E2 | E1 bases | G-PAD padding words chosen to match C's tokens (±5%) | G-PAD, X, C-DIMACS | X and C clause-for-clause | 100% |
| E3 | E1 bases | Scrambled numbering must give the INDEX members a fingerprint distinct from the others | C-SCRAMBLE, C-NEUTRAL, C-HINT, L-NEUTRAL, L-HINT | Header pairs within ±2% tokens | 100% |
| E4 | n = 12, m ∈ {22, 24, 26} | Cell signature (table in E4); b needs ≥ 6 colourings; c-twin = c minus its last edge, colourable | Four encodings per cell | As E1 | Per 3,000 draws: a1 405, a2 349, b 241, c 275 |
| E5 | n = 10, m ∈ {14, 15, 16}; two precoloured vertices (1, 2) | ≥ 4 colourings; cell signature; F-UP needs WP-2 but not WP-1; F-CASE twin = first edge whose removal unforces the query | Four encodings per cell | Precolouring stated before the constraints in every encoding | Per 3,000 draws (query candidates): F-UP 5,096, F-CASE 1,717, NF-READ 12,034 |
| E6 | E1 bases | π′ such that the LIST fingerprint under π′ differs from G's | C-XORD, L-XORD | Same clauses, reordered | First shuffle on 9 of 10 bases, third on 1 |
| E7 | Random 3-SAT, n = 8, m ∈ {24, 26, 28}, satisfiable | Cell signature r1 / r2 | C, L-SW, G-GROUP | Three-digit labels in G-GROUP (3m can exceed 90) | Per 1,000 draws: 963 satisfiable, r1 172, r2 21 (r2 is the binding cell: about 1 in 50) |
| E8 | B4/C4 E1 templates, frames from the B4 lexicon | Three forms with equal models (asserted) | L-DNF, L-CNF, C | Lexicon single-token checks as in B4 | 100% |

### 2.9 Coverage: which sets separate which hypotheses

✓ = the set can move weight between the pair at the core tier (the pair's predictions differ by ≥ 0.10 on the set's primary quantity). ~ = only conditionally (needs traces, or another set's baseline). Blank = no leverage.

| Pair | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | Traces |
|---|---|---|---|---|---|---|---|---|---|
| H-structure vs H-formalism | ✓ | ~ | ~ | ✓ | ✓ | ~ | ✓ | ✓ | ~ |
| H-structure vs H-translate | | | ✓ | | | ~ | ~ | ~ | ✓ |
| H-formalism vs H-translate | ~ | ✓ (X) | ✓ | ~ | ~ | | ~ | ~ | ✓ |
| H-formalism vs H-length (execution) | ✓ (fingerprints) | ✓ | | ~ | | | ✓ | | ~ |
| H-formalism vs H-length-sel | | ✓ (G-PAD) | | | | | ✓ | | |
| H-formalism vs H-surface | ✓ (2 × 2) | | | ✓ (2 × 2) | ✓ (2 × 2) | | ~ | | |
| H-structure vs H-length | ~ | ✓ (accuracy) | | ~ | | | ✓ | | |
| Representation-bound member vs selection shift | | | ~ | | ~ | ✓ | | ✓ | |
| B4 collapse vs A1 `ALWAYS-NO` | | | | | | | | ✓ | ✓ |
| `FF-LIST` vs `UC-DET` vs `DPLL-LIST` | | | | ✓ | | | | | ✓ |

Every pair of hypotheses has at least one ✓ set. The weakest separations are listed in §8.

### 2.10 Item-level and set-level evidence in the library

Every library item carries:

- `predictions`: each member's canonical answer on that encoding, with `how` (native / transported / n/c) and, for valid witnesses, the expected answer text in the encoding's own format;
- `hypotheses`: for each of the five hypotheses, the predicted output on this item, the pre-registered eval-level threshold, and the CoT prediction;
- `disconfirms`: for each possible observation, log10 LRs against members (10% near-miss slips) and against hypotheses (reference profiles), positive = against;
- `set_disconfirms` (E1, E4, E5, E7, E8): log10 LRs against each hypothesis for joint outcome patterns across the encodings of the instance.

The reference profiles are illustrative weights chosen before data (graph-home, CNF-home and logic-home mixes; τ = 0.6 for C and L, 0.95 with a legend, 0.3 scrambled). They show which observations carry evidence and in which direction. The real test fits π.

### 2.11 Recovery on planted mixtures, and the smallest detectable shift

**Setup** (`recovery_sim.py`). Fake models answer E1-type bases (n = 10, m = 15; LIST, LABEL, DSATUR, GUC distinct) in G, S, C and L by drawing a member from π_e, then slipping to a near-miss (one vertex recoloured) with rate ε_e. Members: LIST, LABEL, DSATUR, LF, GUC, OCC, collapse, EXACT (uniform over partitions), none-of-the-above. Fit by EM per encoding and shared; 95% intervals from 100 base-bootstrap replicates (paired across encodings); HAI with bootstrap SE; omnibus LRT with a parametric-bootstrap null (40 replicates). 20 replicate datasets per scenario and N; the LRT was run on 8 of them at N = 100 and 200 and on all 20 at N = 300.

| N bases / encoding | Scenario | max \|bias\| (weights ≥ 0.05) | Mean 95% width | Coverage mean / min | HAI mean ± 95% half-width | HAI detected (lower 95% > 0) | Omnibus LRT rejects (p < .05) |
|---|---|---|---|---|---|---|---|
| 100 | S0 H-structure (no shift) | 0.027 | 0.156 | 0.90 / 0.65 | −0.013 ± 0.056 | 0.00 | 0.00 |
| 100 | S1 H-formalism, HAI = 0.10 | 0.030 | 0.145 | 0.92 / 0.80 | 0.094 ± 0.059 | 0.80 | 0.38 |
| 100 | S2 H-formalism, HAI = 0.05 | 0.033 | 0.152 | 0.93 / 0.80 | 0.063 ± 0.059 | 0.65 | 0.25 |
| 100 | S3 H-length (slips 0.25 on C/L, no shift) | 0.028 | 0.159 | 0.92 / 0.80 | −0.001 ± 0.058 | 0.00 | 0.00 |
| 200 | S0 | 0.015 | 0.115 | 0.92 / 0.80 | 0.009 ± 0.042 | 0.00 | 0.00 |
| 200 | S1 | 0.013 | 0.106 | 0.92 / 0.70 | 0.100 ± 0.043 | 1.00 | 0.50 |
| 200 | S2 | 0.019 | 0.113 | 0.94 / 0.80 | 0.052 ± 0.042 | 0.70 | 0.25 |
| 200 | S3 | 0.024 | 0.118 | 0.93 / 0.80 | 0.001 ± 0.041 | 0.00 | 0.12 |
| **300** | **S0** | **0.011** | **0.097** | **0.93 / 0.75** | **−0.004 ± 0.033** | **0.00** | **0.05** |
| **300** | **S1** | **0.019** | **0.090** | **0.94 / 0.80** | **0.097 ± 0.036** | **1.00** | **0.95** |
| **300** | **S2** | **0.012** | **0.093** | **0.94 / 0.80** | **0.049 ± 0.036** | **0.85** | **0.15** |
| **300** | **S3** | **0.013** | **0.099** | **0.93 / 0.85** | **−0.001 ± 0.034** | **0.05** | **0.05** |

**Two further planted scenarios** (N = 300, 20 replicates):

- **Slip misspecification.** S3 data (length-driven slips only) fitted with one common slip of 0.10: HAI = −0.003 (SD 0.016), the same as with per-encoding slips. The HAI components do not absorb near-miss mass. Other weights (EXACT, none-of-the-above) may; per-encoding slips stay mandatory.
- **Translation latent.** On C and L each response comes from the graph state with τ = 0.6 (else a native mix with GUC 0.25, DSATUR 0.02); a trace code fires with sensitivity 0.85 and false-positive rate 0.10. The two-state model recovers τ̂ = 0.607 (SD 0.025), native GUC 0.244 (SD 0.030), native DSATUR 0.028 (SD 0.021). The model-free answer–trace association is log OR = 0.99 (SD 0.18): the odds of a C/L-home answer are 2.7 times higher in untranslated traces. H-translate is identifiable from answers plus validated traces.

**What this shows.**

1. The SCOPE recovery gates hold at N = 300: |bias| ≤ 0.019 (gate 0.05), mean coverage 0.93 (gate 0.90), mean width 0.09–0.10 (gate 0.2). Some single components under-cover (minimum 0.75–0.85 over 20 replicates), so the coverage calibration step of the C vertical is required before reporting.
2. **The smallest detectable shift at the planned N (300 bases per encoding):**
   - HAI = 0.05 with 85% power (HAI = 0.10 with 100%), with false-positive rates of 0 and 0.05 under the two null scenarios;
   - a single member's Δπ pooled over G+S vs C+L: about 0.07 (per-weight SE ≈ 0.024);
   - a single member between two single encodings: about 0.10;
   - the omnibus LRT is weaker (95% power at HAI = 0.10, 15% at 0.05), because it spreads its degrees of freedom over all members. HAI is the primary test; the LRT is the omnibus check of shared π.
3. **Equivalence (H-structure) is harder than detection.** Under S0 the 95% interval of HAI fell within ±0.05 in 60% of replicates at N = 300. The pre-registered TOST uses the 90% interval; with the simulated SE (0.0176 at N = 300) its power is about 0.77, and N ≈ 320 bases per encoding gives 0.80. The full tier (600) gives about 0.97.

---

## 3. Mechanistic evidence: Phase 2 (only if behavioural evidence)

**Trigger.** H-translate's τ ≥ 0.3 with an answer–trace association, or HAI ≥ 0.10, on at least two models.

- **State variable.** The working representation: when reading C, is "variables x_i and x_j belong to the same vertex" and "vertices u and v are adjacent" linearly decodable at clause positions, and when?
- **Probes.** Pairwise probes for same-vertex and adjacency at the tokens of each conflict clause, with Hewitt & Liang control tasks; compare C, C-SCRAMBLE and C-HINT (R-I2 predicts no difference for the clause-membership program).
- **Interventions.** Patch the adjacency representation from G (same instance, matched positions) into a C run and test whether the answer moves toward the G-profile member, against the same patch on a random-init model and a norm-matched random subspace.
- **Positive control.** A small transformer trained to translate the direct encoding into an edge list (the §1.7 program), to calibrate probes.
- **Models.** Qwen3-14B and gpt-oss-20b, as in the other verticals.
- **Effort.** About 10 person-days if triggered (probes 4, patching 3, positive control 3).

---

## 4. Build scope

| # | Component | Person-days | Shared? |
|---|---|---|---|
| 1 | Renderers for all encodings with matched and crossed orders, token assertions, content hashes (scratch versions in `cf_core.py`) | 2 | Partly (C's order objects, B4's lexicon) |
| 2 | Native CNF and logic member variants (clause-form FIRST and ONL), transport wrapper (translate → apply → map back), canonical answer mapping and parsers per encoding | 3 | Members: yes (C, D/F, B1, B4/C4); wrapper: new |
| 3 | Generators E1–E8 with cell assertions (scratch versions in `build_library.py`, `cf_other_bases.py`) | 3 | No |
| 4 | Trace codes TR1–TR4: lexicon-share parser, edge-list checker, LLM-coder prompt | 2 | Codebook shared |
| 5 | Hand-labelling 200 traces × 2 coders for TR1/TR2 (κ ≥ 0.7) | 4 (annotation) | — |
| 6 | Analysis: two-stage latent model, HAI, parametric-bootstrap LRT, agreement ratio, fingerprint distance, censoring | 3 | Identification engine shared |
| 7 | Recovery harness configs (planted encoding-dependent and translation scenarios; `recovery_sim.py` is the scratch version) | 1 | Harness shared |
| 8 | Dev-batch run, size calibration on C/L, power re-estimate | 1 | — |
| | **Total** | **≈ 19** (15 engineering + 4 annotation) | |

---

## 5. Compute budget

Output tokens are estimates for gpt-oss-20b at high effort, anchored on the other verticals' figures (C: 7k for n = 16 colouring, 10k for 20-variable 3-SAT; B4/C4 E6: 9k for colouring and SAT twins). Prompt tokens are measured on the library (o200k). **Replace every output figure with dev-batch measurements before the core run.**

| Eval ID | Domain | # items (core) | Conditions | Samples/item | Avg prompt tokens | Avg output tokens | Needs activations? |
|---|---|---|---|---|---|---|---|
| E1 | colouring n = 12 | 1,440 (300 bases × 4, + 20% retest) | BE | 1 (1.2 on G/C retest subset) | G 290 · S 290 · C 1,220 · L 2,500 | G/S 5,000 · C/L 12,000 (5–15% at 32k on C/L) | N |
| E1 dev | colouring | 32 (8 bases × 4) | BE | 1 | as above | as above | N |
| E2 | colouring | 450 (150 bases × 3) | BE | 1 | G-PAD 1,200 · X 1,700 · DIMACS 860 | 6,000 · 10,000 · 12,000 | N |
| E2 dev | colouring | 15 | BE | 1 | as above | as above | N |
| E3 | colouring | 750 (150 bases × 5) | BE | 1 | C-arms 1,220–1,290 · L-arms 2,510 | 10,000–12,000 | N |
| E3 dev | colouring | 25 | BE | 1 | as above | as above | N |
| E4 | colouring n = 12 near threshold | 1,200 (5 cells × 60 sets × 4) | BE | 1 | G 310 · S 315 · C 1,370 · L 2,850 | G/S 8,000 · C/L 15,000 (10–20% at 32k on C/L) | N |
| E4 dev | colouring | 80 | BE | 1 | as above | as above | N |
| E5 | backbone n = 10 | 960 (4 cells × 60 × 4) | BE | 1 | G 245 · S 262 · C 1,025 · L 2,110 | G/S 5,000 · C/L 10,000 | N |
| E5 dev | backbone | 64 | BE | 1 | as above | as above | N |
| E6 | colouring | 200 (100 bases × 2) | BE | 1 | 1,220 / 2,500 | 12,000 | N |
| E6 dev | colouring | 10 | BE | 1 | as above | as above | N |
| E7 | 3-SAT n = 8 | 360 (2 cells × 60 × 3) | BE | 1 | C 460 · L-SW 840 · G-GROUP 1,600 | 8,000 · 8,000 · 12,000 | N |
| E7 dev | 3-SAT | 24 | BE | 1 | as above | as above | N |
| E8 | gadget | 384 (4 cells × 32 frames × 3) | BE | 1 | ≈ 100 | 1,500 | N |
| E8 dev | gadget | 48 | BE | 1 | as above | as above | N |

**Totals.**

| Tier | Generations | Input tokens | Output tokens | gpt-oss-20b (batch $0.024 / $0.112 per M) | gpt-oss-120b (batch $0.03 / $0.136 per M) |
|---|---|---|---|---|---|
| Dev batch | 298 | 0.30M | 2.5M | **$0.29** | **$0.35** |
| Core tier | 5,744 | 6.5M | 52.2M | **$6.00** | **$7.29** |
| Full tier (2× bases) | 11,488 | 13.0M | 104.4M | $12.00 | $14.58 |

Per-eval core output: E1 12.2M, E2 4.2M, E3 8.4M, E4 13.8M, E5 7.2M, E6 2.4M, E7 3.4M, E8 0.6M. Trace coding of a 20% sample with gpt-oss-120b (batch) adds about $0.40 per model.

**If cost binds,** run E1, E3, E4 first (≈ $4.0 on gpt-oss-20b, $4.8 on gpt-oss-120b); they carry the three primary quantities. Cut E2 and E6 to 100 bases next.

---

## 6. What would bound each hypothesis

All statements are per model, with the hierarchical pooled estimate; bounds are upper 95% posterior limits checked for attainability in §2.11.

- **H-formalism is bounded to negligible** if |HAI| ≤ 0.05 on E1, the collapse rate in E4 cell b differs by ≤ 0.03 between C/L and G/S, the E5 omission and commission shares differ by ≤ 0.05, the E7 interaction is ≤ 0.05, and FIRST-pattern answers on E8 differ by ≤ 0.05 across forms.
- **H-structure is disconfirmed** (in graded form: "the encoding moves weight by …") if HAI's lower 95% bound exceeds 0.05, or the omnibus LRT rejects with ΔELPD > 2 SE, or R's upper bound is below 0.9.
- **H-translate is bounded** if τ_C, τ_L ≤ 0.2 (upper 95%) and the E3 dial slope is ≤ 0.05; it is reduced to "verbal only" if τ is high but the answer–trace association interval includes 0 and the dial does nothing.
- **H-length (execution) is disconfirmed** if fingerprint distributions among valid answers differ (distance lower 95% > 0.05), or G-PAD's accuracy differs from C's at matched tokens by > 0.10, or E7's longest rendering is not the least accurate. **H-length-sel** is disconfirmed if π(G-PAD) stays with π(G) while π(C) moves.
- **H-surface is disconfirmed** if Δπ(S − G) and Δπ(L − C) differ by > 0.05, or S vs L (same vocabulary) shows a shift.
- **Partial outcomes are reported as weights, not verdicts.** For example: "graph-home weight falls by 0.08 [0.04, 0.12] on C, of which 0.05 is recovered by the legend (E3) and none by padding (E2)" is a graded mix of H-translate and H-formalism, and that is the result.

---

## 7. Evidence-table row

This vertical does not add a family row to Table 14. It adds one column (or a row group for family I).

| Formalism dependence (HAI, 95% CI) | Largest single Δπ_h(form) | Translation rate τ_C / τ_L | Dial effect Δπ(HINT − SCRAMBLE) | Fingerprint distance G vs C | Agreement ratio R | Control recovered |
|---|---|---|---|---|---|---|
| [0.XX [0.XX, 0.XX]] | [member, ±0.XX] | [0.XX / 0.XX] | [±0.XX] | [0.XX] | [0.XX] | §2.11: bias ≤ 0.02, coverage 0.93, HAI detectable at 0.05 (85%) |

---

## 8. Open questions and weak separations

1. **H-structure vs H-translate at τ ≈ 1.** If the model always translates, both make the same answer-level predictions. The separation then rests on the dial (does scrambling lower τ and move π?) and on traces. If scrambling does not lower τ either, they are separable only by traces, which are down-weighted evidence.
2. **B4 collapse vs A1 `ALWAYS-NO` on colouring sets.** Identical answers on every colouring item. Split only by trace codes (K3, K5, polarity counting). E8 carries B4 proper.
3. **The LIST family.** `FF-LIST`, `UC-DET` and DPLL in listing order are answer-identical wherever they succeed. Only E4's a1/a2 cells and traces split them, so E4 needs its full 60 sets per cell.
4. **Statement count and clausal formalism are not separable within colouring bases.** E7 reverses the length direction with a *different* base type, so instance class and direction are confounded there. A within-instance reversal would need a formalism in which colouring is more verbose than CNF; we have not found a natural one.
5. **L is twice as long as C.** L vs C changes surface and length together; S vs L is the clean formalism contrast, C-DIMACS and G-PAD bracket the length effect.
6. **Transparency.** L's atoms name exams and slots, so the timetabling reading is visible; C is opaque. "Formalism" in the symbolic row is partly "opacity"; X and C-HINT address it.
7. **ETR on colouring sets is `n/c`.** PyETR times out from n = 6. ETR's weight on colouring encodings cannot be estimated; ETR enters only through E8.
8. **Reference profiles drive the library's hypothesis-level LRs.** They are illustrative. The pre-registered quantities are the fitted π, HAI, τ and the contrasts.
9. **Differential truncation.** C/L truncate more. If more than 50% of C/L runs truncate on a cell, n is lowered for the whole set. A sensitivity analysis keeps only bases complete in all four encodings.
10. **Answer format cannot be fully matched.** C asks for the set of true variables; G/S/L ask for one line per vertex in listing order. The C vertical's answer-order member (FF-OUT) is therefore undefined on C; at best effort we expect it to carry little weight, and it is reported only on the diagnostic low-effort runs.
11. **Which target formalism?** For colouring bases we expect translation to graph; E7 asks whether SAT-native bases are translated to clauses. If both directions translate to "the source", the latent target is item-dependent and the two-stage model needs a target per base type.
12. **Questions for the B4/C4 owners.** Whether ETR's behaviour on clausal input (fact 4) is a known property of the theory or of PyETR's default procedure, and which ETR procedure should represent the theory on E8.

---

## 9. Proposed edits elsewhere

Not made here; for integration.

**PAPER_SKELETON.md**

- **Table 4, row I.** Change "Not a vertical: modelled as feature-dependent mixture weights π_h(φ(x))" to: "Modelled as π_h(φ(x)); one feature, the input's formalism, has its own vertical (I_cross_formalism: same instance as graph / story / CNF / English premises, ground truth fixed)." Add to the error signature: "π shifts with formalism (HAI), measured with length and order controlled."
- **§5, a note under Table 4 (new).** Some members are *representation-bound*: their predictions change with the form of the same content (MATCH, PRIMACY, ETR and ONL(2) between disjunctive and clausal forms; first-fit with listing order). Family labels can be formalism-relative: "build one model and read the query off it" is C1 in a graph and a B4-style single-model restriction in logic.
- **§6.2 Likelihood model.** Add: predictions computed per encoding (native or transported through the reduction); a canonical answer space; slip rates per encoding; the two-stage selector (encoding → working representation → member) with a latent translation state indicated by trace codes.
- **§6.3 Manipulations.** Add "re-encoding across formalisms (ground truth fixed)", the length ladder (padding, expansion, compression) and the translation dial.
- **§6.4 Table 6.** Add planted rows: "encoding-dependent π, HAI = 0.10 and 0.05" and "translation latent τ = 0.6 with trace codes", with the §2.11 results.
- **§7.2 Table 9.** Add rows "Re-encoded (graph → CNF → logic), orders matched" and "Reduction named (legend)", with predicted directions per family (C1/C2 graph-home down on C/L under H-formalism; collapse up on C/L; no change under H-structure).
- **Table 14.** Add a family-I column group: HAI with interval, τ, dial effect, fingerprint distance, agreement ratio R (the §7 row). Figure 4: one stacked bar per encoding, not only per model.
- **§11 Discussion / DESIGN H4.** Point H4 at this vertical, and note Zhang, Chen & Chen (2026) as the answer-agreement precedent this design extends to procedure agreement.

**SCOPE.md**

- **§3 volume table.** Add: "I: cross-formalism | ~5,740 generations per model (core) | ~52M output tokens | dev ~2.8M tokens | ~19 person-days (4 annotation) | Phase 2 ~10 (if triggered)".
- **Cost per model.** gpt-oss-20b core $6.00, gpt-oss-120b core $7.29 (batch); dev $0.29 / $0.35.
- **$100 plan.** Adds about $13 for both models at the core tier. To stay under $100: run I's core on gpt-oss-20b only in the "real results" stage (+$6), and gpt-oss-120b in the "if good" stage; or run E1, E3, E4 only on both (≈ $8.8).
- **§5 build order.** Stage 2 (after C and B4/C4, whose members and renderers it reuses). E1 and E4 dev batches (≈ $0.15) can run in Stage 1, since they need only C-vertical members plus the CNF renderer.
- **§6 rules.** Add: "Every member's prediction is computed on every encoding of an item; transported predictions are flagged; slip rates are estimated per encoding."
- **§7 weak separations.** Add three rows: H-structure vs H-translate (dial and traces only); B4 collapse vs A1 `ALWAYS-NO` on colouring logic (traces only); FF-LIST vs UC-DET vs DPLL in listing order (dead-end cells and traces only).

---

## References

Only works already in the repo's literature reports. Tags as in the other verticals ([R] read, [A] abstract, [S] secondary, [M] metadata).

- Davis-Stober & Brown (2011); Glöckner (2009); Bröder & Schiffer (2003). Strategy classification, stochastic specifications, multiple-measure likelihoods. [B]
- Duchnowski, Pavlick & Koller (2025). *A Knapsack by Any Other Name* (EHOP). Findings of EMNLP, arXiv 2502.13776. [B, R]
- Hewitt & Liang (2019). *Designing and Interpreting Probes with Control Tasks.* arXiv 1909.03368. [C]
- Karp (1972). Reducibility among combinatorial problems (SAT → independent set). [E]
- Lieder & Griffiths (2017; 2020); Rice's algorithm-selection problem. Strategy selection. [F, S]
- Zhang, Chen & Chen (2026). *Satisfiability Solving with LLMs: A Matched-Pair Evaluation of Reasoning Capability.* FSE, arXiv 2605.28602. Answers agree across SAT, vertex-cover and 3D-packing reductions on about 75–80% of instances. [A]
- Zhou et al. (2024). *What Algorithms can Transformers Learn?* (RASP-L). ICLR, arXiv 2310.16028. [D]
- The direct (one variable per vertex–colour pair) encoding of colouring into CNF is standard; [TODO add a citation from the SAT-encoding literature before the paper].
- Member definitions: the C, D/F, B1/G, E, B4/C4 and A/H verticals of this repo.
