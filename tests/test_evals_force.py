"""The forced-answer pass with the HTTP layer mocked: the force-1 prompt, the forcing routes and the raw-prompt
check, force-2's logit_bias, selection (cut and done, per unit, samples), a forced call recorded and scored
from a text-completions response, the cost cap, resumption, the ledger, the dry run, output directories,
force-1 reproduced, and the API key never leaving the environment."""

from __future__ import annotations

import ast
import gzip
import hashlib
import json
import math
from pathlib import Path

import pytest
from evals_helpers import ITEMS, api_response

from reasoning_heuristics.evals import ledger
from reasoning_heuristics.evals.cache import cache_key
from reasoning_heuristics.evals.client import HttpResponse, OpenRouterClient
from reasoning_heuristics.evals.force import (FORCING_ROUTES, GPT_OSS_LOGIT_BIAS, UnsupportedModel, call_max_tokens,
                                              forced_body, forced_prompt, raw_check_prompt, select)
from reasoning_heuristics.evals.force import main as force_main
from reasoning_heuristics.evals.models import get_model
from reasoning_heuristics.evals.run import main as run_main
from reasoning_heuristics.evals.score import main as score_main
from reasoning_heuristics.evals.scoring import ResponseView

REPO = Path(__file__).resolve().parents[1]
SECRET = "sk-or-test-SECRET-do-not-write"
B4E1 = str(ITEMS / "smoke" / "B4C4_E1_smoke_s1.jsonl.gz")
B4E2 = str(ITEMS / "smoke" / "B4C4_E2_smoke_s1.jsonl.gz")
SOURCE = "2026-11-18-dev-test"
GPT_OSS_SYSTEM = ("<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\n\n"
                  "Reasoning: {}\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|>")
QWEN3_STOP = "Considering the limited time by the user, I have to give the solution based on the thinking directly now."
DEEPINFRA_BF16 = {"order": ["deepinfra/bf16"], "allow_fallbacks": False, "require_parameters": True, "quantizations": ["bf16"]}
BAN = {"200005": -100, "200006": -100, "200007": -100}
CHECK_COST = 0.00001  # each of the raw-prompt check's two calls
FORCE_2_FIELDS = {"forced_select", "forced_sample", "source_sample", "natural_response", "natural_max_tokens",
                  "natural_category", "natural_correct", "natural_answer_key", "same_as_natural"}


def completion(text: str, *, reasoning: str | None = None, finish: str = "stop", completion_tokens: int = 20,
               prompt_tokens: int = 33700, cost: float = 0.001, model: str = "openai/gpt-oss-20b",
               provider: str = "FakeProvider", gen_id: str = "gen-forced") -> dict:
    """An OpenRouter-shaped text completion (POST /completions)."""
    return {"id": gen_id, "object": "text_completion", "model": model, "provider": provider,
            "choices": [{"index": 0, "text": text, "reasoning": reasoning, "logprobs": None,
                         "finish_reason": finish, "native_finish_reason": finish}],
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                      "total_tokens": prompt_tokens + completion_tokens,
                      "completion_tokens_details": {"reasoning_tokens": 0}, "cost": cost}}


def answer(prompt: str, other: bool = False) -> str:
    """An answer line in the item's format: the source model's (C, YES) or another one (A, NO)."""
    if '"ANSWER: <letter>"' in prompt:
        return "ANSWER: A" if other else "ANSWER: C"
    return "ANSWER: NO" if other else "ANSWER: YES"


class Transport:
    """Chat calls answer like the source run's model: items 0-2 stop at the cap with a trace, item 3 stops there
    without one, and the rest finish, with a trace ("Item i: every case checked.") and an answer. /completions
    calls answer like the forced model: the trace of item 2 sends it back to reasoning until max_tokens, item 5's
    forced answer differs from its natural one, and the others repeat it. The raw-prompt check (the prime
    question) is answered like a provider that passes a raw prompt through, unless the first slug of its routing
    is in `wraps`: then /completions reports the chat call's prompt tokens. With `check_status`, the check's
    /completions call fails with that HTTP status. Every POST is recorded, in order."""

    def __init__(self, cost: float = 0.001, wraps: tuple[str, ...] = (), check_status: int | None = None):
        self.chat: list[dict] = []
        self.forced: list[dict] = []
        self.checks: list[tuple[str, dict]] = []
        self.calls: list[str] = []
        self.cost = cost
        self.wraps = wraps
        self.check_status = check_status

    def __call__(self, method, url, headers, body, timeout):
        assert headers["Authorization"] == f"Bearer {SECRET}"
        if method == "GET":
            return HttpResponse(200, json.dumps({"data": {"usage": 1.0}}).encode())
        req = json.loads(body)
        text = req["prompt"] if "prompt" in req else req["messages"][-1]["content"]
        if "Is 17 a prime number?" in text:
            if self.check_status and not url.endswith("/chat/completions"):
                self.checks.append((url, req))
                return HttpResponse(self.check_status, b'{"error": {"message": "No endpoints found that can handle the requested parameters."}}')
            resp = self.check(url, req, text)
        elif url.endswith("/chat/completions"):
            i = len(self.chat)
            self.chat.append(req)
            self.calls.append("chat")
            if i < 4:
                resp = api_response(None, reasoning=f"Item {i}: let me check each case. Still checking " if i < 3 else None,
                                    finish="length", completion_tokens=32768, reasoning_tokens=32768, cost=0.0001,
                                    model=req["model"], gen_id=f"gen-src-{i}")
            else:
                resp = api_response(answer(text), reasoning=f"Item {i}: every case checked.", cost=0.0001,
                                    model=req["model"], gen_id=f"gen-src-{i}")
        else:
            assert url.endswith("/api/v1/completions")
            self.forced.append(req)
            self.calls.append("forced")
            if "Item 2:" in text:
                resp = completion("", reasoning="Wait, let me redo the last case.", finish="length",
                                  completion_tokens=req["max_tokens"], cost=self.cost, model=req["model"])
            else:  # a finished trace is short (2,100 tokens), and so is its forced call's price
                resp = completion(answer(text, other="Item 5:" in text), cost=self.cost if "Still checking" in text else 0.0001,
                                  model=req["model"], gen_id=f"gen-forced-{len(self.forced)}")
        return HttpResponse(200, json.dumps(resp).encode())

    def check(self, url: str, req: dict, text: str) -> dict:
        self.checks.append((url, req))
        self.calls.append("check")
        slug = req["provider"]["order"][0]
        chat, wrapped = url.endswith("/chat/completions"), slug in self.wraps
        tokens = len(text) // 4 + (54 if chat or wrapped else 0)  # the chat template's tokens
        provider = {"deepinfra": "DeepInfra", "dekallm": "DekaLLM"}[slug.split("/")[0]]
        if chat:
            return api_response("YES", reasoning="17 is prime.", prompt_tokens=tokens, completion_tokens=8, reasoning_tokens=6,
                                cost=CHECK_COST, model=req["model"], provider=provider, gen_id="gen-check-chat")
        return completion("YES", reasoning="Need to answer YES." if wrapped else None, prompt_tokens=tokens, completion_tokens=2,
                          cost=CHECK_COST, model=req["model"], provider=provider, gen_id="gen-check-raw")


class NoCalls:
    def __call__(self, method, url, headers, body, timeout):
        raise AssertionError(f"a dry run sent {method} {url}")


@pytest.fixture
def key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", SECRET)


def client(transport):
    return OpenRouterClient(transport, sleep=lambda s: None)


def source_run(tmp_path: Path, transport: Transport, model: str = "openai/gpt-oss-20b", items: tuple[str, ...] = (B4E1,),
               limit: int = 6) -> Path:
    """A thinking run on the first `limit` smoke items, routed to the model's pinned provider (as every real run is)."""
    out = tmp_path / "runs" / SOURCE
    args = ["--items", *items, "--model", model, "--out", str(out), "--cap-usd", "1", "--cache-dir", str(tmp_path / "cache"),
            "--ledger", str(tmp_path / "LEDGER.md"), "--concurrency", "1", "--limit", str(limit)]
    assert run_main(args, client=client(transport)) == 0
    return out


def force(src: Path, transport: Transport, *extra: str) -> int:
    root = src.parent.parent
    return force_main([str(src), "--cap-usd", "1", "--cache-dir", str(root / "cache"), "--ledger", str(root / "LEDGER.md"),
                       "--concurrency", "1", *extra], client=client(transport))


def read_gz(p: Path) -> list[dict]:
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def manifest_of(out: Path) -> dict:
    return json.loads((out / "manifest.json").read_text())


def digests(d: Path) -> dict[str, str]:
    return {str(p.relative_to(d)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.rglob("*")) if p.is_file()}


def run_patterns() -> tuple[str, ...]:
    """The analysis's RUN_PATTERNS, read from its source (importing the script would set its thread settings)."""
    tree = ast.parse((REPO / "analysis" / "prelim_2026_11_18.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "RUN_PATTERNS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise LookupError("RUN_PATTERNS")


# --- templates and routes ---------------------------------------------------------------------------------------


def chat_request(model: str, system: str | None = None, **extra) -> dict:
    messages = ([{"role": "system", "content": system}] if system is not None else []) + [{"role": "user", "content": "Is it so?"}]
    return {"model": model, "messages": messages, "max_tokens": 32768, "provider": {"order": ["p"]}, **extra}


def test_gpt_oss_template_is_exact():
    req = chat_request("openai/gpt-oss-20b", reasoning={"effort": "high"}, temperature=1.0, top_p=1.0)
    assert forced_prompt(req, "I wonder.\n\n") == (
        GPT_OSS_SYSTEM.format("high") + "<|start|>user<|message|>Is it so?<|end|>"
        "<|start|>assistant<|channel|>analysis<|message|>I wonder.<|end|><|start|>assistant<|channel|>final<|message|>")
    req = chat_request("openai/gpt-oss-120b", system="Be brief.", reasoning={"effort": "low"}, temperature=1.0, top_p=1.0)
    assert forced_prompt(req, "I wonder.") == (
        GPT_OSS_SYSTEM.format("low") + "<|start|>developer<|message|># Instructions\n\nBe brief.<|end|>"
        "<|start|>user<|message|>Is it so?<|end|>"
        "<|start|>assistant<|channel|>analysis<|message|>I wonder.<|end|><|start|>assistant<|channel|>final<|message|>")
    body = forced_body(req, "I wonder.", 4096)
    assert body == {"model": "openai/gpt-oss-120b", "provider": {"order": ["p"]}, "prompt": forced_prompt(req, "I wonder."),
                    "max_tokens": 4096, "temperature": 1.0, "top_p": 1.0}
    assert forced_body(req, "I wonder.", 4096, DEEPINFRA_BF16, BAN) == {**body, "provider": DEEPINFRA_BF16, "logit_bias": BAN}


def test_qwen3_template_is_exact():
    req = chat_request("qwen/qwen3-32b", reasoning={"effort": "high"}, temperature=0.6, top_p=0.95, top_k=20)
    assert forced_prompt(req, "I wonder.\n") == (
        "<|im_start|>user\nIs it so?<|im_end|>\n<|im_start|>assistant\n<think>\nI wonder.\n\n"
        f"{QWEN3_STOP}\n</think>\n\n")
    req = chat_request("qwen/qwen3-14b", system="Be brief.", reasoning={"enabled": False}, temperature=0.7, top_p=0.8, top_k=20)
    assert forced_prompt(req, "I wonder.") == (
        "<|im_start|>system\nBe brief.<|im_end|>\n<|im_start|>user\nIs it so?<|im_end|>\n<|im_start|>assistant\n<think>\n"
        f"I wonder.\n\n{QWEN3_STOP}\n</think>\n\n")
    assert forced_body(req, "I wonder.", 4096)["top_k"] == 20  # top_k only when the source request has it


def test_unsupported_models_are_refused(tmp_path, key):
    with pytest.raises(UnsupportedModel, match="no force-1 template"):
        forced_prompt(chat_request("deepseek/deepseek-r1-0528"), "I wonder.")
    t = Transport()
    src = source_run(tmp_path, t, model="deepseek/deepseek-r1-0528")
    for template in ("force-2", "force-1"):
        with pytest.raises(SystemExit, match="no force-1 template"):
            force(src, t, "--template", template)
    assert not t.forced and not t.checks
    assert not (src.parent / "forced").exists() and not (src.parent / "forced-2").exists()


def test_forcing_routes_are_kept_apart_from_the_source_pins():
    for slug, price in (("openai/gpt-oss-20b", (0.03, 0.14)), ("openai/gpt-oss-120b", (0.037, 0.17))):
        route = FORCING_ROUTES[slug]
        assert route.provider == DEEPINFRA_BF16 and (route.price.prompt, route.price.completion) == price
        assert route.context_length == 131072
        assert get_model(slug).provider["order"] == ["dekallm/bf16"]  # the source runs' pin is unchanged
    for slug in ("qwen/qwen3-32b", "qwen/qwen3-14b"):  # their source pin, which passes raw prompts through
        cfg, route = get_model(slug), FORCING_ROUTES[slug]
        assert route.provider == cfg.provider and route.provider["order"] == ["deepinfra/fp8/flex"]
        assert route.price == cfg.pinned_price and route.context_length == cfg.context_length


def test_the_banned_tokens_are_the_harmony_tokens_that_leave_the_final_channel():
    tiktoken = pytest.importorskip("tiktoken")
    try:
        enc = tiktoken.get_encoding("o200k_harmony")
    except Exception as e:  # downloaded on first use: skipped offline or on an older tiktoken
        pytest.skip(f"o200k_harmony is not available: {e}")
    ids = {t: enc.encode_single_token(t) for t in ("<|channel|>", "<|start|>", "<|end|>", "<|return|>")}
    assert GPT_OSS_LOGIT_BIAS == {str(ids[t]): -100 for t in ("<|channel|>", "<|start|>", "<|end|>")} == BAN
    assert str(ids["<|return|>"]) not in GPT_OSS_LOGIT_BIAS  # the answer can still end


def test_the_raw_check_prompts():
    assert raw_check_prompt("openai/gpt-oss-20b") == (  # the 2026-11-18 probes' prompt (batches 10 and 11)
        GPT_OSS_SYSTEM.format("low") + "<|start|>user<|message|>Is 17 a prime number? Answer with one word, YES or NO.<|end|>"
        "<|start|>assistant<|channel|>analysis<|message|>17 has no divisors other than 1 and itself.<|end|>"
        "<|start|>assistant<|channel|>final<|message|>")
    assert raw_check_prompt("qwen/qwen3-14b") == (
        "<|im_start|>user\nIs 17 a prime number? Answer with one word, YES or NO.<|im_end|>\n<|im_start|>assistant\n"
        f"<think>\n17 has no divisors other than 1 and itself.\n\n{QWEN3_STOP}\n</think>\n\n")


# --- selection ----------------------------------------------------------------------------------------------------


def test_selection_takes_responses_cut_at_the_cap_or_finished_with_a_trace():
    def rec(item, finish, reasoning, content=None):
        return {"item_id": item, "sample": 0, "response": api_response(content, reasoning=reasoning, finish=finish)}

    raw = [rec("a", "length", "a trace"), rec("b", "length", None), rec("c", "length", "  \n"), rec("d", "stop", "a trace", "ANSWER: YES"),
           {"item_id": "e", "sample": 0, "response": None}, rec("f", "length", "another trace"), rec("g", "stop", None, "ANSWER: NO"),
           rec("h", "stop", "a trace", " \n"), rec("i", "stop", "a trace", None), rec("j", "stop", "the last trace", "ANSWER: NO")]
    picked, skipped = select(raw)
    assert [r["item_id"] for r in picked] == ["a", "f"] and skipped == {"no_trace": 2}
    picked, skipped = select(raw, "done")
    assert [r["item_id"] for r in picked] == ["d", "j"] and skipped == {"no_trace": 1, "no_content": 2}


def test_response_view_reads_text_completions():
    v = ResponseView.from_api(completion("ANSWER: YES", reasoning="Fine.", finish="stop", completion_tokens=7), max_tokens=4096)
    assert (v.content, v.reasoning, v.finish_reason, v.completion_tokens, v.prompt_tokens) == ("ANSWER: YES", "Fine.", "stop", 7, 33700)
    assert v.provider == "FakeProvider" and v.cost == 0.001 and v.error is None
    chat = ResponseView.from_api(api_response("ANSWER: NO", reasoning="Hm."))
    assert (chat.content, chat.reasoning) == ("ANSWER: NO", "Hm.")


def test_complete_posts_to_completions_with_chats_retries(key):
    calls = []

    def transport(method, url, headers, body, timeout):
        calls.append(url)
        if len(calls) == 1:
            return HttpResponse(503, b'{"error": {"message": "busy"}}')
        return HttpResponse(200, json.dumps(completion("ANSWER: YES")).encode())

    res = client(transport).complete({"model": "m", "prompt": "p", "max_tokens": 8})
    assert res.ok and res.attempts == 2 and calls == ["https://openrouter.ai/api/v1/completions"] * 2


# --- the force-2 pass -----------------------------------------------------------------------------------------------


def test_forced_pass_records_and_scores_completions(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    before = digests(src)
    source_raw = read_gz(src / "raw.jsonl.gz")
    assert force(src, t) == 0
    out = tmp_path / "runs" / "forced-2" / "cut" / SOURCE

    assert len(t.forced) == 3  # items 0-2; item 3 has no trace
    for req, src_rec in zip(t.forced, source_raw[:3]):
        src_req = src_rec["request"]
        assert set(req) == {"model", "provider", "prompt", "max_tokens", "temperature", "top_p", "logit_bias"}
        assert (req["temperature"], req["top_p"], req["max_tokens"]) == (src_req["temperature"], src_req["top_p"], 4096)
        assert req["prompt"] == forced_prompt(src_req, src_rec["response"]["choices"][0]["message"]["reasoning"])

    raw = read_gz(out / "raw.jsonl.gz")
    assert [r["item_id"] for r in raw] == [r["item_id"] for r in source_raw[:3]]
    assert all(r["source_run_id"] == SOURCE and r["forced_template"] == "force-2" and r["run_id"] == f"forced-2/cut/{SOURCE}" for r in raw)
    assert all((r["forced_select"], r["forced_sample"], r["source_sample"], r["sample"]) == ("cut", 0, 0, 0) for r in raw)
    assert not any("natural_response" in r for r in raw)
    assert [r["source_cache_key"] for r in raw] == [r["cache_key"] for r in source_raw[:3]]
    assert all(r["prompt_hash"] == hashlib.sha256(r["request"]["prompt"].encode()).hexdigest()[:16] for r in raw)

    scored = read_gz(out / "scored.jsonl.gz")
    assert all(r["forced"] and r["forced_template"] == "force-2" and r["source_run_id"] == SOURCE and r["forced_select"] == "cut"
               for r in scored)
    assert [r["category"] for r in scored] == ["ok", "ok", "truncated"] and all(r["condition"] == "thinking-high-forced" for r in scored)
    assert scored[2]["reasoning_returned"] and scored[0]["parsed"] in ("YES", "C") and "same_as_natural" not in scored[0]

    m = manifest_of(out)
    assert m["run_id"] == f"forced-2/cut/{SOURCE}" and m["status"] == "complete"
    assert m["source"]["run_id"] == SOURCE and m["source"]["raw_sha256"] == before["raw.jsonl.gz"]
    assert m["forced"] == {"template": "force-2", "endpoint": "https://openrouter.ai/api/v1/completions", "max_tokens": 4096,
                           "select": "cut", "logit_bias": BAN}
    assert m["counts"] == {"candidates": 3, "selected": 3, "units": 1, "samples": 1, "calls": 3, "skipped_no_trace": 1,
                           "skipped_no_room": 0, "max_tokens_lowered": 0, "responses": 3, "answered": 2, "parsed": 2,
                           "still_reasoning": 1, "renewed_reasoning": 1}
    assert m["spend"]["spent_usd"] == pytest.approx(0.003 + 2 * CHECK_COST) and m["git"]["sha"] and m["versions"]["scorer"]
    report = (out / "REPORT.md").read_text()
    assert "## Forced final answers" in report and "2 answered and 1 went back to reasoning" in report
    assert "2 parsed" in report and "1 carried reasoning again" in report and "Raw-prompt check" in report

    assert digests(src) == before  # the source run is never modified; its records stay truncated
    assert [r["category"] for r in read_gz(src / "scored.jsonl.gz")][:4] == ["truncated"] * 4

    (out / "scored.jsonl.gz").unlink()
    assert score_main([str(out)]) == 0  # score.py re-scores a forced pass
    assert read_gz(out / "scored.jsonl.gz") == scored


def test_forced_calls_go_to_the_forcing_route_never_dekallm(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    assert all(req["provider"] == get_model("openai/gpt-oss-20b").provider for req in t.chat)  # the source ran on DekaLLM
    assert force(src, t) == 0
    sent = t.forced + [req for _, req in t.checks]
    assert len(t.forced) == 3 and len(t.checks) == 2 and all(req["provider"] == DEEPINFRA_BF16 for req in sent)
    assert "dekallm" not in json.dumps(sent).lower()
    assert all(req["logit_bias"] == BAN for req in t.forced)  # gpt-oss may not leave the final channel
    m = manifest_of(tmp_path / "runs" / "forced-2" / "cut" / SOURCE)
    assert m["provider_routing"] == DEEPINFRA_BF16 and m["source"]["provider_routing"] == get_model("openai/gpt-oss-20b").provider
    assert (m["price"]["prompt"], m["price"]["completion"]) == (0.03, 0.14) and m["context_length"] == 131072


def test_the_raw_prompt_check_runs_before_any_forced_call_and_is_booked(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    first = len(t.calls)
    assert force(src, t, "--budget-tag", "forced-test", "--budget-usd", "1") == 0
    assert t.calls[first:] == ["check", "check", "forced", "forced", "forced"]
    (raw_url, raw_req), (chat_url, chat_req) = t.checks
    text = raw_check_prompt("openai/gpt-oss-20b")
    assert raw_url == "https://openrouter.ai/api/v1/completions" and chat_url == "https://openrouter.ai/api/v1/chat/completions"
    assert raw_req == {"model": "openai/gpt-oss-20b", "provider": DEEPINFRA_BF16, "max_tokens": 8, "temperature": 0, "prompt": text}
    assert chat_req == {"model": "openai/gpt-oss-20b", "provider": DEEPINFRA_BF16, "max_tokens": 8, "temperature": 0,
                        "messages": [{"role": "user", "content": text}]}
    m = manifest_of(tmp_path / "runs" / "forced-2" / "cut" / SOURCE)
    check = m["raw_check"]
    assert check["passed"] is True and check["prompt"] == text and check["routing"] == DEEPINFRA_BF16
    assert check["completions"]["prompt_tokens"] < check["chat"]["prompt_tokens"]
    assert check["completions"]["text"] == check["chat"]["text"] == "YES" and check["completions"]["provider"] == "DeepInfra"
    assert check["cost_usd"] == pytest.approx(2 * CHECK_COST)
    # booked in the guard and in the ledger row, with the forced calls
    assert m["spend"]["calls"] == 5 and m["spend"]["spent_usd"] == pytest.approx(0.003 + 2 * CHECK_COST)
    assert m["charged_usd"] == pytest.approx(0.003 + 2 * CHECK_COST)
    rows = [r for r in ledger.rows(tmp_path / "LEDGER.md") if r["run_id"].startswith("forced")]
    assert len(rows) == 1 and float(rows[0]["cost_usd"]) == pytest.approx(0.003 + 2 * CHECK_COST)
    assert ledger.spent(tmp_path / "LEDGER.md", "forced-test") == pytest.approx(0.003 + 2 * CHECK_COST)


def test_a_failed_raw_prompt_check_refuses_before_any_forced_call(tmp_path, key):
    t = Transport(wraps=("deepinfra/bf16",))
    src = source_run(tmp_path, t)
    with pytest.raises(SystemExit, match=r"raw-prompt check failed on \['deepinfra/bf16'\] \(served by DeepInfra\)") as e:
        force(src, t, "--notes", "try")
    assert "does not pass a raw prompt through untouched" in str(e.value) and "No forced call was sent" in str(e.value)
    assert not t.forced and len(t.checks) == 2
    assert not (src.parent / "forced-2").exists()  # nothing written but the ledger row for the check's cost
    rows = [r for r in ledger.rows(tmp_path / "LEDGER.md") if r["run_id"].startswith("forced")]
    assert len(rows) == 1 and rows[0]["run_id"] == f"forced-2/cut/{SOURCE}" and rows[0]["items"] == "0"
    assert float(rows[0]["cost_usd"]) == pytest.approx(2 * CHECK_COST) and rows[0]["notes"].startswith("try status=refused")


def test_a_raw_prompt_check_that_cannot_run_refuses_too(tmp_path, key):
    t = Transport(check_status=404)  # e.g. a parameter the endpoint does not support, with require_parameters
    src = source_run(tmp_path, t)
    with pytest.raises(SystemExit, match=r"could not run the raw-prompt check on \['deepinfra/bf16'\]: HTTP 404"):
        force(src, t)
    assert not t.forced and len(t.checks) == 1 and not (src.parent / "forced-2").exists()


def test_force_1_on_gpt_oss_is_refused_where_dekallm_wraps_the_prompt(tmp_path, key):
    t = Transport(wraps=("dekallm/bf16",))  # as DekaLLM does (2026-11-18)
    src = source_run(tmp_path, t)
    with pytest.raises(SystemExit, match=r"\['dekallm/bf16'\] \(served by DekaLLM\)"):
        force(src, t, "--template", "force-1")
    assert not t.forced and [req["provider"]["order"] for _, req in t.checks] == [["dekallm/bf16"]] * 2
    assert not (src.parent / "forced").exists()


def test_select_done_replays_whole_traces_and_compares_with_the_natural_answer(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    source_raw, source_scored = read_gz(src / "raw.jsonl.gz"), read_gz(src / "scored.jsonl.gz")
    assert force(src, t, "--select", "done") == 0
    out = tmp_path / "runs" / "forced-2" / "done" / SOURCE

    assert [req["prompt"] for req in t.forced] == [  # items 4 and 5 finished: each whole trace, closed
        forced_prompt(r["request"], f"Item {i}: every case checked.") for i, r in zip((4, 5), source_raw[4:6])]
    raw = read_gz(out / "raw.jsonl.gz")
    for r, s in zip(raw, source_raw[4:6]):
        assert r["run_id"] == f"forced-2/done/{SOURCE}" and r["forced_select"] == "done" and r["natural_max_tokens"] == 32768
        assert r["natural_response"]["choices"][0]["message"] == {"role": "assistant", "content": s["response"]["choices"][0]["message"]["content"]}
        assert r["natural_response"]["usage"] == s["response"]["usage"]  # the source response, its reasoning removed

    scored = read_gz(out / "scored.jsonl.gz")
    assert [(r["natural_category"], r["natural_answer_key"], r["category"], r["answer_key"], r["same_as_natural"]) for r in scored] == [
        ("ok", "C", "ok", "C", True), ("ok", "C", "ok", "A", False)]  # item 5's forced answer differs
    assert [r["natural_correct"] for r in scored] == [r["correct"] for r in source_scored[4:6]]
    m = manifest_of(out)
    assert m["forced"]["select"] == "done" and m["counts"] == {
        "candidates": 2, "selected": 2, "units": 1, "samples": 1, "calls": 2, "skipped_no_trace": 0, "skipped_no_content": 0,
        "skipped_no_room": 0, "max_tokens_lowered": 0, "responses": 2, "answered": 2, "parsed": 2, "still_reasoning": 0,
        "renewed_reasoning": 0, "natural_ok": 2, "same_as_natural": 1}
    assert "1 of the 2 forced responses whose source response is `ok` gave its answer" in (out / "REPORT.md").read_text()

    (out / "scored.jsonl.gz").unlink()
    assert score_main([str(out)]) == 0  # the natural comparison is re-made from the raw records
    assert read_gz(out / "scored.jsonl.gz") == scored


def test_per_unit_and_samples(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t, items=(B4E1, B4E2), limit=30)  # units: B4/C4 E1 (items 0-27) and B4/C4 E2 (items 28-29)
    ids = [r["item_id"] for r in read_gz(src / "raw.jsonl.gz")]
    assert force(src, t, "--select", "done", "--per-unit", "2", "--samples", "2") == 0
    out = tmp_path / "runs" / "forced-2" / "done" / SOURCE
    raw = read_gz(out / "raw.jsonl.gz")
    assert [(r["item_id"], r["sample"], r["forced_sample"]) for r in raw] == [(ids[i], s, s) for i in (4, 5, 28, 29) for s in (0, 1)]
    assert len(t.forced) == 8 and len({r["cache_key"] for r in raw}) == 8  # two samples of each: distinct keys and records
    assert all(r["cache_key"] == cache_key(r["request"], r["sample"]) for r in raw) and raw[0]["request"] == raw[1]["request"]
    m = manifest_of(out)
    assert {k: m["counts"][k] for k in ("candidates", "selected", "units", "samples", "calls", "responses")} == {
        "candidates": 26, "selected": 4, "units": 2, "samples": 2, "calls": 8, "responses": 8}
    assert (m["items"]["per_unit"], m["items"]["samples"]) == (2, 2)
    sent = len(t.calls)
    assert force(src, t, "--select", "done", "--per-unit", "2", "--samples", "2") == 0 and len(t.calls) == sent  # all done
    assert force(src, t, "--per-unit", "2") == 0  # cut: only E1 has responses cut at the cap
    assert [r["item_id"] for r in read_gz(tmp_path / "runs" / "forced-2" / "cut" / SOURCE / "raw.jsonl.gz")] == ids[:2]


def test_output_dirs_and_run_ids_stay_out_of_the_analysis(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    runs = tmp_path / "runs"
    for args, rel in ((("--select", "cut"), "forced-2/cut"), (("--select", "done"), "forced-2/done"),
                      (("--template", "force-1"), "forced")):
        assert force(src, t, *args) == 0
        out = runs / rel / SOURCE
        assert manifest_of(out)["run_id"] == f"{rel}/{SOURCE}"
        assert {r["run_id"] for r in read_gz(out / "raw.jsonl.gz")} == {r["run_id"] for r in read_gz(out / "scored.jsonl.gz")} == {f"{rel}/{SOURCE}"}
    found = sorted({str(d.relative_to(runs)) for pat in run_patterns() for d in runs.glob(pat)})
    assert found == [SOURCE]  # the analysis's patterns see the source run only


def test_the_cost_guard_stops_at_the_cap(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    # the raw-prompt check books its two calls first; then each forced call reserves 1.25 x its worst case at the
    # forcing route's price: the source's 900 prompt + 32,768 completion tokens, plus max_tokens
    worst = 1.25 * FORCING_ROUTES["openai/gpt-oss-20b"].price.cost(900 + 32768, 4096)
    cap = 2 * CHECK_COST + 0.001 + worst + 0.0005  # the second reservation fits after the first call's $0.001; the third does not
    root = src.parent.parent
    assert force_main([str(src), "--cap-usd", str(cap), "--cache-dir", str(root / "cache"), "--ledger", str(root / "LEDGER.md"),
                       "--concurrency", "1"], client=client(t)) == 2
    m = manifest_of(src.parent / "forced-2" / "cut" / SOURCE)
    assert len(t.forced) == 2 and m["status"] == "stopped" and m["stop_reason"].startswith("cap:")
    assert m["spend"]["spent_usd"] == pytest.approx(0.002 + 2 * CHECK_COST) and m["spend"]["spent_usd"] <= cap


def test_resume_sends_only_the_rest_and_the_cache_never_repays(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    out = src.parent / "forced-2" / "cut" / SOURCE
    assert force(src, t, "--limit", "2") == 0 and len(t.forced) == 2 and len(t.checks) == 2
    assert force(src, t) == 0 and len(t.forced) == 3 and len(t.checks) == 4  # only the missing call, after a new check
    assert force(src, t) == 0 and len(t.forced) == 3 and len(t.checks) == 4  # nothing left to send, and no check
    m = manifest_of(out)
    assert m["resumed_from"] == 3 and len(m["previous_invocations"]) == 2
    assert m["charged_usd_all_invocations"] == pytest.approx(0.003 + 4 * CHECK_COST)
    assert m["raw_check"] == {"passed": None, "skipped": "nothing left to send"}
    assert [p["raw_check"]["passed"] for p in m["previous_invocations"]] == [True, True]
    with pytest.raises(SystemExit, match="different template, max_tokens"):
        force(src, t, "--max-tokens", "2048")
    assert len(t.checks) == 4  # refused before any call
    for p in out.iterdir():
        p.unlink()
    assert force(src, t) == 0 and len(t.forced) == 3 and len(t.checks) == 4  # a fresh pass is answered from the cache
    m = manifest_of(out)
    assert m["cache_hits"] == 3 and m["charged_usd"] == 0 and m["counts"]["responses"] == 3
    assert m["raw_check"]["passed"] is None and m["raw_check"]["skipped"].startswith("no call to send")


def test_a_ledger_row_per_live_invocation(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    assert force(src, t, "--budget-tag", "forced-test", "--budget-usd", "1", "--notes", "first pass") == 0
    rows = [r for r in ledger.rows(tmp_path / "LEDGER.md") if r["run_id"].startswith("forced")]
    assert len(rows) == 1 and rows[0]["run_id"] == f"forced-2/cut/{SOURCE}" and rows[0]["condition"] == "thinking-high-forced"
    assert rows[0]["model"] == "openai/gpt-oss-20b" and rows[0]["items"] == "3"
    assert float(rows[0]["cost_usd"]) == pytest.approx(0.003 + 2 * CHECK_COST)
    assert rows[0]["notes"] == "first pass status=complete"
    assert ledger.spent(tmp_path / "LEDGER.md", "forced-test") == pytest.approx(0.003 + 2 * CHECK_COST)


def test_the_key_is_never_written_anywhere(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    force(src, t)
    force(src, t, "--select", "done")
    for p in tmp_path.rglob("*"):
        if p.is_file():
            data = gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes()
            assert SECRET.encode() not in data, p


def test_the_dry_run_makes_no_call_and_writes_nothing(tmp_path, key, capsys, monkeypatch):
    src = source_run(tmp_path, Transport())
    capsys.readouterr()
    monkeypatch.delenv("OPENROUTER_API_KEY")
    assert force_main([str(src), "--dry-run"], client=client(NoCalls())) == 0
    text = capsys.readouterr().out
    assert "3 calls" in text and "1 stopped there without a trace" in text and "$" in text
    assert "Forced calls go to ['deepinfra/bf16']" in text and "the source run went to ['dekallm/bf16']" in text
    assert force_main([str(src), "--dry-run", "--select", "done", "--per-unit", "1", "--samples", "2"], client=client(NoCalls())) == 0
    text = capsys.readouterr().out
    assert "2 responses finished with a reasoning trace and an answer" in text and "--per-unit 1 keeps" in text
    assert "1 records from 1 units x 2 samples = 2 calls" in text
    assert force_main([str(src), "--dry-run", "--template", "force-1"], client=client(NoCalls())) == 0
    assert "Forced calls go to ['dekallm/bf16']" in capsys.readouterr().out
    assert not (src.parent / "forced").exists() and not (src.parent / "forced-2").exists()


# --- force-1, as it was ----------------------------------------------------------------------------------------------


def test_force_1_takes_only_its_old_options():
    for extra in (("--select", "done"), ("--per-unit", "2"), ("--samples", "2")):
        with pytest.raises(SystemExit):
            force_main(["data/runs/nowhere", "--template", "force-1", *extra])


def test_force_1_is_reproduced_as_it_was(tmp_path, key):
    """force-1 sends what it always sent: the source's own pin, no logit_bias, the same prompts and cache keys, into
    data/runs/forced/<source>, with the same record fields. A second pass from scratch is answered wholly from the
    cache: no call at all, not even the raw-prompt check, and the same scored answers."""
    t = Transport()
    src = source_run(tmp_path, t)
    source_raw = read_gz(src / "raw.jsonl.gz")
    assert force(src, t, "--template", "force-1") == 0
    out = tmp_path / "runs" / "forced" / SOURCE
    pin = get_model("openai/gpt-oss-20b").provider
    bodies = [{"model": r["request"]["model"], "provider": r["request"]["provider"], "max_tokens": 4096,
               "prompt": forced_prompt(r["request"], r["response"]["choices"][0]["message"]["reasoning"]),
               "temperature": r["request"]["temperature"], "top_p": r["request"]["top_p"]} for r in source_raw[:3]]
    assert t.forced == bodies and all(b["provider"] == pin for b in bodies)
    assert [req["provider"] for _, req in t.checks] == [pin, pin]  # the check goes where the calls go

    raw = read_gz(out / "raw.jsonl.gz")
    assert [r["cache_key"] for r in raw] == [cache_key(b, 0) for b in bodies]
    assert all(r["run_id"] == f"forced/{SOURCE}" and r["forced_template"] == "force-1" and not FORCE_2_FIELDS & set(r) for r in raw)
    scored = read_gz(out / "scored.jsonl.gz")
    assert [r["category"] for r in scored] == ["ok", "ok", "truncated"] and not any(FORCE_2_FIELDS & set(r) for r in scored)
    m = manifest_of(out)
    assert m["forced"] == {"template": "force-1", "endpoint": "https://openrouter.ai/api/v1/completions", "max_tokens": 4096}
    assert m["provider_routing"] == m["source"]["provider_routing"] == pin and m["price"]["prompt"] == 0.029
    assert m["counts"]["selected"] == 3 and m["counts"]["skipped_no_trace"] == 1 and m["counts"]["renewed_reasoning"] == 1

    calls = len(t.calls)
    for p in out.iterdir():
        p.unlink()
    assert force(src, t, "--template", "force-1") == 0
    assert len(t.calls) == calls  # nothing sent, not even the raw-prompt check
    again = read_gz(out / "scored.jsonl.gz")
    assert [{**r, "from_cache": None} for r in again] == [{**r, "from_cache": None} for r in scored]
    assert manifest_of(out)["cache_hits"] == 3 and manifest_of(out)["charged_usd"] == 0


# --- the endpoint's context ----------------------------------------------------------------------------------


def test_max_tokens_is_lowered_to_fit_the_context():
    def rec(prompt, completion):
        return {"response": {"usage": {"prompt_tokens": prompt, "completion_tokens": completion}}}
    assert call_max_tokens(rec(1000, 32768), 4096, 40960) == 4096  # room enough
    # the dev Qwen3 item that overflowed DeepInfra's 40,960 tokens on 2026-11-18 (estimate 36,889)
    assert call_max_tokens(rec(4121, 32768), 4096, 40960) == 40960 - math.ceil(1.01 * 36889) - 64 < 4096
    assert call_max_tokens(rec(4121, 32768), 4096, None) == 4096  # no context known: unchanged
    assert call_max_tokens(rec(8000, 32768), 4096, 40960) < 256  # too little room: the pass skips it


def test_a_qwen3_pass_lowers_max_tokens_per_call_to_fit_the_context(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t, model="qwen/qwen3-32b")
    source_raw = {r["item_id"]: r for r in read_gz(src / "raw.jsonl.gz")}
    assert force(src, t, "--max-tokens", "8000") == 0
    assert len(t.forced) == 3
    context = FORCING_ROUTES["qwen/qwen3-32b"].context_length
    out = tmp_path / "runs" / "forced-2" / "cut" / SOURCE
    for r in read_gz(out / "raw.jsonl.gz"):
        want = call_max_tokens(source_raw[r["item_id"]], 8000, context)
        assert r["request"]["max_tokens"] == want < 8000  # 900 + 32,768 prompt tokens leave 6,891 of 40,960
        assert r["request"]["prompt"].endswith("directly now.\n</think>\n\n")
        assert r["request"]["provider"] == get_model("qwen/qwen3-32b").provider and "logit_bias" not in r["request"]
    m = manifest_of(out)
    assert m["forced"]["max_tokens"] == 8000 and m["forced"]["logit_bias"] is None
    assert m["counts"]["max_tokens_lowered"] == 3 and m["counts"]["skipped_no_room"] == 0
