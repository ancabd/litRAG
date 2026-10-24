#!/usr/bin/env python3
"""Retrieval and answer evaluation.

  check    validate a question file and show where each evidence quote lands in the chunks
  search   run one query and print the top chunks (useful while writing questions)
  run      score a retriever on the questions; writes data/runs/<name>/report.md
  ask      answer one question from the corpus, with citations (needs ANTHROPIC_API_KEY)
  answer   answer eval: generate answers for the questions and judge them
  compare  put several runs side by side

Examples:
  python evaluate.py check
  python evaluate.py search "radial symmetry function cutoff"
  python evaluate.py run
  python evaluate.py ask "What test system did Behler and Parrinello use?"
  python evaluate.py answer                         # claude-sonnet-5-5 answers, judged by the same model
  python evaluate.py answer --generator extractive --judge none     # no API key needed
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
from retrieval import available, get_retriever, load_chunks

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
    chunks = load_chunks(args.chunks)
    by_id = {c["chunk_id"]: c for c in chunks}
    r = get_retriever(args.retriever)
    r.index(chunks)
    for h in r.search(args.query, k=args.k):
        c = by_id[h.chunk_id]
        pages = f"p{c['page_start']}" if c.get("page_start") else c.get("source")
        print(f"\n#{h.rank}  {h.score:.2f}  {c['chunk_id']}  {(c.get('title') or '')[:70]} ({c.get('year')})")
        print(f"     {c['section'][:80]}  [{pages}]")
        print(textwrap.indent(textwrap.fill(c["text"][:args.chars], 100), "     "))
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
    return get_generator(args.generator, model=args.model, cache_dir=None if args.no_cache else paths.CACHE / "llm")


def cmd_ask(args) -> int:
    from generation import LLMNotConfigured, answer_question
    chunks = load_chunks(args.chunks)
    r = get_retriever(args.retriever)
    r.index(chunks)
    try:
        gen = _generator(args)
    except LLMNotConfigured as exc:
        print(exc)
        return 2
    ans = answer_question(args.question, r, {c["chunk_id"]: c for c in chunks}, gen, k=args.k)
    by_id = {c["chunk_id"]: c for c in chunks}
    print(textwrap.fill(ans.answer, 100) if ans.answerable else f"Not answerable from the corpus. {ans.answer}")
    if ans.citations:
        print("\nSources:")
        for i, cid in enumerate(ans.citations, 1):
            c = by_id[cid]
            print(f"  [{cid}] {c.get('title')} ({c.get('year')}), {c['section']}")
    for w in ans.warnings:
        print(f"note: {w}")
    cost = f", ${ans.cost:.4f}" if ans.cost else ""
    print(f"\n{ans.generator.get('model') or ans.generator['name']}, {ans.seconds:.1f}s"
          f"{', cached' if ans.cached else ''}{cost}", file=sys.stderr)
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
    s.add_argument("--retriever", default="bm25", choices=available())
    s.add_argument("-k", type=int, default=5)
    s.add_argument("--chars", type=int, default=400, help="characters of each chunk to show")

    r = sub.add_parser("run", help="score a retriever")
    common(r)
    r.add_argument("--retriever", default="bm25", choices=available())
    r.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    r.add_argument("-k", default=",".join(map(str, DEFAULT_KS)), help="cutoffs, e.g. 1,5,10,20")
    r.add_argument("--threshold", type=float, default=0.5)
    r.add_argument("--out", type=Path, default=paths.RUNS)
    r.add_argument("--name", default=None, help="run folder name (default: timestamp + config)")

    from generation.llm import DEFAULT_MODEL

    def gen_args(p):
        p.add_argument("--retriever", default="bm25", choices=available())
        p.add_argument("-k", type=int, default=8, help="passages given to the generator (default: 8)")
        p.add_argument("--generator", default="claude", choices=["claude", "extractive"])
        p.add_argument("--model", default=DEFAULT_MODEL, help=f"generator model (default: {DEFAULT_MODEL})")
        p.add_argument("--no-cache", action="store_true", help="always call the model (default: reuse cached responses)")

    a = sub.add_parser("ask", help="answer one question from the corpus")
    common(a, questions=False)
    a.add_argument("question")
    gen_args(a)

    an = sub.add_parser("answer", help="answer eval: generate and judge answers")
    common(an)
    gen_args(an)
    an.add_argument("--judge", default=DEFAULT_MODEL, help=f"judge model, or 'none' (default: {DEFAULT_MODEL})")
    an.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    an.add_argument("--out", type=Path, default=paths.RUNS)
    an.add_argument("--name", default=None)

    cp = sub.add_parser("compare", help="compare runs")
    cp.add_argument("runs", nargs="+", type=Path)

    args = ap.parse_args(argv)
    if args.cmd == "compare":
        print(compare_runs(args.runs))
        return 0
    return {"check": cmd_check, "search": cmd_search, "run": cmd_run, "ask": cmd_ask, "answer": cmd_answer}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
