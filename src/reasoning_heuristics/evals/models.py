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

from dataclasses import dataclass, field
from typing import Any

THINKING_MAX_TOKENS = 32768
DIRECT_MAX_TOKENS = 1024
DIRECT_SYSTEM_PROMPT = ("Respond with only the final answer in the requested format. "
                        "Do not explain or show your working.")


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
    notes: str = ""


GPT_OSS_SAMPLING = {"temperature": 1.0, "top_p": 1.0}  # OpenAI's recommended settings for gpt-oss
QWEN3_THINKING_SAMPLING = {"temperature": 0.6, "top_p": 0.95, "top_k": 20}  # Qwen3 model card, thinking mode
QWEN3_DIRECT_SAMPLING = {"temperature": 0.7, "top_p": 0.8, "top_k": 20}  # Qwen3 model card, non-thinking mode
R1_SAMPLING = {"temperature": 0.6, "top_p": 0.95}  # DeepSeek-R1 model card
SCOPE = "SCOPE §1 list price (OpenRouter, 2026-11-13)"

MODELS: dict[str, ModelConfig] = {
    "openai/gpt-oss-20b": ModelConfig(
        "openai/gpt-oss-20b", Pricing(0.03, 0.13, SCOPE), GPT_OSS_SAMPLING, {"effort": "high"},
        notes="Reasoning cannot be turned off; effort low is a budget arm, not the direct condition."),
    "openai/gpt-oss-120b": ModelConfig(
        "openai/gpt-oss-120b", Pricing(0.15, 0.60, SCOPE), GPT_OSS_SAMPLING, {"effort": "high"},
        notes="Reasoning cannot be turned off; effort low is a budget arm, not the direct condition."),
    "qwen/qwen3-14b": ModelConfig(
        "qwen/qwen3-14b", Pricing(0.12, 0.24, SCOPE), QWEN3_THINKING_SAMPLING, {"effort": "high"},
        QWEN3_DIRECT_SAMPLING, {"enabled": False}, notes="Hybrid thinking checkpoint."),
    "qwen/qwen3-32b": ModelConfig(
        "qwen/qwen3-32b", Pricing(0.08, 0.28, SCOPE), QWEN3_THINKING_SAMPLING, {"effort": "high"},
        QWEN3_DIRECT_SAMPLING, {"enabled": False}, notes="Hybrid thinking checkpoint."),
    "qwen/qwen3-30b-a3b": ModelConfig(
        "qwen/qwen3-30b-a3b", Pricing(0.12, 0.50, SCOPE), QWEN3_THINKING_SAMPLING, {"effort": "high"},
        QWEN3_DIRECT_SAMPLING, {"enabled": False}, notes="Hybrid thinking checkpoint (MoE)."),
    "deepseek/deepseek-r1-0528": ModelConfig(
        "deepseek/deepseek-r1-0528", Pricing(0.50, 2.15, SCOPE), R1_SAMPLING, {"effort": "high"},
        notes="Reasoning is mandatory."),
    "qwen/qwen3-235b-a22b-thinking-2507": ModelConfig(
        "qwen/qwen3-235b-a22b-thinking-2507", Pricing(0.45, 3.50, SCOPE), QWEN3_THINKING_SAMPLING, {"effort": "high"},
        notes="Thinking-only checkpoint; reasoning is mandatory."),
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

    @property
    def label(self) -> str:
        return f"thinking-{self.effort}" if self.name == "thinking" and self.effort else self.name

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name, "label": self.label, "effort": self.effort, "max_tokens": self.max_tokens,
                "system_prompt": self.system_prompt, "reasoning": self.reasoning, "sampling": self.sampling,
                "prompt_suffix": self.prompt_suffix, **self.extra}


def condition(cfg: ModelConfig, name: str, effort: str | None = "high", max_tokens: int | None = None) -> Condition:
    if name == "thinking":
        reasoning = dict(cfg.thinking_reasoning)
        if "effort" in reasoning and effort:
            reasoning["effort"] = effort
        elif effort and effort != "high":
            raise ValueError(f"{cfg.slug}: reasoning {reasoning} takes no effort level; got {effort!r}")
        return Condition("thinking", effort if "effort" in reasoning else None, max_tokens or THINKING_MAX_TOKENS, None,
                         reasoning, dict(cfg.thinking_sampling))
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
