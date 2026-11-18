# Run 2026-11-18-dev-qwen3-14b-direct

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 1270}.
- **Condition:** `direct`; max_tokens 1024; reasoning `{'enabled': False}`; sampling `{'temperature': 0.7, 'top_p': 0.8, 'top_k': 20}`; system prompt: "Respond with only the final answer in the requested format. Do not explain or show your working.".
- **Items:** 1270 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 60, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1270 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.1266 API-reported over 1 invocation(s) (last cap $0.50; dry-run estimate $0.12, worst case $0.35).
- **Code:** git `802e453b03cea85774978ff8e7041986423ebba9`; scorer `scorer-1.5.0` at `802e453b03cea85774978ff8e7041986423ebba9`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 70 | 70 | 0 | 0 | 38/70 (54%) |
| A/H | E2 | 120 | 110 | 0 | 10 | 59/110 (54%) |
| A/H | E5 | 85 | 85 | 0 | 0 | 4/85 (5%) |
| B4/C4 | E1 | 140 | 140 | 0 | 0 | 121/140 (86%) |
| B4/C4 | E2 | 240 | 240 | 0 | 0 | 223/240 (93%) |
| C | E1 | 60 | 58 | 1 | 1 | 0/58 (0%) |
| C | E2 | 200 | 200 | 0 | 0 | 2/200 (1%) |
| C | E3 | 270 | 270 | 0 | 0 | 0/270 (0%) |
| C | E5 | 85 | 85 | 0 | 0 | 18/85 (21%) |
| **All** | | **1270** | **1258** | **1** | **11** | **465/1258 (37%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 20 | 11 | 11 | 0 | 0 | 374 | 0 (0%) | 0 (0%) | 0.00004 |
| A/H | E1 | ENT | 20 | 7 | 7 | 0 | 0 | 227 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E1 | SAT | 30 | 29 | 34 | 0 | 0 | 2,159 | 0 (0%) | 0 (0%) | 0.00021 |
| A/H | E2 | COL | 40 | 11 | 11 | 0 | 0 | 465 | 0 (0%) | 0 (0%) | 0.00005 |
| A/H | E2 | ENT | 40 | 7 | 7 | 0 | 0 | 214 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E2 | SAT | 40 | 45 | 288 | 0 | 0 | 2,768 | 10 (25%) | 0 (0%) | 0.00032 |
| A/H | E5 | COL | 20 | 73 | 59 | 0 | 0 | 282 | 0 (0%) | 0 (0%) | 0.00004 |
| A/H | E5 | ENT | 20 | 19 | 21 | 0 | 0 | 222 | 0 (0%) | 0 (0%) | 0.00003 |
| A/H | E5 | KNAP | 20 | 18 | 17 | 0 | 0 | 244 | 0 (0%) | 0 (0%) | 0.00003 |
| A/H | E5 | SAT | 25 | 25 | 27 | 0 | 0 | 1,367 | 0 (0%) | 0 (0%) | 0.00014 |
| B4/C4 | E1 | ENT | 140 | 5 | 5 | 0 | 0 | 148 | 0 (0%) | 0 (0%) | 0.00002 |
| B4/C4 | E2 | ENT | 240 | 5 | 5 | 0 | 0 | 145 | 0 (0%) | 0 (0%) | 0.00001 |
| C | E1 | COL | 30 | 116 | 117 | 0 | 0 | 563 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E1 | SAT | 30 | 103 | 137 | 0 | 0 | 1,286 | 1 (3%) | 0 (0%) | 0.00015 |
| C | E2 | COL | 75 | 116 | 118 | 0 | 0 | 577 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E2 | KNAP | 75 | 9 | 9 | 0 | 0 | 208 | 0 (0%) | 0 (0%) | 0.00002 |
| C | E2 | SAT | 50 | 103 | 103 | 0 | 0 | 1,494 | 0 (0%) | 0 (0%) | 0.00016 |
| C | E3 | COL-I | 90 | 6 | 6 | 0 | 0 | 1,559 | 0 (0%) | 0 (0%) | 0.00015 |
| C | E3 | COL-U | 180 | 472 | 472 | 0 | 0 | 1,825 | 0 (0%) | 0 (0%) | 0.00027 |
| C | E5 | COL | 25 | 171 | 152 | 0 | 0 | 664 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E5 | ENT | 20 | 2 | 2 | 0 | 0 | 100 | 0 (0%) | 0 (0%) | 0.00001 |
| C | E5 | SAT | 15 | 128 | 126 | 0 | 0 | 1,743 | 0 (0%) | 0 (0%) | 0.00019 |
| C | E5 | STATE | 25 | 103 | 108 | 0 | 0 | 1,125 | 0 (0%) | 0 (0%) | 0.00013 |
| **All** | | | **1270** | **11** | **106** | **0** | **0** | | **11** | **0** | **0.00010** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 8, max 1,025; 10 responses (1%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_malformed` | 30 |
| `no_answer_marker` | 30 |
| `order_differs_from_requested` | 22 |
| `repeated_variable` | 2 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E1-6919e3b400-SAT_c5-ANS-FREE` | parse_fail | unknown variable(s): x59, x60, x61, x62, x63, x64, x65, x66, x68, x69 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/c5-ANS-FREE | 1 |
| E2 | SAT/J/g=SAT | 5 |
| E2 | SAT/J/g=UNSAT | 5 |

