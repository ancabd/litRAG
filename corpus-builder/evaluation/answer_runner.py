"""Answer eval: retrieve, generate, judge. Writes a run folder like the retrieval eval, with kind "answer".

runs/<timestamp>_answers_<generator>_<retriever>_<chunks>_<split>/
  report.md, summary.json, per_question.jsonl   (same files as retrieval runs)
  human.json                                    your verdicts, added from the app (judge validation)

Per question:
  correct                      judge: answer vs your reference answer (1 / 0.5 / 0)
  supported                    judge: are the answer's claims in the passages it cites (1 / 0.5 / 0)
  cites_gold                   does it cite one of your evidence passages (or an alternative)
  invalid_citations            did it cite a passage id it was never given
  retrieved_gold               was any evidence passage among the k passages it got
  abstained_when_unanswerable  said "not in the corpus" on an unanswerable question (want 1)
  abstained_when_answerable    said "not in the corpus" although the answer was there (want 0)

Groups add retrieval:found / retrieval:missed, which separate retrieval failures from generation failures.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from generation.answer import Generator, answer_question
from retrieval import get_retriever, load_chunks

from .judge import Judge
from .matching import GoldIndex
from .metrics import bootstrap_ci
from .questions import load_questions
from .runner import _git_commit, groups_of

METRICS = ["correct", "supported", "cites_gold", "retrieved_gold", "invalid_citations",
           "abstained_when_unanswerable", "abstained_when_answerable"]
HIGHER_IS_BETTER = {"invalid_citations": False, "abstained_when_answerable": False}


def _passage(c: dict) -> dict:
    return {k: c.get(k) for k in ("chunk_id", "paper_id", "title", "year", "section", "page_start", "text")}


def run_answer_eval(questions_path: Path, chunks_path: Path, generator: Generator, judge: Judge | None,
                    retriever_name: str = "bm25", split: str | None = "dev", k: int = 8,
                    out_root: Path | None = None, name: str | None = None, progress=None,
                    threshold: float = 0.5) -> Path:
    t0 = time.perf_counter()
    if out_root is None:
        import paths
        out_root = paths.RUNS
    questions = load_questions(questions_path)
    if split:
        questions = [q for q in questions if q.split == split]
    chunks = load_chunks(chunks_path)
    by_id = {c["chunk_id"]: c for c in chunks}
    gold = GoldIndex(chunks, threshold=threshold)
    retriever = get_retriever(retriever_name)
    retriever.index(chunks)

    rows, gen_cost, gen_in, gen_out = [], 0.0, 0, 0
    for i, q in enumerate(questions, 1):
        hits = retriever.search(q.question, k=k)
        ans = answer_question(q.question, retriever, by_id, generator, k=k, hits=hits)
        gen_cost += ans.cost or 0.0
        gen_in += ans.input_tokens
        gen_out += ans.output_tokens

        evidence = gold.resolve_question(q) if q.answerable else []
        lenient = set().union(*(e.lenient_chunks for e in evidence)) if evidence else set()
        not_rel = gold.resolve_passages(q.not_relevant)
        resolved = any(e.resolved for e in evidence)
        given = {p["chunk_id"] for p in ans.passages}
        m: dict[str, float | None] = {name: None for name in METRICS}
        judgments: dict[str, dict] = {}
        abstained = not ans.answerable
        if not q.answerable:
            m["abstained_when_unanswerable"] = float(abstained)
        else:
            m["abstained_when_answerable"] = float(abstained)
            if resolved:
                m["retrieved_gold"] = float(bool(lenient & given))
            if abstained:
                if q.answer and judge:  # without a judge, correctness isn't measured at all (not just for abstentions)
                    judgments["correctness"] = {"verdict": "incorrect", "score": 0.0,
                                                "reason": "declined to answer although the corpus has the answer"}
                    m["correct"] = 0.0
            else:
                m["invalid_citations"] = float(bool(ans.invalid_citations))
                if resolved:
                    m["cites_gold"] = float(bool(lenient & set(ans.citations)))
                if judge:
                    if q.answer:
                        judgments["correctness"] = judge.correctness(q.question, q.answer, ans.answer)
                        m["correct"] = judgments["correctness"]["score"]
                    judgments["support"] = judge.support(ans.answer, [_passage(by_id[c]) for c in ans.citations])
                    m["supported"] = judgments["support"]["score"]

        groups = groups_of(q)
        if q.answerable and resolved:
            groups.append("retrieval:found" if lenient & given else "retrieval:missed")
        rows.append({
            "id": q.id, "question": q.question, "type": q.type, "tags": q.tags, "groups": groups,
            "reference": q.answer,
            "answer": ans.to_dict(),
            "evidence": [{"paper": e.paper, "quote": e.quote, "gold_chunks": sorted(e.gold_chunks),
                          "alt_chunks": sorted(e.alt_chunks), "resolved": e.resolved} for e in evidence],
            "not_relevant_chunks": sorted(not_rel),
            "retrieved": [{"chunk_id": h.chunk_id, "score": round(h.score, 4), "rank": r}
                          for r, h in enumerate(hits[:k], 1)],
            "judgments": judgments,
            "metrics": m,
        })
        if progress:
            progress(i, len(questions))

    group_names = sorted({g for r in rows for g in r["groups"]}, key=lambda g: (g != "all", g))
    results = {}
    for g in group_names:
        sub = [r for r in rows if g in r["groups"]]
        results[g] = {}
        for metric in METRICS:
            vals = [r["metrics"][metric] for r in sub if r["metrics"][metric] is not None]
            if vals:
                mean, lo, hi = bootstrap_ci(vals)
                results[g][metric] = {"mean": mean, "lo": lo, "hi": hi, "n": len(vals)}

    chunks_dir = Path(chunks_path) if Path(chunks_path).is_dir() else Path(chunks_path).parent
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    gen_name = generator.config().get("model") or generator.config()["name"]
    run_dir = (Path(out_root) / (name or f"{stamp}_answers_{gen_name}_{retriever_name}_{chunks_dir.name}_{split or 'all'}")).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    no_reference = [r["id"] for r in rows if r["type"] != "unanswerable" and not r["reference"]]
    chunk_run = chunks_dir / "run.json"
    cc = json.loads(chunk_run.read_text()) if chunk_run.exists() else {}
    summary = {
        "kind": "answer",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(),
        "questions_file": str(Path(questions_path).resolve()),
        "questions_sha1": hashlib.sha1(Path(questions_path).read_bytes()).hexdigest()[:12],
        "split": split,
        "chunks": str(chunks_dir.resolve()),
        "chunks_config": {k_: cc.get(k_) for k_ in ("parser", "chunking", "chunks", "papers_by_source")} if cc else None,
        "retriever": retriever.config(),
        "k": k,
        "generator": generator.config(),
        "judge": judge.config() if judge else None,
        "n_questions": len(questions),
        "n_scored": len(rows),
        "no_reference_answer": no_reference,
        "excluded": [],
        "results": results,
        "usage": {
            "generator": {"input_tokens": gen_in, "output_tokens": gen_out, "cost": round(gen_cost, 4)},
            "judge": ({"input_tokens": judge.input_tokens, "output_tokens": judge.output_tokens,
                       "cost": round(judge.cost, 4)} if judge else None),
        },
        "timing": {"total_seconds": round(time.perf_counter() - t0, 1)},
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with open(run_dir / "per_question.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (run_dir / "report.md").write_text(render_answer_report(summary, rows), encoding="utf-8")
    return run_dir


LABELS = {
    "correct": "Correct (judge vs your reference)",
    "supported": "Supported by its citations",
    "cites_gold": "Cites your evidence",
    "retrieved_gold": "Evidence was retrieved",
    "invalid_citations": "Cites passages it wasn't given (lower is better)",
    "abstained_when_unanswerable": "Declines when unanswerable",
    "abstained_when_answerable": "Declines although answerable (lower is better)",
}


def render_answer_report(summary: dict, rows: list[dict]) -> str:
    res = summary["results"]
    g = summary["generator"]
    lines = [f"# Answer eval: {g.get('model') or g['name']}", "",
             f"- **Generator:** `{json.dumps(g)}`",
             f"- **Judge:** `{json.dumps(summary['judge'])}`" if summary["judge"] else "- **Judge:** none (deterministic metrics only)",
             f"- **Retrieval:** {summary['retriever']['name']}, top {summary['k']} from {Path(summary['chunks']).name}",
             f"- **Questions:** {summary['n_scored']} (split: {summary['split']}, file sha1 {summary['questions_sha1']})",
             f"- **Cost:** generator ${summary['usage']['generator']['cost']:.3f}"
             + (f", judge ${summary['usage']['judge']['cost']:.3f}" if summary["usage"]["judge"] else ""), ""]
    if summary["no_reference_answer"]:
        lines += [f"_No reference answer, so correctness isn't judged: {', '.join(summary['no_reference_answer'])}._", ""]
    a = res.get("all", {})
    lines += ["## Overall", "", "| metric | value | n |", "|---|---|---|"]
    for m in METRICS:
        if m in a:
            v = a[m]
            lines.append(f"| {LABELS[m]} | {v['mean']:.2f} [{v['lo']:.2f}, {v['hi']:.2f}] | {v['n']} |")
    for grp in ("retrieval:found", "retrieval:missed"):
        if grp in res and "correct" in res[grp]:
            v = res[grp]["correct"]
            lines.append(f"\nCorrect when {'the evidence was' if grp.endswith('found') else 'no evidence was'} "
                         f"retrieved: {v['mean']:.2f} (n={v['n']})")
    lines += ["", "## Answers", ""]
    for r in rows:
        c = r["judgments"].get("correctness", {})
        s = r["judgments"].get("support", {})
        lines.append(f"**{r['id']}** ({r['type']}): {r['question']}")
        lines.append(f"- answer: {r['answer']['answer']}")
        if r["reference"]:
            lines.append(f"- reference: {r['reference']}")
        if c:
            lines.append(f"- correctness: {c.get('verdict')} ({c.get('reason')})")
        if s:
            lines.append(f"- support: {s.get('verdict')} ({s.get('reason')})")
        lines.append("")
    return "\n".join(lines) + "\n"
