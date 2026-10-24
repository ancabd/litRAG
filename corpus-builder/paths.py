"""Where the data lives. Every command and the server use these defaults, so they work
from any working directory.

    litrag/
      corpus-builder/      code (this folder)
      server/, web/        the app
      data/
        corpus/            manifest, PDFs, abstracts, parse cache   (corpus_builder.py)
        chunks/<run>/      chunks.jsonl per parser + chunk config     (parse_corpus.py)
        questions/         questions.yaml                             (you, the app)
        runs/<run>/        eval results                               (evaluate.py, the app)
        cache/             cached LLM responses

Override with environment variables: LITRAG_DATA moves everything; LITRAG_CORPUS,
LITRAG_CHUNKS, LITRAG_QUESTIONS, LITRAG_RUNS and LITRAG_CACHE move single parts.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _path(env: str, default: Path) -> Path:
    return Path(os.environ.get(env) or default).expanduser().resolve()


DATA = _path("LITRAG_DATA", REPO / "data")
CORPUS = _path("LITRAG_CORPUS", DATA / "corpus")
CHUNKS = _path("LITRAG_CHUNKS", DATA / "chunks")
QUESTIONS = _path("LITRAG_QUESTIONS", DATA / "questions" / "questions.yaml")
RUNS = _path("LITRAG_RUNS", DATA / "runs")
CACHE = _path("LITRAG_CACHE", DATA / "cache")

PREFERRED_CHUNK_RUN = "pymupdf_w400_o60"


def default_chunk_run() -> Path:
    """The chunk run used when none is given: pymupdf_w400_o60 if present, else the newest."""
    preferred = CHUNKS / PREFERRED_CHUNK_RUN
    if (preferred / "chunks.jsonl").exists():
        return preferred
    runs = [d for d in CHUNKS.iterdir() if (d / "chunks.jsonl").exists()] if CHUNKS.exists() else []
    return max(runs, key=lambda d: (d / "chunks.jsonl").stat().st_mtime) if runs else preferred
