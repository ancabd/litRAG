"""Run parsing + chunking over a corpus built by corpus_builder.py.

Input:  <corpus>/manifest.jsonl, <corpus>/pdfs/*.pdf
Output: <out>/<parser>_<chunk config>/
          chunks.jsonl       one chunk per line (the input to indexing)
          papers.csv         per-paper report: source, pages, sections, chunks, warnings, errors
          run.json           config, versions, counts, timings (for reproducibility)
Cache:  <corpus>/parsed/<parser>@<version>/<paper_id>.json
          parsed documents, reused across runs; re-chunking never re-parses
"""
from __future__ import annotations

import csv
import json
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .chunking import ChunkConfig, chunk_document
from .documents import Paragraph, ParsedDocument, ParseError, Section
from .parsers import get_parser
from .parsers.text_parser import TextParser


try:
    from logsink import log  # shared with corpus_builder, so the web app can show progress
except ImportError:  # pragma: no cover - ingest used on its own
    def log(msg: str) -> None:
        print(msg, file=sys.stderr, flush=True)


# ------------------------------------------------------------------ worker side
# Each worker process builds its own parser once (parsers may hold heavy models).

_WORKER_PARSER = None


def _init_worker(parser_name: str, parser_options: dict) -> None:
    global _WORKER_PARSER
    _WORKER_PARSER = get_parser(parser_name, **parser_options)


def _parse_one(pdf_path: str, paper_id: str, cache_path: str) -> tuple[str, str | None, float]:
    """Parse one PDF into the cache. Returns (paper_id, error or None, seconds)."""
    t0 = time.perf_counter()
    try:
        doc = _WORKER_PARSER.parse(Path(pdf_path), paper_id)
        doc.save(Path(cache_path))
        return paper_id, None, time.perf_counter() - t0
    except ParseError as exc:
        return paper_id, str(exc), time.perf_counter() - t0
    except Exception as exc:  # noqa: BLE001 - one bad PDF must never kill the run
        return paper_id, f"{type(exc).__name__}: {exc}", time.perf_counter() - t0


# ------------------------------------------------------------------ main

@dataclass
class PaperReport:
    paper_id: str
    title: str | None
    status: str                 # manifest status
    source: str = "skipped"     # pdf / document / abstract / abstract_fallback / skipped
    n_pages: int | None = None
    n_sections: int = 0
    n_words: int = 0
    n_chunks: int = 0
    parse_seconds: float | None = None
    cached: bool = False
    error: str | None = None
    warnings: list[str] = field(default_factory=list)


def page_labels(pdf: Path) -> dict[int, str] | None:
    """{1-based page: printed page label}, only if the PDF defines labels that differ from 1, 2, 3, ...

    Books and theses often number their pages differently from the PDF (roman numerals for the front
    matter, then 1 on the tenth sheet). Citations should give the printed number.
    """
    try:
        import pymupdf
        with pymupdf.open(pdf) as doc:
            if not doc.get_page_labels():
                return None
            labels = {i + 1: page.get_label() for i, page in enumerate(doc)}
    except Exception:  # noqa: BLE001 - labels are a nicety
        return None
    if all(lbl == str(i) for i, lbl in labels.items()):
        return None
    return {i: lbl for i, lbl in labels.items() if lbl}


def abstract_document(paper_id: str, abstract: str, parser_tag: str = "abstract") -> ParsedDocument:
    return ParsedDocument(paper_id=paper_id, source="abstract", parser=parser_tag, parser_version="1",
                          sections=[Section("Abstract", [Paragraph(abstract.strip())])])


def load_manifest(corpus: Path) -> list[dict]:
    path = corpus / "manifest.jsonl"
    if not path.exists():
        raise SystemExit(f"No manifest at {path}. Run corpus_builder.py first, or pass --corpus.")
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def run(corpus: Path, out: Path, parser_name: str = "pymupdf", cfg: ChunkConfig = ChunkConfig(),
        workers: int | None = None, force: bool = False, only: set[str] | None = None,
        limit: int | None = None, parser_options: dict | None = None, run_name: str | None = None,
        progress=None) -> Path:
    """progress(done, total), if given, is called as files are parsed."""
    t_start = time.perf_counter()
    corpus = corpus.resolve()
    parser_options = parser_options or {}
    parser = get_parser(parser_name, **parser_options)  # validates the name early
    cache_dir = corpus / "parsed" / parser.cache_key
    cache_dir.mkdir(parents=True, exist_ok=True)
    text_parser = TextParser()
    text_cache = corpus / "parsed" / text_parser.cache_key
    run_dir = (out / (run_name or f"{parser.name}_{cfg.name}")).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    papers = load_manifest(corpus)
    if only:
        papers = [p for p in papers if p["openalex_id"] in only]
    if limit:
        papers = papers[:limit]
    reports = {p["openalex_id"]: PaperReport(p["openalex_id"], p.get("title"), p.get("status")) for p in papers}

    # 1. parse full texts that are not cached yet: PDFs with the chosen parser, other uploaded
    #    documents (text, Markdown, HTML, Word) with the text parser
    def source_file(p: dict) -> Path | None:
        rel = p.get("pdf_path") if p.get("status") == "pdf" else p.get("doc_path") if p.get("status") == "document" else None
        return corpus / rel if rel else None

    def cache_of(p: dict) -> Path:
        path = source_file(p)
        uses_text = path is not None and path.suffix.lower() != ".pdf"
        return (text_cache if uses_text else cache_dir) / f"{p['openalex_id']}.json"

    todo, text_todo = [], []
    for p in papers:
        path = source_file(p)
        if path is None:
            continue
        cache = cache_of(p)
        if not path.exists():
            reports[p["openalex_id"]].error = f"File missing: {path}"
            continue
        if cache.exists() and not force and cache.stat().st_mtime >= path.stat().st_mtime:
            reports[p["openalex_id"]].cached = True
            continue
        (todo if path.suffix.lower() == ".pdf" else text_todo).append((str(path), p["openalex_id"], str(cache)))

    n_full = sum(1 for p in papers if source_file(p) is not None)
    n_todo = len(todo) + len(text_todo)
    log(f"Corpus: {corpus}\nParser: {parser.cache_key}   chunks: {cfg}\n"
        f"{n_full} full texts ({n_full - n_todo} cached, {n_todo} to parse)")
    if progress:
        progress(0, n_todo)
    parsed = 0

    def record(done: int, pid: str, err: str | None, secs: float) -> None:
        nonlocal parsed
        parsed += 1
        reports[pid].parse_seconds = round(secs, 2)
        reports[pid].error = err
        if err:
            log(f"  [{parsed}/{n_todo}] FAILED {pid}: {err}")
        elif parsed % 10 == 0 or parsed == n_todo:
            log(f"  [{parsed}/{n_todo}] parsed")
        if progress:
            progress(parsed, n_todo)

    for path, pid, cache in text_todo:
        t0 = time.perf_counter()
        try:
            text_parser.parse(Path(path), pid).save(Path(cache))
            record(0, pid, None, time.perf_counter() - t0)
        except Exception as exc:  # noqa: BLE001
            record(0, pid, str(exc) if isinstance(exc, ParseError) else f"{type(exc).__name__}: {exc}",
                   time.perf_counter() - t0)

    if todo and (workers == 0 or len(todo) == 1):
        # in-process: no worker start-up cost, and safe to call from inside a web server
        _init_worker(parser_name, parser_options)
        for done, job in enumerate(todo, 1):
            record(done, *_parse_one(*job))
    elif todo:
        workers = workers or max(1, min(len(todo), (os.cpu_count() or 2) - 1))
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                                 initargs=(parser_name, parser_options)) as pool:
            futures = [pool.submit(_parse_one, *job) for job in todo]
            for done, fut in enumerate(as_completed(futures), 1):
                record(done, *fut.result())

    # 2. chunk everything, streaming to disk
    n_chunks = 0
    with open(run_dir / "chunks.jsonl", "w", encoding="utf-8") as fh:
        for p in papers:
            pid, rep = p["openalex_id"], reports[p["openalex_id"]]
            doc, source = None, None
            cache = cache_of(p)
            if source_file(p) is not None and cache.exists() and not rep.error:
                doc, source = ParsedDocument.load(cache), p["status"]
            elif p.get("abstract"):
                doc = abstract_document(pid, p["abstract"])
                source = "abstract_fallback" if p.get("status") == "pdf" else "abstract"
            if doc is None:
                continue  # metadata_only, or failed PDF without an abstract
            meta = {**{k: p.get(k) for k in ("title", "year", "authors", "doi", "venue")},
                    "source_override": source}
            chunks = chunk_document(doc, cfg, meta)
            path = source_file(p)
            labels = page_labels(path) if source in ("pdf", "document") and path and path.suffix.lower() == ".pdf" else None
            if labels:
                for c in chunks:
                    c.page_label_start = labels.get(c.page_start) if c.page_start else None
                    c.page_label_end = labels.get(c.page_end) if c.page_end else None
            for c in chunks:
                fh.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")
            n_chunks += len(chunks)
            rep.source, rep.n_pages, rep.n_sections = source, doc.n_pages, len(doc.sections)
            rep.n_words, rep.n_chunks, rep.warnings = doc.n_words, len(chunks), doc.warnings

    # 3. reports
    with open(run_dir / "papers.csv", "w", newline="", encoding="utf-8") as fh:
        fields = list(asdict(next(iter(reports.values()))).keys()) if reports else ["paper_id"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for rep in reports.values():
            row = asdict(rep)
            row["warnings"] = " | ".join(rep.warnings)
            w.writerow(row)

    by_source: dict[str, int] = {}
    for rep in reports.values():
        by_source[rep.source] = by_source.get(rep.source, 0) + 1
    failures = {r.paper_id: r.error for r in reports.values() if r.error}
    summary = {
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "corpus": str(corpus),
        "parser": parser.cache_key,
        "parser_options": parser_options,
        "chunking": asdict(cfg),
        "papers": len(papers),
        "papers_by_source": by_source,
        "chunks": n_chunks,
        "failures": failures,
        "seconds": round(time.perf_counter() - t_start, 1),
        "python": platform.python_version(),
    }
    (run_dir / "run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log(f"\nDone in {summary['seconds']}s: {n_chunks} chunks from "
        + ", ".join(f"{v} {k}" for k, v in sorted(by_source.items())))
    if failures:
        log(f"{len(failures)} file(s) failed to parse (abstract used where available); see papers.csv")
    log(f"Output: {run_dir}")
    return run_dir


def rebuild_runs(corpus: Path, chunks_root: Path, workers: int | None = 0, create_default: bool = False,
                 progress=None) -> list[dict]:
    """Re-chunk every existing run under chunks_root with that run's own parser and chunk settings.

    Used after the corpus changes (e.g. a manually added PDF). Parsed documents are cached,
    so only new or changed PDFs are actually parsed; the rest is re-chunking, which is fast.
    Returns one summary (run.json contents) per run.
    """
    results = []
    chunks_root = Path(chunks_root)
    run_dirs = sorted(d for d in chunks_root.iterdir() if (d / "chunks.jsonl").exists()) if chunks_root.exists() else []
    if not run_dirs and create_default:
        # a new corpus: make the standard run, so the corpus is searchable straight away
        out = run(corpus, chunks_root, "pymupdf", ChunkConfig(), workers=workers, progress=progress)
        return [{"run": out.name, **json.loads((out / "run.json").read_text(encoding="utf-8"))}]
    for run_dir in run_dirs:
        info_path = run_dir / "run.json"
        if not (run_dir / "chunks.jsonl").exists() or not info_path.exists():
            continue
        info = json.loads(info_path.read_text(encoding="utf-8"))
        parser_name = str(info.get("parser") or "pymupdf").split("@")[0]
        c = info.get("chunking") or {}
        cfg = ChunkConfig(c.get("size", 400), c.get("overlap", 60), c.get("min_words", 40))
        out = run(corpus, run_dir.parent, parser_name, cfg, workers=workers,
                  parser_options=info.get("parser_options") or {}, run_name=run_dir.name, progress=progress)
        results.append({"run": run_dir.name, **json.loads((out / "run.json").read_text(encoding="utf-8"))})
    return results


def paper_report(run_dir: Path, paper_id: str) -> dict | None:
    """One paper's row from a run's papers.csv (source, n_chunks, error, warnings)."""
    path = Path(run_dir) / "papers.csv"
    if not path.exists():
        return None
    with open(path, newline="", encoding="utf-8") as fh:
        return next((row for row in csv.DictReader(fh) if row["paper_id"] == paper_id), None)
