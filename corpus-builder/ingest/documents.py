"""Parser-independent document model.

Every parser returns a ParsedDocument; everything downstream (chunking, indexing)
only ever sees this structure. That is what makes parsers swappable.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Paragraph:
    text: str
    page: int | None = None  # 1-based page number, if the source has pages


@dataclass
class Section:
    title: str                 # e.g. "2 Methods"; "Front matter" for text before the first heading
    paragraphs: list[Paragraph] = field(default_factory=list)

    @property
    def n_words(self) -> int:
        return sum(len(p.text.split()) for p in self.paragraphs)


@dataclass
class ParsedDocument:
    paper_id: str
    source: str                # "pdf" or "abstract"
    parser: str                # parser name, e.g. "pymupdf"
    parser_version: str        # bump when the parser's output changes, to invalidate caches
    sections: list[Section] = field(default_factory=list)
    n_pages: int | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def n_words(self) -> int:
        return sum(s.n_words for s in self.sections)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ParsedDocument":
        sections = [Section(s["title"], [Paragraph(**p) for p in s["paragraphs"]]) for s in d["sections"]]
        return cls(**{**d, "sections": sections})

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.to_dict(), ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    @classmethod
    def load(cls, path: Path) -> "ParsedDocument":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def to_markdown(self) -> str:
        """Human-readable dump, for inspecting parser output."""
        out = [f"<!-- {self.paper_id} | parser={self.parser}@{self.parser_version} | "
               f"pages={self.n_pages} | words={self.n_words} -->"]
        for w in self.warnings:
            out.append(f"<!-- warning: {w} -->")
        for s in self.sections:
            out.append(f"\n## {s.title}\n")
            for p in s.paragraphs:
                out.append(f"[p{p.page}] {p.text}\n" if p.page else f"{p.text}\n")
        return "\n".join(out)


class ParseError(Exception):
    """Raised by a parser when a file yields no usable text (scanned PDF, corrupt file, ...)."""
