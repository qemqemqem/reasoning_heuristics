# The noise model for the mixture fits

*Decision record, 2026-11-19. STATUS "Open decisions" asked which noise model the mixture fits should use, because the pre-registered one (SCOPE §6 rule 3) fits the 2026-11-18 data badly. This page gives the diagnosis, the candidates, their evaluation on the 24 gated fits with the committed analysis's settings, and a recommendation. The code is in `src/reasoning_heuristics/identify/noise.py` (options, all defaulting to the pre-registered model) and `analysis/noise_model_eval.py`; the numbers are in [analysis/out/noise_model/](../analysis/out/noise_model/). The committed results page and JSON are not regenerated here.*

<!-- RECOMMENDATION -->

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
| C E2 colouring | gpt-oss-120b low effort | +4 (+4) | +4 (+4) | +51 (+19) | +73 (+25) | – | – | – |
| C E2 colouring | gpt-oss-20b low effort | +12 (+4) | +21 (+4) | +276 (+19) | +289 (+25) | – | – | – |
| C E2 colouring | Qwen3-14B direct | +73 (+4) | +114 (+4) | +1837 (+19) | +1837 (+25) | – | – | – |
| C E2 colouring | Qwen3-14B thinking | +2 (+4) | +2 (+4) | +2 (+19) | +6 (+25) | – | – | – |
| C E2 colouring | Qwen3-32B direct | +154 (+4) | +293 (+4) | +2431 (+19) | +2431 (+25) | – | – | – |
| C E2 colouring | Qwen3-32B thinking | +2 (+4) | +2 (+4) | +2 (+19) | +6 (+25) | – | – | – |
| C E2 knapsack | gpt-oss-120b low effort | +21 (+4) | +21 (+4) | +21 (+14) | +32 (+20) | +38 (+35) | – | – |
| C E2 knapsack | gpt-oss-20b low effort | +21 (+4) | +21 (+4) | +23 (+14) | +48 (+20) | +52 (+35) | – | – |
| C E2 knapsack | Qwen3-14B direct | +14 (+4) | +96 (+4) | +96 (+14) | +106 (+20) | +105 (+35) | – | – |
| C E2 knapsack | Qwen3-14B thinking | +3 (+4) | +3 (+4) | +4 (+14) | +9 (+20) | +6 (+35) | – | – |
| C E2 knapsack | Qwen3-32B direct | +29 (+4) | +153 (+4) | +160 (+14) | +163 (+20) | +239 (+35) | – | – |
| C E2 knapsack | Qwen3-32B thinking | +3 (+4) | +3 (+4) | +3 (+14) | +6 (+20) | +6 (+35) | – | – |
| A/H E5 SAT | gpt-oss-120b low effort | +1 (+4) | +18 (+4) | +61 (+33) | +64 (+37) | +72 (+54) | – | – |
| A/H E5 SAT | gpt-oss-20b low effort | +3 (+4) | +21 (+4) | +163 (+33) | +163 (+37) | +172 (+54) | – | – |
| A/H E5 SAT | Qwen3-14B direct | +3 (+4) | +21 (+4) | +336 (+33) | +336 (+37) | +340 (+54) | – | – |
| A/H E5 SAT | Qwen3-14B thinking | +3 (+4) | +5 (+4) | +23 (+33) | +26 (+37) | +28 (+54) | – | – |
| A/H E5 SAT | Qwen3-32B direct | +2 (+4) | +22 (+4) | +115 (+33) | +115 (+37) | +116 (+54) | – | – |
| A/H E5 SAT | Qwen3-32B thinking | +2 (+4) | +5 (+4) | +22 (+33) | +27 (+37) | +27 (+54) | – | – |
| C E5 SAT, state given | gpt-oss-120b low effort | +0 (+4) | +0 (+4) | +7 (+24) | +14 (+30) | +26 (+45) | – | – |
| C E5 SAT, state given | gpt-oss-20b low effort | +3 (+4) | +8 (+4) | +19 (+24) | +23 (+30) | +30 (+45) | – | – |
| C E5 SAT, state given | Qwen3-14B direct | +24 (+4) | +96 (+4) | +142 (+24) | +144 (+30) | +401 (+45) | – | – |
| C E5 SAT, state given | Qwen3-14B thinking | +0 (+4) | +0 (+4) | +3 (+24) | +4 (+30) | +9 (+45) | – | – |
| C E5 SAT, state given | Qwen3-32B direct | +11 (+4) | +65 (+4) | +77 (+24) | +77 (+30) | +121 (+45) | – | – |
| C E5 SAT, state given | Qwen3-32B thinking | +0 (+4) | +0 (+4) | +0 (+24) | +9 (+30) | +3 (+45) | – | – |
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

- **Free kernel.** g₁…g₆ are free and shared by the unit's members; the M-step sets g_d to the expected share of slips at distance d. The geometric kernel is the special case g_d ∝ ρ^(d−1).
- **The (adds, drops) kernel** (SEQ, "swap-aware"). On a bit vector a slip draws a cell (a, r) with a + r ≤ 6, then sets a of the answer's clear positions and clears r of its set ones, uniformly. A one-for-one swap is the cell (1, 1), an under-filled packing (0, r), an over-true assignment (a, 0). It is an exact pmf (`spaces.BitSpace.slip_ad`), 26 free cells.
- **Lifting the cap.** The cap exists so that slips cannot absorb everything (A/H §5.3 point 3): on a finite channel a member that always slips is RANDOM. On witness channels a slip moves at most six positions, so a member at ε = 1 is a cloud around its answer, not RANDOM, except where six positions cover most of the space (knapsack: 848 of the 1,024 packings are within six items of any given one). Stage 0's `null_q` scenario is the test of whether that matters.
- **The strata q.** q is uniform within strata, the number of colours of a colouring or the number of set positions of a bit vector (items packed, variables true), with the strata's probabilities estimated (one categorical per number of positions n), and the special tokens' total mass τ estimated. The uniform q is the special case P(s) ∝ |stratum s|. Two identifiability rules:
  - Where a member predicts a special token on every item (ALWAYS-UNSAT in C E5), τ and that member's weight are one ridge (only π_member + τ π₀ is identified), so τ = 0 there and the member carries the constant token. In the gated units this applies to C E5 SAT only.
  - A one-answer stratum (one colour for every vertex, all 16 distinct, the empty set, all true) lets q put a point mass on a constant answer. None of the gated units has a member that answers a constant structured answer, so this is identified there; on units that do (e.g. LOCAL-2-ID in C E1 colouring, nearly one colour), the stratum would have to be merged with its neighbour.
- **Per-member ε** (KEQ-h): one rate per tie group. A member with little weight has an unidentified rate; the summary ε is the weight-averaged rate of the slipping members.

<!-- EVALUATION -->
