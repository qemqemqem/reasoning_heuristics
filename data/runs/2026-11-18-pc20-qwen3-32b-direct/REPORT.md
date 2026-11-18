# Run 2026-11-18-pc20-qwen3-32b-direct

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 1380}.
- **Condition:** `direct`; max_tokens 1024; reasoning `{'enabled': False}`; sampling `{'temperature': 0.7, 'top_p': 0.8, 'top_k': 20}`; system prompt: "Respond with only the final answer in the requested format. Do not explain or show your working.".
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1380 responses, 0 failed calls, 160 from cache.
- **Spend:** $0.0702 API-reported over 1 invocation(s) (last cap $0.50; dry-run estimate $0.08, worst case $0.37).
- **Code:** git `9677076ddcc42f1649a601b502371ccf394584c5`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E5 | 340 | 335 | 5 | 0 | 0 | 17/335 (5%) |
| C | E1 | 240 | 236 | 3 | 0 | 1 | 7/236 (3%) |
| C | E2 | 800 | 799 | 0 | 1 | 0 | 3/799 (0%) |
| **All** | | **1380** | **1370** | **8** | **1** | **1** | **27/1370 (2%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 80 | 74 | 72 | 0 | 0 | 294 | 0 (0%) | 0 (0%) | 0.00003 |
| A/H | E5 | ENT | 80 | 26 | 25 | 0 | 0 | 219 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E5 | KNAP | 80 | 19 | 18 | 0 | 0 | 242 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E5 | SAT | 100 | 29 | 27 | 0 | 0 | 1,414 | 0 (0%) | 0 (0%) | 0.00010 |
| C | E1 | COL | 120 | 116 | 116 | 0 | 0 | 563 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E1 | SAT | 120 | 103 | 104 | 0 | 0 | 1,303 | 1 (1%) | 0 (0%) | 0.00011 |
| C | E2 | COL | 300 | 116 | 116 | 0 | 0 | 572 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E2 | KNAP | 300 | 8 | 9 | 0 | 0 | 208 | 0 (0%) | 0 (0%) | 0.00002 |
| C | E2 | SAT | 200 | 103 | 98 | 0 | 0 | 1,492 | 0 (0%) | 0 (0%) | 0.00012 |
| **All** | | | **1380** | **98** | **69** | **0** | **0** | | **1** | **0** | **0.00006** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 0, max 4; 0 responses (0%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 74 |
| `no_answer_marker` | 12 |
| `repeated_variable` | 4 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E2-6efffb290c-SAT_GREEDY-vs-POLARITY_PLACEBO` | partial | missing 1 variable(s): x94 |
| `AH-E5-1c8b9b665a-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `AH-E5-4de14e5b09-SAT-SAT_I+R` | parse_fail | 24 digits for 12 variables |
| `AH-E5-4de14e5b09-SAT-SAT_P` | parse_fail | 23 digits for 12 variables |
| `AH-E5-19afc608cf-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `AH-E5-d2dc1fb011-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x10, x100, x11, x12, x13, x14, x15, x17, x18, x2 |
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x100, x101, x102, x103, x104, x105, x106, x107, x108, x109 |
| `C-E1-4ebeb9d55e-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x100, x12, x15, x16, x17, x18, x19, x2, x20 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/c5-ANS-FREE | 1 |

