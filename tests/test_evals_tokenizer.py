"""The models' own tokenizers (evals/tokenizer.py): the pinned Qwen3 tokenizer.json is downloaded once and checked
against its sha256 (the download mocked), a model without a tokenizer is refused, and, where the libraries and files
are already on this machine (never downloaded here), the real tokenizers encode special-token text as plain text and
cut a trace to a prefix of itself."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

import pytest

from reasoning_heuristics.evals import tokenizer as T


def spec(data: bytes) -> T.HFFile:
    return T.HFFile("Org/Model", "abc123", "tokenizer.json", hashlib.sha256(data).hexdigest())


def test_the_pinned_file_is_downloaded_once_and_checked(tmp_path, monkeypatch):
    calls = []

    def fetch(url):
        calls.append(url)
        return b'{"fake": true}'

    monkeypatch.setattr(T, "fetch", fetch)
    s = spec(b'{"fake": true}')
    path = T.cached_file(s, tmp_path)
    assert path == tmp_path / "Org--Model" / "abc123" / "tokenizer.json" and path.read_bytes() == b'{"fake": true}'
    assert calls == ["https://huggingface.co/Org/Model/resolve/abc123/tokenizer.json"]
    assert T.cached_file(s, tmp_path) == path and len(calls) == 1  # from the cache, its sha256 checked again


def test_a_download_with_the_wrong_sha256_is_refused_and_not_kept(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "fetch", lambda url: b"tampered")
    with pytest.raises(T.TokenizerFileMismatch, match="nothing was written"):
        T.cached_file(spec(b"genuine"), tmp_path)
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


def test_a_cached_file_that_changed_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "fetch", lambda url: b"genuine")
    path = T.cached_file(spec(b"genuine"), tmp_path)
    path.write_bytes(b"changed")
    with pytest.raises(T.TokenizerFileMismatch, match="delete it"):
        T.cached_file(spec(b"genuine"), tmp_path)


def test_qwen3_gets_its_pinned_file_through_the_same_check(tmp_path, monkeypatch):
    pytest.importorskip("tokenizers")
    monkeypatch.setattr(T, "fetch", lambda url: b"not the pinned file")
    with pytest.raises(T.TokenizerFileMismatch, match=T.QWEN3_TOKENIZER.sha256):
        T.for_model("qwen/qwen3-32b", cache_dir=tmp_path)
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


def test_each_model_has_its_own_tokenizer_and_others_are_refused():
    assert T.spec_for("openai/gpt-oss-20b") == T.spec_for("openai/gpt-oss-120b") == "o200k_harmony"
    assert T.spec_for("qwen/qwen3-32b") is T.spec_for("qwen/qwen3-14b") is T.QWEN3_TOKENIZER  # byte-identical files
    assert T.QWEN3_TOKENIZER.url == ("https://huggingface.co/Qwen/Qwen3-32B/resolve/9216db5781bf21249d130ec9da846c4624c16137/"
                                     "tokenizer.json")
    for model in ("deepseek/deepseek-r1-0528", "qwen/qwen3-30b-a3b", "qwen/qwen3-235b-a22b-thinking-2507"):
        with pytest.raises(T.UnknownTokenizer, match="no tokenizer"):
            T.for_model(model)
    assert T.identity({"name": "n", "library": "l", "version": "9", "revision": "r", "file": "f", "sha256": "s"}) == {
        "name": "n", "revision": "r", "sha256": "s"}  # a library upgrade alone does not stop a resume


def tiktoken_has_o200k() -> bool:
    """Whether tiktoken already holds o200k_base.tiktoken in its cache (its own cache rule), so nothing is downloaded."""
    cache = os.environ.get("TIKTOKEN_CACHE_DIR") or os.environ.get("DATA_GYM_CACHE_DIR") or os.path.join(
        tempfile.gettempdir(), "data-gym-cache")
    return (Path(cache) / hashlib.sha1(T.O200K_BASE_URL.encode()).hexdigest()).exists()


def test_gpt_oss_reads_special_token_text_as_plain_text():
    tiktoken = pytest.importorskip("tiktoken")
    if not tiktoken_has_o200k():
        pytest.skip("o200k_base.tiktoken is not cached here (a test downloads nothing)")
    tok = T.for_model("openai/gpt-oss-20b")
    text = "Check <|end|> then <|channel|>final, café 🙂."
    ids = tok.encode(text)
    assert not {200005, 200007} & set(ids) and tok.decode(ids) == text
    assert tok.info() == {"name": "o200k_harmony", "library": "tiktoken", "version": tiktoken.__version__, "revision": None,
                          "file": T.O200K_BASE_URL, "sha256": T.O200K_BASE_SHA256}
    for k in range(len(ids) + 1):  # every cut is a prefix of the text
        cut, kept = T.prefix(tok, ids, k)
        assert text.startswith(cut) and k - 3 <= kept <= k


def test_qwen3_reads_special_token_text_as_plain_text():
    tokenizers = pytest.importorskip("tokenizers")
    spec = T.QWEN3_TOKENIZER
    if not (T.CACHE_DIR / spec.repo.replace("/", "--") / spec.revision / spec.filename).exists():
        pytest.skip("the pinned Qwen3 tokenizer.json is not cached here (a test downloads nothing)")
    tok = T.for_model("qwen/qwen3-14b")
    text = "Check <|im_end|> then <|im_start|>user, café 🙂."
    ids = tok.encode(text)
    assert not {151644, 151645} & set(ids) and tok.decode(ids) == text  # <|im_start|>, <|im_end|>
    assert tok.info() == {"name": "Qwen/Qwen3-32B/tokenizer.json", "library": "tokenizers", "version": tokenizers.__version__,
                          "revision": spec.revision, "file": spec.url, "sha256": spec.sha256}
    for k in range(len(ids) + 1):
        cut, kept = T.prefix(tok, ids, k)
        assert text.startswith(cut) and k - 3 <= kept <= k
