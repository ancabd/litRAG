import time

import pytest


def wait(client, job_id, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        j = client.get(f"/api/jobs/{job_id}").json()
        if j["state"] != "running":
            return j
        time.sleep(0.05)
    raise AssertionError("job did not finish")


def test_llm_status(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    s = client.get("/api/llm").json()
    assert s["configured"] is False and "extractive" in s["generators"] and s["default_model"] == "claude-sonnet-5-5"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert client.get("/api/llm").json()["configured"] is True


def test_ask_extractive_and_missing_key(client, monkeypatch):
    r = client.post("/api/ask", json={"question": "Which material was used, bulk silicon?", "generator": "extractive"})
    assert r.status_code == 200, r.text
    a = r.json()
    assert a["answerable"] and a["citations"] == ["W1#000"]
    assert a["passages"][0]["cited_as"] == 1 and a["passages"][0]["title"].startswith("Generalized")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = client.post("/api/ask", json={"question": "Which material was used?", "generator": "claude"})
    assert r.status_code == 503 and r.json()["detail"]["code"] == "llm_not_configured"
    assert client.post("/api/ask", json={"question": "x"}).status_code == 422


@pytest.fixture
def scripted(client, monkeypatch):
    """Route the 'claude' generator and the judge to a scripted model."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "corpus-builder"))
    from evaluation.judge import Judge
    from generation.answer import LLMGenerator
    from generation.llm import ScriptedLLM

    def respond(system, prompt):
        if "grade answers" in system:
            return '{"verdict": "correct", "reason": "names silicon"}'
        if "supported by the passages" in system:
            return '{"verdict": "supported", "reason": "ok"}'
        if "RFdiffusion" in prompt:
            return '{"answerable": false, "answer": "Not in the passages."}'
        return '{"answerable": true, "answer": "Bulk silicon [W1#000]."}'

    llm = ScriptedLLM(respond, model="claude-sonnet-5-5")
    svc = client.app.state.services
    monkeypatch.setattr(svc.answering, "generator", lambda name, model: LLMGenerator(llm))
    monkeypatch.setattr(svc.answering, "judge", lambda model: None if model == "none" else Judge(llm))
    return llm


def test_ask_with_llm(client, scripted):
    a = client.post("/api/ask", json={"question": "Which material was used to test the potential?"}).json()
    assert a["answer"] == "Bulk silicon [W1#000]." and a["generator"]["model"] == "claude-sonnet-5-5"


def test_answer_eval_job_verdicts_and_agreement(client, scripted, data_dir):
    r = client.post("/api/evals", json={"kind": "answer", "split": "dev"})
    assert r.status_code == 201, r.text  # created; the run itself happens in the background job
    job = wait(client, r.json()["job"]["id"])
    assert job["state"] == "done", job
    name = job["result"]["name"]
    assert "_answers_claude-sonnet-5-5_bm25_" in name

    items = client.get("/api/evals").json()["items"]
    brief = next(i for i in items if i["name"] == name)
    assert brief["kind"] == "answer" and brief["headline"]["correct"]["strict"] == 1.0
    assert brief["headline"]["abstained_when_unanswerable"]["strict"] == 1.0

    run = client.get(f"/api/evals/{name}").json()
    q1 = next(q for q in run["questions"] if q["id"] == "q001")
    assert q1["answer"]["citations"] == ["W1#000"] and q1["judgments"]["correctness"]["verdict"] == "correct"
    assert q1["retrieved"][0]["label"]["kind"] == "evidence" and run["agreement"]["n"] == 0

    v = client.put(f"/api/evals/{name}/verdicts/q001", json={"verdict": "partial"}).json()
    assert v["human"] == {"correctness": "partial"} and v["agreement"]["n"] == 1 and v["agreement"]["agreement"] == 0
    assert (data_dir / "runs" / name / "human.json").exists()
    v = client.put(f"/api/evals/{name}/verdicts/q001", json={"verdict": "correct"}).json()
    assert v["agreement"]["agreement"] == 1.0
    assert client.put(f"/api/evals/{name}/verdicts/q001", json={"verdict": "great"}).status_code == 400
    v = client.put(f"/api/evals/{name}/verdicts/q001", json={"verdict": None}).json()
    assert v["human"] is None and v["agreement"]["n"] == 0


def test_answer_eval_extractive_no_judge_and_errors(client, monkeypatch):
    r = client.post("/api/evals", json={"kind": "answer", "generator": "extractive"})
    job = wait(client, r.json()["job"]["id"])
    assert job["state"] == "done"
    run = client.get(f"/api/evals/{job['result']['name']}").json()
    assert run["judge"] is None and "correct" not in run["headline"]

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = client.post("/api/evals", json={"kind": "answer", "generator": "claude"})
    assert r.status_code == 503
    assert client.post("/api/evals", json={"kind": "nonsense"}).status_code == 400
    assert client.get("/api/jobs/nope").status_code == 404
