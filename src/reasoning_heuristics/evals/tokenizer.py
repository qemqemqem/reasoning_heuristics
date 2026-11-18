"""The models' own tokenizers, for cutting a reasoning trace at K tokens (evals/force.py --truncate-at and
--truncate-frac).

- **gpt-oss:** tiktoken's `o200k_harmony` (o200k_base's ranks plus the harmony special tokens). A trace is encoded
  with no special tokens allowed and `disallowed_special=()`, so any special-token text in it is plain text. The
  loaded ranks are checked against the pinned sha256 of `o200k_base.tiktoken`, which tiktoken checks on download.
- **Qwen3-32B and Qwen3-14B:** the HF `tokenizers` library, with `tokenizer.json` from Qwen/Qwen3-32B at a pinned
  commit. Qwen3-14B's `tokenizer.json` at its own commit is byte-identical (the same sha256, checked 2026-11-18), so
  both use the one file. It is downloaded on first use into data/cache/tokenizers/ (gitignored) and its sha256 is
  checked against the constant here, on download and on every load. Special-token text is encoded as plain text
  (`encode_special_tokens`).
- **Any other model is refused** (`UnknownTokenizer`).

Neither library is a dependency of the package (`pip install -e '.[force]'`), and only a budget pass needs one.

Re-tokenizing the returned trace text can differ slightly from the model's own token stream: the provider returns
text, not tokens, and the same text can have more than one tokenization. force.py records each trace's count by this
tokenizer (`trace_tokens`) beside the source usage's `reasoning_tokens` (`provider_reasoning_tokens`), so the
difference is visible.
"""

from __future__ import annotations

import base64
import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence

from reasoning_heuristics.evals.manifest import REPO

CACHE_DIR = REPO / "data" / "cache" / "tokenizers"
O200K_BASE_URL = "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken"
O200K_BASE_SHA256 = "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"  # tiktoken's own expected hash


@dataclass(frozen=True)
class HFFile:
    """A file of a Hugging Face model repo at a pinned commit, with its sha256."""

    repo: str
    revision: str
    filename: str
    sha256: str

    @property
    def url(self) -> str:
        return f"https://huggingface.co/{self.repo}/resolve/{self.revision}/{self.filename}"


# Qwen/Qwen3-32B at its main branch on 2026-11-18 (last modified 2025-07-26). Qwen/Qwen3-14B's tokenizer.json at
# 40c069824f4251a91eefaf281ebe4c544efd3e18 has the same sha256 and size (11,422,654 bytes).
QWEN3_TOKENIZER = HFFile("Qwen/Qwen3-32B", "9216db5781bf21249d130ec9da846c4624c16137", "tokenizer.json",
                         "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4")
MODEL_TOKENIZERS: dict[str, str | HFFile] = {
    "openai/gpt-oss-20b": "o200k_harmony",
    "openai/gpt-oss-120b": "o200k_harmony",
    "qwen/qwen3-32b": QWEN3_TOKENIZER,
    "qwen/qwen3-14b": QWEN3_TOKENIZER,
}


class UnknownTokenizer(ValueError):
    """A model with no tokenizer here."""


class TokenizerFileMismatch(RuntimeError):
    """A tokenizer file whose sha256 is not the pinned one."""


class Tokenizer(Protocol):
    def encode(self, text: str) -> list[int]: ...

    def decode(self, ids: Sequence[int]) -> str: ...

    def info(self) -> dict[str, Any]:
        """What the manifest records: `name`, `library`, `version`, `revision` (or None), `file` (its URL) and
        `sha256` (the file's)."""
        ...


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TiktokenTokenizer:
    """gpt-oss's o200k_harmony, from tiktoken."""

    def __init__(self, name: str = "o200k_harmony"):
        import tiktoken  # an optional dependency (the `force` extra)

        self.name, self.version = name, tiktoken.__version__
        self.enc = tiktoken.get_encoding(name)
        # o200k_harmony is o200k_base's ranks plus special tokens; the ranks, written out in the .tiktoken format,
        # are the pinned file byte for byte
        ranks = sorted(self.enc._mergeable_ranks.items(), key=lambda kv: kv[1])
        digest = sha256_bytes(b"".join(base64.b64encode(t) + b" " + str(r).encode() + b"\n" for t, r in ranks))
        if digest != O200K_BASE_SHA256:
            raise TokenizerFileMismatch(f"tiktoken {self.version} {name}: its ranks hash to {digest}, not the pinned "
                                        f"o200k_base.tiktoken {O200K_BASE_SHA256}")

    def encode(self, text: str) -> list[int]:
        return self.enc.encode(text, allowed_special=set(), disallowed_special=())

    def decode(self, ids: Sequence[int]) -> str:
        return self.enc.decode(list(ids))

    def info(self) -> dict[str, Any]:
        return {"name": self.name, "library": "tiktoken", "version": self.version, "revision": None,
                "file": O200K_BASE_URL, "sha256": O200K_BASE_SHA256}


def fetch(url: str) -> bytes:
    """GET a public file (tests replace this)."""
    req = urllib.request.Request(url, headers={"User-Agent": "reasoning-heuristics-tokenizer-fetch"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def cached_file(spec: HFFile, cache_dir: Path = CACHE_DIR) -> Path:
    """The pinned file in the cache, downloaded on first use. Its sha256 is checked on download (a mismatch is never
    written) and on every later use (a mismatch raises; delete the file to fetch it again)."""
    path = Path(cache_dir) / spec.repo.replace("/", "--") / spec.revision / spec.filename
    if path.exists():
        digest = sha256_bytes(path.read_bytes())
        if digest != spec.sha256:
            raise TokenizerFileMismatch(f"{path} has sha256 {digest}, not the pinned {spec.sha256}; delete it to download "
                                        "it again")
        return path
    data = fetch(spec.url)
    digest = sha256_bytes(data)
    if digest != spec.sha256:
        raise TokenizerFileMismatch(f"{spec.url} downloaded with sha256 {digest}, not the pinned {spec.sha256}; "
                                    "nothing was written")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return path


class HFTokenizer:
    """A tokenizer.json read with the HF `tokenizers` library."""

    def __init__(self, spec: HFFile, cache_dir: Path = CACHE_DIR):
        import tokenizers  # an optional dependency (the `force` extra)

        self.spec, self.version = spec, tokenizers.__version__
        self.tok = tokenizers.Tokenizer.from_file(str(cached_file(spec, cache_dir)))
        self.tok.encode_special_tokens = True  # special-token text in a trace is plain text

    def encode(self, text: str) -> list[int]:
        return self.tok.encode(text, add_special_tokens=False).ids

    def decode(self, ids: Sequence[int]) -> str:
        return self.tok.decode(list(ids), skip_special_tokens=False)

    def info(self) -> dict[str, Any]:
        return {"name": f"{self.spec.repo}/{self.spec.filename}", "library": "tokenizers", "version": self.version,
                "revision": self.spec.revision, "file": self.spec.url, "sha256": self.spec.sha256}


def spec_for(model: str) -> str | HFFile:
    """Which tokenizer is the model's own: a tiktoken encoding's name, or a pinned tokenizer.json. A model with none
    here is refused."""
    spec = MODEL_TOKENIZERS.get(model)
    if spec is None:
        raise UnknownTokenizer(f"{model}: no tokenizer (evals/tokenizer.py has {sorted(MODEL_TOKENIZERS)}); a trace can "
                               "only be cut at K tokens with the model's own tokenizer")
    return spec


def for_model(model: str, cache_dir: Path = CACHE_DIR) -> Tokenizer:
    """The model's own tokenizer, loaded (and on first use downloaded). A model with none here is refused."""
    spec = spec_for(model)
    return TiktokenTokenizer(spec) if isinstance(spec, str) else HFTokenizer(spec, cache_dir)


def identity(info: dict[str, Any]) -> dict[str, Any]:
    """What a resumed pass must share with the pass it resumes: the tokenizer's name, revision and file sha256 (not
    the library version)."""
    return {k: info.get(k) for k in ("name", "revision", "sha256")}


def prefix(tok: Tokenizer, ids: Sequence[int], k: int) -> tuple[str, int]:
    """The text of the first `k` of `ids`, and how many tokens it holds. A cut inside a UTF-8 character decodes to a
    replacement character at the end, so the cut moves back a token at a time while the text ends in one, at most 3
    tokens (a character is at most 4 bytes). If it still ends in one, the trace holds that character and the cut
    stays at `k`."""
    for kept in range(k, max(k - 3, 0) - 1, -1):
        text = tok.decode(ids[:kept])
        if not text.endswith("�"):
            return text, kept
    return tok.decode(ids[:k]), k
