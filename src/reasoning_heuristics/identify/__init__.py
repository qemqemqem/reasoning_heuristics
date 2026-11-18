"""The identification engine (SCOPE §4 item 4): which heuristics a model's answers come from.

Per (model, condition, eval, domain) it fits the mixture
P(y | x) = sum_h pi_h P(y | h, x) + pi_0 q(y | x)
over the zoo members recorded on the items, and reports the weights with 95% cluster-bootstrap
intervals, the unexplained mass pi_0, the slip rate, error agreement and lifts over a
within-cell permutation baseline.

Modules, in data-flow order:

- `records`: the response record a runner emits, and the join to items (on item_id, hashes checked).
- `units`: item sets, fit units (eval x domain) and the clusters the bootstrap resamples.
- `spaces`: answer spaces per scoring channel: keys, distances, the near-miss slip kernel, q.
- `members`: each member's predicted distribution on an item (set-valued members rebuilt by validity).
- `likelihood`: P(y | h, x) under the near-miss or uniform-candidate slip model, tie groups,
  non-ok categories and censoring (with a token-model hook), the tensors the fit reads.
- `mixture`: EM with availability renormalisation, cluster bootstrap, feature-dependent softmax weights.
- `agreement`: error agreement with explicit tie handling, permutation baselines and lifts.
- `engine`: `fit_all(items, responses)`.

The positive controls (fake models with planted mixtures and the recovery harness, SCOPE §4
item 5) are built on this package and must pass before any LLM data is analysed (DESIGN §5 rule 12).
"""
