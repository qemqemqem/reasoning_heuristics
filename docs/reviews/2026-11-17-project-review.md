# Project review, 2026-11-17

Three code reviewers, one theory auditor and I reviewed the repo as of `2119433` (Stage 1 generators merged). The reviewers were read-only and independent. Each reported a finding as **confirmed** (reproduced by running code) or **suspected**. I re-checked three headline findings myself: the C E3 hash collisions, the dropped `RANDOM (H)` rows and the MC letters. All three reproduce.

This file is the tracking list: the status column is updated as fix PRs merge.

## Where the project stands

- **Built:** the planning docs and the Stage 1 generators. That is 10 evals, with 266 smoke and 1,330 dev items. The 246 tests pass, and CI now runs them (#3).
- **Not built until today:** the Stage 0 shared infrastructure that SCOPE §5 puts *before* Stage 1. That covers the runner, the identification engine, the recovery harness and the trace pipeline. No model has been called and the recovery gate has never run. The runner and the identification engine with its recovery harness are now in progress.
- **Ground truth is right.** A reviewer recomputed every ground-truth key on all 1,596 items with independent code: zero mismatches.
- **Much of what sits around the ground truth is not.** Three kinds of problem:
  - the item identity checks (hashes, lineage, leakage);
  - several zoo members, which collapse into trivial members or break their spec;
  - the per-item likelihood tables, which credit the exact solver with invalid answers.

  On top of these, one eval does not reproduce.
- **Theory notes:** every committed number reproduces, but the frontier only with `--n 600`. Two program bugs and several overstated claims need correcting before any data is analysed.

## Findings

Severity: **H** changes what an item tests or how an answer counts; **M** is a wrong check or a reproducibility problem; **L** is minor or latent.

### Item identity, validators and solvers (fix PR: `fix-validators`; C E3 hash: `fix-generators`)

| # | Sev | Finding | Status |
|---|---|---|---|
| V1 | H | C E3 I-arm: `ColouringTask.content_key` drops the listing order and the target vertex, so items with different answers share a `content_hash` (36 groups, all 108 I-arm items). The target is not in `instance`. | confirmed (re-checked) · open |
| V2 | M | The C E3 asked answer is never checked independently; the set check compares FF with itself. All 108 are correct when recomputed. | confirmed · open |
| V3 | M | `discriminates` compares raw answers, not the scoring channel: 72 items pass with all-zero LR tables (A/H E5 KNAP I/I+R, C E3). | confirmed · open |
| V4 | M | Leakage check: knapsack and TSP get no structural check; only the first instance per base is compared; `complement` is ignored; duplicate clauses defeat the CNF check. | confirmed · open |
| V5 | L | The SAT menu renderer says "three conditions" for mixed-width clauses (4 A/H E1 B1 items). | confirmed · open |
| V6 | L | Latent solver edge cases: fixed colours outside 1..k accepted; χ of the empty graph differs between paths; TSP n=1 crashes; inconsistent premises stored as `follows=False` against the prompt's vacuous-truth definition. None occurs in the data. | confirmed · open |
| V7 | M | The "independent" validator path shares the effective-instance transforms, the task loader and Minisat with the generator path; likelihood readouts are not rechecked; the prediction and hash checks only catch nondeterminism. | design · open |
| V8 | M | Lineage: 520–624 items have a `source_hash` that matches no item (6 of 10 evals); nothing validates lineage. | confirmed · open |
| V9 | L | Hash collisions are claimed checked but aren't; the seed check ignores tier sub-ranges; `rng_for` truncates salts to 8 bytes (safe today). | confirmed · open |

### Heuristic zoo (fix PR: `fix-zoo`)

| # | Sev | Finding | Status |
|---|---|---|---|
| Z1 | H | Colouring `SEARCH`: every placement costs budget and there's no forward checking, so n > b can never succeed. A/H "D DPLL-b" (b=20) answers IMPOSSIBLE on all 72 A/H E1/E2 colouring items, the same as ALWAYS-IMPOSSIBLE. | confirmed · open |
| Z2 | H | UC/GUC/SC never check the final assignment and return clause-violating assignments instead of UNSAT (4 committed items; one false dissociation in C E2). | confirmed · open |
| Z3 | H | SAT `SEARCH` keeps branching after every clause is satisfied; its budget counts decisions only; unused padding variables raise the minimum b by their number. On A/H E2, DPLL-b ≡ ALWAYS-UNSAT today. | confirmed · open |
| Z4 | H | `GREEDY+REPAIR` (k mode) oscillates, so its answer depends on the parity of max_steps (14 of 35 C E5 dev items). | confirmed · open |
| Z5 | M | RO-FF/RO-GREEDY keep the top 25 of 1–2k samples with no smoothing (spec: 10⁴ runs, add-ε). Up to 2.2% of the mass goes to "other". | confirmed · open |
| Z6 | M | ETR's MC output text depends on PYTHONHASHSEED, so **B4/C4 E1 doesn't reproduce**, and 24–48 committed items fail revalidation in a fresh process. The answers are stable. | confirmed · open |
| Z7 | M | SAT `UP-k` gets a free falsified-clause check after the last round, one round stronger than the B1 pseudocode (1 A/H E1 item). | confirmed · open |
| Z8 | M | `WALK` is not WalkSAT/SKC (no zero-break move; scores flips by total unsatisfied clauses, not break count). | confirmed · open |
| Z9 | M | `MATCH-A` is order-dependent; the spec says order-invariant (2 of 20 A/H E1 predictions). | confirmed · open |
| Z10 | M | `MM-S1`: only categorical premises eliminate implicit models ("A; A→B; B→C ⊢ C" gives NO). This needs comparing against the B4/C4 definition and mSentential. | behaviour confirmed, deviation suspected · open |
| Z11 | L | The MOMS tie-break; a GREEDY+REPAIR hang (not triggered by any item); `sat_edits` drops `inverted_clauses`; weak `assert_isomorphic_copy`; PERCEPTION-NOISE never flips signs; a tokens.py docstring. | confirmed · open |

### Generators and likelihood tables (fix PR: `fix-generators`)

| # | Sev | Finding | Status |
|---|---|---|---|
| G1 | H | Set-valued members get no outcome classes, so their unlisted valid solutions share "other" with every invalid answer. On 181 of 325 C E1/E2/E5 witness items, an invalid answer counts as evidence *for* EXACT. A/H E5 KNAP I/I+R tables are all zeros. | confirmed · open |
| G2 | H | Members are silently dropped from tables: `RANDOM (H)` from all 140 C colouring items (label mismatch; re-checked); FF-OUT, LF and EXACT on C E3 (string answers mapped to None). | confirmed (re-checked) · open |
| G3 | H | All 60 B4/C4 E1 MC items have answer "C", so letter position is confounded with correctness (re-checked). | confirmed · open |
| G4 | M | The slip model is uniform with ε fixed at 0.1 and spread over all K classes including the member's own (0.9 + 0.1/K, not the documented 0.90), so adding a member changes every row. Set-valued membership isn't serialised. `disconfirms` must be rebuilt, not reused. | confirmed · open |
| G5 | M | A/H E8 stores a trace-driven prediction (EXACT on the host) that only a model's response can determine; `materialise` doesn't recompute it. | confirmed · open |
| G6 | M | C E3 LOCAL-t proxy audit: LOCAL-t matches FF on the target only when t ≥ d+2, so the audit re-measures nothing, and d* will read t−2 against the doc's gate of t. | behaviour confirmed, cause open · open |
| G7 | M | C E5 has no give-up member, so an IMPOSSIBLE answer on STUCK items is credited to FF-3-ABORT. | confirmed · open |
| G8 | L | `review.py --reuse` reads the gitignored `.jsonl` and crashes on a fresh clone. | confirmed · open |

### Theory notes (fix PR: `theory-fixes`)

| # | Sev | Finding | Status |
|---|---|---|---|
| T1 | M | `frontier.py` reproduces `results.json` only with `--n 600`, not its default; the docs give no command. | confirmed · open |
| T2 | M | `BICOND∘UP-k` "+0 primitives" is an artifact: the plain `UP-k` program also builds the BICOND machinery. Without it, BICOND costs ~12–14% more. The B4 "no simplicity advantage" conclusion holds, more strongly. | confirmed · open |
| T3 | M | The RASP `UP-k` on SAT does k−1 propagation rounds (`UP-1` ≡ ALWAYS-SAT). The zoo's `UP-k` does not share this bug (see Z7 for its own). | confirmed · open |
| T4 | M | Overstatements, among others: "SAT n\* ≈ 70–80" comes from one cell (INDEX-verbose gives ≈ 41); "×4 budget adds +11 to +31" is contradicted by the notes' own table; "all three lenses agree"; "output length tracks solver conflicts"; JW is called most-constrained-first. | confirmed · open |

## Design questions for Andrew

1. **Selection on one member's behaviour.** Some generators select bases on one member's success or failure, following the vertical docs' §2.8 filters:
   - C E1-SAT keeps bases where GREEDY satisfies in all three orders;
   - C E1-COL needs FF to use χ+1 colours in some order;
   - C E5 needs dead-ends.

   SCOPE §6 rule 6 says never select on one heuristic's errors. Selection on x leaves P(y | x) inference valid, but π then describes the selected population, and only some members get a chance to err. Which rule wins? My suggestion: keep the filters, record them on every item, and reword rule 6 to forbid selection on *model responses* and require every filter to be recorded and conditioned on.
2. **The Stage 1 review page** (claude.ai) has no keep/fix/drop marks yet. After the fixes and regeneration, its items will be stale. Where should a rebuilt page live? Your global rule says not on claude.ai.
3. **Member readings.**
   - `MM-S1` vs mSentential: the B4/C4 doc calls its simplified form provisional.
   - CW-MIN: subset-minimal (the code) or "fewest true atoms" (the doc's words).
   - ONLINE-FF: the edge-stream reading.
4. **Still open from SCOPE §9:**
   - the recommended or lean plan;
   - the Phase 2 gate threshold;
   - who hand-labels traces;
   - whether the v1 co-authors judge the ETR variants.

## Plan

1. Fix PRs for validators, zoo, generators and theory, code only.
2. One regeneration of every item set, plus a CI check that the committed sets reproduce.
3. The runner's smoke runs (in progress) and the recovery harness on the regenerated sets.
4. Dev-tier runs within today's $40 budget: gpt-oss-20b thinking; Qwen3-32B and Qwen3-14B thinking and direct; gpt-oss-120b thinking.
5. Mixture fits only where the recovery gates pass.
