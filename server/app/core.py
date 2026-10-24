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
from evaluation.questions import load_questions as load_questions_checked  # noqa: E402
from evaluation.answer_runner import run_answer_eval  # noqa: E402
from evaluation.judge import Judge, agreement  # noqa: E402
from evaluation.runner import run_eval  # noqa: E402
from generation import (DEFAULT_MODEL, PRICES, LLMError, LLMNotConfigured, answer_question,  # noqa: E402
                        available_generators, get_generator)
from library import Library  # noqa: E402
from generation.llm import make_llm  # noqa: E402
from ingest.pipeline import paper_report, rebuild_runs  # noqa: E402
from retrieval import available as available_retrievers  # noqa: E402
from retrieval import get_retriever, load_chunks  # noqa: E402
from retrieval.base import Retriever  # noqa: E402

__all__ = ["load_questions_checked", "DEFAULT_MODEL", "Judge", "LLMError", "LLMNotConfigured", "PRICES", "agreement", "answer_question",
           "available_generators", "get_generator", "make_llm", "run_answer_eval", "run_eval", "Evidence", "MAX_PDF_BYTES", "ManualEditError", "add_manual_pdf", "paper_report", "rebuild_runs",
           "remove_manual_pdf", "set_manual_abstract", "FIELDS", "SPLITS", "TYPES", "GoldIndex", "QuestionFileError", "Retriever", "available_retrievers",
           "Library", "get_retriever", "load_chunks", "ngrams", "parse_questions", "quote_coverage", "words"]
