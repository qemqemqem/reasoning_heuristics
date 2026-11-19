# Run 2026-11-18-budget-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 320}.
- **Condition:** `thinking-high+budget`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 320 (data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz); skipped {'excluded_eval': 0, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 320 responses, 0 failed calls, 0 from cache.
- **Spend:** $1.1938 API-reported over 2 invocation(s) (last cap $1.60; dry-run estimate $0.42, worst case $1.48).
- **Code:** git `43ae447bfdd0487f204cf8d7f36382ffd2bd1509`; scorer `scorer-1.5.2` at `43ae447bfdd0487f204cf8d7f36382ffd2bd1509`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E2 | 120 | 48 | 1 | 71 | 48/48 (100%) |
| C | E2 | 200 | 73 | 0 | 127 | 67/73 (92%) |
| **All** | | **320** | **121** | **1** | **198** | **115/121 (95%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E2 | COL | 40 | 32,768 | 30,765 | 32,768 | 30,736 | 523 | 31 (78%) | 40 (100%) | 0.00432 |
| A/H | E2 | ENT | 40 | 5,070 | 5,798 | 4,854 | 5,630 | 290 | 0 (0%) | 40 (100%) | 0.00082 |
| A/H | E2 | SAT | 40 | 32,768 | 32,768 | 32,768 | 32,768 | 2,353 | 40 (100%) | 40 (100%) | 0.00466 |
| C | E2 | COL | 75 | 22,360 | 22,782 | 22,257 | 22,704 | 533 | 18 (24%) | 75 (100%) | 0.00321 |
| C | E2 | KNAP | 75 | 32,768 | 32,347 | 32,768 | 32,345 | 261 | 67 (89%) | 75 (100%) | 0.00454 |
| C | E2 | SAT | 50 | 32,768 | 31,357 | 32,768 | 31,341 | 1,259 | 42 (84%) | 50 (100%) | 0.00443 |
| **All** | | | **320** | **32,768** | **26,487** | **32,768** | **26,441** | | **198** | **320** | **0.00373** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 19, max 952; 13 responses (4%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E2-1fddfa0400-ENT-ENT_N-hi-mis` | parse_fail | no answer block |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | COL/DSATUR-vs-LF/D(DSATUR|LF) | 1 |
| E2 | COL/DSATUR-vs-LF/G-ONLY | 3 |
| E2 | COL/DSATUR-vs-LF/PLACEBO | 1 |
| E2 | COL/FF-vs-DSATUR/D(DSATUR|FF) | 1 |
| E2 | COL/FF-vs-DSATUR/G-ONLY | 2 |
| E2 | COL/FF-vs-DSATUR/PLACEBO | 2 |
| E2 | COL/FF-vs-LF/BASE | 1 |
| E2 | COL/FF-vs-LF/D(FF|LF) | 2 |
| E2 | COL/FF-vs-LF/D(LF|FF) | 1 |
| E2 | COL/FF-vs-LF/G-ONLY | 2 |
| E2 | COL/FF-vs-LF/PLACEBO | 2 |
| E2 | COL/J/g=impossible | 5 |
| E2 | COL/J/g=possible | 5 |
| E2 | COL/K/g=impossible | 5 |
| E2 | COL/K/g=possible | 4 |
| E2 | COL/U/g=impossible | 4 |
| E2 | COL/U/g=possible | 1 |
| E2 | COL/base/g=impossible | 5 |
| E2 | COL/base/g=possible | 2 |
| E2 | KNAP/PREFIX-vs-RATIO/BASE | 4 |
| E2 | KNAP/PREFIX-vs-RATIO/D(PREFIX|RATIO) | 5 |
| E2 | KNAP/PREFIX-vs-RATIO/D(RATIO|PREFIX) | 3 |
| E2 | KNAP/PREFIX-vs-RATIO/G-ONLY | 4 |
| E2 | KNAP/PREFIX-vs-RATIO/PLACEBO | 4 |
| E2 | KNAP/RATIO-vs-DIFF/BASE | 4 |
| E2 | KNAP/RATIO-vs-DIFF/D(DIFF|RATIO) | 4 |
| E2 | KNAP/RATIO-vs-DIFF/D(RATIO|DIFF) | 4 |
| E2 | KNAP/RATIO-vs-DIFF/G-ONLY | 5 |
| E2 | KNAP/RATIO-vs-DIFF/PLACEBO | 5 |
| E2 | KNAP/RATIO-vs-VALUE/BASE | 5 |
| E2 | KNAP/RATIO-vs-VALUE/D(RATIO|VALUE) | 5 |
| E2 | KNAP/RATIO-vs-VALUE/D(VALUE|RATIO) | 5 |
| E2 | KNAP/RATIO-vs-VALUE/G-ONLY | 5 |
| E2 | KNAP/RATIO-vs-VALUE/PLACEBO | 5 |
| E2 | SAT/GREEDY-vs-POLARITY/BASE | 4 |
| E2 | SAT/GREEDY-vs-POLARITY/D(GREEDY|POLARITY) | 5 |
| E2 | SAT/GREEDY-vs-POLARITY/D(POLARITY|GREEDY) | 4 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 5 |
| E2 | SAT/GREEDY-vs-POLARITY/PLACEBO | 4 |
| E2 | SAT/GREEDY-vs-UC/BASE | 4 |
| E2 | SAT/GREEDY-vs-UC/D(GREEDY|UC) | 4 |
| E2 | SAT/GREEDY-vs-UC/D(UC|GREEDY) | 3 |
| E2 | SAT/GREEDY-vs-UC/G-ONLY | 5 |
| E2 | SAT/GREEDY-vs-UC/PLACEBO | 4 |
| E2 | SAT/J/g=SAT | 5 |
| E2 | SAT/J/g=UNSAT | 5 |
| E2 | SAT/K/g=SAT | 5 |
| E2 | SAT/K/g=UNSAT | 5 |
| E2 | SAT/U/g=SAT | 5 |
| E2 | SAT/U/g=UNSAT | 5 |
| E2 | SAT/base/g=SAT | 5 |
| E2 | SAT/base/g=UNSAT | 5 |

