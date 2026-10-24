"""Generation and answer eval, with a scripted LLM (no network)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluate import main as evaluate_main  # noqa: E402
from evaluation.answer_runner import run_answer_eval  # noqa: E402
from evaluation.judge import Judge, agreement, cohen_kappa  # noqa: E402
from generation.answer import ExtractiveGenerator, LLMGenerator, answer_question, extract_citations  # noqa: E402
from generation.llm import CachedLLM, LLMNotConfigured, LLMResponse, ScriptedLLM, make_llm, parse_json  # noqa: E402
from library import Library  # noqa: E402


def chunk(cid, paper, text, title="Paper"):
    return {"chunk_id": cid, "paper_id": paper, "text": text, "section": "S", "title": title, "year": 2020,
            "source": "pdf", "page_start": 1, "page_end": 1}


CHUNKS = [
    chunk("BP#000", "BP", "The method is demonstrated for bulk silicon and compared with DFT calculations.", "Behler"),
    chunk("BP#001", "BP", "The total energy is a sum of atomic energy contributions.", "Behler"),
    chunk("NQ#000", "NQ", "NequIP uses equivariant convolutions on geometric tensors.", "NequIP"),
]
BY_ID = {c["chunk_id"]: c for c in CHUNKS}


def library():
    return Library(CHUNKS, name="test")


# ------------------------------------------------------------------ parsing helpers

def test_extract_citations():
    text = "Silicon [BP#000]. Energy sum [BP#001; NQ#000] and again [BP#000], see [Fig. 2] or [12]."
    assert extract_citations(text) == ["BP#000", "BP#001", "NQ#000"]
    assert extract_citations("[W2025444507#003][W4225405705#010]") == ["W2025444507#003", "W4225405705#010"]


def test_parse_json_tolerates_fences_and_prose():
    assert parse_json('```json\n{"a": 1, "b": "x {y}"}\n```') == {"a": 1, "b": "x {y}"}
    assert parse_json('Sure! {"verdict": "correct", "reason": "ok"} Hope that helps.')["verdict"] == "correct"
    assert parse_json("no json here") is None


def test_missing_key_is_reported(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMNotConfigured, match="ANTHROPIC_API_KEY"):
        make_llm("claude-sonnet-5-5")


# ------------------------------------------------------------------ generators

def test_llm_generator_validates_citations():
    llm = ScriptedLLM(lambda s, p: '{"answerable": true, "answer": "Bulk silicon [BP#000], see also [XX#999]."}')
    ans = answer_question("What test system demonstrated the method?", library(), LLMGenerator(llm), k=2)
    assert ans.answerable and ans.citations == ["BP#000"] and ans.invalid_citations == ["XX#999"]
    assert any("not provided" in w for w in ans.warnings)
    system, prompt = llm.calls[0]
    assert "Use only information stated in the passages" in system
    assert "[BP#000] Behler (2020) - S, p. 1" in prompt and "Question: What test system demonstrated" in prompt
    assert ans.prompt_version == "answer-v1" and ans.passages[0]["chunk_id"] == "BP#000"


def test_llm_generator_abstains_and_survives_bad_json():
    ans = answer_question("x?", library(),
                          LLMGenerator(ScriptedLLM(lambda s, p: '{"answerable": false, "answer": "Not in these passages."}')))
    assert not ans.answerable
    ans = answer_question("Where was the method demonstrated?", library(),
                          LLMGenerator(ScriptedLLM(lambda s, p: "Bulk silicon [BP#000].")))
    assert ans.answerable and ans.citations == ["BP#000"] and "expected JSON" in ans.warnings[0]


def test_extractive_baseline():
    ans = answer_question("Which test system demonstrated the method, bulk silicon?", library(),
                          ExtractiveGenerator())
    assert ans.answerable and ans.answer.endswith("[BP#000]") and ans.citations == ["BP#000"]
    none = answer_question("zebra giraffe", library(), ExtractiveGenerator())
    assert not none.answerable


def test_cache_makes_repeat_calls_free(tmp_path):
    inner = ScriptedLLM(lambda s, p: "hello", model="claude-haiku-5-5")
    llm = CachedLLM(inner, tmp_path)
    first, second = llm.complete("s", "p"), llm.complete("s", "p")
    assert first.text == second.text == "hello" and len(inner.calls) == 1
    assert not first.cached and second.cached and second.cost == 0.0
    llm.complete("s", "different prompt")
    assert len(inner.calls) == 2
    assert LLMResponse("x", "claude-sonnet-5-5", 1_000_000, 100_000).cost == pytest.approx(3.0)


# ------------------------------------------------------------------ judge

def test_judge_parses_and_rejects_garbage():
    j = Judge(ScriptedLLM(lambda s, p: '{"verdict": "Partial", "reason": "misses DFT"}'))
    assert j.correctness("q", "ref", "ans") == {"verdict": "partial", "score": 0.5, "reason": "misses DFT"}
    assert j.support("ans", []) == {"verdict": "unsupported", "score": 0.0, "reason": "no passages cited"}
    bad = Judge(ScriptedLLM(lambda s, p: "I think it's fine"))
    assert bad.correctness("q", "r", "a")["verdict"] is None


def test_agreement_and_kappa():
    assert cohen_kappa(["a", "b", "a"], ["a", "b", "a"]) == 1.0
    rows = [{"id": f"q{i}", "judgments": {"correctness": {"verdict": v}}} for i, v in
            enumerate(["correct", "partial", "incorrect", "correct"])]
    human = {"q0": {"correctness": "correct"}, "q1": {"correctness": "incorrect"}, "q2": {"correctness": "incorrect"}}
    a = agreement(rows, human)
    assert a["n"] == 3 and a["agreement"] == pytest.approx(2 / 3) and a["disagreements"] == ["q1"]
    assert agreement(rows, {})["n"] == 0


# ------------------------------------------------------------------ answer eval

QUESTIONS = """
- id: q1
  question: Which material was used to demonstrate the Behler potential?
  type: lookup
  answer: Bulk silicon, compared with DFT.
  evidence: [{paper: BP, quote: "demonstrated for bulk silicon"}]
- id: q2
  question: How is the total energy written?
  type: lookup
  answer: As a sum of atomic energy contributions.
  evidence: [{paper: BP, quote: "total energy is a sum of atomic energy contributions"}]
- id: q3
  question: What hit rate does RFdiffusion reach?
  type: unanswerable
- id: q4
  question: What does NequIP use?
  type: lookup
  evidence: [{paper: NQ, quote: "equivariant convolutions on geometric tensors"}]
"""


def scripted(system, prompt):
    """Answers: q1 correct, q2 wrong and uncited, q3 abstains, q4 answers. Judge: compares keywords."""
    if "grade answers" in system:
        return '{"verdict": "correct", "reason": "matches"}' if "silicon" in prompt.split("Answer to grade:")[1] \
            else '{"verdict": "incorrect", "reason": "wrong"}'
    if "check whether an answer is supported" in system:
        return '{"verdict": "supported", "reason": "ok"}'
    if "RFdiffusion" in prompt:
        return '{"answerable": false, "answer": "The passages do not cover this."}'
    if "Behler potential" in prompt:
        return '{"answerable": true, "answer": "Bulk silicon [BP#000]."}'
    if "total energy" in prompt:
        return '{"answerable": true, "answer": "As a product of pair terms."}'
    return '{"answerable": true, "answer": "Equivariant convolutions [NQ#000]."}'


@pytest.fixture
def setup(tmp_path):
    cdir = tmp_path / "chunks" / "run"
    cdir.mkdir(parents=True)
    (cdir / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    q = tmp_path / "q.yaml"
    q.write_text(QUESTIONS)
    return q, cdir


def test_answer_eval_end_to_end(setup, tmp_path):
    qfile, cdir = setup
    llm = ScriptedLLM(scripted, model="claude-sonnet-5-5")
    run_dir = run_answer_eval(qfile, cdir, LLMGenerator(llm), Judge(llm), k=2, out_root=tmp_path / "runs",
                              name="ans", split=None)
    s = json.loads((run_dir / "summary.json").read_text())
    a = s["results"]["all"]
    assert s["kind"] == "answer" and s["n_scored"] == 4 and s["no_reference_answer"] == ["q4"]
    assert a["correct"]["mean"] == 0.5 and a["correct"]["n"] == 2              # q1 right, q2 wrong, q4 unjudged
    assert a["abstained_when_unanswerable"]["mean"] == 1.0
    assert a["abstained_when_answerable"]["mean"] == 0.0
    assert a["cites_gold"]["mean"] == pytest.approx(2 / 3)                     # q1, q4 cite gold; q2 cites nothing
    assert a["supported"]["n"] == 3                                            # q2 judged unsupported without a call
    assert s["usage"]["generator"]["cost"] > 0 and s["judge"]["prompt"] == "judge-v1"
    rows = {json.loads(l)["id"]: json.loads(l) for l in (run_dir / "per_question.jsonl").read_text().splitlines()}
    assert rows["q2"]["judgments"]["support"]["reason"] == "no passages cited"
    assert "retrieval:found" in rows["q1"]["groups"]
    report = (run_dir / "report.md").read_text()
    assert "Correct (judge vs your reference)" in report and "Bulk silicon [BP#000]" in report


def test_answer_eval_without_judge(setup, tmp_path):
    qfile, cdir = setup
    run_dir = run_answer_eval(qfile, cdir, ExtractiveGenerator(), None, k=3, out_root=tmp_path / "runs",
                              name="ext", split=None)
    a = json.loads((run_dir / "summary.json").read_text())["results"]["all"]
    assert "correct" not in a and "supported" not in a and "cites_gold" in a and "retrieved_gold" in a


def test_cli_answer_and_ask_extractive(setup, tmp_path, capsys):
    qfile, cdir = setup
    assert evaluate_main(["answer", "--questions", str(qfile), "--chunks", str(cdir), "--generator", "extractive",
                          "--judge", "none", "--split", "all", "--out", str(tmp_path / "runs"), "--name", "cli"]) == 0
    assert "# Answer eval: extractive" in capsys.readouterr().out
    assert evaluate_main(["ask", "Which bulk silicon test system demonstrated the method?", "--chunks", str(cdir),
                          "--generator", "extractive"]) == 0
    out = capsys.readouterr().out
    assert "bulk silicon" in out and "Sources:" in out and "[BP#000]" in out
