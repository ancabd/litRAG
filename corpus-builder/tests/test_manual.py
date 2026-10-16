"""Manual additions: PDFs and abstracts added by hand must update the manifest and survive rebuilds."""
import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import corpus_builder as cb  # noqa: E402
from ingest.chunking import ChunkConfig  # noqa: E402
from ingest.pipeline import paper_report, rebuild_runs, run  # noqa: E402
from test_corpus_builder import run as build_corpus  # noqa: E402
from test_ingest import make_paper  # noqa: E402

PDF = b"%PDF-1.4 a paper from the library"


def rows(out):
    return {r["openalex_id"]: r for r in cb.load_manifest_rows(out)}


def csv_rows(out):
    with open(out / "manifest.csv", newline="") as fh:
        return {r["openalex_id"]: r for r in csv.DictReader(fh)}


def test_add_pdf_updates_everything_and_survives_rebuild(tmp_path):
    build_corpus(tmp_path, ["10.1103/physrevlett.98.146401"])
    assert rows(tmp_path)["W3"]["status"] == "abstract_only"
    assert (tmp_path / "abstracts" / "W3.md").exists()

    row = cb.add_manual_pdf(tmp_path, "W3", PDF)
    assert row["status"] == "pdf" and row["added_manually"] == ["pdf"] and row["note"] == "added manually"
    assert (tmp_path / "pdfs" / "W3.pdf").read_bytes() == PDF
    assert not (tmp_path / "abstracts" / "W3.md").exists()
    assert rows(tmp_path)["W3"]["pdf_path"] == "pdfs/W3.pdf"
    assert csv_rows(tmp_path)["W3"]["status"] == "pdf" and csv_rows(tmp_path)["W3"]["added_manually"] == "pdf"
    assert json.loads((tmp_path / "manual.jsonl").read_text())["pdf"] is True
    assert rows(tmp_path)["W2"]["status"] == "pdf"  # other papers untouched

    # a full rerun of the corpus builder regenerates the manifest from OpenAlex: the manual PDF must stay
    build_corpus(tmp_path, ["10.1103/physrevlett.98.146401"])
    after = rows(tmp_path)["W3"]
    assert after["status"] == "pdf" and after["added_manually"] == ["pdf"] and after["note"] == "added manually"

    row = cb.remove_manual_pdf(tmp_path, "W3")
    assert row["status"] == "abstract_only" and row["added_manually"] == [] and row["pdf_path"] is None
    assert not (tmp_path / "pdfs" / "W3.pdf").exists() and (tmp_path / "abstracts" / "W3.md").exists()
    assert (tmp_path / "manual.jsonl").read_text() == ""


def test_add_abstract_to_metadata_only_paper(tmp_path):
    session_corpus = build_corpus(tmp_path, ["10.1103/physrevlett.98.146401"], use_s2=False)[0]
    assert session_corpus["W3"].status == "metadata_only"

    row = cb.set_manual_abstract(tmp_path, "W3", "  We fit a   force field to\nDFT data. ")
    assert row["status"] == "abstract_only" and row["abstract"] == "We fit a force field to DFT data."
    assert row["abstract_source"] == "manual" and row["added_manually"] == ["abstract"]
    assert "We fit a force field" in (tmp_path / "abstracts" / "W3.md").read_text()

    build_corpus(tmp_path, ["10.1103/physrevlett.98.146401"], use_s2=False)
    assert rows(tmp_path)["W3"]["abstract"] == "We fit a force field to DFT data."

    row = cb.set_manual_abstract(tmp_path, "W3", "")
    assert row["status"] == "metadata_only" and row["abstract"] is None and row["added_manually"] == []


def test_manual_edit_errors(tmp_path):
    build_corpus(tmp_path, ["10.1103/physrevlett.98.146401"])
    with pytest.raises(cb.ManualEditError, match="isn't a PDF"):
        cb.add_manual_pdf(tmp_path, "W3", b"<html>login</html>")
    with pytest.raises(cb.ManualEditError, match="already has a downloaded full text"):
        cb.add_manual_pdf(tmp_path, "W2", PDF)
    with pytest.raises(cb.ManualEditError, match="No paper"):
        cb.add_manual_pdf(tmp_path, "W999", PDF)
    with pytest.raises(cb.ManualEditError, match="no manually added PDF"):
        cb.remove_manual_pdf(tmp_path, "W2")
    with pytest.raises(cb.ManualEditError, match="already has an abstract"):
        cb.set_manual_abstract(tmp_path, "W1", "replacement")
    assert (tmp_path / "pdfs" / "W2.pdf").exists()  # the downloaded PDF was never touched
    cb.add_manual_pdf(tmp_path, "W3", PDF)
    cb.add_manual_pdf(tmp_path, "W3", PDF + b" v2")  # replacing your own manual PDF is fine
    assert (tmp_path / "pdfs" / "W3.pdf").read_bytes().endswith(b"v2")


def test_rebuild_runs_indexes_the_new_pdf(tmp_path):
    corpus = tmp_path / "corpus"
    (corpus / "pdfs").mkdir(parents=True)
    (corpus / "abstracts").mkdir()
    base = [{"openalex_id": "W1", "status": "abstract_only", "title": "Paywalled", "year": 2020,
             "abstract": "Only the abstract.", "abstract_source": "openalex", "roles": ["seed"], "via_seeds": ["W1"]}]
    cb.write_manifest_rows(base, corpus)
    chunks = tmp_path / "chunks"
    run(corpus, chunks, cfg=ChunkConfig(200, 30), workers=0)
    run(corpus, chunks, cfg=ChunkConfig(100, 20), workers=0)
    assert paper_report(chunks / "pymupdf_w200_o30", "W1")["source"] == "abstract"

    pdf = make_paper(tmp_path / "library.pdf").read_bytes()
    cb.add_manual_pdf(corpus, "W1", pdf)
    results = rebuild_runs(corpus, chunks)
    assert sorted(r["run"] for r in results) == ["pymupdf_w100_o20", "pymupdf_w200_o30"]
    for name in ("pymupdf_w200_o30", "pymupdf_w100_o20"):
        rep = paper_report(chunks / name, "W1")
        assert rep["source"] == "pdf" and int(rep["n_chunks"]) > 1, rep
    info = json.loads((chunks / "pymupdf_w100_o20" / "run.json").read_text())
    assert info["chunking"]["size"] == 100  # each run keeps its own settings
