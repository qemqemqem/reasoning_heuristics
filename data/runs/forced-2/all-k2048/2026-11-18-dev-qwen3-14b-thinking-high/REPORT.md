# Run forced-2/all-k2048/2026-11-18-dev-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 92}.
- **Condition:** `thinking-high-forced-k2048`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 92 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0301 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.03, worst case $0.10).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-14b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 2048 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 92 forced responses, 92 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 92 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 23 of the selected traces were within budget and not sent: their natural answers stand. 92 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 23 of the 91 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | Correct of ok |
|---|---|---|---|---|
| A/H | E1 | 13 | 13 | 8/13 (62%) |
| A/H | E2 | 11 | 11 | 7/11 (64%) |
| A/H | E5 | 17 | 17 | 5/17 (29%) |
| B4/C4 | E1 | 1 | 1 | 1/1 (100%) |
| C | E1 | 10 | 10 | 0/10 (0%) |
| C | E2 | 15 | 15 | 2/15 (13%) |
| C | E3 | 5 | 5 | 1/5 (20%) |
| C | E5 | 20 | 20 | 2/20 (10%) |
| **All** | | **92** | **92** | **26/92 (28%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 11 | 11 | 0 | 0 | 2,421 | 0 (0%) | 0 (0%) | 0.00023 |
| A/H | E1 | ENT | 3 | 7 | 7 | 0 | 0 | 2,295 | 0 (0%) | 0 (0%) | 0.00022 |
| A/H | E1 | SAT | 5 | 37 | 36 | 0 | 0 | 4,584 | 0 (0%) | 0 (0%) | 0.00045 |
| A/H | E2 | COL | 5 | 11 | 90 | 0 | 0 | 2,485 | 0 (0%) | 0 (0%) | 0.00026 |
| A/H | E2 | ENT | 1 | 7 | 7 | 0 | 0 | 2,279 | 0 (0%) | 0 (0%) | 0.00022 |
| A/H | E2 | SAT | 5 | 43 | 42 | 0 | 0 | 4,754 | 0 (0%) | 0 (0%) | 0.00046 |
| A/H | E5 | COL | 5 | 72 | 77 | 0 | 0 | 2,320 | 0 (0%) | 0 (0%) | 0.00024 |
| A/H | E5 | ENT | 2 | 30 | 30 | 0 | 0 | 2,257 | 0 (0%) | 0 (0%) | 0.00022 |
| A/H | E5 | KNAP | 5 | 22 | 19 | 0 | 0 | 2,285 | 0 (0%) | 0 (0%) | 0.00022 |
| A/H | E5 | SAT | 5 | 25 | 25 | 0 | 0 | 3,306 | 0 (0%) | 0 (0%) | 0.00032 |
| B4/C4 | E1 | ENT | 1 | 281 | 281 | 0 | 0 | 2,204 | 0 (0%) | 0 (0%) | 0.00027 |
| C | E1 | COL | 5 | 116 | 230 | 0 | 0 | 2,616 | 0 (0%) | 0 (0%) | 0.00030 |
| C | E1 | SAT | 5 | 103 | 99 | 0 | 0 | 3,259 | 0 (0%) | 0 (0%) | 0.00033 |
| C | E2 | COL | 5 | 116 | 332 | 0 | 0 | 2,609 | 0 (0%) | 0 (0%) | 0.00031 |
| C | E2 | KNAP | 5 | 979 | 816 | 0 | 0 | 2,253 | 0 (0%) | 0 (0%) | 0.00037 |
| C | E2 | SAT | 5 | 103 | 99 | 0 | 0 | 3,446 | 0 (0%) | 0 (0%) | 0.00035 |
| C | E3 | COL-I | 1 | 475 | 475 | 0 | 0 | 3,604 | 0 (0%) | 0 (0%) | 0.00044 |
| C | E3 | COL-U | 4 | 473 | 473 | 0 | 0 | 3,870 | 0 (0%) | 0 (0%) | 0.00046 |
| C | E5 | COL | 5 | 172 | 537 | 0 | 0 | 2,709 | 0 (0%) | 0 (0%) | 0.00036 |
| C | E5 | SAT | 5 | 128 | 123 | 0 | 0 | 3,792 | 0 (0%) | 0 (0%) | 0.00039 |
| C | E5 | STATE | 10 | 103 | 99 | 0 | 0 | 3,092 | 0 (0%) | 0 (0%) | 0.00032 |
| **All** | | | **92** | **103** | **178** | **0** | **0** | | **0** | **0** | **0.00033** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 94, max 1,441; 12 responses (13%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 2 |
| `witness_malformed` | 1 |
| `witness_partial` | 1 |
| `extra_text_in_block` | 1 |
| `latex_unwrapped` | 1 |

