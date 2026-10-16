"""Where everything lives. Defaults follow the repo layout:

    litrag/
      corpus-builder/            core library + data (corpus/, chunks/, questions/, runs/)
      server/                    this package
      web/dist/                  built UI, served at /

Any path can be overridden with an environment variable (useful for tests or
for keeping data outside the repo):
    LITRAG_CORE, LITRAG_CORPUS, LITRAG_CHUNKS, LITRAG_QUESTIONS, LITRAG_RUNS, LITRAG_WEB_DIST
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
    web_dist: Path

    @classmethod
    def from_env(cls, **overrides) -> "Settings":
        def path(env: str, default: Path) -> Path:
            return Path(os.environ.get(env, default)).expanduser().resolve()

        core = Path(overrides.get("core_dir") or path("LITRAG_CORE", REPO_ROOT / "corpus-builder"))
        values = {
            "core_dir": core,
            "corpus_dir": path("LITRAG_CORPUS", core / "corpus"),
            "chunks_root": path("LITRAG_CHUNKS", core / "chunks"),
            "questions_file": path("LITRAG_QUESTIONS", core / "questions" / "questions.yaml"),
            "runs_dir": path("LITRAG_RUNS", core / "runs"),
            "web_dist": path("LITRAG_WEB_DIST", REPO_ROOT / "web" / "dist"),
        }
        values.update({k: Path(v).resolve() for k, v in overrides.items()})
        return cls(**values)


def ensure_core_importable(settings: Settings) -> None:
    """Make the core packages (ingest, retrieval, evaluation) importable without installing them."""
    core = str(settings.core_dir)
    if core not in sys.path:
        sys.path.insert(0, core)
