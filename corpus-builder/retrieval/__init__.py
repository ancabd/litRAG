"""Retriever registry. Same pattern as ingest.parsers: one module per retriever, imported lazily.

Names may carry a variant after a colon, which becomes the retriever's `model` option:
    bm25                 keyword search
    dense                embeddings, default model (nomic-embed-text v1.5)
    dense:bge-small      embeddings with BGE small
    hybrid               BM25 + dense (nomic), fused by rank
    hybrid:bge-small     BM25 + dense (BGE small)
The same string works everywhere: evaluate.py --retriever, the app's menus, the agent's search.

To add a retriever (e.g. a reranker):
  1. create retrieval/<name>.py with a subclass of Retriever
  2. add one line to RETRIEVERS
  3. python evaluate.py run --retriever <name>
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

from .base import Hit, Retriever, RetrieverUnavailable, load_chunks

RETRIEVERS: dict[str, str] = {
    "bm25": "retrieval.bm25:BM25Retriever",
    "dense": "retrieval.dense:DenseRetriever",
    "hybrid": "retrieval.hybrid:HybridRetriever",
}
WITH_MODEL = {"dense", "hybrid"}

# what the app's menus offer (any other valid name works too)
CHOICES = [
    {"name": "bm25", "label": "BM25 (keywords)"},
    {"name": "dense", "label": "Dense: nomic-embed-text v1.5"},
    {"name": "dense:bge-small", "label": "Dense: BGE small v1.5"},
    {"name": "hybrid", "label": "Hybrid: BM25 + nomic"},
    {"name": "hybrid:bge-small", "label": "Hybrid: BM25 + BGE small"},
]


def available() -> list[str]:
    return sorted(RETRIEVERS)


def choices() -> list[dict]:
    return [dict(c) for c in CHOICES]


def split_name(name: str) -> tuple[str, str | None]:
    base, _, variant = name.partition(":")
    return base, (variant or None)


def is_known(name: str) -> bool:
    """Valid retriever name, without loading anything heavy."""
    base, variant = split_name(name)
    if base not in RETRIEVERS:
        return False
    if variant is None:
        return True
    if base not in WITH_MODEL:
        return False
    from .dense import PRESETS
    return variant in PRESETS or "/" in variant


def get_retriever(name: str, **options) -> Retriever:
    base, variant = split_name(name)
    if not is_known(name):
        raise ValueError(f"Unknown retriever {name!r}. Available: {', '.join(c['name'] for c in CHOICES)}")
    if variant is not None:
        options.setdefault("model", variant)
    module_name, cls_name = RETRIEVERS[base].split(":")
    return getattr(importlib.import_module(module_name), cls_name)(**options)


def build_retriever(name: str, chunks: list[dict], cache_dir: Path | None = None, progress=None,
                    **options) -> Retriever:
    """Create and index a retriever; retrievers that cache (dense, hybrid) keep embeddings in `cache_dir`.
    `progress(done, total)` is called while chunks are embedded."""
    r = get_retriever(name, **options)
    if getattr(r, "uses_cache", False):
        if cache_dir is not None:
            r.set_cache_dir(cache_dir)
        if progress is not None:
            r.set_progress(progress)
    r.index(chunks)
    return r


def slug(name: str) -> str:
    """A retriever name usable in a folder name: dense:bge-small -> dense-bge-small."""
    return re.sub(r"[^A-Za-z0-9_.@-]+", "-", name)


__all__ = ["CHOICES", "Hit", "Retriever", "RETRIEVERS", "RetrieverUnavailable", "available", "build_retriever", "choices", "get_retriever",
           "is_known", "load_chunks", "slug", "split_name"]
