# corpus-builder

Builds a paper corpus from a handful of seed papers. For each seed it collects:

- **the seed itself**
- **one hop backward:** every paper the seed cites
- **one hop forward:** the most-cited papers that cite the seed (and optionally the most recent ones)

It then tries to download a free full-text PDF for every paper. Papers without a free PDF get a Markdown file with their metadata and abstract, so they can still be indexed by the RAG pipeline. Everything is recorded in a manifest.

Metadata comes from [OpenAlex](https://openalex.org); missing abstracts fall back to Semantic Scholar.

## Setup

```bash
pip install -r requirements.txt
export OPENALEX_API_KEY=...   # free at https://openalex.org/settings/api
```

The key is optional but recommended: since February 2026 OpenAlex meters usage per day, and a free key gives ten times the keyless allowance. A run on three seeds uses a few dozen API calls, and repeat runs are served from a local cache.

## Usage

```bash
# 1. Dry run: resolve seeds and collect metadata, download nothing
python corpus_builder.py seeds.txt --out corpus --no-download

# 2. Look at corpus/manifest.csv, adjust seeds or limits, then run for real
python corpus_builder.py seeds.txt --out corpus
```

Options:

| Flag | Default | Meaning |
|---|---|---|
| `--max-citing N` | 50 | most-cited papers citing each seed (0 = no forward hop) |
| `--recent-citing N` | 0 | also add the N most recent citing papers per seed |
| `--no-download` | off | metadata only |
| `--no-s2` | off | skip the Semantic Scholar abstract fallback |
| `--s2-api-key` | `$S2_API_KEY` | optional Semantic Scholar key; avoids its shared rate limit |
| `--min-title-score` | 0.85 | how close a title seed must match (0–1) |

The forward hop is capped because popular papers have thousands of citations (Behler–Parrinello has well over a thousand). Most-cited gives you the established follow-up work; `--recent-citing` pulls in current work, at the cost of more noise.

## Seeds file

One paper per line: a DOI (most reliable), `arxiv:2101.03164`, an OpenAlex id (`W2042...`), or an exact title. Title matches are printed with their similarity score; check them, then swap in the DOI. For arXiv seeds, prefer the journal DOI when one exists: OpenAlex often keeps the preprint as a separate record with an incomplete reference list.

## Output

```
corpus/
  pdfs/W123.pdf          free full texts (verified to really be PDFs)
  abstracts/W456.md      metadata + abstract for papers without a free PDF
  manifest.csv           one row per paper, for a spreadsheet
  manifest.jsonl         same, plus abstracts and PDF candidate links
  manual.jsonl           PDFs and abstracts you added by hand (see below)
  .cache/                cached API responses (delete to refetch)
```

`status` in the manifest is one of:

- `pdf`: full text downloaded
- `abstract_only`: no free PDF, abstract saved
- `metadata_only`: no free PDF and no abstract found anywhere
- `not_downloaded`: dry run

`roles` says whether a paper is a seed, a reference, or citing (can be several), and `via_seeds` says which seed led to it. `note` explains why a download failed.

## Behavior worth knowing

- **Free sources only.** It uses open-access links that OpenAlex knows about, trying arXiv first. Nothing is fetched through paywalls.
- **Responses are checked.** Many "PDF links" serve a login or cookie page. Anything that doesn't start with `%PDF` is rejected rather than saved.
- **Preprint/journal duplicates are merged** by normalized title, keeping the published DOI and all PDF links from both records.
- **Missing abstracts are fetched in bulk.** Papers without an abstract in OpenAlex are looked up on Semantic Scholar in one batch request (up to 500 papers). Its keyless API is shared and often answers `429`; the script waits and retries, and if it still fails, the run continues without those abstracts. `429` lines in the log are not errors.
- **Rerunnable.** Downloaded PDFs are kept, API calls are cached, and the manifest is rebuilt each run. If a paper later gets a PDF, its abstract file is removed.
- **Polite.** At most one request per 3 s to arXiv and about one per second to other hosts. A run of a few hundred papers takes tens of minutes, mostly waiting on arXiv.
- **Manual additions survive reruns.** PDFs and abstracts you add yourself (in the app's Papers tab) are recorded in `manual.jsonl`, and every run re-applies them, so regenerating the manifest from OpenAlex never loses them. Their manifest rows have `added_manually` set to `pdf` and/or `abstract`.
- **Some publishers block scripts** even for open-access PDFs. Those papers end up as `abstract_only` with a note; add them with **Add PDF** in the app's Papers tab, which also updates the manifest and re-chunks the paper right away. (Dropping a file into `pdfs/` as `W....pdf` by hand also works, on the next run of this script and `parse_corpus.py`.)

## Tests

```bash
python -m pytest -q
```

The tests run offline against a fake HTTP session.

## Next step: parsing and chunking

See [INGEST.md](INGEST.md). In short: `python parse_corpus.py run` turns `corpus/` into `chunks/<parser>_<config>/chunks.jsonl`.

## Then: retrieval evaluation

See [EVAL.md](EVAL.md). Write questions in `questions/questions.yaml`, check them with `python evaluate.py check`, score with `python evaluate.py run`.
