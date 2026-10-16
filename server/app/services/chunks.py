"""Chunk runs (chunks/<name>/chunks.jsonl) and the retrievers built on them.

A run is loaded once and cached; it is reloaded if its chunks.jsonl changes
(e.g. after `parse_corpus.py run`). Retriever indexes are cached per run, so the
first search on a run builds the index and later searches are fast.
"""
from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path

from ..core import GoldIndex, Retriever, get_retriever, load_chunks

RUN_NAME = re.compile(r"^[A-Za-z0-9_.@-]+$")


@dataclass
class RunData:
    name: str
    mtime: float
    chunks: list[dict]
    by_id: dict[str, dict]
    by_paper: dict[str, list[dict]]
    info: dict | None
    _gold: GoldIndex | None = None
    _retrievers: dict[str, Retriever] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def gold(self) -> GoldIndex:
        with self._lock:
            if self._gold is None:
                self._gold = GoldIndex(self.chunks)
            return self._gold

    def retriever(self, name: str) -> Retriever:
        with self._lock:
            if name not in self._retrievers:
                r = get_retriever(name)
                r.index(self.chunks)
                self._retrievers[name] = r
            return self._retrievers[name]

    def chunk_counts(self) -> dict[str, int]:
        return {pid: len(cs) for pid, cs in self.by_paper.items()}


class ChunkService:
    def __init__(self, chunks_root: Path):
        self.root = chunks_root
        self._runs: dict[str, RunData] = {}
        self._lock = threading.Lock()

    def list_runs(self) -> list[dict]:
        if not self.root.exists():
            return []
        runs = []
        for d in self.root.iterdir():
            f = d / "chunks.jsonl"
            if d.is_dir() and f.exists() and RUN_NAME.match(d.name):
                info = _read_json(d / "run.json") or {}
                runs.append({"name": d.name, "modified": f.stat().st_mtime, "parser": info.get("parser"),
                             "chunking": info.get("chunking"), "chunks": info.get("chunks"),
                             "papers_by_source": info.get("papers_by_source")})
        return sorted(runs, key=lambda r: -r["modified"])

    def invalidate(self) -> None:
        """Drop cached runs (after the chunk files were rebuilt)."""
        with self._lock:
            self._runs.clear()

    def default_run(self) -> str | None:
        runs = self.list_runs()
        return runs[0]["name"] if runs else None

    def get(self, name: str | None) -> RunData | None:
        name = name or self.default_run()
        if not name or not RUN_NAME.match(name):
            return None
        f = self.root / name / "chunks.jsonl"
        if not f.exists():
            return None
        mtime = f.stat().st_mtime
        with self._lock:
            run = self._runs.get(name)
            if run is None or run.mtime != mtime:
                chunks = load_chunks(f)
                by_paper: dict[str, list[dict]] = {}
                for c in chunks:
                    by_paper.setdefault(c["paper_id"], []).append(c)
                run = RunData(name, mtime, chunks, {c["chunk_id"]: c for c in chunks}, by_paper,
                              _read_json(self.root / name / "run.json"))
                self._runs[name] = run
            return run


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
