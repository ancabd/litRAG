import yaml


def test_meta(client):
    m = client.get("/api/meta").json()
    assert m["corpus"]["papers"] == 3 and m["corpus"]["status_counts"]["pdf"] == 1
    assert m["default_run"] == "pymupdf_w400_o60" and m["runs"][0]["parser"] == "pymupdf@2"
    assert "bm25" in m["retrievers"] and m["questions"]["tags"] == ["bp"]
    assert [s["openalex_id"] for s in m["corpus"]["seeds"]] == ["W1", "W2"]


def test_papers_list_filter_sort_paginate(client):
    r = client.get("/api/papers").json()
    assert r["total"] == 3 and [p["openalex_id"] for p in r["items"]] == ["W1", "W2", "W3"]
    assert r["items"][0]["n_chunks"] == 2 and r["items"][2]["n_chunks"] == 0
    assert client.get("/api/papers", params={"q": "equivariant"}).json()["total"] == 1
    assert client.get("/api/papers", params={"q": "behler 2007"}).json()["total"] == 1   # all terms must match
    assert client.get("/api/papers", params={"status": "metadata_only"}).json()["items"][0]["openalex_id"] == "W3"
    assert client.get("/api/papers", params={"role": "seed"}).json()["total"] == 2
    assert client.get("/api/papers", params={"seed": "W1"}).json()["total"] == 2
    assert client.get("/api/papers", params={"sort": "year"}).json()["items"][0]["openalex_id"] == "W2"
    page = client.get("/api/papers", params={"limit": 1, "offset": 1}).json()
    assert page["total"] == 3 and [p["openalex_id"] for p in page["items"]] == ["W2"]


def test_paper_detail_chunks_and_pdf(client):
    d = client.get("/api/papers/W1").json()
    assert d["pdf_available"] and d["n_chunks"] == 2 and d["questions"][0]["id"] == "q001"
    assert d["seeds"] == [{"openalex_id": "W1", "title": d["title"]}]
    assert client.get("/api/papers/W2").json()["pdf_available"] is False
    assert len(client.get("/api/papers/W1/chunks").json()["items"]) == 2
    pdf = client.get("/api/papers/W1/pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    assert client.get("/api/papers/W2/pdf").status_code == 404
    assert client.get("/api/papers/..%2F..%2Fetc%2Fpasswd/pdf").status_code == 404
    assert client.get("/api/papers/W999").status_code == 404


def test_search(client):
    r = client.get("/api/search", params={"q": "silicon"}).json()
    assert r["items"][0]["chunk_id"] == "W1#000" and r["items"][0]["title"].startswith("Generalized")
    within = client.get("/api/search", params={"q": "cutoff", "paper": "W2"}).json()
    assert within["items"] == []
    assert client.get("/api/search", params={"q": "x", "run": "nope"}).status_code == 404
    assert client.get("/api/search", params={"q": "x", "retriever": "nope"}).status_code == 400


def test_evidence_check_with_highlights(client):
    ok = client.post("/api/evidence/check", json={"paper": "W1", "quote": "decays smoothly to zero"}).json()
    assert ok["status"] == "ok" and ok["gold"][0]["chunk_id"] == "W1#001"
    text = ok["gold"][0]["text"]
    assert [text[s:e] for s, e in ok["gold"][0]["highlights"]] == ["decays smoothly to zero"]
    bad = client.post("/api/evidence/check", json={"paper": "W1", "quote": "cutoff radius Rc with a sine"}).json()
    assert bad["status"] == "not_found" and bad["closest"][0]["chunk_id"] == "W1#001"
    assert client.post("/api/evidence/check", json={"paper": "W3", "quote": "x"}).json()["status"] == "paper_missing"
    assert client.post("/api/evidence/check", json={"paper": "W1"}).json()["status"] == "no_quote"


def test_questions_crud_roundtrip(client, data_dir):
    path = data_dir / "questions" / "questions.yaml"
    lst = client.get("/api/questions").json()
    assert [q["id"] for q in lst["items"]] == ["q001", "q002"] and lst["errors"] == []
    assert lst["items"][0]["evidence_status"]["status"] == "ok"
    assert lst["items"][0]["evidence"][0]["title"].startswith("Generalized")
    assert lst["items"][1]["evidence_status"]["status"] == "none"
    v = lst["version"]

    new = {"question": "How does the cutoff function behave?", "type": "lookup", "tags": ["equation", " "],
           "evidence": [{"paper": "W1", "quote": "decays   smoothly to zero"}], "answer": "  "}
    r = client.post("/api/questions", json={"question": new, "version": v})
    assert r.status_code == 201, r.text
    created, v = r.json()["item"], r.json()["version"]
    assert created["id"] == "q003" and created["tags"] == ["equation"] and "answer" not in created
    assert created["evidence"][0]["quote"] == "decays smoothly to zero"

    upd = {**new, "question": "How does the cutoff behave at Rc?", "id": "SHOULD_BE_IGNORED"}
    r = client.put("/api/questions/q003", json={"question": upd, "version": v})
    assert r.status_code == 200 and r.json()["item"]["id"] == "q003"
    v = r.json()["version"]

    r = client.delete("/api/questions/q002", params={"version": v})
    assert r.status_code == 200
    v = r.json()["version"]

    text = path.read_text()
    assert text.startswith("# Header comment that must survive edits.\n# Second header line.\n\n- id: q001")
    data = yaml.safe_load(text)
    assert [q["id"] for q in data] == ["q001", "q003"] and data[1]["question"] == "How does the cutoff behave at Rc?"
    assert client.get("/api/questions").json()["version"] == v

    # the core CLI loader accepts what the UI wrote
    from evaluation.questions import load_questions
    assert [q.id for q in load_questions(path)] == ["q001", "q003"]


def test_validation_errors_are_reported_and_nothing_written(client, data_dir):
    path = data_dir / "questions" / "questions.yaml"
    before = path.read_text()
    v = client.get("/api/questions").json()["version"]
    bad = {"question": "Compare two things", "type": "comparison", "evidence": [{"paper": "W1", "quote": "x"}]}
    r = client.post("/api/questions", json={"question": bad, "version": v})
    assert r.status_code == 422 and any("at least two places" in e for e in r.json()["detail"]["errors"])
    r = client.post("/api/questions", json={"question": {"question": "", "type": "lookup"}, "version": v})
    assert r.status_code == 422
    assert path.read_text() == before


def test_version_conflict_when_file_edited_elsewhere(client, data_dir):
    path = data_dir / "questions" / "questions.yaml"
    v = client.get("/api/questions").json()["version"]
    path.write_text(path.read_text() + "\n# edited in a text editor\n")
    r = client.put("/api/questions/q001", json={"question": {"question": "x", "type": "unanswerable"}, "version": v})
    assert r.status_code == 409 and "changed outside the app" in r.json()["detail"]["message"]
    assert "edited in a text editor" in path.read_text()
    assert client.delete("/api/questions/q001", params={"version": v}).status_code == 409
    assert client.put("/api/questions/q999", json={"question": {"question": "x", "type": "unanswerable"},
                                                   "version": client.get("/api/questions").json()["version"]}
                      ).status_code == 404


def test_invalid_file_is_still_listed(client, data_dir):
    path = data_dir / "questions" / "questions.yaml"
    path.write_text("- id: q1\n  question: typo in type\n  type: lookp\n")
    r = client.get("/api/questions").json()
    assert r["items"][0]["id"] == "q1" and any("type must be one of" in e for e in r["errors"])


def test_spa_fallback_without_build(client):
    r = client.get("/questions/q001")
    assert r.status_code == 200 and "isn't built yet" in r.text
    assert client.get("/api/nope").status_code == 404
