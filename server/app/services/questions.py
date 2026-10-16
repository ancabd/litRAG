"""Read and write questions.yaml: the file stays the single source of truth for both
the UI and `evaluate.py`.

Every write is validated with the core's own rules (evaluation.questions), is
atomic (write a temp file, then rename), and is guarded by a version: the sha1 of
the file as the client last saw it. If the file changed in the meantime (edited in
a text editor, or in another tab), the write is refused with a conflict instead of
silently overwriting those edits.

The comment block at the top of the file is preserved. Comments inside individual
questions are not (YAML libraries drop them on rewrite); use the `notes` field.
"""
from __future__ import annotations

import hashlib
import re
import threading
from pathlib import Path

import yaml

from ..core import FIELDS, QuestionFileError, parse_questions


class VersionConflict(Exception):
    pass


class NotFound(Exception):
    pass


def _header(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            lines.append(line)
        else:
            break
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n\n" if lines else ""


def _clean(q: dict) -> dict:
    """Canonical field order; drop empty optional fields so the YAML stays tidy."""
    out = {}
    for k in FIELDS:
        v = q.get(k)
        if k in ("answer", "notes"):
            v = (v or "").strip() or None
        if k == "tags":
            v = [t.strip() for t in (v or []) if str(t).strip()] or None
        if k == "evidence":
            items = []
            for e in v or []:
                item = {"paper": str(e.get("paper") or "").strip()}
                if (e.get("quote") or "").strip():
                    item["quote"] = " ".join(str(e["quote"]).split())
                alts = _passages(e.get("alternatives"))
                if alts:
                    item["alternatives"] = alts
                items.append(item)
            v = items or None
        if k == "not_relevant":
            v = _passages(v) or None
        if v is not None and v != "":
            out[k] = v
    out.setdefault("split", "dev")
    return out


def _passages(items) -> list[dict]:
    """Clean a list of {paper, quote} passages; drop empty ones and duplicates."""
    out, seen = [], set()
    for e in items or []:
        paper, quote = str(e.get("paper") or "").strip(), " ".join(str(e.get("quote") or "").split())
        if paper and quote and (paper, quote) not in seen:
            seen.add((paper, quote))
            out.append({"paper": paper, "quote": quote})
    return out


def _dump(questions: list[dict]) -> str:
    blocks = [yaml.safe_dump([q], sort_keys=False, allow_unicode=True, width=110, default_flow_style=False)
              for q in questions]
    return "\n".join(blocks)  # blank line between questions, like the hand-written file


class QuestionStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()

    def _read(self) -> tuple[str, list[dict], str]:
        if not self.path.exists():
            return "", [], hashlib.sha1(b"").hexdigest()[:12]
        raw = self.path.read_bytes()
        text = raw.decode("utf-8")
        data = yaml.safe_load(text) or []
        if not isinstance(data, list):
            raise QuestionFileError(f"{self.path}: expected a list of questions")
        return text, data, hashlib.sha1(raw).hexdigest()[:12]

    def load(self) -> tuple[list[dict], str, list[str]]:
        """(questions, version, validation errors). Invalid files are still returned, so they can be fixed."""
        _, data, version = self._read()
        try:
            parse_questions(data, self.path.name)
            errors: list[str] = []
        except QuestionFileError as exc:
            errors = str(exc).splitlines()
        return data, version, errors

    def _write(self, expected_version: str, mutate) -> tuple[list[dict], str]:
        with self._lock:
            text, data, version = self._read()
            if expected_version != version:
                raise VersionConflict("questions.yaml changed since you loaded it")
            data = mutate([dict(q) for q in data])
            data = [_clean(q) for q in data]
            parse_questions(data, self.path.name)  # raises QuestionFileError with all problems
            out = (_header(text) or "# Retrieval eval questions. See EVAL.md for the format.\n\n") + _dump(data)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".yaml.tmp")
            tmp.write_text(out, encoding="utf-8")
            tmp.replace(self.path)
            return data, hashlib.sha1(out.encode("utf-8")).hexdigest()[:12]

    def next_id(self, data: list[dict]) -> str:
        nums = [int(m.group(1)) for q in data if (m := re.fullmatch(r"q(\d+)", str(q.get("id", ""))))]
        return f"q{(max(nums) + 1) if nums else 1:03d}"

    def create(self, question: dict, version: str) -> tuple[dict, str]:
        created = {}

        def mutate(data):
            q = dict(question)
            q["id"] = (q.get("id") or "").strip() or self.next_id(data)
            created.update(q)
            return data + [q]

        data, v = self._write(version, mutate)
        return next(q for q in data if q["id"] == created["id"]), v

    def update(self, qid: str, question: dict, version: str) -> tuple[dict, str]:
        def mutate(data):
            for i, q in enumerate(data):
                if str(q.get("id")) == qid:
                    data[i] = {**question, "id": qid}  # ids never change: results are tracked by id
                    return data
            raise NotFound(qid)

        data, v = self._write(version, mutate)
        return next(q for q in data if q["id"] == qid), v

    def modify(self, qid: str, version: str, change) -> tuple[dict, str]:
        """Apply `change(question_dict) -> question_dict` to one question, with the usual checks."""
        def mutate(data):
            for i, q in enumerate(data):
                if str(q.get("id")) == qid:
                    data[i] = {**change(dict(q)), "id": qid}
                    return data
            raise NotFound(qid)

        data, v = self._write(version, mutate)
        return next(q for q in data if q["id"] == qid), v

    def delete(self, qid: str, version: str) -> str:
        def mutate(data):
            kept = [q for q in data if str(q.get("id")) != qid]
            if len(kept) == len(data):
                raise NotFound(qid)
            return kept

        return self._write(version, mutate)[1]
