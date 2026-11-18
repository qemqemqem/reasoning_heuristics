# Run forced-2/done/2026-11-18-dev-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 138}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 69 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 138 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.1041 API-reported over 2 invocation(s) (last cap $0.20; dry-run estimate $0.10, worst case $0.23).
- **Code:** git `75fb55fb5ebeafb80486f7fb27a1954c03404897`; scorer `scorer-1.5.2` at `75fb55fb5ebeafb80486f7fb27a1954c03404897`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-32b-thinking-high` that finished with a reasoning trace and an answer, each whole trace replayed with the answer forced (the f = 1 acceptance test) (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 69 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 138 forced responses, 138 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 136 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 127 of the 136 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 18 | 18 | 0 | 11/18 (61%) |
| A/H | E2 | 18 | 18 | 0 | 16/18 (89%) |
| A/H | E5 | 24 | 24 | 0 | 18/24 (75%) |
| B4/C4 | E1 | 6 | 6 | 0 | 6/6 (100%) |
| B4/C4 | E2 | 6 | 6 | 0 | 6/6 (100%) |
| C | E1 | 12 | 12 | 0 | 8/12 (67%) |
| C | E2 | 18 | 18 | 0 | 10/18 (56%) |
| C | E3 | 6 | 5 | 1 | 3/5 (60%) |
| C | E5 | 30 | 29 | 1 | 16/29 (55%) |
| **All** | | **138** | **136** | **2** | **94/136 (69%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 6 | 11 | 43 | 0 | 0 | 11,638 | 0 (0%) | 0 (0%) | 0.00075 |
| A/H | E1 | ENT | 6 | 7 | 7 | 0 | 0 | 1,468 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E1 | SAT | 6 | 21 | 22 | 0 | 0 | 24,742 | 0 (0%) | 0 (0%) | 0.00159 |
| A/H | E2 | COL | 6 | 193 | 215 | 0 | 0 | 14,842 | 0 (0%) | 0 (0%) | 0.00100 |
| A/H | E2 | ENT | 6 | 7 | 7 | 0 | 0 | 1,532 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E2 | SAT | 6 | 37 | 32 | 0 | 0 | 24,930 | 0 (0%) | 0 (0%) | 0.00160 |
| A/H | E5 | COL | 6 | 72 | 72 | 0 | 0 | 6,863 | 0 (0%) | 0 (0%) | 0.00046 |
| A/H | E5 | ENT | 6 | 32 | 31 | 0 | 0 | 2,282 | 0 (0%) | 0 (0%) | 0.00015 |
| A/H | E5 | KNAP | 6 | 25 | 21 | 0 | 0 | 10,867 | 0 (0%) | 0 (0%) | 0.00070 |
| A/H | E5 | SAT | 6 | 25 | 21 | 0 | 0 | 21,092 | 0 (0%) | 0 (0%) | 0.00135 |
| B4/C4 | E1 | ENT | 6 | 158 | 250 | 0 | 0 | 711 | 0 (0%) | 0 (0%) | 0.00010 |
| B4/C4 | E2 | ENT | 6 | 163 | 169 | 0 | 0 | 510 | 0 (0%) | 0 (0%) | 0.00007 |
| C | E1 | COL | 6 | 116 | 116 | 0 | 0 | 9,861 | 0 (0%) | 0 (0%) | 0.00066 |
| C | E1 | SAT | 6 | 142 | 184 | 0 | 0 | 13,255 | 0 (0%) | 0 (0%) | 0.00089 |
| C | E2 | COL | 6 | 462 | 358 | 0 | 0 | 10,950 | 0 (0%) | 0 (0%) | 0.00078 |
| C | E2 | KNAP | 6 | 544 | 562 | 0 | 0 | 12,643 | 0 (0%) | 0 (0%) | 0.00094 |
| C | E2 | SAT | 6 | 126 | 180 | 0 | 0 | 22,638 | 0 (0%) | 0 (0%) | 0.00149 |
| C | E3 | COL-I | 2 | 283 | 283 | 0 | 0 | 10,880 | 0 (0%) | 0 (0%) | 0.00076 |
| C | E3 | COL-U | 4 | 472 | 472 | 0 | 0 | 12,226 | 0 (0%) | 0 (0%) | 0.00089 |
| C | E5 | COL | 6 | 8 | 41 | 0 | 0 | 18,695 | 0 (0%) | 0 (0%) | 0.00121 |
| C | E5 | ENT | 6 | 406 | 444 | 0 | 0 | 1,432 | 0 (0%) | 0 (0%) | 0.00019 |
| C | E5 | SAT | 6 | 128 | 170 | 0 | 0 | 20,117 | 0 (0%) | 0 (0%) | 0.00133 |
| C | E5 | STATE | 12 | 115 | 208 | 0 | 0 | 7,551 | 0 (0%) | 0 (0%) | 0.00053 |
| **All** | | | **138** | **104** | **164** | **0** | **0** | | **0** | **0** | **0.00075** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 104, max 887; 44 responses (32%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 7 |
| `positional_values` | 5 |
| `no_answer_marker` | 3 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `C-E3-df0043fbca-d=1_BASE_I` | parse_fail | no answer block |
| `C-E5-3d0c055cdd-ENT_MATCHED_ORDER-A` | parse_fail | no answer block |

