import json

import yaml

EXTRA = [  # a citing paper restating W1's result, and an off-topic passage
    {"chunk_id": "W4#000", "paper_id": "W4", "index": 0, "section": "Introduction", "page_start": 1, "page_end": 1,
     "source": "pdf", "n_words": 20, "title": "A later paper", "year": 2015,
     "text": "Earlier work tested the neural network potential on bulk silicon as the material of choice, comparing it against density functional theory energies with good agreement."},
    {"chunk_id": "W5#000", "paper_id": "W5", "index": 0, "section": "Methods", "page_start": 1, "page_end": 1,
     "source": "pdf", "n_words": 12, "title": "Off topic", "year": 2019,
     "text": "Silicon wafers were cleaned before the material deposition experiment in the lab."},
]


def add_chunks(data_dir):
    f = data_dir / "chunks" / "pymupdf_w400_o60" / "chunks.jsonl"
    f.write_text(f.read_text() + "\n" + "\n".join(json.dumps(c) for c in EXTRA))


def test_review_and_judge_roundtrip(client, data_dir):
    add_chunks(data_dir)
    r = client.get("/api/questions/q001/review", params={"k": 10}).json()
    kinds = {i["chunk_id"]: i["judgment"]["kind"] for i in r["items"]}
    assert kinds["W1#000"] == "evidence" and kinds["W4#000"] == "unjudged" and kinds["W5#000"] == "unjudged"
    assert r["judged"] == 1 and r["evidence"][0]["paper"] == "W1"
    v = r["version"]

    j = client.post("/api/questions/q001/judge", json={"chunk_id": "W4#000", "kind": "alternative", "item": 0, "version": v})
    assert j.status_code == 200, j.text
    assert j.json()["judgment"] == {"kind": "alternative", "item": 0}
    v = j.json()["version"]
    j = client.post("/api/questions/q001/judge", json={"chunk_id": "W5#000", "kind": "not_relevant", "version": v})
    v = j.json()["version"]

    saved = yaml.safe_load((data_dir / "questions" / "questions.yaml").read_text())[0]
    alt = saved["evidence"][0]["alternatives"][0]
    assert alt["paper"] == "W4" and "bulk silicon" in alt["quote"]
    assert saved["not_relevant"][0]["paper"] == "W5"

    kinds = {i["chunk_id"]: i["judgment"]["kind"] for i in client.get("/api/questions/q001/review").json()["items"]}
    assert kinds["W4#000"] == "alternative" and kinds["W5#000"] == "not_relevant"

    # changing your mind moves the passage, it never ends up in two places
    j = client.post("/api/questions/q001/judge", json={"chunk_id": "W4#000", "kind": "not_relevant", "version": v})
    v = j.json()["version"]
    saved = yaml.safe_load((data_dir / "questions" / "questions.yaml").read_text())[0]
    assert "alternatives" not in saved["evidence"][0] and len(saved["not_relevant"]) == 2
    j = client.post("/api/questions/q001/judge", json={"chunk_id": "W4#000", "kind": "clear", "version": v})
    saved = yaml.safe_load((data_dir / "questions" / "questions.yaml").read_text())[0]
    assert [p["paper"] for p in saved["not_relevant"]] == ["W5"]

    # the core eval reads the same file and scores lenient >= strict
    from evaluation.questions import load_questions
    assert load_questions(data_dir / "questions" / "questions.yaml")[0].not_relevant[0].paper == "W5"


def test_editor_save_keeps_judgments(client, data_dir):
    add_chunks(data_dir)
    v = client.get("/api/questions").json()["version"]
    v = client.post("/api/questions/q001/judge", json={"chunk_id": "W4#000", "kind": "alternative", "version": v}).json()["version"]
    q = client.get("/api/questions/q001").json()["item"]
    q["answer"] = "Bulk silicon."
    r = client.put("/api/questions/q001", json={"question": q, "version": v})
    assert r.status_code == 200, r.text
    saved = yaml.safe_load((data_dir / "questions" / "questions.yaml").read_text())[0]
    assert saved["answer"] == "Bulk silicon." and saved["evidence"][0]["alternatives"][0]["paper"] == "W4"
    assert "title" not in saved["evidence"][0]  # display-only fields are never written


def test_judge_errors(client, data_dir):
    add_chunks(data_dir)
    v = client.get("/api/questions").json()["version"]
    own = client.post("/api/questions/q001/judge", json={"chunk_id": "W1#000", "kind": "not_relevant", "version": v})
    assert own.status_code == 400 and "already the question's own evidence" in own.json()["detail"]
    assert client.post("/api/questions/q001/judge", json={"chunk_id": "W4#000", "kind": "alternative", "item": 3,
                                                          "version": v}).status_code == 400
    assert client.post("/api/questions/q001/judge", json={"chunk_id": "nope", "kind": "clear", "version": v}).status_code == 404
    assert client.post("/api/questions/q001/judge", json={"chunk_id": "W4#000", "kind": "clear", "version": "stale"}).status_code == 409


def test_status_flags_broken_alternative(client, data_dir):
    v = client.get("/api/questions").json()["version"]
    q = client.get("/api/questions/q001").json()["item"]
    q["evidence"][0]["alternatives"] = [{"paper": "W2", "quote": "a quote that matches nothing in that paper"}]
    v = client.put("/api/questions/q001", json={"question": q, "version": v}).json()["version"]
    st = client.get("/api/questions").json()["items"][0]["evidence_status"]
    assert st["status"] == "problem" and st["items"][0]["alternatives"][0]["status"] == "not_found"


def test_pooled_review_merges_retrievers(client, data_dir, monkeypatch):
    import time
    from app.routers import questions as qr
    from retrieval import dense
    add_chunks(data_dir)
    # without built embeddings, the pool is BM25 only and says what it skipped
    r = client.get("/api/questions/q001/review", params={"retriever": "pool", "k": 3}).json()
    assert r["retrievers"] == ["bm25"] and {s["name"] for s in r["skipped"]} == {"dense:bge-small", "hybrid:bge-small"}
    assert all(set(i["found_by"]) == {"bm25"} for i in r["items"])

    # with the stand-in model built, dense and hybrid join the pool
    monkeypatch.setattr(qr, "retriever_choices", lambda: [{"name": "bm25", "label": "BM25"},
                                                          {"name": "dense:hash", "label": "Dense"},
                                                          {"name": "hybrid:hash", "label": "Hybrid"}])
    job = client.post("/api/indexes", json={"model": "hash"}).json()["job"]
    for _ in range(200):
        if client.get(f"/api/jobs/{job['id']}").json()["state"] != "running":
            break
        time.sleep(0.02)
    monkeypatch.setattr(dense, "installed", lambda: True)
    r = client.get("/api/questions/q001/review", params={"retriever": "pool", "k": 10}).json()
    assert r["retrievers"] == ["bm25", "dense:hash", "hybrid:hash"] and r["skipped"] == []
    w1 = next(i for i in r["items"] if i["chunk_id"] == "W1#000")
    assert len(w1["found_by"]) >= 2 and w1["judgment"]["kind"] == "evidence"
    best = [min(i["found_by"].values()) for i in r["items"]]
    assert best == sorted(best)  # ordered by each passage's best rank in any retriever
    assert len(r["items"]) <= 30 and [i["rank"] for i in r["items"]] == list(range(1, len(r["items"]) + 1))
    assert client.get("/api/questions/q001/review", params={"retriever": "nope"}).status_code == 400
