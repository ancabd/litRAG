"""PyMuPDF-based parser for scientific papers.

Fast and dependency-light. On top of raw text extraction it:
  - drops running headers/footers, page numbers and the vertical arXiv stamp
  - detects section headings (numbering, known section names, font size, bold)
  - removes the reference list and boilerplate (acknowledgements, author
    contributions, competing interests), but keeps appendices / Methods that come
    after the references (common in Nature-family journals and arXiv papers)
  - re-joins hyphenated line breaks and normalizes ligatures
  - records the page of every paragraph, for citations

Known limits: equations come out as linearized symbols, tables as loose text,
and unusual layouts may get a few headings wrong. Use `parse_corpus.py inspect`
to look at the output, and switch parser if it is not good enough.
"""
from __future__ import annotations

import re
import statistics
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from ..documents import Paragraph, ParsedDocument, ParseError, Section
from .base import Parser

KNOWN_SECTIONS = {
    "abstract", "introduction", "background", "related work", "related works", "theory", "method",
    "methods", "methodology", "materials and methods", "computational methods", "computational details",
    "simulation details", "model", "models", "approach", "experiments", "experimental setup",
    "results", "results and discussion", "discussion", "conclusion", "conclusions", "summary",
    "outlook", "summary and outlook", "conclusions and outlook", "data availability",
    "code availability", "data and code availability", "appendix", "appendices", "supplementary information",
    "supplementary material", "supporting information",
    # sections dropped below, but they still need to be recognized as headings
    "references", "bibliography", "literature cited", "references and notes", "acknowledgments",
    "acknowledgements", "acknowledgment", "acknowledgement", "author contributions", "competing interests",
    "conflicts of interest", "conflict of interest", "declaration of competing interest", "funding",
    "additional information", "author information", "notes", "abbreviations", "orcid",
}
REFERENCE_SECTIONS = {"references", "bibliography", "literature cited", "references and notes"}
BOILERPLATE_SECTIONS = {
    "acknowledgments", "acknowledgements", "acknowledgment", "acknowledgement", "author contributions",
    "competing interests", "conflicts of interest", "conflict of interest",
    "declaration of competing interest", "funding", "additional information", "author information",
    "notes", "orcid", "abbreviations",
}
NUMBERED_HEADING = re.compile(r"^(?:(?:\d{1,2}(?:\.\d{1,2}){0,3}\.?)|(?:[IVX]{1,5}\.)|(?:[A-H](?:\.\d{1,2})*\.?))\s+\S")
CAPTION = re.compile(r"^(?:fig(?:ure)?s?\.?|table|tab\.|scheme|algorithm|eq(?:uation)?\.?)\s*\(?[\dIVXS]", re.I)
ARXIV_STAMP = re.compile(r"^arxiv:\s*\d{4}\.\d{4,5}", re.I)
PAGE_NUMBER = re.compile(r"^(?:page\s*)?\d{1,4}(?:\s*(?:/|of)\s*\d{1,4})?$", re.I)
HYPHEN_BREAK = re.compile(r"(\w)-\s*\n\s*([a-z])")


@dataclass
class _Block:
    page: int
    y0: float
    y1: float
    page_height: float
    text: str
    size: float     # dominant font size
    bold: bool      # all text in the block is bold
    n_lines: int


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    # LaTeX accents (\AA, \"o) arrive as a separate spacing accent; NFKC turns that into
    # " " + combining mark placed *before* the letter. Move it after the letter and compose.
    text = re.sub(r" ?([̀-ͯ])([A-Za-z])", r"\2\1", text)
    text = unicodedata.normalize("NFC", text)
    text = text.replace("­", "").replace("�", "")  # soft hyphen, unmappable glyphs
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", " ", text)
    return text


def _heading_depth(text: str) -> int | None:
    """'2' -> 1, '2.1' -> 2, 'II.' -> 1, 'A.' / 'A.1' -> 1 / 2; None if unnumbered."""
    m = re.match(r"^(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s", text)
    if m:
        return m.group(1).count(".") + 1
    m = re.match(r"^(?:[IVX]{1,5}|[A-H])((?:\.\d{1,2})*)\.?\s", text)
    if m:
        return m.group(1).count(".") + 1
    return None


def _heading_key(text: str) -> str:
    """'2.1 Materials and Methods:' -> 'materials and methods'."""
    t = re.sub(r"^(?:\d{1,2}(?:\.\d{1,2})*\.?|[IVX]{1,5}\.|[A-H]\.)\s+", "", text.strip())
    return re.sub(r"[^a-z ]+", "", t.lower()).strip()


class PyMuPDFParser(Parser):
    name = "pymupdf"
    version = "2"

    def __init__(self, margin: float = 0.2, repeat_fraction: float = 0.3, min_chars: int = 500,
                 drop_boilerplate: bool = True, fragment_words: int = 6):
        self.margin = margin                    # header/footer candidates must lie in this top/bottom fraction
        self.fragment_words = fragment_words    # shorter blocks (equation pieces) are glued to the previous paragraph
        self.repeat_fraction = repeat_fraction  # a margin line on >= this fraction of pages is a running header
        self.min_chars = min_chars              # below this the PDF is treated as unparseable (scanned, empty)
        self.drop_boilerplate = drop_boilerplate

    # ------------------------------------------------------------------ public

    def parse(self, path: Path, paper_id: str) -> ParsedDocument:
        try:
            pdf = pymupdf.open(path)
        except Exception as exc:  # noqa: BLE001 - pymupdf raises several types for broken files
            raise ParseError(f"cannot open PDF: {exc}") from exc
        with pdf:
            n_pages = pdf.page_count
            blocks = self._extract_blocks(pdf)
        if sum(len(b.text) for b in blocks) < self.min_chars:
            raise ParseError("no extractable text (scanned or image-only PDF?)")
        warnings: list[str] = []
        blocks = self._drop_running_headers(blocks, n_pages)
        body_size = self._body_font_size(blocks)
        sections = self._build_sections(blocks, body_size, warnings)
        doc = ParsedDocument(paper_id=paper_id, source="pdf", parser=self.name, parser_version=self.version,
                             sections=[s for s in sections if s.paragraphs], n_pages=n_pages, warnings=warnings)
        if doc.n_words < 100:
            raise ParseError(f"only {doc.n_words} words left after cleaning")
        return doc

    # ------------------------------------------------------------------ extraction

    def _extract_blocks(self, pdf) -> list[_Block]:
        blocks: list[_Block] = []
        flags = pymupdf.TEXT_PRESERVE_WHITESPACE | pymupdf.TEXT_MEDIABOX_CLIP
        for page_no, page in enumerate(pdf, 1):
            height = page.rect.height or 1.0
            for b in page.get_text("dict", flags=flags)["blocks"]:
                if b.get("type") != 0:
                    continue  # image block
                lines, sizes, bold_chars, chars = [], Counter(), 0, 0
                for line in b["lines"]:
                    if abs(line["dir"][1]) > 0.1:
                        continue  # rotated text: arXiv side stamp, axis labels
                    text = "".join(s["text"] for s in line["spans"])
                    if not text.strip():
                        continue
                    lines.append(text)
                    for s in line["spans"]:
                        n = len(s["text"].strip())
                        chars += n
                        sizes[round(s["size"], 1)] += n
                        if s["flags"] & 16 or "bold" in s["font"].lower():
                            bold_chars += n
                if not lines or not chars:
                    continue
                text = _normalize("\n".join(lines))
                text = HYPHEN_BREAK.sub(r"\1\2", text)
                text = re.sub(r"\s*\n\s*", " ", text)
                text = re.sub(r"[ \t]{2,}", " ", text).strip()
                if not text:
                    continue
                blocks.append(_Block(page=page_no, y0=b["bbox"][1], y1=b["bbox"][3], page_height=height,
                                     text=text, size=sizes.most_common(1)[0][0],
                                     bold=bold_chars >= 0.9 * chars, n_lines=len(lines)))
        return blocks

    def _edge_blocks(self, blocks: list[_Block]) -> set[int]:
        """Indices of header/footer candidates: the top 2 and bottom 2 blocks of each page,
        if they lie within the margin zone. Adapts to any page layout."""
        by_page: dict[int, list[int]] = {}
        for i, b in enumerate(blocks):
            by_page.setdefault(b.page, []).append(i)
        edge = set()
        for idx in by_page.values():
            top = sorted(idx, key=lambda i: blocks[i].y0)[:2]
            bottom = sorted(idx, key=lambda i: -blocks[i].y1)[:2]
            edge |= {i for i in top if blocks[i].y1 <= blocks[i].page_height * self.margin}
            edge |= {i for i in bottom if blocks[i].y0 >= blocks[i].page_height * (1 - self.margin)}
        return edge

    def _drop_running_headers(self, blocks: list[_Block], n_pages: int) -> list[_Block]:
        def key(b: _Block) -> str:
            return re.sub(r"\d+", "#", b.text.lower())

        edge = self._edge_blocks(blocks)
        pages_with = Counter(k for k, _ in {(key(blocks[i]), blocks[i].page) for i in edge})
        threshold = max(2, self.repeat_fraction * n_pages)
        kept = []
        for i, b in enumerate(blocks):
            if ARXIV_STAMP.match(b.text):
                continue
            if i in edge and (PAGE_NUMBER.match(b.text) or (n_pages >= 2 and pages_with[key(b)] >= threshold)):
                continue
            kept.append(b)
        return kept

    @staticmethod
    def _body_font_size(blocks: list[_Block]) -> float:
        weighted = Counter()
        for b in blocks:
            weighted[b.size] += len(b.text)
        return weighted.most_common(1)[0][0] if weighted else 10.0

    # ------------------------------------------------------------------ structure

    def _is_heading(self, b: _Block, body_size: float) -> bool:
        text = b.text
        if b.n_lines > 2 or len(text) > 120 or len(text.split()) > 14:
            return False
        if CAPTION.match(text) or text.endswith((",", ";")) or PAGE_NUMBER.match(text):
            return False
        key = _heading_key(text)
        if key in KNOWN_SECTIONS and len(text) < 60:
            return True
        if not re.search(r"[A-Za-z]{3}", text):
            return False  # stray equation fragment or number
        styled = b.size >= body_size * 1.12 or b.bold
        if NUMBERED_HEADING.match(text):
            if styled:
                return True
            # unstyled "2.1 Training data" is a heading; "1. Behler, J. & Parrinello, M." (a reference) is not
            return len(text.split()) <= 8 and not re.search(r"[,&]|\.$", text)
        return styled and not text.endswith(".") and text[:1].isupper()

    def _build_sections(self, blocks: list[_Block], body_size: float, warnings: list[str]) -> list[Section]:
        sections = [Section("Front matter")]
        path: list[tuple[int, str]] = []  # (depth, heading) of enclosing numbered headings
        mode = "keep"  # keep | references | boilerplate
        saw_references = False
        for b in blocks:
            if self._is_heading(b, body_size):
                key = _heading_key(b.text)
                styled = b.size >= body_size * 1.12 or b.bold
                if mode == "references" and key not in KNOWN_SECTIONS and not styled:
                    continue  # still inside the reference list
                if key in REFERENCE_SECTIONS:
                    mode, saw_references = "references", True
                    continue
                if self.drop_boilerplate and key in BOILERPLATE_SECTIONS:
                    mode = "boilerplate"
                    continue
                mode = "keep"
                # "2.1 Training data" under "2 Methods" becomes "2 Methods > 2.1 Training data"
                depth = _heading_depth(b.text)
                if depth is None:
                    path = [(1, b.text)]
                else:
                    path = [(d, t) for d, t in path if d < depth] + [(depth, b.text)]
                sections.append(Section(" > ".join(t for _, t in path)))
                continue
            if mode != "keep":
                continue
            current = sections[-1]
            last = current.paragraphs[-1] if current.paragraphs else None
            if last and (len(b.text.split()) < self.fragment_words
                         or (not re.search(r"[.!?:)\]]\s*$", last.text) and b.text[:1].islower())):
                # equation fragments, and paragraphs broken across a column or page boundary
                last.text += " " + b.text
            else:
                current.paragraphs.append(Paragraph(b.text, b.page))
        if not saw_references:
            warnings.append("no reference section found; reference entries may be mixed into the text")
        if len(sections) <= 2:
            warnings.append("few section headings detected; section labels may be unreliable")
        return sections
