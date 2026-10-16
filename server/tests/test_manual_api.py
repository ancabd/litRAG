import json
import sys
from pathlib import Path

CORE_TESTS = Path(__file__).resolve().parents[2] / "corpus-builder" / "tests"
sys.path.insert(0, str(CORE_TESTS))
from test_ingest import make_paper  # noqa: E402


def manifest(data_dir):
    return {r["openalex_id"]: r for r in map(json.loads, (data_dir / "corpus" / "manifest.jsonl").read_text().splitlines())}


def test_add_pdf_makes_paper_searchable(client, data_dir, tmp_path):
    assert client.get("/api/papers/W2").json()["status"] == "abstract_only"
    pdf = make_paper(tmp_path / "library.pdf").read_bytes()
    r = client.post("/api/papers/W2/pdf", content=pdf, headers={"Content-Type": "application/pdf"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["paper"]["status"] == "pdf" and body["paper"]["added_manually"] == ["pdf"]
    assert body["paper"]["pdf_available"] and body["paper"]["n_chunks"] > 1
    assert body["ingest"] == [{"run": "pymupdf_w400_o60", "source": "pdf", "n_chunks": body["paper"]["n_chunks"],
                               "error": None, "warnings": None}]
    m = manifest(data_dir)["W2"]
    assert m["status"] == "pdf" and m["note"] == "added manually"
    assert "W2" in (data_dir / "corpus" / "manual.jsonl").read_text()
    assert "W2,pdf" in (data_dir / "corpus" / "manifest.csv").read_text().replace('"', "")
    # immediately searchable, and listed with its new status
    hits = client.get("/api/search", params={"q": "appendix sentence", "paper": "W2"}).json()["items"]
    assert hits and hits[0]["source"] == "pdf"
    assert client.get("/api/papers", params={"status": "pdf", "q": "equivariant"}).json()["total"] == 1
    assert client.get("/api/papers/W2/pdf").content.startswith(b"%PDF")

    r = client.delete("/api/papers/W2/pdf")
    assert r.status_code == 200 and r.json()["paper"]["status"] == "abstract_only"
    assert r.json()["ingest"][0]["source"] == "abstract"
    assert client.get("/api/papers/W2/pdf").status_code == 404


def test_unparseable_pdf_is_reported(client, data_dir):
    r = client.post("/api/papers/W2/pdf", content=b"%PDF-1.4 scanned garbage", headers={"Content-Type": "application/pdf"})
    assert r.status_code == 200
    ing = r.json()["ingest"][0]
    assert ing["source"] == "abstract_fallback" and ing["error"]  # saved, but the abstract is used instead


def test_add_abstract_to_metadata_only(client, data_dir):
    r = client.put("/api/papers/W3/abstract", json={"abstract": "A classic fixed-charge force field for proteins."})
    assert r.status_code == 200, r.text
    assert r.json()["paper"]["status"] == "abstract_only" and r.json()["paper"]["abstract_source"] == "manual"
    assert r.json()["ingest"][0]["n_chunks"] == 1
    assert client.get("/api/search", params={"q": "fixed-charge"}).json()["items"][0]["paper_id"] == "W3"
    r = client.put("/api/papers/W3/abstract", json={"abstract": ""})
    assert r.json()["paper"]["status"] == "metadata_only"


def test_manual_errors(client):
    assert client.post("/api/papers/W2/pdf", content=b"<html>", headers={"Content-Type": "application/pdf"}).status_code == 400
    assert client.post("/api/papers/W999/pdf", content=b"%PDF").status_code == 404
    assert client.delete("/api/papers/W2/pdf").status_code == 400
    r = client.put("/api/papers/W2/abstract", json={"abstract": "replace it"})
    assert r.status_code == 400 and "already has an abstract" in r.json()["detail"]
