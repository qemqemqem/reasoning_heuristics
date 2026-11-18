# Run forced-2/all-k16384/2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 53}.
- **Condition:** `thinking-high-forced-k16384`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 53 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0338 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.03, worst case $0.07).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-120b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 16384 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 53 forced responses, 53 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 53 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 62 of the selected traces were within budget and not sent: their natural answers stand. 53 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 13 of the 27 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | Correct of ok |
|---|---|---|---|---|
| A/H | E1 | 7 | 7 | 5/7 (71%) |
| A/H | E2 | 10 | 10 | 6/10 (60%) |
| A/H | E5 | 7 | 7 | 4/7 (57%) |
| C | E1 | 4 | 4 | 2/4 (50%) |
| C | E2 | 10 | 10 | 6/10 (60%) |
| C | E3 | 4 | 4 | 1/4 (25%) |
| C | E5 | 11 | 11 | 2/11 (18%) |
| **All** | | **53** | **53** | **26/53 (49%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 2 | 88 | 88 | 0 | 0 | 16,752 | 0 (0%) | 0 (0%) | 0.00063 |
| A/H | E1 | SAT | 5 | 20 | 20 | 0 | 0 | 18,567 | 0 (0%) | 0 (0%) | 0.00069 |
| A/H | E2 | COL | 5 | 11 | 77 | 0 | 0 | 16,842 | 0 (0%) | 0 (0%) | 0.00064 |
| A/H | E2 | SAT | 5 | 22 | 21 | 0 | 0 | 18,652 | 0 (0%) | 0 (0%) | 0.00069 |
| A/H | E5 | COL | 1 | 89 | 89 | 0 | 0 | 16,696 | 0 (0%) | 0 (0%) | 0.00063 |
| A/H | E5 | KNAP | 3 | 26 | 43 | 0 | 0 | 16,631 | 0 (0%) | 0 (0%) | 0.00062 |
| A/H | E5 | SAT | 3 | 139 | 101 | 0 | 0 | 17,511 | 0 (0%) | 0 (0%) | 0.00066 |
| C | E1 | SAT | 4 | 92 | 92 | 0 | 0 | 17,378 | 0 (0%) | 0 (0%) | 0.00065 |
| C | E2 | KNAP | 5 | 15 | 16 | 0 | 0 | 16,598 | 0 (0%) | 0 (0%) | 0.00058 |
| C | E2 | SAT | 5 | 91 | 59 | 0 | 0 | 17,524 | 0 (0%) | 0 (0%) | 0.00062 |
| C | E3 | COL-U | 4 | 406 | 405 | 0 | 0 | 17,808 | 0 (0%) | 0 (0%) | 0.00068 |
| C | E5 | COL | 5 | 146 | 119 | 0 | 0 | 16,925 | 0 (0%) | 0 (0%) | 0.00058 |
| C | E5 | SAT | 5 | 113 | 114 | 0 | 0 | 17,792 | 0 (0%) | 0 (0%) | 0.00064 |
| C | E5 | STATE | 1 | 96 | 96 | 0 | 0 | 17,570 | 0 (0%) | 0 (0%) | 0.00049 |
| **All** | | | **53** | **89** | **93** | **0** | **0** | | **0** | **0** | **0.00064** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 6, max 119; 3 responses (6%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `witness_partial` | 2 |

