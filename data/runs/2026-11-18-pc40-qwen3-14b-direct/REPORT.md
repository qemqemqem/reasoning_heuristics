# Run 2026-11-18-pc40-qwen3-14b-direct

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 680}.
- **Condition:** `direct`; max_tokens 1024; reasoning `{'enabled': False}`; sampling `{'temperature': 0.7, 'top_p': 0.8, 'top_k': 20}`; system prompt: "Respond with only the final answer in the requested format. Do not explain or show your working.".
- **Items:** 680 (data/items/pc40/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 680 responses, 0 failed calls, 25 from cache.
- **Spend:** $0.0662 API-reported over 1 invocation(s) (last cap $0.30; dry-run estimate $0.07, worst case $0.19).
- **Code:** git `9f33eaae34ec5c7affccdaf2744e5d74a4221624`; scorer `scorer-1.5.0` at `9f33eaae34ec5c7affccdaf2744e5d74a4221624`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | partial | Correct of ok |
|---|---|---|---|---|---|
| C | E5 | 680 | 679 | 1 | 117/679 (17%) |
| **All** | | **680** | **679** | **1** | **117/679 (17%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C | E5 | COL | 200 | 124 | 142 | 0 | 0 | 661 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E5 | ENT | 160 | 2 | 2 | 0 | 0 | 100 | 0 (0%) | 0 (0%) | 0.00001 |
| C | E5 | SAT | 120 | 128 | 128 | 0 | 0 | 1,741 | 0 (0%) | 0 (0%) | 0.00019 |
| C | E5 | STATE | 200 | 103 | 108 | 0 | 0 | 1,127 | 0 (0%) | 0 (0%) | 0.00013 |
| **All** | | | **680** | **115** | **96** | **0** | **0** | | **0** | **0** | **0.00010** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 0, max 0; 0 responses (0%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `no_answer_marker` | 160 |
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E5-d7a03b5171-COL_STUCK_vB_eB` | partial | missing 1 vertex(s): v35 |

