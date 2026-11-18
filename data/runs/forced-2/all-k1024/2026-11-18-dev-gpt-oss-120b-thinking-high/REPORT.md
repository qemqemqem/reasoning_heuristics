# Run forced-2/all-k1024/2026-11-18-dev-gpt-oss-120b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `openai/gpt-oss-120b`; returned `openai/gpt-oss-120b`.
- **Provider:** routing `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; served {'DeepInfra': 102}.
- **Condition:** `thinking-high-forced-k1024`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 1.0, 'top_p': 1.0}`; no system prompt.
- **Items:** 115 (data/items/dev/AH_E1_dev_s1.jsonl.gz, data/items/dev/AH_E2_dev_s1.jsonl.gz, data/items/dev/AH_E5_dev_s1.jsonl.gz, data/items/dev/AH_E8_dev_s1.jsonl.gz, data/items/dev/B4C4_E1_dev_s1.jsonl.gz, data/items/dev/B4C4_E2_dev_s1.jsonl.gz, data/items/dev/C_E1_dev_s1.jsonl.gz, data/items/dev/C_E2_dev_s1.jsonl.gz, data/items/dev/C_E3_dev_s1.jsonl.gz, data/items/dev/C_E5_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_content': 0, 'no_room': 0}.
- **Status:** complete; 102 responses, 0 failed calls, 0 from cache.
- **Spend:** $0.0097 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.01, worst case $0.08).
- **Code:** git `2c27e2b27f86f29699b08001a77d758bc9e977f4`; scorer `scorer-1.5.2` at `2c27e2b27f86f29699b08001a77d758bc9e977f4`.

## Forced final answers

The responses of `2026-11-18-dev-gpt-oss-120b-thinking-high` that finished with a reasoning trace and an answer, or stopped at the cap with one, each trace cut to its first 1024 tokens by the model's tokenizer (`o200k_harmony`) and the answer forced there (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096, logit_bias `{'200005': -100, '200006': -100, '200007': -100}`): 115 selected; 0 skipped (no trace); 0 skipped (no content); 0 skipped (no room). Of 102 forced responses, 102 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 100 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`; the source run `{'order': ['dekallm/bf16'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['bf16']}`.
- **Budget:** 13 of the selected traces were within budget and not sent: their natural answers stand. 102 were cut and sent. `budget.jsonl.gz` has each trace's fate and token counts.
- **Raw-prompt check:** the same text gave 93 prompt tokens as a raw prompt and 147 as a chat user message, so the provider passed the raw prompt through.
- **Agreement with the natural answer:** 20 of the 76 forced responses whose source response is `ok` gave its answer (`same_as_natural`: the same answer key, both ok).

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | parse_fail | partial | Correct of ok |
|---|---|---|---|---|---|---|
| A/H | E1 | 15 | 15 | 0 | 0 | 10/15 (67%) |
| A/H | E2 | 15 | 15 | 0 | 0 | 11/15 (73%) |
| A/H | E5 | 20 | 19 | 1 | 0 | 5/19 (26%) |
| B4/C4 | E1 | 2 | 2 | 0 | 0 | 2/2 (100%) |
| C | E1 | 10 | 9 | 0 | 1 | 0/9 (0%) |
| C | E2 | 15 | 15 | 0 | 0 | 2/15 (13%) |
| C | E3 | 5 | 5 | 0 | 0 | 0/5 (0%) |
| C | E5 | 20 | 20 | 0 | 0 | 1/20 (5%) |
| **All** | | **102** | **100** | **1** | **1** | **31/100 (31%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E1 | COL | 5 | 160 | 149 | 0 | 0 | 1,419 | 0 (0%) | 0 (0%) | 0.00008 |
| A/H | E1 | ENT | 5 | 568 | 806 | 0 | 0 | 1,288 | 0 (0%) | 0 (0%) | 0.00018 |
| A/H | E1 | SAT | 5 | 25 | 145 | 0 | 0 | 3,207 | 0 (0%) | 0 (0%) | 0.00014 |
| A/H | E2 | COL | 5 | 214 | 194 | 0 | 0 | 1,482 | 0 (0%) | 0 (0%) | 0.00009 |
| A/H | E2 | ENT | 5 | 200 | 308 | 0 | 0 | 1,286 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E2 | SAT | 5 | 17 | 19 | 0 | 0 | 3,291 | 0 (0%) | 0 (0%) | 0.00012 |
| A/H | E5 | COL | 5 | 198 | 311 | 0 | 0 | 1,327 | 0 (0%) | 0 (0%) | 0.00010 |
| A/H | E5 | ENT | 5 | 41 | 192 | 0 | 0 | 1,268 | 0 (0%) | 0 (0%) | 0.00008 |
| A/H | E5 | KNAP | 5 | 83 | 169 | 0 | 0 | 1,276 | 0 (0%) | 0 (0%) | 0.00007 |
| A/H | E5 | SAT | 5 | 21 | 91 | 0 | 0 | 2,142 | 0 (0%) | 0 (0%) | 0.00009 |
| B4/C4 | E1 | ENT | 2 | 242 | 242 | 0 | 0 | 1,196 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E1 | COL | 5 | 100 | 101 | 0 | 0 | 1,505 | 0 (0%) | 0 (0%) | 0.00007 |
| C | E1 | SAT | 5 | 103 | 106 | 0 | 0 | 2,020 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E2 | COL | 5 | 100 | 100 | 0 | 0 | 1,501 | 0 (0%) | 0 (0%) | 0.00007 |
| C | E2 | KNAP | 5 | 15 | 25 | 0 | 0 | 1,238 | 0 (0%) | 0 (0%) | 0.00005 |
| C | E2 | SAT | 5 | 104 | 101 | 0 | 0 | 2,164 | 0 (0%) | 0 (0%) | 0.00009 |
| C | E3 | COL-I | 1 | 5 | 5 | 0 | 0 | 2,248 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E3 | COL-U | 4 | 406 | 406 | 0 | 0 | 2,448 | 0 (0%) | 0 (0%) | 0.00015 |
| C | E5 | COL | 5 | 148 | 148 | 0 | 0 | 1,565 | 0 (0%) | 0 (0%) | 0.00008 |
| C | E5 | SAT | 5 | 120 | 119 | 0 | 0 | 2,432 | 0 (0%) | 0 (0%) | 0.00011 |
| C | E5 | STATE | 10 | 100 | 72 | 0 | 0 | 1,890 | 0 (0%) | 0 (0%) | 0.00008 |
| **All** | | | **102** | **102** | **179** | **0** | **0** | | **0** | **0** | **0.00009** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 0, mean 92, max 1,704; 24 responses (24%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `order_differs_from_requested` | 3 |
| `text_after_answer` | 2 |
| `latex_unwrapped` | 2 |
| `witness_partial` | 1 |
| `extra_text_in_block` | 1 |

## Responses that are not ok (first 25, for checking the scorer)

| Item | Category | Detail |
|---|---|---|
| `AH-E5-c0cbfc3e6e-ENT-ENT_N` | parse_fail | unrecognised fact(s): ['NOTHING'] |
| `C-E1-15ec0fc41c-SAT_c5-ANS-FREE` | partial | missing 1 variable(s): x52 |

