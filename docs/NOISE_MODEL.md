# The noise model for the mixture fits

*Decision record, 2026-11-19. STATUS "Open decisions" asked which noise model the mixture fits should use, because the pre-registered one (SCOPE §6 rule 3) fits the 2026-11-18 data badly. This page gives the diagnosis, the candidates, their evaluation on the 24 gated fits with the committed analysis's settings, and a recommendation. The code is in `src/reasoning_heuristics/identify/noise.py` (options, all defaulting to the pre-registered model) and `analysis/noise_model_eval.py`; the numbers are in [analysis/out/noise_model/](../analysis/out/noise_model/). The committed results page and JSON are not regenerated here.*

**Recommendation: KEQ-r.** Keep near-miss slips with an estimated rate, but estimate the kernel's shape (free over distances 1–6), lift the cap on ε to 1 and cut the kernel's reach on small answer spaces, and estimate q's distribution over answer sizes and its special-token mass. On the 24 gated fits it passes every predictive check on 11 (M0: 5), puts ε at its cap on 5 (M0: 14), recovers the planted mixture on all four units at pilot sizes, and leaves the weights the findings rest on where they were. The costs: pure noise puts up to 0.05 on members on knapsack and A/H E5 SAT (M0: under 0.01), the nulls' intervals under-cover at the boundary there, and it was chosen after seeing the data, so its fits on these runs are exploratory. The repeat samples add a limit no noise model removes: in the direct condition the unexplained answers are reproducible procedures (templates, under-filled packings), which need new zoo members (§4.7, §5.5).

## 1. The question

Each fit is the mixture P(y | x) = Σ_h π_h P(y | h, x) + π₀ q(y | x). Under the pre-registered noise model (**M0**):

- a deterministic or set-valued member gives its answer with probability 1 − ε and otherwise slips: D ~ truncated geometric(ρ) on 1–6 positions change (variables flipped, items toggled, vertices recoloured up to renaming);
- ε is shared by every member and capped at 0.5; ρ is on a grid up to 0.9;
- q, "none of the above", is uniform: 2⁻ⁿ over assignments and item sets, n colours drawn uniformly per vertex for a colouring, and half its mass on the special token (UNSAT, IMPOSSIBLE) where the channel has one.

Of the 24 gated fits (C E2 colouring, C E2 knapsack and A/H E5 SAT at 20 per cell, C E5 SAT with a given state at 40; six pilot runs each), 14 put ε at its cap. Five pass every predictive check of the prelim script (the shares of exact, beyond-reach and special-token answers, and the distance profile), and four of those have ε below its cap, which is the results page's rule for "reproduces the data" (the fifth, A/H E5 SAT for Qwen3-14B thinking, has ε at the cap).

## 2. Diagnosis

### 2.1 Distance profiles

Each cell is the observed share of answers at that distance from the nearest member, then the M0 fit's (the mean over 100 fake data sets drawn from it). An arrow marks a gap over 0.05. "Special" is the share of special-token answers. Source: the committed `recovery_at_estimate[...].distance_check`.

<!-- BEGIN nm:profiles -->
| Unit | Run | ε | ρ | d = 0 | d = 1 | d = 2 | d = 3 | d = 4-6 | d = >6 | special | M0 checks failed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C E2 colouring | gpt-oss-120b low effort | 0.41 | 0.90 | 0.42 / 0.44 | 0.04 / 0.06 | 0.10 / 0.10 | 0.13 / 0.09 | 0.29 / 0.26 | 0.01 / 0.05 | 0.00 / 0.00 | beyond_reach |
| C E2 colouring | gpt-oss-20b low effort | 0.50 | 0.90 | 0.28 / 0.39 ↓ | 0.09 / 0.07 | 0.10 / 0.10 | 0.09 / 0.09 | 0.35 / 0.23 ↑ | 0.08 / 0.11 | 0.00 / 0.00 | exact, distance |
| C E2 colouring | Qwen3-14B direct | 0.50 | 0.90 | 0.00 / 0.09 ↓ | 0.00 / 0.02 | 0.00 / 0.02 | 0.02 / 0.02 | 0.20 / 0.04 ↑ | 0.77 / 0.80 | 0.00 / 0.00 | exact, distance |
| C E2 colouring | Qwen3-14B thinking | 0.13 | 0.90 | 0.70 / 0.65 ↑ | 0.02 / 0.02 | 0.07 / 0.06 | 0.06 / 0.06 | 0.15 / 0.19 | 0.00 / 0.03 | 0.00 / 0.00 | exact, beyond_reach |
| C E2 colouring | Qwen3-32B direct | 0.50 | 0.90 | 0.00 / 0.33 ↓ | 0.00 / 0.08 ↓ | 0.03 / 0.07 | 0.08 / 0.06 | 0.56 / 0.13 ↑ | 0.33 / 0.33 | 0.00 / 0.00 | exact, distance |
| C E2 colouring | Qwen3-32B thinking | 0.15 | 0.72 | 0.71 / 0.66 | 0.04 / 0.04 | 0.05 / 0.07 | 0.09 / 0.06 | 0.11 / 0.15 | 0.00 / 0.03 | 0.00 / 0.00 | exact, beyond_reach, distance |
| C E2 knapsack | gpt-oss-120b low effort | 0.13 | 0.70 | 0.87 / 0.87 | 0.02 / 0.05 | 0.07 / 0.04 | 0.03 / 0.02 | 0.00 / 0.02 | 0.00 / 0.00 | 0.00 / 0.00 | distance |
| C E2 knapsack | gpt-oss-20b low effort | 0.29 | 0.60 | 0.72 / 0.72 | 0.10 / 0.13 | 0.15 / 0.08 ↑ | 0.03 / 0.05 | 0.00 / 0.02 | 0.00 / 0.00 | 0.00 / 0.00 | distance |
| C E2 knapsack | Qwen3-14B direct | 0.50 | 0.48 | 0.16 / 0.47 ↓ | 0.39 / 0.25 ↑ | 0.24 / 0.14 ↑ | 0.17 / 0.08 ↑ | 0.04 / 0.06 | 0.00 / 0.00 | 0.00 / 0.00 | exact, distance |
| C E2 knapsack | Qwen3-14B thinking | 0.01 | 0.90 | 0.99 / 0.99 | 0.00 / 0.00 | 0.00 / 0.00 | 0.01 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | pass |
| C E2 knapsack | Qwen3-32B direct | 0.50 | 0.52 | 0.08 / 0.46 ↓ | 0.33 / 0.24 ↑ | 0.40 / 0.14 ↑ | 0.15 / 0.09 ↑ | 0.05 / 0.07 | 0.00 / 0.00 | 0.00 / 0.00 | exact, distance |
| C E2 knapsack | Qwen3-32B thinking | 0.01 | 0.02 | 0.98 / 0.98 | 0.01 / 0.01 | 0.01 / 0.00 | 0.00 / 0.00 | 0.00 / 0.01 | 0.00 / 0.00 | 0.00 / 0.00 | pass |
| A/H E5 SAT | gpt-oss-120b low effort | 0.50 | 0.90 | 0.07 / 0.20 ↓ | 0.06 / 0.05 | 0.12 / 0.06 ↑ | 0.18 / 0.08 ↑ | 0.35 / 0.25 ↑ | 0.05 / 0.05 | 0.16 / 0.31 ↓ | exact, beyond_reach, special, distance |
| A/H E5 SAT | gpt-oss-20b low effort | 0.50 | 0.70 | 0.00 / 0.07 ↓ | 0.06 / 0.03 | 0.07 / 0.04 | 0.18 / 0.08 ↑ | 0.37 / 0.29 ↑ | 0.05 / 0.07 | 0.27 / 0.43 ↓ | exact, beyond_reach, special, distance |
| A/H E5 SAT | Qwen3-14B direct | 0.50 | 0.90 | 0.00 / 0.02 | 0.02 / 0.01 | 0.08 / 0.03 | 0.12 / 0.07 ↑ | 0.58 / 0.30 ↑ | 0.20 / 0.08 ↑ | 0.00 / 0.49 ↓ | beyond_reach, special, distance |
| A/H E5 SAT | Qwen3-14B thinking | 0.50 | 0.90 | 0.27 / 0.31 | 0.08 / 0.07 | 0.08 / 0.08 | 0.08 / 0.09 | 0.28 / 0.21 ↑ | 0.01 / 0.03 | 0.18 / 0.20 | pass |
| A/H E5 SAT | Qwen3-32B direct | 0.50 | 0.90 | 0.00 / 0.02 | 0.03 / 0.01 | 0.08 / 0.03 ↑ | 0.13 / 0.07 ↑ | 0.48 / 0.30 ↑ | 0.24 / 0.09 ↑ | 0.03 / 0.47 ↓ | beyond_reach, special, distance |
| A/H E5 SAT | Qwen3-32B thinking | 0.50 | 0.90 | 0.26 / 0.34 ↓ | 0.09 / 0.08 | 0.09 / 0.09 | 0.12 / 0.09 | 0.32 / 0.21 ↑ | 0.02 / 0.03 | 0.09 / 0.16 ↓ | beyond_reach, special, distance |
| C E5 SAT, state given | gpt-oss-120b low effort | 0.45 | 0.72 | 0.42 / 0.39 | 0.12 / 0.11 | 0.08 / 0.07 | 0.03 / 0.05 | 0.09 / 0.07 | 0.00 / 0.00 | 0.25 / 0.30 ↓ | special |
| C E5 SAT, state given | gpt-oss-20b low effort | 0.50 | 0.84 | 0.17 / 0.26 ↓ | 0.08 / 0.07 | 0.09 / 0.06 | 0.08 / 0.05 | 0.12 / 0.08 | 0.03 / 0.03 | 0.42 / 0.44 | exact |
| C E5 SAT, state given | Qwen3-14B direct | 0.50 | 0.90 | 0.01 / 0.45 ↓ | 0.03 / 0.09 ↓ | 0.13 / 0.09 | 0.20 / 0.07 ↑ | 0.59 / 0.17 ↑ | 0.04 / 0.04 | 0.00 / 0.09 ↓ | exact, special, distance |
| C E5 SAT, state given | Qwen3-14B thinking | 0.16 | 0.58 | 0.55 / 0.54 | 0.05 / 0.05 | 0.03 / 0.03 | 0.01 / 0.01 | 0.02 / 0.01 | 0.00 / 0.00 | 0.35 / 0.35 | pass |
| C E5 SAT, state given | Qwen3-32B direct | 0.50 | 0.90 | 0.03 / 0.40 ↓ | 0.08 / 0.09 | 0.13 / 0.08 ↑ | 0.23 / 0.08 ↑ | 0.38 / 0.16 ↑ | 0.06 / 0.05 | 0.07 / 0.14 ↓ | exact, special, distance |
| C E5 SAT, state given | Qwen3-32B thinking | 0.30 | 0.68 | 0.50 / 0.49 | 0.08 / 0.07 | 0.05 / 0.05 | 0.03 / 0.03 | 0.04 / 0.03 | 0.00 / 0.00 | 0.31 / 0.32 | pass |
<!-- END nm:profiles -->

### 2.2 What the wrong answers look like

From `diagnosis.json` (`describe_answers`). "Wrong, no member's answer" counts wrong answers equal to no deterministic member's answer and outside every set-valued member's solutions (all units, not only the full-answer ones). The signature column gives, for knapsack, how the near wrong answers (1–3 items from the nearest member) differ from it: one item in and one out (a swap), or items dropped only; for SAT, the all-false and all-true answers among the wrong ones; for colouring, how many colours the wrong answers use (counts of 5 or more).

<!-- BEGIN nm:answers -->
| Unit | Run | Answers | Correct | Wrong | Special token | Wrong, no member's answer | of them ≥ 4 away | Signature |
|---|---|---|---|---|---|---|---|---|
| C E2 colouring | gpt-oss-120b low effort | 300 | 63 | 237 | 0 | 173 (73%) | 90 | colours used: 4: 180, 5: 48, 6: 5 |
| C E2 colouring | gpt-oss-20b low effort | 299 | 43 | 256 | 0 | 215 (84%) | 130 | colours used: 4: 173, 5: 70, 6: 12 |
| C E2 colouring | Qwen3-14B direct | 300 | 0 | 300 | 0 | 300 (100%) | 291 | colours used: 10: 5, 13: 7, 14: 6, 15: 8, 16: 42, 3: 5, 4: 81, 5: 34, 6: 63, 7: 36, 8: 6 |
| C E2 colouring | Qwen3-14B thinking | 299 | 98 | 201 | 0 | 90 (45%) | 46 | colours used: 4: 185, 5: 14 |
| C E2 colouring | Qwen3-32B direct | 300 | 0 | 300 | 0 | 300 (100%) | 267 | colours used: 3: 202, 4: 89 |
| C E2 colouring | Qwen3-32B thinking | 290 | 106 | 184 | 0 | 84 (46%) | 33 | colours used: 4: 170, 5: 12 |
| C E2 knapsack | gpt-oss-120b low effort | 300 | 212 | 88 | 0 | 38 (43%) | 0 | swaps (1 in, 1 out) 21/38; drops only 2/38 |
| C E2 knapsack | gpt-oss-20b low effort | 300 | 158 | 142 | 0 | 85 (60%) | 1 | swaps (1 in, 1 out) 44/84; drops only 16/84 |
| C E2 knapsack | Qwen3-14B direct | 300 | 11 | 289 | 0 | 253 (88%) | 13 | swaps (1 in, 1 out) 48/240; drops only 66/240 |
| C E2 knapsack | Qwen3-14B thinking | 278 | 270 | 8 | 0 | 4 (50%) | 0 | swaps (1 in, 1 out) 0/4; drops only 0/4 |
| C E2 knapsack | Qwen3-32B direct | 300 | 1 | 299 | 0 | 276 (92%) | 14 | swaps (1 in, 1 out) 43/262; drops only 168/262 |
| C E2 knapsack | Qwen3-32B thinking | 296 | 286 | 10 | 0 | 7 (70%) | 0 | swaps (1 in, 1 out) 2/7; drops only 2/7 |
| A/H E5 SAT | gpt-oss-120b low effort | 99 | 7 | 92 | 16 | 92 (100%) | 40 | all-false 4, all-true 1 |
| A/H E5 SAT | gpt-oss-20b low effort | 97 | 0 | 97 | 26 | 97 (100%) | 41 | all-false 13, all-true 2 |
| A/H E5 SAT | Qwen3-14B direct | 100 | 0 | 100 | 0 | 100 (100%) | 78 | all-false 18, all-true 6 |
| A/H E5 SAT | Qwen3-14B thinking | 95 | 22 | 73 | 17 | 69 (95%) | 28 | all-false 0, all-true 0 |
| A/H E5 SAT | Qwen3-32B direct | 95 | 0 | 95 | 3 | 95 (100%) | 69 | all-false 0, all-true 3 |
| A/H E5 SAT | Qwen3-32B thinking | 95 | 20 | 75 | 9 | 70 (93%) | 32 | all-false 1, all-true 0 |
| C E5 SAT, state given | gpt-oss-120b low effort | 120 | 79 | 41 | 30 | 39 (95%) | 11 | all-false 0, all-true 0 |
| C E5 SAT, state given | gpt-oss-20b low effort | 120 | 52 | 68 | 51 | 48 (71%) | 17 | all-false 0, all-true 0 |
| C E5 SAT, state given | Qwen3-14B direct | 120 | 1 | 119 | 0 | 119 (100%) | 76 | all-false 0, all-true 0 |
| C E5 SAT, state given | Qwen3-14B thinking | 118 | 104 | 14 | 41 | 12 (86%) | 2 | all-false 0, all-true 0 |
| C E5 SAT, state given | Qwen3-32B direct | 120 | 5 | 115 | 9 | 107 (93%) | 53 | all-false 0, all-true 0 |
| C E5 SAT, state given | Qwen3-32B thinking | 117 | 93 | 24 | 36 | 23 (96%) | 5 | all-false 0, all-true 0 |
<!-- END nm:answers -->

### 2.3 Which mis-specification drives each failure

Four things go wrong, and they are separable in the data:

1. **The ε cap (14 fits).** At ε = 0.5 every slipping member still gives its exact answer with probability 0.5. In the direct condition almost no answer equals a member's (0.00–0.16 of answers), yet the capped fits predict 0.09–0.53. That is the "exact" failure in the six direct-condition fits outside A/H E5 (both colouring, both knapsack, both C E5; in A/H E5 π₀ ≈ 0.95 hides it), and in gpt-oss's A/H E5 fits and gpt-oss-20b's colouring and C E5 fits. Lifting the cap alone (KE against K in the ladder below) gains 41–139 log-likelihood units on the direct fits outside A/H E5 (18–20 there), and nothing on the near-ceiling ones.
2. **q's uniformity (colouring and SAT).**
   - *Colouring:* q colours each of the 16 vertices with one of 16 colours, so a 3- or 4-colour answer has q ≈ 10⁻¹⁶, against ~10⁻⁸ for a slip six vertices from a member. Every answer within six vertices of some member is therefore forced into a slip, ρ goes to the top of its grid (flat over 1–6), and the free kernel piles its mass at distance 6 (g₆ = 0.66–0.93 on the direct fits): the kernel's edge is standing in for q. Fitting q's distribution over the number of colours (KEQ against KE) gains 1,723 and 2,138 units on the two direct fits and 47 and 255 on gpt-oss. Qwen3-14B direct also answers the all-distinct colouring (16 colours) 42 times in 300.
   - *SAT:* q puts half its mass on UNSAT. Where π₀ is large (Qwen3 direct, A/H E5: π₀ ≈ 0.95) the fit predicts 0.47–0.49 UNSAT answers against 0.00–0.03 observed: the "special" and "beyond reach" failures of those fits, and of gpt-oss's A/H E5 fits (0.31 and 0.43 predicted, 0.16 and 0.27 observed). The unexplained assignments are not uniform either: Qwen3-14B direct gives the all-false assignment 18 times and an exactly-half-true one 52 times in 100.
   - *Knapsack:* q is adequate (≤ 7 units).
   - *A valid/invalid split of q would not help.* The far answers are mostly invalid and far from valid: Qwen3-32B's direct colourings are proper 1 time in 300, with six or more conflicting edges (of 36) in 164. And on SAT and k-colouring the valid answers are exactly EXACT's solution set, so a q component uniform over them would be EXACT itself (not identified).
3. **The kernel's shape (knapsack, direct bit vectors).**
   - gpt-oss's wrong packings two items from the nearest member are one-for-one swaps: 44 of the 84 near wrong answers of gpt-oss-20b, and 21 of 38 for gpt-oss-120b, against at most 1 two-item add or drop. The geometric kernel cannot put more mass at distance 2 than at 1; a free kernel gains 21 units on each.
   - Direct-condition answers slip in one direction: Qwen3-32B's wrong packings drop items from a member's packing (168 of 262 near wrong answers are drops only), and Qwen3-14B's C E5 assignments set 60–80% of variables true. A kernel over (adds, drops) instead of distance (SEQ against KEQ) gains a further 79 units on the Qwen3-32B direct knapsack fit and 259 on the Qwen3-14B direct C E5 fit (44 on Qwen3-32B's).
4. **Not the noise model: thinking-condition colouring.** The two Qwen3 thinking colouring fits fail "exact" (0.70 observed, 0.65 predicted) and "beyond reach" (0.00 observed, 0.03–0.04 predicted) with ε at 0.13–0.15 and π₀ = 0. The far answers come from RO-FF (C3), a stored distribution over random-order first-fit colourings with weight 0.30–0.35, which spreads over colourings no zoo member is near. No noise model changes these fits by more than 6 units. That is a zoo question (RO-FF's spread against the list-order members'), not a noise one.

Per-member ε matters little anywhere (KEQ-h against KEQ: 0–25 units, most on gpt-oss), and the four near-ceiling fits that pass under M0 gain at most 9 units from any candidate.

### 2.4 Likelihood ladder

Point fits (no bootstrap) of every candidate, as log-likelihood gained over M0 and free parameters added. The candidates are nested except SEQ, which replaces KEQ's distance kernel.

<!-- BEGIN nm:ladder -->
| Unit | Run | K: Δlog L (Δparams) | KE: Δlog L (Δparams) | KEQ: Δlog L (Δparams) | KEQ-h: Δlog L (Δparams) | SEQ: Δlog L (Δparams) | KEQ-r: Δlog L (Δparams) | SEQ-r: Δlog L (Δparams) |
|---|---|---|---|---|---|---|---|---|
| C E2 colouring | gpt-oss-120b low effort | +4 (+4) | +4 (+4) | +51 (+19) | +73 (+25) | – | +51 (+19) | – |
| C E2 colouring | gpt-oss-20b low effort | +12 (+4) | +21 (+4) | +276 (+19) | +289 (+25) | – | +276 (+19) | – |
| C E2 colouring | Qwen3-14B direct | +73 (+4) | +114 (+4) | +1837 (+19) | +1837 (+25) | – | +1837 (+19) | – |
| C E2 colouring | Qwen3-14B thinking | +2 (+4) | +2 (+4) | +2 (+19) | +6 (+25) | – | +2 (+19) | – |
| C E2 colouring | Qwen3-32B direct | +154 (+4) | +293 (+4) | +2431 (+19) | +2431 (+25) | – | +2431 (+19) | – |
| C E2 colouring | Qwen3-32B thinking | +2 (+4) | +2 (+4) | +2 (+19) | +6 (+25) | – | +2 (+19) | – |
| C E2 knapsack | gpt-oss-120b low effort | +21 (+4) | +21 (+4) | +21 (+14) | +32 (+20) | +37 (+35) | +21 (+14) | +37 (+35) |
| C E2 knapsack | gpt-oss-20b low effort | +21 (+4) | +21 (+4) | +23 (+14) | +48 (+20) | +52 (+35) | +23 (+14) | +51 (+35) |
| C E2 knapsack | Qwen3-14B direct | +14 (+4) | +96 (+4) | +96 (+14) | +106 (+20) | +105 (+35) | +88 (+14) | +96 (+35) |
| C E2 knapsack | Qwen3-14B thinking | +3 (+4) | +3 (+4) | +4 (+14) | +9 (+20) | +6 (+35) | +4 (+14) | +4 (+35) |
| C E2 knapsack | Qwen3-32B direct | +29 (+4) | +153 (+4) | +160 (+14) | +163 (+20) | +239 (+35) | +158 (+14) | +230 (+35) |
| C E2 knapsack | Qwen3-32B thinking | +3 (+4) | +3 (+4) | +3 (+14) | +6 (+20) | +6 (+35) | +2 (+14) | +3 (+35) |
| A/H E5 SAT | gpt-oss-120b low effort | +1 (+4) | +18 (+4) | +61 (+33) | +64 (+37) | +72 (+54) | +59 (+33) | +66 (+54) |
| A/H E5 SAT | gpt-oss-20b low effort | +3 (+4) | +21 (+4) | +163 (+33) | +163 (+37) | +172 (+54) | +160 (+33) | +171 (+54) |
| A/H E5 SAT | Qwen3-14B direct | +3 (+4) | +21 (+4) | +336 (+33) | +336 (+37) | +340 (+54) | +336 (+33) | +339 (+54) |
| A/H E5 SAT | Qwen3-14B thinking | +3 (+4) | +5 (+4) | +23 (+33) | +26 (+37) | +28 (+54) | +17 (+33) | +20 (+54) |
| A/H E5 SAT | Qwen3-32B direct | +2 (+4) | +22 (+4) | +115 (+33) | +115 (+37) | +116 (+54) | +115 (+33) | +115 (+54) |
| A/H E5 SAT | Qwen3-32B thinking | +2 (+4) | +5 (+4) | +22 (+33) | +27 (+37) | +27 (+54) | +19 (+33) | +21 (+54) |
| C E5 SAT, state given | gpt-oss-120b low effort | +0 (+4) | +0 (+4) | +7 (+24) | +14 (+30) | +26 (+45) | +7 (+24) | +26 (+45) |
| C E5 SAT, state given | gpt-oss-20b low effort | +3 (+4) | +8 (+4) | +19 (+24) | +23 (+30) | +30 (+45) | +19 (+24) | +30 (+45) |
| C E5 SAT, state given | Qwen3-14B direct | +24 (+4) | +96 (+4) | +142 (+24) | +144 (+30) | +401 (+45) | +142 (+24) | +401 (+45) |
| C E5 SAT, state given | Qwen3-14B thinking | +0 (+4) | +0 (+4) | +3 (+24) | +4 (+30) | +9 (+45) | +3 (+24) | +9 (+45) |
| C E5 SAT, state given | Qwen3-32B direct | +11 (+4) | +65 (+4) | +77 (+24) | +77 (+30) | +121 (+45) | +77 (+24) | +121 (+45) |
| C E5 SAT, state given | Qwen3-32B thinking | +0 (+4) | +0 (+4) | +0 (+24) | +9 (+30) | +3 (+45) | +0 (+24) | +3 (+45) |
<!-- END nm:ladder -->

## 3. Candidates

All are options of `identify.noise.NoiseModel` (`kernel`, `eps`, `eps_max`, `q`), estimated by one EM (`mixture._GeneralStepper`; closed-form M-steps for every new parameter). The default, `NoiseModel()`, is M0, and its code path is unchanged: `fits --noise M0` reproduces the committed weights, intervals, recovery and checks exactly (`analysis/out/noise_model/m0_check.json`).

| Name | Kernel | ε | q | Extra parameters per unit |
|---|---|---|---|---|
| **M0** | geometric(ρ) over distances 1–6 | shared, ≤ 0.5 | uniform | – |
| **K** | free over distances 1–6 | shared, ≤ 0.5 | uniform | +4 |
| **KE** | free over distances 1–6 | shared, ≤ 1 | uniform | +4 |
| **KEQ** | free over distances 1–6 | shared, ≤ 1 | strata | +4, + one per size stratum − 1 per n, + τ |
| **KEQ-h** | free over distances 1–6 | per member, ≤ 1 | strata | KEQ + (members − 1) |
| **SEQ** | free over (adds, drops), adds + drops ≤ 6 (bit spaces only) | shared, ≤ 1 | strata | KEQ + 21 |
| **KEQ-r** | as KEQ, reach cut per unit (below) | shared, ≤ 1 | strata | as KEQ, fewer kernel cells where the reach is cut |
| **SEQ-r** | as SEQ, reach cut per unit | shared, ≤ 1 | strata | as SEQ, fewer cells where the reach is cut |

- **Free kernel.** g₁…g₆ are free and shared by the unit's members; the M-step sets g_d to the expected share of slips at distance d. The geometric kernel is the special case g_d ∝ ρ^(d−1).
- **The (adds, drops) kernel** (SEQ, "swap-aware"). On a bit vector a slip draws a cell (a, r) with a + r ≤ 6, then sets a of the answer's clear positions and clears r of its set ones, uniformly. A one-for-one swap is the cell (1, 1), an under-filled packing (0, r), an over-true assignment (a, 0). It is an exact pmf (`spaces.BitSpace.slip_ad`), 26 free cells.
- **Lifting the cap.** The cap exists so that slips cannot absorb everything (A/H §5.3 point 3): on a finite channel a member that always slips is RANDOM. On witness channels a slip moves at most six positions, so a member at ε = 1 is a cloud around its answer, not RANDOM, except where six positions cover most of the space (knapsack: 848 of the 1,024 packings are within six items of any given one). Stage 0's `null_q` scenario is the test of whether that matters.
- **The strata q.** q is uniform within strata, the number of colours of a colouring or the number of set positions of a bit vector (items packed, variables true), with the strata's probabilities estimated (one categorical per number of positions n), and the special tokens' total mass τ estimated. The uniform q is the special case P(s) ∝ |stratum s|. Two identifiability rules:
  - Where a member predicts a special token on every item (ALWAYS-UNSAT in C E5), τ and that member's weight are one ridge (only π_member + τ π₀ is identified), so τ = 0 there and the member carries the constant token. In the gated units this applies to C E5 SAT only.
  - A one-answer stratum (one colour for every vertex, all 16 distinct, the empty set, all true) lets q put a point mass on a constant answer. None of the gated units has a member that answers a constant structured answer, so this is identified there; on units that do (e.g. LOCAL-2-ID in C E1 colouring, nearly one colour), the stratum would have to be merged with its neighbour.
- **Per-member ε** (KEQ-h): one rate per tie group. A member with little weight has an unidentified rate; the summary ε is the weight-averaged rate of the slipping members.

- **Reach** (`-r` variants). With the cap lifted, the slip kernel's reach decides whether a member can pass for q. Pure q data sit on the edge of the simplex (π₀ = 1), where any extra flexibility picks up weight by chance; a member whose slips can land on most of the space picks up more. `reach="auto"` cuts the free kernel, per unit, at the largest distance whose ball around an answer holds at most a fifth of the answer space (`spaces.Space.ball_fraction`): 3 for knapsack (176 of 1,024 packings), 4 for A/H E5 SAT (its 12-variable items), 6 for colouring and C E5 SAT, where nothing changes. Inside the ball an always-slipping member is then at least five times denser than q. KEQ-r and SEQ-r are KEQ and SEQ with this reach.

## 4. Evaluation

**Settings.** The prelim script's: 2000 cluster-bootstrap draws per fit (percentile and BCa intervals), and 100 fake data sets drawn from each fit (its weights, those below 0.01 set to 0, and all its noise parameters), which give the predictive checks and, refitted with 200 draws each, recovery at the estimate. The Stage 0 harness plants the 60/30/10 mixture (and `null_q`, `null_always`) on the committed pc20 and pc40 items with the pre-registered noise (ε = 0.1, ρ = 0.3, uniform q), 100 replicates of 100 draws, and fits it with each candidate; every candidate nests that generator. M0's numbers are the committed ones (`analysis/out/prelim_2026_11_18.json`, `data/recovery/pc{20,40}.json`). Not run: the permutation baselines (they do not bear on the noise model); for the supplementary candidates KE and SEQ-r, the refits behind recovery at the estimate and Stage 0 (their predictive checks use the same 100 fake data sets per fit); and K, KEQ-h and SEQ beyond the point fits of the ladder (§2.4), for lack of box time. KEQ-r and SEQ-r are run where their reach is below 6 and equal KEQ and SEQ elsewhere.

**Criteria.** A fit *passes the checks* when its four predictive checks pass, as in the prelim script; the results page also asks for ε below its cap. *Recovery at the estimate* passes on the RECOVERY.md gates (|bias| ≤ 0.05 on every quantity, coverage ≥ 0.9 on every planted weight, median width ≤ 0.2). *Stage 0* counts the gated scenarios (mix, `null_q`, `null_always`) that pass on the four units. *Noise* is the share of answers the fit attributes to a slip or to q (posterior responsibilities), so a model that passes by calling everything noise shows here.

### 4.1 Summary

<!-- BEGIN nm:summary -->
| Model | Fits | Pass every predictive check | … with ε below its cap | ε at its cap | Recovery at the estimate passes (percentile / BCa) | Stage 0 scenarios passed | π₀ (q), median (range) | Answers put on noise (slips + q), median (range) |
|---|---|---|---|---|---|---|---|---|
| M0 | 24 | 5 | 4 | 14 | 6 / 9 | 11 / 12 | 0.09 (0.00–0.97) | 0.63 (0.01–1.00) |
| KE | 24 | 17 | 14 | 5 | not run | – | 0.04 (0.00–0.80) | 0.66 (0.01–1.00) |
| KEQ | 24 | 14 | 12 | 5 | 3 / 8 | 9 / 12 | 0.09 (0.00–0.99) | 0.63 (0.01–1.00) |
| KEQ-r | 24 | 11 | 10 | 5 | 5 / 11 | 9 / 12 | 0.09 (0.00–0.99) | 0.64 (0.01–1.00) |
| SEQ-r | 18 | 15 | 12 | 4 | not run | – | 0.06 (0.01–0.98) | 0.74 (0.01–1.00) |
<!-- END nm:summary -->

### 4.2 Predictive checks, fit by fit

Each cell lists the checks that fail ("pass" if none); "(ε cap)" marks ε at the candidate's cap.

<!-- BEGIN nm:ppc -->
| Unit | Run | M0 | KE | KEQ | KEQ-r | SEQ-r |
|---|---|---|---|---|---|---|
| C E2 colouring | gpt-oss-120b low effort | beyond_reach | beyond_reach | beyond_reach | beyond_reach | – |
| C E2 colouring | gpt-oss-20b low effort | exact, distance (ε cap) | pass | pass | pass | – |
| C E2 colouring | Qwen3-14B direct | exact, distance (ε cap) | pass (ε cap) | beyond_reach (ε cap) | beyond_reach (ε cap) | – |
| C E2 colouring | Qwen3-14B thinking | exact, beyond_reach | exact, beyond_reach | exact, beyond_reach, distance | exact, beyond_reach, distance | – |
| C E2 colouring | Qwen3-32B direct | exact, distance (ε cap) | pass (ε cap) | beyond_reach, distance (ε cap) | beyond_reach, distance (ε cap) | – |
| C E2 colouring | Qwen3-32B thinking | exact, beyond_reach, distance | exact, beyond_reach, distance | beyond_reach, distance | beyond_reach, distance | – |
| C E2 knapsack | gpt-oss-120b low effort | distance | pass | pass | pass | pass |
| C E2 knapsack | gpt-oss-20b low effort | distance | pass | pass | beyond_reach | pass |
| C E2 knapsack | Qwen3-14B direct | exact, distance (ε cap) | pass | pass | pass | pass |
| C E2 knapsack | Qwen3-14B thinking | pass | pass | pass | pass | pass |
| C E2 knapsack | Qwen3-32B direct | exact, distance (ε cap) | pass | pass | pass | pass |
| C E2 knapsack | Qwen3-32B thinking | pass | pass | pass | pass | pass |
| A/H E5 SAT | gpt-oss-120b low effort | exact, beyond_reach, special, distance (ε cap) | pass | pass | pass | pass |
| A/H E5 SAT | gpt-oss-20b low effort | exact, beyond_reach, special, distance (ε cap) | pass (ε cap) | pass (ε cap) | beyond_reach (ε cap) | pass (ε cap) |
| A/H E5 SAT | Qwen3-14B direct | beyond_reach, special, distance (ε cap) | beyond_reach, special, distance (ε cap) | pass (ε cap) | pass (ε cap) | pass (ε cap) |
| A/H E5 SAT | Qwen3-14B thinking | pass (ε cap) | pass | pass | pass | pass |
| A/H E5 SAT | Qwen3-32B direct | beyond_reach, special, distance (ε cap) | special, distance (ε cap) | beyond_reach, distance (ε cap) | distance (ε cap) | pass (ε cap) |
| A/H E5 SAT | Qwen3-32B thinking | beyond_reach, special, distance (ε cap) | pass | pass | beyond_reach | beyond_reach |
| C E5 SAT, state given | gpt-oss-120b low effort | special | special | beyond_reach, special | beyond_reach, special | beyond_reach, special, distance |
| C E5 SAT, state given | gpt-oss-20b low effort | exact (ε cap) | pass | pass | pass | pass |
| C E5 SAT, state given | Qwen3-14B direct | exact, special, distance (ε cap) | exact, special | beyond_reach, distance | beyond_reach, distance | exact, special (ε cap) |
| C E5 SAT, state given | Qwen3-14B thinking | pass | pass | pass | pass | pass |
| C E5 SAT, state given | Qwen3-32B direct | exact, special, distance (ε cap) | pass | special | special | pass |
| C E5 SAT, state given | Qwen3-32B thinking | pass | pass | special | special | pass |
<!-- END nm:ppc -->

### 4.3 Stage 0: planted mixtures at pilot sizes

✓ pass, ✗ fail, n/t not testable; per unit: the 60/30/10 mixture, `null_q`, `null_always`. † fails the gate by definition: the generator's q answers UNSAT half the time, and under the strata q a constant UNSAT is ALWAYS-UNSAT's (τ = 0 on this unit), so the planted "π₀ = 1" is ½ ALWAYS-UNSAT and ½ q in the candidate's terms; the fit returns 0.48 and 0.49.

<!-- BEGIN nm:stage0 -->
| Unit | Items per cell | M0: mix, null q, null always | KEQ: mix, null q, null always | KEQ-r: mix, null q, null always |
|---|---|---|---|---|
| C E2 colouring | pc20 | ✓ ✓ ✓ | ✓ ✓ ✓ | ✓ ✓ ✓ |
| C E2 knapsack | pc20 | ✓ ✗ ✓ | ✓ ✗ ✓ | ✓ ✗ ✓ |
| A/H E5 SAT | pc20 | ✓ ✓ ✓ | ✓ ✗ ✓ | ✓ ✗ ✓ |
| C E5 SAT, state given | pc40 | ✓ ✓ ✓ | ✓ ✗† ✓ | ✓ ✗† ✓ |
<!-- END nm:stage0 -->

### 4.4 The substantive weights

π with its 95% percentile interval, for the members the findings rest on (rows where every candidate gives below 0.02 are left out).

<!-- BEGIN nm:weights -->
| Unit | Member | Run | M0 | KE | KEQ | KEQ-r | SEQ-r |
|---|---|---|---|---|---|---|---|
| C E2 colouring | FF-LIST (C1, list order) | gpt-oss-120b low effort | 0.39 [0.31, 0.47] | 0.39 [0.31, 0.47] | 0.39 [0.31, 0.47] | 0.39 [0.31, 0.47] | – |
| C E2 colouring | FF-LIST (C1, list order) | gpt-oss-20b low effort | 0.35 [0.28, 0.41] | 0.35 [0.29, 0.41] | 0.35 [0.28, 0.41] | 0.35 [0.28, 0.41] | – |
| C E2 colouring | FF-LIST (C1, list order) | Qwen3-14B thinking | 0.46 [0.40, 0.53] | 0.46 [0.40, 0.53] | 0.46 [0.40, 0.53] | 0.46 [0.40, 0.53] | – |
| C E2 colouring | FF-LIST (C1, list order) | Qwen3-32B direct | 0.10 [0.06, 0.15] | 0.11 [0.06, 0.15] | 0.03 [0.00, 0.07] | 0.03 [0.00, 0.07] | – |
| C E2 colouring | FF-LIST (C1, list order) | Qwen3-32B thinking | 0.37 [0.31, 0.44] | 0.37 [0.31, 0.44] | 0.37 [0.31, 0.44] | 0.37 [0.31, 0.44] | – |
| C E2 colouring | RO-FF (C3) | gpt-oss-120b low effort | 0.41 [0.34, 0.48] | 0.41 [0.34, 0.48] | 0.41 [0.34, 0.48] | 0.41 [0.34, 0.48] | – |
| C E2 colouring | RO-FF (C3) | gpt-oss-20b low effort | 0.27 [0.22, 0.33] | 0.28 [0.22, 0.34] | 0.28 [0.22, 0.34] | 0.28 [0.22, 0.34] | – |
| C E2 colouring | RO-FF (C3) | Qwen3-14B thinking | 0.35 [0.29, 0.41] | 0.35 [0.29, 0.41] | 0.35 [0.29, 0.41] | 0.35 [0.29, 0.41] | – |
| C E2 colouring | RO-FF (C3) | Qwen3-32B thinking | 0.30 [0.24, 0.36] | 0.30 [0.24, 0.36] | 0.30 [0.24, 0.36] | 0.30 [0.24, 0.36] | – |
| C E2 colouring | EXACT | gpt-oss-120b low effort | 0.07 [0.04, 0.10] | 0.07 [0.03, 0.10] | 0.06 [0.03, 0.10] | 0.06 [0.03, 0.10] | – |
| C E2 colouring | EXACT | gpt-oss-20b low effort | 0.15 [0.10, 0.20] | 0.14 [0.07, 0.19] | 0.13 [0.08, 0.18] | 0.13 [0.08, 0.18] | – |
| C E2 colouring | EXACT | Qwen3-14B direct | 0.14 [0.08, 0.20] | 0.14 [0.08, 0.20] | 0.03 [0.00, 0.08] | 0.03 [0.00, 0.08] | – |
| C E2 colouring | EXACT | Qwen3-14B thinking | 0.03 [0.00, 0.06] | 0.03 [0.00, 0.06] | 0.03 [0.00, 0.06] | 0.03 [0.00, 0.06] | – |
| C E2 colouring | EXACT | Qwen3-32B direct | 0.40 [0.33, 0.48] | 0.40 [0.32, 0.48] | 0.09 [0.01, 0.16] | 0.09 [0.01, 0.16] | – |
| C E2 colouring | EXACT | Qwen3-32B thinking | 0.06 [0.00, 0.11] | 0.06 [0.00, 0.12] | 0.06 [0.00, 0.12] | 0.06 [0.00, 0.12] | – |
| C E2 knapsack | EXACT | gpt-oss-120b low effort | 0.74 [0.65, 0.82] | 0.72 [0.64, 0.81] | 0.72 [0.64, 0.81] | 0.72 [0.64, 0.81] | 0.72 [0.64, 0.81] |
| C E2 knapsack | EXACT | gpt-oss-20b low effort | 0.62 [0.53, 0.69] | 0.62 [0.53, 0.69] | 0.61 [0.52, 0.69] | 0.61 [0.52, 0.69] | 0.60 [0.51, 0.68] |
| C E2 knapsack | EXACT | Qwen3-14B direct | 0.17 [0.04, 0.30] | 0.19 [0.05, 0.33] | 0.19 [0.05, 0.33] | 0.18 [0.06, 0.30] | 0.19 [0.06, 0.31] |
| C E2 knapsack | EXACT | Qwen3-14B thinking | 0.98 [0.95, 0.99] | 0.98 [0.96, 1.00] | 0.97 [0.95, 0.99] | 0.97 [0.94, 0.99] | 0.97 [0.94, 0.99] |
| C E2 knapsack | EXACT | Qwen3-32B direct | 0.08 [0.00, 0.19] | 0.11 [0.01, 0.24] | 0.10 [0.01, 0.21] | 0.10 [0.01, 0.20] | 0.14 [0.03, 0.26] |
| C E2 knapsack | EXACT | Qwen3-32B thinking | 0.97 [0.95, 0.99] | 0.99 [0.97, 1.00] | 0.98 [0.96, 1.00] | 0.98 [0.96, 0.99] | 0.98 [0.96, 0.99] |
| C E2 knapsack | RATIO+BEST-SINGLE (C1) | gpt-oss-20b low effort | 0.03 [0.00, 0.11] | 0.01 [0.00, 0.06] | 0.01 [0.00, 0.06] | 0.01 [0.00, 0.06] | 0.02 [0.00, 0.09] |
| C E2 knapsack | RATIO+BEST-SINGLE (C1) | Qwen3-14B direct | 0.26 [0.10, 0.41] | 0.28 [0.09, 0.48] | 0.28 [0.09, 0.47] | 0.24 [0.08, 0.40] | 0.24 [0.03, 0.42] |
| C E2 knapsack | RATIO+BEST-SINGLE (C1) | Qwen3-32B direct | 0.59 [0.42, 0.74] | 0.65 [0.44, 0.83] | 0.59 [0.39, 0.76] | 0.57 [0.38, 0.72] | 0.42 [0.18, 0.63] |
| A/H E5 SAT | exact | gpt-oss-120b low effort | 0.30 [0.15, 0.47] | 0.35 [0.17, 0.54] | 0.28 [0.08, 0.42] | 0.22 [0.09, 0.34] | 0.29 [0.15, 0.42] |
| A/H E5 SAT | exact | gpt-oss-20b low effort | 0.05 [0.00, 0.13] | 0.08 [0.00, 0.20] | 0.01 [0.00, 0.09] | 0.00 [0.00, 0.05] | 0.00 [0.00, 0.08] |
| A/H E5 SAT | exact | Qwen3-14B direct | 0.02 [0.00, 0.15] | 0.19 [0.00, 0.34] | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.03] |
| A/H E5 SAT | exact | Qwen3-14B thinking | 0.30 [0.16, 0.42] | 0.31 [0.15, 0.44] | 0.25 [0.10, 0.35] | 0.18 [0.06, 0.31] | 0.22 [0.07, 0.38] |
| A/H E5 SAT | exact | Qwen3-32B direct | 0.02 [0.00, 0.09] | 0.19 [0.00, 0.34] | 0.00 [0.00, 0.08] | 0.00 [0.00, 0.06] | 0.03 [0.00, 0.10] |
| A/H E5 SAT | exact | Qwen3-32B thinking | 0.33 [0.17, 0.48] | 0.37 [0.21, 0.53] | 0.31 [0.15, 0.41] | 0.21 [0.11, 0.33] | 0.22 [0.11, 0.35] |
| A/H E5 SAT | A3 TT[exact] | gpt-oss-120b low effort | 0.01 [0.00, 0.10] | 0.08 [0.00, 0.21] | 0.03 [0.00, 0.13] | 0.02 [0.00, 0.10] | 0.00 [0.00, 0.07] |
| A/H E5 SAT | A3 TT[exact] | gpt-oss-20b low effort | 0.00 [0.00, 0.05] | 0.02 [0.00, 0.15] | 0.03 [0.00, 0.08] | 0.03 [0.00, 0.09] | 0.00 [0.00, 0.00] |
| A/H E5 SAT | A3 TT[exact] | Qwen3-14B direct | 0.00 [0.00, 0.00] | 0.21 [0.00, 0.41] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| A/H E5 SAT | A3 TT[exact] | Qwen3-14B thinking | 0.27 [0.14, 0.40] | 0.33 [0.20, 0.46] | 0.31 [0.14, 0.41] | 0.19 [0.10, 0.30] | 0.19 [0.09, 0.32] |
| A/H E5 SAT | A3 TT[exact] | Qwen3-32B direct | 0.00 [0.00, 0.13] | 0.15 [0.00, 0.31] | 0.00 [0.00, 0.11] | 0.00 [0.00, 0.07] | 0.00 [0.00, 0.12] |
| A/H E5 SAT | A3 TT[exact] | Qwen3-32B thinking | 0.24 [0.13, 0.35] | 0.27 [0.16, 0.38] | 0.22 [0.10, 0.32] | 0.18 [0.09, 0.28] | 0.18 [0.08, 0.30] |
| A/H E5 SAT | C0 POLARITY | gpt-oss-120b low effort | 0.09 [0.00, 0.16] | 0.14 [0.02, 0.25] | 0.11 [0.00, 0.23] | 0.07 [0.00, 0.14] | 0.08 [0.00, 0.15] |
| A/H E5 SAT | C0 POLARITY | gpt-oss-20b low effort | 0.05 [0.00, 0.14] | 0.23 [0.00, 0.40] | 0.00 [0.00, 0.06] | 0.00 [0.00, 0.08] | 0.15 [0.05, 0.26] |
| A/H E5 SAT | C0 POLARITY | Qwen3-14B direct | 0.02 [0.00, 0.07] | 0.09 [0.00, 0.31] | 0.01 [0.00, 0.06] | 0.01 [0.00, 0.06] | 0.02 [0.00, 0.09] |
| A/H E5 SAT | C0 POLARITY | Qwen3-32B direct | 0.02 [0.00, 0.09] | 0.13 [0.00, 0.32] | 0.01 [0.00, 0.09] | 0.01 [0.00, 0.06] | 0.01 [0.00, 0.07] |
| C E5 SAT, state given | EXACT | gpt-oss-120b low effort | 0.84 [0.76, 0.91] | 0.84 [0.76, 0.91] | 0.84 [0.76, 0.90] | 0.84 [0.76, 0.90] | 0.84 [0.76, 0.91] |
| C E5 SAT, state given | EXACT | gpt-oss-20b low effort | 0.61 [0.49, 0.71] | 0.60 [0.47, 0.71] | 0.61 [0.48, 0.71] | 0.61 [0.48, 0.71] | 0.59 [0.46, 0.70] |
| C E5 SAT, state given | EXACT | Qwen3-14B direct | 0.00 [0.00, 0.00] | 0.02 [0.00, 0.08] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.09 [0.00, 0.17] |
| C E5 SAT, state given | EXACT | Qwen3-14B thinking | 0.93 [0.85, 0.99] | 0.93 [0.85, 0.99] | 0.92 [0.83, 0.98] | 0.92 [0.83, 0.98] | 0.93 [0.85, 0.99] |
| C E5 SAT, state given | EXACT | Qwen3-32B direct | 0.00 [0.00, 0.05] | 0.00 [0.00, 0.05] | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.05 [0.00, 0.13] |
| C E5 SAT, state given | EXACT | Qwen3-32B thinking | 0.89 [0.81, 0.96] | 0.89 [0.81, 0.96] | 0.89 [0.81, 0.96] | 0.89 [0.81, 0.96] | 0.89 [0.81, 0.96] |
| C E5 SAT, state given | POLARITY (C0) | gpt-oss-120b low effort | 0.07 [0.01, 0.12] | 0.07 [0.01, 0.12] | 0.03 [0.00, 0.07] | 0.03 [0.00, 0.07] | 0.03 [0.00, 0.09] |
| C E5 SAT, state given | POLARITY (C0) | gpt-oss-20b low effort | 0.06 [0.02, 0.11] | 0.07 [0.02, 0.13] | 0.05 [0.00, 0.12] | 0.05 [0.00, 0.12] | 0.06 [0.00, 0.13] |
| C E5 SAT, state given | POLARITY (C0) | Qwen3-14B direct | 0.48 [0.33, 0.64] | 0.49 [0.33, 0.66] | 0.43 [0.26, 0.60] | 0.43 [0.26, 0.60] | 0.50 [0.34, 0.68] |
| C E5 SAT, state given | POLARITY (C0) | Qwen3-32B direct | 0.57 [0.44, 0.70] | 0.58 [0.44, 0.72] | 0.56 [0.43, 0.70] | 0.56 [0.43, 0.70] | 0.60 [0.47, 0.74] |
| C E5 SAT, state given | POLARITY (C0) | Qwen3-32B thinking | 0.02 [0.00, 0.05] | 0.02 [0.00, 0.06] | 0.02 [0.00, 0.06] | 0.02 [0.00, 0.06] | 0.02 [0.00, 0.05] |
| C E5 SAT, state given | ALWAYS-UNSAT (A1) | gpt-oss-20b low effort | 0.20 [0.10, 0.32] | 0.20 [0.09, 0.32] | 0.24 [0.15, 0.35] | 0.24 [0.15, 0.35] | 0.24 [0.14, 0.35] |
| C E5 SAT, state given | ALWAYS-UNSAT (A1) | Qwen3-14B thinking | 0.02 [0.00, 0.05] | 0.02 [0.00, 0.05] | 0.02 [0.00, 0.05] | 0.02 [0.00, 0.05] | 0.02 [0.00, 0.05] |
| C E5 SAT, state given | ALWAYS-UNSAT (A1) | Qwen3-32B direct | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.02] | 0.03 [0.00, 0.07] | 0.03 [0.00, 0.07] | 0.04 [0.00, 0.08] |
<!-- END nm:weights -->

### 4.5 Noise parameters under KEQ

ε with its interval, the kernel g₁…g₆, q's special-token mass τ, π₀, and the shares of answers the fit puts on members' exact answers, on slips and on q.

<!-- BEGIN nm:params-KEQ -->
| Unit | Run | ε [95%] | kernel g₁…g₆ | τ | π₀ | answers: exact | slip | q |
|---|---|---|---|---|---|---|---|---|
| C E2 colouring | gpt-oss-120b low effort | 0.41 [0.32, 0.49] | 0.15 0.15 0.22 0.14 0.10 0.24 | 0.00 | 0.02 | 0.34 | 0.23 | 0.02 |
| C E2 colouring | gpt-oss-20b low effort | 0.65 [0.58, 0.72] | 0.21 0.12 0.09 0.13 0.28 0.17 | 0.00 | 0.10 | 0.22 | 0.40 | 0.10 |
| C E2 colouring | Qwen3-14B direct | 1.00 [1.00, 1.00] | 0.06 0.00 0.09 0.00 0.00 0.85 | 0.00 | 0.95 | 0.00 | 0.05 | 0.95 |
| C E2 colouring | Qwen3-14B thinking | 0.13 [0.07, 0.19] | 0.27 0.09 0.16 0.25 0.17 0.06 | 0.00 | 0.00 | 0.57 | 0.08 | 0.00 |
| C E2 colouring | Qwen3-32B direct | 1.00 [1.00, 1.00] | 0.00 0.03 0.34 0.24 0.19 0.20 | 0.00 | 0.83 | 0.00 | 0.17 | 0.83 |
| C E2 colouring | Qwen3-32B thinking | 0.15 [0.10, 0.20] | 0.31 0.22 0.16 0.17 0.14 0.00 | 0.00 | 0.00 | 0.60 | 0.10 | 0.00 |
| C E2 knapsack | gpt-oss-120b low effort | 0.12 [0.07, 0.17] | 0.05 0.61 0.34 0.00 0.00 0.00 | 0.00 | 0.01 | 0.87 | 0.12 | 0.01 |
| C E2 knapsack | gpt-oss-20b low effort | 0.27 [0.21, 0.33] | 0.21 0.50 0.29 0.00 0.00 0.00 | 0.00 | 0.02 | 0.71 | 0.26 | 0.02 |
| C E2 knapsack | Qwen3-14B direct | 0.86 [0.79, 0.92] | 0.41 0.27 0.23 0.09 0.00 0.00 | 0.00 | 0.00 | 0.14 | 0.86 | 0.00 |
| C E2 knapsack | Qwen3-14B thinking | 0.00 [0.00, 0.02] | 0.00 1.00 0.00 0.00 0.00 0.00 | 0.00 | 0.01 | 0.99 | 0.00 | 0.01 |
| C E2 knapsack | Qwen3-32B direct | 0.94 [0.89, 0.98] | 0.35 0.39 0.23 0.02 0.00 0.00 | 0.00 | 0.09 | 0.05 | 0.85 | 0.09 |
| C E2 knapsack | Qwen3-32B thinking | 0.02 [0.01, 0.04] | 0.57 0.00 0.19 0.24 0.00 0.00 | 0.00 | 0.01 | 0.98 | 0.02 | 0.01 |
| A/H E5 SAT | gpt-oss-120b low effort | 0.85 [0.66, 0.98] | 0.10 0.17 0.20 0.22 0.19 0.13 | 0.28 | 0.57 | 0.06 | 0.36 | 0.57 |
| A/H E5 SAT | gpt-oss-20b low effort | 1.00 [1.00, 1.00] | 0.10 0.00 0.42 0.00 0.48 0.00 | 0.35 | 0.76 | 0.00 | 0.24 | 0.76 |
| A/H E5 SAT | Qwen3-14B direct | 1.00 [1.00, 1.00] | 0.00 1.00 0.00 0.00 0.00 0.00 | 0.00 | 0.99 | 0.00 | 0.01 | 0.99 |
| A/H E5 SAT | Qwen3-14B thinking | 0.56 [0.32, 0.71] | 0.23 0.18 0.07 0.00 0.35 0.18 | 0.45 | 0.40 | 0.26 | 0.34 | 0.40 |
| A/H E5 SAT | Qwen3-32B direct | 1.00 [1.00, 1.00] | 0.00 1.00 0.00 0.00 0.00 0.00 | 0.03 | 0.99 | 0.00 | 0.01 | 0.99 |
| A/H E5 SAT | Qwen3-32B thinking | 0.58 [0.36, 0.70] | 0.24 0.17 0.13 0.05 0.16 0.25 | 0.24 | 0.39 | 0.25 | 0.35 | 0.39 |
| C E5 SAT, state given | gpt-oss-120b low effort | 0.40 [0.29, 0.52] | 0.38 0.35 0.14 0.13 0.00 0.00 | 0.00 | 0.06 | 0.56 | 0.38 | 0.06 |
| C E5 SAT, state given | gpt-oss-20b low effort | 0.66 [0.52, 0.81] | 0.21 0.25 0.29 0.18 0.06 0.00 | 0.00 | 0.09 | 0.23 | 0.45 | 0.09 |
| C E5 SAT, state given | Qwen3-14B direct | 1.00 [0.96, 1.00] | 0.02 0.17 0.27 0.21 0.18 0.15 | 0.00 | 0.33 | 0.00 | 0.67 | 0.33 |
| C E5 SAT, state given | Qwen3-14B thinking | 0.14 [0.06, 0.22] | 0.56 0.28 0.15 0.00 0.00 0.00 | 0.00 | 0.02 | 0.83 | 0.13 | 0.02 |
| C E5 SAT, state given | Qwen3-32B direct | 0.96 [0.91, 1.00] | 0.07 0.14 0.29 0.23 0.18 0.09 | 0.00 | 0.09 | 0.03 | 0.84 | 0.09 |
| C E5 SAT, state given | Qwen3-32B thinking | 0.30 [0.20, 0.39] | 0.36 0.22 0.19 0.13 0.04 0.06 | 0.00 | 0.00 | 0.69 | 0.29 | 0.00 |
<!-- END nm:params-KEQ -->

### 4.6 What the evaluation shows

- **Fit.** M0 passes every check on 5 of 24 fits; KEQ on 14; KEQ-r on 11 (its three losses against KEQ are marginal "beyond reach" failures on gpt-oss-20b knapsack, gpt-oss-20b and Qwen3-32B thinking A/H E5 SAT: with the reach cut, answers 4–6 positions out are q's, and q's rate of producing them is a little off); KE on 17, but by the wrong attribution (§5.4); SEQ-r on 15 of its 18 bit-space fits. ε is at its cap on 14 fits under M0 and on 5 under KEQ, all five at ε = 1 in the direct condition, where almost no answer is a member's exact answer and the fit says so. What KEQ still fails: the thinking colouring fits (RO-FF, §2.3 item 4, unchanged by any noise model), the direct colouring fits on "beyond reach" (q's random 3- and 4-colourings are farther from the members than the real far answers, which are poor colourings of *this* graph: an instance-aware q would be needed), and the C E5 special-token share of three fits (τ is 0 there by the ridge rule, so constant UNSAT is ALWAYS-UNSAT's).
- **Identifiability at pilot sizes (Stage 0).** The 60/30/10 mixture passes on all four units under every candidate that was run, with the same bias, coverage and width as M0. The nulls are where lifting the cap costs: with six-position slips, pure q data load 0.23 on members on knapsack and 0.07 on A/H E5 SAT (KEQ). Cutting the reach (KEQ-r) brings that to 0.050 and 0.036, at the gate, against 0.007 and 0.004 under M0; q's interval then covers 1 in 2% and 51% of replicates (M0: 73% and 98%; knapsack's null already failed under M0, a boundary effect, RECOVERY.md). On C E5 the `null_q` failure is definitional: M0's q answers UNSAT half the time, and under KEQ a constant UNSAT is ALWAYS-UNSAT's, which gets 0.48 against the 0.5 that definition implies (q 0.49).
- **Recovery at the estimate** passes on 6 fits under M0 (percentile; 9 with BCa), 3 under KEQ (8 with BCa) and 5 under KEQ-r (11 with BCa). The failures are coverage of small planted weights (mostly 0.7–0.89 against the 0.9 gate; 0.35–0.45 for the 0.02 weights of C E5's thinking fits, under M0 too), with bias below 0.05 everywhere but one quantity under KEQ (A/H E5 SAT, Qwen3-32B thinking, q: 0.061; 0.012 under KEQ-r). The extra parameters cost some coverage at these sizes; BCa recovers most of it on colouring.
- **Weights.** Where the findings rest on a weight, it does not move: C1 list-order first fit (FF-LIST) in thinking-condition colouring is 0.46 [0.40, 0.53] and 0.37 [0.31, 0.44] under both M0 and KEQ; EXACT on thinking knapsack and C E5, gpt-oss's knapsack and colouring weights, POLARITY on C E5 direct (0.48 → 0.43, 0.57 → 0.56), RATIO+BEST-SINGLE on direct knapsack (0.26 → 0.28, 0.59 → 0.59) all stay within their intervals. What moves is the direct-condition colouring: M0's EXACT weights there, 0.40 [0.33, 0.48] (Qwen3-32B) and 0.14 (Qwen3-14B), were the uniform q's artefact (every 3- or 4-colouring within six vertices of an optimal one was a slip of EXACT); under KEQ they are 0.09 and 0.03, and q takes 0.83 and 0.95. And under KEQ-r, A/H E5 SAT's thinking-condition weights move with the reach: exact 0.30 → 0.18 and 0.33 → 0.21, A3 TT[exact] 0.27 → 0.19 and 0.24 → 0.18 (intervals overlap), with q's share of the answers rising from about 0.4 to about 0.57, because answers five or six flips from a member are no longer its slips. Those weights depend on how far a slip is allowed to go, which the data on these items do not pin down.
- **Noise mass.** Across the 24 fits the share of answers put on slips or q has the same median under M0 and KEQ (0.63). KEQ does not pass by calling more of the data noise; it moves noise from slips to q where the answers are far (direct colouring) and from q to slips where they are near (direct knapsack: q 0.09 → 0.00).

### 4.7 Recurrence: do wrong answers repeat as often as the fitted model says?

The eight cheap pilot runs were redrawn with a second sample (PR #51). If wrong answers were independent draws from the fitted mixture, two samples of an item would give the same wrong answer with probability Σ_y P(y | x)² over wrong y. The table gives, per fit with repeats, the number of items whose two answers are the same wrong answer, observed, then expected under M0, KEQ and KEQ-r (the sum of that probability over the items; 400 simulated pairs per item; KEQ-r is KEQ on colouring and C E5), split by sample 0's answer: matching no member, a member's answer, a special token.

<!-- BEGIN nm:recurrence -->
| Unit | Run | Items answered twice | unmatched: observed / M0 / KEQ / KEQ-r | member's answer: observed / M0 / KEQ / KEQ-r | special token: observed / M0 / KEQ / KEQ-r |
|---|---|---|---|---|---|
| C E2 colouring | Qwen3-14B direct | 300 | 117 / 0.0 / 6.0 / – | 0 / 0.1 / 0.0 / – | 0 / 0.0 / 0.0 / – |
| C E2 colouring | Qwen3-32B direct | 299 | 17 / 0.0 / 0.0 / – | 0 / 1.1 / 0.0 / – | 0 / 0.0 / 0.0 / – |
| C E2 colouring | gpt-oss-20b low effort | 299 | 2 / 0.1 / 0.1 / – | 9 / 7.7 / 3.9 / – | 0 / 0.0 / 0.0 / – |
| C E2 colouring | gpt-oss-120b low effort | 300 | 17 / 0.1 / 0.1 / – | 24 / 13.3 / 13.3 / – | 0 / 0.0 / 0.0 / – |
| C E2 knapsack | Qwen3-14B direct | 300 | 153 / 0.8 / 1.9 / 2.0 | 22 / 14.6 / 1.6 / 1.5 | 0 / 0.0 / 0.0 / 0.0 |
| C E2 knapsack | Qwen3-32B direct | 300 | 163 / 1.0 / 2.4 / 2.3 | 17 / 28.9 / 0.6 / 0.6 | 0 / 0.0 / 0.0 / 0.0 |
| C E2 knapsack | gpt-oss-20b low effort | 300 | 6 / 0.3 / 0.1 / 0.1 | 13 / 8.1 / 8.1 / 8.2 | 0 / 0.0 / 0.0 / 0.0 |
| C E2 knapsack | gpt-oss-120b low effort | 300 | 9 / 0.0 / 0.0 / 0.1 | 14 / 7.4 / 8.1 / 7.9 | 0 / 0.0 / 0.0 / 0.0 |
| A/H E5 SAT | Qwen3-14B direct | 100 | 46 / 0.0 / 6.5 / 6.2 | 0 / 0.0 / 0.0 / 0.0 | 0 / 23.5 / 0.0 / 0.0 |
| A/H E5 SAT | Qwen3-32B direct | 90 | 17 / 0.0 / 0.2 / 0.2 | 0 / 0.0 / 0.0 / 0.0 | 1 / 20.3 / 0.1 / 0.1 |
| A/H E5 SAT | gpt-oss-20b low effort | 93 | 4 / 0.0 / 2.0 / 1.8 | 0 / 0.1 / 0.0 / 0.0 | 12 / 17.4 / 6.9 / 6.7 |
| A/H E5 SAT | gpt-oss-120b low effort | 98 | 1 / 0.0 / 0.3 / 0.3 | 0 / 0.2 / 0.0 / 0.0 | 5 / 9.1 / 2.5 / 2.5 |
| C E5 SAT, state given | Qwen3-14B direct | 120 | 66 / 0.0 / 0.0 / – | 0 / 8.8 / 0.0 / – | 0 / 0.2 / 0.0 / – |
| C E5 SAT, state given | Qwen3-32B direct | 120 | 19 / 0.0 / 0.0 / – | 0 / 9.5 / 0.1 / – | 0 / 0.6 / 0.4 / – |
| C E5 SAT, state given | gpt-oss-20b low effort | 120 | 0 / 0.0 / 0.0 / – | 0 / 0.2 / 0.0 / – | 6 / 4.5 / 4.5 / – |
| C E5 SAT, state given | gpt-oss-120b low effort | 120 | 0 / 0.0 / 0.0 / – | 0 / 0.2 / 0.1 / – | 0 / 0.0 / 0.0 / – |
<!-- END nm:recurrence -->

- **Qwen3 direct: the unexplained answers are not noise.** 117, 153, 163, 46 and 66 items repeat an answer no member gives, where M0, KEQ and KEQ-r expect 0–6.5. They are reproducible procedures outside the zoo: the repeat-samples analysis lists template answers (all-true, all-false and alternating assignments, colours cycled in list order), and §2.2 shows under-filled packings (drops from a greedy packing) and over-true C E5 assignments. No slip kernel or q in this family generates them, because slips and q are independent draws. The strata q comes closest where the template is a one-answer stratum (all-false, all-distinct colours: 6.0 and 6.5 expected).
- **Member answers repeat more than any per-draw mixture allows** (gpt-oss-120b colouring: 24 observed, 13 expected; Qwen3 direct knapsack: 17–22 observed, where KEQ, with ε ≈ 0.9, expects about 1). Strategy choice looks fixed per item, not drawn afresh per response.
- **The special token:** M0 expects 20–23 repeated UNSATs from Qwen3 direct on A/H E5, from q's fixed half; 0 and 1 are observed. KEQ's estimated τ expects 0.0 and 0.1.
- **gpt-oss:** unmatched wrong answers rarely repeat (0–17 items, mostly 0–9), close to what a noise model allows.

So the noise model can stop manufacturing structure (M0's EXACT weights in direct colouring, its UNSAT mass), but in the direct condition the residual is systematic and belongs to the zoo, not to the noise.

## 5. Recommendation

### 5.1 Adopt KEQ-r

**KEQ-r**: `NoiseModel(kernel="free", eps_max=1.0, q="strata", reach="auto")`, i.e.

- near-miss slips as now, with a **free distance kernel** g₁…g₆ shared by a unit's members;
- **ε estimated up to 1**, with the **kernel's reach cut** where a slip's ball would hold more than a fifth of the answer space (knapsack 3, A/H E5 SAT 4, colouring and C E5 SAT 6);
- **q uniform within size strata** (colours used; items packed or variables true), the strata's probabilities and the special-token mass τ estimated, τ = 0 where a member answers the special token on every item.

Against M0, on the 24 fits with the committed settings:

| | M0 | KEQ-r |
|---|---|---|
| Fits passing every predictive check | 5 | 11 |
| … with ε below its cap (the results page's "reproduces the data") | 4 | 10 |
| Fits with ε at its cap | 14 (at 0.5) | 5 (at 1: no answer is the member's exact output) |
| Recovery at the estimate passes, percentile / BCa | 6 / 9 | 5 / 11 |
| Stage 0: the 60/30/10 mixture, four units | 4 / 4 | 4 / 4 |
| Stage 0: the nulls, four units | 7 / 8 | 5 / 8 (C E5's `null_q` fails by definition, †) |
| Pure noise put on members (`null_q`), knapsack / A/H E5 SAT | 0.007 / 0.004 | 0.050 / 0.036 |
| Median share of answers put on noise (slips + q) | 0.63 | 0.64 |
| C1 list-order first fit, thinking colouring, Qwen3-14B / 32B | 0.46 / 0.37 | 0.46 / 0.37 |
| EXACT, direct colouring, Qwen3-32B / 14B | 0.40 / 0.14 | 0.09 / 0.03 |

Why this one:

1. **It fixes the failures that are the noise model's.** The cap (the "exact" failures of the direct condition), q's colour count (direct colouring) and its UNSAT half (A/H E5), and the kernel's shape (knapsack's swaps) are each a parameter that is now estimated. More than twice as many fits pass, and the five at ε = 1 say something true about the direct condition rather than hitting a limit. (KE passes more, 17, by crediting members with far answers; §5.4.)
2. **It stays identified at pilot sizes.** The planted mixture is recovered as under M0 on all four gated units. KEQ, the same model without the reach cut, fits three more fits but puts 0.23 of pure noise on knapsack's members; KEQ-r keeps that at the 0.05 gate.
3. **It does not buy fit with noise.** The noise share is unchanged; noise moves from slips to q where answers are far and from q to slips where they are near. And it removes two artefacts of M0 that looked like findings: EXACT's weight in direct-condition colouring, and the UNSAT answers M0's q expects to recur (§4.7).
4. **The weights the findings rest on do not change** (§4.4), with one sensitivity: A/H E5 SAT's thinking-condition weights on exact and A3 TT[exact] fall by 0.06–0.12 with the reach cut (§4.6), so they should be quoted with both reaches until the items separate near and far misses better. The findings page's claims are mostly descriptive counts; the fitted weights it quotes (C E5's POLARITY in the direct condition and EXACT in the thinking one, claim 2) stay within their intervals. Claim 4 ("a mixture of heuristics run exactly, plus near misses, rarely reproduces the data") gets new numbers, and the results page's direct-condition colouring weights change.


### 5.2 Trade-offs

- **Pure noise leaks onto members on small bit spaces.** Under KEQ-r, at pilot sizes, about 0.04–0.05 of pure q data goes to members on knapsack and A/H E5 SAT (M0: under 0.01), spread over the members (knapsack: no single member above 0.06 under KEQ, less under KEQ-r). Read weights below about 0.05 on those units as compatible with none, and do not read π₀'s interval at the boundary there: it under-covers (also under M0 on knapsack). The boundary-aware interval for π₀ (RECOVERY.md, "What is left") is the fix for the coverage; it is about a day's work.
- **Recovery at the estimate passes about as often as under M0** (5 against 6 with percentile intervals, 11 against 9 with BCa); small weights' coverage is the binding gate for both (§4.6).
- **ε = 1 is a statement, not a failure.** It says no answer is the member's exact output; such a member's weight is nearness to its answer, and the results page's rule (ε at its cap → "nearness, not use") should keep applying with the cap at 1.
- **More parameters per unit**: 4 for the kernel, up to n per number of positions for q, and τ.
- **The reach threshold is a choice.** A fifth of the answer space is a judgement, not an estimate. It decides knapsack's and A/H E5 SAT's reach (3 and 4), and A/H E5 SAT's thinking weights move with it (§4.6). A larger reach (KEQ) fits better and leaks more noise; a smaller one would push more near misses into q.

### 5.3 Departure from SCOPE §6 rule 3

Rule 3 pre-registers the noise model: near-miss slips, with the slip rate estimated rather than fixed, because uniform slips biased diffuse members' weights (the C vertical's recovery run, and RECOVERY.md's misspecification table). The recommendation keeps that principle: a slip still lands near the member's answer, and its rate is still estimated. It changes four details, all chosen after seeing the 2026-11-18 data:

1. the kernel's shape is estimated per unit (free) instead of geometric;
2. the cap on ε is lifted, and
3. the kernel's reach is cut where a slip could otherwise pass for q;
4. q's distribution over answer sizes, and its special-token mass, are estimated instead of fixed.

Because they were chosen after seeing the data, fits under the new model on these runs are exploratory. To make it confirmatory, freeze it (this page and `NoiseModel` as committed) before the next data that will be analysed (repeat samples, the test split), and report the M0 fits alongside on the 2026-11-18 runs, as the pre-registered analysis.


### 5.4 Not recommended

- **K (free kernel, cap kept)** fixes the knapsack swaps' distance profile but none of the cap or q failures.
- **KE (cap lifted, uniform q)** passes the most checks (17 of 24), and that is the warning in this evaluation: it passes them by putting far answers on members' always-slipping clouds instead of on q. On A/H E5 SAT in the direct condition π₀ falls to 0.47 and 0.53 (KEQ 0.99, M0 0.97) and exact and A3 TT[exact] take 0.15–0.21 each, from answers the recurrence check shows to be reproducible off-zoo procedures; on direct colouring it keeps M0's EXACT artefact (0.40, π₀ 0.33). Its likelihood is 1,700–2,100 units below KEQ's on direct colouring and 115–315 below on A/H E5 SAT. The four checks are coarse (a share of exact answers, of far answers, of special tokens, a distance profile), and a flexible kernel can match them with the wrong attribution; the likelihood ladder and the weights have to be read with them.
- **KEQ-h (per-member ε)** gains 0–25 log-likelihood units for up to 9 more parameters; a member with little weight has an unidentified rate.
- **SEQ-r (adds-and-drops kernel), the runner-up for bit spaces.** On the 18 bit-space fits (knapsack, both SAT units) it passes every check on 15, against 10 for KEQ-r, and SEQ gains 1–259 log-likelihood units over KEQ (§2.4), most on the direct fits. It captures real structure: gpt-oss's one-for-one swaps, the direct condition's dropped items and over-true assignments. Three things keep it second:
  - it has not been through Stage 0 (no box time), and it has 21 more kernel cells per unit;
  - it moves direct-condition attributions: Qwen3-32B's direct knapsack goes from RATIO+BEST-SINGLE 0.57 and DIFF 0.12 (KEQ-r) to 0.42 and 0.26, and C E5's Qwen3-14B direct π₀ from 0.33 to 0.06, by crediting members with the dropped-item and over-true answers that §4.7 shows recur, i.e. are procedures, not slips (KEQ-r does the same for answers within its reach, but less);
  - on the thinking and gpt-oss fits, where the attribution matters, it agrees with KEQ-r; overall it puts more of the data on slips (median noise share 0.74 on its 18 fits, against 0.64 for KEQ-r on 24).

  If gpt-oss's knapsack swaps matter for a claim, run SEQ-r through Stage 0 at pilot size and adopt it for bit spaces if it passes; colouring keeps KEQ-r either way (the kernel is not defined on partitions).
- **A validity-aware q** is not identified on SAT and k-colouring (the valid answers are EXACT's support), and the far answers it would explain are mostly invalid (§2.3).

### 5.5 What the noise model cannot fix, and what would

1. **Template and off-zoo members for the direct condition** (from §4.7 and the repeat-samples analysis): ALWAYS-TRUE, ALWAYS-FALSE and ALTERNATING assignments, CYCLE colourings in list order, a greedy packing that stops early, a polarity-only assignment that ignores the given state. Each is a deterministic member, so it is tested exactly, and the recurrence check says how much of the direct-condition residual each takes.
2. **A repeat-aware likelihood**: with two samples per item, P(y₁, y₂ | x) = Σ_h π_h P(y₁ | h, x) P(y₂ | h, x) + π₀ q(y₁) q(y₂), a member chosen once per item. That uses the recurrence directly instead of checking it afterwards, and separates "the same procedure twice" from "noise twice".
3. **Thinking-condition colouring**: RO-FF's spread (§2.3 item 4) is a zoo question.
4. **An instance-aware q for colouring** (conflicting edges as a stratum) would fix the direct colouring fits' "beyond reach" failure; whether it is worth it depends on item 1.


## Reproduce

Everything heavy runs on the agent box (`remote-run`), three worker processes, niced; see `analysis/noise_model_run.sh` for the steps.

```bash
# the diagnosis (data, and point fits of every candidate)
OMP_NUM_THREADS=1 python analysis/noise_model_eval.py diagnose --out analysis/out/noise_model/diagnosis.json
# one candidate on the 24 gated fits, with recovery at the estimate (or `--recovery-boot 0`: the checks only)
OMP_NUM_THREADS=1 python analysis/noise_model_eval.py fits --noise KEQ --workers 3 --out analysis/out/noise_model/fits_KEQ.json
# Stage 0 with a candidate
OMP_NUM_THREADS=1 python -m reasoning_heuristics.identify.recovery run --items data/items/pc20 --label pc20 \
    --units 'C_E2/colouring;C_E2/knapsack;AH_E5/SAT' --scenarios mix,null_q,null_always --reps 100 --boot 100 \
    --noise KEQ --workers 3 --out analysis/out/noise_model/stage0_pc20_KEQ.json
# this page's tables
python analysis/noise_model_tables.py --write-doc        # or --check
# the check that the evaluation reproduces the committed analysis under M0
OMP_NUM_THREADS=1 python analysis/noise_model_eval.py fits --noise M0 --only "C_E2/knapsack 2026-11-18-pc20-gpt-oss-20b" \
    --out analysis/out/noise_model/m0_check.json
```

A candidate is any option string as well as a name: `--noise kernel=free,eps_max=1,q=strata,reach=auto`.
