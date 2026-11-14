# Stage 1 item sets: summary

Built by `python -m reasoning_heuristics.review` (user seed 1). Smoke = 1 item per design cell;
dev = 5 per cell unless stated. Smoke, dev and test bases come from disjoint seed ranges
(smoke [0, 1e5), dev [1e5, 1e6), test [1e6, 2e6)). A one-item-per-cell test batch is generated
only to check dev-vs-test leakage; it is not committed.

| Eval | Smoke items | Dev items | Dev bases (attempts) | Cells covered (dev) | Items per cell (dev) | Smoke pass | Dev pass | Leakage | Dev gen. time |
|---|---|---|---|---|---|---|---|---|---|
| A/H E1 | 14 | 70 | 35 (35) | 14/14 | 5–5 | 100% | 100% | none | 9.9 s |
| A/H E2 | 24 | 120 | 25 (37) | 24/24 | 5–5 | 100% | 100% | none | 32.6 s |
| A/H E5 | 17 | 85 | 20 (20) | 17/17 | 5–5 | 100% | 100% | none | 0.2 s |
| A/H E8 | 12 | 60 | 5 (9) | 12/12 | 5–5 | 100% | 100% | none | 12.8 s |
| C E1 | 12 | 60 | 10 (2451) | 12/12 | 5–5 | 100% | 100% | none | 23.2 s |
| C E2 | 40 | 200 | 40 (1283) | 40/40 | 5–5 | 100% | 100% | none | 99.0 s |
| C E3 | 54 | 270 | 30 (79) | 54/54 | 5–5 | 100% | 100% | none | 2.3 s |
| C E5 | 17 | 85 | 25 (242) | 17/17 | 5–5 | 100% | 100% | none | 15.1 s |
| B4/C4 E1 | 28 | 140 | 5 (6) | 28/28 | 5–5 | 100% | 100% | none | 2.4 s |
| B4/C4 E2 | 48 | 240 | 5 (5) | 48/48 | 5–5 | 100% | 100% | none | 6.3 s |

**Totals:** 266 smoke items and 1330 dev items across 10 evals.

## Items that failed validation

None. Every smoke and dev item passed every validator, and no dev base leaks into the test batch.

## Validators

Item checks: schema, hashes, seed range, ground truth recomputed by an independent solver, every
prediction recomputed from (instance, member, params), and discrimination (two or more members
disagree). Set checks: each generator's designed invariants (see the review packets). Leakage:
dev vs test bases by hash and by isomorphism (graphs, CNF, premise structure), or by lexicon
partition for B4/C4.
