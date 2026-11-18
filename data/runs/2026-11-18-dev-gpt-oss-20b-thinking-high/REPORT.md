# Run 2026-11-18-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 1270}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 1270 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 60, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1270 responses, 0 failed calls, 0 from cache.
- **Spend:** $3.1662 API-reported over 3 invocation(s) (last cap $1.50; dry-run estimate $1.35, worst case $5.85).
- **Code:** git `62d8345a6eec0691e8eb0c36f085239c09d1f46e`; scorer `scorer-1.5.1` at `e0b1720b2f4387cadc86c4544081f6dc778aaa0e`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 70 | 43 | 0 | 27 | 43/43 (100%) |
| A/H | E2 | 120 | 52 | 0 | 68 | 51/52 (98%) |
| A/H | E5 | 85 | 55 | 0 | 30 | 54/55 (98%) |
| B4/C4 | E1 | 140 | 139 | 1 | 0 | 139/139 (100%) |
| B4/C4 | E2 | 240 | 240 | 0 | 0 | 240/240 (100%) |
| C | E1 | 60 | 46 | 0 | 14 | 45/46 (98%) |
| C | E2 | 200 | 70 | 1 | 129 | 66/70 (94%) |
| C | E3 | 270 | 96 | 0 | 174 | 96/96 (100%) |
| C | E5 | 85 | 65 | 0 | 20 | 65/65 (100%) |
| **All** | | **1270** | **806** | **2** | **462** | **799/806 (99%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 20 | 27,832 | 23,361 | 27,690 | 23,308 | 396 | 8 (40%) | 20 (100%) | 0.00328 |
| A/H | E1 | ENT | 20 | 3,766 | 5,173 | 3,754 | 5,161 | 258 | 0 (0%) | 20 (100%) | 0.00073 |
| A/H | E1 | SAT | 30 | 32,768 | 27,222 | 32,768 | 27,214 | 1,860 | 19 (63%) | 30 (100%) | 0.00387 |
| A/H | E2 | COL | 40 | 32,768 | 30,438 | 32,768 | 30,410 | 478 | 29 (72%) | 40 (100%) | 0.00428 |
| A/H | E2 | ENT | 40 | 4,505 | 5,206 | 4,493 | 5,135 | 245 | 0 (0%) | 40 (100%) | 0.00074 |
| A/H | E2 | SAT | 40 | 32,768 | 32,766 | 32,768 | 32,766 | 2,308 | 39 (98%) | 40 (100%) | 0.00465 |
| A/H | E5 | COL | 20 | 9,220 | 12,178 | 9,152 | 12,103 | 311 | 1 (5%) | 20 (100%) | 0.00171 |
| A/H | E5 | ENT | 20 | 8,182 | 9,600 | 8,142 | 9,568 | 253 | 0 (0%) | 20 (100%) | 0.00135 |
| A/H | E5 | KNAP | 20 | 32,768 | 24,095 | 32,768 | 24,086 | 259 | 11 (55%) | 20 (100%) | 0.00338 |
| A/H | E5 | SAT | 25 | 32,768 | 29,988 | 32,768 | 29,982 | 1,219 | 18 (72%) | 25 (100%) | 0.00423 |
| B4/C4 | E1 | ENT | 140 | 1,994 | 2,804 | 1,934 | 2,628 | 177 | 0 (0%) | 140 (100%) | 0.00040 |
| B4/C4 | E2 | ENT | 240 | 597 | 672 | 580 | 635 | 174 | 0 (0%) | 240 (100%) | 0.00010 |
| C | E1 | COL | 30 | 20,306 | 21,775 | 20,202 | 21,699 | 477 | 8 (27%) | 30 (100%) | 0.00306 |
| C | E1 | SAT | 30 | 27,660 | 26,669 | 27,575 | 26,598 | 1,054 | 6 (20%) | 30 (100%) | 0.00376 |
| C | E2 | COL | 75 | 21,210 | 21,719 | 21,107 | 21,640 | 488 | 18 (24%) | 75 (100%) | 0.00305 |
| C | E2 | KNAP | 75 | 32,768 | 32,428 | 32,768 | 32,427 | 216 | 69 (92%) | 75 (100%) | 0.00455 |
| C | E2 | SAT | 50 | 32,768 | 32,134 | 32,768 | 32,119 | 1,214 | 42 (84%) | 50 (100%) | 0.00453 |
| C | E3 | COL-I | 90 | 17,852 | 18,101 | 17,842 | 18,092 | 1,226 | 0 (0%) | 90 (100%) | 0.00257 |
| C | E3 | COL-U | 180 | 32,768 | 32,518 | 32,768 | 32,504 | 1,426 | 174 (97%) | 180 (100%) | 0.00459 |
| C | E5 | COL | 25 | 25,204 | 25,126 | 25,053 | 25,017 | 544 | 7 (28%) | 25 (100%) | 0.00353 |
| C | E5 | ENT | 20 | 980 | 1,137 | 972 | 1,128 | 131 | 0 (0%) | 20 (100%) | 0.00016 |
| C | E5 | SAT | 15 | 32,768 | 32,170 | 32,768 | 32,157 | 1,406 | 13 (87%) | 15 (100%) | 0.00454 |
| C | E5 | STATE | 25 | 11,304 | 13,994 | 11,201 | 13,934 | 931 | 0 (0%) | 25 (100%) | 0.00199 |
| **All** | | | **1270** | **19,008** | **17,662** | **18,918** | **17,615** | | **462** | **1270** | **0.00249** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 23, max 861; 124 responses (10%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 74 |
| `extra_text_in_block` | 1 |
| `no_answer_marker` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `B4C4-E1-974339c483-M-M2·CD·MC` | parse_fail | no answer block |
| `C-E2-313138f638-COL_FF-vs-DSATUR_BASE` | parse_fail | no answer block |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | COL/c1-NAT | 1 |
| E1 | COL/c2-RELABEL | 2 |
| E1 | COL/c3-ANS-LABEL | 1 |
| E1 | COL/c4-ANS-RAND | 2 |
| E1 | COL/c5-ANS-FREE | 1 |
| E1 | COL/c6-RELIST | 1 |
| E1 | COL/critical/x | 2 |
| E1 | COL/critical/x-prime | 5 |
| E1 | COL/null/x-prime | 1 |
| E1 | SAT/B1/x | 1 |
| E1 | SAT/c2-RELABEL | 2 |
| E1 | SAT/c3-ANS-LABEL | 1 |
| E1 | SAT/c4-ANS-RAND | 1 |
| E1 | SAT/c5-ANS-FREE | 2 |
| E1 | SAT/critical/x | 4 |
| E1 | SAT/critical/x-prime | 5 |
| E1 | SAT/null/x | 5 |
| E1 | SAT/null/x-prime | 4 |
| E2 | COL/DSATUR-vs-LF/D(DSATUR|LF) | 3 |
| E2 | COL/DSATUR-vs-LF/D(LF|DSATUR) | 1 |
| E2 | COL/DSATUR-vs-LF/G-ONLY | 3 |
| E2 | COL/FF-vs-DSATUR/D(DSATUR|FF) | 1 |
| E2 | COL/FF-vs-DSATUR/D(FF|DSATUR) | 2 |
| E2 | COL/FF-vs-DSATUR/G-ONLY | 2 |
| E2 | COL/FF-vs-DSATUR/PLACEBO | 2 |
| E2 | COL/FF-vs-LF/D(FF|LF) | 1 |
| E2 | COL/FF-vs-LF/D(LF|FF) | 1 |
| E2 | COL/FF-vs-LF/G-ONLY | 2 |
| E2 | COL/J/g=impossible | 4 |
| E2 | COL/J/g=possible | 5 |
| E2 | COL/K/g=impossible | 4 |
| E2 | COL/K/g=possible | 5 |
| E2 | COL/U/g=impossible | 3 |
| E2 | COL/U/g=possible | 2 |
| E2 | COL/base/g=impossible | 5 |
| E2 | COL/base/g=possible | 1 |
| E2 | KNAP/PREFIX-vs-RATIO/BASE | 3 |
| E2 | KNAP/PREFIX-vs-RATIO/D(PREFIX|RATIO) | 4 |
| E2 | KNAP/PREFIX-vs-RATIO/D(RATIO|PREFIX) | 5 |
| E2 | KNAP/PREFIX-vs-RATIO/G-ONLY | 5 |
| E2 | KNAP/PREFIX-vs-RATIO/PLACEBO | 5 |
| E2 | KNAP/RATIO-vs-DIFF/BASE | 5 |
| E2 | KNAP/RATIO-vs-DIFF/D(DIFF|RATIO) | 4 |
| E2 | KNAP/RATIO-vs-DIFF/D(RATIO|DIFF) | 3 |
| E2 | KNAP/RATIO-vs-DIFF/G-ONLY | 5 |
| E2 | KNAP/RATIO-vs-DIFF/PLACEBO | 5 |
| E2 | KNAP/RATIO-vs-VALUE/BASE | 5 |
| E2 | KNAP/RATIO-vs-VALUE/D(RATIO|VALUE) | 5 |
| E2 | KNAP/RATIO-vs-VALUE/D(VALUE|RATIO) | 5 |
| E2 | KNAP/RATIO-vs-VALUE/G-ONLY | 5 |
| E2 | KNAP/RATIO-vs-VALUE/PLACEBO | 5 |
| E2 | SAT/GREEDY-vs-POLARITY/BASE | 5 |
| E2 | SAT/GREEDY-vs-POLARITY/D(GREEDY|POLARITY) | 4 |
| E2 | SAT/GREEDY-vs-POLARITY/D(POLARITY|GREEDY) | 4 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 5 |
| E2 | SAT/GREEDY-vs-POLARITY/PLACEBO | 5 |
| E2 | SAT/GREEDY-vs-UC/BASE | 4 |
| E2 | SAT/GREEDY-vs-UC/D(GREEDY|UC) | 3 |
| E2 | SAT/GREEDY-vs-UC/D(UC|GREEDY) | 3 |
| E2 | SAT/GREEDY-vs-UC/G-ONLY | 5 |
| E2 | SAT/GREEDY-vs-UC/PLACEBO | 4 |
| E2 | SAT/J/g=SAT | 5 |
| E2 | SAT/J/g=UNSAT | 5 |
| E2 | SAT/K/g=SAT | 5 |
| E2 | SAT/K/g=UNSAT | 5 |
| E2 | SAT/U/g=SAT | 5 |
| E2 | SAT/U/g=UNSAT | 5 |
| E2 | SAT/base/g=SAT | 4 |
| E2 | SAT/base/g=UNSAT | 5 |
| E3 | d=1/BASE/U-LIST | 5 |
| E3 | d=1/BASE/U-REV | 5 |
| E3 | d=1/CRITICAL/U-LIST | 3 |
| E3 | d=1/CRITICAL/U-REV | 5 |
| E3 | d=1/PLACEBO/U-LIST | 5 |
| E3 | d=1/PLACEBO/U-REV | 5 |
| E3 | d=2/BASE/U-LIST | 5 |
| E3 | d=2/BASE/U-REV | 4 |
| E3 | d=2/CRITICAL/U-LIST | 5 |
| E3 | d=2/CRITICAL/U-REV | 5 |
| E3 | d=2/PLACEBO/U-LIST | 5 |
| E3 | d=2/PLACEBO/U-REV | 5 |
| E3 | d=3/BASE/U-LIST | 5 |
| E3 | d=3/BASE/U-REV | 5 |
| E3 | d=3/CRITICAL/U-LIST | 5 |
| E3 | d=3/CRITICAL/U-REV | 5 |
| E3 | d=3/PLACEBO/U-LIST | 5 |
| E3 | d=3/PLACEBO/U-REV | 5 |
| E3 | d=4/BASE/U-LIST | 4 |
| E3 | d=4/BASE/U-REV | 5 |
| E3 | d=4/CRITICAL/U-LIST | 5 |
| E3 | d=4/CRITICAL/U-REV | 5 |
| E3 | d=4/PLACEBO/U-LIST | 5 |
| E3 | d=4/PLACEBO/U-REV | 5 |
| E3 | d=6/BASE/U-LIST | 5 |
| E3 | d=6/BASE/U-REV | 5 |
| E3 | d=6/CRITICAL/U-LIST | 5 |
| E3 | d=6/CRITICAL/U-REV | 5 |
| E3 | d=6/PLACEBO/U-LIST | 5 |
| E3 | d=6/PLACEBO/U-REV | 5 |
| E3 | d=8/BASE/U-LIST | 5 |
| E3 | d=8/BASE/U-REV | 5 |
| E3 | d=8/CRITICAL/U-LIST | 4 |
| E3 | d=8/CRITICAL/U-REV | 5 |
| E3 | d=8/PLACEBO/U-LIST | 4 |
| E3 | d=8/PLACEBO/U-REV | 5 |
| E5 | COL/CONTROL/vA/eA | 2 |
| E5 | COL/I | 1 |
| E5 | COL/STUCK/vA/eA | 1 |
| E5 | COL/STUCK/vA/eB | 1 |
| E5 | COL/STUCK/vB/eA | 3 |
| E5 | KNAP/I | 1 |
| E5 | KNAP/I+R | 1 |
| E5 | KNAP/N | 5 |
| E5 | KNAP/T | 4 |
| E5 | SAT/CONTROL | 3 |
| E5 | SAT/DEAD | 5 |
| E5 | SAT/DEAD-PERM | 5 |
| E5 | SAT/I | 4 |
| E5 | SAT/I+R | 3 |
| E5 | SAT/N | 3 |
| E5 | SAT/P | 4 |
| E5 | SAT/T | 4 |

