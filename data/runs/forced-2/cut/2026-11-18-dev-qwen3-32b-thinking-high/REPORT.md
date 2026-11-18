# Run forced-2/cut/2026-11-18-dev-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 26}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 26 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_room': 0}.
- **Status:** complete; 26 responses, 0 failed calls, 26 from cache.
- **Spend:** $0.0000 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.06, worst case $0.08).
- **Code:** git `75fb55fb5ebeafb80486f7fb27a1954c03404897`; scorer `scorer-1.5.2` at `75fb55fb5ebeafb80486f7fb27a1954c03404897`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-32b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 26 selected; 0 skipped (no trace); 0 skipped (no room). Of 26 forced responses, 22 answered and 4 went back to reasoning and stopped at max_tokens again (`truncated` below). 22 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 5 | 5 | 0 | 3/5 (60%) |
| A/H | E2 | 13 | 9 | 4 | 5/9 (56%) |
| A/H | E5 | 1 | 1 | 0 | 0/1 (0%) |
| C | E2 | 2 | 2 | 0 | 1/2 (50%) |
| C | E3 | 4 | 4 | 0 | 1/4 (25%) |
| C | E5 | 1 | 1 | 0 | 0/1 (0%) |
| **All** | | **26** | **22** | **4** | **10/22 (45%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | SAT | 5 | 29 | 32 | 0 | 0 | 35,043 | 0 (0%) | 0 (0%) | 0.00225 |
| A/H | E2 | COL | 1 | 134 | 134 | 0 | 0 | 33,155 | 0 (0%) | 0 (0%) | 0.00215 |
| A/H | E2 | SAT | 12 | 45 | 1,391 | 0 | 0 | 32,945 | 4 (33%) | 0 (0%) | 0.00242 |
| A/H | E5 | SAT | 1 | 29 | 29 | 0 | 0 | 34,279 | 0 (0%) | 0 (0%) | 0.00220 |
| C | E2 | SAT | 2 | 186 | 186 | 0 | 0 | 34,269 | 0 (0%) | 0 (0%) | 0.00223 |
| C | E3 | COL-I | 1 | 2,463 | 2,463 | 0 | 0 | 34,324 | 0 (0%) | 0 (0%) | 0.00275 |
| C | E3 | COL-U | 3 | 472 | 328 | 0 | 0 | 34,590 | 0 (0%) | 0 (0%) | 0.00229 |
| C | E5 | COL | 1 | 172 | 172 | 0 | 0 | 33,437 | 0 (0%) | 0 (0%) | 0.00218 |
| **All** | | | **26** | **50** | **808** | **0** | **0** | | **4** | **0** | **0.00234** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 742, max 4,097; 8 responses (31%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 5 |
| `witness_malformed` | 3 |
| `no_answer_marker` | 1 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/J/g=UNSAT | 1 |
| E2 | SAT/U/g=UNSAT | 3 |

