#!/usr/bin/env python3
"""
corpus_builder: build a paper corpus from a few seed papers.

For each seed paper it collects
  - the seed itself,
  - every paper it cites (one hop backward), and
  - the most-cited (and optionally most recent) papers that cite it (one hop forward),
then tries to download a free full-text PDF for each one. Papers without a free
PDF keep their abstract, written to a Markdown file so they can still be indexed.

Metadata comes from OpenAlex (https://openalex.org). Since February 2026 OpenAlex
meters usage per day; a free API key gives ten times the keyless allowance.
Put it in the OPENALEX_API_KEY environment variable or pass --api-key.

Usage:
    python corpus_builder.py seeds.txt --out corpus
    python corpus_builder.py seeds.txt --out corpus --no-download   # dry run: metadata only
"""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from dataclasses import MISSING
from dataclasses import fields as dataclasses_fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlparse

import requests

import paths

OPENALEX = "https://api.openalex.org"
S2 = "https://api.semanticscholar.org/graph/v1/paper"
USER_AGENT = "corpus-builder/0.1 (literature corpus tool for a RAG project)"
SELECT = ",".join([
    "id", "doi", "title", "publication_year", "type", "primary_location",
    "best_oa_location", "locations", "open_access", "abstract_inverted_index",
    "referenced_works", "cited_by_count", "authorships",
])
BATCH = 50  # OpenAlex ids per OR-filter request

# Minimum seconds between requests to the same host (arXiv asks for ~3 s).
HOST_INTERVALS = {
    "api.openalex.org": 0.15,
    "api.semanticscholar.org": 1.1,
    "arxiv.org": 3.0,
    "export.arxiv.org": 3.0,
}
DEFAULT_INTERVAL = 1.0


# --------------------------------------------------------------------------- helpers

def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def short_id(openalex_id: str) -> str:
    """'https://openalex.org/W123' -> 'W123'."""
    return openalex_id.rstrip("/").rsplit("/", 1)[-1]


def clean_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip()
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi, flags=re.I)
    return doi.lower()


def norm_title(title: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (title or "").lower())


def abstract_from_inverted(inv: dict | None) -> str | None:
    """OpenAlex stores abstracts as {word: [positions]}; rebuild the text."""
    if not inv:
        return None
    words = sorted((pos, word) for word, positions in inv.items() for pos in positions)
    return " ".join(word for _, word in words) or None


def parse_seed(line: str) -> tuple[str, str] | None:
    """Classify a seeds-file line as ('doi'|'openalex'|'title', value)."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    m = re.match(r"^(?:https?://openalex\.org/)?(W\d+)$", line, flags=re.I)
    if m:
        return ("openalex", m.group(1).upper())
    m = re.match(r"^arxiv:\s*(\S+)$", line, flags=re.I)
    if m:
        arxiv_id = re.sub(r"v\d+$", "", m.group(1))
        return ("doi", f"10.48550/arxiv.{arxiv_id}".lower())
    if re.match(r"^(https?://(dx\.)?doi\.org/|doi:)?10\.\d{4,9}/\S+$", line, flags=re.I):
        return ("doi", clean_doi(line))
    return ("title", line)


def arxiv_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([^\s?#]+?)(?:v\d+)?(?:\.pdf)?$", url, flags=re.I)
    return m.group(1) if m else None


def pdf_candidates(work: dict) -> list[str]:
    """Ordered list of URLs that might serve a free PDF. arXiv first: it is the most reliable."""
    locations = [work.get("best_oa_location"), work.get("primary_location"), *(work.get("locations") or [])]
    locations = [loc for loc in locations if loc]
    arxiv, other = [], []
    doi = clean_doi(work.get("doi")) or ""
    if doi.startswith("10.48550/arxiv."):
        arxiv.append(f"https://arxiv.org/pdf/{doi.split('arxiv.', 1)[1]}")
    for loc in locations:
        for key in ("landing_page_url", "pdf_url"):
            aid = arxiv_id_from_url(loc.get(key))
            if aid:
                arxiv.append(f"https://arxiv.org/pdf/{aid}")
        if loc.get("pdf_url"):
            other.append(loc["pdf_url"])
    oa_url = (work.get("open_access") or {}).get("oa_url")
    if oa_url:
        other.append(oa_url)
    seen, ordered = set(), []
    for url in arxiv + other:
        if url not in seen:
            seen.add(url)
            ordered.append(url)
    return ordered


def format_authors(work: dict, limit: int = 3) -> str:
    names = [a.get("author", {}).get("display_name") for a in work.get("authorships") or []]
    names = [n for n in names if n]
    if len(names) > limit:
        return ", ".join(names[:limit]) + " et al."
    return ", ".join(names)


class Throttle:
    """Keeps a minimum interval between requests to the same host."""

    def __init__(self, intervals: dict[str, float] | None = None, default: float = DEFAULT_INTERVAL,
                 sleep: Callable[[float], None] = time.sleep, clock: Callable[[], float] = time.monotonic):
        self.intervals = HOST_INTERVALS if intervals is None else intervals
        self.default = default
        self.sleep, self.clock = sleep, clock
        self.last: dict[str, float] = {}

    def wait(self, url: str) -> None:
        host = urlparse(url).netloc.lower()
        interval = self.intervals.get(host, self.default)
        now = self.clock()
        if host in self.last and now - self.last[host] < interval:
            self.sleep(interval - (now - self.last[host]))
        self.last[host] = self.clock()


# --------------------------------------------------------------------------- API clients

class ApiClient:
    """GET with throttling, retries on 429/5xx, and an on-disk JSON cache."""

    def __init__(self, session, throttle: Throttle, cache_dir: Path | None,
                 max_retries: int = 5, sleep: Callable[[float], None] = time.sleep):
        self.session, self.throttle, self.cache_dir = session, throttle, cache_dir
        self.max_retries, self.sleep = max_retries, sleep
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, url: str, params: dict, body=None) -> Path | None:
        if not self.cache_dir:
            return None
        public = {k: v for k, v in sorted(params.items()) if k != "api_key"}
        key = hashlib.sha1(json.dumps([url, public, body]).encode()).hexdigest()
        return self.cache_dir / f"{key}.json"

    def get_json(self, url: str, params: dict | None = None, secret: dict | None = None,
                 body=None, headers: dict | None = None, first_delay: float = 2.0):
        """GET, or POST when `body` is given. `secret` params and `headers` are never cached."""
        params = params or {}
        cache = self._cache_path(url, params, body)
        if cache and cache.exists():
            return json.loads(cache.read_text())
        delay = first_delay
        for attempt in range(self.max_retries):
            self.throttle.wait(url)
            if body is None:
                r = self.session.get(url, params={**params, **(secret or {})}, timeout=30)
            else:
                r = self.session.post(url, params={**params, **(secret or {})}, json=body,
                                      headers=headers or {}, timeout=60)
            if r.status_code == 404:
                return None
            if r.status_code == 429 or r.status_code >= 500:
                retry_after = r.headers.get("Retry-After")
                wait = float(retry_after) if retry_after and retry_after.isdigit() else delay
                log(f"    {r.status_code} from {urlparse(url).netloc}, retrying in {wait:.0f}s")
                self.sleep(wait)
                delay = min(delay * 2, 60)
                continue
            if r.status_code in (401, 403) and "openalex" in url:
                raise SystemExit(f"OpenAlex refused the request ({r.status_code}). "
                                 "Check your API key or your daily usage allowance.")
            r.raise_for_status()
            data = r.json()
            if cache:
                cache.write_text(json.dumps(data))
            return data
        raise RuntimeError(f"Gave up on {url} after {self.max_retries} attempts")


class OpenAlex:
    def __init__(self, client: ApiClient, api_key: str | None):
        self.client = client
        self.secret = {"api_key": api_key} if api_key else {}

    def _get(self, path: str, params: dict | None = None):
        return self.client.get_json(OPENALEX + path, params, self.secret)

    def by_doi(self, doi: str):
        return self._get(f"/works/doi:{doi}", {"select": SELECT})

    def by_id(self, wid: str):
        return self._get(f"/works/{wid}", {"select": SELECT})

    def by_title(self, title: str) -> tuple[dict | None, float]:
        data = self._get("/works", {"search": title, "per_page": 5, "select": SELECT}) or {}
        best, score = None, 0.0
        for work in data.get("results", []):
            s = difflib.SequenceMatcher(None, norm_title(title), norm_title(work.get("title"))).ratio()
            if s > score:
                best, score = work, s
        return best, score

    def many(self, wids: list[str]) -> list[dict]:
        out = []
        for i in range(0, len(wids), BATCH):
            chunk = wids[i:i + BATCH]
            data = self._get("/works", {"filter": "openalex_id:" + "|".join(chunk),
                                        "per_page": BATCH, "select": SELECT}) or {}
            out.extend(data.get("results", []))
        return out

    def citing(self, wid: str, limit: int, sort: str) -> list[dict]:
        out, page = [], 1
        while len(out) < limit:
            per_page = min(200, limit - len(out))
            data = self._get("/works", {"filter": f"cites:{wid}", "sort": sort, "per_page": per_page,
                                        "page": page, "select": SELECT}) or {}
            results = data.get("results", [])
            out.extend(results)
            if len(results) < per_page:
                break
            page += 1
        return out[:limit]


S2_BATCH = 500  # max ids per Semantic Scholar batch request


def s2_abstracts(client: ApiClient, dois: list[str], api_key: str | None = None) -> dict[str, str]:
    """Fallback abstracts from Semantic Scholar, up to 500 papers per request.

    Keyless use shares one rate-limited pool, so a handful of batch requests with
    patient backoff works far better than one request per paper.
    """
    headers = {"x-api-key": api_key} if api_key else {}
    found: dict[str, str] = {}
    for i in range(0, len(dois), S2_BATCH):
        chunk = dois[i:i + S2_BATCH]
        try:
            data = client.get_json(f"{S2}/batch", {"fields": "abstract"},
                                   body={"ids": [f"DOI:{d}" for d in chunk]},
                                   headers=headers, first_delay=5.0)
        except Exception as exc:  # noqa: BLE001 - missing abstracts should never stop the run
            log(f"    Semantic Scholar unavailable ({exc}); continuing without fallback abstracts")
            return found
        for doi, item in zip(chunk, data or []):
            if item and item.get("abstract"):
                found[doi] = item["abstract"]
    return found


# --------------------------------------------------------------------------- corpus

@dataclass
class Paper:
    openalex_id: str
    title: str | None
    doi: str | None
    year: int | None
    type: str | None
    authors: str
    venue: str | None
    cited_by_count: int | None
    is_oa: bool
    roles: list[str] = field(default_factory=list)       # seed / reference / citing
    via_seeds: list[str] = field(default_factory=list)   # which seed(s) led here
    abstract: str | None = None
    abstract_source: str | None = None                   # openalex / semantic_scholar
    pdf_candidates: list[str] = field(default_factory=list)
    status: str = "pending"                              # pdf / abstract_only / metadata_only / not_downloaded
    pdf_path: str | None = None
    pdf_url: str | None = None
    note: str | None = None
    merged_ids: list[str] = field(default_factory=list)  # other OpenAlex records of the same paper
    added_manually: list[str] = field(default_factory=list)  # "pdf" and/or "abstract", from manual.jsonl

    @classmethod
    def from_work(cls, work: dict) -> "Paper":
        abstract = abstract_from_inverted(work.get("abstract_inverted_index"))
        source = ((work.get("primary_location") or {}).get("source") or {}).get("display_name")
        return cls(
            openalex_id=short_id(work["id"]),
            title=work.get("title"),
            doi=clean_doi(work.get("doi")),
            year=work.get("publication_year"),
            type=work.get("type"),
            authors=format_authors(work),
            venue=source,
            cited_by_count=work.get("cited_by_count"),
            is_oa=bool((work.get("open_access") or {}).get("is_oa")),
            abstract=abstract,
            abstract_source="openalex" if abstract else None,
            pdf_candidates=pdf_candidates(work),
        )


class Corpus:
    def __init__(self):
        self.papers: dict[str, Paper] = {}
        self.by_title: dict[str, str] = {}

    def add(self, work: dict, role: str, seed: str) -> Paper:
        new = Paper.from_work(work)
        key = new.openalex_id
        title_key = norm_title(new.title)
        # The same paper often exists twice in OpenAlex (arXiv preprint + journal version).
        if key not in self.papers and len(title_key) > 25 and title_key in self.by_title:
            key = self.by_title[title_key]
            existing = self.papers[key]
            if new.openalex_id not in existing.merged_ids:
                existing.merged_ids.append(new.openalex_id)
            _merge_versions(existing, new)
        elif key not in self.papers:
            self.papers[key] = new
            if len(title_key) > 25:
                self.by_title[title_key] = key
        paper = self.papers[key]
        if role not in paper.roles:
            paper.roles.append(role)
        if seed not in paper.via_seeds:
            paper.via_seeds.append(seed)
        return paper


def _merge_versions(keep: Paper, other: Paper) -> None:
    """Fold a duplicate record into the kept one, preferring the published (non-arXiv) DOI."""
    if other.doi and (not keep.doi or keep.doi.startswith("10.48550/")) and not other.doi.startswith("10.48550/"):
        keep.doi, keep.venue, keep.year = other.doi, other.venue or keep.venue, other.year or keep.year
    if not keep.abstract and other.abstract:
        keep.abstract, keep.abstract_source = other.abstract, other.abstract_source
    keep.cited_by_count = max(keep.cited_by_count or 0, other.cited_by_count or 0)
    keep.is_oa = keep.is_oa or other.is_oa
    for url in other.pdf_candidates:
        if url not in keep.pdf_candidates:
            # arXiv links stay at the front
            keep.pdf_candidates.insert(0 if "arxiv.org" in url else len(keep.pdf_candidates), url)


def resolve_seed(oa: OpenAlex, kind: str, value: str, min_title_score: float) -> dict | None:
    if kind == "doi":
        return oa.by_doi(value)
    if kind == "openalex":
        return oa.by_id(value)
    work, score = oa.by_title(value)
    if work is None or score < min_title_score:
        log(f"  ! no confident title match for {value!r} (best score {score:.2f}); add its DOI instead")
        return None
    if score < 0.95:
        log(f"  ? title matched with score {score:.2f}: {work.get('title')!r} - check this is the right paper")
    return work


def download_pdf(session, throttle: Throttle, urls: Iterable[str], dest: Path) -> tuple[str | None, str | None]:
    """Try each URL; accept only responses that really are PDFs. Returns (url, error)."""
    last_error = "no free PDF link known"
    for url in urls:
        try:
            throttle.wait(url)
            r = session.get(url, timeout=60, stream=True, allow_redirects=True)
            if r.status_code != 200:
                last_error = f"HTTP {r.status_code} from {urlparse(url).netloc}"
                continue
            chunks = r.iter_content(chunk_size=65536)
            first = next(chunks, b"")
            if not first.startswith(b"%PDF"):
                last_error = f"{urlparse(url).netloc} returned a web page, not a PDF"
                continue
            tmp = dest.with_suffix(".part")
            with open(tmp, "wb") as fh:
                fh.write(first)
                for chunk in chunks:
                    fh.write(chunk)
            tmp.replace(dest)
            return url, None
        except requests.RequestException as exc:
            last_error = f"{type(exc).__name__} from {urlparse(url).netloc}"
    return None, last_error


def write_abstract_md(paper: Paper, path: Path) -> None:
    lines = [f"# {paper.title or 'Untitled'}", ""]
    meta = [
        ("Authors", paper.authors), ("Year", paper.year), ("Venue", paper.venue),
        ("DOI", f"https://doi.org/{paper.doi}" if paper.doi else None),
        ("OpenAlex", f"https://openalex.org/{paper.openalex_id}"),
        ("Full text", "not freely available; abstract only"),
    ]
    lines += [f"- **{k}:** {v}" for k, v in meta if v]
    lines += ["", "## Abstract", "", paper.abstract or "_No abstract available._", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


MANIFEST_CSV_FIELDS = ["openalex_id", "status", "title", "year", "authors", "venue", "doi", "cited_by_count",
                       "roles", "via_seeds", "is_oa", "abstract_source", "pdf_path", "pdf_url", "note"]


MANIFEST_CSV_FIELDS = MANIFEST_CSV_FIELDS + ["added_manually"]


def write_manifest(papers: list[Paper], out: Path) -> None:
    write_manifest_rows([asdict(p) for p in papers], out)


def write_manifest_rows(rows: list[dict], out: Path) -> None:
    """Write manifest.jsonl and manifest.csv atomically (temp file + rename), so a reader never sees half a file."""
    jsonl_tmp, csv_tmp = out / "manifest.jsonl.tmp", out / "manifest.csv.tmp"
    with open(jsonl_tmp, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(csv_tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({**row, **{k: ";".join(row.get(k) or []) for k in ("roles", "via_seeds", "added_manually")}})
    jsonl_tmp.replace(out / "manifest.jsonl")
    csv_tmp.replace(out / "manifest.csv")


def load_manifest_rows(out: Path) -> list[dict]:
    with open(out / "manifest.jsonl", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def paper_from_row(row: dict) -> Paper:
    """Manifest row -> Paper; tolerant of rows from older versions or edited by hand (missing fields -> None)."""
    names = {f.name for f in dataclasses_fields(Paper)}
    required = {f.name: None for f in dataclasses_fields(Paper)
                if f.default is MISSING and f.default_factory is MISSING}
    return Paper(**{**required, **{k: v for k, v in row.items() if k in names}})


# --------------------------------------------------------------------------- manual additions
#
# Papers whose full text or abstract you add by hand are recorded in <corpus>/manual.jsonl.
# The manifest is regenerated from OpenAlex on every run of this script; manual.jsonl is
# what makes manual additions survive that: build() re-applies it every time.

MANUAL_FILE = "manual.jsonl"
MAX_PDF_BYTES = 200 * 1024 * 1024


class ManualEditError(ValueError):
    pass


def load_manual(out: Path) -> dict[str, dict]:
    path = out / MANUAL_FILE
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]
    return {r["openalex_id"]: r for r in records}


def _save_manual(out: Path, records: dict[str, dict]) -> None:
    tmp = out / (MANUAL_FILE + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in sorted(records.values(), key=lambda r: r["openalex_id"]):
            if r.get("pdf") or r.get("abstract"):
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(out / MANUAL_FILE)


def _refresh_row(row: dict, out: Path, manual: dict | None) -> dict:
    """Recompute a manifest row's status and files from what is on disk + the manual record."""
    pid = row["openalex_id"]
    pdf = out / "pdfs" / f"{pid}.pdf"
    md = out / "abstracts" / f"{pid}.md"
    added = []
    if manual and manual.get("abstract"):
        row["abstract"], row["abstract_source"] = manual["abstract"], "manual"
        added.append("abstract")
    elif row.get("abstract_source") == "manual":  # manual abstract was removed (it only ever fills a gap)
        row["abstract"], row["abstract_source"] = None, None
    if pdf.exists() and pdf.read_bytes()[:4] == b"%PDF":
        row["status"], row["pdf_path"] = "pdf", str(pdf.relative_to(out))
        if manual and manual.get("pdf"):
            added.append("pdf")
            row["note"], row["pdf_url"] = "added manually", None
        md.unlink(missing_ok=True)
    else:
        row["pdf_path"] = None
        if row.get("status") != "not_downloaded":
            row["status"] = "abstract_only" if row.get("abstract") else "metadata_only"
        if row.get("note") == "added manually":
            row["note"] = "manually added PDF removed"
        md.parent.mkdir(exist_ok=True)
        write_abstract_md(paper_from_row(row), md)
    row["added_manually"] = added
    return row


def _edit_paper(out: Path, paper_id: str, change_manual) -> dict:
    out = Path(out)
    rows = load_manifest_rows(out)
    row = next((r for r in rows if r["openalex_id"] == paper_id), None)
    if row is None:
        raise ManualEditError(f"No paper {paper_id} in {out / 'manifest.jsonl'}")
    manual = load_manual(out)
    record = manual.setdefault(paper_id, {"openalex_id": paper_id})
    change_manual(row, record)
    record["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _save_manual(out, manual)
    _refresh_row(row, out, record)
    write_manifest_rows(rows, out)
    return row


def add_manual_pdf(out: Path, paper_id: str, data: bytes) -> dict:
    """Add a PDF you obtained yourself (e.g. through your library) for a paper without free full text."""
    if not data.startswith(b"%PDF"):
        raise ManualEditError("That file isn't a PDF (it doesn't start with %PDF).")
    if len(data) > MAX_PDF_BYTES:
        raise ManualEditError(f"PDF is larger than {MAX_PDF_BYTES // 2**20} MB.")

    def change(row, record):
        if row.get("status") == "pdf" and "pdf" not in (row.get("added_manually") or []):
            raise ManualEditError(f"{paper_id} already has a downloaded full text.")
        pdfs = Path(out) / "pdfs"
        pdfs.mkdir(exist_ok=True)
        tmp = pdfs / f"{paper_id}.pdf.part"
        tmp.write_bytes(data)
        tmp.replace(pdfs / f"{paper_id}.pdf")
        record["pdf"] = True

    return _edit_paper(out, paper_id, change)


def remove_manual_pdf(out: Path, paper_id: str) -> dict:
    def change(row, record):
        if not record.get("pdf"):
            raise ManualEditError(f"{paper_id} has no manually added PDF to remove.")
        (Path(out) / "pdfs" / f"{paper_id}.pdf").unlink(missing_ok=True)
        record["pdf"] = False

    return _edit_paper(out, paper_id, change)


def set_manual_abstract(out: Path, paper_id: str, abstract: str | None) -> dict:
    """Set (or with None/empty, remove) a manually entered abstract."""
    text = " ".join((abstract or "").split())

    def change(row, record):
        if row.get("abstract") and row.get("abstract_source") != "manual":
            raise ManualEditError(f"{paper_id} already has an abstract from {row.get('abstract_source')}.")
        record["abstract"] = text or None

    return _edit_paper(out, paper_id, change)


# --------------------------------------------------------------------------- main build

def build(seed_lines: list[str], out: Path, *, api_key: str | None = None, max_citing: int = 50,
          recent_citing: int = 0, download: bool = True, use_s2: bool = True,
          min_title_score: float = 0.85, s2_api_key: str | None = None, session=None,
          throttle: Throttle | None = None, sleep: Callable[[float], None] = time.sleep) -> list[Paper]:
    out = out.resolve()  # relative paths depend on the terminal's folder; always report the full path
    out.mkdir(parents=True, exist_ok=True)
    log(f"Output folder: {out}")
    (out / "pdfs").mkdir(exist_ok=True)
    (out / "abstracts").mkdir(exist_ok=True)
    if session is None:
        session = requests.Session()
        session.headers["User-Agent"] = USER_AGENT
    throttle = throttle or Throttle()
    client = ApiClient(session, throttle, out / ".cache", sleep=sleep)
    oa = OpenAlex(client, api_key)
    corpus = Corpus()

    seeds = [s for s in (parse_seed(line) for line in seed_lines) if s]
    log(f"Resolving {len(seeds)} seed(s)...")
    for kind, value in seeds:
        work = resolve_seed(oa, kind, value, min_title_score)
        if not work:
            if kind != "title":
                log(f"  ! OpenAlex has no record for {value}")
            continue
        seed = corpus.add(work, "seed", short_id(work["id"]))
        sid = seed.openalex_id
        log(f"  * {sid}: {seed.title} ({seed.year})")

        refs = [short_id(r) for r in work.get("referenced_works") or []]
        for ref in oa.many(refs):
            corpus.add(ref, "reference", sid)
        log(f"      backward: {len(refs)} references")

        citing = oa.citing(sid, max_citing, "cited_by_count:desc") if max_citing else []
        if recent_citing:
            citing += oa.citing(sid, recent_citing, "publication_date:desc")
        for c in citing:
            corpus.add(c, "citing", sid)
        log(f"      forward:  {len(citing)} citing papers "
            f"({seed.cited_by_count or 0} cite it in total)")

    papers = sorted(corpus.papers.values(), key=lambda p: (-(p.cited_by_count or 0), p.openalex_id))
    missing = [p for p in papers if not p.abstract and p.doi]
    if use_s2 and missing:
        log(f"\n{len(missing)} papers have no abstract in OpenAlex; asking Semantic Scholar in one batch...")
        found = s2_abstracts(client, [p.doi for p in missing], s2_api_key)
        for p in missing:
            if p.doi in found:
                p.abstract, p.abstract_source = found[p.doi], "semantic_scholar"
        log(f"    found {len(found)} of {len(missing)}")

    manual = load_manual(out)
    if manual:
        log(f"Re-applying {len(manual)} manual addition(s) from {MANUAL_FILE}")
    for p in papers:
        m = manual.get(p.openalex_id) or {}
        if m.get("abstract") and not (p.abstract and p.abstract_source != "manual"):
            p.abstract, p.abstract_source = m["abstract"], "manual"
            p.added_manually.append("abstract")
    log(f"\n{len(papers)} unique papers. "
        + ("Fetching full texts..." if download else "Skipping downloads (--no-download)."))

    for i, p in enumerate(papers, 1):
        pdf = out / "pdfs" / f"{p.openalex_id}.pdf"
        stale_abstract = out / "abstracts" / f"{p.openalex_id}.md"
        if pdf.exists() and pdf.read_bytes()[:4] == b"%PDF":
            p.status, p.pdf_path = "pdf", str(pdf.relative_to(out))
            if (manual.get(p.openalex_id) or {}).get("pdf"):
                p.note, p.pdf_url = "added manually", None
                p.added_manually.append("pdf")
            else:
                p.note = "already downloaded"
            stale_abstract.unlink(missing_ok=True)
            continue
        if download:
            url, err = download_pdf(session, throttle, p.pdf_candidates, pdf)
            if url:
                p.status, p.pdf_path, p.pdf_url = "pdf", str(pdf.relative_to(out)), url
                stale_abstract.unlink(missing_ok=True)
                log(f"  [{i}/{len(papers)}] PDF   {p.title}")
                continue
            p.note = err
        if download:
            p.status = "abstract_only" if p.abstract else "metadata_only"
        else:
            p.status = "not_downloaded"
        write_abstract_md(p, out / "abstracts" / f"{p.openalex_id}.md")
        if download:
            log(f"  [{i}/{len(papers)}] {'ABSTR' if p.abstract else 'META '} {p.title}")

    write_manifest(papers, out)
    counts: dict[str, int] = {}
    for p in papers:
        counts[p.status] = counts.get(p.status, 0) + 1
    log("\nDone. " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    log(f"Manifest: {out / 'manifest.csv'} (and manifest.jsonl with abstracts)")
    return papers


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("seeds", type=Path, help="text file: one DOI, arXiv id (arxiv:XXXX), OpenAlex id or title per line")
    ap.add_argument("--out", type=Path, default=paths.CORPUS, help=f"output folder (default: {paths.CORPUS})")
    ap.add_argument("--api-key", default=os.environ.get("OPENALEX_API_KEY"),
                    help="OpenAlex API key (default: $OPENALEX_API_KEY)")
    ap.add_argument("--max-citing", type=int, default=50,
                    help="most-cited papers citing each seed to include (default: 50, 0 = none)")
    ap.add_argument("--recent-citing", type=int, default=0,
                    help="also include this many of the most recent papers citing each seed (default: 0)")
    ap.add_argument("--no-download", action="store_true", help="collect metadata only; download nothing")
    ap.add_argument("--no-s2", action="store_true", help="skip the Semantic Scholar abstract fallback")
    ap.add_argument("--s2-api-key", default=os.environ.get("S2_API_KEY"),
                    help="optional Semantic Scholar API key (default: $S2_API_KEY)")
    ap.add_argument("--min-title-score", type=float, default=0.85,
                    help="minimum similarity for title-based seed matching (0-1, default: 0.85)")
    args = ap.parse_args(argv)

    if not args.api_key:
        log("No OpenAlex API key set: running on the small keyless daily allowance.\n"
            "Get a free key at https://openalex.org/settings/api and set OPENALEX_API_KEY.\n")
    build(args.seeds.read_text(encoding="utf-8").splitlines(), args.out, api_key=args.api_key,
          max_citing=args.max_citing, recent_citing=args.recent_citing, download=not args.no_download,
          use_s2=not args.no_s2, min_title_score=args.min_title_score, s2_api_key=args.s2_api_key)


if __name__ == "__main__":
    main()
