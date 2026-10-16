"""Split ParsedDocuments into chunks for retrieval.

Parser-independent: works on any ParsedDocument. Chunks never cross section
boundaries (so every chunk has one clear section label for citations), are packed
paragraph by paragraph up to a target size, and overlap by a few sentences.
Sizes are in words, which avoids a tokenizer dependency (1 word ~ 1.3 tokens).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .documents import ParsedDocument

SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[\"'])")


@dataclass(frozen=True)
class ChunkConfig:
    size: int = 400      # target words per chunk
    overlap: int = 60    # words repeated from the end of the previous chunk
    min_words: int = 40  # a trailing piece shorter than this is merged into the previous chunk

    def __post_init__(self):
        if not 0 <= self.overlap < self.size:
            raise ValueError("overlap must be >= 0 and smaller than size")

    @property
    def name(self) -> str:
        return f"w{self.size}_o{self.overlap}"


@dataclass
class Chunk:
    chunk_id: str        # "<paper_id>#<index>", stable for a given parser + config
    paper_id: str
    index: int
    text: str
    section: str
    page_start: int | None
    page_end: int | None
    n_words: int
    source: str          # pdf / abstract / abstract_fallback
    parser: str
    # paper metadata, copied from the manifest so every chunk is self-contained
    title: str | None = None
    year: int | None = None
    authors: str | None = None
    doi: str | None = None
    venue: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def heading(self) -> str:
        """'Title (year) > Section', handy as a prefix when embedding or showing a chunk."""
        year = f" ({self.year})" if self.year else ""
        return f"{self.title or self.paper_id}{year} > {self.section}"


def _units(text: str, size: int) -> list[str]:
    """Split a paragraph into sentence-sized units no longer than `size` words."""
    out = []
    for sentence in SENTENCE_END.split(text):
        words = sentence.split()
        for i in range(0, len(words), size):
            out.append(" ".join(words[i:i + size]))
    return [u for u in out if u]


def chunk_document(doc: ParsedDocument, cfg: ChunkConfig, meta: dict | None = None) -> list[Chunk]:
    meta = meta or {}
    chunks: list[Chunk] = []

    for section in doc.sections:
        # (text, page) units in reading order
        units = [(u, p.page) for p in section.paragraphs for u in _units(p.text, cfg.size)]
        pieces: list[list[tuple[str, int | None]]] = []
        current: list[tuple[str, int | None]] = []
        n = 0
        for unit in units:
            w = len(unit[0].split())
            if current and n + w > cfg.size:
                pieces.append(current)
                # carry the last sentences (up to `overlap` words) into the next chunk
                carry, cw = [], 0
                for u in reversed(current):
                    uw = len(u[0].split())
                    if cw + uw > cfg.overlap:
                        break
                    carry.insert(0, u)
                    cw += uw
                current, n = carry, cw
            current.append(unit)
            n += w
        if current:
            if pieces and n < cfg.min_words:
                # tiny tail: merge into previous piece, minus the overlap it already shares
                tail = [u for u in current if u not in pieces[-1]]
                pieces[-1].extend(tail)
            else:
                pieces.append(current)

        for piece in pieces:
            text = " ".join(u for u, _ in piece)
            if len(text.split()) < 5:
                continue
            pages = [p for _, p in piece if p is not None]
            chunks.append(Chunk(
                chunk_id="", paper_id=doc.paper_id, index=0, text=text, section=section.title,
                page_start=min(pages) if pages else None, page_end=max(pages) if pages else None,
                n_words=len(text.split()), source=meta.get("source_override") or doc.source,
                parser=f"{doc.parser}@{doc.parser_version}", title=meta.get("title"), year=meta.get("year"),
                authors=meta.get("authors"), doi=meta.get("doi"), venue=meta.get("venue"),
            ))

    for i, c in enumerate(chunks):
        c.index, c.chunk_id = i, f"{doc.paper_id}#{i:03d}"
    return chunks
