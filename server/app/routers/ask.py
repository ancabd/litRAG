"""Ask: answer a question from the corpus with citations. Retrieval is the same as /api/search;
the generator (an LLM, or the extractive baseline) writes the answer from the top k passages."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from ..core import LLMError, LLMNotConfigured, available_retrievers, keys
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


class KeyIn(BaseModel):
    key: str = Field(..., min_length=10, max_length=500)
    remember: bool = True   # also save it for later runs and the command line
    check: bool = True      # ask Anthropic whether it works before using it


LOCAL = {"127.0.0.1", "::1", "localhost", "testclient"}


def _local_only(request: Request) -> None:
    """The key can only be set or removed from the computer the server runs on, even with --host 0.0.0.0."""
    if (request.client.host if request.client else None) not in LOCAL:
        raise HTTPException(403, "The API key can only be changed from the computer the server runs on.")


@router.put("/llm/key")
async def set_key(body: KeyIn, request: Request, svc: Services = Depends(services)) -> dict:
    _local_only(request)
    key = body.key.strip()
    if any(c.isspace() for c in key):
        raise HTTPException(400, "That doesn't look like an API key: it contains spaces or line breaks.")
    if body.check:
        try:
            await run_in_threadpool(keys.check_key, key)
        except ValueError as exc:
            raise HTTPException(400, str(exc))
        except LLMNotConfigured as exc:
            raise HTTPException(503, str(exc))
        except LLMError as exc:
            raise HTTPException(502, str(exc))
    keys.set_key(key, remember=body.remember)
    return svc.answering.status()


@router.delete("/llm/key")
def remove_key(request: Request, svc: Services = Depends(services)) -> dict:
    _local_only(request)
    keys.clear_key()
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
