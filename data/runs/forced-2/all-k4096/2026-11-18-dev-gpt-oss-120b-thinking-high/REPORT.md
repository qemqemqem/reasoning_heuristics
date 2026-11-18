# Run forced-2/all-k4096/2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 82}.
- **Condition:** `thinking-high-forced-k4096`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 82 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0167 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.02, worst case $0.07).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-120b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 4096 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 82 forced responses, 82 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 80 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 33 of the selected traces were within budget and not sent: their natural answers stand. 82 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 12 of the 56 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | partial | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 11 | 11 | 0 | 8/11 (73%) |
| A/H | E2 | 10 | 10 | 0 | 6/10 (60%) |
| A/H | E5 | 16 | 15 | 1 | 7/15 (47%) |
| C | E1 | 10 | 10 | 0 | 1/10 (10%) |
| C | E2 | 15 | 15 | 0 | 4/15 (27%) |
| C | E3 | 5 | 4 | 1 | 0/4 (0%) |
| C | E5 | 15 | 15 | 0 | 1/15 (7%) |
| **All** | | **82** | **80** | **2** | **27/80 (34%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 160 | 143 | 0 | 0 | 4,491 | 0 (0%) | 0 (0%) | 0.00019 |
| A/H | E1 | ENT | 1 | 100 | 100 | 0 | 0 | 4,387 | 0 (0%) | 0 (0%) | 0.00018 |
| A/H | E1 | SAT | 5 | 21 | 22 | 0 | 0 | 6,279 | 0 (0%) | 0 (0%) | 0.00023 |
| A/H | E2 | COL | 5 | 219 | 227 | 0 | 0 | 4,554 | 0 (0%) | 0 (0%) | 0.00021 |
| A/H | E2 | SAT | 5 | 21 | 115 | 0 | 0 | 6,364 | 0 (0%) | 0 (0%) | 0.00025 |
| A/H | E5 | COL | 5 | 116 | 243 | 0 | 0 | 4,399 | 0 (0%) | 0 (0%) | 0.00020 |
| A/H | E5 | ENT | 1 | 19 | 19 | 0 | 0 | 4,349 | 0 (0%) | 0 (0%) | 0.00016 |
| A/H | E5 | KNAP | 5 | 26 | 210 | 0 | 0 | 4,348 | 0 (0%) | 0 (0%) | 0.00019 |
| A/H | E5 | SAT | 5 | 109 | 94 | 0 | 0 | 5,214 | 0 (0%) | 0 (0%) | 0.00020 |
| C | E1 | COL | 5 | 100 | 100 | 0 | 0 | 4,577 | 0 (0%) | 0 (0%) | 0.00018 |
| C | E1 | SAT | 5 | 94 | 96 | 0 | 0 | 5,092 | 0 (0%) | 0 (0%) | 0.00020 |
| C | E2 | COL | 5 | 100 | 100 | 0 | 0 | 4,573 | 0 (0%) | 0 (0%) | 0.00018 |
| C | E2 | KNAP | 5 | 15 | 32 | 0 | 0 | 4,310 | 0 (0%) | 0 (0%) | 0.00016 |
| C | E2 | SAT | 5 | 102 | 101 | 0 | 0 | 5,235 | 0 (0%) | 0 (0%) | 0.00021 |
| C | E3 | COL-I | 1 | 5 | 5 | 0 | 0 | 5,320 | 0 (0%) | 0 (0%) | 0.00020 |
| C | E3 | COL-U | 4 | 406 | 412 | 0 | 0 | 5,520 | 0 (0%) | 0 (0%) | 0.00027 |
| C | E5 | COL | 5 | 148 | 97 | 0 | 0 | 4,637 | 0 (0%) | 0 (0%) | 0.00019 |
| C | E5 | SAT | 5 | 122 | 121 | 0 | 0 | 5,504 | 0 (0%) | 0 (0%) | 0.00022 |
| C | E5 | STATE | 5 | 96 | 78 | 0 | 0 | 5,153 | 0 (0%) | 0 (0%) | 0.00020 |
| **All** | | | **82** | **100** | **130** | **0** | **0** | | **0** | **0** | **0.00020** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 30, max 1,022; 8 responses (10%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `text_after_answer` | 4 |
| `witness_partial` | 3 |
| `witness_malformed` | 1 |
| `extra_text_in_block` | 1 |
| `order_differs_from_requested` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-7044bcf4a8-COL-COL_I+R` | partial | missing 1: Gil |
| `C-E3-df0043fbca-d=1_CRITICAL_U-REV` | partial | missing 1 vertex(s): v43 |

