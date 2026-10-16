"""Single import point for the corpus-builder core. Everything in the server that
needs core code imports it from here, so the path setup happens exactly once."""
from __future__ import annotations

from .config import Settings, ensure_core_importable

ensure_core_importable(Settings.from_env())

from corpus_builder import (  # noqa: E402
    MAX_PDF_BYTES,
    ManualEditError,
    add_manual_pdf,
    remove_manual_pdf,
    set_manual_abstract,
)
from evaluation.matching import GoldIndex, ngrams, quote_coverage, words  # noqa: E402
from evaluation.questions import FIELDS, SPLITS, TYPES, Evidence, QuestionFileError, parse_questions  # noqa: E402
from evaluation.runner import run_eval  # noqa: E402
from ingest.pipeline import paper_report, rebuild_runs  # noqa: E402
from retrieval import available as available_retrievers  # noqa: E402
from retrieval import get_retriever, load_chunks  # noqa: E402
from retrieval.base import Retriever  # noqa: E402

__all__ = ["run_eval", "Evidence", "MAX_PDF_BYTES", "ManualEditError", "add_manual_pdf", "paper_report", "rebuild_runs",
           "remove_manual_pdf", "set_manual_abstract", "FIELDS", "SPLITS", "TYPES", "GoldIndex", "QuestionFileError", "Retriever", "available_retrievers",
           "get_retriever", "load_chunks", "ngrams", "parse_questions", "quote_coverage", "words"]
