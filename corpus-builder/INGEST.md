# Parsing and chunking

Turns the corpus built by `corpus_builder.py` into `chunks.jsonl`, the input for indexing.

```bash
pip install -r requirements.txt
python parse_corpus.py run                    # writes chunks/pymupdf_w400_o60/
```

## What goes in

| Manifest status | What gets indexed |
|---|---|
| `pdf` | the parsed full text; if parsing fails, the abstract (`source: abstract_fallback`) |
| `abstract_only` | the abstract, as one chunk |
| `metadata_only` | nothing (logged as `skipped`) |

## Output

```
chunks/pymupdf_w400_o60/        one folder per parser + chunk config, so runs never overwrite each other
  chunks.jsonl                  one chunk per line
  papers.csv                    per paper: source, pages, sections, chunks, warnings, parse errors
  run.json                      config, parser version, counts, failures, timing
corpus/parsed/pymupdf@2/        cached parsed documents (one JSON per paper)
```

A chunk looks like this:

```json
{"chunk_id": "W2042#003", "paper_id": "W2042", "index": 3,
 "text": "The energy is a sum of atomic contributions, ...",
 "section": "2 Methods > 2.1 Equivariant features", "page_start": 1, "page_end": 2, "n_words": 196,
 "source": "pdf", "parser": "pymupdf@2",
 "title": "...", "year": 2022, "authors": "...", "doi": "...", "venue": "..."}
```

Every chunk carries its paper's metadata and page range, so the app can cite "Batzner et al. 2022, §2.1, p. 2" without any lookups.

## Common commands

```bash
# Look at what the parser makes of one paper (do this for ~5 papers before trusting it)
python parse_corpus.py inspect corpus/pdfs/W2042.pdf > W2042.md
python parse_corpus.py inspect corpus/pdfs/W2042.pdf --chunks      # see chunk boundaries

# Try another chunk size: reuses the parse cache, takes seconds
python parse_corpus.py run --chunk-size 250 --overlap 40

# Debug a few papers, or re-parse after changing the parser
python parse_corpus.py run --only W2042,W1987 --force
```

Sizes are in words (1 word is roughly 1.3 tokens). Chunks never cross section boundaries, and consecutive chunks overlap by whole sentences.

## What the PyMuPDF parser does

- Keeps the PDF's reading order, which handles two-column layouts
- Drops running headers, footers and page numbers: only blocks at the top or bottom of a page that repeat across pages or are bare numbers, so it adapts to any layout
- Drops the vertical arXiv stamp and other rotated text
- Detects headings from numbering, known section names, font size and bold, and builds paths like `2 Methods > 2.1 Training data`
- Removes the reference list, acknowledgements, author contributions and competing-interest statements, but keeps appendices and Methods that come *after* the references (Nature-style papers)
- Re-joins hyphenated line breaks, normalizes ligatures and LaTeX accents, and glues equation fragments back into their sentence

**Known limits:** equations come out linearized and some math glyphs are lost (a Σ may vanish); tables become loose text; figure contents are not extracted. If `inspect` shows this hurting papers you care about, that's the moment to add a layout-aware parser.

`papers.csv` flags likely problems: a `warnings` column (e.g. "few section headings detected") and an `error` column for PDFs that could not be parsed (scanned or corrupt; their abstract is used instead).

## Adding another parser

1. Create `ingest/parsers/<name>_parser.py`:

   ```python
   from pathlib import Path
   from ..documents import Paragraph, ParsedDocument, ParseError, Section
   from .base import Parser

   class DoclingParser(Parser):
       name = "docling"
       version = "1"            # bump when output changes; invalidates the cache

       def __init__(self):
           from docling.document_converter import DocumentConverter   # heavy import, done once per worker
           self.converter = DocumentConverter()

       def parse(self, path: Path, paper_id: str) -> ParsedDocument:
           ...                  # build Sections of Paragraphs; raise ParseError if there's no text
   ```

2. Register it in `ingest/parsers/__init__.py`:

   ```python
   "docling": "ingest.parsers.docling_parser:DoclingParser",
   ```

3. Run `python parse_corpus.py run --parser docling`. Output goes to `chunks/docling_w400_o60/`, next to the PyMuPDF run, so you can run the same eval on both and compare.

Nothing downstream changes: chunking, indexing and evaluation only ever see `ParsedDocument` and `chunks.jsonl`.

## Tests

```bash
python -m pytest -q
```

Parser tests use PDFs generated on the fly, plus a two-column LaTeX paper (`tests/fixtures/`) compiled when `pdflatex` is available.
