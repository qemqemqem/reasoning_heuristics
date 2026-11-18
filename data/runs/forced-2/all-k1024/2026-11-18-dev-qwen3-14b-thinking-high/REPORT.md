# Run forced-2/all-k1024/2026-11-18-dev-qwen3-14b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-14b`; returned `qwen/qwen3-14b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 104}.
- **Condition:** `thinking-high-forced-k1024`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 104 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0244 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.02, worst case $0.10).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-14b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 1024 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 104 forced responses, 103 answered and 1 went back to reasoning and stopped at max_tokens again (`truncated` below). 103 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 11 of the selected traces were within budget and not sent: their natural answers stand. 104 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 23 of the 102 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | truncated | Correct of ok |
|---|---|---|---|---|---|
| A/H | E1 | 15 | 15 | 0 | 9/15 (60%) |
| A/H | E2 | 15 | 14 | 1 | 9/14 (64%) |
| A/H | E5 | 20 | 20 | 0 | 2/20 (10%) |
| B4/C4 | E1 | 1 | 1 | 0 | 1/1 (100%) |
| C | E1 | 10 | 10 | 0 | 1/10 (10%) |
| C | E2 | 15 | 15 | 0 | 1/15 (7%) |
| C | E3 | 5 | 5 | 0 | 1/5 (20%) |
| C | E5 | 23 | 23 | 0 | 3/23 (13%) |
| **All** | | **104** | **103** | **1** | **27/103 (26%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 11 | 11 | 0 | 0 | 1,397 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E1 | ENT | 5 | 7 | 7 | 0 | 0 | 1,256 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E1 | SAT | 5 | 37 | 36 | 0 | 0 | 3,560 | 0 (0%) | 0 (0%) | 0.00035 |
| A/H | E2 | COL | 5 | 11 | 11 | 0 | 0 | 1,461 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E2 | ENT | 5 | 7 | 7 | 0 | 0 | 1,254 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E2 | SAT | 5 | 40 | 851 | 0 | 0 | 3,730 | 1 (20%) | 0 (0%) | 0.00052 |
| A/H | E5 | COL | 5 | 72 | 60 | 0 | 0 | 1,296 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E5 | ENT | 5 | 16 | 19 | 0 | 0 | 1,236 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E5 | KNAP | 5 | 22 | 20 | 0 | 0 | 1,261 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E5 | SAT | 5 | 25 | 25 | 0 | 0 | 2,282 | 0 (0%) | 0 (0%) | 0.00022 |
| B4/C4 | E1 | ENT | 1 | 384 | 384 | 0 | 0 | 1,181 | 0 (0%) | 0 (0%) | 0.00019 |
| C | E1 | COL | 5 | 203 | 473 | 0 | 0 | 1,591 | 0 (0%) | 0 (0%) | 0.00024 |
| C | E1 | SAT | 5 | 103 | 99 | 0 | 0 | 2,235 | 0 (0%) | 0 (0%) | 0.00023 |
| C | E2 | COL | 5 | 653 | 644 | 0 | 0 | 1,586 | 0 (0%) | 0 (0%) | 0.00028 |
| C | E2 | KNAP | 5 | 927 | 912 | 0 | 0 | 1,229 | 0 (0%) | 0 (0%) | 0.00029 |
| C | E2 | SAT | 5 | 103 | 103 | 0 | 0 | 2,423 | 0 (0%) | 0 (0%) | 0.00025 |
| C | E3 | COL-I | 1 | 2,899 | 2,899 | 0 | 0 | 2,580 | 0 (0%) | 0 (0%) | 0.00080 |
| C | E3 | COL-U | 4 | 473 | 473 | 0 | 0 | 2,846 | 0 (0%) | 0 (0%) | 0.00036 |
| C | E5 | COL | 5 | 737 | 577 | 0 | 0 | 1,684 | 0 (0%) | 0 (0%) | 0.00027 |
| C | E5 | ENT | 3 | 123 | 211 | 0 | 0 | 1,120 | 0 (0%) | 0 (0%) | 0.00015 |
| C | E5 | SAT | 5 | 128 | 118 | 0 | 0 | 2,768 | 0 (0%) | 0 (0%) | 0.00029 |
| C | E5 | STATE | 10 | 110 | 110 | 0 | 0 | 2,068 | 0 (0%) | 0 (0%) | 0.00022 |
| **All** | | | **104** | **103** | **257** | **0** | **0** | | **1** | **0** | **0.00023** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 188, max 4,097; 21 responses (20%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 2 |
| `answer_blocks_disagree` | 1 |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/J/g=SAT | 1 |

