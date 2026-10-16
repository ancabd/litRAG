"""Offline tests: a fake HTTP session stands in for OpenAlex, Semantic Scholar and PDF hosts."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import corpus_builder as cb  # noqa: E402

LONG = "a sufficiently long title so that the duplicate detection applies"


def work(wid, title, doi=None, refs=(), abstract=None, locations=(), cited=0, year=2020):
    inv = None
    if abstract:
        inv = {}
        for i, w in enumerate(abstract.split()):
            inv.setdefault(w, []).append(i)
    return {
        "id": f"https://openalex.org/{wid}", "title": title, "publication_year": year, "type": "article",
        "doi": f"https://doi.org/{doi}" if doi else None, "referenced_works": [f"https://openalex.org/{r}" for r in refs],
        "abstract_inverted_index": inv, "cited_by_count": cited, "locations": list(locations),
        "primary_location": {"source": {"display_name": "Some Journal"}},
        "best_oa_location": locations[0] if locations else None,
        "open_access": {"is_oa": bool(locations)},
        "authorships": [{"author": {"display_name": n}} for n in ("A. One", "B. Two", "C. Three", "D. Four")],
    }


W1 = work("W1", "Generalized neural-network representation of high-dimensional potential-energy surfaces",
          doi="10.1103/physrevlett.98.146401", refs=["W2", "W3"], abstract="seed abstract", cited=5000)
W2 = work("W2", "Paper two " + LONG, doi="10.1000/two", abstract="two abstract", cited=300,
          locations=[{"landing_page_url": "https://arxiv.org/abs/1234.5678v2", "pdf_url": None}])
W3 = work("W3", "Paywalled paper three " + LONG, doi="10.1000/three", cited=200,
          locations=[{"landing_page_url": "https://pub.example/3", "pdf_url": "https://pub.example/3.pdf"}])
W4 = work("W4", "Citing paper four " + LONG, doi="10.1000/four", abstract="four abstract", cited=100,
          locations=[{"landing_page_url": "https://oa.example/4", "pdf_url": "https://oa.example/4.pdf"}])
W5 = work("W5", "Paper Two: " + LONG, doi="10.48550/arxiv.1234.5678", cited=10)  # preprint duplicate of W2
W6 = work("W6", "E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials",
          doi="10.1038/s41467-022-29939-5", refs=["W3"], abstract="nequip", cited=900)
WORKS = {w["id"].rsplit("/", 1)[1]: w for w in (W1, W2, W3, W4, W5, W6)}


class Resp:
    def __init__(self, status=200, data=None, body=b"", headers=None):
        self.status_code, self._data, self.body, self.headers = status, data, body, headers or {}

    def json(self):
        return self._data

    def iter_content(self, chunk_size=65536):
        for i in range(0, len(self.body), chunk_size):
            yield self.body[i:i + chunk_size]

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class FakeSession:
    def __init__(self):
        self.calls = []
        self.fail_once_429 = set()

    def get(self, url, params=None, timeout=None, stream=False, allow_redirects=True):
        params = params or {}
        self.calls.append((url, dict(params)))
        if url in self.fail_once_429:
            self.fail_once_429.discard(url)
            return Resp(429, headers={"Retry-After": "1"})
        if url.startswith(cb.OPENALEX):
            return self._openalex(url[len(cb.OPENALEX):], params)
        if url == "https://arxiv.org/pdf/1234.5678":
            return Resp(200, body=b"%PDF-1.5 arxiv pdf")
        if url == "https://oa.example/4.pdf":
            return Resp(200, body=b"%PDF-1.4 four")
        if url == "https://pub.example/3.pdf":
            return Resp(200, body=b"<html>Please log in</html>")
        return Resp(404)

    def post(self, url, params=None, json=None, headers=None, timeout=None):
        self.calls.append((url, dict(params or {}), json))
        if self.s2_always_429:
            return Resp(429)
        if url == cb.S2 + "/batch":
            return Resp(200, [{"abstract": f"abstract from semantic scholar for {i}"} for i in json["ids"]])
        return Resp(404)

    s2_always_429 = False

    def _openalex(self, path, params):
        if path.startswith("/works/doi:"):
            doi = path.split("doi:", 1)[1]
            hit = [w for w in WORKS.values() if w["doi"] and w["doi"].endswith(doi)]
            return Resp(200, hit[0]) if hit else Resp(404)
        if path.startswith("/works/W"):
            wid = path.rsplit("/", 1)[1]
            return Resp(200, WORKS[wid]) if wid in WORKS else Resp(404)
        if path == "/works" and "search" in params:
            return Resp(200, {"results": [W1, W6]})
        f = params.get("filter", "")
        if f.startswith("openalex_id:"):
            ids = f.split(":", 1)[1].split("|")
            return Resp(200, {"results": [WORKS[i] for i in ids if i in WORKS]})
        if f.startswith("cites:"):
            target = f.split(":", 1)[1]
            res = {"W1": [W4, W5], "W6": [W4]}.get(target, [])
            return Resp(200, {"results": res[: params["per_page"]]})
        return Resp(404)


def no_throttle():
    return cb.Throttle(intervals={}, default=0, sleep=lambda s: None)


def run(tmp_path, seeds, session=None, **kw):
    session = session or FakeSession()
    papers = cb.build(seeds, tmp_path, api_key="KEY", session=session, throttle=no_throttle(),
                      sleep=lambda s: None, **kw)
    return {p.openalex_id: p for p in papers}, session


# --------------------------------------------------------------------------- unit tests

def test_parse_seed_variants():
    assert cb.parse_seed("# comment") is None
    assert cb.parse_seed("   ") is None
    assert cb.parse_seed("https://doi.org/10.1103/PhysRevLett.98.146401") == ("doi", "10.1103/physrevlett.98.146401")
    assert cb.parse_seed("10.1038/s41467-022-29939-5") == ("doi", "10.1038/s41467-022-29939-5")
    assert cb.parse_seed("arxiv:2101.03164v3") == ("doi", "10.48550/arxiv.2101.03164")
    assert cb.parse_seed("https://openalex.org/W2042") == ("openalex", "W2042")
    assert cb.parse_seed("The continuous evolution of biomolecular force fields") == (
        "title", "The continuous evolution of biomolecular force fields")


def test_abstract_reconstruction_orders_words():
    assert cb.abstract_from_inverted({"world": [1], "hello": [0], "again": [3], "hello,": [2]}) == "hello world hello, again"
    assert cb.abstract_from_inverted(None) is None


def test_pdf_candidates_put_arxiv_first():
    assert cb.pdf_candidates(W2) == ["https://arxiv.org/pdf/1234.5678"]
    assert cb.pdf_candidates(W5) == ["https://arxiv.org/pdf/1234.5678"]
    assert cb.pdf_candidates(W3) == ["https://pub.example/3.pdf"]


# --------------------------------------------------------------------------- end-to-end

def test_build_hops_downloads_and_abstracts(tmp_path):
    papers, session = run(tmp_path, ["10.1103/PhysRevLett.98.146401"])

    # seed + 2 references + 2 citing, where W5 is a preprint duplicate of W2
    assert set(papers) == {"W1", "W2", "W3", "W4"}
    assert papers["W2"].merged_ids == ["W5"]
    assert set(papers["W2"].roles) == {"reference", "citing"}
    assert papers["W2"].doi == "10.1000/two"  # published DOI kept over the arXiv one

    # arXiv PDF and publisher OA PDF downloaded; checked by magic bytes
    assert papers["W2"].status == "pdf"
    assert (tmp_path / "pdfs" / "W2.pdf").read_bytes().startswith(b"%PDF")
    assert papers["W4"].status == "pdf"

    # W3's "pdf_url" served a login page: rejected, abstract fetched from Semantic Scholar instead
    assert papers["W3"].status == "abstract_only"
    assert not (tmp_path / "pdfs" / "W3.pdf").exists()
    assert papers["W3"].abstract_source == "semantic_scholar"
    md = (tmp_path / "abstracts" / "W3.md").read_text()
    assert "abstract from semantic scholar for DOI:10.1000/three" in md and "https://doi.org/10.1000/three" in md

    # the seed itself has no free PDF but has an OpenAlex abstract
    assert papers["W1"].status == "abstract_only"
    assert papers["W1"].abstract_source == "openalex"

    # manifests written; the API key never ends up in the cache key or the manifest
    rows = [json.loads(line) for line in (tmp_path / "manifest.jsonl").read_text().splitlines()]
    assert len(rows) == 4
    assert "KEY" not in (tmp_path / "manifest.csv").read_text()
    assert all(c[1].get("api_key") == "KEY" for c in session.calls if c[0].startswith(cb.OPENALEX))
    assert all("api_key" not in c[1] for c in session.calls if c[0].startswith(cb.S2))


def test_semantic_scholar_is_asked_once_for_all_missing_abstracts(tmp_path):
    many = {f"W{100 + i}": work(f"W{100 + i}", f"Abstractless paper number {i} " + LONG, doi=f"10.1000/x{i}")
            for i in range(30)}
    seed = work("W90", "Seed with many abstractless references " + LONG, doi="10.1000/seed",
                refs=list(many), abstract="seed")
    WORKS.update(many, W90=seed)
    try:
        papers, session = run(tmp_path, ["10.1000/seed"], max_citing=0, download=False)
    finally:
        for k in [*many, "W90"]:
            WORKS.pop(k)
    s2_calls = [c for c in session.calls if c[0].startswith(cb.S2)]
    assert len(s2_calls) == 1 and len(s2_calls[0][2]["ids"]) == 30
    assert all(papers[k].abstract_source == "semantic_scholar" for k in many)


def test_semantic_scholar_outage_does_not_stop_the_run(tmp_path):
    session = FakeSession()
    session.s2_always_429 = True
    papers, _ = run(tmp_path, ["10.1103/physrevlett.98.146401"], session=session)
    assert papers["W3"].status == "metadata_only"  # no abstract anywhere, but still in the corpus
    assert papers["W2"].status == "pdf"


def test_title_seed_and_shared_references(tmp_path):
    papers, _ = run(tmp_path, ["E(3)-equivariant graph neural networks for data-efficient and accurate "
                               "interatomic potentials", "10.1103/physrevlett.98.146401"])
    assert "W6" in papers and "seed" in papers["W6"].roles
    assert set(papers["W3"].via_seeds) == {"W6", "W1"}  # referenced by both seeds, stored once


def test_unconfident_title_match_is_skipped(tmp_path):
    papers, _ = run(tmp_path, ["completely unrelated title about cooking pasta"])
    assert papers == {}


def test_rerun_uses_cache_and_keeps_pdfs(tmp_path):
    run(tmp_path, ["10.1103/physrevlett.98.146401"])
    papers, session = run(tmp_path, ["10.1103/physrevlett.98.146401"])
    assert not any(url.startswith(cb.OPENALEX) for url, _ in session.calls)  # all from cache
    assert papers["W2"].status == "pdf" and papers["W2"].note == "already downloaded"


def test_no_download_mode(tmp_path):
    papers, session = run(tmp_path, ["10.1103/physrevlett.98.146401"], download=False, use_s2=False)
    assert all(p.status in ("not_downloaded",) for p in papers.values())
    assert not any("arxiv.org/pdf" in url for url, _ in session.calls)
    assert not list((tmp_path / "pdfs").iterdir())


def test_retries_after_429(tmp_path):
    session = FakeSession()
    session.fail_once_429.add(cb.OPENALEX + "/works/doi:10.1103/physrevlett.98.146401")
    papers, _ = run(tmp_path, ["10.1103/physrevlett.98.146401"], session=session)
    assert "W1" in papers


def test_max_citing_zero_skips_forward_hop(tmp_path):
    papers, _ = run(tmp_path, ["10.1103/physrevlett.98.146401"], max_citing=0)
    assert set(papers) == {"W1", "W2", "W3"}
