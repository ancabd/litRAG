"""Eval runs: list, view, compare, start and delete. Same folders and code as `evaluate.py run`."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from ..core import LLMNotConfigured, QuestionFileError, available_retrievers
from ..deps import Services, services

router = APIRouter(tags=["evals"])


class StartEval(BaseModel):
    kind: str = "retrieval"     # retrieval | answer
    chunks: str | None = None   # chunk run name; default: the newest
    retriever: str = "bm25"
    split: str = "dev"          # dev | test | all
    # answer evals only
    generator: str = "claude"
    model: str | None = None
    judge: str | None = None    # judge model; "none" for no judge; default: same as generator
    k: int = 8


class Verdict(BaseModel):
    verdict: str | None         # correct | partial | incorrect | None to clear


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
    if body.kind == "answer":
        return _start_answer_eval(body, chunks, svc)
    if body.kind != "retrieval":
        raise HTTPException(400, "kind must be retrieval or answer")
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


def _start_answer_eval(body: StartEval, chunks: str, svc: Services) -> dict:
    """Answer evals make many LLM calls, so they run as a background job; poll /api/jobs/{id}."""
    from ..core import load_questions_checked
    if svc.jobs.running("answer_eval"):
        raise HTTPException(409, "An answer eval is already running; wait for it to finish.")
    try:
        load_questions_checked(svc.settings.questions_file)
        gen = svc.answering.generator(body.generator, body.model)
        judge_model = body.judge or (gen.config().get("model") if body.generator == "claude" else None) or "none"
        judge = svc.answering.judge(judge_model)
    except QuestionFileError as exc:
        raise HTTPException(422, {"message": "questions.yaml has problems; fix them before running the eval.",
                                  "errors": str(exc).splitlines()})
    except LLMNotConfigured as exc:
        raise HTTPException(503, {"message": str(exc), "errors": [], "code": "llm_not_configured"})
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    def work(progress):
        return {"name": svc.evals.start_answer(chunks, body.retriever, body.split, gen, judge, body.k, progress)}

    job = svc.jobs.start("answer_eval", work)
    return {"job": job.to_dict()}


@router.get("/jobs/{job_id}")
def job_status(job_id: str, svc: Services = Depends(services)) -> dict:
    job = svc.jobs.get(job_id)
    if job is None:
        raise HTTPException(404, f"No job {job_id} (jobs are forgotten when the server restarts)")
    return job.to_dict()


@router.put("/evals/{name}/verdicts/{qid}")
def set_verdict(name: str, qid: str, body: Verdict, svc: Services = Depends(services)) -> dict:
    try:
        svc.evals.set_verdict(name, qid, body.verdict)
    except FileNotFoundError:
        raise HTTPException(404, f"No eval run {name}")
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    run = svc.evals.get(name, lambda _: None)
    return {"human": next((q.get("human") for q in run["questions"] if q["id"] == qid), None),
            "agreement": run.get("agreement")}
