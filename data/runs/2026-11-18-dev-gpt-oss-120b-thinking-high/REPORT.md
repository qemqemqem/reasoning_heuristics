# Run 2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 1270}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 1270 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'excluded_eval': 60, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 1270 responses, 0 failed calls, 0 from cache.
- **Spend:** $3.3188 API-reported over 2 invocation(s) (last cap $5.81; dry-run estimate $1.73, worst case $7.52).
- **Code:** git `12095bc719ce00f4d3ff50c8e7f73dc16c37054a`; scorer `scorer-1.5.1` at `34f2a739e3b2b71721f4ec75aa792469f382b395`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 70 | 55 | 15 | 55/55 (100%) |
| A/H | E2 | 120 | 73 | 47 | 69/73 (95%) |
| A/H | E5 | 85 | 68 | 17 | 66/68 (97%) |
| B4/C4 | E1 | 140 | 140 | 0 | 140/140 (100%) |
| B4/C4 | E2 | 240 | 240 | 0 | 240/240 (100%) |
| C | E1 | 60 | 55 | 5 | 54/55 (98%) |
| C | E2 | 200 | 156 | 44 | 149/156 (96%) |
| C | E3 | 270 | 127 | 143 | 124/127 (98%) |
| C | E5 | 85 | 72 | 13 | 72/72 (100%) |
| **All** | | **1270** | **986** | **284** | **969/986 (98%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 20 | 14,114 | 15,606 | 14,090 | 15,720 | 396 | 0 (0%) | 20 (100%) | 0.00282 |
| A/H | E1 | ENT | 20 | 3,147 | 3,900 | 2,959 | 3,589 | 258 | 0 (0%) | 20 (100%) | 0.00071 |
| A/H | E1 | SAT | 30 | 32,116 | 23,854 | 30,664 | 23,111 | 1,860 | 15 (50%) | 30 (100%) | 0.00435 |
| A/H | E2 | COL | 40 | 22,614 | 22,289 | 22,820 | 22,604 | 478 | 9 (22%) | 40 (100%) | 0.00403 |
| A/H | E2 | ENT | 40 | 3,073 | 3,332 | 2,780 | 3,115 | 245 | 0 (0%) | 40 (100%) | 0.00061 |
| A/H | E2 | SAT | 40 | 32,768 | 32,618 | 31,622 | 31,550 | 2,308 | 38 (95%) | 40 (100%) | 0.00594 |
| A/H | E5 | COL | 20 | 5,994 | 8,921 | 5,964 | 8,914 | 311 | 1 (5%) | 20 (100%) | 0.00162 |
| A/H | E5 | ENT | 20 | 4,049 | 4,866 | 3,916 | 4,715 | 253 | 0 (0%) | 20 (100%) | 0.00088 |
| A/H | E5 | KNAP | 20 | 23,760 | 21,675 | 23,864 | 21,704 | 259 | 3 (15%) | 20 (100%) | 0.00391 |
| A/H | E5 | SAT | 25 | 32,768 | 27,430 | 31,569 | 26,649 | 1,219 | 13 (52%) | 25 (100%) | 0.00497 |
| B4/C4 | E1 | ENT | 140 | 1,246 | 1,516 | 1,150 | 1,376 | 177 | 0 (0%) | 140 (100%) | 0.00028 |
| B4/C4 | E2 | ENT | 240 | 550 | 608 | 500 | 534 | 174 | 0 (0%) | 240 (100%) | 0.00011 |
| C | E1 | COL | 30 | 13,024 | 15,190 | 12,998 | 15,151 | 477 | 2 (7%) | 30 (100%) | 0.00275 |
| C | E1 | SAT | 30 | 20,173 | 21,131 | 19,402 | 20,212 | 1,054 | 3 (10%) | 30 (100%) | 0.00384 |
| C | E2 | COL | 75 | 13,045 | 13,436 | 12,994 | 13,374 | 488 | 1 (1%) | 75 (100%) | 0.00243 |
| C | E2 | KNAP | 75 | 23,592 | 24,010 | 23,760 | 24,012 | 216 | 14 (19%) | 75 (100%) | 0.00433 |
| C | E2 | SAT | 50 | 32,768 | 29,223 | 31,212 | 27,944 | 1,214 | 29 (58%) | 50 (100%) | 0.00530 |
| C | E3 | COL-I | 90 | 11,730 | 11,976 | 11,748 | 11,987 | 1,226 | 0 (0%) | 90 (100%) | 0.00219 |
| C | E3 | COL-U | 180 | 32,768 | 30,352 | 32,790 | 30,354 | 1,426 | 143 (79%) | 180 (100%) | 0.00551 |
| C | E5 | COL | 25 | 18,995 | 20,017 | 18,896 | 19,855 | 544 | 2 (8%) | 25 (100%) | 0.00362 |
| C | E5 | ENT | 20 | 729 | 775 | 706 | 754 | 131 | 0 (0%) | 20 (100%) | 0.00014 |
| C | E5 | SAT | 15 | 32,768 | 31,257 | 31,148 | 30,033 | 1,406 | 11 (73%) | 15 (100%) | 0.00567 |
| C | E5 | STATE | 25 | 8,706 | 8,643 | 8,341 | 8,368 | 931 | 0 (0%) | 25 (100%) | 0.00158 |
| **All** | | | **1270** | **11,871** | **14,401** | **11,679** | **14,204** | | **284** | **1270** | **0.00261** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 28, max 667; 226 responses (18%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 78 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | COL/c1-NAT | 1 |
| E1 | COL/c4-ANS-RAND | 1 |
| E1 | SAT/c3-ANS-LABEL | 1 |
| E1 | SAT/c4-ANS-RAND | 1 |
| E1 | SAT/c5-ANS-FREE | 1 |
| E1 | SAT/critical/x | 3 |
| E1 | SAT/critical/x-prime | 5 |
| E1 | SAT/null/x | 4 |
| E1 | SAT/null/x-prime | 3 |
| E2 | COL/DSATUR-vs-LF/G-ONLY | 1 |
| E2 | COL/J/g=possible | 2 |
| E2 | COL/K/g=impossible | 3 |
| E2 | COL/K/g=possible | 1 |
| E2 | COL/U/g=impossible | 1 |
| E2 | COL/base/g=impossible | 2 |
| E2 | KNAP/PREFIX-vs-RATIO/D(PREFIX|RATIO) | 1 |
| E2 | KNAP/RATIO-vs-DIFF/BASE | 2 |
| E2 | KNAP/RATIO-vs-DIFF/D(DIFF|RATIO) | 1 |
| E2 | KNAP/RATIO-vs-DIFF/D(RATIO|DIFF) | 2 |
| E2 | KNAP/RATIO-vs-DIFF/PLACEBO | 2 |
| E2 | KNAP/RATIO-vs-VALUE/BASE | 2 |
| E2 | KNAP/RATIO-vs-VALUE/D(VALUE|RATIO) | 2 |
| E2 | KNAP/RATIO-vs-VALUE/G-ONLY | 1 |
| E2 | KNAP/RATIO-vs-VALUE/PLACEBO | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/BASE | 3 |
| E2 | SAT/GREEDY-vs-POLARITY/D(GREEDY|POLARITY) | 4 |
| E2 | SAT/GREEDY-vs-POLARITY/D(POLARITY|GREEDY) | 3 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 5 |
| E2 | SAT/GREEDY-vs-POLARITY/PLACEBO | 1 |
| E2 | SAT/GREEDY-vs-UC/BASE | 3 |
| E2 | SAT/GREEDY-vs-UC/D(GREEDY|UC) | 2 |
| E2 | SAT/GREEDY-vs-UC/D(UC|GREEDY) | 2 |
| E2 | SAT/GREEDY-vs-UC/G-ONLY | 5 |
| E2 | SAT/GREEDY-vs-UC/PLACEBO | 1 |
| E2 | SAT/J/g=SAT | 5 |
| E2 | SAT/J/g=UNSAT | 5 |
| E2 | SAT/K/g=SAT | 5 |
| E2 | SAT/K/g=UNSAT | 5 |
| E2 | SAT/U/g=SAT | 4 |
| E2 | SAT/U/g=UNSAT | 5 |
| E2 | SAT/base/g=SAT | 4 |
| E2 | SAT/base/g=UNSAT | 5 |
| E3 | d=1/BASE/U-LIST | 4 |
| E3 | d=1/BASE/U-REV | 3 |
| E3 | d=1/CRITICAL/U-LIST | 4 |
| E3 | d=1/CRITICAL/U-REV | 5 |
| E3 | d=1/PLACEBO/U-LIST | 3 |
| E3 | d=1/PLACEBO/U-REV | 5 |
| E3 | d=2/BASE/U-LIST | 4 |
| E3 | d=2/BASE/U-REV | 5 |
| E3 | d=2/CRITICAL/U-LIST | 3 |
| E3 | d=2/CRITICAL/U-REV | 4 |
| E3 | d=2/PLACEBO/U-LIST | 2 |
| E3 | d=2/PLACEBO/U-REV | 2 |
| E3 | d=3/BASE/U-LIST | 3 |
| E3 | d=3/BASE/U-REV | 5 |
| E3 | d=3/CRITICAL/U-LIST | 4 |
| E3 | d=3/CRITICAL/U-REV | 3 |
| E3 | d=3/PLACEBO/U-LIST | 4 |
| E3 | d=3/PLACEBO/U-REV | 5 |
| E3 | d=4/BASE/U-LIST | 5 |
| E3 | d=4/BASE/U-REV | 5 |
| E3 | d=4/CRITICAL/U-LIST | 5 |
| E3 | d=4/CRITICAL/U-REV | 4 |
| E3 | d=4/PLACEBO/U-LIST | 2 |
| E3 | d=4/PLACEBO/U-REV | 4 |
| E3 | d=6/BASE/U-LIST | 5 |
| E3 | d=6/BASE/U-REV | 4 |
| E3 | d=6/CRITICAL/U-LIST | 3 |
| E3 | d=6/CRITICAL/U-REV | 4 |
| E3 | d=6/PLACEBO/U-LIST | 4 |
| E3 | d=6/PLACEBO/U-REV | 4 |
| E3 | d=8/BASE/U-LIST | 4 |
| E3 | d=8/BASE/U-REV | 5 |
| E3 | d=8/CRITICAL/U-LIST | 4 |
| E3 | d=8/CRITICAL/U-REV | 5 |
| E3 | d=8/PLACEBO/U-LIST | 3 |
| E3 | d=8/PLACEBO/U-REV | 5 |
| E5 | COL/CONTROL/vA/eA | 1 |
| E5 | COL/I | 1 |
| E5 | COL/STUCK/vB/eB | 1 |
| E5 | KNAP/I+R | 1 |
| E5 | KNAP/N | 1 |
| E5 | KNAP/T | 1 |
| E5 | SAT/CONTROL | 4 |
| E5 | SAT/DEAD | 3 |
| E5 | SAT/DEAD-PERM | 4 |
| E5 | SAT/I | 2 |
| E5 | SAT/I+R | 1 |
| E5 | SAT/N | 4 |
| E5 | SAT/P | 3 |
| E5 | SAT/T | 3 |

