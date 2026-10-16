from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..core import QuestionFileError, available_retrievers
from ..deps import Services, require_run, services
from ..services.evidence import check_evidence, chunk_view, evidence_summary, judge, judgments
from ..services.questions import NotFound, VersionConflict

router = APIRouter(tags=["questions"])


class PassageIn(BaseModel):
    paper: str = ""
    quote: str = ""


class EvidenceIn(BaseModel):
    paper: str = ""
    quote: str | None = None
    alternatives: list[PassageIn] = Field(default_factory=list)


class QuestionIn(BaseModel):
    id: str | None = None
    question: str = ""
    type: str = "lookup"
    tags: list[str] = Field(default_factory=list)
    split: str = "dev"
    answer: str | None = None
    evidence: list[EvidenceIn] = Field(default_factory=list)
    notes: str | None = None
    not_relevant: list[PassageIn] = Field(default_factory=list)


class QuestionWrite(BaseModel):
    question: QuestionIn
    version: str


class Judgment(BaseModel):
    chunk_id: str
    kind: str          # alternative | not_relevant | clear
    item: int = 0      # which evidence item an alternative belongs to
    version: str
    run: str | None = None


class EvidenceCheck(BaseModel):
    paper: str
    quote: str | None = None
    run: str | None = None


def _errors(exc: QuestionFileError) -> HTTPException:
    return HTTPException(422, {"message": "The question is not valid yet", "errors": str(exc).splitlines()})


def _conflict() -> HTTPException:
    return HTTPException(409, {"message": "questions.yaml changed outside the app (or in another tab). "
                                          "Reload to get the latest version."})


def _with_status(svc: Services, q: dict, run: str | None) -> dict:
    data = svc.chunks.get(run)
    titles = svc.corpus.titles()
    out = {**q, "evidence_status": evidence_summary(data, q)}
    out["evidence"] = [{**e, "title": titles.get(str(e.get("paper"))),
                        "alternatives": [{**a, "title": titles.get(str(a.get("paper")))} for a in e.get("alternatives") or []]}
                       for e in q.get("evidence") or []]
    return out


@router.get("/questions")
def list_questions(run: str | None = None, svc: Services = Depends(services)) -> dict:
    questions, version, errors = svc.questions.load()
    return {"version": version, "errors": errors, "file": str(svc.questions.path),
            "items": [_with_status(svc, q, run) for q in questions]}


@router.get("/questions/{qid}")
def get_question(qid: str, run: str | None = None, svc: Services = Depends(services)) -> dict:
    questions, version, _ = svc.questions.load()
    q = next((q for q in questions if str(q.get("id")) == qid), None)
    if q is None:
        raise HTTPException(404, f"No question {qid}")
    return {"version": version, "item": _with_status(svc, q, run)}


@router.post("/questions", status_code=201)
def create_question(body: QuestionWrite, run: str | None = None, svc: Services = Depends(services)) -> dict:
    try:
        q, version = svc.questions.create(body.question.model_dump(), body.version)
    except VersionConflict:
        raise _conflict()
    except QuestionFileError as exc:
        raise _errors(exc)
    return {"version": version, "item": _with_status(svc, q, run)}


@router.put("/questions/{qid}")
def update_question(qid: str, body: QuestionWrite, run: str | None = None,
                    svc: Services = Depends(services)) -> dict:
    try:
        q, version = svc.questions.update(qid, body.question.model_dump(), body.version)
    except VersionConflict:
        raise _conflict()
    except NotFound:
        raise HTTPException(404, f"No question {qid}")
    except QuestionFileError as exc:
        raise _errors(exc)
    return {"version": version, "item": _with_status(svc, q, run)}


@router.delete("/questions/{qid}")
def delete_question(qid: str, version: str, svc: Services = Depends(services)) -> dict:
    try:
        return {"version": svc.questions.delete(qid, version)}
    except VersionConflict:
        raise _conflict()
    except NotFound:
        raise HTTPException(404, f"No question {qid}")
    except QuestionFileError as exc:
        raise _errors(exc)


@router.post("/evidence/check")
def evidence_check(body: EvidenceCheck, svc: Services = Depends(services)) -> dict:
    data = require_run(svc, body.run)
    result = check_evidence(data, body.paper.strip(), body.quote)
    p = svc.corpus.get(body.paper.strip())
    result["title"] = p.get("title") if p else None
    result["manifest_status"] = p.get("status") if p else None
    return result


# ------------------------------------------------------------------ reviewing retrieved passages
# "Pooling": look at what a retriever returns for a question and judge each passage. Passages that
# answer it become alternatives (lenient scoring); the rest are recorded as not relevant.

def _find(svc: Services, qid: str) -> tuple[dict, str]:
    questions, version, errors = svc.questions.load()
    q = next((q for q in questions if str(q.get("id")) == qid), None)
    if q is None:
        raise HTTPException(404, f"No question {qid}")
    if errors:
        raise HTTPException(409, {"message": "questions.yaml has errors; fix them before reviewing.", "errors": errors})
    return q, version


@router.get("/questions/{qid}/review")
def review(qid: str, run: str | None = None, retriever: str = "bm25", k: int = 10,
           svc: Services = Depends(services)) -> dict:
    if retriever not in available_retrievers():
        raise HTTPException(400, f"Unknown retriever {retriever!r}")
    q, version = _find(svc, qid)
    data = require_run(svc, run)
    judged = judgments(data, q)
    hits = data.retriever(retriever).search(q["question"], k=max(1, min(k, 50)))
    titles = svc.corpus.titles()
    items = []
    for rank, h in enumerate(hits, 1):
        c = data.by_id[h.chunk_id]
        items.append({**chunk_view(c), "rank": rank, "score": round(h.score, 3),
                      "title": c.get("title") or titles.get(c["paper_id"]), "year": c.get("year"),
                      "judgment": judged.get(h.chunk_id, {"kind": "unjudged", "item": None})})
    n_judged = sum(i["judgment"]["kind"] != "unjudged" for i in items)
    return {"version": version, "run": data.name, "retriever": retriever, "items": items,
            "judged": n_judged, "evidence": [{"paper": e.get("paper"), "title": titles.get(str(e.get("paper")))}
                                             for e in q.get("evidence") or []]}


@router.post("/questions/{qid}/judge")
def judge_passage(qid: str, body: Judgment, svc: Services = Depends(services)) -> dict:
    data = require_run(svc, body.run)
    chunk = data.by_id.get(body.chunk_id)
    if chunk is None:
        raise HTTPException(404, f"No chunk {body.chunk_id} in {data.name}")
    try:
        q, version = svc.questions.modify(qid, body.version, lambda q: judge(q, chunk, body.kind, body.item, data))
    except VersionConflict:
        raise _conflict()
    except NotFound:
        raise HTTPException(404, f"No question {qid}")
    except ValueError as exc:  # includes QuestionFileError
        if isinstance(exc, QuestionFileError):
            raise _errors(exc)
        raise HTTPException(400, str(exc))
    return {"version": version, "item": _with_status(svc, q, body.run),
            "judgment": judgments(data, q).get(body.chunk_id, {"kind": "unjudged", "item": None})}
