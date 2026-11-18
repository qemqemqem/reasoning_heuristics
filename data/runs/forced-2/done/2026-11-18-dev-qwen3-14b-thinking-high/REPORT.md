# Run forced-2/done/2026-11-18-dev-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 138}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 69 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 138 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.1493 API-reported over 2 invocation(s) (last cap $0.20; dry-run estimate $0.15, worst case $0.26).
- **Code:** git `75fb55fb5ebeafb80486f7fb27a1954c03404897`; scorer `scorer-1.5.2` at `75fb55fb5ebeafb80486f7fb27a1954c03404897`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-14b-thinking-high` that finished with a reasoning trace and an answer, each whole trace replayed with the answer forced (the f = 1 acceptance test) (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 69 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 138 forced responses, 138 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 136 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 131 of the 136 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 18 | 18 | 0 | 14/18 (78%) |
| A/H | E2 | 18 | 18 | 0 | 10/18 (56%) |
| A/H | E5 | 24 | 22 | 2 | 18/22 (82%) |
| B4/C4 | E1 | 6 | 6 | 0 | 6/6 (100%) |
| B4/C4 | E2 | 6 | 6 | 0 | 6/6 (100%) |
| C | E1 | 12 | 12 | 0 | 12/12 (100%) |
| C | E2 | 18 | 18 | 0 | 6/18 (33%) |
| C | E3 | 6 | 6 | 0 | 6/6 (100%) |
| C | E5 | 30 | 30 | 0 | 18/30 (60%) |
| **All** | | **138** | **136** | **2** | **96/136 (71%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 6 | 11 | 43 | 0 | 0 | 13,919 | 0 (0%) | 0 (0%) | 0.00134 |
| A/H | E1 | ENT | 6 | 7 | 7 | 0 | 0 | 2,275 | 0 (0%) | 0 (0%) | 0.00022 |
| A/H | E1 | SAT | 6 | 13 | 21 | 0 | 0 | 25,404 | 0 (0%) | 0 (0%) | 0.00244 |
| A/H | E2 | COL | 6 | 193 | 174 | 0 | 0 | 6,692 | 0 (0%) | 0 (0%) | 0.00068 |
| A/H | E2 | ENT | 6 | 7 | 7 | 0 | 0 | 1,511 | 0 (0%) | 0 (0%) | 0.00015 |
| A/H | E2 | SAT | 6 | 13 | 13 | 0 | 0 | 29,205 | 0 (0%) | 0 (0%) | 0.00281 |
| A/H | E5 | COL | 6 | 72 | 52 | 0 | 0 | 7,141 | 0 (0%) | 0 (0%) | 0.00070 |
| A/H | E5 | ENT | 6 | 32 | 30 | 0 | 0 | 2,365 | 0 (0%) | 0 (0%) | 0.00023 |
| A/H | E5 | KNAP | 6 | 25 | 21 | 0 | 0 | 11,104 | 0 (0%) | 0 (0%) | 0.00107 |
| A/H | E5 | SAT | 6 | 25 | 25 | 0 | 0 | 10,904 | 0 (0%) | 0 (0%) | 0.00105 |
| B4/C4 | E1 | ENT | 6 | 5 | 5 | 0 | 0 | 665 | 0 (0%) | 0 (0%) | 0.00006 |
| B4/C4 | E2 | ENT | 6 | 5 | 5 | 0 | 0 | 506 | 0 (0%) | 0 (0%) | 0.00005 |
| C | E1 | COL | 6 | 115 | 182 | 0 | 0 | 10,235 | 0 (0%) | 0 (0%) | 0.00102 |
| C | E1 | SAT | 6 | 103 | 97 | 0 | 0 | 15,440 | 0 (0%) | 0 (0%) | 0.00150 |
| C | E2 | COL | 6 | 115 | 260 | 0 | 0 | 8,171 | 0 (0%) | 0 (0%) | 0.00083 |
| C | E2 | KNAP | 6 | 10 | 228 | 0 | 0 | 11,212 | 0 (0%) | 0 (0%) | 0.00112 |
| C | E2 | SAT | 6 | 103 | 71 | 0 | 0 | 19,662 | 0 (0%) | 0 (0%) | 0.00190 |
| C | E3 | COL-I | 2 | 450 | 450 | 0 | 0 | 10,266 | 0 (0%) | 0 (0%) | 0.00107 |
| C | E3 | COL-U | 4 | 472 | 472 | 0 | 0 | 17,868 | 0 (0%) | 0 (0%) | 0.00181 |
| C | E5 | COL | 6 | 45 | 74 | 0 | 0 | 16,711 | 0 (0%) | 0 (0%) | 0.00162 |
| C | E5 | ENT | 6 | 300 | 276 | 0 | 0 | 1,226 | 0 (0%) | 0 (0%) | 0.00017 |
| C | E5 | SAT | 6 | 128 | 87 | 0 | 0 | 23,457 | 0 (0%) | 0 (0%) | 0.00227 |
| C | E5 | STATE | 12 | 103 | 74 | 0 | 0 | 10,720 | 0 (0%) | 0 (0%) | 0.00104 |
| **All** | | | **138** | **26** | **100** | **0** | **0** | | **0** | **0** | **0.00108** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 39, max 639; 15 responses (11%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `no_answer_marker` | 6 |
| `latex_unwrapped` | 3 |
| `extra_text_in_block` | 2 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-c0cbfc3e6e-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['switch is down'] |
| `AH-E5-c0cbfc3e6e-ENT-ENT_I` | parse_fail | unrecognised fact(s): ['switch is down'] |

