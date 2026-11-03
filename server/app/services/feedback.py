"""Your ratings of answers on the Ask page, kept in data/feedback/ratings.jsonl.

Each rating stores what produced the answer (method, model, retriever, prompt version, chunk
run, the passages it saw and cited, the agent's steps), so it still means something after the
prompts change. Two questions for an answer, one for a decline:

  faithful   every claim is backed by the passage it cites           yes / partly / no
  complete   it answers the question with everything relevant the
             corpus has (judged against the corpus, not the field)   yes / partly / no
  should_have_answered   (declines only)  the corpus does answer it   yes / no

Ratings are per answer and can be changed; saving the same id again replaces the record.
"""
from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

LEVELS = ("yes", "partly", "no")
SCORE = {"yes": 1.0, "partly": 0.5, "no": 0.0}
FEEDBACK_ID = re.compile(r"^[0-9a-f]{12}$")


class FeedbackError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def setup_of(r: dict) -> dict:
    g = r.get("generator") or {}
    return {"method": g.get("name"), "model": g.get("model"), "retriever": r.get("retriever"),
            "prompt_version": r.get("prompt_version"), "k": r.get("k")}


def setup_label(s: dict) -> str:
    """'Agent (sonnet-5-5) + Hybrid (bge-small)', like the run names on the Results page."""
    model = (s.get("model") or "").removeprefix("claude-")
    method = {"agent": f"Agent ({model})", "extractive": "Extractive"}.get(s.get("method") or "",
                                                                        f"Single shot ({model})")
    name, _, variant = (s.get("retriever") or "").partition(":")
    ret = "BM25" if name == "bm25" else f"{name.capitalize()} ({variant or 'bge-small'})" if name else "?"
    return f"{method} + {ret}"


class FeedbackStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        with open(self.path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def _write(self, rows: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".jsonl.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        tmp.replace(self.path)

    def all(self) -> list[dict]:
        return sorted(self._read(), key=lambda r: r.get("updated") or "", reverse=True)

    def save(self, answer: dict, rating: dict, comment: str | None, feedback_id: str | None = None) -> dict:
        rating = _check(rating, bool(answer.get("answerable")))
        if not str(answer.get("question") or "").strip():
            raise FeedbackError("The answer to rate has no question.")
        with self._lock:
            rows = self._read()
            old = next((r for r in rows if feedback_id and r["id"] == feedback_id), None)
            if feedback_id and old is None:
                raise FeedbackError(f"No rating {feedback_id}.")
            record = {
                "id": old["id"] if old else uuid.uuid4().hex[:12],
                "created": old["created"] if old else _now(),
                "updated": _now(),
                "rating": rating,
                "comment": (comment or "").strip() or None,
                # what was rated; on an update, the stored answer is kept as it was
                "answer": old["answer"] if old else _compact(answer),
            }
            rows = [r for r in rows if r["id"] != record["id"]] + [record]
            self._write(rows)
        return record

    def delete(self, feedback_id: str) -> None:
        with self._lock:
            rows = self._read()
            if not any(r["id"] == feedback_id for r in rows):
                raise FeedbackError(f"No rating {feedback_id}.")
            self._write([r for r in rows if r["id"] != feedback_id])

    def summary(self) -> list[dict]:
        """Ratings per setup: counts and mean score (yes 1, partly 0.5, no 0) per question."""
        groups: dict[str, dict] = {}
        for r in self._read():
            s = setup_of(r["answer"])
            key = json.dumps({k: s[k] for k in ("method", "model", "retriever", "prompt_version")}, sort_keys=True)
            g = groups.setdefault(key, {"setup": s, "label": setup_label(s), "n": 0, "answered": 0, "declined": 0,
                                        "faithful": _empty(), "complete": _empty(),
                                        "should_have_answered": {"yes": 0, "no": 0}, "last": None})
            g["n"] += 1
            g["last"] = max(g["last"] or "", r.get("updated") or "")
            rating = r["rating"]
            if r["answer"].get("answerable"):
                g["answered"] += 1
                for dim in ("faithful", "complete"):
                    if rating.get(dim):
                        g[dim][rating[dim]] += 1
            else:
                g["declined"] += 1
                if rating.get("should_have_answered"):
                    g["should_have_answered"][rating["should_have_answered"]] += 1
        out = []
        for g in groups.values():
            for dim in ("faithful", "complete"):
                n = sum(g[dim][lvl] for lvl in LEVELS)
                g[dim]["n"] = n
                g[dim]["score"] = round(sum(SCORE[lvl] * g[dim][lvl] for lvl in LEVELS) / n, 3) if n else None
            out.append(g)
        return sorted(out, key=lambda g: g["last"] or "", reverse=True)


def _empty() -> dict:
    return {lvl: 0 for lvl in LEVELS}


def _check(rating: dict, answered: bool) -> dict:
    out: dict = {}
    if answered:
        for dim in ("faithful", "complete"):
            v = rating.get(dim)
            if v is not None and v not in LEVELS:
                raise FeedbackError(f"{dim} must be one of {', '.join(LEVELS)}.")
            out[dim] = v
    else:
        v = rating.get("should_have_answered")
        if v is not None and v not in ("yes", "no"):
            raise FeedbackError("should_have_answered must be yes or no.")
        out["should_have_answered"] = v
    if not any(out.values()):
        raise FeedbackError("Pick at least one rating.")
    return out


def _compact(a: dict) -> dict:
    """The answer as rated, without the passage texts (they're in the chunk run, by id)."""
    keep = ("question", "answer", "answerable", "citations", "invalid_citations", "generator", "prompt_version",
            "retriever", "run", "k", "input_tokens", "output_tokens", "cost", "seconds", "warnings")
    out = {k: a.get(k) for k in keep}
    out["passages"] = [{"chunk_id": p.get("chunk_id"), "paper_id": p.get("paper_id"), "rank": p.get("rank"),
                        "cited_as": p.get("cited_as")} for p in a.get("passages") or []]
    out["trace"] = [{k: v for k, v in step.items() if k != "passages"} for step in a.get("trace") or []]
    return out
