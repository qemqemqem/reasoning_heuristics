# Run 2026-11-18-smoke-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 254}.
- **Condition:** `thinking-high`; max_tokens 32768; reasoning `{'effort': 'high'}`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 254 (data/items/smoke/AH_E1_smoke_s1.jsonl.gz, data/items/smoke/AH_E2_smoke_s1.jsonl.gz, data/items/smoke/AH_E5_smoke_s1.jsonl.gz, data/items/smoke/AH_E8_smoke_s1.jsonl.gz, data/items/smoke/B4C4_E1_smoke_s1.jsonl.gz, data/items/smoke/B4C4_E2_smoke_s1.jsonl.gz, data/items/smoke/C_E1_smoke_s1.jsonl.gz, data/items/smoke/C_E2_smoke_s1.jsonl.gz, data/items/smoke/C_E3_smoke_s1.jsonl.gz, data/items/smoke/C_E5_smoke_s1.jsonl.gz); skipped {'excluded_eval': 12, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 254 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.6159 API-reported over 2 invocation(s) (last cap $0.82; dry-run estimate $0.27, worst case $1.17).
- **Code:** git `97163b6225b68ac9cede6aa9aa262cc0d22c8b45`; scorer `scorer-1.5.0` at `3e9851d22b27d83be96d36180aa8bb87a94ba6f0`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 14 | 9 | 5 | 9/9 (100%) |
| A/H | E2 | 24 | 13 | 11 | 13/13 (100%) |
| A/H | E5 | 17 | 13 | 4 | 13/13 (100%) |
| B4/C4 | E1 | 28 | 28 | 0 | 28/28 (100%) |
| B4/C4 | E2 | 48 | 48 | 0 | 48/48 (100%) |
| C | E1 | 12 | 11 | 1 | 9/11 (82%) |
| C | E2 | 40 | 13 | 27 | 10/13 (77%) |
| C | E3 | 54 | 18 | 36 | 18/18 (100%) |
| C | E5 | 17 | 12 | 5 | 12/12 (100%) |
| **All** | | **254** | **165** | **89** | **160/165 (97%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 4 | 24,068 | 24,020 | 24,026 | 23,971 | 339 | 2 (50%) | 4 (100%) | 0.00337 |
| A/H | E1 | ENT | 4 | 2,712 | 4,013 | 2,667 | 3,872 | 242 | 0 (0%) | 4 (100%) | 0.00057 |
| A/H | E1 | SAT | 6 | 27,567 | 24,195 | 27,555 | 24,184 | 1,320 | 3 (50%) | 6 (100%) | 0.00343 |
| A/H | E2 | COL | 8 | 31,099 | 27,783 | 31,083 | 27,747 | 482 | 3 (38%) | 8 (100%) | 0.00390 |
| A/H | E2 | ENT | 8 | 4,790 | 4,413 | 4,645 | 4,336 | 284 | 0 (0%) | 8 (100%) | 0.00063 |
| A/H | E2 | SAT | 8 | 32,768 | 32,768 | 32,768 | 32,768 | 2,276 | 8 (100%) | 8 (100%) | 0.00465 |
| A/H | E5 | COL | 4 | 6,245 | 6,484 | 6,169 | 6,413 | 282 | 0 (0%) | 4 (100%) | 0.00092 |
| A/H | E5 | ENT | 4 | 5,502 | 5,616 | 5,484 | 5,593 | 246 | 0 (0%) | 4 (100%) | 0.00079 |
| A/H | E5 | KNAP | 4 | 26,916 | 26,250 | 26,904 | 26,208 | 259 | 2 (50%) | 4 (100%) | 0.00368 |
| A/H | E5 | SAT | 5 | 25,946 | 25,347 | 25,924 | 25,334 | 1,101 | 2 (40%) | 5 (100%) | 0.00358 |
| B4/C4 | E1 | ENT | 28 | 2,378 | 2,621 | 2,254 | 2,481 | 174 | 0 (0%) | 28 (100%) | 0.00037 |
| B4/C4 | E2 | ENT | 48 | 642 | 684 | 614 | 666 | 173 | 0 (0%) | 48 (100%) | 0.00010 |
| C | E1 | COL | 6 | 19,398 | 19,878 | 19,295 | 19,775 | 477 | 0 (0%) | 6 (100%) | 0.00280 |
| C | E1 | SAT | 6 | 22,545 | 23,663 | 22,456 | 23,590 | 999 | 1 (17%) | 6 (100%) | 0.00334 |
| C | E2 | COL | 15 | 24,414 | 23,806 | 24,311 | 23,740 | 482 | 6 (40%) | 15 (100%) | 0.00335 |
| C | E2 | KNAP | 15 | 32,768 | 32,625 | 32,768 | 32,624 | 216 | 14 (93%) | 15 (100%) | 0.00457 |
| C | E2 | SAT | 10 | 32,768 | 30,151 | 32,768 | 30,124 | 1,206 | 7 (70%) | 10 (100%) | 0.00426 |
| C | E3 | COL-I | 18 | 19,622 | 18,660 | 19,613 | 18,650 | 1,226 | 0 (0%) | 18 (100%) | 0.00265 |
| C | E3 | COL-U | 36 | 32,768 | 32,768 | 32,768 | 32,768 | 1,425 | 36 (100%) | 36 (100%) | 0.00463 |
| C | E5 | COL | 5 | 28,327 | 26,630 | 28,176 | 26,540 | 542 | 2 (40%) | 5 (100%) | 0.00374 |
| C | E5 | ENT | 4 | 1,250 | 1,188 | 1,240 | 1,180 | 132 | 0 (0%) | 4 (100%) | 0.00017 |
| C | E5 | SAT | 3 | 32,768 | 32,768 | 32,768 | 32,768 | 1,402 | 3 (100%) | 3 (100%) | 0.00463 |
| C | E5 | STATE | 5 | 7,786 | 7,829 | 7,683 | 7,770 | 914 | 0 (0%) | 5 (100%) | 0.00112 |
| **All** | | | **254** | **17,564** | **17,179** | **17,504** | **17,138** | | **89** | **254** | **0.00242** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 20, max 652; 19 responses (7%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 11 |
| `extra_text_in_block` | 1 |
| `order_differs_from_requested` | 1 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | COL/critical/x | 1 |
| E1 | COL/critical/x-prime | 1 |
| E1 | SAT/c5-ANS-FREE | 1 |
| E1 | SAT/critical/x-prime | 1 |
| E1 | SAT/null/x | 1 |
| E1 | SAT/null/x-prime | 1 |
| E2 | COL/DSATUR-vs-LF/G-ONLY | 1 |
| E2 | COL/FF-vs-DSATUR/BASE | 1 |
| E2 | COL/FF-vs-DSATUR/G-ONLY | 1 |
| E2 | COL/FF-vs-DSATUR/PLACEBO | 1 |
| E2 | COL/FF-vs-LF/D(LF|FF) | 1 |
| E2 | COL/FF-vs-LF/G-ONLY | 1 |
| E2 | COL/J/g=possible | 1 |
| E2 | COL/K/g=impossible | 1 |
| E2 | COL/K/g=possible | 1 |
| E2 | KNAP/PREFIX-vs-RATIO/BASE | 1 |
| E2 | KNAP/PREFIX-vs-RATIO/D(PREFIX|RATIO) | 1 |
| E2 | KNAP/PREFIX-vs-RATIO/D(RATIO|PREFIX) | 1 |
| E2 | KNAP/PREFIX-vs-RATIO/G-ONLY | 1 |
| E2 | KNAP/PREFIX-vs-RATIO/PLACEBO | 1 |
| E2 | KNAP/RATIO-vs-DIFF/BASE | 1 |
| E2 | KNAP/RATIO-vs-DIFF/D(DIFF|RATIO) | 1 |
| E2 | KNAP/RATIO-vs-DIFF/D(RATIO|DIFF) | 1 |
| E2 | KNAP/RATIO-vs-DIFF/G-ONLY | 1 |
| E2 | KNAP/RATIO-vs-DIFF/PLACEBO | 1 |
| E2 | KNAP/RATIO-vs-VALUE/D(RATIO|VALUE) | 1 |
| E2 | KNAP/RATIO-vs-VALUE/D(VALUE|RATIO) | 1 |
| E2 | KNAP/RATIO-vs-VALUE/G-ONLY | 1 |
| E2 | KNAP/RATIO-vs-VALUE/PLACEBO | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/BASE | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/D(GREEDY|POLARITY) | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/D(POLARITY|GREEDY) | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/PLACEBO | 1 |
| E2 | SAT/GREEDY-vs-UC/BASE | 1 |
| E2 | SAT/GREEDY-vs-UC/G-ONLY | 1 |
| E2 | SAT/J/g=SAT | 1 |
| E2 | SAT/J/g=UNSAT | 1 |
| E2 | SAT/K/g=SAT | 1 |
| E2 | SAT/K/g=UNSAT | 1 |
| E2 | SAT/U/g=SAT | 1 |
| E2 | SAT/U/g=UNSAT | 1 |
| E2 | SAT/base/g=SAT | 1 |
| E2 | SAT/base/g=UNSAT | 1 |
| E3 | d=1/BASE/U-LIST | 1 |
| E3 | d=1/BASE/U-REV | 1 |
| E3 | d=1/CRITICAL/U-LIST | 1 |
| E3 | d=1/CRITICAL/U-REV | 1 |
| E3 | d=1/PLACEBO/U-LIST | 1 |
| E3 | d=1/PLACEBO/U-REV | 1 |
| E3 | d=2/BASE/U-LIST | 1 |
| E3 | d=2/BASE/U-REV | 1 |
| E3 | d=2/CRITICAL/U-LIST | 1 |
| E3 | d=2/CRITICAL/U-REV | 1 |
| E3 | d=2/PLACEBO/U-LIST | 1 |
| E3 | d=2/PLACEBO/U-REV | 1 |
| E3 | d=3/BASE/U-LIST | 1 |
| E3 | d=3/BASE/U-REV | 1 |
| E3 | d=3/CRITICAL/U-LIST | 1 |
| E3 | d=3/CRITICAL/U-REV | 1 |
| E3 | d=3/PLACEBO/U-LIST | 1 |
| E3 | d=3/PLACEBO/U-REV | 1 |
| E3 | d=4/BASE/U-LIST | 1 |
| E3 | d=4/BASE/U-REV | 1 |
| E3 | d=4/CRITICAL/U-LIST | 1 |
| E3 | d=4/CRITICAL/U-REV | 1 |
| E3 | d=4/PLACEBO/U-LIST | 1 |
| E3 | d=4/PLACEBO/U-REV | 1 |
| E3 | d=6/BASE/U-LIST | 1 |
| E3 | d=6/BASE/U-REV | 1 |
| E3 | d=6/CRITICAL/U-LIST | 1 |
| E3 | d=6/CRITICAL/U-REV | 1 |
| E3 | d=6/PLACEBO/U-LIST | 1 |
| E3 | d=6/PLACEBO/U-REV | 1 |
| E3 | d=8/BASE/U-LIST | 1 |
| E3 | d=8/BASE/U-REV | 1 |
| E3 | d=8/CRITICAL/U-LIST | 1 |
| E3 | d=8/CRITICAL/U-REV | 1 |
| E3 | d=8/PLACEBO/U-LIST | 1 |
| E3 | d=8/PLACEBO/U-REV | 1 |
| E5 | COL/STUCK/vA/eB | 1 |
| E5 | COL/STUCK/vB/eB | 1 |
| E5 | KNAP/I+R | 1 |
| E5 | KNAP/N | 1 |
| E5 | SAT/CONTROL | 1 |
| E5 | SAT/DEAD | 1 |
| E5 | SAT/DEAD-PERM | 1 |
| E5 | SAT/I | 1 |
| E5 | SAT/P | 1 |

