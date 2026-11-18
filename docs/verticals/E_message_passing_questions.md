# Family E (message passing): example question library
*Companion to [E_message_passing.md](E_message_passing.md). Machine-readable copy: [`data/examples/E_message_passing.jsonl`](../../data/examples/E_message_passing.jsonl), one object per item.*
**What this is.** Concrete items for every eval in the vertical, built the way the generators will build them (§2.13 of the vertical), at **illustration scale**. Cores have 10 variables instead of n\*; sparse skeletons have ~45 variables instead of ~50.
**How everything here was checked.** Nothing below was worked out by hand. A throwaway pure-Python verifier (kept outside the repo) does all of it:
- ground truth by exact model counting (DPLL with component decomposition), exact backbones and exact marginals;
- every theory's prediction by running its reference implementation on the item;
- every set-level prediction ("eval result"), every weight-resolution table and every likelihood-ratio table, *derived* from those item-level predictions;
- the coverage matrix at the end, computed from the same vectors.
The verifier's reference implementations of C1, D, F and H are stand-ins for the other verticals' code. They follow those verticals' one-line definitions in PAPER_SKELETON Table 4.
**Size.** 163 items in the JSONL: complete counterfactual sets for every eval (every cell of the illustration design). This document shows 44 of them: full prompt text for 26, with each minimal-pair variant given as an exact clause diff against its base. The rest are tabulated.
**Reading the hypothesis blocks.** For each set, one table gives every theory three things:
- **(a) output:** its answer on each item, side by side (with P(True) where the theory is graded or stochastic);
- **(b) eval result:** the set statistic it predicts *if it generated every item* (π = 1), with the set's power for its weight;
- **(c) CoT:** its predicted trace features.

**The readout is graded.** A model is a mixture of theories with weights π. Each set reports:

- **weight resolution:** detectable π and upper-95% bounds on absent competitors, at full and dev-batch sizes;
- **likelihood ratios:** for each outcome pattern, against the nearest other theories.

"Disconfirming" a theory means bounding its weight near zero, never eliminating it.
The JSONL carries the same, per item, in `hypotheses` (theory → {output, eval_prediction, cot_prediction}) and `disconfirms`. In `disconfirms`, each outcome pattern maps to the theories it pushes toward zero, each with its log10 LR and full-study upper-95% weight bound.
**Thresholds** (pre-registered in the vertical):

- an effect is **present (+)** if ≥ 0.15 in probability (thinking runs; direct runs use ≥ 0.25 logit);
- **absent (0)** if ≤ 0.05 (TOST equivalence bound);
- **partial (~)** in between.
**Theory keys.**
| Key | Family | One line |
|---|---|---|
| `E:BP-t` | E | Sum-product BP, t rounds (synchronous), then sign of the marginal. `E:BP-0` = weighted `POLARITY`. |
| `E:BP-t-CAUSAL` | E | BP-t with messages only from clauses earlier in the prompt (decoder-only constraint) |
| `E:LOCAL-EXACT-r` | E (envelope) | Exact answer on the clauses within r hops of the target (local, but not message passing) |
| `B1:WP-t` | E/B1 boundary | Warning propagation (hard messages), t rounds |
| `E:E-in-D` | E∘D | DPLL whose value order is the BP-2 marginal (E as value heuristic inside search) |
| `E:BP-DEC-*` | E (seq) | BP-guided decimation: MAX = most-biased first; OUT = answer order |
| `B1:UP-k` | B1 | k rounds of unit propagation (radius k−1); default `POLARITY` when silent |
| `B1C0:EQ-CONTRACT+POL` | B1∘C0 | Merge 2-clause equivalences, then `POLARITY` of the merged variable |
| `C0:POLARITY` | C0 | Sign of the target's own positive − negative occurrences |
| `C1:GREEDY` / `C1:FIRST-FIT` | C1 | First-mention order, myopic, never revisited |
| `C2:DSATUR` / `C2:UC` / `C2:GUC` | C2 | Adaptive greedy |
| `D:DPLL-*` | D | DPLL with UP and backtracking; `(b=0)` = UP + default; `(complete)` = first solution found |
| `F:WALK-k` / `F:MIN-CONFLICTS-k` | F | WalkSAT / min-conflicts, k flips |
| `H:SAMPLER` / `H:SAMPLE-m` | H | Uniform over solutions (exact marginal) / check the conclusion in sampled models |
| `B4:FIRST` | B4 | Each disjunction read as its first disjunct |
| `A1:ALWAYS-*` | A1 | Constant answer |
| `A2:PRIMACY` / `A2:RECENCY` | A2 | Sign of the target's first / last mention |
| `NULL:EXACT` | null | The model solves it exactly |
| `NULL:NOISY-EXACT` | null | Exact with independent slips |
| `NULL:PERCEPTION-NOISE` | null | Exact reasoning on a misread instance: average over all single misread literals (or edge endpoints) |
| `NULL:RANDOM` | null | Coin flip |

**Contents.**

1. E1-S soft channel (radius; MP vs UP-k, vs C0, vs exact)
2. E1-S hard channel
3. E1-S placement, framing and growth
4. E1-S colouring (BP vs singleton propagation)
5. E1-C periphery–core
6. E2 soft vs hard factorial
7. E3 cover pairs
8. E4 α sweep
9. E5 calibration and lifts
10. E6 decimation

---

## 1. E1-S soft channel: a soft hub d hops away (radius; MP vs UP-k, vs C0, vs exact)
**Reasoning question.** Does the answer about the target depend on soft evidence d hops away, and only up to a finite radius? This is the main test of **MP vs C0** (radius 0) and **MP vs `UP-k`** (no unit clauses, so UP is silent). It also tests **MP vs the exact sampler**, whose effect is flat in d.
**Controlled factors.** Same skeleton, clause order and names throughout. Each effective edit has a matched null that flips the same number of literals at the same distance (token-identical clauses; only which word carries `not` differs). Negation counts are equal between effective and null.
**Varied factors.** Distance d ∈ {1, 2, 3, 4, 6} (shown: d = 1, 3); version ∈ {base, effective, null}; placement ∈ {early, late} (shown: early).
**Design.** The target v heads an equivalence chain v ≡ c₁ ≡ … ≡ c₆. Every chain variable has a balanced pendant pair, and there is a disconnected filler. The hub c_d carries 3 pendant 2-clauses (c_d or leaf). Effective = negate c_d in them; null = negate the leaf instead. v is free, so the question asks for a preference.

### Items
**d = 1** (hub `iron`, target `fork`; 29 variables, 36 clauses; negations base/effective/null = 27/30/30).
- `E1-S/soft-d1-early-base`: ground truth: either value is correct (exact P(fork=True) = 0.89)
- `E1-S/soft-d1-early-effective`: ground truth: either value is correct (exact P(fork=True) = 0.11). Edit:
- `1. (iron or coat)`  →  `1. (not iron or coat)`
- `3. (apple or iron)`  →  `3. (apple or not iron)`
- `5. (king or iron)`  →  `5. (king or not iron)`
- `E1-S/soft-d1-early-null`: ground truth: either value is correct (exact P(fork=True) = 0.89). Edit:
- `1. (iron or coat)`  →  `1. (iron or not coat)`
- `3. (apple or iron)`  →  `3. (not apple or iron)`
- `5. (king or iron)`  →  `5. (not king or iron)`
<details open><summary>Full prompt: <code>E1-S/soft-d1-early-base</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (iron or coat)
2. (book or plum)
3. (apple or iron)
4. (book or not tree)
5. (king or iron)
6. (iron or not fork)
7. (tree or not book)
8. (not horn or hill or not salt)
9. (jar or sea)
10. (sea or not iron)
11. (not ring or bell)
12. (bread or fork)
13. (not sea or iron)
14. (map or hill or salt)
15. (pin or ring)
16. (not wall or tree)
17. (fork or not iron)
18. (not hill or not map or salt)
19. (bear or not hill or map)
20. (not tree or ship)
21. (horn or not bear or hill)
22. (lock or not iron)
23. (cave or wall)
24. (not tree or wall)
25. (moss or not book)
26. (not ring or book)
27. (bear or horn or not salt)
28. (cake or not fork)
29. (harp or not sea)
30. (ring or not sea)
31. (iron or nut)
32. (sea or not ring)
33. (snow or tree)
34. (not wall or key)
35. (ring or not book)
36. (not horn or map or hill)

Choose any assignment that satisfies all the clauses. What value does fork take in your assignment? Answer with one word: True or False.
```

</details>
**d = 3** (hub `ring`, target `fork`; 29 variables, 36 clauses; negations base/effective/null = 27/30/30).
- `E1-S/soft-d3-early-base`: ground truth: either value is correct (exact P(fork=True) = 0.89)
- `E1-S/soft-d3-early-effective`: ground truth: either value is correct (exact P(fork=True) = 0.11). Edit:
- `3. (ring or coat)`  →  `3. (not ring or coat)`
- `4. (king or ring)`  →  `4. (king or not ring)`
- `5. (ring or apple)`  →  `5. (not ring or apple)`
- `E1-S/soft-d3-early-null`: ground truth: either value is correct (exact P(fork=True) = 0.89). Edit:
- `3. (ring or coat)`  →  `3. (ring or not coat)`
- `4. (king or ring)`  →  `4. (not king or ring)`
- `5. (ring or apple)`  →  `5. (ring or not apple)`
<details><summary>Full prompt: <code>E1-S/soft-d3-early-base</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (tree or snow)
2. (cave or wall)
3. (ring or coat)
4. (king or ring)
5. (ring or apple)
6. (fork or not iron)
7. (not horn or not salt or hill)
8. (not sea or iron)
9. (not fork or iron)
10. (not iron or lock)
11. (not wall or key)
12. (sea or not iron)
13. (not hill or not map or salt)
14. (map or hill or not horn)
15. (wall or not tree)
16. (fork or bread)
17. (not hill or bear or map)
18. (ring or pin)
19. (cake or not fork)
20. (not wall or tree)
21. (sea or jar)
22. (book or plum)
23. (not book or ring)
24. (map or hill or salt)
25. (horn or not bear or hill)
26. (book or not ring)
27. (not book or tree)
28. (nut or iron)
29. (not tree or ship)
30. (not book or moss)
31. (not salt or horn or bear)
32. (sea or not ring)
33. (harp or not sea)
34. (ring or not sea)
35. (not ring or bell)
36. (not tree or book)

Choose any assignment that satisfies all the clauses. What value does fork take in your assignment? Answer with one word: True or False.
```

</details>

### Hypothesis block
Columns 2+ are **(a) outputs** on the items shown, using each theory's decision rule: deterministic theories answer by the sign of their score; stochastic ones keep their probability. **(b)** is the set-level effect vector the theory predicts *if it generated every item* (π = 1), computed over the complete set in the JSONL: P(follows edit | effective) − P(follows edit | null), by distance. It is followed by the set's power for that theory's weight. A model mixing theories produces the π-weighted average of these vectors. **(c)** is the predicted trace.
| Theory | `soft-d1-early-base` | `soft-d1-early-effective` | `soft-d1-early-null` | `soft-d3-early-base` | `soft-d3-early-effective` | `soft-d3-early-null` | (b) eval result | (c) CoT |
|---|---|---|---|---|---|---|---|---|
| `E:BP-0` | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-1` | True (0.93) | False (0.07) | True (0.93) | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +0.00, +0.00, +0.00, +0.00 → pattern [+0000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.15 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.09. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2` | True (0.95) | False (0.05) | True (0.95) | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +0.00, +0.00, +0.00 → pattern [++000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `E:BP-1`; an absent `E:BP-1` is bounded at π ≤ 0.08. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-3` | True (1.00) | False (0.00) | True (1.00) | True (0.99) | False (0.01) | True (0.99) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +0.00, +0.00 → pattern [+++00] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `C1:GREEDY`; an absent `C1:GREEDY` is bounded at π ≤ 0.08. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-4` | True (1.00) | False (0.00) | True (1.00) | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +0.00 → pattern [++++0] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.16 detectable against the nearest distinct competitor `H:SAMPLER`; an absent `H:SAMPLER` is bounded at π ≤ 0.09. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-6` | True (1.00) | False (0.00) | True (1.00) | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `H:SAMPLER`; an absent `H:SAMPLER` is bounded at π ≤ 0.17. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-inf` | True (1.00) | False (0.00) | True (1.00) | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `H:SAMPLER`; an absent `H:SAMPLER` is bounded at π ≤ 0.17. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2-CAUSAL` | True (0.98) | False (0.17) | True (0.98) | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +0.00, +0.00, +0.00, +0.00 → pattern [+0000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.15 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.09. | As BP-t, but every piece of evidence cited comes from clauses read before v's last mention. |
| `E:LOCAL-EXACT-1` | True (0.89) | False (0.11) | True (0.89) | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +0.00, +0.00, +0.00, +0.00 → pattern [+0000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.15 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.09. | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `E:LOCAL-EXACT-3` | True (0.89) | False (0.11) | True (0.89) | True (0.89) | False (0.11) | True (0.89) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +0.00, +0.00 → pattern [+++00] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `C1:GREEDY`; an absent `C1:GREEDY` is bounded at π ≤ 0.08. | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `B1:WP-1` | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `B1:WP-3` | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `E:E-in-D(BP-2 values)` | True (1.00) | False (0.00) | True (1.00) | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `H:SAMPLER`; an absent `H:SAMPLER` is bounded at π ≤ 0.17. | Search with tentative assignments whose values are justified by neighbours' tendencies; propagation; backtracking on conflict. |
| `B1:UP-2` | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1:UP-4` | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1:UP-7` | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1C0:EQ-CONTRACT+POL` | True (1.00) | False (0.00) | True (1.00) | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `H:SAMPLER`; an absent `H:SAMPLER` is bounded at π ≤ 0.17. | Equivalence substitutions ("a = b = c"), then a count of the merged variable's occurrences. |
| `C0:POLARITY` | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | One tally of v's own positive vs negative occurrences, then an immediate decision. |
| `C1:GREEDY` | True (1.00) | False (0.00) | True (1.00) | True (1.00) | True (1.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +0.00, +0.00, +0.00 → pattern [++000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `E:BP-1`; an absent `E:BP-1` is bounded at π ≤ 0.08. | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `D:DPLL-POL(complete)` | True (1.00) | False (0.00) | True (1.00) | True (1.00) | True (1.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +0.00, +1.00, +1.00 → pattern [++0++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.16 detectable against the nearest distinct competitor `H:SAMPLER`; an absent `H:SAMPLER` is bounded at π ≤ 0.09. | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `D:DPLL-POL(b=0)` | True (1.00) | True (1.00) | True (1.00) | True (1.00) | True (1.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `F:WALK-k` | True (0.79) | False (0.40) | True (0.74) | True (0.69) | False (0.32) | True (0.67) | effect (eff−null) by d=1,2,3,4,6: +0.34, +0.45, +0.35, +0.36, +0.10 → pattern [++++~] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.25 detectable against the nearest distinct competitor `NULL:PERCEPTION-NOISE`; an absent `NULL:PERCEPTION-NOISE` is bounded at π ≤ 0.15. | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| `H:SAMPLER` | True (0.89) | False (0.11) | True (0.89) | True (0.89) | False (0.11) | True (0.89) | effect (eff−null) by d=1,2,3,4,6: +0.78, +0.78, +0.78, +0.78, +0.78 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `B1C0:EQ-CONTRACT+POL`; an absent `B1C0:EQ-CONTRACT+POL` is bounded at π ≤ 0.17. | Several complete satisfying assignments listed; answer = majority over them (entailment: conclusion checked in each). |
| `A1:ALWAYS-TRUE` | True (1.00) | True (1.00) | True (1.00) | True (1.00) | True (1.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | No structural reasoning; immediate default answer. |
| `A2:PRIMACY` | False (0.00) | False (0.00) | False (0.00) | True (1.00) | True (1.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | Cites surface features: first/last mention, number of negations, length. |
| `A2:RECENCY` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | False (0.00) | False (0.00) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | Cites surface features: first/last mention, number of negations, length. |
| `NULL:EXACT` | either (both values extend to solutions) | either (both values extend to solutions) | either (both values extend to solutions) | either (both values extend to solutions) | either (both values extend to solutions) | either (both values extend to solutions) | either value is correct; a correct solver implies no soft-edit effect beyond its value heuristic → predicts [00000] unless it samples uniformly (then = H:SAMPLER) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `NULL:NOISY-EXACT` | either | either | either | either | either | either | either value is correct; a correct solver implies no soft-edit effect beyond its value heuristic → predicts [00000] unless it samples uniformly (then = H:SAMPLER) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | As EXACT, with an isolated slip (misread value) in failing traces, located independently of the designed factor. |
| `NULL:PERCEPTION-NOISE` | True (0.80) | False (0.20) | True (0.80) | True (0.78) | False (0.22) | True (0.78) | effect (eff−null) by d=1,2,3,4,6: +0.60, +0.58, +0.56, +0.54, +0.50 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `H:SAMPLER`; an absent `H:SAMPLER` is bounded at π ≤ 0.16. | Correct reasoning applied to a misquoted clause or edge (the trace restates one constraint wrongly). |
| `NULL:RANDOM` | coin flip | coin flip | coin flip | coin flip | coin flip | coin flip | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.18 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.11. | Uninformative trace; answer unrelated to any designed factor. |

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (effect per distance d = 1, 2, 3, 4, 6, early placement), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.05 at full-study size and 0.19 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:BP-1` vs `C0:POLARITY` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-1` vs `B1:UP-7` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-1` vs `B1:WP-3` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-1` vs `H:SAMPLER` | 1.57 | 0.09 | 0.05 | 0.34 | ≥ 99 / 14.9 |
| `E:BP-1` vs `NULL:EXACT` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-3` vs `B1C0:EQ-CONTRACT+POL` | 1.41 | 0.10 | 0.06 | 0.38 | ≥ 99 / 12.0 |
| `E:BP-1` vs `F:WALK-k` | 0.95 | 0.15 | 0.09 | 0.56 | 78.2 / 5.4 |
| `E:BP-1` vs `NULL:PERCEPTION-NOISE` | 1.16 | 0.12 | 0.07 | 0.46 | ≥ 99 / 8.1 |
| `E:BP-1` vs `E:LOCAL-EXACT-1` | 0 | **not separated by this set** | — | — | 0 |
| `E:BP-2` vs `E:BP-2-CAUSAL` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-1` vs `C1:GREEDY` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-1` vs `E:BP-2` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-2` vs `E:BP-3` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-1` vs `E:E-in-D(BP-2 values)` | 2.00 | 0.07 | 0.04 | 0.27 | ≥ 99 / 24.1 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `E:BP-0`, `B1:WP-1`, `B1:WP-3`, `B1:UP-2`, `B1:UP-4`, `B1:UP-7`, `C0:POLARITY`, `D:DPLL-POL(b=0)`, `A1:ALWAYS-TRUE`, `A2:PRIMACY`, `A2:RECENCY`, `NULL:RANDOM`, `NULL:EXACT`, `NULL:NOISY-EXACT` | `F:WALK-k`: 50.4 (dev 3.5) → π ≤ 0.11; `E:BP-1`/`E:BP-2-CAUSAL`/`E:LOCAL-EXACT-1`: 86.9 (dev 6.0) → π ≤ 0.08; `NULL:PERCEPTION-NOISE`: ≥ 99 (dev 9.3) → π ≤ 0.07 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-1`, `E:BP-2-CAUSAL`, `E:LOCAL-EXACT-1` | `F:WALK-k`: 78.2 (dev 5.4) → π ≤ 0.09; `E:BP-0`/`B1:WP-1`/`B1:WP-3`…: 86.9 (dev 6.0) → π ≤ 0.08; `E:BP-2`/`C1:GREEDY`: 86.9 (dev 6.0) → π ≤ 0.08 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-2`, `C1:GREEDY` | `E:BP-1`/`E:BP-2-CAUSAL`/`E:LOCAL-EXACT-1`: 86.9 (dev 6.0) → π ≤ 0.08; `E:BP-3`/`E:LOCAL-EXACT-3`: 86.9 (dev 6.0) → π ≤ 0.08; `F:WALK-k`: 86.9 (dev 6.0) → π ≤ 0.08 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-3`, `E:LOCAL-EXACT-3` | `E:BP-2`/`C1:GREEDY`: 86.9 (dev 6.0) → π ≤ 0.08; `E:BP-4`: 86.9 (dev 6.0) → π ≤ 0.08; `NULL:PERCEPTION-NOISE`: 93.3 (dev 6.5) → π ≤ 0.08 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-4` | `H:SAMPLER`: 69.7 (dev 4.8) → π ≤ 0.09; `NULL:PERCEPTION-NOISE`: 86.5 (dev 6.0) → π ≤ 0.08; `E:BP-3`/`E:LOCAL-EXACT-3`: 86.9 (dev 6.0) → π ≤ 0.08 |  |
| `E:BP-6`, `E:BP-inf`, `E:E-in-D(BP-2 values)`, `B1C0:EQ-CONTRACT+POL` | `H:SAMPLER`: 21.4 (dev 1.5) → π ≤ 0.17; `NULL:PERCEPTION-NOISE`: 86.6 (dev 6.0) → π ≤ 0.08; `E:BP-4`: 86.9 (dev 6.0) → π ≤ 0.08 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `D:DPLL-POL(complete)` | `H:SAMPLER`: 69.7 (dev 4.8) → π ≤ 0.09; `E:BP-6`/`E:BP-inf`/`E:E-in-D(BP-2 values)`…: 86.9 (dev 6.0) → π ≤ 0.08; `NULL:PERCEPTION-NOISE`: 96.8 (dev 6.7) → π ≤ 0.08 |  |
| `F:WALK-k` | `NULL:PERCEPTION-NOISE`: 27.6 (dev 1.9) → π ≤ 0.15; `E:BP-0`/`B1:WP-1`/`B1:WP-3`…: 50.4 (dev 3.5) → π ≤ 0.11; `E:BP-1`/`E:BP-2-CAUSAL`/`E:LOCAL-EXACT-1`: 78.2 (dev 5.4) → π ≤ 0.09 |  |
| `H:SAMPLER` | `E:BP-6`/`E:BP-inf`/`E:E-in-D(BP-2 values)`…: 21.4 (dev 1.5) → π ≤ 0.17; `NULL:PERCEPTION-NOISE`: 22.1 (dev 1.5) → π ≤ 0.16; `E:BP-4`: 69.7 (dev 4.8) → π ≤ 0.09 |  |
| `NULL:PERCEPTION-NOISE` | `H:SAMPLER`: 22.1 (dev 1.5) → π ≤ 0.16; `F:WALK-k`: 27.6 (dev 1.9) → π ≤ 0.15; `E:BP-4`: 86.5 (dev 6.0) → π ≤ 0.08 |  |
| effective and null edits shift the answer *equally* (base vs both) | moves weight to an `A2` negation-count cue; bounds every semantic theory | — |

**Key contrasts.**

- **MP vs C0:** `C0:POLARITY` and `E:BP-0` predict [00000]. Any effect at d ≥ 1 moves weight from them to BP-t; the resolution table gives the bound.
- **MP vs `UP-k` / `WP-t`:** there are no unit clauses, so B1 predicts [00000] at every k. A soft effect moves weight from B1 to BP-t, and a step locates t.
- **MP vs exact:** a correct solver allows either value, so it predicts no effect, and the uniform sampler predicts a flat profile. A step at finite d moves weight from both to BP-t.
- **Not distinguished here:**
  - BP-t vs LOCAL-EXACT-t: same step. See **E3 unanchored** and **E5 loopy**.
  - E-in-D vs the sampler vs EQ-CONTRACT: all flat. See **E1-C** (truncation) and **E5b** (lifts), and the trace (T10 contraction).

---

## 2. E1-S hard channel: a unit clause d hops away
**Reasoning question.** Does a *forcing* constraint d hops away reach the answer? It tests radius for every propagating family. It **cannot** separate MP from `UP-k`, because both step at the same distance; the soft channel (§1) and E2 separate them.
**Controlled factors.** Same skeleton, clause order and names throughout. Each effective edit has a matched null that flips the same number of literals at the same distance (token-identical clauses; only which word carries `not` differs). Negation counts are equal between effective and null.
**Varied factors.** Distance d ∈ {1, 2, 3, 4, 6} (shown: d = 2); version ∈ {base, effective, null}; placement ∈ {early, late} (shown: early).
**Design.** The target v heads an equivalence chain v ≡ c₁ ≡ … ≡ c₆. Every chain variable has a balanced pendant pair, and there is a disconnected filler. The hub is the unit clause (c_d). Effective = (not c_d), which flips the truth; null = negate a pendant leaf next to it.

### Items
**d = 2** (hub `sea`, target `fork`; 26 variables, 34 clauses; negations base/effective/null = 27/28/28).
- `E1-S/hard-d2-early-base`: ground truth: True
- `E1-S/hard-d2-early-effective`: ground truth: False. Edit:
- `3. (sea)`  →  `3. (not sea)`
- `E1-S/hard-d2-early-null`: ground truth: True. Edit:
- `5. (sea or jar)`  →  `5. (sea or not jar)`
<details open><summary>Full prompt: <code>E1-S/hard-d2-early-base</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (moss or not book)
2. (not hill or salt or not map)
3. (sea)
4. (iron or nut)
5. (sea or jar)
6. (not ring or book)
7. (not iron or sea)
8. (ring or not book)
9. (ship or not tree)
10. (book or not tree)
11. (not wall or tree)
12. (hill or horn or not bear)
13. (not salt or horn or bear)
14. (book or plum)
15. (ring or pin)
16. (fork or not iron)
17. (cave or wall)
18. (not book or tree)
19. (cake or not fork)
20. (not iron or lock)
21. (not fork or iron)
22. (not sea or iron)
23. (key or not wall)
24. (bear or map or not hill)
25. (harp or not sea)
26. (not sea or ring)
27. (not tree or wall)
28. (tree or snow)
29. (map or salt or hill)
30. (bell or not ring)
31. (hill or not horn or map)
32. (not salt or not horn or hill)
33. (not ring or sea)
34. (bread or fork)

Every assignment that satisfies all the clauses gives fork the same value. Which value is it? Answer with one word: True or False.
```

</details>

### Hypothesis block
Columns 2+ are **(a) outputs** on the items shown, using each theory's decision rule: deterministic theories answer by the sign of their score; stochastic ones keep their probability. **(b)** is the set-level effect vector the theory predicts *if it generated every item* (π = 1), computed over the complete set in the JSONL: P(follows edit | effective) − P(follows edit | null), by distance. It is followed by the set's power for that theory's weight. A model mixing theories produces the π-weighted average of these vectors. **(c)** is the predicted trace.
| Theory | `hard-d2-early-base` | `hard-d2-early-effective` | `hard-d2-early-null` | (b) eval result | (c) CoT |
|---|---|---|---|---|---|
| `E:BP-0` | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `B1:UP-2`; an absent `B1:UP-2` is bounded at π ≤ 0.08. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-1` | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +0.00, +0.00, +0.00, +0.00 → pattern [+0000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `E:BP-2-CAUSAL`; an absent `E:BP-2-CAUSAL` is bounded at π ≤ 0.16. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +0.00, +0.00, +0.00 → pattern [++000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `E:BP-2-CAUSAL`; an absent `E:BP-2-CAUSAL` is bounded at π ≤ 0.16. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-3` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +0.00, +0.00 → pattern [+++00] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.22 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.13. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-4` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +0.00 → pattern [++++0] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.20 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.12. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-6` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-inf` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2-CAUSAL` | tie (0.50) | False (0.00) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +0.50, +0.00, +0.00, +0.00 → pattern [++000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `B1:UP-2`; an absent `B1:UP-2` is bounded at π ≤ 0.16. | As BP-t, but every piece of evidence cited comes from clauses read before v's last mention. |
| `E:LOCAL-EXACT-1` | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +0.00, +0.00, +0.00, +0.00 → pattern [+0000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `E:BP-2-CAUSAL`; an absent `E:BP-2-CAUSAL` is bounded at π ≤ 0.16. | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `E:LOCAL-EXACT-3` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +0.00, +0.00 → pattern [+++00] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.22 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.13. | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `B1:WP-1` | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +0.00, +0.00, +0.00, +0.00 → pattern [+0000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `E:BP-2-CAUSAL`; an absent `E:BP-2-CAUSAL` is bounded at π ≤ 0.16. | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `B1:WP-3` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +0.00, +0.00 → pattern [+++00] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.22 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.13. | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `B1:UP-3` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +0.00, +0.00, +0.00 → pattern [++000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `E:BP-2-CAUSAL`; an absent `E:BP-2-CAUSAL` is bounded at π ≤ 0.16. | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1:WP-2` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +0.00, +0.00, +0.00 → pattern [++000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `E:BP-2-CAUSAL`; an absent `E:BP-2-CAUSAL` is bounded at π ≤ 0.16. | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `E:E-in-D(BP-2 values)` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | Search with tentative assignments whose values are justified by neighbours' tendencies; propagation; backtracking on conflict. |
| `B1:UP-2` | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | effect (eff−null) by d=1,2,3,4,6: +1.00, +0.00, +0.00, +0.00, +0.00 → pattern [+0000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.28 detectable against the nearest distinct competitor `E:BP-2-CAUSAL`; an absent `E:BP-2-CAUSAL` is bounded at π ≤ 0.16. | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1:UP-4` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +0.00, +0.00 → pattern [+++00] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.22 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.13. | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1:UP-7` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1C0:EQ-CONTRACT+POL` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | Equivalence substitutions ("a = b = c"), then a count of the merged variable's occurrences. |
| `C0:POLARITY` | tie (0.50) | tie (0.50) | tie (0.50) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `B1:UP-2`; an absent `B1:UP-2` is bounded at π ≤ 0.08. | One tally of v's own positive vs negative occurrences, then an immediate decision. |
| `C1:GREEDY` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +0.00, +1.00, +0.00 → pattern [++0+0] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.15 detectable against the nearest distinct competitor `F:WALK-k`; an absent `F:WALK-k` is bounded at π ≤ 0.09. | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `D:DPLL-POL(complete)` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `D:DPLL-POL(b=0)` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `F:WALK-k` | True (0.91) | False (0.06) | True (0.89) | effect (eff−null) by d=1,2,3,4,6: +0.95, +0.83, +0.71, +0.45, +0.27 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.29 detectable against the nearest distinct competitor `NULL:PERCEPTION-NOISE`; an absent `NULL:PERCEPTION-NOISE` is bounded at π ≤ 0.17. | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| `H:SAMPLER` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | Several complete satisfying assignments listed; answer = majority over them (entailment: conclusion checked in each). |
| `A1:ALWAYS-TRUE` | True (1.00) | True (1.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `B1:UP-2`; an absent `B1:UP-2` is bounded at π ≤ 0.08. | No structural reasoning; immediate default answer. |
| `A2:PRIMACY` | True (1.00) | True (1.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `B1:UP-2`; an absent `B1:UP-2` is bounded at π ≤ 0.08. | Cites surface features: first/last mention, number of negations, length. |
| `A2:RECENCY` | True (1.00) | True (1.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `B1:UP-2`; an absent `B1:UP-2` is bounded at π ≤ 0.08. | Cites surface features: first/last mention, number of negations, length. |
| `NULL:EXACT` | True (1.00) | False (0.00) | True (1.00) | effect (eff−null) by d=1,2,3,4,6: +1.00, +1.00, +1.00, +1.00, +1.00 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.37. | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `NULL:NOISY-EXACT` | True (0.95) | False (0.05) | True (0.95) | effect (eff−null) by d=1,2,3,4,6: +0.90, +0.90, +0.90, +0.90, +0.90 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.63 detectable against the nearest distinct competitor `B1:UP-7`; an absent `B1:UP-7` is bounded at π ≤ 0.37. | As EXACT, with an isolated slip (misread value) in failing traces, located independently of the designed factor. |
| `NULL:PERCEPTION-NOISE` | True (0.91) | False (0.09) | True (0.91) | effect (eff−null) by d=1,2,3,4,6: +0.85, +0.81, +0.77, +0.73, +0.65 → pattern [+++++] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.41 detectable against the nearest distinct competitor `NULL:NOISY-EXACT`; an absent `NULL:NOISY-EXACT` is bounded at π ≤ 0.24. | Correct reasoning applied to a misquoted clause or edge (the trace restates one constraint wrongly). |
| `NULL:RANDOM` | coin flip | coin flip | coin flip | effect (eff−null) by d=1,2,3,4,6: +0.00, +0.00, +0.00, +0.00, +0.00 → pattern [00000] (+ ≥ 0.15, 0 ≤ 0.05) Power (full study): π ≥ 0.14 detectable against the nearest distinct competitor `B1:UP-2`; an absent `B1:UP-2` is bounded at π ≤ 0.08. | Uninformative trace; answer unrelated to any designed factor. |

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (effect per distance d = 1, 2, 3, 4, 6, early placement), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.05 at full-study size and 0.19 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:BP-2` vs `B1:UP-3` | 0 | **not separated by this set** | — | — | 0 |
| `E:BP-2` vs `B1:WP-2` | 0 | **not separated by this set** | — | — | 0 |
| `E:BP-2` vs `C0:POLARITY` | 1.41 | 0.10 | 0.06 | 0.38 | ≥ 99 / 12.0 |
| `E:BP-2` vs `NULL:EXACT` | 1.73 | 0.08 | 0.05 | 0.31 | ≥ 99 / 18.0 |
| `E:BP-2` vs `B1C0:EQ-CONTRACT+POL` | 1.73 | 0.08 | 0.05 | 0.31 | ≥ 99 / 18.0 |
| `E:BP-2` vs `F:WALK-k` | 0.90 | 0.16 | 0.09 | 0.59 | 70.4 / 4.9 |
| `E:BP-2` vs `NULL:PERCEPTION-NOISE` | 1.27 | 0.11 | 0.06 | 0.42 | ≥ 99 / 9.7 |
| `E:BP-1` vs `E:BP-2` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |
| `E:BP-2` vs `C1:GREEDY` | 1.00 | 0.14 | 0.08 | 0.53 | 86.9 / 6.0 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `E:BP-0`, `C0:POLARITY`, `A1:ALWAYS-TRUE`, `A2:PRIMACY`, `A2:RECENCY`, `NULL:RANDOM` | `E:BP-1`/`E:LOCAL-EXACT-1`/`B1:WP-1`…: 86.9 (dev 6.0) → π ≤ 0.08; `E:BP-2-CAUSAL`: ≥ 99 (dev 7.5) → π ≤ 0.07; `E:BP-2`/`B1:UP-3`/`B1:WP-2`: ≥ 99 (dev 12.0) → π ≤ 0.06 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-1`, `E:LOCAL-EXACT-1`, `B1:WP-1`, `B1:UP-2` | `E:BP-2-CAUSAL`: 21.7 (dev 1.5) → π ≤ 0.16; `E:BP-0`/`C0:POLARITY`/`A1:ALWAYS-TRUE`…: 86.9 (dev 6.0) → π ≤ 0.08; `E:BP-2`/`B1:UP-3`/`B1:WP-2`: 86.9 (dev 6.0) → π ≤ 0.08 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-2`, `B1:UP-3`, `B1:WP-2` | `E:BP-2-CAUSAL`: 21.7 (dev 1.5) → π ≤ 0.16; `F:WALK-k`: 70.4 (dev 4.9) → π ≤ 0.09; `E:BP-1`/`E:LOCAL-EXACT-1`/`B1:WP-1`…: 86.9 (dev 6.0) → π ≤ 0.08 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-3`, `E:LOCAL-EXACT-3`, `B1:WP-3`, `B1:UP-4` | `F:WALK-k`: 34.0 (dev 2.4) → π ≤ 0.13; `E:BP-2`/`B1:UP-3`/`B1:WP-2`: 86.9 (dev 6.0) → π ≤ 0.08; `E:BP-4`: 86.9 (dev 6.0) → π ≤ 0.08 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-4` | `F:WALK-k`: 42.6 (dev 3.0) → π ≤ 0.12; `NULL:PERCEPTION-NOISE`: 52.5 (dev 3.6) → π ≤ 0.11; `NULL:NOISY-EXACT`: 73.8 (dev 5.1) → π ≤ 0.09 |  |
| `E:BP-6`, `E:BP-inf`, `E:E-in-D(BP-2 values)`, `B1:UP-7`, `B1C0:EQ-CONTRACT+POL`, `D:DPLL-POL(complete)`, `D:DPLL-POL(b=0)`, `H:SAMPLER`, `NULL:EXACT` | `NULL:NOISY-EXACT`: 4.3 (dev 0.3) → π ≤ 0.37; `NULL:PERCEPTION-NOISE`: 26.7 (dev 1.8) → π ≤ 0.15; `F:WALK-k`: 82.6 (dev 5.7) → π ≤ 0.08 | the listed theories are tied here; E3 unanchored and E5 loopy (BP vs LOCAL-EXACT); E1-C truncation and E5b lifts (sampler vs EQ-CONTRACT vs E-in-D); the soft channel and E2 (BP vs UP-k); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-2-CAUSAL` | `E:BP-1`/`E:LOCAL-EXACT-1`/`B1:WP-1`…: 21.7 (dev 1.5) → π ≤ 0.16; `E:BP-2`/`B1:UP-3`/`B1:WP-2`: 21.7 (dev 1.5) → π ≤ 0.16; `F:WALK-k`: 77.4 (dev 5.4) → π ≤ 0.09 |  |
| `C1:GREEDY` | `F:WALK-k`: 79.1 (dev 5.5) → π ≤ 0.09; `E:BP-2`/`B1:UP-3`/`B1:WP-2`: 86.9 (dev 6.0) → π ≤ 0.08; `E:BP-4`: 86.9 (dev 6.0) → π ≤ 0.08 |  |
| `F:WALK-k` | `NULL:PERCEPTION-NOISE`: 20.4 (dev 1.4) → π ≤ 0.17; `E:BP-3`/`E:LOCAL-EXACT-3`/`B1:WP-3`…: 34.0 (dev 2.4) → π ≤ 0.13; `E:BP-4`: 42.6 (dev 3.0) → π ≤ 0.12 |  |
| `NULL:NOISY-EXACT` | `E:BP-6`/`E:BP-inf`/`E:E-in-D(BP-2 values)`…: 4.3 (dev 0.3) → π ≤ 0.37; `NULL:PERCEPTION-NOISE`: 10.4 (dev 0.7) → π ≤ 0.24; `F:WALK-k`: 55.8 (dev 3.9) → π ≤ 0.10 |  |
| `NULL:PERCEPTION-NOISE` | `NULL:NOISY-EXACT`: 10.4 (dev 0.7) → π ≤ 0.24; `F:WALK-k`: 20.4 (dev 1.4) → π ≤ 0.17; `E:BP-6`/`E:BP-inf`/`E:E-in-D(BP-2 values)`…: 26.7 (dev 1.8) → π ≤ 0.15 |  |
| effective and null edits shift the answer *equally* (base vs both) | moves weight to an `A2` negation-count cue; bounds every semantic theory | — |

**Key contrasts.**

- **MP vs C0:** C0 predicts [00000]; a step moves weight from it.
- **MP vs `UP-k`: not separated** (resolution 0 above). `E:BP-t` and `B1:UP-(t+1)` share the profile. See the soft channel (§1) and E2.
- **MP vs exact:** exact predicts a flat +1 profile. A step at finite d bounds exact solving's weight *in that condition*; thinking runs are expected to be flat (global propagation), which is the sanity check.

---

## 3. E1-S placement, framing and growth
**Reasoning question.**

- **Placement:** does a late edit propagate less? `E:BP-t-CAUSAL` says yes; abstract BP says no; `A2:RECENCY` says late edits count *more*.
- **Framing:** does a realistic theme change anything? E predicts no.
- **Growth:** does adding far-away clauses change the answer? E predicts no (size invariance); `NOISY-EXACT` and length cues predict yes.
- `E1-S/soft-d1-late-effective`: Does the answer about the target depend on an edit at graph distance d (beyond a semantic no-op edit of the same size at the same distance)? Ground truth: either value is correct (exact P(fork=True) = 0.11).
<details><summary>Full prompt: <code>E1-S/soft-d1-late-effective</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (bear or not hill or map)
2. (book or not tree)
3. (salt or map or hill)
4. (iron or nut)
5. (book or not ring)
6. (not hill or salt or not map)
7. (not wall or key)
8. (iron or not sea)
9. (not sea or harp)
10. (not salt or horn or bear)
11. (hill or not salt or not horn)
12. (not book or tree)
13. (not book or moss)
14. (not ring or sea)
15. (sea or jar)
16. (tree or snow)
17. (lock or not iron)
18. (not iron or fork)
19. (not fork or iron)
20. (bell or not ring)
21. (ring or not book)
22. (map or not horn or hill)
23. (hill or not bear or horn)
24. (book or plum)
25. (ring or pin)
26. (not tree or wall)
27. (ship or not tree)
28. (not fork or cake)
29. (tree or not wall)
30. (wall or cave)
31. (not sea or ring)
32. (not iron or king)
33. (not iron or coat)
34. (bread or fork)
35. (apple or not iron)
36. (not iron or sea)

Choose any assignment that satisfies all the clauses. What value does fork take in your assignment? Answer with one word: True or False.
```

</details>
- `E1-S/soft-d1-early-effective-switch`: Framing check: same counterfactual under a realistic theme. Ground truth: either value is correct (exact P(fork=ON) = 0.11).
<details><summary>Full prompt: <code>E1-S/soft-d1-early-effective-switch</code></summary>

```text
A control panel has switches; each switch is either ON or OFF. The wiring rules below must all hold. Each rule lists some switch positions, and at least one of them must be the case.

Rules:
Rule 1: iron is OFF, or coat is ON.
Rule 2: book is ON, or plum is ON.
Rule 3: apple is ON, or iron is OFF.
Rule 4: book is ON, or tree is OFF.
Rule 5: king is ON, or iron is OFF.
Rule 6: iron is ON, or fork is OFF.
Rule 7: tree is ON, or book is OFF.
Rule 8: horn is OFF, or hill is ON, or salt is OFF.
Rule 9: jar is ON, or sea is ON.
Rule 10: sea is ON, or iron is OFF.
Rule 11: ring is OFF, or bell is ON.
Rule 12: bread is ON, or fork is ON.
Rule 13: sea is OFF, or iron is ON.
Rule 14: map is ON, or hill is ON, or salt is ON.
Rule 15: pin is ON, or ring is ON.
Rule 16: wall is OFF, or tree is ON.
Rule 17: fork is ON, or iron is OFF.
Rule 18: hill is OFF, or map is OFF, or salt is ON.
Rule 19: bear is ON, or hill is OFF, or map is ON.
Rule 20: tree is OFF, or ship is ON.
Rule 21: horn is ON, or bear is OFF, or hill is ON.
Rule 22: lock is ON, or iron is OFF.
Rule 23: cave is ON, or wall is ON.
Rule 24: tree is OFF, or wall is ON.
Rule 25: moss is ON, or book is OFF.
Rule 26: ring is OFF, or book is ON.
Rule 27: bear is ON, or horn is ON, or salt is OFF.
Rule 28: cake is ON, or fork is OFF.
Rule 29: harp is ON, or sea is OFF.
Rule 30: ring is ON, or sea is OFF.
Rule 31: iron is ON, or nut is ON.
Rule 32: sea is ON, or ring is OFF.
Rule 33: snow is ON, or tree is ON.
Rule 34: wall is OFF, or key is ON.
Rule 35: ring is ON, or book is OFF.
Rule 36: horn is OFF, or map is ON, or hill is ON.

Choose any way of setting the switches that obeys all the rules. In your choice, is fork ON or OFF? Answer with one word: ON or OFF.
```

</details>
- `E1-S/soft-d2-growth`: Size invariance: does growing the formula far from the target change the answer? Ground truth: either value is correct (exact P = 0.89).
<details><summary>Full prompt: <code>E1-S/soft-d2-growth</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (book or plum)
2. (not map or not hill or salt)
3. (fork or bread)
4. (ring or not book)
5. (not fork or cake)
6. (not tree or wall)
7. (not book or moss)
8. (not ring or book)
9. (not hill or bear or map)
10. (not book or tree)
11. (not ring or bell)
12. (iron or nut)
13. (sea or king)
14. (not tree or ship)
15. (iron or not sea)
16. (not sea or harp)
17. (hill or map or not horn)
18. (tree or snow)
19. (not wall or key)
20. (not iron or sea)
21. (bear or horn or not salt)
22. (ring or pin)
23. (sea or not ring)
24. (salt or map or hill)
25. (sea or coat)
26. (fork or not iron)
27. (not iron or lock)
28. (sea or jar)
29. (not sea or ring)
30. (sea or apple)
31. (tree or not wall)
32. (horn or not bear or hill)
33. (wall or cave)
34. (not fork or iron)
35. (book or not tree)
36. (hill or not salt or not horn)
37. (not web or rain or not rope)
38. (rain or rose or not fish)
39. (not rain or fish or not web)
40. (belt or rope or rain)
41. (fish or rain or web)
42. (not rope or rain or not belt)
43. (not rope or rose or not rock)
44. (egg or not rose or not rope)
45. (not rope or not web or egg)
46. (not web or not fish or not egg)

Choose any assignment that satisfies all the clauses. What value does fork take in your assignment? Answer with one word: True or False.
```

</details>

| Theory | `soft-d1-early-effective` | **`soft-d1-late-effective`** | **`…-switch`** (same clauses) | `soft-d2-early-base` | **`soft-d2-growth`** | (b) eval result | (c) CoT |
|---|---|---|---|---|---|---|---|
| `E:BP-1` | False (0.07) | False (0.07) | False (0.07) | tie (0.50) | tie (0.50) | placement-free; framing-free; growth-free (identical outputs) | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2` | False (0.05) | False (0.05) | False (0.05) | True (0.97) | True (0.97) | placement-free; framing-free; growth-free (identical outputs) | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2-CAUSAL` | False (0.17) | True (0.60) | False (0.17) | True (0.94) | tie (0.50) | late placement removes the d=1 effect (computed: early +0.81, late 0.00 over the eff−null contrast) | As BP-t, but every piece of evidence cited comes from clauses read before v's last mention. |
| `E:BP-inf-CAUSAL` | False (0.15) | True (0.60) | False (0.15) | True (0.94) | True (0.56) | placement-free; framing-free; growth-free (identical outputs) | As BP-t, but every piece of evidence cited comes from clauses read before v's last mention. |
| `C0:POLARITY` | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | as computed in columns | One tally of v's own positive vs negative occurrences, then an immediate decision. |
| `C1:GREEDY` | False (0.00) | False (0.00) | False (0.00) | True (1.00) | True (1.00) | as computed in columns | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `H:SAMPLER` | False (0.11) | False (0.11) | False (0.11) | True (0.89) | True (0.89) | as computed in columns | Several complete satisfying assignments listed; answer = majority over them (entailment: conclusion checked in each). |
| `F:WALK-k` | False (0.40) | False (0.35) | False (0.40) | True (0.73) | True (0.74) | as computed in columns | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| `A2:RECENCY` | False (0.00) | True (1.00) | False (0.00) | True (1.00) | False (0.00) | late edits weigh more at every d (here v's own mentions are unchanged, so 0) | Cites surface features: first/last mention, number of negations, length. |
| `NULL:PERCEPTION-NOISE` | False (0.20) | False (0.20) | False (0.20) | True (0.79) | True (0.82) | as computed in columns | Correct reasoning applied to a misquoted clause or edge (the trace restates one constraint wrongly). |

**How these outcomes move weight** (the placement contrast is estimated over the complete E1-S set as the feature term "placement × π\_E"; growth and framing as feature terms on π).

| Observed outcome | Moves weight toward | Moves weight away from |
|---|---|---|
| late placement shrinks the d=1 effect toward 0 | `E:BP-t-CAUSAL` (positive placement term) | abstract `E:BP-t`, `A2:RECENCY` |
| no placement effect | abstract `E:BP-t`, `H:SAMPLER` | `E:BP-t-CAUSAL`, `A2:RECENCY`, order-driven `C1:GREEDY` |
| late edits weigh more at every d | `A2:RECENCY` | all E members |
| growth arm changes the answer | `NULL:NOISY-EXACT`, length cues | E (size invariance), C0 |
| switch framing ≠ bare framing | a framing feature term on π (family I: strategy depends on framing) | a framing-free single procedure |

---

## 4. E1-S colouring: a forcing constraint that singleton propagation cannot see
**Reasoning question.** A diamond (v–a, v–b, a–b, a–w, b–w) forces v and w to share a colour in 3-colouring. Precolouring w therefore fixes v, two hops away. Singleton propagation (`WP`, the hard-message limit) cannot see this, because a and b each keep two colours. BP's soft messages lean v toward w's colour, and the exact answer is forced. So in colouring, this "hard" channel separates **soft MP from hard MP / B1**.
**Controlled factors.** Same graph and edge order. The null renames a free pendant node (relabelling no-op). The effective edit recolours the hub.
- `E1-S-col/hard-d2-base`: ground truth **red** (hub Ed = red).
- `E1-S-col/hard-d2-effective`: ground truth **blue** (hub Ed = blue).
- `E1-S-col/hard-d2-null`: ground truth **red** (hub Ed = red; renamed ('Sam', 'Pam')).
<details open><summary>Full prompt: <code>E1-S-col/hard-d2-base</code></summary>

```text
Each person must be given one of three rooms: red, green or blue. Two people who clash cannot be given the same room.

Clashes:
1. Heidi and Gus
2. Gus and Zoe
3. Ed and Yara
4. Zoe and Ed
5. Tom and Ned
6. Fay and Ola
7. Tom and Jo
8. Sam and Ola
9. Ed and Fay
10. Ola and Yara
11. Ed and Pat
12. Zoe and Pat
13. Yara and Fay
14. Ned and Jo
15. Pat and Gus

Fixed: Ed has already been given the red room.

In every valid assignment Gus gets the same room. Which room? Answer with one word: red, green or blue.
```

</details>

| Theory | base | effective | null | (b) eval result | (c) CoT |
|---|---|---|---|---|---|
| `NULL:EXACT` | red | blue | red | follows the hub (base≠effective, base=null): predicted P(answer = hub colour) ≥ 0.85 in the cell | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `NULL:NOISY-EXACT` | red | blue | red | follows the hub (base≠effective, base=null): predicted P(answer = hub colour) ≥ 0.85 in the cell | As EXACT, with an isolated slip (misread value) in failing traces, located independently of the designed factor. |
| `NULL:RANDOM` | uniform over 3 | uniform over 3 | uniform over 3 | does not follow the hub: predicted P(answer changes with the hub) ≤ 0.05 | Uninformative trace; answer unrelated to any designed factor. |
| `C1:FIRST-FIT` | green | green | green | does not follow the hub: predicted P(answer changes with the hub) ≤ 0.05 | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `C2:DSATUR` | red | blue | red | follows the hub (base≠effective, base=null): predicted P(answer = hub colour) ≥ 0.85 in the cell | Adaptive choice: shortest clause / most constrained node first; no backtracking. |
| `B1:WP-t (singleton propagation)` | blue/green/red | blue/green/red | blue/green/red | does not follow the hub: predicted P(answer changes with the hub) ≤ 0.05 | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `E:BP-0` | tie | tie | tie | does not follow the hub: predicted P(answer changes with the hub) ≤ 0.05 | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-1` | tie | tie | tie | does not follow the hub: predicted P(answer changes with the hub) ≤ 0.05 | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2` | red | blue | red | follows the hub (base≠effective, base=null): predicted P(answer = hub colour) ≥ 0.85 in the cell | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-3` | red | blue | red | follows the hub (base≠effective, base=null): predicted P(answer = hub colour) ≥ 0.85 in the cell | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-4` | red | blue | red | follows the hub (base≠effective, base=null): predicted P(answer = hub colour) ≥ 0.85 in the cell | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-5` | red | blue | red | follows the hub (base≠effective, base=null): predicted P(answer = hub colour) ≥ 0.85 in the cell | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:LOCAL-1 (Jones-Plassmann)` | green | green | green | does not follow the hub: predicted P(answer changes with the hub) ≤ 0.05 | Rounds in which nodes that outrank all uncoloured neighbours pick a colour; leftover nodes guess at once. |
| `E:LOCAL-2 (Jones-Plassmann)` | green | green | green | does not follow the hub: predicted P(answer changes with the hub) ≤ 0.05 | Rounds in which nodes that outrank all uncoloured neighbours pick a colour; leftover nodes guess at once. |
| `E:LOCAL-4 (Jones-Plassmann)` | green | green | green | does not follow the hub: predicted P(answer changes with the hub) ≤ 0.05 | Rounds in which nodes that outrank all uncoloured neighbours pick a colour; leftover nodes guess at once. |

**Full-assignment variant** (`E1-S-col/full-base`: same graph, asking for everyone's room). Clashing edges in each theory's full answer:

| Theory | clashes |
|---|---|
| `NULL:EXACT` | 0 |
| `C1:FIRST-FIT` | 0 |
| `C2:DSATUR` | 0 |
| `E:LOCAL-1 (Jones-Plassmann)` | 5 |
| `E:LOCAL-2 (Jones-Plassmann)` | 2 |
| `E:LOCAL-4 (Jones-Plassmann)` | 0 |
| `E:BP-1` | 7 |
| `E:BP-2` | 7 |
| `E:BP-5` | 5 |
| `B1:WP-t (singleton propagation)` | 7 |
| `NULL:RANDOM` | 5.0 |
<details><summary>Full prompt: <code>E1-S-col/full-base</code></summary>

```text
Each person must be given one of three rooms: red, green or blue. Two people who clash cannot be given the same room.

Clashes:
1. Heidi and Gus
2. Gus and Zoe
3. Ed and Yara
4. Zoe and Ed
5. Tom and Ned
6. Fay and Ola
7. Tom and Jo
8. Sam and Ola
9. Ed and Fay
10. Ola and Yara
11. Ed and Pat
12. Zoe and Pat
13. Yara and Fay
14. Ned and Jo
15. Pat and Gus

Fixed: Ed has already been given the red room.

Give a valid room for every person. Answer with a JSON object mapping each person to red, green or blue.
```

</details>

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (P(answer = hub colour) on base, effective, null, plus P(edge clashes) for each edge of the full-assignment variant), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.05 at full-study size and 0.19 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:BP-2` vs `B1:WP-t (singleton propagation)` | 1.73 | 0.08 | 0.05 | 0.31 | ≥ 99 / 18.0 |
| `E:BP-2` vs `NULL:EXACT` | 2.65 | 0.05 | 0.03 | 0.20 | ≥ 99 / 42.1 |
| `E:BP-2` vs `C1:FIRST-FIT` | 3.16 | 0.04 | 0.03 | 0.17 | ≥ 99 / 60.2 |
| `E:BP-2` vs `C2:DSATUR` | 2.65 | 0.05 | 0.03 | 0.20 | ≥ 99 / 42.1 |
| `E:BP-1` vs `E:BP-2` | 1.15 | 0.12 | 0.07 | 0.46 | ≥ 99 / 8.0 |
| `E:BP-2` vs `E:LOCAL-2 (Jones-Plassmann)` | 2.83 | 0.05 | 0.03 | 0.19 | ≥ 99 / 48.1 |
| `E:LOCAL-1 (Jones-Plassmann)` vs `C1:FIRST-FIT` | 2.24 | 0.06 | 0.04 | 0.24 | ≥ 99 / 30.1 |
| `E:BP-2` vs `NULL:RANDOM` | 2.31 | 0.06 | 0.04 | 0.23 | ≥ 99 / 32.1 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `NULL:EXACT`, `NULL:NOISY-EXACT`, `C2:DSATUR`, `E:BP-3`, `E:BP-4` | `E:BP-0`: ≥ 99 (dev 8.0) → π ≤ 0.07; `NULL:RANDOM`: ≥ 99 (dev 18.0) → π ≤ 0.05; `C1:FIRST-FIT`/`E:LOCAL-4 (Jones-Plassmann)`: ≥ 99 (dev 18.0) → π ≤ 0.05 | the listed theories are tied here; E1-C (truncation) and E3 (cover pairs) for BP vs exact; the coverage matrix (end of document) lists the sets that separate them |
| `NULL:RANDOM` | `E:BP-0`: ≥ 99 (dev 10.0) → π ≤ 0.06; `C1:FIRST-FIT`/`E:LOCAL-4 (Jones-Plassmann)`: ≥ 99 (dev 12.0) → π ≤ 0.06; `E:LOCAL-2 (Jones-Plassmann)`: ≥ 99 (dev 16.0) → π ≤ 0.05 |  |
| `C1:FIRST-FIT`, `E:LOCAL-4 (Jones-Plassmann)` | `E:BP-0`: 29.0 (dev 2.0) → π ≤ 0.14; `NULL:RANDOM`: ≥ 99 (dev 12.0) → π ≤ 0.06; `E:LOCAL-2 (Jones-Plassmann)`: ≥ 99 (dev 12.0) → π ≤ 0.06 | the listed theories are tied here; E1-C (truncation) and E3 (cover pairs) for BP vs exact; the coverage matrix (end of document) lists the sets that separate them |
| `B1:WP-t (singleton propagation)` | `E:BP-1`: 29.0 (dev 2.0) → π ≤ 0.14; `E:BP-2`: ≥ 99 (dev 18.0) → π ≤ 0.05; `NULL:RANDOM`: ≥ 99 (dev 26.1) → π ≤ 0.04 |  |
| `E:BP-0` | `C1:FIRST-FIT`/`E:LOCAL-4 (Jones-Plassmann)`: 29.0 (dev 2.0) → π ≤ 0.14; `NULL:EXACT`/`NULL:NOISY-EXACT`/`C2:DSATUR`…: ≥ 99 (dev 8.0) → π ≤ 0.07; `NULL:RANDOM`: ≥ 99 (dev 10.0) → π ≤ 0.06 |  |
| `E:BP-1` | `B1:WP-t (singleton propagation)`: 29.0 (dev 2.0) → π ≤ 0.14; `E:BP-2`: ≥ 99 (dev 8.0) → π ≤ 0.07; `E:BP-5`: ≥ 99 (dev 20.1) → π ≤ 0.05 |  |
| `E:BP-2` | `E:BP-1`: ≥ 99 (dev 8.0) → π ≤ 0.07; `E:BP-5`: ≥ 99 (dev 12.0) → π ≤ 0.06; `B1:WP-t (singleton propagation)`: ≥ 99 (dev 18.0) → π ≤ 0.05 |  |
| `E:BP-5` | `E:BP-2`: ≥ 99 (dev 12.0) → π ≤ 0.06; `E:BP-1`: ≥ 99 (dev 20.1) → π ≤ 0.05; `NULL:RANDOM`: ≥ 99 (dev 28.1) → π ≤ 0.04 |  |
| `E:LOCAL-1 (Jones-Plassmann)` | `E:LOCAL-2 (Jones-Plassmann)`: ≥ 99 (dev 18.0) → π ≤ 0.05; `NULL:RANDOM`: ≥ 99 (dev 22.1) → π ≤ 0.04; `C1:FIRST-FIT`/`E:LOCAL-4 (Jones-Plassmann)`: ≥ 99 (dev 30.1) → π ≤ 0.04 |  |
| `E:LOCAL-2 (Jones-Plassmann)` | `C1:FIRST-FIT`/`E:LOCAL-4 (Jones-Plassmann)`: ≥ 99 (dev 12.0) → π ≤ 0.06; `E:BP-0`: ≥ 99 (dev 14.0) → π ≤ 0.05; `NULL:RANDOM`: ≥ 99 (dev 16.0) → π ≤ 0.05 |  |

**Not separated here:** BP-t (t ≥ 2) vs exact, since both track the hub. See E1-C and E3.

---

## 5. E1-C periphery–core: does local soft evidence pull the answer off the truth?
**Reasoning question.** The truth about v is fixed by a hard random core, joined to v through v ≡ u ≡ c\*, where c\* is a backbone variable that BP can't see. A soft hub d hops out on a separate chain is toward / neutral / against the truth. Does the answer follow the hub, and only for d ≤ r? This is the primary best-effort test: above the budget line, a thinking model that can't finish the core must fall back on something.
**Controlled factors.** The truth is identical across S (asserted). The same core, chain and order within an O level. Negation counts are equal across S (4 balancing clauses). Names are fixed.
**Varied factors.** S ∈ {toward, neutral, against}; d ∈ {1, 2, 4, 6}; chain order O ∈ {hub→v, v→hub}. Shown: d = 2.
Core: 10 variables, 41 clauses (seed 530), c\* = `tree`. Target `nut`, hub `snow`. Ground truth for all items: **False**.
- `E1-C/d2-hub->v-neutral` vs `E1-C/d2-hub->v-toward`:
- `2. (not book or pond or bear)`  →  `2. (pond or not book or bear)`
- `3. (star or pear)`  →  `3. (pear or star)`
- `4. (frog or pond or pin)`  →  `4. (pond or frog or pin)`
- `5. (fork or not ball or tree)`  →  `5. (not ball or tree or fork)`
- `6. (harp or not snow)`  →  `6. (not snow or harp)`
- `7. (reed or not snow)`  →  `7. (not snow or reed)`
- `8. (cup or not snow)`  →  `8. (snow or cup)`
- `9. (not snow or leaf)`  →  `9. (snow or leaf)`
- `10. (not snow or salt)`  →  `10. (salt or not snow)`
- `11. (ship or fork or pin)`  →  `11. (fork or ship or pin)`
- `14. (sea or sock)`  →  `14. (not sock or sea)`
- `15. (cat or gold)`  →  `15. (not gold or cat)`
- `16. (nail or tree or pin)`  →  `16. (nail or pin or tree)`
- `17. (not ball or bear or pond)`  →  `17. (pond or bear or not ball)`
- `19. (ball or frog or not bear)`  →  `19. (ball or not bear or frog)`
- `20. (not nail or pin or not tree)`  →  `20. (not tree or pin or not nail)`
- `23. (book or fork or not ship)`  →  `23. (not ship or fork or book)`
- `24. (not ball or ship or not nail)`  →  `24. (ship or not ball or not nail)`
- `25. (not frog or nail or book)`  →  `25. (nail or book or not frog)`
- `26. (ball or not fork or not bear)`  →  `26. (not bear or ball or not fork)`
- `28. (ship or pin or tree)`  →  `28. (ship or tree or pin)`
- `29. (nail or not ball or not ship)`  →  `29. (not ship or nail or not ball)`
- `30. (fork or not nail or not ball)`  →  `30. (not ball or fork or not nail)`
- `31. (rain or king)`  →  `31. (king or rain)`
- `33. (not oak or snow)`  →  `33. (snow or not oak)`
- `34. (not ball or pin or not pond)`  →  `34. (pin or not ball or not pond)`
- `37. (nail or frog or not book)`  →  `37. (not book or nail or frog)`
- `38. (bear or book or ball)`  →  `38. (book or bear or ball)`
- `39. (not frog or not book or ship)`  →  `39. (not book or ship or not frog)`
- `40. (cake or snow)`  →  `40. (snow or cake)`
- `41. (not star or pen)`  →  `41. (pen or not star)`
- `45. (book or pin or not tree)`  →  `45. (book or not tree or pin)`
- `47. (ship or bear or not pond)`  →  `47. (not pond or ship or bear)`
- `48. (bird or salt)`  →  `48. (salt or bird)`
- `49. (not pin or frog or nail)`  →  `49. (not pin or nail or frog)`
- `50. (pin or book or frog)`  →  `50. (book or frog or pin)`
- `51. (not frog or ball or not nail)`  →  `51. (ball or not frog or not nail)`
- `52. (not frog or not tree or not nail)`  →  `52. (not nail or not frog or not tree)`
- `53. (nail or not ship or not ball)`  →  `53. (not ship or not ball or nail)`
- `55. (star or not egg)`  →  `55. (not egg or star)`
- `56. (not tree or pin or pond)`  →  `56. (pin or pond or not tree)`
- `57. (not star or egg)`  →  `57. (egg or not star)`
- `58. (pond or not bear or nail)`  →  `58. (nail or pond or not bear)`
- `59. (not fork or not frog or ship)`  →  `59. (ship or not fork or not frog)`
- `60. (oak or nest)`  →  `60. (nest or oak)`
- `61. (not hill or egg)`  →  `61. (egg or not hill)`
- `63. (not frog or tree or fork)`  →  `63. (tree or fork or not frog)`
- `64. (not fork or ship or not nail)`  →  `64. (ship or not nail or not fork)`
- `65. (nail or pond or bear)`  →  `65. (pond or nail or bear)`
- `68. (iron or not snow)`  →  `68. (not snow or iron)`
- `69. (not ship or not bear or not frog)`  →  `69. (not bear or not frog or not ship)`
- `70. (not book or not frog or bear)`  →  `70. (not frog or not book or bear)`
- `71. (not tree or not book or ball)`  →  `71. (ball or not tree or not book)`
- `73. (not tree or not nail or pond)`  →  `73. (pond or not tree or not nail)`
- `E1-C/d2-hub->v-against` vs `E1-C/d2-hub->v-toward`:
- `1. (tree or pond or fork)`  →  `1. (fork or tree or pond)`
- `2. (not book or pond or bear)`  →  `2. (pond or not book or bear)`
- `3. (star or pear)`  →  `3. (pear or star)`
- `4. (frog or pond or pin)`  →  `4. (pond or pin or frog)`
- `5. (fork or not ball or tree)`  →  `5. (tree or not ball or fork)`
- `6. (harp or not snow)`  →  `6. (harp or snow)`
- `7. (reed or not snow)`  →  `7. (snow or reed)`
- `8. (cup or not snow)`  →  `8. (snow or cup)`
- `9. (not snow or leaf)`  →  `9. (leaf or snow)`
- `11. (ship or fork or pin)`  →  `11. (pin or ship or fork)`
- `12. (not salt or snow)`  →  `12. (snow or not salt)`
- `13. (sage or not egg)`  →  `13. (not egg or sage)`
- `14. (sea or sock)`  →  `14. (not sock or sea)`
- `15. (cat or gold)`  →  `15. (not cat or gold)`
- `16. (nail or tree or pin)`  →  `16. (tree or nail or pin)`
- `17. (not ball or bear or pond)`  →  `17. (not ball or pond or bear)`
- `18. (not salt or nut)`  →  `18. (nut or not salt)`
- `19. (ball or frog or not bear)`  →  `19. (frog or not bear or ball)`
- `20. (not nail or pin or not tree)`  →  `20. (not tree or not nail or pin)`
- `22. (tree or ball or not fork)`  →  `22. (ball or tree or not fork)`
- `23. (book or fork or not ship)`  →  `23. (not ship or fork or book)`
- `25. (not frog or nail or book)`  →  `25. (nail or book or not frog)`
- `26. (ball or not fork or not bear)`  →  `26. (ball or not bear or not fork)`
- `27. (pin or not ship or not ball)`  →  `27. (not ball or pin or not ship)`
- `28. (ship or pin or tree)`  →  `28. (ship or tree or pin)`
- `29. (nail or not ball or not ship)`  →  `29. (not ball or not ship or nail)`
- `30. (fork or not nail or not ball)`  →  `30. (not nail or not ball or fork)`
- `31. (rain or king)`  →  `31. (not rain or king)`
- `34. (not ball or pin or not pond)`  →  `34. (not pond or pin or not ball)`
- `35. (fire or milk)`  →  `35. (not milk or fire)`
- `37. (nail or frog or not book)`  →  `37. (frog or nail or not book)`
- `38. (bear or book or ball)`  →  `38. (ball or bear or book)`
- `39. (not frog or not book or ship)`  →  `39. (not frog or ship or not book)`
- `40. (cake or snow)`  →  `40. (snow or cake)`
- `41. (not star or pen)`  →  `41. (pen or not star)`
- `42. (oak or not star)`  →  `42. (not star or oak)`
- `44. (map or not hill)`  →  `44. (not hill or map)`
- `47. (ship or bear or not pond)`  →  `47. (bear or not pond or ship)`
- `48. (bird or salt)`  →  `48. (salt or bird)`
- `49. (not pin or frog or nail)`  →  `49. (nail or not pin or frog)`
- `50. (pin or book or frog)`  →  `50. (book or pin or frog)`
- `51. (not frog or ball or not nail)`  →  `51. (ball or not frog or not nail)`
- `52. (not frog or not tree or not nail)`  →  `52. (not tree or not nail or not frog)`
- `53. (nail or not ship or not ball)`  →  `53. (not ball or not ship or nail)`
- `56. (not tree or pin or pond)`  →  `56. (pond or not tree or pin)`
- `57. (not star or egg)`  →  `57. (egg or not star)`
- `58. (pond or not bear or nail)`  →  `58. (not bear or nail or pond)`
- `59. (not fork or not frog or ship)`  →  `59. (not frog or ship or not fork)`
- `62. (pond or not ship or not fork)`  →  `62. (not ship or pond or not fork)`
- `63. (not frog or tree or fork)`  →  `63. (tree or not frog or fork)`
- `64. (not fork or ship or not nail)`  →  `64. (ship or not fork or not nail)`
- `65. (nail or pond or bear)`  →  `65. (nail or bear or pond)`
- `66. (not salt or rock)`  →  `66. (rock or not salt)`
- `68. (iron or not snow)`  →  `68. (not snow or iron)`
- `70. (not book or not frog or bear)`  →  `70. (not book or bear or not frog)`
- `72. (not ship or not ball or not pond)`  →  `72. (not ball or not pond or not ship)`
- `73. (not tree or not nail or pond)`  →  `73. (not tree or pond or not nail)`
- `E1-C/d2-v->hub-against` vs `E1-C/d2-hub->v-toward`:
- `1. (tree or pond or fork)`  →  `1. (not frog or bear or not book)`
- `2. (not book or pond or bear)`  →  `2. (not hill or egg)`
- `3. (star or pear)`  →  `3. (not sock or sea)`
- `4. (frog or pond or pin)`  →  `4. (not star or pen)`
- `5. (fork or not ball or tree)`  →  `5. (pin or not tree or book)`
- `6. (harp or not snow)`  →  `6. (hill or not egg)`
- `7. (reed or not snow)`  →  `7. (not bear or not ship or not frog)`
- `8. (cup or not snow)`  →  `8. (pear or star)`
- `9. (not snow or leaf)`  →  `9. (bear or pond or nail)`
- `10. (not snow or salt)`  →  `10. (not book or ball or not tree)`
- `11. (ship or fork or pin)`  →  `11. (not salt or rock)`
- `12. (not salt or snow)`  →  `12. (not ball or pond or bear)`
- `13. (sage or not egg)`  →  `13. (fork or tree or not frog)`
- `14. (sea or sock)`  →  `14. (star or not egg)`
- `15. (cat or gold)`  →  `15. (tree or pond or fork)`
- `16. (nail or tree or pin)`  →  `16. (not pond or not ball or pin)`
- `17. (not ball or bear or pond)`  →  `17. (not ship or book or fork)`
- `18. (not salt or nut)`  →  `18. (egg or not star)`
- `19. (ball or frog or not bear)`  →  `19. (oak or not star)`
- `20. (not nail or pin or not tree)`  →  `20. (not fork or ship or not frog)`
- `21. (egg or rope)`  →  `21. (ball or not nail or not frog)`
- `22. (tree or ball or not fork)`  →  `22. (not ship or not ball or nail)`
- `23. (book or fork or not ship)`  →  `23. (ship or bear or not pond)`
- `24. (not ball or ship or not nail)`  →  `24. (map or not hill)`
- `25. (not frog or nail or book)`  →  `25. (star or not oak)`
- `26. (ball or not fork or not bear)`  →  `26. (not frog or not book or ship)`
- `27. (pin or not ship or not ball)`  →  `27. (not nail or not tree or not frog)`
- `28. (ship or pin or tree)`  →  `28. (book or frog or pin)`
- `29. (nail or not ball or not ship)`  →  `29. (not bear or ball or frog)`
- `30. (fork or not nail or not ball)`  →  `30. (not ball or not ship or not pond)`
- `31. (rain or king)`  →  `31. (not ball or not nail or fork)`
- `32. (salt or not nut)`  →  `32. (pin or not tree or not nail)`
- `33. (not oak or snow)`  →  `33. (frog or pin or pond)`
- `34. (not ball or pin or not pond)`  →  `34. (rope or egg)`
- `35. (fire or milk)`  →  `35. (ship or pin or fork)`
- `36. (not snow or oak)`  →  `36. (nail or pin or tree)`
- `37. (nail or frog or not book)`  →  `37. (not bear or nail or pond)`
- `38. (bear or book or ball)`  →  `38. (tree or ball or not fork)`
- `39. (not frog or not book or ship)`  →  `39. (frog or not pin or nail)`
- `40. (cake or snow)`  →  `40. (not gold or cat)`
- `41. (not star or pen)`  →  `41. (not rain or king)`
- `42. (oak or not star)`  →  `42. (not book or nail or frog)`
- `43. (star or not oak)`  →  `43. (iron or not snow)`
- `44. (map or not hill)`  →  `44. (book or ball or bear)`
- `45. (book or pin or not tree)`  →  `45. (salt or bird)`
- `46. (hill or horn)`  →  `46. (not ball or not ship or nail)`
- `47. (ship or bear or not pond)`  →  `47. (pond or not nail or not tree)`
- `48. (bird or salt)`  →  `48. (not oak or snow)`
- `49. (not pin or frog or nail)`  →  `49. (not snow or oak)`
- `50. (pin or book or frog)`  →  `50. (pin or not ball or not ship)`
- `51. (not frog or ball or not nail)`  →  `51. (not salt or nut)`
- `52. (not frog or not tree or not nail)`  →  `52. (salt or not nut)`
- `53. (nail or not ship or not ball)`  →  `53. (book or nail or not frog)`
- `54. (not oak or ring)`  →  `54. (not snow or salt)`
- `55. (star or not egg)`  →  `55. (snow or not salt)`
- `56. (not tree or pin or pond)`  →  `56. (harp or snow)`
- `57. (not star or egg)`  →  `57. (snow or reed)`
- `58. (pond or not bear or nail)`  →  `58. (cup or snow)`
- `59. (not fork or not frog or ship)`  →  `59. (leaf or snow)`
- `60. (oak or nest)`  →  `60. (tree or pin or ship)`
- `61. (not hill or egg)`  →  `61. (oak or nest)`
- `62. (pond or not ship or not fork)`  →  `62. (not fire or milk)`
- `63. (not frog or tree or fork)`  →  `63. (hill or horn)`
- `64. (not fork or ship or not nail)`  →  `64. (not egg or sage)`
- `65. (nail or pond or bear)`  →  `65. (ball or not bear or not fork)`
- `66. (not salt or rock)`  →  `66. (not book or pond or bear)`
- `67. (hill or not egg)`  →  `67. (not tree or pond or pin)`
- `68. (iron or not snow)`  →  `68. (ring or not oak)`
- `69. (not ship or not bear or not frog)`  →  `69. (not fork or not ship or pond)`
- `70. (not book or not frog or bear)`  →  `70. (not ball or tree or fork)`
- `71. (not tree or not book or ball)`  →  `71. (not fork or not nail or ship)`
- `72. (not ship or not ball or not pond)`  →  `72. (not ball or not nail or ship)`
- `73. (not tree or not nail or pond)`  →  `73. (snow or cake)`
<details open><summary>Full prompt: <code>E1-C/d2-hub->v-toward</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (tree or pond or fork)
2. (not book or pond or bear)
3. (star or pear)
4. (frog or pond or pin)
5. (fork or not ball or tree)
6. (harp or not snow)
7. (reed or not snow)
8. (cup or not snow)
9. (not snow or leaf)
10. (not snow or salt)
11. (ship or fork or pin)
12. (not salt or snow)
13. (sage or not egg)
14. (sea or sock)
15. (cat or gold)
16. (nail or tree or pin)
17. (not ball or bear or pond)
18. (not salt or nut)
19. (ball or frog or not bear)
20. (not nail or pin or not tree)
21. (egg or rope)
22. (tree or ball or not fork)
23. (book or fork or not ship)
24. (not ball or ship or not nail)
25. (not frog or nail or book)
26. (ball or not fork or not bear)
27. (pin or not ship or not ball)
28. (ship or pin or tree)
29. (nail or not ball or not ship)
30. (fork or not nail or not ball)
31. (rain or king)
32. (salt or not nut)
33. (not oak or snow)
34. (not ball or pin or not pond)
35. (fire or milk)
36. (not snow or oak)
37. (nail or frog or not book)
38. (bear or book or ball)
39. (not frog or not book or ship)
40. (cake or snow)
41. (not star or pen)
42. (oak or not star)
43. (star or not oak)
44. (map or not hill)
45. (book or pin or not tree)
46. (hill or horn)
47. (ship or bear or not pond)
48. (bird or salt)
49. (not pin or frog or nail)
50. (pin or book or frog)
51. (not frog or ball or not nail)
52. (not frog or not tree or not nail)
53. (nail or not ship or not ball)
54. (not oak or ring)
55. (star or not egg)
56. (not tree or pin or pond)
57. (not star or egg)
58. (pond or not bear or nail)
59. (not fork or not frog or ship)
60. (oak or nest)
61. (not hill or egg)
62. (pond or not ship or not fork)
63. (not frog or tree or fork)
64. (not fork or ship or not nail)
65. (nail or pond or bear)
66. (not salt or rock)
67. (hill or not egg)
68. (iron or not snow)
69. (not ship or not bear or not frog)
70. (not book or not frog or bear)
71. (not tree or not book or ball)
72. (not ship or not ball or not pond)
73. (not tree or not nail or pond)
74. (nut or not apple)
75. (not nut or apple)
76. (apple or not tree)
77. (not apple or tree)

Every assignment that satisfies all the clauses gives nut the same value. Which value is it? Answer with one word: True or False.
```

</details>

### Hypothesis block
**(b)** = predicted accuracy(toward) − accuracy(against), computed over the complete set, for (d, O) = (1, h→v), (1, v→h), (2, h→v), (2, v→h), (4, h→v), (4, v→h), (6, h→v), (6, v→h).
| Theory | `d2-hub->v-toward` | `d2-hub->v-neutral` | `d2-hub->v-against` | `d2-v->hub-against` | (b) eval result | (c) CoT |
|---|---|---|---|---|---|---|
| `E:BP-0` | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-1` | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | Δacc: +1.00, +1.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [++000000] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2` | False (0.01) | tie (0.50) | True (0.99) | True (0.99) | Δacc: +1.00, +1.00, +1.00, +1.00, +0.00, +0.00, +0.00, +0.00 → [++++0000] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-3` | False (0.01) | True (0.60) | True (1.00) | True (1.00) | Δacc: +1.00, +1.00, +1.00, +1.00, +0.00, +0.00, +0.00, +0.00 → [++++0000] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-6` | False (0.00) | True (0.76) | True (1.00) | True (1.00) | Δacc: +1.00, +1.00, +1.00, +1.00, +1.00, +1.00, +1.00, +1.00 → [++++++++] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-inf` | False (0.00) | True (1.00) | True (1.00) | True (1.00) | Δacc: +1.00, +1.00, +1.00, +1.00, +1.00, +1.00, +1.00, +1.00 → [++++++++] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2-CAUSAL` | False (0.01) | False (0.22) | True (0.90) | False (0.31) | Δacc: +1.00, +0.00, +1.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [+0+00000] | As BP-t, but every piece of evidence cited comes from clauses read before v's last mention. |
| `E:BP-inf-CAUSAL` | False (0.00) | False (0.16) | True (0.93) | False (0.28) | Δacc: +1.00, +0.00, +1.00, +0.00, +1.00, +0.00, +1.00, +0.00 → [+0+0+0+0] | As BP-t, but every piece of evidence cited comes from clauses read before v's last mention. |
| `E:LOCAL-EXACT-2` | False (0.00) | True (1.00) | True (1.00) | True (1.00) | Δacc: +1.00, +1.00, +1.00, +1.00, +0.00, +0.00, +0.00, +0.00 → [++++0000] | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `E:LOCAL-EXACT-3` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `E:E-in-D(BP-2 values)` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Search with tentative assignments whose values are justified by neighbours' tendencies; propagation; backtracking on conflict. |
| `E:E-in-D(b=0)` | False (0.00) | False (0.00) | True (1.00) | True (1.00) | Δacc: +1.00, +1.00, +1.00, +1.00, +0.00, +0.00, +0.00, +0.00 → [++++0000] | Search with tentative assignments whose values are justified by neighbours' tendencies; propagation; backtracking on conflict. |
| `B1:UP-7` | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | silent -> default (0.50) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1:WP-6` | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | unforced -> default (0.50) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `B1C0:EQ-CONTRACT+POL` | False (0.00) | tie (0.50) | True (1.00) | True (1.00) | Δacc: +1.00, +1.00, +1.00, +1.00, +1.00, +1.00, +1.00, +1.00 → [++++++++] | Equivalence substitutions ("a = b = c"), then a count of the merged variable's occurrences. |
| `C0:POLARITY` | tie (0.50) | tie (0.50) | tie (0.50) | tie (0.50) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | One tally of v's own positive vs negative occurrences, then an immediate decision. |
| `C1:GREEDY` | False (0.00) | True (1.00) | True (1.00) | True (1.00) | Δacc: +1.00, +1.00, +1.00, +0.00, +0.00, +0.00, +1.00, +0.00 → [+++000+0] | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `D:DPLL-POL(complete)` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `D:DPLL-POL(b=0)` | True (1.00) | True (1.00) | True (1.00) | True (1.00) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `F:WALK-k` | False (0.34) | False (0.36) | True (0.58) | False (0.45) | Δacc: +0.34, +0.46, +0.24, +0.24, +0.04, +0.15, +0.27, -0.16 → [++++0~+−] | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| `H:SAMPLER` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Several complete satisfying assignments listed; answer = majority over them (entailment: conclusion checked in each). |
| `A1:ALWAYS-TRUE` | True (1.00) | True (1.00) | True (1.00) | True (1.00) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | No structural reasoning; immediate default answer. |
| `A2:RECENCY` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Cites surface features: first/last mention, number of negations, length. |
| `NULL:EXACT` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `NULL:NOISY-EXACT` | False (0.05) | False (0.05) | False (0.05) | False (0.05) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | As EXACT, with an isolated slip (misread value) in failing traces, located independently of the designed factor. |
| `NULL:PERCEPTION-NOISE` | False (0.12) | False (0.12) | False (0.12) | False (0.12) | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Correct reasoning applied to a misquoted clause or edge (the trace restates one constraint wrongly). |
| `NULL:RANDOM` | coin flip | coin flip | coin flip | coin flip | Δacc: +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00, +0.00 → [00000000] | Uninformative trace; answer unrelated to any designed factor. |

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (Δacc = acc(toward) − acc(against) in the 8 (d, O) cells), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.085 at full-study size and 0.26 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:BP-2` vs `C0:POLARITY` | 2.00 | 0.12 | 0.07 | 0.36 | ≥ 99 / 12.8 |
| `E:BP-2` vs `B1:UP-7` | 2.00 | 0.12 | 0.07 | 0.36 | ≥ 99 / 12.8 |
| `E:BP-2` vs `NULL:EXACT` | 2.00 | 0.12 | 0.07 | 0.36 | ≥ 99 / 12.8 |
| `E:BP-2` vs `B1C0:EQ-CONTRACT+POL` | 2.00 | 0.12 | 0.07 | 0.36 | ≥ 99 / 12.8 |
| `E:BP-2` vs `C1:GREEDY` | 1.41 | 0.17 | 0.10 | 0.51 | 60.1 / 6.4 |
| `E:BP-2` vs `E:BP-2-CAUSAL` | 1.41 | 0.17 | 0.10 | 0.51 | 60.1 / 6.4 |
| `C1:GREEDY` vs `E:BP-2-CAUSAL` | 1.41 | 0.17 | 0.10 | 0.51 | 60.1 / 6.4 |
| `E:BP-2` vs `E:E-in-D(b=0)` | 0 | **not separated by this set** | — | — | 0 |
| `E:BP-2` vs `F:WALK-k` | 1.42 | 0.17 | 0.10 | 0.51 | 60.3 / 6.4 |
| `E:BP-2` vs `E:BP-6` | 2.00 | 0.12 | 0.07 | 0.36 | ≥ 99 / 12.8 |
| `E:BP-1` vs `E:BP-2` | 1.41 | 0.17 | 0.10 | 0.51 | 60.1 / 6.4 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `E:BP-0`, `E:LOCAL-EXACT-3`, `E:E-in-D(BP-2 values)`, `B1:UP-7`, `B1:WP-6`, `C0:POLARITY`, `D:DPLL-POL(complete)`, `D:DPLL-POL(b=0)`, `H:SAMPLER`, `A1:ALWAYS-TRUE`, `A2:RECENCY`, `NULL:EXACT`, `NULL:NOISY-EXACT`, `NULL:PERCEPTION-NOISE`, `NULL:RANDOM` | `F:WALK-k`: 17.0 (dev 1.8) → π ≤ 0.19; `E:BP-1`: 60.1 (dev 6.4) → π ≤ 0.10; `E:BP-2-CAUSAL`: 60.1 (dev 6.4) → π ≤ 0.10 | the listed theories are tied here; E6b (retraction) and the truncation-conditional analysis for E-in-D vs finished search; E5b for the sampler; the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-1` | `F:WALK-k`: 29.0 (dev 3.1) → π ≤ 0.14; `E:BP-0`/`E:LOCAL-EXACT-3`/`E:E-in-D(BP-2 values)`…: 60.1 (dev 6.4) → π ≤ 0.10; `E:BP-2`/`E:BP-3`/`E:LOCAL-EXACT-2`…: 60.1 (dev 6.4) → π ≤ 0.10 |  |
| `E:BP-2`, `E:BP-3`, `E:LOCAL-EXACT-2`, `E:E-in-D(b=0)` | `E:BP-1`: 60.1 (dev 6.4) → π ≤ 0.10; `E:BP-2-CAUSAL`: 60.1 (dev 6.4) → π ≤ 0.10; `C1:GREEDY`: 60.1 (dev 6.4) → π ≤ 0.10 | the listed theories are tied here; E6b (retraction) and the truncation-conditional analysis for E-in-D vs finished search; E5b for the sampler; the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-6`, `E:BP-inf`, `B1C0:EQ-CONTRACT+POL` | `E:BP-2`/`E:BP-3`/`E:LOCAL-EXACT-2`…: ≥ 99 (dev 12.8) → π ≤ 0.07; `E:BP-inf-CAUSAL`: ≥ 99 (dev 12.8) → π ≤ 0.07; `C1:GREEDY`: ≥ 99 (dev 12.8) → π ≤ 0.07 | the listed theories are tied here; E6b (retraction) and the truncation-conditional analysis for E-in-D vs finished search; E5b for the sampler; the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-2-CAUSAL` | `F:WALK-k`: 42.2 (dev 4.5) → π ≤ 0.12; `E:BP-0`/`E:LOCAL-EXACT-3`/`E:E-in-D(BP-2 values)`…: 60.1 (dev 6.4) → π ≤ 0.10; `E:BP-1`: 60.1 (dev 6.4) → π ≤ 0.10 |  |
| `E:BP-inf-CAUSAL` | `E:BP-2-CAUSAL`: 60.1 (dev 6.4) → π ≤ 0.10; `C1:GREEDY`: 60.1 (dev 6.4) → π ≤ 0.10; `F:WALK-k`: 83.7 (dev 8.9) → π ≤ 0.08 |  |
| `C1:GREEDY` | `F:WALK-k`: 58.5 (dev 6.2) → π ≤ 0.10; `E:BP-1`: 60.1 (dev 6.4) → π ≤ 0.10; `E:BP-2`/`E:BP-3`/`E:LOCAL-EXACT-2`…: 60.1 (dev 6.4) → π ≤ 0.10 |  |
| `F:WALK-k` | `E:BP-0`/`E:LOCAL-EXACT-3`/`E:E-in-D(BP-2 values)`…: 17.0 (dev 1.8) → π ≤ 0.19; `E:BP-1`: 29.0 (dev 3.1) → π ≤ 0.14; `E:BP-2-CAUSAL`: 42.2 (dev 4.5) → π ≤ 0.12 |  |

**Key contrasts.**

- **MP vs exact:** exact solving predicts [00000000] (the truth never moves), so a positive Δacc moves weight from it, bounded per the resolution table.
- **MP vs C0 / `UP-k`:** both predict [00000000], because v's own polarity is unchanged and there are no unit clauses; a positive Δacc moves weight from them.
- **MP vs EQ-CONTRACT:** EQ-CONTRACT is flat across d; BP-t steps.
- **MP vs C1:** GREEDY's pattern depends on O; BP's doesn't.
- **Not distinguished here:** E-in-D vs exact on *finished* runs (both 0). The truncation-conditional analysis (CH1b) and E6b separate them.

---

## 6. E2 soft vs hard: own polarity (A) × second-order evidence (B) × truth (D) × order (O)
**Reasoning question.** When nothing forces v locally, does the answer follow v's BP-1 marginal: its neighbours' *tendencies* (B)? Or does it follow its own polarity (A, i.e. C0 = BP-0), first-mention processing (O, i.e. C1), or the truth fixed by a hard core (D)? **MP vs C0** is the A-vs-B contrast. **MP vs `UP-k`**: there are no unit clauses, so UP is silent. **MP vs exact** is the B-vs-D contrast.
**Controlled factors.** Same core, satellites, pendant signs, names and block order in all 24 cells. Negation counts are equalised by 12 balancing clauses on degree-1 pairs (asserted). The link is always the last 4 clauses.
Core seed 948, c\* = `sock`, target `bear`; 68 variables, 85 clauses, 82 negations in every cell.
- `E2/A1+3-_Bpro-T_DFalse_v-first` vs `E2/A1+3-_Bpro-T_DFalse_sat-first`:
- `14. (horn or lock)`  →  `14. (bear or not horn or not hive)`
- `15. (horn or lake)`  →  `15. (not bear or not cup or not fish)`
- `16. (horn or cat)`  →  `16. (not bear or not seed or not book)`
- `17. (hive or rose)`  →  `17. (not bear or egg or rice)`
- `18. (hive or drum)`  →  `18. (salt or fire or door)`
- `19. (hive or card)`  →  `19. (road or dog)`
- `20. (not cup or rope)`  →  `20. (pine or key or not plum)`
- `21. (not cup or iron)`  →  `21. (not key or not moss or not plum)`
- `22. (not cup or snow)`  →  `22. (king or fire or root)`
- `23. (not fish or pond)`  →  `23. (moss or plum or pine)`
- `24. (not fish or bell)`  →  `24. (plum or king or pine)`
- `25. (not fish or wolf)`  →  `25. (not root or fire or not sock)`
- `26. (not seed or shoe)`  →  `26. (sock or fire or key)`
- `27. (not seed or harp)`  →  `27. (key or sock or root)`
- `28. (not seed or belt)`  →  `28. (pine or plum or not king)`
- `29. (not book or ring)`  →  `29. (not sock or fire or moss)`
- `30. (not book or sea)`  →  `30. (wind or pen)`
- `31. (not book or kite)`  →  `31. (horn or lock)`
- `32. (egg or rock)`  →  `32. (horn or lake)`
- `33. (egg or sage)`  →  `33. (horn or cat)`
- `34. (egg or lamp)`  →  `34. (hive or rose)`
- `35. (rice or ink)`  →  `35. (hive or drum)`
- `36. (rice or ball)`  →  `36. (hive or card)`
- `37. (rice or box)`  →  `37. (not cup or rope)`
- `38. (salt or fire or door)`  →  `38. (not cup or iron)`
- `39. (road or dog)`  →  `39. (not cup or snow)`
- `40. (pine or key or not plum)`  →  `40. (not fish or pond)`
- `41. (not key or not moss or not plum)`  →  `41. (not fish or bell)`
- `42. (king or fire or root)`  →  `42. (not fish or wolf)`
- `43. (moss or plum or pine)`  →  `43. (not seed or shoe)`
- `44. (plum or king or pine)`  →  `44. (not seed or harp)`
- `45. (not root or fire or not sock)`  →  `45. (not seed or belt)`
- `46. (sock or fire or key)`  →  `46. (not book or ring)`
- `47. (key or sock or root)`  →  `47. (not book or sea)`
- `48. (pine or plum or not king)`  →  `48. (not book or kite)`
- `49. (not sock or fire or moss)`  →  `49. (egg or rock)`
- `50. (wind or pen)`  →  `50. (egg or sage)`
- `51. (bear or not horn or not hive)`  →  `51. (egg or lamp)`
- `52. (not bear or not cup or not fish)`  →  `52. (rice or ink)`
- `53. (not bear or not seed or not book)`  →  `53. (rice or ball)`
- `54. (not bear or egg or rice)`  →  `54. (rice or box)`
- `E2/A2+2-_Bpro-T_DFalse_sat-first` vs `E2/A1+3-_Bpro-T_DFalse_sat-first`:
- `8. (coat or bean)`  →  `8. (not coat or not bean)`
- `12. (leaf or coin)`  →  `12. (not leaf or coin)`
- `52. (not bear or not cup or not fish)`  →  `52. (bear or cup or fish)`
- `E2/A3+1-_Bpro-T_DFalse_sat-first` vs `E2/A1+3-_Bpro-T_DFalse_sat-first`:
- `8. (coat or bean)`  →  `8. (not coat or not bean)`
- `12. (leaf or coin)`  →  `12. (not leaf or not coin)`
- `39. (road or dog)`  →  `39. (not road or not dog)`
- `52. (not bear or not cup or not fish)`  →  `52. (bear or cup or fish)`
- `53. (not bear or not seed or not book)`  →  `53. (bear or seed or book)`
- `E2/A1+3-_Bpro-F_DFalse_sat-first` vs `E2/A1+3-_Bpro-T_DFalse_sat-first`:
- `8. (coat or bean)`  →  `8. (not coat or not bean)`
- `12. (leaf or coin)`  →  `12. (not leaf or not coin)`
- `51. (bear or not horn or not hive)`  →  `51. (bear or horn or hive)`
- `52. (not bear or not cup or not fish)`  →  `52. (not bear or cup or fish)`
- `53. (not bear or not seed or not book)`  →  `53. (not bear or seed or book)`
- `54. (not bear or egg or rice)`  →  `54. (not bear or not egg or not rice)`
<details open><summary>Full prompt: <code>E2/A1+3-_Bpro-T_DFalse_sat-first</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (not king or pine or door)
2. (not root or not salt or moss)
3. (not door or not salt or key)
4. (not sock or not fire or plum)
5. (not door or not pine or not king)
6. (sock or not king or door)
7. (king or not pine or sock)
8. (coat or bean)
9. (not pine or salt or fire)
10. (root or pine or door)
11. (not salt or not root or not moss)
12. (leaf or coin)
13. (king or not salt or sock)
14. (horn or lock)
15. (horn or lake)
16. (horn or cat)
17. (hive or rose)
18. (hive or drum)
19. (hive or card)
20. (not cup or rope)
21. (not cup or iron)
22. (not cup or snow)
23. (not fish or pond)
24. (not fish or bell)
25. (not fish or wolf)
26. (not seed or shoe)
27. (not seed or harp)
28. (not seed or belt)
29. (not book or ring)
30. (not book or sea)
31. (not book or kite)
32. (egg or rock)
33. (egg or sage)
34. (egg or lamp)
35. (rice or ink)
36. (rice or ball)
37. (rice or box)
38. (salt or fire or door)
39. (road or dog)
40. (pine or key or not plum)
41. (not key or not moss or not plum)
42. (king or fire or root)
43. (moss or plum or pine)
44. (plum or king or pine)
45. (not root or fire or not sock)
46. (sock or fire or key)
47. (key or sock or root)
48. (pine or plum or not king)
49. (not sock or fire or moss)
50. (wind or pen)
51. (bear or not horn or not hive)
52. (not bear or not cup or not fish)
53. (not bear or not seed or not book)
54. (not bear or egg or rice)
55. (key or not plum or pine)
56. (door or not fire or not root)
57. (sock or fire or not moss)
58. (not door or king or moss)
59. (not moss or key or not king)
60. (not plum or not sock or not root)
61. (bag or fork)
62. (not sock or key or plum)
63. (map or bowl)
64. (not king or salt or not root)
65. (not pine or sock or not fire)
66. (not pine or salt or root)
67. (gold or reed)
68. (not door or not sock or not salt)
69. (not salt or not plum or root)
70. (not pine or not salt or plum)
71. (not king or not pine or not sock)
72. (ship or rain)
73. (nut or star)
74. (moon or nest)
75. (fern or gate)
76. (salt or sock or moss)
77. (pear or hill)
78. (plum or not salt or king)
79. (not salt or not plum or moss)
80. (door or not moss or root)
81. (not salt or not fire or root)
82. (bear or frog)
83. (not bear or not frog)
84. (frog or not sock)
85. (not frog or sock)

Every assignment that satisfies all the clauses gives bear the same value. Which value is it? Answer with one word: True or False.
```

</details>

### All 24 cells: P(answer = True) per theory (computed)
Entries are each theory's answer probability under its decision rule: deterministic theories give 0 / 1 (0.5 on ties); stochastic ones keep their probability. The last column is the raw BP-1 marginal, for calibration.

| Cell (A, B, D, O) | `NULL:EXACT` | `E:BP-0` | `E:BP-1` | `E:BP-inf` | `B1:UP-7` | `C0:POLARITY` | `C1:GREEDY` | `D:DPLL-POL(b=0)` | `F:WALK-k` | `NULL:PERCEPTION-NOISE` | BP-1 marginal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1+3-, pro-F, D=False, sat-first | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.09 | 0.07 | 0.01 |
| 1+3-, pro-F, D=False, v-first | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.09 | 0.07 | 0.01 |
| 1+3-, pro-F, D=True, sat-first | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.93 | 0.01 |
| 1+3-, pro-F, D=True, v-first | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.93 | 0.01 |
| 1+3-, pro-T, D=False, sat-first | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.28 | 0.07 | 0.82 |
| 1+3-, pro-T, D=False, v-first | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.29 | 0.07 | 0.82 |
| 1+3-, pro-T, D=True, sat-first | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.85 | 0.93 | 0.82 |
| 1+3-, pro-T, D=True, v-first | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.82 | 0.93 | 0.82 |
| 2+2-, pro-F, D=False, sat-first | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.50 | 0.00 | 1.00 | 0.12 | 0.07 | 0.04 |
| 2+2-, pro-F, D=False, v-first | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.50 | 1.00 | 1.00 | 0.10 | 0.07 | 0.04 |
| 2+2-, pro-F, D=True, sat-first | 1.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.50 | 0.00 | 1.00 | 0.46 | 0.93 | 0.04 |
| 2+2-, pro-F, D=True, v-first | 1.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.50 | 1.00 | 1.00 | 0.48 | 0.93 | 0.04 |
| 2+2-, pro-T, D=False, sat-first | 0.00 | 0.50 | 1.00 | 1.00 | 0.50 | 0.50 | 1.00 | 1.00 | 0.55 | 0.07 | 0.96 |
| 2+2-, pro-T, D=False, v-first | 0.00 | 0.50 | 1.00 | 1.00 | 0.50 | 0.50 | 1.00 | 1.00 | 0.60 | 0.07 | 0.96 |
| 2+2-, pro-T, D=True, sat-first | 1.00 | 0.50 | 1.00 | 1.00 | 0.50 | 0.50 | 1.00 | 1.00 | 0.91 | 0.93 | 0.96 |
| 2+2-, pro-T, D=True, v-first | 1.00 | 0.50 | 1.00 | 1.00 | 0.50 | 0.50 | 1.00 | 1.00 | 0.87 | 0.93 | 0.96 |
| 3+1-, pro-F, D=False, sat-first | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 1.00 | 0.24 | 0.07 | 0.18 |
| 3+1-, pro-F, D=False, v-first | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.20 | 0.07 | 0.18 |
| 3+1-, pro-F, D=True, sat-first | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 0.67 | 0.93 | 0.18 |
| 3+1-, pro-F, D=True, v-first | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.61 | 0.93 | 0.18 |
| 3+1-, pro-T, D=False, sat-first | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.68 | 0.07 | 0.99 |
| 3+1-, pro-T, D=False, v-first | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.71 | 0.07 | 0.99 |
| 3+1-, pro-T, D=True, sat-first | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.96 | 0.93 | 0.99 |
| 3+1-, pro-T, D=True, v-first | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.91 | 0.93 | 0.99 |

### Hypothesis block
**(b)** = predicted contrasts over the 24 cells: β_B (pro-T − pro-F), β_A ((3+,1−) − (1+,3−)), β_D (D=T − D=F), β_{B×O} (β_B in sat-first − in v-first), and β_B in the A-opposed cells only. Pre-registered thresholds: β_B ≥ 0.06 counts as support; TOST ±0.05 counts as absent.
| Theory | `A1+3-_Bpro-T_DFalse_sat-first` | `A1+3-_Bpro-T_DFalse_v-first` | `A2+2-_Bpro-T_DFalse_sat-first` | `A3+1-_Bpro-T_DFalse_sat-first` | `A1+3-_Bpro-F_DFalse_sat-first` | (b) eval result: β_B, β_A, β_D, β_{B×O}, β_B(A-opposed) | (c) CoT |
|---|---|---|---|---|---|---|---|
| `E:BP-0` | False (0.36) | False (0.36) | tie (0.50) | True (0.64) | False (0.36) | +0.00, +1.00, +0.00, +0.00, -1.00 → [B0 A+ D0 BxO0] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-1` | True (0.82) | True (0.82) | True (0.96) | True (0.99) | False (0.01) | +1.00, +0.00, +0.00, +0.00, +1.00 → [B+ A0 D0 BxO0] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2` | True (0.59) | True (0.59) | True (0.93) | True (0.99) | False (0.00) | +1.00, +0.00, +0.00, +0.00, +1.00 → [B+ A0 D0 BxO0] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-4` | True (0.73) | True (0.73) | True (1.00) | True (1.00) | False (0.00) | +1.00, +0.00, +0.00, +0.00, +1.00 → [B+ A0 D0 BxO0] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-inf` | False (0.00) | False (0.00) | True (1.00) | True (1.00) | False (0.00) | +0.67, +0.50, +0.33, +0.00, +0.00 → [B+ A+ D+ BxO0] | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2-CAUSAL` | True (0.71) | False (0.23) | True (0.94) | True (0.99) | False (0.00) | +0.50, +0.50, +0.00, +1.00, +0.00 → [B+ A+ D0 BxO+] | As BP-t, but every piece of evidence cited comes from clauses read before v's last mention. |
| `E:LOCAL-EXACT-1` | True (1.00) | True (1.00) | True (1.00) | True (1.00) | False (0.00) | +1.00, +0.00, +0.00, +0.00, +1.00 → [B+ A0 D0 BxO0] | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `E:LOCAL-EXACT-3` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | False (0.00) | +0.00, +0.00, +1.00, +0.00, +0.00 → [B0 A0 D+ BxO0] | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `E:E-in-D(BP-2 values)` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | False (0.00) | +0.00, +0.00, +1.00, +0.00, +0.00 → [B0 A0 D+ BxO0] | Search with tentative assignments whose values are justified by neighbours' tendencies; propagation; backtracking on conflict. |
| `E:E-in-D(b=0)` | True (1.00) | True (1.00) | True (1.00) | True (1.00) | False (0.00) | +1.00, +0.00, +0.00, +0.00, +1.00 → [B+ A0 D0 BxO0] | Search with tentative assignments whose values are justified by neighbours' tendencies; propagation; backtracking on conflict. |
| `B1:UP-7` | silent -> default (0.00) | silent -> default (0.00) | silent -> default (0.50) | silent -> default (1.00) | silent -> default (0.00) | +0.00, +1.00, +0.00, +0.00, -1.00 → [B0 A+ D0 BxO0] | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `B1:WP-6` | unforced -> default (0.00) | unforced -> default (0.00) | unforced -> default (0.50) | unforced -> default (1.00) | unforced -> default (0.00) | +0.00, +1.00, +0.00, +0.00, -1.00 → [B0 A+ D0 BxO0] | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `B1C0:EQ-CONTRACT+POL` | False (0.00) | False (0.00) | False (0.00) | True (1.00) | False (0.00) | +0.00, +1.00, +0.33, +0.00, -1.00 → [B0 A+ D+ BxO0] | Equivalence substitutions ("a = b = c"), then a count of the merged variable's occurrences. |
| `C0:POLARITY` | False (0.00) | False (0.00) | tie (0.50) | True (1.00) | False (0.00) | +0.00, +1.00, +0.00, +0.00, -1.00 → [B0 A+ D0 BxO0] | One tally of v's own positive vs negative occurrences, then an immediate decision. |
| `C1:GREEDY` | True (1.00) | False (0.00) | True (1.00) | True (1.00) | False (0.00) | +0.50, +0.50, +0.00, +1.00, +0.00 → [B+ A+ D0 BxO+] | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `D:DPLL-POL(complete)` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | False (0.00) | +0.00, +0.00, +1.00, +0.00, +0.00 → [B0 A0 D+ BxO0] | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `D:DPLL-POL(b=0)` | False (0.00) | False (0.00) | True (1.00) | True (1.00) | False (0.00) | +0.00, +1.00, +0.00, +0.00, -1.00 → [B0 A+ D0 BxO0] | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `F:WALK-k` | False (0.28) | False (0.29) | True (0.55) | True (0.68) | False (0.09) | +0.39, +0.23, +0.36, -0.01, +0.13 → [B+ A+ D+ BxO0] | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| `H:SAMPLER` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | False (0.00) | +0.00, +0.00, +1.00, +0.00, +0.00 → [B0 A0 D+ BxO0] | Several complete satisfying assignments listed; answer = majority over them (entailment: conclusion checked in each). |
| `A1:ALWAYS-TRUE` | True (1.00) | True (1.00) | True (1.00) | True (1.00) | True (1.00) | +0.00, +0.00, +0.00, +0.00, +0.00 → [B0 A0 D0 BxO0] | No structural reasoning; immediate default answer. |
| `A2:PRIMACY` | True (1.00) | True (1.00) | True (1.00) | True (1.00) | True (1.00) | +0.00, +0.00, +0.00, +0.00, +0.00 → [B0 A0 D0 BxO0] | Cites surface features: first/last mention, number of negations, length. |
| `A2:RECENCY` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | False (0.00) | +0.00, +0.00, +0.00, +0.00, +0.00 → [B0 A0 D0 BxO0] | Cites surface features: first/last mention, number of negations, length. |
| `NULL:EXACT` | False (0.00) | False (0.00) | False (0.00) | False (0.00) | False (0.00) | +0.00, +0.00, +1.00, +0.00, +0.00 → [B0 A0 D+ BxO0] | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `NULL:NOISY-EXACT` | False (0.05) | False (0.05) | False (0.05) | False (0.05) | False (0.05) | +0.00, +0.00, +0.90, +0.00, +0.00 → [B0 A0 D+ BxO0] | As EXACT, with an isolated slip (misread value) in failing traces, located independently of the designed factor. |
| `NULL:PERCEPTION-NOISE` | False (0.07) | False (0.07) | False (0.07) | False (0.07) | False (0.07) | +0.00, +0.00, +0.85, +0.00, +0.00 → [B0 A0 D+ BxO0] | Correct reasoning applied to a misquoted clause or edge (the trace restates one constraint wrongly). |
| `NULL:RANDOM` | coin flip | coin flip | coin flip | coin flip | coin flip | +0.00, +0.00, +0.00, +0.00, +0.00 → [B0 A0 D0 BxO0] | Uninformative trace; answer unrelated to any designed factor. |

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (P(answer = True) in each of the 24 cells), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.09 at full-study size and 0.22 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:BP-1` vs `C0:POLARITY` | 3.16 | 0.08 | 0.05 | 0.19 | ≥ 99 / 44.9 |
| `E:BP-1` vs `B1:UP-7` | 3.16 | 0.08 | 0.05 | 0.19 | ≥ 99 / 44.9 |
| `E:BP-1` vs `NULL:EXACT` | 3.46 | 0.07 | 0.04 | 0.18 | ≥ 99 / 53.8 |
| `E:BP-1` vs `C1:GREEDY` | 2.45 | 0.10 | 0.06 | 0.25 | ≥ 99 / 26.9 |
| `E:BP-1` vs `E:BP-2-CAUSAL` | 2.45 | 0.10 | 0.06 | 0.25 | ≥ 99 / 26.9 |
| `C1:GREEDY` vs `E:BP-2-CAUSAL` | 2.00 | 0.13 | 0.07 | 0.31 | ≥ 99 / 17.9 |
| `E:BP-1` vs `D:DPLL-POL(b=0)` | 3.46 | 0.07 | 0.04 | 0.18 | ≥ 99 / 53.8 |
| `E:BP-1` vs `NULL:PERCEPTION-NOISE` | 3.22 | 0.08 | 0.05 | 0.19 | ≥ 99 / 46.4 |
| `E:BP-1` vs `E:BP-inf` | 2.00 | 0.13 | 0.07 | 0.31 | ≥ 99 / 17.9 |
| `E:BP-1` vs `F:WALK-k` | 1.82 | 0.14 | 0.08 | 0.34 | 89.0 / 14.9 |
| `E:BP-1` vs `E:E-in-D(b=0)` | 0 | **not separated by this set** | — | — | 0 |
| `E:BP-1` vs `H:SAMPLER` | 3.46 | 0.07 | 0.04 | 0.18 | ≥ 99 / 53.8 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `E:BP-0`, `B1:UP-7`, `B1:WP-6`, `C0:POLARITY` | `B1C0:EQ-CONTRACT+POL`: 53.6 (dev 9.0) → π ≤ 0.10; `D:DPLL-POL(b=0)`: 53.6 (dev 9.0) → π ≤ 0.10; `NULL:RANDOM`: ≥ 99 (dev 17.9) → π ≤ 0.07 | the listed theories are tied here; E1-C chain order (C1 vs BP-CAUSAL) and E6a (C1 vs decimation); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-1`, `E:BP-2`, `E:BP-4`, `E:LOCAL-EXACT-1`, `E:E-in-D(b=0)` | `F:WALK-k`: 89.0 (dev 14.9) → π ≤ 0.08; `E:BP-inf`: ≥ 99 (dev 17.9) → π ≤ 0.07; `E:BP-2-CAUSAL`: ≥ 99 (dev 26.9) → π ≤ 0.06 | the listed theories are tied here; E1-C chain order (C1 vs BP-CAUSAL) and E6a (C1 vs decimation); the coverage matrix (end of document) lists the sets that separate them |
| `E:BP-inf` | `F:WALK-k`: 51.0 (dev 8.5) → π ≤ 0.11; `E:BP-1`/`E:BP-2`/`E:BP-4`…: ≥ 99 (dev 17.9) → π ≤ 0.07; `E:BP-0`/`B1:UP-7`/`B1:WP-6`…: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `E:BP-2-CAUSAL` | `C1:GREEDY`: ≥ 99 (dev 17.9) → π ≤ 0.07; `F:WALK-k`: ≥ 99 (dev 21.8) → π ≤ 0.07; `E:BP-0`/`B1:UP-7`/`B1:WP-6`…: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `E:LOCAL-EXACT-3`, `E:E-in-D(BP-2 values)`, `D:DPLL-POL(complete)`, `H:SAMPLER`, `NULL:EXACT` | `NULL:NOISY-EXACT`: 1.6 (dev 0.3) → π ≤ 0.60; `NULL:PERCEPTION-NOISE`: 3.6 (dev 0.6) → π ≤ 0.41; `F:WALK-k`: 98.2 (dev 16.4) → π ≤ 0.08 | the listed theories are tied here; E1-C chain order (C1 vs BP-CAUSAL) and E6a (C1 vs decimation); the coverage matrix (end of document) lists the sets that separate them |
| `B1C0:EQ-CONTRACT+POL` | `E:BP-0`/`B1:UP-7`/`B1:WP-6`…: 53.6 (dev 9.0) → π ≤ 0.10; `D:DPLL-POL(b=0)`: ≥ 99 (dev 17.9) → π ≤ 0.07; `F:WALK-k`: ≥ 99 (dev 21.5) → π ≤ 0.07 |  |
| `C1:GREEDY` | `E:BP-2-CAUSAL`: ≥ 99 (dev 17.9) → π ≤ 0.07; `F:WALK-k`: ≥ 99 (dev 21.4) → π ≤ 0.07; `E:BP-0`/`B1:UP-7`/`B1:WP-6`…: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `D:DPLL-POL(b=0)` | `E:BP-0`/`B1:UP-7`/`B1:WP-6`…: 53.6 (dev 9.0) → π ≤ 0.10; `B1C0:EQ-CONTRACT+POL`: ≥ 99 (dev 17.9) → π ≤ 0.07; `C1:GREEDY`: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `F:WALK-k` | `E:BP-inf`: 51.0 (dev 8.5) → π ≤ 0.11; `NULL:RANDOM`: 52.9 (dev 8.8) → π ≤ 0.11; `NULL:PERCEPTION-NOISE`: 71.0 (dev 11.9) → π ≤ 0.09 |  |
| `A1:ALWAYS-TRUE`, `A2:PRIMACY` | `NULL:RANDOM`: ≥ 99 (dev 26.9) → π ≤ 0.06; `F:WALK-k`: ≥ 99 (dev 34.8) → π ≤ 0.05; `D:DPLL-POL(b=0)`: ≥ 99 (dev 35.9) → π ≤ 0.05 | the listed theories are tied here; the coverage matrix (end of document) lists the sets that separate them |
| `A2:RECENCY` | `NULL:RANDOM`: ≥ 99 (dev 26.9) → π ≤ 0.06; `F:WALK-k`: ≥ 99 (dev 36.7) → π ≤ 0.05; `E:BP-0`/`B1:UP-7`/`B1:WP-6`…: ≥ 99 (dev 44.9) → π ≤ 0.05 |  |
| `NULL:NOISY-EXACT` | `NULL:PERCEPTION-NOISE`: 0.4 (dev 0.1) → π ≤ 1.00; `E:LOCAL-EXACT-3`/`E:E-in-D(BP-2 values)`/`D:DPLL-POL(complete)`…: 1.6 (dev 0.3) → π ≤ 0.60; `F:WALK-k`: 79.2 (dev 13.2) → π ≤ 0.09 |  |
| `NULL:PERCEPTION-NOISE` | `NULL:NOISY-EXACT`: 0.4 (dev 0.1) → π ≤ 1.00; `E:LOCAL-EXACT-3`/`E:E-in-D(BP-2 values)`/`D:DPLL-POL(complete)`…: 3.6 (dev 0.6) → π ≤ 0.41; `F:WALK-k`: 71.0 (dev 11.9) → π ≤ 0.09 |  |
| `NULL:RANDOM` | `F:WALK-k`: 52.9 (dev 8.8) → π ≤ 0.11; `E:BP-0`/`B1:UP-7`/`B1:WP-6`…: ≥ 99 (dev 17.9) → π ≤ 0.07; `NULL:PERCEPTION-NOISE`: ≥ 99 (dev 19.5) → π ≤ 0.07 |  |

**Key contrasts.**

- **MP vs C0:** BP-t (t ≥ 1) gives B+ A0; POLARITY gives B0 A+.
- **MP vs `UP-k`:** UP is silent, so it takes its default (POLARITY) and gives B0.
- **MP vs exact:** exact gives D+ B0.
- **MP vs C1:** GREEDY gives B×O+ (B only in sat-first). **But so does `E:BP-2-CAUSAL`:** in v-first order the satellite evidence arrives after v's clauses, so a causal reader cannot use it. E2's O factor therefore separates *abstract* E from {C1, causal E}, and E1-C's chain-order profiles separate C1 from causal E (computed resolution in §5).
- **MP vs perception noise:** misread literals mostly affect the link and the core, so PERCEPTION-NOISE tracks D, attenuated (see the cell table).

### Entailment rendering (realistic framing, same clauses)
- `E2/A3+1-_Bpro-T_DFalse_sat-first_ENT`: ground truth **B** (3+1-, pro-T, D=False).
<details><summary>Full prompt: <code>E2/A3+1-_Bpro-T_DFalse_sat-first_ENT</code></summary>

```text
Here are some facts about who attends a meeting. Each fact says that at least one of the listed statements is true.

Facts:
Fact 1: Gus does not attend, or Dan attends, or Bob attends.
Fact 2: Ray does not attend, or Una does not attend, or Tom attends.
Fact 3: Bob does not attend, or Una does not attend, or Kai attends.
Fact 4: Cyd does not attend, or Ida does not attend, or Pia attends.
Fact 5: Bob does not attend, or Dan does not attend, or Gus does not attend.
Fact 6: Cyd attends, or Gus does not attend, or Bob attends.
Fact 7: Gus attends, or Dan does not attend, or Cyd attends.
Fact 8: Heidi does not attend, or Bo does not attend.
Fact 9: Dan does not attend, or Una attends, or Ida attends.
Fact 10: Ray attends, or Dan attends, or Bob attends.
Fact 11: Una does not attend, or Ray does not attend, or Tom does not attend.
Fact 12: Grace does not attend, or Lou does not attend.
Fact 13: Gus attends, or Una does not attend, or Cyd attends.
Fact 14: Eve attends, or Walt attends.
Fact 15: Eve attends, or Yara attends.
Fact 16: Eve attends, or Judy attends.
Fact 17: Dina attends, or Ed attends.
Fact 18: Dina attends, or Laura attends.
Fact 19: Dina attends, or Tina attends.
Fact 20: Xavier does not attend, or Rex attends.
Fact 21: Xavier does not attend, or Bea attends.
Fact 22: Xavier does not attend, or Ted attends.
Fact 23: Pam does not attend, or Ned attends.
Fact 24: Pam does not attend, or Jan attends.
Fact 25: Pam does not attend, or Fay attends.
Fact 26: Ike does not attend, or Val attends.
Fact 27: Ike does not attend, or Quinn attends.
Fact 28: Ike does not attend, or Olga attends.
Fact 29: Mike does not attend, or Hope attends.
Fact 30: Mike does not attend, or Jo attends.
Fact 31: Mike does not attend, or Victor attends.
Fact 32: Pat attends, or Max attends.
Fact 33: Pat attends, or Kim attends.
Fact 34: Pat attends, or Mia attends.
Fact 35: Zoe attends, or Ken attends.
Fact 36: Zoe attends, or Flo attends.
Fact 37: Zoe attends, or Sue attends.
Fact 38: Una attends, or Ida attends, or Bob attends.
Fact 39: Sid does not attend, or Gil does not attend.
Fact 40: Dan attends, or Kai attends, or Pia does not attend.
Fact 41: Kai does not attend, or Tom does not attend, or Pia does not attend.
Fact 42: Gus attends, or Ida attends, or Ray attends.
Fact 43: Tom attends, or Pia attends, or Dan attends.
Fact 44: Pia attends, or Gus attends, or Dan attends.
Fact 45: Ray does not attend, or Ida attends, or Cyd does not attend.
Fact 46: Cyd attends, or Ida attends, or Kai attends.
Fact 47: Kai attends, or Cyd attends, or Ray attends.
Fact 48: Dan attends, or Pia attends, or Gus does not attend.
Fact 49: Cyd does not attend, or Ida attends, or Tom attends.
Fact 50: Frank attends, or Oscar attends.
Fact 51: Ivan attends, or Eve does not attend, or Dina does not attend.
Fact 52: Ivan attends, or Xavier attends, or Pam attends.
Fact 53: Ivan attends, or Ike attends, or Mike attends.
Fact 54: Ivan does not attend, or Pat attends, or Zoe attends.
Fact 55: Kai attends, or Pia does not attend, or Dan attends.
Fact 56: Bob attends, or Ida does not attend, or Ray does not attend.
Fact 57: Cyd attends, or Ida attends, or Tom does not attend.
Fact 58: Bob does not attend, or Gus attends, or Tom attends.
Fact 59: Tom does not attend, or Kai attends, or Gus does not attend.
Fact 60: Pia does not attend, or Cyd does not attend, or Ray does not attend.
Fact 61: Uma attends, or Wes attends.
Fact 62: Cyd does not attend, or Kai attends, or Pia attends.
Fact 63: Sam attends, or Ola attends.
Fact 64: Gus does not attend, or Una attends, or Ray does not attend.
Fact 65: Dan does not attend, or Cyd attends, or Ida does not attend.
Fact 66: Dan does not attend, or Una attends, or Ray attends.
Fact 67: Abe attends, or Lee attends.
Fact 68: Bob does not attend, or Cyd does not attend, or Una does not attend.
Fact 69: Una does not attend, or Pia does not attend, or Ray attends.
Fact 70: Dan does not attend, or Una does not attend, or Pia attends.
Fact 71: Gus does not attend, or Dan does not attend, or Cyd does not attend.
Fact 72: Hal attends, or Wendy attends.
Fact 73: Vera attends, or Ann attends.
Fact 74: Dee attends, or Alice attends.
Fact 75: Carol attends, or Cal attends.
Fact 76: Una attends, or Cyd attends, or Tom attends.
Fact 77: Rosa attends, or Eli attends.
Fact 78: Pia attends, or Una does not attend, or Gus attends.
Fact 79: Una does not attend, or Pia does not attend, or Tom attends.
Fact 80: Bob attends, or Tom does not attend, or Ray attends.
Fact 81: Una does not attend, or Ida does not attend, or Ray attends.
Fact 82: Ivan attends, or Nina attends.
Fact 83: Ivan does not attend, or Nina does not attend.
Fact 84: Nina attends, or Cyd does not attend.
Fact 85: Nina does not attend, or Cyd attends.

Which of the following is correct?
(A) It follows from the facts that Ivan attends.
(B) It follows from the facts that Ivan does not attend.
(C) Neither follows from the facts.
Answer with one letter: A, B or C.
```

</details>
- `E2/A1+3-_Bpro-T_DFalse_sat-first_ENT`: ground truth **B** (1+3-, pro-T, D=False).
<details><summary>Full prompt: <code>E2/A1+3-_Bpro-T_DFalse_sat-first_ENT</code></summary>

```text
Here are some facts about who attends a meeting. Each fact says that at least one of the listed statements is true.

Facts:
Fact 1: Gus does not attend, or Dan attends, or Bob attends.
Fact 2: Ray does not attend, or Una does not attend, or Tom attends.
Fact 3: Bob does not attend, or Una does not attend, or Kai attends.
Fact 4: Cyd does not attend, or Ida does not attend, or Pia attends.
Fact 5: Bob does not attend, or Dan does not attend, or Gus does not attend.
Fact 6: Cyd attends, or Gus does not attend, or Bob attends.
Fact 7: Gus attends, or Dan does not attend, or Cyd attends.
Fact 8: Heidi attends, or Bo attends.
Fact 9: Dan does not attend, or Una attends, or Ida attends.
Fact 10: Ray attends, or Dan attends, or Bob attends.
Fact 11: Una does not attend, or Ray does not attend, or Tom does not attend.
Fact 12: Grace attends, or Lou attends.
Fact 13: Gus attends, or Una does not attend, or Cyd attends.
Fact 14: Eve attends, or Walt attends.
Fact 15: Eve attends, or Yara attends.
Fact 16: Eve attends, or Judy attends.
Fact 17: Dina attends, or Ed attends.
Fact 18: Dina attends, or Laura attends.
Fact 19: Dina attends, or Tina attends.
Fact 20: Xavier does not attend, or Rex attends.
Fact 21: Xavier does not attend, or Bea attends.
Fact 22: Xavier does not attend, or Ted attends.
Fact 23: Pam does not attend, or Ned attends.
Fact 24: Pam does not attend, or Jan attends.
Fact 25: Pam does not attend, or Fay attends.
Fact 26: Ike does not attend, or Val attends.
Fact 27: Ike does not attend, or Quinn attends.
Fact 28: Ike does not attend, or Olga attends.
Fact 29: Mike does not attend, or Hope attends.
Fact 30: Mike does not attend, or Jo attends.
Fact 31: Mike does not attend, or Victor attends.
Fact 32: Pat attends, or Max attends.
Fact 33: Pat attends, or Kim attends.
Fact 34: Pat attends, or Mia attends.
Fact 35: Zoe attends, or Ken attends.
Fact 36: Zoe attends, or Flo attends.
Fact 37: Zoe attends, or Sue attends.
Fact 38: Una attends, or Ida attends, or Bob attends.
Fact 39: Sid attends, or Gil attends.
Fact 40: Dan attends, or Kai attends, or Pia does not attend.
Fact 41: Kai does not attend, or Tom does not attend, or Pia does not attend.
Fact 42: Gus attends, or Ida attends, or Ray attends.
Fact 43: Tom attends, or Pia attends, or Dan attends.
Fact 44: Pia attends, or Gus attends, or Dan attends.
Fact 45: Ray does not attend, or Ida attends, or Cyd does not attend.
Fact 46: Cyd attends, or Ida attends, or Kai attends.
Fact 47: Kai attends, or Cyd attends, or Ray attends.
Fact 48: Dan attends, or Pia attends, or Gus does not attend.
Fact 49: Cyd does not attend, or Ida attends, or Tom attends.
Fact 50: Frank attends, or Oscar attends.
Fact 51: Ivan attends, or Eve does not attend, or Dina does not attend.
Fact 52: Ivan does not attend, or Xavier does not attend, or Pam does not attend.
Fact 53: Ivan does not attend, or Ike does not attend, or Mike does not attend.
Fact 54: Ivan does not attend, or Pat attends, or Zoe attends.
Fact 55: Kai attends, or Pia does not attend, or Dan attends.
Fact 56: Bob attends, or Ida does not attend, or Ray does not attend.
Fact 57: Cyd attends, or Ida attends, or Tom does not attend.
Fact 58: Bob does not attend, or Gus attends, or Tom attends.
Fact 59: Tom does not attend, or Kai attends, or Gus does not attend.
Fact 60: Pia does not attend, or Cyd does not attend, or Ray does not attend.
Fact 61: Uma attends, or Wes attends.
Fact 62: Cyd does not attend, or Kai attends, or Pia attends.
Fact 63: Sam attends, or Ola attends.
Fact 64: Gus does not attend, or Una attends, or Ray does not attend.
Fact 65: Dan does not attend, or Cyd attends, or Ida does not attend.
Fact 66: Dan does not attend, or Una attends, or Ray attends.
Fact 67: Abe attends, or Lee attends.
Fact 68: Bob does not attend, or Cyd does not attend, or Una does not attend.
Fact 69: Una does not attend, or Pia does not attend, or Ray attends.
Fact 70: Dan does not attend, or Una does not attend, or Pia attends.
Fact 71: Gus does not attend, or Dan does not attend, or Cyd does not attend.
Fact 72: Hal attends, or Wendy attends.
Fact 73: Vera attends, or Ann attends.
Fact 74: Dee attends, or Alice attends.
Fact 75: Carol attends, or Cal attends.
Fact 76: Una attends, or Cyd attends, or Tom attends.
Fact 77: Rosa attends, or Eli attends.
Fact 78: Pia attends, or Una does not attend, or Gus attends.
Fact 79: Una does not attend, or Pia does not attend, or Tom attends.
Fact 80: Bob attends, or Tom does not attend, or Ray attends.
Fact 81: Una does not attend, or Ida does not attend, or Ray attends.
Fact 82: Ivan attends, or Nina attends.
Fact 83: Ivan does not attend, or Nina does not attend.
Fact 84: Nina attends, or Cyd does not attend.
Fact 85: Nina does not attend, or Cyd attends.

Which of the following is correct?
(A) It follows from the facts that Ivan attends.
(B) It follows from the facts that Ivan does not attend.
(C) Neither follows from the facts.
Answer with one letter: A, B or C.
```

</details>

| Theory | `A3+1-_Bpro-T_DFalse_sat-first_ENT` | `A1+3-_Bpro-T_DFalse_sat-first_ENT` | (b) eval result | (c) CoT |
|---|---|---|---|---|
| `NULL:EXACT` | B (Ivan does not attend in every model) | B (Ivan does not attend in every model) |  | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `H:SAMPLE-m` | B (every sampled model has the target false) | B (every sampled model has the target false) |  | Several complete satisfying assignments listed; answer = majority over them (entailment: conclusion checked in each). |
| `B1:UP-k` | C (no unit-propagation path; sound relaxation says nothing follows) | C (no unit-propagation path; sound relaxation says nothing follows) |  | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `C0:POLARITY` | A (3+1-) | B (1+3-) |  | One tally of v's own positive vs negative occurrences, then an immediate decision. |
| `B4:FIRST` | A (first disjunct of each fact taken as asserted) | B (first disjunct of each fact taken as asserted) |  | Each disjunction read as its first disjunct ("so X attends"); conclusions drawn from those readings. |
| `E:BP-0 (R-3way, tau=0.2)` | C (M=0.64) | C (M=0.36) | graded: "A follows" where M ≥ 0.8, "neither" where 0.2 < M < 0.8; commits to a probable-but-not-entailed conclusion (A) where the truth is B | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-1 (R-3way, tau=0.2)` | A (M=0.99) | A (M=0.82) | graded: "A follows" where M ≥ 0.8, "neither" where 0.2 < M < 0.8; commits to a probable-but-not-entailed conclusion (A) where the truth is B | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2 (R-3way, tau=0.2)` | A (M=0.99) | C (M=0.59) | graded: "A follows" where M ≥ 0.8, "neither" where 0.2 < M < 0.8; commits to a probable-but-not-entailed conclusion (A) where the truth is B | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-inf (R-3way, tau=0.2)` | A (M=1.00) | B (M=0.00) | graded: "A follows" where M ≥ 0.8, "neither" where 0.2 < M < 0.8; commits to a probable-but-not-entailed conclusion (A) where the truth is B | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `NULL:RANDOM` | uniform over A/B/C | uniform over A/B/C |  | Uninformative trace; answer unrelated to any designed factor. |

**Entailment: how outcomes move weight.** "A" (it follows that the target attends) is a commission error. Among the families here only E (and `B4:FIRST` / `C0`, according to the rendering) predicts it. B1 predicts "C" (sound: nothing follows); exact and `SAMPLE-m` predict "B". So a cell rate of "A" moves weight onto E (or B4 / C0) and away from B1, exact and H, in proportion to that rate. A rate of "C" moves weight onto B1 and low-confidence E; the CNF cells' B contrast separates those two.

---

## 7. E3 cover pairs: two odd cycles vs one even cycle
**Reasoning question.**

- **U** = two disjoint odd m-cycles, which can't be split into two teams. **S** = one even 2m-cycle, which can.
- Every node has degree 2 in both, the counts are identical, and every radius-r ball is a path for r < (m−1)/2.
- So no radius-r procedure can tell them apart for large m.
- **Anchored:** propagation from the fixed people (WP / BP / UP) finds the contradiction only after ~m/2 rounds.
- **Unanchored:** anonymous MP has nothing to propagate, whereas a local procedure that uses names (LOCAL-EXACT) still sees short odd cycles.
- This separates **MP from general local computation**, and both from **exact** (global) solving.
**Controlled factors.** Same names and distractor component; equal node and edge counts; random edge order and orientation. **Varied:** m ∈ {3, …, 15}, anchored, member.
- `E3/m5-anch-U`: ground truth **no**; 16 people, 16 clashes.
<details open><summary>Full prompt: <code>E3/m5-anch-U</code></summary>

```text
The following pairs of people clash:
1. Sid and Hal
2. Yara and Kim
3. Vera and Dee
4. Laura and Eve
5. Bo and Zoe
6. Fay and Lou
7. Eve and Zoe
8. Ann and Hal
9. Ann and Yara
10. Vera and Ken
11. Fay and Frank
12. Lou and Dee
13. Sid and Kim
14. Lou and Ken
15. Bo and Ed
16. Laura and Ed

Ann must be on team A and Bo must be on team B.

Can all 16 people be split into two teams so that no two people who clash are on the same team? Answer with one word: yes or no.
```

</details>
- `E3/m5-anch-S`: ground truth **yes**; 16 people, 16 clashes.
<details><summary>Full prompt: <code>E3/m5-anch-S</code></summary>

```text
The following pairs of people clash:
1. Eve and Sid
2. Laura and Ed
3. Bo and Ed
4. Lou and Ken
5. Eve and Ann
6. Vera and Ken
7. Yara and Bo
8. Laura and Sid
9. Kim and Zoe
10. Zoe and Ann
11. Vera and Dee
12. Fay and Lou
13. Hal and Yara
14. Hal and Kim
15. Frank and Fay
16. Dee and Lou

Ann must be on team A and Bo must be on team B.

Can all 16 people be split into two teams so that no two people who clash are on the same team? Answer with one word: yes or no.
```

</details>
- `E3/m9-anch-U`: ground truth **no**; 24 people, 24 clashes.
<details><summary>Full prompt: <code>E3/m9-anch-U</code></summary>

```text
The following pairs of people clash:
1. Ken and Laura
2. Pia and Lou
3. Ann and Fay
4. Pia and Yara
5. Ed and Kim
6. Ida and Carol
7. Cal and Sue
8. Frank and Ken
9. Sid and Lou
10. Dee and Hal
11. Ed and Eve
12. Heidi and Max
13. Eve and Vera
14. Cal and Ida
15. Sid and Quinn
16. Kim and Zoe
17. Quinn and Bo
18. Ann and Zoe
19. Frank and Yara
20. Vera and Hal
21. Carol and Max
22. Bo and Laura
23. Dee and Fay
24. Carol and Sue

Ann must be on team A and Bo must be on team B.

Can all 24 people be split into two teams so that no two people who clash are on the same team? Answer with one word: yes or no.
```

</details>
- `E3/m9-anch-S`: ground truth **yes**; 24 people, 24 clashes.
<details><summary>Full prompt: <code>E3/m9-anch-S</code></summary>

```text
The following pairs of people clash:
1. Ed and Fay
2. Laura and Ken
3. Carol and Ida
4. Cal and Sue
5. Ann and Vera
6. Hal and Quinn
7. Zoe and Fay
8. Max and Carol
9. Yara and Dee
10. Sid and Dee
11. Kim and Bo
12. Kim and Frank
13. Sue and Carol
14. Pia and Hal
15. Frank and Yara
16. Eve and Bo
17. Ida and Cal
18. Eve and Zoe
19. Ken and Sid
20. Laura and Vera
21. Lou and Ann
22. Ed and Quinn
23. Pia and Lou
24. Max and Heidi

Ann must be on team A and Bo must be on team B.

Can all 24 people be split into two teams so that no two people who clash are on the same team? Answer with one word: yes or no.
```

</details>
- `E3/m5-unanch-U`: ground truth **no**; 16 people, 16 clashes.
<details><summary>Full prompt: <code>E3/m5-unanch-U</code></summary>

```text
The following pairs of people clash:
1. Hal and Kim
2. Ed and Yara
3. Sid and Zoe
4. Sid and Ann
5. Eve and Laura
6. Laura and Zoe
7. Bo and Hal
8. Ken and Vera
9. Dee and Lou
10. Eve and Ann
11. Fay and Lou
12. Kim and Yara
13. Lou and Ken
14. Frank and Fay
15. Vera and Dee
16. Bo and Ed

Can all 16 people be split into two teams so that no two people who clash are on the same team? Answer with one word: yes or no.
```

</details>
- `E3/m5-unanch-S`: ground truth **yes**; 16 people, 16 clashes.
<details><summary>Full prompt: <code>E3/m5-unanch-S</code></summary>

```text
The following pairs of people clash:
1. Yara and Zoe
2. Zoe and Ed
3. Eve and Laura
4. Hal and Ann
5. Sid and Bo
6. Kim and Ann
7. Lou and Fay
8. Ken and Vera
9. Vera and Dee
10. Ken and Lou
11. Fay and Frank
12. Bo and Yara
13. Sid and Laura
14. Hal and Eve
15. Ed and Kim
16. Lou and Dee

Can all 16 people be split into two teams so that no two people who clash are on the same team? Answer with one word: yes or no.
```

</details>

### Computed predictions over the complete set (anchored)
| m | contradiction round (WP/BP/UP) | min radius LOCAL-EXACT | `C1:FIRST-FIT` U / S | `C2:DSATUR` U / S | `F:MIN-CONFLICTS` success S | `NULL:PERCEPTION-NOISE` P(yes) U / S |
|---|---|---|---|---|---|---|
| 3 | 2 | 1 | no / no | no / yes | 1.00 | 0.00 / 0.82 |
| 5 | 3 | 2 | no / yes | no / yes | 1.00 | 0.00 / 0.78 |
| 7 | 4 | 3 | no / no | no / yes | 0.85 | 0.00 / 0.74 |
| 9 | 5 | 4 | no / no | no / yes | 0.64 | 0.00 / 0.71 |
| 11 | 6 | 5 | no / no | no / yes | 0.41 | 0.00 / 0.68 |
| 13 | 7 | 6 | no / no | no / yes | 0.35 | 0.00 / 0.67 |
| 15 | 8 | 7 | no / no | no / yes | 0.13 | 0.00 / 0.65 |

| m (unanchored) | contradiction round | min radius LOCAL-EXACT |
|---|---|---|
| 3 | None | 1 |
| 5 | None | 2 |
| 7 | None | 3 |
| 9 | None | 4 |
| 11 | None | 5 |
| 13 | None | 6 |
| 15 | None | 7 |

### Hypothesis block (items shown)
**(b)** = predicted discrimination Δ(m) = P(no | U) − P(no | S) across m. "Discriminates" means Δ ≥ 0.5; "does not" means Δ ≤ 0.1.
| Theory | `m5-anch-U` | `m5-anch-S` | `m9-anch-U` | `m9-anch-S` | `m5-unanch-U` | `m5-unanch-S` | (b) eval result | (c) CoT |
|---|---|---|---|---|---|---|---|---|
| `NULL:EXACT` | no | yes | no | yes | no | yes | Δ = 1 at every m and both anchorings (needs sequential depth; in direct mode this is the global-computation hypothesis) | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `NULL:NOISY-EXACT` | no | yes | no | yes | no | yes | Δ ≈ 1 − 2ε at every m, unrelated to m | As EXACT, with an isolated slip (misread value) in failing traces, located independently of the designed factor. |
| `NULL:PERCEPTION-NOISE` | no | yes | no | yes | no | yes | Δ = P(no\|U) − P(no\|S) from the table: large at every m, slowly shrinking (misreads rarely flip parity) | Correct reasoning applied to a misquoted clause or edge (the trace restates one constraint wrongly). |
| `NULL:RANDOM` | coin flip | coin flip | coin flip | coin flip | coin flip | coin flip | Δ = 0 | Uninformative trace; answer unrelated to any designed factor. |
| `A1:ALWAYS-YES` | yes | yes | yes | yes | yes | yes | Δ = 0 (always "yes") | No structural reasoning; immediate default answer. |
| `C0/A2:COUNTS` | same as partner item | same as partner item | same as partner item | same as partner item | same as partner item | same as partner item | Δ = 0 at every m (identical counts) | One tally of v's own positive vs negative occurrences, then an immediate decision. |
| `E:WP-t / BP-t` | no if t >= 3 (contradiction at round 3); yes otherwise | yes at every t (no contradiction ever) | no if t >= 5 (contradiction at round 5); yes otherwise | yes at every t (no contradiction ever) | yes at every t (no contradiction ever) | yes at every t (no contradiction ever) | anchored: Δ = 1 for m ≤ 2t−1 (contradiction round ≤ t, table), 0 beyond; unanchored: Δ = 0 at every m | Forcing chains that start at unit clauses or fixed values only; categorical; silent ("cannot be determined") otherwise. |
| `E:LOCAL-EXACT-r` | no if r >= 2; yes otherwise | yes for r < 12 | no if r >= 4; yes otherwise | yes for r < 12 | no if r >= 2; yes otherwise | yes for r < 12 | Δ = 1 for m ≤ 2r+1 in both anchorings (table), 0 beyond | Case split / enumeration restricted to v's r-hop neighbourhood; categorical; no search outside it. |
| `B1:UP-k` | no if k >= 3 | yes (silent) | no if k >= 5 | yes (silent) | yes (silent) | yes (silent) | as WP-t with k rounds | "Clause becomes unit -> forced" chains from unit clauses; nothing graded; "nothing follows" when no unit clause exists. |
| `C1:FIRST-FIT` | no | yes | no | no | no | yes | U "no"; S "no" when mention order creates a dead end (table): Δ small or 0 | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `C2:DSATUR` | no | yes | no | yes | no | yes | Δ = 1 (DSATUR is exact on bipartite graphs) → E3 cannot disconfirm DSATUR vs exact; see E1-S colouring / E4 | Adaptive choice: shortest clause / most constrained node first; no backtracking. |
| `F:MIN-CONFLICTS-k (fail->no)` | no | yes | no | yes | no | yes | S "yes" when found within k, else "no"; U "no" → Δ = success rate (table): indistinguishable from exact when k is large | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| `F:MIN-CONFLICTS-k (fail->yes)` | yes | yes | yes | yes | yes | yes | U "yes" (never certified), S "yes" → Δ = 0 | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (Δ(m) = P(no|U) − P(no|S) for m = 3..15, anchored then unanchored (14 cells)), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.079 at full-study size and 0.32 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:WP/BP-4` vs `B1:UP-4` | 0 | **not separated by this set** | — | — | 0 |
| `E:WP/BP-4` vs `E:LOCAL-EXACT-3` | 1.73 | 0.13 | 0.08 | 0.52 | ≥ 99 / 6.4 |
| `E:WP/BP-4` vs `NULL:EXACT` | 3.32 | 0.07 | 0.04 | 0.27 | ≥ 99 / 23.3 |
| `E:WP/BP-4` vs `C2:DSATUR` | 3.32 | 0.07 | 0.04 | 0.27 | ≥ 99 / 23.3 |
| `E:WP/BP-4` vs `C0/A2:COUNTS` | 1.73 | 0.13 | 0.08 | 0.52 | ≥ 99 / 6.4 |
| `E:WP/BP-4` vs `C1:FIRST-FIT` | 2.00 | 0.11 | 0.06 | 0.45 | ≥ 99 / 8.5 |
| `E:WP/BP-4` vs `NULL:PERCEPTION-NOISE` | 2.38 | 0.09 | 0.05 | 0.38 | ≥ 99 / 12.0 |
| `E:WP/BP-2` vs `E:WP/BP-4` | 1.41 | 0.16 | 0.09 | 0.63 | 69.6 / 4.2 |
| `NULL:EXACT` vs `F:MIN-CONFLICTS (fail->no)` | 1.98 | 0.11 | 0.07 | 0.45 | ≥ 99 / 8.3 |
| `E:LOCAL-EXACT-1` vs `E:LOCAL-EXACT-3` | 2.00 | 0.11 | 0.06 | 0.45 | ≥ 99 / 8.5 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `E:WP/BP-2`, `B1:UP-2` | `E:LOCAL-EXACT-1`: 34.8 (dev 2.1) → π ≤ 0.13; `NULL:RANDOM`/`A1:ALWAYS-YES`/`C0/A2:COUNTS`…: 34.8 (dev 2.1) → π ≤ 0.13; `E:WP/BP-4`/`B1:UP-4`: 69.6 (dev 4.2) → π ≤ 0.09 | MP vs UP-k: use the E1-S soft channel and E2 |
| `E:WP/BP-4`, `B1:UP-4` | `E:WP/BP-2`/`B1:UP-2`: 69.6 (dev 4.2) → π ≤ 0.09; `E:WP/BP-6`/`B1:UP-6`: 69.6 (dev 4.2) → π ≤ 0.09; `E:LOCAL-EXACT-1`: ≥ 99 (dev 6.4) → π ≤ 0.08 | MP vs UP-k: use the E1-S soft channel and E2 |
| `E:WP/BP-6`, `B1:UP-6` | `E:WP/BP-4`/`B1:UP-4`: 69.6 (dev 4.2) → π ≤ 0.09; `F:MIN-CONFLICTS (fail->no)`: ≥ 99 (dev 7.0) → π ≤ 0.07; `E:WP/BP-2`/`B1:UP-2`: ≥ 99 (dev 8.5) → π ≤ 0.06 | MP vs UP-k: use the E1-S soft channel and E2 |
| `E:LOCAL-EXACT-1` | `E:WP/BP-2`/`B1:UP-2`: 34.8 (dev 2.1) → π ≤ 0.13; `E:LOCAL-EXACT-2`: 69.6 (dev 4.2) → π ≤ 0.09; `NULL:RANDOM`/`A1:ALWAYS-YES`/`C0/A2:COUNTS`…: 69.6 (dev 4.2) → π ≤ 0.09 |  |
| `E:LOCAL-EXACT-2` | `E:LOCAL-EXACT-1`: 69.6 (dev 4.2) → π ≤ 0.09; `E:LOCAL-EXACT-3`: 69.6 (dev 4.2) → π ≤ 0.09; `F:MIN-CONFLICTS (fail->no)`: 78.3 (dev 4.8) → π ≤ 0.09 |  |
| `E:LOCAL-EXACT-3` | `F:MIN-CONFLICTS (fail->no)`: 44.9 (dev 2.7) → π ≤ 0.11; `E:LOCAL-EXACT-2`: 69.6 (dev 4.2) → π ≤ 0.09; `E:WP/BP-4`/`B1:UP-4`: ≥ 99 (dev 6.4) → π ≤ 0.08 |  |
| `E:LOCAL-EXACT-5` | `F:MIN-CONFLICTS (fail->no)`: 53.9 (dev 3.3) → π ≤ 0.10; `NULL:PERCEPTION-NOISE`: 83.2 (dev 5.1) → π ≤ 0.08; `NULL:NOISY-EXACT`: ≥ 99 (dev 7.1) → π ≤ 0.07 |  |
| `NULL:EXACT`, `C2:DSATUR` | `NULL:NOISY-EXACT`: 4.9 (dev 0.3) → π ≤ 0.35; `NULL:PERCEPTION-NOISE`: 39.5 (dev 2.4) → π ≤ 0.12; `F:MIN-CONFLICTS (fail->no)`: ≥ 99 (dev 8.3) → π ≤ 0.07 | the listed theories are tied here; the coverage matrix (end of document) lists the sets that separate them |
| `NULL:NOISY-EXACT` | `NULL:EXACT`/`C2:DSATUR`: 4.9 (dev 0.3) → π ≤ 0.35; `NULL:PERCEPTION-NOISE`: 17.2 (dev 1.0) → π ≤ 0.18; `F:MIN-CONFLICTS (fail->no)`: ≥ 99 (dev 6.1) → π ≤ 0.08 |  |
| `NULL:PERCEPTION-NOISE` | `NULL:NOISY-EXACT`: 17.2 (dev 1.0) → π ≤ 0.18; `NULL:EXACT`/`C2:DSATUR`: 39.5 (dev 2.4) → π ≤ 0.12; `F:MIN-CONFLICTS (fail->no)`: 43.7 (dev 2.7) → π ≤ 0.12 |  |
| `NULL:RANDOM`, `A1:ALWAYS-YES`, `C0/A2:COUNTS`, `F:MIN-CONFLICTS (fail->yes)` | `E:WP/BP-2`/`B1:UP-2`: 34.8 (dev 2.1) → π ≤ 0.13; `E:LOCAL-EXACT-1`: 69.6 (dev 4.2) → π ≤ 0.09; `E:WP/BP-4`/`B1:UP-4`: ≥ 99 (dev 6.4) → π ≤ 0.08 | the listed theories are tied here; the coverage matrix (end of document) lists the sets that separate them |
| `C1:FIRST-FIT` | `E:LOCAL-EXACT-2`: ≥ 99 (dev 6.4) → π ≤ 0.08; `E:LOCAL-EXACT-3`: ≥ 99 (dev 6.4) → π ≤ 0.08; `NULL:RANDOM`/`A1:ALWAYS-YES`/`C0/A2:COUNTS`…: ≥ 99 (dev 6.4) → π ≤ 0.08 |  |
| `F:MIN-CONFLICTS (fail->no)` | `NULL:PERCEPTION-NOISE`: 43.7 (dev 2.7) → π ≤ 0.12; `E:LOCAL-EXACT-3`: 44.9 (dev 2.7) → π ≤ 0.11; `E:LOCAL-EXACT-5`: 53.9 (dev 3.3) → π ≤ 0.10 |  |

**SAT framing** (in the JSONL): `E3/m5-anch-U-SAT` truth no, UP conflict at k = no if k >= 4, BP no if t >= 3; `E3/m5-anch-S-SAT` truth yes, UP conflict at k = yes, BP yes.

---

## 8. E4 α sweep on random 3-SAT
**Reasoning question.** Which procedure's success curve *and* failure profile match the model above the budget line? This is the main test against **exact solving** (no failures within budget), **D** (failure → default, rising with n), **F** (near-misses, never UNSAT), and **C2** (early dead ends). The item-level outputs are whole assignments.
**Controlled factors.** n = 12, names alphabetical (a random sample), 3 distinct variables per clause, uniform signs. **Varied:** α (8 levels; 3 shown).
- `E4/alpha3.0`: m = 36; ground truth: SAT; e.g. {"cat": true, "coat": true, "harp": false, "hill": false, "jar": true, "king": true, "lamp": true, "moon": false, "oak": false, "reed": true, "ship": 
<details open><summary>Full prompt: <code>E4/alpha3.0</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (not lamp or shoe or not moon)
2. (not moon or king or lamp)
3. (king or not coat or not ship)
4. (not harp or coat or not hill)
5. (king or oak or coat)
6. (oak or ship or king)
7. (not moon or oak or not jar)
8. (jar or lamp or not hill)
9. (shoe or not reed or ship)
10. (jar or not lamp or reed)
11. (reed or not coat or moon)
12. (not cat or not reed or not oak)
13. (cat or not oak or ship)
14. (not cat or not lamp or not shoe)
15. (cat or not reed or coat)
16. (not hill or harp or not lamp)
17. (not king or not jar or not hill)
18. (not hill or not king or not shoe)
19. (not shoe or not harp or hill)
20. (king or not ship or not hill)
21. (not jar or king or cat)
22. (cat or not jar or not harp)
23. (harp or hill or not moon)
24. (jar or moon or not harp)
25. (not reed or not coat or not moon)
26. (ship or moon or not lamp)
27. (ship or not lamp or cat)
28. (king or reed or harp)
29. (not harp or shoe or not king)
30. (king or not reed or not harp)
31. (not reed or not ship or coat)
32. (not king or not reed or cat)
33. (not king or lamp or reed)
34. (coat or not lamp or moon)
35. (not hill or shoe or king)
36. (jar or not moon or harp)

Find an assignment of True/False values to all variables that satisfies every clause, or state that none exists. Answer with a JSON object mapping every variable to true or false, or with the single word UNSAT.
```

</details>
- `E4/alpha4.2`: m = 50; ground truth: SAT; e.g. {"apple": true, "ball": false, "belt": true, "book": true, "bread": true, "dog": true, "drum": true, "hill": true, "leaf": true, "nail": true, "plum":
<details><summary>Full prompt: <code>E4/alpha4.2</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (not hill or not dog or salt)
2. (not hill or not apple or drum)
3. (salt or book or not nail)
4. (not plum or leaf or not book)
5. (not book or bread or not hill)
6. (belt or not nail or apple)
7. (leaf or not bread or not nail)
8. (not dog or belt or hill)
9. (not book or not belt or dog)
10. (salt or apple or not nail)
11. (not hill or leaf or dog)
12. (dog or not nail or not leaf)
13. (book or dog or not belt)
14. (not book or salt or belt)
15. (ball or apple or not dog)
16. (not dog or leaf or bread)
17. (drum or not apple or dog)
18. (apple or not dog or bread)
19. (belt or not leaf or not apple)
20. (belt or not salt or not plum)
21. (belt or not leaf or dog)
22. (leaf or drum or belt)
23. (leaf or not book or ball)
24. (dog or book or hill)
25. (not ball or not hill or not plum)
26. (not hill or dog or apple)
27. (plum or not bread or not ball)
28. (not hill or book or dog)
29. (nail or belt or bread)
30. (belt or plum or not dog)
31. (not hill or salt or not drum)
32. (book or leaf or belt)
33. (not ball or not hill or nail)
34. (plum or not dog or not ball)
35. (not ball or not bread or hill)
36. (dog or not belt or not hill)
37. (hill or not plum or not salt)
38. (apple or nail or not drum)
39. (not hill or not plum or dog)
40. (leaf or not drum or hill)
41. (plum or not dog or belt)
42. (not ball or not nail or not plum)
43. (apple or not nail or hill)
44. (not belt or not leaf or bread)
45. (belt or plum or dog)
46. (leaf or not apple or not drum)
47. (not book or salt or belt)
48. (not belt or apple or leaf)
49. (hill or salt or belt)
50. (not apple or not belt or book)

Find an assignment of True/False values to all variables that satisfies every clause, or state that none exists. Answer with a JSON object mapping every variable to true or false, or with the single word UNSAT.
```

</details>
- `E4/alpha5.0`: m = 60; ground truth: SAT; e.g. {"book": false, "cat": false, "cave": false, "coin": false, "corn": false, "gold": true, "hive": false, "nail": false, "nut": false, "rope": false, "s
<details><summary>Full prompt: <code>E4/alpha5.0</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (cave or not corn or not ship)
2. (not hive or not rope or coin)
3. (rope or nut or not book)
4. (not corn or gold or not book)
5. (ship or not coin or cave)
6. (book or rope or not salt)
7. (rope or salt or gold)
8. (hive or not nut or not ship)
9. (not gold or hive or not coin)
10. (not cat or nut or salt)
11. (book or cat or not cave)
12. (not gold or not cave or not ship)
13. (ship or nail or corn)
14. (gold or not nail or book)
15. (coin or not cat or gold)
16. (not coin or hive or not corn)
17. (not hive or ship or cave)
18. (hive or coin or not rope)
19. (not hive or not gold or not ship)
20. (gold or salt or nut)
21. (book or not salt or not hive)
22. (book or not cat or salt)
23. (corn or not cave or nail)
24. (not hive or cat or book)
25. (gold or cave or book)
26. (salt or hive or not nut)
27. (rope or not nut or cave)
28. (ship or nut or gold)
29. (not salt or rope or book)
30. (not cave or hive or cat)
31. (not gold or not book or not nail)
32. (not ship or not salt or not gold)
33. (not nut or not hive or gold)
34. (gold or rope or not book)
35. (not book or nut or nail)
36. (not cave or corn or nail)
37. (not salt or hive or not corn)
38. (not book or not hive or not gold)
39. (not rope or not ship or not hive)
40. (not cave or not book or not corn)
41. (not coin or rope or hive)
42. (not cat or hive or not ship)
43. (rope or not nail or not cave)
44. (book or rope or gold)
45. (hive or not cave or ship)
46. (salt or gold or coin)
47. (cave or not nail or corn)
48. (not book or nail or salt)
49. (salt or gold or nut)
50. (book or not nut or not ship)
51. (nail or not coin or not corn)
52. (not ship or hive or not rope)
53. (not corn or nut or not gold)
54. (not coin or cat or not salt)
55. (ship or not nail or not coin)
56. (gold or not cat or cave)
57. (not salt or rope or not nail)
58. (not gold or not cat or not corn)
59. (cat or not hive or nut)
60. (cat or gold or not nail)

Find an assignment of True/False values to all variables that satisfies every clause, or state that none exists. Answer with a JSON object mapping every variable to true or false, or with the single word UNSAT.
```

</details>

### Computed outputs over the complete sweep (violated clauses of the returned assignment; "UNSAT" where the procedure says so)
| Theory | α=3.0 | α=3.5 | α=3.8 | α=4.0 | α=4.2 | α=4.4 | α=4.7 | α=5.0 |
|---|---|---|---|---|---|---|---|---|
| truth | SAT | SAT | SAT | SAT | SAT | UNSAT | SAT | SAT |
| `NULL:EXACT` | 0 viol | 0 viol | 0 viol | 0 viol | 0 viol | UNSAT | 0 viol | 0 viol |
| `NULL:RANDOM` | 4.5 viol | 5.2 viol | 5.8 viol | 6.0 viol | 6.2 viol | 6.6 viol | 7.0 viol | 7.5 viol |
| `E:BP-0+round` | 2 viol | 1 viol | 5 viol | 2 viol | 0 viol | 1 viol | 3 viol | 4 viol |
| `E:BP-1+round` | 1 viol | 2 viol | 1 viol | 1 viol | 0 viol | 1 viol | 2 viol | 3 viol |
| `E:BP-2+round` | 1 viol | 1 viol | 1 viol | 1 viol | 0 viol | 1 viol | 0 viol | 3 viol |
| `E:BP-inf+round` | 0 viol | 1 viol | 1 viol | 1 viol | 0 viol | 1 viol | 0 viol | 0 viol |
| `E:BP-DEC-MAX` | 0 viol | 0 viol | 0 viol | 0 viol | 0 viol | UNSAT | 0 viol | 0 viol |
| `E:BP-DEC-OUT` | 0 viol | 0 viol | UNSAT | 0 viol | 0 viol | UNSAT | 0 viol | 0 viol |
| `E:SP-30` | trivial fixed point (no frozen variables | non-trivial surveys | non-trivial surveys | non-trivial surveys | trivial fixed point (no frozen variables | non-trivial surveys | non-trivial surveys | non-trivial surveys |
| `C2:UC` | UNSAT | 0 viol | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `C2:GUC` | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| `C1:GREEDY` | 0 viol | 0 viol | 2 viol | 3 viol | 1 viol | 1 viol | 1 viol | 2 viol |
| `D:DPLL-4` | 0 viol | 1 viol | 4 viol | 0 viol | 0 viol | 1 viol | 3 viol | 0 viol |
| `D:DPLL-16` | 0 viol | 0 viol | 0 viol | 0 viol | 0 viol | UNSAT | 0 viol | 0 viol |
| `D:DPLL-inf` | 0 viol | 0 viol | 0 viol | 0 viol | 0 viol | UNSAT | 0 viol | 0 viol |
| `F:WALK-50` | 90% solved; median viol 0 | 84% solved; median viol 0 | 62% solved; median viol 0 | 52% solved; median viol 0 | 98% solved; median viol 0 | 0% solved; median viol 2 | 72% solved; median viol 0 | 56% solved; median viol 0 |
| `F:WALK-500` | 100% solved; median viol 0 | 100% solved; median viol 0 | 96% solved; median viol 0 | 100% solved; median viol 0 | 100% solved; median viol 0 | 0% solved; median viol 1 | 100% solved; median viol 0 | 100% solved; median viol 0 |

### Hypothesis block
| Theory | (a) outputs | (b) eval result (set level; pre-registered: joint likelihood over success, false-UNSAT and violation profile; best fit by ΔLL ≥ 10 nats) | (c) CoT |
|---|---|---|---|
| `NULL:EXACT` | α3.0: a satisfying assignment; α4.2: a satisfying assignment; α5.0: a satisfying assignment | correct on every item within budget: no violations, UNSAT exactly on UNSAT items; at n* above budget, the model's failures must then be explained by censoring | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `NULL:RANDOM` | α3.0: uniform random assignment; α4.2: uniform random assignment; α5.0: uniform random assignment | ≈ m/8 violated clauses at every α; never UNSAT | Uninformative trace; answer unrelated to any designed factor. |
| `E:BP-0+round` | α3.0: assignment; α4.2: assignment; α5.0: assignment | many violations from moderate α on; violation count rises smoothly with α | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-1+round` | α3.0: assignment; α4.2: assignment; α5.0: assignment | as BP-0+round, fewer violations | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-2+round` | α3.0: assignment; α4.2: assignment; α5.0: assignment | as BP-0+round, fewer violations | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-inf+round` | α3.0: assignment; α4.2: assignment; α5.0: assignment | as BP-0+round, fewer violations | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:BP-DEC-MAX` | α3.0: assignment; α4.2: assignment; α5.0: assignment | succeeds below its simulated knee, then FAIL → false UNSAT on SAT items; no near-misses | Repeated tally -> fix the most-biased variable -> simplify -> re-tally; no backtracking; FAIL ends in "UNSAT". |
| `E:BP-DEC-OUT` | α3.0: assignment; α4.2: assignment; α5.0: assignment | as BP-DEC-MAX with an earlier knee (fixed order) | Repeated tally -> fix the most-biased variable -> simplify -> re-tally; no backtracking; FAIL ends in "UNSAT". |
| `E:SP-30` | α3.0: trivial fixed point (no frozen variables) -> hands; α4.2: trivial fixed point (no frozen variables) -> hands; α5.0: non-trivial surveys | trivial fixed point at this n → identical to BP-DEC-MAX | Survey tallies over clusters; in practice indistinguishable from BP-DEC at these sizes (trivial fixed point). |
| `C2:UC` | α3.0: UNSAT (dead end); α4.2: UNSAT (dead end); α5.0: UNSAT (dead end) | early dead ends → UNSAT claims on SAT items at low α | Adaptive choice: shortest clause / most constrained node first; no backtracking. |
| `C2:GUC` | α3.0: UNSAT (dead end); α4.2: UNSAT (dead end); α5.0: UNSAT (dead end) | later dead ends than UC | Adaptive choice: shortest clause / most constrained node first; no backtracking. |
| `C1:GREEDY` | α3.0: assignment; α4.2: assignment; α5.0: assignment | violations among late-assigned variables; never UNSAT | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `D:DPLL-4` | α3.0: budget exhausted -> default (partial + polarity); α4.2: assignment; α5.0: assignment | budget exhaustion → default assignment with violations, increasing with α and n | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `D:DPLL-16` | α3.0: assignment; α4.2: assignment; α5.0: assignment | as DPLL-4, later | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `D:DPLL-inf` | α3.0: assignment; α4.2: assignment; α5.0: assignment | exact (search cost peaks near α_c) | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `F:WALK-50` | α3.0: satisfying in 90% of runs; otherwise a near-miss; α4.2: satisfying in 98% of runs; otherwise a near-miss; α5.0: satisfying in 56% of runs; otherwise a near-miss | near-misses (1–3 violations) when unsolved; never UNSAT | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| `F:WALK-500` | α3.0: satisfying in 100% of runs; otherwise a near-miss; α4.2: satisfying in 100% of runs; otherwise a near-miss; α5.0: satisfying in 100% of runs; otherwise a near-miss | near-misses when unsolved; never UNSAT | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |

**Failure-profile categories per α** (S = solved / correct UNSAT, U = claims UNSAT, N = near-miss with ≤ 3 violations, V = > 3 violations):

| Theory | α=3.0 | α=3.5 | α=3.8 | α=4.0 | α=4.2 | α=4.4 | α=4.7 | α=5.0 |
|---|---|---|---|---|---|---|---|---|
| `NULL:EXACT` | S | S | S | S | S | U | S | S |
| `NULL:RANDOM` | V | V | V | V | V | V | V | V |
| `E:BP-0+round` | N | N | V | N | S | N | N | V |
| `E:BP-1+round` | N | N | N | N | S | N | N | N |
| `E:BP-2+round` | N | N | N | N | S | N | S | N |
| `E:BP-inf+round` | S | N | N | N | S | N | S | S |
| `E:BP-DEC-MAX` | S | S | S | S | S | U | S | S |
| `E:BP-DEC-OUT` | S | S | U | S | S | U | S | S |
| `E:SP-30` | S | S | S | S | S | U | S | S |
| `C2:UC` | U | S | U | U | U | U | U | U |
| `C2:GUC` | U | U | U | U | U | U | U | U |
| `C1:GREEDY` | S | S | N | N | N | N | N | N |
| `D:DPLL-4` | S | N | V | S | S | N | N | S |
| `D:DPLL-16` | S | S | S | S | S | U | S | S |
| `D:DPLL-inf` | S | S | S | S | S | U | S | S |
| `F:WALK-50` | S | S | S | S | S | N | S | S |
| `F:WALK-500` | S | S | S | S | S | N | S | S |

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (one-hot failure category (S/U/N/V) at each of 8 α levels), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.09 at full-study size and 0.22 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:BP-DEC-MAX` vs `F:WALK-500` | 1.41 | 0.18 | 0.10 | 0.44 | 53.6 / 9.0 |
| `E:BP-DEC-MAX` vs `D:DPLL-16` | 0 | **not separated by this set** | — | — | 0 |
| `E:BP-DEC-MAX` vs `C2:GUC` | 3.74 | 0.07 | 0.04 | 0.16 | ≥ 99 / 62.8 |
| `E:BP-DEC-MAX` vs `NULL:EXACT` | 0 | **not separated by this set** | — | — | 0 |
| `E:BP-DEC-MAX` vs `E:BP-2+round` | 3.46 | 0.07 | 0.04 | 0.18 | ≥ 99 / 53.8 |
| `E:BP-DEC-MAX` vs `E:BP-DEC-OUT` | 1.41 | 0.18 | 0.10 | 0.44 | 53.6 / 9.0 |
| `E:BP-DEC-MAX` vs `C1:GREEDY` | 3.46 | 0.07 | 0.04 | 0.18 | ≥ 99 / 53.8 |
| `E:BP-DEC-MAX` vs `NULL:RANDOM` | 4.00 | 0.06 | 0.04 | 0.15 | ≥ 99 / 71.8 |
| `E:BP-0+round` vs `E:BP-inf+round` | 2.83 | 0.09 | 0.05 | 0.22 | ≥ 99 / 35.9 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `NULL:EXACT`, `E:BP-DEC-MAX`, `E:SP-30`, `D:DPLL-16`, `D:DPLL-inf` | `E:BP-DEC-OUT`: 53.6 (dev 9.0) → π ≤ 0.10; `F:WALK-50`/`F:WALK-500`: 53.6 (dev 9.0) → π ≤ 0.10; `E:BP-inf+round`: ≥ 99 (dev 35.9) → π ≤ 0.05 | the listed theories are tied here; larger n and α-level replication (the full sweep has 3 n × 8 α × 30 items); E6b for decimation vs search; the coverage matrix (end of document) lists the sets that separate them |
| `NULL:RANDOM` | `E:BP-0+round`: ≥ 99 (dev 53.8) → π ≤ 0.04; `D:DPLL-4`: ≥ 99 (dev 62.8) → π ≤ 0.04; `NULL:EXACT`/`E:BP-DEC-MAX`/`E:SP-30`…: ≥ 99 (dev 71.8) → π ≤ 0.04 |  |
| `E:BP-0+round` | `E:BP-1+round`: ≥ 99 (dev 17.9) → π ≤ 0.07; `E:BP-2+round`: ≥ 99 (dev 26.9) → π ≤ 0.06; `D:DPLL-4`: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `E:BP-1+round` | `E:BP-2+round`: 53.6 (dev 9.0) → π ≤ 0.10; `E:BP-0+round`: ≥ 99 (dev 17.9) → π ≤ 0.07; `E:BP-inf+round`: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `E:BP-2+round` | `E:BP-1+round`: 53.6 (dev 9.0) → π ≤ 0.10; `E:BP-inf+round`: ≥ 99 (dev 17.9) → π ≤ 0.07; `E:BP-0+round`: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `E:BP-inf+round` | `E:BP-2+round`: ≥ 99 (dev 17.9) → π ≤ 0.07; `E:BP-1+round`: ≥ 99 (dev 26.9) → π ≤ 0.06; `D:DPLL-4`: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `E:BP-DEC-OUT` | `NULL:EXACT`/`E:BP-DEC-MAX`/`E:SP-30`…: 53.6 (dev 9.0) → π ≤ 0.10; `F:WALK-50`/`F:WALK-500`: ≥ 99 (dev 17.9) → π ≤ 0.07; `E:BP-inf+round`: ≥ 99 (dev 35.9) → π ≤ 0.05 |  |
| `C2:UC` | `C2:GUC`: 53.6 (dev 9.0) → π ≤ 0.10; `E:BP-DEC-OUT`: ≥ 99 (dev 44.9) → π ≤ 0.05; `NULL:EXACT`/`E:BP-DEC-MAX`/`E:SP-30`…: ≥ 99 (dev 53.8) → π ≤ 0.04 |  |
| `C2:GUC` | `C2:UC`: 53.6 (dev 9.0) → π ≤ 0.10; `E:BP-DEC-OUT`: ≥ 99 (dev 53.8) → π ≤ 0.04; `NULL:EXACT`/`E:BP-DEC-MAX`/`E:SP-30`…: ≥ 99 (dev 62.8) → π ≤ 0.04 |  |
| `C1:GREEDY` | `E:BP-1+round`: ≥ 99 (dev 26.9) → π ≤ 0.06; `E:BP-2+round`: ≥ 99 (dev 35.9) → π ≤ 0.05; `E:BP-inf+round`: ≥ 99 (dev 35.9) → π ≤ 0.05 |  |
| `D:DPLL-4` | `E:BP-0+round`: ≥ 99 (dev 26.9) → π ≤ 0.06; `E:BP-inf+round`: ≥ 99 (dev 26.9) → π ≤ 0.06; `F:WALK-50`/`F:WALK-500`: ≥ 99 (dev 26.9) → π ≤ 0.06 |  |
| `F:WALK-50`, `F:WALK-500` | `NULL:EXACT`/`E:BP-DEC-MAX`/`E:SP-30`…: 53.6 (dev 9.0) → π ≤ 0.10; `E:BP-DEC-OUT`: ≥ 99 (dev 17.9) → π ≤ 0.07; `E:BP-inf+round`: ≥ 99 (dev 26.9) → π ≤ 0.06 | the listed theories are tied here; the coverage matrix (end of document) lists the sets that separate them |

**Key contrasts.**

- **MP vs exact:** BP-DEC predicts false UNSAT on SAT items; exact never does.
- **MP vs `UP-k`:** not addressed here (UP alone returns no assignment). Use E1-S soft and E2.
- **MP vs C0:** BP-0+round is the C0-style one-pass assignment; it is separated from BP-DEC by the violation profile.

---

## 9. E5 calibration: whose marginals do free choices follow?
**Reasoning question.** When the model picks values for variables that aren't forced (in solutions it finds), do its choices follow:

- BP-t (t ≥ 1) marginals;
- its own polarity (t = 0, C0);
- exact solution marginals (a uniform sampler: H, or "solves and samples exactly");
- the bias of a particular solver?

**Tree vs loopy:** on trees BP-∞ = exact, so only loopy formulas separate MP from exact. **Lifts:** F ∪ G and its 2-lift F̃ have identical BP on corresponding variables at every t, but different exact marginals.

### `E5/tree-like` (10 variables, 7 clauses; factor graph is a forest: True)
<details open><summary>Full prompt: <code>E5/tree-like</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (not mint or plum)
2. (mint or ring)
3. (not ring or lake or dog)
4. (not ring or book)
5. (not plum or pear)
6. (not plum or not tree)
7. (mint or not snow or not wolf)

Find an assignment of True/False values to all variables that satisfies every clause. Answer with a JSON object mapping every variable to true or false.
```

</details>
| Variable | `exact` | `BP-0` | `BP-1` | `BP-2` | `BP-inf` | `POLARITY` | `DPLL-POL` | `E-in-D` | `GREEDY` | `BP-DEC-MAX` | `WALK(valid runs)` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `ring` | 0.64 | 0.429 | 0.484 | 0.64 | 0.64 | False | False | True | False | True | 0.61 |
| `plum` | 0.596 | 0.333 | 0.478 | 0.596 | 0.596 | False | True | False | False | False | 0.59 |
| `mint` | 0.494 | 0.571 | 0.494 | 0.494 | 0.494 | True | True | False | True | False | 0.5 |
| `snow` | 0.416 | 0.429 | 0.429 | 0.416 | 0.416 | False | True | False | True | False | 0.435 |
| `wolf` | 0.416 | 0.429 | 0.429 | 0.416 | 0.416 | False | True | True | True | True | 0.475 |
| `lake` | 0.607 | 0.571 | 0.571 | 0.581 | 0.607 | True | True | True | True | True | 0.525 |

### `E5/loopy` (10 variables, 22 clauses; factor graph is a forest: False)
<details><summary>Full prompt: <code>E5/loopy</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (rose or not nest)
2. (not oak or not bag)
3. (box or door or bread)
4. (not map or not door or not bag)
5. (nest or not map or sea)
6. (map or box or not rose)
7. (not bag or oak or not map)
8. (not sock or not door)
9. (bread or not rose or nest)
10. (not rose or sock or door)
11. (not sea or not bread or not map)
12. (not bag or rose or sock)
13. (nest or not sea)
14. (oak or not nest or not map)
15. (oak or not sea)
16. (not rose or oak or not nest)
17. (nest or map or bread)
18. (bread or not sock)
19. (door or not oak or map)
20. (sock or not map or sea)
21. (not bag or not box or not bread)
22. (not oak or sock or rose)

Find an assignment of True/False values to all variables that satisfies every clause. Answer with a JSON object mapping every variable to true or false.
```

</details>
| Variable | `exact` | `BP-0` | `BP-1` | `BP-2` | `BP-inf` | `POLARITY` | `DPLL-POL` | `E-in-D` | `GREEDY` | `BP-DEC-MAX` | `WALK(valid runs)` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `rose` | 0.611 | 0.529 | 0.601 | 0.574 | 0.39 | False | False | True | False | False | 0.66 |
| `oak` | 0.5 | 0.571 | 0.506 | 0.438 | 0.224 | True | False | True | True | False | 0.56 |
| `nest` | 0.444 | 0.571 | 0.447 | 0.279 | 0.24 | True | False | True | True | False | 0.545 |
| `sock` | 0.333 | 0.441 | 0.433 | 0.384 | 0.407 | True | True | False | True | True | 0.375 |
| `door` | 0.556 | 0.471 | 0.576 | 0.58 | 0.436 | True | False | True | True | False | 0.515 |
| `sea` | 0.222 | 0.25 | 0.153 | 0.138 | 0.053 | False | False | True | True | False | 0.245 |

### `E5/lift-F+G` (12 variables, 22 clauses; factor graph is a forest: False)
<details><summary>Full prompt: <code>E5/lift-F+G</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (not fish or not shoe or not seed)
2. (seed or coin or cup)
3. (iron or nail)
4. (seed or cup or cave)
5. (seed or cave)
6. (cup or seed or coin)
7. (not coin or seed or not shoe)
8. (cup or not coin or fish)
9. (iron or nail or ship)
10. (not coin or cave or cup)
11. (ship or iron)
12. (iron or hat or nail)
13. (iron or not ship or hat)
14. (cup or not shoe)
15. (bean or nail)
16. (not cave or cup)
17. (not iron or not bean or ink)
18. (cave or not coin or not seed)
19. (not hat or not iron or ink)
20. (not ink or not nail)
21. (not hat or nail or bean)
22. (ink or not nail)

Find an assignment of True/False values to all variables that satisfies every clause. Answer with a JSON object mapping every variable to true or false.
```

</details>
| Variable | `exact` | `BP-0` | `BP-1` | `BP-2` | `BP-inf` | `POLARITY` | `DPLL-POL` | `E-in-D` | `GREEDY` | `BP-DEC-MAX` | `WALK(valid runs)` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `bean` | 1.0 | 0.667 | 0.592 | 0.851 | 1.0 | True | True | True | False | True | 1.0 |
| `ink` | 1.0 | 0.64 | 0.847 | 0.75 | 1.0 | True | True | True | True | True | 1.0 |
| `nail` | 0.0 | 0.703 | 0.311 | 0.069 | 0.0 | True | False | False | True | False | 0.0 |

### `E5/lift-Ftilde` (12 variables, 22 clauses; factor graph is a forest: False)
<details><summary>Full prompt: <code>E5/lift-Ftilde</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (not pen or fern or wall)
2. (bowl or pen or fern)
3. (star or kite or pond)
4. (not lamp or not pond)
5. (bowl or not belt or pen)
6. (pine or star)
7. (hive or not pond)
8. (not kite or pond or cake)
9. (star or fern or belt)
10. (cake or fern)
11. (star or not pine or kite)
12. (wall or pond)
13. (bowl or pond or pine)
14. (not star or not cake or hive)
15. (not hive or not fern)
16. (bowl or fern)
17. (lamp or not fern)
18. (not kite or not star or hive)
19. (belt or bowl)
20. (not bowl or not wall or lamp)
21. (star or pond)
22. (not pen or not bowl or lamp)

Find an assignment of True/False values to all variables that satisfies every clause. Answer with a JSON object mapping every variable to true or false.
```

</details>
| Variable | `exact` | `BP-0` | `BP-1` | `BP-2` | `BP-inf` | `POLARITY` | `DPLL-POL` | `E-in-D` | `GREEDY` | `BP-DEC-MAX` | `WALK(valid runs)` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `wall` | 0.735 | 0.667 | 0.592 | 0.851 | 1.0 | True | True | False | True | True | 0.68 |
| `cake` | 0.735 | 0.667 | 0.592 | 0.851 | 1.0 | True | False | True | True | True | 0.655 |
| `lamp` | 0.735 | 0.64 | 0.847 | 0.75 | 1.0 | True | True | False | True | True | 0.68 |
| `hive` | 0.735 | 0.64 | 0.847 | 0.75 | 1.0 | True | False | True | True | True | 0.655 |
| `pond` | 0.265 | 0.703 | 0.311 | 0.069 | 0.0 | True | False | True | False | False | 0.32 |
| `fern` | 0.265 | 0.703 | 0.311 | 0.069 | 0.0 | True | True | False | True | False | 0.345 |

**Lift check (computed).** For each target x: exact marginal in F ∪ G vs in F̃ (copy x₀), and BP-∞ in both:

| target | exact F∪G | exact F̃ | BP-∞ F∪G | BP-∞ F̃ (x₀, x₁) |
|---|---|---|---|---|
| `bean` ↔ `wall`,`cake` | 1.0 | 0.735 | 1.0 | 1.0, 1.0 |
| `ink` ↔ `lamp`,`hive` | 1.0 | 0.735 | 1.0 | 1.0, 1.0 |
| `nail` ↔ `pond`,`fern` | 0.0 | 0.265 | 0.0 | 0.0, 0.0 |

### Hypothesis block
| Theory | (a) output (per-variable choices) | (b) eval result (pre-registered) | (c) CoT |
|---|---|---|---|
| `E:BP-t` (t ≥ 1) | frequencies follow the BP-t column | best fit is BP-t with t ≥ 1, ΔLL ≥ 10 over BP-0 and over exact on loopy formulas; lift slope ≈ 0 (CI excludes 0.4) | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `E:E-in-D` | the E-in-D column (deterministic solver: one solution) | frequencies concentrate on the E-in-D solution's values; lift slope partial | Search with tentative assignments whose values are justified by neighbours' tendencies; propagation; backtracking on conflict. |
| `E:BP-DEC-MAX` | the BP-DEC column | same as E-in-D, with no backtracking | Repeated tally -> fix the most-biased variable -> simplify -> re-tally; no backtracking; FAIL ends in "UNSAT". |
| `C0:POLARITY` | the POLARITY column | best fit is BP-0 / POLARITY; lift slope ≈ 0 | One tally of v's own positive vs negative occurrences, then an immediate decision. |
| `C1:GREEDY` | the GREEDY column | order-based scores win | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `D:DPLL-POL` | the DPLL-POL column | solution values of polarity-ordered DPLL win | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| `F:WALK-k` | the WALK column | WALK frequencies win | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| `H:SAMPLER` / solves-and-samples-exactly | the exact column | exact marginals win on loopy formulas; lift slope ≈ calibration slope (≥ 0.4) | Several complete satisfying assignments listed; answer = majority over them (entailment: conclusion checked in each). |
| `NULL:EXACT` (solves, no sampling) | any solution | no systematic preference: frequencies fit no score better than the constant; lift slope undefined | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |
| `NULL:PERCEPTION-NOISE` | exact marginals of misread formulas | ≈ exact column, attenuated toward 0.5 | Correct reasoning applied to a misquoted clause or edge (the trace restates one constraint wrongly). |
| `NULL:RANDOM` | 0.5 | fits nothing; lift slope 0 | Uninformative trace; answer unrelated to any designed factor. |

BP-t enters E5 as a *sampler* with probability-matching to its marginals: free choices follow the marginal. Deterministic solvers (DPLL, E-in-D, GREEDY, BP-DEC) give one solution, so their frequency vector is 0/1.

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (per-variable frequency of True across the 4 example formulas (SE scaled from 8 samples per formula to the full study's 192 formulas)), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.026 at full-study size and 0.08 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:BP-1` vs `E:BP-0` | 0.90 | 0.08 | 0.05 | 0.25 | ≥ 99 / 27.5 |
| `E:BP-1` vs `C0:POLARITY` | 2.56 | 0.03 | 0.02 | 0.09 | ≥ 99 / ≥ 99 |
| `E:BP-inf` vs `H:SAMPLER` | 0.85 | 0.09 | 0.05 | 0.26 | ≥ 99 / 24.5 |
| `E:BP-1` vs `H:SAMPLER` | 0.76 | 0.10 | 0.06 | 0.30 | ≥ 99 / 19.5 |
| `E:BP-1` vs `D:DPLL-POL` | 2.86 | 0.03 | 0.01 | 0.08 | ≥ 99 / ≥ 99 |
| `E:BP-1` vs `F:WALK-k` | 0.75 | 0.10 | 0.06 | 0.30 | ≥ 99 / 19.3 |
| `E:BP-1` vs `NULL:RANDOM` | 1.37 | 0.05 | 0.03 | 0.16 | ≥ 99 / 63.4 |
| `E:BP-1` vs `E:BP-inf` | 1.14 | 0.06 | 0.04 | 0.20 | ≥ 99 / 44.4 |
| `E:E-in-D` vs `D:DPLL-POL` | 4.58 | 0.02 | 0.01 | 0.05 | ≥ 99 / ≥ 99 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `H:SAMPLER` | `F:WALK-k`: 61.2 (dev 6.5) → π ≤ 0.10; `E:BP-2`: 98.7 (dev 10.4) → π ≤ 0.08; `E:BP-1`: ≥ 99 (dev 19.5) → π ≤ 0.06 |  |
| `E:BP-0` | `E:BP-1`: ≥ 99 (dev 27.5) → π ≤ 0.05; `F:WALK-k`: ≥ 99 (dev 45.1) → π ≤ 0.04; `NULL:RANDOM`: ≥ 99 (dev 53.1) → π ≤ 0.03 |  |
| `E:BP-1` | `E:BP-2`: ≥ 99 (dev 18.8) → π ≤ 0.06; `F:WALK-k`: ≥ 99 (dev 19.3) → π ≤ 0.06; `H:SAMPLER`: ≥ 99 (dev 19.5) → π ≤ 0.06 |  |
| `E:BP-2` | `H:SAMPLER`: 98.7 (dev 10.4) → π ≤ 0.08; `E:BP-inf`: ≥ 99 (dev 15.7) → π ≤ 0.06; `F:WALK-k`: ≥ 99 (dev 18.1) → π ≤ 0.06 |  |
| `E:BP-inf` | `E:BP-2`: ≥ 99 (dev 15.7) → π ≤ 0.06; `H:SAMPLER`: ≥ 99 (dev 24.5) → π ≤ 0.05; `F:WALK-k`: ≥ 99 (dev 42.9) → π ≤ 0.04 |  |
| `C0:POLARITY` | `E:BP-0`: ≥ 99 (dev ≥ 99) → π ≤ 0.02; `E:BP-1`: ≥ 99 (dev ≥ 99) → π ≤ 0.02; `C1:GREEDY`: ≥ 99 (dev ≥ 99) → π ≤ 0.02 |  |
| `D:DPLL-POL` | `H:SAMPLER`: ≥ 99 (dev ≥ 99) → π ≤ 0.02; `F:WALK-k`: ≥ 99 (dev ≥ 99) → π ≤ 0.02; `E:BP-2`: ≥ 99 (dev ≥ 99) → π ≤ 0.01 |  |
| `E:E-in-D` | `F:WALK-k`: ≥ 99 (dev ≥ 99) → π ≤ 0.01; `H:SAMPLER`: ≥ 99 (dev ≥ 99) → π ≤ 0.01; `E:BP-0`: ≥ 99 (dev ≥ 99) → π ≤ 0.01 |  |
| `C1:GREEDY` | `C0:POLARITY`: ≥ 99 (dev ≥ 99) → π ≤ 0.02; `E:BP-0`: ≥ 99 (dev ≥ 99) → π ≤ 0.02; `E:BP-1`: ≥ 99 (dev ≥ 99) → π ≤ 0.01 |  |
| `E:BP-DEC-MAX` | `E:BP-inf`: ≥ 99 (dev ≥ 99) → π ≤ 0.02; `E:BP-2`: ≥ 99 (dev ≥ 99) → π ≤ 0.02; `H:SAMPLER`: ≥ 99 (dev ≥ 99) → π ≤ 0.02 |  |
| `F:WALK-k` | `H:SAMPLER`: 61.2 (dev 6.5) → π ≤ 0.10; `E:BP-2`: ≥ 99 (dev 18.1) → π ≤ 0.06; `E:BP-1`: ≥ 99 (dev 19.3) → π ≤ 0.06 |  |
| `NULL:RANDOM` | `E:BP-0`: ≥ 99 (dev 53.1) → π ≤ 0.03; `E:BP-1`: ≥ 99 (dev 63.4) → π ≤ 0.03; `F:WALK-k`: ≥ 99 (dev 81.7) → π ≤ 0.03 |  |

**Key contrasts.**

- **MP vs C0:** the BP-t vs BP-0 columns on the tree-like item (variables listed where they disagree).
- **MP vs exact:** the loopy item and the lift pair.
- **MP vs `UP-k`:** there are no unit clauses, so UP gives no preference (as `NULL:RANDOM` here).

---

## 10. E6 decimation: how does an early commitment shape later ones?
**Reasoning question.** When the assignment is produced one variable at a time, flip the first committed value. Do later values move:

- **through not-yet-committed neighbours** (BP-guided decimation);
- **only at distance 1** (myopic greedy);
- **not at all** (one-pass BP + rounding);
- **as exact conditioning** (all open paths, not radius-limited)?

The factor graph is a tree, so a committed intermediate *blocks* the influence.
- `E6/E6a-free`: ground truth: any satisfying assignment (both values of bowl extend to solutions: exact P(True)=0.29). Stand-in free run (BP-DEC-OUT-∞): `{"bowl": false, "box": true, "coin": true, "corn": false, "fish": true, "hive": false, "lamp": true, "lock": true, "map": true, "star": true}`.
- `E6/E6a-forced-flip`: the assistant turn is teacher-forced to start `{"bowl": true,`; later values are read under the model's own free-run prefix.
<details open><summary>Full prompt: <code>E6/E6a-free</code></summary>

```text
Below is a Boolean formula in conjunctive normal form. Each numbered line is a clause; a clause is satisfied when at least one of its literals is true, and "not x" is the negation of variable x.

Clauses:
1. (not bowl or fish or not lamp)
2. (fish or coin)
3. (not bowl or star)
4. (lamp or box or map)
5. (box or corn)
6. (not corn or hive)
7. (not hive or not lock)

Find an assignment that satisfies every clause. Answer with a JSON object that lists the variables in alphabetical order, mapping each to true or false.
```

</details>

**Computed Δ (P(True) after flip − before) per later variable:**

| Variable | `dist` | `path_status` | `BP-DEC-OUT-1` | `BP-DEC-OUT-2` | `BP-DEC-OUT-inf` | `exact-conditional` | `GREEDY(myopic)` | `BP-t+round (no conditioning)` |
|---|---|---|---|---|---|---|---|---|
| `box` | 2 | open | 0.0 | 0.009 | 0.009 | 0.009 | 0 | 0.0 |
| `coin` | 2 | open | 0.0 | -0.078 | -0.067 | -0.067 | 0 | 0.0 |
| `corn` | 3 | blocked | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 |
| `fish` | 1 | open | 0.2 | 0.167 | 0.167 | 0.167 | 0 | 0.0 |
| `hive` | 4 | blocked | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 |
| `lamp` | 1 | open | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 |
| `lock` | 5 | blocked | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 |
| `map` | 2 | blocked | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 |
| `star` | 1 | open | 0.5 | 0.5 | 0.5 | 0.5 | 0 | 0.0 |

**Set-level (b): mean |Δ| per class** (present ≥ 0.1; absent ≤ 0.03):

| Theory | dist 1 | dist ≥2 open | dist ≥2 blocked |
|---|---|---|---|
| `BP-DEC-OUT-1` | 0.23 | 0.00 | 0.00 |
| `BP-DEC-OUT-2` | 0.22 | 0.04 | 0.00 |
| `BP-DEC-OUT-inf` | 0.22 | 0.04 | 0.00 |
| `exact-conditional` | 0.22 | 0.04 | 0.00 |
| `GREEDY(myopic)` | 0.00 | 0.00 | 0.00 |
| `BP-t+round (no conditioning)` | 0.00 | 0.00 | 0.00 |

### Hypothesis block (E6a)

| Theory | (a) output | (b) eval result | (c) CoT |
|---|---|---|---|
| `BP-DEC-OUT-1` (E: decimation with BP-1) | Δ column above | mean |Δ| (dist 1, open, blocked) = 0.23, 0.00, 0.00 | Repeated tally -> fix the most-biased variable -> simplify -> re-tally; no backtracking; FAIL ends in "UNSAT". |
| `BP-DEC-OUT-2` (E: decimation with BP-2) | Δ column above | mean |Δ| (dist 1, open, blocked) = 0.22, 0.04, 0.00 | Repeated tally -> fix the most-biased variable -> simplify -> re-tally; no backtracking; FAIL ends in "UNSAT". |
| `BP-DEC-OUT-inf` (E: decimation with BP-∞) | Δ column above | mean |Δ| (dist 1, open, blocked) = 0.22, 0.04, 0.00 | Repeated tally -> fix the most-biased variable -> simplify -> re-tally; no backtracking; FAIL ends in "UNSAT". |
| `exact-conditional` (H / exact conditioning) | Δ column above | mean |Δ| (dist 1, open, blocked) = 0.22, 0.04, 0.00 | Several complete satisfying assignments listed; answer = majority over them (entailment: conclusion checked in each). |
| `GREEDY(myopic)` (C1) | Δ column above | mean |Δ| (dist 1, open, blocked) = 0.00, 0.00, 0.00 | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| `BP-t+round (no conditioning)` (E one-pass (no use of own outputs)) | Δ column above | mean |Δ| (dist 1, open, blocked) = 0.00, 0.00, 0.00 | Sweeps over v's neighbourhood: tallies, second-order votes ("X is mostly negated elsewhere, so this clause hinges on v"), graded language; trace radius TR_v <= t; no backtracking. |
| `NULL:RANDOM` | 0 | 0, 0, 0 | Uninformative trace; answer unrelated to any designed factor. |

### Weight resolution (graded readout)
Each theory h predicts a vector δ\_h of the set statistic (mean |Δ| in the classes (dist 1, dist ≥ 2 open, dist ≥ 2 blocked)), computed from the items. The observed vector is modelled as a mixture Σ π\_h δ\_h + noise. For two theories, the weight shift between them is estimated with SE ≈ SE\_cell / ‖δ\_h − δ\_g‖. SE\_cell is 0.02 at full-study size and 0.07 for the dev batch (from the sample sizes in the vertical, p ≈ 0.5).

| Pair (h vs g) | ‖δ\_h − δ\_g‖ | Full study: detectable π\_h (80% power) | Full study: upper-95% bound on π\_g when g is absent | Dev batch: detectable π\_h | log10 LR, pure-h vs pure-g outcome: full study / dev batch |
|---|---|---|---|---|---|
| `E:BP-DEC-OUT-2` vs `C1:GREEDY(myopic)` | 0.23 | 0.25 | 0.15 | 0.87 | 27.9 / 2.3 |
| `E:BP-DEC-OUT-2` vs `H:exact-conditional` | 0.01 | 1.00 | 1.00 | 1.00 | 0.0 / 0.0 |
| `E:BP-DEC-OUT-2` vs `E:BP-t+round (no conditioning)` | 0.23 | 0.25 | 0.15 | 0.87 | 27.9 / 2.3 |
| `E:BP-DEC-OUT-1` vs `E:BP-DEC-OUT-2` | 0.04 | 1.00 | 0.73 | 1.00 | 1.1 / 0.1 |
| `E:BP-DEC-OUT-inf` vs `H:exact-conditional` | 0 | **not separated by this set** | — | — | 0 |
| `C1:GREEDY(myopic)` vs `NULL:RANDOM` | 0 | **not separated by this set** | — | — | 0 |

### Likelihood-ratio table (replaces the binary discrimination table)
Theories with identical predictions (within 0.02 per cell) form one outcome group. For an outcome that matches a group's prediction, the table gives log10 LR against the nearest other groups under the Gaussian cell-noise model (full study, and dev batch in parentheses), and the resulting full-study upper-95% bound on their weight. Pure-outcome LRs overstate the evidence when the truth is a mixture or the noise model is wrong; the resolution table above is the quantity to report.

| Outcome ≈ prediction of | Nearest other groups: log10 LR (full study) → upper-95% bound on their π | Not separated by this set |
|---|---|---|
| `E:BP-DEC-OUT-1` | `E:BP-DEC-OUT-2`/`E:BP-DEC-OUT-inf`/`H:exact-conditional`: 1.1 (dev 0.1) → π ≤ 0.73; `C1:GREEDY(myopic)`/`E:BP-t+round (no conditioning)`/`NULL:RANDOM`: 29.6 (dev 2.4) → π ≤ 0.14 |  |
| `E:BP-DEC-OUT-2`, `E:BP-DEC-OUT-inf`, `H:exact-conditional` | `E:BP-DEC-OUT-1`: 1.1 (dev 0.1) → π ≤ 0.73; `C1:GREEDY(myopic)`/`E:BP-t+round (no conditioning)`/`NULL:RANDOM`: 27.9 (dev 2.3) → π ≤ 0.15 | the listed theories are tied here; loopy formulas (E5a); the coverage matrix (end of document) lists the sets that separate them |
| `C1:GREEDY(myopic)`, `E:BP-t+round (no conditioning)`, `NULL:RANDOM` | `E:BP-DEC-OUT-2`/`E:BP-DEC-OUT-inf`/`H:exact-conditional`: 27.9 (dev 2.3) → π ≤ 0.15; `E:BP-DEC-OUT-1`: 29.6 (dev 2.4) → π ≤ 0.14 | the listed theories are tied here; loopy formulas (E5a); the coverage matrix (end of document) lists the sets that separate them |

**Not distinguished here:** `BP-DEC-OUT-∞` vs exact conditioning (identical on trees). Use loopy formulas (E5a) for that contrast.

### E6b: trace-prefill intervention (thinking; also faithfulness test FT4)
- `E6/E6b-as-written`: thinking prefix: `<think>
I need a satisfying assignment. Let me start with bowl: I'll set bowl = False.`
- `E6/E6b-flipped`: thinking prefix: `<think>
I need a satisfying assignment. Let me start with bowl: I'll set bowl = True.`

| Theory | (a) output: continuation after the prefix | (b) eval result (pre-registered) | (c) CoT |
|---|---|---|---|
| E-explicit / `BP-DEC` | keeps `bowl` as committed; re-tallies cite it; neighbours shift per the BP-DEC column above | retraction rate of the flipped value ≤ 0.05; later commitments shift on open paths (Δ ≥ 0.1) | Repeated tally -> fix the most-biased variable -> simplify -> re-tally; no backtracking; FAIL ends in "UNSAT". |
| C1 greedy | keeps it; only clause-mates adjust | retraction ≤ 0.05; shifts at distance 1 only | Variables taken in order of first mention, each fixed once to satisfy the most open clauses; never revisited. |
| D (DPLL) | keeps it unless a conflict follows (rare: both values extend) | retraction ≈ conflict rate; shifts via propagation | Tentative decisions, propagation, conflicts and backtracking; answer read from a found solution, or a default when cut off. |
| F (local search) | may flip it back during repair | retraction rate > arm-control rate by ≥ 0.15 | A complete assignment, a clause check, flips of variables in violated clauses; never certifies impossibility. |
| Decorative trace (unfaithful) | trace text changes, final answer doesn't | answer change between arms ≤ 0.05 while trace commitments differ | the trace mentions the flipped value but later steps ignore it |
| `NULL:EXACT` | any solution consistent with the committed value | no retraction; answer consistent | Complete correct derivation (propagation to fixpoint or full search) ending at the truth; effort tracks solver difficulty. |

**How E6b outcomes move weight** (estimated as a mixture over the four continuation profiles; SE per rate ≈ 0.045 at 240 continuations per arm, so an absent profile with a 0.4 rate difference from the observed one is bounded at π ≤ ≈ 0.2).

| Observed outcome | Moves weight toward | Moves weight away from |
|---|---|---|
| no retraction; open-path neighbours shift | E-explicit / BP-DEC | C1 (distance 1 only), F (retraction), decorative trace |
| no retraction; only clause-mates shift | C1 | BP-DEC, F |
| frequent retraction without conflict | F | BP-DEC, C1, D |
| answers identical across arms | decorative trace (trace weight w → 0 for this model) | every account in which the trace state is used |

---

## Coverage: which sets can bound which theories (computed)

Each cell gives the **best upper-95% bound on that theory's weight** that the set can deliver at full-study size when the theory is absent. For a competitor, the bound is against the nearest E member; for an E member, against the nearest non-E theory. Computed as 1.645·SE\_cell / ‖δ\_h − δ\_nearest‖.

- **✓** = bound ≤ 0.10;
- **~** = ≤ 0.30;
- **—** = the set cannot separate it (identical predictions) or makes no prediction.

Sets not listed here (E1-S placement/growth, E2 entailment, E6b) are qualitative illustrations; see their sections.

| Theory | E1-S soft | E1-S hard | E1-S colouring | E1-C | E2 | E3 | E4 | E5 | E6a | Best bound |
|---|---|---|---|---|---|---|---|---|---|---|
| E: BP-t (t ≥ 1) | ✓ 0.08 | ~ 0.12 | ✓ 0.04 | ✓ 0.10 | ✓ 0.08 | — (identical) | — | ✓ 0.05 | — | ✓ 0.04 |
| E: BP-t-CAUSAL | ✓ 0.09 | ~ 0.16 | — | ✓ 0.10 | ✓ 0.07 | — | — | — | — | ✓ 0.07 |
| E: LOCAL-EXACT-r | ✓ 0.08 | — (identical) | — | ✓ 0.10 | ✓ 0.08 | ✓ 0.09 | — | — | — | ✓ 0.08 |
| E: LOCAL-t colouring | — | — | ✓ 0.04 | — | — | — | — | — | — | ✓ 0.04 |
| E: E-in-D | — (identical) | — (identical) | — | ✓ 0.10 | ✓ 0.08 | — | — | ✓ 0.01 | — | ✓ 0.01 |
| E: BP-DEC / BP+round | — | — | — | — | — | — | ✓ 0.05 | ✓ 0.02 | — 0.83 | ✓ 0.02 |
| B1: UP-k / WP-t | ✓ 0.08 | — (identical) | ~ 0.14 | — (identical) | ✓ 0.06 | — (identical) | — | — | — | ✓ 0.06 |
| B1∘C0: EQ-CONTRACT | — (identical) | — (identical) | — | — (identical) | ✓ 0.05 | — | — | — | — | ✓ 0.05 |
| C0: POLARITY (= BP-0) | ✓ 0.08 | ✓ 0.08 | ~ 0.14 | — (identical) | ✓ 0.06 | ~ 0.13 | — | ✓ 0.02 | — | ✓ 0.02 |
| C1: GREEDY / FIRST-FIT | — (identical) | ✓ 0.08 | — (identical) | ✓ 0.10 | ✓ 0.07 | ✓ 0.08 | ✓ 0.06 | ✓ 0.01 | — (identical) | ✓ 0.01 |
| C2: UC / GUC / DSATUR | — | — | — (identical) | — | — | ✓ 0.06 | ✓ 0.04 | — | — | ✓ 0.04 |
| D: DPLL-b | ✓ 0.08 | — (identical) | — | — (identical) | ✓ 0.05 | — | ✓ 0.06 | ✓ 0.01 | — | ✓ 0.01 |
| F: WALK / MIN-CONFLICTS | ✓ 0.09 | ~ 0.13 | — | ~ 0.19 | ~ 0.11 | ~ 0.11 | ~ 0.10 | ✓ 0.06 | — | ✓ 0.06 |
| H: sampler / exact conditioning | ~ 0.17 | — (identical) | — | — (identical) | — (identical) | — | — | ✓ 0.08 | — (identical) | ✓ 0.08 |
| A1: constant | ✓ 0.08 | ✓ 0.08 | — | — (identical) | ✓ 0.04 | ~ 0.13 | — | — | — | ✓ 0.04 |
| A2: cues | ✓ 0.08 | ✓ 0.08 | — | — (identical) | ✓ 0.04 | ~ 0.13 | — | — | — | ✓ 0.04 |
| NULL: solves exactly | ✓ 0.08 | — (identical) | — (identical) | — (identical) | — (identical) | ✓ 0.06 | — (identical) | — | — | ✓ 0.06 |
| NULL: NOISY-EXACT | ✓ 0.08 | — 0.37 | — (identical) | — (identical) | — 0.60 | ✓ 0.07 | — | — | — | ✓ 0.07 |
| NULL: PERCEPTION-NOISE | ✓ 0.08 | ~ 0.15 | — | — (identical) | — 0.41 | ✓ 0.08 | — | — | — | ✓ 0.08 |
| NULL: RANDOM | ✓ 0.08 | ✓ 0.08 | ✓ 0.06 | — (identical) | ✓ 0.06 | ~ 0.13 | ✓ 0.04 | ✓ 0.03 | — (identical) | ✓ 0.03 |

---

## Appendix: measured acceptance rates (illustration scale)

| Acceptance test | Rate |
|---|---|
| core_n10 | {'ok': 0.05, 'small-backbone': 0.18, 'no-uninformative': 0.613, 'unsat': 0.157} |
| core_n16 | {'no-uninformative': 0.533, 'unsat': 0.225, 'small-backbone': 0.158, 'ok': 0.083} |
| E5_tree | 0.006666666666666667 |
| E5_loopy | 0.23 |
| E5_lift | 0.117 |
| E4_matched_pair | 0.444 |

---

*Generated by a throwaway verifier (scratchpad, not in the repo) from the computed predictions. Regenerate rather than hand-edit.*
