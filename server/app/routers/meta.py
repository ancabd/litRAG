from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core import SPLITS, TYPES, retriever_choices
from ..deps import Services, services

router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta(svc: Services = Depends(services)) -> dict:
    papers = svc.corpus.all()
    status_counts: dict[str, int] = {}
    for p in papers:
        status_counts[p.get("status") or "unknown"] = status_counts.get(p.get("status") or "unknown", 0) + 1
    questions, _, _ = svc.questions.load()
    tags = sorted({str(t) for q in questions for t in (q.get("tags") or [])})
    return {
        "corpus": {"available": svc.corpus.available, "papers": len(papers), "status_counts": status_counts,
                   "seeds": svc.corpus.seeds()},
        "runs": svc.chunks.list_runs(),
        "default_run": svc.chunks.default_run(),
        "retrievers": [c["name"] for c in retriever_choices()],
        "retriever_choices": retriever_choices(),
        "questions": {"types": list(TYPES), "splits": list(SPLITS), "tags": tags, "count": len(questions)},
        "paths": {k: str(v) for k, v in vars(svc.settings).items()},
    }


@router.get("/health")
def health() -> dict:
    return {"ok": True}
