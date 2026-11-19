# Run 2026-11-19-repeat-pc20-qwen3-14b-direct

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 2760}.
- **Condition:** `direct`; max_tokens 1024; reasoning `{'enabled': False}`; sampling `{'temperature': 0.7, 'top_p': 0.8, 'top_k': 20}`; system prompt: "Respond with only the final answer in the requested format. Do not explain or show your working.".
- **Items:** 1380 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 2760 responses, 0 failed calls, 1380 from cache.
- **Spend:** $0.1108 API-reported over 1 invocation(s) (last cap $0.30; dry-run estimate $0.22, worst case $0.72).
- **Code:** git `ff49489f63bf1d576da4aad6dda3632908945afb`; scorer `scorer-1.5.2` at `ff49489f63bf1d576da4aad6dda3632908945afb`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E5 | 680 | 679 | 1 | 0 | 0 | 37/679 (5%) |
| C | E1 | 480 | 471 | 2 | 2 | 5 | 4/471 (1%) |
| C | E2 | 1600 | 1600 | 0 | 0 | 0 | 23/1600 (1%) |
| **All** | | **2760** | **2750** | **3** | **2** | **5** | **64/2750 (2%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | COL | 160 | 72 | 57 | 0 | 0 | 294 | 0 (0%) | 0 (0%) | 0.00004 |
| A/H | E5 | ENT | 160 | 26 | 24 | 0 | 0 | 219 | 0 (0%) | 0 (0%) | 0.00003 |
| A/H | E5 | KNAP | 160 | 19 | 18 | 0 | 0 | 242 | 0 (0%) | 0 (0%) | 0.00003 |
| A/H | E5 | SAT | 200 | 27 | 27 | 0 | 0 | 1,414 | 0 (0%) | 0 (0%) | 0.00014 |
| C | E1 | COL | 240 | 116 | 117 | 0 | 0 | 563 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E1 | SAT | 240 | 103 | 128 | 0 | 0 | 1,303 | 5 (2%) | 0 (0%) | 0.00015 |
| C | E2 | COL | 600 | 116 | 117 | 0 | 0 | 572 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E2 | KNAP | 600 | 9 | 9 | 0 | 0 | 208 | 0 (0%) | 0 (0%) | 0.00002 |
| C | E2 | SAT | 400 | 103 | 103 | 0 | 0 | 1,492 | 0 (0%) | 0 (0%) | 0.00016 |
| **All** | | | **2760** | **103** | **71** | **0** | **0** | | **5** | **0** | **0.00008** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 0, max 0; 0 responses (0%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 157 |
| `no_answer_marker` | 75 |
| `repeated_variable` | 18 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-a3c3032647-ENT-ENT_I+R` | parse_fail | unrecognised fact(s): ['the door is closed', 'the switch is down'] |
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x59, x60, x61, x62, x63, x64, x65, x66, x68, x69 |
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x1, x10, x11, x13, x14, x15, x16, x17, x18, x19 |
| `C-E1-28e2b6e625-SAT_c5-ANS-FREE` | partial | missing 1 variable(s): x33 |
| `C-E1-28e2b6e625-SAT_c5-ANS-FREE` | partial | missing 1 variable(s): x33 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/c5-ANS-FREE | 5 |

