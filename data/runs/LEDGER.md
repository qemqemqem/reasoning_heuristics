# Inference ledger

One row per live run or probe batch. Costs are API-reported (`usage.cost`, summed); dry runs cost nothing and are not listed.

| Date (UTC) | Run id | Model | Condition | Items | API cost (USD) | Budget tag | Notes |
|---|---|---|---|---|---|---|---|
| 2026-11-18 | probes/2026-11-17 | openai/gpt-oss-20b, openai/gpt-oss-120b, qwen/qwen3-32b, qwen/qwen3-14b, qwen/qwen3-30b-a3b, deepseek/deepseek-r1-0528, qwen/qwen3-235b-a22b-thinking-2507 | probe | 62 | 0.005539 | runner-agent | provider probes (calls in the Items column) |
| 2026-11-18 | 2026-11-18-smoke-qwen3-32b-direct | qwen/qwen3-32b | direct | 254 | 0.019379 | runner-agent | acceptance run (c) status=complete |
| 2026-11-18 | 2026-11-18-smoke-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high | 254 | 0.494084 | runner-agent | acceptance run (b) status=complete |
| 2026-11-18 | 2026-11-18-smoke-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high | 188 | 0.377519 | runner-agent | acceptance run (a) status=stopped |
| 2026-11-18 | 2026-11-18-smoke-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high | 66 | 0.238390 | runner-agent | acceptance run (a), resumed after IncompleteRead status=complete; Items corrected by hand from 254 to the 66 new responses (this process started before the ledger fix) |
| 2026-11-18 | 2026-11-18-dev-qwen3-32b-direct | qwen/qwen3-32b | direct | 1270 | 0.098578 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-qwen3-14b-direct | qwen/qwen3-14b | direct | 1270 | 0.126604 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-120b-thinking-high | openai/gpt-oss-120b | thinking-high | 49 | 0.182745 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high | 29 | 0.113582 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-20b-thinking-low | openai/gpt-oss-20b | thinking-low | 1270 | 0.171011 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high | 22 | 0.101905 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high | 24 | 0.135034 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-pc20-qwen3-32b-direct | qwen/qwen3-32b | direct | 1380 | 0.070247 | pilot-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc20-gpt-oss-20b-thinking-low | openai/gpt-oss-20b | thinking-low | 1380 | 0.232987 | pilot-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc20-qwen3-14b-direct | qwen/qwen3-14b | direct | 1380 | 0.094906 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc20-gpt-oss-120b-thinking-low | openai/gpt-oss-120b | thinking-low | 1380 | 0.385609 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc40-qwen3-32b-direct | qwen/qwen3-32b | direct | 680 | 0.047409 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc40-qwen3-14b-direct | qwen/qwen3-14b | direct | 680 | 0.066183 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc40-gpt-oss-20b-thinking-low | openai/gpt-oss-20b | thinking-low | 680 | 0.091675 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc40-gpt-oss-120b-thinking-low | openai/gpt-oss-120b | thinking-low | 680 | 0.214093 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc20-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high | 267 | 0.556014 | pilot-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high | 1246 | 2.124990 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high | 1247 | 2.181735 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-120b-thinking-high | openai/gpt-oss-120b | thinking-high | 1221 | 3.136093 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc20-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high | 1113 | 3.007536 | pilot-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high | 1 | 0.004149 | dev-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc40-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high | 680 | 1.682940 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc40-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high | 680 | 1.599790 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-pc20-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high | 1380 | 3.022961 | pilot2-2026-11-18 | status=complete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high | 1136 | 2.669481 | dev-2026-11-18 | status=incomplete |
| 2026-11-18 | 2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high | 105 | 0.383138 | dev-2026-11-18 | status=complete |
| 2026-11-18 | forced/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced | 3 | 0.006672 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 status=stopped |
| 2026-11-18 | forced/2026-11-18-dev-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high-forced | 3 | 0.010783 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 status=stopped |
| 2026-11-18 | forced/2026-11-18-pc20-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced | 14 | 0.031523 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 status=complete |
| 2026-11-18 | forced/2026-11-18-pc20-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high-forced | 21 | 0.069206 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 status=complete |
| 2026-11-18 | forced/2026-11-18-pc40-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced | 14 | 0.029639 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 status=complete |
| 2026-11-18 | forced/2026-11-18-pc40-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high-forced | 21 | 0.069890 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 status=complete |
| 2026-11-18 | forced/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced | 23 | 0.049849 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 (resumed after the context fix) status=complete |
| 2026-11-18 | forced/2026-11-18-dev-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high-forced | 25 | 0.079308 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 (resumed after the context fix) status=complete |
| 2026-11-18 | forced/2026-11-18-dev-gpt-oss-120b-thinking-high | openai/gpt-oss-120b | thinking-high-forced | 284 | 0.352518 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 status=complete |
| 2026-11-18 | forced/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced | 52 | 0.075976 | forced-2026-11-18 | forced final answers, force-1, max_tokens 4096 status=incomplete |
| 2026-11-18 | probes/2026-11-18-forced-answer | openai/gpt-oss-20b, openai/gpt-oss-120b, qwen/qwen3-32b, qwen/qwen3-14b | probe | 101 | 0.090900 | forced-2026-11-18 | forced-answer probes (PROBES.md): batches 01-09 by the key's usage counter, including 3 calls lost to a script crash; 10-12 API-reported |
| 2026-11-18 | forced-2/done/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced | 66 | 0.031073 | forced2-2026-11-18 | force-2 acceptance: f=1, per-unit 3 status=complete |
| 2026-11-18 | forced-2/done/2026-11-18-dev-gpt-oss-120b-thinking-high | openai/gpt-oss-120b | thinking-high-forced | 68 | 0.037649 | forced2-2026-11-18 | force-2 acceptance: f=1, per-unit 3 status=complete |
| 2026-11-18 | forced-2/done/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced | 66 | 0.031090 | forced2-2026-11-18 | force-2 acceptance: repeatability status=complete |
| 2026-11-18 | forced-2/done/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced | 69 | 0.052104 | forced2-2026-11-18 | force-2 acceptance: f=1, per-unit 3 status=complete |
| 2026-11-18 | forced-2/done/2026-11-18-dev-gpt-oss-120b-thinking-high | openai/gpt-oss-120b | thinking-high-forced | 68 | 0.035532 | forced2-2026-11-18 | force-2 acceptance: repeatability status=complete |
| 2026-11-18 | forced-2/done/2026-11-18-dev-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high-forced | 69 | 0.074725 | forced2-2026-11-18 | force-2 acceptance: f=1, per-unit 3 status=complete |
| 2026-11-18 | forced-2/done/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced | 69 | 0.052036 | forced2-2026-11-18 | force-2 acceptance: repeatability status=complete |
| 2026-11-18 | forced-2/done/2026-11-18-dev-qwen3-14b-thinking-high | qwen/qwen3-14b | thinking-high-forced | 69 | 0.074581 | forced2-2026-11-18 | force-2 acceptance: repeatability status=complete |
| 2026-11-18 | forced-2/cut/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced | 462 | 0.479219 | forced2-2026-11-18 | force-2: all cut traces status=complete |
| 2026-11-18 | forced-2/cut/2026-11-18-dev-gpt-oss-120b-thinking-high | openai/gpt-oss-120b | thinking-high-forced | 284 | 0.357814 | forced2-2026-11-18 | force-2: all cut traces status=complete |
| 2026-11-18 | forced-2/cut/2026-11-18-dev-gpt-oss-120b-thinking-high | openai/gpt-oss-120b | thinking-high-forced | 9 | 0.011808 | forced2-2026-11-18 | force-2: resumed after #42 to re-send the 9 provider-empty replies status=complete |
| 2026-11-18 | probes/2026-11-18-forced-answer | openai/gpt-oss-20b, openai/gpt-oss-120b, qwen/qwen3-32b, qwen/qwen3-14b | probe | 125 | 0.094900 | forced2-2026-11-18 | batch 13: answer-format header probe (PROBES.md), API-reported |
| 2026-11-18 | forced-2/all-k1024/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced-k1024 | 101 | 0.026132 | sweep-2026-11-18 | budget sweep, per-unit 5 status=complete |
| 2026-11-18 | forced-2/all-k2048/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced-k2048 | 90 | 0.027019 | sweep-2026-11-18 | budget sweep, per-unit 5 status=complete |
| 2026-11-18 | forced-2/all-k4096/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced-k4096 | 83 | 0.036595 | sweep-2026-11-18 | budget sweep, per-unit 5 status=complete |
| 2026-11-18 | forced-2/all-k1024/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k1024 | 55 | 0.005938 | sweep-2026-11-18 | budget sweep, per-unit 5 status=incomplete |
| 2026-11-18 | forced-2/all-k2048/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k2048 | 0 | 0.000000 | sweep-2026-11-18 | budget sweep, per-unit 5 status=refused: raw-prompt check failed |
| 2026-11-18 | forced-2/all-k8192/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced-k8192 | 70 | 0.046753 | sweep-2026-11-18 | budget sweep, per-unit 5 status=complete |
| 2026-11-18 | forced-2/all-k16384/2026-11-18-dev-qwen3-32b-thinking-high | qwen/qwen3-32b | thinking-high-forced-k16384 | 31 | 0.036697 | sweep-2026-11-18 | budget sweep, per-unit 5 status=complete |
| 2026-11-18 | forced-2/all-k4096/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k4096 | 93 | 0.016313 | sweep-2026-11-18 | budget sweep, per-unit 5 status=complete |
| 2026-11-18 | forced-2/all-k8192/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k8192 | 83 | 0.019247 | sweep-2026-11-18 | budget sweep, per-unit 5 status=complete |
| 2026-11-18 | forced-2/all-k16384/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k16384 | 67 | 0.030393 | sweep-2026-11-18 | budget sweep, per-unit 5 status=complete |
| 2026-11-18 | forced-2/all-k1024/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k1024 | 51 | 0.004802 | sweep-2026-11-18 | budget sweep, per-unit 5 (retry at concurrency 2 after HTTP 429s) status=incomplete |
| 2026-11-18 | forced-2/all-k2048/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k2048 | 100 | 0.011364 | sweep-2026-11-18 | budget sweep, per-unit 5 (retry at concurrency 2 after HTTP 429s) status=incomplete |
| 2026-11-18 | forced-2/all-k1024/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k1024 | 2 | 0.000694 | sweep-2026-11-18 | budget sweep, per-unit 5 (second retry, concurrency 1) status=complete |
| 2026-11-18 | forced-2/all-k2048/2026-11-18-dev-gpt-oss-20b-thinking-high | openai/gpt-oss-20b | thinking-high-forced-k2048 | 1 | 0.000103 | sweep-2026-11-18 | budget sweep, per-unit 5 (second retry, concurrency 1) status=complete |
