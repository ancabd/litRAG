# litrag

Agentic RAG over academic literature (tested on machine-learned interatomic potentials and biomolecular simulation), with an evaluation harness and a web app.

```
litrag/
  corpus-builder/   core library + command-line tools
                    corpus_builder.py   seeds -> papers, PDFs, abstracts   (README.md)
                    parse_corpus.py     PDFs + abstracts -> chunks          (INGEST.md)
                    evaluate.py         retrieval evaluation                (EVAL.md)
                    data lives here too: corpus/, chunks/, questions/, runs/
  server/           FastAPI app: the core as an HTTP API, and serves the UI
  web/              React + TypeScript UI (Vite); web/dist is the built version
```

The command-line tools and the app work on the same files. Questions you write in the app go to `corpus-builder/questions/questions.yaml`, which is exactly what `evaluate.py` reads.

## Setup

```bash
pip install -r corpus-builder/requirements.txt -r server/requirements.txt
```

The built UI is included in `web/dist`, so Node is only needed if you change the UI.

## Run the app

```bash
cd server
python -m app            # http://127.0.0.1:8000   (API docs: /api/docs)
```

- **Questions**: write, edit and delete eval questions. Each evidence quote is checked live against the chunks, and the matching passage is shown with the quote highlighted. "Find a passage" searches the corpus and turns a passage, or the words you select in it, into evidence. "Review retrieved passages" shows what the retriever returns for the question; mark passages that answer it too (alternatives, for lenient scoring) or don't (see EVAL.md).
- **Papers**: every paper in the corpus with its OpenAlex id, full-text status, why it's in the corpus (seed, cited by a seed, or citing one), its abstract, its chunks, a link to the PDF, and the questions that use it as evidence.
- **Adding what's missing**: for abstract-only and metadata-only papers, add a PDF you have (drop it on the paper's page or its row in the list), or paste an abstract. The app saves the PDF to `corpus/pdfs/`, updates `manifest.jsonl` and `manifest.csv`, records the addition in `corpus/manual.jsonl` (so `corpus_builder.py` keeps it on later runs), and re-chunks every chunk run. The paper is searchable and usable as evidence straight away, and the page tells you if the PDF couldn't be parsed (e.g. a scanned PDF), in which case the abstract is used. A PDF you added can be removed again.
- **Search**: BM25 over all chunks.

The chunk run (e.g. `pymupdf_w400_o60`) is picked in the sidebar; evidence checks, search and chunk counts all use it.

**Saving is safe to mix with a text editor.** Every save is validated with the same rules as `evaluate.py check`, written atomically, and refused if `questions.yaml` changed since the app loaded it. You then get a "Reload file" button, and your unsaved form edits are kept. The comment block at the top of the file is preserved; comments *inside* questions are not, so use the `notes` field.

## Working on the UI

```bash
cd server && python -m app --reload     # terminal 1: API on :8000
cd web && npm install && npm run dev    # terminal 2: UI on http://localhost:5173, live reload
npm run build                           # writes web/dist, which `python -m app` serves
```

## Tests

```bash
cd corpus-builder && python -m pytest -q     # core: corpus building, parsing, chunking, retrieval eval
cd server && python -m pytest -q             # API
cd web && npm run typecheck                  # UI types
```

## Architecture, and where things go next

```
web (React)  --/api-->  server/app/routers  -->  server/app/services  -->  corpus-builder (core)
                        one file per area:       corpus, chunks,          ingest, retrieval,
                        meta, papers,            questions, evidence      evaluation
                        questions, search
```

- **Routers** only translate HTTP; **services** hold the logic and caches (chunk runs and retriever indexes are loaded once and reloaded when their files change); the **core** stays usable from the command line.
- **Adding a retriever** (dense, hybrid, rerank): a new file in `corpus-builder/retrieval/` plus one registry line. It then shows up in `evaluate.py`, in `/api/search?retriever=...` and in `/api/meta`.
- **Adding "ask a question"**: a `server/app/routers/ask.py` that calls `ChunkService.get(run).retriever(...)` for passages and an LLM for the answer (streamed), a hook in `web/src/api/hooks.ts`, and a page in `web/src/pages/` with a route in `App.tsx`. The search results view (`ChunkCard`) is reused for citations.
- **Paths** default to the layout above; override them with `LITRAG_CORE`, `LITRAG_CORPUS`, `LITRAG_CHUNKS`, `LITRAG_QUESTIONS`, `LITRAG_RUNS` or `LITRAG_WEB_DIST`.
