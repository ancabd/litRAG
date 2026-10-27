from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Hit:
    chunk_id: str
    score: float
    rank: int  # 1-based


def load_chunks(path: Path) -> list[dict]:
    """Load chunks.jsonl. Accepts the file or the run folder that contains it."""
    path = Path(path)
    if path.is_dir():
        path = path / "chunks.jsonl"
    if not path.exists():
        raise SystemExit(f"No chunks at {path}. Run `python parse_corpus.py run` first.")
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


class RetrieverUnavailable(RuntimeError):
    """The retriever can't run here: a missing package, or a model that can't be downloaded."""


class Retriever(ABC):
    """Indexes chunks once, then answers queries with ranked chunk ids.

    `config()` must describe every setting that changes results; it is stored with
    each eval run so results stay reproducible and comparable.
    """

    name: str = "base"

    @abstractmethod
    def index(self, chunks: list[dict]) -> None:
        ...

    @abstractmethod
    def search(self, query: str, k: int = 10) -> list[Hit]:
        ...

    def config(self) -> dict:
        return {"name": self.name}
