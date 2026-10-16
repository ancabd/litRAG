"""Find the gold chunks for an evidence quote, in any chunking of the corpus.

A chunk counts as gold for an evidence item if it belongs to the evidence paper
and contains enough of the quote. Matching is on word trigrams after normalizing
case and punctuation, so it tolerates small differences in parsing (ligatures,
spacing, a garbled symbol) and quotes that are split across two chunks.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .questions import Evidence, Question


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).lower())


def ngrams(ws: list[str], n: int = 3) -> set[tuple[str, ...]]:
    if len(ws) < n:
        return {tuple(ws)} if ws else set()
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def quote_coverage(quote: str, text: str, n: int = 3) -> float:
    """Fraction of the quote's word n-grams that appear in `text`."""
    q = ngrams(words(quote), n)
    if not q:
        return 0.0
    if len(next(iter(q))) < n:  # very short quote: whole-word match ("sine" must not match "cosine")
        return 1.0 if f" {' '.join(next(iter(q)))} " in f" {' '.join(words(text))} " else 0.0
    return len(q & ngrams(words(text), n)) / len(q)


@dataclass
class ResolvedEvidence:
    paper: str
    quote: str | None
    gold_chunks: set[str]          # chunks matching the original quote (strict)
    paper_in_corpus: bool
    paper_source: str | None       # pdf / abstract / abstract_fallback, from the chunks
    alt_chunks: set[str] = field(default_factory=set)      # chunks matching any alternative (lenient)
    alt_papers: set[str] = field(default_factory=set)
    unresolved_alternatives: list[str] = field(default_factory=list)  # "paper: quote…" that matched nothing

    @property
    def resolved(self) -> bool:
        return bool(self.gold_chunks)

    @property
    def lenient_chunks(self) -> set[str]:
        return self.gold_chunks | self.alt_chunks


class GoldIndex:
    """Chunks grouped by paper, with cached n-gram sets for fast matching."""

    def __init__(self, chunks: list[dict], threshold: float = 0.5):
        self.threshold = threshold
        self.by_paper: dict[str, list[dict]] = {}
        for c in chunks:
            self.by_paper.setdefault(c["paper_id"], []).append(c)
        self._grams: dict[str, set] = {}

    def _chunk_grams(self, c: dict) -> set:
        if c["chunk_id"] not in self._grams:
            self._grams[c["chunk_id"]] = ngrams(words(c["text"]))
        return self._grams[c["chunk_id"]]

    def resolve(self, ev: Evidence) -> ResolvedEvidence:
        r = self._resolve_one(ev)
        for alt in ev.alternatives:
            a = self._resolve_one(alt)
            if a.gold_chunks:
                r.alt_chunks |= a.gold_chunks
                r.alt_papers.add(alt.paper)
            else:
                r.unresolved_alternatives.append(f"{alt.paper}: {(alt.quote or '')[:60]}")
        return r

    def resolve_passages(self, passages: list[Evidence]) -> set[str]:
        """Chunks matching any of the given passages (used for not_relevant judgments)."""
        out: set[str] = set()
        for p in passages:
            out |= self._resolve_one(p).gold_chunks
        return out

    def _resolve_one(self, ev: Evidence) -> ResolvedEvidence:
        chunks = self.by_paper.get(ev.paper, [])
        source = chunks[0].get("source") if chunks else None
        gold: set[str] = set()
        if ev.quote and chunks:
            qw = words(ev.quote)
            q = ngrams(qw)
            for c in chunks:
                if len(qw) < 3:
                    cov = quote_coverage(ev.quote, c["text"])
                else:
                    cov = len(q & self._chunk_grams(c)) / len(q)
                if cov >= self.threshold:
                    gold.add(c["chunk_id"])
        return ResolvedEvidence(ev.paper, ev.quote, gold, bool(chunks), source)

    def resolve_question(self, q: Question) -> list[ResolvedEvidence]:
        return [self.resolve(e) for e in q.evidence]

    def best_matches(self, ev: Evidence, top: int = 3) -> list[tuple[float, dict]]:
        """For `check`: the closest chunks of the paper, to help fix a quote that doesn't match."""
        if not ev.quote:
            return []
        scored = [(quote_coverage(ev.quote, c["text"]), c) for c in self.by_paper.get(ev.paper, [])]
        return sorted(scored, key=lambda x: -x[0])[:top]
