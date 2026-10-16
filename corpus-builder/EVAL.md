# Retrieval evaluation

Scores how well a retriever finds the passages that answer your questions.

```bash
python evaluate.py check     # are the questions valid, and can every evidence quote be found?
python evaluate.py run       # score BM25 on the dev split -> runs/<timestamp>_.../report.md
```

## Writing questions

Questions live in `questions/questions.yaml`; the comments at the top of that file explain every field. The loop:

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

Unanswerable questions are skipped here; they're scored later, in the answer eval (does the system decline?).

## Runs

Each run writes a folder under `runs/`:

- `report.md`: overall metrics, breakdown, and every miss with what was retrieved instead (start reading here)
- `summary.json`: all numbers plus the full configuration: retriever settings, chunk config, parser version, question file hash, git commit
- `per_question.jsonl`: gold and retrieved chunks for each question, for error analysis

Compare runs side by side (it warns if the question file changed between them):

```bash
python evaluate.py compare runs/<bm25 run> runs/<other run>
```

Worth committing the `report.md` files: together they're the history of the project's results.

## Adding a retriever

Same pattern as parsers. Create `retrieval/<name>.py` with a subclass of `retrieval.base.Retriever` (`index(chunks)`, `search(query, k)`, and `config()` returning every setting that affects results), add one line to `RETRIEVERS` in `retrieval/__init__.py`, then `python evaluate.py run --retriever <name>`.
