"""Dense retrieval: embed every chunk once with a local model, then rank by cosine similarity.

    get_retriever("dense")              # nomic-embed-text v1.5 (the default)
    get_retriever("dense:bge-small")    # BGE small v1.5
    get_retriever("dense:hash")         # no model: hashed bag of words, for tests and offline smoke runs

The corpus is a few thousand chunks, so the index is a plain numpy matrix and a search is
one matrix-vector product; no vector database is needed.

Embeddings are cached on disk per chunk run and model, in
    data/chunks/<run>/embeddings/<model>/{vectors.npy, ids.json, meta.json}
keyed by a hash of each chunk's text, so building the index again (a new server process, a
re-chunked paper after adding a PDF) only embeds the chunks that changed.

Models run on the CPU unless a GPU is available. They need the optional dependencies:
    pip install -r requirements-dense.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .base import Hit, Retriever, RetrieverUnavailable


@dataclass(frozen=True)
class Preset:
    model: str                 # Hugging Face id (or "hash")
    query_prefix: str = ""     # what the model was trained to see before a query ...
    doc_prefix: str = ""       # ... and before a passage
    max_tokens: int = 512      # tokens of a chunk the model reads; the rest is cut off
    trust_remote_code: bool = False
    note: str = ""
    extra: dict = field(default_factory=dict)


PRESETS: dict[str, Preset] = {
    "nomic": Preset("nomic-ai/nomic-embed-text-v1.5", "search_query: ", "search_document: ", max_tokens=2048,
                    trust_remote_code=True,
                    note="137M parameters, 768 dims, reads whole chunks (we cap at 2048 tokens to bound memory)"),
    "bge-small": Preset("BAAI/bge-small-en-v1.5", "Represent this sentence for searching relevant passages: ", "",
                        max_tokens=512, note="33M parameters, 384 dims, fast; reads the first 512 tokens"),
    "hash": Preset("hash", max_tokens=10**9, note="no model: hashed bag of words, for tests and offline runs"),
}
DEFAULT_PRESET = "nomic"


def preset(name_or_model: str) -> tuple[str, Preset]:
    """A preset by short name, or any Hugging Face model id (no prefixes, 512 tokens)."""
    if name_or_model in PRESETS:
        return name_or_model, PRESETS[name_or_model]
    if "/" in name_or_model:
        return name_or_model, Preset(name_or_model)
    raise ValueError(f"Unknown embedding model {name_or_model!r}. Presets: {', '.join(PRESETS)}, "
                     "or a Hugging Face id like BAAI/bge-base-en-v1.5")


# ------------------------------------------------------------------ embedders

class HashEmbedder:
    """Deterministic stand-in for a model: lowercase words hashed into 512 buckets, L2-normalized."""

    dims = 512

    def encode(self, texts: list[str], batch_size: int = 32, progress=None) -> np.ndarray:
        out = np.zeros((len(texts), self.dims), dtype=np.float32)
        for i, t in enumerate(texts):
            for w in re.findall(r"[a-z0-9]+", t.lower()):
                out[i, int(hashlib.md5(w.encode()).hexdigest()[:8], 16) % self.dims] += 1.0
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        if progress and texts:
            progress(len(texts), len(texts))
        return out / np.where(norms == 0, 1, norms)

    def count_tokens(self, text: str) -> int:
        return len(text.split())


class SentenceTransformerEmbedder:
    """A sentence-transformers model, loaded once per process and shared."""

    _cache: dict[str, "SentenceTransformerEmbedder"] = {}
    _lock = threading.Lock()

    def __init__(self, p: Preset):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RetrieverUnavailable("Dense retrieval needs sentence-transformers: "
                                       "pip install -r corpus-builder/requirements-dense.txt") from exc
        try:
            self.model = SentenceTransformer(p.model, trust_remote_code=p.trust_remote_code,
                                             device=os.environ.get("LITRAG_DEVICE") or None)
        except ImportError as exc:  # e.g. nomic's custom code needs einops
            raise RetrieverUnavailable(f"{p.model} needs another package: {exc}. "
                                       "pip install -r corpus-builder/requirements-dense.txt") from exc
        except (OSError, ValueError) as exc:
            raise RetrieverUnavailable(f"Couldn't load {p.model}: {exc}. The first use downloads it from Hugging "
                                       "Face (a few hundred MB), so it needs an internet connection once.") from exc
        self.model.max_seq_length = p.max_tokens
        self.dims = self.model.get_sentence_embedding_dimension()

    @classmethod
    def get(cls, p: Preset) -> "SentenceTransformerEmbedder":
        with cls._lock:
            if p.model not in cls._cache:
                cls._cache[p.model] = cls(p)
            return cls._cache[p.model]

    def encode(self, texts: list[str], batch_size: int = 32, progress=None) -> np.ndarray:
        out = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            out.append(self.model.encode(batch, batch_size=batch_size, normalize_embeddings=True,
                                         convert_to_numpy=True, show_progress_bar=False).astype(np.float32))
            if progress:
                progress(min(start + batch_size, len(texts)), len(texts))
        return np.vstack(out) if out else np.zeros((0, self.dims), dtype=np.float32)

    def count_tokens(self, text: str) -> int:
        return len(self.model.tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"])


def make_embedder(p: Preset):
    return HashEmbedder() if p.model == "hash" else SentenceTransformerEmbedder.get(p)


# ------------------------------------------------------------------ retriever

def doc_text(c: dict) -> str:
    """What gets embedded for a chunk: title and section give the passage its context."""
    head = " - ".join(x for x in (c.get("title"), c.get("section")) if x)
    return f"{head}\n{c['text']}" if head else c["text"]


def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


class DenseRetriever(Retriever):
    name = "dense"
    uses_cache = True  # Library and the eval runners pass a cache folder (see set_cache_dir)

    def __init__(self, model: str = DEFAULT_PRESET, batch_size: int = 32, embedder=None, progress=None):
        self.preset_name, self.preset = preset(model)
        self.batch_size = batch_size
        self._embedder = embedder
        self.cache_dir: Path | None = None
        self.progress = progress
        self.ids: list[str] = []
        self.matrix: np.ndarray | None = None
        self.stats: dict = {}

    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = make_embedder(self.preset)
        return self._embedder

    def set_cache_dir(self, folder: Path | None) -> None:
        self.cache_dir = Path(folder) if folder else None

    def set_progress(self, progress) -> None:
        self.progress = progress

    def config(self) -> dict:
        p = self.preset
        return {"name": self.name, "model": p.model, "preset": self.preset_name, "query_prefix": p.query_prefix,
                "doc_prefix": p.doc_prefix, "max_tokens": p.max_tokens, "text": "title - section + chunk"}

    # cache: one folder per model, vectors aligned with ids, one text hash per id
    def _model_dir(self) -> Path | None:
        if self.cache_dir is None:
            return None
        slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", self.preset.model)
        return self.cache_dir / slug

    def _load_cache(self) -> dict[str, tuple[str, np.ndarray]]:
        d = self._model_dir()
        if d is None or not (d / "vectors.npy").exists():
            return {}
        try:
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            if meta.get("doc_prefix") != self.preset.doc_prefix or meta.get("max_tokens") != self.preset.max_tokens:
                return {}  # embedded differently: start over
            ids = json.loads((d / "ids.json").read_text(encoding="utf-8"))
            vectors = np.load(d / "vectors.npy")
            return {cid: (h, vectors[i]) for i, (cid, h) in enumerate(ids)}
        except (OSError, ValueError, KeyError):
            return {}

    def _save_cache(self, ids: list[str], hashes: list[str], matrix: np.ndarray) -> None:
        d = self._model_dir()
        if d is None:
            return
        d.mkdir(parents=True, exist_ok=True)
        np.save(d / "vectors.tmp.npy", matrix)
        os.replace(d / "vectors.tmp.npy", d / "vectors.npy")
        (d / "ids.json").write_text(json.dumps(list(zip(ids, hashes))), encoding="utf-8")
        (d / "meta.json").write_text(json.dumps({**self.config(), "dims": int(matrix.shape[1]) if matrix.size else 0,
                                                  "chunks": len(ids)}, indent=2), encoding="utf-8")

    def index(self, chunks: list[dict]) -> None:
        texts = [self.preset.doc_prefix + doc_text(c) for c in chunks]
        hashes = [_hash(t) for t in texts]
        cached = self._load_cache()
        todo = [i for i, (c, h) in enumerate(zip(chunks, hashes))
                if c["chunk_id"] not in cached or cached[c["chunk_id"]][0] != h]
        new = self.embedder.encode([texts[i] for i in todo], self.batch_size, self.progress) if todo else None
        rows, j = [], 0
        for i, c in enumerate(chunks):
            if j < len(todo) and todo[j] == i:
                rows.append(new[j])
                j += 1
            else:
                rows.append(cached[c["chunk_id"]][1])
        dims = getattr(self.embedder, "dims", 0) if not rows else len(rows[0])
        self.matrix = np.vstack(rows).astype(np.float32) if rows else np.zeros((0, dims), dtype=np.float32)
        self.ids = [c["chunk_id"] for c in chunks]
        if todo or not cached:
            self._save_cache(self.ids, hashes, self.matrix)
        self.stats = {"chunks": len(chunks), "embedded_now": len(todo), "from_cache": len(chunks) - len(todo)}

    def truncated(self, chunks: list[dict]) -> int:
        """How many chunks are longer than the model reads (their end is ignored)."""
        return sum(self.embedder.count_tokens(self.preset.doc_prefix + doc_text(c)) > self.preset.max_tokens
                   for c in chunks)

    def search(self, query: str, k: int = 10) -> list[Hit]:
        if self.matrix is None:
            raise RuntimeError("index() first")
        if not len(self.ids):
            return []
        q = self.embedder.encode([self.preset.query_prefix + query], 1)[0]
        scores = self.matrix @ q
        k = min(k, len(self.ids))
        top = np.argpartition(-scores, k - 1)[:k]
        top = top[np.argsort(-scores[top], kind="stable")]
        return [Hit(self.ids[i], float(scores[i]), r) for r, i in enumerate(top, 1)]


def cache_status(cache_dir: Path | None, model: str, chunks: list[dict]) -> dict:
    """How much of a chunk run is already embedded with `model` (a preset name), without loading the model."""
    r = DenseRetriever(model)
    r.set_cache_dir(cache_dir)
    cached = r._load_cache()
    ok = sum(1 for c in chunks
             if c["chunk_id"] in cached and cached[c["chunk_id"]][0] == _hash(r.preset.doc_prefix + doc_text(c)))
    return {"model": r.preset_name, "model_id": r.preset.model, "note": r.preset.note, "chunks": len(chunks),
            "embedded": ok, "ready": ok == len(chunks) and len(chunks) > 0}


def installed() -> bool:
    """Whether the packages for real models are installed (checked without importing them)."""
    import importlib.util
    return importlib.util.find_spec("sentence_transformers") is not None


__all__ = ["DEFAULT_PRESET", "cache_status", "installed", "DenseRetriever", "RetrieverUnavailable", "HashEmbedder", "PRESETS", "Preset", "doc_text", "preset"]
