# Status

*Current state of the work as of 2026-11-18 (morning). Update this file when a stage finishes or a decision is made.*

## Summary

The design work, the first stage of generators, the identification engine and the first model runs are done. **Preliminary results are in: [results page](results/2026-11-18-results.html)** (dev split, one sample per item, not pre-registered). About $24 of the $40 budget for 2026-11-17/18 is spent.

- We have:
  - a literature review;
  - a design document;
  - eval designs for seven verticals with 649 hand-built example questions;
  - theoretical priors for every heuristic family;
  - a paper outline with stand-in values;
  - a scope and budget plan for real results at about $95.
- The Stage 1 item sets were regenerated after the review fixes (#16): 266 smoke and 1,330 dev items across ten evals. All of them pass automatic validation, with no leakage and no hash collisions. CI checks that the committed sets reproduce.
- **A project review on 2026-11-17 found real defects** ([reviews/2026-11-17-project-review.md](reviews/2026-11-17-project-review.md)). Ground truth was right on every item. But several zoo members collapsed into trivial ones, the per-item likelihood tables credited the exact solver with invalid answers, item identity had gaps, and B4/C4 E1 didn't reproduce. The fixes have merged (#7, #12, #13, #14), and every item set was regenerated with them (#16). What is still open is listed in the review, under [Open after the fixes](reviews/2026-11-17-project-review.md#open-after-the-fixes).
- **Don't mark the review page yet.** It still shows the pre-fix items, so it is stale until it is rebuilt from the regenerated sets. It also needs a home other than claude.ai.
- The runner and scorer are built (#8; scorer-1.5.1 since #32). The identification engine and the recovery harness are built (#17, #24, #27): mixture weights are reported only where fake-model recovery passes, which on the regenerated items means a few units at 20 or 40 items per cell ([RECOVERY.md](RECOVERY.md)).
- Runs (#18–#31, #34): dev items (5 per cell) for every model and condition, and pilot items (20 and 40 per cell, `data/items/pc20`, `pc40`) on the gated units, for Qwen3-14B and Qwen3-32B (thinking off, and thinking at high effort) and gpt-oss-20b and gpt-oss-120b (low effort; dev also at high effort). gpt-oss-20b at high effort on dev came in last (#34): 462 of its 1,270 responses hit the token cap.

## Where each part stands

| Part | State | Where |
|---|---|---|
| Literature review | Done: six reports and a synthesis | [LITERATURE.md](LITERATURE.md), [literature/](literature/) |
| Design document | Draft v0.2 (2026-11-13). Partly superseded by the scope, theory and skeleton documents, which win where they disagree | [DESIGN.md](DESIGN.md) |
| Heuristic zoo | 9 families, about 57 named heuristics, two nuisance models (slips and misreading) | [PAPER_SKELETON.md](PAPER_SKELETON.md) §5, [verticals/](verticals/) |
| Eval designs | 7 verticals, about 50 evals (8 of them in the cross-formalism vertical). Each eval names the heuristic it supports, the competitors it disconfirms, and hypotheses about the answer, the aggregate result and the chain of thought | [verticals/](verticals/) |
| Example questions | 649 hand-checked items, every prediction computed by code | [data/examples/](../data/examples/) |
| Theoretical priors | Done. Three lenses (what transformers can compute, what RASP-L simplicity predicts they learn, what LLMs already do), with a verdict per family in direct and thinking mode. Corrected on 2026-11-17 after a reproducibility audit, before any model output was analysed (no verdict changed; see the corrections log). **Frozen at git tag `priors-frozen-2026-11-17`** | [theory/README.md](theory/README.md) |
| Paper outline | Stand-in values, with theory priors filled in. Priors frozen (tag `priors-frozen-2026-11-17`) | [PAPER_SKELETON.md](PAPER_SKELETON.md) |
| Scope and budget | About $15–20 for preliminary results and about $95 for real results (gpt-oss-20b and 120b) | [SCOPE.md](SCOPE.md) |
| Shared engineering: item schema, domain library, heuristic zoo code, counterfactual tooling, validators | Built and tested. The 2026-11-17 review found defects in the zoo, the validators and the likelihood tables, fixed in #12 (validators), #13 (generators and tables) and #14 (zoo). CI runs the tests on every PR (#3) | `src/reasoning_heuristics/`, [GENERATORS.md](GENERATORS.md), [review](reviews/2026-11-17-project-review.md) |
| Stage 1 generators | Built: A/H E1, E2, E5, E8; C E1, E2, E3, E5; B4/C4 E1, E2. **Regenerated after the review fixes (#16):** 266 smoke and 1,330 dev items (3.3 MB of `.jsonl.gz`), all passing validation, every designed cell filled, no dev-to-test leakage, no hash collisions. The sets reproduce byte for byte (checked under four hash seeds), and CI's `reproduce-items` job checks that on every PR. A few lower-priority cells aren't built (listed in GENERATORS.md) | `src/reasoning_heuristics/generators/`, `data/items/`, [review/summary.md](../review/summary.md) |
| Manual review of items | Page is live, no marks yet. **Stale:** it shows the pre-fix items. Rebuild it from the regenerated sets, and give it a home other than claude.ai, before marking | [Review page](https://claude.ai/artifact/AEidKBQZisLzHB8BudFtb1), `scripts/review_page/` |
| Runner (OpenRouter client, cache, cost guard, manifests) and scorer | Built and tested with the HTTP layer mocked: thin custom runner, thinking and direct conditions, one versioned scorer. No batch endpoint yet; E8 continuations not built | [RUNNER.md](RUNNER.md), `src/reasoning_heuristics/evals/` |
| Identification engine (mixture fit with a slip model) | Built: cluster bootstrap with percentile and BCa intervals, permutation baselines, error agreement (#17, #24) | `src/reasoning_heuristics/identify/` |
| Recovery harness (fake models with planted mixtures) | Built and run on every unit at 5, 10, 20 and 40 items per cell (#24, #27). The gates pass, with both nulls, only on C E2 colouring and A/H E5 SAT at 20 and 40, and on A/H E5 colouring and C E5 SAT with a given state at 40; knapsack's mixture passes at 20 and 40 | [RECOVERY.md](RECOVERY.md) |
| Trace pipeline (codebook, parsers, LLM coder, faithfulness probes) | Not started. The E8 specs for faithfulness probes exist | SCOPE §4 item 6 |
| Stage 2 generators (B1/G, D/F, E, cross-formalism) | Not started. The cross-formalism vertical has a working library builder | SCOPE §5, `scripts/cross_formalism/` |
| Model runs | Smoke, dev and pilot runs done for gpt-oss-20b, gpt-oss-120b, Qwen3-14B and Qwen3-32B (#15, #18–#31, #34); every run scored with scorer-1.5.1 (#32, #34). About $24 spent | `data/runs/`, `data/runs/LEDGER.md` |
| Analysis and results page | Fits, predictive checks (including a distance-profile check), error agreement against permutation chance, descriptive counts, and a self-contained HTML page with hand-written claims | `analysis/prelim_2026_11_18.py`, `analysis/results_page.py`, [results page](results/2026-11-18-results.html), [findings](results/findings.html) |
| Phase 2 (mechanistic interpretability) | Gated on behavioural evidence | SCOPE §8 |

## What the first data say (2026-11-18, preliminary)

The [results page](results/2026-11-18-results.html) has the numbers, intervals, chance levels and strength labels. In brief:

- **Some errors carry greedy signatures.** On colouring, a wrong colouring that equals any member's is usually first fit in the listed vertex order (40–99 per run, against about 1 from a random-order first fit). On knapsack, gpt-oss's wrong packings often equal a greedy rule's, but mostly because they are near-optimal; the part specific to greedy is modest.
- **The thinking condition matters most.** Qwen3 is correct far more often in the thinking condition than in the direct one, which also differs in token cap, system prompt and sampling, and its wrong colourings are often listing-order first fit's. That fits the priors' "truncated exact search, seeded by greedy", though answers alone cannot show the search.
- **The mixture model rarely fits.** Of 24 fits, 14 have the slip rate at its cap, and only 4, all near ceiling, pass every predictive check (6 without a check added after seeing the data). The near-miss noise model is the weak link (see Open decisions).
- **Effort removes the errors in gpt-oss.** At high effort gpt-oss gets nearly everything it finishes right. Paired by item on dev, of the 542 items gpt-oss-20b got wrong at low effort, 190 become correct, 347 run out of tokens and 4 stay wrong. That includes the 3-colourable graphs it called impossible. The two runs differ only in the effort setting.
- **False impossibility.** gpt-oss and Qwen3 in the thinking condition often call 3-colourable graphs impossible (C E5), and gpt-oss-20b at low effort often calls satisfiable formulas UNSAT. The give-ups are as common on control items, where list-order greedy succeeds, as on the items where it gets stuck.
- **Textbook transfer.** Under a redefined connective (A/H E5 entailment), gpt-oss-120b at low effort mostly answers the textbook problem; a reworded restatement just before the question fixes most of it (retention or clearer wording; not yet separated).

## What we learned before any data

- **Thinking and direct answering should use different heuristics.**
  - Direct answers favour short, shallow programs: defaults, the density cue, a few rounds of unit propagation, one-shot scoring.
  - Thinking favours truncated exact search, seeded by greedy.
  - [theory/README.md](theory/README.md) §2.
- **In thinking mode the families combine into one procedure.** The zoo needs composite members such as `SEARCH(b, order, value, default)`; one is already in the code.
- **Compute only forces heuristics on large SAT.**
  - Exact search fits a 32k-token budget for our colouring and entailment sizes.
  - So errors there are shortcuts the model chose, or noise, rather than heuristics forced by the budget.
  - Misreading and slips may outweigh every heuristic family, which is why they are first-class rows.
- **Restriction (ETR and mental models) is the most informative contested family.**
  - Simplicity doesn't favour it.
  - So any weight it carries comes from training data.
  - The joint predictions for that are in theory/README.md §2, point 3.
- **The formalism only shows up where heuristics fail.**
  - Listing-order heuristics return the same answer in every formalism whenever they succeed.
  - So the cross-formalism evals depend on dead-end items and traces.
  - [verticals/I_cross_formalism.md](verticals/I_cross_formalism.md).
- **Compute everything.** Hand reasoning was wrong several times during design, so every ground truth and prediction comes from code and is checked by an independent solver.

## Next steps

1. ~~Land the review fixes, then regenerate every item set and add a CI check that the committed sets reproduce.~~ Done: the fixes in #7, #12, #13 and #14; the regeneration and the CI check in #16.
2. **Review the items.** Rebuild the review page from the regenerated items, then mark the 50 items keep, fix or drop. The marks become generator changes, not edits to single items.
3. ~~Build the runner.~~ Done (#8): a thin custom OpenRouter runner, as SCOPE §4 specifies, with thinking and direct conditions and one versioned scorer.
4. ~~Build the identification engine and recovery harness.~~ Done (#17, #24, #27); see RECOVERY.md for where the gates pass.
5. ~~First runs.~~ Done: smoke, dev and pilot runs (#15, #18–#31, #34), with preliminary results (#28, #29 and the results page). Still to do: calibrate sizes so the hardest cell scores 40–80%, and freeze. Decide the noise model first (Open decisions).
6. **Pilot and power analysis**, then the Stage 2 generators (SCOPE §5).

## Open decisions

- **Decided 2026-11-17:**
  - Phase 1 stays mostly on thinking models, with a cheap direct-answer (thinking off) arm on every eval ([decision](decisions/2026-11-17-direct-answer-arm.md)).
  - The runner is a thin custom one (DESIGN §9 question 5).
  - Agents open and merge PRs regularly ([RULES.md](../RULES.md)).
- **From the 2026-11-18 results:**
  - **The noise model.** Most fits put the slip rate at its cap: answers miss the members in ways the near-miss model with a uniform q cannot produce (on knapsack, more two-item swaps than one-item slips; with thinking, more exact matches and fewer far answers than predicted). The options are a validity-aware q, a richer error model, or per-member ε. Each departs from SCOPE §6 rule 3.
  - **Boundary-aware intervals.** Percentile and BCa intervals under-cover at the edge of the simplex (π₀ = 1 on knapsack); about a day's work.
  - **gpt-oss's 32k-token cap** truncates 22% of gpt-oss-120b's and 36% of gpt-oss-20b's high-effort dev responses, and over 90% on some units: A/H E2 SAT for both, and C E2 knapsack for gpt-oss-20b. On C E3's uninstructed colouring gadgets (COL-U), where the design expected about 10%, they truncate 143 and 174 of 180. Raise it, or calibrate item sizes to it. This decides whether high effort has any heuristics to find: the answers it finishes are nearly all right, so its hard items show up only as truncations.
  - **Repeat samples.** Every count is one sample per item; DESIGN §5 rule 8 asks for repeats.
  - **Where the results page lives** (it is a repo file for now).
- **From the 2026-11-17 review** (its "Design questions" section):
  - selection filters that depend on one member's behaviour vs SCOPE §6 rule 6;
  - where the rebuilt review page lives;
  - `MM-S1` vs mSentential, and the CW-MIN reading.

- **Theory-driven design changes** ([theory/README.md](theory/README.md) §5): composite members, SAT sizes centred on each model's budget line, depth up to 12–16, prompt given twice, adjacency vs shuffled edge lists. The generators support all of them as options. Whether they become defaults is undecided.
- **Scope decisions** ([SCOPE.md](SCOPE.md) §9):
  - recommended vs lean full-study plan (can wait for the pilot);
  - Stage 1 verticals as proposed;
  - the Phase 2 gate threshold;
  - who hand-labels traces.
- **Design questions** ([DESIGN.md](DESIGN.md) §9):
  - pilot domains;
  - showcase for interpretability;
  - which length measure H2 is judged on;
  - whether the v1 co-authors join;
  - runner choice.
- **DESIGN.md is out of date.** It should be revised to match SCOPE, the theory notes and the paper outline, or marked as historical.

## Running what exists

```
pip install -e '.[dev]'                            # into a virtualenv; pulls python-sat and PyETR 1.0.0
python -m reasoning_heuristics.generate --vertical C --eval E1 --tier dev --seed 1
python -m reasoning_heuristics.review              # all smoke and dev sets, packets, summary
python scripts/review_page/build_review.py out.html
pytest -q
```

API keys go in `keys.env`, which is gitignored. The runner reads `OPENROUTER_API_KEY` from the environment; see [RUNNER.md](RUNNER.md).
