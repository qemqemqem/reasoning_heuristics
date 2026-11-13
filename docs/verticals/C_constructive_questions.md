# Vertical C: example question library

*Companion to [C_constructive.md](C_constructive.md). Machine-readable copy: [`data/examples/C_constructive.jsonl`](../../data/examples/C_constructive.jsonl) (one object per item; fields `eval_id`, `cell`, `pair_id`, `domain`, `framing`, `prompt`, `answer_format`, `ground_truth`, `predictions`, `trace_predictions`, `hypotheses`, `likelihood_ratios`, `disconfirms` (theories pushed toward zero, log10 LR ≤ −2), `supports` (theories within 0.5 of the best), `params`, `notes`).*

**What this is.** One complete counterfactual set per eval (E1–E6; E1, E2 and E5 have two or three), 39 items in all, each with the exact prompt, the ground truth, every relevant member's predicted answer (family C and the nearest competitors from D, F, E, B1, A, H and the nulls), predicted trace features, and how strongly each possible outcome moves weight between the theories (likelihood ratios). They are written so that the generator spec in [C_constructive.md §2.8](C_constructive.md#28-generator-specifications) reproduces them at scale.

**How the numbers were checked.** Every ground truth and every prediction below was computed by executing the member on the item, not by hand: brute-force enumeration for chromatic numbers, optimal partitions, SAT solutions, knapsack optima and entailment countermodels; reference implementations of every member; 10⁴-run Monte Carlo for random-order members and 300–400 runs for local search. The scripts live outside the repo (throwaway scratch), as requested; the gadget lemma (first-fit colour 1 ⇔ NOR-circuit value) was additionally checked on 1,500 random gadgets.

**Sizes.** Items are at dev scale (n = 8–34) so that prompts are readable. The full-study sizes are in the generator spec (e.g. E1 colouring n = 16, E3 gadgets n = 68).

**How to read a set.**

- *Outputs by cell* gives each theory's predicted answer on each item, side by side. Colourings are partitions, coded P1, P2, … (legend below the table): two items with the same code got the same partition, whatever the colour names (in the re-themed item, course labels c## are matched to vertex labels v##). SAT assignments are coded S1, S2, … (not to be confused with family A).
- **The readout is graded, not binary.** A model can use several heuristics at once. Every theory h gets: a mixture weight π_h (posterior mean and 95% interval); a lift (the share of errors matching h, above its matched baseline); a log-likelihood gain over the null and over its nearest competitor; and, for traces, a faithfulness-weighted share T_h of traces matching h's signature. Weights may depend on item features and on the model (strategy selection, family I).
- *Weight readouts* give, for each theory: how far this dev set already separates it from its nearest competitor (log10 likelihood ratio); and, at full-study size, the smallest weight the set detects (80% power) and the upper 95% bound it places on the weight when the theory is absent. The *signature* is what the aggregate would look like if the theory carried all the weight; the *trace* column is its predicted trace signature. Together with the theory's entry in *Outputs by cell*, these form the item's hypothesis block. The JSONL repeats them per item, with the full likelihood-ratio table.
- *Likelihood ratios* replace pass/fail discrimination. For each pattern of outcomes over the set's items, the table gives the theories it favours, the theories it pushes toward zero weight (at least 100:1 against), and the theories it weakly disfavours. Disconfirming a competitor therefore means bounding its weight, not eliminating it. When theories are tied on a set (log10 LR > −0.5), the table names them, and *Not separated by this set* names the set that separates them.
- **Noise model behind the likelihood ratios** (pre-registered): P_h(y) = 0.8·core_h(y) + 0.2·[0.8·Unif(candidate answers) + 0.2·Unif(answer space)].
  - Executed members put all their core mass on their own prediction. Distributional members use their Monte-Carlo distribution.
  - EXACT is uniform over the optimal solutions. NOISY-EXACT is EXACT with slip rate 0.5.
  - PERCEPTION-NOISE averages EXACT over single-constraint misreads. RANDOM is uniform over the answer space.
  - The ratios grow as the slip rate falls: a slip rate of 0.1 makes them larger, and a slip rate of 0.4 makes them smaller.
  - The main analysis uses the near-miss (distance-kernel) slip model instead ([C_constructive.md §2.10](C_constructive.md#210-fake-model-recovery-with-graded-mixtures-behavioural-positive-controls)). The simpler model used here understates how far order-free diffuse solvers (EXACT, F) are separated from deterministic members. So the ratios for the "every answer optimal and predicted by no member" patterns are conservative, while the deterministic-vs-deterministic ratios are much the same under both models.
- Readout conventions: in E3 the uninstructed readout is the bit "the target has the same colour as the first-listed vertex" (invariant to colour names). `same`/`diff` = value of that bit.

**Theories** (definitions in [C_constructive.md §1.3](C_constructive.md#13-members-pseudocode)): C0 `POLARITY`; C1 `FF-LIST`, `FF-LABEL`, `FF-OUT` (greedy in the requested answer order), `LF`, `GREEDY-MENTION`, `GREEDY-INDEX`, `GREEDY-CM`, knapsack `RATIO-*`, `DIFF`, `VALUE`, `LARGEST-FIT`, `INPUT-FIT`; C2 `DSATUR`, `UC-DET`, `GUC`/`SC`; C3 `RO-FF`, `RO-GREEDY`; hybrid `GREEDY+REPAIR` (C→F); D `DPLL-σ`; F `MIN-CONFLICTS`, `WALK`; E `LOCAL-t`; B1 `DROP-LAST-EDGES`, `UP-fixpoint`; A `DENSITY`, `ALL-T`, `ALWAYS-YES`; H `RANDOM`; nulls `EXACT` (the model solves it, order-free), `NOISY-EXACT`, `PERCEPTION-NOISE`.

## Contents

- [E1 · Order source on isomorphic copies (graph colouring)](#e1-col-a) — 7 items
- [E1 · Order source on isomorphic copies (3-SAT)](#e1-sat-a) — 3 items
- [E2 · Rule discrimination by single-edge edits (graph colouring)](#e2-col-a) — 5 items
- [E2 · Rule discrimination by single-number edits (knapsack)](#e2-knap-a) — 5 items
- [E3 · Depth-stress gadget: order-only minimal triple (graph colouring)](#e3-col-a) — 7 items
- [E4 · Item-level co-failure at matched density (3-SAT)](#e4-sat-a) — 2 items
- [E5 · Dead-end localisation: vertex order × edge order (3-colouring)](#e5-col-a) — 4 items
- [E5 · Controlled partial states (3-SAT)](#e5-sat-state-a) — 2 items
- [E5 · Greedy countermodel construction in entailment](#e5-ent-a) — 2 items
- [E6 · Early answering: is the trace doing the work?](#e6-ea-a) — 2 items

<a id="e1-col-a"></a>
## E1 · Order source on isomorphic copies (graph colouring)  (`E1-COL-A`)

**Reasoning question.** When the model builds a colouring, how much weight does each order carry: the listing (FF-LIST), the label numbers (FF-LABEL), the order in which it was asked to write the answer (FF-OUT), a score order (LF, DSATUR), a random order (RO-FF), or none (exact / local search)? Correct answers count: with 48 optimal partitions, *which* one comes back is the fingerprint. On c1-c5 FF-LIST needs 4 colours while the optimum is 3, so a backtracking search in listing order (DPLL-LIST) separates from FF-LIST here.

**Controlled.** Edge set, label multiset, token count, answer length (all copies). c2-c5 share listing and labels and differ only in the requested answer order; c1 vs c2 differ only in labels; c2 vs c6 differ only in listing.  
**Varied.** Label assignment (c1->c2), requested answer order (c2->c3, c4, c5), listing order (c2->c6), framing (c2->exams).

**Outputs by cell** (each theory's predicted answer on each item) — c1 uses its own labels in the prompt; its column is shown mapped into c2's labels (`params.label_map_to_c2`), so equal codes mean the same structural answer

| Theory | `c1-NAT` | `c2-RELABEL` | `c3-ANS-LABEL` | `c4-ANS-RAND` | `c5-ANS-FREE` | `c6-RELIST` | `c2-RELABEL/theme-exams` |
|---|---|---|---|---|---|---|---|
| FF-LIST | P1 | P1 | P1 | P1 | P1 | P2 | P1 |
| FF-LABEL | P1 | P3 | P3 | P3 | P3 | P3 | P3 |
| FF-OUT (AR) | P1 | P1 | P3 | P4 | FF over the model's own emitted order (self-consistency test) | P2 | — |
| LF | P5 | P5 | P5 | P5 | P5 | P5 | — |
| DSATUR | P5 | P5 | P5 | P5 | P5 | P5 | P5 |
| DPLL-LIST (D, k=3) | P5 | P5 | P5 | P5 | P5 | P2 | — |
| DPLL-LABEL (D, k=3) | P5 | P3 | P3 | P3 | P3 | P3 | — |
| GREEDY+REPAIR-LIST (C->F) | P1 | P1 | P1 | P1 | P1 | P2 | — |
| RO-FF (C3) | P(partition = FF-LIST) 0.022; P(3 colours) 0.697; P(modal partition) 0.173 | P(partition = FF-LIST) 0.022; P(3 colours) 0.697; P(modal partition) 0.173 | P(partition = FF-LIST) 0.022; P(3 colours) 0.697; P(modal partition) 0.173 | P(partition = FF-LIST) 0.022; P(3 colours) 0.697; P(modal partition) 0.173 | P(partition = FF-LIST) 0.022; P(3 colours) 0.697; P(modal partition) 0.173 | P(partition = FF-LIST) 0.08; P(3 colours) 0.697; P(modal partition) 0.173 | — |
| MIN-CONFLICTS (F) | P(valid) 1.0; P(Grundy \| valid) 0.33; distinct partitions 48 | P(valid) 1.0; P(Grundy \| valid) 0.33; distinct partitions 48 | P(valid) 1.0; P(Grundy \| valid) 0.33; distinct partitions 48 | P(valid) 1.0; P(Grundy \| valid) 0.33; distinct partitions 48 | P(valid) 1.0; P(Grundy \| valid) 0.33; distinct partitions 48 | P(valid) 1.0; P(Grundy \| valid) 0.33; distinct partitions 48 | — |
| LOCAL-2-ID (E) | P6 (valid: False) | P7 (valid: False) | P7 (valid: False) | P7 (valid: False) | P7 (valid: False) | P7 (valid: False) | — |
| TEXTBOOK-TRANSFER (A3) | — | — | — | — | — | — | as on c2 (recognises colouring) |
| FRAMING-DEPENDENT STRATEGY (H4 alternative) | — | — | — | — | — | — | a different member than on c2 |

Same prediction in every cell of this set: **EXACT (model solves it, order-free)**: a proper optimal colouring; which of the optimal partitions is chosen is unrelated to listing, labels or answer order; **NOISY-EXACT**: an exact answer with each vertex colour corrupted with prob. eps; conflicts at random places; **PERCEPTION-NOISE**: exact answer for a misread graph; conflicts sit on misread edges; **RANDOM (H)**: uniform random colours; about a third of edges in conflict.

<details><summary>Legend: partitions / assignments</summary>

- **P1** = `v22 v51 v57 v96 | v32 | v43 | v46 v48 v83 v88`
- **P2** = `v22 v32 v46 v51 v57 v83 | v43 v48 | v88 v96`
- **P3** = `v22 v32 v46 v51 v57 v83 | v43 v48 v88 | v96`
- **P4** = `v22 v46 v51 v57 v96 | v32 v83 v88 | v43 v48`
- **P5** = `v22 v46 v51 v57 v96 | v32 | v43 v48 v83 v88`
- **P6** = `v22 v51 v57 v96 | v32 v43 v46 v48 v83 v88`
- **P7** = `v22 v32 v46 v51 v57 v83 v88 v96 | v43 v48`

</details>

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| FF-LIST | Weight: π_FF-LIST (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching FF-LIST above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with GREEDY+REPAIR-LIST (C->F) (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following FF-LIST favour it over the nearest non-tied competitor FF-OUT (AR) by log10 LR = 8.2 (separated). Full set (500 items): detects π_FF-LIST (jointly with the tied theories) >= 0.03 (80% power) and bounds it <= 0.02 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | matched-copy lift (agreement with this copy's prediction minus agreement with the same member's prediction for another copy of the same graph) = (1 - eps - c), pooled over c2-c6; answer changes only at c6; 4 colours on c1-c5 (3 on c6) | commits vertices in listing order; colour = smallest unused by earlier-listed neighbours; no revisions (readout: faithfulness-weighted share T_h) |
| FF-LABEL | Weight: π_FF-LABEL (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching FF-LABEL above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following FF-LABEL favour it over the nearest competitor DPLL-LABEL (D) by log10 LR = 3.3 (separated). Full set (500 items): detects π_FF-LABEL >= 0.09 (80% power) and bounds it <= 0.05 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | matched-copy lift (agreement with this copy's prediction minus agreement with the same member's prediction for another copy of the same graph) = (1 - eps - c), pooled over c2-c6; answer changes c1->c2, then constant (3 colours) | commits in ascending label number (readout: faithfulness-weighted share T_h) |
| FF-OUT (AR) | Weight: π_FF-OUT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | matched-copy lift (agreement with this copy's prediction minus agreement with the same member's prediction for another copy of the same graph) = (1 - eps - c), pooled over c2-c6; answer changes across c2/c3/c4; in c5 answer = FF over its own emitted order in most of items | commits in the requested answer order (readout: faithfulness-weighted share T_h) |
| LF | Weight: π_LF (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching LF above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with DSATUR (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following LF favour it over the nearest non-tied competitor DPLL-LIST (D) by log10 LR = 3.3 (separated). Full set (500 items): detects π_LF (jointly with the tied theories) >= 0.09 (80% power) and bounds it <= 0.05 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | one partition across c2-c6 (= DSATUR's here); match above the other members' baseline | orders by degree; mentions degree (readout: faithfulness-weighted share T_h) |
| DSATUR | Weight: π_DSATUR (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DSATUR above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with LF (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following DSATUR favour it over the nearest non-tied competitor DPLL-LIST (D) by log10 LR = 3.3 (separated). Full set (500 items): detects π_DSATUR (jointly with the tied theories) >= 0.09 (80% power) and bounds it <= 0.05 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | one partition across c2-c6 (= LF's here) | picks the most constrained vertex each step; mentions saturation (readout: faithfulness-weighted share T_h) |
| DPLL-LIST (D, k=3) | Weight: π_DPLL-LIST (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DPLL-LIST above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following DPLL-LIST favour it over the nearest competitor DSATUR by log10 LR = 3.3 (separated). Full set (500 items): detects π_DPLL-LIST >= 0.09 (80% power) and bounds it <= 0.05 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | 3-colour answers; equals DSATUR/LF on c1-c5 and FF-LIST at c6 (where FF-LIST is optimal): separates from FF-LIST on c1-c5 and from DSATUR/LF at c6 | listing order with chronological backtracking where FF-LIST would need a 4th colour (readout: faithfulness-weighted share T_h) |
| DPLL-LABEL (D, k=3) | Weight: π_DPLL-LABEL (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DPLL-LABEL above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following DPLL-LABEL favour it over the nearest competitor FF-LABEL by log10 LR = 3.3 (separated). Full set (500 items): detects π_DPLL-LABEL >= 0.09 (80% power) and bounds it <= 0.05 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | tied with FF-LABEL on c2-c6 (FF-LABEL is optimal there): not separable here; see E5-COL | label order; no backtracking needed on c2-c6 (readout: faithfulness-weighted share T_h) |
| GREEDY+REPAIR-LIST (C->F) | Weight: π_GREEDY+REPAIR-LIST (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching GREEDY+REPAIR-LIST above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with FF-LIST (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following GREEDY+REPAIR-LIST favour it over the nearest non-tied competitor FF-OUT (AR) by log10 LR = 8.2 (separated). Full set (500 items): detects π_GREEDY+REPAIR-LIST (jointly with the tied theories) >= 0.03 (80% power) and bounds it <= 0.02 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | class elimination fails on this graph, so it equals FF-LIST: not separable here; see E5-COL | FF pass in listing order, verification, a failed attempt to empty colour 4 (readout: faithfulness-weighted share T_h) |
| RO-FF (C3) | Weight: π_RO-FF (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | within-copy sample diversity ~ RO-FF's predicted entropy; valid answers Grundy near 1; no order lift | arbitrary starting vertex; commitment order uncorrelated with listing/labels (\|tau\| < 0.2) (readout: faithfulness-weighted share T_h) |
| MIN-CONFLICTS (F) | Weight: π_MIN-CONFLICTS (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer optimal and predicted by no C/D member']. π may vary with item features and model (family I). | order lifts ~ 0; Grundy rate of valid answers near its own 0.33 and the base rate 0.25, far below the first-fit family's 1.0 | complete guess first, then fixes of conflicted vertices anywhere (readout: faithfulness-weighted share T_h) |
| LOCAL-2-ID (E) | Weight: π_LOCAL-2-ID (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching LOCAL-2-ID above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following LOCAL-2-ID favour it over the nearest competitor NOISY-EXACT by log10 LR = 17.3 (separated). Full set (500 items): detects π_LOCAL-2-ID >= 0.01 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | label-sensitive, listing-invariant; invalid colourings | parallel 'each vertex looks at its neighbours' rounds; rarely verbalised (readout: faithfulness-weighted share T_h) |
| EXACT (model solves it, order-free) | Weight: π_EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer optimal and predicted by no C/D member']. π may vary with item features and model (family I). | valid = 1 - eps; every order lift ~ 0; Grundy rate = base rate among optimal colourings | case analysis or search; commitments not in listing order; may cite triangles/structure (readout: faithfulness-weighted share T_h) |
| NOISY-EXACT | Weight: π_NOISY-EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | order lifts ~ 0; conflicts spread uniformly; error rate rises smoothly with n | correct procedure with sporadic slips (a stated colour contradicts the stated rule) (readout: faithfulness-weighted share T_h) |
| PERCEPTION-NOISE | Weight: π_PERCEPTION-NOISE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | most conflicts on edges the trace misquotes (K11); no order lift | quotes an edge that is not in the graph, or omits one, then reasons correctly (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer off the candidate set (arbitrary / invalid)']. π may vary with item features and model (family I). | valid rate ~ 0; answers independent of every manipulation | no per-vertex reasoning (readout: faithfulness-weighted share T_h) |
| TEXTBOOK-TRANSFER (A3) | Weight: framing shift Δπ_TEXTBOOK-TRANSFER (A3) = π(themed) - π(textbook) with 95% interval from paired items; H4 (within domain) predicts \|Δπ\| <= 0.1 | no themed/textbook difference | names the textbook problem (readout: faithfulness-weighted share T_h) |
| FRAMING-DEPENDENT STRATEGY (H4 alternative) | Weight: framing shift Δπ_FRAMING-DEPENDENT STRATEGY (H4 alternative) = π(themed) - π(textbook) with 95% interval from paired items; H4 (within domain) predicts \|Δπ\| <= 0.1 | member identified on themed items differs from c2's in most of pairs | domain talk (rooms, students) instead of colours (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| answers = FF-LIST's prediction on every item | FF-LIST, GREEDY+REPAIR-LIST (C->F) | FF-OUT (AR) (-8), RO-FF (C3) (-9), NOISY-EXACT (-16), DPLL-LIST (D) (-16), FF-LABEL (-16), MIN-CONFLICTS (F) (-18), EXACT (-18), PERCEPTION-NOISE (-18), DPLL-LABEL (D) (-20), DSATUR (-20), LF (-20), LOCAL-2-ID (E) (-20), RANDOM (H) (-27) | — |
| answers = FF-LABEL's prediction on every item | FF-LABEL | DPLL-LABEL (D) (-3), RO-FF (C3) (-6), FF-OUT (AR) (-11), EXACT (-12), MIN-CONFLICTS (F) (-12), NOISY-EXACT (-12), PERCEPTION-NOISE (-13), FF-LIST (-16), GREEDY+REPAIR-LIST (C->F) (-16), DPLL-LIST (D) (-20), DSATUR (-20), LF (-20), LOCAL-2-ID (E) (-20), RANDOM (H) (-27) | — |
| answers = LF's prediction on every item | DSATUR, LF | DPLL-LIST (D) (-3), RO-FF (C3) (-5), EXACT (-10), NOISY-EXACT (-11), PERCEPTION-NOISE (-11), MIN-CONFLICTS (F) (-12), DPLL-LABEL (D) (-16), FF-OUT (AR) (-17), FF-LABEL (-20), FF-LIST (-20), GREEDY+REPAIR-LIST (C->F) (-20), LOCAL-2-ID (E) (-20), RANDOM (H) (-27) | — |
| answers = DSATUR's prediction on every item | DSATUR, LF | DPLL-LIST (D) (-3), RO-FF (C3) (-5), EXACT (-10), NOISY-EXACT (-11), PERCEPTION-NOISE (-11), MIN-CONFLICTS (F) (-12), DPLL-LABEL (D) (-16), FF-OUT (AR) (-17), FF-LABEL (-20), FF-LIST (-20), GREEDY+REPAIR-LIST (C->F) (-20), LOCAL-2-ID (E) (-20), RANDOM (H) (-27) | — |
| answers = DPLL-LIST (D)'s prediction on every item | DPLL-LIST (D) | DSATUR (-3), LF (-3), RO-FF (C3) (-5), EXACT (-10), MIN-CONFLICTS (F) (-11), NOISY-EXACT (-11), PERCEPTION-NOISE (-11), FF-OUT (AR) (-14), DPLL-LABEL (D) (-16), FF-LIST (-16), GREEDY+REPAIR-LIST (C->F) (-16), FF-LABEL (-20), LOCAL-2-ID (E) (-20), RANDOM (H) (-27) | — |
| answers = DPLL-LABEL (D)'s prediction on every item | DPLL-LABEL (D) | FF-LABEL (-3), RO-FF (C3) (-5), EXACT (-10), MIN-CONFLICTS (F) (-10), NOISY-EXACT (-11), PERCEPTION-NOISE (-11), FF-OUT (AR) (-14), DPLL-LIST (D) (-16), DSATUR (-16), LF (-16), FF-LIST (-20), GREEDY+REPAIR-LIST (C->F) (-20), LOCAL-2-ID (E) (-20), RANDOM (H) (-27) | — |
| answers = GREEDY+REPAIR-LIST (C->F)'s prediction on every item | FF-LIST, GREEDY+REPAIR-LIST (C->F) | FF-OUT (AR) (-8), RO-FF (C3) (-9), NOISY-EXACT (-16), DPLL-LIST (D) (-16), FF-LABEL (-16), MIN-CONFLICTS (F) (-18), EXACT (-18), PERCEPTION-NOISE (-18), DPLL-LABEL (D) (-20), DSATUR (-20), LF (-20), LOCAL-2-ID (E) (-20), RANDOM (H) (-27) | — |
| answers = LOCAL-2-ID (E)'s prediction on every item | LOCAL-2-ID (E) | NOISY-EXACT (-17), DPLL-LABEL (D) (-20), DPLL-LIST (D) (-20), DSATUR (-20), EXACT (-20), FF-LABEL (-20), FF-LIST (-20), FF-OUT (AR) (-20), GREEDY+REPAIR-LIST (C->F) (-20), LF (-20), MIN-CONFLICTS (F) (-20), PERCEPTION-NOISE (-20), RO-FF (C3) (-20), RANDOM (H) (-29) | — |
| every answer optimal and predicted by no C/D member | MIN-CONFLICTS (F), EXACT (-0.0) | RO-FF (C3) (-2), FF-OUT (AR) (-8), DPLL-LABEL (D) (-10), DPLL-LIST (D) (-10), DSATUR (-10), FF-LABEL (-10), FF-LIST (-10), GREEDY+REPAIR-LIST (C->F) (-10), LF (-10), LOCAL-2-ID (E) (-10), RANDOM (H) (-17) | NOISY-EXACT (-1.1), PERCEPTION-NOISE (-1.4) |
| every answer off the candidate set (arbitrary / invalid) | RANDOM (H) | NOISY-EXACT (-6), DPLL-LABEL (D) (-8), DPLL-LIST (D) (-8), DSATUR (-8), EXACT (-8), FF-LABEL (-8), FF-LIST (-8), FF-OUT (AR) (-8), GREEDY+REPAIR-LIST (C->F) (-8), LF (-8), LOCAL-2-ID (E) (-8), MIN-CONFLICTS (F) (-8), PERCEPTION-NOISE (-8), RO-FF (C3) (-8) | — |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | DPLL-LABEL (D) | DPLL-LIST (D) | DSATUR | EXACT | FF-LABEL | FF-LIST | FF-OUT (AR) | GREEDY+REPAIR-LIST (C->F) | LF | LOCAL-2-ID (E) | MIN-CONFLICTS (F) | NOISY-EXACT | PERCEPTION-NOISE | RANDOM (H) | RO-FF (C3) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| answers = FF-LIST's prediction on every item | -19.7 | -16.4 | -19.7 | -18.1 | -16.4 | 0.0 | -8.2 | 0.0 | -19.7 | -19.7 | -17.9 | -16.3 | -18.3 | -27.3 | -9.2 |
| answers = FF-LABEL's prediction on every item | -3.3 | -19.7 | -19.7 | -11.6 | 0.0 | -16.4 | -10.7 | -16.4 | -19.7 | -19.7 | -11.8 | -12.1 | -12.8 | -27.3 | -5.6 |
| answers = LF's prediction on every item | -16.4 | -3.3 | 0.0 | -10.0 | -19.7 | -19.7 | -17.2 | -19.7 | 0.0 | -19.7 | -11.6 | -11.1 | -11.4 | -27.3 | -4.6 |
| answers = DSATUR's prediction on every item | -16.4 | -3.3 | 0.0 | -10.0 | -19.7 | -19.7 | -17.2 | -19.7 | 0.0 | -19.7 | -11.6 | -11.1 | -11.4 | -27.3 | -4.6 |
| answers = DPLL-LIST (D)'s prediction on every item | -16.4 | 0.0 | -3.3 | -10.0 | -19.7 | -16.4 | -13.9 | -16.4 | -3.3 | -19.7 | -11.0 | -11.1 | -11.4 | -27.3 | -4.9 |
| answers = DPLL-LABEL (D)'s prediction on every item | 0.0 | -16.4 | -16.4 | -10.0 | -3.3 | -19.7 | -13.9 | -19.7 | -16.4 | -19.7 | -10.4 | -11.1 | -11.4 | -27.3 | -4.7 |
| answers = GREEDY+REPAIR-LIST (C->F)'s prediction on every item | -19.7 | -16.4 | -19.7 | -18.1 | -16.4 | 0.0 | -8.2 | 0.0 | -19.7 | -19.7 | -17.9 | -16.3 | -18.3 | -27.3 | -9.2 |
| answers = LOCAL-2-ID (E)'s prediction on every item | -19.7 | -19.7 | -19.7 | -19.7 | -19.7 | -19.7 | -19.7 | -19.7 | -19.7 | 0.0 | -19.7 | -17.3 | -19.7 | -29.1 | -19.7 |
| every answer optimal and predicted by no C/D member | -9.7 | -9.7 | -9.7 | -0.0 | -9.7 | -9.7 | -8.5 | -9.7 | -9.7 | -9.7 | 0.0 | -1.1 | -1.4 | -17.3 | -2.5 |
| every answer off the candidate set (arbitrary / invalid) | -8.4 | -8.4 | -8.4 | -8.4 | -8.4 | -8.4 | -8.4 | -8.4 | -8.4 | -8.4 | -8.4 | -6.0 | -8.4 | 0.0 | -8.4 |

</details>

**Not separated by this set.** FF-LABEL vs DPLL-LABEL (FF-LABEL is optimal on c2-c6, so they coincide) and FF-LIST vs GREEDY+REPAIR-LIST (class elimination fails on this graph) -> E5-COL and trace codes (backtracking vs repair). LF vs DSATUR coincide on this graph -> E2-COL. DPLL-LIST coincides with DSATUR/LF on c1-c5 but splits from them at c6.

### `E1-COL-A` · `c1-NAT`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "p": 0.38, "seed": 11, "copy": "labels ascend along listing; answer in listing order", "label_map_to_c2": {"v83": "v32", "v43": "v88", "v88": "v22", "v51": "v51", "v96": "v43", "v22": "v48", "v57": "v46", "v32": "v96", "v48": "v57", "v46": "v83"}}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v22, v32, v43, v46, v48, v51, v57, v83, v88, v96
Neighbours (one line per vertex, same order):
v22: v32, v83
v32: v22, v46, v83, v96
v43: v48, v51, v88
v46: v32
v48: v43, v96
v51: v43
v57: v96
v83: v22, v32, v96
v88: v43, v96
v96: v32, v48, v57, v83, v88

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v22, v32, v43, v46, v48, v51, v57, v83, v88, v96.
```

Ground truth: chromatic_number = 3; n_optimal_partitions = 48; grundy_fraction_among_optimal = 0.25; check = any proper colouring; optimal iff it uses 3 colours

Item hypotheses: column `c1-NAT` of the outputs table, plus the eval and trace rows above. Isomorphic copies: identical edge set and label multiset; token counts equal across copies. FF-LIST changes only in c6; FF-LABEL changes between c1 and c2; FF-OUT follows the requested answer order.

### `E1-COL-A` · `c2-RELABEL`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "p": 0.38, "seed": 11, "copy": "same listing as c1; labels permuted; answer in listing order"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v48, v96, v88, v83, v57, v51, v46, v32, v22, v43
Neighbours (one line per vertex, same order):
v48: v96, v32
v96: v48, v83, v32, v43
v88: v57, v51, v22
v83: v96
v57: v88, v43
v51: v88
v46: v43
v32: v48, v96, v43
v22: v88, v43
v43: v96, v57, v46, v32, v22

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v48, v96, v88, v83, v57, v51, v46, v32, v22, v43.
```

Ground truth: chromatic_number = 3; n_optimal_partitions = 48; grundy_fraction_among_optimal = 0.25; check = any proper colouring; optimal iff it uses 3 colours

Item hypotheses: column `c2-RELABEL` of the outputs table, plus the eval and trace rows above. Isomorphic copies: identical edge set and label multiset; token counts equal across copies. FF-LIST changes only in c6; FF-LABEL changes between c1 and c2; FF-OUT follows the requested answer order.

### `E1-COL-A` · `c3-ANS-LABEL`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "p": 0.38, "seed": 11, "copy": "as c2; answer requested in label order"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v48, v96, v88, v83, v57, v51, v46, v32, v22, v43
Neighbours (one line per vertex, same order):
v48: v96, v32
v96: v48, v83, v32, v43
v88: v57, v51, v22
v83: v96
v57: v88, v43
v51: v88
v46: v43
v32: v48, v96, v43
v22: v88, v43
v43: v96, v57, v46, v32, v22

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v22, v32, v43, v46, v48, v51, v57, v83, v88, v96.
```

Ground truth: chromatic_number = 3; n_optimal_partitions = 48; grundy_fraction_among_optimal = 0.25; check = any proper colouring; optimal iff it uses 3 colours

Item hypotheses: column `c3-ANS-LABEL` of the outputs table, plus the eval and trace rows above. Isomorphic copies: identical edge set and label multiset; token counts equal across copies. FF-LIST changes only in c6; FF-LABEL changes between c1 and c2; FF-OUT follows the requested answer order.

### `E1-COL-A` · `c4-ANS-RAND`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "p": 0.38, "seed": 11, "copy": "as c2; answer requested in a random order"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v48, v96, v88, v83, v57, v51, v46, v32, v22, v43
Neighbours (one line per vertex, same order):
v48: v96, v32
v96: v48, v83, v32, v43
v88: v57, v51, v22
v83: v96
v57: v88, v43
v51: v88
v46: v43
v32: v48, v96, v43
v22: v88, v43
v43: v96, v57, v46, v32, v22

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v51, v96, v22, v46, v32, v57, v83, v88, v48, v43.
```

Ground truth: chromatic_number = 3; n_optimal_partitions = 48; grundy_fraction_among_optimal = 0.25; check = any proper colouring; optimal iff it uses 3 colours

Item hypotheses: column `c4-ANS-RAND` of the outputs table, plus the eval and trace rows above. Isomorphic copies: identical edge set and label multiset; token counts equal across copies. FF-LIST changes only in c6; FF-LABEL changes between c1 and c2; FF-OUT follows the requested answer order.

### `E1-COL-A` · `c5-ANS-FREE`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "p": 0.38, "seed": 11, "copy": "as c2; answer order left to the model"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v48, v96, v88, v83, v57, v51, v46, v32, v22, v43
Neighbours (one line per vertex, same order):
v48: v96, v32
v96: v48, v83, v32, v43
v88: v57, v51, v22
v83: v96
v57: v88, v43
v51: v88
v46: v43
v32: v48, v96, v43
v22: v88, v43
v43: v96, v57, v46, v32, v22

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in any order you like.
```

Ground truth: chromatic_number = 3; n_optimal_partitions = 48; grundy_fraction_among_optimal = 0.25; check = any proper colouring; optimal iff it uses 3 colours

Item hypotheses: column `c5-ANS-FREE` of the outputs table, plus the eval and trace rows above. Isomorphic copies: identical edge set and label multiset; token counts equal across copies. FF-LIST changes only in c6; FF-LABEL changes between c1 and c2; FF-OUT follows the requested answer order.

### `E1-COL-A` · `c6-RELIST`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "p": 0.38, "seed": 11, "copy": "labels as c2; vertices re-listed in a new order; answer in that order"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v32, v96, v51, v43, v83, v48, v46, v88, v57, v22
Neighbours (one line per vertex, same order):
v32: v96, v43, v48
v96: v32, v43, v83, v48
v51: v88
v43: v32, v96, v46, v57, v22
v83: v96
v48: v32, v96
v46: v43
v88: v51, v57, v22
v57: v43, v88
v22: v43, v88

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v32, v96, v51, v43, v83, v48, v46, v88, v57, v22.
```

Ground truth: chromatic_number = 3; n_optimal_partitions = 48; grundy_fraction_among_optimal = 0.25; check = any proper colouring; optimal iff it uses 3 colours

Item hypotheses: column `c6-RELIST` of the outputs table, plus the eval and trace rows above. Isomorphic copies: identical edge set and label multiset; token counts equal across copies. FF-LIST changes only in c6; FF-LABEL changes between c1 and c2; FF-OUT follows the requested answer order.

### `E1-COL-A` · `c2-RELABEL/theme-exams`

*Domain:* colouring · *framing:* realistic: exam timetabling · *params:* `{"same_graph_as": "c2", "theme": "exams"}`

Prompt:

```text
A college must timetable 10 exams. Two exams that share a student cannot be in the same slot.
Exams (in this order): c48, c96, c88, c83, c57, c51, c46, c32, c22, c43
Clashes (each exam followed by the exams it clashes with):
c48: c96, c32
c96: c48, c83, c32, c43
c88: c57, c51, c22
c83: c96
c57: c88, c43
c51: c88
c46: c43
c32: c48, c96, c43
c22: c88, c43
c43: c96, c57, c46, c32, c22

Give each exam a slot number 1, 2, 3, ... so that clashing exams get different slots, using as few slots as possible.
After the line ANSWER:, write one line `exam: slot` per exam, in this order: c48, c96, c88, c83, c57, c51, c46, c32, c22, c43.
```

Ground truth: chromatic_number = 3; n_optimal_partitions = 48

Item hypotheses: column `c2-RELABEL/theme-exams` of the outputs table, plus the eval and trace rows above. Re-themed c2 (course labels c##). Every C prediction is identical to c2 up to the label prefix; a change between c2 and this item is a framing effect (H4), not an order effect.

<a id="e1-sat-a"></a>
## E1 · Order source on isomorphic copies (3-SAT)  (`E1-SAT-A`)

**Reasoning question.** How is the weight behind the returned satisfying assignment split between first-mention order (GREEDY-MENTION), label order (GREEDY-INDEX), static polarity (POLARITY, C0), unit-clause steps (UC-DET, C2) and search?

**Controlled.** Clause multiset, labels' token counts, answer length.  
**Varied.** Labels (c1→c2), clause order (c2→c6).

**Outputs by cell** (each theory's predicted answer on each item) — c1 uses its own labels in the prompt; its column is shown mapped into c2's labels (`params.label_map_to_c2`), so equal codes mean the same structural answer

| Theory | `c1-NAT` | `c2-RELABEL` | `c6-RELIST` |
|---|---|---|---|
| GREEDY-MENTION | S1 | S1 | S2 |
| GREEDY-INDEX | S1 | S3 | S3 |
| POLARITY (C0) | S4 | S4 | S4 |
| UC-DET (C2) | S1 | S1 | S5 (falsified: C19, C21) |
| DPLL-MENTION (D) | S1 | S1 | S1 |
| RO-GREEDY (C3) | P(satisfying) 0.566 | P(satisfying) 0.566 | P(satisfying) 0.566 |
| ALL-T (A1) | S6 | S6 | S6 |
| NOISY-EXACT | a solution with random flips | a solution with random flips | a solution with random flips |
| PERCEPTION-NOISE | a solution of a misread formula | a solution of a misread formula | a solution of a misread formula |

Same prediction in every cell of this set: **WALK (F)**: a satisfying assignment reached by flips from a random start; order-free; **EXACT (order-free)**: one of the 8 solutions, unrelated to order or labels; **RANDOM (H)**: uniform random assignment (7/8 of clauses true on average).

<details><summary>Legend: partitions / assignments</summary>

- **S1** = `x10=T x21=F x22=F x32=T x38=T x57=T x60=T x78=F`
- **S2** = `x10=T x21=F x22=F x32=F x38=F x57=T x60=T x78=F`
- **S3** = `x10=T x21=F x22=T x32=T x38=F x57=F x60=T x78=F`
- **S4** = `x10=T x21=F x22=T x32=T x38=F x57=T x60=T x78=F`
- **S5** = `x10=F x21=T x22=F x32=F x38=T x57=F x60=T x78=F`
- **S6** = `x10=T x21=T x22=T x32=T x38=T x57=T x60=T x78=T`

</details>

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| GREEDY-MENTION | Weight: π_GREEDY-MENTION (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching GREEDY-MENTION above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following GREEDY-MENTION favour it over the nearest competitor DPLL-MENTION (D) by log10 LR = 2.3 (separated). Full set (500 items): detects π_GREEDY-MENTION >= 0.06 (80% power) and bounds it <= 0.04 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | matched-copy lift = (1 - eps - c) (Hamming-kernel likelihood), pooled over copies; answer changes c2->c6 (clause order) only | variables in first-mention order with per-variable counts of still-open clauses; no revisions (readout: faithfulness-weighted share T_h) |
| GREEDY-INDEX | Weight: π_GREEDY-INDEX (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching GREEDY-INDEX above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following GREEDY-INDEX favour it over the nearest competitor EXACT by log10 LR = 2.7 (separated). Full set (500 items): detects π_GREEDY-INDEX >= 0.05 (80% power) and bounds it <= 0.03 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | matched-copy lift = (1 - eps - c) (Hamming-kernel likelihood), pooled over copies; answer changes c1->c2 (labels) only | variables in label order (readout: faithfulness-weighted share T_h) |
| POLARITY (C0) | Weight: π_POLARITY (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching POLARITY above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following POLARITY favour it over the nearest competitor NOISY-EXACT by log10 LR = 5.8 (separated). Full set (500 items): detects π_POLARITY >= 0.02 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | answer constant across all copies and equal to POLARITY | occurrence tallies over all clauses; no use of earlier choices (readout: faithfulness-weighted share T_h) |
| UC-DET (C2) | Weight: π_UC-DET (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching UC-DET above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following UC-DET favour it over the nearest competitor DPLL-MENTION (D) by log10 LR = 2.3 (separated). Full set (500 items): detects π_UC-DET >= 0.06 (80% power) and bounds it <= 0.04 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | matches UC-DET; in c6 falsifies exactly the clauses UC-DET falsifies | 'forced'/'unit clause' steps between free choices (readout: faithfulness-weighted share T_h) |
| DPLL-MENTION (D) | Weight: π_DPLL-MENTION (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DPLL-MENTION above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following DPLL-MENTION favour it over the nearest competitor GREEDY-MENTION by log10 LR = 2.3 (separated). Full set (500 items): detects π_DPLL-MENTION >= 0.06 (80% power) and bounds it <= 0.04 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | valid in every copy; equals DPLL's first solution | decisions plus propagation, backtracking on conflict (readout: faithfulness-weighted share T_h) |
| RO-GREEDY (C3) | Weight: no likelihood computed for this theory in this set (see the coverage matrix for the set that bounds it). | sample diversity within a copy; no order lift | arbitrary variable order (readout: faithfulness-weighted share T_h) |
| WALK (F) | Weight: π_WALK (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer a solution predicted by no member']. π may vary with item features and model (family I). | order lifts ~ 0 | full guess, then flips of variables in false clauses (readout: faithfulness-weighted share T_h) |
| ALL-T (A1) | Weight: π_ALL-T (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching ALL-T above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following ALL-T favour it over the nearest competitor NOISY-EXACT by log10 LR = 5.8 (separated). Full set (500 items): detects π_ALL-T >= 0.02 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | answer all-T regardless of copy | no per-variable reasoning (readout: faithfulness-weighted share T_h) |
| EXACT (order-free) | Weight: π_EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer a solution predicted by no member']. π may vary with item features and model (family I). | valid = 1 - eps; all order lifts ~ 0 | search with revisions (readout: faithfulness-weighted share T_h) |
| NOISY-EXACT | Weight: π_NOISY-EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer a solution predicted by no member']. π may vary with item features and model (family I). | order lifts ~ 0; falsified clauses uniform | correct procedure, sporadic slips (readout: faithfulness-weighted share T_h) |
| PERCEPTION-NOISE | Weight: π_PERCEPTION-NOISE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer a solution predicted by no member']. π may vary with item features and model (family I). | falsified clauses are ones the trace misquotes | misquoted literal (K11) (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | valid rate ~ (8 solutions / 256) | none (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| answers = GREEDY-MENTION's prediction on every item | GREEDY-MENTION | DPLL-MENTION (D) (-2), UC-DET (C2) (-2), EXACT (-3), WALK (F) (-3), PERCEPTION-NOISE (-3), NOISY-EXACT (-3), GREEDY-INDEX (-5), RANDOM (H) (-7), ALL-T (A1) (-7), POLARITY (C0) (-7) | — |
| answers = GREEDY-INDEX's prediction on every item | GREEDY-INDEX | EXACT (-3), WALK (F) (-3), PERCEPTION-NOISE (-3), NOISY-EXACT (-3), DPLL-MENTION (D) (-5), GREEDY-MENTION (-5), UC-DET (C2) (-5), RANDOM (H) (-7), ALL-T (A1) (-7), POLARITY (C0) (-7) | — |
| answers = POLARITY (C0)'s prediction on every item | POLARITY (C0) | NOISY-EXACT (-6), PERCEPTION-NOISE (-6), RANDOM (H) (-7), ALL-T (A1) (-7), DPLL-MENTION (D) (-7), EXACT (-7), GREEDY-INDEX (-7), GREEDY-MENTION (-7), UC-DET (C2) (-7), WALK (F) (-7) | — |
| answers = UC-DET (C2)'s prediction on every item | UC-DET (C2) | DPLL-MENTION (D) (-2), GREEDY-MENTION (-2), NOISY-EXACT (-4), EXACT (-4), WALK (F) (-4), PERCEPTION-NOISE (-4), GREEDY-INDEX (-5), RANDOM (H) (-7), ALL-T (A1) (-7), POLARITY (C0) (-7) | — |
| answers = DPLL-MENTION (D)'s prediction on every item | DPLL-MENTION (D) | GREEDY-MENTION (-2), UC-DET (C2) (-2), EXACT (-3), WALK (F) (-3), PERCEPTION-NOISE (-3), NOISY-EXACT (-3), GREEDY-INDEX (-5), RANDOM (H) (-7), ALL-T (A1) (-7), POLARITY (C0) (-7) | — |
| answers = ALL-T (A1)'s prediction on every item | ALL-T (A1) | NOISY-EXACT (-6), RANDOM (H) (-7), DPLL-MENTION (D) (-7), EXACT (-7), GREEDY-INDEX (-7), GREEDY-MENTION (-7), PERCEPTION-NOISE (-7), POLARITY (C0) (-7), UC-DET (C2) (-7), WALK (F) (-7) | — |
| every answer a solution predicted by no member | EXACT, WALK (F), PERCEPTION-NOISE (-0.2), NOISY-EXACT (-0.5) | RANDOM (H) (-4), ALL-T (A1) (-4), DPLL-MENTION (D) (-4), GREEDY-INDEX (-4), GREEDY-MENTION (-4), POLARITY (C0) (-4), UC-DET (C2) (-4) | — |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | ALL-T (A1) | DPLL-MENTION (D) | EXACT | GREEDY-INDEX | GREEDY-MENTION | NOISY-EXACT | PERCEPTION-NOISE | POLARITY (C0) | RANDOM (H) | UC-DET (C2) | WALK (F) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| answers = GREEDY-MENTION's prediction on every item | -7.0 | -2.3 | -2.7 | -4.7 | 0.0 | -3.1 | -2.9 | -7.0 | -6.9 | -2.3 | -2.7 |
| answers = GREEDY-INDEX's prediction on every item | -7.0 | -4.7 | -2.7 | 0.0 | -4.7 | -3.1 | -2.8 | -7.0 | -6.9 | -4.7 | -2.7 |
| answers = POLARITY (C0)'s prediction on every item | -7.0 | -7.0 | -7.0 | -7.0 | -7.0 | -5.8 | -6.1 | 0.0 | -6.9 | -7.0 | -7.0 |
| answers = UC-DET (C2)'s prediction on every item | -7.0 | -2.3 | -4.1 | -4.7 | -2.3 | -4.0 | -4.3 | -7.0 | -6.9 | 0.0 | -4.1 |
| answers = DPLL-MENTION (D)'s prediction on every item | -7.0 | 0.0 | -2.7 | -4.7 | -2.3 | -3.1 | -2.9 | -7.0 | -6.9 | -2.3 | -2.7 |
| answers = ALL-T (A1)'s prediction on every item | 0.0 | -7.0 | -7.0 | -7.0 | -7.0 | -5.8 | -7.0 | -7.0 | -6.9 | -7.0 | -7.0 |
| every answer a solution predicted by no member | -4.3 | -4.3 | 0.0 | -4.3 | -4.3 | -0.5 | -0.2 | -4.3 | -4.3 | -4.3 | 0.0 |

</details>

**Not separated by this set.** UC-DET and DPLL-MENTION coincide with GREEDY-MENTION on c1 and c2; c6 separates them (UC-DET falsifies C19, C21; DPLL and GREEDY return different valid assignments). WALK vs EXACT are both order-free → E4 co-failure.

### `E1-SAT-A` · `c1-NAT`

*Domain:* 3-SAT · *framing:* textbook · *params:* `{"n": 8, "m": 24, "alpha": 3.0, "seed": 5, "copy": "labels ascend in first-mention order", "label_map_to_c2": {"x22": "x22", "x38": "x78", "x10": "x57", "x78": "x21", "x32": "x32", "x60": "x38", "x57": "x60", "x21": "x10"}}`

<details><summary>Prompt</summary>

```text
A formula over 8 true/false variables. Every clause must contain at least one true literal.
C1: not x10 or not x21 or not x22
C2: not x32 or not x10 or not x38
C3: x57 or x21 or x60
C4: x21 or not x60 or x57
C5: x10 or not x38 or not x57
C6: x21 or not x57 or x60
C7: not x32 or x21 or x10
C8: not x78 or not x57 or not x22
C9: x32 or not x21 or x10
C10: not x57 or x10 or not x78
C11: x78 or x57 or not x60
C12: not x10 or not x21 or not x78
C13: not x60 or x21 or x32
C14: not x21 or not x60 or not x22
C15: x22 or not x38 or x32
C16: x78 or not x38 or x57
C17: x57 or not x78 or x60
C18: x78 or not x60 or not x38
C19: x32 or not x38 or not x60
C20: x22 or x10 or not x32
C21: x22 or x78 or x21
C22: not x10 or not x78 or not x57
C23: not x38 or x22 or x60
C24: x21 or not x32 or x38

Find values for all variables that make every clause true, or say UNSAT if none exist.
After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, in this order: x10, x21, x22, x32, x38, x57, x60, x78.
```

</details>

Ground truth: satisfiable = True; n_solutions = 8; check = any satisfying assignment

Item hypotheses: column `c1-NAT` of the outputs table, plus the eval and trace rows above. GREEDY-MENTION's prediction moves with clause order (c6); GREEDY-INDEX's with labels (c1 vs c2); POLARITY and UC's unit steps do not.

### `E1-SAT-A` · `c2-RELABEL`

*Domain:* 3-SAT · *framing:* textbook · *params:* `{"n": 8, "m": 24, "alpha": 3.0, "seed": 5, "copy": "same clauses and order; variables relabelled"}`

<details><summary>Prompt</summary>

```text
A formula over 8 true/false variables. Every clause must contain at least one true literal.
C1: not x57 or not x10 or not x22
C2: not x32 or not x57 or not x78
C3: x60 or x10 or x38
C4: x10 or not x38 or x60
C5: x57 or not x78 or not x60
C6: x10 or not x60 or x38
C7: not x32 or x10 or x57
C8: not x21 or not x60 or not x22
C9: x32 or not x10 or x57
C10: not x60 or x57 or not x21
C11: x21 or x60 or not x38
C12: not x57 or not x10 or not x21
C13: not x38 or x10 or x32
C14: not x10 or not x38 or not x22
C15: x22 or not x78 or x32
C16: x21 or not x78 or x60
C17: x60 or not x21 or x38
C18: x21 or not x38 or not x78
C19: x32 or not x78 or not x38
C20: x22 or x57 or not x32
C21: x22 or x21 or x10
C22: not x57 or not x21 or not x60
C23: not x78 or x22 or x38
C24: x10 or not x32 or x78

Find values for all variables that make every clause true, or say UNSAT if none exist.
After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, in this order: x57, x10, x22, x32, x78, x60, x38, x21.
```

</details>

Ground truth: satisfiable = True; n_solutions = 8; check = any satisfying assignment

Item hypotheses: column `c2-RELABEL` of the outputs table, plus the eval and trace rows above. GREEDY-MENTION's prediction moves with clause order (c6); GREEDY-INDEX's with labels (c1 vs c2); POLARITY and UC's unit steps do not.

### `E1-SAT-A` · `c6-RELIST`

*Domain:* 3-SAT · *framing:* textbook · *params:* `{"n": 8, "m": 24, "alpha": 3.0, "seed": 5, "copy": "labels as c2; clause order shuffled"}`

<details><summary>Prompt</summary>

```text
A formula over 8 true/false variables. Every clause must contain at least one true literal.
C1: x60 or not x21 or x38
C2: x57 or not x78 or not x60
C3: x32 or not x10 or x57
C4: x22 or x21 or x10
C5: not x57 or not x10 or not x22
C6: x21 or x60 or not x38
C7: not x57 or not x21 or not x60
C8: not x21 or not x60 or not x22
C9: not x78 or x22 or x38
C10: x60 or x10 or x38
C11: x21 or not x38 or not x78
C12: x21 or not x78 or x60
C13: not x57 or not x10 or not x21
C14: x22 or x57 or not x32
C15: x22 or not x78 or x32
C16: x10 or not x38 or x60
C17: x10 or not x60 or x38
C18: x32 or not x78 or not x38
C19: not x38 or x10 or x32
C20: not x32 or x10 or x57
C21: not x60 or x57 or not x21
C22: x10 or not x32 or x78
C23: not x10 or not x38 or not x22
C24: not x32 or not x57 or not x78

Find values for all variables that make every clause true, or say UNSAT if none exist.
After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, in this order: x60, x21, x38, x57, x78, x32, x10, x22.
```

</details>

Ground truth: satisfiable = True; n_solutions = 8; check = any satisfying assignment

Item hypotheses: column `c6-RELIST` of the outputs table, plus the eval and trace rows above. GREEDY-MENTION's prediction moves with clause order (c6); GREEDY-INDEX's with labels (c1 vs c2); POLARITY and UC's unit steps do not.

<a id="e2-col-a"></a>
## E2 · Rule discrimination by single-edge edits (graph colouring)  (`E2-COL-A`)

**Reasoning question.** Within constructive colouring, how is weight split between first-fit in listing order, DSATUR (most constrained first) and largest-first? Each edit changes exactly one rule's output (computed), leaving the chromatic number unchanged, except G-ONLY, which changes only the chromatic number.

**Controlled.** Listing order and labels identical across the set; every edit adds one edge (one neighbour entry in two lines).  
**Varied.** Which edge is added (cell = which members' outputs change).

**Outputs by cell** (each theory's predicted answer on each item)

| Theory | `BASE` | `D(FF\|DSATUR)` | `D(DSATUR\|FF)` | `PLACEBO` | `G-ONLY` |
|---|---|---|---|---|---|
| FF-LIST | P1 | P2 | P1 | P1 | P1 |
| DSATUR | P3 | P3 | P4 | P3 | P3 |
| LF | P4 | P4 | P4 | P4 | P5 |
| DPLL-LIST (D) | P6 | P6 | P6 | P6 | P1 |
| EXACT (order-free) | a proper 3-colouring | a proper 3-colouring | a proper 3-colouring | a proper 3-colouring | a proper 4-colouring |
| NOISY-EXACT | exact answer with slips | exact answer with slips | exact answer with slips | exact answer with slips | exact answer with slips |
| PERCEPTION-NOISE | exact for a misread graph | exact for a misread graph | exact for a misread graph | exact for a misread graph | exact for a misread graph |
| RANDOM (H) | random colours | random colours | random colours | random colours | random colours |

Same prediction in every cell of this set: **MIN-CONFLICTS (F)**: an order-free proper colouring; one added edge barely moves its distribution.

<details><summary>Legend: partitions / assignments</summary>

- **P1** = `v22 v79 v99 | v24 v52 v64 | v29 | v39 v46 v58`
- **P2** = `v22 v79 v99 | v24 v52 v64 | v29 v58 | v39 v46`
- **P3** = `v22 v39 v79 | v24 v52 v64 | v29 | v46 v58 v99`
- **P4** = `v22 v39 v46 | v24 v79 | v29 v52 v58 v64 v99`
- **P5** = `v22 v39 v46 | v24 v79 | v29 v52 v64 v99 | v58`
- **P6** = `v22 v39 v79 | v24 v46 | v29 v52 v58 v64 v99`

</details>

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| FF-LIST | Weight: π_FF-LIST (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching FF-LIST above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following FF-LIST favour it over the nearest competitor RO-FF (C3) by log10 LR = 8.2 (separated). Full set (720 items): detects π_FF-LIST >= 0.02 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] flip(D(FF\|DSATUR)) - flip(PLACEBO) = 1 - eps above placebo and DDI(FF,DSATUR) positive  | listing order; mex rule; no revisions (readout: faithfulness-weighted share T_h) |
| DSATUR | Weight: π_DSATUR (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DSATUR above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following DSATUR favour it over the nearest competitor RO-FF (C3) by log10 LR = 7.0 (separated). Full set (720 items): detects π_DSATUR >= 0.02 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] flip(D(DSATUR\|FF)) - flip(PLACEBO) = 1 - eps above placebo and DDI negative | most-constrained-first; saturation mentioned (readout: faithfulness-weighted share T_h) |
| LF | Weight: π_LF (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching LF above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following LF favour it over the nearest competitor EXACT by log10 LR = 3.3 (separated). Full set (720 items): detects π_LF >= 0.06 (80% power) and bounds it <= 0.04 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] flips where LF's output changes (tracked as a covariate) | degree order (readout: faithfulness-weighted share T_h) |
| DPLL-LIST (D) | Weight: π_DPLL-LIST (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DPLL-LIST above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following DPLL-LIST favour it over the nearest competitor EXACT by log10 LR = 3.3 (separated). Full set (720 items): detects π_DPLL-LIST >= 0.06 (80% power) and bounds it <= 0.04 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] answer = 3-colouring at BASE (FF needs 4); flips only where its first solution changes | backtracking when a 4th colour is needed (readout: faithfulness-weighted share T_h) |
| MIN-CONFLICTS (F) | Weight: π_MIN-CONFLICTS (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer optimal and predicted by no C/D member']. π may vary with item features and model (family I). | [cell: -] flip rates equal across D cells; slightly higher in G-ONLY | guess-then-fix (readout: faithfulness-weighted share T_h) |
| EXACT (order-free) | Weight: π_EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer optimal and predicted by no C/D member']. π may vary with item features and model (family I). | [cell: -] flip(G-ONLY) - flip(PLACEBO) = 1 - eps above placebo; no difference between D cells | search, revisions (readout: faithfulness-weighted share T_h) |
| NOISY-EXACT | Weight: π_NOISY-EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer optimal and predicted by no C/D member']. π may vary with item features and model (family I). | [cell: -] flip rates equal in all cells | sporadic slips (readout: faithfulness-weighted share T_h) |
| PERCEPTION-NOISE | Weight: π_PERCEPTION-NOISE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | [cell: -] flip rates equal; conflicts on misquoted edges | K11 misquotes (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer off the candidate set (arbitrary / invalid)']. π may vary with item features and model (family I). | [cell: -] flip ~ 1 in all cells (answers never repeat) | none (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| answers = FF-LIST's prediction on every item | FF-LIST | RO-FF (C3) (-8), DPLL-LIST (D) (-11), NOISY-EXACT (-11), MIN-CONFLICTS (F) (-13), EXACT (-13), PERCEPTION-NOISE (-13), DSATUR (-14), LF (-14), RANDOM (H) (-23) | — |
| answers = DSATUR's prediction on every item | DSATUR | RO-FF (C3) (-7), NOISY-EXACT (-10), EXACT (-10), MIN-CONFLICTS (F) (-11), PERCEPTION-NOISE (-11), LF (-12), DPLL-LIST (D) (-14), FF-LIST (-14), RANDOM (H) (-23) | — |
| answers = LF's prediction on every item | LF | EXACT (-3), NOISY-EXACT (-4), RO-FF (C3) (-4), MIN-CONFLICTS (F) (-5), PERCEPTION-NOISE (-5), DSATUR (-12), DPLL-LIST (D) (-14), FF-LIST (-14), RANDOM (H) (-23) | — |
| answers = DPLL-LIST (D)'s prediction on every item | DPLL-LIST (D) | EXACT (-3), MIN-CONFLICTS (F) (-4), NOISY-EXACT (-4), RO-FF (C3) (-4), PERCEPTION-NOISE (-5), FF-LIST (-11), DSATUR (-14), LF (-14), RANDOM (H) (-23) | — |
| every answer optimal and predicted by no C/D member | MIN-CONFLICTS (F), EXACT, RO-FF (C3) (-0.0), NOISY-EXACT (-0.1) | RANDOM (H) (-3) | PERCEPTION-NOISE (-0.6), DPLL-LIST (D) (-1.3), DSATUR (-1.3), FF-LIST (-1.3), LF (-1.3) |
| every answer off the candidate set (arbitrary / invalid) | RANDOM (H) | NOISY-EXACT (-5), DPLL-LIST (D) (-7), DSATUR (-7), EXACT (-7), FF-LIST (-7), LF (-7), MIN-CONFLICTS (F) (-7), PERCEPTION-NOISE (-7), RO-FF (C3) (-7) | — |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | DPLL-LIST (D) | DSATUR | EXACT | FF-LIST | LF | MIN-CONFLICTS (F) | NOISY-EXACT | PERCEPTION-NOISE | RANDOM (H) | RO-FF (C3) |
|---|---|---|---|---|---|---|---|---|---|---|
| answers = FF-LIST's prediction on every item | -10.7 | -14.2 | -12.8 | 0.0 | -14.2 | -12.8 | -11.4 | -13.4 | -23.0 | -8.2 |
| answers = DSATUR's prediction on every item | -14.2 | 0.0 | -10.5 | -14.2 | -11.5 | -10.9 | -9.6 | -11.3 | -23.0 | -7.0 |
| answers = LF's prediction on every item | -14.2 | -11.5 | -3.3 | -14.2 | 0.0 | -4.6 | -4.3 | -5.1 | -23.0 | -4.3 |
| answers = DPLL-LIST (D)'s prediction on every item | 0.0 | -14.2 | -3.3 | -10.7 | -14.2 | -3.8 | -4.3 | -5.1 | -23.0 | -4.5 |
| every answer optimal and predicted by no C/D member | -1.3 | -1.3 | -0.0 | -1.3 | -1.3 | 0.0 | -0.1 | -0.6 | -2.7 | -0.0 |
| every answer off the candidate set (arbitrary / invalid) | -7.0 | -7.0 | -7.0 | -7.0 | -7.0 | -7.0 | -5.0 | -7.0 | 0.0 | -7.0 |

</details>

**Not separated by this set.** LF and DSATUR coincide after the D(DSATUR|FF) edit; LF vs DSATUR needs its own double dissociation (in the full E2 grid). FF-LIST vs DPLL-LIST *is* separated here: at BASE, FF-LIST needs 4 colours and DPLL-LIST finds a 3-colouring.

### `E2-COL-A` · `BASE`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "seed": 23, "edit": "none", "listing": "identical across the set", "labels": "identical across the set"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v99, v39, v79, v22, v46, v52, v24, v58, v29, v64
Neighbours (one line per vertex, same order):
v99: v39, v24
v39: v99, v52, v24
v79: v46, v52, v29, v64
v22: v24, v58, v64
v46: v79, v52, v29, v64
v52: v39, v79, v46
v24: v99, v39, v22, v58, v29
v58: v22, v24
v29: v79, v46, v24
v64: v79, v22, v46

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v99, v39, v79, v22, v46, v52, v24, v58, v29, v64.
```

Ground truth: chromatic_number = 3

Item hypotheses: column `BASE` of the outputs table, plus the eval and trace rows above. Single-edge additions to the base. Cell = which members' outputs change (computed). An edge between differently coloured FF vertices never changes FF (lemma), which makes D(DSATUR|FF) edits easy to find.

### `E2-COL-A` · `D(FF|DSATUR)`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "seed": 23, "edit": "add edge v39-v58", "listing": "identical across the set", "labels": "identical across the set"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v99, v39, v79, v22, v46, v52, v24, v58, v29, v64
Neighbours (one line per vertex, same order):
v99: v39, v24
v39: v99, v52, v24, v58
v79: v46, v52, v29, v64
v22: v24, v58, v64
v46: v79, v52, v29, v64
v52: v39, v79, v46
v24: v99, v39, v22, v58, v29
v58: v39, v22, v24
v29: v79, v46, v24
v64: v79, v22, v46

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v99, v39, v79, v22, v46, v52, v24, v58, v29, v64.
```

Ground truth: chromatic_number = 3

Item hypotheses: column `D(FF\|DSATUR)` of the outputs table, plus the eval and trace rows above. Single-edge additions to the base. Cell = which members' outputs change (computed). An edge between differently coloured FF vertices never changes FF (lemma), which makes D(DSATUR|FF) edits easy to find.

### `E2-COL-A` · `D(DSATUR|FF)`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "seed": 23, "edit": "add edge v39-v29", "listing": "identical across the set", "labels": "identical across the set"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v99, v39, v79, v22, v46, v52, v24, v58, v29, v64
Neighbours (one line per vertex, same order):
v99: v39, v24
v39: v99, v52, v24, v29
v79: v46, v52, v29, v64
v22: v24, v58, v64
v46: v79, v52, v29, v64
v52: v39, v79, v46
v24: v99, v39, v22, v58, v29
v58: v22, v24
v29: v39, v79, v46, v24
v64: v79, v22, v46

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v99, v39, v79, v22, v46, v52, v24, v58, v29, v64.
```

Ground truth: chromatic_number = 3

Item hypotheses: column `D(DSATUR\|FF)` of the outputs table, plus the eval and trace rows above. Single-edge additions to the base. Cell = which members' outputs change (computed). An edge between differently coloured FF vertices never changes FF (lemma), which makes D(DSATUR|FF) edits easy to find.

### `E2-COL-A` · `PLACEBO`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "seed": 23, "edit": "add edge v39-v64", "listing": "identical across the set", "labels": "identical across the set"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v99, v39, v79, v22, v46, v52, v24, v58, v29, v64
Neighbours (one line per vertex, same order):
v99: v39, v24
v39: v99, v52, v24, v64
v79: v46, v52, v29, v64
v22: v24, v58, v64
v46: v79, v52, v29, v64
v52: v39, v79, v46
v24: v99, v39, v22, v58, v29
v58: v22, v24
v29: v79, v46, v24
v64: v39, v79, v22, v46

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v99, v39, v79, v22, v46, v52, v24, v58, v29, v64.
```

Ground truth: chromatic_number = 3

Item hypotheses: column `PLACEBO` of the outputs table, plus the eval and trace rows above. Single-edge additions to the base. Cell = which members' outputs change (computed). An edge between differently coloured FF vertices never changes FF (lemma), which makes D(DSATUR|FF) edits easy to find.

### `E2-COL-A` · `G-ONLY`

*Domain:* colouring · *framing:* textbook · *params:* `{"n": 10, "seed": 23, "edit": "add edge v58-v64", "listing": "identical across the set", "labels": "identical across the set"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v99, v39, v79, v22, v46, v52, v24, v58, v29, v64
Neighbours (one line per vertex, same order):
v99: v39, v24
v39: v99, v52, v24
v79: v46, v52, v29, v64
v22: v24, v58, v64
v46: v79, v52, v29, v64
v52: v39, v79, v46
v24: v99, v39, v22, v58, v29
v58: v22, v24, v64
v29: v79, v46, v24
v64: v79, v22, v46, v58

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v99, v39, v79, v22, v46, v52, v24, v58, v29, v64.
```

Ground truth: chromatic_number = 4

Item hypotheses: column `G-ONLY` of the outputs table, plus the eval and trace rows above. Single-edge additions to the base. Cell = which members' outputs change (computed). An edge between differently coloured FF vertices never changes FF (lemma), which makes D(DSATUR|FF) edits easy to find.

<a id="e2-knap-a"></a>
## E2 · Rule discrimination by single-number edits (knapsack)  (`E2-KNAP-A`)

**Reasoning question.** How is weight split among packing rules: value-per-weight (RATIO), value-minus-weight (DIFF, a no-division proxy), value, weight, listing order, and the optimum?

**Controlled.** Item names, number of items, capacity; every number two-digit (token count unchanged).  
**Varied.** One value or weight changed by ≤ 6.

**Outputs by cell** (each theory's predicted answer on each item)

| Theory | `BASE` | `D(RATIO\|DIFF)` | `D(DIFF\|RATIO)` | `PLACEBO` | `G-ONLY` |
|---|---|---|---|---|---|
| RATIO-SKIP | A,C,E,F,J | C,E,F,I,J | A,C,E,F,J | A,C,E,F,J | A,C,E,F,J |
| RATIO-PREFIX | A,C,E,F,J | C,E,F,I,J | A,C,E,F,J | A,C,E,F,J | A,C,E,F,J |
| DIFF | A,D,E,F,I,J | A,D,E,F,I,J | A,E,F,H,I,J | A,D,E,F,I,J | A,D,E,F,I,J |
| VALUE | C,F,H,J | C,F,H,J | A,C,F,H,J | C,F,H,J | C,F,H,J |
| LARGEST-FIT | C,D,G | C,D,G | C,D,G | C,D,G | C,D,G |
| INPUT-FIT | A,B,C,D,F | A,B,C,D,F | A,B,C,D,F | A,B,C,D,F | A,B,C,D,F |
| RATIO+BEST-SINGLE | A,C,E,F,J | C,E,F,I,J | A,C,E,F,J | A,C,E,F,J | A,C,E,F,J |
| DP-EXACT | C,E,F,I,J | C,E,F,I,J | C,E,F,I,J | C,E,F,I,J | A,C,F,I,J |
| NOISY-EXACT | optimum with occasional swaps | optimum with occasional swaps | optimum with occasional swaps | optimum with occasional swaps | optimum with occasional swaps |
| PERCEPTION-NOISE | optimum for a misread number | optimum for a misread number | optimum for a misread number | optimum for a misread number | optimum for a misread number |
| RANDOM (H) | random feasible subset | random feasible subset | random feasible subset | random feasible subset | random feasible subset |

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| RATIO-SKIP | Weight: π_RATIO-SKIP (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching RATIO-SKIP above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with RATIO+BEST-SINGLE, RATIO-PREFIX (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following RATIO-SKIP favour it over the nearest non-tied competitor PERCEPTION-NOISE by log10 LR = 12.5 (separated). Full set (400 items): detects π_RATIO-SKIP (jointly with the tied theories) >= 0.01 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] flip(D(RATIO\|DIFF)) - flip(PLACEBO) = 1 - eps above placebo; DDI(RATIO,DIFF) positive | computes value per kg, sorts, keeps going after a misfit (readout: faithfulness-weighted share T_h) |
| RATIO-PREFIX | Weight: π_RATIO-PREFIX (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ["answers = RATIO-SKIP's set on every item"]. π may vary with item features and model (family I). | [cell: -] as RATIO-SKIP here (no skip occurs); separated in PREFIX/SKIP pairs | value per kg; stops at the first misfit (readout: faithfulness-weighted share T_h) |
| DIFF | Weight: π_DIFF (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DIFF above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following DIFF favour it over the nearest competitor PERCEPTION-NOISE by log10 LR = 13.0 (separated). Full set (400 items): detects π_DIFF >= 0.01 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] flip(D(DIFF\|RATIO)) - flip(PLACEBO) = 1 - eps above placebo; DDI negative | value minus weight; no division (readout: faithfulness-weighted share T_h) |
| VALUE | Weight: π_VALUE (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching VALUE above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following VALUE favour it over the nearest competitor RANDOM (H) by log10 LR = 14.6 (separated). Full set (400 items): detects π_VALUE >= 0.01 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] flips where VALUE changes (covariate; D(DIFF\|RATIO) also moves VALUE) | most valuable first (readout: faithfulness-weighted share T_h) |
| LARGEST-FIT | Weight: π_LARGEST-FIT (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching LARGEST-FIT above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following LARGEST-FIT favour it over the nearest competitor RANDOM (H) by log10 LR = 14.6 (separated). Full set (400 items): detects π_LARGEST-FIT >= 0.01 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] answer = C,D,G throughout | heaviest first (readout: faithfulness-weighted share T_h) |
| INPUT-FIT | Weight: π_INPUT-FIT (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching INPUT-FIT above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following INPUT-FIT favour it over the nearest competitor RANDOM (H) by log10 LR = 14.6 (separated). Full set (400 items): detects π_INPUT-FIT >= 0.01 (80% power) and bounds it <= 0.01 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] answer = A,B,C,D,F throughout | items in listed order (readout: faithfulness-weighted share T_h) |
| RATIO+BEST-SINGLE | Weight: π_RATIO+BEST-SINGLE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ["answers = RATIO-SKIP's set on every item"]. π may vary with item features and model (family I). | [cell: -] as RATIO-PREFIX here | compares greedy total with best single item (readout: faithfulness-weighted share T_h) |
| DP-EXACT | Weight: π_DP-EXACT (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DP-EXACT above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with EXACT, PERCEPTION-NOISE (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following DP-EXACT favour it over the nearest non-tied competitor NOISY-EXACT by log10 LR = 1.0 (weakly separated). Full set (400 items): detects π_DP-EXACT (jointly with the tied theories) >= 0.23 (80% power) and bounds it <= 0.14 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | [cell: -] flip(G-ONLY) - flip(PLACEBO) = 1 - eps above placebo; no D-cell difference | capacity table or subset comparison; revises the chosen set (readout: faithfulness-weighted share T_h) |
| NOISY-EXACT | Weight: π_NOISY-EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | [cell: -] flip rates equal in all cells | arithmetic slips (readout: faithfulness-weighted share T_h) |
| PERCEPTION-NOISE | Weight: π_PERCEPTION-NOISE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ["answers = DP-EXACT's set on every item"]. π may vary with item features and model (family I). | [cell: -] errors involve the misquoted number | misquotes a value or weight (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | [cell: -] flip ~ 1 everywhere | none (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| answers = RATIO-SKIP's set on every item | RATIO+BEST-SINGLE, RATIO-PREFIX, RATIO-SKIP | PERCEPTION-NOISE (-12), NOISY-EXACT (-13), DP-EXACT (-14), EXACT (-14), RANDOM (H) (-15), DIFF (-18), INPUT-FIT (-18), LARGEST-FIT (-18), VALUE (-18) | — |
| answers = DIFF's set on every item | DIFF | PERCEPTION-NOISE (-13), RANDOM (H) (-15), NOISY-EXACT (-16), DP-EXACT (-18), EXACT (-18), INPUT-FIT (-18), LARGEST-FIT (-18), RATIO+BEST-SINGLE (-18), RATIO-PREFIX (-18), RATIO-SKIP (-18), VALUE (-18) | — |
| answers = VALUE's set on every item | VALUE | RANDOM (H) (-15), PERCEPTION-NOISE (-16), NOISY-EXACT (-16), DIFF (-18), DP-EXACT (-18), EXACT (-18), INPUT-FIT (-18), LARGEST-FIT (-18), RATIO+BEST-SINGLE (-18), RATIO-PREFIX (-18), RATIO-SKIP (-18) | — |
| answers = LARGEST-FIT's set on every item | LARGEST-FIT | RANDOM (H) (-15), NOISY-EXACT (-16), DIFF (-18), DP-EXACT (-18), EXACT (-18), INPUT-FIT (-18), PERCEPTION-NOISE (-18), RATIO+BEST-SINGLE (-18), RATIO-PREFIX (-18), RATIO-SKIP (-18), VALUE (-18) | — |
| answers = INPUT-FIT's set on every item | INPUT-FIT | RANDOM (H) (-15), NOISY-EXACT (-16), DIFF (-18), DP-EXACT (-18), EXACT (-18), LARGEST-FIT (-18), PERCEPTION-NOISE (-18), RATIO+BEST-SINGLE (-18), RATIO-PREFIX (-18), RATIO-SKIP (-18), VALUE (-18) | — |
| answers = DP-EXACT's set on every item | DP-EXACT, EXACT, PERCEPTION-NOISE (-0.5) | RATIO+BEST-SINGLE (-14), RATIO-PREFIX (-14), RATIO-SKIP (-14), RANDOM (H) (-15), DIFF (-18), INPUT-FIT (-18), LARGEST-FIT (-18), VALUE (-18) | NOISY-EXACT (-1.0) |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | DIFF | DP-EXACT | EXACT | INPUT-FIT | LARGEST-FIT | NOISY-EXACT | PERCEPTION-NOISE | RANDOM (H) | RATIO+BEST-SINGLE | RATIO-PREFIX | RATIO-SKIP | VALUE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| answers = RATIO-SKIP's set on every item | -18.1 | -14.4 | -14.4 | -18.1 | -18.1 | -13.1 | -12.5 | -14.6 | 0.0 | 0.0 | 0.0 | -18.1 |
| answers = DIFF's set on every item | 0.0 | -18.1 | -18.1 | -18.1 | -18.1 | -16.1 | -13.0 | -14.6 | -18.1 | -18.1 | -18.1 | -18.1 |
| answers = VALUE's set on every item | -18.1 | -18.1 | -18.1 | -18.1 | -18.1 | -16.1 | -15.8 | -14.6 | -18.1 | -18.1 | -18.1 | 0.0 |
| answers = LARGEST-FIT's set on every item | -18.1 | -18.1 | -18.1 | -18.1 | 0.0 | -16.1 | -18.1 | -14.6 | -18.1 | -18.1 | -18.1 | -18.1 |
| answers = INPUT-FIT's set on every item | -18.1 | -18.1 | -18.1 | 0.0 | -18.1 | -16.1 | -18.1 | -14.6 | -18.1 | -18.1 | -18.1 | -18.1 |
| answers = DP-EXACT's set on every item | -18.1 | 0.0 | 0.0 | -18.1 | -18.1 | -1.0 | -0.5 | -14.6 | -14.4 | -14.4 | -14.4 | -18.1 |

</details>

**Not separated by this set.** RATIO-SKIP, RATIO-PREFIX and RATIO+BEST-SINGLE coincide on this set (no item is skipped before a later one fits) → separated by the PREFIX/SKIP pairs of E2-KNAP.

### `E2-KNAP-A` · `BASE`

*Domain:* knapsack · *framing:* realistic: packing · *params:* `{"n": 10, "capacity": 224, "seed": 7, "edit": "none"}`

Prompt:

```text
You can carry at most 224 kg. Choose items to maximise total value without exceeding the limit.
Items (value, weight in kg):
A: value 24, weight 22
B: value 19, weight 48
C: value 77, weight 84
D: value 34, weight 59
E: value 43, weight 38
F: value 86, weight 10
G: value 11, weight 78
H: value 48, weight 68
I: value 45, weight 50
J: value 92, weight 41

After the line ANSWER:, write the letters of the chosen items in alphabetical order, separated by commas.
```

Ground truth: optimal_value = 343; optimal_set = ['C', 'E', 'F', 'I', 'J']

Item hypotheses: column `BASE` of the outputs table, plus the eval and trace rows above. One number changed by at most 6; all numbers stay two-digit (token count unchanged).

### `E2-KNAP-A` · `D(RATIO|DIFF)`

*Domain:* knapsack · *framing:* realistic: packing · *params:* `{"n": 10, "capacity": 224, "seed": 7, "edit": "A value 24->18"}`

Prompt:

```text
You can carry at most 224 kg. Choose items to maximise total value without exceeding the limit.
Items (value, weight in kg):
A: value 18, weight 22
B: value 19, weight 48
C: value 77, weight 84
D: value 34, weight 59
E: value 43, weight 38
F: value 86, weight 10
G: value 11, weight 78
H: value 48, weight 68
I: value 45, weight 50
J: value 92, weight 41

After the line ANSWER:, write the letters of the chosen items in alphabetical order, separated by commas.
```

Ground truth: optimal_value = 343; optimal_set = ['C', 'E', 'F', 'I', 'J']

Item hypotheses: column `D(RATIO\|DIFF)` of the outputs table, plus the eval and trace rows above. One number changed by at most 6; all numbers stay two-digit (token count unchanged).

### `E2-KNAP-A` · `D(DIFF|RATIO)`

*Domain:* knapsack · *framing:* realistic: packing · *params:* `{"n": 10, "capacity": 224, "seed": 7, "edit": "A weight 22->16"}`

Prompt:

```text
You can carry at most 224 kg. Choose items to maximise total value without exceeding the limit.
Items (value, weight in kg):
A: value 24, weight 16
B: value 19, weight 48
C: value 77, weight 84
D: value 34, weight 59
E: value 43, weight 38
F: value 86, weight 10
G: value 11, weight 78
H: value 48, weight 68
I: value 45, weight 50
J: value 92, weight 41

After the line ANSWER:, write the letters of the chosen items in alphabetical order, separated by commas.
```

Ground truth: optimal_value = 343; optimal_set = ['C', 'E', 'F', 'I', 'J']

Item hypotheses: column `D(DIFF\|RATIO)` of the outputs table, plus the eval and trace rows above. One number changed by at most 6; all numbers stay two-digit (token count unchanged).

### `E2-KNAP-A` · `PLACEBO`

*Domain:* knapsack · *framing:* realistic: packing · *params:* `{"n": 10, "capacity": 224, "seed": 7, "edit": "A value 24->20"}`

Prompt:

```text
You can carry at most 224 kg. Choose items to maximise total value without exceeding the limit.
Items (value, weight in kg):
A: value 20, weight 22
B: value 19, weight 48
C: value 77, weight 84
D: value 34, weight 59
E: value 43, weight 38
F: value 86, weight 10
G: value 11, weight 78
H: value 48, weight 68
I: value 45, weight 50
J: value 92, weight 41

After the line ANSWER:, write the letters of the chosen items in alphabetical order, separated by commas.
```

Ground truth: optimal_value = 343; optimal_set = ['C', 'E', 'F', 'I', 'J']

Item hypotheses: column `PLACEBO` of the outputs table, plus the eval and trace rows above. One number changed by at most 6; all numbers stay two-digit (token count unchanged).

### `E2-KNAP-A` · `G-ONLY`

*Domain:* knapsack · *framing:* realistic: packing · *params:* `{"n": 10, "capacity": 224, "seed": 7, "edit": "E weight 38->40"}`

Prompt:

```text
You can carry at most 224 kg. Choose items to maximise total value without exceeding the limit.
Items (value, weight in kg):
A: value 24, weight 22
B: value 19, weight 48
C: value 77, weight 84
D: value 34, weight 59
E: value 43, weight 40
F: value 86, weight 10
G: value 11, weight 78
H: value 48, weight 68
I: value 45, weight 50
J: value 92, weight 41

After the line ANSWER:, write the letters of the chosen items in alphabetical order, separated by commas.
```

Ground truth: optimal_value = 324; optimal_set = ['A', 'C', 'F', 'I', 'J']

Item hypotheses: column `G-ONLY` of the outputs table, plus the eval and trace rows above. One number changed by at most 6; all numbers stay two-digit (token count unchanged).

<a id="e3-col-a"></a>
## E3 · Depth-stress gadget: order-only minimal triple (graph colouring)  (`E3-COL-A`)

**Reasoning question.** How much of the model's dependence on listing order propagates through a dependency chain of depth d (π_seq: sequential first-fit), and how much is a shallow cue (π_proxy) or absent (π_order-free)? The three versions are the *same labelled graph*; only two adjacent vertices swap places in the listing. Under FF-LIST the swap in CRITICAL flips the target's colour class through a depth-2 NOR chain; the swap in PLACEBO cannot (outside the target's dependency cone).

**Controlled.** Labelled graph (identical edge set and labels), n = 34, m = 48, positions of the swapped pairs (adjacent lines), reference vertex (first-listed, never swapped).  
**Varied.** Which pair is swapped (none / in-cone / out-of-cone); answer format (uninstructed in listing order, uninstructed in reversed order, instructed single query). Full study: depth d ∈ {1,2,3,4,6,8} at n = 68.

**Outputs by cell** (each theory's predicted answer on each item)

| Theory | `d=2/BASE/U-LIST` | `d=2/BASE/U-REV` | `d=2/BASE/I` | `d=2/CRITICAL/U-LIST` | `d=2/CRITICAL/I` | `d=2/PLACEBO/U-LIST` | `d=2/PLACEBO/I` |
|---|---|---|---|---|---|---|---|
| FF-LIST (C1 seq) | same | same | — | diff | — | same | — |
| FF-REV / AR (reversed answer order) | diff | diff | — | diff | — | diff | — |
| LOCAL-3-LIST (const-depth proxy) | same | same | 1 | same | 1 | same | 1 |
| DSATUR (C2) | diff | diff | — | diff | — | diff | — |
| LF (C1 static) | diff | diff | — | diff | — | diff | — |
| RO-FF (C3) | P(bit)=0.25, same in all three versions | P(bit)=0.25, same in all three versions | — | P(bit)=0.25, same in all three versions | — | P(bit)=0.25, same in all three versions | — |
| DPLL-LIST (D) | same | same | — | diff | — | same | — |
| NOISY-FF-eps | FF bit with slips | FF bit with slips | FF answer with slips | FF bit with slips | FF answer with slips | FF bit with slips | FF answer with slips |
| PERCEPTION-NOISE | colouring of a misread graph | colouring of a misread graph | — | colouring of a misread graph | — | colouring of a misread graph | — |
| RANDOM (H) | random bit | random bit | 1, 2 or 3 at random | random bit | 1, 2 or 3 at random | random bit | 1, 2 or 3 at random |
| FF-LIST executed (C1 seq) | — | — | 1 | — | 2 | — | 1 |
| ANSWER-1 (A1 default) | — | — | 1 | — | 1 | — | 1 |
| Goal-directed cone evaluation (D-like) | — | — | 1 | — | 2 | — | 1 |

Same prediction in every cell of this set: **EXACT (order-free)**: a proper 3-colouring unrelated to the listing.

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| FF-LIST (C1 seq) | Weight: π_FF-LIST (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching FF-LIST above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with DPLL-LIST (D) (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following FF-LIST favour it over the nearest non-tied competitor RANDOM (H) by log10 LR = 0.8 (weakly separated). Full set (1080 items): detects π_FF-LIST (jointly with the tied theories) >= 0.23 (80% power) and bounds it <= 0.14 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | A2 (FF-consistent on both BASE and CRITICAL) = (1 - eps)^2 at this depth under BE; placebo consistency = 1 - eps | commits all vertices in listing order; target last (readout: faithfulness-weighted share T_h) |
| FF-REV / AR (reversed answer order) | Weight: π_FF-REV / AR (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching FF-REV / AR above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with DSATUR (C2), LF (C1 static), EXACT (order-free), PERCEPTION-NOISE, RO-FF (C3), NOISY-EXACT (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following FF-REV / AR favour it over the nearest non-tied competitor RANDOM (H) by log10 LR = 0.8 (weakly separated). Full set (1080 items): detects π_FF-REV / AR (jointly with the tied theories) >= 0.23 (80% power) and bounds it <= 0.14 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | in U-REV: bit constant across versions (A2 = 0 vs FF-LIST) | commits in the reversed (answer) order (readout: faithfulness-weighted share T_h) |
| LOCAL-3-LIST (const-depth proxy) | Weight: π_LOCAL-3-LIST (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching LOCAL-3-LIST above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following LOCAL-3-LIST favour it over the nearest competitor RANDOM (H) by log10 LR = 0.8 (weakly separated). Full set (1080 items): detects π_LOCAL-3-LIST >= 0.23 (80% power) and bounds it <= 0.14 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | bit constant here (A2 = 0); flips only at depths within its horizon | local reasoning near the target (readout: faithfulness-weighted share T_h) |
| DSATUR (C2) | Weight: π_DSATUR (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DSATUR above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with FF-REV / AR, LF (C1 static), EXACT (order-free), PERCEPTION-NOISE, RO-FF (C3), NOISY-EXACT (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following DSATUR favour it over the nearest non-tied competitor RANDOM (H) by log10 LR = 0.8 (weakly separated). Full set (1080 items): detects π_DSATUR (jointly with the tied theories) >= 0.23 (80% power) and bounds it <= 0.14 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | bit constant across versions (graph identical) | most constrained first (readout: faithfulness-weighted share T_h) |
| LF (C1 static) | Weight: π_LF (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching LF above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with DSATUR (C2), FF-REV / AR, EXACT (order-free), PERCEPTION-NOISE, RO-FF (C3), NOISY-EXACT (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following LF favour it over the nearest non-tied competitor RANDOM (H) by log10 LR = 0.8 (weakly separated). Full set (1080 items): detects π_LF (jointly with the tied theories) >= 0.23 (80% power) and bounds it <= 0.14 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | bit constant across versions | degree order (readout: faithfulness-weighted share T_h) |
| RO-FF (C3) | Weight: π_RO-FF (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ["bits = FF-REV / AR's on BASE/CRITICAL/PLACEBO", "bits = DSATUR (C2)'s on BASE/CRITICAL/PLACEBO", "bits = LF (C1 static)'s on BASE/CRITICAL/PLACEBO", 'bit constant across the three versions', 'bit flips on CRITICAL and on PLACEBO']. π may vary with item features and model (family I). | flip rate equal in CRITICAL and PLACEBO (sampling only) | arbitrary order (readout: faithfulness-weighted share T_h) |
| DPLL-LIST (D) | Weight: π_DPLL-LIST (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DPLL-LIST above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with FF-LIST (C1 seq) (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following DPLL-LIST favour it over the nearest non-tied competitor RANDOM (H) by log10 LR = 0.8 (weakly separated). Full set (1080 items): detects π_DPLL-LIST (jointly with the tied theories) >= 0.23 (80% power) and bounds it <= 0.14 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | identical to FF-LIST (FF never dead-ends on gadgets): not separable here; see E5-COL | listing order, no backtracking needed (readout: faithfulness-weighted share T_h) |
| EXACT (order-free) | Weight: π_EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ["bits = FF-REV / AR's on BASE/CRITICAL/PLACEBO", "bits = DSATUR (C2)'s on BASE/CRITICAL/PLACEBO", "bits = LF (C1 static)'s on BASE/CRITICAL/PLACEBO", 'bit constant across the three versions', 'bit flips on CRITICAL and on PLACEBO']. π may vary with item features and model (family I). | bit constant across versions | structural reasoning; order-free (readout: faithfulness-weighted share T_h) |
| NOISY-FF-eps | Weight: π_NOISY-FF-eps (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ["[instructed] answers = FF-LIST executed (C1 seq)'s on BASE/CRITICAL/PLACEBO"]. π may vary with item features and model (family I). | A2 decays smoothly with depth, same in all conditions | full pass, sporadic slips (readout: faithfulness-weighted share T_h) |
| PERCEPTION-NOISE | Weight: π_PERCEPTION-NOISE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ["bits = FF-REV / AR's on BASE/CRITICAL/PLACEBO", "bits = DSATUR (C2)'s on BASE/CRITICAL/PLACEBO", "bits = LF (C1 static)'s on BASE/CRITICAL/PLACEBO", 'bit constant across the three versions', 'bit flips on CRITICAL and on PLACEBO']. π may vary with item features and model (family I). | flips equal in CRITICAL and PLACEBO | misquoted edges (K11) (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['bit flips on CRITICAL and on PLACEBO']. π may vary with item features and model (family I). | A2 ~ 0.25; flip rate ~ 0.5 in CRITICAL and PLACEBO | none (readout: faithfulness-weighted share T_h) |
| FF-LIST executed (C1 seq) | Weight: π_FF-LIST executed (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching FF-LIST executed above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with NOISY-FF-eps (0.3) (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following FF-LIST executed favour it over the nearest non-tied competitor ANSWER-1 (A1 default) by log10 LR = 1.1 (weakly separated). Full set (1080 items): detects π_FF-LIST executed (jointly with the tied theories) >= 0.17 (80% power) and bounds it <= 0.10 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | A2 (FF-consistent on both BASE and CRITICAL) = (1 - eps)^2 at this depth under BE; placebo consistency = 1 - eps; under ND, A2 falls to its floor beyond the model's depth d* | goes through all vertices in order; no shortcuts (readout: faithfulness-weighted share T_h) |
| ANSWER-1 (A1 default) | Weight: π_ANSWER-1 (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching ANSWER-1 above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Tied on this set with LOCAL-3-LIST (const proxy) (log10 LR > -0.5): this set estimates their weights only jointly; the set named under 'Not separated by this set' separates them. Dev set: answers following ANSWER-1 favour it over the nearest non-tied competitor NOISY-FF-eps (0.3) by log10 LR = 0.9 (weakly separated). Full set (1080 items): detects π_ANSWER-1 (jointly with the tied theories) >= 0.20 (80% power) and bounds it <= 0.11 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | A2 = 0; answer constant | no execution (readout: faithfulness-weighted share T_h) |
| Goal-directed cone evaluation (D-like) | Weight: no likelihood computed for this theory in this set (see the coverage matrix for the set that bounds it). | as FF-LIST in answers | evaluates only the target's ancestors, backwards; tokens grow with depth (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| bits = FF-LIST (C1 seq)'s on BASE/CRITICAL/PLACEBO | DPLL-LIST (D), FF-LIST (C1 seq) | — | RANDOM (H) (-0.8), NOISY-EXACT (-0.9), LOCAL-3-LIST (const proxy) (-0.9), EXACT (order-free) (-1.1), PERCEPTION-NOISE (-1.1), RO-FF (C3) (-1.1), DSATUR (C2) (-1.9), FF-REV / AR (-1.9), LF (C1 static) (-1.9) |
| bits = FF-REV / AR's on BASE/CRITICAL/PLACEBO | DSATUR (C2), FF-REV / AR, LF (C1 static), EXACT (order-free) (-0.3), PERCEPTION-NOISE (-0.3), RO-FF (C3) (-0.3), NOISY-EXACT (-0.5) | LOCAL-3-LIST (const proxy) (-3) | RANDOM (H) (-0.8), DPLL-LIST (D) (-1.9), FF-LIST (C1 seq) (-1.9) |
| bits = LOCAL-3-LIST (const proxy)'s on BASE/CRITICAL/PLACEBO | LOCAL-3-LIST (const proxy) | DSATUR (C2) (-3), FF-REV / AR (-3), LF (C1 static) (-3) | RANDOM (H) (-0.8), DPLL-LIST (D) (-0.9), FF-LIST (C1 seq) (-0.9), NOISY-EXACT (-1.1), EXACT (order-free) (-1.4), PERCEPTION-NOISE (-1.4), RO-FF (C3) (-1.4) |
| bits = DSATUR (C2)'s on BASE/CRITICAL/PLACEBO | DSATUR (C2), FF-REV / AR, LF (C1 static), EXACT (order-free) (-0.3), PERCEPTION-NOISE (-0.3), RO-FF (C3) (-0.3), NOISY-EXACT (-0.5) | LOCAL-3-LIST (const proxy) (-3) | RANDOM (H) (-0.8), DPLL-LIST (D) (-1.9), FF-LIST (C1 seq) (-1.9) |
| bits = LF (C1 static)'s on BASE/CRITICAL/PLACEBO | DSATUR (C2), FF-REV / AR, LF (C1 static), EXACT (order-free) (-0.3), PERCEPTION-NOISE (-0.3), RO-FF (C3) (-0.3), NOISY-EXACT (-0.5) | LOCAL-3-LIST (const proxy) (-3) | RANDOM (H) (-0.8), DPLL-LIST (D) (-1.9), FF-LIST (C1 seq) (-1.9) |
| bits = DPLL-LIST (D)'s on BASE/CRITICAL/PLACEBO | DPLL-LIST (D), FF-LIST (C1 seq) | — | RANDOM (H) (-0.8), NOISY-EXACT (-0.9), LOCAL-3-LIST (const proxy) (-0.9), EXACT (order-free) (-1.1), PERCEPTION-NOISE (-1.1), RO-FF (C3) (-1.1), DSATUR (C2) (-1.9), FF-REV / AR (-1.9), LF (C1 static) (-1.9) |
| bit constant across the three versions | DSATUR (C2), FF-REV / AR, LF (C1 static), EXACT (order-free) (-0.3), PERCEPTION-NOISE (-0.3), RO-FF (C3) (-0.3), NOISY-EXACT (-0.5) | LOCAL-3-LIST (const proxy) (-3) | RANDOM (H) (-0.8), DPLL-LIST (D) (-1.9), FF-LIST (C1 seq) (-1.9) |
| bit flips on CRITICAL and on PLACEBO | EXACT (order-free), PERCEPTION-NOISE, RO-FF (C3), NOISY-EXACT, RANDOM (H) (-0.1), DSATUR (C2) (-0.3), FF-REV / AR (-0.3), LF (C1 static) (-0.3), DPLL-LIST (D) (-0.3), FF-LIST (C1 seq) (-0.3) | — | LOCAL-3-LIST (const proxy) (-1.2) |
| [instructed] answers = FF-LIST executed (C1 seq)'s on BASE/CRITICAL/PLACEBO | FF-LIST executed (C1 seq), NOISY-FF-eps (0.3) (-0.4) | — | ANSWER-1 (A1 default) (-1.1), LOCAL-3-LIST (const proxy) (-1.1), RANDOM (H) (-1.2) |
| [instructed] answers = LOCAL-3-LIST (const proxy)'s on BASE/CRITICAL/PLACEBO | ANSWER-1 (A1 default), LOCAL-3-LIST (const proxy) | — | NOISY-FF-eps (0.3) (-0.9), FF-LIST executed (C1 seq) (-1.1), RANDOM (H) (-1.2) |
| [instructed] answers = ANSWER-1 (A1 default)'s on BASE/CRITICAL/PLACEBO | ANSWER-1 (A1 default), LOCAL-3-LIST (const proxy) | — | NOISY-FF-eps (0.3) (-0.9), FF-LIST executed (C1 seq) (-1.1), RANDOM (H) (-1.2) |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | ANSWER-1 (A1 default) | DPLL-LIST (D) | DSATUR (C2) | EXACT (order-free) | FF-LIST (C1 seq) | FF-LIST executed (C1 seq) | FF-REV / AR | LF (C1 static) | LOCAL-3-LIST (const proxy) | NOISY-EXACT | NOISY-FF-eps (0.3) | PERCEPTION-NOISE | RANDOM (H) | RO-FF (C3) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bits = FF-LIST (C1 seq)'s on BASE/CRITICAL/PLACEBO | nan | 0.0 | -1.9 | -1.1 | 0.0 | nan | -1.9 | -1.9 | -0.9 | -0.9 | nan | -1.1 | -0.8 | -1.1 |
| bits = FF-REV / AR's on BASE/CRITICAL/PLACEBO | nan | -1.9 | 0.0 | -0.3 | -1.9 | nan | 0.0 | 0.0 | -2.9 | -0.5 | nan | -0.3 | -0.8 | -0.3 |
| bits = LOCAL-3-LIST (const proxy)'s on BASE/CRITICAL/PLACEBO | nan | -0.9 | -2.9 | -1.4 | -0.9 | nan | -2.9 | -2.9 | 0.0 | -1.1 | nan | -1.4 | -0.8 | -1.4 |
| bits = DSATUR (C2)'s on BASE/CRITICAL/PLACEBO | nan | -1.9 | 0.0 | -0.3 | -1.9 | nan | 0.0 | 0.0 | -2.9 | -0.5 | nan | -0.3 | -0.8 | -0.3 |
| bits = LF (C1 static)'s on BASE/CRITICAL/PLACEBO | nan | -1.9 | 0.0 | -0.3 | -1.9 | nan | 0.0 | 0.0 | -2.9 | -0.5 | nan | -0.3 | -0.8 | -0.3 |
| bits = DPLL-LIST (D)'s on BASE/CRITICAL/PLACEBO | nan | 0.0 | -1.9 | -1.1 | 0.0 | nan | -1.9 | -1.9 | -0.9 | -0.9 | nan | -1.1 | -0.8 | -1.1 |
| bit constant across the three versions | nan | -1.9 | 0.0 | -0.3 | -1.9 | nan | 0.0 | 0.0 | -2.9 | -0.5 | nan | -0.3 | -0.8 | -0.3 |
| bit flips on CRITICAL and on PLACEBO | nan | -0.3 | -0.3 | 0.0 | -0.3 | nan | -0.3 | -0.3 | -1.2 | -0.0 | nan | 0.0 | -0.1 | 0.0 |
| [instructed] answers = FF-LIST executed (C1 seq)'s on BASE/CRITICAL/PLACEBO | -1.1 | nan | nan | nan | nan | 0.0 | nan | nan | -1.1 | nan | -0.4 | nan | -1.2 | nan |
| [instructed] answers = LOCAL-3-LIST (const proxy)'s on BASE/CRITICAL/PLACEBO | 0.0 | nan | nan | nan | nan | -1.1 | nan | nan | 0.0 | nan | -0.9 | nan | -1.2 | nan |
| [instructed] answers = ANSWER-1 (A1 default)'s on BASE/CRITICAL/PLACEBO | 0.0 | nan | nan | nan | nan | -1.1 | nan | nan | 0.0 | nan | -0.9 | nan | -1.2 | nan |

</details>

**Not separated by this set.** FF-LIST vs DPLL-LIST vs GREEDY+REPAIR: first-fit never dead-ends on these gadgets, so all three give the same bit → E5-COL. The depth curve (several d) is needed to tell FF-LIST from a const-depth proxy with a long horizon; one depth only rules the proxy in or out at that depth.

### `E3-COL-A` · `d=2/BASE/U-LIST`

*Domain:* colouring (gadget) · *framing:* textbook · *params:* `{"width": 3, "D_max": 3, "target_depth": 2, "n": 34, "m": 48, "swap": null, "target": "v29", "reference_vertex": "v65", "seed": 31}`

<details><summary>Prompt</summary>

```text
Graph with 34 vertices.
Vertices (in this order): v65, v57, v34, v52, v92, v38, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29
Neighbours (one line per vertex, same order):
v65: v57
v57: v65, v83, v60
v34: v52, v83, v93, v50
v52: v34
v92: v38, v37
v38: v92
v71: v15
v15: v71, v37, v22
v43: v53, v60, v93, v22
v53: v43
v47: v96, v50
v96: v47
v83: v57, v34, v49, v89, v29
v60: v57, v43, v32, v29
v93: v34, v43, v49, v32, v79
v50: v34, v47, v21
v37: v92, v15, v89
v22: v15, v43, v79, v21
v49: v83, v93, v80, v97, v13, v98, v16, v88
v32: v60, v93, v80, v97, v13, v54
v79: v93, v22, v54, v85
v89: v83, v37, v98
v21: v50, v22, v85
v80: v49, v32
v97: v49, v32
v13: v49, v32
v98: v49, v89
v54: v32, v79
v85: v79, v21, v35, v28
v16: v49, v88
v88: v49, v16
v35: v85, v28
v28: v85, v35
v29: v83, v60

Colour every vertex with one of the colours 1, 2, ..., 3 so that neighbours get different colours. If this is impossible, say IMPOSSIBLE.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v65, v57, v34, v52, v92, v38, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29.
```

</details>

Ground truth: colourable_with_3 = True; readout = bit = v29 has the same colour as v65 (first-listed vertex); check = any proper 3-colouring is correct; the bit is a fingerprint, not a correctness criterion

Item hypotheses: column `d=2/BASE/U-LIST` of the outputs table, plus the eval and trace rows above. All three versions have the identical labelled graph; only two adjacent vertices swap places in the listing. Ground truth, chromatic number and every order-invariant member are therefore unchanged by construction.

### `E3-COL-A` · `d=2/BASE/U-REV`

*Domain:* colouring (gadget) · *framing:* textbook · *params:* `{"width": 3, "D_max": 3, "target_depth": 2, "n": 34, "m": 48, "swap": null, "target": "v29", "reference_vertex": "v65", "seed": 31}`

<details><summary>Prompt</summary>

```text
Graph with 34 vertices.
Vertices (in this order): v65, v57, v34, v52, v92, v38, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29
Neighbours (one line per vertex, same order):
v65: v57
v57: v65, v83, v60
v34: v52, v83, v93, v50
v52: v34
v92: v38, v37
v38: v92
v71: v15
v15: v71, v37, v22
v43: v53, v60, v93, v22
v53: v43
v47: v96, v50
v96: v47
v83: v57, v34, v49, v89, v29
v60: v57, v43, v32, v29
v93: v34, v43, v49, v32, v79
v50: v34, v47, v21
v37: v92, v15, v89
v22: v15, v43, v79, v21
v49: v83, v93, v80, v97, v13, v98, v16, v88
v32: v60, v93, v80, v97, v13, v54
v79: v93, v22, v54, v85
v89: v83, v37, v98
v21: v50, v22, v85
v80: v49, v32
v97: v49, v32
v13: v49, v32
v98: v49, v89
v54: v32, v79
v85: v79, v21, v35, v28
v16: v49, v88
v88: v49, v16
v35: v85, v28
v28: v85, v35
v29: v83, v60

Colour every vertex with one of the colours 1, 2, ..., 3 so that neighbours get different colours. If this is impossible, say IMPOSSIBLE.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v29, v28, v35, v88, v16, v85, v54, v98, v13, v97, v80, v21, v89, v79, v32, v49, v22, v37, v50, v93, v60, v83, v96, v47, v53, v43, v15, v71, v38, v92, v52, v34, v57, v65.
```

</details>

Ground truth: colourable_with_3 = True; readout = bit = v29 has the same colour as v65 (first-listed vertex); check = any proper 3-colouring is correct; the bit is a fingerprint, not a correctness criterion

Item hypotheses: column `d=2/BASE/U-REV` of the outputs table, plus the eval and trace rows above. All three versions have the identical labelled graph; only two adjacent vertices swap places in the listing. Ground truth, chromatic number and every order-invariant member are therefore unchanged by construction.

### `E3-COL-A` · `d=2/BASE/I`

*Domain:* colouring (gadget) · *framing:* textbook · *params:* `{"width": 3, "D_max": 3, "target_depth": 2, "n": 34, "m": 48, "swap": null, "target": "v29", "reference_vertex": "v65", "seed": 31}`

<details><summary>Prompt</summary>

```text
Graph with 34 vertices.
Vertices (in this order): v65, v57, v34, v52, v92, v38, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29
Neighbours (one line per vertex, same order):
v65: v57
v57: v65, v83, v60
v34: v52, v83, v93, v50
v52: v34
v92: v38, v37
v38: v92
v71: v15
v15: v71, v37, v22
v43: v53, v60, v93, v22
v53: v43
v47: v96, v50
v96: v47
v83: v57, v34, v49, v89, v29
v60: v57, v43, v32, v29
v93: v34, v43, v49, v32, v79
v50: v34, v47, v21
v37: v92, v15, v89
v22: v15, v43, v79, v21
v49: v83, v93, v80, v97, v13, v98, v16, v88
v32: v60, v93, v80, v97, v13, v54
v79: v93, v22, v54, v85
v89: v83, v37, v98
v21: v50, v22, v85
v80: v49, v32
v97: v49, v32
v13: v49, v32
v98: v49, v89
v54: v32, v79
v85: v79, v21, v35, v28
v16: v49, v88
v88: v49, v16
v35: v85, v28
v28: v85, v35
v29: v83, v60

Go through the vertices one at a time in the listed order. Give each vertex the smallest positive integer not already used by one of its neighbours that come earlier in the list. What colour does v29 get?
After the line ANSWER:, write only the colour number of v29.
```

</details>

Ground truth: answer = 1; check = unique: first-fit colour of the target in listing order

Item hypotheses: column `d=2/BASE/I` of the outputs table, plus the eval and trace rows above. All three versions have the identical labelled graph; only two adjacent vertices swap places in the listing. Ground truth, chromatic number and every order-invariant member are therefore unchanged by construction.

### `E3-COL-A` · `d=2/CRITICAL/U-LIST`

*Domain:* colouring (gadget) · *framing:* textbook · *params:* `{"width": 3, "D_max": 3, "target_depth": 2, "n": 34, "m": 48, "swap": "input/pendant pair of v34 (in target's cone)", "target": "v29", "reference_vertex": "v65", "seed": 31}`

<details><summary>Prompt</summary>

```text
Graph with 34 vertices.
Vertices (in this order): v65, v57, v52, v34, v92, v38, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29
Neighbours (one line per vertex, same order):
v65: v57
v57: v65, v83, v60
v52: v34
v34: v52, v83, v93, v50
v92: v38, v37
v38: v92
v71: v15
v15: v71, v37, v22
v43: v53, v60, v93, v22
v53: v43
v47: v96, v50
v96: v47
v83: v57, v34, v49, v89, v29
v60: v57, v43, v32, v29
v93: v34, v43, v49, v32, v79
v50: v34, v47, v21
v37: v92, v15, v89
v22: v15, v43, v79, v21
v49: v83, v93, v80, v97, v13, v98, v16, v88
v32: v60, v93, v80, v97, v13, v54
v79: v93, v22, v54, v85
v89: v83, v37, v98
v21: v50, v22, v85
v80: v49, v32
v97: v49, v32
v13: v49, v32
v98: v49, v89
v54: v32, v79
v85: v79, v21, v35, v28
v16: v49, v88
v88: v49, v16
v35: v85, v28
v28: v85, v35
v29: v83, v60

Colour every vertex with one of the colours 1, 2, ..., 3 so that neighbours get different colours. If this is impossible, say IMPOSSIBLE.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v65, v57, v52, v34, v92, v38, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29.
```

</details>

Ground truth: colourable_with_3 = True; readout = bit = v29 has the same colour as v65 (first-listed vertex); check = any proper 3-colouring is correct; the bit is a fingerprint, not a correctness criterion

Item hypotheses: column `d=2/CRITICAL/U-LIST` of the outputs table, plus the eval and trace rows above. All three versions have the identical labelled graph; only two adjacent vertices swap places in the listing. Ground truth, chromatic number and every order-invariant member are therefore unchanged by construction.

### `E3-COL-A` · `d=2/CRITICAL/I`

*Domain:* colouring (gadget) · *framing:* textbook · *params:* `{"width": 3, "D_max": 3, "target_depth": 2, "n": 34, "m": 48, "swap": "input/pendant pair of v34 (in target's cone)", "target": "v29", "reference_vertex": "v65", "seed": 31}`

<details><summary>Prompt</summary>

```text
Graph with 34 vertices.
Vertices (in this order): v65, v57, v52, v34, v92, v38, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29
Neighbours (one line per vertex, same order):
v65: v57
v57: v65, v83, v60
v52: v34
v34: v52, v83, v93, v50
v92: v38, v37
v38: v92
v71: v15
v15: v71, v37, v22
v43: v53, v60, v93, v22
v53: v43
v47: v96, v50
v96: v47
v83: v57, v34, v49, v89, v29
v60: v57, v43, v32, v29
v93: v34, v43, v49, v32, v79
v50: v34, v47, v21
v37: v92, v15, v89
v22: v15, v43, v79, v21
v49: v83, v93, v80, v97, v13, v98, v16, v88
v32: v60, v93, v80, v97, v13, v54
v79: v93, v22, v54, v85
v89: v83, v37, v98
v21: v50, v22, v85
v80: v49, v32
v97: v49, v32
v13: v49, v32
v98: v49, v89
v54: v32, v79
v85: v79, v21, v35, v28
v16: v49, v88
v88: v49, v16
v35: v85, v28
v28: v85, v35
v29: v83, v60

Go through the vertices one at a time in the listed order. Give each vertex the smallest positive integer not already used by one of its neighbours that come earlier in the list. What colour does v29 get?
After the line ANSWER:, write only the colour number of v29.
```

</details>

Ground truth: answer = 2; check = unique: first-fit colour of the target in listing order

Item hypotheses: column `d=2/CRITICAL/I` of the outputs table, plus the eval and trace rows above. All three versions have the identical labelled graph; only two adjacent vertices swap places in the listing. Ground truth, chromatic number and every order-invariant member are therefore unchanged by construction.

### `E3-COL-A` · `d=2/PLACEBO/U-LIST`

*Domain:* colouring (gadget) · *framing:* textbook · *params:* `{"width": 3, "D_max": 3, "target_depth": 2, "n": 34, "m": 48, "swap": "input/pendant pair of v92 (outside the cone)", "target": "v29", "reference_vertex": "v65", "seed": 31}`

<details><summary>Prompt</summary>

```text
Graph with 34 vertices.
Vertices (in this order): v65, v57, v34, v52, v38, v92, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29
Neighbours (one line per vertex, same order):
v65: v57
v57: v65, v83, v60
v34: v52, v83, v93, v50
v52: v34
v38: v92
v92: v38, v37
v71: v15
v15: v71, v37, v22
v43: v53, v60, v93, v22
v53: v43
v47: v96, v50
v96: v47
v83: v57, v34, v49, v89, v29
v60: v57, v43, v32, v29
v93: v34, v43, v49, v32, v79
v50: v34, v47, v21
v37: v92, v15, v89
v22: v15, v43, v79, v21
v49: v83, v93, v80, v97, v13, v98, v16, v88
v32: v60, v93, v80, v97, v13, v54
v79: v93, v22, v54, v85
v89: v83, v37, v98
v21: v50, v22, v85
v80: v49, v32
v97: v49, v32
v13: v49, v32
v98: v49, v89
v54: v32, v79
v85: v79, v21, v35, v28
v16: v49, v88
v88: v49, v16
v35: v85, v28
v28: v85, v35
v29: v83, v60

Colour every vertex with one of the colours 1, 2, ..., 3 so that neighbours get different colours. If this is impossible, say IMPOSSIBLE.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v65, v57, v34, v52, v38, v92, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29.
```

</details>

Ground truth: colourable_with_3 = True; readout = bit = v29 has the same colour as v65 (first-listed vertex); check = any proper 3-colouring is correct; the bit is a fingerprint, not a correctness criterion

Item hypotheses: column `d=2/PLACEBO/U-LIST` of the outputs table, plus the eval and trace rows above. All three versions have the identical labelled graph; only two adjacent vertices swap places in the listing. Ground truth, chromatic number and every order-invariant member are therefore unchanged by construction.

### `E3-COL-A` · `d=2/PLACEBO/I`

*Domain:* colouring (gadget) · *framing:* textbook · *params:* `{"width": 3, "D_max": 3, "target_depth": 2, "n": 34, "m": 48, "swap": "input/pendant pair of v92 (outside the cone)", "target": "v29", "reference_vertex": "v65", "seed": 31}`

<details><summary>Prompt</summary>

```text
Graph with 34 vertices.
Vertices (in this order): v65, v57, v34, v52, v38, v92, v71, v15, v43, v53, v47, v96, v83, v60, v93, v50, v37, v22, v49, v32, v79, v89, v21, v80, v97, v13, v98, v54, v85, v16, v88, v35, v28, v29
Neighbours (one line per vertex, same order):
v65: v57
v57: v65, v83, v60
v34: v52, v83, v93, v50
v52: v34
v38: v92
v92: v38, v37
v71: v15
v15: v71, v37, v22
v43: v53, v60, v93, v22
v53: v43
v47: v96, v50
v96: v47
v83: v57, v34, v49, v89, v29
v60: v57, v43, v32, v29
v93: v34, v43, v49, v32, v79
v50: v34, v47, v21
v37: v92, v15, v89
v22: v15, v43, v79, v21
v49: v83, v93, v80, v97, v13, v98, v16, v88
v32: v60, v93, v80, v97, v13, v54
v79: v93, v22, v54, v85
v89: v83, v37, v98
v21: v50, v22, v85
v80: v49, v32
v97: v49, v32
v13: v49, v32
v98: v49, v89
v54: v32, v79
v85: v79, v21, v35, v28
v16: v49, v88
v88: v49, v16
v35: v85, v28
v28: v85, v35
v29: v83, v60

Go through the vertices one at a time in the listed order. Give each vertex the smallest positive integer not already used by one of its neighbours that come earlier in the list. What colour does v29 get?
After the line ANSWER:, write only the colour number of v29.
```

</details>

Ground truth: answer = 1; check = unique: first-fit colour of the target in listing order

Item hypotheses: column `d=2/PLACEBO/I` of the outputs table, plus the eval and trace rows above. All three versions have the identical labelled graph; only two adjacent vertices swap places in the listing. Ground truth, chromatic number and every order-invariant member are therefore unchanged by construction.

<a id="e4-sat-a"></a>
## E4 · Item-level co-failure at matched density (3-SAT)  (`E4-SAT-A`)

**Reasoning question.** At fixed density and fixed search hardness, what share of the model's failures falls on the items where the no-backtracking members fail?

**Controlled.** n = 12, m = 42 (α = 3.5), DPLL node count matched (within 3), labels.  
**Varied.** Whether UC-DET / GREEDY dead-end.

**Outputs by cell** (each theory's predicted answer on each item)

| Theory | `UC-FAILS` | `UC-OK` |
|---|---|---|
| UC-DET (C2) | S1 (falsified: C30) | S2 |
| UC-DET-ABORT (C2) | UNSAT | same as UC-DET |
| GREEDY-MENTION (C1) | S3 (falsified: C17, C30, C41) | S4 |
| GUC-DET / SC-DET (C2) | x21=T x25=F x42=F x44=T x53=T x58=F x64=F x77=T x80=F x82=F x88=T x94=F (falsified ['C19', 'C38']) | x21=F x25=T x42=T x44=T x53=F x58=T x64=T x77=F x80=T x82=F x88=T x94=F |
| POLARITY (C0) | S5 (falsified: C11, C17, C22) | S6 (falsified: C24) |
| RO-GREEDY (C3) | P(satisfying) 0.002 | P(satisfying) 0.364 |
| DENSITY (A2) | SAT (alpha = 3.5 < 4.26) | SAT (alpha = 3.5 < 4.26) |
| EXACT | a satisfying assignment | a satisfying assignment |
| NOISY-EXACT | near-solution | near-solution |
| PERCEPTION-NOISE | solution of a misread formula | solution of a misread formula |
| RANDOM (H) | random assignment | random assignment |

Same prediction in every cell of this set: **DPLL (D)**: a satisfying assignment (both items; equal node counts); **WALK (F)**: satisfying assignment usually (alpha 3.5 is easy for local search).

<details><summary>Legend: partitions / assignments</summary>

- **S1** = `x21=T x25=T x42=F x44=T x53=F x58=F x64=T x77=F x80=T x82=T x88=T x94=T`
- **S2** = `x21=T x25=F x42=T x44=T x53=T x58=F x64=F x77=F x80=F x82=T x88=T x94=T`
- **S3** = `x21=T x25=T x42=F x44=T x53=F x58=F x64=F x77=T x80=T x82=T x88=T x94=T`
- **S4** = `x21=F x25=T x42=T x44=T x53=F x58=T x64=T x77=F x80=F x82=F x88=T x94=F`
- **S5** = `x21=T x25=F x42=T x44=T x53=T x58=T x64=F x77=T x80=T x82=T x88=T x94=T`
- **S6** = `x21=F x25=T x42=T x44=T x53=F x58=T x64=T x77=F x80=F x82=T x88=T x94=T`

</details>

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| UC-DET (C2) | Weight: π_UC-DET (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['fails UC-FAILS (invalid), solves UC-OK']. π may vary with item features and model (family I). | co-failure: P(model fails \| member fails) - P(model fails \| member succeeds) = 1 - eps at matched alpha and DPLL nodes | forced steps; a clause becomes false; continues without undoing (readout: faithfulness-weighted share T_h) |
| UC-DET-ABORT (C2) | Weight: π_UC-DET-ABORT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['says UNSAT on UC-FAILS, solves UC-OK']. π may vary with item features and model (family I). | co-failure: P(model fails \| member fails) - P(model fails \| member succeeds) = 1 - eps at matched alpha and DPLL nodes; false UNSAT on UC-FAILS items | declares UNSAT at the first false clause, no backtracking (readout: faithfulness-weighted share T_h) |
| GREEDY-MENTION (C1) | Weight: π_GREEDY-MENTION (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['fails UC-FAILS (invalid), solves UC-OK']. π may vary with item features and model (family I). | co-failure: P(model fails \| member fails) - P(model fails \| member succeeds) = 1 - eps at matched alpha and DPLL nodes | per-variable counts in mention order (readout: faithfulness-weighted share T_h) |
| GUC-DET / SC-DET (C2) | Weight: π_GUC-DET / SC-DET (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['fails UC-FAILS (invalid), solves UC-OK']. π may vary with item features and model (family I). | co-failure: P(model fails \| member fails) - P(model fails \| member succeeds) = 1 - eps at matched alpha and DPLL nodes; GUC and SC tied on this pair | shortest-clause-first (readout: faithfulness-weighted share T_h) |
| POLARITY (C0) | Weight: π_POLARITY (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['fails both']. π may vary with item features and model (family I). | co-failure: P(model fails \| member fails) - P(model fails \| member succeeds) = 1 - eps at matched alpha and DPLL nodes | tallies (readout: faithfulness-weighted share T_h) |
| RO-GREEDY (C3) | Weight: π_RO-GREEDY (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['fails UC-FAILS (invalid), solves UC-OK', 'fails both']. π may vary with item features and model (family I). | model success ~ RO-GREEDY's success probability | arbitrary order (readout: faithfulness-weighted share T_h) |
| DPLL (D) | Weight: π_DPLL (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['solves both']. π may vary with item features and model (family I). | no co-failure at matched nodes; success tracks node count | backtracking (readout: faithfulness-weighted share T_h) |
| WALK (F) | Weight: π_WALK (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['solves both']. π may vary with item features and model (family I). | success independent of UC failure | flips (readout: faithfulness-weighted share T_h) |
| DENSITY (A2) | Weight: π_DENSITY (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | identical behaviour on both items (same alpha) | cites clause/variable ratio (readout: faithfulness-weighted share T_h) |
| EXACT | Weight: π_EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['solves both']. π may vary with item features and model (family I). | solves both | search (readout: faithfulness-weighted share T_h) |
| NOISY-EXACT | Weight: π_NOISY-EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['solves both']. π may vary with item features and model (family I). | failure equal on both (same length) | slips (readout: faithfulness-weighted share T_h) |
| PERCEPTION-NOISE | Weight: π_PERCEPTION-NOISE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['solves both']. π may vary with item features and model (family I). | failure equal; falsified clauses misquoted | K11 (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['fails both']. π may vary with item features and model (family I). | fails both | none (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| fails UC-FAILS (invalid), solves UC-OK | GREEDY-MENTION (C1), GUC-DET / SC-DET (C2), UC-DET (C2), RO-GREEDY (C3) (-0.4) | RANDOM (H) (-2) | DENSITY (A2) (-0.5), PERCEPTION-NOISE (-0.6), NOISY-EXACT (-0.8), DPLL (D) (-1.1), EXACT (-1.1), POLARITY (C0) (-1.1), UC-DET-ABORT (C2) (-1.1), WALK (F) (-1.1) |
| says UNSAT on UC-FAILS, solves UC-OK | UC-DET-ABORT (C2) | POLARITY (C0) (-2), RANDOM (H) (-302) | NOISY-EXACT (-0.8), DPLL (D) (-1.1), EXACT (-1.1), GREEDY-MENTION (C1) (-1.1), GUC-DET / SC-DET (C2) (-1.1), UC-DET (C2) (-1.1), WALK (F) (-1.1), PERCEPTION-NOISE (-1.2), DENSITY (A2) (-1.4), RO-GREEDY (C3) (-1.5) |
| solves both | DPLL (D), EXACT, WALK (F), NOISY-EXACT (-0.2), PERCEPTION-NOISE (-0.3) | POLARITY (C0) (-2), RANDOM (H) (-6) | DENSITY (A2) (-0.5), GREEDY-MENTION (C1) (-1.1), GUC-DET / SC-DET (C2) (-1.1), UC-DET (C2) (-1.1), UC-DET-ABORT (C2) (-1.1), RO-GREEDY (C3) (-1.5) |
| fails both | RANDOM (H), POLARITY (C0) (-0.1), RO-GREEDY (C3) (-0.3) | DPLL (D) (-2), EXACT (-2), UC-DET-ABORT (C2) (-2), WALK (F) (-2) | DENSITY (A2) (-0.7), PERCEPTION-NOISE (-1.0), GREEDY-MENTION (C1) (-1.2), GUC-DET / SC-DET (C2) (-1.2), UC-DET (C2) (-1.2), NOISY-EXACT (-1.6) |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | DENSITY (A2) | DPLL (D) | EXACT | GREEDY-MENTION (C1) | GUC-DET / SC-DET (C2) | NOISY-EXACT | PERCEPTION-NOISE | POLARITY (C0) | RANDOM (H) | RO-GREEDY (C3) | UC-DET (C2) | UC-DET-ABORT (C2) | WALK (F) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fails UC-FAILS (invalid), solves UC-OK | -0.5 | -1.1 | -1.1 | 0.0 | 0.0 | -0.8 | -0.6 | -1.1 | -2.4 | -0.4 | 0.0 | -1.1 | -1.1 |
| says UNSAT on UC-FAILS, solves UC-OK | -1.4 | -1.1 | -1.1 | -1.1 | -1.1 | -0.8 | -1.2 | -2.2 | -302.4 | -1.5 | -1.1 | 0.0 | -1.1 |
| solves both | -0.5 | 0.0 | 0.0 | -1.1 | -1.1 | -0.2 | -0.3 | -2.2 | -5.7 | -1.5 | -1.1 | -1.1 | 0.0 |
| fails both | -0.7 | -2.4 | -2.4 | -1.2 | -1.2 | -1.6 | -1.0 | -0.1 | 0.0 | -0.3 | -1.2 | -2.4 | -2.4 |

</details>

**Not separated by this set.** GUC vs SC are tied on this pair (same falsified clauses) → E2-SAT contrasts. Two items only illustrate a cell; inference uses ~40 items per (n, α) cell.

### `E4-SAT-A` · `UC-FAILS`

*Domain:* 3-SAT · *framing:* textbook · *params:* `{"n": 12, "m": 42, "alpha": 3.5, "dpll_nodes": 6, "seed": 41}`

<details><summary>Prompt</summary>

```text
A formula over 12 true/false variables. Every clause must contain at least one true literal.
C1: x21 or not x94 or not x25
C2: x88 or x64 or x21
C3: not x42 or x80 or not x44
C4: x44 or x77 or x53
C5: x21 or not x64 or not x25
C6: x80 or x88 or x58
C7: not x53 or not x80 or x58
C8: x77 or not x58 or x53
C9: x64 or x21 or not x80
C10: not x58 or x44 or x42
C11: not x82 or not x80 or not x53
C12: x88 or x64 or not x53
C13: x94 or x80 or x44
C14: x44 or not x80 or x21
C15: not x25 or not x53 or not x21
C16: x42 or x82 or not x64
C17: not x21 or not x94 or not x77
C18: x53 or x82 or x25
C19: x25 or x80 or x42
C20: x88 or not x77 or not x44
C21: x82 or not x25 or x21
C22: not x88 or not x42 or not x21
C23: x58 or x80 or x77
C24: not x21 or x82 or not x58
C25: not x64 or not x53 or x80
C26: not x82 or not x64 or not x77
C27: not x42 or not x25 or x82
C28: not x42 or x80 or x53
C29: not x42 or x53 or x77
C30: not x44 or not x25 or not x21
C31: x77 or x80 or x21
C32: x77 or x88 or not x21
C33: x58 or x25 or not x64
C34: not x53 or x80 or not x58
C35: x82 or x77 or not x88
C36: x80 or not x64 or x42
C37: not x53 or not x64 or x82
C38: not x88 or x94 or x42
C39: not x82 or x94 or not x21
C40: x80 or x64 or x53
C41: not x94 or x64 or x53
C42: x58 or x21 or not x82

Find values for all variables that make every clause true, or say UNSAT if none exist.
After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, in this order: x21, x94, x25, x88, x64, x42, x80, x44, x77, x53, x58, x82.
```

</details>

Ground truth: satisfiable = True; n_solutions = 2

Item hypotheses: column `UC-FAILS` of the outputs table, plus the eval and trace rows above. Two items at the same density and (nearly) the same DPLL node count. They differ in whether the no-backtracking members fail. Co-failure tests whether the model fails on the item the C member fails on.

### `E4-SAT-A` · `UC-OK`

*Domain:* 3-SAT · *framing:* textbook · *params:* `{"n": 12, "m": 42, "alpha": 3.5, "dpll_nodes": 4, "seed": 41}`

<details><summary>Prompt</summary>

```text
A formula over 12 true/false variables. Every clause must contain at least one true literal.
C1: not x21 or x88 or not x44
C2: not x21 or x58 or not x64
C3: x21 or x64 or x58
C4: not x80 or x25 or not x21
C5: x80 or not x64 or not x53
C6: not x88 or x25 or x42
C7: not x58 or not x82 or x64
C8: not x80 or x77 or x42
C9: not x42 or not x77 or x21
C10: not x64 or not x77 or x44
C11: not x53 or not x80 or x88
C12: x82 or x42 or x44
C13: x21 or x25 or not x58
C14: not x42 or x64 or x82
C15: x25 or x44 or not x88
C16: x44 or not x82 or not x80
C17: x88 or not x80 or not x21
C18: not x42 or not x64 or not x21
C19: not x25 or not x44 or not x21
C20: not x77 or x64 or not x82
C21: x53 or x82 or x64
C22: x58 or x44 or x88
C23: x58 or not x25 or not x88
C24: not x44 or not x82 or x21
C25: x82 or not x88 or not x53
C26: x94 or x42 or not x64
C27: x53 or not x21 or not x58
C28: x94 or x53 or not x77
C29: x64 or x21 or not x25
C30: x94 or not x82 or not x88
C31: not x58 or not x94 or x82
C32: not x80 or x82 or x88
C33: x58 or x64 or x94
C34: x88 or x80 or not x53
C35: not x58 or x64 or x80
C36: not x21 or x80 or x88
C37: x21 or x58 or not x44
C38: x21 or not x44 or not x53
C39: x42 or x21 or x58
C40: not x25 or not x21 or not x80
C41: x94 or x64 or x88
C42: not x80 or x42 or not x64

Find values for all variables that make every clause true, or say UNSAT if none exist.
After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, in this order: x21, x88, x44, x58, x64, x80, x25, x53, x42, x82, x77, x94.
```

</details>

Ground truth: satisfiable = True; n_solutions = 13

Item hypotheses: column `UC-OK` of the outputs table, plus the eval and trace rows above. Two items at the same density and (nearly) the same DPLL node count. They differ in whether the no-backtracking members fail. Co-failure tests whether the model fails on the item the C member fails on.

<a id="e5-col-a"></a>
## E5 · Dead-end localisation: vertex order × edge order (3-colouring)  (`E5-COL-A`)

**Reasoning question.** When the model fails a 3-colourable graph, how are its failures split between first-fit dead ends (false IMPOSSIBLE, or a conflict at the stuck vertex that moves with the *vertex* order), a dropped constraint (conflict on late-listed edges that moves with the *edge* order), or unlocalised (local search, noise)?

**Controlled.** Graph (STUCK items), n, m; CONTROL matched on n, m (±1) and order-free search hardness (degree-order backtracking nodes).  
**Varied.** Vertex listing order (A/B), edge listing order (A/B), stuck vs control graph.

**Outputs by cell** (each theory's predicted answer on each item)

| Theory | `STUCK/vertexA/edgeA` | `STUCK/vertexB/edgeA` | `STUCK/vertexA/edgeB` | `CONTROL/vertexA/edgeA` |
|---|---|---|---|---|
| FF-3-LIST-ABORT (C1) | IMPOSSIBLE | IMPOSSIBLE | IMPOSSIBLE | P1 |
| FF-3-LIST-INFEAS (C1) | P2 (conflicts: v32-v86, v86-v12) | P3 (conflicts: v32-v86, v96-v12) | P2 (conflicts: v32-v86, v86-v12) | P1 |
| FF-3-EDGE-MENTION (C1 variant) | P4 | P4 | IMPOSSIBLE | P5 |
| GREEDY+REPAIR-LIST (C->F) | init FF-3-LIST-INFEAS; P(valid) 1.0; mean vertices changed from FF 1; modal P4 | init FF-3-LIST-INFEAS; P(valid) 1.0; mean vertices changed from FF 3; modal P4 | init FF-3-LIST-INFEAS; P(valid) 1.0; mean vertices changed from FF 1; modal P4 | init FF-3-LIST-INFEAS; P(valid) 1.0; mean vertices changed from FF 0; modal P1 |
| DPLL-LIST (D) | P4 | P4 | P4 | P1 |
| DROP-LAST-EDGES (B1) | P6 (conflicts: v88-v12) | P4 | P7 (conflicts: v23-v66) | P8 (conflicts: v34-v11) |
| MIN-CONFLICTS (F) | P(valid) 0.803 | P(valid) 0.803 | P(valid) 0.803 | P(valid) 1.0 |
| EXACT | a proper 3-colouring | a proper 3-colouring | a proper 3-colouring | a proper 3-colouring |
| NOISY-EXACT | proper colouring with slips | proper colouring with slips | proper colouring with slips | proper colouring with slips |
| PERCEPTION-NOISE | colouring of a misread graph | colouring of a misread graph | colouring of a misread graph | colouring of a misread graph |
| RANDOM (H) | random colours | random colours | random colours | random colours |

Same prediction in every cell of this set: **DENSITY (A2)**: possible (m/n = 1.83; identical across the four items).

<details><summary>Legend: partitions / assignments</summary>

- **P1** = `v11 v12 v88 | v18 v23 v34 v54 v86 | v32 v66 v77 v96`
- **P2** = `v11 v18 v23 v34 v54 v77 | v12 v32 v66 v86 | v88 v96`
- **P3** = `v11 v18 v23 v34 v54 v77 | v12 v96 | v32 v66 v86 v88`
- **P4** = `v11 v18 v23 v34 v54 v77 | v12 v32 v66 | v86 v88 v96`
- **P5** = `v11 v18 v23 v54 v86 | v12 v34 v88 | v32 v66 v77 v96`
- **P6** = `v11 v18 v23 v34 v54 v77 | v12 v32 v66 v88 | v86 v96`
- **P7** = `v11 v18 v23 v34 v54 v66 v77 | v12 v32 | v86 v88 v96`
- **P8** = `v11 v18 v23 v34 v54 v86 | v12 v88 | v32 v66 v77 v96`

</details>

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| FF-3-LIST-ABORT (C1) | Weight: π_FF-3-LIST-ABORT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['IMPOSSIBLE on the three STUCK items, valid on CONTROL']. π may vary with item features and model (family I). | false IMPOSSIBLE rate STUCK - CONTROL = 1 - eps, unchanged by edge order | reaches the stuck vertex in listing order, says no colour is left, stops without revising (readout: faithfulness-weighted share T_h) |
| FF-3-LIST-INFEAS (C1) | Weight: π_FF-3-LIST-INFEAS (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['conflict at the stuck vertex on STUCK items (moves with vertex order), valid on CONTROL']. π may vary with item features and model (family I). | conflicts involve the stuck vertex in most of infeasible answers; location moves with vertex order , not edge order | forced colour at the stuck vertex (readout: faithfulness-weighted share T_h) |
| FF-3-EDGE-MENTION (C1 variant) | Weight: π_FF-3-EDGE-MENTION (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | IMPOSSIBLE moves with edge order, not vertex order | processes vertices in order of first mention in the edge list (readout: faithfulness-weighted share T_h) |
| GREEDY+REPAIR-LIST (C->F) | Weight: π_GREEDY+REPAIR-LIST (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['valid on all four']. π may vary with item features and model (family I). | valid; answer differs from FF-3-LIST-INFEAS by few vertices near the stuck vertex | first pass, conflict at the stuck vertex, local recolouring (readout: faithfulness-weighted share T_h) |
| DPLL-LIST (D) | Weight: π_DPLL-LIST (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['valid on all four']. π may vary with item features and model (family I). | valid on all four items; no STUCK-CONTROL difference at matched order-free hardness | chronological backtracking from the stuck vertex (readout: faithfulness-weighted share T_h) |
| DROP-LAST-EDGES (B1) | Weight: π_DROP-LAST-EDGES (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['conflict on late edges where predicted (moves with edge order)']. π may vary with item features and model (family I). | conflicts on the last-listed edges; location moves with edge order only | neighbourhood quotes omit the late edges (readout: faithfulness-weighted share T_h) |
| MIN-CONFLICTS (F) | Weight: π_MIN-CONFLICTS (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['valid on all four']. π may vary with item features and model (family I). | no STUCK-CONTROL difference; conflicts unlocalised | guess then fix anywhere (readout: faithfulness-weighted share T_h) |
| DENSITY (A2) | Weight: π_DENSITY (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | same answer on all four items | cites density (readout: faithfulness-weighted share T_h) |
| EXACT | Weight: π_EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['valid on all four']. π may vary with item features and model (family I). | valid on all four; never IMPOSSIBLE | search (readout: faithfulness-weighted share T_h) |
| NOISY-EXACT | Weight: π_NOISY-EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | conflict location uniform; no order interaction | slips (readout: faithfulness-weighted share T_h) |
| PERCEPTION-NOISE | Weight: π_PERCEPTION-NOISE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | conflicts on misquoted edges | K11 (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['unlocalised conflicts on all four']. π may vary with item features and model (family I). | about a third of edges in conflict | none (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| IMPOSSIBLE on the three STUCK items, valid on CONTROL | FF-3-LIST-ABORT (C1) | FF-3-EDGE-MENTION (C1 variant) (-3), NOISY-EXACT (-3), DPLL-LIST (D) (-4), EXACT (-4), FF-3-LIST-INFEAS (C1) (-4), GREEDY+REPAIR-LIST (C->F) (-4), MIN-CONFLICTS (F) (-4), PERCEPTION-NOISE (-4), DENSITY (A2) (-4), DROP-LAST-EDGES (B1) (-5), RANDOM (H) (-1200) | — |
| conflict at the stuck vertex on STUCK items (moves with vertex order), valid on CONTROL | FF-3-LIST-INFEAS (C1) | NOISY-EXACT (-3), PERCEPTION-NOISE (-3), DPLL-LIST (D) (-4), DROP-LAST-EDGES (B1) (-4), EXACT (-4), FF-3-EDGE-MENTION (C1 variant) (-4), FF-3-LIST-ABORT (C1) (-4), GREEDY+REPAIR-LIST (C->F) (-4), MIN-CONFLICTS (F) (-4), DENSITY (A2) (-4), RANDOM (H) (-304) | — |
| conflict on late edges where predicted (moves with edge order) | DROP-LAST-EDGES (B1) | NOISY-EXACT (-3), PERCEPTION-NOISE (-3), DPLL-LIST (D) (-4), EXACT (-4), FF-3-EDGE-MENTION (C1 variant) (-4), FF-3-LIST-INFEAS (C1) (-4), GREEDY+REPAIR-LIST (C->F) (-4), MIN-CONFLICTS (F) (-4), DENSITY (A2) (-4), FF-3-LIST-ABORT (C1) (-5), RANDOM (H) (-304) | — |
| valid on all four | DPLL-LIST (D), EXACT, GREEDY+REPAIR-LIST (C->F), MIN-CONFLICTS (F) (-0.3) | DROP-LAST-EDGES (B1) (-4), FF-3-LIST-ABORT (C1) (-4), FF-3-LIST-INFEAS (C1) (-4), RANDOM (H) (-1200) | PERCEPTION-NOISE (-0.8), DENSITY (A2) (-1.1), NOISY-EXACT (-1.3), FF-3-EDGE-MENTION (C1 variant) (-1.3) |
| unlocalised conflicts on all four | RANDOM (H) | PERCEPTION-NOISE (-2), NOISY-EXACT (-2), MIN-CONFLICTS (F) (-3), DPLL-LIST (D) (-5), DROP-LAST-EDGES (B1) (-5), EXACT (-5), FF-3-EDGE-MENTION (C1 variant) (-5), FF-3-LIST-ABORT (C1) (-5), FF-3-LIST-INFEAS (C1) (-5), GREEDY+REPAIR-LIST (C->F) (-5) | DENSITY (A2) (-1.2) |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | DENSITY (A2) | DPLL-LIST (D) | DROP-LAST-EDGES (B1) | EXACT | FF-3-EDGE-MENTION (C1 variant) | FF-3-LIST-ABORT (C1) | FF-3-LIST-INFEAS (C1) | GREEDY+REPAIR-LIST (C->F) | MIN-CONFLICTS (F) | NOISY-EXACT | PERCEPTION-NOISE | RANDOM (H) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IMPOSSIBLE on the three STUCK items, valid on CONTROL | -4.2 | -4.0 | -5.3 | -4.0 | -2.6 | 0.0 | -4.0 | -4.0 | -4.0 | -3.1 | -4.2 | -1199.7 |
| conflict at the stuck vertex on STUCK items (moves with vertex order), valid on CONTROL | -4.2 | -4.0 | -4.0 | -4.0 | -4.0 | -4.0 | 0.0 | -4.0 | -4.0 | -2.8 | -3.3 | -303.6 |
| conflict on late edges where predicted (moves with edge order) | -4.2 | -4.0 | 0.0 | -4.0 | -4.0 | -5.3 | -4.0 | -4.0 | -4.1 | -2.8 | -3.3 | -303.6 |
| valid on all four | -1.1 | 0.0 | -4.0 | 0.0 | -1.3 | -4.0 | -4.0 | 0.0 | -0.3 | -1.3 | -0.8 | -1199.7 |
| unlocalised conflicts on all four | -1.2 | -5.4 | -5.4 | -5.4 | -5.4 | -5.4 | -5.4 | -5.4 | -3.3 | -2.2 | -2.0 | 0.0 |

</details>

**Not separated by this set.** GREEDY+REPAIR vs DPLL-LIST when both end valid: separated by the number of vertices changed from the FF prefix (repair: few, near the stuck vertex) and by trace codes (local repair vs chronological backtracking).

### `E5-COL-A` · `STUCK/vertexA/edgeA`

*Domain:* colouring (k=3) · *framing:* textbook · *params:* `{"n": 12, "m": 22, "seed": 53, "listing_dpll_nodes": 34, "order_free_hardness_nodes": 12, "variant": "FF-3 in listing order gets stuck"}`

Prompt:

```text
Graph with 12 vertices and 22 edges.
Vertices (in this order): v23, v66, v34, v86, v96, v18, v54, v11, v12, v77, v32, v88
Edges: v23-v66, v23-v96, v23-v12, v66-v96, v34-v86, v34-v96, v34-v32, v34-v88, v86-v18, v86-v12, v86-v77, v86-v32, v96-v11, v96-v12, v96-v77, v96-v32, v18-v88, v54-v32, v11-v12, v11-v32, v12-v77, v12-v88

Colour every vertex with one of the colours 1, 2, ..., 3 so that the two ends of every edge get different colours. If this is impossible, answer IMPOSSIBLE.
After the line ANSWER:, write IMPOSSIBLE or one line `vertex: colour` per vertex, in this order: v23, v66, v34, v86, v96, v18, v54, v11, v12, v77, v32, v88.
```

Ground truth: colourable_with_3 = True; example = P4

Item hypotheses: column `STUCK/vertexA/edgeA` of the outputs table, plus the eval and trace rows above. Stuck-vs-control items are matched on n, m and backtracking nodes; within the stuck graph, vertex order and edge order are crossed.

### `E5-COL-A` · `STUCK/vertexB/edgeA`

*Domain:* colouring (k=3) · *framing:* textbook · *params:* `{"n": 12, "m": 22, "seed": 53, "listing_dpll_nodes": 32, "order_free_hardness_nodes": 12, "variant": "vertex list re-ordered: stuck vertex moves"}`

Prompt:

```text
Graph with 12 vertices and 22 edges.
Vertices (in this order): v11, v18, v23, v88, v77, v32, v54, v12, v66, v34, v86, v96
Edges: v11-v32, v11-v12, v96-v11, v18-v88, v86-v18, v23-v12, v23-v66, v23-v96, v12-v88, v34-v88, v12-v77, v86-v77, v96-v77, v54-v32, v34-v32, v86-v32, v96-v32, v86-v12, v96-v12, v66-v96, v34-v86, v34-v96

Colour every vertex with one of the colours 1, 2, ..., 3 so that the two ends of every edge get different colours. If this is impossible, answer IMPOSSIBLE.
After the line ANSWER:, write IMPOSSIBLE or one line `vertex: colour` per vertex, in this order: v11, v18, v23, v88, v77, v32, v54, v12, v66, v34, v86, v96.
```

Ground truth: colourable_with_3 = True; example = P4

Item hypotheses: column `STUCK/vertexB/edgeA` of the outputs table, plus the eval and trace rows above. Stuck-vs-control items are matched on n, m and backtracking nodes; within the stuck graph, vertex order and edge order are crossed.

### `E5-COL-A` · `STUCK/vertexA/edgeB`

*Domain:* colouring (k=3) · *framing:* textbook · *params:* `{"n": 12, "m": 22, "seed": 53, "listing_dpll_nodes": 34, "order_free_hardness_nodes": 12, "variant": "edge list reversed: last-listed edges change"}`

Prompt:

```text
Graph with 12 vertices and 22 edges.
Vertices (in this order): v23, v66, v34, v86, v96, v18, v54, v11, v12, v77, v32, v88
Edges: v12-v88, v12-v77, v11-v32, v11-v12, v54-v32, v18-v88, v96-v32, v96-v77, v96-v12, v96-v11, v86-v32, v86-v77, v86-v12, v86-v18, v34-v88, v34-v32, v34-v96, v34-v86, v66-v96, v23-v12, v23-v96, v23-v66

Colour every vertex with one of the colours 1, 2, ..., 3 so that the two ends of every edge get different colours. If this is impossible, answer IMPOSSIBLE.
After the line ANSWER:, write IMPOSSIBLE or one line `vertex: colour` per vertex, in this order: v23, v66, v34, v86, v96, v18, v54, v11, v12, v77, v32, v88.
```

Ground truth: colourable_with_3 = True; example = P4

Item hypotheses: column `STUCK/vertexA/edgeB` of the outputs table, plus the eval and trace rows above. Stuck-vs-control items are matched on n, m and backtracking nodes; within the stuck graph, vertex order and edge order are crossed.

### `E5-COL-A` · `CONTROL/vertexA/edgeA`

*Domain:* colouring (k=3) · *framing:* textbook · *params:* `{"n": 12, "m": 21, "seed": 53, "listing_dpll_nodes": 12, "order_free_hardness_nodes": 12, "variant": "matched control: FF-3 succeeds"}`

Prompt:

```text
Graph with 12 vertices and 21 edges.
Vertices (in this order): v18, v23, v32, v96, v66, v86, v77, v54, v34, v12, v88, v11
Edges: v18-v32, v18-v96, v18-v66, v18-v88, v23-v32, v23-v96, v23-v77, v23-v12, v32-v86, v32-v54, v32-v12, v32-v88, v32-v11, v96-v86, v96-v34, v66-v12, v86-v77, v86-v88, v77-v54, v77-v88, v34-v11

Colour every vertex with one of the colours 1, 2, ..., 3 so that the two ends of every edge get different colours. If this is impossible, answer IMPOSSIBLE.
After the line ANSWER:, write IMPOSSIBLE or one line `vertex: colour` per vertex, in this order: v18, v23, v32, v96, v66, v86, v77, v54, v34, v12, v88, v11.
```

Ground truth: colourable_with_3 = True; example = P1

Item hypotheses: column `CONTROL/vertexA/edgeA` of the outputs table, plus the eval and trace rows above. Stuck-vs-control items are matched on n, m and backtracking nodes; within the stuck graph, vertex order and edge order are crossed.

<a id="e5-sat-state-a"></a>
## E5 · Controlled partial states (3-SAT)  (`E5-SAT-STATE-A`)

**Reasoning question.** Given fixed values for three variables, how is the completion's weight split between ignoring them (POLARITY, C0), counting only the clauses they leave open (GREEDY, C1), following the clauses they make unit (UC, C2), and search?

**Controlled.** Formula identical in both items; same three variables fixed.  
**Varied.** The fixed values.

**Outputs by cell** (each theory's predicted answer on each item)

| Theory | `STATE-s1: POLARITY vs GREEDY` | `STATE-s2: UC vs GREEDY` |
|---|---|---|
| GREEDY-MENTION from state (C1) | S1 | S2 (falsified: C3) |
| POLARITY (C0) | S3 (falsified: C14) | S4 |
| UC-DET from state (C2) | S5 (falsified: C19) | S6 |
| DPLL from state (D) | S7 | S6 |
| WALK (F) | a valid completion by flips | a valid completion by flips |
| EXACT | one of 4 completions | one of 4 completions |
| NOISY-EXACT | near-valid completion | near-valid completion |
| PERCEPTION-NOISE | completion of a misread formula | completion of a misread formula |
| RANDOM (H) | random completion | random completion |

<details><summary>Legend: partitions / assignments</summary>

- **S1** = `x24=F x28=T x37=F x51=F x57=F x59=T x80=F x84=F x86=T x88=F`
- **S2** = `x24=F x28=T x37=F x51=T x57=F x59=T x80=F x84=F x86=T x88=F`
- **S3** = `x24=F x28=T x37=F x51=F x57=F x59=T x80=F x84=T x86=F x88=F`
- **S4** = `x24=F x28=T x37=F x51=T x57=F x59=T x80=F x84=T x86=F x88=F`
- **S5** = `x24=F x28=T x37=T x51=F x57=F x59=T x80=T x84=F x86=F x88=T`
- **S6** = `x24=F x28=T x37=T x51=T x57=F x59=T x80=F x84=T x86=F x88=T`
- **S7** = `x24=F x28=T x37=T x51=F x57=F x59=T x80=F x84=F x86=T x88=F`

</details>

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| GREEDY-MENTION from state (C1) | Weight: π_GREEDY-MENTION (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching GREEDY-MENTION above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following GREEDY-MENTION favour it over the nearest competitor NOISY-EXACT by log10 LR = 2.4 (separated). Full set (600 items): detects π_GREEDY-MENTION >= 0.03 (80% power) and bounds it <= 0.02 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | s1: answer = GREEDY completion in most of s1 items, above POLARITY's rate | counts only clauses the fixed values leave open (readout: faithfulness-weighted share T_h) |
| POLARITY (C0) | Weight: π_POLARITY (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching POLARITY above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following POLARITY favour it over the nearest competitor NOISY-EXACT by log10 LR = 2.6 (separated). Full set (600 items): detects π_POLARITY >= 0.03 (80% power) and bounds it <= 0.02 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | completions identical across s1/s2 for the free variables (state-blind) | tallies over all clauses (readout: faithfulness-weighted share T_h) |
| UC-DET from state (C2) | Weight: π_UC-DET (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching UC-DET above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following UC-DET favour it over the nearest competitor DPLL from state (D) by log10 LR = 2.2 (separated). Full set (600 items): detects π_UC-DET >= 0.04 (80% power) and bounds it <= 0.02 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | s2: answer = UC completion; forced values taken in most of s2 items | 'forced by clause ...' (readout: faithfulness-weighted share T_h) |
| DPLL from state (D) | Weight: π_DPLL (posterior mean, 95% interval) from the mixture fit; lift = share of errors matching DPLL above the matched baseline; Δlog10 L vs RANDOM and vs the nearest competitor. Dev set: answers following DPLL favour it over the nearest competitor EXACT by log10 LR = 1.2 (weakly separated). Full set (600 items): detects π_DPLL >= 0.08 (80% power) and bounds it <= 0.05 (upper 95%) when it carries no weight. π may vary with item features and model (family I). | valid completions in both states | decisions with backtracking (readout: faithfulness-weighted share T_h) |
| WALK (F) | Weight: π_WALK (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer a solution predicted by no member']. π may vary with item features and model (family I). | valid, not tied to member completions | flips (readout: faithfulness-weighted share T_h) |
| EXACT | Weight: π_EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer a solution predicted by no member']. π may vary with item features and model (family I). | valid = 1 - eps | search (readout: faithfulness-weighted share T_h) |
| NOISY-EXACT | Weight: π_NOISY-EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer a solution predicted by no member']. π may vary with item features and model (family I). | falsified clauses uniform | slips (readout: faithfulness-weighted share T_h) |
| PERCEPTION-NOISE | Weight: π_PERCEPTION-NOISE (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['every answer a solution predicted by no member']. π may vary with item features and model (family I). | falsified clauses misquoted | K11 (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | rarely valid | none (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| answers = GREEDY-MENTION from state (C1)'s prediction on every item | GREEDY-MENTION from state (C1) | NOISY-EXACT (-2), PERCEPTION-NOISE (-3), EXACT (-3), WALK (F) (-3), RANDOM (H) (-4), DPLL from state (D) (-4), POLARITY (C0) (-4), UC-DET from state (C2) (-4) | — |
| answers = POLARITY (C0)'s prediction on every item | POLARITY (C0) | NOISY-EXACT (-3), PERCEPTION-NOISE (-3), EXACT (-3), WALK (F) (-3), RANDOM (H) (-4), DPLL from state (D) (-4), GREEDY-MENTION from state (C1) (-4), UC-DET from state (C2) (-4) | — |
| answers = UC-DET from state (C2)'s prediction on every item | UC-DET from state (C2) | DPLL from state (D) (-2), NOISY-EXACT (-3), PERCEPTION-NOISE (-3), EXACT (-3), WALK (F) (-3), RANDOM (H) (-4), GREEDY-MENTION from state (C1) (-4), POLARITY (C0) (-4) | — |
| answers = DPLL from state (D)'s prediction on every item | DPLL from state (D) | UC-DET from state (C2) (-2), RANDOM (H) (-4), GREEDY-MENTION from state (C1) (-4), POLARITY (C0) (-4) | EXACT (-1.2), WALK (F) (-1.2), PERCEPTION-NOISE (-1.3), NOISY-EXACT (-1.5) |
| every answer a solution predicted by no member | EXACT, WALK (F), PERCEPTION-NOISE (-0.1), NOISY-EXACT (-0.3) | RANDOM (H) (-3), DPLL from state (D) (-3), GREEDY-MENTION from state (C1) (-3), POLARITY (C0) (-3), UC-DET from state (C2) (-3) | — |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | DPLL from state (D) | EXACT | GREEDY-MENTION from state (C1) | NOISY-EXACT | PERCEPTION-NOISE | POLARITY (C0) | RANDOM (H) | UC-DET from state (C2) | WALK (F) |
|---|---|---|---|---|---|---|---|---|---|
| answers = GREEDY-MENTION from state (C1)'s prediction on every item | -4.3 | -2.7 | 0.0 | -2.4 | -2.5 | -4.3 | -4.0 | -4.3 | -2.7 |
| answers = POLARITY (C0)'s prediction on every item | -4.3 | -2.8 | -4.3 | -2.6 | -2.8 | 0.0 | -4.0 | -4.3 | -2.8 |
| answers = UC-DET from state (C2)'s prediction on every item | -2.2 | -2.8 | -4.3 | -2.6 | -2.6 | -4.3 | -4.0 | 0.0 | -2.8 |
| answers = DPLL from state (D)'s prediction on every item | 0.0 | -1.2 | -4.3 | -1.5 | -1.3 | -4.3 | -4.0 | -2.2 | -1.2 |
| every answer a solution predicted by no member | -3.1 | 0.0 | -3.1 | -0.3 | -0.1 | -3.1 | -2.8 | -3.1 | 0.0 |

</details>

**Not separated by this set.** In s2, UC-DET and DPLL give the same completion → s1 separates them (UC-DET falsifies C19 there).

### `E5-SAT-STATE-A` · `STATE-s1: POLARITY vs GREEDY`

*Domain:* 3-SAT (partial assignment given) · *framing:* textbook · *params:* `{"n": 10, "m": 35, "fixed": {"x51": "F", "x24": "F", "x57": "F"}, "seed": 61}`

<details><summary>Prompt</summary>

```text
A formula over 10 true/false variables. Every clause must contain at least one true literal.
C1: not x51 or not x24 or not x57
C2: not x37 or x51 or not x84
C3: not x51 or x84 or x24
C4: not x24 or x84 or x37
C5: not x59 or not x88 or not x86
C6: not x80 or not x84 or not x24
C7: x57 or not x24 or not x86
C8: x37 or not x86 or x59
C9: not x59 or not x24 or x28
C10: not x59 or not x57 or x28
C11: not x51 or x88 or x59
C12: x28 or not x59 or not x51
C13: x59 or not x37 or x84
C14: x86 or x51 or x80
C15: not x24 or x28 or x37
C16: not x88 or not x51 or x59
C17: x88 or x57 or not x24
C18: x51 or not x24 or x84
C19: not x80 or x24 or x86
C20: not x24 or not x51 or not x28
C21: not x57 or x59 or x51
C22: not x24 or x86 or x84
C23: not x80 or not x37 or not x86
C24: not x84 or not x86 or x88
C25: not x86 or not x88 or x24
C26: not x80 or x24 or x88
C27: not x86 or not x24 or x51
C28: not x80 or not x84 or not x28
C29: not x57 or x80 or not x84
C30: not x80 or x28 or x51
C31: not x57 or x28 or not x37
C32: not x88 or not x24 or x37
C33: not x80 or x51 or not x84
C34: not x24 or not x88 or x86
C35: x84 or not x24 or not x37

These values are already fixed and must not be changed: x51=F, x24=F, x57=F.

Find values for all variables that make every clause true (keeping the fixed values), or say UNSAT if none exist.
After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, in this order: x51, x24, x57, x37, x84, x59, x88, x86, x80, x28.
```

</details>

Ground truth: completion_exists = True; n_completions = 4

Item hypotheses: column `STATE-s1: POLARITY vs GREEDY` of the outputs table, plus the eval and trace rows above. Same formula in both items; only the fixed values differ. C0 ignores them, C1 counts only clauses they leave open, C2 follows the clauses they make unit.

### `E5-SAT-STATE-A` · `STATE-s2: UC vs GREEDY`

*Domain:* 3-SAT (partial assignment given) · *framing:* textbook · *params:* `{"n": 10, "m": 35, "fixed": {"x51": "T", "x24": "F", "x57": "F"}, "seed": 61}`

<details><summary>Prompt</summary>

```text
A formula over 10 true/false variables. Every clause must contain at least one true literal.
C1: not x51 or not x24 or not x57
C2: not x37 or x51 or not x84
C3: not x51 or x84 or x24
C4: not x24 or x84 or x37
C5: not x59 or not x88 or not x86
C6: not x80 or not x84 or not x24
C7: x57 or not x24 or not x86
C8: x37 or not x86 or x59
C9: not x59 or not x24 or x28
C10: not x59 or not x57 or x28
C11: not x51 or x88 or x59
C12: x28 or not x59 or not x51
C13: x59 or not x37 or x84
C14: x86 or x51 or x80
C15: not x24 or x28 or x37
C16: not x88 or not x51 or x59
C17: x88 or x57 or not x24
C18: x51 or not x24 or x84
C19: not x80 or x24 or x86
C20: not x24 or not x51 or not x28
C21: not x57 or x59 or x51
C22: not x24 or x86 or x84
C23: not x80 or not x37 or not x86
C24: not x84 or not x86 or x88
C25: not x86 or not x88 or x24
C26: not x80 or x24 or x88
C27: not x86 or not x24 or x51
C28: not x80 or not x84 or not x28
C29: not x57 or x80 or not x84
C30: not x80 or x28 or x51
C31: not x57 or x28 or not x37
C32: not x88 or not x24 or x37
C33: not x80 or x51 or not x84
C34: not x24 or not x88 or x86
C35: x84 or not x24 or not x37

These values are already fixed and must not be changed: x51=T, x24=F, x57=F.

Find values for all variables that make every clause true (keeping the fixed values), or say UNSAT if none exist.
After the line ANSWER:, write UNSAT or the values as `x=T` / `x=F`, comma-separated, in this order: x51, x24, x57, x37, x84, x59, x88, x86, x80, x28.
```

</details>

Ground truth: completion_exists = True; n_completions = 4

Item hypotheses: column `STATE-s2: UC vs GREEDY` of the outputs table, plus the eval and trace rows above. Same formula in both items; only the fixed values differ. C0 ignores them, C1 counts only clauses they leave open, C2 follows the clauses they make unit.

<a id="e5-ent-a"></a>
## E5 · Greedy countermodel construction in entailment  (`E5-ENT-A`)

**Reasoning question.** How much weight does greedy countermodel construction without revision carry in deciding 'does it follow?' (GREEDY-CM says YES whenever its one attempt fails), against exact reasoning and cues? Premise order changes GREEDY-CM's mention order and so its answer.

**Controlled.** Premise set, conclusion, atoms.  
**Varied.** Premise order.

**Outputs by cell** (each theory's predicted answer on each item)

| Theory | `ORDER-A` | `ORDER-B (premises reversed)` |
|---|---|---|
| GREEDY-CM (C1) | YES | NO |
| EXACT (truth table) | NO | NO |
| ALWAYS-YES (A1) | YES | YES |
| NOISY-EXACT | NO with prob. 1-eps | NO with prob. 1-eps |
| RANDOM (H) | YES/NO at 50% | YES/NO at 50% |

Same prediction in every cell of this set: **UP-fixpoint (B1)**: NO (nothing derivable without a categorical premise); **ETR / ONLINE-STATE (C4)**: to be computed with PyETR (B4/C4 verticals).

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| GREEDY-CM (C1) | Weight: π_GREEDY-CM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['YES on ORDER-A, NO on ORDER-B']. π may vary with item features and model (family I). | YES on ORDER-A and NO on ORDER-B in most of such pairs; never YES on items where GREEDY-CM finds the countermodel | builds one situation atom by atom in mention order; no revision; concludes 'follows' when it fails (readout: faithfulness-weighted share T_h) |
| EXACT (truth table) | Weight: π_EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['NO on both']. π may vary with item features and model (family I). | NO on both orders | cases or countermodel search with revision (readout: faithfulness-weighted share T_h) |
| UP-fixpoint (B1) | Weight: π_UP-fixpoint (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['NO on both']. π may vary with item features and model (family I). | NO on both (sound: never says YES without a derivation) | derives literals from categorical premises (readout: faithfulness-weighted share T_h) |
| ALWAYS-YES (A1) | Weight: π_ALWAYS-YES (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['YES on both']. π may vary with item features and model (family I). | YES on both orders | no case analysis (readout: faithfulness-weighted share T_h) |
| ETR / ONLINE-STATE (C4) | Weight: no likelihood computed for this theory in this set (see the coverage matrix for the set that bounds it). | premise-order effect pattern from PyETR | premise-by-premise updating (readout: faithfulness-weighted share T_h) |
| NOISY-EXACT | Weight: π_NOISY-EXACT (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['NO on both']. π may vary with item features and model (family I). | order-free | slips (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | order-free | none (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| YES on ORDER-A, NO on ORDER-B | GREEDY-CM (C1) | — | RANDOM (H) (-0.5), NOISY-EXACT (-0.6), ALWAYS-YES (A1) (-0.9), EXACT (truth table) (-0.9), UP-fixpoint (B1) (-0.9) |
| NO on both | EXACT (truth table), UP-fixpoint (B1), NOISY-EXACT (-0.2) | — | RANDOM (H) (-0.5), GREEDY-CM (C1) (-0.9), ALWAYS-YES (A1) (-1.9) |
| YES on both | ALWAYS-YES (A1) | — | RANDOM (H) (-0.5), GREEDY-CM (C1) (-0.9), NOISY-EXACT (-1.1), EXACT (truth table) (-1.9), UP-fixpoint (B1) (-1.9) |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | ALWAYS-YES (A1) | EXACT (truth table) | GREEDY-CM (C1) | NOISY-EXACT | RANDOM (H) | UP-fixpoint (B1) |
|---|---|---|---|---|---|---|
| YES on ORDER-A, NO on ORDER-B | -0.9 | -0.9 | 0.0 | -0.6 | -0.5 | -0.9 |
| NO on both | -1.9 | 0.0 | -0.9 | -0.2 | -0.5 | 0.0 |
| YES on both | 0.0 | -1.9 | -0.9 | -1.1 | -0.5 | -1.9 |

</details>

**Not separated by this set.** ETR / C4 premise-order predictions are not yet computed for this pair (PyETR, owned by the B4/C4 verticals); until then, a YES/NO order effect does not separate GREEDY-CM from C4.

### `E5-ENT-A` · `ORDER-A`

*Domain:* propositional entailment · *framing:* textbook · *params:* `{"atoms": 5, "premises": 4, "seed": 71}`

Prompt:

```text
Premises:
1. Not both E and C.
2. B or C (or both).
3. Not both B and A.
4. E or A (or both).

Conclusion: D.

After the line ANSWER:, write YES if the conclusion must be true whenever all premises are true, otherwise NO.
```

Ground truth: follows = False; countermodels = 2

Item hypotheses: column `ORDER-A` of the outputs table, plus the eval and trace rows above. GREEDY-CM errs only by commission (YES when a countermodel exists) and its error depends on premise order. Coordinate with the B4/C4 verticals: ETR/C4 predictions for these two orders are to be added from PyETR.

### `E5-ENT-A` · `ORDER-B (premises reversed)`

*Domain:* propositional entailment · *framing:* textbook · *params:* `{"atoms": 5, "premises": 4, "seed": 71}`

Prompt:

```text
Premises:
1. E or A (or both).
2. Not both B and A.
3. B or C (or both).
4. Not both E and C.

Conclusion: D.

After the line ANSWER:, write YES if the conclusion must be true whenever all premises are true, otherwise NO.
```

Ground truth: follows = False; countermodels = 2

Item hypotheses: column `ORDER-B (premises reversed)` of the outputs table, plus the eval and trace rows above. GREEDY-CM errs only by commission (YES when a countermodel exists) and its error depends on premise order. Coordinate with the B4/C4 verticals: ETR/C4 predictions for these two orders are to be added from PyETR.

<a id="e6-ea-a"></a>
## E6 · Early answering: is the trace doing the work?  (`E6-EA-A`)

**Reasoning question.** When the trace is cut at fraction f and an answer forced, what share of answers reflects the commitments made so far (faithful constructive trace), and what share was fixed before the trace (post hoc)? The shares set the trace reliability r.

**Controlled.** Item (E1 c2), model, decoding.  
**Varied.** Truncation fraction f (full study: 0, .1, .25, .5, .75).

**Outputs by cell** (each theory's predicted answer on each item)

| Theory | `EARLY-ANSWER f=0.0` | `EARLY-ANSWER f=0.5` |
|---|---|---|
| FAITHFUL C1 trace | the model's default (no information yet) | committed vertices keep their trace colours; the rest follow FF from the trace state |
| POST-HOC trace (answer pre-committed) | the final answer already at f=0 | the final answer already at f=0 |
| LATENT EXACT + narrated trace | a valid colouring at every f | a valid colouring at every f |
| RANDOM (H) | random colouring | random colouring |

**Weight readouts, signatures and trace predictions** (pre-registered; `[cell: …]` marks cell-specific wording)

| Theory | Weight readout (quantities; dev-set separation; full-size power) | Signature if the theory carried all the weight (π = 1) | Trace signature and faithfulness-weighted readout |
|---|---|---|---|
| FAITHFUL C1 trace | Weight: π_FAITHFUL C1 trace (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['f=0 default, f=0.5 keeps prefix + FF continuation']. π may vary with item features and model (family I). | agreement with the final answer rises in steps as vertices are committed (near 1 - eps on committed items, chance on uncommitted ones at f=0) | - (readout: faithfulness-weighted share T_h) |
| POST-HOC trace (answer pre-committed) | Weight: π_POST-HOC trace (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['final answer already at f=0 and f=0.5']. π may vary with item features and model (family I). | agreement with the final answer at f=0 = 1 - eps | - (readout: faithfulness-weighted share T_h) |
| LATENT EXACT + narrated trace | Weight: π_LATENT EXACT + narrated trace (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: ['valid non-FF answers at both']. π may vary with item features and model (family I). | valid forced answers at f=0 that differ from FF | - (readout: faithfulness-weighted share T_h) |
| RANDOM (H) | Weight: π_RANDOM (posterior mean, 95% interval) from the mixture fit; Δlog10 L vs RANDOM and vs nearest competitor. Outcome patterns that favour it on the dev set: none (it is never the best single explanation here). π may vary with item features and model (family I). | agreement at chance for all f | - (readout: faithfulness-weighted share T_h) |

**Likelihood ratios on the dev set** (log10 P(pattern | theory) minus the best theory's, under the library noise model; 0 = best)

| Outcome pattern over the set's items | Favoured (within 0.5 log10 of the best) | Pushed toward zero (≤ −2, i.e. ≥ 100:1 against) | Weakly disfavoured (−2 < log10 LR < −0.5) |
|---|---|---|---|
| f=0 default, f=0.5 keeps prefix + FF continuation | FAITHFUL C1 trace | LATENT EXACT + narrated trace (-3), POST-HOC trace (answer pre-committed) (-3), RANDOM (H) (-600) | — |
| final answer already at f=0 and f=0.5 | POST-HOC trace (answer pre-committed) | FAITHFUL C1 trace (-3), LATENT EXACT + narrated trace (-3), RANDOM (H) (-600) | — |
| valid non-FF answers at both | LATENT EXACT + narrated trace | FAITHFUL C1 trace (-3), POST-HOC trace (answer pre-committed) (-3), RANDOM (H) (-600) | — |

<details><summary>Full log10 likelihood-ratio matrix</summary>

| Outcome pattern | FAITHFUL C1 trace | LATENT EXACT + narrated trace | POST-HOC trace (answer pre-committed) | RANDOM (H) |
|---|---|---|---|---|
| f=0 default, f=0.5 keeps prefix + FF continuation | 0.0 | -2.6 | -2.6 | -599.9 |
| final answer already at f=0 and f=0.5 | -2.6 | -2.6 | 0.0 | -599.9 |
| valid non-FF answers at both | -2.6 | 0.0 | -2.6 | -599.9 |

</details>

**Not separated by this set.** Shown with a synthetic FF-LIST trace (the fake-model control). Real runs truncate the model's own trace.

### `E6-EA-A` · `EARLY-ANSWER f=0.0`

*Domain:* colouring · *framing:* textbook · *params:* `{"truncate_fraction": 0.0, "source_item": "E1 c2-RELABEL"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v48, v96, v88, v83, v57, v51, v46, v32, v22, v43
Neighbours (one line per vertex, same order):
v48: v96, v32
v96: v48, v83, v32, v43
v88: v57, v51, v22
v83: v96
v57: v88, v43
v51: v88
v46: v43
v32: v48, v96, v43
v22: v88, v43
v43: v96, v57, v46, v32, v22

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v48, v96, v88, v83, v57, v51, v46, v32, v22, v43.

[assistant prefill]
<think>

</think>
ANSWER:

```

Ground truth: note = same item as E1 c2

Item hypotheses: column `EARLY-ANSWER f=0.0` of the outputs table, plus the eval and trace rows above. E6 re-prompts truncate the model's own best-effort trace at f in {0, .1, .25, .5, .75} and force an answer. Shown with a synthetic trace.

### `E6-EA-A` · `EARLY-ANSWER f=0.5`

*Domain:* colouring · *framing:* textbook · *params:* `{"truncate_fraction": 0.5, "source_item": "E1 c2-RELABEL"}`

Prompt:

```text
Graph with 10 vertices.
Vertices (in this order): v48, v96, v88, v83, v57, v51, v46, v32, v22, v43
Neighbours (one line per vertex, same order):
v48: v96, v32
v96: v48, v83, v32, v43
v88: v57, v51, v22
v83: v96
v57: v88, v43
v51: v88
v46: v43
v32: v48, v96, v43
v22: v88, v43
v43: v96, v57, v46, v32, v22

Colour every vertex with a positive integer so that neighbours get different colours, using as few colours as possible.
After the line ANSWER:, write one line `vertex: colour` per vertex, in this order: v48, v96, v88, v83, v57, v51, v46, v32, v22, v43.

[assistant prefill]
<think>
I'll go through the vertices in the listed order.
v48: earlier neighbours none, so 1.
v96: earlier neighbours v48 use 1, so 2.
v88: earlier neighbours none, so 1.
v83: earlier neighbours v96 use 2, so 1.
v57: earlier neighbours v88 use 1, so 2.
</think>
ANSWER:

```

Ground truth: note = same item as E1 c2

Item hypotheses: column `EARLY-ANSWER f=0.5` of the outputs table, plus the eval and trace rows above. E6 re-prompts truncate the model's own best-effort trace at f in {0, .1, .25, .5, .75} and force an answer. Shown with a synthetic trace.

