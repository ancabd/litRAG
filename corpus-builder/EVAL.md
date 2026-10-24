# Evaluation

Two evals on the same questions: **retrieval** (does the retriever find the passages that answer them?) and **answers** (given those passages, is the generated answer right, grounded in what it cites, and does it decline when it should?).

```bash
python evaluate.py check     # are the questions valid, and can every evidence quote be found?
python evaluate.py run       # score BM25 on the dev split -> data/runs/<timestamp>_.../report.md
python evaluate.py ask "How does NequIP differ from Behler-Parrinello symmetry functions?"
python evaluate.py answer    # answer eval: generate, then judge, every dev question
```

## Writing questions

Questions live in `data/questions/questions.yaml`; the comments at the top of that file explain every field. The loop:

1. **Think of a question** you would genuinely ask while reading these papers. Phrase it your way, not the paper's: copying the paper's wording makes keyword search look better than it is.
2. **Find the answer**: `python evaluate.py search "a few keywords"` prints the top chunks with paper, section and page.
3. **Record the evidence**: the paper's OpenAlex id (shown in the search output as `W...#003`, the part before `#`) and a 10–30 word quote of the passage. For equations, quote the sentence just before or after the formula; the formula itself usually comes out garbled.
4. **Run `python evaluate.py check`.** It tells you if a paper id is wrong or a quote doesn't match, and shows the closest chunks so you can fix it.

Evidence is stored as paper + quote, never as a chunk id, so the same questions work for every parser and chunk size. A chunk counts as gold when it contains at least half the quote's word trigrams (tune with `--threshold`).

**Guarding against fooling yourself:**

- Use `split: dev` for questions you look at and tune on, and `split: test` for a held-back set you run only at the end (`--split test`). If you tune on the test questions, the final numbers are inflated.
- Write the questions *before* tuning retrieval, and don't edit a question because a retriever got it wrong. Fix it only if the question or evidence itself was wrong.
- If you search for keywords from your question to find the evidence, BM25 is likely to rank that passage first. Keep that in mind when BM25 looks surprisingly good; questions written straight from your own reading are a fairer test.

## When another passage says the same thing

Your corpus was built by following citations, so most results appear in several places: the original paper, the review, and every later paper whose introduction restates it. Retrieval often finds one of those restatements instead of your original source. Counted strictly, that's a miss, even though the passage answers the question. (In IR this is called *incomplete relevance judgments*.)

The fix is the standard one, *pooling*: look at what the retriever returns for each question and judge it. In the app, open a question and use **Review retrieved passages**:

- **Answers it** adds the passage as an *alternative* for that evidence item (on two-part questions you pick which part).
- **Doesn't answer it** records it under `not_relevant`, so it isn't shown for review again.
- **Undo** clears a judgment.

Judgments are saved straight to `questions.yaml` (format in the comments at the top of that file), and quotes are taken from the middle of the passage, so they still resolve after re-chunking. `evaluate.py check` verifies them like any evidence.

Every metric is then reported twice:

- **strict**: only your original evidence counts. This measures *attribution*: did it find the source you'd cite?
- **lenient**: alternatives count too. This measures *answerability*: did it find something that answers the question?

The gap between the two is a result in itself; the report lists the questions that were found only through alternatives. **judged@10** says how much of each question's top 10 you've judged. When it's low, unjudged passages may still answer questions, so even the lenient score undercounts. Judge before comparing retrievers: a new retriever surfaces passages nobody has judged yet, which biases the comparison against it.

## Metrics

| metric | meaning |
|---|---|
| `hit@k` | a gold chunk is in the top k |
| `recall@k` | fraction of a question's evidence items found in the top k (differs from hit@k only for multihop/comparison) |
| `mrr` | 1 / rank of the first gold chunk |
| `ndcg@10` | ranking quality over the top 10, rewarding gold chunks near the top |
| `paper_hit@k` | the right *paper* is in the top k, maybe not the right passage |
| `lenient_*` | the same metric, with alternatives accepted as gold |
| `judged@10` | share of the top 10 that is judged (evidence, alternative or not relevant) |

Every number comes with a 95% bootstrap confidence interval over questions. With 20 questions these intervals are wide (±0.2 is normal), which is exactly why they're reported: two retrievers whose intervals overlap heavily aren't clearly different yet.

Results are broken down by `type:` and `tag:`. That's where the equation question lives: compare `tag:equation` with `all`. A large gap whose misses show garbled math is the signal to try a better parser.

Unanswerable questions are skipped here; the answer eval scores them (does the system decline?).

## Runs

Runs can be started from the terminal (`python evaluate.py run`) or from the app's **Results** tab (**Run eval**); both use the same code and write to the same place, and the Results tab lists, shows and compares all of them. Each run writes a folder under `data/runs/`:

- `report.md`: overall metrics, breakdown, and every miss with what was retrieved instead (start reading here)
- `summary.json`: all numbers plus the full configuration: retriever settings, chunk config, parser version, question file hash, git commit
- `per_question.jsonl`: gold and retrieved chunks for each question, for error analysis

Compare runs side by side (it warns if the question file changed between them):

```bash
python evaluate.py compare ../data/runs/<bm25 run> ../data/runs/<other run>
```

Worth committing the `report.md` files: together they're the history of the project's results.

## Answer evaluation

`ask` and `answer` need `ANTHROPIC_API_KEY` (create a key at https://platform.claude.com). The options both share: `--retriever`, `--k` (passages given to the model, default 8), `--generator claude|extractive`, `--model` (default `claude-sonnet-5-5`), `--no-cache`. `answer` also takes `--judge <model>` (default: the generator's model; `none` for no judge), `--split`, `--name`.

For each question it retrieves the top k passages, asks the model to answer from them only, citing each claim as `[chunk_id]`, or to say the passages don't answer it. Then:

| metric | what it asks | how |
|---|---|---|
| `correct` | does the answer match your `answer` field? | LLM judge: correct 1, partial 0.5, incorrect 0 |
| `supported` | do the passages it cites actually say this? | LLM judge, sees only the cited passages |
| `cites_gold` | does it cite your evidence (or an alternative)? | exact, no judge |
| `retrieved_gold` | was your evidence among the k passages at all? | exact |
| `invalid_citations` | does it cite ids it wasn't given? (lower is better) | exact |
| `abstained_when_unanswerable` | does it decline unanswerable questions? | exact |
| `abstained_when_answerable` | does it decline questions the corpus answers? (lower is better) | exact |

Results are also split into `retrieval:found` and `retrieval:missed`. That split is the most useful number here: a wrong answer when the evidence *was* retrieved is a generation problem (prompt, model); when it wasn't, no prompt will fix it and the retriever is what to work on.

**Reference answers.** `correct` needs the question's `answer` field; questions without one are listed in the report and scored on the other metrics only. Write references as the key facts, not a paragraph: the judge accepts different wording and extra correct detail, but marks contradictions and missing key facts.

**Can you trust the judge?** An LLM grading an LLM is only worth reporting with evidence that it grades like you do. On an answer run's page in the app, open answers and give your own verdict; the page shows agreement and Cohen's κ (≥ 0.6 is substantial). Your verdicts are saved in the run folder as `human.json`. Grading 15–20 answers is enough at this scale, and it's the number to put in a write-up next to the score.

**The extractive baseline** (`--generator extractive`) needs no key: it returns the retrieved sentence that overlaps most with the question, with its citation, or declines when nothing overlaps. An LLM that doesn't clearly beat it isn't adding much.

**Cost and caching.** Every request and response is cached in `data/cache/llm/`, keyed by model, prompts and token limit, so rerunning the same setup costs nothing and gives the same answers; changing the prompt, model or passages makes new calls. Each run records tokens and dollars for the generator and the judge. With Sonnet, 20 questions with 8 passages each cost a few cents. Prompts are versioned (`generation/prompts.py`) and the version is stored in every run, so bump it when you change a prompt.

Answer runs go in `data/runs/` next to retrieval runs (`report.md` lists every answer that wasn't fully correct, with the judge's reasons), and `compare` works on them too.

## Adding a generator

`generation/answer.py` has the `Generator` interface: `generate(question, passages)` returns the answer text, whether it's answerable, the LLM response (for usage) and any warnings; `answer_question` wraps it, extracts and checks the citations, and returns an `Answer`. Add a subclass and one line to `GENERATORS`, and it can be used from `evaluate.py --generator`, the Ask page and the answer eval. An agentic generator (one that rewrites the query, searches again, or reads more of a paper before answering) also needs the retriever, so it will extend this interface to receive it and decide itself what to fetch.

## Adding a retriever

Same pattern as parsers. Create `retrieval/<name>.py` with a subclass of `retrieval.base.Retriever` (`index(chunks)`, `search(query, k)`, and `config()` returning every setting that affects results), add one line to `RETRIEVERS` in `retrieval/__init__.py`, then `python evaluate.py run --retriever <name>`.
