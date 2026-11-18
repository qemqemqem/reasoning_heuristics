# Run 2026-11-18-smoke-qwen3-32b-direct

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 254}.
- **Condition:** `direct`; max_tokens 1024; reasoning `{'enabled': False}`; sampling `{'temperature': 0.7, 'top_p': 0.8, 'top_k': 20}`; system prompt: "Respond with only the final answer in the requested format. Do not explain or show your working.".
- **Items:** 254 (data/items/smoke/AH_E1_smoke_s1.jsonl.gz, data/items/smoke/AH_E2_smoke_s1.jsonl.gz, data/items/smoke/AH_E5_smoke_s1.jsonl.gz, data/items/smoke/AH_E8_smoke_s1.jsonl.gz, data/items/smoke/B4C4_E1_smoke_s1.jsonl.gz, data/items/smoke/B4C4_E2_smoke_s1.jsonl.gz, data/items/smoke/C_E1_smoke_s1.jsonl.gz, data/items/smoke/C_E2_smoke_s1.jsonl.gz, data/items/smoke/C_E3_smoke_s1.jsonl.gz, data/items/smoke/C_E5_smoke_s1.jsonl.gz); skipped {'excluded_eval': 12, 'unsupported': 0, 'not_included': 0}.
- **Status:** complete; 254 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0194 API-reported over 1 invocation(s) (last cap $0.10; dry-run estimate $0.02, worst case $0.07).
- **Code:** git `950c540656155ed970083b9786dcdaf2b7be6c95`; scorer `scorer-1.5.0` at `3e9851d22b27d83be96d36180aa8bb87a94ba6f0`.

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 14 | 14 | 0 | 0 | 8/14 (57%) |
| A/H | E2 | 24 | 21 | 0 | 3 | 9/21 (43%) |
| A/H | E5 | 17 | 16 | 1 | 0 | 0/16 (0%) |
| B4/C4 | E1 | 28 | 28 | 0 | 0 | 21/28 (75%) |
| B4/C4 | E2 | 48 | 48 | 0 | 0 | 46/48 (96%) |
| C | E1 | 12 | 12 | 0 | 0 | 0/12 (0%) |
| C | E2 | 40 | 40 | 0 | 0 | 1/40 (2%) |
| C | E3 | 54 | 54 | 0 | 0 | 4/54 (7%) |
| C | E5 | 17 | 17 | 0 | 0 | 4/17 (24%) |
| **All** | | **254** | **250** | **1** | **3** | **93/250 (37%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 4 | 57 | 57 | 0 | 0 | 313 | 0 (0%) | 0 (0%) | 0.00003 |
| A/H | E1 | ENT | 4 | 7 | 7 | 0 | 0 | 211 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E1 | SAT | 6 | 29 | 29 | 0 | 0 | 1,489 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E2 | COL | 8 | 194 | 210 | 0 | 0 | 465 | 0 (0%) | 0 (0%) | 0.00008 |
| A/H | E2 | ENT | 8 | 7 | 7 | 0 | 0 | 253 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E2 | SAT | 8 | 38 | 408 | 0 | 0 | 2,752 | 3 (38%) | 0 (0%) | 0.00027 |
| A/H | E5 | COL | 4 | 74 | 58 | 0 | 0 | 260 | 0 (0%) | 0 (0%) | 0.00003 |
| A/H | E5 | ENT | 4 | 19 | 19 | 0 | 0 | 215 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E5 | KNAP | 4 | 18 | 18 | 0 | 0 | 241 | 0 (0%) | 0 (0%) | 0.00002 |
| A/H | E5 | SAT | 5 | 25 | 27 | 0 | 0 | 1,220 | 0 (0%) | 0 (0%) | 0.00008 |
| B4/C4 | E1 | ENT | 28 | 5 | 12 | 0 | 0 | 145 | 0 (0%) | 0 (0%) | 0.00001 |
| B4/C4 | E2 | ENT | 48 | 5 | 5 | 0 | 0 | 144 | 0 (0%) | 0 (0%) | 0.00001 |
| C | E1 | COL | 6 | 116 | 116 | 0 | 0 | 564 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E1 | SAT | 6 | 103 | 71 | 0 | 0 | 1,215 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E2 | COL | 15 | 116 | 116 | 0 | 0 | 570 | 0 (0%) | 0 (0%) | 0.00006 |
| C | E2 | KNAP | 15 | 7 | 8 | 0 | 0 | 208 | 0 (0%) | 0 (0%) | 0.00002 |
| C | E2 | SAT | 10 | 103 | 83 | 0 | 0 | 1,484 | 0 (0%) | 0 (0%) | 0.00011 |
| C | E3 | COL-I | 18 | 6 | 6 | 0 | 0 | 1,559 | 0 (0%) | 0 (0%) | 0.00010 |
| C | E3 | COL-U | 36 | 473 | 473 | 0 | 0 | 1,824 | 0 (0%) | 0 (0%) | 0.00022 |
| C | E5 | COL | 5 | 8 | 8 | 0 | 0 | 663 | 0 (0%) | 0 (0%) | 0.00004 |
| C | E5 | ENT | 4 | 4 | 4 | 0 | 0 | 100 | 0 (0%) | 0 (0%) | 0.00001 |
| C | E5 | SAT | 3 | 128 | 87 | 0 | 0 | 1,738 | 0 (0%) | 0 (0%) | 0.00013 |
| C | E5 | STATE | 5 | 103 | 89 | 0 | 0 | 1,107 | 0 (0%) | 0 (0%) | 0.00009 |
| **All** | | | **254** | **8** | **111** | **0** | **0** | | **3** | **0** | **0.00008** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 13, max 1,025; 4 responses (2%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 4 |
| `no_answer_marker` | 3 |
| `order_differs_from_requested` | 2 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-c67d6cd1c2-SAT-SAT_N` | parse_fail | 24 digits for 12 variables |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/J/g=SAT | 1 |
| E2 | SAT/J/g=UNSAT | 1 |
| E2 | SAT/U/g=UNSAT | 1 |

