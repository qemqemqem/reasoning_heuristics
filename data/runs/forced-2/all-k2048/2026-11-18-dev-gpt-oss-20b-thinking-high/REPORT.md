# Run forced-2/all-k2048/2026-11-18-dev-gpt-oss-20b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-20b`; returned `openai/gpt-oss-20b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 101}.
- **Condition:** `thinking-high-forced-k2048`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 101 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0115 API-reported over 2 invocation(s) (last cap $0.05; dry-run estimate $0.01, worst case $0.07).
- **Code:** git `95999b544d9e2d01e836b4ec922c091cdbb76b48`; scorer `scorer-1.5.2` at `95999b544d9e2d01e836b4ec922c091cdbb76b48`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-20b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 2048 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 101 forced responses, 99 answered and 2 went back to reasoning and stopped at max_tokens again (`truncated` below). 93 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 14 of the selected traces were within budget and not sent: their natural answers stand. 101 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 15 of the 56 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | declared_impossible | partial | truncated | Correct of ok |
|---|---|---|---|---|---|---|---|---|
| A/H | E1 | 15 | 15 | 0 | 0 | 0 | 0 | 9/15 (60%) |
| A/H | E2 | 15 | 15 | 0 | 0 | 0 | 0 | 8/15 (53%) |
| A/H | E5 | 20 | 16 | 2 | 0 | 1 | 1 | 6/16 (38%) |
| B4/C4 | E1 | 1 | 1 | 0 | 0 | 0 | 0 | 1/1 (100%) |
| C | E1 | 10 | 10 | 0 | 0 | 0 | 0 | 0/10 (0%) |
| C | E2 | 15 | 14 | 0 | 0 | 0 | 1 | 3/14 (21%) |
| C | E3 | 5 | 5 | 0 | 0 | 0 | 0 | 0/5 (0%) |
| C | E5 | 20 | 17 | 2 | 1 | 0 | 0 | 1/17 (6%) |
| **All** | | **101** | **93** | **4** | **1** | **1** | **2** | **28/93 (30%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 280 | 477 | 0 | 0 | 2,443 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E1 | ENT | 5 | 7 | 53 | 0 | 0 | 2,312 | 0 (0%) | 0 (0%) | 0.00008 |
| A/H | E1 | SAT | 5 | 13 | 73 | 0 | 0 | 4,231 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E2 | COL | 5 | 11 | 11 | 0 | 0 | 2,506 | 0 (0%) | 0 (0%) | 0.00008 |
| A/H | E2 | ENT | 5 | 7 | 7 | 0 | 0 | 2,310 | 0 (0%) | 0 (0%) | 0.00007 |
| A/H | E2 | SAT | 5 | 13 | 15 | 0 | 0 | 4,316 | 0 (0%) | 0 (0%) | 0.00013 |
| A/H | E5 | COL | 5 | 11 | 26 | 0 | 0 | 2,351 | 0 (0%) | 0 (0%) | 0.00007 |
| A/H | E5 | ENT | 5 | 9 | 345 | 0 | 0 | 2,292 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E5 | KNAP | 5 | 23 | 42 | 0 | 0 | 2,300 | 0 (0%) | 0 (0%) | 0.00007 |
| A/H | E5 | SAT | 5 | 13 | 830 | 0 | 0 | 3,166 | 1 (20%) | 0 (0%) | 0.00021 |
| B4/C4 | E1 | ENT | 1 | 300 | 300 | 0 | 0 | 2,205 | 0 (0%) | 0 (0%) | 0.00011 |
| C | E1 | COL | 5 | 100 | 121 | 0 | 0 | 2,529 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E1 | SAT | 5 | 83 | 86 | 0 | 0 | 3,044 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E2 | COL | 5 | 181 | 209 | 0 | 0 | 2,525 | 0 (0%) | 0 (0%) | 0.00010 |
| C | E2 | KNAP | 5 | 14 | 16 | 0 | 0 | 2,262 | 0 (0%) | 0 (0%) | 0.00007 |
| C | E2 | SAT | 5 | 7 | 843 | 0 | 0 | 3,188 | 1 (20%) | 0 (0%) | 0.00021 |
| C | E3 | COL-I | 1 | 2 | 2 | 0 | 0 | 3,272 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E3 | COL-U | 4 | 428 | 336 | 0 | 0 | 3,472 | 0 (0%) | 0 (0%) | 0.00014 |
| C | E5 | COL | 5 | 146 | 119 | 0 | 0 | 2,589 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E5 | SAT | 5 | 13 | 114 | 0 | 0 | 3,456 | 0 (0%) | 0 (0%) | 0.00012 |
| C | E5 | STATE | 10 | 90 | 344 | 0 | 0 | 2,914 | 0 (0%) | 0 (0%) | 0.00013 |
| **All** | | | **101** | **14** | **218** | **0** | **0** | | **2** | **0** | **0.00011** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 154, max 4,586; 22 responses (22%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `extra_text_in_block` | 7 |
| `latex_unwrapped` | 4 |
| `order_differs_from_requested` | 3 |
| `no_answer_marker` | 3 |
| `witness_malformed` | 1 |
| `fenced_answer_no_marker` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-19256cba91-SAT-SAT_I+R` | partial | no assignment |
| `AH-E5-c0cbfc3e6e-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['door is closed'] |
| `AH-E5-c0cbfc3e6e-ENT-ENT_I` | parse_fail | no answer block |
| `C-E5-cff1984132-SAT_DEAD-PERM` | declared_impossible | no answer block; Cannot determine |
| `C-E5-c226e60135-SAT_DEAD-PERM` | parse_fail | no answer block |
| `C-E5-4f7ee728ed-STATE_SAT_s1` | parse_fail | variable x17 given two values (False, True) |

## Truncation by cell (censored, SCOPE §6 rule 2)

| Eval | Cell | Truncated |
|---|---|---|
| E2 | SAT/GREEDY-vs-UC/D(GREEDY|UC) | 1 |
| E5 | SAT/N | 1 |

