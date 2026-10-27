"""Hybrid retrieval: BM25 and dense, merged with reciprocal rank fusion (RRF).

    get_retriever("hybrid")             # BM25 + BGE small v1.5 (same as "hybrid:bge-small")

Each retriever ranks the chunks; a chunk's fused score is the sum over the two rankings of
1 / (k_rrf + rank). RRF uses only ranks, so the two scales (BM25 scores, cosine similarities)
never have to be made comparable, and there is no weight to tune. k_rrf = 60 is the value from
the original RRF paper (Cormack et al., 2009) and rarely needs changing.

BM25 keeps exact technical terms (TIP3P, ff14SB, E(3)); the dense side catches paraphrases
("rotational symmetry" vs "equivariant").
"""
from __future__ import annotations

from pathlib import Path

from .base import Hit, Retriever
from .bm25 import BM25Retriever
from .dense import DEFAULT_PRESET, DenseRetriever


class HybridRetriever(Retriever):
    name = "hybrid"
    uses_cache = True

    def __init__(self, model: str = DEFAULT_PRESET, k_rrf: int = 60, candidates: int = 100, embedder=None,
                 progress=None):
        self.bm25 = BM25Retriever()
        self.dense = DenseRetriever(model, embedder=embedder, progress=progress)
        self.k_rrf, self.candidates = k_rrf, candidates

    def set_cache_dir(self, folder: Path | None) -> None:
        self.dense.set_cache_dir(folder)

    def set_progress(self, progress) -> None:
        self.dense.set_progress(progress)

    @property
    def stats(self) -> dict:
        return self.dense.stats

    def config(self) -> dict:
        return {"name": self.name, "fusion": "rrf", "k_rrf": self.k_rrf, "candidates": self.candidates,
                "bm25": self.bm25.config(), "dense": self.dense.config()}

    def index(self, chunks: list[dict]) -> None:
        self.bm25.index(chunks)
        self.dense.index(chunks)

    def search(self, query: str, k: int = 10) -> list[Hit]:
        n = max(self.candidates, k)
        fused: dict[str, float] = {}
        for hits in (self.bm25.search(query, k=n), self.dense.search(query, k=n)):
            for h in hits:
                fused[h.chunk_id] = fused.get(h.chunk_id, 0.0) + 1.0 / (self.k_rrf + h.rank)
        ranked = sorted(fused.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
        return [Hit(cid, score, r) for r, (cid, score) in enumerate(ranked, 1)]


__all__ = ["HybridRetriever"]
