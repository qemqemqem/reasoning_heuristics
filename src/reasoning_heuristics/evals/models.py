"""Models, conditions and the exact request each condition sends.

Conditions (decision record docs/decisions/2026-11-17-direct-answer-arm.md):

- **thinking** (primary, SCOPE §1): reasoning on at the given effort (default high), max_tokens
  32,768, the item prompt as the only message, each model's recommended sampling.
- **direct** (secondary): reasoning off, the fixed system instruction `DIRECT_SYSTEM_PROMPT`
  (an experimental factor, recorded in every manifest; DESIGN §5 rule 10), max_tokens 1,024.
  Only models that can turn reasoning off have a direct condition. gpt-oss cannot: its `low`
  effort is a budget arm of the thinking condition, not direct.

Provider pins (`provider`) and the pinned endpoint's prices come from the probes
(`python -m reasoning_heuristics.evals.probe`, results under data/runs/probes/). A live run
refuses an unpinned model unless `--no-pin` is given, because SCOPE §1 requires the provider and
precision to be pinned before any pilot.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

THINKING_MAX_TOKENS = 32768
DIRECT_MAX_TOKENS = 1024
DIRECT_SYSTEM_PROMPT = ("Respond with only the final answer in the requested format. "
                        "Do not explain or show your working.")
# The "budget" variant of the thinking condition (--budget-notice; Andrew's suggestion, 2026-11-18): the model is told its
# token budget, and what happens at the cap (force.py). Appended to the item prompt; {max_tokens} is the condition's.
BUDGET_NOTICE = ("\n\nYou have a budget of {max_tokens:,} tokens for your reasoning and your answer together. If you reach it "
                 "before you have answered, your reasoning will be cut off and you will have to give your final answer straight away.")


@dataclass(frozen=True)
class Pricing:
    prompt: float  # USD per million prompt tokens
    completion: float  # USD per million completion tokens (reasoning included)
    source: str

    def cost(self, prompt_tokens: float, completion_tokens: float) -> float:
        return (prompt_tokens * self.prompt + completion_tokens * self.completion) / 1e6


@dataclass(frozen=True)
class ModelConfig:
    slug: str
    list_price: Pricing  # SCOPE §1 list prices (2026-11-13); used by dry runs
    thinking_sampling: dict[str, Any]
    thinking_reasoning: dict[str, Any]  # effort is filled in per run
    direct_sampling: dict[str, Any] | None = None  # None: the model cannot turn reasoning off
    direct_reasoning: dict[str, Any] | None = None
    direct_prompt_suffix: str = ""  # e.g. " /no_think" if a provider only honours the tag
    provider: dict[str, Any] | None = None  # pinned routing (probes)
    pinned_price: Pricing | None = None  # the pinned endpoint's prices (probes)
    context_length: int | None = None  # the pinned endpoint's context
    max_completion_tokens: int | None = None  # the pinned endpoint's completion limit; a larger max_tokens is refused
    notes: str = ""


GPT_OSS_SAMPLING = {"temperature": 1.0, "top_p": 1.0}  # OpenAI's recommended settings for gpt-oss
QWEN3_THINKING_SAMPLING = {"temperature": 0.6, "top_p": 0.95, "top_k": 20}  # Qwen3 model card, thinking mode
QWEN3_DIRECT_SAMPLING = {"temperature": 0.7, "top_p": 0.8, "top_k": 20}  # Qwen3 model card, non-thinking mode
R1_SAMPLING = {"temperature": 0.6, "top_p": 0.95}  # DeepSeek-R1 model card
SCOPE = "SCOPE §1 list price (OpenRouter, 2026-11-13)"
PROBED = "OpenRouter endpoint listing, 2026-11-17 (data/runs/probes/2026-11-17)"


def pin(tag: str, quantization: str) -> dict[str, Any]:
    """One endpoint, no fallbacks, and every request parameter must be supported by it."""
    return {"order": [tag], "allow_fallbacks": False, "require_parameters": True, "quantizations": [quantization]}


# Pins (data/runs/probes/2026-11-17/PROBES.md). Every probed endpoint returned the reasoning text.
# Full precision is preferred; among equals, the endpoint that reports reasoning tokens, has a
# completion limit of at least 32,768 and costs least.
MODELS: dict[str, ModelConfig] = {
    "openai/gpt-oss-20b": ModelConfig(
        "openai/gpt-oss-20b", Pricing(0.03, 0.13, SCOPE), GPT_OSS_SAMPLING, {"effort": "high"},
        provider=pin("dekallm/bf16", "bf16"), pinned_price=Pricing(0.029, 0.14, PROBED), context_length=131072,
        max_completion_tokens=117964,
        notes="Reasoning cannot be turned off (every endpoint answers HTTP 400 'Reasoning is mandatory' to enabled:false "
              "and effort:none); effort low is a budget arm, not the direct condition. Pinned to DekaLLM bf16: bf16 holds "
              "the released MXFP4 expert weights exactly, and it reports reasoning tokens. Not DeepInfra bf16 (HTTP 429 "
              "rate-limited upstream on all 6 attempts), not AkashML fp4 (reports 0 reasoning tokens alongside reasoning "
              "text), not the fp8 endpoints (a lossy re-quantisation). Fallback if DekaLLM fails: coreweave/fp4."),
    "openai/gpt-oss-120b": ModelConfig(
        "openai/gpt-oss-120b", Pricing(0.15, 0.60, SCOPE), GPT_OSS_SAMPLING, {"effort": "high"},
        provider=pin("dekallm/bf16", "bf16"), pinned_price=Pricing(0.03, 0.18, PROBED), context_length=131072,
        max_completion_tokens=117964,
        notes="Reasoning cannot be turned off. Pinned to DekaLLM bf16, the cheapest bf16 endpoint that answered the probe "
              "(Crusoe bf16 also did, at $0.25/M; DeepInfra bf16 was degraded, status -5)."),
    "qwen/qwen3-14b": ModelConfig(
        "qwen/qwen3-14b", Pricing(0.12, 0.24, SCOPE), QWEN3_THINKING_SAMPLING, {"effort": "high"},
        QWEN3_DIRECT_SAMPLING, {"enabled": False}, provider=pin("deepinfra/fp8/flex", "fp8"),
        pinned_price=Pricing(0.096, 0.192, PROBED), context_length=40960, max_completion_tokens=36864,
        notes="Hybrid thinking checkpoint. No bf16 endpoint exists on OpenRouter (DeepInfra fp8 tiers and NextBit int4), "
              "so fp8 is pinned. deepinfra/fp8 (standard tier) caps completions at 16,384, so the flex tier is pinned. "
              "reasoning {enabled: false} is honoured (0 reasoning tokens); /no_think leaves an empty think block."),
    "qwen/qwen3-32b": ModelConfig(
        "qwen/qwen3-32b", Pricing(0.08, 0.28, SCOPE), QWEN3_THINKING_SAMPLING, {"effort": "high"},
        QWEN3_DIRECT_SAMPLING, {"enabled": False}, provider=pin("deepinfra/fp8/flex", "fp8"),
        pinned_price=Pricing(0.064, 0.224, PROBED), context_length=40960, max_completion_tokens=36864,
        notes="Hybrid thinking checkpoint. Every OpenRouter endpoint is fp8 (DeepInfra tiers, SiliconFlow, Tenstorrent), "
              "so fp8 is pinned; Phase 2 should use the official FP8 checkpoint or say how bf16 differs. deepinfra/fp8 "
              "(standard) caps completions at 16,384 and Tenstorrent's context is 20,000, so the flex tier is pinned "
              "(36,864 completion tokens, 40,960 context, cheapest). reasoning {enabled: false} and {effort: none} are "
              "honoured (0 reasoning tokens) on every endpoint; /no_think leaves an empty think block (1 token)."),
    "qwen/qwen3-30b-a3b": ModelConfig(
        "qwen/qwen3-30b-a3b", Pricing(0.12, 0.50, SCOPE), QWEN3_THINKING_SAMPLING, {"effort": "high"},
        QWEN3_DIRECT_SAMPLING, {"enabled": False}, provider=pin("deepinfra/fp8/flex", "fp8"),
        pinned_price=Pricing(0.096, 0.40, PROBED), context_length=40960, max_completion_tokens=36864,
        notes="Hybrid thinking checkpoint (MoE). DeepInfra fp8 is the only provider; flex tier for the 32k budget."),
    "deepseek/deepseek-r1-0528": ModelConfig(
        "deepseek/deepseek-r1-0528", Pricing(0.50, 2.15, SCOPE), R1_SAMPLING, {"effort": "high"},
        provider=pin("siliconflow/fp8", "fp8"), pinned_price=Pricing(0.50, 2.18, PROBED), context_length=163840,
        max_completion_tokens=147456,
        notes="Reasoning is mandatory (HTTP 400 to enabled:false). Pinned to SiliconFlow fp8, R1's release precision; "
              "DeepInfra serves fp4 (a re-quantisation). No seed support."),
    "qwen/qwen3-235b-a22b-thinking-2507": ModelConfig(
        "qwen/qwen3-235b-a22b-thinking-2507", Pricing(0.45, 3.50, SCOPE), QWEN3_THINKING_SAMPLING, {"effort": "high"},
        provider=pin("venice/fp8", "fp8"), pinned_price=Pricing(0.45, 3.50, PROBED), context_length=128000,
        max_completion_tokens=16384,
        notes="Thinking-only checkpoint; reasoning is mandatory and /no_think is ignored. Venice fp8 is the only "
              "endpoint and caps completions at 16,384, so the 32k best-effort condition cannot run on OpenRouter today."),
}


def get_model(slug: str) -> ModelConfig:
    if slug not in MODELS:
        raise KeyError(f"unknown model {slug!r}; configured: {sorted(MODELS)}")
    return MODELS[slug]


@dataclass(frozen=True)
class Condition:
    """Everything about a run's requests except the prompt."""

    name: str  # "thinking" | "direct"
    effort: str | None
    max_tokens: int
    system_prompt: str | None
    reasoning: dict[str, Any]
    sampling: dict[str, Any]
    prompt_suffix: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
    variant: str | None = None  # e.g. "budget" (BUDGET_NOTICE); part of the label

    @property
    def label(self) -> str:
        base = f"thinking-{self.effort}" if self.name == "thinking" and self.effort else self.name
        return f"{base}+{self.variant}" if self.variant else base

    def to_json(self) -> dict[str, Any]:
        # "variant" only when set, so the manifests of runs without one (and their resumes) are unchanged
        return {"name": self.name, "label": self.label, "effort": self.effort, "max_tokens": self.max_tokens,
                "system_prompt": self.system_prompt, "reasoning": self.reasoning, "sampling": self.sampling,
                "prompt_suffix": self.prompt_suffix, **({"variant": self.variant} if self.variant else {}), **self.extra}


def condition(cfg: ModelConfig, name: str, effort: str | None = "high", max_tokens: int | None = None,
              budget_notice: bool = False) -> Condition:
    if budget_notice and name != "thinking":
        raise ValueError("the budget notice is a variant of the thinking condition only")
    if name == "thinking":
        reasoning = dict(cfg.thinking_reasoning)
        if "effort" in reasoning and effort:
            reasoning["effort"] = effort
        elif effort and effort != "high":
            raise ValueError(f"{cfg.slug}: reasoning {reasoning} takes no effort level; got {effort!r}")
        cond = Condition("thinking", effort if "effort" in reasoning else None, max_tokens or THINKING_MAX_TOKENS, None,
                         reasoning, dict(cfg.thinking_sampling))
        if budget_notice:
            cond = replace(cond, prompt_suffix=BUDGET_NOTICE.format(max_tokens=cond.max_tokens), variant="budget")
        return cond
    if name == "direct":
        if cfg.direct_reasoning is None:
            raise ValueError(f"{cfg.slug} cannot turn reasoning off, so it has no direct condition ({cfg.notes})")
        return Condition("direct", None, max_tokens or DIRECT_MAX_TOKENS, DIRECT_SYSTEM_PROMPT, dict(cfg.direct_reasoning),
                         dict(cfg.direct_sampling or {}), cfg.direct_prompt_suffix)
    raise ValueError(f"unknown condition {name!r} (thinking | direct)")


def request_body(cfg: ModelConfig, cond: Condition, prompt: str, provider: dict[str, Any] | None,
                 seed: int | None = None) -> dict[str, Any]:
    """The exact chat-completions body for one item (DESIGN §5 rule 10: it is stored verbatim)."""
    messages = []
    if cond.system_prompt:
        messages.append({"role": "system", "content": cond.system_prompt})
    messages.append({"role": "user", "content": prompt + cond.prompt_suffix})
    body: dict[str, Any] = {"model": cfg.slug, "messages": messages, "max_tokens": cond.max_tokens, **cond.sampling,
                            "reasoning": cond.reasoning}
    if seed is not None:
        body["seed"] = seed
    if provider:
        body["provider"] = provider
    return body
