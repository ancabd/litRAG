"""BM25 keyword retrieval, implemented directly on an inverted index (numpy).

Written out rather than taken from a library so the tokenizer can handle
scientific text: model and force-field names like "TIP3P", "ff14SB", "E(3)",
"SO(3)" or "DFT-D3" stay searchable as whole tokens, and hyphenated terms are
indexed both whole and by part ("machine-learned" -> machine-learned, machine, learned).
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter

import numpy as np

from .base import Hit, Retriever

STOPWORDS = frozenset("""
a an and are as at be been but by can for from has have in into is it its of on or such that the
their them then there these they this to was were which while with we our us also not no than
""".split())

TOKEN = re.compile(r"[a-z0-9]+(?:\([a-z0-9]+\))?(?:[-'.][a-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", text).lower()
    out = []
    for tok in TOKEN.findall(text):
        tok = tok.strip(".'")
        if not tok or tok in STOPWORDS:
            continue
        out.append(tok)
        # also index the parts: "e(3)-equivariant" -> e(3), equivariant, e, 3
        parts = [p for p in tok.split("-") if p] if "-" in tok else []
        for p in parts:
            if p not in STOPWORDS:
                out.append(p)
        for p in parts or [tok]:
            if "(" in p:
                out.extend(s for s in re.split(r"[()]", p) if s and s not in STOPWORDS)
    return out


class BM25Retriever(Retriever):
    name = "bm25"

    def __init__(self, k1: float = 1.2, b: float = 0.75, include_title: bool = True,
                 include_section: bool = True):
        self.k1, self.b = k1, b
        self.include_title, self.include_section = include_title, include_section

    def config(self) -> dict:
        return {"name": self.name, "k1": self.k1, "b": self.b,
                "include_title": self.include_title, "include_section": self.include_section}

    def _doc_text(self, c: dict) -> str:
        parts = []
        if self.include_title and c.get("title"):
            parts.append(c["title"])
        if self.include_section and c.get("section"):
            parts.append(c["section"])
        parts.append(c["text"])
        return "\n".join(parts)

    def index(self, chunks: list[dict]) -> None:
        self.ids = [c["chunk_id"] for c in chunks]
        n = len(chunks)
        postings: dict[str, tuple[list[int], list[int]]] = {}
        lengths = np.zeros(n, dtype=np.float32)
        for i, c in enumerate(chunks):
            toks = tokenize(self._doc_text(c))
            lengths[i] = len(toks)
            for term, tf in Counter(toks).items():
                docs, tfs = postings.setdefault(term, ([], []))
                docs.append(i)
                tfs.append(tf)
        avgdl = float(lengths.mean()) if n else 1.0
        norm = self.k1 * (1 - self.b + self.b * lengths / max(avgdl, 1e-9))
        self.postings = {}
        for term, (docs, tfs) in postings.items():
            d = np.asarray(docs, dtype=np.int32)
            tf = np.asarray(tfs, dtype=np.float32)
            idf = math.log(1 + (n - len(d) + 0.5) / (len(d) + 0.5))
            # precompute each posting's full BM25 contribution: query time is then just a sum
            self.postings[term] = (d, idf * tf * (self.k1 + 1) / (tf + norm[d]))
        self.n = n

    def search(self, query: str, k: int = 10) -> list[Hit]:
        scores = np.zeros(self.n, dtype=np.float32)
        for term in set(tokenize(query)):
            if term in self.postings:
                d, w = self.postings[term]
                scores[d] += w
        k = min(k, self.n)
        if k <= 0:
            return []
        top = np.argpartition(-scores, k - 1)[:k]
        top = top[np.argsort(-scores[top], kind="stable")]
        return [Hit(self.ids[i], float(scores[i]), r) for r, i in enumerate(top, 1) if scores[i] > 0]
