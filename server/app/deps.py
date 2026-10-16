"""Service container, created once per app and handed to routes via FastAPI dependencies."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request

from .config import Settings
from .services.chunks import ChunkService, RunData
from .services.corpus import CorpusService, ManualEditor
from .services.evalruns import EvalRunService
from .services.questions import QuestionStore


@dataclass
class Services:
    settings: Settings
    corpus: CorpusService
    chunks: ChunkService
    questions: QuestionStore
    manual: ManualEditor
    evals: EvalRunService

    @classmethod
    def build(cls, settings: Settings) -> "Services":
        chunks = ChunkService(settings.chunks_root)
        return cls(settings, CorpusService(settings.corpus_dir), chunks, QuestionStore(settings.questions_file),
                   ManualEditor(settings.corpus_dir, settings.chunks_root, chunks),
                   EvalRunService(settings.runs_dir, settings.chunks_root, settings.questions_file))


def services(request: Request) -> Services:
    return request.app.state.services


def require_run(svc: Services, run: str | None) -> RunData:
    data = svc.chunks.get(run)
    if data is None:
        if run:
            raise HTTPException(404, f"Chunk run '{run}' not found in {svc.settings.chunks_root}")
        raise HTTPException(409, "No chunks yet. Run `python parse_corpus.py run` in corpus-builder first.")
    return data
