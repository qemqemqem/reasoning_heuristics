# Run forced-2/cut/2026-11-18-pc20-qwen3-32b-thinking-high

Descriptive summary, written by `python -m reasoning_heuristics.evals.score`. No mixture fits and no claims about which heuristic a model uses.

- **Model:** requested `qwen/qwen3-32b`; returned `qwen/qwen3-32b`.
- **Provider:** routing `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; served {'DeepInfra': 14}.
- **Condition:** `thinking-high-forced`; max_tokens 4096; reasoning `None`; sampling `{'temperature': 0.6, 'top_p': 0.95, 'top_k': 20}`; no system prompt.
- **Items:** 14 (data/items/pc20/C_E2_dev_s1.jsonl.gz, data/items/pc20/AH_E5_dev_s1.jsonl.gz, data/items/pc20/C_E1_dev_s1.jsonl.gz); skipped {'no_trace': 0, 'no_room': 0}.
- **Status:** complete; 14 responses, 0 failed calls, 14 from cache.
- **Spend:** $0.0000 API-reported over 1 invocation(s) (last cap $0.20; dry-run estimate $0.03, worst case $0.04).
- **Code:** git `75fb55fb5ebeafb80486f7fb27a1954c03404897`; scorer `scorer-1.5.2` at `75fb55fb5ebeafb80486f7fb27a1954c03404897`.

## Forced final answers

The responses of `2026-11-18-pc20-qwen3-32b-thinking-high` that stopped at the cap with a reasoning trace, replayed with the thinking closed (template `force-2`, `https://openrouter.ai/api/v1/completions`, max_tokens 4096): 14 selected; 0 skipped (no trace); 0 skipped (no room). Of 14 forced responses, 14 answered and 0 went back to reasoning and stopped at max_tokens again (`truncated` below). 14 parsed (`ok`); 0 carried reasoning again (`renewed_reasoning`, which should be 0 under force-2).

- **Routing:** forced calls `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`; the source run `{'order': ['deepinfra/fp8/flex'], 'allow_fallbacks': False, 'require_parameters': True, 'quantizations': ['fp8']}`.

These records are a stratum of their own. The source run's records stay as they are (a truncated one stays `truncated`: censored, SCOPE §6 rule 2).

## Response categories

Correct is among `ok` responses only; the other categories are never counted as right or wrong (DESIGN §5 rule 5).

| Vertical | Eval | Responses | ok | Correct of ok |
|---|---|---|---|---|
| A/H | E5 | 5 | 5 | 1/5 (20%) |
| C | E1 | 2 | 2 | 0/2 (0%) |
| C | E2 | 7 | 7 | 0/7 (0%) |
| **All** | | **14** | **14** | **1/14 (7%)** |

## Tokens per response

API-reported. Completion tokens include reasoning tokens. Truncated responses count at the tokens they used.

| Vertical | Eval | Kind | n | Completion median | Completion mean | Reasoning median | Reasoning mean | Prompt mean | Truncated | Reasoning text returned | API $/item |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A/H | E5 | SAT | 5 | 29 | 28 | 0 | 0 | 34,273 | 0 (0%) | 0 (0%) | 0.00220 |
| C | E1 | SAT | 2 | 702 | 702 | 0 | 0 | 33,963 | 0 (0%) | 0 (0%) | 0.00233 |
| C | E2 | SAT | 7 | 313 | 317 | 0 | 0 | 34,296 | 0 (0%) | 0 (0%) | 0.00227 |
| **All** | | | **14** | **298** | **269** | **0** | **0** | | **0** | **0** | **0.00225** |

## Visible text before the answer

`pre_answer_tokens` (proxy tokens of visible content before the final answer block): median 214, mean 218, max 963; 9 responses (64%) have more than 20. In the direct condition these are responses that worked in the visible output and may need flagging or exclusion.

## Parse flags

| Flag | Responses |
|---|---|
| `positional_values` | 1 |

