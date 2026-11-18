# Run 2026-11-18-pc40-qwen3-32b-direct

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 680}.
- **Condition:** `direct`; max_tokens 1024; reasoning `{'enabled': False}`; sampling `{'temperature': 0.7, 'top_p': 0.8, 'top_k': 20}`; system prompt: "Respond with only the final answer in the requested format. Do not explain or show your working.".
- **Items:** 680 (data/items/pc40/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 680 responses, 0 failed calls, 25 from cache.
- **Spend:** $0.0474 API-reported over 1 invocation(s) (last cap $0.30; dry-run estimate $0.05, worst case $0.19).
- **Code:** git `9f33eaae34ec5c7affccdaf2744e5d74a4221624`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | partial | Correct of ok |
|---|---|---|---|---|---|
| C | E5 | 680 | 679 | 1 | 81/679 (12%) |
| **All** | | **680** | **679** | **1** | **81/679 (12%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C | E5 | COL | 200 | 168 | 91 | 0 | 0 | 661 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E5 | ENT | 160 | 5 | 4 | 0 | 0 | 100 | 0 (0%) | 0 (0%) | 0.00001 |
| C | E5 | SAT | 120 | 128 | 106 | 0 | 0 | 1,741 | 0 (0%) | 0 (0%) | 0.00014 |
| C | E5 | STATE | 200 | 103 | 104 | 0 | 0 | 1,127 | 0 (0%) | 0 (0%) | 0.00010 |
| **All** | | | **680** | **103** | **77** | **0** | **0** | | **0** | **0** | **0.00007** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 0, max 0; 0 responses (0%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `no_answer_marker` | 95 |
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E5-0089d6b6a7-COL_STUCK_vB_eB` | partial | missing 1 vertex(s): v34 |

