# Run 2026-11-18-pc40-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 680}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 680 (data/items/pc40/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 680 responses, 0 failed calls, 0 from cache.
- **Spend:** $1.6829 API-reported over 1 invocation(s) (last cap $2.50; dry-run estimate $1.39, worst case $5.03).
- **Code:** git `9f33eaae34ec5c7affccdaf2744e5d74a4221624`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| C | E5 | 680 | 657 | 9 | 14 | 406/657 (62%) |
| **All** | | **680** | **657** | **9** | **14** | **406/657 (62%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C | E5 | COL | 200 | 15,228 | 15,767 | 9,326 | 9,649 | 634 | 1 (0%) | 200 (100%) | 0.00357 |
| C | E5 | ENT | 160 | 1,578 | 1,784 | 1,094 | 1,148 | 73 | 1 (1%) | 160 (100%) | 0.00040 |
| C | E5 | SAT | 120 | 18,076 | 19,997 | 11,444 | 12,534 | 1,714 | 9 (8%) | 120 (100%) | 0.00459 |
| C | E5 | STATE | 200 | 6,894 | 7,567 | 4,286 | 4,760 | 1,100 | 3 (2%) | 200 (100%) | 0.00177 |
| **All** | | | **680** | **10,694** | **10,812** | **6,536** | **6,720** | | **14** | **680** | **0.00247** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 152, max 1,490; 290 responses (43%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `no_answer_marker` | 143 |
| `positional_values` | 50 |
| `latex_unwrapped` | 36 |
| `extra_text_in_block` | 3 |
| `fenced_answer_no_marker` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E5-c00da18e71-COL_STUCK_vB_eB` | parse_fail | no answer block |
| `C-E5-abe098ce3e-COL_STUCK_vB_eA` | parse_fail | no answer block |
| `C-E5-44a2799844-SAT_DEAD` | parse_fail | no answer block |
| `C-E5-53fbfc7c34-SAT_CONTROL` | parse_fail | no answer block |
| `C-E5-4b035f3c8b-SAT_DEAD` | parse_fail | unknown variable(s): x79 |
| `C-E5-5b4502de93-SAT_DEAD` | parse_fail | 24 values without names for 25 variables |
| `C-E5-5b4502de93-SAT_CONTROL` | parse_fail | 24 values without names for 25 variables |
| `C-E5-511656cda9-STATE_COL_s3` | parse_fail | no answer block |
| `C-E5-32a6b56753-ENT_FAIL_ORDER-B` | parse_fail | no answer block |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E5 | COL/STUCK/vB/eA | 1 |
| E5 | ENT/FAIL/ORDER-B | 1 |
| E5 | SAT/CONTROL | 4 |
| E5 | SAT/DEAD | 2 |
| E5 | SAT/DEAD-PERM | 3 |
| E5 | STATE/SAT/s1 | 1 |
| E5 | STATE/SAT/s2 | 1 |
| E5 | STATE/SAT/s3 | 1 |

