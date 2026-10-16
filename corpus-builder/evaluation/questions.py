"""The question file format, and its validation.

A question file is YAML: a list of questions like

    - id: q001
      question: What cutoff function do Behler and Parrinello use?
      type: lookup                 # lookup | multihop | comparison | unanswerable
      tags: [equation, behler-parrinello]
      split: dev                   # dev (tune on these) | test (final numbers only)
      answer: A cosine cutoff, fc = 0.5 [cos(pi R/Rc) + 1] for R <= Rc, else 0.
      evidence:
        - paper: W2042658765       # OpenAlex id, as in the manifest / chunk paper_id
          quote: "0.5 [cos(pi Rij/Rc) + 1]"   # a short exact-ish passage from the paper

Evidence is a paper plus a quote, never a chunk id: chunk ids change with every
parser or chunk size, while the quote finds the right chunk(s) in any of them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

TYPES = ("lookup", "multihop", "comparison", "unanswerable")
SPLITS = ("dev", "test")


@dataclass
class Evidence:
    paper: str
    quote: str | None = None
    # other passages that answer the same part of the question (e.g. a later paper restating the
    # original result). Strict scoring uses only the original; lenient scoring accepts these too.
    alternatives: list["Evidence"] = field(default_factory=list)


@dataclass
class Question:
    id: str
    question: str
    type: str
    tags: list[str] = field(default_factory=list)
    split: str = "dev"
    answer: str | None = None
    evidence: list[Evidence] = field(default_factory=list)
    notes: str | None = None
    # passages reviewed and judged NOT to answer the question (so they aren't reviewed again)
    not_relevant: list[Evidence] = field(default_factory=list)

    @property
    def answerable(self) -> bool:
        return self.type != "unanswerable"


class QuestionFileError(ValueError):
    pass


FIELDS = ("id", "question", "type", "tags", "split", "answer", "evidence", "notes", "not_relevant")
EVIDENCE_FIELDS = ("paper", "quote", "alternatives")


def _passages(items, where: str, what: str, errors: list[str]) -> list[Evidence]:
    """Parse a list of {paper, quote} passages (alternatives, not_relevant): both fields required."""
    out = []
    if items is None:
        return out
    if not isinstance(items, list):
        errors.append(f"{where}: {what} must be a list")
        return out
    for e in items:
        if not isinstance(e, dict) or not e.get("paper") or not e.get("quote"):
            errors.append(f"{where}: each item in {what} needs a 'paper' and a 'quote'")
            continue
        if set(e) - {"paper", "quote"}:
            errors.append(f"{where}: unknown field(s) {sorted(set(e) - {'paper', 'quote'})} in {what}")
        out.append(Evidence(str(e["paper"]), str(e["quote"])))
    return out


def load_questions(path: Path) -> list[Question]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    return parse_questions(data, str(path))


def parse_questions(data, path: str = "questions") -> list[Question]:
    """Validate already-loaded question data (a list of dicts). Raises QuestionFileError."""
    if not isinstance(data, list):
        raise QuestionFileError(f"{path}: expected a list of questions at the top level")
    questions, errors, seen = [], [], set()
    for i, raw in enumerate(data):
        where = f"{path}, question #{i + 1}"
        if not isinstance(raw, dict):
            errors.append(f"{where}: not a mapping")
            continue
        qid = str(raw.get("id") or "")
        where = f"{path}, {qid or f'question #{i + 1}'}"
        unknown = set(raw) - set(FIELDS)
        if unknown:
            errors.append(f"{where}: unknown field(s) {sorted(unknown)} (typo?)")
        if not qid:
            errors.append(f"{where}: missing id")
        elif qid in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(qid)
        if not str(raw.get("question") or "").strip():
            errors.append(f"{where}: missing question text")
        qtype = raw.get("type")
        if qtype not in TYPES:
            errors.append(f"{where}: type must be one of {TYPES}, got {qtype!r}")
        split = raw.get("split", "dev")
        if split not in SPLITS:
            errors.append(f"{where}: split must be one of {SPLITS}, got {split!r}")
        tags = raw.get("tags") or []
        if not isinstance(tags, list):
            errors.append(f"{where}: tags must be a list, e.g. [equation]")
            tags = []
        evidence = []
        for e in raw.get("evidence") or []:
            if not isinstance(e, dict) or not e.get("paper"):
                errors.append(f"{where}: each evidence item needs a 'paper' (and ideally a 'quote')")
                continue
            if set(e) - set(EVIDENCE_FIELDS):
                errors.append(f"{where}: unknown field(s) {sorted(set(e) - set(EVIDENCE_FIELDS))} in evidence")
            alts = _passages(e.get("alternatives"), where, "alternatives", errors)
            evidence.append(Evidence(str(e["paper"]), str(e["quote"]) if e.get("quote") else None, alts))
        not_relevant = _passages(raw.get("not_relevant"), where, "not_relevant", errors)
        if qtype == "unanswerable" and evidence:
            errors.append(f"{where}: unanswerable questions must not have evidence")
        if qtype in TYPES and qtype != "unanswerable" and not evidence:
            errors.append(f"{where}: answerable questions need at least one evidence item")
        if qtype in ("multihop", "comparison") and len(evidence) < 2:
            errors.append(f"{where}: {qtype} questions need evidence from at least two places")
        questions.append(Question(qid, str(raw.get("question", "")).strip(), qtype, [str(t) for t in tags],
                                  split, raw.get("answer"), evidence, raw.get("notes"), not_relevant))
    if errors:
        raise QuestionFileError("\n".join(errors))
    return questions
