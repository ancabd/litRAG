"""Alternative evidence, strict vs lenient scoring, and judgment coverage."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluate import main as evaluate_main  # noqa: E402
from evaluation.matching import GoldIndex  # noqa: E402
from evaluation.metrics import question_metrics  # noqa: E402
from evaluation.questions import Evidence, QuestionFileError, parse_questions  # noqa: E402
from evaluation.runner import compare_runs, run_eval  # noqa: E402
from retrieval.base import Hit  # noqa: E402


def chunk(cid, paper, text):
    return {"chunk_id": cid, "paper_id": paper, "text": text, "section": "S", "title": f"Paper {paper}",
            "source": "pdf", "page_start": 1, "page_end": 1}


CHUNKS = [
    chunk("ORIG#000", "ORIG", "The total energy is expressed as a sum of atomic energy contributions from atomic networks."),
    chunk("CITE#000", "CITE", "Following earlier work, the total energy is written as a sum of atomic energies predicted by networks."),
    chunk("REV#000", "REV", "Reviews note that atomic energy decomposition is central to high dimensional neural network potentials."),
    chunk("WAT#000", "WAT", "Water models such as TIP3P are parameterized against experimental liquid properties."),
    chunk("B#000", "B", "Equivariant message passing uses tensor products of spherical harmonics on edges."),
]
PAPER = {c["chunk_id"]: c["paper_id"] for c in CHUNKS}


def test_parse_alternatives_and_not_relevant():
    qs = parse_questions([{
        "id": "q1", "question": "x?", "type": "lookup",
        "evidence": [{"paper": "ORIG", "quote": "sum of atomic energy contributions",
                      "alternatives": [{"paper": "CITE", "quote": "written as a sum of atomic energies"}]}],
        "not_relevant": [{"paper": "WAT", "quote": "Water models such as TIP3P"}],
    }])
    assert qs[0].evidence[0].alternatives[0].paper == "CITE" and qs[0].not_relevant[0].paper == "WAT"


@pytest.mark.parametrize("bad, msg", [
    ({"evidence": [{"paper": "A", "quote": "q", "alternatives": [{"paper": "B"}]}]}, "needs a 'paper' and a 'quote'"),
    ({"evidence": [{"paper": "A", "quote": "q", "alternatives": "B"}]}, "must be a list"),
    ({"evidence": [{"paper": "A", "quote": "q", "altrenatives": []}]}, "unknown field"),
    ({"evidence": [{"paper": "A", "quote": "q"}], "not_relevant": [{"paper": "B", "quote": "x", "why": "y"}]}, "unknown field"),
])
def test_bad_alternatives_rejected(bad, msg):
    with pytest.raises(QuestionFileError, match=msg):
        parse_questions([{"id": "q1", "question": "x?", "type": "lookup", **bad}])


def test_strict_vs_lenient_metrics():
    g = GoldIndex(CHUNKS)
    ev = [g.resolve(Evidence("ORIG", "sum of atomic energy contributions",
                             [Evidence("CITE", "written as a sum of atomic energies"),
                              Evidence("REV", "this quote is in no chunk at all anywhere")]))]
    assert ev[0].gold_chunks == {"ORIG#000"} and ev[0].alt_chunks == {"CITE#000"}
    assert len(ev[0].unresolved_alternatives) == 1
    hits = [Hit("CITE#000", 3, 1), Hit("WAT#000", 2, 2), Hit("ORIG#000", 1, 3)]
    strict = question_metrics(hits, PAPER, ev, ks=(1, 3))
    lenient = question_metrics(hits, PAPER, ev, ks=(1, 3), lenient=True)
    assert strict["hit@1"] == 0 and strict["hit@3"] == 1 and strict["mrr"] == pytest.approx(1 / 3)
    assert lenient["hit@1"] == 1 and lenient["mrr"] == 1.0
    assert strict["paper_hit@1"] == 0 and lenient["paper_hit@1"] == 1


def test_alternatives_belong_to_their_evidence_item():
    """Two-part question: an alternative for part A must not satisfy part B."""
    g = GoldIndex(CHUNKS)
    ev = [g.resolve(Evidence("ORIG", "sum of atomic energy contributions",
                             [Evidence("CITE", "written as a sum of atomic energies")])),
          g.resolve(Evidence("B", "tensor products of spherical harmonics"))]
    hits = [Hit("CITE#000", 2, 1), Hit("WAT#000", 1, 2)]
    m = question_metrics(hits, PAPER, ev, ks=(2,), lenient=True)
    assert m["recall@2"] == 0.5 and m["hit@2"] == 1


def test_runner_reports_both_and_judged(tmp_path):
    cdir = tmp_path / "chunks" / "run"
    cdir.mkdir(parents=True)
    (cdir / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    q = tmp_path / "q.yaml"
    q.write_text("""
- id: q1
  question: how is the total energy written as a sum of atomic energies
  type: lookup
  evidence:
    - paper: ORIG
      quote: sum of atomic energy contributions
      alternatives:
        - {paper: CITE, quote: written as a sum of atomic energies}
        - {paper: REV, quote: not a real quote from anywhere in the corpus}
  not_relevant:
    - {paper: WAT, quote: Water models such as TIP3P}
""")
    run_dir = run_eval(q, cdir, ks=(1, 10), out_root=tmp_path / "runs", name="r")
    s = json.loads((run_dir / "summary.json").read_text())["results"]["all"]
    assert s["lenient_hit@1"]["mean"] >= s["hit@1"]["mean"]
    assert 0 < s["judged@10"]["mean"] <= 1
    report = (run_dir / "report.md").read_text()
    assert "| metric | strict | lenient |" in report and "judged@10" in report
    assert "alternative didn't match any chunk" in report
    row = json.loads((run_dir / "per_question.jsonl").read_text().splitlines()[0])
    assert row["evidence"][0]["alt_chunks"] == ["CITE#000"] and row["not_relevant_chunks"] == ["WAT#000"]
    assert "lenient_mrr" in compare_runs([run_dir])


def test_check_flags_broken_alternatives(tmp_path, capsys):
    cdir = tmp_path / "chunks"
    cdir.mkdir()
    (cdir / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    q = tmp_path / "q.yaml"
    q.write_text("""
- id: q1
  question: x
  type: lookup
  evidence:
    - paper: ORIG
      quote: sum of atomic energy contributions
      alternatives: [{paper: CITE, quote: a quote that does not exist in that paper}]
""")
    assert evaluate_main(["check", "--questions", str(q), "--chunks", str(cdir)]) == 1
    assert "alternative not found" in capsys.readouterr().out
