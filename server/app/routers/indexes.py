"""Embedding indexes for dense and hybrid retrieval: which are built, and building one with progress.

Building embeds every chunk of a chunk run with one model (a minute or two on a CPU) and caches
the result in data/chunks/<run>/embeddings/. Dense and hybrid with the same model share it.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core import dense_retrieval
from ..deps import Services, require_run, services

router = APIRouter(tags=["indexes"])
MODELS = ("bge-small",)  # the presets the app offers


def _status(svc: Services, run) -> dict:
    building = {j.meta.get("model"): j.to_dict() for j in svc.jobs.running("index") if j.meta.get("run") == run.name}
    return {
        "run": run.name,
        "installed": dense_retrieval.installed(),
        "models": [{**dense_retrieval.cache_status(run.embeddings_dir, m, run.chunks), "job": building.get(m)}
                   for m in MODELS],
    }


@router.get("/indexes")
def list_indexes(run: str | None = None, svc: Services = Depends(services)) -> dict:
    return _status(svc, require_run(svc, run))


class BuildIndex(BaseModel):
    model: str
    run: str | None = None


@router.post("/indexes", status_code=201)
def build_index(body: BuildIndex, svc: Services = Depends(services)) -> dict:
    if body.model not in dense_retrieval.PRESETS:
        raise HTTPException(400, f"Unknown model {body.model!r}; try {', '.join(MODELS)}")
    data = require_run(svc, body.run)
    if body.model != "hash" and not dense_retrieval.installed():
        raise HTTPException(503, {"message": "Dense retrieval needs sentence-transformers: "
                                             "pip install -r corpus-builder/requirements-dense.txt, then restart the server.",
                                  "errors": [], "code": "retriever_unavailable"})
    for j in svc.jobs.running("index"):
        if j.meta == {"run": data.name, "model": body.model}:
            return {"job": j.to_dict()}  # already building: follow that job

    def work(progress):
        r = data.retriever(f"dense:{body.model}", progress=progress)
        return {"run": data.name, "model": body.model, **getattr(r, "stats", {})}

    job = svc.jobs.start("index", work, meta={"run": data.name, "model": body.model})
    return {"job": job.to_dict()}
