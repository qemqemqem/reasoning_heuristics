# Forced-answer probes, 2026-11-18

**Question.** Can a thinking response that stopped at its 32,768-token cap get one more chance to answer through OpenRouter? Andrew asked for this on 2026-11-18. It is also the "`</think>` plus answer forcing" that C's design (docs/verticals/C_constructive.md §2.1) gives BE runs.

**Source responses.** Each probe took one response per unit from the dev thinking-high runs (`data/runs/2026-11-18-dev-*-thinking-high`): the first cut at the cap, or, for batch 12's `done` set, the first that finished. Each carries its reasoning in `choices[0].message.reasoning`.

## The main finding: DekaLLM wraps raw prompts

Raw text completions (`POST /api/v1/completions`) are the way to force an answer. We write the model's chat template ourselves, with the trace as its thinking, and close the thinking. That only works if the provider passes the prompt through untouched.

**DekaLLM, gpt-oss's configured pin, does not.** It wraps the prompt as a chat user message (batch 11):
- **Equal token counts.** Its `/completions` and `/chat/completions` calls with the same text report the same prompt_tokens: 160 = 160 for gpt-oss-20b, 206 = 206 for gpt-oss-120b.
- **Fresh reasoning.** The model then reasons afresh ("The user asks…").

So every gpt-oss probe sent to DekaLLM (batches 03, 04, 06, 07, 08, 09) measured a re-prompt with the trace as user text, not a forced continuation. Their answer rates, and the effects of the wrap-up sentence and the answer header, say nothing about forcing. The same holds for force-1's live gpt-oss passes (`data/runs/forced/2026-11-18-dev-gpt-oss-*`, each with an INVALID.md).

**Providers that honour raw prompts** (batch 11): the raw call reports fewer prompt tokens than the chat call, and the model continues the prompt directly, with no new reasoning.

| Model | Provider | Raw / chat prompt_tokens |
|---|---|---|
| Qwen3-32B and Qwen3-14B | DeepInfra fp8 flex (their pin) | 42 / 51 |
| gpt-oss-20b and gpt-oss-120b | DeepInfra bf16 | 93 / 147 |
| gpt-oss-20b and gpt-oss-120b | Parasail fp4 | 93 / 206 |
| gpt-oss-120b | Cerebras fp16 | 93 / 206 (leaves `<|return|>` in the text) |

**With a provider that honours raw prompts, forcing works** (batch 12, gpt-oss-20b on DeepInfra bf16, force-1's prompt):

| Set | Variant | Answered | Renewed reasoning | Notes |
|---|---|---|---|---|
| 8 traces cut at the cap | plain | 8 of 8 | 0 | one wrote 2,325 tokens of visible working first |
| 8 traces cut at the cap | `logit_bias` banning `<|channel|>`, `<|start|>`, `<|end|>` | 8 of 8 | 0 | one unparseable: `<v85>: 1` |
| 8 traces that finished | the whole trace replayed, then the answer forced | 8 of 8 | 0 | **8 of 8 equal the model's own natural answer** |

Qwen3 (batch 05, DeepInfra, its stop sentence before `</think>`) answered 5 of 5. It is the one valid forcing batch among 03–09.

## Parameter support (batch 10, and `GET /api/v1/models/<slug>/endpoints`)

| Provider | logprobs | logit_bias | Raw prompts |
|---|---|---|---|
| DekaLLM, gpt-oss | yes | yes | no |
| DeepInfra, gpt-oss | no | yes | yes |
| Parasail, gpt-oss | yes | yes | yes |
| DeepInfra, Qwen3 | no | yes | yes |

**Notes:**
- **DeepInfra Qwen3 rejects logprobs.** With `require_parameters: true`, a request asking for them fails with "No endpoints found … Filter by Parameters".
- **No Qwen3 provider gives logprobs at a usable context.** Tenstorrent (Qwen3-32B) has logprobs, but its context is 20k.

## Batch 13: an answer-format header (force-2 plus a header)

On a provider that passes raw prompts through, does a header at the start of the forced answer help? `probe_header.py` re-sends committed force-2 requests with the header appended to the prompt: `ANSWER:` for C and B4/C4 items, `{"` for A/H JSON items. It does this for two sets: every non-ok answer of the dev cut passes (provider-empty replies excluded), and 20 finished traces per model as an f = 1 control. In all: 125 calls, $0.095, run on 2026-11-18.

Only calls that got a response are counted below. DeepInfra rate-limited gpt-oss-20b (HTTP 429 after 4 attempts) on 16 of its 23 failure calls and 10 of its 20 controls.

| Model | Failures now ok | Controls ok and the model's own answer |
|---|---|---|
| gpt-oss-20b | 7 of 7 | 10 of 10 |
| gpt-oss-120b | 5 of 14 | 17 of 20: on 3 A/H items it wrote nothing after `{"` |
| Qwen3-32B | 3 of 4 | 18 of 20 (20 ok), as without the header |
| Qwen3-14B | 1 of 3 | 18 of 20 (20 ok), as without the header |

**Conclusion:**
- **The header is mixed, so force-2 stays without one.** It rescues some format failures, but it makes a new failure on gpt-oss-120b's JSON items, an empty answer.
- **Qwen3's runaway digit strings** already start in the required format, so no header can help them.
- **The remaining non-ok forced answers are reported by kind** (declines, partial answers, format slips, runaways) rather than forced into a format.

## All batches

The scripts are the final versions: `probe_chat.py` (01–02), `probe_raw.py` (03–09; its `WRAP` and `PREFIX` switches select 04, 06 and 07), `probe_logit.py` (10), `probe_wrap.py` (11, reconstructed from two inline runs), `probe_force2.py` (12) and `probe_header.py` (13). Every file holds the full request and response of each call.

| File | Endpoint, model, provider | What was sent | Calls | Valid as forcing? |
|---|---|---|---|---|
| 01 | chat, gpt-oss-20b, DekaLLM | knapsack only. `reprompt`: the trace as a visible assistant turn, then "budget used up". `details`: the trace as `reasoning_details` (dropped: prompt_tokens 256). `prefill`: the trace plus "Final answer:" | 3 | no (chat API) |
| 02 | chat, gpt-oss-20b, DekaLLM | `reprompt`, and `short` ("Do not start over…"), on 5 units: 9 of 10 reasoned again until max_tokens | 10 | no (chat API) |
| 03, 04, 06, 07, 08 | raw, gpt-oss-20b, DekaLLM | the harmony prompt, with variants: a wrap-up sentence (04), an answer header (06), both (07), max_tokens 4,096 (08) | 28 | no (wrapped) |
| 05 | raw, Qwen3-32B, DeepInfra | the Qwen3 template with the stop sentence: 5 of 5 answered, 3 correct | 5 | yes |
| 09 | raw, gpt-oss-120b, DekaLLM | the harmony prompt, max_tokens 4,096 | 8 | no (wrapped) |
| 10 | raw, all four models | a one-word question, with and without the end tokens banned, logprobs requested | 6 | parameter check |
| 11 | raw and chat, 9 provider endpoints | the same text both ways: prompt_tokens compared | 18 | wrapping check |
| 12 | raw, gpt-oss-20b, DeepInfra bf16 | force-1's prompt: 8 cut traces plain and banned, 8 finished traces banned | 24 | yes |
| 13 | raw, all four models, DeepInfra | force-2 requests plus an answer header: every non-ok cut answer and 20 controls per model | 125 | yes (see above) |

**Batch sizes.** These are 1–24 calls each, one sample per item: enough to choose a method, not to estimate rates. Acceptance tests at scale come with force-2 (docs/RUNNER.md).

**Cost.** The API reported $0.0668 for batches 01–09 (54 saved calls). The key's usage counter moved $0.0692 over that window; the difference is a first run of `probe_chat.py` that sent 3 calls and then crashed before saving anything. Batches 10–12 cost about $0.03 (key counter). No API key is in any file (byte scan, decompressed).

**Note on 01.** The unit names passed to the script did not match the items' `domain` field ("3-SAT", "colouring (gadget)"), so only knapsack was selected. Batch 02 corrected this.
