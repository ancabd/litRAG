"""Dense and hybrid retrievers through the API (the hash preset stands in for a real model)."""
import sys


def test_meta_lists_retriever_choices(client):
    meta = client.get("/api/meta").json()
    names = [c["name"] for c in meta["retriever_choices"]]
    assert names == ["bm25", "dense:bge-small", "hybrid:bge-small"] and meta["retrievers"] == names


def test_search_with_dense_and_hybrid(client, data_dir):
    for name in ("dense:hash", "hybrid:hash"):
        r = client.get("/api/search", params={"q": "bulk silicon test system", "retriever": name})
        assert r.status_code == 200, r.text
        assert r.json()["items"][0]["chunk_id"] == "W1#000"
    emb = list(data_dir.rglob("embeddings/hash/vectors.npy"))
    assert emb, "embeddings are cached in the chunk run folder"
    assert client.get("/api/search", params={"q": "x", "retriever": "dense:nope"}).status_code == 400


def test_missing_dense_package_is_a_503_with_instructions(client, monkeypatch):
    from retrieval import dense
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    monkeypatch.setattr(dense.SentenceTransformerEmbedder, "_cache", {})
    r = client.get("/api/search", params={"q": "silicon", "retriever": "dense:bge-small"})
    assert r.status_code == 503 and "requirements-dense.txt" in r.json()["detail"]["message"]


def wait_job(client, job_id, tries=200):
    import time
    for _ in range(tries):
        j = client.get(f"/api/jobs/{job_id}").json()
        if j["state"] != "running":
            return j
        time.sleep(0.02)
    raise AssertionError("job did not finish")


def test_index_status_and_build_with_progress(client, monkeypatch):
    from retrieval import dense
    st = client.get("/api/indexes").json()
    assert [m["model"] for m in st["models"]] == ["bge-small"]
    assert all(not m["ready"] and m["embedded"] == 0 and m["chunks"] > 0 for m in st["models"])

    monkeypatch.setattr(dense, "installed", lambda: False)
    r = client.post("/api/indexes", json={"model": "bge-small"})
    assert r.status_code == 503 and "requirements-dense.txt" in r.json()["detail"]["message"]
    assert client.post("/api/indexes", json={"model": "nope"}).status_code == 400

    r = client.post("/api/indexes", json={"model": "hash"})  # the stand-in model needs no packages
    assert r.status_code == 201, r.text
    job = wait_job(client, r.json()["job"]["id"])
    assert job["state"] == "done" and job["result"]["embedded_now"] == job["result"]["chunks"]
    assert job["total"] == job["result"]["chunks"] and job["meta"] == {"run": job["result"]["run"], "model": "hash"}
    # the built retriever is reused by searches right away
    assert client.get("/api/search", params={"q": "silicon", "retriever": "dense:hash"}).status_code == 200
