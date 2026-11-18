# I — Cross-formalism question library

*Companion to [I_cross_formalism.md](I_cross_formalism.md). Machine-readable copy: [`data/examples/I_cross_formalism.jsonl`](../../data/examples/I_cross_formalism.jsonl). Built by [`scripts/cross_formalism/build_library.py`](../../scripts/cross_formalism/build_library.py) and rendered by `render_questions_md.py` in the same folder.*

## How to read this library

- **What is here.** 81 items in 8 question sets (E1–E8). Every item is one encoding of one instance. `set_id` links the encodings of one instance (same ground truth); `pair_id` links counterfactual partners (truth twins, length-ladder and dial arms of a base); `encoding` names the rendering.
- **Items by encoding:** G 12, S 12, C 18, L 12, G-PAD 2, X 2, C-DIMACS 2, C-SCRAMBLE 1, C-NEUTRAL 1, C-HINT 1, L-NEUTRAL 1, L-HINT 1, C-XORD 2, L-XORD 2, L-SW 2, G-GROUP 2, L-DNF 4, L-CNF 4.
- **Encodings.** **G** = graph colouring, symbolic labels; **S** = story: exam timetable; **C** = CNF, opaque variables; **L** = English premises, clause for clause; **G-PAD** = G with long labels (tokens ≈ C); **X** = CNF with named atoms v37.1 (statements of C, labels of G); **C-DIMACS** = C in DIMACS notation (fewer tokens); **C-SCRAMBLE** = C with variable numbers permuted; **C-NEUTRAL** = C + neutral header (token control); **C-HINT** = C + legend naming the reduction; **L-NEUTRAL** = L + neutral header; **L-HINT** = L + legend; **C-XORD** = C, vertices in a different order; **L-XORD** = L, vertices in a different order; **L-SW** = switch rules in English; **G-GROUP** = graph: one vertex per group, no two adjacent; **L-DNF** = English, disjunction of conjunctions; **L-CNF** = English, four clauses.
- **How everything was computed.** No value here was worked out by hand.
  - Colouring ground truth: enumeration of every colouring by backtracking, checked against PySAT (Glucose 4) on the direct CNF encoding. Backbone (E5) truth: enumeration, checked by PySAT with the negated query as an assumption. SAT-native truth (E7): truth table and PySAT. Gadget truth (E8): truth table, with the three logical forms checked to have the same models.
  - Members: reference implementations in `scripts/cross_formalism/cf_members.py` (definitions from the owning verticals). ETR: PyETR 1.0.0, computed on E8 only; on colouring-derived logic it times out from n = 6 (n = 5 took 18 s), so ETR is `n/c` there.
  - Tokens: o200k_base (the gpt-oss tokenizer family).
- **Prediction cells.** Each member's answer on each encoding, mapped to the canonical space (a colouring of the underlying graph, IMP = IMPOSSIBLE/UNSAT/NO, or YES/NO). Valid colourings are named by the members that produce them: LIST = the lexicographically first colouring in listing order (FF-LIST, UC-DET, DPLL-LIST and DPLL-MENTION when they succeed); LABEL = the same in label order; DSATUR, LF, GUC (GUC-DET), OCC (DPLL-OCC). `ᵗ` = transported (the member is not defined on this surface; its prediction is computed by translating through the reduction, which is what H-translate says the model does). Unmarked = native.
- **Readout is graded.** The response distribution on encoding e is Σ_h π_{h,e}·p_h(y | x_e) plus a none-of-the-above term. Hypotheses are statements about how π_{h,e} depends on e (vertical §2.2).
- **Sign convention.** Every likelihood ratio is a **log10 LR, positive = evidence against that theory**, relative to the theory (member, or hypothesis) that predicts the observation best. Member LRs use a 10% near-miss slip (one vertex recoloured) for deterministic members. Hypothesis LRs use the **reference profiles** of `build_library.py` (illustrative weights, not estimates) and are per single response; set-level LRs add the log-probabilities of the responses across the encodings of one instance, assuming independent responses given the hypothesis.
- **Hypothesis blocks.** Every item carries, for each of H-structure, H-formalism, H-translate, H-length and H-surface: (a) the predicted output on this item, (b) the pre-registered eval-level threshold, (c) the chain-of-thought prediction. Trace codes TR1–TR4 are defined in vertical §2.5; member codes K… are those of the owning verticals.

## E1. Witness fingerprints across four formalisms

- **Reasoning question.** When a model solves the same 3-colouring instance as a graph, a timetable story, a CNF formula and a list of English premises, does *which* valid answer it returns (the fingerprint of the procedure) stay the same? Fingerprints are read among valid answers, so the comparison does not depend on accuracy.
- **Varied:** Encoding: G, S, C, L (same instance, same listing order and label order).
- **Controlled:** Ground truth (colourable, ≥ 20 partitions); vertex listing order = first-mention order; label order = variable-index order = alphabetical order of exam names; colours 1, 2, 3 everywhere; answer format (a witness or IMPOSSIBLE).
- **Pre-registered eval-level predictions** (from the hypothesis blocks):
  - **H-structure:** Pooled over E1: every |Δπ_h(e, G)| 90% interval within ±0.05 (TOST); omnibus shared-π vs encoding-specific-π: ΔELPD < 2 SE and parametric-bootstrap LRT p > .05; cross-encoding / retest agreement ratio R >= 0.9.
  - **H-formalism:** Home-advantage index HAI >= 0.10 (lower 95% > 0.05), using only components identifiable on E1 items: graph-home DSATUR (= DPLL-DSATUR) and LF weight higher on G/S than C/L; CNF/logic-home GUC-DET, DPLL-OCC and the collapse members (POLARITY, GREEDY, FIRST, BICOND, ONL; answer IMPOSSIBLE) higher on C/L than G/S; R <= 0.8.
  - **H-translate:** Translation rate tau_C, tau_L >= 0.5 (κ-corrected); weight on graph-home members in translated C/L traces exceeds untranslated ones by >= 0.20; π on C/L lies on the segment between the C/L-home and G profiles.
  - **H-length:** Valid-answer fingerprint distributions equal across encodings (total-variation distance <= 0.05); accuracy differences fully absorbed by length-dependent slip (see E2).
  - **H-surface:** Δπ(S − G) and Δπ(L − C) equal and non-zero (>= 0.10); Δπ(C − G) and Δπ(L − S) within ±0.05.

### E1 · I-E1-B1 · base 1

**Ground truth:** colourable = True, n_colourings = 228, n_partitions = 38 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** G: 280 tokens, 18 statements · S: 278 tokens, 18 statements · C: 1214 tokens, 102 statements · L: 2458 tokens, 102 statements.

**Prompt, G** (graph colouring, symbolic labels):

```
Graph with 12 vertices and 18 edges.
Vertices (in this order): v83, v32, v56, v55, v25, v16, v49, v71, v80, v13, v62, v94
Edges (in this order):
v83 - v49
v83 - v80
v32 - v80
v56 - v16
v56 - v13
v55 - v16
v55 - v80
v55 - v62
v25 - v80
v25 - v13
v16 - v94
v49 - v80
v49 - v94
v71 - v80
v71 - v94
v80 - v13
v13 - v94
v62 - v94
Colour every vertex with one of the colours 1, 2, 3 so that the two ends of every edge get different colours.

Think it through as carefully as you need. If no such colouring exists, finish with the line "ANSWER: IMPOSSIBLE". Otherwise finish with the line "ANSWER:" followed by one line `vertex: colour` per vertex, in this order: v83, v32, v56, v55, v25, v16, v49, v71, v80, v13, v62, v94.
```

**Prompt, S** (story: exam timetable):

```
A school must timetable 12 exams into three slots: slot 1, slot 2 and slot 3.
Exams (in this order): Welding, Finance, Poetry, Mechanics, Ecology, Ceramics, Italian, Statistics, Urdu, Algebra, Quilting, Zoology
Some pairs of exams share a student, so the two exams in each pair must be in different slots. The pairs are (in this order):
Welding and Italian
Welding and Urdu
Finance and Urdu
Poetry and Ceramics
Poetry and Algebra
Mechanics and Ceramics
Mechanics and Urdu
Mechanics and Quilting
Ecology and Urdu
Ecology and Algebra
Ceramics and Zoology
Italian and Urdu
Italian and Zoology
Statistics and Urdu
Statistics and Zoology
Urdu and Algebra
Algebra and Zoology
Quilting and Zoology
Put every exam in one of the three slots so that no student has two exams in the same slot.

Think it through as carefully as you need. If no such timetable exists, finish with the line "ANSWER: IMPOSSIBLE". Otherwise finish with the line "ANSWER:" followed by one line `exam: slot` per exam, in this order: Welding, Finance, Poetry, Mechanics, Ecology, Ceramics, Italian, Statistics, Urdu, Algebra, Quilting, Zoology.
```

**Prompt, C** (CNF, opaque variables):

```
CNF formula over 36 Boolean variables (x01 to x36) with 102 clauses (in this order):
(x31 ∨ x32 ∨ x33)
(x10 ∨ x11 ∨ x12)
(x19 ∨ x20 ∨ x21)
(x16 ∨ x17 ∨ x18)
(x07 ∨ x08 ∨ x09)
(x04 ∨ x05 ∨ x06)
(x13 ∨ x14 ∨ x15)
(x25 ∨ x26 ∨ x27)
(x28 ∨ x29 ∨ x30)
(x01 ∨ x02 ∨ x03)
(x22 ∨ x23 ∨ x24)
(x34 ∨ x35 ∨ x36)
(¬x31 ∨ ¬x32)
… (85 lines omitted; full prompt in the JSONL) …
(¬x03 ∨ ¬x36)
(¬x22 ∨ ¬x34)
(¬x23 ∨ ¬x35)
(¬x24 ∨ ¬x36)
Find an assignment of true/false to the variables that makes every clause true.

Think it through as carefully as you need. If no such assignment exists, finish with the line "ANSWER: UNSAT". Otherwise finish with the line "ANSWER:" followed by the variables you set to true, separated by spaces (every other variable is false).
```

**Prompt, L** (English premises, clause for clause):

```
Here are some statements:
1. The Welding exam is in slot 1, slot 2 or slot 3.
2. The Finance exam is in slot 1, slot 2 or slot 3.
3. The Poetry exam is in slot 1, slot 2 or slot 3.
4. The Mechanics exam is in slot 1, slot 2 or slot 3.
5. The Ecology exam is in slot 1, slot 2 or slot 3.
6. The Ceramics exam is in slot 1, slot 2 or slot 3.
7. The Italian exam is in slot 1, slot 2 or slot 3.
8. The Statistics exam is in slot 1, slot 2 or slot 3.
9. The Urdu exam is in slot 1, slot 2 or slot 3.
10. The Algebra exam is in slot 1, slot 2 or slot 3.
11. The Quilting exam is in slot 1, slot 2 or slot 3.
12. The Zoology exam is in slot 1, slot 2 or slot 3.
13. If the Welding exam is in slot 1, then the Welding exam is not in slot 2.
… (85 lines omitted; full prompt in the JSONL) …
99. If the Algebra exam is in slot 3, then the Zoology exam is not in slot 3.
100. If the Quilting exam is in slot 1, then the Zoology exam is not in slot 1.
101. If the Quilting exam is in slot 2, then the Zoology exam is not in slot 2.
102. If the Quilting exam is in slot 3, then the Zoology exam is not in slot 3.
Question: Can all of these statements be true at the same time? If they can, describe a situation in which they are all true.

Think it through as carefully as you need. If they cannot all be true, finish with the line "ANSWER: NO". Otherwise finish with the line "ANSWER:" followed by one line `exam: slot` per exam, in this order: Welding, Finance, Poetry, Mechanics, Ecology, Ceramics, Italian, Statistics, Urdu, Algebra, Quilting, Zoology.
```

**Predictions per encoding** (canonical answer):

| Member (family, home) | G | S | C | L |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=UC-INDEX | LABEL=UC-INDEX | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ |
| `LF` (C1, graph) | LF | LF | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC ᵗ | GUC ᵗ | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC ᵗ | OCC ᵗ | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| LIST-family fingerprint in G, S, C and L | 0.00 | 0.17 | 0.06 | 0.35 | 0.21 |
| DSATUR in G and S; GUC-DET in C and L | 1.14 | 0.00 | 0.50 | 1.47 | 1.23 |
| DSATUR in all four | 0.00 | 1.23 | 0.31 | 0.35 | 1.23 |
| valid in G and S; IMPOSSIBLE in C and L | 1.16 | 0.00 | 0.50 | 1.33 | 0.61 |
| LIST in G and C; DSATUR in S and L | 0.00 | 0.68 | 0.18 | 0.35 | 1.23 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `UC-DET-INDEX` 6.0, `GUC-DET` 6.0 | H-structure +0.00 · H-formalism +0.07 · H-translate +0.03 · H-length +0.18 · H-surface +0.00 |
| answer = fingerprint #1 (DPLL-INDEX, FF-LABEL, UC-DET-INDEX) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.14 · H-formalism +0.00 · H-translate +0.08 · H-length +0.31 · H-surface +0.14 |
| answer = fingerprint #2 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.32 · H-translate +0.10 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.61 · H-translate +0.16 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #4 (GUC-DET) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.62 · H-formalism +0.00 · H-translate +0.26 · H-length +0.78 · H-surface +0.62 |
| answer = fingerprint #5 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.33 · H-formalism +0.00 · H-translate +0.17 · H-length +0.48 · H-surface +0.33 |
| another valid colouring (no member predicts it) | `RANDOM` 3.6, `LF` 2.0, `DSATUR` 2.0, `DPLL-DSATUR` 2.0, `DPLL-OCC` 2.0, `FF-LIST` 1.8 | H-structure +0.04 · H-formalism +0.00 · H-translate +0.03 · H-length +0.08 · H-surface +0.04 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.49 · H-formalism +0.61 · H-translate +0.53 · H-length +0.00 · H-surface +0.49 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.50 · H-formalism +0.00 · H-translate +0.23 · H-length +0.59 · H-surface +0.50 |

### E1 · I-E1-B2 · base 2

**Ground truth:** colourable = True, n_colourings = 552, n_partitions = 92 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** G: 280 tokens, 18 statements · S: 295 tokens, 18 statements · C: 1214 tokens, 102 statements · L: 2535 tokens, 102 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | G | S | C | L |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=UC-INDEX | LABEL=UC-INDEX | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ |
| `LF` (C1, graph) | LF | LF | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC ᵗ | GUC ᵗ | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC ᵗ | OCC ᵗ | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| LIST-family fingerprint in G, S, C and L | 0.00 | 0.18 | 0.07 | 0.35 | 0.21 |
| DSATUR in G and S; GUC-DET in C and L | 1.21 | 0.00 | 0.52 | 1.54 | 1.31 |
| DSATUR in all four | 0.00 | 1.33 | 0.33 | 0.35 | 1.33 |
| valid in G and S; IMPOSSIBLE in C and L | 1.16 | 0.00 | 0.50 | 1.34 | 0.61 |
| LIST in G and C; DSATUR in S and L | 0.00 | 0.73 | 0.19 | 0.35 | 1.33 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `UC-DET-INDEX` 6.0, `GUC-DET` 6.0 | H-structure +0.00 · H-formalism +0.07 · H-translate +0.03 · H-length +0.18 · H-surface +0.00 |
| answer = fingerprint #1 (DPLL-INDEX, FF-LABEL, UC-DET-INDEX) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.14 · H-formalism +0.00 · H-translate +0.08 · H-length +0.31 · H-surface +0.14 |
| answer = fingerprint #2 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.37 · H-translate +0.11 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.66 · H-translate +0.16 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #4 (GUC-DET) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.65 · H-formalism +0.00 · H-translate +0.27 · H-length +0.81 · H-surface +0.65 |
| answer = fingerprint #5 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.35 · H-formalism +0.00 · H-translate +0.18 · H-length +0.51 · H-surface +0.35 |
| another valid colouring (no member predicts it) | `RANDOM` 3.3, `DPLL-OCC` 2.0, `FF-LIST` 1.8, `FF-LIST-INFEAS` 1.8, `FF-LABEL` 1.8, `DPLL-LIST` 1.8 | H-structure +0.04 · H-formalism +0.00 · H-translate +0.02 · H-length +0.04 · H-surface +0.04 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.50 · H-formalism +0.59 · H-translate +0.54 · H-length +0.00 · H-surface +0.50 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.50 · H-formalism +0.00 · H-translate +0.23 · H-length +0.59 · H-surface +0.50 |

### E1 · I-E1-B3 · base 3

**Ground truth:** colourable = True, n_colourings = 528, n_partitions = 88 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** G: 280 tokens, 18 statements · S: 294 tokens, 18 statements · C: 1214 tokens, 102 statements · L: 2537 tokens, 102 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | G | S | C | L |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=UC-INDEX | LABEL=UC-INDEX | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ |
| `LF` (C1, graph) | LF | LF | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC ᵗ | GUC ᵗ | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC ᵗ | OCC ᵗ | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| LIST-family fingerprint in G, S, C and L | 0.00 | 0.18 | 0.07 | 0.35 | 0.21 |
| DSATUR in G and S; GUC-DET in C and L | 1.20 | 0.00 | 0.52 | 1.52 | 1.31 |
| DSATUR in all four | 0.00 | 1.33 | 0.33 | 0.35 | 1.33 |
| valid in G and S; IMPOSSIBLE in C and L | 1.16 | 0.00 | 0.50 | 1.34 | 0.61 |
| LIST in G and C; DSATUR in S and L | 0.00 | 0.74 | 0.19 | 0.35 | 1.33 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `UC-DET-INDEX` 6.0, `GUC-DET` 6.0 | H-structure +0.00 · H-formalism +0.07 · H-translate +0.03 · H-length +0.18 · H-surface +0.00 |
| answer = fingerprint #1 (DPLL-INDEX, FF-LABEL, UC-DET-INDEX) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.14 · H-formalism +0.00 · H-translate +0.08 · H-length +0.31 · H-surface +0.14 |
| answer = fingerprint #2 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.35 · H-translate +0.11 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.67 · H-translate +0.16 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #4 (GUC-DET) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.65 · H-formalism +0.00 · H-translate +0.27 · H-length +0.81 · H-surface +0.65 |
| answer = fingerprint #5 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.36 · H-formalism +0.00 · H-translate +0.18 · H-length +0.51 · H-surface +0.36 |
| another valid colouring (no member predicts it) | `RANDOM` 3.3, `DPLL-OCC` 2.0, `FF-LIST` 1.9, `FF-LIST-INFEAS` 1.9, `DPLL-LIST` 1.9, `DPLL-LIST-b12` 1.9 | H-structure +0.03 · H-formalism +0.00 · H-translate +0.02 · H-length +0.04 · H-surface +0.03 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.51 · H-formalism +0.59 · H-translate +0.54 · H-length +0.00 · H-surface +0.51 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.50 · H-formalism +0.00 · H-translate +0.23 · H-length +0.59 · H-surface +0.50 |

## E2. Length ladder

- **Reasoning question.** Is the G → C difference a length effect (tokens or statement count) or a formalism effect? G-PAD adds tokens only; X expands every edge into per-colour clauses but keeps G's labels; C-DIMACS removes tokens from C.
- **Varied:** Encoding: G-PAD, X, C-DIMACS (G and C of the same instance are in E1).
- **Controlled:** Instance, orders, answer format.
- **Pre-registered eval-level predictions** (from the hypothesis blocks):
  - **H-structure:** G-PAD, X and C-DIMACS have the same π as G and C (all |Δπ| within ±0.05).
  - **H-formalism:** Δπ(G → G-PAD) within ±0.05 (tokens alone change nothing); Δπ(G → X) >= 0.10 toward CNF-home members; Δπ(X → C) within ±0.05.
  - **H-translate:** X behaves like G (transparent atoms are translated: tau_X >= 0.8); C-DIMACS like C.
  - **H-length:** Δπ and accuracy change G → G-PAD >= 80% of the G → C change; C-DIMACS (fewer tokens) is closer to G than C is.
  - **H-surface:** All five encodings here are symbolic: no differences beyond ±0.05.

### E2 · I-E1-B1 · base 1

**Ground truth:** colourable = True, n_colourings = 228, n_partitions = 38 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** G-PAD: 1168 tokens, 18 statements · X: 1699 tokens, 102 statements · C-DIMACS: 855 tokens, 102 statements.

**Prompt, G-PAD** (G with long labels (tokens ≈ C)):

```
Graph with 12 vertices and 18 edges.
Vertices (in this order): v83-pumice-onyx-kelp-harbor-basil-amber, v32-nectar-pumice-ember-amber-maple-kelp, v56-russet-basil-lumen-ember-quartz-nectar, v55-kelp-dune-amber-ember-quartz-garnet, v25-onyx-amber-pumice-nectar-maple-juniper, v16-onyx-russet-lumen-juniper-cedar-harbor, v49-amber-harbor-nectar-kelp-garnet-lumen, v71-fjord-harbor-maple-pumice-indigo-cedar, v80-quartz-amber-garnet-ember-fjord-harbor, v13-maple-juniper-pumice-basil-kelp-harbor, v62-cedar-ember-onyx-harbor-garnet-fjord, v94-juniper-ember-cedar-russet-amber-lumen
Edges (in this order):
v83-pumice-onyx-kelp-harbor-basil-amber - v49-amber-harbor-nectar-kelp-garnet-lumen
v83-pumice-onyx-kelp-harbor-basil-amber - v80-quartz-amber-garnet-ember-fjord-harbor
v32-nectar-pumice-ember-amber-maple-kelp - v80-quartz-amber-garnet-ember-fjord-harbor
v56-russet-basil-lumen-ember-quartz-nectar - v16-onyx-russet-lumen-juniper-cedar-harbor
v56-russet-basil-lumen-ember-quartz-nectar - v13-maple-juniper-pumice-basil-kelp-harbor
v55-kelp-dune-amber-ember-quartz-garnet - v16-onyx-russet-lumen-juniper-cedar-harbor
v55-kelp-dune-amber-ember-quartz-garnet - v80-quartz-amber-garnet-ember-fjord-harbor
v55-kelp-dune-amber-ember-quartz-garnet - v62-cedar-ember-onyx-harbor-garnet-fjord
v25-onyx-amber-pumice-nectar-maple-juniper - v80-quartz-amber-garnet-ember-fjord-harbor
v25-onyx-amber-pumice-nectar-maple-juniper - v13-maple-juniper-pumice-basil-kelp-harbor
v16-onyx-russet-lumen-juniper-cedar-harbor - v94-juniper-ember-cedar-russet-amber-lumen
v49-amber-harbor-nectar-kelp-garnet-lumen - v80-quartz-amber-garnet-ember-fjord-harbor
v49-amber-harbor-nectar-kelp-garnet-lumen - v94-juniper-ember-cedar-russet-amber-lumen
v71-fjord-harbor-maple-pumice-indigo-cedar - v80-quartz-amber-garnet-ember-fjord-harbor
v71-fjord-harbor-maple-pumice-indigo-cedar - v94-juniper-ember-cedar-russet-amber-lumen
v80-quartz-amber-garnet-ember-fjord-harbor - v13-maple-juniper-pumice-basil-kelp-harbor
v13-maple-juniper-pumice-basil-kelp-harbor - v94-juniper-ember-cedar-russet-amber-lumen
v62-cedar-ember-onyx-harbor-garnet-fjord - v94-juniper-ember-cedar-russet-amber-lumen
Colour every vertex with one of the colours 1, 2, 3 so that the two ends of every edge get different colours.

Think it through as carefully as you need. If no such colouring exists, finish with the line "ANSWER: IMPOSSIBLE". Otherwise finish with the line "ANSWER:" followed by one line `vertex: colour` per vertex, in this order: v83-pumice-onyx-kelp-harbor-basil-amber, v32-nectar-pumice-ember-amber-maple-kelp, v56-russet-basil-lumen-ember-quartz-nectar, v55-kelp-dune-amber-ember-quartz-garnet, v25-onyx-amber-pumice-nectar-maple-juniper, v16-onyx-russet-lumen-juniper-cedar-harbor, v49-amber-harbor-nectar-kelp-garnet-lumen, v71-fjord-harbor-maple-pumice-indigo-cedar, v80-quartz-amber-garnet-ember-fjord-harbor, v13-maple-juniper-pumice-basil-kelp-harbor, v62-cedar-ember-onyx-harbor-garnet-fjord, v94-juniper-ember-cedar-russet-amber-lumen.
```

**Prompt, X** (CNF with named atoms v37.1 (statements of C, labels of G)):

```
Atoms: for each vertex v of a graph and each colour c in 1, 2, 3, the atom v.c means "vertex v has colour c" (so v37.2 means vertex v37 has colour 2).
CNF formula over 36 atoms (v13.1 to v94.3) with 102 clauses (in this order):
(v83.1 ∨ v83.2 ∨ v83.3)
(v32.1 ∨ v32.2 ∨ v32.3)
(v56.1 ∨ v56.2 ∨ v56.3)
(v55.1 ∨ v55.2 ∨ v55.3)
(v25.1 ∨ v25.2 ∨ v25.3)
(v16.1 ∨ v16.2 ∨ v16.3)
(v49.1 ∨ v49.2 ∨ v49.3)
(v71.1 ∨ v71.2 ∨ v71.3)
(v80.1 ∨ v80.2 ∨ v80.3)
(v13.1 ∨ v13.2 ∨ v13.3)
(v62.1 ∨ v62.2 ∨ v62.3)
(v94.1 ∨ v94.2 ∨ v94.3)
… (86 lines omitted; full prompt in the JSONL) …
(¬v13.3 ∨ ¬v94.3)
(¬v62.1 ∨ ¬v94.1)
(¬v62.2 ∨ ¬v94.2)
(¬v62.3 ∨ ¬v94.3)
Find an assignment of true/false to the atoms that makes every clause true.

Think it through as carefully as you need. If no such assignment exists, finish with the line "ANSWER: UNSAT". Otherwise finish with the line "ANSWER:" followed by the atoms you set to true, separated by spaces (every other atom is false).
```

**Prompt, C-DIMACS** (C in DIMACS notation (fewer tokens)):

```
A CNF formula in DIMACS format. Each line after the header is one clause: the literals in the clause, ending in 0. A positive number i means variable i is true; a negative number -i means variable i is false.
p cnf 36 102
31 32 33 0
10 11 12 0
19 20 21 0
16 17 18 0
7 8 9 0
4 5 6 0
13 14 15 0
25 26 27 0
28 29 30 0
1 2 3 0
22 23 24 0
34 35 36 0
… (86 lines omitted; full prompt in the JSONL) …
-3 -36 0
-22 -34 0
-23 -35 0
-24 -36 0
Find an assignment of true/false to the variables that makes every clause true.

Think it through as carefully as you need. If no such assignment exists, finish with the line "ANSWER: UNSAT". Otherwise finish with the line "ANSWER:" followed by the numbers of the variables you set to true, separated by spaces (every other variable is false).
```

**Predictions per encoding** (canonical answer):

| Member (family, home) | G-PAD | X | C-DIMACS |
|---|---|---|---|
| `FF-LIST` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=UC-INDEX | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ |
| `LF` (C1, graph) | LF | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC ᵗ | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC ᵗ | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G-PAD: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / X: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / C-DIMACS: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** G-PAD: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G-PAD (translation rate; measured from traces in the real run). / X: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.9 for X (translation rate; measured from traces in the real run). / C-DIMACS: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C-DIMACS (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Item-level evidence, G-PAD** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `UC-DET-INDEX` 6.0, `GUC-DET` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.18 · H-surface +0.00 |
| answer = fingerprint #1 (DPLL-INDEX, FF-LABEL, UC-DET-INDEX) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #2 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #4 (GUC-DET) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.16 · H-surface +0.00 |
| answer = fingerprint #5 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.15 · H-surface +0.00 |
| another valid colouring (no member predicts it) | `RANDOM` 3.6, `LF` 2.0, `DSATUR` 2.0, `DPLL-DSATUR` 2.0, `DPLL-OCC` 2.0, `FF-LIST` 1.8 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.03 · H-surface +0.00 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.49 · H-formalism +0.49 · H-translate +0.49 · H-length +0.00 · H-surface +0.49 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.09 · H-surface +0.00 |

### E2 · I-E1-B2 · base 2

**Ground truth:** colourable = True, n_colourings = 552, n_partitions = 92 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** G-PAD: 1248 tokens, 18 statements · X: 1699 tokens, 102 statements · C-DIMACS: 855 tokens, 102 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | G-PAD | X | C-DIMACS |
|---|---|---|---|
| `FF-LIST` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=UC-INDEX | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ |
| `LF` (C1, graph) | LF | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR | DSATUR ᵗ | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=UC=DROP | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC ᵗ | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC ᵗ | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=UC=DROP ᵗ | LIST=UC=DROP | LIST=UC=DROP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G-PAD: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / X: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / C-DIMACS: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** G-PAD: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G-PAD (translation rate; measured from traces in the real run). / X: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.9 for X (translation rate; measured from traces in the real run). / C-DIMACS: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C-DIMACS (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Item-level evidence, G-PAD** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `UC-DET-INDEX` 6.0, `GUC-DET` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.18 · H-surface +0.00 |
| answer = fingerprint #1 (DPLL-INDEX, FF-LABEL, UC-DET-INDEX) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #2 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #4 (GUC-DET) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.16 · H-surface +0.00 |
| answer = fingerprint #5 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.16 · H-surface +0.00 |
| another valid colouring (no member predicts it) | `RANDOM` 3.3, `DPLL-OCC` 2.0, `FF-LIST` 1.8, `FF-LIST-INFEAS` 1.8, `FF-LABEL` 1.8, `DPLL-LIST` 1.8 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.01 · H-surface +0.00 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.50 · H-formalism +0.50 · H-translate +0.50 · H-length +0.00 · H-surface +0.50 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.09 · H-surface +0.00 |

## E3. Translation dial

- **Reasoning question.** Does making the reduction visible move the weights toward the graph profile (H-translate), or do the weights follow the surface formalism whatever the model is told (H-formalism)?
- **Varied:** Header: none (E1's C and L) / neutral / legend; variable numbering: natural / scrambled.
- **Controlled:** Clauses and clause order; legend and neutral header within ±1.3% tokens of each other.
- **Pre-registered eval-level predictions** (from the hypothesis blocks):
  - **H-structure:** No dial effect: π on C-SCRAMBLE, C-NEUTRAL, C-HINT, L-NEUTRAL, L-HINT all within ±0.05 of G.
  - **H-formalism:** No dial effect, but all C/L arms differ from G by HAI >= 0.10; HINT − NEUTRAL within ±0.05.
  - **H-translate:** Monotone dial: graph-home weight SCRAMBLE < NEUTRAL < HINT, with Δπ(HINT − SCRAMBLE) >= 0.10 and the change in tau predicting the change in π (slope 0.5–2 of the predicted).
  - **H-length:** HINT and NEUTRAL (token-matched) equal; SCRAMBLE equal to C (same tokens).
  - **H-surface:** C-arms and L-arms differ by the same surface shift as in E1; no dial effect.

### E3 · I-E1-B1 · dial: scrambled

**Ground truth:** colourable = True, n_colourings = 228, n_partitions = 38 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** C-SCRAMBLE: 1214 tokens, 102 statements.

**Prompt, C-SCRAMBLE** (C with variable numbers permuted):

```
CNF formula over 36 Boolean variables (x01 to x36) with 102 clauses (in this order):
(x11 ∨ x33 ∨ x25)
(x10 ∨ x20 ∨ x15)
(x26 ∨ x04 ∨ x32)
(x18 ∨ x28 ∨ x23)
(x22 ∨ x08 ∨ x31)
(x07 ∨ x14 ∨ x12)
(x34 ∨ x24 ∨ x03)
(x36 ∨ x01 ∨ x16)
(x17 ∨ x06 ∨ x35)
(x21 ∨ x30 ∨ x13)
(x19 ∨ x05 ∨ x29)
(x02 ∨ x09 ∨ x27)
(¬x11 ∨ ¬x33)
… (85 lines omitted; full prompt in the JSONL) …
(¬x13 ∨ ¬x27)
(¬x19 ∨ ¬x02)
(¬x05 ∨ ¬x09)
(¬x29 ∨ ¬x27)
Find an assignment of true/false to the variables that makes every clause true.

Think it through as carefully as you need. If no such assignment exists, finish with the line "ANSWER: UNSAT". Otherwise finish with the line "ANSWER:" followed by the variables you set to true, separated by spaces (every other variable is false).
```

**Predictions per encoding** (canonical answer):

| Member (family, home) | C-SCRAMBLE |
|---|---|
| `FF-LIST` (C1, graph) | LIST=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | n.a. ⁿ |
| `LF` (C1, graph) | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP |
| `UC-DET` (C2, cnf) | LIST=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=UC=DROP |
| `FIRST` (B4, logic) | IMP |
| `BICOND` (B4, logic) | IMP ᵗ |
| `ONL(1)` (C4, logic) | IMP |
| `ONL(64)` (C4, logic) | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid |
| `RO-FF` (C3, graph) | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution ᵗ |
| `WALK` (F, cnf) | distribution |
| `ALWAYS-NO` (A1, any) | IMP |
| `RANDOM` (H, any) | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.3 for C-SCRAMBLE (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Item-level evidence, C-SCRAMBLE** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `GUC-DET` 6.0, `DPLL-OCC` 6.0, `RANDOM` 5.2 | H-structure +0.00 · H-formalism +0.08 · H-translate +0.06 · H-length +0.18 · H-surface +0.00 |
| answer = fingerprint #1 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0, `DPLL-DSATUR` 6.0 | H-structure +0.00 · H-formalism +0.33 · H-translate +0.21 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #2 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0, `DROP-LAST-1` 6.0 | H-structure +0.00 · H-formalism +0.63 · H-translate +0.34 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-INDEX, UC-DET-INDEX) | `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `GUC-DET` 6.0, `DPLL-OCC` 6.0, `RO-FF` 6.0 | H-structure +0.81 · H-formalism +0.00 · H-translate +0.12 · H-length +0.64 · H-surface +0.81 |
| answer = fingerprint #4 (GUC-DET) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.60 · H-formalism +0.00 · H-translate +0.11 · H-length +0.76 · H-surface +0.60 |
| answer = fingerprint #5 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.32 · H-formalism +0.00 · H-translate +0.07 · H-length +0.47 · H-surface +0.32 |
| another valid colouring (no member predicts it) | `RANDOM` 3.7, `FF-LIST` 2.0, `FF-LIST-INFEAS` 2.0, `LF` 2.0, `DSATUR` 2.0, `DPLL-LIST` 2.0 | H-structure +0.03 · H-formalism +0.00 · H-translate +0.01 · H-length +0.09 · H-surface +0.03 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.49 · H-formalism +0.61 · H-translate +0.57 · H-length +0.00 · H-surface +0.49 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.49 · H-formalism +0.00 · H-translate +0.10 · H-length +0.58 · H-surface +0.49 |

### E3 · I-E1-B1 · dial

**Ground truth:** colourable = True, n_colourings = 228, n_partitions = 38 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** C-NEUTRAL: 1274 tokens, 102 statements · C-HINT: 1290 tokens, 102 statements · L-NEUTRAL: 2506 tokens, 102 statements · L-HINT: 2522 tokens, 102 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | C-NEUTRAL | C-HINT | L-NEUTRAL | L-HINT |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ |
| `LF` (C1, graph) | LF ᵗ | LF ᵗ | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR ᵗ | DSATUR ᵗ | DSATUR ᵗ | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR ᵗ | DSATUR ᵗ | DSATUR ᵗ | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP | IMP | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP | IMP | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX | LABEL=UC-INDEX | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC | GUC | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX | LABEL=UC-INDEX | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC | OCC | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP | LIST=UC=DROP |
| `FIRST` (B4, logic) | IMP | IMP | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(1)` (C4, logic) | IMP | IMP | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP | IMP | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution ᵗ | distribution ᵗ | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution ᵗ | distribution ᵗ | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution | distribution | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** C-NEUTRAL: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / C-HINT: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L-NEUTRAL: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here. / L-HINT: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** C-NEUTRAL: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C-NEUTRAL (translation rate; measured from traces in the real run). / C-HINT: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.95 for C-HINT (translation rate; measured from traces in the real run). / L-NEUTRAL: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L-NEUTRAL (translation rate; measured from traces in the real run). / L-HINT: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.95 for L-HINT (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Item-level evidence, C-NEUTRAL** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `UC-DET-INDEX` 6.0, `GUC-DET` 6.0 | H-structure +0.00 · H-formalism +0.07 · H-translate +0.03 · H-length +0.18 · H-surface +0.00 |
| answer = fingerprint #1 (DPLL-INDEX, FF-LABEL, UC-DET-INDEX) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.14 · H-formalism +0.00 · H-translate +0.08 · H-length +0.31 · H-surface +0.14 |
| answer = fingerprint #2 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.32 · H-translate +0.10 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.61 · H-translate +0.16 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #4 (GUC-DET) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.62 · H-formalism +0.00 · H-translate +0.26 · H-length +0.78 · H-surface +0.62 |
| answer = fingerprint #5 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.33 · H-formalism +0.00 · H-translate +0.17 · H-length +0.48 · H-surface +0.33 |
| another valid colouring (no member predicts it) | `RANDOM` 3.6, `LF` 2.0, `DSATUR` 2.0, `DPLL-DSATUR` 2.0, `DPLL-OCC` 2.0, `FF-LIST` 1.8 | H-structure +0.04 · H-formalism +0.00 · H-translate +0.03 · H-length +0.08 · H-surface +0.04 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.49 · H-formalism +0.61 · H-translate +0.53 · H-length +0.00 · H-surface +0.49 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.50 · H-formalism +0.00 · H-translate +0.23 · H-length +0.59 · H-surface +0.50 |

## E4. Feasibility near the threshold: dead ends and collapse

- **Reasoning question.** Where do false IMPOSSIBLE answers come from in each formalism: first-fit dead ends (C1), unit-propagation dead ends (C2), collapse members that read the surface (POLARITY, GREEDY, FIRST, BICOND, ONL), or truncated search (D)? Does B1's drop-the-last-constraint error (false 'possible') depend on formalism?
- **Varied:** Cell (a1: FF dead end rescued by UC-DET; a2: FF and UC-DET dead ends; b: no constructive member fails; c: not colourable, last edge critical; c-twin: c minus its last edge) × encoding (G, S, C, L).
- **Controlled:** Within a cell set, the instance; between c and c-twin, the encoding (truth flips with one edge).
- **Pre-registered eval-level predictions** (from the hypothesis blocks):
  - **H-structure:** Cell contrasts (a1 − b), (a2 − a1), (c-twin − b) and the collapse rate in cell b equal across encodings (each Δ within ±0.05) once every member's native prediction is applied.
  - **H-formalism:** Collapse rate (false IMPOSSIBLE in cell b, where no constructive member fails) >= 0.10 on C/L and <= 0.03 on G/S; the first-fit dead-end contrast (a1 − b) larger on G/S than on C/L by >= 0.10 (first-fit is graph-home; unit propagation rescues a1 on C/L).
  - **H-translate:** C/L cell pattern = tau·(G/S pattern) + (1 − tau)·(C/L-home pattern), tau from traces; collapse answers come from untranslated traces (odds ratio >= 2).
  - **H-length:** Error rates rise with tokens in every cell by the same amount: no cell × encoding interaction beyond PERCEPTION-NOISE's computed one (cell c: false 'possible' 0.09 on G/S vs 0.34 on C/L at a 3% per-statement drop rate).
  - **H-surface:** Cell pattern shared within {S, L} and within {G, C}.

### E4 · I-E4-a1 · a1

**Ground truth:** colourable = True, n_colourings = 36, n_partitions = 6 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

*Colourable. FF-LIST dead-ends; UC-DET (unit propagation first) and DSATUR succeed.*

**Length per encoding:** G: 316 tokens, 24 statements · S: 322 tokens, 24 statements · C: 1412 tokens, 120 statements · L: 2961 tokens, 120 statements.

**Prompt, G** (graph colouring, symbolic labels):

```
Graph with 12 vertices and 24 edges.
Vertices (in this order): v52, v69, v30, v76, v19, v14, v36, v45, v12, v86, v35, v89
Edges (in this order):
v52 - v76
v52 - v36
v52 - v35
v69 - v30
v69 - v76
v69 - v19
v69 - v14
v69 - v12
v30 - v12
v30 - v35
v30 - v89
… (9 lines omitted; full prompt in the JSONL) …
v45 - v86
v12 - v86
v12 - v89
v35 - v89
Colour every vertex with one of the colours 1, 2, 3 so that the two ends of every edge get different colours.

Think it through as carefully as you need. If no such colouring exists, finish with the line "ANSWER: IMPOSSIBLE". Otherwise finish with the line "ANSWER:" followed by one line `vertex: colour` per vertex, in this order: v52, v69, v30, v76, v19, v14, v36, v45, v12, v86, v35, v89.
```

**Prompt, S** (story: exam timetable):

```
A school must timetable 12 exams into three slots: slot 1, slot 2 and slot 3.
Exams (in this order): Rhetoric, Statistics, Journalism, Tectonics, Finance, Ecology, Optics, Poetry, Ceramics, Virology, Nutrition, Welding
Some pairs of exams share a student, so the two exams in each pair must be in different slots. The pairs are (in this order):
Rhetoric and Tectonics
Rhetoric and Optics
Rhetoric and Nutrition
Statistics and Journalism
Statistics and Tectonics
Statistics and Finance
Statistics and Ecology
Statistics and Ceramics
Journalism and Ceramics
Journalism and Nutrition
Journalism and Welding
… (9 lines omitted; full prompt in the JSONL) …
Poetry and Virology
Ceramics and Virology
Ceramics and Welding
Nutrition and Welding
Put every exam in one of the three slots so that no student has two exams in the same slot.

Think it through as carefully as you need. If no such timetable exists, finish with the line "ANSWER: IMPOSSIBLE". Otherwise finish with the line "ANSWER:" followed by one line `exam: slot` per exam, in this order: Rhetoric, Statistics, Journalism, Tectonics, Finance, Ecology, Optics, Poetry, Ceramics, Virology, Nutrition, Welding.
```

**Prompt, C** (CNF, opaque variables):

```
CNF formula over 36 Boolean variables (x01 to x36) with 120 clauses (in this order):
(x22 ∨ x23 ∨ x24)
(x25 ∨ x26 ∨ x27)
(x10 ∨ x11 ∨ x12)
(x28 ∨ x29 ∨ x30)
(x07 ∨ x08 ∨ x09)
(x04 ∨ x05 ∨ x06)
(x16 ∨ x17 ∨ x18)
(x19 ∨ x20 ∨ x21)
(x01 ∨ x02 ∨ x03)
(x31 ∨ x32 ∨ x33)
(x13 ∨ x14 ∨ x15)
(x34 ∨ x35 ∨ x36)
(¬x22 ∨ ¬x23)
… (103 lines omitted; full prompt in the JSONL) …
(¬x03 ∨ ¬x36)
(¬x13 ∨ ¬x34)
(¬x14 ∨ ¬x35)
(¬x15 ∨ ¬x36)
Find an assignment of true/false to the variables that makes every clause true.

Think it through as carefully as you need. If no such assignment exists, finish with the line "ANSWER: UNSAT". Otherwise finish with the line "ANSWER:" followed by the variables you set to true, separated by spaces (every other variable is false).
```

**Prompt, L** (English premises, clause for clause):

```
Here are some statements:
1. The Rhetoric exam is in slot 1, slot 2 or slot 3.
2. The Statistics exam is in slot 1, slot 2 or slot 3.
3. The Journalism exam is in slot 1, slot 2 or slot 3.
4. The Tectonics exam is in slot 1, slot 2 or slot 3.
5. The Finance exam is in slot 1, slot 2 or slot 3.
6. The Ecology exam is in slot 1, slot 2 or slot 3.
7. The Optics exam is in slot 1, slot 2 or slot 3.
8. The Poetry exam is in slot 1, slot 2 or slot 3.
9. The Ceramics exam is in slot 1, slot 2 or slot 3.
10. The Virology exam is in slot 1, slot 2 or slot 3.
11. The Nutrition exam is in slot 1, slot 2 or slot 3.
12. The Welding exam is in slot 1, slot 2 or slot 3.
13. If the Rhetoric exam is in slot 1, then the Rhetoric exam is not in slot 2.
… (103 lines omitted; full prompt in the JSONL) …
117. If the Ceramics exam is in slot 3, then the Welding exam is not in slot 3.
118. If the Nutrition exam is in slot 1, then the Welding exam is not in slot 1.
119. If the Nutrition exam is in slot 2, then the Welding exam is not in slot 2.
120. If the Nutrition exam is in slot 3, then the Welding exam is not in slot 3.
Question: Can all of these statements be true at the same time? If they can, describe a situation in which they are all true.

Think it through as carefully as you need. If they cannot all be true, finish with the line "ANSWER: NO". Otherwise finish with the line "ANSWER:" followed by one line `exam: slot` per exam, in this order: Rhetoric, Statistics, Journalism, Tectonics, Finance, Ecology, Optics, Poetry, Ceramics, Virology, Nutrition, Welding.
```

**Predictions per encoding** (canonical answer):

| Member (family, home) | G | S | C | L |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | invalid | invalid | invalid ᵗ | invalid ᵗ |
| `FF-LABEL` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `LF` (C1, graph) | DSATUR=LF | DSATUR=LF | DSATUR=LF ᵗ | DSATUR=LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR=LF | DSATUR=LF | DSATUR=LF ᵗ | DSATUR=LF ᵗ |
| `DPLL-LIST` (D, graph) | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR=LF | DSATUR=LF | DSATUR=LF ᵗ | DSATUR=LF ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GUC-DET` (C2, cnf) | GUC ᵗ | GUC ᵗ | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL ᵗ | LABEL ᵗ | LABEL | LABEL |
| `DPLL-OCC` (D, cnf) | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP |
| `DPLL-MENTION-b24` (D, cnf) | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |
| `PERCEPTION-NOISE` (nuisance, any) | P(answer possible) = 1.000 | P(answer possible) = 1.000 | P(answer possible) = 1.000 | P(answer possible) = 1.000 |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| IMPOSSIBLE in G and S; valid in C and L | 0.14 | 0.00 | 0.08 | 0.32 | 0.12 |
| valid in G and S; IMPOSSIBLE in C and L | 0.02 | 0.21 | 0.09 | 0.34 | 0.00 |
| IMPOSSIBLE in all four | 0.00 | 0.19 | 0.07 | 0.32 | 0.08 |
| valid in all four | 0.14 | 0.00 | 0.08 | 0.32 | 0.02 |
| invalid colouring in all four | 0.67 | 1.21 | 0.85 | 0.00 | 1.23 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `FF-LIST-INFEAS` 6.0, `RANDOM` 4.5, `FF-LIST` 1.0, `FF-LABEL` 1.0, `POLARITY` 1.0, `GREEDY-MENTION` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| an invalid colouring | `FF-LIST` 6.0, `FF-LABEL` 6.0, `POLARITY` 6.0, `GREEDY-MENTION` 6.0, `UC-DET-INDEX` 6.0, `FIRST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0, `DPLL-DSATUR` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `FF-LIST-INFEAS` 6.0, `RANDOM` 4.5, `FF-LIST` 1.0, `FF-LABEL` 1.0, `POLARITY` 1.0, `GREEDY-MENTION` 1.0 | H-structure +0.08 · H-formalism +0.00 · H-translate +0.05 · H-length +0.17 · H-surface +0.08 |
| an invalid colouring | `FF-LIST` 6.0, `FF-LABEL` 6.0, `POLARITY` 6.0, `GREEDY-MENTION` 6.0, `UC-DET-INDEX` 6.0, `FIRST` 6.0 | H-structure +0.33 · H-formalism +0.59 · H-translate +0.42 · H-length +0.00 · H-surface +0.33 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0, `DPLL-DSATUR` 6.0 | H-structure +0.00 · H-formalism +0.15 · H-translate +0.05 · H-length +0.16 · H-surface +0.00 |

### E4 · I-E4-a2 · a2

**Ground truth:** colourable = True, n_colourings = 6, n_partitions = 1 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

*Colourable. FF-LIST and UC-DET both dead-end; DSATUR succeeds.*

**Length per encoding:** G: 304 tokens, 22 statements · S: 317 tokens, 22 statements · C: 1346 tokens, 114 statements · L: 2808 tokens, 114 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | G | S | C | L |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | invalid | invalid | invalid ᵗ | invalid ᵗ |
| `FF-LABEL` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `LF` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `DSATUR` (C2, graph) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ |
| `DPLL-LIST` (D, graph) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ |
| `DPLL-DSATUR` (D, graph) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET-INDEX` (C2, cnf) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX |
| `GUC-DET` (C2, cnf) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX |
| `DPLL-MENTION` (D, cnf) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX |
| `DPLL-INDEX` (D, cnf) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX |
| `DPLL-OCC` (D, cnf) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX |
| `DPLL-MENTION-b24` (D, cnf) | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX ᵗ | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX | LIST=LABEL=DSATUR=GUC=OCC=DROP=UC-INDEX |
| `FIRST` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |
| `PERCEPTION-NOISE` (nuisance, any) | P(answer possible) = 1.000 | P(answer possible) = 1.000 | P(answer possible) = 1.000 | P(answer possible) = 1.000 |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| IMPOSSIBLE in G and S; valid in C and L | 0.10 | 0.00 | 0.06 | 0.24 | 0.01 |
| valid in G and S; IMPOSSIBLE in C and L | 0.10 | 0.02 | 0.06 | 0.43 | 0.00 |
| IMPOSSIBLE in all four | 0.10 | 0.03 | 0.07 | 0.43 | 0.00 |
| valid in all four | 0.10 | 0.00 | 0.06 | 0.24 | 0.01 |
| invalid colouring in all four | 0.61 | 1.33 | 0.83 | 0.00 | 1.34 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `FF-LIST-INFEAS` 6.0, `RANDOM` 5.2, `MIN-CONFLICTS` 1.3, `FF-LIST` 1.0, `FF-LABEL` 1.0, `LF` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| an invalid colouring | `FF-LIST` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `POLARITY` 6.0, `GREEDY-MENTION` 6.0, `UC-DET` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST-INFEAS` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0, `DPLL-DSATUR` 6.0, `DROP-LAST-1` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `FF-LIST-INFEAS` 6.0, `RANDOM` 5.2, `MIN-CONFLICTS` 1.3, `FF-LIST` 1.0, `FF-LABEL` 1.0, `LF` 1.0 | H-structure +0.06 · H-formalism +0.00 · H-translate +0.03 · H-length +0.13 · H-surface +0.06 |
| an invalid colouring | `FF-LIST` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `POLARITY` 6.0, `GREEDY-MENTION` 6.0, `UC-DET` 6.0 | H-structure +0.30 · H-formalism +0.66 · H-translate +0.41 · H-length +0.00 · H-surface +0.30 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST-INFEAS` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0, `DPLL-DSATUR` 6.0, `DROP-LAST-1` 6.0 | H-structure +0.03 · H-formalism +0.00 · H-translate +0.02 · H-length +0.19 · H-surface +0.03 |

### E4 · I-E4-b · b

**Ground truth:** colourable = True, n_colourings = 24, n_partitions = 4 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

*Colourable. FF-LIST, UC-DET and DSATUR all succeed: only collapse members (POLARITY, GREEDY, FIRST, BICOND, ONL) and cues say IMPOSSIBLE.*

**Length per encoding:** G: 304 tokens, 22 statements · S: 307 tokens, 22 statements · C: 1346 tokens, 114 statements · L: 2793 tokens, 114 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | G | S | C | L |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX ᵗ | LABEL=DSATUR=LF=UC-INDEX ᵗ |
| `LF` (C1, graph) | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX ᵗ | LABEL=DSATUR=LF=UC-INDEX ᵗ |
| `DSATUR` (C2, graph) | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX ᵗ | LABEL=DSATUR=LF=UC-INDEX ᵗ |
| `DPLL-LIST` (D, graph) | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX ᵗ | LABEL=DSATUR=LF=UC-INDEX ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=DSATUR=LF=UC-INDEX ᵗ | LABEL=DSATUR=LF=UC-INDEX ᵗ | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC ᵗ | GUC ᵗ | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=DSATUR=LF=UC-INDEX ᵗ | LABEL=DSATUR=LF=UC-INDEX ᵗ | LABEL=DSATUR=LF=UC-INDEX | LABEL=DSATUR=LF=UC-INDEX |
| `DPLL-OCC` (D, cnf) | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP |
| `DPLL-MENTION-b24` (D, cnf) | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP ᵗ | LIST=OCC=UC=DROP | LIST=OCC=UC=DROP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |
| `PERCEPTION-NOISE` (nuisance, any) | P(answer possible) = 1.000 | P(answer possible) = 1.000 | P(answer possible) = 1.000 | P(answer possible) = 1.000 |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| IMPOSSIBLE in G and S; valid in C and L | 0.62 | 0.67 | 0.64 | 0.94 | 0.00 |
| valid in G and S; IMPOSSIBLE in C and L | 1.16 | 0.00 | 0.50 | 1.33 | 0.54 |
| IMPOSSIBLE in all four | 1.32 | 0.15 | 0.66 | 1.49 | 0.00 |
| valid in all four | 0.00 | 0.05 | 0.02 | 0.32 | 0.07 |
| invalid colouring in all four | 0.91 | 1.28 | 1.04 | 0.00 | 1.31 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `RANDOM` 4.7, `POLARITY` 1.0, `GREEDY-MENTION` 1.0, `FIRST` 1.0, `BICOND` 1.0, `ONL(1)` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| an invalid colouring | `POLARITY` 5.9, `GREEDY-MENTION` 5.9, `FIRST` 5.9, `BICOND` 5.9, `ONL(1)` 5.9, `ONL(64)` 5.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `RANDOM` 4.7, `POLARITY` 1.0, `GREEDY-MENTION` 1.0, `FIRST` 1.0, `BICOND` 1.0, `ONL(1)` 1.0 | H-structure +0.00 · H-formalism +0.01 · H-translate +0.01 · H-length +0.16 · H-surface +0.00 |
| an invalid colouring | `POLARITY` 5.9, `GREEDY-MENTION` 5.9, `FIRST` 5.9, `BICOND` 5.9, `ONL(1)` 5.9, `ONL(64)` 5.9 | H-structure +0.45 · H-formalism +0.63 · H-translate +0.52 · H-length +0.00 · H-surface +0.45 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.50 · H-formalism +0.00 · H-translate +0.23 · H-length +0.59 · H-surface +0.50 |

### E4 · I-E4-c · c

**Ground truth:** colourable = False, n_colourings = 0, n_partitions = 0 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

*Not colourable; removing the last-listed edge makes it colourable (B1 DROP-LAST-1 says possible). Truth twin of c-twin.*

**Length per encoding:** G: 304 tokens, 22 statements · S: 315 tokens, 22 statements · C: 1346 tokens, 114 statements · L: 2809 tokens, 114 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | G | S | C | L |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | invalid | invalid | invalid ᵗ | invalid ᵗ |
| `FF-LABEL` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `LF` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `DSATUR` (C2, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `DPLL-LIST` (D, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `DPLL-LIST-b12` (D, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `DPLL-DSATUR` (D, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `DROP-LAST-1` (B1, graph) | invalid | invalid | invalid ᵗ | invalid ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET-INDEX` (C2, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GUC-DET` (C2, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `DPLL-MENTION` (D, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `DPLL-INDEX` (D, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `DPLL-OCC` (D, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `DPLL-MENTION-b24` (D, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |
| `PERCEPTION-NOISE` (nuisance, any) | P(answer possible) = 0.086 | P(answer possible) = 0.086 | P(answer possible) = 0.343 | P(answer possible) = 0.343 |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| IMPOSSIBLE in G and S; valid in C and L | 0.03 | 0.03 | 0.03 | 0.03 | 0.00 |
| valid in G and S; IMPOSSIBLE in C and L | 0.06 | 0.00 | 0.03 | 0.40 | 0.03 |
| IMPOSSIBLE in all four | 0.06 | 0.00 | 0.03 | 0.40 | 0.00 |
| valid in all four | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| invalid colouring in all four | 0.65 | 0.88 | 0.74 | 0.00 | 0.88 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| an invalid colouring | `RO-FF` 6.0, `FF-LIST` 1.0, `FF-LABEL` 1.0, `LF` 1.0, `DSATUR` 1.0, `DPLL-LIST` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST-INFEAS` 6.0, `DROP-LAST-1` 6.0, `RO-FF` 6.0, `MIN-CONFLICTS` 6.0, `WALK` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| an invalid colouring | `RO-FF` 6.0, `FF-LIST` 1.0, `FF-LABEL` 1.0, `LF` 1.0, `DSATUR` 1.0, `DPLL-LIST` 1.0 | H-structure +0.32 · H-formalism +0.44 · H-translate +0.37 · H-length +0.00 · H-surface +0.32 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST-INFEAS` 6.0, `DROP-LAST-1` 6.0, `RO-FF` 6.0, `MIN-CONFLICTS` 6.0, `WALK` 6.0 | H-structure +0.03 · H-formalism +0.00 · H-translate +0.02 · H-length +0.20 · H-surface +0.03 |

### E4 · I-E4-c-twin · c-twin

**Ground truth:** colourable = True, n_colourings = 72, n_partitions = 12 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

*Twin of c with the last edge removed: colourable. Same encodings; the truth flips with one edge.*

**Length per encoding:** G: 298 tokens, 21 statements · S: 308 tokens, 21 statements · C: 1313 tokens, 111 statements · L: 2731 tokens, 111 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | G | S | C | L |
|---|---|---|---|---|
| `FF-LIST` (C1, graph) | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | IMP | IMP | IMP ᵗ | IMP ᵗ |
| `LF` (C1, graph) | LF | LF | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ |
| `DPLL-LIST` (D, graph) | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=GUC=UC-INDEX ᵗ | LABEL=GUC=UC-INDEX ᵗ | LABEL=GUC=UC-INDEX | LABEL=GUC=UC-INDEX |
| `GUC-DET` (C2, cnf) | LABEL=GUC=UC-INDEX ᵗ | LABEL=GUC=UC-INDEX ᵗ | LABEL=GUC=UC-INDEX | LABEL=GUC=UC-INDEX |
| `DPLL-MENTION` (D, cnf) | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=GUC=UC-INDEX ᵗ | LABEL=GUC=UC-INDEX ᵗ | LABEL=GUC=UC-INDEX | LABEL=GUC=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC ᵗ | OCC ᵗ | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP ᵗ | LIST=DSATUR=UC=DROP | LIST=DSATUR=UC=DROP |
| `FIRST` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP ᵗ | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP ᵗ | IMP ᵗ | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution | distribution | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution ᵗ | distribution ᵗ | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform | uniform | uniform |
| `PERCEPTION-NOISE` (nuisance, any) | P(answer possible) = 1.000 | P(answer possible) = 1.000 | P(answer possible) = 1.000 | P(answer possible) = 1.000 |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| IMPOSSIBLE in G and S; valid in C and L | 0.30 | 0.34 | 0.32 | 0.56 | 0.00 |
| valid in G and S; IMPOSSIBLE in C and L | 0.53 | 0.00 | 0.28 | 0.80 | 0.23 |
| IMPOSSIBLE in all four | 0.67 | 0.14 | 0.41 | 0.94 | 0.00 |
| valid in all four | 0.00 | 0.03 | 0.01 | 0.26 | 0.06 |
| invalid colouring in all four | 0.92 | 1.23 | 1.04 | 0.00 | 1.26 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `RANDOM` 4.2, `FF-LABEL` 1.0, `POLARITY` 1.0, `GREEDY-MENTION` 1.0, `FIRST` 1.0, `BICOND` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| an invalid colouring | `FF-LABEL` 5.8, `POLARITY` 5.8, `GREEDY-MENTION` 5.8, `FIRST` 5.8, `BICOND` 5.8, `ONL(1)` 5.8 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| a valid colouring | `RANDOM` 4.2, `FF-LABEL` 1.0, `POLARITY` 1.0, `GREEDY-MENTION` 1.0, `FIRST` 1.0, `BICOND` 1.0 | H-structure +0.00 · H-formalism +0.01 · H-translate +0.00 · H-length +0.13 · H-surface +0.00 |
| an invalid colouring | `FF-LABEL` 5.8, `POLARITY` 5.8, `GREEDY-MENTION` 5.8, `FIRST` 5.8, `BICOND` 5.8, `ONL(1)` 5.8 | H-structure +0.46 · H-formalism +0.60 · H-translate +0.51 · H-length +0.00 · H-surface +0.46 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.20 · H-formalism +0.00 · H-translate +0.11 · H-length +0.33 · H-surface +0.20 |

## E5. Backbone entailment: omission vs commission

- **Reasoning question.** Asked whether a vertex must take a colour, does the model under-conclude (propagation only: B1 UP-k / E WP-t), over-conclude from one model (C1/C2 READ, counter-model search), or solve exactly — and does the split depend on formalism? Does the fitted propagation depth count graph hops or statement rounds?
- **Varied:** Cell (F-UP: forced, two hops of propagation; F-CASE: forced only by case analysis; F-CASE-twin: one edge removed, not forced; NF-READ: not forced, first-fit's model says yes) × encoding.
- **Controlled:** Within a cell set, the instance and query; between F-CASE and its twin, the encoding.
- **Pre-registered eval-level predictions** (from the hypothesis blocks):
  - **H-structure:** Omission share (propagation only: NO on F-CASE) and commission share (single-model or counter-model construction: YES on NF-READ and F-CASE-twin) equal across encodings (±0.05); fitted propagation depth equal in graph hops (WP-t on G/S matches UP-2t on C/L).
  - **H-formalism:** Omission share higher on L and C than on G/S by >= 0.10 (deriving consequences is the home move in logic); commission share higher on G/S by >= 0.10 (building a colouring is the home move for graphs); fitted propagation depth equal in statement rounds (UP-k on C/L with k ≈ t on G/S, i.e. half the graph depth).
  - **H-translate:** C/L traces that translate (TR1/TR2) show the G/S split; untranslated ones show the C/L-home split.
  - **H-length:** Accuracy falls with tokens through symmetric slips; the omission / commission split is unchanged.
  - **H-surface:** Split shared within {S, L} and within {G, C}.

### E5 · I-E5-F-UP · F-UP

**Ground truth:** answer = YES, n_models = 6, share_of_models_with_query_true = 1.0 (verified by enumeration of all colourings extending the precolouring, PySAT: CNF plus the negated query is UNSAT iff YES).

*Forced, derivable by propagation: WP-2 (two graph hops) = UP-4; WP-1 = UP-2 do not reach it.*

**Length per encoding:** G: 241 tokens, 17 statements · S: 264 tokens, 17 statements · C: 1008 tokens, 87 statements · L: 2093 tokens, 87 statements.

**Prompt, G** (graph colouring, symbolic labels):

```
Graph with 10 vertices and 15 edges.
Vertices (in this order): v72, v59, v66, v12, v98, v56, v35, v45, v49, v13
Edges (in this order):
v72 - v12
v72 - v98
v59 - v66
v59 - v35
v66 - v12
v66 - v56
v12 - v98
v12 - v56
v98 - v56
v98 - v35
v98 - v13
v56 - v35
v56 - v49
v45 - v13
v49 - v13
Already coloured: v66 has colour 2, v56 has colour 1.
Consider every way of colouring all vertices with the colours 1, 2, 3 so that the two ends of every edge get different colours and the already-coloured vertices keep their colours.
Question: In every such colouring, does v98 have colour 2?

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**Prompt, S** (story: exam timetable):

```
A school must timetable 10 exams into three slots: slot 1, slot 2 and slot 3.
Exams (in this order): Statistics, Optics, Quilting, Botany, Welding, Mechanics, Harmony, Italian, Kinetics, Ceramics
Some pairs of exams share a student, so the two exams in each pair must be in different slots. The pairs are (in this order):
Statistics and Botany
Statistics and Welding
Optics and Quilting
Optics and Harmony
Quilting and Botany
Quilting and Mechanics
Botany and Welding
Botany and Mechanics
Welding and Mechanics
Welding and Harmony
Welding and Ceramics
Mechanics and Harmony
Mechanics and Kinetics
Italian and Ceramics
Kinetics and Ceramics
Already fixed: Quilting is in slot 2, Mechanics is in slot 1.
Consider every timetable that puts each exam in one of the three slots, keeps the fixed exams where they are, and never puts two exams that share a student in the same slot.
Question: In every such timetable, is Welding in slot 2?

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**Prompt, C** (CNF, opaque variables):

```
CNF formula over 30 Boolean variables (x01 to x30) with 87 clauses (in this order):
(x23)
(x16)
(x25 ∨ x26 ∨ x27)
(x19 ∨ x20 ∨ x21)
(x22 ∨ x23 ∨ x24)
(x01 ∨ x02 ∨ x03)
(x28 ∨ x29 ∨ x30)
(x16 ∨ x17 ∨ x18)
(x07 ∨ x08 ∨ x09)
(x10 ∨ x11 ∨ x12)
(x13 ∨ x14 ∨ x15)
(x04 ∨ x05 ∨ x06)
(¬x25 ∨ ¬x26)
… (70 lines omitted; full prompt in the JSONL) …
(¬x12 ∨ ¬x06)
(¬x13 ∨ ¬x04)
(¬x14 ∨ ¬x05)
(¬x15 ∨ ¬x06)
Question: Is x29 true in every assignment that makes every clause true?

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**Prompt, L** (English premises, clause for clause):

```
Here are some statements:
1. The Quilting exam is in slot 2.
2. The Mechanics exam is in slot 1.
3. The Statistics exam is in slot 1, slot 2 or slot 3.
4. The Optics exam is in slot 1, slot 2 or slot 3.
5. The Quilting exam is in slot 1, slot 2 or slot 3.
6. The Botany exam is in slot 1, slot 2 or slot 3.
7. The Welding exam is in slot 1, slot 2 or slot 3.
8. The Mechanics exam is in slot 1, slot 2 or slot 3.
9. The Harmony exam is in slot 1, slot 2 or slot 3.
10. The Italian exam is in slot 1, slot 2 or slot 3.
11. The Kinetics exam is in slot 1, slot 2 or slot 3.
12. The Ceramics exam is in slot 1, slot 2 or slot 3.
13. If the Statistics exam is in slot 1, then the Statistics exam is not in slot 2.
… (71 lines omitted; full prompt in the JSONL) …
85. If the Kinetics exam is in slot 1, then the Ceramics exam is not in slot 1.
86. If the Kinetics exam is in slot 2, then the Ceramics exam is not in slot 2.
87. If the Kinetics exam is in slot 3, then the Ceramics exam is not in slot 3.
Question: Does it follow that the Welding exam is in slot 2?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**Predictions per encoding:**

| Member | G | S | C | L |
|---|---|---|---|---|
| `EXACT` | YES | YES | YES | YES |
| `WP-1` | NO | NO | NO ᵗ | NO ᵗ |
| `WP-2` | YES | YES | YES ᵗ | YES ᵗ |
| `WP-inf` | YES | YES | YES ᵗ | YES ᵗ |
| `UP-2` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-3` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-4` | YES ᵗ | YES ᵗ | YES | YES |
| `UP-inf` | YES ᵗ | YES ᵗ | YES | YES |
| `FF-LIST-READ` | YES | YES | YES ᵗ | YES ᵗ |
| `DSATUR-READ` | YES | YES | YES ᵗ | YES ᵗ |
| `FF-CM` | YES | YES | YES ᵗ | YES ᵗ |
| `UC-READ` | YES ᵗ | YES ᵗ | YES | YES |
| `UC-CM` | YES ᵗ | YES ᵗ | YES | YES |
| `GREEDY-CM` | YES ᵗ | YES ᵗ | YES | YES |
| `FIRST` | NO ᵗ | NO ᵗ | NO | NO |
| `BICOND` | NO ᵗ | NO ᵗ | NO ᵗ | NO |
| `ONL(1)-reset` | YES ᵗ | YES ᵗ | NO | YES |
| `ONL(8)-reset` | YES ᵗ | YES ᵗ | NO | YES |
| `SAMPLE-3` | 1.0 | 1.0 | 1.0 | 1.0 |
| `ALWAYS-YES` | YES | YES | YES | YES |
| `ALWAYS-NO` | NO | NO | NO | NO |
| `ETR` | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| YES in all four | 0.00 | 0.03 | 0.01 | 0.26 | 0.04 |
| NO in all four | 0.69 | 0.56 | 0.63 | 0.00 | 0.51 |
| YES in G and S; NO in C and L | 0.67 | 0.54 | 0.61 | 0.00 | 0.60 |
| NO in G and S; YES in C and L | 0.07 | 0.10 | 0.08 | 0.31 | 0.00 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `WP-1` 1.0, `UP-2` 1.0, `UP-3` 1.0, `FIRST` 1.0, `BICOND` 1.0, `ALWAYS-NO` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `SAMPLE-3` 6.0, `EXACT` 0.9, `WP-2` 0.9, `WP-inf` 0.9, `UP-4` 0.9, `UP-inf` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `WP-1` 1.0, `UP-2` 1.0, `UP-3` 1.0, `FIRST` 1.0, `BICOND` 1.0, `ONL(1)-reset` 1.0 | H-structure +0.00 · H-formalism +0.01 · H-translate +0.00 · H-length +0.13 · H-surface +0.00 |
| answer NO | `SAMPLE-3` 6.0, `EXACT` 0.9, `WP-2` 0.9, `WP-inf` 0.9, `UP-4` 0.9, `UP-inf` 0.9 | H-structure +0.34 · H-formalism +0.29 · H-translate +0.32 · H-length +0.00 · H-surface +0.34 |

### E5 · I-E5-F-CASE · F-CASE

**Ground truth:** answer = YES, n_models = 8, share_of_models_with_query_true = 1.0 (verified by enumeration of all colourings extending the precolouring, PySAT: CNF plus the negated query is UNSAT iff YES).

*Forced only by case analysis: UP to fixpoint (= WP to fixpoint) does not derive it (B1 omission).*

**Length per encoding:** G: 247 tokens, 18 statements · S: 266 tokens, 18 statements · C: 1041 tokens, 90 statements · L: 2149 tokens, 90 statements.

**Predictions per encoding:**

| Member | G | S | C | L |
|---|---|---|---|---|
| `EXACT` | YES | YES | YES | YES |
| `WP-1` | NO | NO | NO ᵗ | NO ᵗ |
| `WP-2` | NO | NO | NO ᵗ | NO ᵗ |
| `WP-inf` | NO | NO | NO ᵗ | NO ᵗ |
| `UP-2` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-3` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-4` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-inf` | NO ᵗ | NO ᵗ | NO | NO |
| `FF-LIST-READ` | NO | NO | NO ᵗ | NO ᵗ |
| `DSATUR-READ` | YES | YES | YES ᵗ | YES ᵗ |
| `FF-CM` | YES | YES | YES ᵗ | YES ᵗ |
| `UC-READ` | YES ᵗ | YES ᵗ | YES | YES |
| `UC-CM` | YES ᵗ | YES ᵗ | YES | YES |
| `GREEDY-CM` | YES ᵗ | YES ᵗ | YES | YES |
| `FIRST` | NO ᵗ | NO ᵗ | NO | NO |
| `BICOND` | NO ᵗ | NO ᵗ | NO ᵗ | NO |
| `ONL(1)-reset` | NO ᵗ | NO ᵗ | NO | NO |
| `ONL(8)-reset` | NO ᵗ | NO ᵗ | NO | NO |
| `SAMPLE-3` | 1.0 | 1.0 | 1.0 | 1.0 |
| `ALWAYS-YES` | YES | YES | YES | YES |
| `ALWAYS-NO` | NO | NO | NO | NO |
| `ETR` | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| YES in all four | 0.00 | 0.00 | 0.00 | 0.08 | 0.03 |
| NO in all four | 0.10 | 0.11 | 0.10 | 0.00 | 0.07 |
| YES in G and S; NO in C and L | 0.10 | 0.10 | 0.10 | 0.00 | 0.09 |
| NO in G and S; YES in C and L | 0.01 | 0.00 | 0.00 | 0.08 | 0.00 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `WP-1` 1.0, `WP-2` 1.0, `WP-inf` 1.0, `UP-2` 1.0, `UP-3` 1.0, `UP-4` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `SAMPLE-3` 6.0, `EXACT` 0.9, `DSATUR-READ` 0.9, `FF-CM` 0.9, `UC-READ` 0.9, `UC-CM` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `WP-1` 1.0, `WP-2` 1.0, `WP-inf` 1.0, `UP-2` 1.0, `UP-3` 1.0, `UP-4` 1.0 | H-structure +0.01 · H-formalism +0.00 · H-translate +0.01 · H-length +0.05 · H-surface +0.01 |
| answer NO | `SAMPLE-3` 6.0, `EXACT` 0.9, `DSATUR-READ` 0.9, `FF-CM` 0.9, `UC-READ` 0.9, `UC-CM` 0.9 | H-structure +0.05 · H-formalism +0.07 · H-translate +0.06 · H-length +0.00 · H-surface +0.05 |

### E5 · I-E5-NF-READ · NF-READ

**Ground truth:** answer = NO, n_models = 4, share_of_models_with_query_true = 0.5 (verified by enumeration of all colourings extending the precolouring, PySAT: CNF plus the negated query is UNSAT iff YES).

*Not forced; the first-fit model has the query true (single-model commission), DSATUR's model does not.*

**Length per encoding:** G: 247 tokens, 18 statements · S: 259 tokens, 18 statements · C: 1041 tokens, 90 statements · L: 2129 tokens, 90 statements.

**Predictions per encoding:**

| Member | G | S | C | L |
|---|---|---|---|---|
| `EXACT` | NO | NO | NO | NO |
| `WP-1` | NO | NO | NO ᵗ | NO ᵗ |
| `WP-2` | NO | NO | NO ᵗ | NO ᵗ |
| `WP-inf` | NO | NO | NO ᵗ | NO ᵗ |
| `UP-2` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-3` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-4` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-inf` | NO ᵗ | NO ᵗ | NO | NO |
| `FF-LIST-READ` | YES | YES | YES ᵗ | YES ᵗ |
| `DSATUR-READ` | NO | NO | NO ᵗ | NO ᵗ |
| `FF-CM` | NO | NO | NO ᵗ | NO ᵗ |
| `UC-READ` | YES ᵗ | YES ᵗ | YES | YES |
| `UC-CM` | NO ᵗ | NO ᵗ | NO | NO |
| `GREEDY-CM` | YES ᵗ | YES ᵗ | YES | YES |
| `FIRST` | NO ᵗ | NO ᵗ | NO | NO |
| `BICOND` | NO ᵗ | NO ᵗ | NO ᵗ | NO |
| `ONL(1)-reset` | NO ᵗ | NO ᵗ | NO | NO |
| `ONL(8)-reset` | NO ᵗ | NO ᵗ | NO | NO |
| `SAMPLE-3` | 0.125 | 0.125 | 0.125 | 0.125 |
| `ALWAYS-YES` | YES | YES | YES | YES |
| `ALWAYS-NO` | NO | NO | NO | NO |
| `ETR` | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| YES in all four | 0.51 | 0.38 | 0.46 | 0.00 | 0.42 |
| NO in all four | 0.00 | 0.04 | 0.02 | 0.23 | 0.03 |
| YES in G and S; NO in C and L | 0.03 | 0.07 | 0.05 | 0.26 | 0.00 |
| NO in G and S; YES in C and L | 0.50 | 0.38 | 0.45 | 0.00 | 0.47 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `WP-1` 0.9, `WP-2` 0.9, `WP-inf` 0.9, `UP-2` 0.9, `UP-3` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `FF-LIST-READ` 0.9, `UC-READ` 0.9, `GREEDY-CM` 0.9, `ALWAYS-YES` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `WP-1` 0.9, `WP-2` 0.9, `WP-inf` 0.9, `UP-2` 0.9, `UP-3` 0.9 | H-structure +0.25 · H-formalism +0.17 · H-translate +0.22 · H-length +0.00 · H-surface +0.25 |
| answer NO | `FF-LIST-READ` 0.9, `UC-READ` 0.9, `GREEDY-CM` 0.9, `ALWAYS-YES` 0.9 | H-structure +0.00 · H-formalism +0.03 · H-translate +0.01 · H-length +0.12 · H-surface +0.00 |

### E5 · I-E5-F-CASE-twin · F-CASE-twin

**Ground truth:** answer = NO, n_models = 12, share_of_models_with_query_true = 0.667 (verified by enumeration of all colourings extending the precolouring, PySAT: CNF plus the negated query is UNSAT iff YES).

*Twin of F-CASE with edge (0, 1) removed: the query is no longer forced (truth flips, encodings fixed).*

**Length per encoding:** G: 241 tokens, 17 statements · S: 261 tokens, 17 statements · C: 1008 tokens, 87 statements · L: 2080 tokens, 87 statements.

**Predictions per encoding:**

| Member | G | S | C | L |
|---|---|---|---|---|
| `EXACT` | NO | NO | NO | NO |
| `WP-1` | NO | NO | NO ᵗ | NO ᵗ |
| `WP-2` | NO | NO | NO ᵗ | NO ᵗ |
| `WP-inf` | NO | NO | NO ᵗ | NO ᵗ |
| `UP-2` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-3` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-4` | NO ᵗ | NO ᵗ | NO | NO |
| `UP-inf` | NO ᵗ | NO ᵗ | NO | NO |
| `FF-LIST-READ` | NO | NO | NO ᵗ | NO ᵗ |
| `DSATUR-READ` | NO | NO | NO ᵗ | NO ᵗ |
| `FF-CM` | YES | YES | YES ᵗ | YES ᵗ |
| `UC-READ` | YES ᵗ | YES ᵗ | YES | YES |
| `UC-CM` | NO ᵗ | NO ᵗ | NO | NO |
| `GREEDY-CM` | YES ᵗ | YES ᵗ | YES | YES |
| `FIRST` | NO ᵗ | NO ᵗ | NO | NO |
| `BICOND` | NO ᵗ | NO ᵗ | NO ᵗ | NO |
| `ONL(1)-reset` | NO ᵗ | NO ᵗ | NO | NO |
| `ONL(8)-reset` | NO ᵗ | NO ᵗ | NO | NO |
| `SAMPLE-3` | 0.296 | 0.296 | 0.296 | 0.296 |
| `ALWAYS-YES` | YES | YES | YES | YES |
| `ALWAYS-NO` | NO | NO | NO | NO |
| `ETR` | n/c ⁿ | n/c ⁿ | n/c ⁿ | n/c ⁿ |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** G: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / S: Answer distribution = the graph reference profile's: members whose home formalism is 'graph' carry extra weight here. / C: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** G: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for G (translation rate; measured from traces in the real run). / S: Answer distribution = tau * graph profile + (1 - tau) * graph profile, tau = n/a for S (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| YES in all four | 0.69 | 0.41 | 0.57 | 0.00 | 0.44 |
| NO in all four | 0.00 | 0.08 | 0.03 | 0.28 | 0.07 |
| YES in G and S; NO in C and L | 0.09 | 0.17 | 0.12 | 0.36 | 0.00 |
| NO in G and S; YES in C and L | 0.67 | 0.39 | 0.55 | 0.00 | 0.58 |

**Item-level evidence, G** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `WP-1` 0.9, `WP-2` 0.9, `WP-inf` 0.9, `UP-2` 0.9, `UP-3` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `FF-CM` 0.9, `UC-READ` 0.9, `GREEDY-CM` 0.9, `ALWAYS-YES` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `WP-1` 0.9, `WP-2` 0.9, `WP-inf` 0.9, `UP-2` 0.9, `UP-3` 0.9 | H-structure +0.34 · H-formalism +0.18 · H-translate +0.27 · H-length +0.00 · H-surface +0.34 |
| answer NO | `FF-CM` 0.9, `UC-READ` 0.9, `GREEDY-CM` 0.9, `ALWAYS-YES` 0.9 | H-structure +0.00 · H-formalism +0.05 · H-translate +0.02 · H-length +0.14 · H-surface +0.00 |

## E6. Crossed order

- **Reasoning question.** E1 matches vertex order across encodings. Here C and L list the vertices in a different order. Order-dependent members then predict a different canonical answer from G's; order-free members do not. The predicted drop in cross-encoding agreement checks that E1's agreement is not produced by order matching alone.
- **Varied:** Encoding: C-XORD, L-XORD (G of the same instance is in E1).
- **Controlled:** Instance, label order, answer format.
- **Pre-registered eval-level predictions** (from the hypothesis blocks):
  - **H-structure:** Cross-encoding agreement drops from E1's matched-order level by exactly the predicted amount Σ_h π_h·(1 − agreement of h across the two orders) (95% interval of observed − predicted includes 0).
  - **H-formalism:** As H-structure for order-dependent members (order is read from each encoding's own surface); a larger drop indicates more weight moving between members.
  - **H-translate:** Translated traces rebuild the graph in the encoding's own first-mention order (π'); fingerprints follow π', not G's π_L.
  - **H-length:** Same as matched order: crossing order changes no length feature.
  - **H-surface:** No specific prediction.

### E6 · I-E1-B2 · crossed order

**Ground truth:** colourable = True, n_colourings = 552, n_partitions = 92 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** C-XORD: 1214 tokens, 102 statements · L-XORD: 2535 tokens, 102 statements.

**Prompt, C-XORD** (C, vertices in a different order):

```
CNF formula over 36 Boolean variables (x01 to x36) with 102 clauses (in this order):
(x10 ∨ x11 ∨ x12)
(x34 ∨ x35 ∨ x36)
(x25 ∨ x26 ∨ x27)
(x13 ∨ x14 ∨ x15)
(x22 ∨ x23 ∨ x24)
(x04 ∨ x05 ∨ x06)
(x19 ∨ x20 ∨ x21)
(x28 ∨ x29 ∨ x30)
(x07 ∨ x08 ∨ x09)
(x31 ∨ x32 ∨ x33)
(x01 ∨ x02 ∨ x03)
(x16 ∨ x17 ∨ x18)
(¬x10 ∨ ¬x11)
… (85 lines omitted; full prompt in the JSONL) …
(¬x21 ∨ ¬x03)
(¬x19 ∨ ¬x16)
(¬x20 ∨ ¬x17)
(¬x21 ∨ ¬x18)
Find an assignment of true/false to the variables that makes every clause true.

Think it through as carefully as you need. If no such assignment exists, finish with the line "ANSWER: UNSAT". Otherwise finish with the line "ANSWER:" followed by the variables you set to true, separated by spaces (every other variable is false).
```

**Prompt, L-XORD** (L, vertices in a different order):

```
Here are some statements:
1. The Harmony exam is in slot 1, slot 2 or slot 3.
2. The Zoology exam is in slot 1, slot 2 or slot 3.
3. The Rhetoric exam is in slot 1, slot 2 or slot 3.
4. The Italian exam is in slot 1, slot 2 or slot 3.
5. The Quilting exam is in slot 1, slot 2 or slot 3.
6. The Ceramics exam is in slot 1, slot 2 or slot 3.
7. The Optics exam is in slot 1, slot 2 or slot 3.
8. The Statistics exam is in slot 1, slot 2 or slot 3.
9. The Geology exam is in slot 1, slot 2 or slot 3.
10. The Urdu exam is in slot 1, slot 2 or slot 3.
11. The Algebra exam is in slot 1, slot 2 or slot 3.
12. The Nutrition exam is in slot 1, slot 2 or slot 3.
13. If the Harmony exam is in slot 1, then the Harmony exam is not in slot 2.
… (85 lines omitted; full prompt in the JSONL) …
99. If the Optics exam is in slot 3, then the Algebra exam is not in slot 3.
100. If the Optics exam is in slot 1, then the Nutrition exam is not in slot 1.
101. If the Optics exam is in slot 2, then the Nutrition exam is not in slot 2.
102. If the Optics exam is in slot 3, then the Nutrition exam is not in slot 3.
Question: Can all of these statements be true at the same time? If they can, describe a situation in which they are all true.

Think it through as carefully as you need. If they cannot all be true, finish with the line "ANSWER: NO". Otherwise finish with the line "ANSWER:" followed by one line `exam: slot` per exam, in this order: Harmony, Optics, Urdu, Statistics, Zoology, Quilting, Geology, Rhetoric, Algebra, Nutrition, Italian, Ceramics.
```

**Predictions per encoding** (canonical answer):

| Member (family, home) | C-XORD | L-XORD |
|---|---|---|
| `FF-LIST` (C1, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ |
| `LF` (C1, graph) | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR ᵗ | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR ᵗ | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=UC=DROP ᵗ | LIST=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=UC=DROP | LIST=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | GUC | GUC |
| `DPLL-MENTION` (D, cnf) | LIST=UC=DROP | LIST=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=UC=DROP | LIST=UC=DROP |
| `FIRST` (B4, logic) | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** C-XORD: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L-XORD: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** C-XORD: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C-XORD (translation rate; measured from traces in the real run). / L-XORD: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L-XORD (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Item-level evidence, C-XORD** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `UC-DET-INDEX` 6.0, `GUC-DET` 6.0 | H-structure +0.00 · H-formalism +0.07 · H-translate +0.03 · H-length +0.18 · H-surface +0.00 |
| answer = fingerprint #1 (DPLL-INDEX, FF-LABEL, UC-DET-INDEX) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.15 · H-formalism +0.00 · H-translate +0.08 · H-length +0.31 · H-surface +0.15 |
| answer = fingerprint #2 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.37 · H-translate +0.11 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.66 · H-translate +0.16 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #4 (GUC-DET) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.65 · H-formalism +0.00 · H-translate +0.27 · H-length +0.79 · H-surface +0.65 |
| answer = fingerprint #5 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.36 · H-formalism +0.00 · H-translate +0.18 · H-length +0.53 · H-surface +0.36 |
| another valid colouring (no member predicts it) | `RANDOM` 3.3, `DPLL-OCC` 2.0, `FF-LABEL` 1.9, `UC-DET-INDEX` 1.9, `DPLL-INDEX` 1.9, `FF-LIST` 1.7 | H-structure +0.03 · H-formalism +0.00 · H-translate +0.02 · H-length +0.04 · H-surface +0.03 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.50 · H-formalism +0.59 · H-translate +0.54 · H-length +0.00 · H-surface +0.50 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.50 · H-formalism +0.00 · H-translate +0.23 · H-length +0.59 · H-surface +0.50 |

### E6 · I-E1-B3 · crossed order

**Ground truth:** colourable = True, n_colourings = 528, n_partitions = 88 (verified by backtracking enumeration of all colourings, PySAT Glucose4 on the direct CNF encoding).

**Length per encoding:** C-XORD: 1214 tokens, 102 statements · L-XORD: 2537 tokens, 102 statements.

**Predictions per encoding** (canonical answer):

| Member (family, home) | C-XORD | L-XORD |
|---|---|---|
| `FF-LIST` (C1, graph) | LIST=GUC=UC=DROP ᵗ | LIST=GUC=UC=DROP ᵗ |
| `FF-LIST-INFEAS` (C1, graph) | LIST=GUC=UC=DROP ᵗ | LIST=GUC=UC=DROP ᵗ |
| `FF-LABEL` (C1, graph) | LABEL=UC-INDEX ᵗ | LABEL=UC-INDEX ᵗ |
| `LF` (C1, graph) | LF ᵗ | LF ᵗ |
| `DSATUR` (C2, graph) | DSATUR ᵗ | DSATUR ᵗ |
| `DPLL-LIST` (D, graph) | LIST=GUC=UC=DROP ᵗ | LIST=GUC=UC=DROP ᵗ |
| `DPLL-LIST-b12` (D, graph) | LIST=GUC=UC=DROP ᵗ | LIST=GUC=UC=DROP ᵗ |
| `DPLL-DSATUR` (D, graph) | DSATUR ᵗ | DSATUR ᵗ |
| `DROP-LAST-1` (B1, graph) | LIST=GUC=UC=DROP ᵗ | LIST=GUC=UC=DROP ᵗ |
| `POLARITY` (C0, cnf) | IMP | IMP |
| `GREEDY-MENTION` (C1, cnf) | IMP | IMP |
| `UC-DET` (C2, cnf) | LIST=GUC=UC=DROP | LIST=GUC=UC=DROP |
| `UC-DET-INDEX` (C2, cnf) | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `GUC-DET` (C2, cnf) | LIST=GUC=UC=DROP | LIST=GUC=UC=DROP |
| `DPLL-MENTION` (D, cnf) | LIST=GUC=UC=DROP | LIST=GUC=UC=DROP |
| `DPLL-INDEX` (D, cnf) | LABEL=UC-INDEX | LABEL=UC-INDEX |
| `DPLL-OCC` (D, cnf) | OCC | OCC |
| `DPLL-MENTION-b24` (D, cnf) | LIST=GUC=UC=DROP | LIST=GUC=UC=DROP |
| `FIRST` (B4, logic) | IMP | IMP |
| `BICOND` (B4, logic) | IMP ᵗ | IMP |
| `ONL(1)` (C4, logic) | IMP | IMP |
| `ONL(64)` (C4, logic) | IMP | IMP |
| `ETR` (B4/C4, logic) | n/c ⁿ | n/c ⁿ |
| `EXACT` (null, any) | uniform over valid | uniform over valid |
| `RO-FF` (C3, graph) | distribution ᵗ | distribution ᵗ |
| `MIN-CONFLICTS` (F, graph) | distribution ᵗ | distribution ᵗ |
| `WALK` (F, cnf) | distribution | distribution |
| `ALWAYS-NO` (A1, any) | IMP | IMP |
| `RANDOM` (H, any) | uniform | uniform |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** C-XORD: Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here. / L-XORD: Answer distribution = the logic reference profile's: members whose home formalism is 'logic' carry extra weight here.
- **H-translate:** C-XORD: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C-XORD (translation rate; measured from traces in the real run). / L-XORD: Answer distribution = tau * graph profile + (1 - tau) * logic profile, tau = 0.6 for L-XORD (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Item-level evidence, C-XORD** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer = fingerprint #0 (DPLL-LIST, DPLL-LIST-b12, DPLL-MENTION, DPLL-MENTION-b24…) | `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-DSATUR` 6.0, `UC-DET-INDEX` 6.0, `DPLL-INDEX` 6.0 | H-structure +0.02 · H-formalism +0.00 · H-translate +0.01 · H-length +0.20 · H-surface +0.02 |
| answer = fingerprint #1 (DPLL-INDEX, FF-LABEL, UC-DET-INDEX) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.14 · H-formalism +0.00 · H-translate +0.08 · H-length +0.31 · H-surface +0.14 |
| answer = fingerprint #2 (LF) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.35 · H-translate +0.11 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #3 (DPLL-DSATUR, DSATUR) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DPLL-LIST` 6.0, `DPLL-LIST-b12` 6.0 | H-structure +0.00 · H-formalism +0.67 · H-translate +0.16 · H-length +0.17 · H-surface +0.00 |
| answer = fingerprint #4 (DPLL-OCC) | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.36 · H-formalism +0.00 · H-translate +0.18 · H-length +0.51 · H-surface +0.36 |
| another valid colouring (no member predicts it) | `RANDOM` 3.3, `DPLL-OCC` 2.0, `FF-LIST` 1.9, `FF-LIST-INFEAS` 1.9, `DPLL-LIST` 1.9, `DPLL-LIST-b12` 1.9 | H-structure +0.03 · H-formalism +0.00 · H-translate +0.01 · H-length +0.03 · H-surface +0.03 |
| an invalid colouring | `POLARITY` 5.7, `GREEDY-MENTION` 5.7, `FIRST` 5.7, `BICOND` 5.7, `ONL(1)` 5.7, `ONL(64)` 5.7 | H-structure +0.51 · H-formalism +0.58 · H-translate +0.54 · H-length +0.00 · H-surface +0.51 |
| IMPOSSIBLE / UNSAT / NO | `FF-LIST` 6.0, `FF-LIST-INFEAS` 6.0, `FF-LABEL` 6.0, `LF` 6.0, `DSATUR` 6.0, `DPLL-LIST` 6.0 | H-structure +0.50 · H-formalism +0.00 · H-translate +0.23 · H-length +0.59 · H-surface +0.50 |

## E7. Reverse direction: a SAT-native base

- **Reasoning question.** With a random 3-SAT base, the graph rendering (pick one vertex per group, no two adjacent) is the longest encoding, reversing E1's length confound. Do variable-driven members (UC-DET, GREEDY, POLARITY; CNF-home) and group-driven members (PICK-FIRST, MCG; graph-home) trade weight by formalism?
- **Varied:** Cell (r1: group-driven members dead-end, variable-driven succeed; r2: the reverse) × encoding (C, L-SW, G-GROUP).
- **Controlled:** Instance and clause order.
- **Pre-registered eval-level predictions** (from the hypothesis blocks):
  - **H-structure:** PICK-FIRST, UC-DET and GREEDY weights equal across C, L-SW and G-GROUP (±0.05).
  - **H-formalism:** Graph rendering raises PICK-FIRST / MCG weight (false NO in r1) and lowers UC-DET / GREEDY weight (false NO in r2) by >= 0.10 each.
  - **H-translate:** If the canonical target is graph: C/L-SW traces translate to the group graph (unlikely); if it is SAT: G-GROUP traces translate to clauses (TR1 'one literal per clause'), and G-GROUP π moves to the C profile.
  - **H-length:** G-GROUP is the longest encoding here, so it should be the least accurate; if formalism (not length) drove E1, G-GROUP should instead look like G in E1.
  - **H-surface:** L-SW (NL) differs from C and G-GROUP (symbolic) by the E1 surface shift.

### E7 · I-E7-r1 · r1

**Ground truth:** satisfiable = True, n_models = 9 (verified by truth-table enumeration, PySAT Glucose4).

*Reverse direction: here the graph rendering is the longest (statements and tokens), so length and formalism are crossed relative to E1–E6.*

**Length per encoding:** C: 430 tokens, 24 statements · L-SW: 781 tokens, 24 statements · G-GROUP: 1393 tokens, 236 statements.

**Prompt, C** (CNF, opaque variables):

```
CNF formula over 8 Boolean variables (x1 to x8) with 24 clauses (in this order):
(¬x2 ∨ ¬x1 ∨ ¬x5)
(x1 ∨ x4 ∨ ¬x5)
(x1 ∨ ¬x5 ∨ x2)
(¬x7 ∨ x1 ∨ ¬x2)
(¬x4 ∨ x3 ∨ ¬x8)
(¬x5 ∨ x1 ∨ ¬x4)
(x3 ∨ ¬x7 ∨ ¬x6)
(¬x1 ∨ ¬x2 ∨ x3)
(¬x5 ∨ ¬x7 ∨ x4)
(x1 ∨ x5 ∨ x7)
(x5 ∨ ¬x4 ∨ ¬x7)
(x8 ∨ ¬x5 ∨ x2)
(x2 ∨ x8 ∨ ¬x1)
… (7 lines omitted; full prompt in the JSONL) …
(¬x5 ∨ x4 ∨ x6)
(x4 ∨ x3 ∨ ¬x6)
(x6 ∨ x8 ∨ x2)
(x1 ∨ x7 ∨ x8)
Find an assignment of true/false to the variables that makes every clause true.

Think it through as carefully as you need. If no such assignment exists, finish with the line "ANSWER: UNSAT". Otherwise finish with the line "ANSWER:" followed by the variables you set to true, separated by spaces (every other variable is false).
```

**Prompt, L-SW** (switch rules in English):

```
A panel has 8 switches, numbered 1 to 8; each switch is either on or off. Here are some rules:
1. At least one of these is true: switch 2 is off, switch 1 is off, switch 5 is off.
2. At least one of these is true: switch 1 is on, switch 4 is on, switch 5 is off.
3. At least one of these is true: switch 1 is on, switch 5 is off, switch 2 is on.
4. At least one of these is true: switch 7 is off, switch 1 is on, switch 2 is off.
5. At least one of these is true: switch 4 is off, switch 3 is on, switch 8 is off.
6. At least one of these is true: switch 5 is off, switch 1 is on, switch 4 is off.
7. At least one of these is true: switch 3 is on, switch 7 is off, switch 6 is off.
8. At least one of these is true: switch 1 is off, switch 2 is off, switch 3 is on.
9. At least one of these is true: switch 5 is off, switch 7 is off, switch 4 is on.
10. At least one of these is true: switch 1 is on, switch 5 is on, switch 7 is on.
11. At least one of these is true: switch 5 is on, switch 4 is off, switch 7 is off.
12. At least one of these is true: switch 8 is on, switch 5 is off, switch 2 is on.
13. At least one of these is true: switch 2 is on, switch 8 is on, switch 1 is off.
… (7 lines omitted; full prompt in the JSONL) …
21. At least one of these is true: switch 5 is off, switch 4 is on, switch 6 is on.
22. At least one of these is true: switch 4 is on, switch 3 is on, switch 6 is off.
23. At least one of these is true: switch 6 is on, switch 8 is on, switch 2 is on.
24. At least one of these is true: switch 1 is on, switch 7 is on, switch 8 is on.
Question: Can all of the rules hold at the same time? If they can, give a setting of the switches that satisfies every rule.

Think it through as carefully as you need. If the rules cannot all hold, finish with the line "ANSWER: NO". Otherwise finish with the line "ANSWER:" followed by the numbers of the switches that are on, separated by spaces (every other switch is off).
```

**Prompt, G-GROUP** (graph: one vertex per group, no two adjacent):

```
A graph has 72 vertices in 24 groups of three and 164 edges.
Groups (in this order):
Group 1: u199, u150, u680
Group 2: u220, u890, u935
Group 3: u295, u613, u146
Group 4: u500, u703, u179
Group 5: u145, u311, u932
Group 6: u828, u787, u995
Group 7: u751, u158, u734
Group 8: u299, u529, u221
Group 9: u843, u223, u864
Group 10: u497, u227, u267
Group 11: u914, u259, u167
Group 12: u537, u578, u713
… (173 lines omitted; full prompt in the JSONL) …
u779 - u414
u779 - u576
u117 - u780
u780 - u639
Pick exactly one vertex from each group so that no two picked vertices are joined by an edge.

Think it through as carefully as you need. If this is impossible, finish with the line "ANSWER: IMPOSSIBLE". Otherwise finish with the line "ANSWER:" followed by one line `group: vertex` per group, in group order.
```

**Predictions per encoding:**

| Member | C | L-SW | G-GROUP |
|---|---|---|---|
| `POLARITY` | YES-valid | YES-valid | YES-valid ᵗ |
| `GREEDY-MENTION` | YES-valid | YES-valid | YES-valid ᵗ |
| `UC-DET` | YES-valid | YES-valid | YES-valid ᵗ |
| `GUC-DET` | NO | NO | NO ᵗ |
| `PICK-FIRST` | NO ᵗ | NO ᵗ | NO |
| `PICK-MINDEG` | YES-valid ᵗ | YES-valid ᵗ | YES-valid |
| `MCG` | NO ᵗ | NO ᵗ | NO |
| `EXACT` | YES-valid | YES-valid | YES-valid |
| `ALWAYS-NO` | NO | NO | NO |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Same member weights as on C (CNF profile used as the invariant reference here).
- **H-formalism:** Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L-SW: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-SW (translation rate; measured from traces in the real run). / G-GROUP: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for G-GROUP (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| NO in G-GROUP only | 0.23 | 0.00 | 0.10 | 0.23 | 0.23 |
| NO in C and L-SW only | 0.00 | 0.15 | 0.07 | 0.09 | 0.00 |
| valid in all three | 0.00 | 0.15 | 0.07 | 0.13 | 0.00 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES-valid | `GUC-DET` 1.3, `PICK-FIRST` 1.3, `MCG` 1.3, `ALWAYS-NO` 1.3 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer YES-invalid | — | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `POLARITY` 1.3, `GREEDY-MENTION` 1.3, `UC-DET` 1.3, `PICK-MINDEG` 1.3, `EXACT` 1.3 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

### E7 · I-E7-r2 · r2

**Ground truth:** satisfiable = True, n_models = 13 (verified by truth-table enumeration, PySAT Glucose4).

*Reverse direction: here the graph rendering is the longest (statements and tokens), so length and formalism are crossed relative to E1–E6.*

**Length per encoding:** C: 488 tokens, 28 statements · L-SW: 893 tokens, 28 statements · G-GROUP: 1805 tokens, 308 statements.

**Predictions per encoding:**

| Member | C | L-SW | G-GROUP |
|---|---|---|---|
| `POLARITY` | NO | NO | NO ᵗ |
| `GREEDY-MENTION` | NO | NO | NO ᵗ |
| `UC-DET` | NO | NO | NO ᵗ |
| `GUC-DET` | YES-valid | YES-valid | YES-valid ᵗ |
| `PICK-FIRST` | YES-valid ᵗ | YES-valid ᵗ | YES-valid |
| `PICK-MINDEG` | NO ᵗ | NO ᵗ | NO |
| `MCG` | YES-valid ᵗ | YES-valid ᵗ | YES-valid |
| `EXACT` | YES-valid | YES-valid | YES-valid |
| `ALWAYS-NO` | NO | NO | NO |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Same member weights as on C (CNF profile used as the invariant reference here).
- **H-formalism:** Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run). / L-SW: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-SW (translation rate; measured from traces in the real run). / G-GROUP: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for G-GROUP (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| NO in G-GROUP only | 0.00 | 0.18 | 0.08 | 0.08 | 0.00 |
| NO in C and L-SW only | 0.12 | 0.00 | 0.05 | 0.21 | 0.12 |
| valid in all three | 0.12 | 0.00 | 0.05 | 0.21 | 0.12 |

**Item-level evidence, C** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES-valid | `POLARITY` 1.3, `GREEDY-MENTION` 1.3, `UC-DET` 1.3, `PICK-MINDEG` 1.3, `ALWAYS-NO` 1.3 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer YES-invalid | — | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `GUC-DET` 1.3, `PICK-FIRST` 1.3, `MCG` 1.3, `EXACT` 1.3 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

## E8. A logic-native gadget in three logical forms

- **Reasoning question.** The B4/C4 E1 disjunction gadget, written as a disjunction of conjunctions (its home form), as four English clauses, and as symbolic CNF. English clauses and symbolic CNF have identical member predictions (computed), so any change between them is a pure weight shift. Between the disjunctive and clausal English forms, several members' own predictions change (MATCH, PRIMACY, ETR, ONL(2)) while FIRST's does not.
- **Varied:** Cell (M, N, U, V; DC order) × form (L-DNF, L-CNF, C).
- **Controlled:** Logical content (the three forms have the same models, checked).
- **Pre-registered eval-level predictions** (from the hypothesis blocks):
  - **H-structure:** L-CNF and C (identical member predictions, computed) give the same answers within ±0.05 per cell; the L-DNF → L-CNF change equals Σ_h π_h·Δ_h from the computed member changes (MATCH-L/A, PRIMACY, ETR and ONL(2) are representation-bound here; FIRST is not).
  - **H-formalism:** Weights equal on L-DNF and L-CNF (both English logic); B4 weights (FIRST, MATCH, ETR, ONL) lower on C than on L-CNF by >= 0.10, a pure weight shift. A form-bound variant (the logical form selects) instead predicts a FIRST-pattern drop already from L-DNF to L-CNF.
  - **H-translate:** C traces re-express the clauses as cases or as English statements (TR1) and then follow the L-CNF profile.
  - **H-length:** Tokens differ little here (92–122); no difference predicted beyond slips.
  - **H-surface:** Same prediction as H-formalism on this set (L-DNF, L-CNF English; C symbolic): E8 does not separate them; the E1 2 × 2 does.

### E8 · I-E8-M · M1·DC

**Ground truth:** answer = NO (verified by truth table over 5 atoms; the three forms are checked to be logically equivalent).

**Length per encoding:** L-DNF: 92 tokens, — statements · L-CNF: 116 tokens, — statements · C: 98 tokens, — statements.

**Prompt, L-DNF** (English, disjunction of conjunctions):

```
Here are some statements:
1. Either the box is red and the box is heavy, or the jar is blue and the jar is cold.
2. The box is red.
Question: Does it follow that the box is heavy?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**Prompt, L-CNF** (English, four clauses):

```
Here are some statements:
1. The box is red or the jar is blue.
2. The box is red or the jar is cold.
3. The box is heavy or the jar is blue.
4. The box is heavy or the jar is cold.
5. The box is red.
Question: Does it follow that the box is heavy?
A conclusion follows only if it must be true whenever all of the statements are true.

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**Prompt, C** (CNF, opaque variables):

```
CNF formula over 5 Boolean variables (x1 to x5) with 5 clauses (in this order):
(x1 ∨ x3)
(x1 ∨ x4)
(x2 ∨ x3)
(x2 ∨ x4)
(x1)
Question: Is x2 true in every assignment that makes every clause true?

Think it through as carefully as you need. Finish with a final line that is exactly "ANSWER: YES" or "ANSWER: NO".
```

**Predictions per encoding:**

| Member | L-DNF | L-CNF | C |
|---|---|---|---|
| `EXACT` | NO ⁿ | NO ⁿ | NO ⁿ |
| `FIRST` | YES ⁿ | YES ⁿ | YES ⁿ |
| `MATCH-L` | YES ⁿ | NO ⁿ | NO ⁿ |
| `MATCH-A` | YES ⁿ | NO ⁿ | NO ⁿ |
| `ONL(1)` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ONL(2)` | NO ⁿ | YES ⁿ | YES ⁿ |
| `UP-1` | NO ⁿ | NO ⁿ | NO ⁿ |
| `PRIMACY` | YES ⁿ | NO ⁿ | NO ⁿ |
| `RECENCY` | NO ⁿ | NO ⁿ | NO ⁿ |
| `GREEDY-CM` | NO ⁿ | NO ⁿ | NO ⁿ |
| `ALWAYS-YES` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ETR` | YES ⁿ | YES ⁿ | YES ⁿ |
| `SAMPLE-3` | 0.512 ⁿ | 0.512 ⁿ | 0.512 ⁿ |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** L-DNF: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-DNF (translation rate; measured from traces in the real run). / L-CNF: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-CNF (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| YES in L-DNF only | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |
| YES in all three | 0.00 | 0.20 | 0.09 | 0.00 | 0.20 |
| NO in all three | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |
| YES in L-DNF and L-CNF; NO in C | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |

**Item-level evidence, L-DNF** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `ONL(2)` 0.9, `UP-1` 0.9, `RECENCY` 0.9, `GREEDY-CM` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `FIRST` 0.9, `MATCH-L` 0.9, `MATCH-A` 0.9, `ONL(1)` 0.9, `PRIMACY` 0.9, `ALWAYS-YES` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, L-CNF** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `MATCH-L` 0.9, `MATCH-A` 0.9, `UP-1` 0.9, `PRIMACY` 0.9, `RECENCY` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `FIRST` 0.9, `ONL(1)` 0.9, `ONL(2)` 0.9, `ALWAYS-YES` 0.9, `ETR` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

### E8 · I-E8-N · N1·DC

**Ground truth:** answer = YES (verified by truth table over 5 atoms; the three forms are checked to be logically equivalent).

**Length per encoding:** L-DNF: 93 tokens, — statements · L-CNF: 117 tokens, — statements · C: 100 tokens, — statements.

**Predictions per encoding:**

| Member | L-DNF | L-CNF | C |
|---|---|---|---|
| `EXACT` | YES ⁿ | YES ⁿ | YES ⁿ |
| `FIRST` | NO ⁿ | NO ⁿ | NO ⁿ |
| `MATCH-L` | YES ⁿ | YES ⁿ | YES ⁿ |
| `MATCH-A` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ONL(1)` | NO ⁿ | NO ⁿ | NO ⁿ |
| `ONL(2)` | YES ⁿ | NO ⁿ | NO ⁿ |
| `UP-1` | YES ⁿ | YES ⁿ | YES ⁿ |
| `PRIMACY` | YES ⁿ | NO ⁿ | NO ⁿ |
| `RECENCY` | NO ⁿ | NO ⁿ | NO ⁿ |
| `GREEDY-CM` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ALWAYS-YES` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ETR` | YES ⁿ | NO ⁿ | NO ⁿ |
| `SAMPLE-3` | 1.0 ⁿ | 1.0 ⁿ | 1.0 ⁿ |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** L-DNF: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-DNF (translation rate; measured from traces in the real run). / L-CNF: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-CNF (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| YES in L-DNF only | 0.00 | 0.27 | 0.11 | 0.00 | 0.27 |
| YES in all three | 0.08 | 0.00 | 0.04 | 0.08 | 0.00 |
| NO in all three | 0.00 | 0.27 | 0.11 | 0.00 | 0.27 |
| YES in L-DNF and L-CNF; NO in C | 0.00 | 0.27 | 0.11 | 0.00 | 0.27 |

**Item-level evidence, L-DNF** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `FIRST` 1.0, `ONL(1)` 1.0, `RECENCY` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `SAMPLE-3` 6.0, `EXACT` 0.9, `MATCH-L` 0.9, `MATCH-A` 0.9, `ONL(2)` 0.9, `UP-1` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, L-CNF** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `FIRST` 1.0, `ONL(1)` 1.0, `ONL(2)` 1.0, `PRIMACY` 1.0, `RECENCY` 1.0, `ETR` 1.0 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `SAMPLE-3` 6.0, `EXACT` 0.9, `MATCH-L` 0.9, `MATCH-A` 0.9, `UP-1` 0.9, `GREEDY-CM` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

### E8 · I-E8-U · U1·DC

**Ground truth:** answer = NO (verified by truth table over 5 atoms; the three forms are checked to be logically equivalent).

**Length per encoding:** L-DNF: 92 tokens, — statements · L-CNF: 116 tokens, — statements · C: 98 tokens, — statements.

**Predictions per encoding:**

| Member | L-DNF | L-CNF | C |
|---|---|---|---|
| `EXACT` | NO ⁿ | NO ⁿ | NO ⁿ |
| `FIRST` | YES ⁿ | YES ⁿ | YES ⁿ |
| `MATCH-L` | NO ⁿ | NO ⁿ | NO ⁿ |
| `MATCH-A` | NO ⁿ | NO ⁿ | NO ⁿ |
| `ONL(1)` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ONL(2)` | NO ⁿ | YES ⁿ | YES ⁿ |
| `UP-1` | NO ⁿ | NO ⁿ | NO ⁿ |
| `PRIMACY` | YES ⁿ | NO ⁿ | NO ⁿ |
| `RECENCY` | NO ⁿ | NO ⁿ | NO ⁿ |
| `GREEDY-CM` | NO ⁿ | NO ⁿ | NO ⁿ |
| `ALWAYS-YES` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ETR` | NO ⁿ | YES ⁿ | YES ⁿ |
| `SAMPLE-3` | 0.364 ⁿ | 0.364 ⁿ | 0.364 ⁿ |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** L-DNF: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-DNF (translation rate; measured from traces in the real run). / L-CNF: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-CNF (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| YES in L-DNF only | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |
| YES in all three | 0.00 | 0.21 | 0.09 | 0.00 | 0.21 |
| NO in all three | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |
| YES in L-DNF and L-CNF; NO in C | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |

**Item-level evidence, L-DNF** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `MATCH-L` 0.9, `MATCH-A` 0.9, `ONL(2)` 0.9, `UP-1` 0.9, `RECENCY` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `FIRST` 0.9, `ONL(1)` 0.9, `PRIMACY` 0.9, `ALWAYS-YES` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, L-CNF** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `MATCH-L` 0.9, `MATCH-A` 0.9, `UP-1` 0.9, `PRIMACY` 0.9, `RECENCY` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `FIRST` 0.9, `ONL(1)` 0.9, `ONL(2)` 0.9, `ALWAYS-YES` 0.9, `ETR` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

### E8 · I-E8-V · V1·DC

**Ground truth:** answer = NO (verified by truth table over 5 atoms; the three forms are checked to be logically equivalent).

**Length per encoding:** L-DNF: 98 tokens, — statements · L-CNF: 122 tokens, — statements · C: 102 tokens, — statements.

**Predictions per encoding:**

| Member | L-DNF | L-CNF | C |
|---|---|---|---|
| `EXACT` | NO ⁿ | NO ⁿ | NO ⁿ |
| `FIRST` | YES ⁿ | YES ⁿ | YES ⁿ |
| `MATCH-L` | NO ⁿ | NO ⁿ | NO ⁿ |
| `MATCH-A` | NO ⁿ | NO ⁿ | NO ⁿ |
| `ONL(1)` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ONL(2)` | YES ⁿ | YES ⁿ | YES ⁿ |
| `UP-1` | NO ⁿ | NO ⁿ | NO ⁿ |
| `PRIMACY` | YES ⁿ | NO ⁿ | NO ⁿ |
| `RECENCY` | NO ⁿ | NO ⁿ | NO ⁿ |
| `GREEDY-CM` | NO ⁿ | NO ⁿ | NO ⁿ |
| `ALWAYS-YES` | YES ⁿ | YES ⁿ | YES ⁿ |
| `ETR` | YES ⁿ | YES ⁿ | YES ⁿ |
| `SAMPLE-3` | 0.422 ⁿ | 0.422 ⁿ | 0.422 ⁿ |

**Hypothesis outputs on this set** (per encoding, from the hypothesis blocks):

- **H-structure:** Answer distribution = the graph reference profile's (members weighted as on G); deterministic members return the same canonical answer as on the other encodings of this set.
- **H-formalism:** Answer distribution = the cnf reference profile's: members whose home formalism is 'cnf' carry extra weight here.
- **H-translate:** L-DNF: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-DNF (translation rate; measured from traces in the real run). / L-CNF: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = n/a for L-CNF (translation rate; measured from traces in the real run). / C: Answer distribution = tau * graph profile + (1 - tau) * cnf profile, tau = 0.6 for C (translation rate; measured from traces in the real run).
- **H-length:** Graph reference profile with a slip rate that grows with prompt tokens (illustration: eps = 0.1 * tokens / tokens(G), capped at 0.4).
- **H-surface:** Symbolic encodings (G, C, X, ...) follow the graph profile; natural-language ones (S, L) follow the logic profile.
- **CoT predictions:** H-translate: TR1 (names the reduction, e.g. 'this is graph 3-colouring') or TR2 (rebuilds a conflict / neighbour list) within the first 1,500 thinking tokens; graph-lexicon share >= 0.6 of coded content words afterwards; TR4 maps the answer back. H-formalism: Trace stays in this encoding's own vocabulary (no TR1/TR2 translation event); member codes are those of the home formalism (graph: neighbour/colour; CNF: clause/unit/variable; logic: statement/case/suppose).

**Set-level evidence** (log10 LR against each hypothesis for the joint outcome over this set's encodings; positive = against):

| Joint outcome over the set | H-structure | H-formalism | H-translate | H-length | H-surface |
|---|---|---|---|---|---|
| YES in L-DNF only | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |
| YES in all three | 0.00 | 0.21 | 0.09 | 0.00 | 0.21 |
| NO in all three | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |
| YES in L-DNF and L-CNF; NO in C | 0.07 | 0.00 | 0.03 | 0.07 | 0.00 |

**Item-level evidence, L-DNF** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `MATCH-L` 0.9, `MATCH-A` 0.9, `UP-1` 0.9, `RECENCY` 0.9, `GREEDY-CM` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `FIRST` 0.9, `ONL(1)` 0.9, `ONL(2)` 0.9, `PRIMACY` 0.9, `ALWAYS-YES` 0.9, `ETR` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

**Item-level evidence, L-CNF** (one response; 6.0 is the floor: the member gives the observation probability below 1e-6):

| Observation | Strongest evidence against members (log10 LR) | Against hypotheses (log10 LR) |
|---|---|---|
| answer YES | `EXACT` 0.9, `MATCH-L` 0.9, `MATCH-A` 0.9, `UP-1` 0.9, `PRIMACY` 0.9, `RECENCY` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |
| answer NO | `FIRST` 0.9, `ONL(1)` 0.9, `ONL(2)` 0.9, `ALWAYS-YES` 0.9, `ETR` 0.9 | H-structure +0.00 · H-formalism +0.00 · H-translate +0.00 · H-length +0.00 · H-surface +0.00 |

