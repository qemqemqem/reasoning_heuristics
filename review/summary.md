# Stage 1 item sets: summary

Built by `python -m reasoning_heuristics.review` (user seed 1). Smoke = 1 item per design cell;
dev = 5 per cell unless stated. Smoke, dev and test bases come from disjoint seed ranges
(smoke [0, 1e5), dev [1e5, 1e6), test [1e6, 2e6)). A one-item-per-cell test batch is generated
only to check dev-vs-test leakage; it is not committed.

| Eval | Smoke items | Dev items | Dev bases (attempts) | Cells covered (dev) | Items per cell (dev) | Smoke pass | Dev pass | Leakage |
|---|---|---|---|---|---|---|---|---|
| A/H E1 | 14 | 70 | 35 (35) | 14/14 | 5–5 | 100% | 100% | none |
| A/H E2 | 24 | 120 | 25 (37) | 24/24 | 5–5 | 100% | 100% | none |
| A/H E5 | 17 | 85 | 20 (20) | 17/17 | 5–5 | 100% | 100% | none |
| A/H E8 | 12 | 60 | 5 (9) | 12/12 | 5–5 | 100% | 100% | none |
| C E1 | 12 | 60 | 10 (2451) | 12/12 | 5–5 | 100% | 100% | none |
| C E2 | 40 | 200 | 40 (1283) | 40/40 | 5–5 | 100% | 100% | none |
| C E3 | 54 | 270 | 30 (79) | 54/54 | 5–5 | 100% | 100% | none |
| C E5 | 17 | 85 | 25 (141) | 17/17 | 5–5 | 100% | 100% | none |
| B4/C4 E1 | 28 | 140 | 5 (6) | 28/28 | 5–5 | 100% | 100% | none |
| B4/C4 E2 | 48 | 240 | 5 (5) | 48/48 | 5–5 | 100% | 100% | none |

**Totals:** 266 smoke items and 1330 dev items across 10 evals.

## Items that failed validation

None. Every smoke and dev item passed every validator, and no dev instance leaks into the test batch.

## Known lineage gaps (reported, not failed)

The lineage check (`validate/checks.py`) enforces: **source-resolves**: a variant's source_hash is the content hash of an item in the same collection; **root-is-base**: an item with no source is its own base: content_hash == base_hash; **source-same-base**: a variant shares the base_hash of the item it was made from; **base-provenance**: every item of one base carries the base's seed, split and tier.
The (generator, rule) pairs below are listed in `KNOWN_LINEAGE_GAPS`: they are reported here instead of
failing validation until their generators are fixed. Any other lineage violation fails.

None.

## Hash collisions across sets

None: no 16-hex content or presentation hash is shared by two different contents or prompts across every smoke, dev and test set built here.

## Validators

Item checks: schema, hashes, the seed's tier range, ground truth and the readouts behind the likelihood
tables (solution, completion and optimal-partition counts, optimal sets, the C E3 asked answer)
recomputed by `validate/independent.py` (its own instance reading and stated-rule transforms,
CaDiCaL instead of the generators' MiniSat), consistent premises, every prediction recomputed from
(instance, member, params), and discrimination (two or more members differ on the item's scoring
channel, and its likelihood table is non-degenerate). Set checks: hash
collisions, lineage, and each generator's designed invariants (see the review packets). Leakage: every
test instance against every dev instance, by base hash and by isomorphism of the stated problem
(graphs, canonical CNF, premise structure, knapsack item multisets, TSP distance matrices), or by
lexicon partition for B4/C4.
