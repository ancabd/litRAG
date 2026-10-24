"""Chunk runs (data/chunks/<name>/chunks.jsonl), each held as a core Library.

A run is loaded once and cached; it is reloaded if its chunks.jsonl changes
(e.g. after `parse_corpus.py run`). The Library caches retriever indexes, so the
first search on a run builds the index and later searches are fast.
"""
from __future__ import annotations

import json
import re
import threading
from pathlib import Path

from ..core import Library, load_chunks

RUN_NAME = re.compile(r"^[A-Za-z0-9_.@-]+$")


class RunData(Library):
    """A chunk run as the server holds it: the core Library plus the file time it was loaded from."""

    def __init__(self, name: str, mtime: float, chunks: list[dict], info: dict | None):
        super().__init__(chunks, name=name, info=info)
        self.mtime = mtime


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
                run = RunData(name, mtime, load_chunks(f), _read_json(self.root / name / "run.json"))
                self._runs[name] = run
            return run


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
