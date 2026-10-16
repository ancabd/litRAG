from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..documents import ParsedDocument


class Parser(ABC):
    """Turns one file into a ParsedDocument.

    Subclasses set `name` and `version`. Bump `version` whenever a change alters the
    output: cached results are keyed on (name, version), so old ones are ignored.
    Raise ingest.documents.ParseError when a file has no usable text.
    """

    name: str = "base"
    version: str = "0"
    suffixes: tuple[str, ...] = (".pdf",)

    @abstractmethod
    def parse(self, path: Path, paper_id: str) -> ParsedDocument:
        ...

    @property
    def cache_key(self) -> str:
        return f"{self.name}@{self.version}"
