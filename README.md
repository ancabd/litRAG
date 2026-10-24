# litrag

Agentic RAG over the literature on machine-learned interatomic potentials and biomolecular simulation, with an evaluation harness and a web app.

```
litrag/
  corpus-builder/   core library + command-line tools
                    corpus_builder.py   seeds -> papers, PDFs, abstracts   (README.md)
                    parse_corpus.py     PDFs + abstracts -> chunks          (INGEST.md)
                    evaluate.py         ask, retrieval eval, answer eval    (EVAL.md)
  data/             everything the tools read and write (code never lives here)
                    corpus/      papers, PDFs, abstracts, manifest
                    chunks/      one folder per parser + chunk config
                    questions/   questions.yaml, your eval set
                    runs/        one folder per eval run
                    cache/       cached LLM responses (rerunning an eval is free)
  server/           FastAPI app: the core as an HTTP API, and serves the UI
  web/              React + TypeScript UI (Vite); web/dist is the built version
```

The command-line tools and the app work on the same files. Questions you write in the app go to `data/questions/questions.yaml`, which is exactly what `evaluate.py` reads.

## Setup

```bash
pip install -r corpus-builder/requirements.txt -r server/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...     # for answers; create one at https://platform.claude.com
```

Without a key everything except Claude's answers works, and the extractive baseline stands in for them.

**Upgrading from the layout where data lived inside `corpus-builder/`:** copy your old `corpus/`, `chunks/`, `questions/` and `runs/` folders into `corpus-builder/` (or unzip this over your old folder), then from the repo root:

```bash
python move_data.py           # shows what it would move
python move_data.py --apply   # moves them into data/; never overwrites a folder that has content
```

Your `questions.yaml` replaces the template, which is kept as `questions.template.yaml`.

The built UI is included in `web/dist`, so Node is only needed if you change the UI.

## Run the app

```bash
cd server
python -m app            # http://127.0.0.1:8000   (API docs: /api/docs)
```

- **Ask**: ask a question in your own words. The top passages (8 by default) go to Claude, which answers only from them and cites each claim; the citations are numbered links to the passages, which are listed below the answer with the uncited ones folded away. If the passages don't answer the question it says so instead of guessing. Each answer shows the model, tokens and cost; identical questions are answered from the cache.
- **Questions**: write, edit and delete eval questions. Each evidence quote is checked live against the chunks, and the matching passage is shown with the quote highlighted. "Find a passage" searches the corpus and turns a passage, or the words you select in it, into evidence. "Review retrieved passages" shows what the retriever returns for the question; mark passages that answer it too (alternatives, for lenient scoring) or don't (see EVAL.md).
- **Papers**: every paper in the corpus with its OpenAlex id, full-text status, why it's in the corpus (seed, cited by a seed, or citing one), its abstract, its chunks, a link to the PDF, and the questions that use it as evidence.
- **Adding what's missing**: for abstract-only and metadata-only papers, add a PDF you have (drop it on the paper's page or its row in the list), or paste an abstract. The app saves the PDF to `data/corpus/pdfs/`, updates `manifest.jsonl` and `manifest.csv`, records the addition in `data/corpus/manual.jsonl` (so `corpus_builder.py` keeps it on later runs), and re-chunks every chunk run. The paper is searchable and usable as evidence straight away, and the page tells you if the PDF couldn't be parsed (e.g. a scanned PDF), in which case the abstract is used. A PDF you added can be removed again.
- **Search**: BM25 over all chunks.
- **Results**: every eval run, whether started here or from the terminal with `evaluate.py run` / `evaluate.py answer` (same code, same `data/runs/` folder). Pick **Retrieval** or **Answers** before running.
  - A retrieval run shows strict and lenient scores with 95% intervals, the breakdown by type and tag, and each question's top 10 labeled as your evidence, alternative, not relevant or not reviewed.
  - An answer run (it runs in the background with a progress bar) shows whether answers are correct against your reference answers, supported by what they cite, and decline when they should, plus each generated answer next to your reference with the judge's verdict and reasons. Grade answers yourself with **Your verdict**: the page reports how often the judge agrees with you (and Cohen's κ), which is what makes the judge's score worth quoting.
  - Select runs of one kind to compare them, including which questions moved.

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
cd corpus-builder && python -m pytest -q     # core: corpus building, parsing, chunking, evals, generation (offline)
cd server && python -m pytest -q             # API
cd web && npm run typecheck                  # UI types
```

## Architecture, and where things go next

```
web (React)  --/api-->  server/app/routers  -->  server/app/services  -->  corpus-builder (core)
                        one file per area:       corpus, chunks,          ingest, retrieval,
                        meta, papers,            questions, evidence,     evaluation, generation
                        questions, search,       evalruns, answering,
                        ask, evals               jobs
```

- **`corpus-builder/library.py`** is the one way to read a chunk run: `search` (with `paper`, `year_from`/`year_to`, `exclude` filters), `chunk`, `neighbours`, `paper` (title, year, section outline), `section_chunks`. The CLI, the evals, the server (each cached chunk run is a `Library`) and the generators all use it, so they see the corpus the same way. The agent's tools will be thin wrappers over these methods.
- **Routers** only translate HTTP; **services** hold the logic and caches (chunk runs and retriever indexes are loaded once and reloaded when their files change); the **core** stays usable from the command line.
- **Adding a retriever** (dense, hybrid, rerank): a new file in `corpus-builder/retrieval/` plus one registry line. It then shows up in `evaluate.py`, in `/api/search?retriever=...` and in `/api/meta`.
- **Generation** lives in `corpus-builder/generation/`: `llm.py` (the Anthropic client, the on-disk cache, prices), `prompts.py` (versioned prompts; the version is recorded in every run) and `answer.py` (generators). Generators get the question and the `Library` and decide what to read; every answer carries a step-by-step `trace` and the list of passages it saw, and its citations are checked against those. The LLM layer has `complete` (one prompt) and `chat` (a conversation with tool use), both cached. A new generator, e.g. the agentic loop, is a `Generator` subclass plus one registry line, and then shows up in `evaluate.py`, the Ask page and the answer eval.
- **Long jobs** (answer evals) run in a background thread (`services/jobs.py`) and the UI polls `/api/jobs/{id}`.
- **Paths** default to the layout above. `LITRAG_DATA` moves the whole data folder; `LITRAG_CORPUS`, `LITRAG_CHUNKS`, `LITRAG_QUESTIONS`, `LITRAG_RUNS`, `LITRAG_CACHE`, `LITRAG_CORE` and `LITRAG_WEB_DIST` move single parts. The command-line tools find `data/` from any working directory.
