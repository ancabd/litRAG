#!/usr/bin/env python3
"""Retrieval and answer evaluation.

  check    validate a question file and show where each evidence quote lands in the chunks
  search   run one query and print the top chunks (useful while writing questions)
  run      score a retriever on the questions; writes data/runs/<name>/report.md
  ask      answer one question from the corpus, with citations (needs ANTHROPIC_API_KEY)
  answer   answer eval: generate answers for the questions and judge them
  index    build (and cache) the embeddings for dense / hybrid retrieval, with progress
  compare  put several runs side by side

Retrievers: bm25 (default), dense, dense:bge-small, hybrid, hybrid:bge-small  (dense needs
requirements-dense.txt; the first use of a model embeds the corpus, later uses read the cache)

Examples:
  python evaluate.py check
  python evaluate.py search "radial symmetry function cutoff"
  python evaluate.py run
  python evaluate.py index --retriever dense            # embed the corpus once (a few minutes on a CPU)
  python evaluate.py run --retriever hybrid
  python evaluate.py ask "What test system did Behler and Parrinello use?"
  python evaluate.py ask --generator agent "Which cutoff radius does NequIP use, and how does it compare to SchNet?"
  python evaluate.py answer                         # claude-sonnet-5-5 answers, judged by the same model
  python evaluate.py answer --generator extractive --judge none     # no API key needed
  python evaluate.py answer --generator agent --model claude-haiku-5-5 --judge claude-sonnet-5-5
  python evaluate.py compare data/runs/A data/runs/B
"""
from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

import paths
from evaluation.matching import GoldIndex
from evaluation.questions import QuestionFileError, load_questions
from evaluation.runner import DEFAULT_KS, compare_runs, run_eval
from retrieval import choices as retriever_choices
from retrieval import is_known, load_chunks

DEFAULT_QUESTIONS = paths.QUESTIONS
DEFAULT_CHUNKS = paths.default_chunk_run()


def cmd_check(args) -> int:
    try:
        questions = load_questions(args.questions)
    except QuestionFileError as exc:
        print(f"Question file has errors:\n{exc}")
        return 1
    chunks = load_chunks(args.chunks)
    gold = GoldIndex(chunks, threshold=args.threshold)
    n_ok, problems = 0, 0
    counts: dict[str, int] = {}
    for q in questions:
        counts[f"{q.split}/{q.type}"] = counts.get(f"{q.split}/{q.type}", 0) + 1
        if not q.answerable:
            n_ok += 1
            continue
        lines, bad = [], False
        for ev in q.evidence:
            r = gold.resolve(ev)
            if r.resolved:
                c = next(c for c in gold.by_paper[ev.paper] if c["chunk_id"] in r.gold_chunks)
                lines.append(f"    ok  {ev.paper} -> {', '.join(sorted(r.gold_chunks))}  ({c['section'][:50]}; {r.paper_source})")
            elif not r.paper_in_corpus:
                bad = True
                lines.append(f"    !!  {ev.paper}: paper not in these chunks (wrong id, or metadata-only?)")
            elif not ev.quote:
                bad = True
                lines.append(f"    !!  {ev.paper}: no quote given; add a short passage so the gold chunk can be found")
            else:
                bad = True
                lines.append(f"    !!  {ev.paper}: quote not found ({r.paper_source}). Closest chunks:")
                for cov, c in gold.best_matches(ev):
                    lines.append(f"          {cov:.0%} of quote in {c['chunk_id']} ({c['section'][:40]}): "
                                 f"{c['text'][:110]}...")
            if ev.alternatives:
                lines.append(f"        alternatives: {len(ev.alternatives) - len(r.unresolved_alternatives)} of "
                             f"{len(ev.alternatives)} found")
                for a in r.unresolved_alternatives:
                    bad = True
                    lines.append(f"    !!  alternative not found (typo, or the paper's chunks changed): {a}")
        if q.not_relevant:
            missing = [p for p in q.not_relevant if not gold.resolve_passages([p])]
            if missing:
                lines.append(f"    note: {len(missing)} not-relevant judgment(s) no longer match a chunk")
        if bad or args.verbose:
            print(f"{'!!' if bad else 'ok'} {q.id} [{q.split}/{q.type}] {q.question[:90]}")
            print("\n".join(lines))
        problems += bad
        n_ok += not bad
    print(f"\n{len(questions)} questions: {n_ok} ok, {problems} with evidence problems")
    print("By split/type: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 1 if problems else 0


def cmd_search(args) -> int:
    from library import Library
    library = Library.load(args.chunks)
    for h in library.search(args.query, k=args.k, retriever=args.retriever, paper=args.paper):
        c = library.chunk(h.chunk_id)
        pages = f"p{c['page_start']}" if c.get("page_start") else c.get("source")
        print(f"\n#{h.rank}  {h.score:.2f}  {c['chunk_id']}  {(c.get('title') or '')[:70]} ({c.get('year')})")
        print(f"     {c['section'][:80]}  [{pages}]")
        print(textwrap.indent(textwrap.fill(c["text"][:args.chars], 100), "     "))
    return 0


def retriever_name(value: str) -> str:
    """argparse type: any registered retriever, with an optional model after a colon."""
    if not is_known(value):
        names = ", ".join(c["name"] for c in retriever_choices())
        raise argparse.ArgumentTypeError(f"unknown retriever {value!r} (try: {names}, or dense:<huggingface id>)")
    return value


def cmd_index(args) -> int:
    from library import Library
    from retrieval import build_retriever
    import time
    library = Library.load(args.chunks)

    def progress(done, total):
        print(f"\r  embedded {done}/{total} chunks", end="", file=sys.stderr, flush=True)

    t0 = time.perf_counter()
    try:
        r = build_retriever(args.retriever, library.chunks, library.embeddings_dir, progress=progress)
    except RuntimeError as exc:
        print(exc)
        return 2
    print(file=sys.stderr)
    dense = getattr(r, "dense", r)
    st = getattr(r, "stats", {}) or {}
    print(f"{args.retriever} on {library.name}: {st.get('chunks', len(library))} chunks, "
          f"{st.get('embedded_now', 0)} embedded now, {st.get('from_cache', 0)} from the cache, "
          f"{time.perf_counter() - t0:.0f}s")
    if hasattr(dense, "truncated"):
        n = dense.truncated(library.chunks)
        if n:
            print(f"note: {n} of {len(library)} chunks are longer than {dense.preset.max_tokens} tokens; "
                  "the model only reads their beginning (a smaller chunk size avoids this)")
    if args.query:
        for h in library.search(args.query, k=5, retriever=args.retriever):
            c = library.chunk(h.chunk_id)
            print(f"  #{h.rank} {h.score:.3f} {c['chunk_id']} {(c.get('title') or '')[:60]}")
    return 0


def cmd_run(args) -> int:
    try:
        ks = tuple(sorted({int(k) for k in args.k.split(",")} | {10}))
        run_dir = run_eval(args.questions, args.chunks, args.retriever, None if args.split == "all" else args.split,
                           ks, args.out, threshold=args.threshold, name=args.name)
    except QuestionFileError as exc:
        print(f"Question file has errors:\n{exc}")
        return 1
    print((run_dir / "report.md").read_text())
    print(f"Run saved to {run_dir}", file=sys.stderr)
    return 0


def _generator(args):
    from generation import get_generator
    options = {}
    if args.generator == "agent":
        options = {"max_turns": args.max_turns, "token_budget": args.token_budget}
        if args.tools:
            options["tools"] = tuple(t.strip() for t in args.tools.split(",") if t.strip())
    return get_generator(args.generator, model=args.model, cache_dir=None if args.no_cache else paths.CACHE / "llm",
                         **options)


def _short(v, n: int = 70) -> str:
    v = v if isinstance(v, str) else ", ".join(f"{k}={x}" for k, x in v.items())
    return v if len(v) <= n else v[: n - 1] + "…"


def print_trace(ans, file=None) -> None:
    """One line per step: what it did, what came back, tokens and time."""
    file = file or sys.stderr
    for s in ans.trace:
        args = dict(s["input"])
        main = args.pop("query", None) or args.pop("chunk_id", None) or args.pop("paper_id", None)
        what = f'"{_short(main, 60)}"' if s["action"] == "search" else (_short(main) if main else "")
        if args and s["action"] not in ("answer", "give_up"):
            what += f" ({_short(args, 40)})"
        if s["action"] in ("answer", "give_up"):
            what = ""
        tokens = f"{s['input_tokens']:,} in / {s['output_tokens']:,} out" if s["input_tokens"] else ""
        if s.get("cache_read_tokens"):
            tokens += f" ({s['cache_read_tokens']:,} cached)"
        note = f"-> {s['note']}" if s.get("note") else ""
        print(f"  {s['step']:>2}. {s['action']:<12}{what} {note}".rstrip() + (f"   [{tokens}, {s['seconds']:.1f}s]" if tokens else ""),
              file=file)
        if s.get("thought"):
            print(textwrap.indent(textwrap.fill(s["thought"], 96), "      | "), file=file)


def cmd_ask(args) -> int:
    from generation import LLMNotConfigured
    from library import Library
    library = Library.load(args.chunks)
    try:
        gen = _generator(args)
    except LLMNotConfigured as exc:
        print(exc)
        return 2
    ans = gen.answer(args.question, library, k=args.k, retriever=args.retriever)
    by_id = library.by_id
    if args.generator == "agent" or args.trace:
        print("Steps:", file=sys.stderr)
        print_trace(ans)
        print(file=sys.stderr)
    text = ans.answer if ans.answerable else f"Not answerable from the corpus. {ans.answer}"
    # wrap each paragraph, keep the model's line breaks
    print("\n".join(textwrap.fill(line, 100) if line.strip() else "" for line in text.splitlines()))
    if ans.citations:
        print("\nSources:")
        for i, cid in enumerate(ans.citations, 1):
            c = by_id[cid]
            print(f"  [{cid}] {c.get('title')} ({c.get('year')}), {c['section']}")
    for w in ans.warnings:
        print(f"note: {w}")
    cost = f", ${ans.cost:.4f}" if ans.cost else ""
    read = f" ({ans.cache_read_tokens:,} from the prompt cache)" if ans.cache_read_tokens else ""
    tokens = f", {ans.input_tokens:,} input tokens{read}" if ans.input_tokens else ""
    print(f"\n{ans.generator.get('model') or ans.generator['name']}, {len(ans.passages)} passages read, "
          f"{ans.seconds:.1f}s{tokens}{', cached' if ans.cached else ''}{cost}", file=sys.stderr)
    return 0


def cmd_answer(args) -> int:
    from evaluation.answer_runner import run_answer_eval
    from evaluation.judge import Judge
    from generation import LLMNotConfigured
    from generation.llm import make_llm
    try:
        gen = _generator(args)
        judge = None if args.judge == "none" else Judge(make_llm(args.judge, None if args.no_cache else paths.CACHE / "llm"))
    except LLMNotConfigured as exc:
        print(exc)
        return 2

    def progress(done, total):
        print(f"\r  {done}/{total} questions", end="", file=sys.stderr, flush=True)

    try:
        run_dir = run_answer_eval(args.questions, args.chunks, gen, judge, args.retriever,
                                  None if args.split == "all" else args.split, args.k, args.out,
                                  name=args.name, progress=progress)
    except QuestionFileError as exc:
        print(f"Question file has errors:\n{exc}")
        return 1
    print(file=sys.stderr)
    print((run_dir / "report.md").read_text())
    print(f"Run saved to {run_dir}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, questions=True):
        if questions:
            p.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS, help=f"default: {DEFAULT_QUESTIONS}")
        p.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS, help=f"default: {DEFAULT_CHUNKS}")

    c = sub.add_parser("check", help="validate questions and locate their evidence")
    common(c)
    c.add_argument("--threshold", type=float, default=0.5, help="fraction of the quote a gold chunk must contain")
    c.add_argument("-v", "--verbose", action="store_true", help="also list questions without problems")

    s = sub.add_parser("search", help="query the chunks")
    common(s, questions=False)
    s.add_argument("query")
    s.add_argument("--retriever", default="bm25", type=retriever_name, help="bm25, dense, dense:bge-small, hybrid, hybrid:bge-small")
    s.add_argument("-k", type=int, default=5)
    s.add_argument("--chars", type=int, default=400, help="characters of each chunk to show")
    s.add_argument("--paper", help="only search this paper (OpenAlex id)")

    r = sub.add_parser("run", help="score a retriever")
    common(r)
    r.add_argument("--retriever", default="bm25", type=retriever_name, help="bm25, dense, dense:bge-small, hybrid, hybrid:bge-small")
    r.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    r.add_argument("-k", default=",".join(map(str, DEFAULT_KS)), help="cutoffs, e.g. 1,5,10,20")
    r.add_argument("--threshold", type=float, default=0.5)
    r.add_argument("--out", type=Path, default=paths.RUNS)
    r.add_argument("--name", default=None, help="run folder name (default: timestamp + config)")

    from generation.answer import available_generators
    from generation.llm import DEFAULT_MODEL

    def gen_args(p):
        p.add_argument("--retriever", default="bm25", type=retriever_name, help="bm25, dense, dense:bge-small, hybrid, hybrid:bge-small")
        p.add_argument("-k", type=int, default=8, help="passages per search (default: 8)")
        p.add_argument("--generator", default="claude", choices=available_generators())
        p.add_argument("--model", default=DEFAULT_MODEL, help=f"generator model (default: {DEFAULT_MODEL})")
        p.add_argument("--no-cache", action="store_true", help="always call the model (default: reuse cached responses)")
        p.add_argument("--max-turns", type=int, default=8, help="agent: most model calls per question (default: 8)")
        p.add_argument("--token-budget", type=int, default=100_000,
                       help="agent: most tokens per question over all turns (default: 100000)")
        p.add_argument("--tools", help="agent: comma-separated tools (default: search,read_around,open_paper)")

    a = sub.add_parser("ask", help="answer one question from the corpus")
    common(a, questions=False)
    a.add_argument("question")
    gen_args(a)
    a.add_argument("--trace", action="store_true", help="print the steps (always on for the agent)")

    an = sub.add_parser("answer", help="answer eval: generate and judge answers")
    common(an)
    gen_args(an)
    an.add_argument("--judge", default=DEFAULT_MODEL, help=f"judge model, or 'none' (default: {DEFAULT_MODEL})")
    an.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    an.add_argument("--out", type=Path, default=paths.RUNS)
    an.add_argument("--name", default=None)

    ix = sub.add_parser("index", help="build the embedding cache for dense / hybrid retrieval")
    common(ix, questions=False)
    ix.add_argument("--retriever", default="dense", type=retriever_name)
    ix.add_argument("--query", help="also run this query and print the top 5, as a quick check")

    cp = sub.add_parser("compare", help="compare runs")
    cp.add_argument("runs", nargs="+", type=Path)

    args = ap.parse_args(argv)
    if args.cmd == "compare":
        print(compare_runs(args.runs))
        return 0
    return {"check": cmd_check, "search": cmd_search, "run": cmd_run, "ask": cmd_ask, "answer": cmd_answer,
            "index": cmd_index}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
