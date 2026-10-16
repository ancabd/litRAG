"""Paper metadata from the corpus manifest, reloaded automatically when the file changes."""
from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass
from pathlib import Path

PAPER_ID = re.compile(r"^W\d+$")


@dataclass
class _Snapshot:
    mtime: float
    papers: list[dict]
    by_id: dict[str, dict]


class CorpusService:
    def __init__(self, corpus_dir: Path):
        self.corpus_dir = corpus_dir
        self.manifest = corpus_dir / "manifest.jsonl"
        self._snap: _Snapshot | None = None
        self._lock = threading.Lock()

    @property
    def available(self) -> bool:
        return self.manifest.exists()

    def _load(self) -> _Snapshot:
        if not self.manifest.exists():
            return _Snapshot(0.0, [], {})
        mtime = self.manifest.stat().st_mtime
        with self._lock:
            if self._snap is None or self._snap.mtime != mtime:
                with open(self.manifest, encoding="utf-8") as fh:
                    papers = [json.loads(line) for line in fh if line.strip()]
                self._snap = _Snapshot(mtime, papers, {p["openalex_id"]: p for p in papers})
            return self._snap

    def all(self) -> list[dict]:
        return self._load().papers

    def get(self, paper_id: str) -> dict | None:
        return self._load().by_id.get(paper_id)

    def titles(self) -> dict[str, str]:
        return {pid: p.get("title") or pid for pid, p in self._load().by_id.items()}

    def pdf_path(self, paper_id: str) -> Path | None:
        """Path of the paper's PDF, only if it is a real file inside corpus/pdfs."""
        if not PAPER_ID.match(paper_id):
            return None
        p = self.get(paper_id)
        if not p or not p.get("pdf_path"):
            return None
        path = (self.corpus_dir / p["pdf_path"]).resolve()
        pdfs = (self.corpus_dir / "pdfs").resolve()
        if pdfs not in path.parents or not path.is_file():
            return None
        return path

    def query(self, q: str = "", status: str | None = None, role: str | None = None, seed: str | None = None,
              sort: str = "cited", chunk_counts: dict[str, int] | None = None,
              offset: int = 0, limit: int = 50) -> dict:
        papers = self.all()
        facets_base = papers
        if q:
            terms = q.lower().split()
            def hay(p: dict) -> str:
                return " ".join(str(p.get(k) or "") for k in ("openalex_id", "title", "authors", "venue", "doi",
                                                             "year")).lower()
            papers = [p for p in papers if all(t in hay(p) for t in terms)]
            facets_base = papers
        if status:
            papers = [p for p in papers if p.get("status") == status]
        if role:
            papers = [p for p in papers if role in (p.get("roles") or [])]
        if seed:
            papers = [p for p in papers if seed in (p.get("via_seeds") or []) or p["openalex_id"] == seed]
        keys = {
            "cited": lambda p: (-(p.get("cited_by_count") or 0), p["openalex_id"]),
            "year": lambda p: (-(p.get("year") or 0), p["openalex_id"]),
            "year_asc": lambda p: ((p.get("year") or 9999), p["openalex_id"]),
            "title": lambda p: ((p.get("title") or "").lower(), p["openalex_id"]),
        }
        papers = sorted(papers, key=keys.get(sort, keys["cited"]))
        status_counts: dict[str, int] = {}
        for p in facets_base:
            status_counts[p.get("status") or "unknown"] = status_counts.get(p.get("status") or "unknown", 0) + 1
        counts = chunk_counts or {}
        return {
            "total": len(papers),
            "offset": offset,
            "limit": limit,
            "status_counts": status_counts,
            "items": [summary(p, counts.get(p["openalex_id"], 0)) for p in papers[offset:offset + limit]],
        }

    def seeds(self) -> list[dict]:
        return [summary(p) for p in self.all() if "seed" in (p.get("roles") or [])]


def summary(p: dict, n_chunks: int | None = None) -> dict:
    out = {k: p.get(k) for k in ("openalex_id", "title", "authors", "year", "venue", "doi", "status",
                                 "roles", "via_seeds", "cited_by_count")}
    out["added_manually"] = p.get("added_manually") or []
    if n_chunks is not None:
        out["n_chunks"] = n_chunks
    return out


# ------------------------------------------------------------------ manual additions

class ManualEditor:
    """Adds PDFs/abstracts by hand, then re-chunks every chunk run so the paper is searchable.

    The file work is done by the core (corpus_builder: manifest, manual.jsonl, abstracts/;
    ingest.pipeline: chunks). Edits are serialized: one at a time.
    """

    def __init__(self, corpus_dir: Path, chunks_root: Path, chunk_service):
        self.corpus_dir, self.chunks_root, self.chunks = corpus_dir, chunks_root, chunk_service
        self._lock = threading.Lock()

    def _apply(self, edit, paper_id: str) -> dict:
        from ..core import paper_report, rebuild_runs  # imported here: heavy, only needed for edits

        with self._lock:
            row = edit()
            runs = rebuild_runs(self.corpus_dir, self.chunks_root)
            self.chunks.invalidate()
        ingest = []
        for r in runs:
            rep = paper_report(self.chunks_root / r["run"], paper_id) or {}
            ingest.append({"run": r["run"], "source": rep.get("source"), "n_chunks": int(rep.get("n_chunks") or 0),
                           "error": rep.get("error") or None, "warnings": rep.get("warnings") or None})
        return {"paper": row, "ingest": ingest}

    def add_pdf(self, paper_id: str, data: bytes) -> dict:
        from ..core import add_manual_pdf
        return self._apply(lambda: add_manual_pdf(self.corpus_dir, paper_id, data), paper_id)

    def remove_pdf(self, paper_id: str) -> dict:
        from ..core import remove_manual_pdf
        return self._apply(lambda: remove_manual_pdf(self.corpus_dir, paper_id), paper_id)

    def set_abstract(self, paper_id: str, abstract: str | None) -> dict:
        from ..core import set_manual_abstract
        return self._apply(lambda: set_manual_abstract(self.corpus_dir, paper_id, abstract), paper_id)
