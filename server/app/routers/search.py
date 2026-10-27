"""Retrieval over a chunk run, through the same Library.search the generators use."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..core import is_retriever
from ..deps import Services, require_run, services
from ..services.evidence import chunk_view

router = APIRouter(tags=["search"])


@router.get("/search")
def search(q: str = Query(..., min_length=1), run: str | None = None, retriever: str = "bm25",
           k: int = Query(10, ge=1, le=100), paper: str | None = None, svc: Services = Depends(services)) -> dict:
    if not is_retriever(retriever):
        raise HTTPException(400, f"Unknown retriever {retriever!r}; try bm25, dense or hybrid")
    data = require_run(svc, run)
    hits = data.search(q, k=k, retriever=retriever, paper=paper)
    titles = svc.corpus.titles()
    items = []
    for rank, h in enumerate(hits, 1):
        c = data.by_id[h.chunk_id]
        items.append({**chunk_view(c), "rank": rank, "score": round(h.score, 3),
                      "title": c.get("title") or titles.get(c["paper_id"]), "year": c.get("year"),
                      "authors": c.get("authors")})
    return {"query": q, "run": data.name, "retriever": data.retriever(retriever).config(), "items": items}
