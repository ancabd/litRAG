"""Ingestion: turn the corpus (PDFs + abstracts) into retrieval-ready chunks.

    documents.py  the parser-independent document model (what every parser returns)
    parsers/      one module per parser, behind a small registry
    chunking.py   splits parsed documents into chunks
    pipeline.py   runs it all over a corpus: caching, parallelism, output files
"""
