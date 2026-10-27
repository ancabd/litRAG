# litrag

Agentic RAG over the literature on machine-learned interatomic potentials and biomolecular simulation, with an evaluation harness and a web app.


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

- **Ask**: ask a question in your own words, and pick **Single shot**, **Agent** or the **Extractive baseline**. With the agent, its steps (each search, what it read, tokens) are listed under the answer. With single shot, the top passages (8 by default) go to Claude, which answers only from them and cites each claim; the citations are numbered links to the passages, which are listed below the answer with the uncited ones folded away. If the passages don't answer the question it says so instead of guessing. Each answer shows the model, tokens and cost; identical questions are answered from the cache.
- **Questions**: write, edit and delete eval questions. Each evidence quote is checked live against the chunks, and the matching passage is shown with the quote highlighted. "Find a passage" searches the corpus and turns a passage, or the words you select in it, into evidence. "Review retrieved passages" shows what the retriever returns for the question; mark passages that answer it too (alternatives, for lenient scoring) or don't (see EVAL.md).
- **Papers**: every paper in the corpus with its OpenAlex id, full-text status, why it's in the corpus (seed, cited by a seed, or citing one), its abstract, its chunks, a link to the PDF, and the questions that use it as evidence.
- **Adding what's missing**: for abstract-only and metadata-only papers, add a PDF you have (drop it on the paper's page or its row in the list), or paste an abstract. The app saves the PDF to `data/corpus/pdfs/`, updates `manifest.jsonl` and `manifest.csv`, records the addition in `data/corpus/manual.jsonl` (so `corpus_builder.py` keeps it on later runs), and re-chunks every chunk run. The paper is searchable and usable as evidence straight away, and the page tells you if the PDF couldn't be parsed (e.g. a scanned PDF), in which case the abstract is used. A PDF you added can be removed again.
- **Search**: BM25 over all chunks.
- **Results**: every eval run, whether started here or from the terminal with `evaluate.py run` / `evaluate.py answer` (same code, same `data/runs/` folder). Pick **Retrieval** or **Answers** before running; for answers, pick the **Method** (single shot, agent or extractive baseline), the model and the judge.
  - A retrieval run shows strict and lenient scores with 95% intervals, the breakdown by type and tag, and each question's top 10 labeled as your evidence, alternative, not relevant or not reviewed.
  - An answer run (it runs in the background with a progress bar) shows whether answers are correct against your reference answers, supported by what they cite, and decline when they should, plus each generated answer next to your reference with the judge's verdict and reasons. Grade answers yourself with **Your verdict**: the page reports how often the judge agrees with you (and Cohen's κ), which is what makes the judge's score worth quoting.
  - Select runs of one kind to compare them, including which questions moved.

The chunk run (e.g. `pymupdf_w400_o60`) is picked in the sidebar; evidence checks, search and chunk counts all use it.

**Saving is safe to mix with a text editor.** Every save is validated with the same rules as `evaluate.py check`, written atomically, and refused if `questions.yaml` changed since the app loaded it. You then get a "Reload file" button, and your unsaved form edits are kept. The comment block at the top of the file is preserved; comments *inside* questions are not, so use the `notes` field.

## Structure
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

## How answering works: single shot and the agent

There are three generators, chosen with `--generator` on the command line (and in the app):

| Generator | What it does | Needs a key |
|---|---|---|
| `extractive` | Searches once with the question and returns the best-overlapping sentence. The floor. | no |
| `claude` | Searches once with the question and gives the top k passages to Claude, which answers from them. | yes |
| `agent` | Claude decides what to search and read, in a loop, until it can answer. | yes |

Single shot has one weakness the agent is built for: the question is the only search. If the question uses different words than the paper ("rotational symmetry" vs "E(3)-equivariant"), or needs two facts where the second depends on the first ("which cutoff does the model that introduced continuous-filter convolutions use?"), one search can't find everything, and no prompt fixes a passage that was never retrieved.

### The loop

```
                 question
                    │
                    ▼
     ┌─────────────────────────────┐
     │ Claude                      │◄────────────────────────────────┐
     │  system prompt (how to work)│                                 │
     │  tools (what it can do)     │                                 │
     │  the conversation so far    │                                 │
     └──────────────┬──────────────┘                                 │
                    │ one or more tool calls                         │
     ┌──────────────┼──────────────────┬──────────────────┐          │
     ▼              ▼                  ▼                  ▼          │
  search        read_around        open_paper        give_up, or a   │
  (query,       (passage id,       (paper id)        reply with no   │
   k, paper,     before, after)                      tool call       │
   year_from)                                             ▼          │
     │              │                  │            Answer + trace   │
     └──────────────┴────────┬─────────┘                             │
                             ▼                                       │
              Library: BM25 index, chunks in reading                 │
              order, paper outlines                                  │
                             │                                       │
                             ▼                                       │
              tool results (passages with their ids) ────────────────┘
              added to the conversation; budgets checked
```

Each turn, Claude sees the whole conversation so far and either calls tools or finishes:

1. **The question goes in** with a system prompt (`generation/prompts.py`, versioned as `agent-v2`) that explains the tools and the rules. The rules are the same as single shot: answer only from passages it has read, cite every claim as `[chunk_id]`, give up rather than guess.
2. **Claude calls tools.** It can call several in one turn, for example opening a paper and reading around a passage at once. Each call runs against the `Library` (`corpus-builder/generation/tools.py`) and the results go back as passages with their ids.
3. **Repeat** until Claude replies without calling a tool (that reply is the answer) or calls `give_up`.
4. **Check the answer.** Its citations are checked against every passage it actually read; an id it never saw counts as an invalid citation, exactly as in single shot.

| Tool | What it returns | Typical use |
|---|---|---|
| `search(query, k, paper_id, year_from)` | the top k passages for a keyword query, optionally within one paper or from a year on | rephrasing with the paper's vocabulary; the second hop of a multi-hop question; looking inside one paper |
| `read_around(chunk_id, before, after)` | the neighbouring passages of the same paper, in reading order | a passage cut off mid-argument; the definitions around an equation |
| `open_paper(paper_id)` | title, authors, year, abstract, and the list of sections with their first passage | finding where in a paper to look |
| `give_up(reason)` | ends the loop without an answer | the papers don't cover the question |

**Budgets keep it bounded.** `max_turns` (default 8 model calls) and `token_budget` (default 100,000 tokens over all turns). When either runs out, the last turn offers only `give_up`, with a note to answer now, so every question ends with an answer or an explicit give-up.

**Cost.** Every turn re-sends the conversation, so it grows. Three things keep that cheap:
- A passage is shown in full only once; when a later search returns it again, only its id and heading are repeated.
- Prompt caching is on, so the repeated part of each turn is billed at a fraction of the input price (5% on Sonnet and Opus 5.5, 10% on Haiku).
- Every request is cached on disk, so rerunning an eval costs nothing.

Expect most questions to take 2–4 turns and a few thousand to a few tens of thousands of input tokens, most of them cache reads; the exact tokens and cost of every answer are recorded, so the first real eval run will tell.

**The trace.** Every step is recorded: the tool, its arguments, which passages came back and how many were new, tokens, time, and Claude's own short note on what it is doing. `evaluate.py ask --generator agent` prints it (numbers here are illustrative):

```
Steps:
   1. search      "NequIP radial cutoff" (k=5) -> 5 passages, 5 new   [2,310 in / 61 out, 2.1s]
      | Let me find NequIP's cutoff first.
   2. search      "SchNet cosine cutoff" (k=5) -> 5 passages, 3 new   [5,020 in / 58 out (2,280 cached), 1.8s]
      | Now SchNet's.
   3. answer      [7,650 in / 95 out (4,990 cached), 2.4s]
```

Answer runs save the trace of every question in `per_question.jsonl`.

**How it is evaluated.** Exactly like single shot, with `evaluate.py answer --generator agent` (or **Answers** on the Results tab, picking an "agent" model): same questions, same judge, same metrics. Differences from single shot:
- "Evidence retrieved" means the evidence was among *any* passage the agent read, not just the first search.
- Each question also records its effort: model calls, tool calls, searches, passages read, tokens, cost, time, and whether it gave up or ran out of budget. The run page and the report show the averages.



**Running it.**

```bash
cd corpus-builder
python evaluate.py ask --generator agent "How does NequIP's cutoff compare to SchNet's?"
python evaluate.py ask --generator agent --model claude-haiku-5-5 --max-turns 4 "..."
python evaluate.py ask --generator agent --tools search "..."        # ablation: search only
python evaluate.py answer --generator agent --judge claude-sonnet-5-5  # the answer eval
```

**Extending it.** A new tool is a `Tool` subclass in `generation/tools.py` (name, description, JSON schema, and a `run` that uses the `Library`) plus one line in `TOOLS`; turn it on with `--tools`. Planned next:
- `find_papers`, a search over titles and abstracts that returns papers rather than passages
- `citations`, which follows references and citing papers within the corpus, once the corpus builder saves the citation graph

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

- **`corpus-builder/library.py`** is the one way to read a chunk run: `search` (with `paper`, `year_from`/`year_to`, `exclude` filters), `chunk`, `neighbours`, `paper` (title, year, section outline), `section_chunks`. The CLI, the evals, the server (each cached chunk run is a `Library`) and the generators all use it, so they see the corpus the same way. The agent's tools are thin wrappers over these methods.
- **Routers** only translate HTTP; **services** hold the logic and caches (chunk runs and retriever indexes are loaded once and reloaded when their files change); the **core** stays usable from the command line.
- **Adding a retriever** (dense, hybrid, rerank): a new file in `corpus-builder/retrieval/` plus one registry line. It then shows up in `evaluate.py`, in `/api/search?retriever=...` and in `/api/meta`.
- **Generation** lives in `corpus-builder/generation/`: `llm.py` (the Anthropic client, the on-disk cache, prices), `prompts.py` (versioned prompts; the version is recorded in every run), `answer.py` (the generator interface and the single-shot generators), `agent.py` (the agent loop) and `tools.py` (the agent's tools). Generators get the question and the `Library` and decide what to read; every answer carries a step-by-step `trace` and the list of passages it saw, and its citations are checked against those. The LLM layer has `complete` (one prompt) and `chat` (a conversation with tool use), both cached. A new generator is a `Generator` subclass plus one registry line, and then shows up in `evaluate.py`, the Ask page and the answer eval.
- **Long jobs** (answer evals) run in a background thread (`services/jobs.py`) and the UI polls `/api/jobs/{id}`.
- **Paths** default to the layout above. `LITRAG_DATA` moves the whole data folder; `LITRAG_CORPUS`, `LITRAG_CHUNKS`, `LITRAG_QUESTIONS`, `LITRAG_RUNS`, `LITRAG_CACHE`, `LITRAG_CORE` and `LITRAG_WEB_DIST` move single parts. The command-line tools find `data/` from any working directory.
