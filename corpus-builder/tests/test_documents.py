"""Uploaded documents: the text parser and their path through parsing and chunking."""
import json
import zipfile

import pytest

import corpus_builder as cb
from ingest.documents import ParseError
from ingest.parsers.text_parser import TextParser, guess_title
from ingest.pipeline import rebuild_runs


def parse(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content if isinstance(content, bytes) else content.encode())
    return TextParser().parse(path, "D0001")


def test_markdown_sections_and_cleanup(tmp_path):
    doc = parse(tmp_path, "a.md", "# Title\n\nIntro with **bold** and a [link](http://x.org).\n\n"
                                  "## Setup\n\n```\ncode block\n```\n\n- first item\n- second item\n\n"
                                  "Setext heading\n--------------\n\nUnder it.\n")
    assert [s.title for s in doc.sections] == ["Title", "Setup", "Setext heading"]
    assert doc.sections[0].paragraphs[0].text == "Intro with bold and a link."
    assert [p.text for p in doc.sections[1].paragraphs] == ["code block", "first item", "second item"]
    assert doc.source == "document" and doc.sections[0].paragraphs[0].page is None


def test_plain_text_has_one_section_named_after_nothing(tmp_path):
    doc = parse(tmp_path, "a.txt", "# not a heading in plain text\n\nSecond paragraph.")
    assert [s.title for s in doc.sections] == ["Text"]
    assert len(doc.sections[0].paragraphs) == 2


def test_html_skips_scripts_and_navigation(tmp_path):
    doc = parse(tmp_path, "a.html", "<html><head><title>T</title><style>p{}</style></head><body><nav>Menu</nav>"
                                    "<p>Before.</p><h2>Part <i>one</i></h2><p>Hello &amp; welcome.</p>"
                                    "<script>alert(1)</script><ul><li>x</li><li>y</li></ul></body></html>")
    assert [s.title for s in doc.sections] == ["T", "Part one"]
    assert [p.text for p in doc.sections[1].paragraphs] == ["Hello & welcome.", "x", "y"]
    assert "Menu" not in json.dumps(doc.to_dict()) and "alert" not in json.dumps(doc.to_dict())


def test_docx_headings_from_styles(tmp_path):
    w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    path = tmp_path / "a.docx"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", f'<w:document {w}><w:body>'
                   '<w:p><w:r><w:t>Front text.</w:t></w:r></w:p>'
                   '<w:p><w:pPr><w:pStyle w:val="Kop2"/></w:pPr><w:r><w:t>Results</w:t></w:r></w:p>'
                   '<w:p><w:r><w:t xml:space="preserve">It </w:t></w:r><w:r><w:t>worked.</w:t></w:r></w:p>'
                   '</w:body></w:document>')
        # localized style id ("Kop2" in Dutch Word) with the standard style name
        z.writestr("word/styles.xml", f'<w:styles {w}><w:style w:styleId="Kop2"><w:name w:val="heading 2"/></w:style></w:styles>')
    doc = TextParser().parse(path, "D1")
    assert [(s.title, [p.text for p in s.paragraphs]) for s in doc.sections] == [
        ("Text", ["Front text."]), ("Results", ["It worked."])]
    assert guess_title(path, "my_lab-report.docx") == "my lab report"


def test_empty_and_broken_files_raise(tmp_path):
    with pytest.raises(ParseError):
        parse(tmp_path, "a.md", "\n\n   \n")
    with pytest.raises(ParseError):
        parse(tmp_path, "b.docx", b"PK not really a zip")


def test_non_utf8_text_is_read(tmp_path):
    doc = parse(tmp_path, "a.txt", "Caf\xe9 au lait.".encode("cp1252"))
    assert doc.sections[0].paragraphs[0].text == "Café au lait."


def test_documents_are_parsed_cached_and_chunked(tmp_path):
    corpus, chunks = tmp_path / "corpus", tmp_path / "chunks"
    body = " ".join(f"Sentence {i} about the Nose-Hoover thermostat." for i in range(120))
    cb.add_document(corpus, "notes.md", f"# Notes\n\n## Thermostats\n\n{body}\n".encode())
    runs = rebuild_runs(corpus, chunks, create_default=True)
    assert runs[0]["run"] == "pymupdf_w400_o60" and runs[0]["papers_by_source"] == {"document": 1}
    rows = [json.loads(line) for line in open(chunks / "pymupdf_w400_o60" / "chunks.jsonl")]
    assert len(rows) >= 2 and {r["section"] for r in rows} == {"Thermostats"}
    assert rows[0]["paper_id"] == "D0001" and rows[0]["title"] == "Notes" and rows[0]["source"] == "document"
    assert (corpus / "parsed" / "text@1" / "D0001.json").exists()
    # without create_default and without runs, nothing happens
    assert rebuild_runs(corpus, tmp_path / "none") == []
    cb.remove_document(corpus, "D0001")
    assert rebuild_runs(corpus, chunks)[0]["chunks"] == 0


def test_printed_page_numbers_from_pdf_labels(tmp_path):
    """A book whose PDF numbers its front matter i, ii and then 1, 2: chunks carry the printed numbers."""
    import pymupdf
    from ingest.pipeline import page_labels
    doc = pymupdf.open()
    for i in range(4):
        page = doc.new_page()
        page.insert_textbox(pymupdf.Rect(72, 72, 520, 760),
                            f"Page {i} text about thermostats and barostats in molecular simulation. " * 25)
    doc.set_page_labels([{"startpage": 0, "prefix": "", "style": "r", "firstpagenum": 1},
                         {"startpage": 2, "prefix": "", "style": "D", "firstpagenum": 1}])
    pdf = tmp_path / "book.pdf"
    doc.save(pdf)
    assert page_labels(pdf) == {1: "i", 2: "ii", 3: "1", 4: "2"}

    plain = pymupdf.open()
    plain.new_page()
    plain.save(tmp_path / "plain.pdf")
    assert page_labels(tmp_path / "plain.pdf") is None

    corpus, chunks = tmp_path / "corpus", tmp_path / "chunks"
    cb.add_document(corpus, "book.pdf", pdf.read_bytes(), title="A book")
    rebuild_runs(corpus, chunks, create_default=True)
    rows = [json.loads(line) for line in open(chunks / "pymupdf_w400_o60" / "chunks.jsonl")]
    by_page = {r["page_start"]: r["page_label_start"] for r in rows}
    assert by_page.get(1) == "i" and by_page.get(3) == "1"
