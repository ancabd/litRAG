from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from ..core import MAX_PDF_BYTES, ManualEditError

from ..deps import Services, services
from ..services.corpus import summary
from ..services.evidence import chunk_view

router = APIRouter(tags=["papers"])


@router.get("/papers")
def list_papers(q: str = "", status: str | None = None, role: str | None = None, seed: str | None = None,
                sort: str = "cited", run: str | None = None, offset: int = Query(0, ge=0),
                limit: int = Query(50, ge=1, le=500), svc: Services = Depends(services)) -> dict:
    data = svc.chunks.get(run)
    return svc.corpus.query(q, status, role, seed, sort, data.chunk_counts() if data else None, offset, limit)


@router.get("/papers/{paper_id}")
def get_paper(paper_id: str, run: str | None = None, svc: Services = Depends(services)) -> dict:
    p = svc.corpus.get(paper_id)
    if not p:
        raise HTTPException(404, f"No paper {paper_id} in the manifest")
    data = svc.chunks.get(run)
    titles = svc.corpus.titles()
    questions, _, _ = svc.questions.load()
    cited_in = [{"id": q.get("id"), "question": q.get("question")} for q in questions
                if any(str(e.get("paper")) == paper_id for e in q.get("evidence") or [])]
    return {
        **summary(p, len(data.by_paper.get(paper_id, [])) if data else None),
        "abstract": p.get("abstract"),
        "abstract_source": p.get("abstract_source"),
        "added_manually": p.get("added_manually") or [],
        "is_oa": p.get("is_oa"),
        "type": p.get("type"),
        "pdf_available": svc.corpus.pdf_path(paper_id) is not None,
        "pdf_url": p.get("pdf_url"),
        "note": p.get("note"),
        "seeds": [{"openalex_id": s, "title": titles.get(s, s)} for s in p.get("via_seeds") or []],
        "questions": cited_in,
        "run": data.name if data else None,
    }


@router.get("/papers/{paper_id}/chunks")
def paper_chunks(paper_id: str, run: str | None = None, svc: Services = Depends(services)) -> dict:
    data = svc.chunks.get(run)
    if data is None:
        return {"run": None, "items": []}
    return {"run": data.name, "items": [chunk_view(c) for c in data.by_paper.get(paper_id, [])]}


@router.get("/papers/{paper_id}/pdf")
def paper_pdf(paper_id: str, svc: Services = Depends(services)):
    path = svc.corpus.pdf_path(paper_id)
    if path is None:
        raise HTTPException(404, f"No downloaded PDF for {paper_id}")
    return FileResponse(path, media_type="application/pdf", filename=f"{paper_id}.pdf",
                        content_disposition_type="inline")


# ------------------------------------------------------------------ manual additions
# Add what the corpus builder couldn't get: a PDF you downloaded yourself, or an abstract.
# Each change updates manifest.jsonl/csv + manual.jsonl (so it survives corpus_builder reruns),
# then re-chunks every chunk run, so the paper is immediately searchable and usable as evidence.

class AbstractIn(BaseModel):
    abstract: str = ""


def _manual_result(svc: Services, paper_id: str, result: dict) -> dict:
    return {"paper": get_paper(paper_id, None, svc), "ingest": result["ingest"]}


@router.post("/papers/{paper_id}/pdf")
async def add_pdf(paper_id: str, request: Request, svc: Services = Depends(services)) -> dict:
    """Body: the raw PDF bytes (Content-Type: application/pdf)."""
    if not svc.corpus.get(paper_id):
        raise HTTPException(404, f"No paper {paper_id} in the manifest")
    if int(request.headers.get("content-length") or 0) > MAX_PDF_BYTES:
        raise HTTPException(413, f"PDF is larger than {MAX_PDF_BYTES // 2**20} MB")
    data = await request.body()
    try:
        result = await run_in_threadpool(svc.manual.add_pdf, paper_id, data)
    except ManualEditError as exc:
        raise HTTPException(400, str(exc))
    return _manual_result(svc, paper_id, result)


@router.delete("/papers/{paper_id}/pdf")
async def remove_pdf(paper_id: str, svc: Services = Depends(services)) -> dict:
    try:
        result = await run_in_threadpool(svc.manual.remove_pdf, paper_id)
    except ManualEditError as exc:
        raise HTTPException(400, str(exc))
    return _manual_result(svc, paper_id, result)


@router.put("/papers/{paper_id}/abstract")
async def set_abstract(paper_id: str, body: AbstractIn, svc: Services = Depends(services)) -> dict:
    """Set a manual abstract; an empty string removes it."""
    try:
        result = await run_in_threadpool(svc.manual.set_abstract, paper_id, body.abstract)
    except ManualEditError as exc:
        raise HTTPException(400, str(exc))
    return _manual_result(svc, paper_id, result)
