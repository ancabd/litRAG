def test_start_list_get_compare_delete(client, data_dir):
    assert client.get("/api/evals").json()["items"] == []
    r = client.post("/api/evals", json={"retriever": "bm25", "split": "dev"})
    assert r.status_code == 201, r.text
    first = r.json()["name"]
    assert first.endswith("_bm25_pymupdf_w400_o60_dev")

    items = client.get("/api/evals").json()["items"]
    assert [i["name"] for i in items] == [first]
    assert items[0]["n_scored"] == 1 and items[0]["headline"]["hit@1"]["strict"] == 1.0
    assert items[0]["headline"]["hit@1"]["lenient"] == 1.0 and items[0]["chunks"] == "pymupdf_w400_o60"

    run = client.get(f"/api/evals/{first}").json()
    q = run["questions"][0]
    assert q["id"] == "q001" and q["strict_rank"] == 1 and q["lenient_rank"] == 1
    top = q["retrieved"][0]
    assert top["label"]["kind"] == "evidence" and top["text"].startswith("We demonstrate")
    assert run["chunks_available"] and "## Overall" in run["report"]
    assert any(e["id"] == "q002" for e in run["summary"]["excluded"])  # unanswerable

    import time
    time.sleep(1.1)  # run folders are named by the second
    second = client.post("/api/evals", json={"split": "all"}).json()["name"]
    cmp = client.get("/api/evals/compare", params={"names": f"{first},{second}"}).json()
    assert [r["name"] for r in cmp["runs"]] == [first, second] and cmp["same_questions"]
    assert cmp["questions"][0]["id"] == "q001" and cmp["questions"][0]["per_run"][1]["strict_rank"] == 1
    assert "lenient_mrr" in cmp["runs"][0]["results"]
    pair = cmp["paired"][0]
    assert pair["base"] == first and pair["run"] == second
    assert pair["metrics"]["mrr"]["diff"] == 0 and pair["metrics"]["mrr"]["tied"] == pair["metrics"]["mrr"]["n"]

    assert client.delete(f"/api/evals/{first}").status_code == 200
    assert [i["name"] for i in client.get("/api/evals").json()["items"]] == [second]


def test_eval_errors(client, data_dir):
    assert client.post("/api/evals", json={"retriever": "nope"}).status_code == 400
    assert client.post("/api/evals", json={"split": "train"}).status_code == 400
    assert client.post("/api/evals", json={"chunks": "missing_run"}).status_code == 404
    assert client.get("/api/evals/nope").status_code == 404
    assert client.get("/api/evals/compare", params={"names": "a"}).status_code == 400
    assert client.delete("/api/evals/..").status_code in (404, 405)  # normalized away or refused
    assert client.delete("/api/evals/%2E%2E%2Fcorpus").status_code in (404, 405)
    assert (data_dir / "corpus" / "manifest.jsonl").exists()  # nothing outside runs/ can be deleted

    (data_dir / "questions" / "questions.yaml").write_text("- id: q1\n  question: x\n  type: lookp\n")
    r = client.post("/api/evals", json={})
    assert r.status_code == 422 and any("type must be one of" in e for e in r.json()["detail"]["errors"])


def test_cli_runs_show_up(client, data_dir):
    """A run made with evaluate.py in the terminal appears in the app."""
    from evaluation.runner import run_eval
    run_eval(data_dir / "questions" / "questions.yaml", data_dir / "chunks" / "pymupdf_w400_o60",
             out_root=data_dir / "runs", name="from_terminal")
    assert "from_terminal" in [i["name"] for i in client.get("/api/evals").json()["items"]]
