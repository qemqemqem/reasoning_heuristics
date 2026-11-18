# Recovery: positive controls for the identification engine

*The Stage 0 gate (SCOPE §4 item 5; DESIGN §5 rule 12): before any LLM data is analysed, fake models with planted mixtures must be recovered with |bias| ≤ 0.05, 95% coverage ≥ 0.9 and median interval width ≤ 0.2. Results on the regenerated items are in [data/recovery/](../data/recovery/) (`dev.json`, `pc10.json`, `pc20.json`, `pc40.json`). The pre-regeneration results are in [data/recovery/pre-regeneration/](../data/recovery/pre-regeneration/).*

> **Status: in progress.** The next section covers the candidate units on the regenerated items. Everything from "Bottom line" down still describes the **pre-regeneration items** (main 89ac750, before #13, #14 and #16), whose result files now live in `data/recovery/pre-regeneration/`. This page will be rebuilt for the regenerated items once the sweep of the other units finishes.

## Regenerated items: candidate units

**Items.**

- Dev size (5 items per cell): `data/items/dev` as on main after #22. On C E1 and C E2, the SAT items list `ALWAYS-UNSAT (A1 give-up)`.
- 20 per cell: `data/items/pc20` (#21, #22).
- 10 and 40 per cell: generated into scratch with `python -m reasoning_heuristics.generate --vertical V --eval E --tier dev --seed 1 --per-cell N`, using main's generator code. For C E1 and C E2 that means after #22.

At 20 per cell, the C E2 colouring and knapsack results and all A/H E5 results were computed on scratch copies whose items are identical to `data/items/pc20`. Each result file records the sha256 of every item file it read.

**Engine changes in this round**

- **Special-token predictions do not slip** (`likelihood.py`).
  - A deterministic prediction of UNSAT, IMPOSSIBLE or X used to slip to "q without that token". On a channel with one special token, q gives that token ½. So at ε = 0.5 (the cap), a member predicting the token on every item (ALWAYS-UNSAT, ALWAYS-IMPOSSIBLE) was identical to q, and pure noise put 0.36–0.41 on ALWAYS-UNSAT.
  - A special token has no near misses, so such a prediction now gives the token with probability 1 at any ε.
  - The change touches only units where some member predicts a special token on a witness channel: A/H E5 colouring and entailment, C E1 and C E2 SAT, and the four C E5 witness units. Those units were rerun.
  - Elsewhere the code path is unchanged. A/H E5 SAT, rerun as a control, reproduces its results exactly.
- **BCa intervals** (bias-corrected and accelerated; Efron 1987) are reported next to the percentile cluster-bootstrap intervals, on the same fits. The acceleration comes from a leave-one-cluster-out jackknife.
  - Both methods are reported throughout, against the same gates.
  - Neither method nor any gate was tuned.
- **`recovery run --units`** now takes a `;`-separated list, because unit names contain commas. A name that matches no unit stops the run. Before this fix, "C E5 colouring with a given state" was silently skipped.

**Where the candidate units pass**

The table uses the 60/30/10 mixture: 100 replicates at 10, 20 and 40 per cell, and 40 replicates at dev size (5). A size passes when all three gates pass. A size marked *pending* is still running.

| Unit | mixture, percentile intervals | mixture, BCa intervals | null q | null ALWAYS |
|---|---|---|---|---|
| C E2 colouring | 20 and 40 (min coverage 0.92, 0.90) | 5, 10, 20 (0.90–0.93); 40 misses (0.89) | pass at every size | pass at every size |
| C E2 knapsack | 20 and 40 (0.92, 0.91) | 20 and 40 (0.92, 0.90) | fails coverage at 10, 20 and 40 (0.81, 0.73, 0.52; bias ≤ 0.01) | pass at every size |
| A/H E5 SAT | 20 and 40 (0.90, 0.91) | none (0.88 at 20, 0.89 at 40) | pass | pass |
| C E5 SAT with a given state | 40 (0.94; GUC-DET and SC-DET from state are tied there, see below) | 40 (0.93) | pass at 40, fails below | pass |
| C E1 SAT (after #22) | none at 5 or 20 (0.86 on ALWAYS-UNSAT at 20); 10 and 40 *pending* | 20 (0.92) | fails at 5 and 20 (coverage 0.78 at 20) | pass at 5 and 20 |
| C E2 SAT (after #22) | none at 5 or 20 (width 0.28 at 20); 10 and 40 *pending* | none at 5 or 20 | fails at 5 and 20 (coverage 0.89 at 20) | pass at 5 and 20 |
| A/H E5 entailment | none at 5–40 (0.81 at 20 and 0.87 at 40, on B4 FIRST) | none at 5–40 (0.88 at 20 and at 40) | pass | pass |

**Why they fail**

- **Coverage at the margin.** On A/H E5 SAT, C E2 colouring and C E2 knapsack, the smallest per-weight coverage sits at 0.88–0.93 from 20 per cell on. That is within the Monte Carlo error of a minimum over three weights (SE about 0.03 at 100 replicates).
  - The methods differ by case. BCa helps a small, skewed weight: ALWAYS-UNSAT on C E1 SAT goes from 0.86 to 0.92, and B4 FIRST on A/H E5 entailment from 0.81 to 0.88.
  - BCa is no better on A/H E5 SAT, and worse at the q = 1 boundary: C E2 knapsack null q goes from 0.73 to 0.62 at 20 per cell.
- **Null q at the boundary.** The truth, q = 1, sits on the edge of the simplex.
  - Whenever more than 97.5% of the bootstrap refits give some member a sliver of weight, the percentile interval ends just below 1 and counts as a miss.
  - More items make that more likely, so knapsack's coverage falls from 0.81 to 0.52 between 10 and 40 per cell, with |bias| ≤ 0.01 throughout. Running EM 20 times longer leaves fewer bootstrap refits at exactly 1, not more; checked on C E1 SAT at 20 per cell.
  - This is the known failure of bootstrap intervals at a boundary. A boundary-aware interval (profile likelihood with the χ̄² limit) would be the principled alternative, and it isn't implemented.
- **ALWAYS-UNSAT and q** are told apart only by how often the answer is UNSAT: always, against q's ½.
  - Under pure noise, ALWAYS-UNSAT takes the excess UNSAT share. That is about 0.4/√N of the weight for N items: 0.07 at dev size on C E1, 0.03 at 20 per cell.
  - This holds on every SAT unit that lists ALWAYS-UNSAT. The bias shrinks with N; the boundary miss above does not.
- **Near-ties, by the design of the items.**
  - On C E5 SAT with a given state, GUC-DET from state and SC-DET from state differ on 1 of the 60 items at 20 per cell. Every fit puts the pair's weight on one or the other (coverage 0.01–0.03).
  - The same pair is tied on every item at 10 and at 40 per cell. It then forms one group, and the triple moves to GREEDY-MENTION / GREEDY-MENTION-ABORT from state. So the pass at 40 does not include the GUC/SC split: on those items only the pair's sum is identified, and the fit reports it as one group.
  - On C E2 SAT, the C2 procedures answer UNSAT on 90–96% of the dev items, so ALWAYS-UNSAT is GUC-DET's nearest competitor: 27 separating items of 200 at 20 per cell. The planted pair's intervals stay 0.33 wide.
- **Null ALWAYS now passes on C E1 and C E2 SAT.** The constant-UNSAT responder goes to ALWAYS-UNSAT, not RO-GREEDY.

## Bottom line (pre-regeneration items)

- **No unit passes the gate at the committed dev size (5 items per cell).** The units are small (10–270 items, 5–30 clusters), so intervals are wide and coverage is poor almost everywhere.
- **Where it passes:** the table at the end gives, per unit, the size at which the mixture passes and the null scenarios' verdicts. The mixture and both nulls pass together only on C E2 colouring (10 per cell), A/H E5 SAT (20) and A/H E5 entailment (40).
- **On witness channels, 9 of the 12 units with a planted triple reach bias ≤ 0.05 and width ≤ 0.2 for the 60/30/10 mixture somewhere between 5 and 40 items per cell** (table below).
  - **Coverage is the gate that binds.** The percentile cluster bootstrap covers about 0.77–0.93 per weight at those sizes.
  - In the 30-replicate sweep the mixture first passes all three gates at 10 per cell on C E2 colouring, at 20 on A/H E5 SAT and C E2 knapsack, and at 40 on A/H E5 entailment and C E1 SAT.
  - **With 100 replicates at 40 per cell, six of eight witness units pass all three gates**: A/H E5 SAT, C E1 SAT, C E2 SAT / colouring / knapsack, and C E5 SAT with a given state. A/H E5 colouring misses, with EXACT at 0.84 ± 0.04, and so does C E1 colouring (DPLL-LABEL 0.88 ± 0.03). The 30-replicate coverage misses were mostly noise.
- **Eight of the 23 units have linear dependencies, so their unexplained mass can't be identified on these items.**
  - On every two-valued channel q = ½ always-positive + ½ always-negative. That covers all six A/H decision units, B4/C4 E2 and C E5 entailment.
  - B4/C4 E2 also has dependencies among noise models, and one among procedures that matters for H6.
  - `null_q` is therefore *not testable* on those units, and the engine reports the weights involved as *not identified*, with their identified combinations and ranges.
- **Structural failures that more items won't fix:**
  - C E3's FF-LIST loses 0.14–0.31 of its weight to the LOCAL-t proxies, which agree with it within their horizon;
  - B4/C4 E1's NOISY-EXACT is absorbed by the EXACT group (σ_min/σ_max = 0.0004);
  - on two-valued channels, noise models (SAMPLE-m, WALK, NOISY-EXACT) are near-mixtures of the procedures.
- **Misspecification:** fitting the uniform-candidate slip model to near-miss data raises the worst bias to 0.07–0.18, and it lands on the unexplained mass every time: slips are mistaken for "none of the above". This is the C vertical's finding again, and the reason the near-miss model is the pre-registered one.
- **Off-zoo:** a withheld procedure's 0.3 goes mostly onto zoo members: 0.13–0.35 onto other members (0.72 on C E3), against 0.00–0.08 to q (0.20 on one 10-item unit). Wherever q is identified, nearly every withheld group puts ≥ 0.06 on a single member, failing A/H's criterion. **π_0 is a poor detector of an off-zoo strategy**; goodness-of-fit checks would have to do that job.
- **Censoring works with the hook:**
  - excluding runs truncated at a member-dependent rate biases that member's weight by 0.10–0.22;
  - giving the fit the true truncation rates as a `TokenModel` brings it back to within ±0.05 on most units. The exceptions are C E3 (−0.14), the two C E5 colouring units (−0.08) and C E5 entailment (+0.11).

## How to run it

```bash
OMP_NUM_THREADS=1 python -m reasoning_heuristics.identify.recovery run --items data/items/dev --label dev \
    --reps 40 --boot 100 --single-reps 10 --feature-reps 16 --feature-boot 30 --offzoo-reps 8 \
    --workers 8 --out data/recovery/dev.json
python -m reasoning_heuristics.identify.recovery report data/recovery/dev.json data/recovery/pc*.json
```

- Each item set is one command. The harness isn't tuned to the committed items, so it reruns as-is on the regenerated sets.
- Each result file records:
  - the command;
  - the git SHA, and whether the tree was dirty;
  - the sha256 of every item file it read;
  - the planted triple and the identifiability analysis of every unit.
- `merge` folds a rerun of some units into a result file and keeps both provenances. That's how the units whose planted triple changed when the rule began avoiding dependent members were rerun.
- `--units` takes unit names separated by `;`, since names contain commas. A name that matches no unit stops the run.
- Workers are processes, so set `OMP_NUM_THREADS=1`.

**Larger item sets for the sweep** are generated into a scratch directory, never into `data/items`. Generation is deterministic in code, tier, seed and parameters:

```bash
python -m reasoning_heuristics.generate --vertical V --eval E --tier dev --seed 1 --per-cell N --out-dir DIR
python -m reasoning_heuristics.identify.recovery run --items DIR/dev --label pcN --scenarios mix,null_q,null_always \
    --reps 100 --boot 100 --workers 4 --out data/recovery/pcN.json
```

## What is tested

**The engine** (`src/reasoning_heuristics/identify/`). Per fit unit (one eval × one domain; the response side adds model × condition) it fits P(y | x) = Σ_h π_h P(y | h, x) + π_0 q(y | x) by EM. Its components:

- **Likelihoods** are built from `predictions` + `instance` + the raw answer, not from the items' `disconfirms` tables. Set-valued members are rebuilt by validity: EXACT is uniform over every valid solution of the stated instance, and TT[exact] over the valid solutions under the textbook rule.
- **Near-miss slips** are the pre-registered noise model.
  - A deterministic or set-valued member gives its answer with probability 1 − ε. Otherwise D ~ truncated geometric(ρ) positions change: variables flipped, items or literals toggled, vertices recoloured up to renaming, or another decision or option.
  - The kernel is an exact pmf over the answer space. ε and ρ are estimated.
  - A prediction that is a special token (UNSAT, IMPOSSIBLE, X) does not slip: it has no near misses.
  - Distributional members are complete noise models and are used as stored.
- **q, "none of the above"**, is a uniformly random answer. With probability ½ it is a special token instead (UNSAT, IMPOSSIBLE) where the channel has one.
  - **C E3's bit channel is {same, different, IMPOSSIBLE}**, with q uniform over the three: the U-arm format admits IMPOSSIBLE, and FF-OUT and LF predict it on every U-REV item.
  - The items' stored outcome classes and the scorer's `outcome_class` lump IMPOSSIBLE with "other" on that channel.
- **Ties** are merged. Members with identical predictions on every item form one group, and a group identical to q is folded into the unexplained mass.
- **Linear dependencies** are found from the rank and null space of the (item, outcome) × (groups + q) matrix (`engine.identifiability`).
  - Every member of a dependency is reported as not identified, with the range of values consistent with the fit (π ≥ 0) and the identified combinations.
  - On finite channels a slip is a mixture with q, so ε is held at 0 there and π_0 includes slips.
- **Availability:** a member with no prediction on an item drops out there, and the other weights are renormalised (a Luce choice model).
- **95% intervals** come from a cluster bootstrap that resamples items sharing a base or a counterfactual set together. The percentile interval is the primary one. The BCa interval, with acceleration from a leave-one-cluster-out jackknife, is reported next to it on the same fits.

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
  - h2 is h1's nearest competitor: the group with the fewest separating items, more than zero;
  - h3 is the group of another family that is most separated from both.
  - Members of a linear dependency are avoided when three others remain.
- **Slips** are planted at ε = 0.1, ρ = 0.3 on witness channels, and not at all on finite channels.
- **The feature** is the first factor of the cell label that takes two values in the unit.

**The gates**, per unit and scenario, over replicates:

- |mean π̂ − π| ≤ 0.05 for every identified quantity, planted or absent, the unexplained mass included;
- the 95% interval contains the planted value in ≥ 90% of replicates, for every planted quantity;
- the median width over planted quantities and replicates is ≤ 0.2.

A scenario that plants weight on a member identified only in combination is **not testable on that unit**. It is listed separately, neither passed nor failed.

The gated scenarios are `single`, `mix`, `mix_uniform_slips`, `feature`, `null_q` and `null_always`. `off_zoo` has its own criterion (A/H §5.3 P6: < 0.2 of the withheld mass on any single member). `clustered`, `truncated` and the misspecification fits are checks.

## Results at the committed dev size

Item set `data/items/dev`, git 974633576d, 40 replicates × 100 bootstrap draws (10 per single member).

| Unit | items | clusters | single | mix | mix, uniform slips | feature | null q | null ALWAYS | all |
|---|---|---|---|---|---|---|---|---|---|
| AH_E1/COL | 20 | 10 | fail 3/7, 2 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E1/ENT | 20 | 10 | fail 3/12, 3 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E1/SAT | 30 | 15 | fail 5/10, 2 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E2/COL | 40 | 10 | fail 2/7, 3 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage) | not testable | not testable | fail (2 not testable) |
| AH_E2/ENT | 40 | 5 | fail 3/12, 2 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E2/SAT | 40 | 10 | fail 7/10, 2 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| AH_E5/COL | 20 | 5 | PASS | fail (bias, coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | PASS | fail (coverage) | fail |
| AH_E5/ENT | 20 | 5 | PASS | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | PASS | PASS | fail |
| AH_E5/KNAP | 20 | 5 | fail 4/6 | – | – | – | PASS | PASS | fail |
| AH_E5/SAT | 25 | 5 | PASS | fail (coverage, width) | fail (coverage, width) | fail (bias, coverage, width) | PASS | PASS | fail |
| B4C4_E1/entailment | 140 | 20 | fail 5/17 | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage) | fail (bias, coverage, width) | fail (bias, coverage) | fail |
| B4C4_E2/entailment | 240 | 25 | PASS, 9 not testable | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage, width) | not testable | not testable | fail (2 not testable) |
| C_E1/3-SAT | 30 | 5 | fail 2/10 | fail (coverage, width) | fail (coverage, width) | fail (coverage, width) | PASS | fail (bias, coverage) | fail |
| C_E1/colouring | 30 | 5 | fail 3/12 | fail (coverage, width) | fail (bias, coverage, width) | fail (coverage, width) | PASS | fail (bias, coverage) | fail |
| C_E2/3-SAT | 50 | 10 | fail 1/8 | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, coverage) | fail |
| C_E2/colouring | 75 | 15 | fail 2/9 | fail (coverage) | fail (coverage) | fail (coverage, width) | PASS | PASS | fail |
| C_E2/knapsack | 75 | 15 | PASS | fail (coverage, width) | fail (bias, coverage, width) | fail (coverage, width) | PASS | PASS | fail |
| C_E3/colouring (gadget) | 270 | 30 | fail 12/16 | fail (bias, coverage, width) | n/a (finite) | fail (bias, coverage) | fail (bias, coverage, width) | fail (bias, coverage) | fail |
| C_E5/3-SAT | 15 | 5 | fail 1/10 | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, width) | fail (bias, coverage) | fail |
| C_E5/3-SAT (partial assignment given) | 15 | 5 | fail 1/7 | fail (coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (width) | fail (bias, coverage, width) | fail |
| C_E5/colouring (k=3) | 25 | 5 | fail 2/12 | fail (bias, coverage) | fail (bias, coverage, width) | fail (bias, coverage) | fail (bias, coverage, width) | PASS | fail |
| C_E5/colouring (k=3, partial colouring given) | 10 | 5 | fail 2/6 | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | fail (bias, coverage, width) | PASS | fail |
| C_E5/propositional entailment | 20 | 5 | fail 3/8, 3 not testable | fail (bias, coverage) | n/a (finite) | fail (bias, coverage) | not testable | not testable | fail (2 not testable) |

**The 60/30/10 mixture in detail** (worst quantity for each gate):

| Unit | triple (0.6 / 0.3 / 0.1) | max \|bias\| | on | min coverage | on | median width |
|---|---|---|---|---|---|---|
| AH_E1/COL | A2 DENSITY-U / B1 DROP-CONSTRAINT(last 3) / H SAMPLE-8 | 0.079 | A2 DENSITY-U | 0.500 | H SAMPLE-8 | 0.483 |
| AH_E1/ENT | A2 FREQ / D case-split (b = 4) / H SAMPLE-8 | 0.080 | D case-split (b = 4) | 0.400 | H SAMPLE-8 | 0.667 |
| AH_E1/SAT | A2 LENGTH-M / B1 UP-3 / F WALK-200 | 0.090 | B1 UP-3 = D∘DENSITY | 0.475 | F WALK-200 | 0.440 |
| AH_E2/COL | A2 DENSITY-D / A2 LENGTH-M / NOISY-EXACT | 0.098 | NOISY-EXACT | 0.050 | NOISY-EXACT | 0.500 |
| AH_E2/ENT | A2 ATMOSPHERE / A2 PRIMACY / H SAMPLE-8 | 0.099 | H SAMPLE-8 | 0.200 | H SAMPLE-8 | 0.249 |
| AH_E2/SAT | A2 DENSITY-D / A2 LENGTH-M / F WALK-200 | 0.059 | F WALK-200 | 0.525 | F WALK-200 | 0.454 |
| AH_E5/COL | A3 TT[FIRST-FIT] / C1 FIRST-FIT (stated rule) / B1 DROP-CONSTRAINT(last 3) | 0.059 | D DPLL (first solution) | 0.675 | B1 DROP-CONSTRAINT(last 3) | 0.325 |
| AH_E5/ENT | A1 NONE / A3 TT[exact] / B4 FIRST | 0.064 | exact | 0.550 | B4 FIRST | 0.301 |
| AH_E5/KNAP | (no triple) ||||||
| AH_E5/SAT | C0 POLARITY / C1 GREEDY / A3 TT[exact] | 0.011 | C0 POLARITY | 0.625 | A3 TT[exact] | 0.240 |
| B4C4_E1/entailment | BICOND / ONL(2) / NOISY-EXACT | 0.093 | NOISY-EXACT | 0.000 | NOISY-EXACT | 0.332 |
| B4C4_E2/entailment | AFFIRM / C1-GREEDY / CW-MIN | 0.065 | CW-MIN | 0.325 | CW-MIN | 0.239 |
| C_E1/3-SAT | DPLL-INDEX (D, T first) / DPLL-MENTION (D, T first) / EXACT | 0.005 | EXACT | 0.725 | DPLL-MENTION (D, T first) | 0.242 |
| C_E1/colouring | FF-LABEL / DPLL-LABEL (D) / DSATUR | 0.040 | DSATUR | 0.550 | DSATUR | 0.246 |
| C_E2/3-SAT | GUC-DET (C2) / SC-DET (C2) / POLARITY (C0) | 0.154 | SC-DET (C2) | 0.550 | SC-DET (C2) | 0.296 |
| C_E2/colouring | FF-LABEL / DPLL-LIST (D) / EXACT | 0.012 | FF-LABEL | 0.825 | DPLL-LIST (D) | 0.176 |
| C_E2/knapsack | DIFF / RATIO-SKIP / EXACT | 0.011 | DIFF | 0.875 | RATIO-SKIP | 0.248 |
| C_E3/colouring (gadget) | DPLL-LIST (D, k=3) / DSATUR (C2, label ties) / LF (C1 static, label ties) | 0.311 | DPLL-LIST (D, k=3) = FF-LIST (C1 seq) | 0.000 | DPLL-LIST (D, k=3) = FF-LIST (C1 seq) | 0.210 |
| C_E5/3-SAT | GUC-DET (C2) / SC-DET (C2) / DPLL-MENTION (D) | 0.067 | q | 0.650 | SC-DET (C2) | 0.401 |
| C_E5/3-SAT (partial assignment given) | GREEDY-MENTION from state (C1) / GREEDY-MENTION-ABORT from state (C1) / POLARITY (C0, ignores state) | 0.037 | GREEDY-MENTION-ABORT from state (C1) | 0.725 | GREEDY-MENTION from state (C1) | 0.356 |
| C_E5/colouring (k=3) | FF-3-EDGE-MENTION-ABORT (C1 variant) / PHANTOM-ADJACENT (B4) / DPLL-LIST (D) | 0.105 | PHANTOM-ADJACENT (B4) | 0.325 | PHANTOM-ADJACENT (B4) | 0.163 |
| C_E5/colouring (k=3, partial colouring given) | FF-3-LIST from state (C1, ABORT) / DPLL-LIST from state (D) / RANDOM (H) | 0.109 | FF-3-LIST from state (C1, ABORT) | 0.700 | DPLL-LIST from state (D) = DSATUR-3 from state (C2) | 0.453 |
| C_E5/propositional entailment | ETR-1p (R1) / ETR-default (R1) / SAMPLE-3 (H) | 0.089 | SAMPLE-3 (H) | 0.075 | ETR-1p (R1) | 0.147 |

**Single members that fail** (the first gate each fails on, and its worst quantity):

- **AH_E1/COL**: H SAMPLE-8 (bias, coverage, width; bias 0.50 on H SAMPLE-8); NOISY-EXACT (bias, coverage, width; bias 0.78 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage; bias 0.66 on PERCEPTION-NOISE)
- **AH_E1/ENT**: H SAMPLE-8 (bias, coverage; bias 1.00 on H SAMPLE-8); NOISY-EXACT (bias, coverage; bias 1.00 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage; bias 1.00 on PERCEPTION-NOISE)
- **AH_E1/SAT**: F WALK-200 (bias, width; bias 0.17 on F WALK-200); H SAMPLE-8 (bias, coverage; bias 0.93 on H SAMPLE-8); NOISY-EXACT-READ (bias, coverage; bias 0.96 on NOISY-EXACT-READ); NOISY-EXACT-STEP (bias, coverage; bias 0.99 on NOISY-EXACT-STEP); PERCEPTION-NOISE (bias, coverage, width; bias 0.43 on PERCEPTION-NOISE)
- **AH_E2/COL**: NOISY-EXACT (bias, coverage, width; bias 0.78 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage, width; bias 0.43 on PERCEPTION-NOISE)
- **AH_E2/ENT**: H SAMPLE-8 (bias, coverage, width; bias 0.36 on H SAMPLE-8); NOISY-EXACT (bias, coverage; bias 1.00 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage; bias 0.91 on PERCEPTION-NOISE)
- **AH_E2/SAT**: C1 GREEDY (width; bias 0.00 on C1 GREEDY); D DPLL-b+PL (width; bias 0.00 on D DPLL-b+PL); F WALK-200 (bias, coverage, width; bias 0.08 on F WALK-200); H SAMPLE-8 (bias, coverage, width; bias 0.50 on H SAMPLE-8); NOISY-EXACT-READ (bias, coverage, width; bias 1.00 on NOISY-EXACT-READ); NOISY-EXACT-STEP (bias, coverage, width; bias 0.84 on NOISY-EXACT-STEP); PERCEPTION-NOISE (bias, coverage, width; bias 0.39 on PERCEPTION-NOISE)
- **AH_E5/KNAP**: C1 INPUT-FIT (coverage; bias 0.01 on q); C1 LARGEST-FIT (coverage; bias 0.02 on q); C1 RATIO-SKIP (coverage; bias 0.03 on q); C1 VALUE (coverage; bias 0.02 on q)
- **B4C4_E1/entailment**: AFFIRM = ALWAYS-YES (coverage; bias 0.02 on q); C1-GREEDY (bias, coverage; bias 0.24 on C1-GREEDY); NOISY-EXACT (bias, coverage; bias 1.00 on NOISY-EXACT); PERCEPTION-NOISE (bias, coverage, width; bias 0.74 on PERCEPTION-NOISE); SAMPLE-3 (coverage; bias 0.04 on q)
- **C_E1/3-SAT**: GREEDY-OUT (AR) (coverage; bias 0.01 on GREEDY-OUT (AR)); RO-GREEDY (C3) (bias, width; bias 0.07 on RO-GREEDY (C3))
- **C_E1/colouring**: FF-OUT (AR) (coverage; bias 0.01 on q); NOISY-EXACT (bias, coverage, width; bias 0.71 on NOISY-EXACT); RO-FF (C3) (bias, coverage, width; bias 0.18 on RO-FF (C3))
- **C_E2/3-SAT**: RO-GREEDY (C3) (width; bias 0.00 on RO-GREEDY (C3))
- **C_E2/colouring**: NOISY-EXACT (bias, coverage, width; bias 0.36 on NOISY-EXACT); RO-FF (C3) (bias, coverage, width; bias 0.16 on RO-FF (C3))
- **C_E3/colouring (gadget)**: DPLL-LIST (D, k=3) = FF-LIST (C1 seq) (bias, coverage; bias 0.78 on DPLL-LIST (D, k=3) = FF-LIST (C1 seq)); LOCAL-1-LIST (const proxy) (coverage; bias 0.04 on LOCAL-1-LIST (const proxy)); LOCAL-4-LIST (const proxy) (coverage; bias 0.04 on LOCAL-4-LIST (const proxy)); ANSWER-1 (A1 default; = LOCAL-0) (coverage; bias 0.03 on ANSWER-1 (A1 default; = LOCAL-0)); LOCAL-2-LIST (const proxy) (coverage; bias 0.02 on q); LOCAL-5-LIST (const proxy) (coverage; bias 0.04 on LOCAL-5-LIST (const proxy)); LOCAL-3-LIST (const proxy) (coverage; bias 0.03 on q); LOCAL-6-LIST (const proxy) (coverage; bias 0.03 on LOCAL-6-LIST (const proxy)); LOCAL-7-LIST (const proxy) (coverage; bias 0.01 on q); LOCAL-9-LIST (const proxy) (coverage; bias 0.03 on LOCAL-9-LIST (const proxy)); LOCAL-11-LIST (const proxy) (coverage; bias 0.02 on q); LOCAL-8-LIST (const proxy) (coverage; bias 0.04 on LOCAL-8-LIST (const proxy))
- **C_E5/3-SAT**: RO-GREEDY (C3) (width; bias 0.00 on RO-GREEDY (C3))
- **C_E5/3-SAT (partial assignment given)**: EXACT (bias, width; bias 0.07 on EXACT)
- **C_E5/colouring (k=3)**: NOISY-EXACT (bias, coverage, width; bias 0.52 on NOISY-EXACT); PHANTOM-ADJACENT (B4) (bias, coverage, width; bias 0.17 on PHANTOM-ADJACENT (B4))
- **C_E5/colouring (k=3, partial colouring given)**: EXACT (bias, coverage, width; bias 0.20 on EXACT); FF-3-LIST from state (C1, ABORT) (bias, width; bias 0.19 on FF-3-LIST from state (C1, ABORT))
- **C_E5/propositional entailment**: ETR-1p (R1) (width; bias 0.00 on ETR-1p (R1)); ETR-default (R1) (width; bias 0.00 on ETR-default (R1)); SAMPLE-3 (H) (bias, coverage, width; bias 0.73 on SAMPLE-3 (H))

**Linear dependencies** (`engine.identifiability`: rank of the (item, outcome) × (groups + q) matrix; witness channels on sampled outcomes). Every member of a dependency is identified only in combination; the fits report the identified combinations shown (one basis of them):

- **AH_E1/COL** (rank 9 of 10): `q = 0.5 × A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT = D DPLL-b + 0.5 × A1 ALWAYS-POSSIBLE = A2 DENSITY-D`. Not identified on their own: A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT = D DPLL-b, A1 ALWAYS-POSSIBLE = A2 DENSITY-D, q. Identified combinations reported: `A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT = D DPLL-b + 0.5 × q`; `A1 ALWAYS-POSSIBLE = A2 DENSITY-D + 0.5 × q`.
- **AH_E1/ENT** (rank 15 of 16): `q = 0.5 × A1 ALWAYS-YES + 0.5 × A1 NONE = A2 ATMOSPHERE = A2 DENSITY`. Not identified on their own: A1 ALWAYS-YES, A1 NONE = A2 ATMOSPHERE = A2 DENSITY, q. Identified combinations reported: `A1 ALWAYS-YES + 0.5 × q`; `A1 NONE = A2 ATMOSPHERE = A2 DENSITY + 0.5 × q`.
- **AH_E1/SAT** (rank 12 of 13): `q = 0.5 × A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY + 0.5 × A1 ALWAYS-UNSAT = C1 GREEDY`. Not identified on their own: A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY, A1 ALWAYS-UNSAT = C1 GREEDY, q. Identified combinations reported: `A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY + 0.5 × q`; `A1 ALWAYS-UNSAT = C1 GREEDY + 0.5 × q`.
- **AH_E2/COL** (rank 9 of 11): `q = 0.5 × A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT = D DPLL-b + 0.5 × A1 ALWAYS-POSSIBLE`; `H SAMPLE-8 = 1 × A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT = D DPLL-b`. Not identified on their own: A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT = D DPLL-b, A1 ALWAYS-POSSIBLE, H SAMPLE-8, q. Identified combinations reported: `A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT = D DPLL-b + 0.5 × q + 1 × H SAMPLE-8`; `A1 ALWAYS-POSSIBLE + 0.5 × q`.
- **AH_E2/ENT** (rank 14 of 15): `q = 0.5 × A1 ALWAYS-YES + 0.5 × A1 NONE = A2 DENSITY = B4 FIRST`. Not identified on their own: A1 ALWAYS-YES, A1 NONE = A2 DENSITY = B4 FIRST, q. Identified combinations reported: `A1 ALWAYS-YES + 0.5 × q`; `A1 NONE = A2 DENSITY = B4 FIRST + 0.5 × q`.
- **AH_E2/SAT** (rank 12 of 13): `q = 0.5 × A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY + 0.5 × A1 ALWAYS-UNSAT = C2 UC = D DPLL-b`. Not identified on their own: A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY, A1 ALWAYS-UNSAT = C2 UC = D DPLL-b, q. Identified combinations reported: `A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY + 0.5 × q`; `A1 ALWAYS-UNSAT = C2 UC = D DPLL-b + 0.5 × q`.
- **B4C4_E2/entailment** (rank 15 of 20): `q = 0.5 × ALWAYS-YES = BICOND + 0.5 × NONE`; `SAMPLE-3 = 0.125 × ALWAYS-YES = BICOND + 0.875 × ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1`; `PERCEPTION-NOISE = 0.93 × ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 + 0.0699 × NONE`; `NOISY-EXACT = 0.0149 × ALWAYS-YES = BICOND + 0.97 × ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 + 0.0149 × NONE`; `ETR-1p, ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1, MM-G, MM-S1 = MM-elim span only 3 directions (MM-S1 = MM-elim = 1 × ETR-1p + -1 × ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 + 1 × MM-G): their weights are identified only up to this combination`. Not identified on their own: ALWAYS-YES = BICOND, ETR-1p, ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1, MM-G, MM-S1 = MM-elim, NOISY-EXACT, NONE, PERCEPTION-NOISE, SAMPLE-3, q. Identified combinations reported: `ALWAYS-YES = BICOND + 0.5 × q + 0.125 × SAMPLE-3 + 0.0149 × NOISY-EXACT`; `ETR-1p + 1 × MM-S1 = MM-elim`; `ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 + 0.875 × SAMPLE-3 + 0.93 × PERCEPTION-NOISE + 0.97 × NOISY-EXACT + -1 × MM-S1 = MM-elim`; `MM-G + 1 × MM-S1 = MM-elim`; `NONE + 0.5 × q + 0.0699 × PERCEPTION-NOISE + 0.0149 × NOISY-EXACT`.
- **C_E5/propositional entailment** (rank 10 of 12): `q = 0.5 × ALWAYS-YES (A1) + 0.5 × MM-S1 (B4) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound)`; `NOISY-EXACT = 0.0386 × ALWAYS-YES (A1) + 0.961 × MM-S1 (B4) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound)`. Not identified on their own: ALWAYS-YES (A1), MM-S1 (B4) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound), NOISY-EXACT, q. Identified combinations reported: `ALWAYS-YES (A1) + 0.5 × q + 0.0386 × NOISY-EXACT`; `MM-S1 (B4) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound) + 0.5 × q + 0.961 × NOISY-EXACT`.
- Full rank: AH_E5/COL, AH_E5/ENT, AH_E5/KNAP, AH_E5/SAT, B4C4_E1/entailment, C_E1/3-SAT, C_E1/colouring, C_E2/3-SAT, C_E2/colouring, C_E2/knapsack, C_E3/colouring (gadget), C_E5/3-SAT, C_E5/3-SAT (partial assignment given), C_E5/colouring (k=3), C_E5/colouring (k=3, partial colouring given).

**Identifiability diagnostics** (finite channels: rank of the (item, value) × (groups + q) design; A/H §5.3 asks for σ_min/σ_max ≥ 0.05) and the least-separated pairs:

| Unit | rank / columns | σ ratio | weakest direction | least-separated pair (items) |
|---|---|---|---|---|
| AH_E1/COL | 9 / 10 | 0.0 | q, A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT = D DPLL-b, A1 ALWAYS-POSSIBLE = A2 DENSITY-D | A1 ALWAYS-POSSIBLE = A2 DENSITY-D vs A2 DENSITY-U (2) |
| AH_E1/ENT | 15 / 16 | 0.0 | q, A1 NONE = A2 ATMOSPHERE = A2 DENSITY, A1 ALWAYS-YES | B1 UP-1 vs B1 UP-2 = B1 UP-3 (1) |
| AH_E1/SAT | 12 / 13 | 0.0 | q, A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY, A1 ALWAYS-UNSAT = C1 GREEDY | C2 UC vs D DPLL-b (3) |
| AH_E2/COL | 10 / 11 | 0.0 | q, A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT = D DPLL-b, A1 ALWAYS-POSSIBLE | A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT = D DPLL-b vs B4 ADD-CONSTRAINT(adjacent) (2) |
| AH_E2/ENT | 14 / 15 | 0.0 | q, A1 NONE = A2 DENSITY = B4 FIRST, A1 ALWAYS-YES | A1 NONE = A2 DENSITY = B4 FIRST vs A2 RECENCY (2) |
| AH_E2/SAT | 12 / 13 | 0.0 | q, A1 ALWAYS-UNSAT = C2 UC = D DPLL-b, A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY | A1 ALWAYS-UNSAT = C2 UC = D DPLL-b vs C1 GREEDY (1) |
| AH_E5/COL | (witness channel) | | | B1 DROP-CONSTRAINT(last 3) vs C2 DSATUR (stated rule) (8) |
| AH_E5/ENT | (witness channel) | | | B4 FIRST vs exact (8) |
| AH_E5/KNAP | (witness channel) | | | C1 RATIO-SKIP vs C1 VALUE (6) |
| AH_E5/SAT | (witness channel) | | | A3 TT[exact] vs exact (15) |
| B4C4_E1/entailment | 18 / 18 | 0.0004 | BICOND = CW-COMP = CW-MIN = EXACT = MM-G = MM-S1 = ONL(4), NOISY-EXACT | FIRST vs ONL(1) = ONL(1)-strict (5) |
| B4C4_E2/entailment | 15 / 20 | 0.0 | ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1, PERCEPTION-NOISE, MM-G, MM-S1 = MM-elim | MM-G vs ONL(1) = ONL(1)-strict (10) |
| C_E1/3-SAT | (witness channel) | | | DPLL-MENTION (D, T first) vs UC-DET (C2) (14) |
| C_E1/colouring | (witness channel) | | | DSATUR vs DSATUR-LABEL (2) |
| C_E2/3-SAT | (witness channel) | | | GUC-DET (C2) vs SC-DET (C2) (6) |
| C_E2/colouring | (witness channel) | | | DSATUR vs DSATUR-LABEL (45) |
| C_E2/knapsack | (witness channel) | | | DIFF vs RATIO-SKIP (38) |
| C_E3/colouring (gadget) | 17 / 17 | 0.1166 | DPLL-LIST (D, k=3) = FF-LIST (C1 seq), LOCAL-5-LIST (const proxy), LOCAL-11-LIST (const proxy), LOCAL-7-LIST (const proxy) | LOCAL-2-LIST (const proxy) vs LOCAL-5-LIST (const proxy) (24) |
| C_E5/3-SAT | (witness channel) | | | GUC-DET (C2) vs SC-DET (C2) (4) |
| C_E5/3-SAT (partial assignment given) | (witness channel) | | | DPLL from state (D) vs UC-DET from state (C2) (2) |
| C_E5/colouring (k=3) | (witness channel) | | | FF-3-EDGE-MENTION-ABORT (C1 variant) vs PHANTOM-ADJACENT (B4) (2) |
| C_E5/colouring (k=3, partial colouring given) | (witness channel) | | | DPLL-LIST from state (D) = DSATUR-3 from state (C2) vs EXACT (5) |
| C_E5/propositional entailment | 10 / 12 | 0.0 | NOISY-EXACT, MM-S1 (B4) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound), q | ETR-1p (R1) vs ETR-default (R1) (2) |

## Items per cell needed

The sweep reruns `mix`, `null_q` and `null_always` on dev-tier item sets generated at 10, 20 and 40 items per cell (30 replicates, 60 bootstrap draws). For each unit and size, the table gives the 60/30/10 mixture's worst bias (b), its smallest per-weight coverage (c) and its median width (w), then the `null_q` verdict.

| Unit | dev (items/cell) | pc10 (items/cell) | pc20 (items/cell) | pc40 (items/cell) |
|---|---|---|---|---|
| AH_E1/COL | 5: mix fail (b 0.079, c 0.500, w 0.483); q not testable | 10: mix fail (b 0.088, c 0.300, w 0.410); q not testable | 20: mix fail (b 0.098, c 0.000, w 0.347); q not testable | 40: mix fail (b 0.100, c 0.000, w 0.242); q not testable |
| AH_E1/ENT | 5: mix fail (b 0.080, c 0.400, w 0.667); q not testable | 10: mix fail (b 0.160, c 0.033, w 0.182); q not testable | 20: mix fail (b 0.140, c 0.000, w 0.362); q not testable | 40: mix fail (b 0.094, c 0.100, w 0.306); q not testable |
| AH_E1/SAT | 5: mix fail (b 0.090, c 0.475, w 0.440); q not testable | 10: mix fail (b 0.100, c 0.100, w 0.454); q not testable | 20: mix fail (b 0.057, c 0.500, w 0.368); q not testable | 40: mix fail (b 0.065, c 0.500, w 0.244); q not testable |
| AH_E2/COL | 5: mix fail (b 0.098, c 0.050, w 0.500); q not testable | 10: mix fail (b 0.098, c 0.033, w 0.382); q not testable | 20: mix fail (b 0.084, c 0.167, w 0.257); q not testable | 40: mix fail (b 0.096, c 0.033, w 0.185); q not testable |
| AH_E2/ENT | 5: mix fail (b 0.099, c 0.200, w 0.249); q not testable | 10: mix fail (b 0.092, c 0.133, w 0.269); q not testable | 20: mix fail (b 0.077, c 0.500, w 0.200); q not testable | 40: mix fail (b 0.089, c 0.100, w 0.150); q not testable |
| AH_E2/SAT | 5: mix fail (b 0.059, c 0.525, w 0.454); q not testable | 10: mix fail (b 0.050, c 0.567, w 0.373); q not testable | 20: mix fail (b 0.088, c 0.767, w 0.410); q not testable | 40: mix fail (b 0.065, c 0.900, w 0.416); q not testable |
| AH_E5/COL | 5: mix fail (b 0.059, c 0.675, w 0.325); q PASS | 10: mix fail (b 0.039, c 0.800, w 0.296); q PASS | 20: mix fail (b 0.028, c 0.833, w 0.239); q PASS | 40: mix fail (b 0.011, c 0.867, w 0.173); q PASS |
| AH_E5/ENT | 5: mix fail (b 0.064, c 0.550, w 0.301); q PASS | 10: mix fail (b 0.028, c 0.767, w 0.237); q PASS | 20: mix fail (b 0.045, c 0.767, w 0.184); q PASS | 40: mix PASS (b 0.026, c 0.933, w 0.131); q PASS |
| AH_E5/KNAP | 5: mix –; q PASS | 10: mix –; q fail | 20: mix –; q fail | 40: mix –; q PASS |
| AH_E5/SAT | 5: mix fail (b 0.011, c 0.625, w 0.240); q PASS | 10: mix fail (b 0.006, c 0.867, w 0.191); q PASS | 20: mix PASS (b 0.015, c 0.933, w 0.153); q PASS | 40: mix PASS (b 0.007, c 0.900, w 0.108); q PASS |
| B4C4_E1/entailment | 5: mix fail (b 0.093, c 0.000, w 0.332); q fail | 10: mix fail (b 0.100, c 0.000, w 0.264); q fail | 20: mix fail (b 0.083, c 0.067, w 0.192); q fail | 40: mix fail (b 0.096, c 0.033, w 0.130); q fail |
| B4C4_E2/entailment | 5: mix fail (b 0.065, c 0.325, w 0.239); q not testable | 10: mix fail (b 0.059, c 0.333, w 0.163); q not testable | 20: mix fail (b 0.041, c 0.300, w 0.120); q not testable | 40: mix fail (b 0.028, c 0.267, w 0.094); q not testable |
| C_E1/3-SAT | 5: mix fail (b 0.005, c 0.725, w 0.242); q PASS | 10: mix fail (b 0.011, c 0.833, w 0.198); q PASS | 20: mix fail (b 0.005, c 0.833, w 0.145); q PASS | 40: mix PASS (b 0.002, c 0.900, w 0.110); q PASS |
| C_E1/colouring | 5: mix fail (b 0.040, c 0.550, w 0.246); q PASS | 10: mix fail (b 0.019, c 0.767, w 0.220); q PASS | 20: mix fail (b 0.008, c 0.767, w 0.175); q PASS | 40: mix fail (b 0.004, c 0.867, w 0.122); q PASS |
| C_E2/3-SAT | 5: mix fail (b 0.154, c 0.550, w 0.296); q fail | 10: mix fail (b 0.054, c 0.033, w 0.169); q fail | 20: mix fail (b 0.006, c 0.900, w 0.238); q PASS | 40: mix fail (b 0.003, c 0.867, w 0.187); q PASS |
| C_E2/colouring | 5: mix fail (b 0.012, c 0.825, w 0.176); q PASS | 10: mix PASS (b 0.007, c 0.933, w 0.135); q PASS | 20: mix fail (b 0.005, c 0.800, w 0.095); q PASS | 40: mix fail (b 0.001, c 0.867, w 0.066); q PASS |
| C_E2/knapsack | 5: mix fail (b 0.011, c 0.875, w 0.248); q PASS | 10: mix fail (b 0.016, c 0.867, w 0.195); q fail | 20: mix PASS (b 0.008, c 0.900, w 0.149); q fail | 40: mix fail (b 0.002, c 0.867, w 0.105); q fail |
| C_E3/colouring (gadget) | 5: mix fail (b 0.311, c 0.000, w 0.210); q fail | 10: mix fail (b 0.233, c 0.133, w 0.184); q fail | 20: mix fail (b 0.159, c 0.167, w 0.126); q fail | 40: mix fail (b 0.137, c 0.067, w 0.115); q fail |
| C_E5/3-SAT | 5: mix fail (b 0.067, c 0.650, w 0.401); q fail | 10: mix fail (b 0.044, c 0.867, w 0.371); q fail | 20: mix fail (b 0.020, c 0.867, w 0.362); q PASS | 40: mix fail (b 0.005, c 0.767, w 0.232); q PASS |
| C_E5/3-SAT (partial assignment given) | 5: mix fail (b 0.037, c 0.725, w 0.356); q fail | 10: mix fail (b 0.046, c 0.833, w 0.279); q PASS | 20: mix fail (b 0.007, c 0.867, w 0.235); q PASS | 40: mix fail (b 0.015, c 0.867, w 0.170); q PASS |
| C_E5/colouring (k=3) | 5: mix fail (b 0.105, c 0.325, w 0.163); q fail | 10: mix fail (b 0.100, c 0.567, w 0.223); q fail | 20: mix fail (b 0.066, c 0.767, w 0.364); q fail | 40: mix fail (b 0.064, c 0.867, w 0.404); q fail |
| C_E5/colouring (k=3, partial colouring given) | 5: mix fail (b 0.109, c 0.700, w 0.453); q fail | 10: mix fail (b 0.131, c 0.833, w 0.469); q fail | 20: mix fail (b 0.120, c 0.733, w 0.338); q fail | 40: mix fail (b 0.070, c 0.600, w 0.238); q fail |
| C_E5/propositional entailment | 5: mix fail (b 0.089, c 0.075, w 0.147); q not testable | 10: mix fail (b 0.092, c 0.033, w 0.167); q not testable | 20: mix fail (b 0.131, c 0.167, w 0.118); q not testable | 40: mix fail (b 0.072, c 0.300, w 0.539); q not testable |

| Unit | bias and width pass from (items/cell) | all three gates pass at |
|---|---|---|
| AH_E1/COL | not reached | – |
| AH_E1/ENT | not reached | – |
| AH_E1/SAT | not reached | – |
| AH_E2/COL | not reached | – |
| AH_E2/ENT | not reached | – |
| AH_E2/SAT | not reached | – |
| AH_E5/COL | 40 | – |
| AH_E5/ENT | 20 | 40 |
| AH_E5/KNAP | no planted triple (fewer than 3 members on every item) | – |
| AH_E5/SAT | 10 | 20, 40 |
| B4C4_E1/entailment | not reached | – |
| B4C4_E2/entailment | 20 | – |
| C_E1/3-SAT | 10 | 40 |
| C_E1/colouring | 20 | – |
| C_E2/3-SAT | 40 | – |
| C_E2/colouring | 5 | 10 |
| C_E2/knapsack | 10 | 20 |
| C_E3/colouring (gadget) | not reached | – |
| C_E5/3-SAT | not reached | – |
| C_E5/3-SAT (partial assignment given) | 40 | – |
| C_E5/colouring (k=3) | not reached | – |
| C_E5/colouring (k=3, partial colouring given) | not reached | – |
| C_E5/propositional entailment | not reached | – |


**Reading the sweep.**

- **Bias and width** fall as expected on the witness units. Width shrinks roughly as 1/√(items per cell), so the dev widths of 0.16–0.45 reach 0.2 at about 5 × (w_dev / 0.2)² items per cell.
- **Coverage is the binding gate.** At 20 and 40 per cell it sits at 0.77–0.93 per weight on units whose bias is under 0.02.
  - Thirty replicates give a binomial SE of about 0.05 per coverage, and the gate takes the minimum over three weights. A calibrated 95% interval would show a minimum ≤ 0.87 in about one run in six.
  - The 100-replicate check below separates the two.
- **For the power analysis**, on the current items and zoo, as items per cell:
  - C E2 colouring and knapsack and A/H E5 SAT need about 10–20;
  - C E1, C E2 SAT, A/H E5 colouring and entailment, and C E5 SAT with a given state need about 40, coverage permitting;
  - C E5 SAT and colouring need more than 40 (widths 0.23–0.40 at 40);
  - C E5 colouring with a given state improves slowly (bias 0.07, width 0.24 at 40 per cell);
  - C E5 colouring (k = 3) does not improve (a near-tie);
  - the decision-channel units, B4/C4 E1 and C E3 fail for reasons that more items do not fix (below).

**Coverage with 100 replicates.** Thirty replicates can't tell a calibrated interval from a slightly short one. So the 60/30/10 mixture was rerun at 40 items per cell, with 100 replicates and 100 bootstrap draws, on the eight witness units whose bias and width already passed there (`pre-regeneration/coverage_pc40.json`):

| Unit | all three gates | coverage of each planted weight (± binomial SE) | max \|bias\| | median width |
|---|---|---|---|---|
| AH_E5/COL | fail | A3 TT[FIRST-FIT] (0.6): 0.99 ± 0.01; C1 FIRST-FIT (stated rule) (0.3): 0.92 ± 0.03; exact (0.1): 0.84 ± 0.04 | 0.019 | 0.185 |
| AH_E5/SAT | PASS | C0 POLARITY (0.6): 0.91 ± 0.03; C1 GREEDY (0.3): 0.91 ± 0.03; A3 TT[exact] (0.1): 0.92 ± 0.03 | 0.001 | 0.111 |
| C_E1/3-SAT | PASS | DPLL-INDEX (D, T first) (0.6): 0.90 ± 0.03; DPLL-MENTION (D, T first) (0.3): 0.90 ± 0.03; EXACT (0.1): 0.90 ± 0.03 | 0.003 | 0.113 |
| C_E1/colouring | fail | FF-LABEL (0.6): 0.90 ± 0.03; DPLL-LABEL (D) (0.3): 0.88 ± 0.03; DSATUR (0.1): 0.94 ± 0.02 | 0.006 | 0.138 |
| C_E2/3-SAT | PASS | GUC-DET (C2) (0.6): 0.94 ± 0.02; SC-DET (C2) (0.3): 0.94 ± 0.02; POLARITY (C0) (0.1): 0.95 ± 0.02 | 0.001 | 0.174 |
| C_E2/colouring | PASS | FF-LABEL (0.6): 0.90 ± 0.03; DSATUR-LABEL (0.3): 0.92 ± 0.03; EXACT (0.1): 0.93 ± 0.03 | 0.001 | 0.070 |
| C_E2/knapsack | PASS | DIFF (0.6): 0.95 ± 0.02; RATIO-SKIP (0.3): 0.90 ± 0.03; EXACT (0.1): 0.90 ± 0.03 | 0.002 | 0.112 |
| C_E5/3-SAT (partial assignment given) | PASS | GREEDY-MENTION from state (C1) (0.6): 0.92 ± 0.03; GREEDY-MENTION-ABORT from state (C1) (0.3): 0.93 ± 0.03; POLARITY (C0, ignores state) (0.1): 0.93 ± 0.03 | 0.002 | 0.176 |

Six of the eight pass all three gates. The misses are the 0.1 EXACT weight on A/H E5 colouring (0.84) and C E1 colouring's 0.3 DPLL-LABEL weight (0.88). At 40 items per cell, then, the percentile cluster bootstrap covers close to nominal on the witness units, slightly short for some weights. The 30-replicate misses in the sweep were mostly binomial noise. A principled alternative (BCa) is to be compared against it on the regenerated sets.

## Misspecification: the uniform slip model on near-miss data

Same data (the near-miss 60/30/10 fake model), two fits. The table gives each fit's worst bias and smallest coverage, and the quantity the bias lands on.

| Unit | near-miss fit: max \|bias\| / min coverage | uniform fit on near-miss data | on | near-miss fit on uniform data | on |
|---|---|---|---|---|---|
| AH_E5/COL | 0.059 / 0.675 | 0.094 / 0.550 | q | 0.071 / 0.525 | C1 FIRST-FIT (stated rule) |
| AH_E5/ENT | 0.064 / 0.550 | 0.091 / 0.600 | q | 0.064 / 0.650 | exact |
| AH_E5/SAT | 0.011 / 0.625 | 0.102 / 0.775 | q | 0.034 / 0.750 | C0 POLARITY |
| C_E1/3-SAT | 0.005 / 0.725 | 0.083 / 0.775 | q | 0.058 / 0.775 | DPLL-INDEX (D, T first) |
| C_E1/colouring | 0.040 / 0.550 | 0.099 / 0.550 | q | 0.097 / 0.725 | FF-LABEL |
| C_E2/3-SAT | 0.154 / 0.550 | 0.175 / 0.550 | q | 0.147 / 0.575 | GUC-DET (C2) |
| C_E2/colouring | 0.012 / 0.825 | 0.066 / 0.700 | q | 0.053 / 0.725 | FF-LABEL |
| C_E2/knapsack | 0.011 / 0.875 | 0.098 / 0.750 | q | 0.037 / 0.800 | RATIO-SKIP |
| C_E5/3-SAT | 0.067 / 0.650 | 0.177 / 0.600 | q | 0.120 / 0.575 | GUC-DET (C2) |
| C_E5/3-SAT (partial assignment given) | 0.037 / 0.725 | 0.154 / 0.725 | q | 0.081 / 0.675 | GREEDY-MENTION-ABORT from state (C1) |
| C_E5/colouring (k=3) | 0.105 / 0.325 | 0.183 / 0.325 | q | 0.141 / 0.200 | FF-3-EDGE-MENTION-ABORT (C1 variant) |
| C_E5/colouring (k=3, partial colouring given) | 0.109 / 0.700 | 0.150 / 0.700 | q | 0.093 / 0.625 | DPLL-LIST from state (D) = DSATUR-3 from state (C2) |

Fitting slips as uniform over the candidate answers, when they are really near misses, sends the near misses to q. The unexplained mass is overstated by 0.07–0.18 on every witness unit, against 0.005–0.15 for the matched fit. The reverse (near-miss fit on uniform-slip data) costs less, 0.03–0.15, and lands on a planted member. This repeats the C vertical's recovery finding (SCOPE §6 rule 3): the slip model is part of the pre-registration, and its rate is estimated, not fixed.

## Off-zoo: where a withheld procedure's weight goes

0.7 on the triple's first member, 0.3 on a group the fit does not have, each group in turn. Means over 8 replicates.

| Unit | withheld groups | to q (mean) | onto h1 (mean excess) | onto other members (mean) | groups with ≥ 0.2 of the withheld 0.3 on one member |
|---|---|---|---|---|---|
| AH_E1/COL | 8 | 0.003 | -0.054 | 0.351 | 2 of 8 |
| AH_E1/ENT | 13 | 0.001 | -0.051 | 0.350 | 2 of 13 |
| AH_E1/SAT | 11 | 0.004 | -0.009 | 0.306 | 2 of 11 |
| AH_E2/COL | 9 | 0.014 | +0.013 | 0.272 | 1 of 9 |
| AH_E2/ENT | 13 | 0.009 | +0.012 | 0.279 | 2 of 13 |
| AH_E2/SAT | 11 | 0.001 | -0.022 | 0.321 | 2 of 11 |
| AH_E5/COL | 6 | 0.034 | +0.028 | 0.238 | 6 of 6 |
| AH_E5/ENT | 3 | 0.027 | +0.041 | 0.233 | 3 of 3 |
| AH_E5/SAT | 4 | 0.056 | +0.067 | 0.178 | 4 of 4 |
| B4C4_E1/entailment | 14 | 0.008 | -0.054 | 0.346 | 14 of 14 |
| B4C4_E2/entailment | 18 | 0.000 | -0.007 | 0.307 | 0 of 18 |
| C_E1/3-SAT | 8 | 0.041 | -0.006 | 0.265 | 8 of 8 |
| C_E1/colouring | 10 | 0.054 | -0.005 | 0.251 | 8 of 10 |
| C_E2/3-SAT | 7 | 0.061 | -0.108 | 0.347 | 7 of 7 |
| C_E2/colouring | 8 | 0.038 | +0.011 | 0.251 | 7 of 8 |
| C_E2/knapsack | 6 | 0.079 | +0.096 | 0.126 | 5 of 6 |
| C_E3/colouring (gadget) | 2 | 0.032 | -0.456 | 0.724 | 2 of 2 |
| C_E5/3-SAT | 9 | 0.033 | -0.049 | 0.315 | 9 of 9 |
| C_E5/3-SAT (partial assignment given) | 6 | 0.037 | +0.061 | 0.202 | 5 of 6 |
| C_E5/colouring (k=3) | 11 | 0.083 | -0.090 | 0.307 | 11 of 11 |
| C_E5/colouring (k=3, partial colouring given) | 5 | 0.203 | -0.155 | 0.252 | 4 of 5 |
| C_E5/propositional entailment | 10 | 0.053 | -0.085 | 0.332 | 0 of 10 |

**Most of the withheld 0.3 lands on zoo members, not on q.**
- q receives 0.00–0.08, and 0.20 only on the 10-item C E5 state colouring unit.
- The members whose near-miss kernels reach the withheld answers absorb the rest. A/H's criterion asks that no single member take 0.2 of the withheld mass. It fails for nearly every withheld group on every unit where q is identified; the decision units mostly can't be judged, because q isn't identified there.
- So a small π_0 does not show that the zoo is complete. Off-zoo strategies have to be caught by goodness-of-fit: posterior-predictive checks per cell, and model comparison against an extended zoo.

## Checks: clustered strategies and censoring

| Unit | clustered: max \|bias\| / min coverage / width | truncated, excluded: bias on h1 | truncated, token model: bias on h1 |
|---|---|---|---|
| AH_E1/COL | 0.056 / 0.600 / 0.465 | -0.106 | -0.055 |
| AH_E1/ENT | 0.092 / 0.550 / 0.750 | -0.117 | 0.021 |
| AH_E1/SAT | 0.069 / 0.400 / 0.468 | -0.135 | -0.050 |
| AH_E2/COL | 0.094 / 0.125 / 0.500 | -0.096 | -0.011 |
| AH_E2/ENT | 0.070 / 0.225 / 0.433 | -0.128 | 0.011 |
| AH_E2/SAT | 0.086 / 0.275 / 0.400 | -0.138 | -0.008 |
| AH_E5/COL | 0.023 / 0.375 / 0.600 | -0.148 | -0.040 |
| AH_E5/ENT | 0.028 / 0.375 / 0.604 | -0.129 | -0.006 |
| AH_E5/SAT | 0.026 / 0.425 / 0.600 | -0.135 | -0.001 |
| B4C4_E1/entailment | 0.100 / 0.000 / 0.600 | -0.014 | 0.013 |
| B4C4_E2/entailment | 0.090 / 0.500 / 0.358 | -0.122 | 0.005 |
| C_E1/3-SAT | 0.039 / 0.400 / 0.604 | -0.133 | -0.006 |
| C_E1/colouring | 0.044 / 0.400 / 0.607 | -0.131 | -0.018 |
| C_E2/3-SAT | 0.143 / 0.650 / 0.500 | -0.177 | -0.027 |
| C_E2/colouring | 0.003 / 0.800 / 0.436 | -0.112 | 0.009 |
| C_E2/knapsack | 0.010 / 0.700 / 0.459 | -0.098 | -0.008 |
| C_E3/colouring (gadget) | 0.546 / 0.000 / 0.103 | -0.330 | -0.135 |
| C_E5/3-SAT | 0.035 / 0.350 / 0.599 | -0.044 | -0.051 |
| C_E5/3-SAT (partial assignment given) | 0.055 / 0.325 / 0.600 | -0.064 | 0.004 |
| C_E5/colouring (k=3) | 0.077 / 0.075 / 0.154 | -0.165 | -0.082 |
| C_E5/colouring (k=3, partial colouring given) | 0.125 / 0.350 / 0.600 | -0.189 | -0.080 |
| C_E5/propositional entailment | 0.100 / 0.025 / 0.147 | -0.216 | 0.107 |

- **Clustered.** When every variant of a base is answered by the same member, the realised mixture varies with only 5–30 clusters per unit. The cluster bootstrap widens (to 0.4–0.6 on most units), but coverage still falls to 0.0–0.8 at dev size. The study needs more bases per unit, not more variants per base.
- **Censoring.** Excluding truncated runs biases the frequently truncated member by 0.10–0.22 on most units (0.33 on C E3). With the true truncation probabilities as the token model, that bias drops to within ±0.05 on most units; C E3, the C E5 colouring units and C E5 entailment keep 0.08–0.14.
  - The hook works; the missing piece is a fitted token model that predicts each member's tokens on each item.

## What fails, and why

1. **Weights the items can't identify** (see Limitations): q and the constant groups on two-valued channels; noise models that are fixed mixtures of procedures; and a four-way dependency among procedures on B4/C4 E2. Scenarios that plant weight on them are not testable, at any size, on these designs.
2. **Near-dependencies on two-valued channels.** At full rank a binary answer still carries one bit per item, and these units have 9–18 groups.
   - Noise models (SAMPLE-m, WALK-200, NOISY-EXACT, PERCEPTION-NOISE) are nearly fixed mixtures of the procedures. A planted noise model is lost (bias 0.06–0.10 at 0.1 weight; most single-member scenarios for these fail by 0.4–1.0).
   - B4/C4 E1 is the extreme case: σ_min/σ_max = 0.0004, EXACT group vs NOISY-EXACT.
   - More items don't fix this. Items on which the noise models' probabilities vary independently of the procedures would.
3. **Procedures that agree on most items.**
   - C E3's FF-LIST (= DPLL-LIST) loses 0.14–0.31 of its 0.6 to the LOCAL-t proxies, which agree with it whenever the target is within their horizon. Only the deep items separate them, and the leak shrinks slowly with size (0.31 at dev, 0.23 at 10, 0.16 at 20, 0.14 at 40 per cell).
   - C E5 colouring (k = 3): FF-3-EDGE-MENTION-ABORT vs PHANTOM-ADJACENT differ on 2 of 25 items, and the interval widths stay near 0.4 even at 40 per cell.
   - C E1 colouring: DSATUR vs DSATUR-LABEL differ on 2 of 30 items.
4. **Coverage.** See the sweep and the coverage check.
5. **The constant responder is credited to a member.** This is correct given the zoo, but it fails `null_always`:
   - on the C SAT units an always-UNSAT responder goes to RO-GREEDY, whose stored distribution puts 0.5 on UNSAT;
   - on C E1 colouring, the one-colour answer goes to LOCAL-2-ID, whose answer is nearly all colour 1, via near-miss slips;
   - on C E3 the constant bit goes to the LOCAL-t proxies, and on B4/C4 E1 to the members that answer YES or A.
6. **Small units.** C E5's state units (10–15 items at dev) and A/H E5 (20–25 items, 5 clusters) need several times the items before the width gate can pass.

## Limitations: what the items cannot identify, and what would fix it

`engine.identifiability` computes the rank and null space of the (item, outcome) × (groups + q) matrix for every unit. On finite channels the matrix is exact, with ε = 0. On witness channels it uses the candidate answers plus draws from every component.

A dependency means no amount of data on these items separates the members involved: only combinations of their weights are identified. The engine reports each involved weight as *not identified*, with the range of values consistent with the fit (π ≥ 0). The harness marks a scenario *not testable* when it plants weight on any such member, whichever member the elimination happens to pick as the pivot. On the committed dev sets:

1. **q on two-valued channels: all six A/H decision units, B4/C4 E2 and C E5 entailment.**
   - On a YES/NO (SAT/UNSAT, POSSIBLE/IMPOSSIBLE) channel, the uniform q equals ½ always-positive + ½ always-negative on every item. In fact any item-independent q is some such mixture.
   - So wherever the zoo has a constant-positive and a constant-negative group, the unexplained mass is not identified. Those groups are the ALWAYS members, plus any member that happens to give the same answer on every item of the unit: C1 GREEDY = ALWAYS-UNSAT on A/H E1 SAT, and C E5 entailment's EXACT group, which answers NO on every item.
   - Only π_pos + π_0/2 and π_neg + π_0/2 are estimable, and `null_q` is not testable there.
   - **Fixes:**
     - score these items on a channel with more than two outcomes. The A/H formats already ask for a witness, which would make q identifiable; alternatively add a third answer such as "cannot tell";
     - balance the ground truth within each unit, so EXACT is not constant (C E5 entailment);
     - or pre-register that on decision channels π_0 is reported only through these combinations.
2. **Noise models that are fixed mixtures of procedures:** B4/C4 E2's SAMPLE-3, PERCEPTION-NOISE and NOISY-EXACT; C E5 entailment's NOISY-EXACT; A/H E2 colouring's SAMPLE-8.
   - On these items each one's answer distribution is the same mixture of other members on every item. For example, NOISY-EXACT = 0.97 × the EXACT group + 0.015 × ALWAYS-YES + 0.015 × NONE on all 240 B4/C4 E2 items, because its flip rate does not vary.
   - SAMPLE-8 never finds a colouring of these graphs, so it equals ALWAYS-IMPOSSIBLE to 10⁻⁷. The pairwise tie test missed this.
   - **Fix:** vary the instances along the dimension the noise model depends on (sizes and step counts for NOISY-EXACT, colouring density for SAMPLE-m), or merge these members with the procedures they reduce to.
3. **A dependency among procedures (B4/C4 E2).**
   - ETR-1p, the EXACT group (ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1), MM-G and MM-S1 (= MM-elim) span only three directions. On every one of the 48 cells, MM-S1's answer is ETR-1p's + MM-G's − the EXACT group's.
   - Their weights are identified only up to this combination, whichever member is named the pivot.
   - **This is a design gap for H6**, which asks whether cognitive members explain errors better than surface ones. H6 needs B4/C4 items that separate MM-S1 from the ETR-1p / MM-G / EXACT combination, i.e. inference forms on which that identity fails.
   - The zoo fixes (MM-S1's implicit models, MATCH-A's order dependence) may change this dependency, so the regenerated items need the same analysis. `run` records it per unit (`identifiability`).
4. **Near-dependencies.**
   - B4/C4 E1 is full rank, but its σ_min/σ_max is 0.0004, far below the 0.05 that A/H §5.3 pre-registers. Its weakest direction is the EXACT group vs NOISY-EXACT. All its MC items currently have answer C; the options are being rotated.
   - Pairs separated on a few items (DSATUR vs DSATUR-LABEL on 2 of 30 C E1 colouring items) are identified in principle but not at dev size.

**Other limitations.**

- **Selection.** Some generators select bases on a member's behaviour: C E1 SAT keeps bases where GREEDY satisfies in every order, and C E5 requires dead ends. Selection depends on x only, so inference on P(y | x) stays valid, but π then describes the selected population, not instances at large.
- **The slip model.** Both fake models and fit use the near-miss kernel. Real slips may differ; the misspecification check covers only the uniform-candidate alternative.
- **Distributional members are used as stored.**
  - RO-FF and RO-GREEDY keep only their 25 most frequent outcomes and lump the rest, which the likelihood spreads like q. That makes them partly collinear with q, and their single-member scenarios fail by 0.07–0.18. A fix is in progress.
  - NOISY-EXACT's stored "_other" lump is likewise uniform, not a near miss of the exact answer.
- **Availability.** The identifiability matrix ignores the renormalisation over available members (FF-OUT, the LOCAL-t members, ETR on two A/H E1 items). The fit does not ignore it.
- **The unexplained mass on witness channels** puts ½ on the special token where there is one. q's IMPOSSIBLE / UNSAT answers then look like an abort member's on the items where that member aborts. That is the likely reason π_0 is under-estimated in `null_q` on C E5 colouring (by 0.35–0.37) and C E2 SAT (by 0.08). On C E3 a third of q's answers are IMPOSSIBLE, which FF-OUT and LF predict.
- **Not built:** the hierarchical cross-model fit and a fitted token model.

## What is left

- **Regenerate the item sets** after the generator and zoo fixes, and rerun this harness (two commands, above). Its dependency analysis may change: MM-S1's implicit models and MATCH-A's order dependence affect B4/C4 E2's four-way dependency.
- **Intervals.** Coverage is the binding gate. Calibrate the cluster bootstrap (bootstrap-t or BCa), or use the posterior intervals of the hierarchical fit. Then rerun the coverage check with ≥ 100 replicates at the sizes the power analysis picks.
- **Design fixes** for the not-testable units: see Limitations.
- **The hierarchical cross-model fit** (DESIGN §3 O3) and a **fitted token model** for censoring.
- **Off-zoo detection.** The unexplained mass does not flag a missing strategy (above), so posterior-predictive checks per cell are needed.

## Where the gates pass (pre-regeneration items)

For each unit: the smallest size (items per cell; 5 = dev, then 10, 20 and 40) at which the 60/30/10 mixture passes all three gates, and the two null scenarios at that size, or at 40 if the mixture never passes.

- **Not reached by 40**: the trend is toward passing, but 40 items per cell was not enough.
- **Fails by design**: more items won't fix it.
- `single` and `feature` were run at dev size only, where they fail on every unit. They have not been checked at the larger sizes.

| Unit | Mixture passes all three gates at | null q | null ALWAYS |
|---|---|---|---|
| A/H E1 SAT, COL, ENT; A/H E2 SAT, COL, ENT | **fails by design**: q isn't identified on a two-valued channel (q = ½ always-positive + ½ always-negative), and the noise models are near-mixtures of the procedures; the mixture fails at every size | not testable | not testable |
| A/H E5 colouring | not reached by 40: the 0.1 weight's coverage is 0.84 at 40 (100 replicates); bias and width pass | pass | pass |
| A/H E5 entailment | **40** | pass | pass |
| A/H E5 knapsack | no mixture test: fewer than three members on every item | pass at 40 | pass |
| A/H E5 SAT | **20** (40 confirmed with 100 replicates) | pass | pass |
| B4/C4 E1 | **fails by design**: NOISY-EXACT is nearly the EXACT group (σ_min/σ_max = 0.0004), and every MC item has answer C | fail | fail |
| B4/C4 E2 | **fails by design**: five linear dependencies, one of them among procedures (H6); the identified mixture covers only 0.27–0.33 | not testable | not testable |
| C E1 SAT | **40** (100 replicates) | pass | fail: always-UNSAT goes to RO-GREEDY |
| C E1 colouring | not reached by 40: coverage 0.88 ± 0.03 at 40 (100 replicates); bias and width pass from 20 | pass | fail: one colour goes to LOCAL-2-ID |
| C E2 SAT | **40** (100 replicates) | pass | fail: always-UNSAT goes to RO-GREEDY |
| C E2 colouring | **10** (40 confirmed with 100 replicates) | pass | pass |
| C E2 knapsack | **20** (40 confirmed with 100 replicates) | fail: coverage 0.67–0.87 | pass |
| C E3 | **fails by design**: FF-LIST (= DPLL-LIST) leaks 0.14–0.31 to the LOCAL-t proxies at every size | fail | fail |
| C E5 SAT | not reached by 40: width 0.23 | pass | fail |
| C E5 SAT with a given state | **40** (100 replicates) | pass | fail |
| C E5 colouring (k = 3) | **fails by design** at these sizes: FF-3-EDGE-MENTION-ABORT vs PHANTOM-ADJACENT is a near-tie, and widths stay at 0.4 | fail | pass |
| C E5 colouring with a given state | not reached by 40: bias 0.07, width 0.24 | fail | pass |
| C E5 entailment | **fails by design**: q and NOISY-EXACT are combinations of other members, and EXACT answers NO on every item | not testable | not testable |

On these items, the mixture and both null scenarios pass together only on **C E2 colouring (10), A/H E5 SAT (20) and A/H E5 entailment (40)**.
- C E1 SAT, C E2 SAT and C E5 SAT with a given state recover the mixture at 40, but they credit a constant responder to a member (RO-GREEDY stores 0.5 on UNSAT).
- C E2 knapsack's `null_q` intervals under-cover.
