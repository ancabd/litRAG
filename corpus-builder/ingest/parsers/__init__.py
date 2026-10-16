"""Parser registry.

Parsers are registered by name and imported lazily, so a heavy optional parser
(Docling, GROBID, ...) costs nothing unless it is selected.

To add a parser:
  1. create ingest/parsers/<name>_parser.py with a subclass of Parser
  2. add one line to PARSERS below
  3. run:  python parse_corpus.py run --parser <name>
"""
from __future__ import annotations

import importlib

from .base import Parser

PARSERS: dict[str, str] = {
    "pymupdf": "ingest.parsers.pymupdf_parser:PyMuPDFParser",
    # "docling": "ingest.parsers.docling_parser:DoclingParser",
    # "grobid":  "ingest.parsers.grobid_parser:GrobidParser",
}


def available() -> list[str]:
    return sorted(PARSERS)


def get_parser(name: str, **options) -> Parser:
    if name not in PARSERS:
        raise ValueError(f"Unknown parser {name!r}. Available: {', '.join(available())}")
    module_name, cls_name = PARSERS[name].split(":")
    cls = getattr(importlib.import_module(module_name), cls_name)
    return cls(**options)


__all__ = ["Parser", "PARSERS", "available", "get_parser"]
