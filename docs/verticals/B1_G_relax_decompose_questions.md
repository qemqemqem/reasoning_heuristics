# B1 / G question library: worked counterfactual sets

*Companion to [B1_G_relax_decompose.md](B1_G_relax_decompose.md). It holds 42 items in 6 sets, one set per eval. Each set is a base item plus minimal-pair variants covering the cells of its design. The machine-readable copy is [`data/examples/B1_G_relax_decompose.jsonl`](../../data/examples/B1_G_relax_decompose.jsonl).*

## How these items were produced and checked

**Computed, not hand-derived.** Every ground truth and every heuristic prediction below was computed by throwaway scripts (kept outside the repo) using:

- **z3 4.13.3** for entailment ground truth;
- **PyETR 1.0.0** (`default_procedure_does_it_follow`) for ETR predictions;
- **brute-force enumeration** for model probabilities P(q | premises), colourings and knapsack;
- the reference implementations in §1.4 of the vertical doc: `UP-k`, `UP-PASS`, `UP-REFUTE`, `RES-w`, `PS(sel)`, `BC-b`, `FC-budget-b`, B4 strengthenings, `DROP(sel)`, `IGNORE-CROSSLINKS`, `FIRST-FIT-cap`, `DSATUR-cap`, `CYCLIC`, `MIN-CONFLICTS` (simulated, 2,000 runs), `DP-LIST` and greedy rules.

Prompts are generated from the same structures, so each prompt matches its computed answer.

**Item sizes are dev-tier**, so a reader can follow them. The full-study generators scale the same templates (doc §2.6–§2.11): N up to 224 premises, d up to 32, graphs to n = 24, knapsack to n = 24.

## Hypothesis blocks: three predictions per theory, per item

| Field | What it predicts |
|---|---|
| **(a) Output** | The answer on this item |
| **(b) Eval prediction** | The aggregate result over the item's cell, as a pre-registered level on a cell rate. It maps onto π_h and lift (doc §2.5a). |
| **(c) CoT** | The trace features the L0/L1 coding scheme should find (doc §2.4) |

- (c) is listed once per set, because it is the same for every item in a set.
- Stochastic nulls (`NOISY-EXACT`, `PERCEPTION-NOISE`, `SAMPLE-m`, `RANDOM`, `MIN-CONFLICTS`) predict distributions. Their weight is bounded by cell rates, not by single items.

## Scalar readouts and disconfirmation

Heuristics may be used only partly. So the evidence from these items is read out as **weights**, not verdicts (doc §2.5a):

- **π_h**: the mixture weight, as a posterior mean with a 95% interval;
- **lift**: the share of errors h explains above a permutation baseline;
- **ΔELPD / log₁₀ BF**: against the null, and against the nearest competitor;
- **trace match share**, weighted by faithfulness.

**Item level.** Each item lists, for every possible outcome, the theories it counts against, with a **log₁₀ likelihood ratio per response**: about 1.26 for 3-way answers at lapse ε = 0.1, and more when there are more outcome categories. These add up over samples and items inside the mixture fit.

**Set level.** Each set's **discrimination table** groups theories by their predicted answer pattern:

- A row gives the log₁₀ LR in favour of its theories over every other theory, if that pattern is observed.
- Theories that share a row cannot be separated by that set, and the last column names the set that separates them.

**The weight statements.** Every set can move weight away from at least its two nearest competitors. Typically each set has the power to bound π_competitor ≤ 0.1 (upper 95%), or to detect π_h ≥ 0.04–0.06 per model (doc §2.5a). The doc's §2.12 matrix shows that the library as a whole can bound every theory's weight, including the nulls.

## Answer abbreviations

In the discrimination tables, T / F / U = TRUE / FALSE / UNDETERMINED.

## Sets at a glance

| Set | Eval | Domain | Items | Key counterfactual |
|---|---|---|---|---|
| E1 | Propagation depth × cone shape | Entailment | 9 | Matched-d trio (chain3 / ladder3 / tree3) and matched-s triple (tree3 / ladder4 / chain7); catches (reversed link, negated fact, missing antecedent); bare framing |
| E2 | Omission vs commission; case-split ladder | Entailment | 13 | Dilemma vs sibling; b* = 1 gadget vs sibling; illusory vs control; AC/DA/MP/MT quartet; P(q) = 0.75 vs entailed; DS |
| E3 | Premise selection | Entailment | 7 | Early/late × proof/reverse order; disjunctive phrasing; query first; catch |
| E4 | Critical-constraint localisation | Coloring | 5 | Odd wheel R1; last conflict swapped; feasible sibling; irrelevant pendant last vs first |
| E5 | Cross-link quads; header move | Coloring, entailment | 6 | NC / SC / BD clustered; SC interleaved; header splits vs does not split the chain |
| E6 | DP cost dial | Knapsack | 2 | Low-R vs high-R at matched greedy gaps |

## E1 — Propagation depth vs cone size (UP-k) and catch siblings

- **Target:** UP-k (B1). **Nearest competitors:** NOISY-EXACT / FC-budget (size-limited); BC-b (unfolding-limited); BICONDITIONAL / DROP-CONJUNCT (B4 commission).
- **Note:** Dev-tier illustration (N = 28). Full-study items use N = 112-224 and d up to 32 (doc §2.6). Catches here have P(q) = 0.8-0.9, so SAMPLE-3 commits often; the full generator balances P(q) near 0.5.

**(c) CoT predictions for this set** (pre-registered; scored by the L0 parser and the validated L1 codes, doc §2.4):

| Theory | Predicted trace features |
|---|---|
| `UP-2` | Asserts derived literals in non-decreasing depth order (tau_depth >= 0.6), including fan-out literals that are not ancestors of the query; stops after round 2 and says the query is not settled if it needs more; no case splits; no goals stated first. |
| `UP-4` | As UP-2 but stops after round 4. |
| `UP-inf` | Depth-ordered assertions to the fixpoint (fan-out literals included); reaches the query iff it is propagation-derivable; no case splits. |
| `FC-inf (MP only)` | As UP-inf; every step cites a conditional in its written direction; no contrapositive ('since not B, not A') or disjunctive-syllogism steps. |
| `RES-2 (3 rounds)` | States composed conditionals or derived disjunctions ('so if A then C', 'so A or C') before applying them; no case branches. |
| `UP-PASS-1` | Walks the premises once in printed order, asserting a literal when its premise is read; never returns to an earlier premise (tau_text >= 0.6). |
| `PS(RECENT,12)` | Never quotes or uses premises before the last 12. |
| `PS(FIRST,12)` | Never quotes or uses premises after the first 12. |
| `PS(SHORT,2)` | Never uses an 'If ... and ...' rule or any premise with 3+ literals. |
| `BC-10` | Starts from the query and states sub-goals ('to show X we need Y') before confirming facts; asserts no fan-out literals; gives up after about 10 sub-goals. |
| `BICONDITIONAL` | Uses some conditional backwards (from its consequent to its antecedent) or from a false antecedent to a false consequent. |
| `DROP-CONJUNCT` | Fires an 'If A and B' rule after establishing only one of A, B. |
| `CLOSED-WORLD` | Concludes 'not X' because X was not derived. |
| `FIRST` | Treats an 'A or B' premise as asserting A. |
| `FREQ` | No derivation connecting facts to the query; justifies the answer by how the query is mentioned. |
| `NONE` | No derivation; says at once that the premises do not settle it. |
| `EXACT` | A complete derivation of the query, or a demonstration that both values are consistent. |
| `FC-budget-8` | Asserts every derivable literal in breadth-first order and stops after about 8 assertions. |
| `NOISY-EXACT(eps=0.05)` | Depth-ordered derivation in which one cone literal is skipped or one rule misapplied; the error is visible as a gap or an unjustified step. |
| `PERCEPTION-NOISE(rho=0.03)` | A premise is misquoted or omitted when restated, and the derivation is correct relative to the misread premises. |
| `SAMPLE-3` | Tries a few concrete truth assignments and checks them against the premises. |
| `RANDOM` | No relation between the trace and the answer. |

### E1-a · chain(d=3) determined

- **Tests:** Does accuracy depend on derivation depth d alone (UP-k), or on cone size s (NOISY-EXACT, FC-budget), unfolding u (BC), or fan-in (PS(SHORT), RES-2)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms. **Varied:** cone shape and depth.
- **Ground truth:** `TRUE`. **Params:** `{"shape": "chain", "d": 3, "cone_size_s": 3, "unfolding_u": 3, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": 0.0, "variant": "determined", "P_q": 1.0, "bfs_index": 5, "up_depth": 3}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the green fan is running, then the blue door is open.
2. If the green fan is running, then the gold tap is dripping.
3. If the red bell is ringing and the green clock is stopped, then the purple flag is raised.
4. If the purple valve is shut and the silver box is full, then the black flag is raised.
5. If the green alarm is armed, then the white pump is working.
6. If the red fan is running and the orange alarm is armed, then the pink lamp is on.
7. If the gold valve is shut and the brown gate is locked, then the green valve is shut.
8. If the gold pump is working, then the purple fan is running.
9. The silver alarm is armed.
10. The white gate is locked.
11. If the gold tap is dripping, then the white flag is raised.
12. The purple tap is dripping.
13. If the white flag is raised, then the gold flag is raised.
14. The purple box is full.
15. The purple clock is stopped.
16. If the grey bell is ringing, then the white lamp is on.
17. If the gold fan is running and the silver bell is ringing, then the black lamp is on.
18. If the black alarm is armed and the blue clock is stopped, then the blue flag is raised.
19. The purple alarm is armed.
20. If the grey flag is raised, then the orange clock is stopped.
21. If the gold tap is dripping, then the orange pump is working.
22. If the pink flag is raised, then the blue lamp is on.
23. If the purple gate is locked, then the gold flag is raised.
24. If the blue fan is running and the green pump is working, then the orange door is open.
25. The grey valve is shut.
26. If the brown tap is dripping and the gold box is full, then the silver door is open.
27. The grey fan is running.
28. The green fan is running.

Question: Is it true that the gold flag is raised?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | chain(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-4` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `UP-inf` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `RES-2 (3 rounds)` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `PS(RECENT,12)` | UNDETERMINED | chain(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,12)` | UNDETERMINED | chain(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(SHORT,2)` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `DROP-CONJUNCT` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | chain(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-budget-8` | TRUE | chain(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | chain(d=3) determined: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.89, else UNDETERMINED | chain(d=3) determined: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | chain(d=3) determined: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | chain(d=3) determined: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `UP-2`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-4`, `UP-PASS-1`, `UP-inf`

### E1-b · ladder(d=3) determined

- **Tests:** Does accuracy depend on derivation depth d alone (UP-k), or on cone size s (NOISY-EXACT, FC-budget), unfolding u (BC), or fan-in (PS(SHORT), RES-2)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms. **Varied:** cone shape and depth.
- **Ground truth:** `TRUE`. **Params:** `{"shape": "ladder", "d": 3, "cone_size_s": 5, "unfolding_u": 7, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": 0.0, "variant": "determined", "P_q": 1.0, "bfs_index": 7, "up_depth": 3}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the grey alarm is armed, then the white flag is raised.
2. If the silver alarm is armed, then the blue lamp is on.
3. If the gold door is open, then the silver door is open.
4. If the gold fan is running, then the silver fan is running.
5. The blue door is open.
6. If the white door is open and the blue clock is stopped, then the black lamp is on.
7. If the blue door is open, then the black door is open.
8. If the pink gate is locked and the purple lamp is on, then the blue gate is locked.
9. The orange pump is working.
10. The gold flag is raised.
11. If the red box is full and the green box is full, then the blue pump is working.
12. If the gold tap is dripping and the white fan is running, then the grey box is full.
13. The white tap is dripping.
14. If the blue door is open and the gold fan is running, then the grey bell is ringing.
15. If the grey bell is ringing and the black clock is stopped, then the green box is full.
16. If the brown bell is ringing, then the silver tap is dripping.
17. If the gold fan is running and the blue door is open, then the black clock is stopped.
18. The gold lamp is on.
19. The purple bell is ringing.
20. The gold fan is running.
21. The black valve is shut.
22. If the black clock is stopped and the grey bell is ringing, then the red box is full.
23. If the black alarm is armed, then the green fan is running.
24. If the blue fan is running, then the gold gate is locked.
25. If the black pump is working, then the red lamp is on.
26. The purple tap is dripping.
27. If the silver flag is raised, then the orange valve is shut.
28. If the blue alarm is armed, then the blue pump is working.

Question: Is it true that the blue pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | ladder(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-4` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `UP-inf` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | ladder(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-PASS-1` | UNDETERMINED | ladder(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(RECENT,12)` | UNDETERMINED | ladder(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,12)` | UNDETERMINED | ladder(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(SHORT,2)` | UNDETERMINED | ladder(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BC-10` | UNDETERMINED | ladder(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `DROP-CONJUNCT` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | ladder(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-budget-8` | TRUE | ladder(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.77, else UNDETERMINED | ladder(d=3) determined: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.81, else UNDETERMINED | ladder(d=3) determined: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | ladder(d=3) determined: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | ladder(d=3) determined: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-PASS-1`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `UP-4`, `UP-inf`

### E1-c · tree(d=3) determined

- **Tests:** Does accuracy depend on derivation depth d alone (UP-k), or on cone size s (NOISY-EXACT, FC-budget), unfolding u (BC), or fan-in (PS(SHORT), RES-2)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms. **Varied:** cone shape and depth.
- **Ground truth:** `TRUE`. **Params:** `{"shape": "tree", "d": 3, "cone_size_s": 7, "unfolding_u": 7, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": 0.1, "variant": "determined", "P_q": 1.0, "bfs_index": 9, "up_depth": 3}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the blue tap is dripping and the red pump is working, then the silver door is open.
2. The pink clock is stopped.
3. If the black alarm is armed, then the gold box is full.
4. If the brown valve is shut, then the grey gate is locked.
5. If the silver pump is working and the green fan is running, then the red pump is working.
6. The orange flag is raised.
7. If the brown tap is dripping, then the orange tap is dripping.
8. The white valve is shut.
9. The blue bell is ringing.
10. If the silver gate is locked, then the silver door is open.
11. The green tap is dripping.
12. The orange gate is locked.
13. The gold fan is running.
14. The pink tap is dripping.
15. If the black pump is working, then the red alarm is armed.
16. If the grey flag is raised and the pink clock is stopped, then the silver pump is working.
17. If the gold fan is running, then the grey alarm is armed.
18. If the blue bell is ringing and the green tap is dripping, then the red lamp is on.
19. If the pink box is full and the red lamp is on, then the blue tap is dripping.
20. If the pink tap is dripping, then the silver box is full.
21. The grey flag is raised.
22. If the silver tap is dripping, then the purple lamp is on.
23. If the brown clock is stopped, then the brown box is full.
24. If the pink tap is dripping and the gold fan is running, then the pink box is full.
25. If the red box is full, then the gold lamp is on.
26. If the orange gate is locked and the orange flag is raised, then the green fan is running.
27. If the red tap is dripping and the silver flag is raised, then the white tap is dripping.
28. If the black tap is dripping, then the green clock is stopped.

Question: Is it true that the silver door is open?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-4` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `UP-inf` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-PASS-1` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(RECENT,12)` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,12)` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(SHORT,2)` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BC-10` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `DROP-CONJUNCT` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | tree(d=3) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-budget-8` | UNDETERMINED | tree(d=3) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.70, else UNDETERMINED | tree(d=3) determined: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.63, else UNDETERMINED | tree(d=3) determined: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | tree(d=3) determined: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | tree(d=3) determined: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `FC-budget-8`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-PASS-1`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `UP-4`, `UP-inf`

### E1-d · chain(d=7) determined

- **Tests:** Does accuracy depend on derivation depth d alone (UP-k), or on cone size s (NOISY-EXACT, FC-budget), unfolding u (BC), or fan-in (PS(SHORT), RES-2)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms. **Varied:** cone shape and depth.
- **Ground truth:** `TRUE`. **Params:** `{"shape": "chain", "d": 7, "cone_size_s": 7, "unfolding_u": 7, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": 0.07, "variant": "determined", "P_q": 1.0, "bfs_index": 9, "up_depth": 7}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. The orange clock is stopped.
2. If the pink box is full, then the pink door is open.
3. If the silver box is full and the white bell is ringing, then the gold bell is ringing.
4. If the silver flag is raised, then the brown alarm is armed.
5. If the orange tap is dripping and the purple valve is shut, then the blue bell is ringing.
6. If the brown lamp is on, then the green clock is stopped.
7. If the black flag is raised and the red pump is working, then the blue gate is locked.
8. The pink bell is ringing.
9. If the gold box is full, then the purple lamp is on.
10. If the grey alarm is armed and the grey box is full, then the grey bell is ringing.
11. If the gold clock is stopped, then the grey fan is running.
12. If the green clock is stopped, then the silver flag is raised.
13. The gold clock is stopped.
14. The blue flag is raised.
15. If the green flag is raised and the pink gate is locked, then the gold alarm is armed.
16. The silver door is open.
17. If the grey gate is locked and the brown fan is running, then the blue valve is shut.
18. The brown bell is ringing.
19. If the pink box is full, then the brown lamp is on.
20. If the red clock is stopped, then the black pump is working.
21. If the brown alarm is armed, then the gold tap is dripping.
22. The grey tap is dripping.
23. If the purple door is open and the purple pump is working, then the black box is full.
24. The silver bell is ringing.
25. If the silver pump is working and the green gate is locked, then the gold pump is working.
26. If the gold clock is stopped, then the pink box is full.
27. If the gold tap is dripping, then the black pump is working.
28. The green pump is working.

Question: Is it true that the black pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | chain(d=7) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-4` | UNDETERMINED | chain(d=7) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-inf` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `RES-2 (3 rounds)` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | UNDETERMINED | chain(d=7) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(RECENT,12)` | UNDETERMINED | chain(d=7) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,12)` | UNDETERMINED | chain(d=7) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(SHORT,2)` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `DROP-CONJUNCT` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | chain(d=7) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | chain(d=7) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-budget-8` | UNDETERMINED | chain(d=7) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.70, else UNDETERMINED | chain(d=7) determined: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.78, else UNDETERMINED | chain(d=7) determined: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | chain(d=7) determined: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | chain(d=7) determined: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `FC-budget-8`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `UP-2`, `UP-4`, `UP-PASS-1`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-inf`

### E1-e · ladder(d=4) determined

- **Tests:** Does accuracy depend on derivation depth d alone (UP-k), or on cone size s (NOISY-EXACT, FC-budget), unfolding u (BC), or fan-in (PS(SHORT), RES-2)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms. **Varied:** cone shape and depth.
- **Ground truth:** `TRUE`. **Params:** `{"shape": "ladder", "d": 4, "cone_size_s": 7, "unfolding_u": 15, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": -0.06, "variant": "determined", "P_q": 1.0, "bfs_index": 9, "up_depth": 4}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the pink fan is running, then the green box is full.
2. The green pump is working.
3. The white alarm is armed.
4. If the blue gate is locked and the orange flag is raised, then the silver tap is dripping.
5. If the gold valve is shut and the grey tap is dripping, then the silver alarm is armed.
6. If the gold door is open, then the orange pump is working.
7. The orange flag is raised.
8. If the black pump is working, then the grey lamp is on.
9. The silver clock is stopped.
10. If the blue clock is stopped, then the grey door is open.
11. The brown alarm is armed.
12. If the blue tap is dripping, then the pink gate is locked.
13. If the purple valve is shut and the silver alarm is armed, then the purple gate is locked.
14. The gold box is full.
15. If the brown flag is raised, then the white pump is working.
16. The grey clock is stopped.
17. If the grey tap is dripping and the gold valve is shut, then the purple valve is shut.
18. The blue gate is locked.
19. If the blue gate is locked, then the purple tap is dripping.
20. If the gold bell is ringing, then the green door is open.
21. If the orange valve is shut, then the purple gate is locked.
22. The white clock is stopped.
23. If the silver tap is dripping and the brown door is open, then the gold valve is shut.
24. If the orange flag is raised and the blue gate is locked, then the brown door is open.
25. If the orange flag is raised, then the orange alarm is armed.
26. If the silver box is full, then the purple clock is stopped.
27. If the silver flag is raised and the white door is open, then the grey alarm is armed.
28. If the brown door is open and the silver tap is dripping, then the grey tap is dripping.

Question: Is it true that the purple gate is locked?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-4` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `UP-inf` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-PASS-1` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(RECENT,12)` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,12)` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(SHORT,2)` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BC-10` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `DROP-CONJUNCT` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | ladder(d=4) determined: >= 85% of responses 'TRUE' (correct). |
| `FC-budget-8` | UNDETERMINED | ladder(d=4) determined: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.70, else UNDETERMINED | ladder(d=4) determined: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.76, else UNDETERMINED | ladder(d=4) determined: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | ladder(d=4) determined: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | ladder(d=4) determined: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `FC-budget-8`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-PASS-1`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `UP-4`, `UP-inf`

### E1-f · chain(d=3) catch-reversed

- **Tests:** Catch sibling: is the model sound (UNDETERMINED) or does it commit like a restriction (B4) or a cue (A)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms; same skeleton and names as its determined sibling. **Varied:** one edit (reversed).
- **Ground truth:** `UNDETERMINED`. **Params:** `{"shape": "chain", "d": 3, "cone_size_s": 3, "unfolding_u": 3, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": 0.0, "variant": "reversed", "P_q": 0.8, "bfs_index": null, "up_depth": null}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the green fan is running, then the blue door is open.
2. If the green fan is running, then the gold tap is dripping.
3. If the red bell is ringing and the green clock is stopped, then the purple flag is raised.
4. If the purple valve is shut and the silver box is full, then the black flag is raised.
5. If the green alarm is armed, then the white pump is working.
6. If the red fan is running and the orange alarm is armed, then the pink lamp is on.
7. If the gold valve is shut and the brown gate is locked, then the green valve is shut.
8. If the gold pump is working, then the purple fan is running.
9. The silver alarm is armed.
10. The white gate is locked.
11. If the white flag is raised, then the gold tap is dripping.
12. The purple tap is dripping.
13. If the white flag is raised, then the gold flag is raised.
14. The purple box is full.
15. The purple clock is stopped.
16. If the grey bell is ringing, then the white lamp is on.
17. If the gold fan is running and the silver bell is ringing, then the black lamp is on.
18. If the black alarm is armed and the blue clock is stopped, then the blue flag is raised.
19. The purple alarm is armed.
20. If the grey flag is raised, then the orange clock is stopped.
21. If the gold tap is dripping, then the orange pump is working.
22. If the pink flag is raised, then the blue lamp is on.
23. If the purple gate is locked, then the gold flag is raised.
24. If the blue fan is running and the green pump is working, then the orange door is open.
25. The grey valve is shut.
26. If the brown tap is dripping and the gold box is full, then the silver door is open.
27. The grey fan is running.
28. The green fan is running.

Question: Is it true that the gold flag is raised?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-4` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-inf` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-PASS-1` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(RECENT,12)` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(FIRST,12)` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(SHORT,2)` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | TRUE | chain(d=3) catch-reversed: commission 'TRUE' in >= 50% of responses. |
| `DROP-CONJUNCT` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `CLOSED-WORLD` | FALSE | chain(d=3) catch-reversed: commission 'FALSE' in >= 50% of responses. |
| `FIRST` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `FREQ` | TRUE | chain(d=3) catch-reversed: commission 'TRUE' in >= 50% of responses. |
| `NONE` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-budget-8` | UNDETERMINED | chain(d=3) catch-reversed: >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | chain(d=3) catch-reversed: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | UNDETERMINED (a lost premise cannot create a derivation) | chain(d=3) catch-reversed: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 0.51, FALSE w.p. 0.01, else UNDETERMINED | chain(d=3) catch-reversed: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | chain(d=3) catch-reversed: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `FREQ`

### E1-g · chain(d=3) catch-negfact

- **Tests:** Catch sibling: is the model sound (UNDETERMINED) or does it commit like a restriction (B4) or a cue (A)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms; same skeleton and names as its determined sibling. **Varied:** one edit (negfact).
- **Ground truth:** `UNDETERMINED`. **Params:** `{"shape": "chain", "d": 3, "cone_size_s": 3, "unfolding_u": 3, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": 0.0, "variant": "negfact", "P_q": 0.833, "bfs_index": null, "up_depth": null}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the green fan is running, then the blue door is open.
2. If the green fan is running, then the gold tap is dripping.
3. If the red bell is ringing and the green clock is stopped, then the purple flag is raised.
4. If the purple valve is shut and the silver box is full, then the black flag is raised.
5. If the green alarm is armed, then the white pump is working.
6. If the red fan is running and the orange alarm is armed, then the pink lamp is on.
7. If the gold valve is shut and the brown gate is locked, then the green valve is shut.
8. If the gold pump is working, then the purple fan is running.
9. The silver alarm is armed.
10. The white gate is locked.
11. If the gold tap is dripping, then the white flag is raised.
12. The purple tap is dripping.
13. If the white flag is raised, then the gold flag is raised.
14. The purple box is full.
15. The purple clock is stopped.
16. If the grey bell is ringing, then the white lamp is on.
17. If the gold fan is running and the silver bell is ringing, then the black lamp is on.
18. If the black alarm is armed and the blue clock is stopped, then the blue flag is raised.
19. The purple alarm is armed.
20. If the grey flag is raised, then the orange clock is stopped.
21. If the gold tap is dripping, then the orange pump is working.
22. If the pink flag is raised, then the blue lamp is on.
23. If the purple gate is locked, then the gold flag is raised.
24. If the blue fan is running and the green pump is working, then the orange door is open.
25. The grey valve is shut.
26. If the brown tap is dripping and the gold box is full, then the silver door is open.
27. The grey fan is running.
28. The green fan is not running.

Question: Is it true that the gold flag is raised?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-4` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-inf` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-PASS-1` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(RECENT,12)` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(FIRST,12)` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(SHORT,2)` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | FALSE | chain(d=3) catch-negfact: commission 'FALSE' in >= 50% of responses. |
| `DROP-CONJUNCT` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `CLOSED-WORLD` | FALSE | chain(d=3) catch-negfact: commission 'FALSE' in >= 50% of responses. |
| `FIRST` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `FREQ` | TRUE | chain(d=3) catch-negfact: commission 'TRUE' in >= 50% of responses. |
| `NONE` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-budget-8` | UNDETERMINED | chain(d=3) catch-negfact: >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | chain(d=3) catch-negfact: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | UNDETERMINED (a lost premise cannot create a derivation) | chain(d=3) catch-negfact: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 0.58, FALSE w.p. 0.00, else UNDETERMINED | chain(d=3) catch-negfact: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | chain(d=3) catch-negfact: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `FALSE` → against `BC-10`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `FREQ`

### E1-h · tree(d=3) catch-missing

- **Tests:** Catch sibling: is the model sound (UNDETERMINED) or does it commit like a restriction (B4) or a cue (A)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms; same skeleton and names as its determined sibling. **Varied:** one edit (missing).
- **Ground truth:** `UNDETERMINED`. **Params:** `{"shape": "tree", "d": 3, "cone_size_s": 7, "unfolding_u": 7, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": 0.1, "variant": "missing", "P_q": 0.889, "bfs_index": null, "up_depth": null}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the blue tap is dripping and the red pump is working, then the silver door is open.
2. The pink clock is stopped.
3. If the black alarm is armed, then the gold box is full.
4. If the brown valve is shut, then the grey gate is locked.
5. If the silver pump is working and the green fan is running, then the red pump is working.
6. The orange flag is raised.
7. If the brown tap is dripping, then the orange tap is dripping.
8. The white valve is shut.
9. The blue bell is ringing.
10. If the silver gate is locked, then the silver door is open.
11. The green tap is dripping.
12. The orange gate is locked.
13. The gold fan is running.
14. The pink tap is dripping.
15. If the black pump is working, then the red alarm is armed.
16. If the grey flag is raised and the pink clock is stopped, then the silver pump is working.
17. If the gold fan is running, then the grey alarm is armed.
18. If the blue bell is ringing and the green tap is dripping, then the red lamp is on.
19. If the pink box is full and the red lamp is on, then the blue tap is dripping.
20. If the pink tap is dripping, then the silver box is full.
21. The grey flag is raised.
22. If the silver tap is dripping, then the purple lamp is on.
23. If the brown clock is stopped, then the brown box is full.
24. If the pink tap is dripping and the grey bell is ringing, then the pink box is full.
25. If the red box is full, then the gold lamp is on.
26. If the orange gate is locked and the orange flag is raised, then the green fan is running.
27. If the red tap is dripping and the silver flag is raised, then the white tap is dripping.
28. If the black tap is dripping, then the green clock is stopped.

Question: Is it true that the silver door is open?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-4` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-inf` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-PASS-1` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(RECENT,12)` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(FIRST,12)` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(SHORT,2)` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `DROP-CONJUNCT` | TRUE | tree(d=3) catch-missing: commission 'TRUE' in >= 50% of responses. |
| `CLOSED-WORLD` | FALSE | tree(d=3) catch-missing: commission 'FALSE' in >= 50% of responses. |
| `FIRST` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `FREQ` | TRUE | tree(d=3) catch-missing: commission 'TRUE' in >= 50% of responses. |
| `NONE` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-budget-8` | UNDETERMINED | tree(d=3) catch-missing: >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | tree(d=3) catch-missing: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | UNDETERMINED (a lost premise cannot create a derivation) | tree(d=3) catch-missing: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 0.70, FALSE w.p. 0.00, else UNDETERMINED | tree(d=3) catch-missing: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | tree(d=3) catch-missing: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `CLOSED-WORLD`, `DROP-CONJUNCT`, `FREQ`

### E1-i · chain(d=3) determined bare

- **Tests:** Does accuracy depend on derivation depth d alone (UP-k), or on cone size s (NOISY-EXACT, FC-budget), unfolding u (BC), or fan-in (PS(SHORT), RES-2)?
- **Controlled:** premise-type quota, N, fan-out, q mentioned twice with matched polarity, |tau_proof| <= 0.15, neutral atoms; same skeleton and names as its determined sibling. **Varied:** rendering (bare logic).
- **Ground truth:** `TRUE`. **Params:** `{"shape": "chain", "d": 3, "cone_size_s": 3, "unfolding_u": 3, "N": 28, "quota": "9 facts/11 one-antecedent/8 AND-rules", "fanout": 2, "tau_proof": 0.0, "variant": "bare", "P_q": 1.0, "bfs_index": 5, "up_depth": 3}`

```text
Below are some premises about propositions P1, P2, .... Assume they are all true and that nothing else is known.

Premises:
1. If P1, then P45.
2. If P1, then P2.
3. If P36 and P37, then P38.
4. If P29 and P30, then P31.
5. If P10, then P11.
6. If P42 and P43, then P44.
7. If P26 and P27, then P28.
8. If P12, then P14.
9. P3 is true.
10. P47 is true.
11. If P2, then P13.
12. P48 is true.
13. If P13, then P24.
14. P6 is true.
15. P49 is true.
16. If P17, then P18.
17. If P19 and P20, then P21.
18. If P32 and P33, then P34.
19. P5 is true.
20. If P8, then P9.
21. If P2, then P46.
22. If P15, then P16.
23. If P35, then P24.
24. If P22 and P23, then P25.
25. P4 is true.
26. If P39 and P40, then P41.
27. P7 is true.
28. P1 is true.

Question: Is P24 true?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-2` | UNDETERMINED | chain(d=3) determined bare: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-4` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `UP-inf` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `RES-2 (3 rounds)` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `PS(RECENT,12)` | UNDETERMINED | chain(d=3) determined bare: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,12)` | UNDETERMINED | chain(d=3) determined bare: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(SHORT,2)` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `DROP-CONJUNCT` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | chain(d=3) determined bare: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `FC-budget-8` | TRUE | chain(d=3) determined bare: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | chain(d=3) determined bare: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.89, else UNDETERMINED | chain(d=3) determined bare: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | chain(d=3) determined bare: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | chain(d=3) determined bare: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `UP-2`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `PS(FIRST,12)`, `PS(RECENT,12)`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-2`, `UP-4`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DROP-CONJUNCT`, `EXACT`, `FC-budget-8`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `PS(SHORT,2)`, `RES-2 (3 rounds)`, `UP-4`, `UP-PASS-1`, `UP-inf`

### E1 discrimination table (entailment)

Each row is one theory's predicted answer pattern across the set (items in order E1-a, E1-b, E1-c, E1-d, E1-e, E1-f, E1-g, E1-h, E1-i). The third column gives the **log₁₀ likelihood ratio** in favour of the row's theories over each other theory, if the pattern is observed once per item (lapse ε = 0.1, 3 outcome categories, 1.26 per differing item). With r samples per item and a cell of n items, multiply by about r·n/(items in set). A mixed observation moves weight in proportion. It is not a rule-out.

| Observed pattern | Favours | log₁₀ LR vs each other theory | Not separable here (see) |
|---|---|---|---|
| T / T / U / U / U / U / U / U / T | `FC-budget-8` | `FREQ` +7.5, `CLOSED-WORLD` +7.5, `BICONDITIONAL` +6.3, `DROP-CONJUNCT` +5.0, `UP-inf` +3.8, `UP-2` +3.8, `PS(RECENT,12)` +3.8, `PS(FIRST,12)` +3.8, `NONE` +3.8, `FIRST` +3.8, `FC-inf (MP only)` +3.8, `EXACT` +3.8, `UP-4` +2.5, `RES-2 (3 rounds)` +2.5, `PS(SHORT,2)` +2.5, `BC-10` +2.5, `UP-PASS-1` +1.3 |  |

**Stochastic nulls in this set** (weight bounded by cell-level rates, not by single items):

- `NOISY-EXACT(eps=0.05)`: chain(d=3) determined: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `PERCEPTION-NOISE(rho=0.03)`: chain(d=3) determined: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `SAMPLE-3`: chain(d=3) determined: depth-invariant; commission on catches = P(q)^3 +/- 0.08. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `RANDOM`: chain(d=3) determined: each answer 33% +/- 8%. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.

## E2 — Omission vs commission; case-split ladder

- **Target:** UP-inf / RES-w (B1, sound). **Nearest competitors:** DPLL-b (D, case analysis); ETR / BICONDITIONAL / CLOSED-WORLD / FIRST (B4); SAMPLE-3 (H, probability-driven).

**(c) CoT predictions for this set** (pre-registered; scored by the L0 parser and the validated L1 codes, doc §2.4):

| Theory | Predicted trace features |
|---|---|
| `UP-inf` | Depth-ordered assertions to the fixpoint (fan-out literals included); reaches the query iff it is propagation-derivable; no case splits. |
| `UP-REFUTE-inf` | 'Suppose not Q' then propagates backwards (contrapositives) until a premise is violated; no explicit case branches. |
| `FC-inf (MP only)` | As UP-inf; every step cites a conditional in its written direction; no contrapositive ('since not B, not A') or disjunctive-syllogism steps. |
| `RES-2 (3 rounds)` | States composed conditionals or derived disjunctions ('so if A then C', 'so A or C') before applying them; no case branches. |
| `BC-10` | Starts from the query and states sub-goals ('to show X we need Y') before confirming facts; asserts no fan-out literals; gives up after about 10 sub-goals. |
| `BICONDITIONAL` | Uses some conditional backwards (from its consequent to its antecedent) or from a false antecedent to a false consequent. |
| `CLOSED-WORLD` | Concludes 'not X' because X was not derived. |
| `FIRST` | Treats an 'A or B' premise as asserting A. |
| `FREQ` | No derivation connecting facts to the query; justifies the answer by how the query is mentioned. |
| `NONE` | No derivation; says at once that the premises do not settle it. |
| `EXACT` | A complete derivation of the query, or a demonstration that both values are consistent. |
| `NOISY-EXACT(eps=0.05)` | Depth-ordered derivation in which one cone literal is skipped or one rule misapplied; the error is visible as a gap or an unjustified step. |
| `SAMPLE-3` | Tries a few concrete truth assignments and checks them against the premises. |
| `RANDOM` | No relation between the trace and the answer. |
| `DPLL-b` | Explicit case analysis: 'Case 1: X ... Case 2: not X ... in both cases Q', propagation inside each branch; nesting depth >= b* when it succeeds. |
| `RES-w (w=2..3)` | States composed conditionals or derived disjunctions ('so if A then C', 'so A or C') before applying them; no case branches. |
| `ETR (PyETR)` | Lists possibilities / alternatives for each premise and merges them; may treat an 'or else' alternative as settled once one part matches. |

### E2-a · T2 2-way dilemma (b*=0: reductio suffices; w*=2)

- **Tests:** Does the model case-split (DPLL / RES-2 / exact) or only propagate (UP-inf: UNDETERMINED on both)?
- **Controlled:** premise count, forms, positions, atom strings. **Varied:** one consequent atom (C -> D) in premise 3.
- **Ground truth:** `TRUE`. **Params:** `{"b_star": 0, "w_star": 2, "P_q": 1.0, "up_answer": "UNDETERMINED"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. The red gate is locked, or the brown pump is working (or both).
2. If the red gate is locked, then the blue fan is running.
3. If the brown pump is working, then the blue fan is running.
4. The silver clock is stopped.
5. The green lamp is on.

Question: Is it true that the blue fan is running?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | T2 2-way dilemma (b*=0: reductio suffices; w*=2): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-REFUTE-inf` | TRUE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T2 2-way dilemma (b*=0: reductio suffices; w*=2): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `RES-2 (3 rounds)` | TRUE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): >= 85% of responses 'TRUE' (correct). |
| `BC-10` | UNDETERMINED | T2 2-way dilemma (b*=0: reductio suffices; w*=2): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | TRUE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | FALSE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): commission 'FALSE' in >= 50% of responses. |
| `FIRST` | TRUE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | T2 2-way dilemma (b*=0: reductio suffices; w*=2): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.95, else UNDETERMINED | T2 2-way dilemma (b*=0: reductio suffices; w*=2): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | T2 2-way dilemma (b*=0: reductio suffices; w*=2): depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T2 2-way dilemma (b*=0: reductio suffices; w*=2): each answer 33% +/- 8%. |
| `DPLL-b` | TRUE iff b >= 0 (b* = 0) | T2 2-way dilemma (b*=0: reductio suffices; w*=2): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | TRUE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | TRUE | T2 2-way dilemma (b*=0: reductio suffices; w*=2): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `CLOSED-WORLD`, `DPLL-b`, `FC-inf (MP only)`, `NONE`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FIRST`, `FREQ`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`

### E2-b · T2 sibling (one consequent changed)

- **Tests:** Does the model case-split (DPLL / RES-2 / exact) or only propagate (UP-inf: UNDETERMINED on both)?
- **Controlled:** premise count, forms, positions, atom strings. **Varied:** one consequent atom (C -> D) in premise 3.
- **Ground truth:** `UNDETERMINED`. **Params:** `{"b_star": null, "w_star": null, "P_q": 0.8, "up_answer": "UNDETERMINED"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. The red gate is locked, or the brown pump is working (or both).
2. If the red gate is locked, then the blue fan is running.
3. If the brown pump is working, then the purple gate is locked.
4. The silver clock is stopped.
5. The green lamp is on.

Question: Is it true that the blue fan is running?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | T2 sibling (one consequent changed): >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-REFUTE-inf` | UNDETERMINED | T2 sibling (one consequent changed): >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T2 sibling (one consequent changed): >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | T2 sibling (one consequent changed): >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | T2 sibling (one consequent changed): >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | UNDETERMINED | T2 sibling (one consequent changed): >= 85% of responses 'UNDETERMINED' (correct). |
| `CLOSED-WORLD` | FALSE | T2 sibling (one consequent changed): commission 'FALSE' in >= 50% of responses. |
| `FIRST` | TRUE | T2 sibling (one consequent changed): commission 'TRUE' in >= 50% of responses. |
| `FREQ` | TRUE | T2 sibling (one consequent changed): commission 'TRUE' in >= 50% of responses. |
| `NONE` | UNDETERMINED | T2 sibling (one consequent changed): >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | T2 sibling (one consequent changed): >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | T2 sibling (one consequent changed): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 0.51, FALSE w.p. 0.01, else UNDETERMINED | T2 sibling (one consequent changed): depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T2 sibling (one consequent changed): each answer 33% +/- 8%. |
| `DPLL-b` | UNDETERMINED | T2 sibling (one consequent changed): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | UNDETERMINED | T2 sibling (one consequent changed): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | UNDETERMINED | T2 sibling (one consequent changed): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `CLOSED-WORLD`, `FIRST`, `FREQ`

### E2-c · T2 case-split b*=1, w*=2 (base)

- **Tests:** Nested case analysis: UP-inf and RES-w (small w) omit; DPLL with b >= 2 or exact succeed.
- **Controlled:** random 2/3-clause theory over 6 atoms, found by search; UP-inf does not derive F. **Varied:** -.
- **Ground truth:** `TRUE`. **Params:** `{"b_star": 1, "w_star": 2, "P_q": 1.0, "up_answer": "UNDETERMINED"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. At least one of these is true: the red gate is locked, the brown pump is working, the blue fan is running.
2. If the blue fan is running, then the red gate is locked or the brown pump is working (or both).
3. If the brown pump is working, then the red gate is locked or the blue fan is running (or both).
4. If the brown pump is working and the blue fan is running, then the red gate is locked.
5. If the red gate is locked, then the purple gate is locked.
6. If the purple gate is locked, then the white alarm is armed.
7. The silver clock is stopped.
8. The green lamp is on.

Question: Is it true that the white alarm is armed?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | T2 case-split b*=1, w*=2 (base): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `UP-REFUTE-inf` | UNDETERMINED | T2 case-split b*=1, w*=2 (base): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `FC-inf (MP only)` | UNDETERMINED | T2 case-split b*=1, w*=2 (base): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `RES-2 (3 rounds)` | TRUE | T2 case-split b*=1, w*=2 (base): >= 85% of responses 'TRUE' (correct). |
| `BC-10` | UNDETERMINED | T2 case-split b*=1, w*=2 (base): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | TRUE | T2 case-split b*=1, w*=2 (base): >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | FALSE | T2 case-split b*=1, w*=2 (base): commission 'FALSE' in >= 50% of responses. |
| `FIRST` | TRUE | T2 case-split b*=1, w*=2 (base): >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | T2 case-split b*=1, w*=2 (base): >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | T2 case-split b*=1, w*=2 (base): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | T2 case-split b*=1, w*=2 (base): >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.95, else UNDETERMINED | T2 case-split b*=1, w*=2 (base): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | T2 case-split b*=1, w*=2 (base): depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T2 case-split b*=1, w*=2 (base): each answer 33% +/- 8%. |
| `DPLL-b` | TRUE iff b >= 1 (b* = 1) | T2 case-split b*=1, w*=2 (base): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | TRUE | T2 case-split b*=1, w*=2 (base): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | TRUE | T2 case-split b*=1, w*=2 (base): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `CLOSED-WORLD`, `DPLL-b`, `FC-inf (MP only)`, `NONE`, `UP-REFUTE-inf`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FIRST`, `FREQ`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`

### E2-d · T2 sibling (one literal flipped)

- **Tests:** Type-G pair for UP-inf: g flips, UP-inf stays UNDETERMINED.
- **Controlled:** all other premises identical. **Varied:** polarity of one literal in premise 4.
- **Ground truth:** `UNDETERMINED`. **Params:** `{"b_star": null, "w_star": null, "P_q": 0.833, "up_answer": "UNDETERMINED"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. At least one of these is true: the red gate is locked, the brown pump is working, the blue fan is running.
2. If the blue fan is running, then the red gate is locked or the brown pump is working (or both).
3. If the brown pump is working, then the red gate is locked or the blue fan is running (or both).
4. It is not the case that the red gate is locked and the brown pump is working and the blue fan is running are all true.
5. If the red gate is locked, then the purple gate is locked.
6. If the purple gate is locked, then the white alarm is armed.
7. The silver clock is stopped.
8. The green lamp is on.

Question: Is it true that the white alarm is armed?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-REFUTE-inf` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `CLOSED-WORLD` | FALSE | T2 sibling (one literal flipped): commission 'FALSE' in >= 50% of responses. |
| `FIRST` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `FREQ` | TRUE | T2 sibling (one literal flipped): commission 'TRUE' in >= 50% of responses. |
| `NONE` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | T2 sibling (one literal flipped): >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | T2 sibling (one literal flipped): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 0.58, FALSE w.p. 0.00, else UNDETERMINED | T2 sibling (one literal flipped): depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T2 sibling (one literal flipped): each answer 33% +/- 8%. |
| `DPLL-b` | UNDETERMINED | T2 sibling (one literal flipped): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | UNDETERMINED | T2 sibling (one literal flipped): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | TRUE | T2 sibling (one literal flipped): >= 85% 'TRUE' |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `CLOSED-WORLD`, `ETR (PyETR)`, `FREQ`

### E2-e · T3 illusory (ETR commits)

- **Tests:** Illusory inference: does the model commit like ETR/MM (B4) where B1 stays sound?
- **Controlled:** premise 1 and padding identical. **Varied:** premise 2 (K -> not A).
- **Ground truth:** `UNDETERMINED`. **Params:** `{"b_star": null, "w_star": null, "P_q": 0.75, "up_answer": "UNDETERMINED"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. Either the brown pump is working and the red gate is locked, or else the blue fan is running and the purple gate is locked (but not both).
2. The red gate is locked.
3. The green pump is working.
4. The white alarm is armed.

Question: Is it true that the brown pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-REFUTE-inf` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `CLOSED-WORLD` | FALSE | T3 illusory (ETR commits): commission 'FALSE' in >= 50% of responses. |
| `FIRST` | TRUE (reads the first alternative as given) | T3 illusory (ETR commits): commission 'TRUE (reads the first alternative as given)' in >= 50% of responses. |
| `FREQ` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `NONE` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | T3 illusory (ETR commits): >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | T3 illusory (ETR commits): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 0.42, FALSE w.p. 0.02, else UNDETERMINED | T3 illusory (ETR commits): depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T3 illusory (ETR commits): each answer 33% +/- 8%. |
| `DPLL-b` | UNDETERMINED | T3 illusory (ETR commits): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | UNDETERMINED | T3 illusory (ETR commits): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | TRUE | T3 illusory (ETR commits): >= 85% 'TRUE' |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `CLOSED-WORLD`, `ETR (PyETR)`, `FIRST`

### E2-f · T3 control (conclusion follows)

- **Tests:** Illusory inference: does the model commit like ETR/MM (B4) where B1 stays sound?
- **Controlled:** premise 1 and padding identical. **Varied:** premise 2 (K -> not A).
- **Ground truth:** `TRUE`. **Params:** `{"b_star": 0, "w_star": 0, "P_q": 1.0, "up_answer": "TRUE"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. Either the brown pump is working and the red gate is locked, or else the blue fan is running and the purple gate is locked (but not both).
2. The purple gate is not locked.
3. The green pump is working.
4. The white alarm is armed.

Question: Is it true that the brown pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | T3 control (conclusion follows): >= 85% of responses 'TRUE' (correct). |
| `UP-REFUTE-inf` | TRUE | T3 control (conclusion follows): >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T3 control (conclusion follows): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `RES-2 (3 rounds)` | TRUE | T3 control (conclusion follows): >= 85% of responses 'TRUE' (correct). |
| `BC-10` | UNDETERMINED | T3 control (conclusion follows): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | TRUE | T3 control (conclusion follows): >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | T3 control (conclusion follows): >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE (reads the first alternative as given) | T3 control (conclusion follows): commission 'TRUE (reads the first alternative as given)' in >= 50% of responses. |
| `FREQ` | UNDETERMINED | T3 control (conclusion follows): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `NONE` | UNDETERMINED | T3 control (conclusion follows): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | T3 control (conclusion follows): >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.95, else UNDETERMINED | T3 control (conclusion follows): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | T3 control (conclusion follows): depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T3 control (conclusion follows): each answer 33% +/- 8%. |
| `DPLL-b` | TRUE iff b >= 0 (b* = 0) | T3 control (conclusion follows): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | TRUE | T3 control (conclusion follows): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | TRUE | T3 control (conclusion follows): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `DPLL-b`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FIRST`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`

### E2-g · T4 AC bait

- **Tests:** Converse/inverse baits vs valid MP/MT: commission (BICONDITIONAL, CLOSED-WORLD) vs omission of MT (FC, MM-initial).
- **Controlled:** conditional, padding, positions. **Varied:** the categorical premise and the queried atom.
- **Ground truth:** `UNDETERMINED`. **Params:** `{"b_star": null, "w_star": null, "P_q": 0.5, "up_answer": "UNDETERMINED"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the red gate is locked, then the brown pump is working.
2. The brown pump is working.
3. The silver clock is stopped.
4. The green lamp is on.

Question: Is it true that the red gate is locked?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-REFUTE-inf` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | TRUE | T4 AC bait: commission 'TRUE' in >= 50% of responses. |
| `CLOSED-WORLD` | FALSE | T4 AC bait: commission 'FALSE' in >= 50% of responses. |
| `FIRST` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `FREQ` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `NONE` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | T4 AC bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | T4 AC bait: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 0.12, FALSE w.p. 0.12, else UNDETERMINED | T4 AC bait: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T4 AC bait: each answer 33% +/- 8%. |
| `DPLL-b` | UNDETERMINED | T4 AC bait: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | UNDETERMINED | T4 AC bait: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | UNDETERMINED | T4 AC bait: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`

### E2-h · T4 DA bait

- **Tests:** Converse/inverse baits vs valid MP/MT: commission (BICONDITIONAL, CLOSED-WORLD) vs omission of MT (FC, MM-initial).
- **Controlled:** conditional, padding, positions. **Varied:** the categorical premise and the queried atom.
- **Ground truth:** `UNDETERMINED`. **Params:** `{"b_star": null, "w_star": null, "P_q": 0.5, "up_answer": "UNDETERMINED"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the red gate is locked, then the brown pump is working.
2. The red gate is not locked.
3. The silver clock is stopped.
4. The green lamp is on.

Question: Is it true that the brown pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | T4 DA bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-REFUTE-inf` | UNDETERMINED | T4 DA bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T4 DA bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | T4 DA bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | T4 DA bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | FALSE | T4 DA bait: commission 'FALSE' in >= 50% of responses. |
| `CLOSED-WORLD` | FALSE | T4 DA bait: commission 'FALSE' in >= 50% of responses. |
| `FIRST` | UNDETERMINED | T4 DA bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `FREQ` | TRUE | T4 DA bait: commission 'TRUE' in >= 50% of responses. |
| `NONE` | UNDETERMINED | T4 DA bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | T4 DA bait: >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | T4 DA bait: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 0.12, FALSE w.p. 0.12, else UNDETERMINED | T4 DA bait: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T4 DA bait: each answer 33% +/- 8%. |
| `DPLL-b` | UNDETERMINED | T4 DA bait: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | UNDETERMINED | T4 DA bait: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | UNDETERMINED | T4 DA bait: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `FALSE` → against `BC-10`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `FREQ`

### E2-i · T4 MP

- **Tests:** Converse/inverse baits vs valid MP/MT: commission (BICONDITIONAL, CLOSED-WORLD) vs omission of MT (FC, MM-initial).
- **Controlled:** conditional, padding, positions. **Varied:** the categorical premise and the queried atom.
- **Ground truth:** `TRUE`. **Params:** `{"b_star": 0, "w_star": 0, "P_q": 1.0, "up_answer": "TRUE"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the red gate is locked, then the brown pump is working.
2. The red gate is locked.
3. The silver clock is stopped.
4. The green lamp is on.

Question: Is it true that the brown pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `UP-REFUTE-inf` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `RES-2 (3 rounds)` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | T4 MP: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | T4 MP: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.95, else UNDETERMINED | T4 MP: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | T4 MP: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T4 MP: each answer 33% +/- 8%. |
| `DPLL-b` | TRUE iff b >= 0 (b* = 0) | T4 MP: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | TRUE | T4 MP: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | TRUE | T4 MP: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `DPLL-b`, `NONE`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`

### E2-j · T4 MT

- **Tests:** Converse/inverse baits vs valid MP/MT: commission (BICONDITIONAL, CLOSED-WORLD) vs omission of MT (FC, MM-initial).
- **Controlled:** conditional, padding, positions. **Varied:** the categorical premise and the queried atom.
- **Ground truth:** `FALSE`. **Params:** `{"b_star": null, "w_star": 0, "P_q": 0.0, "up_answer": "FALSE"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the red gate is locked, then the brown pump is working.
2. The brown pump is not working.
3. The silver clock is stopped.
4. The green lamp is on.

Question: Is it true that the red gate is locked?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | FALSE | T4 MT: >= 85% of responses 'FALSE' (correct). |
| `UP-REFUTE-inf` | FALSE | T4 MT: >= 85% of responses 'FALSE' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T4 MT: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `RES-2 (3 rounds)` | FALSE | T4 MT: >= 85% of responses 'FALSE' (correct). |
| `BC-10` | UNDETERMINED | T4 MT: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | FALSE | T4 MT: >= 85% of responses 'FALSE' (correct). |
| `CLOSED-WORLD` | FALSE | T4 MT: >= 85% of responses 'FALSE' (correct). |
| `FIRST` | FALSE | T4 MT: >= 85% of responses 'FALSE' (correct). |
| `FREQ` | UNDETERMINED | T4 MT: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `NONE` | UNDETERMINED | T4 MT: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | FALSE | T4 MT: >= 85% of responses 'FALSE' (correct). |
| `NOISY-EXACT(eps=0.05)` | FALSE w.p. 0.95, else UNDETERMINED | T4 MT: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 0.00, FALSE w.p. 1.00, else UNDETERMINED | T4 MT: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T4 MT: each answer 33% +/- 8%. |
| `DPLL-b` | FALSE | T4 MT: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | FALSE | T4 MT: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | FALSE | T4 MT: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `FALSE` → against `BC-10`, `FC-inf (MP only)`, `FREQ`, `NONE`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FIRST`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`

### E2-k · T5 P(q)=0.75, g=U

- **Tests:** Probable-but-not-entailed: does commission rise with P(q) (BP / SAMPLE) or stay at zero (B1)?
- **Controlled:** rule, padding. **Varied:** premise 1 ('A or B' -> 'A'; a deletion edit).
- **Ground truth:** `UNDETERMINED`. **Params:** `{"b_star": null, "w_star": null, "P_q": 0.75, "up_answer": "UNDETERMINED"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. The red gate is locked, or the brown pump is working (or both).
2. If the red gate is locked, then the white pump is working.
3. The silver clock is stopped.
4. The green lamp is on.

Question: Is it true that the white pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | T5 P(q)=0.75, g=U: >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-REFUTE-inf` | UNDETERMINED | T5 P(q)=0.75, g=U: >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T5 P(q)=0.75, g=U: >= 85% of responses 'UNDETERMINED' (correct). |
| `RES-2 (3 rounds)` | UNDETERMINED | T5 P(q)=0.75, g=U: >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | T5 P(q)=0.75, g=U: >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | UNDETERMINED | T5 P(q)=0.75, g=U: >= 85% of responses 'UNDETERMINED' (correct). |
| `CLOSED-WORLD` | FALSE | T5 P(q)=0.75, g=U: commission 'FALSE' in >= 50% of responses. |
| `FIRST` | TRUE | T5 P(q)=0.75, g=U: commission 'TRUE' in >= 50% of responses. |
| `FREQ` | TRUE | T5 P(q)=0.75, g=U: commission 'TRUE' in >= 50% of responses. |
| `NONE` | UNDETERMINED | T5 P(q)=0.75, g=U: >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | T5 P(q)=0.75, g=U: >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | T5 P(q)=0.75, g=U: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 0.42, FALSE w.p. 0.02, else UNDETERMINED | T5 P(q)=0.75, g=U: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T5 P(q)=0.75, g=U: each answer 33% +/- 8%. |
| `DPLL-b` | UNDETERMINED | T5 P(q)=0.75, g=U: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | UNDETERMINED | T5 P(q)=0.75, g=U: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | UNDETERMINED | T5 P(q)=0.75, g=U: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `CLOSED-WORLD`, `FIRST`, `FREQ`

### E2-l · T5 sibling (entailed)

- **Tests:** Probable-but-not-entailed: does commission rise with P(q) (BP / SAMPLE) or stay at zero (B1)?
- **Controlled:** rule, padding. **Varied:** premise 1 ('A or B' -> 'A'; a deletion edit).
- **Ground truth:** `TRUE`. **Params:** `{"b_star": 0, "w_star": 0, "P_q": 1.0, "up_answer": "TRUE"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. The red gate is locked.
2. If the red gate is locked, then the white pump is working.
3. The silver clock is stopped.
4. The green lamp is on.

Question: Is it true that the white pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `UP-REFUTE-inf` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `RES-2 (3 rounds)` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `FIRST` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | T5 sibling (entailed): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | T5 sibling (entailed): >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.95, else UNDETERMINED | T5 sibling (entailed): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | T5 sibling (entailed): depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T5 sibling (entailed): each answer 33% +/- 8%. |
| `DPLL-b` | TRUE iff b >= 0 (b* = 0) | T5 sibling (entailed): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | TRUE | T5 sibling (entailed): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | TRUE | T5 sibling (entailed): accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `DPLL-b`, `NONE`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`

### E2-m · T6 disjunctive syllogism

- **Tests:** Rule-direction set R: UP fires DS; FC (conditionals only) does not.
- **Controlled:** padding. **Varied:** -.
- **Ground truth:** `TRUE`. **Params:** `{"b_star": 0, "w_star": 0, "P_q": 1.0, "up_answer": "TRUE"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. The red gate is locked, or the brown pump is working (or both).
2. The red gate is not locked.
3. The silver clock is stopped.
4. The green lamp is on.

Question: Is it true that the brown pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | T6 disjunctive syllogism: >= 85% of responses 'TRUE' (correct). |
| `UP-REFUTE-inf` | TRUE | T6 disjunctive syllogism: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | T6 disjunctive syllogism: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `RES-2 (3 rounds)` | TRUE | T6 disjunctive syllogism: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | UNDETERMINED | T6 disjunctive syllogism: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | TRUE | T6 disjunctive syllogism: >= 85% of responses 'TRUE' (correct). |
| `CLOSED-WORLD` | TRUE | T6 disjunctive syllogism: >= 85% of responses 'TRUE' (correct). |
| `FIRST` | UNDETERMINED (first-disjunct reading contradicts premise 2; implementation falls back) | T6 disjunctive syllogism: commission 'UNDETERMINED (first-disjunct reading contradicts premise 2; implementation falls back)' in >= 50% of responses. |
| `FREQ` | UNDETERMINED | T6 disjunctive syllogism: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `NONE` | UNDETERMINED | T6 disjunctive syllogism: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | T6 disjunctive syllogism: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.95, else UNDETERMINED | T6 disjunctive syllogism: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `SAMPLE-3` | TRUE w.p. 1.00, FALSE w.p. 0.00, else UNDETERMINED | T6 disjunctive syllogism: depth-invariant; commission on catches = P(q)^3 +/- 0.08. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | T6 disjunctive syllogism: each answer 33% +/- 8%. |
| `DPLL-b` | TRUE iff b >= 0 (b* = 0) | T6 disjunctive syllogism: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `RES-w (w=2..3)` | TRUE | T6 disjunctive syllogism: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |
| `ETR (PyETR)` | TRUE | T6 disjunctive syllogism: accuracy >= 85% iff b >= b*; failures UNDETERMINED with case-split traces |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `DPLL-b`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FC-inf (MP only)`, `FIRST`, `FREQ`, `NONE`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `CLOSED-WORLD`, `DPLL-b`, `ETR (PyETR)`, `EXACT`, `FIRST`, `RES-2 (3 rounds)`, `RES-w (w=2..3)`, `UP-REFUTE-inf`, `UP-inf`

### E2 discrimination table (entailment)

Each row is one theory's predicted answer pattern across the set (items in order E2-a, E2-b, E2-c, E2-d, E2-e, E2-f, E2-g, E2-h, E2-i, E2-j, E2-k, E2-l, E2-m). The third column gives the **log₁₀ likelihood ratio** in favour of the row's theories over each other theory, if the pattern is observed once per item (lapse ε = 0.1, 3 outcome categories, 1.26 per differing item). With r samples per item and a cell of n items, multiply by about r·n/(items in set). A mixed observation moves weight in proportion. It is not a rule-out.

| Observed pattern | Favours | log₁₀ LR vs each other theory | Not separable here (see) |
|---|---|---|---|
| T / U / T / T / T / T / U / U / T / F / U / T / T | `ETR (PyETR)` | `NONE` +11.3, `DPLL-b` +10.0, `CLOSED-WORLD` +10.0, `FREQ` +8.8, `FC-inf (MP only)` +8.8, `BC-10` +8.8, `FIRST` +7.5, `UP-inf` +5.0, `BICONDITIONAL` +5.0, `UP-REFUTE-inf` +3.8, `RES-w (w=2..3)` +2.5, `RES-2 (3 rounds)` +2.5, `EXACT` +2.5 |  |

**Stochastic nulls in this set** (weight bounded by cell-level rates, not by single items):

- `NOISY-EXACT(eps=0.05)`: T2 2-way dilemma (b*=0: reductio suffices; w*=2): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `SAMPLE-3`: T2 2-way dilemma (b*=0: reductio suffices; w*=2): depth-invariant; commission on catches = P(q)^3 +/- 0.08. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `RANDOM`: T2 2-way dilemma (b*=0: reductio suffices; w*=2): each answer 33% +/- 8%. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.

## E3 — Premise selection: position x proof order, phrasing, query position

- **Target:** PS(sel) (B1). **Nearest competitors:** UP-PASS-1 / C4 (order-driven); UP-inf (no selection); FC-inf / PS(TYPE).

**(c) CoT predictions for this set** (pre-registered; scored by the L0 parser and the validated L1 codes, doc §2.4):

| Theory | Predicted trace features |
|---|---|
| `UP-inf` | Depth-ordered assertions to the fixpoint (fan-out literals included); reaches the query iff it is propagation-derivable; no case splits. |
| `UP-PASS-1` | Reads premises in printed order once; asserts a literal only when its premise is read after its antecedent is known (tau_text >= 0.6). |
| `PS(RECENT,6)` | Never quotes or uses premises 1-6. |
| `PS(FIRST,6)` | Never quotes or uses premises 7-12. |
| `FC-inf (MP only)` | As UP-inf; every step cites a conditional in its written direction; no contrapositive ('since not B, not A') or disjunctive-syllogism steps. |
| `PS(TYPE:disjunction)` | Never uses the 'Either ... or ...' premise. |
| `BC-10` | Starts from the query and states sub-goals ('to show X we need Y') before confirming facts; asserts no fan-out literals; gives up after about 10 sub-goals. |
| `BICONDITIONAL` | Uses some conditional backwards (from its consequent to its antecedent) or from a false antecedent to a false consequent. |
| `FREQ` | No derivation connecting facts to the query; justifies the answer by how the query is mentioned. |
| `NONE` | No derivation; says at once that the premises do not settle it. |
| `EXACT` | A complete derivation of the query, or a demonstration that both values are consistent. |
| `NOISY-EXACT(eps=0.05)` | Depth-ordered derivation in which one cone literal is skipped or one rule misapplied; the error is visible as a gap or an unjustified step. |
| `PERCEPTION-NOISE(rho=0.03)` | A premise is misquoted or omitted when restated, and the derivation is correct relative to the misread premises. |
| `RANDOM` | No relation between the trace and the answer. |

### E3-a · P early, proof order

- **Tests:** Which premises does the model ignore: early (recency), late (primacy), disjunctions (type), or none (UP-inf)? Does order relative to the proof matter (UP-PASS / C4)?
- **Controlled:** same 12 premises and names in every cell; distractors keep their relative order. **Varied:** P early, proof order.
- **Ground truth:** `TRUE`. **Params:** `{"d": 3, "N": 12, "cone_positions": [1, 2, 4, 6], "proof_order": true, "variant": "position/order"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. The black box is full.
2. If the black box is full, then the grey flag is raised.
3. If the black door is open, then the orange alarm is armed.
4. If the grey flag is raised, then the red clock is stopped.
5. If the black box is full, then the white flag is raised.
6. If the red clock is stopped, then the orange alarm is armed.
7. The purple box is full.
8. The purple bell is ringing.
9. If the blue valve is shut, then the white alarm is armed.
10. If the brown box is full and the red fan is running, then the green lamp is on.
11. If the green gate is locked and the red flag is raised, then the gold flag is raised.
12. If the purple tap is dripping and the black tap is dripping, then the orange clock is stopped.

Question: Is it true that the orange alarm is armed?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `PS(RECENT,6)` | UNDETERMINED | P early, proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,6)` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `PS(TYPE:disjunction)` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | P early, proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | P early, proof order: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | P early, proof order: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.89, else UNDETERMINED | P early, proof order: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | P early, proof order: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `NONE`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `NONE`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `UP-PASS-1`, `UP-inf`

### E3-b · P early, reverse proof order

- **Tests:** Which premises does the model ignore: early (recency), late (primacy), disjunctions (type), or none (UP-inf)? Does order relative to the proof matter (UP-PASS / C4)?
- **Controlled:** same 12 premises and names in every cell; distractors keep their relative order. **Varied:** P early, reverse proof order.
- **Ground truth:** `TRUE`. **Params:** `{"d": 3, "N": 12, "cone_positions": [6, 4, 2, 1], "proof_order": false, "variant": "position/order"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the red clock is stopped, then the orange alarm is armed.
2. If the grey flag is raised, then the red clock is stopped.
3. If the black door is open, then the orange alarm is armed.
4. If the black box is full, then the grey flag is raised.
5. If the black box is full, then the white flag is raised.
6. The black box is full.
7. The purple box is full.
8. The purple bell is ringing.
9. If the blue valve is shut, then the white alarm is armed.
10. If the brown box is full and the red fan is running, then the green lamp is on.
11. If the green gate is locked and the red flag is raised, then the gold flag is raised.
12. If the purple tap is dripping and the black tap is dripping, then the orange clock is stopped.

Question: Is it true that the orange alarm is armed?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | P early, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | UNDETERMINED | P early, reverse proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(RECENT,6)` | UNDETERMINED | P early, reverse proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,6)` | TRUE | P early, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `FC-inf (MP only)` | TRUE | P early, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `PS(TYPE:disjunction)` | TRUE | P early, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | P early, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | P early, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | P early, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | P early, reverse proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | P early, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | P early, reverse proof order: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.89, else UNDETERMINED | P early, reverse proof order: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | P early, reverse proof order: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `NONE`, `UP-PASS-1`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `NONE`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `UP-inf`

### E3-c · P late, proof order

- **Tests:** Which premises does the model ignore: early (recency), late (primacy), disjunctions (type), or none (UP-inf)? Does order relative to the proof matter (UP-PASS / C4)?
- **Controlled:** same 12 premises and names in every cell; distractors keep their relative order. **Varied:** P late, proof order.
- **Ground truth:** `TRUE`. **Params:** `{"d": 3, "N": 12, "cone_positions": [7, 8, 10, 12], "proof_order": true, "variant": "position/order"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the black door is open, then the orange alarm is armed.
2. If the black box is full, then the white flag is raised.
3. The purple box is full.
4. The purple bell is ringing.
5. If the blue valve is shut, then the white alarm is armed.
6. If the brown box is full and the red fan is running, then the green lamp is on.
7. The black box is full.
8. If the black box is full, then the grey flag is raised.
9. If the green gate is locked and the red flag is raised, then the gold flag is raised.
10. If the grey flag is raised, then the red clock is stopped.
11. If the purple tap is dripping and the black tap is dripping, then the orange clock is stopped.
12. If the red clock is stopped, then the orange alarm is armed.

Question: Is it true that the orange alarm is armed?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `PS(RECENT,6)` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `PS(FIRST,6)` | UNDETERMINED | P late, proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `FC-inf (MP only)` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `PS(TYPE:disjunction)` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | P late, proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | P late, proof order: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | P late, proof order: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.89, else UNDETERMINED | P late, proof order: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | P late, proof order: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `NONE`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `NONE`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `UP-PASS-1`, `UP-inf`

### E3-d · P late, reverse proof order

- **Tests:** Which premises does the model ignore: early (recency), late (primacy), disjunctions (type), or none (UP-inf)? Does order relative to the proof matter (UP-PASS / C4)?
- **Controlled:** same 12 premises and names in every cell; distractors keep their relative order. **Varied:** P late, reverse proof order.
- **Ground truth:** `TRUE`. **Params:** `{"d": 3, "N": 12, "cone_positions": [12, 10, 8, 7], "proof_order": false, "variant": "position/order"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the black door is open, then the orange alarm is armed.
2. If the black box is full, then the white flag is raised.
3. The purple box is full.
4. The purple bell is ringing.
5. If the blue valve is shut, then the white alarm is armed.
6. If the brown box is full and the red fan is running, then the green lamp is on.
7. If the red clock is stopped, then the orange alarm is armed.
8. If the grey flag is raised, then the red clock is stopped.
9. If the green gate is locked and the red flag is raised, then the gold flag is raised.
10. If the black box is full, then the grey flag is raised.
11. If the purple tap is dripping and the black tap is dripping, then the orange clock is stopped.
12. The black box is full.

Question: Is it true that the orange alarm is armed?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | P late, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | UNDETERMINED | P late, reverse proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(RECENT,6)` | TRUE | P late, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `PS(FIRST,6)` | UNDETERMINED | P late, reverse proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `FC-inf (MP only)` | TRUE | P late, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `PS(TYPE:disjunction)` | TRUE | P late, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | P late, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | P late, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | P late, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | P late, reverse proof order: <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | P late, reverse proof order: >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | P late, reverse proof order: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.89, else UNDETERMINED | P late, reverse proof order: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | P late, reverse proof order: each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `NONE`, `UP-PASS-1`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `NONE`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `UP-inf`

### E3-e · O disjunctive phrasing of the middle link (late, proof order)

- **Tests:** Which premises does the model ignore: early (recency), late (primacy), disjunctions (type), or none (UP-inf)? Does order relative to the proof matter (UP-PASS / C4)?
- **Controlled:** same 12 premises and names in every cell; distractors keep their relative order. **Varied:** O disjunctive phrasing of the middle link (late, proof order).
- **Ground truth:** `TRUE`. **Params:** `{"d": 3, "N": 12, "cone_positions": [7, 8, 10, 12], "proof_order": true, "variant": "disj"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the black door is open, then the orange alarm is armed.
2. If the black box is full, then the white flag is raised.
3. The purple box is full.
4. The purple bell is ringing.
5. If the blue valve is shut, then the white alarm is armed.
6. If the brown box is full and the red fan is running, then the green lamp is on.
7. The black box is full.
8. If the black box is full, then the grey flag is raised.
9. If the green gate is locked and the red flag is raised, then the gold flag is raised.
10. Either it is not the case that the grey flag is raised, or the red clock is stopped.
11. If the purple tap is dripping and the black tap is dripping, then the orange clock is stopped.
12. If the red clock is stopped, then the orange alarm is armed.

Question: Is it true that the orange alarm is armed?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | O disjunctive phrasing of the middle link (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | TRUE | O disjunctive phrasing of the middle link (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `PS(RECENT,6)` | TRUE | O disjunctive phrasing of the middle link (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `PS(FIRST,6)` | UNDETERMINED | O disjunctive phrasing of the middle link (late, proof order): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `FC-inf (MP only)` | UNDETERMINED | O disjunctive phrasing of the middle link (late, proof order): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(TYPE:disjunction)` | UNDETERMINED | O disjunctive phrasing of the middle link (late, proof order): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BC-10` | UNDETERMINED | O disjunctive phrasing of the middle link (late, proof order): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `BICONDITIONAL` | TRUE | O disjunctive phrasing of the middle link (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | O disjunctive phrasing of the middle link (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | O disjunctive phrasing of the middle link (late, proof order): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | O disjunctive phrasing of the middle link (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | O disjunctive phrasing of the middle link (late, proof order): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.89, else UNDETERMINED | O disjunctive phrasing of the middle link (late, proof order): accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | O disjunctive phrasing of the middle link (late, proof order): each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `FC-inf (MP only)`, `NONE`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `NONE`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `EXACT`, `FREQ`, `UP-PASS-1`, `UP-inf`

### E3-f · Q query first (late, proof order)

- **Tests:** Which premises does the model ignore: early (recency), late (primacy), disjunctions (type), or none (UP-inf)? Does order relative to the proof matter (UP-PASS / C4)?
- **Controlled:** same 12 premises and names in every cell; distractors keep their relative order. **Varied:** Q query first (late, proof order).
- **Ground truth:** `TRUE`. **Params:** `{"d": 3, "N": 12, "cone_positions": [7, 8, 10, 12], "proof_order": true, "variant": "qfirst"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Question: Is it true that the orange alarm is armed?

Premises:
1. If the black door is open, then the orange alarm is armed.
2. If the black box is full, then the white flag is raised.
3. The purple box is full.
4. The purple bell is ringing.
5. If the blue valve is shut, then the white alarm is armed.
6. If the brown box is full and the red fan is running, then the green lamp is on.
7. The black box is full.
8. If the black box is full, then the grey flag is raised.
9. If the green gate is locked and the red flag is raised, then the gold flag is raised.
10. If the grey flag is raised, then the red clock is stopped.
11. If the purple tap is dripping and the black tap is dripping, then the orange clock is stopped.
12. If the red clock is stopped, then the orange alarm is armed.

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `PS(RECENT,6)` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `PS(FIRST,6)` | UNDETERMINED | Q query first (late, proof order): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `FC-inf (MP only)` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `PS(TYPE:disjunction)` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `BICONDITIONAL` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | Q query first (late, proof order): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | Q query first (late, proof order): >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | Q query first (late, proof order): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | TRUE w.p. 0.89, else UNDETERMINED | Q query first (late, proof order): accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | Q query first (late, proof order): each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `NONE`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `NONE`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `UP-PASS-1`, `UP-inf`

### E3-g · catch: reversed middle link (late, proof order)

- **Tests:** Which premises does the model ignore: early (recency), late (primacy), disjunctions (type), or none (UP-inf)? Does order relative to the proof matter (UP-PASS / C4)?
- **Controlled:** same 12 premises and names in every cell; distractors keep their relative order. **Varied:** catch: reversed middle link (late, proof order).
- **Ground truth:** `UNDETERMINED`. **Params:** `{"d": 3, "N": 12, "cone_positions": [7, 8, 10, 12], "proof_order": true, "variant": "catch"}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
1. If the black door is open, then the orange alarm is armed.
2. If the black box is full, then the white flag is raised.
3. The purple box is full.
4. The purple bell is ringing.
5. If the blue valve is shut, then the white alarm is armed.
6. If the brown box is full and the red fan is running, then the green lamp is on.
7. The black box is full.
8. If the black box is full, then the grey flag is raised.
9. If the green gate is locked and the red flag is raised, then the gold flag is raised.
10. If the red clock is stopped, then the grey flag is raised.
11. If the purple tap is dripping and the black tap is dripping, then the orange clock is stopped.
12. If the red clock is stopped, then the orange alarm is armed.

Question: Is it true that the orange alarm is armed?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `UP-PASS-1` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(RECENT,6)` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(FIRST,6)` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `FC-inf (MP only)` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `PS(TYPE:disjunction)` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `BC-10` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `BICONDITIONAL` | TRUE | catch: reversed middle link (late, proof order): commission 'TRUE' in >= 50% of responses. |
| `FREQ` | TRUE | catch: reversed middle link (late, proof order): commission 'TRUE' in >= 50% of responses. |
| `NONE` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `EXACT` | UNDETERMINED | catch: reversed middle link (late, proof order): >= 85% of responses 'UNDETERMINED' (correct). |
| `NOISY-EXACT(eps=0.05)` | UNDETERMINED (commission only by misapplication, rate eps_c) | catch: reversed middle link (late, proof order): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `PERCEPTION-NOISE(rho=0.03)` | UNDETERMINED (a lost premise cannot create a derivation) | catch: reversed middle link (late, proof order): accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | catch: reversed middle link (late, proof order): each answer 33% +/- 8%. |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `BC-10`, `EXACT`, `FC-inf (MP only)`, `NONE`, `UP-PASS-1`, `UP-inf`
- `FALSE` → against `BC-10`, `BICONDITIONAL`, `EXACT`, `FC-inf (MP only)`, `FREQ`, `NONE`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BICONDITIONAL`, `FREQ`

### E3 discrimination table (entailment)

Each row is one theory's predicted answer pattern across the set (items in order E3-a, E3-b, E3-c, E3-d, E3-e, E3-f, E3-g). The third column gives the **log₁₀ likelihood ratio** in favour of the row's theories over each other theory, if the pattern is observed once per item (lapse ε = 0.1, 3 outcome categories, 1.26 per differing item). With r samples per item and a cell of n items, multiply by about r·n/(items in set). A mixed observation moves weight in proportion. It is not a rule-out.

| Observed pattern | Favours | log₁₀ LR vs each other theory | Not separable here (see) |
|---|---|---|---|
| U / U / U / U / U / U / U | `NONE` | `FREQ` +8.8, `BICONDITIONAL` +8.8, `UP-inf` +7.5, `EXACT` +7.5, `PS(TYPE:disjunction)` +6.3, `FC-inf (MP only)` +6.3, `BC-10` +6.3, `UP-PASS-1` +5.0, `PS(RECENT,6)` +5.0, `PS(FIRST,6)` +2.5 |  |

**Stochastic nulls in this set** (weight bounded by cell-level rates, not by single items):

- `NOISY-EXACT(eps=0.05)`: P early, proof order: accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `PERCEPTION-NOISE(rho=0.03)`: P early, proof order: accuracy = 0.97^(cone premises) +/- 0.08; violations/omissions not tied to a fixed premise across samples. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `RANDOM`: P early, proof order: each answer 33% +/- 8%. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.

## E4 — Critical-constraint localisation on an odd wheel

- **Target:** DROP(sel) (B1). **Nearest competitors:** FIRST-FIT-cap / DSATUR-cap (C); MIN-CONFLICTS (F); PERCEPTION-NOISE.
- **Note:** W5 is small; the full study uses random 4-critical graphs n = 12-24 (doc §2.9).

**(c) CoT predictions for this set** (pre-registered; scored by the L0 parser and the validated L1 codes, doc §2.4):

| Theory | Predicted trace features |
|---|---|
| `EXACT` | Systematic search or a proof of impossibility (e.g. 'the rim is an odd cycle, so the hub needs a 4th slot'). |
| `DROP(LAST)` | The last-listed conflict is never mentioned or checked; any final check skips it. |
| `DROP(FIRST)` | The first-listed conflict is never mentioned or checked. |
| `DROP(LONG)` | The conflict whose two people are furthest apart in the people list is never checked. |
| `FIRST-FIT-cap` | Assigns people one by one in the listed order, lowest free slot; at the first person with no free slot, forces a slot and moves on. |
| `DSATUR-cap` | Chooses the most-constrained person next; forced conflict at the first saturated person. |
| `CYCLIC` | Slots assigned 1,2,3,1,2,3... in list order with no checking. |
| `MIN-CONFLICTS` | Writes a full assignment, then repeatedly moves a person in conflict; ends with one remaining conflict that varies across samples. |
| `DENSITY` | Answer justified by how many conflicts there are. |
| `NOISY-EXACT` | Search with a slip: one conflict misread or a check skipped at random. |
| `PERCEPTION-NOISE` | A conflict is misquoted or omitted when the list is restated. |
| `RANDOM` | No relation between trace and answer. |

### E4-a · UNSAT critical (odd wheel), rendering R1

- **Tests:** Which conflict does an infeasible answer violate, and does that move with list position (DROP) or with intro order (FIRST-FIT, CYCLIC), or vary across samples (MIN-CONFLICTS, noise)?
- **Controlled:** graph (odd wheel W5: hub + 5-cycle, 4-edge-critical), names, intro order. **Varied:** UNSAT critical (odd wheel), rendering R1.
- **Ground truth:** `IMPOSSIBLE`. **Params:** `{"n": 6, "m": 10, "k": 3, "intro_order": ["Eli", "Cal", "Ann", "Ben", "Fay", "Dee"], "edge_order": ["Ben-Fay", "Fay-Ann", "Fay-Eli", "Eli-Dee", "Ben-Cal", "Cal-Fay", "Dee-Cal", "Ann-Eli", "Dee-Fay", "Ben-Ann"]}`

```text
6 people must each be given one of 3 meeting slots, numbered 1 to 3. Some pairs of people are in conflict and must not share a slot.

People: Eli, Cal, Ann, Ben, Fay, Dee

Conflicts:
1. Ben and Fay
2. Fay and Ann
3. Fay and Eli
4. Eli and Dee
5. Ben and Cal
6. Cal and Fay
7. Dee and Cal
8. Ann and Eli
9. Dee and Fay
10. Ben and Ann

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Eli": 1, "Cal": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `DROP(LAST)` | violates exactly Ben-Ann | cell: >= 60% of responses 'violates exactly Ben-Ann'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DROP(FIRST)` | violates exactly Ben-Fay | cell: >= 60% of responses 'violates exactly Ben-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DROP(LONG)` | violates exactly Eli-Dee | cell: >= 60% of responses 'violates exactly Eli-Dee'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `FIRST-FIT-cap` | violates exactly Fay-Ann | cell: >= 60% of responses 'violates exactly Fay-Ann'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DSATUR-cap` | violates exactly Dee-Fay | cell: >= 60% of responses 'violates exactly Dee-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `CYCLIC` | violates exactly Cal-Fay | cell: >= 60% of responses 'violates exactly Cal-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: Ben-Ann 0.12; Cal-Fay 0.11; Dee-Cal 0.11 (consistency sum p^2 = 0.10) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `DENSITY` | IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling | cell: >= 60% of responses 'IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `NOISY-EXACT` | stochastic: mostly IMPOSSIBLE; slips violate a uniformly random conflict | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `PERCEPTION-NOISE` | stochastic: a randomly lost conflict is violated (weak late-list gradient) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.86 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `FIRST-FIT-cap`
- `other violation pattern` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `proper colouring` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Ben-Ann` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Ben-Fay` → against `CYCLIC`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Cal-Fay` → against `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Dee-Fay` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Eli-Dee` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Fay-Ann` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`

### E4-b · UNSAT, R1 with the last conflict swapped with the 5th

- **Tests:** Which conflict does an infeasible answer violate, and does that move with list position (DROP) or with intro order (FIRST-FIT, CYCLIC), or vary across samples (MIN-CONFLICTS, noise)?
- **Controlled:** graph (odd wheel W5: hub + 5-cycle, 4-edge-critical), names, intro order. **Varied:** UNSAT, R1 with the last conflict swapped with the 5th.
- **Ground truth:** `IMPOSSIBLE`. **Params:** `{"n": 6, "m": 10, "k": 3, "intro_order": ["Eli", "Cal", "Ann", "Ben", "Fay", "Dee"], "edge_order": ["Ben-Fay", "Fay-Ann", "Fay-Eli", "Eli-Dee", "Ben-Ann", "Cal-Fay", "Dee-Cal", "Ann-Eli", "Dee-Fay", "Ben-Cal"]}`

```text
6 people must each be given one of 3 meeting slots, numbered 1 to 3. Some pairs of people are in conflict and must not share a slot.

People: Eli, Cal, Ann, Ben, Fay, Dee

Conflicts:
1. Ben and Fay
2. Fay and Ann
3. Fay and Eli
4. Eli and Dee
5. Ben and Ann
6. Cal and Fay
7. Dee and Cal
8. Ann and Eli
9. Dee and Fay
10. Ben and Cal

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Eli": 1, "Cal": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `DROP(LAST)` | violates exactly Ben-Cal | cell: >= 60% of responses 'violates exactly Ben-Cal'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DROP(FIRST)` | violates exactly Ben-Fay | cell: >= 60% of responses 'violates exactly Ben-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DROP(LONG)` | violates exactly Eli-Dee | cell: >= 60% of responses 'violates exactly Eli-Dee'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `FIRST-FIT-cap` | violates exactly Fay-Ann | cell: >= 60% of responses 'violates exactly Fay-Ann'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DSATUR-cap` | violates exactly Dee-Fay | cell: >= 60% of responses 'violates exactly Dee-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `CYCLIC` | violates exactly Cal-Fay | cell: >= 60% of responses 'violates exactly Cal-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: Ben-Ann 0.12; Cal-Fay 0.11; Dee-Cal 0.11 (consistency sum p^2 = 0.10) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `DENSITY` | IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling | cell: >= 60% of responses 'IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `NOISY-EXACT` | stochastic: mostly IMPOSSIBLE; slips violate a uniformly random conflict | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `PERCEPTION-NOISE` | stochastic: a randomly lost conflict is violated (weak late-list gradient) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.86 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `FIRST-FIT-cap`
- `other violation pattern` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `proper colouring` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Ben-Cal` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Ben-Fay` → against `CYCLIC`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Cal-Fay` → against `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Dee-Fay` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Eli-Dee` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Fay-Ann` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`

### E4-c · feasible sibling (one conflict replaced in place; same n, m), R1 order

- **Tests:** Which conflict does an infeasible answer violate, and does that move with list position (DROP) or with intro order (FIRST-FIT, CYCLIC), or vary across samples (MIN-CONFLICTS, noise)?
- **Controlled:** graph (odd wheel W5: hub + 5-cycle, 4-edge-critical), names, intro order. **Varied:** feasible sibling (one conflict replaced in place; same n, m), R1 order.
- **Ground truth:** `proper colouring`. **Params:** `{"n": 6, "m": 10, "k": 3, "intro_order": ["Eli", "Cal", "Ann", "Ben", "Fay", "Dee"], "edge_order": ["Ben-Fay", "Fay-Ann", "Fay-Eli", "Eli-Dee", "Cal-Ann", "Cal-Fay", "Dee-Cal", "Ann-Eli", "Dee-Fay", "Ben-Ann"]}`

```text
6 people must each be given one of 3 meeting slots, numbered 1 to 3. Some pairs of people are in conflict and must not share a slot.

People: Eli, Cal, Ann, Ben, Fay, Dee

Conflicts:
1. Ben and Fay
2. Fay and Ann
3. Fay and Eli
4. Eli and Dee
5. Cal and Ann
6. Cal and Fay
7. Dee and Cal
8. Ann and Eli
9. Dee and Fay
10. Ben and Ann

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Eli": 1, "Cal": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | proper colouring | cell: >= 85% of responses match (correct) |
| `DROP(LAST)` | proper colouring | cell: >= 85% of responses match (correct) |
| `DROP(FIRST)` | proper colouring | cell: >= 85% of responses match (correct) |
| `DROP(LONG)` | proper colouring | cell: >= 85% of responses match (correct) |
| `FIRST-FIT-cap` | proper colouring | cell: >= 85% of responses match (correct) |
| `DSATUR-cap` | proper colouring | cell: >= 85% of responses match (correct) |
| `CYCLIC` | violates exactly Cal-Fay | cell: >= 60% of responses 'violates exactly Cal-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: proper 1.00 (consistency sum p^2 = 1.00) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `DENSITY` | IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling | cell: >= 60% of responses 'IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `NOISY-EXACT` | stochastic: mostly IMPOSSIBLE; slips violate a uniformly random conflict | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `PERCEPTION-NOISE` | stochastic: a randomly lost conflict is violated (weak late-list gradient) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.43 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `other violation pattern` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `proper colouring` → against `CYCLIC`
- `violates exactly Cal-Fay` → against `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`

### E4-d · UNSAT + irrelevant pendant conflict listed LAST

- **Tests:** Which conflict does an infeasible answer violate, and does that move with list position (DROP) or with intro order (FIRST-FIT, CYCLIC), or vary across samples (MIN-CONFLICTS, noise)?
- **Controlled:** graph (odd wheel W5: hub + 5-cycle, 4-edge-critical), names, intro order. **Varied:** UNSAT + irrelevant pendant conflict listed LAST.
- **Ground truth:** `IMPOSSIBLE`. **Params:** `{"n": 7, "m": 11, "k": 3, "intro_order": ["Eli", "Cal", "Ann", "Ben", "Fay", "Dee", "Gus"], "edge_order": ["Ben-Fay", "Fay-Ann", "Fay-Eli", "Eli-Dee", "Ben-Cal", "Cal-Fay", "Dee-Cal", "Ann-Eli", "Dee-Fay", "Ben-Ann", "Eli-Gus"]}`

```text
7 people must each be given one of 3 meeting slots, numbered 1 to 3. Some pairs of people are in conflict and must not share a slot.

People: Eli, Cal, Ann, Ben, Fay, Dee, Gus

Conflicts:
1. Ben and Fay
2. Fay and Ann
3. Fay and Eli
4. Eli and Dee
5. Ben and Cal
6. Cal and Fay
7. Dee and Cal
8. Ann and Eli
9. Dee and Fay
10. Ben and Ann
11. Eli and Gus

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Eli": 1, "Cal": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `DROP(LAST)` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `DROP(FIRST)` | violates exactly Ben-Fay | cell: >= 60% of responses 'violates exactly Ben-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DROP(LONG)` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `FIRST-FIT-cap` | violates exactly Fay-Ann | cell: >= 60% of responses 'violates exactly Fay-Ann'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DSATUR-cap` | violates exactly Dee-Fay | cell: >= 60% of responses 'violates exactly Dee-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `CYCLIC` | violates exactly Cal-Fay, Eli-Gus | cell: >= 60% of responses 'violates exactly Cal-Fay, Eli-Gus'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: Ben-Cal 0.11; Fay-Eli 0.11; Ben-Ann 0.11 (consistency sum p^2 = 0.10) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `DENSITY` | IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling | cell: >= 60% of responses 'IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `NOISY-EXACT` | stochastic: mostly IMPOSSIBLE; slips violate a uniformly random conflict | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `PERCEPTION-NOISE` | stochastic: a randomly lost conflict is violated (weak late-list gradient) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.73 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(FIRST)`, `DSATUR-cap`, `FIRST-FIT-cap`
- `other violation pattern` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `proper colouring` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Ben-Fay` → against `CYCLIC`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Cal-Fay, Eli-Gus` → against `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Dee-Fay` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Fay-Ann` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`

### E4-e · UNSAT + irrelevant pendant conflict listed FIRST

- **Tests:** Which conflict does an infeasible answer violate, and does that move with list position (DROP) or with intro order (FIRST-FIT, CYCLIC), or vary across samples (MIN-CONFLICTS, noise)?
- **Controlled:** graph (odd wheel W5: hub + 5-cycle, 4-edge-critical), names, intro order. **Varied:** UNSAT + irrelevant pendant conflict listed FIRST.
- **Ground truth:** `IMPOSSIBLE`. **Params:** `{"n": 7, "m": 11, "k": 3, "intro_order": ["Eli", "Cal", "Ann", "Ben", "Fay", "Dee", "Gus"], "edge_order": ["Eli-Gus", "Ben-Fay", "Fay-Ann", "Fay-Eli", "Eli-Dee", "Ben-Cal", "Cal-Fay", "Dee-Cal", "Ann-Eli", "Dee-Fay", "Ben-Ann"]}`

```text
7 people must each be given one of 3 meeting slots, numbered 1 to 3. Some pairs of people are in conflict and must not share a slot.

People: Eli, Cal, Ann, Ben, Fay, Dee, Gus

Conflicts:
1. Eli and Gus
2. Ben and Fay
3. Fay and Ann
4. Fay and Eli
5. Eli and Dee
6. Ben and Cal
7. Cal and Fay
8. Dee and Cal
9. Ann and Eli
10. Dee and Fay
11. Ben and Ann

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Eli": 1, "Cal": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `DROP(LAST)` | violates exactly Ben-Ann | cell: >= 60% of responses 'violates exactly Ben-Ann'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DROP(FIRST)` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `DROP(LONG)` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `FIRST-FIT-cap` | violates exactly Fay-Ann | cell: >= 60% of responses 'violates exactly Fay-Ann'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DSATUR-cap` | violates exactly Dee-Fay | cell: >= 60% of responses 'violates exactly Dee-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `CYCLIC` | violates exactly Eli-Gus, Cal-Fay | cell: >= 60% of responses 'violates exactly Eli-Gus, Cal-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: Ben-Cal 0.11; Fay-Eli 0.11; Ben-Ann 0.11 (consistency sum p^2 = 0.10) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `DENSITY` | IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling | cell: >= 60% of responses 'IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `NOISY-EXACT` | stochastic: mostly IMPOSSIBLE; slips violate a uniformly random conflict | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `PERCEPTION-NOISE` | stochastic: a randomly lost conflict is violated (weak late-list gradient) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.73 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(LAST)`, `DSATUR-cap`, `FIRST-FIT-cap`
- `other violation pattern` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `proper colouring` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Ben-Ann` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Dee-Fay` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Eli-Gus, Cal-Fay` → against `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Fay-Ann` → against `CYCLIC`, `DROP(FIRST)`, `DROP(LAST)`, `DROP(LONG)`, `DSATUR-cap`, `EXACT`

### E4 discrimination table (coloring)

Each row is one theory's predicted answer pattern across the set (items in order E4-a, E4-b, E4-c, E4-d, E4-e). The third column gives the **log₁₀ likelihood ratio** in favour of the row's theories over each other theory, if the pattern is observed once per item (lapse ε = 0.1, 9 outcome categories, 1.86 per differing item). With r samples per item and a cell of n items, multiply by about r·n/(items in set). A mixed observation moves weight in proportion. It is not a rule-out.

| Observed pattern | Favours | log₁₀ LR vs each other theory | Not separable here (see) |
|---|---|---|---|
| violates exactly Cal-Fay / violates exactly Cal-Fay / violates exactly Cal-Fay / violates exactly Cal-Fay, Eli-Gus / violates exactly Eli-Gus, Cal-Fay | `CYCLIC` | `FIRST-FIT-cap` +9.3, `EXACT` +9.3, `DSATUR-cap` +9.3, `DROP(LONG)` +9.3, `DROP(LAST)` +9.3, `DROP(FIRST)` +9.3 |  |

**Stochastic nulls in this set** (weight bounded by cell-level rates, not by single items):

- `MIN-CONFLICTS`: cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `DENSITY`: cell: >= 60% of responses 'IMPOSSIBLE (m/n >= 1.6) on both the UNSAT item and its sibling'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `NOISY-EXACT`: cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `PERCEPTION-NOISE`: cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `RANDOM`: cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.

## E5 — Cross-link quads (two teams) and header-move pair

- **Target:** IGNORE-CROSSLINKS (G). **Nearest competitors:** IC-ALIGN (reconciles); DROP(LAST, m=2) (addendum); FIRST-FIT-cap / DSATUR-cap (C).

**(c) CoT predictions for this set** (pre-registered; scored by the L0 parser and the validated L1 codes, doc §2.4):

| Theory | Predicted trace features |
|---|---|
| `EXACT` | Systematic search or a proof of impossibility (e.g. 'the rim is an odd cycle, so the hub needs a 4th slot'). |
| `IC-GRAPH` | Colours each team in its own block starting from slot 1; never re-checks the 'Also' conflicts after combining. |
| `IC-ALIGN` | Colours each team separately, then swaps team B's slots to satisfy the cross-team conflicts. |
| `DROP(LAST,m=2)` | The last two listed conflicts are never checked. |
| `FIRST-FIT-cap` | Assigns people one by one in the listed order, lowest free slot; at the first person with no free slot, forces a slot and moves on. |
| `DSATUR-cap` | Chooses the most-constrained person next; forced conflict at the first saturated person. |
| `CYCLIC` | Slots assigned 1,2,3,1,2,3... in list order with no checking. |
| `MIN-CONFLICTS` | Writes a full assignment, then repeatedly moves a person in conflict; ends with one remaining conflict that varies across samples. |
| `NOISY-EXACT` | Search with a slip: one conflict misread or a check skipped at random. |
| `RANDOM` | No relation between trace and answer. |
| `UP-inf` | Depth-ordered assertions to the fixpoint (fan-out literals included); reaches the query iff it is propagation-derivable; no case splits. |
| `UP-PASS-1` | Walks the premises once in printed order, asserting a literal when its premise is read; never returns to an earlier premise (tau_text >= 0.6). |
| `BC-10` | Starts from the query and states sub-goals ('to show X we need Y') before confirming facts; asserts no fan-out literals; gives up after about 10 sub-goals. |
| `FREQ` | No derivation connecting facts to the query; justifies the answer by how the query is mentioned. |
| `NONE` | No derivation; says at once that the premises do not settle it. |
| `NOISY-EXACT(eps=0.05)` | Depth-ordered derivation in which one cone literal is skipped or one rule misapplied; the error is visible as a gap or an unjustified step. |
| `PS(RECENT,6)` | Never uses premises 1-6. |
| `PS(FIRST,6)` | Never uses premises 7-12. |
| `IC-TEXT` | Reasons inside each Part separately; a literal derived in Part 1 is never used in Part 2. |

### E5-a · NC clustered

- **Tests:** Are the teams solved separately and never reconciled (IGNORE-CROSSLINKS), so that answers fail exactly when canonical team colourings clash?
- **Controlled:** teams, intra-team conflicts, positions, cross-link count and endpoint degrees. **Varied:** cross-link endpoints (cell) and rendering.
- **Ground truth:** `proper colouring`. **Params:** `{"cross_links": ["Ann-Gus", "Ann-Hal"], "canonical_A": {"Ann": 1, "Ben": 2, "Cal": 2, "Dee": 1, "Eli": 1}, "canonical_B": {"Fay": 1, "Gus": 2, "Hal": 2, "Ivy": 1, "Jon": 1}, "rendering": "clustered"}`

```text
10 people must each be given one of 2 shifts, numbered 1 to 2. Some pairs of people are in conflict and must not share a slot.

People: Ann, Ben, Cal, Dee, Eli, Fay, Gus, Hal, Ivy, Jon

Conflicts:
Team North conflicts:
1. Ann and Ben
2. Ann and Cal
3. Ben and Dee
4. Cal and Eli
Team South conflicts:
5. Fay and Gus
6. Fay and Hal
7. Gus and Ivy
8. Hal and Jon
Also, across teams:
9. Ann and Gus
10. Ann and Hal

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Ann": 1, "Ben": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | proper colouring | cell: >= 85% of responses match (correct) |
| `IC-GRAPH` | proper colouring | cell: >= 85% of responses match (correct) |
| `IC-ALIGN` | proper colouring | cell: >= 85% of responses match (correct) |
| `DROP(LAST,m=2)` | proper colouring | cell: >= 85% of responses match (correct) |
| `FIRST-FIT-cap` | proper colouring | cell: >= 85% of responses match (correct) |
| `DSATUR-cap` | proper colouring | cell: >= 85% of responses match (correct) |
| `CYCLIC` | violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Ann-Gus | cell: >= 60% of responses 'violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Ann-Gus'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: proper 1.00 (consistency sum p^2 = 1.00) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `NOISY-EXACT` | stochastic: rare random violations, equal across cells | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.43 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `other violation pattern` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `proper colouring` → against `CYCLIC`
- `violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Ann-Gus` → against `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`

### E5-b · SC clustered

- **Tests:** Are the teams solved separately and never reconciled (IGNORE-CROSSLINKS), so that answers fail exactly when canonical team colourings clash?
- **Controlled:** teams, intra-team conflicts, positions, cross-link count and endpoint degrees. **Varied:** cross-link endpoints (cell) and rendering.
- **Ground truth:** `proper colouring`. **Params:** `{"cross_links": ["Dee-Fay", "Dee-Ivy"], "canonical_A": {"Ann": 1, "Ben": 2, "Cal": 2, "Dee": 1, "Eli": 1}, "canonical_B": {"Fay": 1, "Gus": 2, "Hal": 2, "Ivy": 1, "Jon": 1}, "rendering": "clustered"}`

```text
10 people must each be given one of 2 shifts, numbered 1 to 2. Some pairs of people are in conflict and must not share a slot.

People: Ann, Ben, Cal, Dee, Eli, Fay, Gus, Hal, Ivy, Jon

Conflicts:
Team North conflicts:
1. Ann and Ben
2. Ann and Cal
3. Ben and Dee
4. Cal and Eli
Team South conflicts:
5. Fay and Gus
6. Fay and Hal
7. Gus and Ivy
8. Hal and Jon
Also, across teams:
9. Dee and Fay
10. Dee and Ivy

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Ann": 1, "Ben": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | proper colouring | cell: >= 85% of responses match (correct) |
| `IC-GRAPH` | violates exactly Dee-Fay, Dee-Ivy | cell: >= 60% of responses 'violates exactly Dee-Fay, Dee-Ivy'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `IC-ALIGN` | proper colouring | cell: >= 85% of responses match (correct) |
| `DROP(LAST,m=2)` | violates exactly Dee-Fay, Dee-Ivy | cell: >= 60% of responses 'violates exactly Dee-Fay, Dee-Ivy'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `FIRST-FIT-cap` | proper colouring | cell: >= 85% of responses match (correct) |
| `DSATUR-cap` | proper colouring | cell: >= 85% of responses match (correct) |
| `CYCLIC` | violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Dee-Fay | cell: >= 60% of responses 'violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Dee-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: proper 1.00 (consistency sum p^2 = 1.00) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `NOISY-EXACT` | stochastic: rare random violations, equal across cells | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.56 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `other violation pattern` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `proper colouring` → against `CYCLIC`, `DROP(LAST,m=2)`, `IC-GRAPH`
- `violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Dee-Fay` → against `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `violates exactly Dee-Fay, Dee-Ivy` → against `CYCLIC`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`

### E5-c · BD clustered

- **Tests:** Are the teams solved separately and never reconciled (IGNORE-CROSSLINKS), so that answers fail exactly when canonical team colourings clash?
- **Controlled:** teams, intra-team conflicts, positions, cross-link count and endpoint degrees. **Varied:** cross-link endpoints (cell) and rendering.
- **Ground truth:** `IMPOSSIBLE`. **Params:** `{"cross_links": ["Dee-Fay", "Eli-Gus"], "canonical_A": {"Ann": 1, "Ben": 2, "Cal": 2, "Dee": 1, "Eli": 1}, "canonical_B": {"Fay": 1, "Gus": 2, "Hal": 2, "Ivy": 1, "Jon": 1}, "rendering": "clustered"}`

```text
10 people must each be given one of 2 shifts, numbered 1 to 2. Some pairs of people are in conflict and must not share a slot.

People: Ann, Ben, Cal, Dee, Eli, Fay, Gus, Hal, Ivy, Jon

Conflicts:
Team North conflicts:
1. Ann and Ben
2. Ann and Cal
3. Ben and Dee
4. Cal and Eli
Team South conflicts:
5. Fay and Gus
6. Fay and Hal
7. Gus and Ivy
8. Hal and Jon
Also, across teams:
9. Dee and Fay
10. Eli and Gus

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Ann": 1, "Ben": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | IMPOSSIBLE | cell: >= 85% of responses match (correct) |
| `IC-GRAPH` | violates exactly Dee-Fay | cell: >= 60% of responses 'violates exactly Dee-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `IC-ALIGN` | violates exactly Dee-Fay | cell: >= 60% of responses 'violates exactly Dee-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DROP(LAST,m=2)` | violates exactly Dee-Fay | cell: >= 60% of responses 'violates exactly Dee-Fay'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `FIRST-FIT-cap` | violates exactly Eli-Gus | cell: >= 60% of responses 'violates exactly Eli-Gus'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `DSATUR-cap` | violates exactly Cal-Eli | cell: >= 60% of responses 'violates exactly Cal-Eli'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `CYCLIC` | violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Dee-Fay, Eli-Gus | cell: >= 60% of responses 'violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Dee-Fay, Eli-Gus'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: Fay-Gus 0.17; Ben-Dee 0.15; Ann-Ben 0.14 (consistency sum p^2 = 0.14) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `NOISY-EXACT` | stochastic: rare random violations, equal across cells | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.73 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `other violation pattern` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `proper colouring` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Dee-Fay, Eli-Gus` → against `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `violates exactly Cal-Eli` → against `CYCLIC`, `DROP(LAST,m=2)`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `violates exactly Dee-Fay` → against `CYCLIC`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`
- `violates exactly Eli-Gus` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `IC-ALIGN`, `IC-GRAPH`

### E5-d · SC interleaved

- **Tests:** Are the teams solved separately and never reconciled (IGNORE-CROSSLINKS), so that answers fail exactly when canonical team colourings clash?
- **Controlled:** teams, intra-team conflicts, positions, cross-link count and endpoint degrees. **Varied:** cross-link endpoints (cell) and rendering.
- **Ground truth:** `proper colouring`. **Params:** `{"cross_links": ["Dee-Fay", "Dee-Ivy"], "canonical_A": {"Ann": 1, "Ben": 2, "Cal": 2, "Dee": 1, "Eli": 1}, "canonical_B": {"Fay": 1, "Gus": 2, "Hal": 2, "Ivy": 1, "Jon": 1}, "rendering": "interleaved"}`

```text
10 people must each be given one of 2 shifts, numbered 1 to 2. Some pairs of people are in conflict and must not share a slot.

People: Ann, Ben, Cal, Dee, Eli, Fay, Gus, Hal, Ivy, Jon

Conflicts:
1. Ben and Dee
2. Cal and Eli
3. Ann and Cal
4. Ann and Ben
5. Dee and Fay
6. Hal and Jon
7. Gus and Ivy
8. Fay and Hal
9. Fay and Gus
10. Dee and Ivy

Give every person a slot so that no two people in conflict share a slot. If that is impossible, say so. Think as carefully as you need to, then end with a final line `ANSWER: {"Ann": 1, "Ben": 2, ...}` listing every person, or `ANSWER: IMPOSSIBLE`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `EXACT` | proper colouring | cell: >= 85% of responses match (correct) |
| `IC-GRAPH` | violates exactly Dee-Fay, Dee-Ivy | cell: >= 60% of responses 'violates exactly Dee-Fay, Dee-Ivy'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `IC-ALIGN` | proper colouring | cell: >= 85% of responses match (correct) |
| `DROP(LAST,m=2)` | proper colouring | cell: >= 85% of responses match (correct) |
| `FIRST-FIT-cap` | proper colouring | cell: >= 85% of responses match (correct) |
| `DSATUR-cap` | proper colouring | cell: >= 85% of responses match (correct) |
| `CYCLIC` | violates exactly Ben-Dee, Cal-Eli, Ann-Cal, Dee-Fay, Hal-Jon, Gus-Ivy, Fay-Hal | cell: >= 60% of responses 'violates exactly Ben-Dee, Cal-Eli, Ann-Cal, Dee-Fay, Hal-Jon, Gus-Ivy, Fay-Hal'; single-violation answers concentrated on the predicted constraint (>= chance + 15pp); consistency >= 0.6 |
| `MIN-CONFLICTS` | stochastic: proper 1.00 (consistency sum p^2 = 1.00) | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `NOISY-EXACT` | stochastic: rare random violations, equal across cells | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |
| `RANDOM` | stochastic: uniform random slots | cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.56 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `IMPOSSIBLE` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `other violation pattern` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `proper colouring` → against `CYCLIC`, `IC-GRAPH`
- `violates exactly Ben-Dee, Cal-Eli, Ann-Cal, Dee-Fay, Hal-Jon, Gus-Ivy, Fay-Hal` → against `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`, `IC-GRAPH`
- `violates exactly Dee-Fay, Dee-Ivy` → against `CYCLIC`, `DROP(LAST,m=2)`, `DSATUR-cap`, `EXACT`, `FIRST-FIT-cap`, `IC-ALIGN`

### E5-e · header splits the chain (positions 2,4 | 8,10)

- **Tests:** Does a purely textual section boundary stop chaining across it (IC-TEXT)?
- **Controlled:** identical premise sequence. **Varied:** position of the 'Part 2' header only.
- **Ground truth:** `TRUE`. **Params:** `{"cone_positions": [2, 4, 8, 10], "header_before": 7}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
Part 1:
1. If the silver flag is raised, then the blue pump is working.
2. The green door is open.
3. If the green door is open, then the green pump is working.
4. If the green door is open, then the gold pump is working.
5. The red bell is ringing.
6. The white flag is raised.
Part 2:
7. If the purple door is open, then the orange flag is raised.
8. If the gold pump is working, then the black lamp is on.
9. If the white clock is stopped and the grey pump is working, then the orange bell is ringing.
10. If the black lamp is on, then the blue pump is working.
11. If the gold clock is stopped and the blue tap is dripping, then the pink clock is stopped.
12. If the grey valve is shut and the orange valve is shut, then the grey gate is locked.

Question: Is it true that the blue pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | header splits the chain (positions 2,4 | 8,10): >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | TRUE | header splits the chain (positions 2,4 | 8,10): >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | header splits the chain (positions 2,4 | 8,10): >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | header splits the chain (positions 2,4 | 8,10): >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | header splits the chain (positions 2,4 | 8,10): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | header splits the chain (positions 2,4 | 8,10): >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | header splits the chain (positions 2,4 | 8,10): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | header splits the chain (positions 2,4 | 8,10): each answer 33% +/- 8%. |
| `PS(RECENT,6)` | UNDETERMINED | header splits the chain (positions 2,4 | 8,10): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,6)` | UNDETERMINED | header splits the chain (positions 2,4 | 8,10): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `IC-TEXT` | UNDETERMINED | header splits the chain (positions 2,4 | 8,10): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `IC-TEXT`, `NOISY-EXACT(eps=0.05)`, `NONE`, `PS(FIRST,6)`, `PS(RECENT,6)`, `RANDOM`
- `FALSE` → against `BC-10`, `EXACT`, `FREQ`, `IC-TEXT`, `NOISY-EXACT(eps=0.05)`, `NONE`, `PS(FIRST,6)`, `PS(RECENT,6)`, `RANDOM`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `EXACT`, `FREQ`, `NOISY-EXACT(eps=0.05)`, `RANDOM`, `UP-PASS-1`, `UP-inf`

### E5-f · header after the chain (all in Part 1)

- **Tests:** Does a purely textual section boundary stop chaining across it (IC-TEXT)?
- **Controlled:** identical premise sequence. **Varied:** position of the 'Part 2' header only.
- **Ground truth:** `TRUE`. **Params:** `{"cone_positions": [2, 4, 8, 10], "header_before": 11}`

```text
Below are some facts and rules. Assume they are all true and that nothing else is known.

Premises:
Part 1:
1. If the silver flag is raised, then the blue pump is working.
2. The green door is open.
3. If the green door is open, then the green pump is working.
4. If the green door is open, then the gold pump is working.
5. The red bell is ringing.
6. The white flag is raised.
7. If the purple door is open, then the orange flag is raised.
8. If the gold pump is working, then the black lamp is on.
9. If the white clock is stopped and the grey pump is working, then the orange bell is ringing.
10. If the black lamp is on, then the blue pump is working.
Part 2:
11. If the gold clock is stopped and the blue tap is dripping, then the pink clock is stopped.
12. If the grey valve is shut and the orange valve is shut, then the grey gate is locked.

Question: Is it true that the blue pump is working?

Answer TRUE if the premises guarantee it, FALSE if the premises guarantee that it is not the case, or UNDETERMINED if the premises do not settle it. Think as carefully as you need to, then end your response with a final line of the form `ANSWER: TRUE`, `ANSWER: FALSE` or `ANSWER: UNDETERMINED`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `UP-inf` | TRUE | header after the chain (all in Part 1): >= 85% of responses 'TRUE' (correct). |
| `UP-PASS-1` | TRUE | header after the chain (all in Part 1): >= 85% of responses 'TRUE' (correct). |
| `BC-10` | TRUE | header after the chain (all in Part 1): >= 85% of responses 'TRUE' (correct). |
| `FREQ` | TRUE | header after the chain (all in Part 1): >= 85% of responses 'TRUE' (correct). |
| `NONE` | UNDETERMINED | header after the chain (all in Part 1): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `EXACT` | TRUE | header after the chain (all in Part 1): >= 85% of responses 'TRUE' (correct). |
| `NOISY-EXACT(eps=0.05)` | TRUE w.p. 0.86, else UNDETERMINED | header after the chain (all in Part 1): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. |
| `RANDOM` | uniform over TRUE / FALSE / UNDETERMINED | header after the chain (all in Part 1): each answer 33% +/- 8%. |
| `PS(RECENT,6)` | UNDETERMINED | header after the chain (all in Part 1): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `PS(FIRST,6)` | UNDETERMINED | header after the chain (all in Part 1): <= 15% correct; >= 70% of errors UNDETERMINED or chance-polarity guesses (polarity accuracy 50 +/- 8%). |
| `IC-TEXT` | TRUE | header after the chain (all in Part 1): >= 85% of responses 'TRUE' (correct). |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `TRUE` → against `NOISY-EXACT(eps=0.05)`, `NONE`, `PS(FIRST,6)`, `PS(RECENT,6)`, `RANDOM`
- `FALSE` → against `BC-10`, `EXACT`, `FREQ`, `IC-TEXT`, `NOISY-EXACT(eps=0.05)`, `NONE`, `PS(FIRST,6)`, `PS(RECENT,6)`, `RANDOM`, `UP-PASS-1`, `UP-inf`
- `UNDETERMINED` → against `BC-10`, `EXACT`, `FREQ`, `IC-TEXT`, `NOISY-EXACT(eps=0.05)`, `RANDOM`, `UP-PASS-1`, `UP-inf`

### E5 discrimination table (coloring)

Each row is one theory's predicted answer pattern across the set (items in order E5-a, E5-b, E5-c, E5-d). The third column gives the **log₁₀ likelihood ratio** in favour of the row's theories over each other theory, if the pattern is observed once per item (lapse ε = 0.1, 4 outcome categories, 1.43 per differing item). With r samples per item and a cell of n items, multiply by about r·n/(items in set). A mixed observation moves weight in proportion. It is not a rule-out.

| Observed pattern | Favours | log₁₀ LR vs each other theory | Not separable here (see) |
|---|---|---|---|
| violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Ann-Gus / violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Dee-Fay / violates exactly Ann-Cal, Ben-Dee, Cal-Eli, Fay-Hal, Gus-Ivy, Hal-Jon, Dee-Fay, Eli-Gus / violates exactly Ben-Dee, Cal-Eli, Ann-Cal, Dee-Fay, Hal-Jon, Gus-Ivy, Fay-Hal | `CYCLIC` | `IC-GRAPH` +5.7, `IC-ALIGN` +5.7, `FIRST-FIT-cap` +5.7, `EXACT` +5.7, `DSATUR-cap` +5.7, `DROP(LAST,m=2)` +5.7 |  |

**Stochastic nulls in this set** (weight bounded by cell-level rates, not by single items):

- `MIN-CONFLICTS`: cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `NOISY-EXACT`: cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `RANDOM`: cell: violated-constraint identity spread over constraints; cross-sample consistency <= 0.3 Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.

### E5 discrimination table (entailment)

Each row is one theory's predicted answer pattern across the set (items in order E5-e, E5-f). The third column gives the **log₁₀ likelihood ratio** in favour of the row's theories over each other theory, if the pattern is observed once per item (lapse ε = 0.1, 3 outcome categories, 1.26 per differing item). With r samples per item and a cell of n items, multiply by about r·n/(items in set). A mixed observation moves weight in proportion. It is not a rule-out.

| Observed pattern | Favours | log₁₀ LR vs each other theory | Not separable here (see) |
|---|---|---|---|
| U / T | `IC-TEXT` | `UP-inf` +1.3, `UP-PASS-1` +1.3, `PS(RECENT,6)` +1.3, `PS(FIRST,6)` +1.3, `NONE` +1.3, `FREQ` +1.3, `EXACT` +1.3, `BC-10` +1.3 |  |

**Stochastic nulls in this set** (weight bounded by cell-level rates, not by single items):

- `NOISY-EXACT(eps=0.05)`: header splits the chain (positions 2,4 | 8,10): accuracy = 0.95^s +/- 0.08 (s = cone size); across the matched-d trio accuracy is ordered chain > ladder > tree. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.
- `RANDOM`: header splits the chain (positions 2,4 | 8,10): each answer 33% +/- 8%. Readout: π for this null, with its 95% interval. It is bounded at ≤ 0.1 (upper 95%) when cell rates fall outside this band in ≥ 2 cells, or when a deterministic row above is matched with cross-sample consistency ≥ 0.6.

## E6 — Knapsack reachable-sum dial

- **Target:** DP-LIST (G). **Nearest competitors:** ENUMERATION (D); RATIO / VALUE (C).
- **Note:** Answers alone cannot separate DP from any exact method; the disconfirming evidence is the trace-cost ratio and DP-table events.

**(c) CoT predictions for this set** (pre-registered; scored by the L0 parser and the validated L1 codes, doc §2.4):

| Theory | Predicted trace features |
|---|---|
| `DP-LIST / DP-EXACT / EXACT` | Writes a table of reachable (weight, value) pairs item by item; predicted table size sum |L| = 32 (reachable sums R = 9). |
| `RATIO` | Computes value/weight ratios and sorts; adds items in ratio order; ~n steps. |
| `VALUE` | Sorts by value. |
| `LARGEST-FIT` | Sorts by weight. |
| `DP-ROUND(10)` | Rounds weights to tens before combining. |
| `ENUMERATION (D)` | Lists subsets; cost ~ 2^n = 256 regardless of R. |

### E6-a · low-R (3 distinct weights)

- **Tests:** Does reasoning cost scale with the DP state count (DP-LIST) rather than with 2^n (enumeration) or n (greedy)?
- **Controlled:** n, digit lengths, W (+/-3), optimal-vs-RATIO gap. **Varied:** weight multiset (3 distinct values vs all distinct).
- **Ground truth:** `[1, 2, 5] (value 141)`. **Params:** `{"n": 8, "W": 108, "dp_list_cost": 32, "reachable_sums": 9, "opt_minus_ratio": 2}`

```text
You are packing a bag that can hold at most 108 kg. The items are:
1. weight 29 kg, value 49
2. weight 29 kg, value 49
3. weight 39 kg, value 34
4. weight 39 kg, value 13
5. weight 39 kg, value 43
6. weight 29 kg, value 35
7. weight 39 kg, value 30
8. weight 29 kg, value 41

Choose items so that the total weight is at most 108 kg and the total value is as large as possible. Think as carefully as you need to, then end with a final line `ANSWER: [item numbers]`, e.g. `ANSWER: [1, 4, 5]`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `DP-LIST / DP-EXACT / EXACT` | [1, 2, 5] (value 141) | pair: thinking tokens(high-R) / tokens(low-R) >= 2 and DP tables in >= 50% of traces |
| `RATIO` | [1, 2, 8] (value 139) | pair: token ratio high/low within 0.8-1.25; answers identical to its prediction in >= 85% |
| `VALUE` | [1, 2, 5] (value 141) | pair: token ratio high/low within 0.8-1.25; answers identical to its prediction in >= 85% |
| `LARGEST-FIT` | [1, 3, 4] (value 96) | pair: token ratio high/low within 0.8-1.25; answers identical to its prediction in >= 85% |
| `DP-ROUND(10)` | [1, 2, 5, 8] (true weight 126 > W: infeasible) | pair: overshoot answers (weight in (W, W + sum residues]) in >= 30% |
| `ENUMERATION (D)` | [1, 2, 5] (value 141) within budget | pair: token ratio high/low within 0.8-1.25; answers identical to its prediction in >= 85% |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `DP table cost tracks R (tokens high/low >= 2)` → against `RATIO`, `VALUE`, `LARGEST-FIT`, `ENUMERATION (D)`
- `tokens invariant to R` → against `DP-LIST / DP-EXACT / EXACT (as process)`
- `answer = RATIO set` → against `DP-LIST / DP-EXACT / EXACT`, `DP-ROUND(10)`, `VALUE`, `LARGEST-FIT`

### E6-b · high-R (distinct weights)

- **Tests:** Does reasoning cost scale with the DP state count (DP-LIST) rather than with 2^n (enumeration) or n (greedy)?
- **Controlled:** n, digit lengths, W (+/-3), optimal-vs-RATIO gap. **Varied:** weight multiset (3 distinct values vs all distinct).
- **Ground truth:** `[4, 5, 6] (value 114)`. **Params:** `{"n": 8, "W": 105, "dp_list_cost": 113, "reachable_sums": 53, "opt_minus_ratio": 2}`

```text
You are packing a bag that can hold at most 105 kg. The items are:
1. weight 30 kg, value 35
2. weight 16 kg, value 15
3. weight 22 kg, value 22
4. weight 55 kg, value 59
5. weight 31 kg, value 37
6. weight 12 kg, value 18
7. weight 52 kg, value 21
8. weight 46 kg, value 13

Choose items so that the total weight is at most 105 kg and the total value is as large as possible. Think as carefully as you need to, then end with a final line `ANSWER: [item numbers]`, e.g. `ANSWER: [1, 4, 5]`.
```

| Theory | (a) Output | (b) Eval prediction (cell) |
|---|---|---|
| `DP-LIST / DP-EXACT / EXACT` | [4, 5, 6] (value 114) | pair: thinking tokens(high-R) / tokens(low-R) >= 2 and DP tables in >= 50% of traces |
| `RATIO` | [1, 3, 5, 6] (value 112) | pair: token ratio high/low within 0.8-1.25; answers identical to its prediction in >= 85% |
| `VALUE` | [4, 5, 6] (value 114) | pair: token ratio high/low within 0.8-1.25; answers identical to its prediction in >= 85% |
| `LARGEST-FIT` | [4, 8] (value 72) | pair: token ratio high/low within 0.8-1.25; answers identical to its prediction in >= 85% |
| `DP-ROUND(10)` | [2, 4, 5, 6] (true weight 114 > W: infeasible) | pair: overshoot answers (weight in (W, W + sum residues]) in >= 30% |
| `ENUMERATION (D)` | [4, 5, 6] (value 114) within budget | pair: token ratio high/low within 0.8-1.25; answers identical to its prediction in >= 85% |

**Outcome → evidence against each theory** (log₁₀ likelihood ratio per response = 1.26 at lapse ε = 0.1; it adds over responses and feeds the π_h fit; it is not a binary rule-out):

- `DP table cost tracks R (tokens high/low >= 2)` → against `RATIO`, `VALUE`, `LARGEST-FIT`, `ENUMERATION (D)`
- `tokens invariant to R` → against `DP-LIST / DP-EXACT / EXACT (as process)`
- `answer = RATIO set` → against `DP-LIST / DP-EXACT / EXACT`, `DP-ROUND(10)`, `VALUE`, `LARGEST-FIT`

### E6 discrimination table (knapsack)

Each row is one theory's predicted answer pattern across the set (items in order E6-a, E6-b). The third column gives the **log₁₀ likelihood ratio** in favour of the row's theories over each other theory, if the pattern is observed once per item (lapse ε = 0.1, 3 outcome categories, 1.26 per differing item). With r samples per item and a cell of n items, multiply by about r·n/(items in set). A mixed observation moves weight in proportion. It is not a rule-out.

| Observed pattern | Favours | log₁₀ LR vs each other theory | Not separable here (see) |
|---|---|---|---|
| [1, 2, 5] (value 141) within budget / [4, 5, 6] (value 114) within budget | `ENUMERATION (D)` | `VALUE` +2.5, `RATIO` +2.5, `LARGEST-FIT` +2.5, `DP-ROUND(10)` +2.5, `DP-LIST / DP-EXACT / EXACT` +2.5 |  |