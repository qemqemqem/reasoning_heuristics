# Provider probes

Run 2026-11-18T02:18:55Z to 2026-11-18T02:22:48Z. Question: "What is 17 + 25? Reply with just the number." (max_tokens 2048). API-reported spend $0.0055.

Variants: `on` = the model's thinking setting; `off` = reasoning {enabled: false}; `none` = reasoning {effort: none}; `no_think` = no reasoning parameter and " /no_think" appended to the prompt. Thinking off is honoured when the response has no reasoning text, zero reasoning tokens and no <think> block.

## openai/gpt-oss-20b

| Endpoint | Provider | Quantization | Context | Max completion | $/M in | $/M out | reasoning | seed | top_k | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `darkbloom/fp8` | Darkbloom | fp8 | 131072 | 117964 | 0.018 | 0.090 | y | y | y | 0 |
| `akashml/fp4` | AkashML | fp4 | 131072 | 117964 | 0.018 | 0.090 | y | y | y | 0 |
| `deepinfra/bf16/flex` | DeepInfra | bf16 | 131072 | 117964 | 0.024 | 0.112 | y | y | y | -5 |
| `dekallm/bf16` | DekaLLM | bf16 | 131072 | 117964 | 0.029 | 0.140 | y | y | n | 0 |
| `coreweave/fp4` | CoreWeave | fp4 | 131072 | 117964 | 0.030 | 0.130 | y | y | y | 0 |
| `deepinfra/bf16` | DeepInfra | bf16 | 131072 | 117964 | 0.030 | 0.140 | y | y | y | 0 |
| `parasail/fp4` | Parasail | fp4 | 131072 | 117964 | 0.030 | 0.150 | y | y | y | 0 |
| `siliconflow/fp8` | SiliconFlow | fp8 | 131072 | 8192 | 0.040 | 0.180 | y | n | y | -5 |
| `amazon-bedrock/eu-west-1` | Amazon Bedrock | unknown | 131072 | 117964 | 0.070 | 0.150 | y | n | y | 0 |
| `amazon-bedrock` | Amazon Bedrock | unknown | 131072 | 117964 | 0.070 | 0.150 | y | n | y | 0 |
| `groq` | Groq | unknown | 131072 | 65536 | 0.075 | 0.300 | y | y | n | 0 |
| `primeintellect/fp4` | PrimeIntellect | fp4 | 131072 | 32768 | 0.200 | 0.300 | y | y | y | 0 |

| Endpoint | Variant | Served by | Reasoning text | Reasoning tokens | Completion tokens | Content | Off honoured | Cost | Error |
|---|---|---|---|---|---|---|---|---|---|
| `dekallm/bf16` | on | DekaLLM | 150 chars | 47 | 54 | '42' | – | 9.909e-06 |  |
| `dekallm/bf16` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `dekallm/bf16` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `deepinfra/bf16` | on | – | – chars | – | – | '' | – | – | attempt 6: HTTP 429: {"error":{"message":"Provider returned error","code":429,"m |
| `deepinfra/bf16` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `deepinfra/bf16` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `darkbloom/fp8` | on | Darkbloom | 121 chars | 39 | 50 | '42' | – | 5.958e-06 |  |
| `darkbloom/fp8` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `darkbloom/fp8` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `akashml/fp4` | on | AkashML | 128 chars | 0 | 47 | '42' | – | 5.4e-06 |  |
| `akashml/fp4` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `akashml/fp4` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `coreweave/fp4` | on | CoreWeave | 271 chars | 69 | 84 | '42' | – | 1.329e-05 |  |
| `coreweave/fp4` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `coreweave/fp4` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |

## openai/gpt-oss-120b

| Endpoint | Provider | Quantization | Context | Max completion | $/M in | $/M out | reasoning | seed | top_k | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `near-ai/fp4` | Near AI | fp4 | 131072 | 117964 | 0.030 | 0.150 | y | y | y | 0 |
| `venice/int4` | Venice | int4 | 128000 | 32768 | 0.030 | 0.150 | y | n | y | 0 |
| `coreweave/fp4` | CoreWeave | fp4 | 131072 | 117964 | 0.030 | 0.170 | y | y | y | 0 |
| `dekallm/bf16` | DekaLLM | bf16 | 131072 | 117964 | 0.030 | 0.180 | y | y | n | 0 |
| `akashml/fp4` | AkashML | fp4 | 131072 | 117964 | 0.030 | 0.187 | y | y | y | 0 |
| `deepinfra/bf16` | DeepInfra | bf16 | 131072 | 117964 | 0.037 | 0.170 | y | y | y | -5 |
| `crusoe/bf16` | Crusoe | bf16 | 131072 | 117964 | 0.050 | 0.250 | y | y | y | 0 |
| `sail-research/fp4` | Sail Research | fp4 | 131072 | 117964 | 0.060 | 0.400 | y | y | y | 0 |
| `digitalocean` | DigitalOcean | unknown | 128000 | 4096 | 0.060 | 0.420 | y | n | n | 0 |
| `google-vertex/global` | Google | unknown | 131072 | 117964 | 0.090 | 0.360 | y | y | y | 0 |
| `mancer/fp8` | Mancer 2 | fp8 | 131072 | 117964 | 0.095 | 0.375 | y | y | y | 0 |
| `baseten/fp4/us` | BaseTen | fp4 | 128072 | 115264 | 0.100 | 0.500 | y | n | n | 0 |
| `baseten/fp4` | BaseTen | fp4 | 128072 | 115264 | 0.100 | 0.500 | y | n | n | 0 |
| `parasail/fp4` | Parasail | fp4 | 131072 | 117964 | 0.100 | 0.750 | y | y | y | 0 |
| `primeintellect/fp4` | PrimeIntellect | fp4 | 131072 | 65536 | 0.137 | 0.293 | y | y | y | 0 |
| `sambanova` | SambaNova | unknown | 131072 | 117964 | 0.140 | 0.950 | y | n | y | 0 |
| `amazon-bedrock/eu-west-1` | Amazon Bedrock | unknown | 131072 | 117964 | 0.150 | 0.600 | y | n | y | 0 |
| `nebius/fp4` | Nebius | fp4 | 131072 | 117964 | 0.150 | 0.600 | y | y | y | 0 |
| `amazon-bedrock` | Amazon Bedrock | unknown | 131072 | 117964 | 0.150 | 0.600 | y | n | y | 0 |
| `siliconflow/fp8` | SiliconFlow | fp8 | 131072 | 8192 | 0.150 | 0.600 | y | n | y | 0 |
| `together` | Together | unknown | 131072 | 117964 | 0.150 | 0.600 | y | n | y | 0 |
| `groq` | Groq | unknown | 131072 | 65536 | 0.150 | 0.600 | y | y | n | 0 |
| `parasail/fast` | Parasail | fp4 | 131072 | 117964 | 0.150 | 0.750 | y | y | y | 0 |
| `cerebras/fp16` | Cerebras | fp16 | 131072 | 40960 | 0.350 | 0.750 | y | y | n | 0 |

| Endpoint | Variant | Served by | Reasoning text | Reasoning tokens | Completion tokens | Content | Off honoured | Cost | Error |
|---|---|---|---|---|---|---|---|---|---|
| `dekallm/bf16` | on | DekaLLM | 250 chars | 60 | 71 | '42' | – | 1.521e-05 |  |
| `dekallm/bf16` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `dekallm/bf16` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `crusoe/bf16` | on | Crusoe | 115 chars | 33 | 44 | '42' | – | 1.505e-05 |  |
| `crusoe/bf16` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `crusoe/bf16` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `cerebras/fp16` | on | Cerebras | 118 chars | 34 | 45 | '42' | – | 6.21e-05 |  |
| `cerebras/fp16` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `cerebras/fp16` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `mancer/fp8` | on | Mancer 2 | 97 chars | 25 | 39 | '42' | – | 2e-05 |  |
| `mancer/fp8` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `mancer/fp8` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `near-ai/fp4` | on | Near AI | 154 chars | 44 | 55 | '42' | – | 1.02e-05 |  |
| `near-ai/fp4` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `near-ai/fp4` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |

## qwen/qwen3-32b

| Endpoint | Provider | Quantization | Context | Max completion | $/M in | $/M out | reasoning | seed | top_k | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `deepinfra/fp8/flex` | DeepInfra | fp8 | 40960 | 36864 | 0.064 | 0.224 | y | y | y | 0 |
| `deepinfra/fp8` | DeepInfra | fp8 | 40960 | 16384 | 0.080 | 0.280 | y | y | y | 0 |
| `deepinfra/fp8/priority` | DeepInfra | fp8 | 40960 | 36864 | 0.120 | 0.420 | y | y | y | 0 |
| `tenstorrent/fp8` | Tenstorrent | fp8 | 20000 | 16400 | 0.140 | 0.400 | y | y | y | 0 |
| `siliconflow/fp8` | SiliconFlow | fp8 | 131072 | 117964 | 0.140 | 0.570 | y | n | y | 0 |

| Endpoint | Variant | Served by | Reasoning text | Reasoning tokens | Completion tokens | Content | Off honoured | Cost | Error |
|---|---|---|---|---|---|---|---|---|---|
| `deepinfra/fp8/flex` | on | DeepInfra | 574 chars | 144 | 228 | '42' | – | 5.2672e-05 |  |
| `deepinfra/fp8/flex` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 2.464e-06 |  |
| `deepinfra/fp8/flex` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 2.464e-06 |  |
| `deepinfra/fp8/flex` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 3.2e-06 |  |
| `deepinfra/fp8/priority` | on | DeepInfra | 638 chars | 160 | 220 | '42' | – | 9.54e-05 |  |
| `deepinfra/fp8/priority` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 4.62e-06 |  |
| `deepinfra/fp8/priority` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 4.62e-06 |  |
| `deepinfra/fp8/priority` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 6e-06 |  |
| `siliconflow/fp8` | on | SiliconFlow | 748 chars | 290 | 293 | '42' | – | 0.00017037 |  |
| `siliconflow/fp8` | off | SiliconFlow | 0 chars | 0 | 2 | '42' | True | 5.06e-06 |  |
| `siliconflow/fp8` | none | SiliconFlow | 0 chars | 0 | 2 | '42' | True | 5.06e-06 |  |
| `siliconflow/fp8` | no_think | SiliconFlow | 2 chars | 2 | 5 | '42' | False | 6.77e-06 |  |
| `deepinfra/fp8` | on | DeepInfra | 431 chars | 109 | 165 | '42' | – | 4.82e-05 |  |
| `deepinfra/fp8` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 3.08e-06 |  |
| `deepinfra/fp8` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 3.08e-06 |  |
| `deepinfra/fp8` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 4e-06 |  |
| `tenstorrent/fp8` | on | Tenstorrent | 431 chars | 109 | 172 | '42' | – | 7.216e-05 |  |
| `tenstorrent/fp8` | off | Tenstorrent | 0 chars | 0 | 3 | '42' | True | 5.12e-06 |  |
| `tenstorrent/fp8` | none | Tenstorrent | 0 chars | 0 | 3 | '42' | True | 5.12e-06 |  |
| `tenstorrent/fp8` | no_think | Tenstorrent | 2 chars | 1 | 7 | '42' | False | 6.72e-06 |  |

## qwen/qwen3-14b

| Endpoint | Provider | Quantization | Context | Max completion | $/M in | $/M out | reasoning | seed | top_k | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `deepinfra/fp8/flex` | DeepInfra | fp8 | 40960 | 36864 | 0.096 | 0.192 | y | y | y | 0 |
| `nextbit/int4` | NextBit | int4 | 40960 | 36864 | 0.100 | 0.220 | y | y | n | 0 |
| `deepinfra/fp8` | DeepInfra | fp8 | 40960 | 16384 | 0.120 | 0.240 | y | y | y | 0 |
| `deepinfra/fp8/priority` | DeepInfra | fp8 | 40960 | 36864 | 0.180 | 0.360 | y | y | y | 0 |

| Endpoint | Variant | Served by | Reasoning text | Reasoning tokens | Completion tokens | Content | Off honoured | Cost | Error |
|---|---|---|---|---|---|---|---|---|---|
| `deepinfra/fp8/flex` | on | DeepInfra | 793 chars | 199 | 311 | '42' | – | 6.2112e-05 |  |
| `deepinfra/fp8/flex` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 3.264e-06 |  |
| `deepinfra/fp8/flex` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 3.264e-06 |  |
| `deepinfra/fp8/flex` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 3.936e-06 |  |
| `deepinfra/fp8/priority` | on | DeepInfra | 599 chars | 151 | 234 | '42' | – | 8.874e-05 |  |
| `deepinfra/fp8/priority` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 6.12e-06 |  |
| `deepinfra/fp8/priority` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 6.12e-06 |  |
| `deepinfra/fp8/priority` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 7.38e-06 |  |
| `nextbit/int4` | on | NextBit | 523 chars | 132 | 199 | '42' | – | 4.628e-05 |  |
| `nextbit/int4` | off | NextBit | 0 chars | 0 | 3 | '42' | True | 3.46e-06 |  |
| `nextbit/int4` | none | NextBit | 0 chars | 0 | 3 | '42' | True | 3.46e-06 |  |
| `nextbit/int4` | no_think | NextBit | 2 chars | 1 | 6 | '42' | False | 4.22e-06 |  |
| `deepinfra/fp8` | on | DeepInfra | 394 chars | 99 | 144 | '42' | – | 3.756e-05 |  |
| `deepinfra/fp8` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 4.08e-06 |  |
| `deepinfra/fp8` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 4.08e-06 |  |
| `deepinfra/fp8` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 4.92e-06 |  |

## qwen/qwen3-30b-a3b

| Endpoint | Provider | Quantization | Context | Max completion | $/M in | $/M out | reasoning | seed | top_k | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `deepinfra/fp8/flex` | DeepInfra | fp8 | 40960 | 36864 | 0.096 | 0.400 | y | y | y | 0 |
| `deepinfra/fp8` | DeepInfra | fp8 | 40960 | 16384 | 0.120 | 0.500 | y | y | y | 0 |
| `deepinfra/fp8/priority` | DeepInfra | fp8 | 40960 | 36864 | 0.180 | 0.750 | y | y | y | 0 |

| Endpoint | Variant | Served by | Reasoning text | Reasoning tokens | Completion tokens | Content | Off honoured | Cost | Error |
|---|---|---|---|---|---|---|---|---|---|
| `deepinfra/fp8/flex` | on | DeepInfra | 801 chars | 201 | 292 | '42' | – | 0.0001192 |  |
| `deepinfra/fp8/flex` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 3.888e-06 |  |
| `deepinfra/fp8/flex` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 3.888e-06 |  |
| `deepinfra/fp8/flex` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 5.184e-06 |  |
| `deepinfra/fp8/priority` | on | DeepInfra | 429 chars | 108 | 158 | '42' | – | 0.000123 |  |
| `deepinfra/fp8/priority` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 7.29e-06 |  |
| `deepinfra/fp8/priority` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 7.29e-06 |  |
| `deepinfra/fp8/priority` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 9.72e-06 |  |
| `deepinfra/fp8` | on | DeepInfra | 1389 chars | 352 | 512 | '42' | – | 0.000259 |  |
| `deepinfra/fp8` | off | DeepInfra | 0 chars | 0 | 3 | '42' | True | 4.86e-06 |  |
| `deepinfra/fp8` | none | DeepInfra | 0 chars | 0 | 3 | '42' | True | 4.86e-06 |  |
| `deepinfra/fp8` | no_think | DeepInfra | 2 chars | 1 | 6 | '42' | False | 6.48e-06 |  |

## deepseek/deepseek-r1-0528

| Endpoint | Provider | Quantization | Context | Max completion | $/M in | $/M out | reasoning | seed | top_k | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `deepinfra/fp4` | DeepInfra | fp4 | 163840 | 32768 | 0.500 | 2.150 | y | y | y | 0 |
| `siliconflow/fp8` | SiliconFlow | fp8 | 163840 | 147456 | 0.500 | 2.180 | y | n | y | 0 |
| `streamlake` | StreamLake | unknown | 128000 | 32000 | 0.571 | 2.286 | y | n | n | 0 |

| Endpoint | Variant | Served by | Reasoning text | Reasoning tokens | Completion tokens | Content | Off honoured | Cost | Error |
|---|---|---|---|---|---|---|---|---|---|
| `siliconflow/fp8` | on | SiliconFlow | 1793 chars | 575 | 577 | '42' | – | 0.00126736 |  |
| `siliconflow/fp8` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `siliconflow/fp8` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `deepinfra/fp4` | on | DeepInfra | 966 chars | 246 | 326 | '42' | – | 0.0007104 |  |
| `deepinfra/fp4` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `deepinfra/fp4` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `streamlake` | on | StreamLake | 673 chars | 208 | 213 | '42' | – | 0.000497767 |  |
| `streamlake` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `streamlake` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |

## qwen/qwen3-235b-a22b-thinking-2507

| Endpoint | Provider | Quantization | Context | Max completion | $/M in | $/M out | reasoning | seed | top_k | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `venice/fp8` | Venice | fp8 | 128000 | 16384 | 0.450 | 3.500 | y | n | y | 0 |

| Endpoint | Variant | Served by | Reasoning text | Reasoning tokens | Completion tokens | Content | Off honoured | Cost | Error |
|---|---|---|---|---|---|---|---|---|---|
| `venice/fp8` | on | Venice | 1015 chars | 262 | 343 | '42' | – | 0.0012122 |  |
| `venice/fp8` | off | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `venice/fp8` | none | – | – chars | – | – | '' | – | – | HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cann |
| `venice/fp8` | no_think | Venice | 258 chars | 66 | 95 | '42' | False | 0.0003442 |  |

