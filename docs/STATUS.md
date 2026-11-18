# Status

*Current state of the work as of 2026-11-17. Update this file when a stage finishes or a decision is made.*

## Summary

The design work and the first stage of question generators are finished. No model has been run yet: **$0 of inference is spent.**

- We have:
  - a literature review;
  - a design document;
  - eval designs for seven verticals with 649 hand-built example questions;
  - theoretical priors for every heuristic family;
  - a paper outline with stand-in values;
  - a scope and budget plan for real results at about $95.
- The Stage 1 generators produce 1,330 dev items across ten evals, and all of them pass automatic validation.
- Those items now need a human pass on the [review page](https://claude.ai/artifact/AEidKBQZisLzHB8BudFtb1). After that comes the runner, the identification engine, and the first dev runs on gpt-oss-20b.

## Where each part stands

| Part | State | Where |
|---|---|---|
| Literature review | Done: six reports and a synthesis | [LITERATURE.md](LITERATURE.md), [literature/](literature/) |
| Design document | Draft v0.2 (2026-11-13). Partly superseded by the scope, theory and skeleton documents, which win where they disagree | [DESIGN.md](DESIGN.md) |
| Heuristic zoo | 9 families, about 57 named heuristics, two nuisance models (slips and misreading) | [PAPER_SKELETON.md](PAPER_SKELETON.md) §5, [verticals/](verticals/) |
| Eval designs | 7 verticals, about 50 evals (8 of them in the cross-formalism vertical). Each eval names the heuristic it supports, the competitors it disconfirms, and hypotheses about the answer, the aggregate result and the chain of thought | [verticals/](verticals/) |
| Example questions | 649 hand-checked items, every prediction computed by code | [data/examples/](../data/examples/) |
| Theoretical priors | Done. Three lenses (what transformers can compute, what RASP-L simplicity predicts they learn, what LLMs already do), with a verdict per family in direct and thinking mode | [theory/README.md](theory/README.md) |
| Paper outline | Stand-in values, with theory priors filled in. Freeze the priors before the first run | [PAPER_SKELETON.md](PAPER_SKELETON.md) |
| Scope and budget | About $15–20 for preliminary results and about $95 for real results (gpt-oss-20b and 120b) | [SCOPE.md](SCOPE.md) |
| Shared engineering: item schema, domain library, heuristic zoo code, counterfactual tooling, validators | Built and tested (246 tests) | `src/reasoning_heuristics/`, [GENERATORS.md](GENERATORS.md) |
| Stage 1 generators | Built: A/H E1, E2, E5, E8; C E1, E2, E3, E5; B4/C4 E1, E2. Output is 266 smoke and 1,330 dev items, all passing validation, with no dev-to-test leakage. A few lower-priority cells aren't built (listed in GENERATORS.md) | `src/reasoning_heuristics/generators/`, `data/items/` |
| Manual review of items | Page is live, no marks yet | [Review page](https://claude.ai/artifact/AEidKBQZisLzHB8BudFtb1), `scripts/review_page/` |
| Runner (OpenRouter client, cache, cost guard, manifests) and scorer | Built and tested with the HTTP layer mocked: thin custom runner, thinking and direct conditions, one versioned scorer. No batch endpoint yet; E8 continuations not built | [RUNNER.md](RUNNER.md), `src/reasoning_heuristics/evals/` |
| Identification engine (mixture fit with a slip model) | Not started | SCOPE §4 item 4 |
| Recovery harness (fake models with planted mixtures) | Not started. The C and cross-formalism designs ran their own recovery simulations | SCOPE §4 item 5, `scripts/cross_formalism/recovery_sim.py` |
| Trace pipeline (codebook, parsers, LLM coder, faithfulness probes) | Not started. The E8 specs for faithfulness probes exist | SCOPE §4 item 6 |
| Stage 2 generators (B1/G, D/F, E, cross-formalism) | Not started. The cross-formalism vertical has a working library builder | SCOPE §5, `scripts/cross_formalism/` |
| Model runs | None | |
| Phase 2 (mechanistic interpretability) | Gated on behavioural evidence | SCOPE §8 |

## What we've learned so far, before any data

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

1. **Review the items.** Mark the 50 items on the review page keep, fix or drop. The marks become generator changes, not edits to single items.
2. **Build the runner.** First decide between a thin custom runner and Inspect AI (DESIGN §9 question 5).
3. **Build the identification engine and recovery harness.** Pass the recovery gates on fake models (free): |bias| ≤ 0.05, 95% coverage ≥ 0.9, median interval width ≤ 0.2.
4. **First runs on gpt-oss-20b.** Smoke, then dev (about $8 per pass over all verticals). Then calibrate sizes so the hardest cell scores 40–80%, and freeze.
5. **Pilot and power analysis**, then the Stage 2 generators (SCOPE §5).

## Open decisions

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
