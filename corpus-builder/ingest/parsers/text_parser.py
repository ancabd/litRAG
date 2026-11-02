"""Parser for uploaded documents that are not PDFs: plain text, Markdown, HTML and Word (.docx).

Sections come from the document's own headings: Markdown `#` lines, HTML <h1>-<h4>, Word's
Title/Heading styles. Text before the first heading goes into a section named after the
document's title. Paragraphs are blocks separated by blank lines (text, Markdown) or the
document's own paragraphs (HTML, Word). No pages, so citations point to sections.

Only the standard library is used: .docx is a zip of XML, read directly.
"""
from __future__ import annotations

import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

from ..documents import Paragraph, ParsedDocument, ParseError, Section
from .base import Parser

TEXT_SUFFIXES = (".txt", ".text", ".md", ".markdown", ".rst")
HTML_SUFFIXES = (".html", ".htm")
DOCX_SUFFIXES = (".docx",)
SUFFIXES = TEXT_SUFFIXES + HTML_SUFFIXES + DOCX_SUFFIXES

MD_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
MD_SETEXT = re.compile(r"^\s{0,3}(=+|-+)\s*$")
MD_NOISE = [(re.compile(r"!\[([^\]]*)\]\([^)]*\)"), r"\1"),       # images -> alt text
            (re.compile(r"\[([^\]]+)\]\([^)]*\)"), r"\1"),        # links -> link text
            (re.compile(r"(\*\*|__)(.+?)\1"), r"\2"),             # bold
            (re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)"), r"\1"),  # italics
            (re.compile(r"`([^`]+)`"), r"\1")]                    # inline code
FENCE = re.compile(r"^\s*(```|~~~)")


def _clean(text: str) -> str:
    return " ".join(text.split())


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


# ------------------------------------------------------------------ format readers
# Each returns blocks in reading order: ("h", level, text) or ("p", 0, text).

def _markdown_blocks(text: str, markdown: bool) -> list[tuple[str, int, str]]:
    blocks: list[tuple[str, int, str]] = []
    para: list[str] = []
    in_fence = False

    def flush():
        if para:
            t = _clean(" ".join(para))
            if markdown:
                for pat, rep in MD_NOISE:
                    t = pat.sub(rep, t)
            if t:
                blocks.append(("p", 0, t))
            para.clear()

    for line in text.splitlines():
        if markdown and FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            para.append(line)
            continue
        if markdown:
            m = MD_HEADING.match(line)
            if m:
                flush()
                blocks.append(("h", len(m.group(1)), _clean(m.group(2))))
                continue
            if MD_SETEXT.match(line) and len(para) == 1:  # "Title\n=====" style heading
                blocks.append(("h", 1 if line.strip()[0] == "=" else 2, _clean(para[0])))
                para.clear()
                continue
            if re.match(r"^\s*([-*+]|\d+[.)])\s+", line):   # list item: its own paragraph
                flush()
                para.append(re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", line))
                continue
        if not line.strip():
            flush()
        else:
            para.append(line)
    flush()
    return blocks


class _HTMLBlocks(HTMLParser):
    BLOCK = {"p", "div", "li", "td", "th", "pre", "blockquote", "dd", "dt", "section", "article",
             "tr", "br", "figcaption", "caption"}
    SKIP = {"script", "style", "nav", "header", "footer", "noscript", "svg", "head", "form", "button"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, int, str]] = []
        self.title: str | None = None
        self._buf: list[str] = []
        self._skip = 0
        self._heading: int | None = None
        self._in_title = False

    def _flush(self):
        t = _clean("".join(self._buf))
        self._buf = []
        if t:
            self.blocks.append(("h", self._heading, t) if self._heading else ("p", 0, t))

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag in self.SKIP:
            self._skip += 1
        elif re.fullmatch(r"h[1-6]", tag):
            self._flush()
            self._heading = int(tag[1])
        elif tag in self.BLOCK:
            self._flush()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self.SKIP:
            self._skip = max(0, self._skip - 1)
        elif re.fullmatch(r"h[1-6]", tag):
            self._flush()
            self._heading = None
        elif tag in self.BLOCK:
            self._flush()

    def handle_data(self, data):
        if self._in_title:
            self.title = _clean((self.title or "") + " " + data) or None
        elif not self._skip:
            self._buf.append(data)

    def close(self):
        super().close()
        self._flush()


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _docx_blocks(path: Path) -> tuple[list[tuple[str, int, str]], str | None]:
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml")
            styles = z.read("word/styles.xml") if "word/styles.xml" in z.namelist() else None
    except (zipfile.BadZipFile, KeyError) as exc:
        raise ParseError(f"not a readable .docx file ({exc})")
    names: dict[str, str] = {}  # style id -> style name ("Heading1" -> "heading 1")
    if styles:
        for st in ElementTree.fromstring(styles).iter(W + "style"):
            name = st.find(W + "name")
            if name is not None:
                names[st.get(W + "styleId") or ""] = (name.get(W + "val") or "").lower()
    blocks, title = [], None
    for p in ElementTree.fromstring(xml).iter(W + "p"):
        text = _clean("".join(t.text or "" for t in p.iter(W + "t")))
        if not text:
            continue
        style = p.find(f"{W}pPr/{W}pStyle")
        sid = style.get(W + "val") if style is not None else ""
        name = names.get(sid, sid.lower())
        m = re.match(r"heading\s*(\d)", name)
        if name == "title":
            title = title or text
            blocks.append(("h", 1, text))
        elif m:
            blocks.append(("h", int(m.group(1)), text))
        else:
            blocks.append(("p", 0, text))
    return blocks, title


# ------------------------------------------------------------------ parser

def read_blocks(path: Path) -> tuple[list[tuple[str, int, str]], str | None]:
    """(blocks, title or None) for any supported non-PDF file."""
    suffix = path.suffix.lower()
    if suffix in DOCX_SUFFIXES:
        return _docx_blocks(path)
    text = _read_text(path)
    if suffix in HTML_SUFFIXES:
        h = _HTMLBlocks()
        h.feed(text)
        h.close()
        first_h1 = next((t for kind, lvl, t in h.blocks if kind == "h" and lvl == 1), None)
        return h.blocks, h.title or first_h1
    blocks = _markdown_blocks(text, markdown=suffix in (".md", ".markdown"))
    first_h1 = next((t for kind, lvl, t in blocks if kind == "h" and lvl == 1), None)
    return blocks, first_h1


def guess_title(path: Path, filename: str | None = None) -> str:
    """A title for an uploaded file: its own title or first top-level heading, else the file name."""
    title = None
    try:
        if path.suffix.lower() == ".pdf":
            import pymupdf
            with pymupdf.open(path) as pdf:
                title = _clean((pdf.metadata or {}).get("title") or "") or None
        else:
            title = read_blocks(path)[1]
    except Exception:  # noqa: BLE001 - a title is a nicety; parsing errors surface at parse time
        title = None
    if title and len(title) <= 200:
        return title
    stem = Path(filename or path.name).stem
    return _clean(re.sub(r"[_\-]+", " ", stem)) or stem


class TextParser(Parser):
    name = "text"
    version = "1"
    suffixes = SUFFIXES

    def parse(self, path: Path, paper_id: str) -> ParsedDocument:
        if path.suffix.lower() not in SUFFIXES:
            raise ParseError(f"unsupported file type {path.suffix!r}")
        blocks, title = read_blocks(path)
        sections: list[Section] = []
        current = Section(title or "Text")
        for kind, _level, text in blocks:
            if kind == "h":
                if current.paragraphs:
                    sections.append(current)
                current = Section(text)
            else:
                current.paragraphs.append(Paragraph(text))
        if current.paragraphs:
            sections.append(current)
        doc = ParsedDocument(paper_id=paper_id, source="document", parser=self.name,
                             parser_version=self.version, sections=sections)
        if doc.n_words == 0:
            raise ParseError("no text found in the file")
        return doc
