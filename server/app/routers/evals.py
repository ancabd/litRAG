"""Eval runs: list, view, compare, start and delete. Same folders and code as `evaluate.py run`."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from ..core import QuestionFileError, available_retrievers
from ..deps import Services, services

router = APIRouter(tags=["evals"])


class StartEval(BaseModel):
    chunks: str | None = None   # chunk run name; default: the newest
    retriever: str = "bm25"
    split: str = "dev"          # dev | test | all


@router.get("/evals")
def list_evals(svc: Services = Depends(services)) -> dict:
    return {"items": svc.evals.list(), "runs_dir": str(svc.settings.runs_dir)}


@router.get("/evals/compare")
def compare_evals(names: str, svc: Services = Depends(services)) -> dict:
    wanted = [n for n in names.split(",") if n]
    if len(wanted) < 2:
        raise HTTPException(400, "Pick at least two runs to compare")
    try:
        return svc.evals.compare(wanted)
    except FileNotFoundError as exc:
        raise HTTPException(404, f"No eval run {exc}")


@router.get("/evals/{name}")
def get_eval(name: str, svc: Services = Depends(services)) -> dict:
    def lookup(chunks_name: str):
        data = svc.chunks.get(chunks_name) if chunks_name else None
        return data.by_id if data and data.name == chunks_name else None

    run = svc.evals.get(name, lookup)
    if run is None:
        raise HTTPException(404, f"No eval run {name}")
    return run


@router.post("/evals", status_code=201)
async def start_eval(body: StartEval, svc: Services = Depends(services)) -> dict:
    if body.retriever not in available_retrievers():
        raise HTTPException(400, f"Unknown retriever {body.retriever!r}")
    if body.split not in ("dev", "test", "all"):
        raise HTTPException(400, "split must be dev, test or all")
    chunks = body.chunks or svc.chunks.default_run()
    if not chunks:
        raise HTTPException(409, "No chunks yet. Run `python parse_corpus.py run` in corpus-builder first.")
    try:
        name = await run_in_threadpool(svc.evals.start, chunks, body.retriever, body.split)
    except QuestionFileError as exc:
        raise HTTPException(422, {"message": "questions.yaml has problems; fix them before running the eval.",
                                  "errors": str(exc).splitlines()})
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc))
    return {"name": name}


@router.delete("/evals/{name}")
def delete_eval(name: str, svc: Services = Depends(services)) -> dict:
    if not svc.evals.delete(name):
        raise HTTPException(404, f"No eval run {name}")
    return {"deleted": name}
