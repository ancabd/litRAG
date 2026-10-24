"""Library: one chunk run, and every way of looking things up in it.

The CLI, the evals, the server and the generators (including the agent's tools) all go
through this one object, so they search and read the corpus the same way.

    lib = Library.load(paths.default_chunk_run())
    hits = lib.search("equivariant message passing", k=8)              # ranked Hits
    hits = lib.search("training data", paper="W4225405705")            # within one paper
    lib.chunk("W4225405705#003"), lib.neighbours("W4225405705#003")    # read around a passage
    lib.paper("W4225405705")                                           # title, year, sections
    lib.section_chunks("W4225405705", "2 Methods > 2.1 Equivariant features")

Retriever indexes are built on first use and cached per retriever (and its options).
"""
from __future__ import annotations

import json
import threading
from pathlib import Path

from retrieval import Hit, Retriever, get_retriever, load_chunks

PAPER_FIELDS = ("title", "year", "authors", "venue", "doi")


class Library:
    def __init__(self, chunks: list[dict], name: str | None = None, info: dict | None = None,
                 path: Path | None = None):
        self.name, self.info, self.path = name, info, path
        self.chunks = chunks
        self.by_id: dict[str, dict] = {c["chunk_id"]: c for c in chunks}
        self.by_paper: dict[str, list[dict]] = {}
        for c in chunks:
            self.by_paper.setdefault(c["paper_id"], []).append(c)
        for cs in self.by_paper.values():
            cs.sort(key=lambda c: c.get("index", 0))
        self._retrievers: dict[str, Retriever] = {}
        self._gold = None
        self._lock = threading.RLock()

    @classmethod
    def load(cls, path: Path | str) -> "Library":
        """From a chunk run folder (or its chunks.jsonl)."""
        path = Path(path)
        folder = path if path.is_dir() else path.parent
        info = None
        if (folder / "run.json").exists():
            try:
                info = json.loads((folder / "run.json").read_text(encoding="utf-8"))
            except ValueError:
                info = None
        return cls(load_chunks(path), name=folder.name, info=info, path=folder)

    # ------------------------------------------------------------------ search

    def retriever(self, name: str = "bm25", **options) -> Retriever:
        key = name + (json.dumps(options, sort_keys=True) if options else "")
        with self._lock:
            if key not in self._retrievers:
                r = get_retriever(name, **options)
                r.index(self.chunks)
                self._retrievers[key] = r
            return self._retrievers[key]

    def search(self, query: str, k: int = 10, retriever: str = "bm25", paper: str | None = None,
               year_from: int | None = None, year_to: int | None = None, exclude: set[str] | None = None) -> list[Hit]:
        """Top k chunks for `query`, optionally only from one paper or a range of years.

        Filters are applied to the full ranking, so a filtered search still returns k hits when
        k matching chunks exist. Ranks are renumbered 1..k after filtering.
        """
        r = self.retriever(retriever)
        filtered = paper is not None or year_from is not None or year_to is not None or bool(exclude)
        hits = r.search(query, k=len(self.chunks) if filtered else k)
        if filtered:
            def keep(h: Hit) -> bool:
                c = self.by_id[h.chunk_id]
                y = c.get("year")
                return ((paper is None or c["paper_id"] == paper)
                        and (year_from is None or (y is not None and y >= year_from))
                        and (year_to is None or (y is not None and y <= year_to))
                        and not (exclude and h.chunk_id in exclude))
            hits = [h for h in hits if keep(h)]
        return [Hit(h.chunk_id, h.score, i) for i, h in enumerate(hits[:k], 1)]

    # ------------------------------------------------------------------ reading

    def chunk(self, chunk_id: str) -> dict | None:
        return self.by_id.get(chunk_id)

    def neighbours(self, chunk_id: str, before: int = 1, after: int = 1) -> list[dict]:
        """The chunk with up to `before`/`after` chunks around it from the same paper, in reading order."""
        c = self.by_id.get(chunk_id)
        if c is None:
            return []
        cs = self.by_paper[c["paper_id"]]
        i = next(i for i, x in enumerate(cs) if x["chunk_id"] == chunk_id)
        return cs[max(0, i - before): i + after + 1]

    def paper(self, paper_id: str) -> dict | None:
        """Metadata and outline of a paper, from its chunks: title, year, ..., source, sections."""
        cs = self.by_paper.get(paper_id)
        if not cs:
            return None
        first = cs[0]
        return {"paper_id": paper_id, **{f: first.get(f) for f in PAPER_FIELDS},
                "source": "pdf" if any(c.get("source") == "pdf" for c in cs) else first.get("source"),
                "n_chunks": len(cs), "sections": self.sections(paper_id)}

    def sections(self, paper_id: str) -> list[dict]:
        """[{section, n_chunks, first_chunk}] in reading order."""
        out: list[dict] = []
        for c in self.by_paper.get(paper_id, []):
            if out and out[-1]["section"] == c.get("section"):
                out[-1]["n_chunks"] += 1
            else:
                out.append({"section": c.get("section"), "n_chunks": 1, "first_chunk": c["chunk_id"]})
        return out

    def section_chunks(self, paper_id: str, section: str, include_subsections: bool = True) -> list[dict]:
        """Chunks of one section. `2 Methods` also returns `2 Methods > 2.1 ...` unless include_subsections=False."""
        def match(s: str | None) -> bool:
            return s == section or (include_subsections and bool(s) and s.startswith(section + " > "))
        return [c for c in self.by_paper.get(paper_id, []) if match(c.get("section"))]

    # ------------------------------------------------------------------ misc

    @property
    def gold(self):
        """Evidence-quote matcher over these chunks (built on first use)."""
        with self._lock:
            if self._gold is None:
                from evaluation.matching import GoldIndex
                self._gold = GoldIndex(self.chunks)
            return self._gold

    def chunk_counts(self) -> dict[str, int]:
        return {pid: len(cs) for pid, cs in self.by_paper.items()}

    def __len__(self) -> int:
        return len(self.chunks)


__all__ = ["Library"]
