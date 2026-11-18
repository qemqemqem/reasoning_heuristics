# Run 2026-11-18-pc40-gpt-oss-120b-thinking-low

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 680}.
- **Condition:** `thinking-low`; max_tokens 32768; reasoning `{'effort': 'low'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 680 (data/items/pc40/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 680 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.2141 API-reported over 1 invocation(s) (last cap $0.50; dry-run estimate $1.10, worst case $4.03).
- **Code:** git `9f33eaae34ec5c7affccdaf2744e5d74a4221624`; scorer `scorer-1.5.0` at `9f33eaae34ec5c7affccdaf2744e5d74a4221624`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | partial | Correct of ok |
|---|---|---|---|---|---|
| C | E5 | 680 | 679 | 1 | 359/679 (53%) |
| **All** | | **680** | **679** | **1** | **359/679 (53%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C | E5 | COL | 200 | 2,050 | 1,885 | 1,970 | 1,849 | 541 | 0 (0%) | 200 (100%) | 0.00036 |
| C | E5 | ENT | 160 | 174 | 177 | 158 | 162 | 131 | 0 (0%) | 160 (100%) | 0.00004 |
| C | E5 | SAT | 120 | 3,158 | 2,879 | 2,998 | 2,768 | 1,404 | 0 (0%) | 120 (100%) | 0.00056 |
| C | E5 | STATE | 200 | 1,634 | 1,790 | 1,516 | 1,707 | 932 | 0 (0%) | 200 (100%) | 0.00035 |
| **All** | | | **680** | **1,568** | **1,630** | **1,496** | **1,573** | | **0** | **680** | **0.00031** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 0, max 0; 0 responses (0%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E5-39c223a848-SAT_DEAD` | partial | missing 1 variable(s): x45 |

