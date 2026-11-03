import json


def ask(client, question="Which material was used to test the potential?"):
    r = client.post("/api/ask", json={"question": question, "generator": "extractive", "k": 3})
    assert r.status_code == 200, r.text
    return {**r.json(), "k": 3, "answerable": True}  # rate it as an answer, whatever the baseline decided


def test_rate_update_summarize_and_delete(client, data_dir):
    answer = ask(client)
    r = client.post("/api/feedback", json={"answer": answer, "rating": {"faithful": "yes", "complete": "partly"},
                                           "comment": "  misses the DFT comparison "})
    assert r.status_code == 200, r.text
    rec = r.json()
    assert rec["rating"] == {"faithful": "yes", "complete": "partly"} and rec["comment"] == "misses the DFT comparison"
    stored = rec["answer"]
    assert stored["question"] == answer["question"] and stored["k"] == 3 and stored["retriever"] == "bm25"
    assert stored["passages"] and "text" not in stored["passages"][0]  # ids, not texts

    # change your mind: same id, answer kept as first rated
    r = client.put(f"/api/feedback/{rec['id']}", json={"answer": {**answer, "answer": "changed"},
                                                       "rating": {"faithful": "no", "complete": "partly"}})
    assert r.status_code == 200 and r.json()["rating"]["faithful"] == "no"
    assert r.json()["answer"]["answer"] == answer["answer"] and r.json()["created"] == rec["created"]

    lines = (data_dir / "feedback" / "ratings.jsonl").read_text().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["rating"]["faithful"] == "no"

    body = client.get("/api/feedback").json()
    assert len(body["items"]) == 1
    s = body["summary"][0]
    assert s["label"] == "Extractive + BM25" and s["n"] == 1 and s["answered"] == 1
    assert s["faithful"] == {"yes": 0, "partly": 0, "no": 1, "n": 1, "score": 0.0}
    assert s["complete"]["score"] == 0.5

    assert client.delete(f"/api/feedback/{rec['id']}").status_code == 200
    assert client.get("/api/feedback").json()["items"] == []
    assert client.delete(f"/api/feedback/{rec['id']}").status_code == 404


def test_declines_are_rated_on_whether_to_answer(client):
    answer = ask(client)
    declined = {**answer, "answerable": False}
    r = client.post("/api/feedback", json={"answer": declined, "rating": {"should_have_answered": "yes", "faithful": "yes"}})
    assert r.status_code == 200
    assert r.json()["rating"] == {"should_have_answered": "yes"}  # faithfulness doesn't apply to a decline
    s = client.get("/api/feedback").json()["summary"][0]
    assert s["declined"] == 1 and s["should_have_answered"] == {"yes": 1, "no": 0} and s["faithful"]["score"] is None


def test_bad_ratings_are_refused(client):
    answer = ask(client)
    assert client.post("/api/feedback", json={"answer": answer, "rating": {}}).status_code == 400
    assert client.post("/api/feedback", json={"answer": answer, "rating": {"faithful": "mostly"}}).status_code == 400
    assert client.post("/api/feedback", json={"answer": {**answer, "question": ""},
                                              "rating": {"faithful": "yes"}}).status_code == 400
    assert client.put("/api/feedback/abcdefabcdef", json={"answer": answer, "rating": {"faithful": "yes"}}).status_code == 404


def test_setups_are_grouped_and_labelled(client):
    from app.services.feedback import setup_label
    assert setup_label({"method": "agent", "model": "claude-sonnet-5-5", "retriever": "hybrid:bge-small"}) == \
        "Agent (sonnet-5-5) + Hybrid (bge-small)"
    assert setup_label({"method": "claude", "model": "claude-haiku-5-5", "retriever": "dense:bge-small"}) == \
        "Single shot (haiku-5-5) + Dense (bge-small)"
    answer = ask(client)
    client.post("/api/feedback", json={"answer": answer, "rating": {"faithful": "yes"}})
    client.post("/api/feedback", json={"answer": {**answer, "retriever": "hybrid:bge-small"}, "rating": {"complete": "no"}})
    labels = {s["label"] for s in client.get("/api/feedback").json()["summary"]}
    assert labels == {"Extractive + BM25", "Extractive + Hybrid (bge-small)"}
