# Run forced-2/all-k1024/2026-11-18-dev-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 101}.
- **Condition:** `thinking-high-forced-k1024`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 101 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0261 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.01, worst case $0.11).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-qwen3-32b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 1024 tokens by the model's tokenizer (`Qwen/Qwen3-32B/tokenizer.json`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 101 forced responses, 99 answered and 2 went back to reasoning and stopped at max_tokens again (`truncated` below). 98 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.
- **Budget:** 14 of the selected traces were within budget and not sent: their natural answers stand. 101 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 63 prompt tokens as a raw prompt and 72 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 18 of the 97 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | truncated | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 14 | 14 | 0 | 0 | 10/14 (71%) |
| A/H | E2 | 14 | 13 | 0 | 1 | 10/13 (77%) |
| A/H | E5 | 20 | 19 | 1 | 0 | 4/19 (21%) |
| B4/C4 | E1 | 1 | 1 | 0 | 0 | 1/1 (100%) |
| C | E1 | 10 | 10 | 0 | 0 | 0/10 (0%) |
| C | E2 | 15 | 15 | 0 | 0 | 0/15 (0%) |
| C | E3 | 5 | 5 | 0 | 0 | 1/5 (20%) |
| C | E5 | 22 | 21 | 0 | 1 | 2/21 (10%) |
| **All** | | **101** | **98** | **1** | **2** | **28/98 (29%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 108 | 88 | 0 | 0 | 1,396 | 0 (0%) | 0 (0%) | 0.00011 |
| A/H | E1 | ENT | 4 | 7 | 7 | 0 | 0 | 1,258 | 0 (0%) | 0 (0%) | 0.00008 |
| A/H | E1 | SAT | 5 | 37 | 36 | 0 | 0 | 3,560 | 0 (0%) | 0 (0%) | 0.00024 |
| A/H | E2 | COL | 5 | 186 | 194 | 0 | 0 | 1,461 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E2 | ENT | 4 | 7 | 7 | 0 | 0 | 1,254 | 0 (0%) | 0 (0%) | 0.00008 |
| A/H | E2 | SAT | 5 | 38 | 846 | 0 | 0 | 3,730 | 1 (20%) | 0 (0%) | 0.00043 |
| A/H | E5 | COL | 5 | 72 | 77 | 0 | 0 | 1,296 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E5 | ENT | 5 | 29 | 111 | 0 | 0 | 1,236 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E5 | KNAP | 5 | 22 | 521 | 0 | 0 | 1,261 | 0 (0%) | 0 (0%) | 0.00020 |
| A/H | E5 | SAT | 5 | 25 | 23 | 0 | 0 | 2,282 | 0 (0%) | 0 (0%) | 0.00015 |
| B4/C4 | E1 | ENT | 1 | 456 | 456 | 0 | 0 | 1,180 | 0 (0%) | 0 (0%) | 0.00018 |
| C | E1 | COL | 5 | 840 | 896 | 0 | 0 | 1,592 | 0 (0%) | 0 (0%) | 0.00030 |
| C | E1 | SAT | 5 | 1,137 | 1,064 | 0 | 0 | 2,235 | 0 (0%) | 0 (0%) | 0.00038 |
| C | E2 | COL | 5 | 642 | 671 | 0 | 0 | 1,586 | 0 (0%) | 0 (0%) | 0.00025 |
| C | E2 | KNAP | 5 | 932 | 1,046 | 0 | 0 | 1,229 | 0 (0%) | 0 (0%) | 0.00031 |
| C | E2 | SAT | 5 | 480 | 1,572 | 0 | 0 | 2,423 | 0 (0%) | 0 (0%) | 0.00051 |
| C | E3 | COL-I | 1 | 3,409 | 3,409 | 0 | 0 | 2,579 | 0 (0%) | 0 (0%) | 0.00093 |
| C | E3 | COL-U | 4 | 536 | 556 | 0 | 0 | 2,846 | 0 (0%) | 0 (0%) | 0.00031 |
| C | E5 | COL | 5 | 171 | 322 | 0 | 0 | 1,684 | 0 (0%) | 0 (0%) | 0.00018 |
| C | E5 | ENT | 2 | 423 | 423 | 0 | 0 | 1,121 | 0 (0%) | 0 (0%) | 0.00017 |
| C | E5 | SAT | 5 | 501 | 577 | 0 | 0 | 2,768 | 0 (0%) | 0 (0%) | 0.00031 |
| C | E5 | STATE | 10 | 600 | 1,319 | 0 | 0 | 2,068 | 1 (10%) | 0 (0%) | 0.00043 |
| **All** | | | **101** | **186** | **598** | **0** | **0** | | **2** | **0** | **0.00026** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 522, max 4,234; 45 responses (45%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `latex_unwrapped` | 4 |
| `extra_text_in_block` | 3 |
| `witness_partial` | 2 |
| `order_differs_from_requested` | 2 |
| `positional_values` | 2 |
| `fenced_answer_no_marker` | 1 |
| `answer_blocks_disagree` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-c0cbfc3e6e-ENT-ENT_T` | parse_fail | unrecognised fact(s): ['NOTHING'] |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/J/g=SAT | 1 |
| E5 | STATE/SAT/s3 | 1 |

