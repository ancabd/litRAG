"""Tests for parsing and chunking, on PDFs generated on the fly."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingest.chunking import ChunkConfig, chunk_document  # noqa: E402
from ingest.documents import Paragraph, ParsedDocument, ParseError, Section  # noqa: E402
from ingest.parsers import available, get_parser  # noqa: E402
from ingest.pipeline import run  # noqa: E402

BODY = ("Machine-learned interatomic potentials map atomic configurations to energies and forces. "
        "They are trained on reference data from density functional theory calculations. ")


def para(n: int, tag: str) -> str:
    return " ".join(f"{tag} sentence {i} says that {BODY}" for i in range(n))


def make_paper(path: Path) -> Path:
    """A 4-page paper with the usual mess of a real one."""
    doc = pymupdf.open()
    W, H = 595, 842
    for _ in range(4):
        doc.new_page(width=W, height=H)
    pages = [doc[i] for i in range(4)]
    for i, page in enumerate(pages, 1):
        page.insert_text((60, 30), "J. Chem. Phys. 160, 0941 (2024)", fontsize=8)          # running header
        page.insert_text((W / 2, H - 25), str(i), fontsize=8)                               # page number
    pages[0].insert_text((20, 600), "arXiv:2401.01234v2 [physics.chem-ph] 5 Jan 2024", fontsize=9, rotate=90)

    def box(page, y0, y1, text, size=10, bold=False):
        if len(text) < 80 and "\n" not in text:
            y1 = max(y1, y0 + size * 2.2)  # single line: make the box tall enough for the font
        rc = page.insert_textbox(pymupdf.Rect(60, y0, W - 60, y1), text, fontsize=size,
                                 fontname="hebo" if bold else "helv")
        assert rc >= 0, f"text did not fit: {text[:40]}"

    p1 = pages[0]
    box(p1, 60, 110, "Equivariant potentials for proteins", size=18, bold=True)
    box(p1, 115, 135, "Ada Lovelace, Alan Turing")
    box(p1, 145, 162, "Abstract", size=12, bold=True)
    box(p1, 165, 260, "We present an equivariant poten-\ntial for biomolecular simulation. " + para(2, "abs"))
    box(p1, 275, 292, "1 Introduction", size=12, bold=True)
    box(p1, 295, 560, para(6, "intro"))
    box(p1, 570, 780, para(5, "intro2"))

    p2 = pages[1]
    box(p2, 60, 77, "2 Methods", size=12, bold=True)
    box(p2, 80, 300, para(5, "methods"))
    box(p2, 310, 345, "Figure 1. Architecture of the network.", bold=True)
    box(p2, 355, 372, "2.1 Training data", size=11, bold=True)
    box(p2, 375, 600, para(5, "data"))

    p3 = pages[2]
    box(p3, 60, 77, "Acknowledgments", size=12, bold=True)
    box(p3, 80, 120, "We thank the funding agency for generous support of this work.")
    box(p3, 130, 147, "References", size=12, bold=True)
    box(p3, 150, 400, "\n".join(f"{i}. Behler, J. & Parrinello, M. Generalized neural-network representation. "
                               f"Phys. Rev. Lett. 98, 146401 (2007)." for i in range(1, 9)))
    box(p3, 410, 427, "Appendix A: Symmetry functions", size=12, bold=True)
    box(p3, 430, 700, para(5, "appendix"))

    box(pages[3], 60, 300, para(5, "appendix2"))
    doc.save(path)
    return path


@pytest.fixture
def paper(tmp_path):
    return make_paper(tmp_path / "W1.pdf")


# ------------------------------------------------------------------ parser

def test_registry():
    assert "pymupdf" in available()
    with pytest.raises(ValueError, match="Unknown parser"):
        get_parser("nope")


def test_pymupdf_structure(paper):
    doc = get_parser("pymupdf").parse(paper, "W1")
    titles = [s.title for s in doc.sections]
    assert titles[:5] == ["Equivariant potentials for proteins", "Abstract", "1 Introduction",
                          "2 Methods", "2 Methods > 2.1 Training data"]
    assert "Appendix A: Symmetry functions" in titles   # kept although it follows the references
    assert not any("References" in t or "Acknowledg" in t for t in titles)
    assert not any(t.startswith("Figure") for t in titles)

    text = doc.to_markdown()
    assert "potential for biomolecular" in text            # hyphenated line break re-joined
    assert "Behler, J. & Parrinello" not in text           # reference list removed
    assert "funding agency" not in text                    # boilerplate removed
    assert "J. Chem. Phys." not in text                    # running header removed
    assert "arXiv:2401" not in text                        # vertical stamp removed
    assert "Figure 1. Architecture" in text                # caption kept as text
    assert "appendix2 sentence 0" in text                  # last page kept

    appendix = next(s for s in doc.sections if s.title.startswith("Appendix"))
    assert {p.page for p in appendix.paragraphs} == {3, 4}  # page numbers tracked
    assert doc.n_pages == 4 and not doc.warnings


def test_unparseable_pdf_raises(tmp_path):
    empty = pymupdf.open()
    empty.new_page()
    empty.save(tmp_path / "empty.pdf")
    with pytest.raises(ParseError):
        get_parser("pymupdf").parse(tmp_path / "empty.pdf", "X")
    (tmp_path / "broken.pdf").write_bytes(b"%PDF-1.4 garbage")
    with pytest.raises(ParseError):
        get_parser("pymupdf").parse(tmp_path / "broken.pdf", "X")


def test_document_roundtrip(paper, tmp_path):
    doc = get_parser("pymupdf").parse(paper, "W1")
    doc.save(tmp_path / "c" / "W1.json")
    assert ParsedDocument.load(tmp_path / "c" / "W1.json") == doc


# ------------------------------------------------------------------ chunker

def make_doc(*sections):
    return ParsedDocument("P", "pdf", "test", "1",
                          [Section(t, [Paragraph(x, page=i + 1) for i, x in enumerate(ps)]) for t, ps in sections])


def test_chunks_respect_size_overlap_and_sections():
    long = para(30, "x")  # ~600+ words
    doc = make_doc(("Intro", [long]), ("Methods", [para(3, "m")]))
    chunks = chunk_document(doc, ChunkConfig(size=150, overlap=30, min_words=20))
    assert all(c.n_words <= 150 + 30 for c in chunks)
    assert {c.section for c in chunks} == {"Intro", "Methods"}
    intro = [c for c in chunks if c.section == "Intro"]
    assert len(intro) >= 4
    # consecutive chunks share text (overlap), and no chunk mixes sections
    assert intro[0].text.split()[-5:] == intro[1].text.split()[:len(intro[1].text.split())][
        intro[1].text.split().index(intro[0].text.split()[-5]):][:5]
    assert [c.chunk_id for c in chunks] == [f"P#{i:03d}" for i in range(len(chunks))]


def test_tiny_tail_is_merged_and_giant_sentence_split():
    doc = make_doc(("S", [" ".join(["word"] * 1000)]))  # one 1000-word "sentence"
    chunks = chunk_document(doc, ChunkConfig(size=300, overlap=0, min_words=150))
    assert sum(c.n_words for c in chunks) == 1000
    assert all(c.n_words <= 400 for c in chunks)
    assert len(chunks) == 3  # 300 + 300 + (300 + 100 merged tail)


def test_pages_recorded():
    doc = make_doc(("S", [para(4, "a"), para(4, "b"), para(4, "c")]))
    chunks = chunk_document(doc, ChunkConfig(size=200, overlap=0, min_words=10))
    assert chunks[0].page_start == 1 and chunks[-1].page_end == 3


def test_bad_chunk_config():
    with pytest.raises(ValueError):
        ChunkConfig(size=100, overlap=100)


# ------------------------------------------------------------------ pipeline

def make_corpus(tmp_path):
    corpus = tmp_path / "corpus"
    (corpus / "pdfs").mkdir(parents=True)
    make_paper(corpus / "pdfs" / "W1.pdf")
    (corpus / "pdfs" / "W2.pdf").write_bytes(b"%PDF-1.4 broken")
    rows = [
        {"openalex_id": "W1", "status": "pdf", "pdf_path": "pdfs/W1.pdf", "title": "Equivariant", "year": 2024,
         "authors": "A. Lovelace", "doi": "10.1/one", "venue": "JCP", "abstract": "abs one"},
        {"openalex_id": "W2", "status": "pdf", "pdf_path": "pdfs/W2.pdf", "title": "Broken pdf", "year": 2020,
         "abstract": "The broken paper still has an abstract about force fields."},
        {"openalex_id": "W3", "status": "abstract_only", "title": "Paywalled", "year": 2007,
         "abstract": "Neural network potentials for high-dimensional surfaces."},
        {"openalex_id": "W4", "status": "metadata_only", "title": "Nothing", "abstract": None},
    ]
    (corpus / "manifest.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    return corpus


def test_pipeline_end_to_end(tmp_path):
    corpus = make_corpus(tmp_path)
    out = run(corpus, tmp_path / "chunks", cfg=ChunkConfig(200, 30), workers=2)
    assert out.name == "pymupdf_w200_o30"

    chunks = [json.loads(line) for line in (out / "chunks.jsonl").read_text().splitlines()]
    by_paper = {}
    for c in chunks:
        by_paper.setdefault(c["paper_id"], []).append(c)
    assert set(by_paper) == {"W1", "W2", "W3"}                     # W4 has nothing to index
    assert all(c["source"] == "pdf" and c["title"] == "Equivariant" for c in by_paper["W1"])
    assert by_paper["W2"][0]["source"] == "abstract_fallback"     # parse failure -> abstract
    assert by_paper["W3"][0]["source"] == "abstract" and by_paper["W3"][0]["section"] == "Abstract"

    summary = json.loads((out / "run.json").read_text())
    assert summary["parser"] == "pymupdf@2" and "W2" in summary["failures"]
    assert summary["papers_by_source"] == {"pdf": 1, "abstract_fallback": 1, "abstract": 1, "skipped": 1}
    assert (corpus / "parsed" / "pymupdf@2" / "W1.json").exists()


def test_pipeline_rechunk_uses_cache(tmp_path):
    corpus = make_corpus(tmp_path)
    run(corpus, tmp_path / "chunks", cfg=ChunkConfig(200, 30), workers=1)
    out = run(corpus, tmp_path / "chunks", cfg=ChunkConfig(100, 20), workers=1)
    report = (out / "papers.csv").read_text()
    assert "W1,Equivariant,pdf,pdf,4" in report and ",True," in report  # cached=True for W1
    assert out.name == "pymupdf_w100_o20"


# ------------------------------------------------------------------ real LaTeX output

@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex not installed")
def test_two_column_latex_paper(tmp_path):
    """A real two-column LaTeX layout: fancyhdr header, page numbers, equation, \\AA, bibliography, appendix."""
    tex = Path(__file__).parent / "fixtures" / "twocolumn_paper.tex"
    shutil.copy(tex, tmp_path / "paper.tex")
    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "paper.tex"], cwd=tmp_path,
                       capture_output=True, timeout=120)
    doc = get_parser("pymupdf").parse(tmp_path / "paper.pdf", "P")
    titles = [s.title for s in doc.sections]
    assert titles == ["Abstract", "1 Introduction", "2 Methods > 2.1 Equivariant features",
                      "2 Methods > 2.2 Training data", "3 Results", "4 Conclusion", "A Hyperparameters"]
    text = doc.to_markdown()
    assert "J. Chem. Phys." not in text                       # running header
    assert not any(p.text.strip().isdigit() for s in doc.sections for p in s.paragraphs)  # page numbers
    assert "5 Å" in text                                      # LaTeX \AA recomposed
    assert "Phys. Rev. Lett. 98" not in text                  # bibliography removed
    assert "funding agency" not in text                       # acknowledgments removed
    eq = next(s for s in doc.sections if "Equivariant features" in s.title).paragraphs[0].text
    assert eq.startswith("The energy is a sum of atomic contributions, E =") and "(1)" in eq
