"""Dense and hybrid retrieval: registry names, the embedding cache, fusion, and the sentence-transformers adapter.

Real models are never downloaded here: the "hash" preset (hashed bag of words) and a fake
sentence_transformers module stand in for them.
"""
import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.runner import run_eval  # noqa: E402
from generation.prompts import agent_system  # noqa: E402
from generation.tools import TOOLS, ToolContext  # noqa: E402
from library import Library  # noqa: E402
from retrieval import build_retriever, get_retriever, is_known, slug  # noqa: E402
from retrieval import dense as dense_mod  # noqa: E402
from retrieval.base import Hit  # noqa: E402
from retrieval.dense import DenseRetriever, Preset, RetrieverUnavailable  # noqa: E402
from retrieval.hybrid import HybridRetriever  # noqa: E402


def chunk(pid, i, text, title="Paper", section="S"):
    return {"chunk_id": f"{pid}#{i:03d}", "paper_id": pid, "index": i, "text": text, "title": title,
            "section": section, "year": 2020, "source": "pdf", "page_start": 1, "page_end": 1, "n_words": len(text.split())}


CHUNKS = [
    chunk("BP", 0, "Atom-centered symmetry functions describe each atomic environment within a cutoff radius.", "Behler"),
    chunk("BP", 1, "The total energy is a sum of atomic energies from element-specific neural networks.", "Behler"),
    chunk("NQ", 0, "NequIP uses E(3)-equivariant convolutions over geometric tensors.", "NequIP"),
    chunk("TP", 0, "The TIP3P water model uses three interaction sites.", "Water models"),
]


def test_names_variants_and_slugs():
    assert all(is_known(n) for n in ["bm25", "dense", "dense:bge-small", "hybrid:nomic", "dense:BAAI/bge-base-en-v1.5"])
    assert not any(is_known(n) for n in ["bm25:nomic", "dense:nope", "sparse", "hybrid:"[:-1] + ":x"])
    r = get_retriever("dense:bge-small")      # no model is loaded until the first index/search
    assert r.config()["model"] == "BAAI/bge-small-en-v1.5" and r.config()["query_prefix"].startswith("Represent")
    assert get_retriever("hybrid").config()["dense"]["model"] == "nomic-ai/nomic-embed-text-v1.5"
    assert slug("dense:BAAI/bge-base-en-v1.5") == "dense-BAAI-bge-base-en-v1.5"
    with pytest.raises(ValueError, match="Unknown retriever"):
        get_retriever("dense:nope")


def test_dense_search_and_incremental_cache(tmp_path):
    r = build_retriever("dense:hash", CHUNKS, tmp_path)
    assert r.search("symmetry functions cutoff radius", k=1)[0].chunk_id == "BP#000"
    assert r.stats == {"chunks": 4, "embedded_now": 4, "from_cache": 0}
    files = sorted(p.name for p in (tmp_path / "hash").iterdir())
    assert files == ["ids.json", "meta.json", "vectors.npy"]
    assert json.loads((tmp_path / "hash" / "meta.json").read_text())["chunks"] == 4

    again = build_retriever("dense:hash", CHUNKS, tmp_path)
    assert again.stats["embedded_now"] == 0 and np.allclose(again.matrix, r.matrix)

    changed = [dict(c) for c in CHUNKS] + [chunk("NEW", 0, "A brand new passage about water models.")]
    changed[1]["text"] = "Edited text after re-parsing."
    third = build_retriever("dense:hash", changed, tmp_path)
    assert third.stats == {"chunks": 5, "embedded_now": 2, "from_cache": 3}  # only the edited and the new chunk


def test_cache_is_ignored_when_the_embedding_setup_changes(tmp_path, monkeypatch):
    build_retriever("dense:hash", CHUNKS, tmp_path)
    monkeypatch.setitem(dense_mod.PRESETS, "hash", Preset("hash", doc_prefix="passage: ", max_tokens=10**9))
    r = build_retriever("dense:hash", CHUNKS, tmp_path)
    assert r.stats["embedded_now"] == 4


def test_empty_and_without_cache():
    r = DenseRetriever("hash")
    r.index([])
    assert r.search("anything") == []
    r.index(CHUNKS[:2])  # no cache folder: works, nothing written
    assert len(r.search("energy", k=5)) == 2


class FixedRanker:
    def __init__(self, ids):
        self.ids = ids

    def search(self, query, k=10):
        return [Hit(c, 1.0, r) for r, c in enumerate(self.ids[:k], 1)]


def test_reciprocal_rank_fusion():
    h = HybridRetriever("hash", k_rrf=60)
    h.bm25, h.dense = FixedRanker(["A", "B", "C"]), FixedRanker(["C", "A", "D"])
    hits = h.search("q", k=4)
    # A: 1/61 + 1/62, C: 1/63 + 1/61, B: 1/62, D: 1/63
    assert [x.chunk_id for x in hits] == ["A", "C", "B", "D"] and [x.rank for x in hits] == [1, 2, 3, 4]
    assert hits[0].score == pytest.approx(1 / 61 + 1 / 62)


def test_hybrid_keeps_exact_terms_and_caches(tmp_path):
    r = build_retriever("hybrid:hash", CHUNKS, tmp_path)
    assert r.search("TIP3P", k=1)[0].chunk_id == "TP#000"
    assert r.config()["fusion"] == "rrf" and r.config()["bm25"]["name"] == "bm25"
    assert (tmp_path / "hash" / "vectors.npy").exists()


def test_library_caches_embeddings_in_the_chunk_run(tmp_path):
    run = tmp_path / "pymupdf_w400_o60"
    run.mkdir()
    (run / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    lib = Library.load(run)
    hits = lib.search("water model interaction sites", k=2, retriever="dense:hash", paper="TP")
    assert [h.chunk_id for h in hits] == ["TP#000"]
    assert (run / "embeddings" / "hash" / "vectors.npy").exists()
    assert lib.retriever("dense:hash") is lib.retriever("dense:hash") and lib.retriever("bm25") is not None


def test_retrieval_eval_with_hybrid(tmp_path):
    run = tmp_path / "chunks" / "test_run"
    run.mkdir(parents=True)
    (run / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    q = tmp_path / "q.yaml"
    q.write_text("""- id: q001
  question: How do Behler-Parrinello networks describe atomic environments?
  type: lookup
  split: dev
  evidence:
  - paper: BP
    quote: Atom-centered symmetry functions describe each atomic environment within a cutoff radius.
""")
    d = run_eval(q, run, "hybrid:hash", out_root=tmp_path / "runs")
    assert "hybrid-hash" in d.name and (run / "embeddings" / "hash").exists()
    summary = json.loads((d / "summary.json").read_text())
    assert summary["retriever"]["name"] == "hybrid" and summary["results"]["all"]["hit@5"]["mean"] == 1.0


def test_agent_describes_the_search_it_has():
    assert "keyword search (BM25)" in agent_system("bm25") and "{" not in agent_system("bm25")
    assert "semantic search" in agent_system("dense:bge-small") and "BM25" not in agent_system("dense")
    assert "keyword and semantic" in agent_system("hybrid")
    lib = Library([dict(c) for c in CHUNKS])
    assert TOOLS["search"].spec(ToolContext(lib, retriever="dense")).get("description").startswith("Semantic search")
    assert TOOLS["search"].spec(ToolContext(lib, retriever="bm25"))["description"].startswith("Keyword search (BM25)")


def test_sentence_transformers_adapter(monkeypatch):
    """The real adapter, against a fake sentence_transformers module: prefixes, normalization, truncation."""
    seen = {}

    class FakeModel:
        def __init__(self, name, trust_remote_code=False, device=None):
            seen["init"] = (name, trust_remote_code, device)
            self.max_seq_length = 0
            self.tokenizer = lambda text, add_special_tokens, truncation: {"input_ids": text.split()}

        def get_sentence_embedding_dimension(self):
            return 3

        def encode(self, texts, batch_size, normalize_embeddings, convert_to_numpy, show_progress_bar):
            assert normalize_embeddings and convert_to_numpy
            seen.setdefault("texts", []).extend(texts)
            return np.array([[1.0, 0.0, 0.0] if "symmetry" in t else [0.0, 1.0, 0.0] for t in texts])

    monkeypatch.setitem(sys.modules, "sentence_transformers", types.SimpleNamespace(SentenceTransformer=FakeModel))
    monkeypatch.setattr(dense_mod.SentenceTransformerEmbedder, "_cache", {})
    r = DenseRetriever("nomic")
    r.index(CHUNKS)
    assert seen["init"] == ("nomic-ai/nomic-embed-text-v1.5", True, None)
    assert r.embedder.model.max_seq_length == 2048
    assert all(t.startswith("search_document: ") for t in seen["texts"])
    assert r.search("symmetry", k=1)[0].chunk_id == "BP#000" and seen["texts"][-1] == "search_query: symmetry"
    assert r.truncated(CHUNKS) == 0


def test_missing_package_is_a_clear_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)  # import fails
    monkeypatch.setattr(dense_mod.SentenceTransformerEmbedder, "_cache", {})
    with pytest.raises(RetrieverUnavailable, match="requirements-dense.txt"):
        DenseRetriever("bge-small").index(CHUNKS)
