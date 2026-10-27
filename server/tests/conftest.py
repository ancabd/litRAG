import json
import sys
from pathlib import Path

import pytest

SERVER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER))

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402

PAPERS = [
    {"openalex_id": "W1", "status": "pdf", "pdf_path": "pdfs/W1.pdf", "title": "Generalized neural-network representation of high-dimensional potential-energy surfaces",
     "authors": "J. Behler, M. Parrinello", "year": 2007, "venue": "PRL", "doi": "10.1103/physrevlett.98.146401",
     "roles": ["seed"], "via_seeds": ["W1"], "cited_by_count": 3000, "abstract": "Neural networks for PES."},
    {"openalex_id": "W2", "status": "abstract_only", "title": "E(3)-equivariant graph neural networks for interatomic potentials",
     "authors": "S. Batzner et al.", "year": 2022, "roles": ["seed"], "via_seeds": ["W2"], "cited_by_count": 900,
     "abstract": "NequIP uses E(3)-equivariant convolutions."},
    {"openalex_id": "W3", "status": "metadata_only", "title": "A paywalled force field paper", "year": 1995,
     "roles": ["reference"], "via_seeds": ["W1"], "cited_by_count": 50},
]
CHUNKS = [
    {"chunk_id": "W1#000", "paper_id": "W1", "index": 0, "section": "Introduction", "page_start": 1, "page_end": 1,
     "source": "pdf", "n_words": 15, "title": PAPERS[0]["title"], "year": 2007,
     "text": "We demonstrate the method for bulk silicon, comparing energies with density functional theory."},
    {"chunk_id": "W1#001", "paper_id": "W1", "index": 1, "section": "2 Method", "page_start": 2, "page_end": 2,
     "source": "pdf", "n_words": 16, "title": PAPERS[0]["title"], "year": 2007,
     "text": "The cutoff function decays smoothly to zero at the cutoff radius Rc, using a cosine form."},
    {"chunk_id": "W2#000", "paper_id": "W2", "index": 0, "section": "Abstract", "page_start": None, "page_end": None,
     "source": "abstract", "n_words": 6, "title": PAPERS[1]["title"], "year": 2022,
     "text": "NequIP uses E(3)-equivariant convolutions on geometric tensors."},
]
QUESTIONS = """# Header comment that must survive edits.
# Second header line.

- id: q001
  question: Which material was used to test the potential?
  type: lookup
  tags: [bp]
  split: dev
  answer: Bulk silicon.
  evidence:
    - paper: W1
      quote: "the method for bulk silicon"   # inline comment (allowed to be lost)

- id: q002
  question: What hit rate did RFdiffusion reach?
  type: unanswerable
  split: dev
"""


@pytest.fixture(autouse=True)
def isolated_keys(tmp_path, monkeypatch):
    """Keep tests away from your real API key: no environment key, no saved key, no session key."""
    from generation import keys
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("LITRAG_KEY_FILE", str(tmp_path / "litrag-credentials.json"))
    monkeypatch.setattr(keys, "_session_key", None)
    yield keys


@pytest.fixture
def data_dir(tmp_path):
    core = tmp_path / "core"
    (core / "corpus" / "pdfs").mkdir(parents=True)
    (core / "corpus" / "manifest.jsonl").write_text("\n".join(json.dumps(p) for p in PAPERS))
    (core / "corpus" / "pdfs" / "W1.pdf").write_bytes(b"%PDF-1.4 tiny")
    run = core / "chunks" / "pymupdf_w400_o60"
    run.mkdir(parents=True)
    (run / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in CHUNKS))
    (run / "run.json").write_text(json.dumps({"parser": "pymupdf@2", "chunking": {"size": 400, "overlap": 60},
                                              "chunks": 3}))
    (core / "questions").mkdir()
    (core / "questions" / "questions.yaml").write_text(QUESTIONS)
    return core


@pytest.fixture
def client(data_dir, tmp_path):
    from fastapi.testclient import TestClient

    real_core = SERVER.parent / "corpus-builder"
    settings = Settings.from_env(core_dir=real_core, corpus_dir=data_dir / "corpus",
                                 chunks_root=data_dir / "chunks",
                                 questions_file=data_dir / "questions" / "questions.yaml",
                                 runs_dir=data_dir / "runs", cache_dir=data_dir / "cache",
                                 web_dist=tmp_path / "no-dist")
    return TestClient(create_app(settings))
