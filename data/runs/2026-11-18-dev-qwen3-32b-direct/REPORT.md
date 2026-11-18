# Run 2026-11-18-dev-qwen3-32b-direct

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 1270}.
- **Condition:** `direct`; max_tokens 1024; reasoning `{'enabled': False}`; sampling `{'temperature': 0.7, 'top_p': 0.8, 'top_k': 20}`; system prompt: "Respond with only the final answer in the requested format. Do not explain or show your working.".
- **Items:** 1270 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 60, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1270 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0986 API-reported over 1 invocation(s) (last cap $0.50; dry-run estimate $0.09, worst case $0.36).
- **Code:** git `802e453b03cea85774978ff8e7041986423ebba9`; scorer `scorer-1.5.0` at `802e453b03cea85774978ff8e7041986423ebba9`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E1 | 70 | 70 | 0 | 0 | 0 | 37/70 (53%) |
| A/H | E2 | 120 | 116 | 0 | 0 | 4 | 59/116 (51%) |
| A/H | E5 | 85 | 84 | 1 | 0 | 0 | 6/84 (7%) |
| B4/C4 | E1 | 140 | 140 | 0 | 0 | 0 | 114/140 (81%) |
| B4/C4 | E2 | 240 | 240 | 0 | 0 | 0 | 229/240 (95%) |
| C | E1 | 60 | 57 | 2 | 0 | 1 | 1/57 (2%) |
| C | E2 | 200 | 199 | 0 | 1 | 0 | 1/199 (1%) |
| C | E3 | 270 | 269 | 0 | 0 | 1 | 18/269 (7%) |
| C | E5 | 85 | 85 | 0 | 0 | 0 | 11/85 (13%) |
| **All** | | **1270** | **1260** | **3** | **1** | **6** | **476/1260 (38%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 20 | 135 | 137 | 0 | 0 | 374 | 0 (0%) | 0 (0%) | 0.00005 |
| A/H | E1 | ENT | 20 | 7 | 7 | 0 | 0 | 227 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E1 | SAT | 30 | 29 | 32 | 0 | 0 | 2,159 | 0 (0%) | 0 (0%) | 0.00015 |
| A/H | E2 | COL | 40 | 191 | 226 | 0 | 0 | 465 | 0 (0%) | 0 (0%) | 0.00008 |
| A/H | E2 | ENT | 40 | 7 | 7 | 0 | 0 | 214 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E2 | SAT | 40 | 38 | 132 | 0 | 0 | 2,768 | 4 (10%) | 0 (0%) | 0.00021 |
| A/H | E5 | COL | 20 | 74 | 71 | 0 | 0 | 282 | 0 (0%) | 0 (0%) | 0.00003 |
| A/H | E5 | ENT | 20 | 15 | 21 | 0 | 0 | 222 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E5 | KNAP | 20 | 19 | 18 | 0 | 0 | 244 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E5 | SAT | 25 | 25 | 27 | 0 | 0 | 1,367 | 0 (0%) | 0 (0%) | 0.00009 |
| B4/C4 | E1 | ENT | 140 | 5 | 16 | 0 | 0 | 148 | 0 (0%) | 0 (0%) | 0.00001 |
| B4/C4 | E2 | ENT | 240 | 5 | 5 | 0 | 0 | 145 | 0 (0%) | 0 (0%) | 0.00001 |
| C | E1 | COL | 30 | 116 | 116 | 0 | 0 | 563 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E1 | SAT | 30 | 103 | 153 | 0 | 0 | 1,286 | 1 (3%) | 0 (0%) | 0.00012 |
| C | E2 | COL | 75 | 116 | 116 | 0 | 0 | 577 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E2 | KNAP | 75 | 9 | 9 | 0 | 0 | 208 | 0 (0%) | 0 (0%) | 0.00002 |
| C | E2 | SAT | 50 | 103 | 93 | 0 | 0 | 1,494 | 0 (0%) | 0 (0%) | 0.00012 |
| C | E3 | COL-I | 90 | 6 | 17 | 0 | 0 | 1,559 | 1 (1%) | 0 (0%) | 0.00010 |
| C | E3 | COL-U | 180 | 473 | 473 | 0 | 0 | 1,825 | 0 (0%) | 0 (0%) | 0.00022 |
| C | E5 | COL | 25 | 8 | 87 | 0 | 0 | 664 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E5 | ENT | 20 | 5 | 4 | 0 | 0 | 100 | 0 (0%) | 0 (0%) | 0.00001 |
| C | E5 | SAT | 15 | 128 | 112 | 0 | 0 | 1,743 | 0 (0%) | 0 (0%) | 0.00014 |
| C | E5 | STATE | 25 | 103 | 108 | 0 | 0 | 1,125 | 0 (0%) | 0 (0%) | 0.00010 |
| **All** | | | **1270** | **11** | **110** | **0** | **0** | | **6** | **0** | **0.00008** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 5, max 1,129; 8 responses (1%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 26 |
| `no_answer_marker` | 14 |
| `order_differs_from_requested` | 9 |
| `witness_malformed` | 4 |
| `latex_unwrapped` | 2 |
| `repeated_variable` | 2 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-1c8b9b665a-SAT-SAT_P` | parse_fail | 24 digits for 12 variables |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x10, x100, x11, x12, x13, x14, x15, x17, x18, x2 |
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x100, x101, x102, x103, x104, x105, x106, x107, x108, x109 |
| `C-E2-effa8ba7e3-SAT_GREEDY-vs-UC_D(UC_GREEDY)` | partial | missing 1 variable(s): x97 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/c5-ANS-FREE | 1 |
| E2 | SAT/J/g=SAT | 2 |
| E2 | SAT/J/g=UNSAT | 1 |
| E2 | SAT/U/g=SAT | 1 |
| E3 | d=6/CRITICAL/I | 1 |

