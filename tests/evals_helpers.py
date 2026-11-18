"""Shared helpers for the evals tests: load committed items, render a member's answer as a model
response in the item's own answer format, and build fake OpenRouter responses."""

from __future__ import annotations

import gzip
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from reasoning_heuristics.evals.scoring import AnswerFormat, UnsupportedItem, answer_format
from reasoning_heuristics.heuristics.tasks import load_task

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "data" / "items"


@lru_cache(maxsize=None)
def committed_items(tier: str = "smoke") -> tuple[dict[str, Any], ...]:
    out = []
    for f in sorted((ITEMS / tier).glob("*.jsonl.gz")):
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            out += [json.loads(line) for line in fh if line.strip()]
    return tuple(out)


def runnable(items) -> list[dict[str, Any]]:
    out = []
    for it in items:
        try:
            answer_format(it)
        except UnsupportedItem:
            continue
        out.append(it)
    return out


def first_with(fmt_kind: str, tier: str = "smoke", **match) -> dict[str, Any]:
    for it in runnable(committed_items(tier)):
        if answer_format(it).kind == fmt_kind and all(it.get(k) == v for k, v in match.items()):
            return it
    raise LookupError(fmt_kind)


def render(item: dict[str, Any], answer: Any) -> str | None:
    """A member answer written the way the item's prompt asks for it, or None if the format cannot
    express it (set-valued placeholders such as "CHI=4", a bare "SAT" on a witness format)."""
    fmt: AnswerFormat = answer_format(item)
    task = load_task(item["instance"])
    k = fmt.kind
    if k == "json_sat":
        if answer == "UNSAT":
            return '{"satisfiable": false, "assignment": null}'
        if answer == "SAT":
            return '{"satisfiable": true, "assignment": null}' if item["extra"]["channel"] == "decision" else None
        bits = "".join("1" if answer[v] else "0" for v in task.cnf.var_names)
        return json.dumps({"satisfiable": True, "assignment": bits})
    if k == "json_col":
        if answer == "IMPOSSIBLE":
            return '{"possible": false, "rooms": null}'
        if answer == "POSSIBLE":
            return '{"possible": true, "rooms": null}' if item["extra"]["channel"] == "decision" else None
        if not isinstance(answer, dict):
            return None
        return json.dumps({"possible": True, "rooms": {v: answer[v] for v in task.graph.vertices}})
    if k == "json_ent_yn":
        return json.dumps({"follows": answer == "YES"})
    if k == "json_ent_open":
        return json.dumps({"conclusion": "CONTRADICTORY" if answer == "X" else answer})
    if k == "json_knap":
        return json.dumps({"items": answer})
    if k == "ans_col":
        if answer == "IMPOSSIBLE":
            return "ANSWER:\nIMPOSSIBLE" if fmt.allow_impossible else None
        if not isinstance(answer, dict):
            return None
        order = list(task.answer_order or task.graph.vertices)
        return "ANSWER:\n" + "\n".join(f"{v}: {answer[v]}" for v in order)
    if k == "ans_sat":
        if answer == "UNSAT":
            return "ANSWER:\nUNSAT"
        if not isinstance(answer, dict):
            return None
        order = list(task.answer_order or task.cnf.var_names)
        return "ANSWER:\n" + ", ".join(f"{v}={'T' if answer[v] else 'F'}" for v in order)
    if k == "ans_knap":
        return "ANSWER:\n" + ", ".join(sorted(answer)) if isinstance(answer, list) else None
    if k == "ans_single_colour":
        return f"ANSWER:\n{answer[fmt.target]}" if isinstance(answer, dict) else None
    if k == "ans_yn":
        return f"I checked every case.\n\nANSWER: {'YES' if answer == 'YES' else 'NO'}"
    if k == "ans_letter":
        return f"ANSWER: {answer}"
    raise AssertionError(k)


def api_response(content: str | None, *, reasoning: str | None = "thinking...", finish: str = "stop",
                 completion_tokens: int = 1200, reasoning_tokens: int = 1000, prompt_tokens: int = 900,
                 cost: float = 0.0002, model: str = "openai/gpt-oss-20b", provider: str = "TestProvider",
                 gen_id: str = "gen-test") -> dict[str, Any]:
    """An OpenRouter-shaped chat completion."""
    return {
        "id": gen_id, "provider": provider, "model": model, "object": "chat.completion", "created": 1763400000,
        "choices": [{"index": 0, "finish_reason": finish, "native_finish_reason": finish,
                     "message": {"role": "assistant", "content": content, "reasoning": reasoning}}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                  "total_tokens": prompt_tokens + completion_tokens,
                  "completion_tokens_details": {"reasoning_tokens": reasoning_tokens}, "cost": cost},
    }
