"""Evidence checking for the UI: does a (paper, quote) pair land in a chunk, and where exactly?

Uses the same matching as `evaluate.py` (core GoldIndex), and adds character spans
of the matched words so the UI can highlight them.
"""
from __future__ import annotations

import re

from ..core import Evidence, GoldIndex, ngrams, parse_questions, quote_coverage, words
from .chunks import RunData

WORD = re.compile(r"[A-Za-z0-9]+")


def match_spans(quote: str, text: str, n: int = 3) -> list[tuple[int, int]]:
    """Character spans in `text` covered by the quote's word n-grams (merged)."""
    qw = words(quote)
    if not qw:
        return []
    found = [(m.start(), m.end(), m.group().lower()) for m in WORD.finditer(text)]
    tw = [w for _, _, w in found]
    marked = [False] * len(tw)
    size = n if len(qw) >= n else len(qw)
    grams = ngrams(qw, size)
    for i in range(len(tw) - size + 1):
        if tuple(tw[i:i + size]) in grams:
            for j in range(i, i + size):
                marked[j] = True
    spans: list[tuple[int, int]] = []
    for (s, e, _), m in zip(found, marked):
        if not m:
            continue
        if spans and re.fullmatch(r"\W*", text[spans[-1][1]:s]):
            spans[-1] = (spans[-1][0], e)  # adjacent marked words: extend the span
        else:
            spans.append((s, e))
    return spans


def chunk_view(c: dict, quote: str | None = None, coverage: float | None = None) -> dict:
    out = {k: c.get(k) for k in ("chunk_id", "paper_id", "section", "page_start", "page_end", "source",
                                 "n_words", "text")}
    if quote:
        out["highlights"] = match_spans(quote, c["text"])
    if coverage is not None:
        out["coverage"] = round(coverage, 3)
    return out


def check_evidence(run: RunData, paper: str, quote: str | None, threshold: float = 0.5) -> dict:
    """Status of one evidence item against a chunk run.

    status: ok | paper_missing | no_quote | not_found
    """
    gold: GoldIndex = run.gold
    chunks = gold.by_paper.get(paper, [])
    base = {"paper": paper, "quote": quote, "run": run.name,
            "paper_source": chunks[0].get("source") if chunks else None}
    if not chunks:
        return {**base, "status": "paper_missing", "gold": [], "closest": []}
    if not quote or not quote.strip():
        return {**base, "status": "no_quote", "gold": [], "closest": []}
    scored = sorted(((quote_coverage(quote, c["text"]), c) for c in chunks), key=lambda x: -x[0])
    gold_chunks = [chunk_view(c, quote, cov) for cov, c in scored if cov >= threshold]
    if gold_chunks:
        return {**base, "status": "ok", "gold": gold_chunks, "closest": []}
    return {**base, "status": "not_found", "gold": [],
            "closest": [chunk_view(c, quote, cov) for cov, c in scored[:3] if cov > 0]}


def evidence_summary(run: RunData | None, question: dict) -> dict:
    """Compact per-question status for list views: ok | problem | unchecked | none."""
    ev = question.get("evidence") or []
    if question.get("type") == "unanswerable":
        return {"status": "none", "items": []}
    if run is None:
        return {"status": "unchecked", "items": []}
    items = []
    for e in ev:
        r = check_evidence(run, str(e.get("paper") or ""), e.get("quote"))
        alts = [check_evidence(run, str(a.get("paper") or ""), a.get("quote")) for a in e.get("alternatives") or []]
        items.append({"paper": r["paper"], "status": r["status"], "gold": [g["chunk_id"] for g in r["gold"]],
                      "alternatives": [{"paper": a["paper"], "status": a["status"],
                                        "gold": [g["chunk_id"] for g in a["gold"]]} for a in alts]})
    ok = items and all(i["status"] == "ok" and all(a["status"] == "ok" for a in i["alternatives"]) for i in items)
    return {"status": "ok" if ok else "problem", "items": items}


# ------------------------------------------------------------------ reviewing retrieved passages

def quote_for_chunk(c: dict, n: int = 28) -> str:
    """A quote that identifies this passage: words from the middle of the chunk.

    The start of a chunk overlaps with the previous one, so a quote from there would match
    two chunks; the middle doesn't. Being plain text, the quote still finds the right chunk
    after re-chunking with other sizes.
    """
    ws = c["text"].split()
    if len(ws) <= n:
        return " ".join(ws)
    start = max(0, len(ws) // 2 - n // 2)
    return " ".join(ws[start:start + n])


def judgments(run: RunData, question: dict) -> dict[str, dict]:
    """chunk_id -> {kind: evidence|alternative|not_relevant, item: evidence index}."""
    q = parse_questions([question])[0]
    gold: GoldIndex = run.gold
    out: dict[str, dict] = {}
    for c in gold.resolve_passages(q.not_relevant):
        out[c] = {"kind": "not_relevant", "item": None}
    for i, ev in enumerate(q.evidence):
        r = gold.resolve(ev)
        for c in r.alt_chunks:
            out[c] = {"kind": "alternative", "item": i}
        for c in r.gold_chunks:
            out[c] = {"kind": "evidence", "item": i}
    return out


def judge(question: dict, chunk: dict, kind: str, item: int, run: RunData) -> dict:
    """Return the question with `chunk` marked as an alternative for evidence `item`, as not relevant,
    or (kind == "clear") with any judgment of it removed."""
    gold: GoldIndex = run.gold
    cid = chunk["chunk_id"]
    q = dict(question)
    evidence = [dict(e) for e in q.get("evidence") or []]

    def matches(p: dict) -> bool:
        return cid in gold.resolve_passages([Evidence(p["paper"], p["quote"])])

    current = judgments(run, question).get(cid)
    if current and current["kind"] == "evidence":
        raise ValueError("This passage is already the question's own evidence.")
    # remove existing judgments of this chunk first, so a passage is only ever in one place
    q["not_relevant"] = [p for p in q.get("not_relevant") or [] if not matches(p)]
    for e in evidence:
        e["alternatives"] = [a for a in e.get("alternatives") or [] if not matches(a)]
    passage = {"paper": chunk["paper_id"], "quote": quote_for_chunk(chunk)}
    if kind == "alternative":
        if not 0 <= item < len(evidence):
            raise ValueError(f"No evidence item {item + 1} on this question.")
        evidence[item]["alternatives"] = evidence[item]["alternatives"] + [passage]
    elif kind == "not_relevant":
        q["not_relevant"] = q["not_relevant"] + [passage]
    elif kind != "clear":
        raise ValueError(f"Unknown judgment {kind!r}")
    q["evidence"] = evidence
    return q
