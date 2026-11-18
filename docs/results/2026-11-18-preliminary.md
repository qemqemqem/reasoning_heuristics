# Preliminary results, 2026-11-18: three gated units, two pilot-size runs

*Dev split, one sample per item, two cheap conditions. This is not the pre-registered study, and nothing here tests a hypothesis of DESIGN §4.*

Every table between `<!-- BEGIN prelim:… -->` markers is written by one command (DESIGN §5 rule 6), from the committed item sets and the committed runs:

```bash
OMP_NUM_THREADS=1 python analysis/prelim_2026_11_18.py --runs-root data/runs           # 20–35 minutes on 6 workers
OMP_NUM_THREADS=1 python analysis/prelim_2026_11_18.py --runs-root data/runs --check   # recompute; fail if a table differs
python analysis/prelim_2026_11_18.py --render-only --check                             # seconds: tables match the JSON (a test runs this)
```

- **The JSON.** The command writes [analysis/out/prelim_2026_11_18.json](../../analysis/out/prelim_2026_11_18.json). It holds every number below and more: per-cell exclusions, the full fit reports, the identifiability analysis, the permutation baselines and the recovery replicates' summaries. Every random draw is seeded.
- **Which runs.** The script finds every `2026-11-18-dev-*`, `-pc20-*` and `-pc40-*` run that has scored records, and fits every gated unit of each one's item set. So when more runs land, a rerun puts them in the JSON, and a page can be built from it alone (its `schema` key describes the fields).
- **This doc stays pinned.** Its tables are rendered only for the five runs it describes, so they and the prose stay in step.
- **Checking.** The prose is written by hand. The [audit](#audit) lists how its numbers were checked.

## Bottom line

- **What is fitted.** Mixture weights are reported only where the fake-model recovery gates pass at this item size (DESIGN §5 rule 12): C E2 colouring, C E2 knapsack and A/H E5 SAT, at 20 items per cell. The data are two cheap conditions, Qwen3-32B with thinking off and gpt-oss-20b at low reasoning effort. Everything else is descriptive.
- **Five of the six fits do not reproduce their data.** In each of them the slip rate sits at its cap (ε = 0.5). Fake data drawn from the fitted mixture miss a simple feature of the real answers (§3.5):
  - on colouring, the fitted mixtures predict that 33% (Qwen3-32B) and 39% (gpt-oss-20b) of answers equal a member's answer; the data have 0% and 28%;
  - on knapsack, Qwen3-32B's fit predicts 46% such answers; the data have 8%;
  - on A/H E5 SAT, they predict UNSAT on 47% and 43% of items; the data have 3% and 27%.

  Read these fits' weights as "whose answers the model's answers are near", not as procedures the model runs.
- **The one fit whose model reproduces its data is gpt-oss-20b on C E2 knapsack.**
  - 158 of 300 answers are optimal, and EXACT's weight is 0.616 [0.535, 0.688].
  - When it errs, its answer is often a greedy rule's: 57 of 142 wrong answers equal one exactly. The weights on RATIO-SKIP (0.136), VALUE (0.115) and DIFF (0.096) each lie far above their permutation chance levels (0.005–0.008; p = 0.0005, the smallest possible with 2,000 permutations).
  - Its fitted model reproduces the data: 72% of answers equal a member's answer, and the model predicts 72%. Fake data planted at its estimate are recovered with |bias| ≤ 0.007 and coverage 0.89–0.96 (BCa 0.91–0.96).
- **C E2 colouring.** gpt-oss-20b gives listing-order first fit's wrong colouring on 40 of the 232 items where both are wrong, and each other greedy member's on at most 2. This unit has no structure-matched chance level. Qwen3-32B with thinking off gives no optimal colouring and none equal to any member's; 299 of its 300 colourings are improper.
- **A/H E5 SAT: we found no zoo member that accounts for the answers.** Neither model solved an item, and no answer equals any member's assignment.
  - Qwen3-32B's unexplained mass, 0.94, equals the level shuffled answers get (0.95).
  - gpt-oss-20b's, 0.87, is below its shuffled level (0.98). Its assignments lie nearer to POLARITY's and to the solutions than shuffled ones do, though none equals either: weights of 0.05, against chance levels of 0.002–0.006.
- **Not shown:** anything about best-effort thinking, the test split, or differences between models (model and condition change together).

## 1. What was run

<!-- BEGIN prelim:runs -->
| Run | Model | Condition | max_tokens | Served by | Responses | From the response cache | Visible working: max pre_answer_tokens | API cost | Scorer | Item files changed since the run |
|---|---|---|---|---|---|---|---|---|---|---|
| `2026-11-18-pc20-qwen3-32b-direct` | qwen/qwen3-32b | direct | 1,024 | DeepInfra (1380) | 1380 | 160 (160 are the dev run's own responses) | 4 (0 over 20) | $0.0702 | scorer-1.5.0 | C_E1, C_E2 |
| `2026-11-18-pc20-gpt-oss-20b-thinking-low` | openai/gpt-oss-20b | thinking-low | 32,768 | DekaLLM (1380) | 1380 | 160 (160 are the dev run's own responses) | 140 (1 over 20) | $0.2330 | scorer-1.5.0 | C_E1, C_E2 |
| `2026-11-18-dev-qwen3-32b-direct` | qwen/qwen3-32b | direct | 1,024 | DeepInfra (1270) | 1270 | 0 | 1129 (8 over 20) | $0.0986 | scorer-1.5.0 | C_E1, C_E2 |
| `2026-11-18-dev-qwen3-14b-direct` | qwen/qwen3-14b | direct | 1,024 | DeepInfra (1270) | 1270 | 0 | 1025 (10 over 20) | $0.1266 | scorer-1.5.0 | C_E1, C_E2 |
| `2026-11-18-dev-gpt-oss-20b-thinking-low` | openai/gpt-oss-20b | thinking-low | 32,768 | DekaLLM (1270) | 1270 | 0 | 567 (81 over 20) | $0.1710 | scorer-1.5.0 | C_E1, C_E2 |
<!-- END prelim:runs -->

- **Pilot size, 20 items per design cell**, on [data/items/pc20/](../../data/items/pc20/): C E2 (800 items), A/H E5 (340) and C E1 (240). These are dev-split items: same tier and seed as `data/items/dev`, more items per cell.
- **Dev size, 5 per cell**, on [data/items/dev/](../../data/items/dev/): 1,270 items over nine evals (A/H E8 excluded).
- **Not included.** The pilot-size Qwen3-32B thinking-high run, and the four high-effort dev runs, were still running when this was written. So the primary condition (thinking at best effort) is absent from this document.
- **Conditions.**
  - *direct* (Qwen3): thinking off, max_tokens 1,024, and the system instruction "Respond with only the final answer in the requested format. Do not explain or show your working."
  - *thinking-low* (gpt-oss-20b): reasoning effort low, max_tokens 32,768. gpt-oss cannot turn reasoning off, so this is a budget arm of the thinking condition, not a direct condition ([decision record](../decisions/2026-11-17-direct-answer-arm.md)).
- **Responses shared between runs.** Each pilot run took 160 responses from the response cache. They are the paired dev run's own responses to the same prompts (same generation ids; the table counts them), on the 160 items the two sets share. That includes 75 of the 300 C E2 colouring items and 25 of the 100 A/H E5 SAT items. So the pilot and dev runs of one model are not independent samples on those items.
- **Item drift.** All five runs were scored before #22 added the A1 give-up member (ALWAYS-UNSAT) to the C E1 and C E2 SAT items, so their manifests record the earlier C E1 and C E2 files. Responses are joined to the current files by item_id with the content hash checked (`identify.records.join`, which raises on any mismatch); every one of the 6,570 joins succeeds. #22 changed only the SAT items, and only by adding that member: the colouring and knapsack records are identical, and ids, prompts and content hashes are unchanged ([audit](#audit)).

## 2. Which units are fitted, and why

DESIGN §5 rule 12 allows mixture weights only for units and item sizes where the fake-model recovery gates pass: |bias| ≤ 0.05, 95% coverage ≥ 0.9 and median interval width ≤ 0.2. At 20 items per cell, on the regenerated items, that is three units. Every other unit gets descriptive statistics only (§6).

<!-- BEGIN prelim:units -->
| Unit (20 per cell) | Items | Here | Why (docs/RECOVERY.md) | Members predicting UNSAT / IMPOSSIBLE / X (items) |
|---|---|---|---|---|
| AH_E5/COL | 80 | descriptive only | passes at 40 per cell (the mixture with either interval, and both nulls) but not at 20 (smallest coverage 0.86, median width 0.245; BCa 0.90, 0.239); no A/H E5 run at 40 per cell exists | C1 FIRST-FIT (stated rule) (28) |
| AH_E5/ENT | 80 | descriptive only | not reached by 40: bias and width pass from 20, but the 0.1 weight (B4 FIRST) covers 0.81 at 20 and 0.87 at 40 (BCa 0.88 at both); both nulls pass | B4 FIRST (24) |
| AH_E5/KNAP | 80 | descriptive only | no mixture test: fewer than three members on every item; null q fails coverage from 20 per cell on (the boundary) | none |
| AH_E5/SAT | 100 | **fitted** | the mixture passes the three gates at 20 per cell on the regenerated items (see the text) | none |
| C_E1/3-SAT | 120 | descriptive only | the mixture passes only with BCa intervals (0.92 at 20, 0.90 at 40); with percentile intervals the 0.1 ALWAYS-UNSAT weight covers 0.86 at 20 and 0.79 at 40; null q fails at every size (the boundary) | ALWAYS-UNSAT (A1 give-up) (120); GREEDY-OUT (AR) (11); GUC-DET (C2) (50); UC-DET (C2) (81); stored distributions: RANDOM (H), RO-GREEDY (C3) |
| C_E1/colouring | 120 | descriptive only | the mixture passes only with BCa intervals, at 20 (0.91); with percentile intervals it covers 0.88 at 20 and 0.87 at 40; null ALWAYS fails at every size, by design (the one-colour answer goes to LOCAL-2-ID) | none |
| C_E2/3-SAT | 200 | descriptive only | the mixture passes at 40 per cell but not at 20 (coverage 0.88, median width 0.28), and null q fails at every size (0.88 at 40), so the three never pass together | ALWAYS-UNSAT (A1 give-up) (200); DPLL-MENTION (D, T first) (40); EXACT (40); GREEDY-INDEX (160); GREEDY-MENTION (160); GUC-DET (C2) (173); SC-DET (C2) (158); UC-DET (C2) (177); stored distributions: RANDOM (H), RO-GREEDY (C3) |
| C_E2/colouring | 300 | **fitted** | the mixture passes the three gates at 20 per cell on the regenerated items (see the text) | none |
| C_E2/knapsack | 300 | **fitted** | the mixture passes the three gates at 20 per cell on the regenerated items (see the text) | none |
<!-- END prelim:units -->

**The three fitted units.** The gate verdicts come from [RECOVERY.md](../RECOVERY.md) ("Regenerated items: candidate units", #24). Each uses the 60/30/10 mixture with 100 replicates, computed on items identical to `data/items/pc20`:

| Unit | Mixture, percentile intervals | Mixture, BCa intervals | null q | null ALWAYS |
|---|---|---|---|---|
| C E2 colouring | passes at 20 and 40 (min coverage 0.92, 0.90) | passes at 5, 10 and 20; misses at 40 (0.89) | passes at every size | passes at every size |
| C E2 knapsack | passes at 20 and 40 (0.92, 0.91) | passes at 20 and 40 (0.92, 0.90) | **fails coverage at every size** (0.81, 0.73, 0.52 at 10, 20, 40), with bias ≤ 0.01 | passes at every size |
| A/H E5 SAT | passes at 20 and 40 (0.90, 0.91): **at the gate** | **fails** (0.88 at 20, 0.89 at 40) | passes | passes |

- **Percentile intervals are primary**, because they are the ones that pass on all three units. BCa intervals from the same bootstrap draws are reported next to them. On A/H E5 SAT the BCa intervals do not pass the gate, so they are shown for comparison only.
- **On C E2 knapsack, an all-noise responder's π₀ interval is not calibrated.** When every answer is q, the estimate of π₀ is right (bias ≤ 0.01). But its percentile interval stops just short of 1 more often than it should, and with more items it does so more often: coverage is 0.73 at 20 per cell (RECOVERY.md, "Null q at the boundary"). A π₀ interval near 1 on this unit would under-cover. Neither knapsack fit is near 1, but gpt-oss-20b's π₀ sits at the other boundary, 0.
- **What the gates test.** Each uses one planted triple per unit (FF-LABEL / DPLL-LIST / EXACT; DIFF / RATIO-SKIP / EXACT; C0 POLARITY / C1 GREEDY / A3 TT[exact]), with slips at ε = 0.1 and ρ = 0.3, plus the two nulls. They do not test weight planted on other members, or the slip rates the real data produce. §3.5 checks both at the fitted estimates.
- **The special-token fix of #24 does not touch these units.** That fix stops deterministic predictions of UNSAT, IMPOSSIBLE or X from slipping, and it applies only where some member makes such a prediction. On the three fitted units, no member predicts a special token on any item: not as a deterministic answer, and not as mass in a stored distribution (last column above; last row of each identifiability table). The colouring (fewest colours) and knapsack answer spaces have no special token at all. A/H E5 SAT's has UNSAT, but only q gives it mass. RECOVERY.md reports that A/H E5 SAT, rerun as a control, reproduces its results exactly, and the point estimates here are the same before and after the merge ([audit](#audit)).
- **Four other pc20 units do have such members**: A/H E5 colouring and entailment, and C E1 and C E2 SAT. Under the strict rule, C E1 SAT and A/H E5 entailment still fail after the fix, so they stay descriptive.
- **A fourth gated unit, for later runs.** The script also fits C E5 SAT with a given partial assignment on 40-per-cell runs, where its mixture and both nulls pass (RECOVERY.md). There, GUC-DET and SC-DET from state are tied on every item, so the engine gives them one weight. The script stops if that tie ever breaks, because the gate covers only their sum. This doc's tables cover only the five pc20 runs it pins, so it has no such fit; the 40-per-cell fits are on the [results page](2026-11-18-results.html).

**Dev-size runs (5 per cell): descriptive only.** No unit passes the gates at the committed dev size (RECOVERY.md, Bottom line). Some also fail for reasons that more items will not fix:

<!-- BEGIN prelim:dev_units -->
| Unit (5 per cell) | Items | Gate status at larger sizes (docs/RECOVERY.md) |
|---|---|---|
| AH_E1/COL | 20 | fails by design at every size run (5–20 per cell): q is not identified on a two-valued channel (q = ½ always-positive + ½ always-negative), so the nulls are not testable, and the noise models are near-mixtures of the procedures |
| AH_E1/ENT | 20 | fails by design at every size run (5–20 per cell): q is not identified on a two-valued channel (q = ½ always-positive + ½ always-negative), so the nulls are not testable, and the noise models are near-mixtures of the procedures |
| AH_E1/SAT | 30 | fails by design at every size run (5–20 per cell): q is not identified on a two-valued channel (q = ½ always-positive + ½ always-negative), so the nulls are not testable, and the noise models are near-mixtures of the procedures |
| AH_E2/COL | 40 | fails by design: as A/H E1 |
| AH_E2/ENT | 40 | fails by design: as A/H E1 |
| AH_E2/SAT | 40 | fails by design: as A/H E1 |
| AH_E5/COL | 20 | passes at 40 per cell (the mixture with either interval, and both nulls) but not at 20 (smallest coverage 0.86, median width 0.245; BCa 0.90, 0.239); no A/H E5 run at 40 per cell exists |
| AH_E5/ENT | 20 | not reached by 40: bias and width pass from 20, but the 0.1 weight (B4 FIRST) covers 0.81 at 20 and 0.87 at 40 (BCa 0.88 at both); both nulls pass |
| AH_E5/KNAP | 20 | no mixture test: fewer than three members on every item; null q fails coverage from 20 per cell on (the boundary) |
| AH_E5/SAT | 25 | passes at 20 per cell; fitted on the 20-per-cell runs |
| B4C4_E1/entailment | 140 | fails by design (run at dev size only): NOISY-EXACT is nearly the EXACT group (σ_min/σ_max = 0.0004) |
| B4C4_E2/entailment | 240 | fails by design (run at dev size only): five linear dependencies, one of them among procedures (the H6 gap) |
| C_E1/3-SAT | 30 | the mixture passes only with BCa intervals (0.92 at 20, 0.90 at 40); with percentile intervals the 0.1 ALWAYS-UNSAT weight covers 0.86 at 20 and 0.79 at 40; null q fails at every size (the boundary) |
| C_E1/colouring | 30 | the mixture passes only with BCa intervals, at 20 (0.91); with percentile intervals it covers 0.88 at 20 and 0.87 at 40; null ALWAYS fails at every size, by design (the one-colour answer goes to LOCAL-2-ID) |
| C_E2/3-SAT | 50 | the mixture passes at 40 per cell but not at 20 (coverage 0.88, median width 0.28), and null q fails at every size (0.88 at 40), so the three never pass together |
| C_E2/colouring | 75 | passes at 20 per cell; fitted on the 20-per-cell runs |
| C_E2/knapsack | 75 | passes at 20 per cell; fitted on the 20-per-cell runs |
| C_E3/colouring (gadget) | 270 | fails by design (run at dev size only): DPLL-LIST = FF-LIST and six LOCAL-t proxies span only six directions, so the mixture is not testable, and null q loads 0.41 on members |
| C_E5/3-SAT | 15 | not reached by 40: at 40 per cell the median width is 0.24 and the 0.1 weight's coverage 0.89 |
| C_E5/3-SAT (partial assignment given) | 15 | passes at 40 per cell; fitted on the 40-per-cell runs |
| C_E5/colouring (k=3) | 25 | fails at these sizes by a near-tie (FF-3-EDGE-MENTION-ABORT against ALWAYS-IMPOSSIBLE = PHANTOM-ADJACENT): coverage 0.48 at 20; at 40, coverage 0.89 but median width 0.46 |
| C_E5/colouring (k=3, partial colouring given) | 10 | not reached by 40: bias and coverage pass at 40, but the median width is 0.27, and null q fails at every size |
| C_E5/propositional entailment | 20 | fails by design: q and NOISY-EXACT are combinations of other members, and the EXACT group answers 'does not follow' on every item (mixture bias 0.08–0.13 at every size) |
<!-- END prelim:dev_units -->

## 3. Fits

**How to read a weight.** The fit is P(y | x) = Σ_h π_h P(y | h, x) + π₀ q(y | x) per (model, condition, eval, domain). π_h is the share of answers attributed to "member h's answer, or a near miss of it". A near miss changes D positions of h's answer (vertices recoloured, items toggled, variables flipped), with D ~ truncated geometric(ρ) on 1–6. ε is the share of each member's answers that are near misses. π₀ is the unexplained mass, q a uniformly random answer (with half its mass on UNSAT where the channel has that token). Members that predict the same answer on every item share one weight (a tie group, "A = B"). Intervals are 95% percentile intervals from 2,000 cluster-bootstrap draws; a cluster is a base with its variants.

**ε and ρ are bounded.** The engine caps ε at 0.5 (`EPS_MAX`, so that slips cannot absorb everything) and takes ρ from a grid on [0.02, 0.9]. An estimate at 0.5 or 0.9 with an interval of zero width means every bootstrap replicate sat on the bound.

### 3.1 C E2 colouring (300 items, 15 cells, 60 clusters; fewest colours)

<!-- BEGIN prelim:weights_C_E2_colouring -->
| Weight | Qwen3-32B direct: π [95% percentile] | BCa | gpt-oss-20b thinking-low: π [95% percentile] | BCa |
|---|---|---|---|---|
| DPLL-LIST (D) | 0.023 [0.000, 0.069] | [0.000, 0.074] | 0.029 [0.000, 0.060] | [0.001, 0.070] |
| DSATUR | 0.038 [0.000, 0.074] | [0.011, 0.089] | 0.000 [0.000, 0.010] | [0.000, 0.035] |
| DSATUR-LABEL | 0.000 [0.000, 0.034] | [0.000, 0.034] | 0.040 [0.013, 0.071] | [0.017, 0.076] |
| EXACT | 0.405 [0.327, 0.479] | [0.332, 0.483] | 0.150 [0.103, 0.201] | [0.105, 0.201] |
| FF-LABEL | 0.044 [0.018, 0.074] | [0.021, 0.080] | 0.036 [0.012, 0.064] | [0.016, 0.069] |
| FF-LIST = GREEDY+REPAIR-LIST (C->F) | 0.104 [0.062, 0.147] | [0.066, 0.151] | 0.346 [0.284, 0.410] | [0.290, 0.416] |
| LF | 0.053 [0.019, 0.095] | [0.023, 0.101] | 0.038 [0.010, 0.072] | [0.014, 0.079] |
| NOISY-EXACT | 0.000 [0.000, 0.000] | [0.000, 0.000] | 0.000 [0.000, 0.000] | [0.000, 0.048] |
| RO-FF (C3) | 0.000 [0.000, 0.000] | [0.000, 0.000] | 0.275 [0.219, 0.333] | [0.219, 0.333] |
| **unexplained mass π₀ (q)** | 0.333 [0.267, 0.403] | [0.273, 0.407] | 0.087 [0.060, 0.117] | [0.061, 0.121] |
| ε (slip rate; cap 0.5) | 0.500 [0.500, 0.500] | – | 0.500 [0.500, 0.500] | – |
| ρ (slip shape; grid 0.02–0.9) | 0.900 [0.900, 0.900] | – | 0.900 [0.900, 0.900] | – |
| answers fitted (rows) / clusters | 300 / 60 |  | 299 / 60 |  |
| log-likelihood | -7642.2 |  | -3707.6 |  |
<!-- END prelim:weights_C_E2_colouring -->

<!-- BEGIN prelim:ident_C_E2_colouring -->
| Identifiability: C_E2/colouring |  |
|---|---|
| rank / columns (groups + q) | 10 / 10 |
| σ_min / σ_max of the design (columns scaled) | 0.159 |
| linear dependencies | none |
| weights reported as not identified (with ranges) | none |
| tie groups (identical predictions on every item; one weight) | FF-LIST = GREEDY+REPAIR-LIST (C->F) |
| members folded into q (identical to q on every item) | RANDOM (H) |
| least-separated pairs | DSATUR vs DSATUR-LABEL: 168 of 300 items; DPLL-LIST (D) vs FF-LIST = GREEDY+REPAIR-LIST (C->F): 244 of 300 items; LF vs DSATUR-LABEL: 253 of 300 items |
| data ties in either fit (identical likelihood on every answered row) | none |
| members that predict UNSAT / IMPOSSIBLE / X | none; stored distributions with special-token mass: none; special tokens in the answer space: none |
<!-- END prelim:ident_C_E2_colouring -->

- **gpt-oss-20b (low effort).**
  - 43 of 299 answers are optimal colourings (14%), and 246 are proper (82%; §6).
  - The weight spreads over three components: listing-order first fit 0.346 (FF-LIST, tied with GREEDY+REPAIR-LIST, which gives the same colouring on every item), random-order first fit 0.275 (RO-FF) and EXACT 0.150. The unexplained mass is 0.087.
  - RO-FF is a stored distribution over the first-fit colourings that random vertex orders produce: 335–3,102 distinct colourings per item, with an `_other` lump below 0.0001 (§3.4). So its weight says that about a quarter of the answers are attributed to first fit under *some* vertex order, not to any one order.
  - FF-LIST is the only deterministic member whose wrong colourings gpt-oss-20b reproduces often (§4.1).
- **Qwen3-32B (direct).**
  - No answer is optimal. 299 of 300 are improper: two adjacent vertices share a colour.
  - No answer equals any member's. 89% are more than 3 recolourings from every member, and 33% more than 6 (§3.4).
  - The fit gives EXACT 0.405 and q 0.333, with ε and ρ on their bounds. So the 0.405 is near misses of optimal colourings, under a slip kernel stretched to its widest. It is not a rate of solving.

### 3.2 C E2 knapsack (300 items, 15 cells, 60 clusters)

<!-- BEGIN prelim:weights_C_E2_knapsack -->
| Weight | Qwen3-32B direct: π [95% percentile] | BCa | gpt-oss-20b thinking-low: π [95% percentile] | BCa |
|---|---|---|---|---|
| DIFF | 0.147 [0.018, 0.301] | [0.038, 0.326] | 0.096 [0.040, 0.158] | [0.043, 0.167] |
| EXACT | 0.085 [0.000, 0.193] | [0.001, 0.208] | 0.616 [0.535, 0.688] | [0.540, 0.692] |
| INPUT-FIT | 0.000 [0.000, 0.000] | [0.000, 0.000] | 0.004 [0.000, 0.017] | [0.000, 0.024] |
| LARGEST-FIT | 0.000 [0.000, 0.009] | [0.000, 0.017] | 0.000 [0.000, 0.000] | [0.000, 0.000] |
| RATIO+BEST-SINGLE = RATIO-PREFIX | 0.586 [0.422, 0.741] | [0.406, 0.731] | 0.032 [0.000, 0.106] | [0.000, 0.113] |
| RATIO-SKIP | 0.000 [0.000, 0.062] | [0.000, 0.165] | 0.136 [0.051, 0.213] | [0.059, 0.218] |
| VALUE | 0.080 [0.000, 0.191] | [0.009, 0.226] | 0.115 [0.060, 0.179] | [0.064, 0.191] |
| **unexplained mass π₀ (q)** | 0.102 [0.000, 0.213] | [0.010, 0.269] | 0.000 [0.000, 0.000] | [0.000, 0.000] |
| ε (slip rate; cap 0.5) | 0.500 [0.500, 0.500] | – | 0.287 [0.231, 0.344] | – |
| ρ (slip shape; grid 0.02–0.9) | 0.520 [0.460, 0.580] | – | 0.600 [0.520, 0.680] | – |
| answers fitted (rows) / clusters | 300 / 60 |  | 300 / 60 |  |
| log-likelihood | -1728.7 |  | -822.1 |  |
<!-- END prelim:weights_C_E2_knapsack -->

<!-- BEGIN prelim:ident_C_E2_knapsack -->
| Identifiability: C_E2/knapsack |  |
|---|---|
| rank / columns (groups + q) | 8 / 8 |
| σ_min / σ_max of the design (columns scaled) | 0.335 |
| linear dependencies | none |
| weights reported as not identified (with ranges) | none |
| tie groups (identical predictions on every item; one weight) | RATIO+BEST-SINGLE = RATIO-PREFIX |
| members folded into q (identical to q on every item) | none |
| least-separated pairs | DIFF vs RATIO-SKIP: 121 of 300 items; RATIO+BEST-SINGLE = RATIO-PREFIX vs RATIO-SKIP: 163 of 300 items; VALUE vs RATIO-SKIP: 285 of 300 items |
| data ties in either fit (identical likelihood on every answered row) | none |
| members that predict UNSAT / IMPOSSIBLE / X | none; stored distributions with special-token mass: none; special tokens in the answer space: none |
<!-- END prelim:ident_C_E2_knapsack -->

- **gpt-oss-20b (low effort).**
  - 158 of 300 answers are optimal (53%), and 293 are feasible.
  - EXACT takes 0.616. Three greedy rules share most of the rest: RATIO-SKIP 0.136, VALUE 0.115 and DIFF 0.096.
  - This is the only fit whose slip rate is inside its range (ε = 0.29), and the only one whose fitted model reproduces all three statistics of the predictive check (§3.5).
  - π₀ is 0, with an interval of zero width: no answer needs q.
- **Qwen3-32B (direct).**
  - 1 of 300 answers is optimal, and 272 are feasible.
  - The weight goes mostly to the ratio-greedy prefix: RATIO+BEST-SINGLE and RATIO-PREFIX are identical on every item, and together take 0.586. Then come DIFF 0.147, q 0.102, EXACT 0.085 and VALUE 0.080, with ε at its cap.
  - Only 24 answers (8%) equal a member's answer, and 218 (73%) are one or two items away from the nearest member's (§3.4). So these weights describe which members' answers the model's answers are near, not answers it reproduces.

### 3.3 A/H E5 SAT (100 items, 5 cells, 20 clusters)

<!-- BEGIN prelim:weights_AH_E5_SAT -->
| Weight | Qwen3-32B direct: π [95% percentile] | BCa | gpt-oss-20b thinking-low: π [95% percentile] | BCa |
|---|---|---|---|---|
| A3 TT[exact] | 0.000 [0.000, 0.133] | [0.000, 0.174] | 0.000 [0.000, 0.052] | [0.000, 0.068] |
| C0 POLARITY | 0.025 [0.000, 0.093] | [0.000, 0.140] | 0.052 [0.000, 0.144] | [0.000, 0.161] |
| C1 GREEDY | 0.000 [0.000, 0.000] | [0.000, 0.000] | 0.000 [0.000, 0.010] | [0.000, 0.073] |
| D DPLL (first solution) | 0.009 [0.000, 0.059] | [0.000, 0.079] | 0.030 [0.000, 0.095] | [0.000, 0.106] |
| exact | 0.024 [0.000, 0.093] | [0.000, 0.127] | 0.049 [0.000, 0.135] | [0.000, 0.173] |
| **unexplained mass π₀ (q)** | 0.942 [0.794, 0.999] | [0.818, 1.000] | 0.869 [0.738, 0.956] | [0.738, 0.956] |
| ε (slip rate; cap 0.5) | 0.500 [0.500, 0.500] | – | 0.500 [0.500, 0.500] | – |
| ρ (slip shape; grid 0.02–0.9) | 0.900 [0.020, 0.900] | – | 0.700 [0.020, 0.900] | – |
| answers fitted (rows) / clusters | 95 / 20 |  | 97 / 20 |  |
| log-likelihood | -963.0 |  | -744.1 |  |
<!-- END prelim:weights_AH_E5_SAT -->

<!-- BEGIN prelim:ident_AH_E5_SAT -->
| Identifiability: AH_E5/SAT |  |
|---|---|
| rank / columns (groups + q) | 6 / 6 |
| σ_min / σ_max of the design (columns scaled) | 0.476 |
| linear dependencies | none |
| weights reported as not identified (with ranges) | none |
| tie groups (identical predictions on every item; one weight) | none |
| members folded into q (identical to q on every item) | none |
| least-separated pairs | A3 TT[exact] vs exact: 60 of 100 items; C1 GREEDY vs D DPLL (first solution): 97 of 100 items; C0 POLARITY vs A3 TT[exact]: 100 of 100 items |
| data ties in either fit (identical likelihood on every answered row) | none |
| members that predict UNSAT / IMPOSSIBLE / X | none; stored distributions with special-token mass: none; special tokens in the answer space: UNSAT |
<!-- END prelim:ident_AH_E5_SAT -->

- **The items.** All 100 are satisfiable, most with one or two solutions under the stated rule (median 2, at most 29). Two of the five cells invert the clause rule ("satisfied when at least one literal is FALSE"), and one inverts the starred clauses only.
- **Both runs.** No answer satisfies the stated rule (0 of 95 for Qwen3-32B, 0 of 97 for gpt-oss-20b), and none equals any member's assignment.
  - The unexplained mass takes almost everything: 0.94 for Qwen3-32B and 0.87 for gpt-oss-20b, with no member above 0.06.
  - gpt-oss-20b answered UNSAT on 26 of 97 satisfiable items. No A/H E5 member predicts UNSAT, so only q can take those answers.
  - q puts half its mass on UNSAT, far more than either model's share of UNSAT answers (§3.5).

### 3.4 How far the answers are from the members

The distance from each answer to the nearest member's answer (for a set-valued member, its nearest solution): vertices recoloured up to renaming, items toggled, variables flipped. A slip reaches at most 6 positions, so an answer more than 6 away from every member can only be explained by q, or by a stored distribution's `_other` lump. Taking the nearest of a set's solutions favours set-valued members with many solutions: EXACT has up to 149,388 optimal colourings on one C E2 item.

<!-- BEGIN prelim:near -->
| Unit | Run | Answers | Positions per item | d = 0 | d = 1 | d = 2 | d = 3 | d = 4-6 | d = >6 | special token |
|---|---|---|---|---|---|---|---|---|---|---|
| C_E2/colouring | Qwen3-32B direct | 300 | 16 | 0 | 1 (0%) | 8 (3%) | 24 (8%) | 168 (56%) | 99 (33%) | 0 |
| C_E2/colouring | gpt-oss-20b thinking-low | 299 | 16 | 84 (28%) | 28 (9%) | 31 (10%) | 26 (9%) | 105 (35%) | 25 (8%) | 0 |
| C_E2/knapsack | Qwen3-32B direct | 300 | 10 | 24 (8%) | 98 (33%) | 120 (40%) | 44 (15%) | 14 (5%) | 0 | 0 |
| C_E2/knapsack | gpt-oss-20b thinking-low | 300 | 10 | 215 (72%) | 29 (10%) | 45 (15%) | 10 (3%) | 1 (0%) | 0 | 0 |
| AH_E5/SAT | Qwen3-32B direct | 95 | 12/16 | 0 | 3 (3%) | 8 (8%) | 12 (13%) | 46 (48%) | 23 (24%) | 3 (3%) |
| AH_E5/SAT | gpt-oss-20b thinking-low | 97 | 12/16 | 0 | 6 (6%) | 7 (7%) | 17 (18%) | 36 (37%) | 5 (5%) | 26 (27%) |
<!-- END prelim:near -->

**Stored-distribution members.** RO-FF (random-order first fit) and NOISY-EXACT are distributions stored on the items: the outcomes of a Monte Carlo run, plus a lump `_other` for the rest. The likelihood spreads `_other` exactly like q (RECOVERY.md, Limitations), so weight that arrives through it is unexplained mass under another name. On C E2 colouring, RO-FF lists 335–3,102 distinct colourings per item, with an `_other` lump below 0.0001. NOISY-EXACT keeps up to 0.32 of its mass in the lump.

<!-- BEGIN prelim:lumps -->
| Unit | Run | Stored-distribution member | Mean `_other` mass per item | Fitted π | Share of its fitted responsibility that comes through `_other` (q-shaped) |
|---|---|---|---|---|---|
| C_E2/colouring | Qwen3-32B direct | NOISY-EXACT | 0.29 | 0.000 | – |
| C_E2/colouring | Qwen3-32B direct | RO-FF (C3) | 0.00 | 0.000 | – |
| C_E2/colouring | gpt-oss-20b thinking-low | NOISY-EXACT | 0.29 | 0.000 | – |
| C_E2/colouring | gpt-oss-20b thinking-low | RO-FF (C3) | 0.00 | 0.275 | 0.00 |
<!-- END prelim:lumps -->

### 3.5 Checks at the fitted estimates

The Stage 0 gates were run at one operating point (a 0.6 / 0.3 / 0.1 triple, ε = 0.1, ρ = 0.3). Two checks ask whether the fits deserve the gates' trust where they actually landed. Both use fake models that answer the same items, with the same exclusions, from each fitted mixture: its weights (those below 0.01 set to 0), its ε and its ρ. They are positive controls at the estimate, not new gates.

**Recovery at the estimate.** 100 fake data sets per fit, each refitted with 200 bootstrap draws, scored with the Stage 0 gates:

<!-- BEGIN prelim:recovery -->
| Unit | Run whose fit is planted | planted ε / ρ | Replicates | max \|bias\| | Percentile: gates | min coverage | median width | BCa: gates | min coverage | median width |
|---|---|---|---|---|---|---|---|---|---|---|
| C_E2/colouring | Qwen3-32B direct | 0.50 / 0.90 | 100 | 0.012 (NOISY-EXACT) | PASS | 0.91 (FF-LIST = GREEDY+REPAIR-LIST (C->F)) | 0.064 | PASS | 0.90 (EXACT) | 0.067 |
| C_E2/colouring | gpt-oss-20b thinking-low | 0.50 / 0.90 | 100 | 0.011 (NOISY-EXACT) | fail (coverage) | 0.88 (DPLL-LIST (D)) | 0.070 | PASS | 0.90 (FF-LIST = GREEDY+REPAIR-LIST (C->F)) | 0.072 |
| C_E2/knapsack | Qwen3-32B direct | 0.50 / 0.52 | 100 | 0.017 (unexplained (q)) | PASS | 0.91 (DIFF) | 0.115 | fail (coverage) | 0.87 (unexplained (q)) | 0.114 |
| C_E2/knapsack | gpt-oss-20b thinking-low | 0.29 / 0.60 | 100 | 0.007 (unexplained (q)) | fail (coverage) | 0.89 (DIFF) | 0.107 | PASS | 0.91 (RATIO-SKIP) | 0.108 |
| AH_E5/SAT | Qwen3-32B direct | 0.50 / 0.90 | 100 | 0.011 (exact) | fail (coverage) | 0.57 (exact) | 0.058 | fail (coverage) | 0.70 (exact) | 0.068 |
| AH_E5/SAT | gpt-oss-20b thinking-low | 0.50 / 0.70 | 100 | 0.006 (unexplained (q)) | fail (coverage) | 0.81 (D DPLL (first solution)) | 0.103 | fail (coverage) | 0.85 (D DPLL (first solution)) | 0.113 |
<!-- END prelim:recovery -->

**Does the fitted model reproduce the data?** Three statistics of the real answers, against the same statistics of the fake data sets (mean, and 5th–95th percentile over the 100). "Outside" marks an observed value outside that range.

<!-- BEGIN prelim:ppc -->
| Unit | Run | Answers equal to a member's answer: observed vs fitted model [5–95%] | Answers beyond every member's slip reach | Special-token answers (UNSAT) |
|---|---|---|---|---|
| C_E2/colouring | Qwen3-32B direct | 0.00 vs 0.33 [0.29, 0.38] **outside** | 0.33 vs 0.34 [0.29, 0.38] | 0.00 vs 0.00 [0.00, 0.00] |
| C_E2/colouring | gpt-oss-20b thinking-low | 0.28 vs 0.39 [0.35, 0.43] **outside** | 0.10 vs 0.12 [0.09, 0.15] | 0.00 vs 0.00 [0.00, 0.00] |
| C_E2/knapsack | Qwen3-32B direct | 0.08 vs 0.46 [0.41, 0.51] **outside** | 0.00 vs 0.00 [0.00, 0.00] | 0.00 vs 0.00 [0.00, 0.00] |
| C_E2/knapsack | gpt-oss-20b thinking-low | 0.72 vs 0.72 [0.69, 0.75] | 0.00 vs 0.00 [0.00, 0.00] | 0.00 vs 0.00 [0.00, 0.00] |
| AH_E5/SAT | Qwen3-32B direct | 0.00 vs 0.02 [0.00, 0.05] | 0.27 vs 0.55 [0.46, 0.62] **outside** | 0.03 vs 0.47 [0.38, 0.55] **outside** |
| AH_E5/SAT | gpt-oss-20b thinking-low | 0.00 vs 0.07 [0.03, 0.10] **outside** | 0.32 vs 0.50 [0.42, 0.58] **outside** | 0.27 vs 0.43 [0.34, 0.52] **outside** |
<!-- END prelim:ppc -->

**Reading the two checks.**

- **If the near-miss model were right, the colouring and knapsack intervals would be about right.**
  - Fake data drawn from each of those four fits are recovered with |bias| ≤ 0.017 and median widths of 0.06–0.12.
  - The worst per-weight coverage is 0.88–0.91 with percentile intervals and 0.87–0.91 with BCa. That is at the 0.9 gate, within its Monte Carlo error (about ±0.03 at 100 replicates).
- **On A/H E5 SAT the members' small weights are not well covered even then.**
  - The weights planted at 0.02–0.05 are covered in 57–87% of replicates.
  - Qwen3-32B's π₀ is covered in 84%.
  - So intervals on those weights are too narrow to trust.
- **But the near-miss model does not reproduce the data in five of the six fits**:
  - **Colouring, both runs.** The fitted mixtures expect 33% and 39% of answers to equal a member's answer; the data have 0% and 28%.
  - **Qwen3-32B on knapsack.** It expects 46%; the data have 8%.
  - **A/H E5 SAT, both runs.** q puts half its mass on UNSAT, so the fits expect 47% and 43% UNSAT answers, against 3% and 27%. They also expect about half the answers to lie beyond every member's slip reach, against 27% and 32%. gpt-oss-20b's fit also expects 7% exact matches, against 0%.
  - **Why.** In each of these fits the slip rate is at its cap. The answers miss the members more often, or by more, than a near-miss model with ε ≤ 0.5 can produce, and q is the wrong shape for what is left. The weights are the best fit of a model that cannot generate these answers.
- **gpt-oss-20b on knapsack passes all three statistics**: 72% exact matches against 72% expected, nothing beyond reach, no special tokens. Its slip rate is inside its range.

Per-quantity detail of the recovery check (quantities planted at 0 are listed only where their mean estimate is at least 0.02):

<!-- BEGIN prelim:recovery_detail -->
| Unit | Run | Quantity | Planted | Mean estimate | Bias | Coverage, percentile | Coverage, BCa | Median width (percentile) |
|---|---|---|---|---|---|---|---|---|
| C_E2/colouring | Qwen3-32B direct | DPLL-LIST (D) | 0.023 | 0.025 | +0.002 | 0.97 | 0.98 | 0.066 |
| C_E2/colouring | Qwen3-32B direct | DSATUR | 0.038 | 0.037 | -0.002 | 0.93 | 0.96 | 0.056 |
| C_E2/colouring | Qwen3-32B direct | EXACT | 0.405 | 0.395 | -0.010 | 0.92 | 0.90 | 0.146 |
| C_E2/colouring | Qwen3-32B direct | FF-LABEL | 0.044 | 0.041 | -0.003 | 0.96 | 0.97 | 0.045 |
| C_E2/colouring | Qwen3-32B direct | FF-LIST = GREEDY+REPAIR-LIST (C->F) | 0.104 | 0.104 | -0.001 | 0.91 | 0.92 | 0.068 |
| C_E2/colouring | Qwen3-32B direct | LF | 0.053 | 0.051 | -0.001 | 0.93 | 0.93 | 0.053 |
| C_E2/colouring | Qwen3-32B direct | unexplained (q) | 0.333 | 0.334 | +0.000 | 0.91 | 0.90 | 0.106 |
| C_E2/colouring | gpt-oss-20b thinking-low | DPLL-LIST (D) | 0.029 | 0.030 | +0.002 | 0.88 | 0.93 | 0.070 |
| C_E2/colouring | gpt-oss-20b thinking-low | DSATUR-LABEL | 0.040 | 0.037 | -0.003 | 0.92 | 0.96 | 0.059 |
| C_E2/colouring | gpt-oss-20b thinking-low | EXACT | 0.150 | 0.142 | -0.008 | 0.96 | 0.98 | 0.113 |
| C_E2/colouring | gpt-oss-20b thinking-low | FF-LABEL | 0.036 | 0.036 | -0.000 | 0.89 | 0.94 | 0.042 |
| C_E2/colouring | gpt-oss-20b thinking-low | FF-LIST = GREEDY+REPAIR-LIST (C->F) | 0.346 | 0.347 | +0.001 | 0.91 | 0.90 | 0.108 |
| C_E2/colouring | gpt-oss-20b thinking-low | LF | 0.038 | 0.039 | +0.000 | 0.93 | 0.96 | 0.046 |
| C_E2/colouring | gpt-oss-20b thinking-low | RO-FF (C3) | 0.275 | 0.273 | -0.002 | 0.94 | 0.94 | 0.101 |
| C_E2/colouring | gpt-oss-20b thinking-low | unexplained (q) | 0.087 | 0.085 | -0.002 | 0.99 | 0.99 | 0.066 |
| C_E2/knapsack | Qwen3-32B direct | DIFF | 0.147 | 0.139 | -0.008 | 0.91 | 0.91 | 0.123 |
| C_E2/knapsack | Qwen3-32B direct | EXACT | 0.085 | 0.080 | -0.004 | 0.93 | 0.92 | 0.091 |
| C_E2/knapsack | Qwen3-32B direct | RATIO+BEST-SINGLE = RATIO-PREFIX | 0.586 | 0.570 | -0.016 | 0.94 | 0.94 | 0.160 |
| C_E2/knapsack | Qwen3-32B direct | VALUE | 0.080 | 0.076 | -0.005 | 0.92 | 0.93 | 0.075 |
| C_E2/knapsack | Qwen3-32B direct | unexplained (q) | 0.102 | 0.119 | +0.017 | 0.95 | 0.87 | 0.127 |
| C_E2/knapsack | gpt-oss-20b thinking-low | DIFF | 0.097 | 0.093 | -0.004 | 0.89 | 0.92 | 0.110 |
| C_E2/knapsack | gpt-oss-20b thinking-low | EXACT | 0.619 | 0.613 | -0.006 | 0.96 | 0.96 | 0.139 |
| C_E2/knapsack | gpt-oss-20b thinking-low | RATIO+BEST-SINGLE = RATIO-PREFIX | 0.032 | 0.031 | -0.000 | 0.93 | 0.94 | 0.062 |
| C_E2/knapsack | gpt-oss-20b thinking-low | RATIO-SKIP | 0.137 | 0.136 | -0.000 | 0.92 | 0.91 | 0.131 |
| C_E2/knapsack | gpt-oss-20b thinking-low | VALUE | 0.116 | 0.118 | +0.003 | 0.92 | 0.94 | 0.091 |
| AH_E5/SAT | Qwen3-32B direct | C0 POLARITY | 0.025 | 0.021 | -0.004 | 0.75 | 0.78 | 0.052 |
| AH_E5/SAT | Qwen3-32B direct | exact | 0.024 | 0.013 | -0.011 | 0.57 | 0.70 | 0.034 |
| AH_E5/SAT | Qwen3-32B direct | unexplained (q) | 0.951 | 0.959 | +0.008 | 0.84 | 0.88 | 0.080 |
| AH_E5/SAT | gpt-oss-20b thinking-low | C0 POLARITY | 0.052 | 0.049 | -0.002 | 0.85 | 0.92 | 0.091 |
| AH_E5/SAT | gpt-oss-20b thinking-low | D DPLL (first solution) | 0.030 | 0.029 | -0.001 | 0.81 | 0.85 | 0.079 |
| AH_E5/SAT | gpt-oss-20b thinking-low | exact | 0.049 | 0.043 | -0.006 | 0.87 | 0.91 | 0.101 |
| AH_E5/SAT | gpt-oss-20b thinking-low | unexplained (q) | 0.869 | 0.876 | +0.006 | 0.91 | 0.90 | 0.147 |
<!-- END prelim:recovery_detail -->

## 4. Agreement, and the permutation baselines

- **EA** (error agreement) is P(y = h(x) | y wrong, h(x) wrong): among items where both the answer and member h's answer are wrong, how often they are the same answer. **Co-error** is P(y = h(x) | h(x) wrong), the rate at which the model makes h's errors. Both use exact agreement, with ties included (`ties="include"`: a wrong answer shared by several members counts for each). Set-valued members have no single wrong answer and get neither.
- **Chance** is the engine's within-cell permutation baseline. Answers are shuffled among items of the same cell whose answer spaces match (the same item letters, or the same variable names), 2,000 times, and the statistic is recomputed; the weights are refitted (point estimates). **Lift** is observed minus chance, and **p** is the one-sided permutation p-value. Its smallest possible value is 1/2,001 ≈ 0.0005.
- **Multiple comparisons.** Each fit tests up to 8 quantities on each of three statistics. A Bonferroni threshold of 0.05/8 ≈ 0.006 per statistic within a fit is passed by the knapsack lifts at the floor and by two of gpt-oss-20b's A/H E5 SAT weights (p = 0.002 and 0.005). Treat larger p-values as exploratory.
- **C E2 colouring has no permutation baseline.** Its exchangeable share is 0: no two items in a cell share their vertex labels, so the engine's shuffle cannot move any answer, and it reports no chance level, lift or p-value. The only chance level available is q's. A uniformly random colouring (q) equals a given member's exact colouring with probability at most 3 × 10⁻¹³ on these items (`q_exact_chance_log10_max` in the JSON: −12.5). That floor is far too low to be a fair bar: answers that look like colourings at all would clear it.

### 4.1 C E2 colouring

<!-- BEGIN prelim:agreement_C_E2_colouring -->
| Run | Member group | Exchangeable share | EA (agree / both wrong) | chance | lift | p | co-error (agree / member wrong) | chance | lift | p | π | chance | lift | p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-32B direct | DPLL-LIST (D) | 0.00 | – | – | – | – | – | – | – | – | 0.023 | – | – | – |
| Qwen3-32B direct | DSATUR | 0.00 | 0.000 (0/143) | – | – | – | 0.000 (0/143) | – | – | – | 0.038 | – | – | – |
| Qwen3-32B direct | DSATUR-LABEL | 0.00 | 0.000 (0/90) | – | – | – | 0.000 (0/90) | – | – | – | 0.000 | – | – | – |
| Qwen3-32B direct | EXACT | 0.00 | – | – | – | – | – | – | – | – | 0.405 | – | – | – |
| Qwen3-32B direct | FF-LABEL | 0.00 | 0.000 (0/228) | – | – | – | 0.000 (0/228) | – | – | – | 0.044 | – | – | – |
| Qwen3-32B direct | FF-LIST = GREEDY+REPAIR-LIST (C->F) | 0.00 | 0.000 (0/244) | – | – | – | 0.000 (0/244) | – | – | – | 0.104 | – | – | – |
| Qwen3-32B direct | LF | 0.00 | 0.000 (0/222) | – | – | – | 0.000 (0/222) | – | – | – | 0.053 | – | – | – |
| Qwen3-32B direct | NOISY-EXACT | 0.00 | – | – | – | – | – | – | – | – | 0.000 | – | – | – |
| Qwen3-32B direct | RO-FF (C3) | 0.00 | – | – | – | – | – | – | – | – | 0.000 | – | – | – |
| Qwen3-32B direct | unexplained (q) | 0.00 | – | – | – | – | – | – | – | – | 0.333 | – | – | – |
| gpt-oss-20b thinking-low | DPLL-LIST (D) | 0.00 | – | – | – | – | – | – | – | – | 0.029 | – | – | – |
| gpt-oss-20b thinking-low | DSATUR | 0.00 | 0.000 (0/137) | – | – | – | 0.000 (0/143) | – | – | – | 0.000 | – | – | – |
| gpt-oss-20b thinking-low | DSATUR-LABEL | 0.00 | 0.012 (1/86) | – | – | – | 0.011 (1/90) | – | – | – | 0.040 | – | – | – |
| gpt-oss-20b thinking-low | EXACT | 0.00 | – | – | – | – | – | – | – | – | 0.150 | – | – | – |
| gpt-oss-20b thinking-low | FF-LABEL | 0.00 | 0.000 (0/216) | – | – | – | 0.000 (0/227) | – | – | – | 0.036 | – | – | – |
| gpt-oss-20b thinking-low | FF-LIST = GREEDY+REPAIR-LIST (C->F) | 0.00 | 0.172 (40/232) | – | – | – | 0.164 (40/244) | – | – | – | 0.346 | – | – | – |
| gpt-oss-20b thinking-low | LF | 0.00 | 0.009 (2/215) | – | – | – | 0.009 (2/222) | – | – | – | 0.038 | – | – | – |
| gpt-oss-20b thinking-low | NOISY-EXACT | 0.00 | – | – | – | – | – | – | – | – | 0.000 | – | – | – |
| gpt-oss-20b thinking-low | RO-FF (C3) | 0.00 | – | – | – | – | – | – | – | – | 0.275 | – | – | – |
| gpt-oss-20b thinking-low | unexplained (q) | 0.00 | – | – | – | – | – | – | – | – | 0.087 | – | – | – |
<!-- END prelim:agreement_C_E2_colouring -->

### 4.2 C E2 knapsack

<!-- BEGIN prelim:agreement_C_E2_knapsack -->
| Run | Member group | Exchangeable share | EA (agree / both wrong) | chance | lift | p | co-error (agree / member wrong) | chance | lift | p | π | chance | lift | p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-32B direct | DIFF | 1.00 | 0.043 (11/256) | 0.004 | 0.039 | 0.0005 | 0.043 (11/257) | 0.004 | 0.039 | 0.0005 | 0.147 | 0.003 | 0.144 | 0.0005 |
| Qwen3-32B direct | EXACT | 1.00 | – | – | – | – | – | – | – | – | 0.085 | 0.004 | 0.081 | 0.0005 |
| Qwen3-32B direct | INPUT-FIT | 1.00 | 0.000 (0/294) | 0.000 | -0.000 | 1.000 | 0.000 (0/295) | 0.000 | -0.000 | 1.000 | 0.000 | 0.000 | -0.000 | 0.189 |
| Qwen3-32B direct | LARGEST-FIT | 1.00 | 0.000 (0/299) | 0.003 | -0.003 | 1.000 | 0.000 (0/300) | 0.003 | -0.003 | 1.000 | 0.000 | 0.006 | -0.006 | 0.754 |
| Qwen3-32B direct | RATIO+BEST-SINGLE = RATIO-PREFIX | 1.00 | 0.056 (15/266) | 0.005 | 0.051 | 0.0005 | 0.056 (15/267) | 0.005 | 0.051 | 0.0005 | 0.586 | 0.013 | 0.573 | 0.0005 |
| Qwen3-32B direct | RATIO-SKIP | 1.00 | 0.039 (9/228) | 0.005 | 0.035 | 0.0005 | 0.039 (9/228) | 0.005 | 0.035 | 0.0005 | 0.000 | 0.002 | -0.002 | 0.284 |
| Qwen3-32B direct | VALUE | 1.00 | 0.005 (1/207) | 0.003 | 0.002 | 0.245 | 0.005 (1/208) | 0.002 | 0.002 | 0.417 | 0.080 | 0.003 | 0.077 | 0.0005 |
| Qwen3-32B direct | unexplained (q) | 1.00 | – | – | – | – | – | – | – | – | 0.102 | 0.969 | -0.867 | 1.000 |
| gpt-oss-20b thinking-low | DIFF | 1.00 | 0.216 (27/125) | 0.007 | 0.209 | 0.0005 | 0.105 (27/257) | 0.007 | 0.098 | 0.0005 | 0.096 | 0.005 | 0.091 | 0.0005 |
| gpt-oss-20b thinking-low | EXACT | 1.00 | – | – | – | – | – | – | – | – | 0.616 | 0.039 | 0.577 | 0.0005 |
| gpt-oss-20b thinking-low | INPUT-FIT | 1.00 | 0.007 (1/139) | 0.001 | 0.006 | 0.0015 | 0.003 (1/295) | 0.001 | 0.003 | 0.187 | 0.004 | 0.001 | 0.004 | 0.034 |
| gpt-oss-20b thinking-low | LARGEST-FIT | 1.00 | 0.000 (0/142) | 0.000 | -0.000 | 1.000 | 0.000 (0/300) | 0.000 | -0.000 | 1.000 | 0.000 | 0.000 | -0.000 | 0.694 |
| gpt-oss-20b thinking-low | RATIO+BEST-SINGLE = RATIO-PREFIX | 1.00 | 0.119 (16/134) | 0.004 | 0.116 | 0.0005 | 0.060 (16/267) | 0.004 | 0.056 | 0.0005 | 0.032 | 0.001 | 0.030 | 0.0005 |
| gpt-oss-20b thinking-low | RATIO-SKIP | 1.00 | 0.259 (29/112) | 0.008 | 0.251 | 0.0005 | 0.127 (29/228) | 0.008 | 0.119 | 0.0005 | 0.136 | 0.008 | 0.129 | 0.0005 |
| gpt-oss-20b thinking-low | VALUE | 1.00 | 0.188 (19/101) | 0.005 | 0.183 | 0.0005 | 0.091 (19/208) | 0.005 | 0.086 | 0.0005 | 0.115 | 0.006 | 0.109 | 0.0005 |
| gpt-oss-20b thinking-low | unexplained (q) | 1.00 | – | – | – | – | – | – | – | – | 0.000 | 0.940 | -0.940 | 1.000 |
<!-- END prelim:agreement_C_E2_knapsack -->

### 4.3 A/H E5 SAT

<!-- BEGIN prelim:agreement_AH_E5_SAT -->
| Run | Member group | Exchangeable share | EA (agree / both wrong) | chance | lift | p | co-error (agree / member wrong) | chance | lift | p | π | chance | lift | p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-32B direct | A3 TT[exact] | 1.00 | – | – | – | – | – | – | – | – | 0.000 | 0.038 | -0.038 | 0.797 |
| Qwen3-32B direct | C0 POLARITY | 1.00 | 0.000 (0/95) | 0.001 | -0.001 | 1.000 | 0.000 (0/95) | 0.001 | -0.001 | 1.000 | 0.024 | 0.008 | 0.016 | 0.133 |
| Qwen3-32B direct | C1 GREEDY | 1.00 | 0.000 (0/91) | 0.000 | 0.000 | 1.000 | 0.000 (0/91) | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | -0.000 | 0.359 |
| Qwen3-32B direct | D DPLL (first solution) | 1.00 | – | – | – | – | – | – | – | – | 0.009 | 0.002 | 0.007 | 0.082 |
| Qwen3-32B direct | exact | 1.00 | – | – | – | – | – | – | – | – | 0.024 | 0.006 | 0.018 | 0.106 |
| Qwen3-32B direct | unexplained (q) | 1.00 | – | – | – | – | – | – | – | – | 0.942 | 0.945 | -0.003 | 0.557 |
| gpt-oss-20b thinking-low | A3 TT[exact] | 1.00 | – | – | – | – | – | – | – | – | 0.000 | 0.002 | -0.002 | 0.136 |
| gpt-oss-20b thinking-low | C0 POLARITY | 1.00 | 0.000 (0/97) | 0.000 | 0.000 | 1.000 | 0.000 (0/97) | 0.000 | 0.000 | 1.000 | 0.052 | 0.002 | 0.050 | 0.0020 |
| gpt-oss-20b thinking-low | C1 GREEDY | 1.00 | 0.000 (0/93) | 0.000 | 0.000 | 1.000 | 0.000 (0/93) | 0.000 | 0.000 | 1.000 | 0.000 | 0.001 | -0.001 | 0.270 |
| gpt-oss-20b thinking-low | D DPLL (first solution) | 1.00 | – | – | – | – | – | – | – | – | 0.030 | 0.005 | 0.025 | 0.013 |
| gpt-oss-20b thinking-low | exact | 1.00 | – | – | – | – | – | – | – | – | 0.049 | 0.006 | 0.042 | 0.0050 |
| gpt-oss-20b thinking-low | unexplained (q) | 1.00 | – | – | – | – | – | – | – | – | 0.869 | 0.984 | -0.114 | 1.000 |
<!-- END prelim:agreement_AH_E5_SAT -->

**Reading.**

- **C E2 knapsack.** Every lift worth reading has p = 0.0005, the floor, which passes the Bonferroni threshold within its fit.
  - **gpt-oss-20b.**
    - Where both are wrong, its answer equals RATIO-SKIP's on 0.26 of items, DIFF's on 0.22, VALUE's on 0.19 and the ratio-greedy prefix's on 0.12. The chance levels are 0.004–0.008.
    - The weights are EXACT 0.616 (chance 0.039), and RATIO-SKIP 0.136, VALUE 0.115 and DIFF 0.096 (chance 0.005–0.008).
  - **Qwen3-32B.**
    - Its EA is 0.056 for the ratio-greedy prefix, 0.043 for DIFF and 0.039 for RATIO-SKIP, against chance levels of 0.004–0.005.
    - Its weights are RATIO-PREFIX 0.586 (chance 0.013), and DIFF 0.147, EXACT 0.085 and VALUE 0.080 (chance 0.003–0.004).
    - VALUE's weight is above chance while its EA is not (1 of 207; p = 0.245): its weight is near misses.
  - **The shuffles.** The mixture gives shuffled answers π₀ = 0.94–0.97. The weights above come from the link between each answer and its own item.
- **C E2 colouring has no permutation baseline** (above). The exact counts are in §4.1: FF-LIST 40 of 232 for gpt-oss-20b, and 0–2 for every other deterministic member; 0 of everything for Qwen3-32B.
- **A/H E5 SAT has no exact agreement at all.** No answer equals any member's wrong answer, so EA and co-error are 0, against chance levels of 0.000–0.001.
  - Qwen3-32B's unexplained mass is at its chance level: 0.942 against 0.945.
  - gpt-oss-20b's is below its chance level: 0.869 against 0.984. POLARITY's weight (0.052) and the stated-rule solutions' (0.049) are above their chance levels (0.002 and 0.006; p = 0.002 and 0.005). DPLL's 0.030 is weakly above (chance 0.005; p = 0.013).
  - No answer equals any of these members' answers. So this says only that gpt-oss-20b's assignments lie nearer to those members' answers, within the slip kernel's reach, than shuffled assignments do. The recovery check also finds these small weights' intervals too narrow (§3.5).

How many answers are wrong (the pool EA is computed on):

<!-- BEGIN prelim:wrong -->
| Unit | Run | ok answers | wrong | correct |
|---|---|---|---|---|
| C_E2/colouring | Qwen3-32B direct | 300 | 300 | 0 |
| C_E2/colouring | gpt-oss-20b thinking-low | 299 | 256 | 43 |
| C_E2/knapsack | Qwen3-32B direct | 300 | 299 | 1 |
| C_E2/knapsack | gpt-oss-20b thinking-low | 300 | 142 | 158 |
| AH_E5/SAT | Qwen3-32B direct | 95 | 95 | 0 |
| AH_E5/SAT | gpt-oss-20b thinking-low | 97 | 97 | 0 |
<!-- END prelim:wrong -->

## 5. Excluded responses

Responses that are not `ok` are kept out of the likelihood and counted per cell and category (DESIGN §5 rule 5). On the fitted units of the pilot runs:

<!-- BEGIN prelim:excluded -->
| Unit | Run | Cell | Excluded (category count) | Of the cell's responses |
|---|---|---|---|---|
| C_E2/colouring | Qwen3-32B direct | – | none | 0 of 300 |
| C_E2/colouring | gpt-oss-20b thinking-low | COL/FF-vs-DSATUR/G-ONLY | parse_fail 1 | 1 of 20 |
| C_E2/knapsack | Qwen3-32B direct | – | none | 0 of 300 |
| C_E2/knapsack | gpt-oss-20b thinking-low | – | none | 0 of 300 |
| AH_E5/SAT | Qwen3-32B direct | SAT/I+R | parse_fail 1 | 1 of 20 |
| AH_E5/SAT | Qwen3-32B direct | SAT/P | parse_fail 4 | 4 of 20 |
| AH_E5/SAT | gpt-oss-20b thinking-low | SAT/I | parse_fail 1 | 1 of 20 |
| AH_E5/SAT | gpt-oss-20b thinking-low | SAT/N | parse_fail 2 | 2 of 20 |
<!-- END prelim:excluded -->

- **No response on the fitted units was truncated.** Truncation is censoring (SCOPE §6 rule 2): a truncated response would be excluded, and the fit has no token model to correct for that.
- **Elsewhere, only the direct condition truncated**, at its 1,024-token cap: on the pilot run, 1 of 120 C E1 SAT responses; on the dev runs, A/H E2 SAT (4 of 40 for Qwen3-32B, 10 of 40 for Qwen3-14B), C E1 SAT (1 of 30 each) and C E3 (1 of 270, Qwen3-32B). gpt-oss-20b at low effort never reached its 32,768 cap. Per-unit counts are in §6, and per-cell counts in the JSON (`truncated_by_cell`).

## 6. Descriptive statistics for every run and unit

From the scorer's own fields (`category`, `correct`, `valid`, `members_matched`, `sets_matched`; docs/RUNNER.md, "The scored record"):

- **Correct** and **valid** are among ok answers. On entailment and decision units `valid` is not defined, and is shown as "–".
- **Members matched** are the members whose prediction has the same channel value as the answer. A set-valued member appears there only when its set has one solution. Members that match exactly the same answers are merged ("A = B"), and the top three are shown.
- **Sets matched** are the set-valued members (EXACT, TT[exact]) whose solution set contains the answer.
- **Special-token answers** are UNSAT, IMPOSSIBLE or X answers given as `ok`.
- **ALWAYS-UNSAT is missing on the C SAT units.** The scorer ran before #22 added it, so `members_matched` never lists it there. It predicts UNSAT on every item, so the UNSAT count among the special-token answers is its match count.

These are counts, not mixture weights. On a unit that is not fitted they say which members' answers the model gave, not which procedure produced them. Some patterns stand out in the tables. They are counts on 5–20 items per cell, with one sample each:

- **Constant decisions on the A/H colouring decision items.** On A/H E1 and E2 colouring, each dev run gave the same decision on (nearly) every item:
  - Qwen3-32B direct said POSSIBLE on all 60;
  - Qwen3-14B direct said IMPOSSIBLE on all 60, and gpt-oss-20b on 59.
  - Their accuracy, 29–31 of 60, is what a constant answer scores on these items.
- **Give-up answers on witness tasks.** gpt-oss-20b answered:
  - IMPOSSIBLE on 24 of 25 C E5 colouring (k = 3) items, getting none right;
  - IMPOSSIBLE on 150 of 269 C E3 items;
  - UNSAT on 80 of 200 pilot C E2 SAT items, and 53 of 110 C E1 SAT items.
- **Qwen3 direct colourings are rarely valid.** On C E1 and C E2 colouring, 2 of 420 pilot answers and 27 of 210 dev answers from the two Qwen3 models are valid colourings.
- **B4/C4 entailment is near ceiling** in all three dev runs (81–99% correct).

### 6.1 Pilot-size runs (20 per cell)

<!-- BEGIN prelim:desc_pilot -->
| Unit | Run | Responses | ok | Not ok | Correct of ok | Valid of ok | Match ≥1 member (of ok) | Wrong answers matching ≥1 member | Members matched most (answers) | Sets matched (answers) | Special-token answers | Median tokens: reasoning / completion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AH_E5/COL | Qwen3-32B direct | 80 | 80 | – | 5/80 (6%) | 5/66 (8%) | 14/80 (18%) | 11/75 (15%) | C1 FIRST-FIT (stated rule) 13; B1 DROP-CONSTRAINT(last 3) 4; C2 DSATUR (stated rule) = D DPLL (first solution) 3 | exact 4; A3 TT[exact] 1 | IMPOSSIBLE 14 | 0 / 74 |
| AH_E5/COL | gpt-oss-20b thinking-low | 80 | 78 | parse_fail 1, partial 1 | 32/78 (41%) | 32/36 (89%) | 34/78 (44%) | 19/46 (41%) | C1 FIRST-FIT (stated rule) 27; D DPLL (first solution) 15; exact = C2 DSATUR (stated rule) 13 | exact 19; A3 TT[exact] 16 | IMPOSSIBLE 42 | 890 / 960 |
| AH_E5/ENT | Qwen3-32B direct | 80 | 80 | – | 8/80 (10%) | – | 17/80 (21%) | 9/72 (12%) | A3 TT[exact] 16; exact 8; B4 FIRST 3 | – | – | 0 / 26 |
| AH_E5/ENT | gpt-oss-20b thinking-low | 80 | 69 | parse_fail 11 | 50/69 (72%) | – | 58/69 (84%) | 8/19 (42%) | exact 50; A3 TT[exact] 32; B4 FIRST 24 | – | – | 626 / 648 |
| AH_E5/KNAP | Qwen3-32B direct | 80 | 80 | – | 4/80 (5%) | 48/80 (60%) | 8/80 (10%) | 4/76 (5%) | A3 TT[exact] 5; exact = C1 RATIO-SKIP 4; C1 VALUE 3 | – | – | 0 / 19 |
| AH_E5/KNAP | gpt-oss-20b thinking-low | 80 | 80 | – | 60/80 (75%) | 74/80 (92%) | 55/80 (69%) | 1/20 (5%) | exact 50; C1 RATIO-SKIP 31; A3 TT[exact] 27 | exact 10; A3 TT[exact] 4 | – | 1,157 / 1,178 |
| AH_E5/SAT (fitted) | Qwen3-32B direct | 100 | 95 | parse_fail 5 | 0/95 (0%) | 0/92 (0%) | 0/95 (0%) | 0/95 (0%) | – | – | UNSAT 3 | 0 / 29 |
| AH_E5/SAT (fitted) | gpt-oss-20b thinking-low | 100 | 97 | parse_fail 3 | 0/97 (0%) | 0/71 (0%) | 0/97 (0%) | 0/97 (0%) | – | – | UNSAT 26 | 2,140 / 2,164 |
| C_E1/3-SAT | Qwen3-32B direct | 120 | 116 | parse_fail 3, truncated 1 | 6/116 (5%) | 6/101 (6%) | 13/116 (11%) | 12/110 (11%) | UC-DET (C2) 12; GUC-DET (C2) 6; GREEDY-OUT (AR) 1 | EXACT 6 | UNSAT 15 | 0 / 103 |
| C_E1/3-SAT | gpt-oss-20b thinking-low | 120 | 110 | parse_fail 8, partial 2 | 7/110 (6%) | 7/57 (12%) | 46/110 (42%) | 46/103 (45%) | UC-DET (C2) 40; GUC-DET (C2) 27; GREEDY-OUT (AR) 4 | EXACT 7 | UNSAT 53 | 386 / 486 |
| C_E1/colouring | Qwen3-32B direct | 120 | 120 | – | 1/120 (1%) | 1/120 (1%) | 0/120 (0%) | 0/119 (0%) | – | EXACT 1 | – | 0 / 116 |
| C_E1/colouring | gpt-oss-20b thinking-low | 120 | 118 | parse_fail 2 | 66/118 (56%) | 104/118 (88%) | 14/118 (12%) | 4/52 (8%) | FF-LIST = GREEDY+REPAIR-LIST (C->F) 12; FF-OUT (AR) 9; DPLL-LIST (D) 8 | EXACT 66 | – | 1,254 / 1,358 |
| C_E2/3-SAT | Qwen3-32B direct | 200 | 199 | partial 1 | 2/199 (1%) | 0/194 (0%) | 5/199 (3%) | 3/197 (2%) | GREEDY-INDEX = GREEDY-MENTION 5; GUC-DET (C2) = UC-DET (C2) 4; DPLL-MENTION (D, T first) = EXACT = SC-DET (C2) 2 | – | UNSAT 5 | 0 / 103 |
| C_E2/3-SAT | gpt-oss-20b thinking-low | 200 | 200 | – | 16/200 (8%) | 3/120 (2%) | 80/200 (40%) | 67/184 (36%) | GUC-DET (C2) 71; UC-DET (C2) 70; GREEDY-INDEX = GREEDY-MENTION 62 | EXACT 3 | UNSAT 80 | 1,492 / 1,590 |
| C_E2/colouring (fitted) | Qwen3-32B direct | 300 | 300 | – | 0/300 (0%) | 1/300 (0%) | 0/300 (0%) | 0/300 (0%) | – | – | – | 0 / 116 |
| C_E2/colouring (fitted) | gpt-oss-20b thinking-low | 300 | 299 | parse_fail 1 | 43/299 (14%) | 246/299 (82%) | 53/299 (18%) | 41/256 (16%) | FF-LIST = GREEDY+REPAIR-LIST (C->F) 47; DPLL-LIST (D) 10; LF 4 | EXACT 43 | – | 1,007 / 1,110 |
| C_E2/knapsack (fitted) | Qwen3-32B direct | 300 | 300 | – | 1/300 (0%) | 272/300 (91%) | 24/300 (8%) | 23/299 (8%) | RATIO+BEST-SINGLE = RATIO-PREFIX 15; DIFF 11; RATIO-SKIP 10 | – | – | 0 / 8 |
| C_E2/knapsack (fitted) | gpt-oss-20b thinking-low | 300 | 300 | – | 158/300 (53%) | 293/300 (98%) | 215/300 (72%) | 57/142 (40%) | EXACT 158; RATIO-SKIP 71; VALUE 70 | – | – | 828 / 844 |
<!-- END prelim:desc_pilot -->

### 6.2 Dev-size runs (5 per cell)

<!-- BEGIN prelim:desc_dev -->
| Unit | Run | Responses | ok | Not ok | Correct of ok | Valid of ok | Match ≥1 member (of ok) | Wrong answers matching ≥1 member | Members matched most (answers) | Sets matched (answers) | Special-token answers | Median tokens: reasoning / completion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AH_E1/COL | Qwen3-32B direct | 20 | 20 | – | 11/20 (55%) | 0/20 (0%) | 20/20 (100%) | 9/9 (100%) | A1 ALWAYS-POSSIBLE = A2 DENSITY-D 20; A2 DENSITY-U 18; A2 LENGTH-M 16 | – | – | 0 / 135 |
| AH_E1/COL | Qwen3-14B direct | 20 | 20 | – | 9/20 (45%) | – | 20/20 (100%) | 11/11 (100%) | A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT 20; D DPLL-b 11; C2 DSATUR = exact 9 | – | IMPOSSIBLE 20 | 0 / 11 |
| AH_E1/COL | gpt-oss-20b thinking-low | 20 | 20 | – | 9/20 (45%) | – | 20/20 (100%) | 11/11 (100%) | A1 ALWAYS-IMPOSSIBLE = B4 ADD-CONSTRAINT(adjacent) = C1 FIRST-FIT 20; D DPLL-b 11; C2 DSATUR = exact 9 | – | IMPOSSIBLE 20 | 58 / 74 |
| AH_E1/ENT | Qwen3-32B direct | 20 | 20 | – | 9/20 (45%) | – | 20/20 (100%) | 11/11 (100%) | A2 FREQ 14; A2 RECENCY 14; B4 MATCH 12 | – | – | 0 / 7 |
| AH_E1/ENT | Qwen3-14B direct | 20 | 20 | – | 13/20 (65%) | – | 20/20 (100%) | 7/7 (100%) | B1 UP-1 15; A2 FREQ 14; A2 RECENCY 14 | – | – | 0 / 7 |
| AH_E1/ENT | gpt-oss-20b thinking-low | 20 | 20 | – | 19/20 (95%) | – | 20/20 (100%) | 1/1 (100%) | exact 19; B1 UP-2 = B1 UP-3 18; B1 UP-1 17 | – | – | 499 / 511 |
| AH_E1/SAT | Qwen3-32B direct | 30 | 30 | – | 17/30 (57%) | 0/23 (0%) | 30/30 (100%) | 13/13 (100%) | A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY 27; B1 UP-3 = D∘DENSITY 26; A2 LENGTH-M 19 | – | UNSAT 3 | 0 / 29 |
| AH_E1/SAT | Qwen3-14B direct | 30 | 30 | – | 16/30 (53%) | 0/17 (0%) | 30/30 (100%) | 14/14 (100%) | A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY 28; B1 UP-3 = D∘DENSITY 25; A2 LENGTH-M 20 | – | UNSAT 2 | 0 / 29 |
| AH_E1/SAT | gpt-oss-20b thinking-low | 30 | 30 | – | 18/30 (60%) | 1/15 (7%) | 30/30 (100%) | 12/12 (100%) | B1 UP-3 = D∘DENSITY 19; A1 ALWAYS-SAT = A2 DENSITY-D = A2 DENSITY-U = C0 POLARITY 18; A2 LENGTH-M 18 | – | UNSAT 12 | 1,725 / 1,750 |
| AH_E2/COL | Qwen3-32B direct | 40 | 40 | – | 20/40 (50%) | 0/34 (0%) | 40/40 (100%) | 20/20 (100%) | A1 ALWAYS-POSSIBLE 40; A2 DENSITY-D = A2 DENSITY-U 30; A2 LENGTH-M 20 | – | – | 0 / 191 |
| AH_E2/COL | Qwen3-14B direct | 40 | 40 | – | 20/40 (50%) | – | 40/40 (100%) | 20/20 (100%) | A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT 40; B4 ADD-CONSTRAINT(adjacent) 38; C2 DSATUR 28 | – | IMPOSSIBLE 40 | 0 / 11 |
| AH_E2/COL | gpt-oss-20b thinking-low | 40 | 40 | – | 21/40 (52%) | 0/1 (0%) | 40/40 (100%) | 19/19 (100%) | A1 ALWAYS-IMPOSSIBLE = C1 FIRST-FIT 39; B4 ADD-CONSTRAINT(adjacent) 37; C2 DSATUR 29 | – | IMPOSSIBLE 39 | 60 / 77 |
| AH_E2/ENT | Qwen3-32B direct | 40 | 40 | – | 23/40 (58%) | – | 40/40 (100%) | 17/17 (100%) | A2 FREQ 29; A2 PRIMACY 25; B4 MATCH 25 | – | – | 0 / 7 |
| AH_E2/ENT | Qwen3-14B direct | 40 | 40 | – | 24/40 (60%) | – | 40/40 (100%) | 16/16 (100%) | A1 ALWAYS-YES 30; D case-split (b = 4) 29; A2 FREQ 24 | – | – | 0 / 7 |
| AH_E2/ENT | gpt-oss-20b thinking-low | 40 | 40 | – | 38/40 (95%) | – | 40/40 (100%) | 2/2 (100%) | exact 38; B4 MATCH 34; D case-split (b = 4) 31 | – | – | 546 / 558 |
| AH_E2/SAT | Qwen3-32B direct | 40 | 36 | truncated 4 | 16/36 (44%) | 0/7 (0%) | 36/36 (100%) | 20/20 (100%) | A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY 27; A2 DENSITY-D = A2 DENSITY-U = D∘DENSITY 23; A2 LENGTH-M = A2 LENGTH-T 18 | – | UNSAT 9 | 0 / 38 |
| AH_E2/SAT | Qwen3-14B direct | 40 | 30 | truncated 10 | 15/30 (50%) | 0/11 (0%) | 30/30 (100%) | 15/15 (100%) | A1 ALWAYS-SAT = B1 UP-3 = C0 POLARITY 30; A2 DENSITY-D = A2 DENSITY-U = A2 LENGTH-M = A2 LENGTH-T = D∘DENSITY 20; exact 15 | – | – | 0 / 45 |
| AH_E2/SAT | gpt-oss-20b thinking-low | 40 | 40 | – | 18/40 (45%) | 0/10 (0%) | 40/40 (100%) | 22/22 (100%) | A2 LENGTH-M = A2 LENGTH-T 30; A2 DENSITY-D = A2 DENSITY-U = D∘DENSITY 26; A1 ALWAYS-UNSAT = C2 UC = D DPLL-b = D DPLL-b+PL 22 | – | UNSAT 22 | 466 / 484 |
| AH_E5/COL | Qwen3-32B direct | 20 | 20 | – | 0/20 (0%) | 0/17 (0%) | 3/20 (15%) | 3/20 (15%) | C1 FIRST-FIT (stated rule) 3 | – | IMPOSSIBLE 3 | 0 / 74 |
| AH_E5/COL | Qwen3-14B direct | 20 | 20 | – | 0/20 (0%) | 0/14 (0%) | 0/20 (0%) | 0/20 (0%) | – | – | IMPOSSIBLE 6 | 0 / 73 |
| AH_E5/COL | gpt-oss-20b thinking-low | 20 | 19 | partial 1 | 9/19 (47%) | 9/10 (90%) | 8/19 (42%) | 6/10 (60%) | C1 FIRST-FIT (stated rule) 6; exact = B1 DROP-CONSTRAINT(last 3) = C2 DSATUR (stated rule) = D DPLL (first solution) 2 | A3 TT[exact] = exact 7 | IMPOSSIBLE 9 | 886 / 954 |
| AH_E5/ENT | Qwen3-32B direct | 20 | 20 | – | 6/20 (30%) | – | 9/20 (45%) | 3/14 (21%) | A3 TT[exact] 9; exact 6 | – | – | 0 / 15 |
| AH_E5/ENT | Qwen3-14B direct | 20 | 20 | – | 4/20 (20%) | – | 8/20 (40%) | 4/16 (25%) | A3 TT[exact] 8; exact 4 | – | – | 0 / 19 |
| AH_E5/ENT | gpt-oss-20b thinking-low | 20 | 17 | parse_fail 3 | 12/17 (71%) | – | 15/17 (88%) | 3/5 (60%) | exact 12; B4 FIRST 9; A3 TT[exact] 5 | – | – | 574 / 601 |
| AH_E5/KNAP | Qwen3-32B direct | 20 | 20 | – | 0/20 (0%) | 12/20 (60%) | 1/20 (5%) | 1/20 (5%) | C1 VALUE 1 | – | – | 0 / 19 |
| AH_E5/KNAP | Qwen3-14B direct | 20 | 20 | – | 0/20 (0%) | 10/20 (50%) | 2/20 (10%) | 2/20 (10%) | C1 RATIO-SKIP 2 | – | – | 0 / 18 |
| AH_E5/KNAP | gpt-oss-20b thinking-low | 20 | 20 | – | 11/20 (55%) | 17/20 (85%) | 11/20 (55%) | 0/9 (0%) | exact 11; A3 TT[exact] 7; C1 VALUE 4 | – | – | 1,010 / 1,036 |
| AH_E5/SAT | Qwen3-32B direct | 25 | 24 | parse_fail 1 | 0/24 (0%) | 0/24 (0%) | 0/24 (0%) | 0/24 (0%) | – | – | – | 0 / 25 |
| AH_E5/SAT | Qwen3-14B direct | 25 | 25 | – | 0/25 (0%) | 0/25 (0%) | 0/25 (0%) | 0/25 (0%) | – | – | – | 0 / 25 |
| AH_E5/SAT | gpt-oss-20b thinking-low | 25 | 24 | parse_fail 1 | 0/24 (0%) | 0/16 (0%) | 0/24 (0%) | 0/24 (0%) | – | – | UNSAT 8 | 2,618 / 2,636 |
| B4C4_E1/entailment | Qwen3-32B direct | 140 | 140 | – | 114/140 (81%) | – | 140/140 (100%) | 26/26 (100%) | BICOND = CW-COMP = CW-MIN = EXACT = MM-G = MM-S1 = ONL(4) 114; MATCH-L 102; ONL(2) 99 | – | – | 0 / 5 |
| B4C4_E1/entailment | Qwen3-14B direct | 140 | 140 | – | 121/140 (86%) | – | 140/140 (100%) | 19/19 (100%) | BICOND = CW-COMP = CW-MIN = EXACT = MM-G = MM-S1 = ONL(4) 121; MATCH-L 109; ONL(2) 106 | – | – | 0 / 5 |
| B4C4_E1/entailment | gpt-oss-20b thinking-low | 140 | 138 | declared_impossible 1, parse_fail 1 | 133/138 (96%) | – | 138/138 (100%) | 5/5 (100%) | BICOND = CW-COMP = CW-MIN = EXACT = MM-G = MM-S1 = ONL(4) 133; ONL(2) 118; MATCH-L 117 | – | – | 181 / 228 |
| B4C4_E2/entailment | Qwen3-32B direct | 240 | 240 | – | 229/240 (95%) | – | 240/240 (100%) | 11/11 (100%) | ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 229; ETR-1p 204; CW-MIN 191 | – | – | 0 / 5 |
| B4C4_E2/entailment | Qwen3-14B direct | 240 | 240 | – | 223/240 (93%) | – | 240/240 (100%) | 17/17 (100%) | ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 223; ETR-1p 208; ETR-1p-R2 183 | – | – | 0 / 5 |
| B4C4_E2/entailment | gpt-oss-20b thinking-low | 240 | 240 | – | 237/240 (99%) | – | 240/240 (100%) | 3/3 (100%) | ETR-default = EXACT = FIRST = MATCH-A = MATCH-L = ONL(2) = ONL(4) = UP-1 237; ETR-1p 214; ETR-1p-R2 189 | – | – | 75 / 86 |
| C_E1/3-SAT | Qwen3-32B direct | 30 | 27 | parse_fail 2, truncated 1 | 1/27 (4%) | 1/27 (4%) | 0/27 (0%) | 0/26 (0%) | – | EXACT 1 | – | 0 / 103 |
| C_E1/3-SAT | Qwen3-14B direct | 30 | 28 | parse_fail 1, truncated 1 | 0/28 (0%) | 0/28 (0%) | 0/28 (0%) | 0/28 (0%) | – | – | – | 0 / 103 |
| C_E1/3-SAT | gpt-oss-20b thinking-low | 30 | 27 | parse_fail 2, partial 1 | 0/27 (0%) | 0/17 (0%) | 6/27 (22%) | 6/27 (22%) | GUC-DET (C2) 5; UC-DET (C2) 5 | – | UNSAT 10 | 333 / 421 |
| C_E1/colouring | Qwen3-32B direct | 30 | 30 | – | 0/30 (0%) | 0/30 (0%) | 0/30 (0%) | 0/30 (0%) | – | – | – | 0 / 116 |
| C_E1/colouring | Qwen3-14B direct | 30 | 30 | – | 0/30 (0%) | 4/30 (13%) | 0/30 (0%) | 0/30 (0%) | – | – | – | 0 / 116 |
| C_E1/colouring | gpt-oss-20b thinking-low | 30 | 29 | parse_fail 1 | 15/29 (52%) | 27/29 (93%) | 2/29 (7%) | 0/14 (0%) | DPLL-LABEL (D) = FF-LABEL = FF-OUT (AR) 2; DPLL-LIST (D) = FF-LIST = GREEDY+REPAIR-LIST (C->F) 1 | EXACT 15 | – | 1,322 / 1,426 |
| C_E2/3-SAT | Qwen3-32B direct | 50 | 49 | partial 1 | 1/49 (2%) | 0/45 (0%) | 4/49 (8%) | 3/48 (6%) | GUC-DET (C2) = SC-DET (C2) = UC-DET (C2) 4; GREEDY-INDEX = GREEDY-MENTION 3; DPLL-MENTION (D, T first) = EXACT 1 | – | UNSAT 4 | 0 / 103 |
| C_E2/3-SAT | Qwen3-14B direct | 50 | 50 | – | 0/50 (0%) | 0/50 (0%) | 0/50 (0%) | 0/50 (0%) | – | – | – | 0 / 103 |
| C_E2/3-SAT | gpt-oss-20b thinking-low | 50 | 50 | – | 4/50 (8%) | 0/24 (0%) | 26/50 (52%) | 22/46 (48%) | SC-DET (C2) 25; UC-DET (C2) 24; GUC-DET (C2) 23 | – | UNSAT 26 | 208 / 269 |
| C_E2/colouring | Qwen3-32B direct | 75 | 75 | – | 0/75 (0%) | 0/75 (0%) | 0/75 (0%) | 0/75 (0%) | – | – | – | 0 / 116 |
| C_E2/colouring | Qwen3-14B direct | 75 | 75 | – | 0/75 (0%) | 23/75 (31%) | 0/75 (0%) | 0/75 (0%) | – | – | – | 0 / 116 |
| C_E2/colouring | gpt-oss-20b thinking-low | 75 | 75 | – | 11/75 (15%) | 62/75 (83%) | 13/75 (17%) | 11/64 (17%) | FF-LIST = GREEDY+REPAIR-LIST (C->F) 12; LF 3; DPLL-LIST (D) 1 | EXACT 11 | – | 874 / 977 |
| C_E2/knapsack | Qwen3-32B direct | 75 | 75 | – | 0/75 (0%) | 56/75 (75%) | 1/75 (1%) | 1/75 (1%) | RATIO+BEST-SINGLE = RATIO-PREFIX 1 | – | – | 0 / 9 |
| C_E2/knapsack | Qwen3-14B direct | 75 | 75 | – | 2/75 (3%) | 43/75 (57%) | 7/75 (9%) | 5/73 (7%) | DIFF 5; RATIO-SKIP 4; RATIO+BEST-SINGLE = RATIO-PREFIX 3 | – | – | 0 / 9 |
| C_E2/knapsack | gpt-oss-20b thinking-low | 75 | 75 | – | 34/75 (45%) | 71/75 (95%) | 50/75 (67%) | 16/41 (39%) | EXACT 34; DIFF 19; RATIO-SKIP 13 | – | – | 793 / 812 |
| C_E3/colouring (gadget) | Qwen3-32B direct | 270 | 269 | truncated 1 | 18/269 (7%) | 0/180 (0%) | 205/269 (76%) | 187/251 (75%) | DSATUR (C2, label ties) 130; DPLL-LIST (D, k=3) = FF-LIST (C1 seq) 100; LF (C1 static, label ties) 96 | – | – | 0 / 473 |
| C_E3/colouring (gadget) | Qwen3-14B direct | 270 | 270 | – | 0/270 (0%) | 0/180 (0%) | 163/270 (60%) | 163/270 (60%) | DPLL-LIST (D, k=3) = FF-LIST (C1 seq) 92; DSATUR (C2, label ties) 80; LF (C1 static, label ties) 53 | – | – | 0 / 472 |
| C_E3/colouring (gadget) | gpt-oss-20b thinking-low | 270 | 269 | partial 1 | 92/269 (34%) | 5/29 (17%) | 116/269 (43%) | 24/177 (14%) | DPLL-LIST (D, k=3) = FF-LIST (C1 seq) 104; DSATUR (C2, label ties) 53; ANSWER-1 (A1 default; = LOCAL-0) 46 | – | IMPOSSIBLE 150 | 220 / 307 |
| C_E5/3-SAT | Qwen3-32B direct | 15 | 15 | – | 0/15 (0%) | 0/14 (0%) | 1/15 (7%) | 1/15 (7%) | ALWAYS-UNSAT (A1 give-up) = GREEDY-MENTION-ABORT (C1) = SC-DET (C2) = UC-DET (C2) 1 | – | UNSAT 1 | 0 / 128 |
| C_E5/3-SAT | Qwen3-14B direct | 15 | 15 | – | 0/15 (0%) | 0/15 (0%) | 0/15 (0%) | 0/15 (0%) | – | – | – | 0 / 128 |
| C_E5/3-SAT | gpt-oss-20b thinking-low | 15 | 15 | – | 0/15 (0%) | 0/13 (0%) | 2/15 (13%) | 2/15 (13%) | ALWAYS-UNSAT (A1 give-up) = GREEDY-MENTION-ABORT (C1) = SC-DET (C2) = UC-DET (C2) 2; GUC-DET (C2) 1 | – | UNSAT 2 | 2,597 / 2,711 |
| C_E5/3-SAT (partial assignment given) | Qwen3-32B direct | 15 | 15 | – | 0/15 (0%) | 0/15 (0%) | 0/15 (0%) | 0/15 (0%) | – | – | – | 0 / 103 |
| C_E5/3-SAT (partial assignment given) | Qwen3-14B direct | 15 | 15 | – | 0/15 (0%) | 0/15 (0%) | 0/15 (0%) | 0/15 (0%) | – | – | – | 0 / 103 |
| C_E5/3-SAT (partial assignment given) | gpt-oss-20b thinking-low | 15 | 15 | – | 8/15 (53%) | 4/10 (40%) | 6/15 (40%) | 1/7 (14%) | ALWAYS-UNSAT (A1 give-up) = GREEDY-MENTION-ABORT from state (C1) 5; DPLL from state (D) = UC-DET from state (C2) 5; EXACT = GUC-DET from state (C2) = SC-DET from state (C2) 4 | EXACT 4 | UNSAT 5 | 2,602 / 2,678 |
| C_E5/colouring (k=3) | Qwen3-32B direct | 25 | 25 | – | 0/25 (0%) | 0/12 (0%) | 13/25 (52%) | 13/25 (52%) | ALWAYS-IMPOSSIBLE (A1 give-up) = PHANTOM-ADJACENT (B4) 13; FF-3-EDGE-MENTION-ABORT (C1 variant) 12; FF-3-LIST-ABORT (C1) 10 | – | IMPOSSIBLE 13 | 0 / 8 |
| C_E5/colouring (k=3) | Qwen3-14B direct | 25 | 25 | – | 0/25 (0%) | 0/25 (0%) | 0/25 (0%) | 0/25 (0%) | – | – | – | 0 / 171 |
| C_E5/colouring (k=3) | gpt-oss-20b thinking-low | 25 | 25 | – | 0/25 (0%) | 0/1 (0%) | 24/25 (96%) | 24/25 (96%) | ALWAYS-IMPOSSIBLE (A1 give-up) = PHANTOM-ADJACENT (B4) 24; FF-3-EDGE-MENTION-ABORT (C1 variant) 22; FF-3-LIST-ABORT (C1) 20 | – | IMPOSSIBLE 24 | 68 / 79 |
| C_E5/colouring (k=3, partial colouring given) | Qwen3-32B direct | 10 | 10 | – | 0/10 (0%) | 0/10 (0%) | 0/10 (0%) | 0/10 (0%) | – | – | – | 0 / 116 |
| C_E5/colouring (k=3, partial colouring given) | Qwen3-14B direct | 10 | 10 | – | 0/10 (0%) | 0/10 (0%) | 0/10 (0%) | 0/10 (0%) | – | – | – | 0 / 115 |
| C_E5/colouring (k=3, partial colouring given) | gpt-oss-20b thinking-low | 10 | 10 | – | 7/10 (70%) | 2/3 (67%) | 8/10 (80%) | 2/3 (67%) | ALWAYS-IMPOSSIBLE (A1 give-up) = FF-3-LIST from state (C1, ABORT) 7; DPLL-LIST from state (D) = DSATUR-3 from state (C2) 6; EXACT 5 | EXACT 2 | IMPOSSIBLE 7 | 737 / 748 |
| C_E5/propositional entailment | Qwen3-32B direct | 20 | 20 | – | 11/20 (55%) | – | 20/20 (100%) | 9/9 (100%) | ETR-1p (R1) = ETR-default (R1) 15; GREEDY-CM (not-C first) (C1) 15; GREEDY-CM-MENTION (C1) 14 | – | – | 0 / 5 |
| C_E5/propositional entailment | Qwen3-14B direct | 20 | 20 | – | 18/20 (90%) | – | 20/20 (100%) | 2/2 (100%) | FIRST (B4) 18; NONE (A1 give-up: does not follow) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound) 18; MM-S1 (B4) 17 | – | – | 0 / 2 |
| C_E5/propositional entailment | gpt-oss-20b thinking-low | 20 | 20 | – | 20/20 (100%) | – | 20/20 (100%) | – | NONE (A1 give-up: does not follow) = TRUTH TABLE (exact) = UP-fixpoint (B1, sound) 20; FIRST (B4) 18; MM-S1 (B4) 17 | – | – | 160 / 170 |
<!-- END prelim:desc_dev -->

## 7. Caveats

**About the data.**

- **Dev split, not the pre-registered test split.** The items come from dev seeds, and the pc20 sets were chosen as the sizes the recovery sweep validated. Nothing here was pre-registered: not the units, not the statistics, not the thresholds.
- **One sample per item.** There are no repeats, so run-to-run variance is not measured (DESIGN §5 rule 8). On the items the pilot and dev sets share, each pilot run reused the dev run's responses from the cache (§1).
- **Two cheap conditions, two different models.** Qwen3-32B answered with thinking off. gpt-oss-20b thought at low effort: median reasoning tokens per item of 830–2,140 on the fitted units (§6), against the 32k budget of the primary condition. Model and condition change together, so no difference between the two runs can be put down to the model or to thinking. There is no cross-model fit (DESIGN §3 O3).
- **Qwen3 is served at fp8.** OpenRouter serves Qwen3-32B and Qwen3-14B only at fp8 (DeepInfra flex; RUNNER.md, provider pins). gpt-oss-20b is served at bf16, which holds its released weights exactly.
- **The direct condition's instruction conflicts with the prompts.** The system message says to answer without working, while the prompts say "Think as carefully as you need". The conflict is part of the condition (RUNNER.md, Open questions). Qwen3-32B's pilot responses show no visible working: `pre_answer_tokens` is at most 4. In the dev runs, 8 Qwen3-32B and 10 Qwen3-14B direct responses have more than 20 tokens of visible text before the answer (§1).
- **Truncation is censored, and excluded.** Truncated responses carry no answer and are kept out of the fits. None of the fitted units' responses was truncated; the other rates are in §5 and §6.
- **C SAT `members_matched` predates the give-up member** (§6). This affects only the descriptive tables.

**About the fits.**

- **The gates pass only for these three units at this size, and only just on A/H E5 SAT.** Its 60/30/10 mixture's percentile coverage is 0.90, exactly at the gate (BCa: 0.88). C E2 knapsack's null-q intervals under-cover at the boundary (π₀ near 1). An interval that touches 0, like gpt-oss-20b's π₀ on knapsack, sits on the other boundary, where coverage was not checked.
- **The gates were checked at one operating point**, which the real fits do not share: a planted triple of other members, with slips at ε = 0.1. §3.5 re-checks each fit at its own estimate.
- **The slip rate sits at its cap in five of the six fits** (ε = 0.5, `EPS_MAX`), and ρ sits at its grid's edge (0.9) in three of them. The near-miss model wants more slip mass than the engine allows. Those fits do not reproduce the share of answers that equal a member's answer (§3.5).
- **A weight is not a count of exact matches.** π_h includes h's near misses, up to 6 positions away. Where no answer equals any member's (Qwen3-32B on colouring, both runs on A/H E5 SAT), every weight on a member is near misses.
- **No structure-matched chance level on C E2 colouring** (§4). The q-based level is not a fair bar.
- **Multiple comparisons.** p-values are per member and statistic, uncorrected (§4).
- **Selection.** C E2 items are built so that members disagree. The weights describe these items, not instances at large (RECOVERY.md, Limitations).
- **Off-zoo strategies.** A small π₀ does not show that the zoo is complete: in recovery, a withheld procedure's weight went mostly onto zoo members (RECOVERY.md, Off-zoo).

## 8. What this does and does not show

Every statement below is about these dev-split items, one sample each, in two cheap conditions. Each comes with the chance level it was compared against.

**What the data show.**

1. **gpt-oss-20b at low effort solves about half the C E2 knapsack items, and its errors coincide with greedy rules' errors far more often than chance.**
   - 158 of 300 answers are optimal. EXACT's weight is 0.616 [0.535, 0.688] (BCa [0.540, 0.692]), against a permutation chance level of 0.039.
   - Of the 142 wrong answers, 57 equal a greedy member's answer exactly.
   - Per member, where both are wrong, gpt-oss-20b gives RATIO-SKIP's answer on 29 of 112 items (0.26), DIFF's on 27 of 125 (0.22) and VALUE's on 19 of 101 (0.19). The within-cell permutation chance for each is 0.005–0.008 (p = 0.0005 each).
   - This is the one fit whose model reproduces the data (§3.5). At its estimate, fake data are recovered with |bias| ≤ 0.007 and coverage 0.89–0.96.
2. **gpt-oss-20b reproduces one colouring heuristic's wrong answers, and essentially no other's.** Where both are wrong, it gives listing-order first fit's (FF-LIST's) colouring on 40 of 232 C E2 items. For each other deterministic greedy member (FF-LABEL, LF, DSATUR, DSATUR-LABEL), the count is 0–2 out of 86–216.
   - This unit has no structure-matched chance level (§4). The comparison is between members, which are all exact 16-vertex colourings.
3. **Qwen3-32B with thinking off reproduces greedy knapsack answers above chance, but rarely.**
   - Where both are wrong, it gives the ratio-greedy prefix's answer on 15 of 266 items (0.056), DIFF's on 11 of 256 and RATIO-SKIP's on 9 of 228. The permutation chance for each is 0.004–0.005 (p = 0.0005 each).
   - That is 23 of its 299 wrong answers. Most of the rest are one or two items from a member's answer: near misses, which the fit cannot describe well (§3.5).
4. **On A/H E5 SAT we found no zoo member that accounts for the answers.** Neither model satisfied the stated rule on any item, and no answer equals any member's assignment.
   - Qwen3-32B's unexplained mass (0.942) equals its permutation chance level (0.945): its answers are no nearer the members' answers for their own items than shuffled answers are.
   - gpt-oss-20b's (0.869) is below its chance level (0.984). Its assignments are slightly nearer to POLARITY's and to the solutions than shuffled ones: weights of 0.05, against chance levels of 0.002–0.006 (p = 0.002 and 0.005).

**What the data do not show.**

- **Which procedure either model runs.** These are agreements between answers. Identification also needs manipulation signatures, traces or process measures (DESIGN §3 O3), and none were analysed here.
- **Weights that are rates of heuristic use, in five of the six fits.** In those fits the slip rate sits at its cap, and the fitted model fails to reproduce the data (§3.5). Their weights say whose answers the model's answers are near.
- **Anything about thinking at best effort,** the primary condition. Both conditions here are cheap arms.
- **Any difference between the models.** Model and condition change together, and there is no cross-model fit or paired test (DESIGN §5 rule 7).
- **That the zoo is complete.** gpt-oss-20b's π₀ of 0 on knapsack does not show it: in recovery, an off-zoo procedure's weight went mostly onto zoo members (RECOVERY.md, Off-zoo).
- **Anything about the units that were not fitted.** Their match counts (§6) are counts, not weights.
- **Anything about the test split or other item sizes.**

## Audit

A hostile-reviewer pass before the PR. Earlier syntheses in this lab drifted towards overstatement, so this one was audited like a result. The checks below were run by separate code, in a scratch directory, not by `analysis/prelim_2026_11_18.py`.

**Numbers re-derived independently of the script.**

1. **The knapsack and A/H E5 SAT fits.** A second implementation shares no code with `reasoning_heuristics.identify` or the scorer:
   - it reads the item JSON and the scored answers itself;
   - it rebuilds EXACT and TT[exact] by brute force (optimal subsets; satisfying assignments under the stated and the textbook rule);
   - it writes the near-miss likelihood from its definition;
   - it maximises with its own EM over the same ρ grid, profiling ρ.

   **Result:** in three of the four fits, every weight agrees with the engine's within 0.003. In two of those, ε, ρ and the log-likelihood match too. In the third, gpt-oss-20b on SAT, the independent fit takes ρ = 0.68 against the engine's 0.70, for a log-likelihood 0.006 higher. The fourth is Qwen3-32B on knapsack:
   - the independent π₀ is 0.088, against the engine's 0.102, and the other weights move by up to 0.009;
   - the independent fit's log-likelihood is 0.09 higher, at ρ = 0.54 rather than 0.52;
   - so the engine's EM stops slightly short of the optimum along a flat direction (π₀ against the ratio-greedy group and VALUE), well inside π₀'s interval [0.000, 0.213].
2. **The colouring likelihood.** The partition kernel was rewritten from its definition: a sum over injective namings of the answer's blocks. On 60 random gpt-oss-20b rows (526 row–member pairs, EXACT included where it has at most 60 solutions), it matches the engine's coefficients to within 2 × 10⁻¹⁶ relative, and q exactly. An independent EM on the engine's rows then reproduces both colouring fits: every weight to four decimals, and the log-likelihoods exactly.
3. **Correct answers, exact matches, EA and co-error.** These were recounted from the instances for all six fits, with optimality, propriety and satisfiability judged by fresh code and answers compared as canonical forms. Every count in §4 and §6 matches: for example, RATIO-SKIP's 29 of 112 and FF-LIST's 40 of 232.
4. **A/H E5 SAT has 0 correct answers.** Clause evaluation was rewritten, with inverted and starred clauses flipped. 0 of 92 (Qwen3-32B) and 0 of 71 (gpt-oss-20b) assignments satisfy the stated rule, and every item is satisfiable, so the 3 and 26 UNSAT answers are wrong too. This agrees with the scorer's `valid` on every answer.

**Claims verified on the items.**

5. **Item drift (#22).** The pre-#22 pc20 files were taken from git (62d8345), and their sha256 equals the runs' manifests. Compared with the current files:
   - all 420 colouring and 300 knapsack records are identical as JSON objects;
   - the 320 SAT records differ only by the added ALWAYS-UNSAT member, with its hypotheses, traces, `disconfirms` column and channel spec;
   - no prediction was removed or changed, and ids, prompts and hashes are unchanged.
6. **The recovery numbers in §2 were measured on these items.** Main's `data/recovery/pc20.json` (#24) read an A/H E5 file with the same sha256 as main's, decompressed. Its C E2 file is the pre-#22 one, whose colouring and knapsack records are identical to main's (check 5).
7. **No member of a fitted unit predicts a special token.** Every member's prediction on every item was enumerated: none is UNSAT, IMPOSSIBLE or X, and no stored distribution has mass on one. The script repeats this check (`special_tokens` in the JSON).
8. **The merge of #24 changed nothing here.** A run on the engine before the merge and the final run give identical point estimates, slip parameters and log-likelihoods for all six fits.
9. **The numbers reproduce.** A second full run, on a clean tree at the committed code, reproduced the first run's JSON exactly, apart from its provenance fields.

**Claims checked against their tables.** Every number in the prose was compared with the generated table it comes from, or with the JSON. The bottom line was compared with §3–§6, and each item in §8 with its table. That pass changed these drafts:

- **Removed:**
  - reading Qwen3-32B's 0.405 on EXACT (colouring) as a rate of solving: it gives no optimal colouring, so the weight is near misses;
  - reading RO-FF's weight as one random vertex order: its support is first fit under any order;
  - "the ratio-greedy prefix is the nearest member most often" (Qwen3-32B knapsack): true in exploration, but the script does not compute it;
  - a count of all-false assignments on A/H E5 SAT, for the same reason;
  - "the EXACT group is tied with most members" on B4/C4: the tables do not show it.
- **Corrected:**
  - gpt-oss-20b's unexplained mass on A/H E5 SAT is below its permutation chance level (0.869 against 0.984), not "about what shuffled answers get", as a draft of the bottom line said; that held only for Qwen3-32B;
  - gpt-oss-20b on knapsack is the only fit that reproduces all three predictive statistics, not the only one that reproduces the exact-match share: Qwen3-32B's A/H E5 SAT fit matches that one too;
  - prose weights are quoted to three decimals, as in the tables, because two-decimal roundings of values such as 0.275 and 0.085 are ambiguous;
  - q's chance of giving a member's exact colouring is up to 3 × 10⁻¹³, not the 3 × 10⁻¹⁵ a draft estimated by hand. The JSON's 6-decimal rounding had stored it as 0, so the script now records its log10;
  - truncation hit three units, not two;
  - 2 of 420 pilot Qwen3 colourings are valid, not 1;
  - gpt-oss-20b's median reasoning tokens on the fitted units, now quoted from §6;
  - the reasons C E1 SAT and C E2 SAT are not fitted, updated to RECOVERY.md after #24 (null ALWAYS now passes there, and null q fails);
  - gate verdicts, which an earlier draft took from the recovery branch, are now cited from RECOVERY.md on main.
- **Reworded:**
  - "there is no member that explains A/H E5 SAT" became "we found no zoo member that accounts for the answers", with the permutation chance level beside it;
  - "fitted" weights are described as "whose answers the model's answers are near" wherever the slip rate is at its cap.
