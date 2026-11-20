# Run 2026-11-19-repeat-pc40-gpt-oss-120b-thinking-low

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 1360}.
- **Condition:** `thinking-low`; max_tokens 32768; reasoning `{'effort': 'low'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 680 (data/items/pc40/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1360 responses, 0 failed calls, 680 from cache.
- **Spend:** $0.2052 API-reported over 1 invocation(s) (last cap $0.90; dry-run estimate $2.21, worst case $8.05).
- **Code:** git `ff49489f63bf1d576da4aad6dda3632908945afb`; scorer `scorer-1.5.2` at `ff49489f63bf1d576da4aad6dda3632908945afb`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | partial | Correct of ok |
|---|---|---|---|---|---|
| C | E5 | 1360 | 1359 | 1 | 721/1359 (53%) |
| **All** | | **1360** | **1359** | **1** | **721/1359 (53%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C | E5 | COL | 400 | 1,944 | 1,868 | 1,896 | 1,832 | 541 | 0 (0%) | 400 (100%) | 0.00035 |
| C | E5 | ENT | 320 | 174 | 174 | 158 | 160 | 131 | 0 (0%) | 320 (100%) | 0.00004 |
| C | E5 | SAT | 240 | 2,912 | 2,721 | 2,788 | 2,612 | 1,404 | 0 (0%) | 240 (100%) | 0.00053 |
| C | E5 | STATE | 400 | 1,631 | 1,780 | 1,534 | 1,696 | 932 | 0 (0%) | 400 (100%) | 0.00035 |
| **All** | | | **1360** | **1,541** | **1,594** | **1,469** | **1,536** | | **0** | **1360** | **0.00031** |

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

