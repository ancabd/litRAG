"""Retrieval over a chunk run. This is also the first half of the future /api/ask:
an answer route will call the same RunData.retriever(...).search(...) and hand the
hits to an LLM."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..core import available_retrievers
from ..deps import Services, require_run, services
from ..services.evidence import chunk_view

router = APIRouter(tags=["search"])


@router.get("/search")
def search(q: str = Query(..., min_length=1), run: str | None = None, retriever: str = "bm25",
           k: int = Query(10, ge=1, le=100), paper: str | None = None, svc: Services = Depends(services)) -> dict:
    if retriever not in available_retrievers():
        raise HTTPException(400, f"Unknown retriever {retriever!r}; available: {available_retrievers()}")
    data = require_run(svc, run)
    r = data.retriever(retriever)
    hits = r.search(q, k=len(data.chunks) if paper else k)
    if paper:
        hits = [h for h in hits if data.by_id[h.chunk_id]["paper_id"] == paper][:k]
    titles = svc.corpus.titles()
    items = []
    for rank, h in enumerate(hits, 1):
        c = data.by_id[h.chunk_id]
        items.append({**chunk_view(c), "rank": rank, "score": round(h.score, 3),
                      "title": c.get("title") or titles.get(c["paper_id"]), "year": c.get("year"),
                      "authors": c.get("authors")})
    return {"query": q, "run": data.name, "retriever": r.config(), "items": items}
