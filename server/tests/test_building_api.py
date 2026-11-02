import json
import sys
import time
import zipfile
from pathlib import Path

import pytest

CORE_TESTS = Path(__file__).resolve().parents[2] / "corpus-builder" / "tests"
sys.path.insert(0, str(CORE_TESTS))
from test_ingest import make_paper  # noqa: E402

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402

SERVER = Path(__file__).resolve().parents[1]

NOTES = b"""# Field notes

Thermostats keep the temperature of a molecular dynamics simulation close to a target value.

## Langevin dynamics

The Langevin thermostat adds friction and random kicks to each particle, which samples the canonical ensemble.
"""


@pytest.fixture
def empty(tmp_path):
    """An app over a data folder with nothing in it yet."""
    from fastapi.testclient import TestClient
    data = tmp_path / "data"
    settings = Settings.from_env(core_dir=SERVER.parent / "corpus-builder", corpus_dir=data / "corpus",
                                 chunks_root=data / "chunks", questions_file=data / "questions" / "questions.yaml",
                                 runs_dir=data / "runs", cache_dir=data / "cache", web_dist=tmp_path / "no-dist")
    return TestClient(create_app(settings)), data


def wait(client, job: dict) -> dict:
    for _ in range(200):
        job = client.get(f"/api/jobs/{job['id']}").json()
        if job["state"] != "running":
            return job
        time.sleep(0.05)
    raise AssertionError("job did not finish")


def test_empty_corpus_overview(empty):
    client, _ = empty
    o = client.get("/api/corpus").json()
    assert o["papers"] == 0 and o["documents"] == 0 and o["runs"] == [] and o["job"] is None
    assert ".md" in o["suffixes"] and ".docx" in o["suffixes"]


def test_upload_documents_builds_a_searchable_corpus(empty, tmp_path):
    client, data = empty
    r = client.post("/api/corpus/documents", params={"filename": "notes.md"}, content=NOTES)
    assert r.status_code == 200, r.text
    assert r.json()["openalex_id"] == "D0001" and r.json()["title"] == "Field notes"
    assert r.json()["status"] == "document" and r.json()["source_file"] == "notes.md"
    pdf = make_paper(tmp_path / "handbook.pdf").read_bytes()
    r = client.post("/api/corpus/documents", params={"filename": "handbook.pdf", "title": "My handbook"}, content=pdf)
    assert r.json()["openalex_id"] == "D0002" and r.json()["title"] == "My handbook"

    job = wait(client, client.post("/api/corpus/reindex").json())
    assert job["state"] == "done", job
    assert job["result"]["runs"][0]["run"] == "pymupdf_w400_o60"
    assert any("full texts" in line for line in job["meta"]["log"])

    o = client.get("/api/corpus").json()
    assert o["documents"] == 2 and o["papers"] == 0 and o["runs"] == ["pymupdf_w400_o60"]
    hits = client.get("/api/search", params={"q": "Langevin friction random kicks"}).json()["items"]
    assert hits and hits[0]["paper_id"] == "D0001" and hits[0]["section"] == "Langevin dynamics"
    assert client.get("/api/papers/D0002/pdf").content.startswith(b"%PDF")
    listed = client.get("/api/papers", params={"role": "document"}).json()
    assert listed["total"] == 2

    r = client.delete("/api/corpus/documents/D0001")
    assert r.status_code == 200
    assert wait(client, r.json()["job"])["state"] == "done"
    assert client.get("/api/papers/D0001").status_code == 404
    assert not (data / "corpus" / "documents" / "D0001.md").exists()
    hits = client.get("/api/search", params={"q": "Langevin friction random kicks"}).json()["items"]
    assert all(h["paper_id"] != "D0001" for h in hits)


def test_upload_rejects_bad_files(empty):
    client, _ = empty
    r = client.post("/api/corpus/documents", params={"filename": "old.doc"}, content=b"stuff")
    assert r.status_code == 400 and ".doc" in r.json()["detail"]
    r = client.post("/api/corpus/documents", params={"filename": "fake.pdf"}, content=b"hello")
    assert r.status_code == 400 and "isn't a PDF" in r.json()["detail"]
    r = client.post("/api/corpus/documents", params={"filename": "empty.txt"}, content=b"")
    assert r.status_code == 400
    assert client.delete("/api/corpus/documents/D0042").status_code == 404


def test_docx_and_html_documents(empty, tmp_path):
    client, _ = empty
    w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    docx = tmp_path / "r.docx"
    with zipfile.ZipFile(docx, "w") as z:
        z.writestr("word/document.xml", f'<w:document {w}><w:body>'
                   '<w:p><w:pPr><w:pStyle w:val="Title"/></w:pPr><w:r><w:t>Lab handbook</w:t></w:r></w:p>'
                   '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Safety</w:t></w:r></w:p>'
                   '<w:p><w:r><w:t>Always wear goggles when </w:t></w:r><w:r><w:t>handling the centrifuge rotor.</w:t></w:r></w:p>'
                   '</w:body></w:document>')
    html = b"<html><head><title>Wiki page</title><script>var x;</script></head><body><nav>Home</nav>" \
           b"<h2>Pumps</h2><p>The peristaltic pump needs new tubing every month of use.</p></body></html>"
    assert client.post("/api/corpus/documents", params={"filename": "r.docx"}, content=docx.read_bytes()).json()["title"] == "Lab handbook"
    assert client.post("/api/corpus/documents", params={"filename": "w.html"}, content=html).json()["title"] == "Wiki page"
    assert wait(client, client.post("/api/corpus/reindex").json())["state"] == "done"
    hit = client.get("/api/search", params={"q": "goggles centrifuge"}).json()["items"][0]
    assert hit["paper_id"] == "D0001" and hit["section"] == "Safety"
    hit = client.get("/api/search", params={"q": "peristaltic tubing"}).json()["items"][0]
    assert hit["paper_id"] == "D0002" and hit["section"] == "Pumps" and "var x" not in hit["text"]


def test_build_from_seeds_runs_builder_then_chunks(empty, monkeypatch):
    client, data = empty
    import app.core as core
    from corpus_builder import Paper, write_manifest_rows
    from dataclasses import asdict
    calls = {}

    def fake_build(seed_lines, out, *, api_key, max_citing, recent_citing, download, progress):
        calls.update(seeds=seed_lines, key=api_key, max_citing=max_citing, download=download)
        from logsink import log
        log("Resolving 2 seed(s)...")
        out.mkdir(parents=True, exist_ok=True)
        p = Paper("W9", "Neural thermostats", None, 2024, "article", "A. Author", None, 3, True, roles=["seed"],
                  abstract="We learn a thermostat for coarse-grained molecular dynamics with a neural network.",
                  status="abstract_only")
        write_manifest_rows([asdict(p)], out)
        progress(1, 1)
        return [p]

    monkeypatch.setattr(core, "build_corpus", fake_build)
    r = client.post("/api/corpus/build", json={"seeds": "10.1103/PhysRevLett.98.146401\n# comment\narxiv:2101.03164",
                                              "max_citing": 10, "download": False, "openalex_key": " k "})
    assert r.status_code == 200, r.text
    job = wait(client, r.json())
    assert job["state"] == "done", job
    assert calls == {"seeds": ["10.1103/PhysRevLett.98.146401", "arxiv:2101.03164"], "key": "k", "max_citing": 10,
                     "download": False}
    assert job["result"]["papers"] == 1 and job["meta"]["phase"] == "parse"
    assert "Resolving 2 seed(s)..." in job["meta"]["log"]
    assert client.get("/api/search", params={"q": "neural thermostat"}).json()["items"][0]["paper_id"] == "W9"
    # only for a new corpus
    r = client.post("/api/corpus/build", json={"seeds": "10.1/abc"})
    assert r.status_code == 409


def test_build_validates_seeds(empty):
    client, _ = empty
    assert client.post("/api/corpus/build", json={"seeds": "  \n# only a comment"}).status_code == 400
    assert client.post("/api/corpus/build", json={"seeds": "x"}).status_code in (200, 400)
