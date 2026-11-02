"""Make a corpus from the app: build it from seed papers, or upload your own documents.

Both end with parsing and chunking, which can take minutes for a few hundred PDFs, so they run
as background jobs (kind "corpus"); poll /api/jobs/{id}. The job's meta carries its phase and
the last lines of its log, the same messages the command-line tools print.
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from ..core import DOCUMENT_SUFFIXES, MAX_PDF_BYTES, ManualEditError, parse_seed
from ..deps import Services, services
from ..services.corpus import summary

router = APIRouter(tags=["corpus"])

LOG_LINES = 300


def _running(svc: Services):
    jobs = svc.jobs.running("corpus")
    return jobs[0] if jobs else None


def _start(svc: Services, action: str, fn, **kwargs):
    if _running(svc):
        raise HTTPException(409, "The corpus is already being built or re-indexed; wait for that to finish.")
    lines: list[str] = []
    meta = {"action": action, "phase": "parse" if action != "build" else "collect", "log": lines}

    def log(line: str) -> None:
        lines.append(line)
        if len(lines) > LOG_LINES:
            del lines[:-LOG_LINES]

    def phase(name: str) -> None:
        meta["phase"] = name

    def work(progress):
        return fn(progress=progress, log=log, **({"phase": phase} if action == "build" else {}), **kwargs)

    job = svc.jobs.start("corpus", work, meta=meta)
    return job


@router.get("/corpus")
def corpus_overview(svc: Services = Depends(services)) -> dict:
    job = _running(svc)
    return {
        **svc.corpus.overview(),
        "runs": [r["name"] for r in svc.chunks.list_runs()],
        "job": job.to_dict() if job else None,
        "openalex_key": bool(os.environ.get("OPENALEX_API_KEY")),
        "suffixes": list(DOCUMENT_SUFFIXES),
        "max_bytes": MAX_PDF_BYTES,
    }


class BuildIn(BaseModel):
    seeds: str
    max_citing: int = Field(50, ge=0, le=500)
    recent_citing: int = Field(0, ge=0, le=500)
    download: bool = True
    openalex_key: str | None = None


@router.post("/corpus/build")
def build(body: BuildIn, svc: Services = Depends(services)) -> dict:
    lines = [line.strip() for line in body.seeds.splitlines() if line.strip() and not line.strip().startswith("#")]
    if not lines:
        raise HTTPException(400, "Add at least one seed: a DOI, an arXiv id, an OpenAlex id or a title, one per line.")
    if len(lines) > 50:
        raise HTTPException(400, "At most 50 seeds at a time.")
    bad = [line for line in lines if parse_seed(line) is None]
    if bad:
        raise HTTPException(400, "Couldn't read these seeds: " + "; ".join(bad[:5]))
    if svc.corpus.overview()["papers"]:
        raise HTTPException(409, "The corpus already has papers. Building from seeds here only starts a new "
                                 "corpus; to change an existing one, rerun corpus_builder.py with your seeds file.")
    key = (body.openalex_key or "").strip() or os.environ.get("OPENALEX_API_KEY") or None
    job = _start(svc, "build", svc.manual.build_from_seeds, seed_lines=lines, max_citing=body.max_citing,
                 recent_citing=body.recent_citing, download=body.download, openalex_key=key)
    return job.to_dict()


@router.post("/corpus/documents")
async def upload_document(request: Request, filename: str = Query(..., min_length=1, max_length=255),
                          title: str | None = Query(None, max_length=300),
                          svc: Services = Depends(services)) -> dict:
    """Body: the raw file. Stores it; call POST /corpus/reindex once the last file is uploaded."""
    if _running(svc):
        raise HTTPException(409, "The corpus is being built or re-indexed; upload again when that's done.")
    if int(request.headers.get("content-length") or 0) > MAX_PDF_BYTES:
        raise HTTPException(413, f"{filename} is larger than {MAX_PDF_BYTES // 2**20} MB")
    data = await request.body()
    try:
        row = await run_in_threadpool(svc.manual.add_document, filename, data, title)
    except ManualEditError as exc:
        raise HTTPException(400, str(exc))
    return summary(row)


@router.delete("/corpus/documents/{doc_id}")
async def delete_document(doc_id: str, svc: Services = Depends(services)) -> dict:
    """Removes the document and starts re-indexing, so its chunks disappear from search."""
    if _running(svc):
        raise HTTPException(409, "The corpus is being built or re-indexed; try again when that's done.")
    try:
        row = await run_in_threadpool(svc.manual.remove_document, doc_id)
    except ManualEditError as exc:
        raise HTTPException(404, str(exc))
    return {"document": summary(row), "job": _start(svc, "reindex", svc.manual.reindex).to_dict()}


@router.post("/corpus/reindex")
def reindex(svc: Services = Depends(services)) -> dict:
    return _start(svc, "reindex", svc.manual.reindex).to_dict()
