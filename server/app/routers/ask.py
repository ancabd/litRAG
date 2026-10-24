"""Ask: answer a question from the corpus with citations. Retrieval is the same as /api/search;
the generator (an LLM, or the extractive baseline) writes the answer from the top k passages."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from ..core import LLMError, LLMNotConfigured, available_retrievers
from ..deps import Services, require_run, services

router = APIRouter(tags=["ask"])


class AskIn(BaseModel):
    question: str = Field(..., min_length=3)
    run: str | None = None
    retriever: str = "bm25"
    generator: str = "claude"
    model: str | None = None
    k: int = Field(8, ge=1, le=30)


@router.get("/llm")
def llm_status(svc: Services = Depends(services)) -> dict:
    return svc.answering.status()


@router.post("/ask")
async def ask(body: AskIn, svc: Services = Depends(services)) -> dict:
    if body.retriever not in available_retrievers():
        raise HTTPException(400, f"Unknown retriever {body.retriever!r}")
    data = require_run(svc, body.run)
    try:
        return await run_in_threadpool(svc.answering.ask, data, body.question.strip(), body.retriever,
                                       body.generator, body.model, body.k, svc.corpus.titles())
    except LLMNotConfigured as exc:
        raise HTTPException(503, {"message": str(exc), "errors": [], "code": "llm_not_configured"})
    except LLMError as exc:
        raise HTTPException(502, str(exc))
    except ValueError as exc:
        raise HTTPException(400, str(exc))
