"""Tests for BM25, gold matching, metrics and the eval runner."""
import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluate import main as evaluate_main  # noqa: E402
from evaluation.matching import GoldIndex, quote_coverage  # noqa: E402
from evaluation.metrics import bootstrap_ci, question_metrics  # noqa: E402
from evaluation.questions import Evidence, QuestionFileError, load_questions  # noqa: E402
from evaluation.runner import compare_runs, run_eval  # noqa: E402
from retrieval import get_retriever  # noqa: E402
from retrieval.base import Hit  # noqa: E402
from retrieval.bm25 import tokenize  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def chunk(cid, paper, text, section="1 Intro", title="Some paper"):
    return {"chunk_id": cid, "paper_id": paper, "text": text, "section": section, "title": title,
            "year": 2020, "source": "pdf", "page_start": 1, "page_end": 1}


CHUNKS = [
    chunk("BP#000", "BP", "We demonstrate the method for bulk silicon, comparing energies with density functional theory.",
          title="Generalized neural-network representation"),
    chunk("BP#001", "BP", "The cutoff function decays smoothly to zero at the cutoff radius Rc, using a cosine form.",
          section="2 Method", title="Generalized neural-network representation"),
    chunk("BP#002", "BP", "Symmetry functions are invariant descriptors of the atomic environment under rotation.",
          section="2 Method", title="Generalized neural-network representation"),
    chunk("NQ#000", "NQ", "NequIP uses E(3)-equivariant convolutions acting on geometric tensors, unlike invariant models.",
          title="E(3)-equivariant graph neural networks"),
    chunk("NQ#001", "NQ", "We train on molecular dynamics data of small molecules and water with the TIP3P model.",
          title="E(3)-equivariant graph neural networks"),
    chunk("FF#000", "FF", "Polarizable force fields let the charge distribution respond to the environment.",
          title="The continuous evolution of biomolecular force fields", section="Abstract"),
]

QUESTIONS_YAML = """
- id: q1
  question: Which material was used to test the neural network potential?
  type: lookup
  tags: [bp]
  evidence: [{paper: BP, quote: "the method for bulk silicon, comparing energies"}]
- id: q2
  question: how does the cutoff function behave at the cutoff radius
  type: lookup
  tags: [bp, equation]
  evidence: [{paper: BP, quote: "decays smoothly to zero at the cutoff radius"}]
- id: q3
  question: compare equivariant NequIP features with invariant symmetry function descriptors
  type: comparison
  evidence:
    - {paper: BP, quote: "Symmetry functions are invariant descriptors of the atomic environment"}
    - {paper: NQ, quote: "E(3)-equivariant convolutions acting on geometric tensors"}
- id: q4
  question: What hit rate did RFdiffusion reach?
  type: unanswerable
- id: q5
  question: a question whose quote is wrong
  type: lookup
  evidence: [{paper: FF, quote: "this sentence does not appear anywhere in the corpus at all"}]
- id: q6
  question: held-out question about polarizable force fields
  type: lookup
  split: test
  evidence: [{paper: FF, quote: "charge distribution respond to the environment"}]
"""


@pytest.fixture
def setup(tmp_path):
    cdir = tmp_path / "chunks" / "pymupdf_w400_o60"
    cdir.mkdir(parents=True)
    (cdir / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    (cdir / "run.json").write_text(json.dumps({"parser": "pymupdf@2", "chunking": {"size": 400}}))
    q = tmp_path / "questions.yaml"
    q.write_text(QUESTIONS_YAML)
    return q, cdir


# ------------------------------------------------------------------ BM25

def test_tokenizer_keeps_scientific_terms():
    toks = tokenize("E(3)-equivariant NequIP with TIP3P water, ff14SB and DFT-D3; the SO(3) group.")
    for t in ["e(3)-equivariant", "e(3)", "equivariant", "nequip", "tip3p", "ff14sb", "dft-d3", "d3", "so(3)"]:
        assert t in toks, t
    assert "the" not in toks and "with" not in toks


def test_bm25_ranks_exact_terms():
    r = get_retriever("bm25")
    r.index(CHUNKS)
    assert r.search("TIP3P water model", k=3)[0].chunk_id == "NQ#001"
    assert r.search("silicon", k=3)[0].chunk_id == "BP#000"
    assert r.search("polarizable", k=3)[0].chunk_id == "FF#000"
    hits = r.search("cutoff radius cosine", k=10)
    assert hits[0].chunk_id == "BP#001" and [h.rank for h in hits] == list(range(1, len(hits) + 1))
    assert r.search("zzzunknownzzz", k=5) == []


def test_title_field_helps_and_can_be_disabled():
    with_title = get_retriever("bm25")
    with_title.index(CHUNKS)
    assert with_title.search("continuous evolution", k=1)[0].chunk_id == "FF#000"
    no_title = get_retriever("bm25", include_title=False)
    no_title.index(CHUNKS)
    assert no_title.search("continuous evolution", k=1) == []


# ------------------------------------------------------------------ matching

def test_quote_coverage_is_robust():
    text = "The cutoff function decays smoothly to zero at the cutoff radius Rc, using a cosine form."
    assert quote_coverage("decays smoothly to zero at the cutoff radius", text) == 1.0
    assert quote_coverage("Decays  smoothly, to ZERO at the cutoff-radius", text) == 1.0  # case, punctuation
    assert quote_coverage("decays smoothly to zero at the cutoff radius R_c defined above", text) > 0.5
    assert quote_coverage("something entirely different here", text) == 0.0
    assert quote_coverage("cosine", text) == 1.0 and quote_coverage("sine", text) == 0.0


def test_gold_index_resolves_and_reports():
    g = GoldIndex(CHUNKS)
    assert g.resolve(Evidence("BP", "invariant descriptors of the atomic environment")).gold_chunks == {"BP#002"}
    missing_paper = g.resolve(Evidence("XX", "anything"))
    assert not missing_paper.resolved and not missing_paper.paper_in_corpus
    assert not g.resolve(Evidence("BP", None)).resolved


# ------------------------------------------------------------------ metrics

def test_question_metrics_exact():
    g = GoldIndex(CHUNKS)
    ev = [g.resolve(Evidence("BP", "invariant descriptors of the atomic environment")),
          g.resolve(Evidence("NQ", "E(3)-equivariant convolutions acting on geometric tensors"))]
    paper = {c["chunk_id"]: c["paper_id"] for c in CHUNKS}
    hits = [Hit("FF#000", 3, 1), Hit("NQ#000", 2, 2), Hit("BP#000", 1.5, 3), Hit("BP#002", 1, 4)]
    m = question_metrics(hits, paper, ev, ks=(1, 3, 5))
    assert m["hit@1"] == 0 and m["hit@3"] == 1
    assert m["recall@3"] == 0.5 and m["recall@5"] == 1.0
    assert m["mrr"] == 0.5
    assert m["paper_hit@1"] == 0 and m["paper_hit@3"] == 1
    ideal = 1 + 1 / math.log2(3)
    assert m["ndcg@10"] == pytest.approx((1 / math.log2(3) + 1 / math.log2(5)) / ideal)


def test_bootstrap_ci_brackets_mean():
    mean, lo, hi = bootstrap_ci([1, 0, 1, 1, 0, 1, 1, 1, 0, 1])
    assert mean == 0.7 and lo < 0.7 < hi and 0 <= lo and hi <= 1
    assert bootstrap_ci([1.0]) == (1.0, 1.0, 1.0)


# ------------------------------------------------------------------ question file

def test_question_validation_catches_mistakes(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("""
- id: a
  question: x
  type: lookp
- id: a
  question: y
  type: comparison
  evidence: [{paper: P, quote: q}]
- id: c
  question: z
  type: unanswerable
  evidence: [{paper: P}]
  tgas: [typo]
""")
    with pytest.raises(QuestionFileError) as exc:
        load_questions(bad)
    msg = str(exc.value)
    assert "type must be one of" in msg and "duplicate id" in msg
    assert "at least two places" in msg and "must not have evidence" in msg and "unknown field" in msg


def test_shipped_template_is_valid():
    qs = load_questions(ROOT / "questions" / "questions.yaml")
    assert len(qs) >= 7 and {q.type for q in qs} == {"lookup", "comparison", "unanswerable"}
    assert sum("equation" in q.tags for q in qs) >= 2


# ------------------------------------------------------------------ runner + CLI

def test_run_eval_end_to_end(setup, tmp_path):
    qfile, cdir = setup
    run_dir = run_eval(qfile, cdir, "bm25", split="dev", ks=(1, 5, 10), out_root=tmp_path / "runs", name="r1")
    s = json.loads((run_dir / "summary.json").read_text())
    assert s["n_questions"] == 5 and s["n_scored"] == 3                    # q6 is test split
    reasons = {e["id"]: e["reason"] for e in s["excluded"]}
    assert "unanswerable" in reasons["q4"] and "no evidence quote" in reasons["q5"]
    assert s["results"]["all"]["hit@10"]["mean"] == 1.0
    assert s["results"]["type:comparison"]["recall@10"]["n"] == 1
    assert s["results"]["tag:equation"]["hit@1"]["mean"] == 1.0
    assert s["chunks_config"]["parser"] == "pymupdf@2" and s["retriever"]["name"] == "bm25"
    rows = [json.loads(l) for l in (run_dir / "per_question.jsonl").read_text().splitlines()]
    assert {r["id"] for r in rows} == {"q1", "q2", "q3"}
    report = (run_dir / "report.md").read_text()
    assert "| hit@10 |" in report and "tag:equation" in report and "q5 excluded" in report

    run2 = run_eval(qfile, cdir, "bm25", split="all", ks=(1, 5, 10), out_root=tmp_path / "runs", name="r2")
    table = compare_runs([run_dir, run2])
    assert "r1" in table and "r2" in table and "| mrr |" in table


def test_cli(setup, tmp_path, capsys):
    qfile, cdir = setup
    assert evaluate_main(["check", "--questions", str(qfile), "--chunks", str(cdir)]) == 1  # q5 is broken
    out = capsys.readouterr().out
    assert "!! q5" in out and "quote not found" in out and "Closest chunks" in out and "1 with evidence problems" in out
    assert evaluate_main(["search", "TIP3P", "--chunks", str(cdir), "-k", "2"]) == 0
    assert "NQ#001" in capsys.readouterr().out
    assert evaluate_main(["run", "--questions", str(qfile), "--chunks", str(cdir),
                          "--out", str(tmp_path / "runs"), "--name", "cli"]) == 0
    assert "## Overall" in capsys.readouterr().out
