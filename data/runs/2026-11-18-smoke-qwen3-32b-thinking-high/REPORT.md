# Run 2026-11-18-smoke-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 254}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 254 (data/items/smoke/AH_E1_smoke_s1.jsonl.gz, data/items/smoke/AH_E2_smoke_s1.jsonl.gz, data/items/smoke/AH_E5_smoke_s1.jsonl.gz, data/items/smoke/AH_E8_smoke_s1.jsonl.gz, data/items/smoke/B4C4_E1_smoke_s1.jsonl.gz, data/items/smoke/B4C4_E2_smoke_s1.jsonl.gz, data/items/smoke/C_E1_smoke_s1.jsonl.gz, data/items/smoke/C_E2_smoke_s1.jsonl.gz, data/items/smoke/C_E3_smoke_s1.jsonl.gz, data/items/smoke/C_E5_smoke_s1.jsonl.gz); skipped {'excluded_eval': 12, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 254 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.4941 API-reported (cap $1.75; dry-run estimate $0.44, worst case $1.88).
- **Code:** git `03a87c1a14f64d320edbf389ed7975829f0c14db`; scorer `scorer-1.4.0` at `654ea00eaa43dfdae4065216b9f5e20276869b1d`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 14 | 14 | 0 | 11/14 (79%) |
| A/H | E2 | 24 | 20 | 4 | 13/20 (65%) |
| A/H | E5 | 17 | 17 | 0 | 10/17 (59%) |
| B4/C4 | E1 | 28 | 28 | 0 | 28/28 (100%) |
| B4/C4 | E2 | 48 | 48 | 0 | 48/48 (100%) |
| C | E1 | 12 | 12 | 0 | 3/12 (25%) |
| C | E2 | 40 | 40 | 0 | 21/40 (52%) |
| C | E3 | 54 | 53 | 1 | 41/53 (77%) |
| C | E5 | 17 | 16 | 1 | 13/16 (81%) |
| **All** | | **254** | **248** | **6** | **188/248 (76%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 4 | 12,640 | 12,218 | 10,392 | 9,776 | 286 | 0 (0%) | 4 (100%) | 0.00276 |
| A/H | E1 | ENT | 4 | 1,894 | 1,831 | 1,685 | 1,647 | 184 | 0 (0%) | 4 (100%) | 0.00042 |
| A/H | E1 | SAT | 6 | 14,818 | 16,059 | 9,133 | 9,611 | 1,462 | 0 (0%) | 6 (100%) | 0.00369 |
| A/H | E2 | COL | 8 | 12,036 | 11,594 | 9,712 | 9,436 | 438 | 0 (0%) | 8 (100%) | 0.00262 |
| A/H | E2 | ENT | 8 | 1,278 | 1,264 | 1,136 | 1,163 | 226 | 0 (0%) | 8 (100%) | 0.00030 |
| A/H | E2 | SAT | 8 | 29,442 | 27,667 | 19,226 | 18,529 | 2,724 | 4 (50%) | 8 (100%) | 0.00637 |
| A/H | E5 | COL | 4 | 4,748 | 5,842 | 3,867 | 4,986 | 233 | 0 (0%) | 4 (100%) | 0.00132 |
| A/H | E5 | ENT | 4 | 2,348 | 2,282 | 2,271 | 2,207 | 188 | 0 (0%) | 4 (100%) | 0.00052 |
| A/H | E5 | KNAP | 4 | 10,129 | 10,367 | 6,762 | 6,810 | 214 | 0 (0%) | 4 (100%) | 0.00234 |
| A/H | E5 | SAT | 5 | 21,865 | 19,729 | 13,741 | 12,997 | 1,193 | 0 (0%) | 5 (100%) | 0.00450 |
| B4/C4 | E1 | ENT | 28 | 1,109 | 1,438 | 876 | 1,045 | 118 | 0 (0%) | 28 (100%) | 0.00033 |
| B4/C4 | E2 | ENT | 48 | 466 | 507 | 404 | 435 | 117 | 0 (0%) | 48 (100%) | 0.00012 |
| C | E1 | COL | 6 | 6,998 | 7,818 | 4,586 | 5,198 | 537 | 0 (0%) | 6 (100%) | 0.00179 |
| C | E1 | SAT | 6 | 14,521 | 14,942 | 9,048 | 9,260 | 1,188 | 0 (0%) | 6 (100%) | 0.00342 |
| C | E2 | COL | 15 | 8,377 | 8,737 | 5,559 | 5,670 | 543 | 0 (0%) | 15 (100%) | 0.00199 |
| C | E2 | KNAP | 15 | 12,693 | 13,094 | 7,423 | 7,628 | 181 | 0 (0%) | 15 (100%) | 0.00294 |
| C | E2 | SAT | 10 | 19,276 | 20,426 | 12,045 | 12,494 | 1,458 | 0 (0%) | 10 (100%) | 0.00467 |
| C | E3 | COL-I | 18 | 7,092 | 7,683 | 4,423 | 4,720 | 1,532 | 0 (0%) | 18 (100%) | 0.00182 |
| C | E3 | COL-U | 36 | 10,248 | 12,273 | 5,745 | 6,896 | 1,797 | 1 (3%) | 36 (100%) | 0.00286 |
| C | E5 | COL | 5 | 13,967 | 14,218 | 8,768 | 8,750 | 636 | 0 (0%) | 5 (100%) | 0.00323 |
| C | E5 | ENT | 4 | 2,144 | 2,101 | 1,510 | 1,476 | 74 | 0 (0%) | 4 (100%) | 0.00048 |
| C | E5 | SAT | 3 | 21,786 | 24,439 | 13,389 | 16,004 | 1,711 | 1 (33%) | 3 (100%) | 0.00558 |
| C | E5 | STATE | 5 | 6,527 | 6,834 | 3,851 | 4,497 | 1,080 | 0 (0%) | 5 (100%) | 0.00160 |
| **All** | | | **254** | **7,276** | **8,462** | **4,404** | **5,402** | | **6** | **254** | **0.00195** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 124, max 772; 95 responses (37%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 34 |
| `positional_values` | 6 |
| `placeholder_names` | 4 |
| `no_answer_marker` | 4 |
| `extra_text_in_block` | 2 |
| `witness_malformed` | 1 |
| `witness_partial` | 1 |
| `fenced_answer_no_marker` | 1 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/J/g=SAT | 1 |
| E2 | SAT/J/g=UNSAT | 1 |
| E2 | SAT/K/g=SAT | 1 |
| E2 | SAT/K/g=UNSAT | 1 |
| E3 | d=4/PLACEBO/U-REV | 1 |
| E5 | SAT/DEAD-PERM | 1 |

