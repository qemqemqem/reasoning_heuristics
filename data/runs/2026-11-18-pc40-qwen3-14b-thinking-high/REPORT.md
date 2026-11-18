# Run 2026-11-18-pc40-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 680}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 680 (data/items/pc40/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 680 responses, 0 failed calls, 0 from cache.
- **Spend:** $1.5998 API-reported over 1 invocation(s) (last cap $2.00; dry-run estimate $1.21, worst case $4.33).
- **Code:** git `9f33eaae34ec5c7affccdaf2744e5d74a4221624`; scorer `scorer-1.5.0` at `9f33eaae34ec5c7affccdaf2744e5d74a4221624`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| C | E5 | 680 | 642 | 17 | 21 | 419/642 (65%) |
| **All** | | **680** | **642** | **17** | **21** | **419/642 (65%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C | E5 | COL | 200 | 16,651 | 17,166 | 9,806 | 10,096 | 634 | 5 (2%) | 200 (100%) | 0.00336 |
| C | E5 | ENT | 160 | 1,718 | 1,749 | 1,304 | 1,363 | 73 | 0 (0%) | 160 (100%) | 0.00034 |
| C | E5 | SAT | 120 | 21,453 | 22,506 | 13,208 | 14,093 | 1,714 | 14 (12%) | 120 (100%) | 0.00449 |
| C | E5 | STATE | 200 | 7,638 | 8,181 | 4,959 | 5,166 | 1,100 | 2 (1%) | 200 (100%) | 0.00168 |
| **All** | | | **680** | **11,960** | **11,838** | **7,186** | **7,296** | | **21** | **680** | **0.00235** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 137, max 972; 298 responses (44%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `no_answer_marker` | 52 |
| `latex_unwrapped` | 40 |
| `fenced_answer_no_marker` | 6 |
| `positional_values` | 2 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E5-2c2dfe9dad-COL_CONTROL_vA_eA` | parse_fail | no answer block |
| `C-E5-ce8a789b13-COL_STUCK_vA_eA` | parse_fail | no answer block |
| `C-E5-39624622bd-COL_STUCK_vA_eA` | parse_fail | no answer block |
| `C-E5-36e5e59b5c-COL_CONTROL_vA_eA` | parse_fail | no answer block |
| `C-E5-d9ea4cc24a-COL_STUCK_vB_eB` | parse_fail | no answer block |
| `C-E5-937ea72041-COL_STUCK_vA_eA` | parse_fail | no answer block |
| `C-E5-a31864ce07-COL_STUCK_vA_eB` | parse_fail | no answer block |
| `C-E5-5230a16001-COL_STUCK_vA_eB` | parse_fail | no answer block |
| `C-E5-0ecc0ad6bb-COL_CONTROL_vA_eA` | parse_fail | no answer block |
| `C-E5-ab798ac378-SAT_DEAD-PERM` | parse_fail | no answer block |
| `C-E5-68a8492052-SAT_CONTROL` | parse_fail | no answer block |
| `C-E5-d895bfea64-SAT_CONTROL` | parse_fail | no answer block |
| `C-E5-fe7d04059f-SAT_CONTROL` | parse_fail | no answer block |
| `C-E5-590cb8a088-SAT_CONTROL` | parse_fail | no answer block |
| `C-E5-6170c88726-ENT_MATCHED_ORDER-B` | parse_fail | no answer block |
| `C-E5-651da004d3-ENT_FAIL_ORDER-B` | parse_fail | no answer block |
| `C-E5-9d3fea6aab-ENT_MATCHED_ORDER-B` | parse_fail | no answer block |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E5 | COL/STUCK/vA/eA | 2 |
| E5 | COL/STUCK/vA/eB | 1 |
| E5 | COL/STUCK/vB/eA | 1 |
| E5 | COL/STUCK/vB/eB | 1 |
| E5 | SAT/CONTROL | 4 |
| E5 | SAT/DEAD | 4 |
| E5 | SAT/DEAD-PERM | 6 |
| E5 | STATE/SAT/s1 | 1 |
| E5 | STATE/SAT/s2 | 1 |

