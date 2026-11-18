# Run forced/2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DekaLLM': 284}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 284 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0}.
- **Status:** complete; 284 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.3525 API-reported over 1 invocation(s) (last cap $0.65; dry-run estimate $0.29, worst case $0.50).
- **Code:** git `3223682c25e56bc749b4ebed1cf3a1732b022c07`; scorer `scorer-1.5.2` at `7d32556690649dcbcff0cffd5ae6d66f2c8cadda`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-120b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-1`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 284 selected; 0 stopped at the cap without a trace and were skipped. Of 284 forced responses, 205 answered and 63 went back to reasoning and stopped at max_tokens again (`truncated` below).

These records are a stratum of their own. The source run's records stay `truncated` (censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|
| A/H | E1 | 15 | 10 | 0 | 0 | 5 | 4/10 (40%) |
| A/H | E2 | 47 | 38 | 8 | 0 | 1 | 22/38 (58%) |
| A/H | E5 | 17 | 15 | 0 | 0 | 2 | 4/15 (27%) |
| C | E1 | 5 | 5 | 0 | 0 | 0 | 4/5 (80%) |
| C | E2 | 44 | 35 | 0 | 0 | 9 | 15/35 (43%) |
| C | E3 | 143 | 80 | 16 | 2 | 45 | 21/80 (26%) |
| C | E5 | 13 | 12 | 0 | 0 | 1 | 3/12 (25%) |
| **All** | | **284** | **195** | **24** | **2** | **63** | **73/195 (37%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | SAT | 15 | 95 | 1,567 | 0 | 1,493 | 35,223 | 5 (33%) | 7 (47%) | 0.00134 |
| A/H | E2 | COL | 9 | 14 | 111 | 0 | 0 | 33,344 | 0 (0%) | 0 (0%) | 0.00102 |
| A/H | E2 | SAT | 38 | 36 | 163 | 0 | 104 | 35,198 | 1 (3%) | 1 (3%) | 0.00109 |
| A/H | E5 | COL | 1 | 390 | 390 | 0 | 0 | 33,252 | 0 (0%) | 0 (0%) | 0.00107 |
| A/H | E5 | KNAP | 3 | 28 | 52 | 0 | 0 | 33,136 | 0 (0%) | 0 (0%) | 0.00100 |
| A/H | E5 | SAT | 13 | 24 | 676 | 0 | 608 | 34,120 | 2 (15%) | 2 (15%) | 0.00115 |
| C | E1 | COL | 2 | 101 | 101 | 0 | 0 | 33,357 | 0 (0%) | 0 (0%) | 0.00102 |
| C | E1 | SAT | 3 | 99 | 1,238 | 0 | 1,061 | 34,008 | 0 (0%) | 1 (33%) | 0.00124 |
| C | E2 | COL | 1 | 103 | 103 | 0 | 0 | 33,351 | 0 (0%) | 0 (0%) | 0.00102 |
| C | E2 | KNAP | 14 | 18 | 384 | 0 | 305 | 33,092 | 1 (7%) | 3 (21%) | 0.00106 |
| C | E2 | SAT | 29 | 97 | 1,207 | 0 | 1,092 | 34,088 | 8 (28%) | 9 (31%) | 0.00124 |
| C | E3 | COL-U | 143 | 409 | 1,708 | 0 | 1,471 | 34,303 | 45 (31%) | 70 (49%) | 0.00134 |
| C | E5 | COL | 2 | 160 | 160 | 8 | 8 | 33,418 | 0 (0%) | 1 (50%) | 0.00103 |
| C | E5 | SAT | 11 | 120 | 480 | 0 | 360 | 34,281 | 1 (9%) | 1 (9%) | 0.00111 |
| **All** | | | **284** | **407** | **1,177** | **0** | **1,013** | | **63** | **95** | **0.00124** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 11, max 403; 21 responses (7%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `answer_only_in_reasoning` | 16 |
| `witness_partial` | 8 |
| `order_differs_from_requested` | 8 |
| `witness_malformed` | 3 |
| `extra_text_in_block` | 2 |
| `no_answer_marker` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E2-19256cba91-SAT-SAT-SAT_J_g=SAT` | parse_fail | no answer block |
| `AH-E2-1c8b9b665a-SAT-UNSAT-SAT_K_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-1c8b9b665a-SAT-UNSAT-SAT_J_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-adac35d43f-SAT-SAT-SAT_U_g=SAT` | parse_fail | no answer block |
| `AH-E2-30e355f86c-SAT-UNSAT-SAT_base_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-30e355f86c-SAT-UNSAT-SAT_U_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-643ef3947c-SAT-UNSAT-SAT_U_g=UNSAT` | parse_fail | no answer block |
| `AH-E2-beae284e57-SAT-SAT-SAT_K_g=SAT` | parse_fail | no answer block |
| `C-E3-df0043fbca-d=1_CRITICAL_U-LIST` | parse_fail | empty content |
| `C-E3-c9b8388799-d=1_CRITICAL_U-REV` | partial | missing 1 vertex(s): v55 |
| `C-E3-c88de4bdf9-d=1_PLACEBO_U-LIST` | parse_fail | empty content |
| `C-E3-a27fc7978c-d=2_BASE_U-LIST` | parse_fail | empty content |
| `C-E3-d8b624d603-d=2_BASE_U-LIST` | partial | missing 6 vertex(s): v60, v70, v99, v64, v33, v89 |
| `C-E3-d8b624d603-d=2_PLACEBO_U-REV` | parse_fail | empty content |
| `C-E3-fb19e0b10b-d=3_PLACEBO_U-LIST` | parse_fail | empty content |
| `C-E3-3b60d2f9bd-d=3_BASE_U-REV` | parse_fail | empty content |
| `C-E3-725dfed728-d=4_CRITICAL_U-LIST` | parse_fail | empty content |
| `C-E3-725dfed728-d=4_PLACEBO_U-REV` | parse_fail | empty content |
| `C-E3-2944af2c50-d=6_BASE_U-LIST` | parse_fail | empty content |
| `C-E3-44103b792f-d=6_BASE_U-LIST` | parse_fail | empty content |
| `C-E3-dff21f42d6-d=6_BASE_U-LIST` | parse_fail | empty content |
| `C-E3-9a0fe047c8-d=8_BASE_U-REV` | parse_fail | empty content |
| `C-E3-9a0fe047c8-d=8_CRITICAL_U-REV` | parse_fail | empty content |
| `C-E3-d94132c512-d=8_CRITICAL_U-LIST` | parse_fail | empty content |
| `C-E3-9daf13803c-d=8_CRITICAL_U-LIST` | parse_fail | empty content |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E1 | SAT/critical/x | 3 |
| E1 | SAT/critical/x-prime | 1 |
| E1 | SAT/null/x | 1 |
| E2 | KNAP/RATIO-vs-DIFF/PLACEBO | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/D(GREEDY|POLARITY) | 2 |
| E2 | SAT/GREEDY-vs-POLARITY/D(POLARITY|GREEDY) | 2 |
| E2 | SAT/GREEDY-vs-POLARITY/G-ONLY | 1 |
| E2 | SAT/GREEDY-vs-POLARITY/PLACEBO | 1 |
| E2 | SAT/GREEDY-vs-UC/BASE | 1 |
| E2 | SAT/GREEDY-vs-UC/G-ONLY | 1 |
| E2 | SAT/base/g=SAT | 1 |
| E3 | d=1/BASE/U-LIST | 1 |
| E3 | d=1/CRITICAL/U-LIST | 1 |
| E3 | d=1/CRITICAL/U-REV | 1 |
| E3 | d=1/PLACEBO/U-REV | 3 |
| E3 | d=2/BASE/U-REV | 4 |
| E3 | d=2/CRITICAL/U-LIST | 3 |
| E3 | d=2/CRITICAL/U-REV | 1 |
| E3 | d=2/PLACEBO/U-REV | 1 |
| E3 | d=3/BASE/U-LIST | 2 |
| E3 | d=3/BASE/U-REV | 1 |
| E3 | d=3/CRITICAL/U-LIST | 2 |
| E3 | d=3/CRITICAL/U-REV | 3 |
| E3 | d=3/PLACEBO/U-LIST | 1 |
| E3 | d=3/PLACEBO/U-REV | 2 |
| E3 | d=4/BASE/U-REV | 2 |
| E3 | d=4/CRITICAL/U-LIST | 3 |
| E3 | d=4/CRITICAL/U-REV | 1 |
| E3 | d=4/PLACEBO/U-LIST | 1 |
| E3 | d=4/PLACEBO/U-REV | 1 |
| E3 | d=6/BASE/U-REV | 1 |
| E3 | d=6/CRITICAL/U-LIST | 2 |
| E3 | d=6/CRITICAL/U-REV | 2 |
| E3 | d=6/PLACEBO/U-LIST | 1 |
| E3 | d=6/PLACEBO/U-REV | 1 |
| E3 | d=8/BASE/U-LIST | 2 |
| E3 | d=8/BASE/U-REV | 1 |
| E3 | d=8/PLACEBO/U-LIST | 1 |
| E5 | SAT/CONTROL | 1 |
| E5 | SAT/N | 2 |

