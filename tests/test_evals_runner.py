"""The runner with the HTTP layer mocked: retries, cache hits, the cost cap, budgets, manifests,
resumption, re-scoring from disk, and the API key never leaving the environment."""

from __future__ import annotations

import gzip
import json
import urllib.error
from pathlib import Path

import pytest
from evals_helpers import ITEMS, api_response

from reasoning_heuristics.evals import cost as C
from reasoning_heuristics.evals import ledger
from reasoning_heuristics.evals.cache import ResponseCache, cache_key
from reasoning_heuristics.evals.client import FatalAPIError, HttpResponse, MissingKeyError, OpenRouterClient, usable
from reasoning_heuristics.evals.models import BUDGET_NOTICE, DIRECT_SYSTEM_PROMPT, Pricing, condition, get_model, request_body
from reasoning_heuristics.evals.run import main as run_main
from reasoning_heuristics.evals.score import main as score_main

SECRET = "sk-or-test-SECRET-do-not-write"
B4E1 = str(ITEMS / "smoke" / "B4C4_E1_smoke_s1.jsonl.gz")


class FakeTransport:
    """Answers chat completions like a model; can fail first, and records every call."""

    def __init__(self, fail_first: list[int] | None = None, cost: float = 0.0001, exc_first: int = 0,
                 charged_errors: list[float] | None = None):
        self.calls: list[dict] = []
        self.fail_first = list(fail_first or [])
        self.exc_first = exc_first
        self.cost = cost
        self.charged_errors = list(charged_errors or [])  # 200s with an error body that still report usage.cost
        self.key_usage = 1.0

    def __call__(self, method, url, headers, body, timeout):
        assert headers["Authorization"] == f"Bearer {SECRET}"
        if method == "GET":
            if url.endswith("/key"):
                self.key_usage += 0.25
                return HttpResponse(200, json.dumps({"data": {"usage": self.key_usage, "label": "secret label"}}).encode())
            return HttpResponse(200, json.dumps({"data": {"endpoints": []}}).encode())
        req = json.loads(body)
        self.calls.append(req)
        if self.exc_first:
            self.exc_first -= 1
            raise urllib.error.URLError("connection reset")
        if self.fail_first:
            return HttpResponse(self.fail_first.pop(0), b'{"error": {"message": "busy"}}', {})
        if self.charged_errors:
            cost = self.charged_errors.pop(0)
            body = {"choices": [{"finish_reason": "error", "error": {"code": 502, "message": "upstream died"},
                                 "message": {"content": None}}], "usage": {"completion_tokens": 900, "cost": cost}}
            return HttpResponse(200, json.dumps(body).encode())
        prompt = req["messages"][-1]["content"]
        content = "ANSWER: C" if '"ANSWER: <letter>"' in prompt else "ANSWER: YES"
        resp = api_response(content, cost=self.cost, model=req["model"], provider="FakeProvider",
                            gen_id=f"gen-{len(self.calls)}")
        return HttpResponse(200, json.dumps(resp).encode())


@pytest.fixture
def key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", SECRET)


def client(transport):
    return OpenRouterClient(transport, sleep=lambda s: None)


def run(tmp_path, transport, *extra, out="run1", items=B4E1, limit=6):
    args = ["--items", items, "--model", "openai/gpt-oss-20b", "--out", str(tmp_path / out), "--cap-usd", "1",
            "--provider", "fakeprovider", "--cache-dir", str(tmp_path / "cache"), "--ledger", str(tmp_path / "LEDGER.md"),
            "--concurrency", "3", *([] if limit is None else ["--limit", str(limit)]), *extra]
    return run_main(args, client=client(transport))


def read_gz(p: Path) -> list[dict]:
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


# --- client ------------------------------------------------------------------------------------------------


def test_retries_with_backoff_then_succeeds(key):
    sleeps = []
    t = FakeTransport(fail_first=[503, 429])
    c = OpenRouterClient(t, sleep=sleeps.append)
    res = c.chat({"model": "m", "messages": [{"role": "user", "content": 'x "ANSWER: YES"'}]})
    assert res.ok and res.attempts == 3 and len(res.errors) == 2 and len(sleeps) == 2
    assert 0 < sleeps[0] <= sleeps[1] * 2  # exponential with jitter


def test_network_errors_and_errors_inside_200_are_retried(key):
    t = FakeTransport(exc_first=2)
    assert client(t).chat({"model": "m", "messages": [{"role": "user", "content": "q"}]}).attempts == 3

    class ErrorBody(FakeTransport):
        def __call__(self, method, url, headers, body, timeout):
            if len(self.calls) == 0:
                self.calls.append({})
                return HttpResponse(200, json.dumps({"choices": [{"finish_reason": "error", "error": {"code": 502}}]}).encode())
            return super().__call__(method, url, headers, body, timeout)

    res = client(ErrorBody()).chat({"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert res.ok and res.attempts == 2


def test_exhausted_retries_return_an_error_not_an_exception(key):
    res = OpenRouterClient(FakeTransport(fail_first=[503] * 10), max_attempts=3, sleep=lambda s: None).chat(
        {"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert not res.ok and res.attempts == 3 and "503" in res.error


@pytest.mark.parametrize("status", [400, 401, 402, 403, 404])
def test_fatal_statuses_are_not_retried(key, status):
    t = FakeTransport(fail_first=[status])
    with pytest.raises(FatalAPIError):
        client(t).chat({"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert len(t.calls) == 1


def test_key_is_read_from_the_environment_at_call_time(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    c = client(FakeTransport())
    with pytest.raises(MissingKeyError):
        c.chat({"model": "m", "messages": []})
    monkeypatch.setenv("OPENROUTER_API_KEY", SECRET)
    assert c.chat({"model": "m", "messages": [{"role": "user", "content": "q"}]}).ok
    assert SECRET not in json.dumps(vars(c), default=str)


# --- requests and conditions -------------------------------------------------------------------------------


def test_thinking_and_direct_requests():
    q = get_model("qwen/qwen3-32b")
    th = request_body(q, condition(q, "thinking"), "PROMPT", {"order": ["p"], "allow_fallbacks": False})
    assert th["max_tokens"] == 32768 and th["reasoning"] == {"effort": "high"} and th["messages"] == [{"role": "user", "content": "PROMPT"}]
    assert th["provider"] == {"order": ["p"], "allow_fallbacks": False} and th["temperature"] == 0.6
    di = request_body(q, condition(q, "direct"), "PROMPT", None)
    assert di["max_tokens"] == 1024 and di["reasoning"] == {"enabled": False}
    assert di["messages"][0] == {"role": "system", "content": DIRECT_SYSTEM_PROMPT}
    g = get_model("openai/gpt-oss-20b")
    assert request_body(g, condition(g, "thinking", "low"), "P", None)["reasoning"] == {"effort": "low"}
    with pytest.raises(ValueError, match="cannot turn reasoning off"):
        condition(g, "direct")


def test_samples_are_separate_cache_keys():
    g = get_model("openai/gpt-oss-20b")
    body = request_body(g, condition(g, "thinking"), "P", None)
    assert cache_key(body, 0) != cache_key(body, 1)
    assert cache_key(body, 0) == cache_key(json.loads(json.dumps(body)), 0)
    other = request_body(g, condition(g, "thinking"), "P", {"order": ["x"], "allow_fallbacks": False})
    assert cache_key(other, 0) != cache_key(body, 0)  # provider routing is part of the key


# --- runs ------------------------------------------------------------------------------------------------------------


def test_run_writes_raw_scored_report_manifest_and_ledger(tmp_path, key):
    t = FakeTransport()
    assert run(tmp_path, t) == 0
    out = tmp_path / "run1"
    m = json.loads((out / "manifest.json").read_text())
    assert m["status"] == "complete" and m["model_requested"] == "openai/gpt-oss-20b"
    assert m["models_returned"] == ["openai/gpt-oss-20b"] and m["providers_served"] == {"FakeProvider": 6}
    assert m["provider_routing"] == {"order": ["fakeprovider"], "allow_fallbacks": False, "require_parameters": True}
    assert m["condition"]["max_tokens"] == 32768 and m["condition"]["reasoning"] == {"effort": "high"}
    assert list(m["items"]["files"]) == ["data/items/smoke/B4C4_E1_smoke_s1.jsonl.gz"]
    assert all(len(h) == 64 for h in m["items"]["files"].values())
    assert m["git"]["sha"] and m["versions"]["python-sat"] and m["versions"]["pyetr"] == "1.0.0"
    assert m["versions"]["scorer"].startswith("scorer-") and m["spend"]["spent_usd"] == pytest.approx(0.0006)
    raw = read_gz(out / "raw.jsonl.gz")
    assert len(raw) == 6 and all(r["request"]["messages"][-1]["content"] for r in raw)
    assert all(r["response"]["usage"]["cost"] == 0.0001 for r in raw)
    scored = read_gz(out / "scored.jsonl.gz")
    need = {"item_id", "content_hash", "model", "category", "parsed", "answer_key", "outcome_class", "correct",
            "reasoning_tokens", "completion_tokens", "truncated", "scorer_version", "pre_answer_tokens", "condition"}
    assert all(need <= set(r) for r in scored) and {r["category"] for r in scored} == {"ok"}
    assert "Response categories" in (out / "REPORT.md").read_text()
    rows = ledger.rows(tmp_path / "LEDGER.md")
    assert len(rows) == 1 and rows[0]["run_id"] == "run1" and float(rows[0]["cost_usd"]) == pytest.approx(0.0006)


def test_rerun_hits_the_cache_and_never_repays(tmp_path, key):
    t = FakeTransport()
    run(tmp_path, t)
    n = len(t.calls)
    run(tmp_path, t, out="run2")
    assert len(t.calls) == n  # nothing sent
    m = json.loads((tmp_path / "run2" / "manifest.json").read_text())
    assert m["cache_hits"] == 6 and m["charged_usd"] == 0 and m["status"] == "complete"
    assert all(r["from_cache"] for r in read_gz(tmp_path / "run2" / "raw.jsonl.gz"))
    assert len(ledger.rows(tmp_path / "LEDGER.md")) == 1  # a cache-only run costs nothing and books nothing


def test_resume_into_the_same_directory_sends_only_the_rest(tmp_path, key):
    t = FakeTransport()
    run(tmp_path, t, "--no-cache", limit=3)
    run(tmp_path, t, "--no-cache", limit=6)
    assert len(t.calls) == 6
    assert len(read_gz(tmp_path / "run1" / "raw.jsonl.gz")) == 6
    m = json.loads((tmp_path / "run1" / "manifest.json").read_text())
    assert m["resumed_from"] == 3 and len(m["previous_invocations"]) == 1
    assert m["previous_invocations"][0]["git"]["sha"] and m["previous_invocations"][0]["charged_usd"] == pytest.approx(0.0003)
    assert m["charged_usd"] == pytest.approx(0.0003) and m["charged_usd_all_invocations"] == pytest.approx(0.0006)
    with pytest.raises(SystemExit, match="different condition"):
        run(tmp_path, t, "--no-cache", "--effort", "low", limit=6)


def test_a_body_cut_short_is_retried(key):
    """Seen live: http.client.IncompleteRead escaped the retry loop and stopped run (a)."""
    import http.client

    class CutShort(FakeTransport):
        def __call__(self, method, url, headers, body, timeout):
            if not self.calls:
                self.calls.append({})
                raise http.client.IncompleteRead(b"{\"id\": \"gen-", 1991)
            return super().__call__(method, url, headers, body, timeout)

    res = client(CutShort()).chat({"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert res.ok and res.attempts == 2 and "IncompleteRead" in res.errors[0]


def test_cap_stops_cleanly_before_the_spend_would_pass_it(tmp_path, key):
    g = get_model("openai/gpt-oss-20b")
    # each reservation is >= 1.25 * 32768 * $0.13/M = $0.00533; each call then costs $0.005
    t = FakeTransport(cost=0.005)
    cap = 0.012  # two calls fit ($0.010); a third reservation ($0.010 + $0.0053) would pass the cap
    args = ["--items", B4E1, "--model", g.slug, "--out", str(tmp_path / "capped"), "--cap-usd", str(cap), "--provider", "fp",
            "--cache-dir", str(tmp_path / "c"), "--ledger", str(tmp_path / "L.md"), "--concurrency", "1", "--limit", "10"]
    assert run_main(args, client=client(t)) == 2
    m = json.loads((tmp_path / "capped" / "manifest.json").read_text())
    assert m["status"] == "stopped" and m["stop_reason"].startswith("cap:")
    assert len(t.calls) == 2 and m["spend"]["spent_usd"] == pytest.approx(0.010) and m["spend"]["spent_usd"] <= cap
    assert len(read_gz(tmp_path / "capped" / "scored.jsonl.gz")) == 2


def test_budget_tag_caps_a_run_by_the_ledger_total(tmp_path, key):
    led = tmp_path / "LEDGER.md"
    ledger.append(led, date="2026-11-17", run_id="probe", model="m", condition="probe", items=1, cost_usd=2.99, budget_tag="mine")
    t = FakeTransport()
    with pytest.raises(C.CapReached):
        run(tmp_path, t, "--budget-tag", "mine", "--budget-usd", "2.99")
    assert run(tmp_path, t, "--budget-tag", "mine", "--budget-usd", "3.00") in (0, 2)
    m = json.loads((tmp_path / "run1" / "manifest.json").read_text())
    assert m["cap_usd"] == pytest.approx(0.01) and m["budget_spent_before_usd"] == pytest.approx(2.99)
    assert ledger.spent(led, "mine") <= 3.00 + 1e-9


def test_price_mismatch_stops_the_run(tmp_path, key):
    t = FakeTransport(cost=5.0)  # far above any reserved worst case
    assert run(tmp_path, t, limit=4) == 2
    m = json.loads((tmp_path / "run1" / "manifest.json").read_text())
    assert m["status"] == "stopped" and "worst case" in m["stop_reason"]


def test_fatal_error_stops_the_run_and_is_recorded(tmp_path, key):
    t = FakeTransport(fail_first=[402])
    assert run(tmp_path, t, "--concurrency", "1", limit=3) == 2
    m = json.loads((tmp_path / "run1" / "manifest.json").read_text())
    assert m["status"] == "stopped" and "402" in m["stop_reason"]
    scored = read_gz(tmp_path / "run1" / "scored.jsonl.gz")
    assert scored[0]["category"] == "api_error"


def test_unpinned_model_is_refused_without_no_pin(tmp_path, key, monkeypatch):
    import dataclasses

    from reasoning_heuristics.evals import models as M

    monkeypatch.setitem(M.MODELS, "openai/gpt-oss-20b", dataclasses.replace(M.MODELS["openai/gpt-oss-20b"], provider=None))
    args = ["--items", B4E1, "--model", "openai/gpt-oss-20b", "--out", str(tmp_path / "x"), "--cap-usd", "1", "--limit", "1",
            "--cache-dir", str(tmp_path / "c"), "--ledger", str(tmp_path / "L.md")]
    with pytest.raises(SystemExit, match="no pinned provider"):
        run_main(args, client=client(FakeTransport()))
    assert run_main(args + ["--no-pin"], client=client(FakeTransport())) == 0


def test_pinned_routing_and_completion_limit(tmp_path, key):
    t = FakeTransport()
    args = ["--items", B4E1, "--model", "qwen/qwen3-32b", "--out", str(tmp_path / "p"), "--cap-usd", "1", "--limit", "1",
            "--cache-dir", str(tmp_path / "c"), "--ledger", str(tmp_path / "L.md")]
    assert run_main(args, client=client(t)) == 0
    assert t.calls[0]["provider"] == {"order": ["deepinfra/fp8/flex"], "allow_fallbacks": False,
                                      "require_parameters": True, "quantizations": ["fp8"]}
    m = json.loads((tmp_path / "p" / "manifest.json").read_text())
    assert m["price"]["completion"] == 0.224  # the pinned endpoint's price, not the list price
    with pytest.raises(SystemExit, match="completion limit"):
        run_main(["--items", B4E1, "--model", "qwen/qwen3-235b-a22b-thinking-2507", "--out", str(tmp_path / "q"),
                  "--cap-usd", "1", "--limit", "1"], client=client(t))


def test_dry_run_sends_nothing_and_writes_nothing(tmp_path, capsys):
    args = ["--items", str(ITEMS / "smoke"), "--model", "qwen/qwen3-32b", "--condition", "direct", "--out", str(tmp_path / "d"),
            "--dry-run", "--exclude-eval", "E8"]
    assert run_main(args) == 0
    text = capsys.readouterr().out
    assert "| **Total** | | **254** |" in text and not (tmp_path / "d").exists()


def test_dry_run_from_a_runs_measured_tokens(tmp_path, key, capsys):
    run(tmp_path, FakeTransport(), limit=4)  # every fake response reports 1,200 completion tokens
    capsys.readouterr()
    args = ["--items", B4E1, "--model", "openai/gpt-oss-20b", "--out", str(tmp_path / "d"), "--dry-run", "--limit", "4",
            "--tokens-from", str(tmp_path / "run1")]
    assert run_main(args) == 0
    text = capsys.readouterr().out
    assert "Output tokens (measured)" in text and "| B4/C4 | E1 | 4 | " in text and "| 4,800 |" in text


def test_direct_run_records_the_system_instruction(tmp_path, key):
    t = FakeTransport()
    args = ["--items", B4E1, "--model", "qwen/qwen3-32b", "--condition", "direct", "--out", str(tmp_path / "direct"),
            "--cap-usd", "1", "--provider", "fp", "--cache-dir", str(tmp_path / "c"), "--ledger", str(tmp_path / "L.md"), "--limit", "2"]
    assert run_main(args, client=client(t)) == 0
    m = json.loads((tmp_path / "direct" / "manifest.json").read_text())
    assert m["condition"]["system_prompt"] == DIRECT_SYSTEM_PROMPT and m["condition"]["label"] == "direct"
    assert t.calls[0]["messages"][0]["content"] == DIRECT_SYSTEM_PROMPT and t.calls[0]["max_tokens"] == 1024


def test_score_command_rescores_from_disk_and_refuses_item_drift(tmp_path, key):
    run(tmp_path, FakeTransport())
    out = tmp_path / "run1"
    before = read_gz(out / "scored.jsonl.gz")
    (out / "scored.jsonl.gz").unlink()
    assert score_main([str(out)]) == 0
    after = read_gz(out / "scored.jsonl.gz")
    assert [r["parsed"] for r in after] == [r["parsed"] for r in before]
    m = json.loads((out / "manifest.json").read_text())
    m["items"]["files"]["data/items/smoke/B4C4_E1_smoke_s1.jsonl.gz"] = "0" * 64
    (out / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(SystemExit, match="changed since the run"):
        score_main([str(out)])


def test_the_key_is_never_written_anywhere(tmp_path, key):
    run(tmp_path, FakeTransport())
    for p in tmp_path.rglob("*"):
        if p.is_file():
            data = gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes()
            assert SECRET.encode() not in data, p


def test_cache_import_from_runs(tmp_path, key):
    run(tmp_path, FakeTransport())
    fresh = ResponseCache(tmp_path / "fresh")
    assert fresh.import_runs([tmp_path / "run1" / "raw.jsonl.gz"]) == 6
    raw = read_gz(tmp_path / "run1" / "raw.jsonl.gz")
    assert fresh.get(raw[0]["cache_key"])["response"] == raw[0]["response"]


def test_cost_guard_reservations():
    g = C.CostGuard(0.01, Pricing(0.0, 0.1, "test"), 1000, safety=1.0)  # worst case 0.0001 + prompt
    w = g.worst_case("")
    n = 0
    while g.reserve(w):
        n += 1
    assert abs(n - 0.01 / w) <= 1 and g.refused == 1 and g.reserved <= g.cap
    g.settle(w, {"cost": w / 2})
    assert g.spent == pytest.approx(w / 2)
    with pytest.raises(C.CapReached):
        C.CostGuard(0, Pricing(0, 0, "t"), 1)


def test_probe_records_listing_reasoning_and_thinking_off(tmp_path, key):
    from reasoning_heuristics.evals.probe import main as probe_main

    listing = {"data": {"id": "qwen/qwen3-32b", "endpoints": [
        {"provider_name": "Alpha", "tag": "alpha/bf16", "quantization": "bf16", "context_length": 40960,
         "max_completion_tokens": 40960, "pricing": {"prompt": "0.0000001", "completion": "0.0000003"},
         "supported_parameters": ["reasoning", "top_k", "seed"], "status": 0}]}}

    class ProbeTransport(FakeTransport):
        def __call__(self, method, url, headers, body, timeout):
            assert headers["Authorization"] == f"Bearer {SECRET}"
            if method == "GET":
                return HttpResponse(200, json.dumps(listing).encode())
            req = json.loads(body)
            self.calls.append(req)
            off = req.get("reasoning") in ({"enabled": False}, {"effort": "none"}) or req["messages"][0]["content"].endswith("/no_think")
            resp = api_response("42", reasoning=None if off else "17 plus 25 is 42.", reasoning_tokens=0 if off else 12,
                                provider="Alpha", model=req["model"], cost=0.00001)
            return HttpResponse(200, json.dumps(resp).encode())

    t = ProbeTransport()
    led = tmp_path / "L.md"
    assert probe_main(["--model", "qwen/qwen3-32b", "--out", str(tmp_path / "p"), "--cap-usd", "0.05", "--ledger", str(led),
                       "--budget-tag", "mine", "--budget-usd", "3"], client=client(t)) == 0
    assert len(t.calls) == 4 and all(c["provider"] == {"order": ["alpha/bf16"], "allow_fallbacks": False} for c in t.calls)
    md = (tmp_path / "p" / "PROBES.md").read_text()
    assert "| `alpha/bf16` | Alpha | bf16 | 40960 |" in md and "| `alpha/bf16` | off | Alpha | 0 chars | 0 |" in md
    results = json.loads((tmp_path / "p" / "probes.json").read_text())
    on = next(p for p in results["models"]["qwen/qwen3-32b"]["probed"] if p["variant"] == "on")
    assert on["summary"]["reasoning_returned"] and not on["summary"]["thinking_off_honoured"]
    assert ledger.spent(led, "mine") == pytest.approx(0.00004)


# --- follow-ups: charged failures, key usage, scoring against the items at the run's SHA ---------------------


def test_charged_failed_attempts_are_booked(tmp_path, key):
    t = FakeTransport(charged_errors=[0.002], cost=0.0001)
    assert run(tmp_path, t, "--concurrency", "1", limit=2) == 0
    raw = read_gz(tmp_path / "run1" / "raw.jsonl.gz")
    assert raw[0]["failed_attempt_costs"] == [0.002] and raw[0]["charged_usd"] == pytest.approx(0.0021)
    assert raw[1]["failed_attempt_costs"] == [] and raw[1]["charged_usd"] == pytest.approx(0.0001)
    m = json.loads((tmp_path / "run1" / "manifest.json").read_text())
    assert m["spend"]["spent_usd"] == pytest.approx(0.0022) and m["spend"]["failed_attempt_cost_usd"] == pytest.approx(0.002)
    assert m["charged_usd"] == pytest.approx(0.0022)
    assert float(ledger.rows(tmp_path / "LEDGER.md")[0]["cost_usd"]) == pytest.approx(0.0022)


def test_no_retry_when_a_charged_failure_leaves_no_room_under_the_cap(tmp_path, key):
    # one reservation is about $0.0053; the failed attempt is charged $0.005, so a retry could pass $0.008
    t = FakeTransport(charged_errors=[0.005, 0.005])
    args = ["--items", B4E1, "--model", "openai/gpt-oss-20b", "--out", str(tmp_path / "c"), "--cap-usd", "0.008",
            "--provider", "fp", "--cache-dir", str(tmp_path / "cache"), "--ledger", str(tmp_path / "L.md"),
            "--concurrency", "1", "--limit", "3"]
    assert run_main(args, client=client(t)) == 2
    m = json.loads((tmp_path / "c" / "manifest.json").read_text())
    assert len(t.calls) == 1 and m["status"] == "stopped" and m["stop_reason"].startswith("cap:")
    assert m["spend"]["spent_usd"] == pytest.approx(0.005) and m["spend"]["spent_usd"] <= 0.008


def test_manifest_records_the_key_usage_counter_but_nothing_else_about_the_key(tmp_path, key):
    run(tmp_path, FakeTransport(), limit=2)
    m = json.loads((tmp_path / "run1" / "manifest.json").read_text())
    assert m["key_usage"]["before"] == {"usage": 1.25} and m["key_usage"]["after"] == {"usage": 1.5}
    assert m["key_usage"]["delta_usd"] == pytest.approx(0.25)
    assert "secret label" not in (tmp_path / "run1" / "manifest.json").read_text()


def test_rescore_against_the_items_at_the_runs_git_sha(tmp_path, key, monkeypatch):
    run(tmp_path, FakeTransport(), limit=3)
    out = tmp_path / "run1"
    before = read_gz(out / "scored.jsonl.gz")
    from reasoning_heuristics.evals import score as S

    monkeypatch.setattr(S, "sha256_file", lambda p: "f" * 64)  # the working-tree items were regenerated
    with pytest.raises(SystemExit, match="changed since the run"):
        score_main([str(out)])
    assert score_main([str(out), "--items-at-run-sha"]) == 0  # git show <sha>:<path>, hash-checked
    assert [r["parsed"] for r in read_gz(out / "scored.jsonl.gz")] == [r["parsed"] for r in before]
    assert json.loads((out / "scoring.json").read_text())["items_source"].startswith("git ")
    m = json.loads((out / "manifest.json").read_text())
    m["items"]["files"]["data/items/smoke/B4C4_E1_smoke_s1.jsonl.gz"] = "0" * 64
    (out / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(SystemExit, match="not the run's"):
        score_main([str(out), "--items-at-run-sha"])


def test_the_budget_notice_variant():
    cfg = get_model("openai/gpt-oss-20b")
    plain, notice = condition(cfg, "thinking", "high"), condition(cfg, "thinking", "high", budget_notice=True)
    assert (plain.label, notice.label) == ("thinking-high", "thinking-high+budget")
    assert notice.prompt_suffix == BUDGET_NOTICE.format(max_tokens=32768) and "32,768 tokens" in notice.prompt_suffix
    assert "variant" not in plain.to_json() and notice.to_json()["variant"] == "budget"  # old manifests unchanged
    body = request_body(cfg, notice, "Is it so?", None)
    assert body["messages"] == [{"role": "user", "content": "Is it so?" + notice.prompt_suffix}]
    assert {k: v for k, v in body.items() if k != "messages"} == {k: v for k, v in request_body(cfg, plain, "Is it so?", None).items()
                                                                  if k != "messages"}  # nothing else differs
    assert "16,384 tokens" in condition(cfg, "thinking", "high", 16384, budget_notice=True).prompt_suffix
    with pytest.raises(ValueError):
        condition(get_model("qwen/qwen3-32b"), "direct", None, budget_notice=True)


# --- empty replies without usage (a provider failure, not an answer) -----------------------------------------------

EMPTY_REPLY = {"id": "gen-empty", "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": ""}}]}


class EmptyFirst(FakeTransport):
    """The first `n` POSTs come back as an empty reply with no usage, as DeepInfra's gpt-oss-120b endpoint sent 9 of
    284 forced calls on 2026-11-18."""

    def __init__(self, n: int = 1, **kw):
        super().__init__(**kw)
        self.empty = n

    def __call__(self, method, url, headers, body, timeout):
        if method == "POST" and self.empty:
            self.empty -= 1
            self.calls.append(json.loads(body))
            return HttpResponse(200, json.dumps(EMPTY_REPLY).encode())
        return super().__call__(method, url, headers, body, timeout)


def test_an_empty_reply_without_usage_is_retried(key):
    res = client(EmptyFirst()).chat({"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert res.ok and res.attempts == 2 and "empty reply without usage" in res.errors[0]


def test_a_reply_without_usage_but_with_output_is_kept(key):
    class NoUsage(FakeTransport):
        def __call__(self, method, url, headers, body, timeout):
            if method == "POST":
                self.calls.append(json.loads(body))
                return HttpResponse(200, json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": "ANSWER: YES"}}]}).encode())
            return super().__call__(method, url, headers, body, timeout)

    res = client(NoUsage()).chat({"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert res.ok and res.attempts == 1


def test_usable():
    assert usable(api_response("ANSWER: YES")) and not usable(None) and not usable(EMPTY_REPLY)
    assert usable({"choices": [{"finish_reason": "stop", "message": {"content": "x"}}]})  # output, no usage: kept
    assert usable({"choices": [{"finish_reason": "length", "message": {"content": None, "reasoning": "hm"}}]})
    assert not usable({"choices": []}) and not usable({"error": {"code": 502}})


def test_a_resume_resends_a_stored_empty_reply_and_the_cache_does_not_serve_it(tmp_path, key):
    """Records written before the client retried empty replies: the resume and the cache must not count them done."""
    t = FakeTransport()
    run(tmp_path, t, limit=3)
    raw_path = tmp_path / "run1" / "raw.jsonl.gz"
    recs = read_gz(raw_path)
    recs[0]["response"] = EMPTY_REPLY
    with gzip.open(raw_path, "wt", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in recs)
    cache = ResponseCache(tmp_path / "cache")
    cache.put(recs[0]["cache_key"], {"request": recs[0]["request"], "response": EMPTY_REPLY, "sample": 0, "source": "old"})
    sent = len(t.calls)
    run(tmp_path, t, limit=3)
    assert len(t.calls) == sent + 1  # only the emptied item is sent again, and not served from the cache
    again = read_gz(raw_path)
    assert len(again) == 3 and all(usable(r["response"]) for r in again)
    assert usable(cache.get(recs[0]["cache_key"])["response"])


ACCOUNT = "user_2abcDEF345ghiJKL678mnoPQR9"  # an OpenRouter account id, as error bodies carry it (made up)


class AccountInErrors(FakeTransport):
    """Fails with bodies that carry the account id, the way OpenRouter's errors do, then answers."""

    def __init__(self, statuses: list[int]):
        super().__init__()
        self.statuses = list(statuses)

    def __call__(self, method, url, headers, body, timeout):
        if self.statuses:
            self.calls.append({})
            status = self.statuses.pop(0)
            err = {"error": {"message": "Provider returned error", "code": status,
                             "metadata": {"raw": "upstream timeout", "provider_name": "P", "is_byok": False}},
                   "user_id": ACCOUNT}
            return HttpResponse(200 if status == 200 else status, json.dumps(err).encode())
        return super().__call__(method, url, headers, body, timeout)


def test_the_account_id_is_redacted_from_retried_errors(key):
    res = client(AccountInErrors([504, 200])).chat({"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert res.ok and len(res.errors) == 2
    assert all(ACCOUNT not in e and ACCOUNT[:8] not in e for e in res.errors)
    assert "user_[redacted]" in res.errors[0]


def test_the_account_id_is_redacted_from_fatal_errors(key):
    with pytest.raises(FatalAPIError) as exc:
        client(AccountInErrors([402])).chat({"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert ACCOUNT not in str(exc.value) and ACCOUNT[:8] not in str(exc.value) and "402" in str(exc.value)


def test_the_account_id_is_redacted_from_exhausted_retries(key):
    res = OpenRouterClient(AccountInErrors([503] * 3), max_attempts=3, sleep=lambda s: None).chat(
        {"model": "m", "messages": [{"role": "user", "content": "q"}]})
    assert not res.ok and ACCOUNT[:8] not in res.error and all(ACCOUNT[:8] not in e for e in res.errors)


@pytest.mark.parametrize("text", [
    f'{{"user_id":"{ACCOUNT}"}}', f'{{"user_id": "{ACCOUNT}"}}', f"account {ACCOUNT} over its limit",
    f'{{"user_id":"{ACCOUNT}"}}'[:24],  # cut mid-id by a length limit: the stub must go too
])
def test_redact_removes_account_ids(text):
    from reasoning_heuristics.evals.client import redact
    out = redact(text)
    assert ACCOUNT[:8] not in out and "user_2a" not in out
