# Run forced-2/done/2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 136}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 68 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 136 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0732 API-reported over 2 invocation(s) (last cap $0.15; dry-run estimate $0.07, worst case $0.17).
- **Code:** git `75fb55fb5ebeafb80486f7fb27a1954c03404897`; scorer `scorer-1.5.2` at `75fb55fb5ebeafb80486f7fb27a1954c03404897`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-120b-thinking-high` that finished with a reasoning trace and an answer, each whole trace replayed with the answer forced (the f = 1 acceptance test) (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 68 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 136 forced responses, 136 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 136 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 136 of the 136 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | Correct of ok |
|---|---|---|---|---|
| A/H | E1 | 18 | 18 | 18/18 (100%) |
| A/H | E2 | 16 | 16 | 14/16 (88%) |
| A/H | E5 | 24 | 24 | 24/24 (100%) |
| B4/C4 | E1 | 6 | 6 | 6/6 (100%) |
| B4/C4 | E2 | 6 | 6 | 6/6 (100%) |
| C | E1 | 12 | 12 | 12/12 (100%) |
| C | E2 | 18 | 18 | 16/18 (89%) |
| C | E3 | 6 | 6 | 6/6 (100%) |
| C | E5 | 30 | 30 | 30/30 (100%) |
| **All** | | **136** | **136** | **132/136 (97%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 6 | 105 | 88 | 0 | 0 | 18,595 | 0 (0%) | 0 (0%) | 0.00070 |
| A/H | E1 | ENT | 6 | 7 | 7 | 0 | 0 | 3,203 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E1 | SAT | 6 | 19 | 19 | 0 | 0 | 24,689 | 0 (0%) | 0 (0%) | 0.00091 |
| A/H | E2 | COL | 6 | 133 | 152 | 0 | 0 | 23,032 | 0 (0%) | 0 (0%) | 0.00088 |
| A/H | E2 | ENT | 6 | 7 | 7 | 0 | 0 | 2,901 | 0 (0%) | 0 (0%) | 0.00011 |
| A/H | E2 | SAT | 4 | 22 | 22 | 0 | 0 | 31,798 | 0 (0%) | 0 (0%) | 0.00118 |
| A/H | E5 | COL | 6 | 72 | 72 | 0 | 0 | 7,833 | 0 (0%) | 0 (0%) | 0.00030 |
| A/H | E5 | ENT | 6 | 33 | 33 | 0 | 0 | 7,041 | 0 (0%) | 0 (0%) | 0.00026 |
| A/H | E5 | KNAP | 6 | 26 | 35 | 0 | 0 | 16,710 | 0 (0%) | 0 (0%) | 0.00062 |
| A/H | E5 | SAT | 6 | 17 | 17 | 0 | 0 | 15,399 | 0 (0%) | 0 (0%) | 0.00053 |
| B4/C4 | E1 | ENT | 6 | 4 | 106 | 0 | 0 | 1,246 | 0 (0%) | 0 (0%) | 0.00006 |
| B4/C4 | E2 | ENT | 6 | 32 | 52 | 0 | 0 | 519 | 0 (0%) | 0 (0%) | 0.00003 |
| C | E1 | COL | 6 | 98 | 98 | 0 | 0 | 15,133 | 0 (0%) | 0 (0%) | 0.00057 |
| C | E1 | SAT | 6 | 91 | 92 | 0 | 0 | 20,415 | 0 (0%) | 0 (0%) | 0.00069 |
| C | E2 | COL | 6 | 98 | 98 | 0 | 0 | 13,976 | 0 (0%) | 0 (0%) | 0.00048 |
| C | E2 | KNAP | 6 | 14 | 14 | 0 | 0 | 23,053 | 0 (0%) | 0 (0%) | 0.00085 |
| C | E2 | SAT | 6 | 91 | 92 | 0 | 0 | 29,087 | 0 (0%) | 0 (0%) | 0.00109 |
| C | E3 | COL-I | 4 | 4 | 4 | 0 | 0 | 17,148 | 0 (0%) | 0 (0%) | 0.00063 |
| C | E3 | COL-U | 2 | 404 | 404 | 0 | 0 | 24,038 | 0 (0%) | 0 (0%) | 0.00095 |
| C | E5 | COL | 6 | 146 | 146 | 0 | 0 | 25,147 | 0 (0%) | 0 (0%) | 0.00087 |
| C | E5 | ENT | 6 | 4 | 4 | 0 | 0 | 717 | 0 (0%) | 0 (0%) | 0.00002 |
| C | E5 | SAT | 6 | 117 | 117 | 0 | 0 | 26,849 | 0 (0%) | 0 (0%) | 0.00101 |
| C | E5 | STATE | 12 | 93 | 66 | 0 | 0 | 8,549 | 0 (0%) | 0 (0%) | 0.00028 |
| **All** | | | **136** | **33** | **68** | **0** | **0** | | **0** | **0** | **0.00054** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 6, max 296; 7 responses (5%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 2 |

