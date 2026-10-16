"""Eval runs: the folders `evaluate.py run` writes under runs/ (summary.json, per_question.jsonl, report.md).

The app reads the same folders the CLI writes, and starts new runs with the same core
function (evaluation.runner.run_eval), so terminal runs and app runs are interchangeable.
"""
from __future__ import annotations

import json
import re
import shutil
import threading
from pathlib import Path

from ..core import run_eval

NAME = re.compile(r"^[A-Za-z0-9_.@-]+$")
HEADLINE = ["hit@1", "hit@5", "hit@10", "recall@10", "mrr", "ndcg@10", "paper_hit@10"]


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _first_rank(retrieved: list[dict], gold: set[str]) -> int | None:
    return next((h["rank"] for h in retrieved if h["chunk_id"] in gold), None)


def _label(cid: str, row: dict) -> dict:
    for i, e in enumerate(row.get("evidence") or []):
        if cid in (e.get("gold_chunks") or []):
            return {"kind": "evidence", "item": i}
    for i, e in enumerate(row.get("evidence") or []):
        if cid in (e.get("alt_chunks") or []):
            return {"kind": "alternative", "item": i}
    if cid in (row.get("not_relevant_chunks") or []):
        return {"kind": "not_relevant", "item": None}
    return {"kind": "unjudged", "item": None}


def ranks(row: dict) -> dict:
    """First rank of a gold chunk, strict (original evidence) and lenient (alternatives too)."""
    strict = set().union(*[set(e.get("gold_chunks") or []) for e in row.get("evidence") or []] or [set()])
    lenient = strict.union(*[set(e.get("alt_chunks") or []) for e in row.get("evidence") or []] or [set()])
    return {"strict_rank": _first_rank(row["retrieved"], strict), "lenient_rank": _first_rank(row["retrieved"], lenient)}


class EvalRunService:
    def __init__(self, runs_dir: Path, chunks_root: Path, questions_file: Path):
        self.root, self.chunks_root, self.questions_file = runs_dir, chunks_root, questions_file
        self._lock = threading.Lock()

    def _dir(self, name: str) -> Path | None:
        if not NAME.match(name):
            return None
        d = (self.root / name).resolve()
        if d.parent != self.root.resolve() or not (d / "summary.json").exists():
            return None
        return d

    def list(self) -> list[dict]:
        if not self.root.exists():
            return []
        out = []
        for d in self.root.iterdir():
            s = _read_json(d / "summary.json") if d.is_dir() and NAME.match(d.name) else None
            if s:
                out.append(self._brief(d.name, s))
        return sorted(out, key=lambda r: r["created"] or "", reverse=True)

    @staticmethod
    def _brief(name: str, s: dict) -> dict:
        a = (s.get("results") or {}).get("all") or {}
        cc = s.get("chunks_config") or {}
        return {
            "name": name,
            "created": s.get("created"),
            "retriever": s.get("retriever"),
            "chunks": Path(s.get("chunks") or "").name or None,
            "parser": cc.get("parser"),
            "split": s.get("split"),
            "n_scored": s.get("n_scored"),
            "n_questions": s.get("n_questions"),
            "questions_sha1": s.get("questions_sha1"),
            "git_commit": s.get("git_commit"),
            "headline": {m: {"strict": (a.get(m) or {}).get("mean"), "lenient": (a.get("lenient_" + m) or {}).get("mean")}
                         for m in HEADLINE if m in a},
            "judged": (a.get("judged@10") or {}).get("mean"),
        }

    def get(self, name: str, chunk_lookup) -> dict | None:
        """Full run. `chunk_lookup(run_name)` -> {chunk_id: chunk} or None, to show passage text."""
        d = self._dir(name)
        if d is None:
            return None
        s = _read_json(d / "summary.json")
        rows = []
        if (d / "per_question.jsonl").exists():
            with open(d / "per_question.jsonl", encoding="utf-8") as fh:
                rows = [json.loads(line) for line in fh if line.strip()]
        chunks_name = Path(s.get("chunks") or "").name
        chunks = chunk_lookup(chunks_name) or {}
        for r in rows:
            r.update(ranks(r))
            for h in r["retrieved"]:
                c = chunks.get(h["chunk_id"])
                h["label"] = _label(h["chunk_id"], r)
                if c:
                    h.update({"paper_id": c["paper_id"], "title": c.get("title"), "year": c.get("year"),
                              "section": c.get("section"), "page_start": c.get("page_start"),
                              "page_end": c.get("page_end"), "source": c.get("source"), "text": c.get("text"),
                              "n_words": c.get("n_words")})
        report = (d / "report.md").read_text(encoding="utf-8") if (d / "report.md").exists() else None
        return {**self._brief(name, s), "summary": s, "questions": rows, "report": report,
                "chunks_available": bool(chunks)}

    def start(self, chunks_run: str, retriever: str, split: str | None) -> str:
        if not NAME.match(chunks_run) or not (self.chunks_root / chunks_run / "chunks.jsonl").exists():
            raise FileNotFoundError(f"No chunk run '{chunks_run}'")
        with self._lock:  # one eval at a time
            run_dir = run_eval(self.questions_file, self.chunks_root / chunks_run, retriever,
                               None if split in (None, "all") else split, out_root=self.root)
        return run_dir.name

    def delete(self, name: str) -> bool:
        d = self._dir(name)
        if d is None:
            return False
        shutil.rmtree(d)
        return True

    def compare(self, names: list[str]) -> dict:
        runs = []
        for n in names:
            d = self._dir(n)
            if d is None:
                raise FileNotFoundError(n)
            s = _read_json(d / "summary.json")
            rows = {}
            if (d / "per_question.jsonl").exists():
                for line in (d / "per_question.jsonl").read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        r = json.loads(line)
                        rows[r["id"]] = {"question": r["question"], **ranks(r)}
            runs.append((n, s, rows))
        ids = sorted({qid for _, _, rows in runs for qid in rows})
        return {
            "runs": [{**self._brief(n, s), "results": (s.get("results") or {}).get("all") or {}} for n, s, _ in runs],
            "same_questions": len({s.get("questions_sha1") for _, s, _ in runs}) <= 1,
            "questions": [{"id": qid,
                           "question": next((rows[qid]["question"] for _, _, rows in runs if qid in rows), ""),
                           "per_run": [({"strict_rank": rows[qid]["strict_rank"], "lenient_rank": rows[qid]["lenient_rank"]}
                                        if qid in rows else None) for _, _, rows in runs]}
                          for qid in ids],
        }
