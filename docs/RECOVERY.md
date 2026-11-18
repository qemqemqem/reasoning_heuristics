# Recovery: positive controls for the identification engine

*The Stage 0 gate (SCOPE §4 item 5; DESIGN §5 rule 12): before any LLM data is analysed, fake models with planted mixtures must be recovered with |bias| ≤ 0.05, 95% coverage ≥ 0.9 and median interval width ≤ 0.2. Results on the regenerated items are in [data/recovery/](../data/recovery/): `dev.json`, `pc10.json`, `pc20.json`, `pc40.json`. The pre-regeneration results are in [data/recovery/pre-regeneration/](../data/recovery/pre-regeneration/); this page as it stood for them is `docs/RECOVERY.md` at e68b755.*

**Items.**

- **5 per cell:** `data/items/dev` as on main after #22. In it, the C E1 and C E2 SAT items list `ALWAYS-UNSAT (A1 give-up)`.
- **20 per cell:** `data/items/pc20` (#21, #22) for C E1, C E2 and A/H E5. The other evals at 20 per cell, and every eval at 10 and 40, are scratch sets generated with `python -m reasoning_heuristics.generate --vertical V --eval E --tier dev --seed 1 --per-cell N` from main's generator code; for C E1 and C E2 that means after #22.
- **B4/C4 E1, B4/C4 E2 and C E3** were run at dev size only. They fail there for reasons that more items don't fix (the table at the end), and they are the slowest units.
- Every result file records, for each run merged into it: the command, the code SHA, and the sha256 of every item file it read.

**Code.** The engine as of #24:

- special-token predictions do not slip;
- BCa intervals are reported next to the percentile ones;
- `--units` is `;`-separated.

Units on which no member predicts a special token were run before the no-slip change. The change does not touch their code path: A/H E5 SAT, rerun as a control, reproduces its results exactly.

## Bottom line

- **No unit passes at dev size (5 items per cell).** There the units have 10–270 items in 5–30 clusters.
- **The 60/30/10 mixture passes all three gates** with 100 replicates and percentile intervals here:

  | Unit | Items per cell |
  |---|---|
  | C E2 colouring | 20 and 40 |
  | C E2 knapsack | 20 and 40 |
  | A/H E5 SAT | 20 and 40 |
  | A/H E5 colouring | 40 |
  | C E5 SAT with a given state | 40 (GUC-DET and SC-DET from state are tied on those items and share one weight) |

  C E2 SAT also passes, at 40 per cell, on the items after #22. C E1 SAT passes only with BCa intervals, at 20 and 40. With percentile intervals, its 0.1 ALWAYS-UNSAT weight covers 0.79–0.86, at a bias of 0.02 or less.

  With BCa intervals the list changes only at the margin: C E2 colouring also passes at 5 and 10 but not at 40; C E1 SAT passes at 20 and 40, and C E1 colouring at 20; A/H E5 SAT passes at neither size.
- **The mixture and both null scenarios pass together** at these sizes:
  - C E2 colouring at 20 and 40;
  - A/H E5 SAT at 20 and 40;
  - A/H E5 colouring at 40;
  - C E5 SAT with a given state at 40.

  C E2 knapsack's `null_q` fails coverage at every size from 10 on (a boundary effect, with bias ≤ 0.01).
- **A pass refers to the exact item sets run.** At 20 per cell those are `data/items/pc20` for C E1, C E2 and A/H E5. The 10- and 40-per-cell sets, and 20 per cell for the other evals, are not committed: they regenerate deterministically with the command above, and the result files record each file's sha256, so a regeneration can be checked against them. The closing table also lists what each pass covers, including the members it can only report as one group.
- **Coverage is the gate that binds.** Where bias and width pass (near-tie runs aside), the smallest per-weight coverage is 0.79–0.94, on the 0.1 or the 0.3 weight. At 100 replicates the binomial SE is about 0.03, so verdicts at 0.88–0.92 are close calls in either direction.
  - BCa raises the 0.1 weight's coverage by a median of 0.02 and changes little else.
  - The two methods' verdicts differ on 7 unit-sizes, in both directions (see Percentile against BCa).
- **Fails by design**, where more items won't help:
  - the six A/H decision units: q is not identified on a two-valued channel, and the noise models are near-mixtures of the procedures;
  - B4/C4 E1 (σ_min/σ_max = 0.0004);
  - B4/C4 E2 (five dependencies, including the H6 gap, which the zoo fixes did not close);
  - C E3 (a new exact dependency between DPLL-LIST = FF-LIST and the LOCAL-t proxies);
  - C E5 entailment;
  - C E5 colouring (k = 3), whose near-tie (2 of 25 dev items) collapses coverage at 5–10 per cell and keeps the width at 0.46 at 40. See the closing table for each.
- **Engine changes this round (#24):**
  - **Special-token predictions no longer slip.** Before, pure noise put 0.36–0.41 on ALWAYS-UNSAT on C E5 SAT with a given state.
  - **BCa intervals** are reported next to the percentile ones.
  - **`--units` is `;`-separated.** The comma split had silently skipped a unit.
- **#22 added ALWAYS-UNSAT to C E1 and C E2 SAT.** That makes `null_always` pass there: a constant-UNSAT responder now goes to ALWAYS-UNSAT instead of RO-GREEDY. It also makes `null_q` fail there: pure noise loads about 0.4/√N on ALWAYS-UNSAT, and q = 1 sits on the boundary.
- **Misspecification:** fitting uniform slips to near-miss data raises the worst bias to 0.03–0.14 (against 0.01–0.09 for the matched fit), and on 7 of 12 witness units the bias lands on q.
- **Off-zoo:** a withheld procedure's 0.3 goes to zoo members (0.13–0.92), not to q (0.00–0.11). So a small π_0 does not show the zoo is complete.
- **Censoring:** excluding truncated runs biases the frequently truncated member by −0.06 to −0.23. The token-model hook brings that back to within ±0.045 on all but two units.

## How to run it

```bash
OMP_NUM_THREADS=1 python -m reasoning_heuristics.identify.recovery run --items data/items/dev --label dev \
    --reps 40 --boot 100 --single-reps 10 --feature-reps 16 --feature-boot 30 --offzoo-reps 8 \
    --workers 8 --out data/recovery/dev.json
python -m reasoning_heuristics.identify.recovery report data/recovery/dev.json data/recovery/pc*.json
```

- **Each item set is one command.** The harness isn't tuned to the committed items, so it reruns as-is on regenerated sets.
- **Each result file records:**
  - the command;
  - the git SHA, and whether the tree was dirty;
  - the sha256 of every item file it read;
  - the planted triple and the identifiability analysis of every unit.
- **`--units`** takes unit names separated by `;`, since names contain commas. A name that matches no unit stops the run.
- **`merge`** folds a rerun of some units into a result file and keeps both provenances. That is how the units the no-slip change touches, and C E1 / C E2 SAT after #22, were rerun.
- **`report`** prints every table on this page, including the closing one.
- **Threads:** workers are processes, so set `OMP_NUM_THREADS=1`.

**Larger item sets for the sweep** are generated into a scratch directory, never into `data/items`. Generation is deterministic in code, tier, seed and parameters.

```bash
python -m reasoning_heuristics.generate --vertical V --eval E --tier dev --seed 1 --per-cell N --out-dir DIR
python -m reasoning_heuristics.identify.recovery run --items DIR/dev --label pcN --scenarios mix,null_q,null_always \
    --reps 100 --boot 100 --workers 4 --out data/recovery/pcN.json
```

## What is tested

**The engine** (`src/reasoning_heuristics/identify/`). Per fit unit (one eval × one domain; the response side adds model × condition), it fits P(y | x) = Σ_h π_h P(y | h, x) + π_0 q(y | x) by EM. Its parts:

- **Likelihoods** are built from `predictions` + `instance` + the raw answer, not from the items' `disconfirms` tables. Set-valued members are rebuilt by validity: EXACT is uniform over every valid solution of the stated instance, and TT[exact] over the valid solutions under the textbook rule.
- **Near-miss slips** are the pre-registered noise model.
  - A deterministic or set-valued member gives its answer with probability 1 − ε. Otherwise D ~ truncated geometric(ρ) positions change: variables flipped, items or literals toggled, vertices recoloured up to renaming, or another decision or option. The kernel is an exact pmf over the answer space.
  - ε and ρ are estimated.
  - A prediction that is a special token (UNSAT, IMPOSSIBLE, X) does not slip: it has no near misses. Were it to slip to "q without the token", a member predicting the token on every item would equal q at ε = 0.5.
  - Distributional members are complete noise models and are used as stored.
- **q, "none of the above"**, is a uniformly random answer. With probability ½ it is instead the special token, on channels that have one.
  - **C E3's bit channel is {same, different, IMPOSSIBLE}**, with q uniform over the three. The U-arm format admits IMPOSSIBLE, and FF-OUT and LF predict it on every U-REV item.
  - The items' stored outcome classes and the scorer's `outcome_class` lump IMPOSSIBLE with "other" on that channel.
- **Ties** are merged. Members with identical predictions on every item of the unit form one group, which has one weight. A group identical to q is folded into the unexplained mass.
- **Linear dependencies** are found from the rank and null space of the (item, outcome) × (groups + q) matrix (`engine.identifiability`).
  - Every member of a dependency is reported as not identified, with the range of values consistent with the fit (π ≥ 0) and the identified combinations.
  - On finite channels a slip is a mixture with q, so there ε is held at 0 and π_0 includes slips.
- **Availability:** a member with no prediction on an item drops out there, and the other weights are renormalised (a Luce choice model).
- **95% intervals** come from a cluster bootstrap that resamples together the items sharing a base or a counterfactual set.
  - The percentile interval is the primary one.
  - The BCa interval (bias-corrected and accelerated, Efron 1987), with acceleration from a leave-one-cluster-out jackknife, is computed on the same fits and reported next to it.

**The fake models** (`identify/fake.py`) answer the real items through the same likelihood model the fit uses. For the misspecification check they use the other model.

| Scenario | Planted | Gate truth |
|---|---|---|
| `single` | 100% one member, each tie group in turn (0.95 + 0.05 q for a group missing on some items) | that group |
| `mix` | 0.6 / 0.3 / 0.1 on the planted triple | the three weights |
| `mix_uniform_slips` | the same, with slips uniform over the other candidate answers, fitted with that model | the three weights |
| `feature` | 0.7 / 0.2 / 0.1 at one level of an item feature, 0.2 / 0.7 / 0.1 at the other; fitted with π = softmax(β·φ(x)) | the weights at each level |
| `null_q` | every answer from q | π_0 = 1 |
| `null_always` | one fixed answer on every item (first decision value, option A, UNSAT or IMPOSSIBLE, the empty set, one colour everywhere), no slips | the group giving that answer on every item if there is one, else π_0 = 1 |
| `off_zoo` | 0.7 on the triple's first member, 0.3 on a group the fit withholds (each group in turn) | where the withheld 0.3 goes |
| `clustered` | the `mix` weights, one member per cluster (all variants of a base answered alike) | the three weights |
| `truncated` | the `mix` weights, runs truncated at 0.4 for the 0.6 member and 0.05 otherwise; fitted with truncated runs excluded, and with the true rates as the token model | the three weights |

- **The planted triple** is chosen by a rule, never by hand:
  - h1 is the first deterministic group of the largest family;
  - h2 is h1's nearest competitor, the group with the fewest separating items (more than zero), so the mixture tests the hardest split h1 has;
  - h3 is the group of another family that is most separated from both;
  - members of a linear dependency are avoided when three others remain.
  - The rule runs on each item set separately. A pair tied on every item of one set is a single group there, but in a set where one item separates it, it becomes h1 and h2.
- **Slips** are planted at ε = 0.1, ρ = 0.3 on witness channels, and not at all on finite channels.
- **The feature** is the first factor of the cell label that takes two values in the unit.

**The gates**, per unit and scenario, over replicates:

- |mean π̂ − π| ≤ 0.05 for every identified quantity, planted or absent, the unexplained mass included;
- the 95% interval contains the planted value in ≥ 90% of replicates, for every planted quantity;
- the median width over planted quantities and replicates is ≤ 0.2.

**What a pass covers.** A pass says two things:

1. The three planted weights are recovered within the gates.
2. No identified quantity is biased by more than 0.05. The identified quantities are each tie group's weight, each identified combination, and π_0.

It says nothing about:

- how weight splits among the members of a tie group, which share one weight;
- the members of a linear dependency, which are not identified;
- any near-tied pair other than h1 and its nearest competitor.

The closing table lists, for each unit that passes, the groups it reports as one weight.

A scenario that plants weight on a member identified only in combination is **not testable on that unit**. It is listed separately, neither passed nor failed. The gated scenarios are `single`, `mix`, `mix_uniform_slips`, `feature`, `null_q` and `null_always`. `off_zoo` has its own criterion (A/H §5.3 P6: less than 0.2 of the withheld mass on any single member). `clustered`, `truncated` and the misspecification fits are checks.

## Results at dev size (5 items per cell)

Item set `data/items/dev`, git 2c9a5fa20a; AH_E5/COL, AH_E5/ENT, C_E5/3-SAT, C_E5/3-SAT (partial assignment given), C_E5/colouring (k=3) rerun at git 7d87ac657b; C_E5/colouring (k=3, partial colouring given) rerun at git 06e34f4ba0; C_E1/3-SAT, C_E2/3-SAT rerun at git e3df332fc7; AH_E1/COL, AH_E1/ENT, AH_E1/SAT, AH_E2/COL, AH_E2/ENT, AH_E2/SAT, AH_E5/KNAP, B4C4_E1/entailment, B4C4_E2/entailment, C_E1/colouring, C_E3/colouring (gadget), C_E5/propositional entailment rerun at git 2c9a5fa20a; 40 replicates × 100 bootstrap draws (10 per single member).

| Unit | items | clusters | single | mix | mix, uniform slips | feature | null q | null ALWAYS | all |
|---|---|---|---|---|---|---|---|---|---|
| AH_E1/COL | 20 | 10 | fail 3/8, 2 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E1/ENT | 20 | 10 | fail 3/12, 3 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage) | not testable | not testable | fail (2 not testable) |
| AH_E1/SAT | 30 | 15 | fail 5/10, 2 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E2/COL | 40 | 10 | fail 2/8, 3 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E2/ENT | 40 | 5 | fail 3/12, 2 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E2/SAT | 40 | 10 | fail 6/9, 2 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E5/COL | 20 | 5 | PASS | fail (coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | PASS | fail (coverage) | fail |
| AH_E5/ENT | 20 | 5 | PASS | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | PASS | PASS | fail |
| AH_E5/KNAP | 20 | 5 | fail 4/6 | – | – | – | PASS | PASS | fail |
| AH_E5/SAT | 25 | 5 | PASS | fail (coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | PASS | PASS | fail |
| B4C4_E1/entailment | 140 | 20 | fail 5/17 | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage) | fail (bias, coverage, width) | fail (bias, coverage) | fail |
| B4C4_E2/entailment | 240 | 25 | PASS, 9 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| C_E1/3-SAT | 30 | 5 | fail 2/11 | fail (bias, coverage, width) | fail (coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | PASS | fail |
| C_E1/colouring | 30 | 5 | fail 2/12 | fail (coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | PASS | fail (bias, coverage) | fail |
| C_E2/3-SAT | 50 | 10 | fail 1/9 | fail (coverage) | fail (coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | PASS | fail |
| C_E2/colouring | 75 | 15 | fail 2/9 | fail (coverage) | fail (coverage) | fail (coverage, width) | PASS | PASS | fail |
| C_E2/knapsack | 75 | 15 | PASS | fail (coverage, width) | fail (bias, coverage, width) | fail (coverage, width) | PASS | PASS | fail |
| C_E3/colouring (gadget) | 270 | 30 | fail 10/11, 8 not testable | not testable | n/a (finite) | not testable | fail (bias, coverage, width) | fail (bias, coverage) | fail (2 not testable) |
| C_E5/3-SAT | 15 | 5 | fail 1/11 | fail (coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | PASS | fail |
| C_E5/3-SAT (partial assignment given) | 15 | 5 | fail 2/8 | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | PASS | fail |
| C_E5/colouring (k=3) | 25 | 5 | fail 1/12 | fail (bias, coverage) | fail (bias, coverage) | fail (bias, coverage) | fail (bias, width) | PASS | fail |
| C_E5/colouring (k=3, partial colouring given) | 10 | 5 | fail 1/6 | fail (bias, coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | PASS | fail |
| C_E5/propositional entailment | 20 | 5 | fail 3/8, 3 not testable | fail (bias, coverage) | n/a (finite) | fail (bias, coverage) | not testable | not testable | fail (2 not testable) |

**The 60/30/10 mixture in detail** (worst quantity for each gate):

| Unit | triple (0.6 / 0.3 / 0.1) | max \|bias\| | on | min coverage | on | median width | BCa: min coverage / median width |
|---|---|---|---|---|---|---|---|
| AH_E1/COL | A2 DENSITY-U / B1 DROP-CONSTRAINT(last 3) / H SAMPLE-8 | 0.071 | H SAMPLE-8 | 0.575 | H SAMPLE-8 | 0.616 | 0.650 / 0.597 |
| AH_E1/ENT | A2 FREQ / D case-split (b = 4) / H SAMPLE-8 | 0.091 | H SAMPLE-8 | 0.550 | H SAMPLE-8 | 0.667 | 0.625 / 0.852 |
| AH_E1/SAT | A2 LENGTH-M / B1 UP-3 / F WALK-200 | 0.085 | A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY + 0.5 × q | 0.750 | A2 LENGTH-M | 0.461 | 0.775 / 0.485 |
| AH_E2/COL | A2 DENSITY-D / A2 LENGTH-M / NOISY-EXACT | 0.100 | NOISY-EXACT | 0.025 | NOISY-EXACT | 0.453 | 0.050 / 0.446 |
| AH_E2/ENT | A2 ATMOSPHERE / A2 PRIMACY / H SAMPLE-8 | 0.099 | H SAMPLE-8 | 0.200 | H SAMPLE-8 | 0.249 | 0.225 / 0.264 |
| AH_E2/SAT | A2 DENSITY-D / A2 LENGTH-M / F WALK-200 | 0.064 | exact | 0.525 | F WALK-200 | 0.435 | 0.575 / 0.432 |
| AH_E5/COL | A3 TT[FIRST-FIT] / C1 FIRST-FIT (stated rule) / B1 DROP-CONSTRAINT(last 3) | 0.048 | C1 FIRST-FIT (stated rule) | 0.675 | B1 DROP-CONSTRAINT(last 3) | 0.367 | 0.675 / 0.391 |
| AH_E5/ENT | A1 NONE / A3 TT[exact] / B4 FIRST | 0.064 | exact | 0.575 | B4 FIRST | 0.306 | 0.625 / 0.339 |
| AH_E5/KNAP | (no triple) ||||||
| AH_E5/SAT | C0 POLARITY / C1 GREEDY / A3 TT[exact] | 0.011 | C0 POLARITY | 0.625 | A3 TT[exact] | 0.240 | 0.700 / 0.244 |
| B4C4_E1/entailment | BICOND / ONL(2) / NOISY-EXACT | 0.100 | NOISY-EXACT | 0.000 | NOISY-EXACT | 0.332 | 0.000 / 0.333 |
| B4C4_E2/entailment | AFFIRM / C1-GREEDY / CW-MIN | 0.060 | CW-MIN | 0.400 | CW-MIN | 0.236 | 0.425 / 0.236 |
| C_E1/3-SAT | DPLL-INDEX (D, T first) / DPLL-MENTION (D, T first) / ALWAYS-UNSAT (A1 give-up) | 0.052 | UC-DET (C2) | 0.725 | ALWAYS-UNSAT (A1 give-up) | 0.241 | 0.650 / 0.238 |
| C_E1/colouring | FF-LABEL / DPLL-LABEL (D) / DSATUR | 0.041 | DSATUR-LABEL | 0.800 | DSATUR | 0.224 | 0.850 / 0.226 |
| C_E2/3-SAT | GUC-DET (C2) / ALWAYS-UNSAT (A1 give-up) / POLARITY (C0) | 0.017 | GUC-DET (C2) | 0.525 | GUC-DET (C2) | 0.193 | 0.525 / 0.191 |
| C_E2/colouring | FF-LABEL / DPLL-LIST (D) / EXACT | 0.017 | FF-LABEL | 0.875 | EXACT | 0.187 | 0.900 / 0.187 |
| C_E2/knapsack | DIFF / RATIO-SKIP / EXACT | 0.011 | DIFF | 0.875 | RATIO-SKIP | 0.248 | 0.925 / 0.252 |
| C_E3/colouring (gadget) | DPLL-LIST (D, k=3) / DSATUR (C2, label ties) / LF (C1 static, label ties) | not testable: planted weight on DPLL-LIST (D, k=3) = FF-LIST (C1 seq), identified only in combination: DPLL-LIST (D, k=3) = FF-LIST (C1 seq), LOCAL-3-LIST (const proxy, reaches the target), LOCAL-4-LIST (const proxy, reaches the target), LOCAL-5-LIST (const proxy, reaches the target), LOCAL-6-LIST (const proxy, reaches the target), LOCAL-8-LIST (const proxy, reaches the target), LOCAL-10-LIST (const proxy, reaches the target) span only 6 directions (LOCAL-10-LIST (const proxy, reaches the target) = 1 × DPLL-LIST (D, k=3) = FF-LIST (C1 seq) + -1 × LOCAL-3-LIST (const proxy, reaches the target) + -1 × LOCAL-4-LIST (const proxy, reaches the target) + -1 × LOCAL-5-LIST (const proxy, reaches the target) + -1 × LOCAL-6-LIST (const proxy, reaches the target) + -1 × LOCAL-8-LIST (const proxy, reaches the target)): their weights are identified only up to this combination ||||||
| C_E5/3-SAT | GUC-DET (C2) / SC-DET (C2) / DPLL-MOMS-POLARITY (D) | 0.034 | GUC-DET (C2) | 0.625 | DPLL-MOMS-POLARITY (D) | 0.443 | 0.600 / 0.467 |
| C_E5/3-SAT (partial assignment given) | GREEDY-MENTION from state (C1) / GREEDY-MENTION-ABORT from state (C1) / POLARITY (C0, ignores state) | 0.054 | GREEDY-MENTION-ABORT from state (C1) | 0.700 | POLARITY (C0, ignores state) | 0.400 | 0.750 / 0.396 |
| C_E5/colouring (k=3) | FF-3-EDGE-MENTION-ABORT (C1 variant) / ALWAYS-IMPOSSIBLE (A1 give-up) / DROP-LAST-3-EDGES + exact (B1) | 0.090 | FF-3-EDGE-MENTION-ABORT (C1 variant) | 0.025 | ALWAYS-IMPOSSIBLE (A1 give-up) = PHANTOM-ADJACENT (B4) | 0.159 | 0.025 / 0.160 |
| C_E5/colouring (k=3, partial colouring given) | ALWAYS-IMPOSSIBLE (A1 give-up) / DPLL-LIST from state (D) / FF-3-LIST from state (C1, INFEAS) | 0.053 | DPLL-LIST from state (D) = DSATUR-3 from state (C2) | 0.575 | FF-3-LIST from state (C1, INFEAS) | 0.541 | 0.550 / 0.493 |
| C_E5/propositional entailment | FIRST (B4) / ETR-1p (R1) / SAMPLE-3 (H) | 0.125 | NONE (A1 give-up: does not follow) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound) + 0.5 × q + 0.961 × NOISY-EXACT | 0.050 | FIRST (B4) | 0.133 | 0.050 / 0.125 |

**Single members that fail** (the first gate each fails on, and its worst quantity):

- **AH_E1/COL**: H SAMPLE-8 (bias, coverage; bias 0.50 on H SAMPLE-8); NOISY-EXACT (bias, coverage, width; bias 0.98 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage; bias 0.77 on PERCEPTION-NOISE)
- **AH_E1/ENT**: H SAMPLE-8 (bias, coverage; bias 1.00 on H SAMPLE-8); NOISY-EXACT (bias, coverage; bias 1.00 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage; bias 1.00 on PERCEPTION-NOISE)
- **AH_E1/SAT**: F WALK-200 (bias, coverage, width; bias 0.34 on F WALK-200); H SAMPLE-8 (bias, coverage; bias 0.91 on H SAMPLE-8); NOISY-EXACT-READ (bias, coverage; bias 1.00 on NOISY-EXACT-READ); NOISY-EXACT-STEP (bias, coverage; bias 0.95 on NOISY-EXACT-STEP); PERCEPTION-NOISE (bias, coverage, width; bias 0.39 on PERCEPTION-NOISE)
- **AH_E2/COL**: NOISY-EXACT (bias, coverage, width; bias 0.91 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage, width; bias 0.46 on PERCEPTION-NOISE)
- **AH_E2/ENT**: H SAMPLE-8 (bias, coverage, width; bias 0.36 on H SAMPLE-8); NOISY-EXACT (bias, coverage; bias 1.00 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage; bias 0.91 on PERCEPTION-NOISE)
- **AH_E2/SAT**: C1 GREEDY (width; bias 0.00 on C1 GREEDY); F WALK-200 (bias, coverage, width; bias 0.10 on F WALK-200); H SAMPLE-8 (bias, coverage; bias 0.50 on H SAMPLE-8); NOISY-EXACT-READ (bias, coverage, width; bias 0.90 on NOISY-EXACT-READ); NOISY-EXACT-STEP (bias, coverage, width; bias 0.82 on NOISY-EXACT-STEP); PERCEPTION-NOISE (bias, coverage, width; bias 0.54 on PERCEPTION-NOISE)
- **AH_E5/KNAP**: C1 INPUT-FIT (coverage; bias 0.01 on q); C1 LARGEST-FIT (coverage; bias 0.02 on q); C1 RATIO-SKIP (coverage; bias 0.03 on q); C1 VALUE (coverage; bias 0.02 on q)
- **B4C4_E1/entailment**: AFFIRM = ALWAYS-YES (coverage; bias 0.02 on q); C1-GREEDY (bias, coverage; bias 0.24 on C1-GREEDY); NOISY-EXACT (bias, coverage; bias 0.91 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage, width; bias 0.76 on PERCEPTION-NOISE); SAMPLE-3 (coverage; bias 0.04 on q)
- **C_E1/3-SAT**: GREEDY-OUT (AR) (coverage; bias 0.01 on GREEDY-OUT (AR)); RO-GREEDY (C3) (bias, coverage, width; bias 0.10 on RO-GREEDY (C3))
- **C_E1/colouring**: FF-OUT (AR) (coverage; bias 0.02 on q); NOISY-EXACT (bias, coverage, width; bias 0.68 on NOISY-EXACT)
- **C_E2/3-SAT**: RO-GREEDY (C3) (bias, coverage, width; bias 0.19 on RO-GREEDY (C3))
- **C_E2/colouring**: NOISY-EXACT (bias, coverage, width; bias 0.45 on NOISY-EXACT); RO-FF (C3) (coverage; bias 0.02 on RO-FF (C3))
- **C_E3/colouring (gadget)**: DSATUR (C2, label ties) (bias, coverage; bias 0.11 on DSATUR (C2, label ties)); EXACT (coverage; bias 0.04 on EXACT); FF-OUT (AR, answer order) (bias, coverage; bias 0.06 on FF-OUT (AR, answer order)); LF (C1 static, label ties) (bias, coverage; bias 0.12 on LF (C1 static, label ties)); LOCAL-2-LIST (const proxy, one round short) (coverage; bias 0.02 on LOCAL-2-LIST (const proxy, one round short)); ANSWER-1 (A1 default; = LOCAL-0) (coverage; bias 0.02 on ANSWER-1 (A1 default; = LOCAL-0)); LOCAL-3-LIST (const proxy, one round short) (coverage; bias 0.01 on q); LOCAL-4-LIST (const proxy, one round short) (coverage; bias 0.02 on LOCAL-4-LIST (const proxy, one round short)); LOCAL-7-LIST (const proxy, one round short) (coverage; bias 0.03 on q); LOCAL-9-LIST (const proxy, one round short) (coverage; bias 0.02 on LOCAL-9-LIST (const proxy, one round short))
- **C_E5/3-SAT**: RO-GREEDY (C3) (bias, coverage, width; bias 0.50 on RO-GREEDY (C3))
- **C_E5/3-SAT (partial assignment given)**: DPLL from state (D) (bias; bias 0.07 on DPLL from state (D)); EXACT (bias, width; bias 0.06 on EXACT)
- **C_E5/colouring (k=3)**: NOISY-EXACT (bias, coverage, width; bias 0.49 on NOISY-EXACT)
- **C_E5/colouring (k=3, partial colouring given)**: EXACT (bias, width; bias 0.14 on EXACT)
- **C_E5/propositional entailment**: ETR-1p (R1) = ETR-default (R1) (width; bias 0.00 on ETR-1p (R1) = ETR-default (R1)); FIRST (B4) (width; bias 0.00 on FIRST (B4)); SAMPLE-3 (H) (bias, coverage; bias 0.82 on SAMPLE-3 (H))

**Linear dependencies** (`engine.identifiability`: rank of the (item, outcome) × (groups + q) matrix; witness channels on sampled outcomes). Every member of a dependency is identified only in combination; the fits report the identified combinations shown (one basis of them):

- **AH_E1/COL** (rank 10 of 11): `q = 0.5 × A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT + 0.5 × A1 ALWAYS-POSSIBLE = A2 DENSITY-D`. Not identified on their own: A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT, A1 ALWAYS-POSSIBLE = A2 DENSITY-D, q. Identified combinations reported: `A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT + 0.5 × q`; `A1 ALWAYS-POSSIBLE = A2 DENSITY-D + 0.5 × q`.
- **AH_E1/ENT** (rank 15 of 16): `q = 0.5 × A1 ALWAYS-YES + 0.5 × A1 NONE = A2 ATMOSPHERE = A2 DENSITY`. Not identified on their own: A1 ALWAYS-YES, A1 NONE = A2 ATMOSPHERE = A2 DENSITY, q. Identified combinations reported: `A1 ALWAYS-YES + 0.5 × q`; `A1 NONE = A2 ATMOSPHERE = A2 DENSITY + 0.5 × q`.
- **AH_E1/SAT** (rank 12 of 13): `q = 0.5 × A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY + 0.5 × A1 ALWAYS-UNSAT = C1 GREEDY`. Not identified on their own: A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY, A1 ALWAYS-UNSAT = C1 GREEDY, q. Identified combinations reported: `A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY + 0.5 × q`; `A1 ALWAYS-UNSAT = C1 GREEDY + 0.5 × q`.
- **AH_E2/COL** (rank 10 of 12): `q = 0.5 × A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT + 0.5 × A1 ALWAYS-POSSIBLE`; `H SAMPLE-8 = 1 × A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT`. Not identified on their own: A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT, A1 ALWAYS-POSSIBLE, H SAMPLE-8, q. Identified combinations reported: `A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT + 0.5 × q + 1 × H SAMPLE-8`; `A1 ALWAYS-POSSIBLE + 0.5 × q`.
- **AH_E2/ENT** (rank 14 of 15): `q = 0.5 × A1 ALWAYS-YES + 0.5 × A1 NONE = A2 DENSITY = B4 FIRST`. Not identified on their own: A1 ALWAYS-YES, A1 NONE = A2 DENSITY = B4 FIRST, q. Identified combinations reported: `A1 ALWAYS-YES + 0.5 × q`; `A1 NONE = A2 DENSITY = B4 FIRST + 0.5 × q`.
- **AH_E2/SAT** (rank 11 of 12): `q = 0.5 × A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY + 0.5 × A1 ALWAYS-UNSAT = C2 UC = D DPLL-b = D DPLL-b+PL`. Not identified on their own: A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY, A1 ALWAYS-UNSAT = C2 UC = D DPLL-b = D DPLL-b+PL, q. Identified combinations reported: `A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY + 0.5 × q`; `A1 ALWAYS-UNSAT = C2 UC = D DPLL-b = D DPLL-b+PL + 0.5 × q`.
- **B4C4_E2/entailment** (rank 15 of 20): `q = 0.5 × ALWAYS-YES = BICOND + 0.5 × NONE`; `SAMPLE-3 = 0.125 × ALWAYS-YES = BICOND + 0.875 × ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1`; `PERCEPTION-NOISE = 0.93 × ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 + 0.0699 × NONE`; `NOISY-EXACT = 0.0149 × ALWAYS-YES = BICOND + 0.97 × ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 + 0.0149 × NONE`; `ETR-1p, ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1, MM-G, MM-S1 = MM-elim span only 3 directions (MM-S1 = MM-elim = 1 × ETR-1p + -1 × ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 + 1 × MM-G): their weights are identified only up to this combination`. Not identified on their own: ALWAYS-YES = BICOND, ETR-1p, ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1, MM-G, MM-S1 = MM-elim, NOISY-EXACT, NONE, PERCEPTION-NOISE, SAMPLE-3, q. Identified combinations reported: `ALWAYS-YES = BICOND + 0.5 × q + 0.125 × SAMPLE-3 + 0.0149 × NOISY-EXACT`; `ETR-1p + 1 × MM-S1 = MM-elim`; `ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 + 0.875 × SAMPLE-3 + 0.93 × PERCEPTION-NOISE + 0.97 × NOISY-EXACT + -1 × MM-S1 = MM-elim`; `MM-G + 1 × MM-S1 = MM-elim`; `NONE + 0.5 × q + 0.0699 × PERCEPTION-NOISE + 0.0149 × NOISY-EXACT`.
- **C_E3/colouring (gadget)** (rank 18 of 20): `DPLL-LIST (D, k=3) = FF-LIST (C1 seq), LOCAL-3-LIST (const proxy, reaches the target), LOCAL-4-LIST (const proxy, reaches the target), LOCAL-5-LIST (const proxy, reaches the target), LOCAL-6-LIST (const proxy, reaches the target), LOCAL-8-LIST (const proxy, reaches the target), LOCAL-10-LIST (const proxy, reaches the target) span only 6 directions (LOCAL-10-LIST (const proxy, reaches the target) = 1 × DPLL-LIST (D, k=3) = FF-LIST (C1 seq) + -1 × LOCAL-3-LIST (const proxy, reaches the target) + -1 × LOCAL-4-LIST (const proxy, reaches the target) + -1 × LOCAL-5-LIST (const proxy, reaches the target) + -1 × LOCAL-6-LIST (const proxy, reaches the target) + -1 × LOCAL-8-LIST (const proxy, reaches the target)): their weights are identified only up to this combination`; `RANDOM (H) = 0`. Not identified on their own: DPLL-LIST (D, k=3) = FF-LIST (C1 seq), LOCAL-3-LIST (const proxy, reaches the target), RANDOM (H), LOCAL-4-LIST (const proxy, reaches the target), LOCAL-5-LIST (const proxy, reaches the target), LOCAL-6-LIST (const proxy, reaches the target), LOCAL-8-LIST (const proxy, reaches the target), LOCAL-10-LIST (const proxy, reaches the target). Identified combinations reported: `DPLL-LIST (D, k=3) = FF-LIST (C1 seq) + 1 × LOCAL-10-LIST (const proxy, reaches the target)`; `LOCAL-3-LIST (const proxy, reaches the target) + -1 × LOCAL-10-LIST (const proxy, reaches the target)`; `LOCAL-4-LIST (const proxy, reaches the target) + -1 × LOCAL-10-LIST (const proxy, reaches the target)`; `LOCAL-5-LIST (const proxy, reaches the target) + -1 × LOCAL-10-LIST (const proxy, reaches the target)`; `LOCAL-6-LIST (const proxy, reaches the target) + -1 × LOCAL-10-LIST (const proxy, reaches the target)`; `LOCAL-8-LIST (const proxy, reaches the target) + -1 × LOCAL-10-LIST (const proxy, reaches the target)`.
- **C_E5/propositional entailment** (rank 10 of 12): `q = 0.5 × ALWAYS-YES (A1) + 0.5 × NONE (A1 give-up: does not follow) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound)`; `NOISY-EXACT = 0.0386 × ALWAYS-YES (A1) + 0.961 × NONE (A1 give-up: does not follow) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound)`. Not identified on their own: ALWAYS-YES (A1), NOISY-EXACT, NONE (A1 give-up: does not follow) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound), q. Identified combinations reported: `ALWAYS-YES (A1) + 0.5 × q + 0.0386 × NOISY-EXACT`; `NONE (A1 give-up: does not follow) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound) + 0.5 × q + 0.961 × NOISY-EXACT`.
- Full rank: AH_E5/COL, AH_E5/ENT, AH_E5/KNAP, AH_E5/SAT, B4C4_E1/entailment, C_E1/3-SAT, C_E1/colouring, C_E2/3-SAT, C_E2/colouring, C_E2/knapsack, C_E5/3-SAT, C_E5/3-SAT (partial assignment given), C_E5/colouring (k=3), C_E5/colouring (k=3, partial colouring given).

**Identifiability diagnostics** (finite channels: rank of the (item, value) × (groups + q) design; A/H §5.3 asks for σ_min/σ_max ≥ 0.05) and the least-separated pairs:

| Unit | rank / columns | σ ratio | weakest direction | least-separated pair (items) |
|---|---|---|---|---|
| AH_E1/COL | 10 / 11 | 0.0 | q, A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT, A1 ALWAYS-POSSIBLE = A2 DENSITY-D | A1 ALWAYS-POSSIBLE = A2 DENSITY-D vs A2 DENSITY-U (2) |
| AH_E1/ENT | 15 / 16 | 0.0 | q, A1 NONE = A2 ATMOSPHERE = A2 DENSITY, A1 ALWAYS-YES | B1 UP-1 vs B1 UP-2 = B1 UP-3 (1) |
| AH_E1/SAT | 12 / 13 | 0.0 | q, A1 ALWAYS-UNSAT = C1 GREEDY, A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY | A1 ALWAYS-UNSAT = C1 GREEDY vs C2 UC (3) |
| AH_E2/COL | 11 / 12 | 0.0 | q, A1 ALWAYS-POSSIBLE, A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT | A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT vs B4 ADD-CONSTRAINT(adjacent) (2) |
| AH_E2/ENT | 14 / 15 | 0.0 | q, A1 NONE = A2 DENSITY = B4 FIRST, A1 ALWAYS-YES | A1 NONE = A2 DENSITY = B4 FIRST vs A2 RECENCY (2) |
| AH_E2/SAT | 11 / 12 | 0.0 | q, A1 ALWAYS-UNSAT = C2 UC = D DPLL-b = D DPLL-b+PL, A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY | A1 ALWAYS-UNSAT = C2 UC = D DPLL-b = D DPLL-b+PL vs C1 GREEDY (1) |
| AH_E5/COL | (witness channel) | | | B1 DROP-CONSTRAINT(last 3) vs C2 DSATUR (stated rule) (8) |
| AH_E5/ENT | (witness channel) | | | B4 FIRST vs exact (8) |
| AH_E5/KNAP | (witness channel) | | | C1 RATIO-SKIP vs C1 VALUE (6) |
| AH_E5/SAT | (witness channel) | | | A3 TT[exact] vs exact (15) |
| B4C4_E1/entailment | 18 / 18 | 0.0004 | BICOND = CW-COMP = CW-MIN = EXACT = MM-G = MM-S1 = ONL(4), NOISY-EXACT | FIRST vs ONL(1) = ONL(1)-strict (5) |
| B4C4_E2/entailment | 15 / 20 | 0.0 | ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1, PERCEPTION-NOISE, MM-G, MM-S1 = MM-elim | MM-G vs ONL(1) = ONL(1)-strict (10) |
| C_E1/3-SAT | (witness channel) | | | DPLL-MENTION (D, T first) vs UC-DET (C2) (14) |
| C_E1/colouring | (witness channel) | | | DSATUR vs DSATUR-LABEL (2) |
| C_E2/3-SAT | (witness channel) | | | ALWAYS-UNSAT (A1 give-up) vs SC-DET (C2) (2) |
| C_E2/colouring | (witness channel) | | | DSATUR vs DSATUR-LABEL (45) |
| C_E2/knapsack | (witness channel) | | | DIFF vs RATIO-SKIP (38) |
| C_E3/colouring (gadget) | 18 / 20 | 0.0 | RANDOM (H), DPLL-LIST (D, k=3) = FF-LIST (C1 seq) | LOCAL-2-LIST (const proxy, one round short) vs LOCAL-3-LIST (const proxy, reaches the target) (21) |
| C_E5/3-SAT | (witness channel) | | | ALWAYS-UNSAT (A1 give-up) vs GREEDY-MENTION-ABORT (C1) (5) |
| C_E5/3-SAT (partial assignment given) | (witness channel) | | | DPLL from state (D) vs UC-DET from state (C2) (1) |
| C_E5/colouring (k=3) | (witness channel) | | | ALWAYS-IMPOSSIBLE (A1 give-up) = PHANTOM-ADJACENT (B4) vs FF-3-EDGE-MENTION-ABORT (C1 variant) (2) |
| C_E5/colouring (k=3, partial colouring given) | (witness channel) | | | ALWAYS-IMPOSSIBLE (A1 give-up) = FF-3-LIST from state (C1, ABORT) vs DPLL-LIST from state (D) = DSATUR-3 from state (C2) (5) |
| C_E5/propositional entailment | 10 / 12 | 0.0 | NONE (A1 give-up: does not follow) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound), q, ALWAYS-YES (A1), NOISY-EXACT | ETR-1p (R1) = ETR-default (R1) vs FIRST (B4) (2) |

## Items per cell

The sweep reruns `mix`, `null_q` and `null_always` on dev-tier item sets at 10, 20 and 40 items per cell, with 100 replicates and 100 bootstrap draws. For each unit and size, the table gives the 60/30/10 mixture's worst bias (b), its smallest per-weight coverage (c) and its median width (w), with the BCa interval's coverage and width beside them, and then the `null_q` verdict.

| Unit | dev (items/cell) | pc10 (items/cell) | pc20 (items/cell) | pc40 (items/cell) |
|---|---|---|---|---|
| AH_E1/COL | 5: mix fail (b 0.071, c 0.575, w 0.616; BCa c 0.650, w 0.597); q not testable | 10: mix fail (b 0.090, c 0.300, w 0.431; BCa c 0.470, w 0.431); q not testable | 20: mix fail (b 0.097, c 0.030, w 0.327; BCa c 0.050, w 0.327); q not testable | – |
| AH_E1/ENT | 5: mix fail (b 0.091, c 0.550, w 0.667; BCa c 0.625, w 0.852); q not testable | 10: mix fail (b 0.118, c 0.050, w 0.185; BCa c 0.090, w 0.204); q not testable | 20: mix fail (b 0.098, c 0.050, w 0.385; BCa c 0.060, w 0.395); q not testable | – |
| AH_E1/SAT | 5: mix fail (b 0.085, c 0.750, w 0.461; BCa c 0.775, w 0.485); q not testable | 10: mix fail (b 0.091, c 0.180, w 0.487; BCa c 0.280, w 0.475); q not testable | 20: mix fail (b 0.069, c 0.420, w 0.384; BCa c 0.630, w 0.382); q not testable | – |
| AH_E2/COL | 5: mix fail (b 0.100, c 0.025, w 0.453; BCa c 0.050, w 0.446); q not testable | 10: mix fail (b 0.100, c 0.010, w 0.389; BCa c 0.020, w 0.391); q not testable | 20: mix fail (b 0.098, c 0.030, w 0.278; BCa c 0.040, w 0.275); q not testable | – |
| AH_E2/ENT | 5: mix fail (b 0.099, c 0.200, w 0.249; BCa c 0.225, w 0.264); q not testable | 10: mix fail (b 0.084, c 0.230, w 0.266; BCa c 0.400, w 0.253); q not testable | 20: mix fail (b 0.075, c 0.480, w 0.211; BCa c 0.650, w 0.209); q not testable | – |
| AH_E2/SAT | 5: mix fail (b 0.064, c 0.525, w 0.435; BCa c 0.575, w 0.432); q not testable | 10: mix fail (b 0.063, c 0.550, w 0.374; BCa c 0.640, w 0.377); q not testable | 20: mix fail (b 0.077, c 0.440, w 0.195; BCa c 0.440, w 0.198); q not testable | – |
| AH_E5/COL | 5: mix fail (b 0.048, c 0.675, w 0.367; BCa c 0.675, w 0.391); q PASS | 10: mix fail (b 0.051, c 0.810, w 0.300; BCa c 0.840, w 0.300); q PASS | 20: mix fail (b 0.026, c 0.860, w 0.245; BCa c 0.900, w 0.239); q PASS | 40: mix PASS (b 0.013, c 0.900, w 0.177; BCa c 0.910, w 0.177); q PASS |
| AH_E5/ENT | 5: mix fail (b 0.064, c 0.575, w 0.306; BCa c 0.625, w 0.339); q PASS | 10: mix fail (b 0.034, c 0.800, w 0.237; BCa c 0.850, w 0.240); q PASS | 20: mix fail (b 0.028, c 0.810, w 0.181; BCa c 0.880, w 0.184); q PASS | 40: mix fail (b 0.022, c 0.870, w 0.137; BCa c 0.880, w 0.136); q PASS |
| AH_E5/KNAP | 5: mix –; q PASS | 10: mix –; q PASS | 20: mix –; q fail | 40: mix –; q fail |
| AH_E5/SAT | 5: mix fail (b 0.011, c 0.625, w 0.240; BCa c 0.700, w 0.244); q PASS | 10: mix fail (b 0.006, c 0.830, w 0.211; BCa c 0.840, w 0.213); q PASS | 20: mix PASS (b 0.003, c 0.900, w 0.157; BCa c 0.880, w 0.159); q PASS | 40: mix PASS (b 0.001, c 0.910, w 0.111; BCa c 0.890, w 0.111); q PASS |
| B4C4_E1/entailment | 5: mix fail (b 0.100, c 0.000, w 0.332; BCa c 0.000, w 0.333); q fail | – | – | – |
| B4C4_E2/entailment | 5: mix fail (b 0.060, c 0.400, w 0.236; BCa c 0.425, w 0.236); q not testable | – | – | – |
| C_E1/3-SAT | 5: mix fail (b 0.052, c 0.725, w 0.241; BCa c 0.650, w 0.238); q fail | 10: mix fail (b 0.024, c 0.840, w 0.203; BCa c 0.860, w 0.208); q fail | 20: mix fail (b 0.022, c 0.860, w 0.163; BCa c 0.920, w 0.163); q fail | 40: mix fail (b 0.016, c 0.790, w 0.115; BCa c 0.900, w 0.113); q fail |
| C_E1/colouring | 5: mix fail (b 0.041, c 0.800, w 0.224; BCa c 0.850, w 0.226); q PASS | 10: mix fail (b 0.013, c 0.800, w 0.203; BCa c 0.840, w 0.207); q PASS | 20: mix fail (b 0.010, c 0.880, w 0.168; BCa c 0.910, w 0.169); q PASS | 40: mix fail (b 0.005, c 0.870, w 0.133; BCa c 0.890, w 0.134); q PASS |
| C_E2/3-SAT | 5: mix fail (b 0.017, c 0.525, w 0.193; BCa c 0.525, w 0.191); q fail | 10: mix fail (b 0.108, c 0.000, w 0.177; BCa c 0.000, w 0.175); q fail | 20: mix fail (b 0.011, c 0.880, w 0.277; BCa c 0.910, w 0.280); q fail | 40: mix PASS (b 0.001, c 0.920, w 0.176; BCa c 0.920, w 0.175); q fail |
| C_E2/colouring | 5: mix fail (b 0.017, c 0.875, w 0.187; BCa c 0.900, w 0.187); q PASS | 10: mix fail (b 0.007, c 0.880, w 0.141; BCa c 0.900, w 0.140); q PASS | 20: mix PASS (b 0.000, c 0.920, w 0.098; BCa c 0.930, w 0.099); q PASS | 40: mix PASS (b 0.001, c 0.900, w 0.070; BCa c 0.890, w 0.069); q PASS |
| C_E2/knapsack | 5: mix fail (b 0.011, c 0.875, w 0.248; BCa c 0.925, w 0.252); q PASS | 10: mix fail (b 0.009, c 0.880, w 0.197; BCa c 0.890, w 0.191); q fail | 20: mix PASS (b 0.010, c 0.920, w 0.152; BCa c 0.920, w 0.149); q fail | 40: mix PASS (b 0.003, c 0.910, w 0.112; BCa c 0.900, w 0.110); q fail |
| C_E3/colouring (gadget) | 5: mix not testable; q fail | – | – | – |
| C_E5/3-SAT | 5: mix fail (b 0.034, c 0.625, w 0.443; BCa c 0.600, w 0.467); q fail | 10: mix fail (b 0.014, c 0.660, w 0.385; BCa c 0.740, w 0.402); q fail | 20: mix fail (b 0.008, c 0.870, w 0.373; BCa c 0.860, w 0.386); q fail | 40: mix fail (b 0.008, c 0.890, w 0.243; BCa c 0.890, w 0.242); q PASS |
| C_E5/3-SAT (partial assignment given) | 5: mix fail (b 0.054, c 0.700, w 0.400; BCa c 0.750, w 0.396); q fail | 10: mix fail (b 0.011, c 0.890, w 0.314; BCa c 0.930, w 0.314); q fail | 20: mix fail (b 0.014, c 0.020, w 0.181; BCa c 0.010, w 0.168); q fail | 40: mix PASS (b 0.008, c 0.940, w 0.179; BCa c 0.930, w 0.177); q PASS |
| C_E5/colouring (k=3) | 5: mix fail (b 0.090, c 0.025, w 0.159; BCa c 0.025, w 0.160); q fail | 10: mix fail (b 0.008, c 0.020, w 0.151; BCa c 0.010, w 0.140); q fail | 20: mix fail (b 0.041, c 0.480, w 0.139; BCa c 0.480, w 0.134); q PASS | 40: mix fail (b 0.009, c 0.890, w 0.457; BCa c 0.880, w 0.466); q PASS |
| C_E5/colouring (k=3, partial colouring given) | 5: mix fail (b 0.053, c 0.575, w 0.541; BCa c 0.550, w 0.493); q fail | 10: mix fail (b 0.031, c 0.690, w 0.457; BCa c 0.730, w 0.498); q fail | 20: mix fail (b 0.095, c 0.600, w 0.288; BCa c 0.720, w 0.315); q fail | 40: mix fail (b 0.013, c 0.920, w 0.266; BCa c 0.920, w 0.263); q fail |
| C_E5/propositional entailment | 5: mix fail (b 0.125, c 0.050, w 0.133; BCa c 0.050, w 0.125); q not testable | 10: mix fail (b 0.093, c 0.110, w 0.144; BCa c 0.100, w 0.158); q not testable | 20: mix fail (b 0.087, c 0.160, w 0.136; BCa c 0.200, w 0.174); q not testable | 40: mix fail (b 0.077, c 0.270, w 0.181; BCa c 0.330, w 0.216); q not testable |

| Unit | bias and width pass from (items/cell) | all three gates pass at (percentile) | ... with BCa intervals |
|---|---|---|---|
| AH_E1/COL | not reached | – | – |
| AH_E1/ENT | not reached | – | – |
| AH_E1/SAT | not reached | – | – |
| AH_E2/COL | not reached | – | – |
| AH_E2/ENT | not reached | – | – |
| AH_E2/SAT | not reached | – | – |
| AH_E5/COL | 40 | 40 | 40 |
| AH_E5/ENT | 20 | – | – |
| AH_E5/KNAP | no planted triple (fewer than 3 members on every item) | – | – |
| AH_E5/SAT | 20 | 20, 40 | – |
| B4C4_E1/entailment | not reached | – | – |
| B4C4_E2/entailment | not reached | – | – |
| C_E1/3-SAT | 20 | – | 20, 40 |
| C_E1/colouring | 20 | – | 20 |
| C_E2/3-SAT | 5 | 40 | 40 |
| C_E2/colouring | 5 | 20, 40 | 5, 10, 20 |
| C_E2/knapsack | 10 | 20, 40 | 20, 40 |
| C_E3/colouring (gadget) | not testable | – | – |
| C_E5/3-SAT | not reached | – | – |
| C_E5/3-SAT (partial assignment given) | 20 | 40 | 40 |
| C_E5/colouring (k=3) | 10 | – | – |
| C_E5/colouring (k=3, partial colouring given) | not reached | – | – |
| C_E5/propositional entailment | not reached | – | – |

**Reading the sweep.**

- **Bias** passes at 5 or 10 per cell on most witness units. The exceptions are the A/H decision units, B4/C4 and C E5 entailment (by design), the near-tie runs, and C E5 colouring with a given state (0.095 at 20).
- **Width** shrinks roughly as 1/√(items per cell). The small C E5 units still have widths of 0.24–0.46 at 40 per cell.
- **Coverage binds**, at 0.79–0.94 for the smallest weight once bias and width pass. Where the items separate the planted pair by only one or two items, it collapses to 0.00–0.03.
- **For the power analysis**, on the current items and zoo, in items per cell:
  - C E2 colouring and knapsack and A/H E5 SAT pass from 20;
  - A/H E5 colouring and C E5 SAT with a given state pass at 40;
  - C E2 SAT passes at 40;
  - C E1 SAT passes at 20 and 40 with BCa intervals only (with percentile intervals, coverage is 0.86 and 0.79 on ALWAYS-UNSAT);
  - A/H E5 entailment and C E1 colouring are close at 40 (coverage 0.87, on B4 FIRST at 0.1 and on DPLL-LABEL at 0.3);
  - C E5 SAT and both C E5 colouring units need more than 40, because their widths are still 0.24–0.46.

## Percentile against BCa intervals

BCa (Efron 1987) corrects the percentile interval for the bootstrap distribution's median bias (z0, from the share of bootstrap fits below the estimate) and its skewness (the acceleration, from the leave-one-cluster-out jackknife). Both intervals come from the same 100 bootstrap fits per replicate, so the comparison isolates how the interval is built. The table covers all 153 planted weights in the 100-replicate mixture runs (10, 20 and 40 per cell, every testable unit).

| planted weight | weights | median coverage, percentile | median coverage, BCa | BCa − percentile: median (range) | median width, percentile / BCa |
|---|---|---|---|---|---|
| 0.6 | 51 | 0.91 | 0.91 | +0.00 (-0.04 to +0.06) | 0.269 / 0.265 |
| 0.3 | 51 | 0.88 | 0.90 | +0.01 (-0.06 to +0.12) | 0.265 / 0.251 |
| 0.1 | 51 | 0.86 | 0.89 | +0.02 (-0.05 to +0.21) | 0.100 / 0.103 |

- **The small weight gains a little.** BCa helps the 0.1 weight, whose bootstrap distribution is squeezed against zero: a median of +0.02, and up to +0.21. It changes little for the 0.3 and 0.6 weights. Median widths agree to within 0.015.
- **The boundary is worse.** Where the truth sits on the boundary (`null_q`, π_0 = 1), BCa covers worse than the percentile interval. On C E2 knapsack it gets 0.76 / 0.62 / 0.46 at 10 / 20 / 40 per cell, against 0.81 / 0.73 / 0.52.
- **The gate verdict differs** on 7 unit-sizes, in both directions, always at the margin:

  - C E2 colouring at 10 per cell: percentile fails (0.88), BCa passes (0.90)
  - A/H E5 SAT at 20 per cell: percentile passes (0.90), BCa fails (0.88)
  - C E1 SAT at 20 per cell: percentile fails (0.86), BCa passes (0.92)
  - C E1 colouring at 20 per cell: percentile fails (0.88), BCa passes (0.91)
  - A/H E5 SAT at 40 per cell: percentile passes (0.91), BCa fails (0.89)
  - C E1 SAT at 40 per cell: percentile fails (0.79), BCa passes (0.90)
  - C E2 colouring at 40 per cell: percentile passes (0.90), BCa fails (0.89)

- **Neither interval fixes a near-tie or the boundary.** Both are reported throughout, with the gates unchanged. The closing table lists the sizes at which each method passes.

## Misspecification: the uniform slip model on near-miss data

Same data (the near-miss 60/30/10 fake model), two fits. The table gives each fit's worst bias and smallest coverage, and the quantity the bias lands on.

| Unit | near-miss fit: max \|bias\| / min coverage | uniform fit on near-miss data | on | near-miss fit on uniform data | on |
|---|---|---|---|---|---|
| AH_E5/COL | 0.048 / 0.675 | 0.084 / 0.625 | A3 TT[FIRST-FIT] | 0.074 / 0.750 | A3 TT[FIRST-FIT] |
| AH_E5/ENT | 0.064 / 0.575 | 0.078 / 0.600 | q | 0.060 / 0.625 | exact |
| AH_E5/SAT | 0.011 / 0.625 | 0.102 / 0.775 | q | 0.034 / 0.750 | C0 POLARITY |
| C_E1/3-SAT | 0.052 / 0.725 | 0.138 / 0.400 | q | 0.050 / 0.625 | DPLL-MENTION (D, T first) |
| C_E1/colouring | 0.041 / 0.800 | 0.092 / 0.500 | q | 0.053 / 0.675 | FF-LABEL |
| C_E2/3-SAT | 0.017 / 0.525 | 0.032 / 0.500 | ALWAYS-UNSAT (A1 give-up) | 0.040 / 0.575 | GUC-DET (C2) |
| C_E2/colouring | 0.017 / 0.875 | 0.074 / 0.750 | NOISY-EXACT | 0.052 / 0.750 | FF-LABEL |
| C_E2/knapsack | 0.011 / 0.875 | 0.098 / 0.750 | q | 0.037 / 0.800 | RATIO-SKIP |
| C_E5/3-SAT | 0.034 / 0.625 | 0.054 / 0.650 | q | 0.051 / 0.650 | GUC-DET (C2) |
| C_E5/3-SAT (partial assignment given) | 0.054 / 0.700 | 0.125 / 0.775 | q | 0.060 / 0.800 | GREEDY-MENTION from state (C1) |
| C_E5/colouring (k=3) | 0.090 / 0.025 | 0.123 / 0.025 | ALWAYS-IMPOSSIBLE (A1 give-up) = PHANTOM-ADJACENT (B4) | 0.027 / 0.000 | FF-3-EDGE-MENTION-ABORT (C1 variant) |
| C_E5/colouring (k=3, partial colouring given) | 0.053 / 0.575 | 0.033 / 0.475 | DPLL-LIST from state (D) = DSATUR-3 from state (C2) | 0.063 / 0.550 | DPLL-LIST from state (D) = DSATUR-3 from state (C2) |

Fitting slips as uniform over the candidate answers, when they are really near misses, raises the worst bias to 0.03–0.14 on the 12 witness units. The matched near-miss fit gives 0.01–0.09.

- On 7 of the 12 units the extra bias lands on q (0.05–0.14): near misses are mistaken for "none of the above". This repeats the C vertical's recovery finding (SCOPE §6 rule 3). The slip model is part of the pre-registration, and its rate is estimated, not fixed.
- On the other five it lands on a member: NOISY-EXACT, ALWAYS-UNSAT, A3 TT[FIRST-FIT], or a tie group.
- The reverse, a near-miss fit on uniform-slip data, costs about as much (0.03–0.07), and lands on a planted member on 11 of the 12 units.

## Off-zoo: where a withheld procedure's weight goes

0.7 on the triple's first member and 0.3 on a group the fit does not have, each group in turn. Means over 8 replicates.

| Unit | withheld groups | to q (mean) | onto h1 (mean excess) | onto other members (mean) | groups with ≥ 0.2 of the withheld 0.3 on one member |
|---|---|---|---|---|---|
| AH_E1/COL | 9 | 0.001 | -0.071 | 0.370 | 2 of 9 |
| AH_E1/ENT | 13 | 0.000 | -0.040 | 0.340 | 2 of 13 |
| AH_E1/SAT | 11 | 0.002 | -0.002 | 0.300 | 2 of 11 |
| AH_E2/COL | 10 | 0.011 | -0.036 | 0.324 | 1 of 10 |
| AH_E2/ENT | 13 | 0.010 | +0.013 | 0.278 | 2 of 13 |
| AH_E2/SAT | 10 | 0.003 | -0.007 | 0.305 | 2 of 10 |
| AH_E5/COL | 6 | 0.026 | +0.048 | 0.226 | 6 of 6 |
| AH_E5/ENT | 3 | 0.028 | +0.038 | 0.235 | 3 of 3 |
| AH_E5/SAT | 4 | 0.056 | +0.067 | 0.178 | 4 of 4 |
| B4C4_E1/entailment | 14 | 0.008 | -0.055 | 0.346 | 14 of 14 |
| B4C4_E2/entailment | 18 | 0.000 | -0.006 | 0.306 | 0 of 18 |
| C_E1/3-SAT | 9 | 0.005 | +0.023 | 0.273 | 9 of 9 |
| C_E1/colouring | 10 | 0.035 | +0.011 | 0.253 | 9 of 10 |
| C_E2/3-SAT | 8 | 0.039 | -0.084 | 0.346 | 8 of 8 |
| C_E2/colouring | 8 | 0.019 | +0.005 | 0.275 | 8 of 8 |
| C_E2/knapsack | 6 | 0.079 | +0.096 | 0.126 | 5 of 6 |
| C_E3/colouring (gadget) | 2 | 0.018 | -0.636 | 0.918 | 2 of 2 |
| C_E5/3-SAT | 10 | 0.044 | +0.004 | 0.251 | 9 of 10 |
| C_E5/3-SAT (partial assignment given) | 7 | 0.030 | +0.034 | 0.236 | 7 of 7 |
| C_E5/colouring (k=3) | 11 | 0.056 | -0.047 | 0.291 | 10 of 11 |
| C_E5/colouring (k=3, partial colouring given) | 5 | 0.110 | -0.045 | 0.235 | 4 of 5 |
| C_E5/propositional entailment | 10 | 0.026 | -0.087 | 0.361 | 0 of 10 |

**Most of the withheld 0.3 lands on zoo members, not on q.**

- q receives 0.00–0.11 (unit means). The members whose near-miss kernels reach the withheld answers absorb the rest (0.13–0.92; C E3 is the extreme).
- A/H's criterion asks that no single member take 0.2 of the withheld mass. On every witness unit, it fails for nearly every withheld group. Where q isn't identified (the A/H decision units, B4/C4 E2, C E5 entailment), the criterion can't be judged.
- **So a small π_0 does not show that the zoo is complete.** Off-zoo strategies have to be caught by goodness-of-fit: posterior-predictive checks per cell, and model comparison against an extended zoo.

## Checks: clustered strategies and censoring

| Unit | clustered: max \|bias\| / min coverage / width | truncated, excluded: bias on h1 | truncated, token model: bias on h1 |
|---|---|---|---|
| AH_E1/COL | 0.065 / 0.550 / 0.735 | -0.182 | -0.087 |
| AH_E1/ENT | 0.082 / 0.400 / 0.705 | -0.142 | -0.043 |
| AH_E1/SAT | 0.114 / 0.450 / 0.495 | -0.188 | -0.036 |
| AH_E2/COL | 0.100 / 0.100 / 0.500 | -0.074 | -0.019 |
| AH_E2/ENT | 0.070 / 0.225 / 0.433 | -0.128 | 0.011 |
| AH_E2/SAT | 0.062 / 0.325 / 0.500 | -0.169 | -0.008 |
| AH_E5/COL | 0.040 / 0.500 / 0.600 | -0.144 | -0.011 |
| AH_E5/ENT | 0.016 / 0.375 / 0.605 | -0.121 | -0.021 |
| AH_E5/SAT | 0.026 / 0.425 / 0.600 | -0.135 | -0.001 |
| B4C4_E1/entailment | 0.093 / 0.000 / 0.600 | -0.011 | 0.013 |
| B4C4_E2/entailment | 0.066 / 0.550 / 0.383 | -0.111 | -0.010 |
| C_E1/3-SAT | 0.072 / 0.250 / 0.600 | -0.128 | 0.021 |
| C_E1/colouring | 0.053 / 0.325 / 0.600 | -0.099 | 0.007 |
| C_E2/3-SAT | 0.043 / 0.375 / 0.300 | -0.064 | -0.028 |
| C_E2/colouring | 0.010 / 0.800 / 0.442 | -0.110 | 0.009 |
| C_E2/knapsack | 0.010 / 0.700 / 0.459 | -0.098 | -0.008 |
| C_E3/colouring (gadget) | not testable | not testable | not testable |
| C_E5/3-SAT | 0.030 / 0.475 / 0.618 | -0.081 | 0.037 |
| C_E5/3-SAT (partial assignment given) | 0.058 / 0.400 / 0.600 | -0.155 | -0.009 |
| C_E5/colouring (k=3) | 0.011 / 0.175 / 0.153 | -0.059 | 0.034 |
| C_E5/colouring (k=3, partial colouring given) | 0.025 / 0.350 / 0.600 | -0.060 | 0.009 |
| C_E5/propositional entailment | 0.108 / 0.000 / 0.135 | -0.225 | -0.087 |

- **Clustered.** When every variant of a base is answered by the same member, the realised mixture varies with only 5–30 clusters per unit. The cluster bootstrap widens (to 0.3–0.7 on most units), but coverage still falls to 0.0–0.8 at dev size. The study needs more bases per unit, not more variants per base.
- **Censoring.**
  - Excluding truncated runs biases the frequently truncated member by −0.06 to −0.23 on most units.
  - With the true truncation probabilities as the token model, that bias drops to within ±0.045 on all but A/H E1 colouring and C E5 entailment (−0.09 each).
  - The hook works. What's missing is a fitted token model that predicts each member's tokens on each item.
  - C E3's planted triple is not testable, so its checks are not reported.

## What fails, and why

1. **Weights the items can't identify** (see Limitations).
   - q and the constant groups on two-valued channels.
   - Noise models that are fixed mixtures of procedures.
   - The four-way dependency among procedures on B4/C4 E2.
   - The LOCAL-t proxies with DPLL-LIST = FF-LIST on C E3.

   Scenarios that plant weight on them are not testable on these designs, at any size.
2. **Near-dependencies on two-valued channels.** At full rank a binary answer still carries one bit per item, and these units have 10–19 groups.
   - Noise models (SAMPLE-m, WALK-200, NOISY-EXACT, PERCEPTION-NOISE) are nearly fixed mixtures of the procedures. A planted noise model is lost: the A/H decision units' mixtures have bias 0.06–0.12 and coverage 0.0–0.75 at every size run, and most single-member scenarios for these members fail by 0.3–1.0.
   - B4/C4 E1 is the extreme case, with σ_min/σ_max = 0.0004 between the EXACT group and NOISY-EXACT.
   - More items don't fix this. Items on which the noise models' probabilities vary independently of the procedures would.
3. **Near-ties: pairs separated on one or two items.** The planted pair is h1 and its nearest competitor, so a near-tie in the item set shows up directly. Every fit puts the pair's weight on one member or the other, and the bootstrap does not show the ridge, because the separating item tilts it. Coverage drops to 0.00–0.03.
   - C E2 SAT at 10 per cell: GUC-DET and SC-DET differ on 1 of 100 items.
   - C E5 SAT with a given state at 20: GUC-DET and SC-DET from state differ on 1 of 60. They are tied on every item at 10 and 40, so there they form one group.
   - C E5 colouring (k = 3): FF-3-EDGE-MENTION-ABORT and the ALWAYS-IMPOSSIBLE = PHANTOM-ADJACENT group differ on 2 of 25 dev items.

   Whether a unit passes can turn on whether its item set happens to contain one separating item.
4. **Coverage at the margin.** On the units whose bias and width pass (near-tie runs aside), the smallest per-weight coverage is 0.79–0.94, on the 0.1 or the 0.3 weight. The SE of each coverage is about 0.03 at 100 replicates, and the gate takes the minimum over three weights, so verdicts at 0.88–0.92 can flip between runs and between the two interval methods.
5. **Null q at the boundary** (C E2 knapsack; the SAT units that list ALWAYS-UNSAT). See Limitations. On C E2 knapsack the bias is ≤ 0.01, and the failure is coverage alone.
6. **The constant responder is credited to a member.** This is correct given the zoo, but it fails `null_always`:
   - on C E1 colouring, the one-colour answer goes to LOCAL-2-ID (E), whose answer is nearly all one colour;
   - on C E3, the constant answer goes to the LOCAL-t proxies;
   - on B4/C4 E1, the constant YES goes to ALWAYS-YES on the decision items.

   On C E1 and C E2 SAT it now passes: since #22 those zoos list ALWAYS-UNSAT, and the constant-UNSAT responder goes there rather than to RO-GREEDY.
7. **Small units.** The C E5 units with a given state (10–15 items at dev) and A/H E5 (20–25 items, 5 clusters) need several times the items before the width gate can pass.

## Limitations: what the items cannot identify, and what would fix it

`engine.identifiability` computes the rank and null space of the (item, outcome) × (groups + q) matrix for every unit. On finite channels the matrix is exact, with ε = 0. On witness channels it uses the candidate answers plus draws from every component.

A dependency means no amount of data on these items separates the members involved: only combinations of their weights are identified. The engine reports each involved weight as *not identified*, with the range of values consistent with the fit (π ≥ 0). The harness marks a scenario *not testable* when it plants weight on any such member, whichever member the elimination happens to pick as the pivot. On the regenerated dev sets, 9 of the 23 units have dependencies:

1. **q on two-valued channels: all six A/H decision units, B4/C4 E2 and C E5 entailment.**
   - On a YES/NO (SAT/UNSAT, POSSIBLE/IMPOSSIBLE) channel, the uniform q equals ½ always-positive + ½ always-negative on every item. Any item-independent q is some such mixture.
   - So wherever the zoo has a constant-positive and a constant-negative group, the unexplained mass is not identified. Those groups are the ALWAYS members, plus any member that gives the same answer on every item of the unit: C1 GREEDY = ALWAYS-UNSAT on A/H E1 SAT, and C E5 entailment's EXACT group, which answers "does not follow" on every item.
   - Only π_pos + π_0/2 and π_neg + π_0/2 are estimable, and `null_q` and `null_always` are not testable there.
   - **Fixes:**
     - Score these items on a channel with more than two outcomes. The A/H formats already ask for a witness, which would make q identifiable; another option is a third answer such as "cannot tell".
     - Balance the ground truth within each unit, so EXACT is not constant (C E5 entailment).
     - Or pre-register that on decision channels π_0 is reported only through these combinations.
2. **Noise models that are fixed mixtures of procedures:**
   - **Which:** B4/C4 E2's SAMPLE-3, PERCEPTION-NOISE and NOISY-EXACT; C E5 entailment's NOISY-EXACT; A/H E2 colouring's SAMPLE-8, which never finds a colouring and so equals ALWAYS-IMPOSSIBLE = C1 FIRST-FIT.
   - **Why:** on these items each one's answer distribution is the same mixture of other members on every item. For example, NOISY-EXACT = 0.97 × the EXACT group + 0.015 × ALWAYS-YES + 0.015 × NONE on all 240 B4/C4 E2 items, because its flip rate does not vary.
   - **Fix:** vary the instances along the dimension the noise model depends on (sizes and step counts for NOISY-EXACT, colouring density for SAMPLE-m), or merge these members with the procedures they reduce to.
3. **A dependency among procedures on B4/C4 E2, unchanged by the zoo fixes.**
   - ETR-1p, the EXACT group (ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1), MM-G and MM-S1 = MM-elim span only three directions. On every item, MM-S1's answer is ETR-1p's plus MM-G's minus the EXACT group's.
   - Their weights are identified only up to this combination.
   - **This is a design gap for H6**, which asks whether cognitive members explain errors better than surface ones. H6 needs B4/C4 items that separate MM-S1 from the ETR-1p / MM-G / EXACT combination: inference forms on which that identity fails.
4. **A dependency among procedures on C E3 (new on the regenerated items).**
   - DPLL-LIST = FF-LIST and the LOCAL-3, -4, -5, -6, -8 and -10-LIST proxies ("reaches the target") span only six directions. LOCAL-10-LIST = DPLL-LIST − LOCAL-3 − LOCAL-4 − LOCAL-5 − LOCAL-6 − LOCAL-8 on every item.
   - On the pre-regeneration items, the same members were nearly dependent, and FF-LIST lost 0.14–0.31 of its weight to the proxies.
   - The planted triple cannot avoid them, so `mix` is not testable on C E3.
   - **Fix:** more variety in the targets' depths relative to the proxies' horizons, so that no proxy's answers are a signed sum of the others'.
   - C E3's RANDOM (H) ("uniform over 3^67 colourings") has no prediction the engine can score on the bit or colour channels, so it is unavailable on every item, which makes it a zero column. Its projection would be P(same) = 1/3.
5. **Near-dependencies.**
   - **B4/C4 E1** is full rank, but its σ_min/σ_max is 0.0004, far below the 0.05 that A/H §5.3 pre-registers. Its weakest direction is the EXACT group vs NOISY-EXACT. (The regenerated MC items now rotate their answers across A–D.)
   - **Pairs that differ on one or two items:**
     - GUC-DET vs SC-DET on C E2 SAT at 10 per cell;
     - GUC-DET from state vs SC-DET from state on C E5 SAT with a state at 20 per cell;
     - ALWAYS-UNSAT vs SC-DET on C E2 SAT (2 of 50 dev items);
     - DSATUR vs DSATUR-LABEL on C E1 colouring.

     Such a pair is identified in principle, but every fit puts the pair's weight on one member or the other, and the intervals do not show it (coverage 0.00–0.03). The engine merges only exact ties. A near-tie check that reports such pairs as a sum, or more items that separate them, would fix it.

**Other limitations.**

- **The boundary.** Under `null_q` the truth, π_0 = 1, sits on the edge of the simplex, and bootstrap intervals are not valid there (Andrews 2000). On C E2 knapsack, percentile and BCa both miss it in 19–54% of replicates at 10–40 per cell, while |bias| stays ≤ 0.01. Members with π_h = 0 sit on the boundary too, but the gates check only their bias.
- **ALWAYS-UNSAT against q.** On SAT units that list ALWAYS-UNSAT, it is told apart from q only by how often the answer is UNSAT (always, against q's ½). Pure noise therefore puts about 0.4/√N of its weight on it for N items. The bias shrinks with N; the boundary miss does not.
- **Selection.** Some generators select bases on a member's behaviour: C E1 SAT keeps bases where GREEDY satisfies in every order, and C E5 requires dead ends. Selection depends on x only, so inference on P(y | x) stays valid, but π then describes the selected population, not instances at large.
- **The slip model.** Fake models and fit both use the near-miss kernel. Real slips may differ, and the misspecification check covers only the uniform-candidate alternative.
- **Distributional members are used as stored.** RO-FF and RO-GREEDY keep only their 25 most frequent outcomes and lump the rest, which the likelihood spreads like q. That makes them partly collinear with q, and their single-member scenarios fail by 0.02–0.50. NOISY-EXACT's stored "_other" lump is likewise uniform, not a near miss of the exact answer.
- **Availability.** The identifiability matrix ignores the renormalisation over available members (FF-OUT, the LOCAL-t members, and any member with no prediction on some items). The fit does not ignore it.
- **Not built:** the hierarchical cross-model fit, a fitted token model, and a boundary-aware interval (see What is left).

## What is left

- **A boundary-aware interval for π_0 (not built; the gates stay as pre-registered either way).**
  - **The standard fix** inverts the likelihood-ratio test. The interval is {c : 2[ℓ(π̂) − max_{π_0 = c} ℓ(π)] ≤ κ}. At the boundary the statistic is χ̄²-distributed: for the one boundary parameter, a 50:50 mixture of χ²_0 and χ²_1 (Self & Liang 1987), so κ = 2.71.
  - **What it needs:**
    1. **A constrained EM, with π_0 held at c and the other weights renormalised.** This is a one-line change to the MM step.
    2. **A root search over c for each interval.** That is about 10–20 constrained fits per replicate, against the 100 bootstrap fits now.
    3. **A correction for clustering.** The items within a base are dependent, so the LR statistic has to be rescaled before the χ̄² threshold applies, for example with a Rao–Scott-type correction from the cluster sandwich.
  - **Cost:** (1) and (2) are small; (3) is the real work, and it needs its own coverage check. Doing the same for member weights that sit at zero needs χ̄² weights that depend on how many weights sit there, estimated by simulation.
  - **Estimate:** about a day for π_0 alone, with tests and a coverage rerun.
- **A near-tie check.** Report pairs that differ on fewer than a few items as one sum, as exact ties are now, or flag them in the fit output.
- **Design fixes** for the not-testable and design-limited units, listed above.
- **The hierarchical cross-model fit** (DESIGN §3 O3) and a **fitted token model** for censoring.
- **Off-zoo detection.** The unexplained mass does not flag a missing strategy (see Off-zoo above), so posterior-predictive checks per cell are needed.

## Where the gates pass (regenerated items)

For each unit the table gives:

- the sizes (items per cell: 5 = dev, then 10, 20 and 40) at which the 60/30/10 mixture passes all three gates, with percentile and with BCa intervals;
- the two null scenarios, by size;
- the sizes at which the mixture (percentile) and both nulls pass together.

`recovery report` computes it from the result files. The runs behind it:

- 100 replicates at 10–40 per cell, and 40 at dev size.
- The six A/H decision units were run up to 20 per cell. They fail by design at every size, and at 40 they would have taken most of the run time.
- B4/C4 E1, B4/C4 E2 and C E3 were run at dev size only.
- `single` and `feature` were run at dev size only, where they fail on every unit.

**Read "passes" as the notes below say: a pass covers the planted triple and the bias of every identified quantity, not every member's own weight.**

| Unit | mixture passes at (percentile) | mixture passes at (BCa) | null q | null ALWAYS | mixture and both nulls pass at |
|---|---|---|---|---|---|
| AH_E1/COL | none (5–20) | none (5–20) | not testable at every size (5–20) | not testable at every size (5–20) | – |
| AH_E1/ENT | none (5–20) | none (5–20) | not testable at every size (5–20) | not testable at every size (5–20) | – |
| AH_E1/SAT | none (5–20) | none (5–20) | not testable at every size (5–20) | not testable at every size (5–20) | – |
| AH_E2/COL | none (5–20) | none (5–20) | not testable at every size (5–20) | not testable at every size (5–20) | – |
| AH_E2/ENT | none (5–20) | none (5–20) | not testable at every size (5–20) | not testable at every size (5–20) | – |
| AH_E2/SAT | none (5–20) | none (5–20) | not testable at every size (5–20) | not testable at every size (5–20) | – |
| AH_E5/COL | 40 | 40 | pass at every size (5–40) | fail at 5; pass at 10, 20, 40 | 40 |
| AH_E5/ENT | none (5–40) | none (5–40) | pass at every size (5–40) | pass at every size (5–40) | – |
| AH_E5/KNAP | no planted triple | no planted triple | pass at 5, 10; fail at 20, 40 | pass at every size (5–40) | – |
| AH_E5/SAT | 20, 40 | none (5–40) | pass at every size (5–40) | pass at every size (5–40) | 20, 40 |
| B4C4_E1/entailment | none (5) | none (5) | fail at 5 | fail at 5 | – |
| B4C4_E2/entailment | none (5) | none (5) | not testable at 5 | not testable at 5 | – |
| C_E1/3-SAT | none (5–40) | 20, 40 | fail at every size (5–40) | pass at every size (5–40) | – |
| C_E1/colouring | none (5–40) | 20 | pass at every size (5–40) | fail at every size (5–40) | – |
| C_E2/3-SAT | 40 | 40 | fail at every size (5–40) | pass at every size (5–40) | – |
| C_E2/colouring | 20, 40 | 5, 10, 20 | pass at every size (5–40) | pass at every size (5–40) | 20, 40 |
| C_E2/knapsack | 20, 40 | 20, 40 | pass at 5; fail at 10, 20, 40 | pass at every size (5–40) | – |
| C_E3/colouring (gadget) | not testable | not testable | fail at 5 | fail at 5 | – |
| C_E5/3-SAT | none (5–40) | none (5–40) | fail at 5, 10, 20; pass at 40 | pass at every size (5–40) | – |
| C_E5/3-SAT (partial assignment given) | 40 | 40 | fail at 5, 10, 20; pass at 40 | pass at every size (5–40) | 40 |
| C_E5/colouring (k=3) | none (5–40) | none (5–40) | fail at 5, 10; pass at 20, 40 | pass at every size (5–40) | – |
| C_E5/colouring (k=3, partial colouring given) | none (5–40) | none (5–40) | fail at every size (5–40) | pass at every size (5–40) | – |
| C_E5/propositional entailment | none (5–40) | none (5–40) | not testable at every size (5–40) | not testable at every size (5–40) | – |

**What each pass covers.** Members tied on every item of a unit form one group with one weight, and the fit reports only that sum. These are the groups in the passing units, at the sizes where they pass:

| Unit | Sizes | Planted triple (0.6 / 0.3 / 0.1) | Reported as one weight |
|---|---|---|---|
| C E2 colouring | 20, 40 | FF-LABEL / DPLL-LIST (D) / EXACT at 20; FF-LABEL / DSATUR-LABEL / EXACT at 40 | FF-LIST = GREEDY+REPAIR-LIST (C→F). RANDOM (H) is identical to q and is folded into the unexplained mass |
| C E2 knapsack | 20, 40 (mixture only) | DIFF / RATIO-SKIP / EXACT | RATIO+BEST-SINGLE = RATIO-PREFIX |
| A/H E5 SAT | 20, 40 | C0 POLARITY / C1 GREEDY / A3 TT[exact] | none |
| A/H E5 colouring | 40 | A3 TT[FIRST-FIT] / C1 FIRST-FIT (stated rule) / exact | none |
| C E5 SAT with a given state | 40 | GREEDY-MENTION / GREEDY-MENTION-ABORT from state / POLARITY | **GUC-DET from state = SC-DET from state**: tied on every item at 40 per cell, so only their sum is identified. On the 20-per-cell set they differ on one item, and their split fails (coverage 0.01–0.03). RANDOM (H) is folded into q |
| C E2 SAT | 40 (mixture only) | GUC-DET (C2) / SC-DET (C2) / POLARITY (C0) | GREEDY-INDEX = GREEDY-MENTION. RANDOM (H) is folded into q |
| C E1 SAT | 20, 40 (mixture with BCa only) | DPLL-INDEX / DPLL-MENTION (D, T first) / ALWAYS-UNSAT | none. RANDOM (H) is folded into q |

In every unit, a pair that differs on only one to three items is identified in principle but is not checked unless it is the planted pair. The engine reports the least-separated pairs per unit (`least_separated` in the result files).

**Why the others fail.**

- **A/H E1 and A/H E2 (SAT, colouring, entailment): fails by design.**
  - q is not identified on a two-valued channel (q = ½ always-positive + ½ always-negative), so the null scenarios are not testable.
  - The noise models (SAMPLE-8, WALK-200, NOISY-EXACT, PERCEPTION-NOISE) are near-mixtures of the procedures, and the mixture fails at every size run, with bias 0.06–0.12 and coverage 0.01–0.75.
  - Fix: a channel with more than two outcomes (the witness), or report π_0 only through the identified combinations.
- **A/H E5 entailment: not reached by 40.** Bias and width pass from 20, but the 0.1 weight (B4 FIRST) covers 0.81 at 20 and 0.87 at 40 (BCa 0.88 and 0.88). Both nulls pass.
- **A/H E5 knapsack: no mixture test**, because fewer than three members are available on every item. `null_q` fails coverage from 20 on (the boundary).
- **B4/C4 E1: fails by design.**
  - NOISY-EXACT is nearly the EXACT group (σ_min/σ_max = 0.0004).
  - The 0.1 NOISY-EXACT weight covers 0.00, `null_q` loads 0.25 on members, and the constant YES goes to ALWAYS-YES.
- **B4/C4 E2: fails by design.**
  - There are five linear dependencies, including the ETR-1p / EXACT group / MM-G / MM-S1 identity that blocks H6. The zoo fixes did not remove it.
  - The nulls are not testable.
  - On identified quantities, the mixture covers 0.40 at dev size.
- **C E1 SAT:** the mixture passes only with BCa intervals (0.92 at 20 and 0.90 at 40 per cell).
  - With percentile intervals, the 0.1 ALWAYS-UNSAT weight covers 0.84, 0.86 and 0.79 at 10, 20 and 40, with bias ≤ 0.02. It is the skewed small-weight case that BCa corrects.
  - `null_q` fails at every size. ALWAYS-UNSAT takes about 0.03 of pure noise, and q's interval misses 1 in 22% of replicates (the boundary).
  - `null_always` passes.
- **C E1 colouring: not reached by 40.**
  - The mixture covers 0.88 / 0.87 at 20 / 40 per cell (BCa: 0.91, a pass, at 20; 0.89 at 40). Bias and width pass from 20.
  - `null_always` fails by design: the one-colour answer goes to LOCAL-2-ID (E), whose answer is nearly all one colour.
- **C E2 SAT:** the mixture passes at 40 (0.92 with both methods), after near-ties at the smaller sizes.
  - At 10 per cell, GUC-DET and SC-DET differ on 1 of 100 items (coverage 0.00).
  - At 20, ALWAYS-UNSAT is GUC-DET's nearest competitor, and widths are 0.28.
  - `null_q` fails at every size (0.88 at 40), from the ALWAYS-UNSAT boundary, so the three never pass together.
  - `null_always` passes.
- **C E3: fails by design.**
  - The mixture is not testable. DPLL-LIST = FF-LIST and six LOCAL-t proxies span only six directions, and the planted triple can't avoid them.
  - `null_q` loads 0.41 on members: on the three-valued channel, the many proxies nearly span q.
  - The constant answer goes to the proxies.
- **C E5 SAT: not reached by 40.** Width is 0.24 and the 0.1 weight's coverage 0.89 at 40 per cell. `null_q` passes at 40 and fails below it, from ALWAYS-UNSAT's share at the boundary.
- **C E5 colouring (k = 3): fails at these sizes, by a near-tie.**
  - FF-3-EDGE-MENTION-ABORT and the ALWAYS-IMPOSSIBLE = PHANTOM-ADJACENT group differ on 2 of 25 dev items. Coverage is 0.01–0.03 at 5 and 10 per cell, and 0.48 at 20.
  - At 40, coverage recovers to 0.89 but width is 0.46.
- **C E5 colouring with a given state: not reached by 40.** Bias and coverage pass at 40, but width is 0.27, and `null_q` fails on width.
- **C E5 entailment: fails by design.** q and NOISY-EXACT are combinations of other members, and the EXACT group answers "does not follow" on every item. The mixture's bias is 0.08–0.13 at every size.
