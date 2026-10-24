"""Where everything lives. Defaults follow the repo layout:

    litrag/
      corpus-builder/            core library (code only)
      data/                      corpus/, chunks/, questions/, runs/, cache/
      server/                    this package
      web/dist/                  built UI, served at /

These match corpus-builder/paths.py, and the same environment variables override them
(useful for tests or for keeping data outside the repo):
    LITRAG_DATA (moves all of data/), LITRAG_CORPUS, LITRAG_CHUNKS, LITRAG_QUESTIONS,
    LITRAG_RUNS, LITRAG_CACHE, plus LITRAG_CORE and LITRAG_WEB_DIST
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    core_dir: Path
    corpus_dir: Path
    chunks_root: Path
    questions_file: Path
    runs_dir: Path
    cache_dir: Path
    web_dist: Path

    @classmethod
    def from_env(cls, **overrides) -> "Settings":
        def path(env: str, default: Path) -> Path:
            return Path(os.environ.get(env, default)).expanduser().resolve()

        core = Path(overrides.get("core_dir") or path("LITRAG_CORE", REPO_ROOT / "corpus-builder"))
        data = path("LITRAG_DATA", REPO_ROOT / "data")
        values = {
            "core_dir": core,
            "corpus_dir": path("LITRAG_CORPUS", data / "corpus"),
            "chunks_root": path("LITRAG_CHUNKS", data / "chunks"),
            "questions_file": path("LITRAG_QUESTIONS", data / "questions" / "questions.yaml"),
            "runs_dir": path("LITRAG_RUNS", data / "runs"),
            "cache_dir": path("LITRAG_CACHE", data / "cache"),
            "web_dist": path("LITRAG_WEB_DIST", REPO_ROOT / "web" / "dist"),
        }
        values.update({k: Path(v).resolve() for k, v in overrides.items()})
        return cls(**values)


def ensure_core_importable(settings: Settings) -> None:
    """Make the core packages (ingest, retrieval, evaluation) importable without installing them."""
    core = str(settings.core_dir)
    if core not in sys.path:
        sys.path.insert(0, core)
