"""The forced-answer pass with the HTTP layer mocked: the force-1 templates, selection, a forced call
recorded and scored from a text-completions response, the cost cap, resumption, the ledger, the
dry run, and the API key never leaving the environment."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import pytest
from evals_helpers import ITEMS, api_response

from reasoning_heuristics.evals import ledger
from reasoning_heuristics.evals.client import HttpResponse, OpenRouterClient
from reasoning_heuristics.evals.force import UnsupportedModel, forced_body, forced_prompt, select
from reasoning_heuristics.evals.force import main as force_main
from reasoning_heuristics.evals.models import get_model
from reasoning_heuristics.evals.run import main as run_main
from reasoning_heuristics.evals.score import main as score_main
from reasoning_heuristics.evals.scoring import ResponseView

SECRET = "sk-or-test-SECRET-do-not-write"
B4E1 = str(ITEMS / "smoke" / "B4C4_E1_smoke_s1.jsonl.gz")
SOURCE = "2026-11-18-dev-test"
GPT_OSS_SYSTEM = ("<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: 2024-06\n\n"
                  "Reasoning: {}\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|>")
QWEN3_STOP = "Considering the limited time by the user, I have to give the solution based on the thinking directly now."


def completion(text: str, *, reasoning: str | None = None, finish: str = "stop", completion_tokens: int = 20,
               cost: float = 0.001, model: str = "openai/gpt-oss-20b", gen_id: str = "gen-forced") -> dict:
    """An OpenRouter-shaped text completion (POST /completions)."""
    return {"id": gen_id, "object": "text_completion", "model": model, "provider": "FakeProvider",
            "choices": [{"index": 0, "text": text, "reasoning": reasoning, "logprobs": None,
                         "finish_reason": finish, "native_finish_reason": finish}],
            "usage": {"prompt_tokens": 33700, "completion_tokens": completion_tokens, "total_tokens": 33700 + completion_tokens,
                      "completion_tokens_details": {"reasoning_tokens": 0}, "cost": cost}}


class Transport:
    """Chat calls answer like the source run's model: items 0-2 stop at the cap with a trace, item 3 stops
    there without one, the rest answer. /completions calls answer like the forced model; the trace of
    item 2 sends it back to reasoning until max_tokens. Every POST is recorded with its URL."""

    def __init__(self, cost: float = 0.001):
        self.chat: list[dict] = []
        self.forced: list[dict] = []
        self.cost = cost

    def __call__(self, method, url, headers, body, timeout):
        assert headers["Authorization"] == f"Bearer {SECRET}"
        if method == "GET":
            return HttpResponse(200, json.dumps({"data": {"usage": 1.0}}).encode())
        req = json.loads(body)
        if url.endswith("/chat/completions"):
            i = len(self.chat)
            self.chat.append(req)
            if i < 4:
                resp = api_response(None, reasoning=f"Item {i}: let me check each case. Still checking " if i < 3 else None,
                                    finish="length", completion_tokens=32768, reasoning_tokens=32768, cost=0.0001,
                                    model=req["model"], gen_id=f"gen-src-{i}")
            else:
                resp = api_response("ANSWER: C" if '"ANSWER: <letter>"' in req["messages"][-1]["content"] else "ANSWER: YES",
                                    cost=0.0001, model=req["model"], gen_id=f"gen-src-{i}")
        else:
            assert url.endswith("/api/v1/completions")
            self.forced.append(req)
            if "Item 2:" in req["prompt"]:
                resp = completion("", reasoning="Wait, let me redo the last case.", finish="length",
                                  completion_tokens=req["max_tokens"], cost=self.cost, model=req["model"])
            else:
                resp = completion("ANSWER: C" if '"ANSWER: <letter>"' in req["prompt"] else "ANSWER: YES",
                                  cost=self.cost, model=req["model"], gen_id=f"gen-forced-{len(self.forced)}")
        return HttpResponse(200, json.dumps(resp).encode())


class NoCalls:
    def __call__(self, method, url, headers, body, timeout):
        raise AssertionError(f"a dry run sent {method} {url}")


@pytest.fixture
def key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", SECRET)


def client(transport):
    return OpenRouterClient(transport, sleep=lambda s: None)


def source_run(tmp_path: Path, transport: Transport, model: str = "openai/gpt-oss-20b") -> Path:
    """A thinking run on 6 smoke items, routed to the model's pinned provider (as every real run is)."""
    out = tmp_path / "runs" / SOURCE
    args = ["--items", B4E1, "--model", model, "--out", str(out), "--cap-usd", "1", "--cache-dir", str(tmp_path / "cache"),
            "--ledger", str(tmp_path / "LEDGER.md"), "--concurrency", "1", "--limit", "6"]
    assert run_main(args, client=client(transport)) == 0
    return out


def force(src: Path, transport: Transport, *extra: str) -> int:
    root = src.parent.parent
    return force_main([str(src), "--cap-usd", "1", "--cache-dir", str(root / "cache"), "--ledger", str(root / "LEDGER.md"),
                       "--concurrency", "1", *extra], client=client(transport))


def read_gz(p: Path) -> list[dict]:
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def digests(d: Path) -> dict[str, str]:
    return {str(p.relative_to(d)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.rglob("*")) if p.is_file()}


# --- templates ---------------------------------------------------------------------------------------------


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
    with pytest.raises(SystemExit, match="no force-1 template"):
        force(src, t)
    assert not t.forced and not (src.parent / "forced").exists()


# --- selection and the forced pass ----------------------------------------------------------------------------


def test_selection_takes_responses_cut_at_the_cap_with_a_trace():
    def rec(item, finish, reasoning):
        return {"item_id": item, "sample": 0, "response": api_response(None, reasoning=reasoning, finish=finish)}

    raw = [rec("a", "length", "a trace"), rec("b", "length", None), rec("c", "length", "  \n"), rec("d", "stop", "a trace"),
           {"item_id": "e", "sample": 0, "response": None}, rec("f", "length", "another trace")]
    picked, no_trace = select(raw)
    assert [r["item_id"] for r in picked] == ["a", "f"] and no_trace == 2


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


def test_forced_pass_records_and_scores_completions(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    before = digests(src)
    source_raw = read_gz(src / "raw.jsonl.gz")
    assert force(src, t) == 0
    out = tmp_path / "runs" / "forced" / SOURCE

    assert len(t.forced) == 3  # items 0-2; item 3 has no trace
    for req, src_rec in zip(t.forced, source_raw[:3]):
        src_req = src_rec["request"]
        assert set(req) == {"model", "provider", "prompt", "max_tokens", "temperature", "top_p"}
        assert req["provider"] == src_req["provider"] == get_model("openai/gpt-oss-20b").provider
        assert (req["temperature"], req["top_p"], req["max_tokens"]) == (src_req["temperature"], src_req["top_p"], 4096)
        assert req["prompt"] == forced_prompt(src_req, src_rec["response"]["choices"][0]["message"]["reasoning"])

    raw = read_gz(out / "raw.jsonl.gz")
    assert [r["item_id"] for r in raw] == [r["item_id"] for r in source_raw[:3]]
    assert all(r["source_run_id"] == SOURCE and r["forced_template"] == "force-1" and r["run_id"] == f"forced/{SOURCE}" for r in raw)
    assert [r["source_cache_key"] for r in raw] == [r["cache_key"] for r in source_raw[:3]]
    assert all(r["prompt_hash"] == hashlib.sha256(r["request"]["prompt"].encode()).hexdigest()[:16] for r in raw)

    scored = read_gz(out / "scored.jsonl.gz")
    assert all(r["forced"] and r["forced_template"] == "force-1" and r["source_run_id"] == SOURCE for r in scored)
    assert [r["category"] for r in scored] == ["ok", "ok", "truncated"] and all(r["condition"] == "thinking-high-forced" for r in scored)
    assert scored[2]["reasoning_returned"] and scored[0]["parsed"] in ("YES", "C")

    m = json.loads((out / "manifest.json").read_text())
    assert m["run_id"] == f"forced/{SOURCE}" and m["status"] == "complete"
    assert m["source"]["run_id"] == SOURCE and m["source"]["raw_sha256"] == before["raw.jsonl.gz"]
    assert m["forced"] == {"template": "force-1", "endpoint": "https://openrouter.ai/api/v1/completions", "max_tokens": 4096}
    assert m["counts"] == {"selected": 3, "skipped_no_trace": 1, "responses": 3, "answered": 2, "still_reasoning": 1}
    assert m["price"]["completion"] == 0.14 and m["provider_routing"] == get_model("openai/gpt-oss-20b").provider
    assert m["spend"]["spent_usd"] == pytest.approx(0.003) and m["git"]["sha"] and m["versions"]["scorer"]
    report = (out / "REPORT.md").read_text()
    assert "## Forced final answers" in report and "2 answered and 1 went back to reasoning" in report

    assert digests(src) == before  # the source run is never modified; its records stay truncated
    assert [r["category"] for r in read_gz(src / "scored.jsonl.gz")][:4] == ["truncated"] * 4

    (out / "scored.jsonl.gz").unlink()
    assert score_main([str(out)]) == 0  # score.py re-scores a forced pass
    assert read_gz(out / "scored.jsonl.gz") == scored


def test_the_cost_guard_stops_at_the_cap(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    # each forced call reserves 1.25 x its worst case: the source's 900 prompt + 32,768 completion tokens, plus max_tokens
    worst = 1.25 * get_model("openai/gpt-oss-20b").pinned_price.cost(900 + 32768, 4096)
    cap = 0.001 + worst + 0.0005  # the second reservation fits after the first call's $0.001; the third does not
    root = src.parent.parent
    assert force_main([str(src), "--cap-usd", str(cap), "--cache-dir", str(root / "cache"), "--ledger", str(root / "LEDGER.md"),
                       "--concurrency", "1"], client=client(t)) == 2
    m = json.loads((src.parent / "forced" / SOURCE / "manifest.json").read_text())
    assert len(t.forced) == 2 and m["status"] == "stopped" and m["stop_reason"].startswith("cap:")
    assert m["spend"]["spent_usd"] == pytest.approx(0.002) and m["spend"]["spent_usd"] <= cap


def test_resume_sends_only_the_rest_and_the_cache_never_repays(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    out = src.parent / "forced" / SOURCE
    assert force(src, t, "--limit", "2") == 0 and len(t.forced) == 2
    assert force(src, t) == 0 and len(t.forced) == 3  # only the missing call
    assert force(src, t) == 0 and len(t.forced) == 3  # nothing left to send
    m = json.loads((out / "manifest.json").read_text())
    assert m["resumed_from"] == 3 and len(m["previous_invocations"]) == 2 and m["charged_usd_all_invocations"] == pytest.approx(0.003)
    with pytest.raises(SystemExit, match="different template, max_tokens"):
        force(src, t, "--max-tokens", "2048")
    for p in out.iterdir():
        p.unlink()
    assert force(src, t) == 0 and len(t.forced) == 3  # a fresh pass is answered from the cache
    m = json.loads((out / "manifest.json").read_text())
    assert m["cache_hits"] == 3 and m["charged_usd"] == 0 and m["counts"]["responses"] == 3


def test_a_ledger_row_per_live_invocation(tmp_path, key):
    t = Transport()
    src = source_run(tmp_path, t)
    assert force(src, t, "--budget-tag", "forced-test", "--budget-usd", "1", "--notes", "first pass") == 0
    rows = [r for r in ledger.rows(tmp_path / "LEDGER.md") if r["run_id"].startswith("forced/")]
    assert len(rows) == 1 and rows[0]["run_id"] == f"forced/{SOURCE}" and rows[0]["condition"] == "thinking-high-forced"
    assert rows[0]["model"] == "openai/gpt-oss-20b" and rows[0]["items"] == "3" and float(rows[0]["cost_usd"]) == pytest.approx(0.003)
    assert rows[0]["notes"] == "first pass status=complete" and ledger.spent(tmp_path / "LEDGER.md", "forced-test") == pytest.approx(0.003)


def test_the_key_is_never_written_anywhere(tmp_path, key):
    t = Transport()
    force(source_run(tmp_path, t), t)
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
    assert not (src.parent / "forced").exists()
