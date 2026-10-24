#!/usr/bin/env python3
"""Parse and chunk the corpus.

  run      parse all PDFs (cached), chunk PDFs + abstracts, write chunks.jsonl
  inspect  parse one PDF and print the result, to check parser quality
  parsers  list available parsers

Examples:
  python parse_corpus.py run
  python parse_corpus.py run --chunk-size 300 --overlap 50      # re-chunks without re-parsing
  python parse_corpus.py run --parser docling                   # once a docling parser is registered
  python parse_corpus.py inspect ../data/corpus/pdfs/W2042.pdf > W2042.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import paths
from ingest.chunking import ChunkConfig, chunk_document
from ingest.parsers import available, get_parser
from ingest.pipeline import run


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="parse and chunk the whole corpus")
    r.add_argument("--corpus", type=Path, default=paths.CORPUS, help=f"corpus folder (default: {paths.CORPUS})")
    r.add_argument("--out", type=Path, default=paths.CHUNKS, help=f"output root (default: {paths.CHUNKS})")
    r.add_argument("--parser", default="pymupdf", choices=available())
    r.add_argument("--chunk-size", type=int, default=400, help="target words per chunk (default: 400)")
    r.add_argument("--overlap", type=int, default=60, help="overlap in words (default: 60)")
    r.add_argument("--min-words", type=int, default=40, help="merge trailing chunks shorter than this")
    r.add_argument("--workers", type=int, default=None, help="parallel parser processes (default: CPUs - 1)")
    r.add_argument("--force", action="store_true", help="re-parse even if cached")
    r.add_argument("--only", default=None, help="comma-separated paper ids, for debugging")
    r.add_argument("--limit", type=int, default=None, help="process only the first N papers")
    r.add_argument("--name", default=None, help="output subfolder name (default: <parser>_w<size>_o<overlap>)")

    i = sub.add_parser("inspect", help="parse one PDF and print sections (and optionally chunks)")
    i.add_argument("pdf", type=Path)
    i.add_argument("--parser", default="pymupdf", choices=available())
    i.add_argument("--chunks", action="store_true", help="print chunks instead of the parsed document")
    i.add_argument("--chunk-size", type=int, default=400)
    i.add_argument("--overlap", type=int, default=60)

    sub.add_parser("parsers", help="list available parsers")
    args = ap.parse_args(argv)

    if args.cmd == "parsers":
        print("\n".join(available()))
    elif args.cmd == "inspect":
        doc = get_parser(args.parser).parse(args.pdf, args.pdf.stem)
        if args.chunks:
            for c in chunk_document(doc, ChunkConfig(args.chunk_size, args.overlap)):
                print(f"\n=== {c.chunk_id} | {c.section} | pages {c.page_start}-{c.page_end} | {c.n_words} words\n{c.text}")
        else:
            print(doc.to_markdown())
        print(f"\n{len(doc.sections)} sections, {doc.n_words} words, {doc.n_pages} pages", file=sys.stderr)
    else:
        cfg = ChunkConfig(args.chunk_size, args.overlap, args.min_words)
        only = set(args.only.split(",")) if args.only else None
        run(args.corpus, args.out, args.parser, cfg, workers=args.workers, force=args.force,
            only=only, limit=args.limit, run_name=args.name)


if __name__ == "__main__":
    main()
