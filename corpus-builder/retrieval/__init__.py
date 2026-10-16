"""Retriever registry. Same pattern as ingest.parsers: one module per retriever, imported lazily.

To add a retriever (dense, hybrid, reranked, ...):
  1. create retrieval/<name>.py with a subclass of Retriever
  2. add one line to RETRIEVERS
  3. python evaluate.py run --retriever <name>
"""
from __future__ import annotations

import importlib

from .base import Hit, Retriever, load_chunks

RETRIEVERS: dict[str, str] = {
    "bm25": "retrieval.bm25:BM25Retriever",
    # "dense":  "retrieval.dense:DenseRetriever",
    # "hybrid": "retrieval.hybrid:HybridRetriever",
}


def available() -> list[str]:
    return sorted(RETRIEVERS)


def get_retriever(name: str, **options) -> Retriever:
    if name not in RETRIEVERS:
        raise ValueError(f"Unknown retriever {name!r}. Available: {', '.join(available())}")
    module_name, cls_name = RETRIEVERS[name].split(":")
    return getattr(importlib.import_module(module_name), cls_name)(**options)


__all__ = ["Hit", "Retriever", "RETRIEVERS", "available", "get_retriever", "load_chunks"]
