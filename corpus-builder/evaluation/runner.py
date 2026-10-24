"""Run a retrieval eval and write a self-describing run folder.

runs/<timestamp>_<retriever>_<chunks>_<split>/
  report.md            human-readable results: overall, by type and tag, misses
  summary.json         all aggregate numbers plus the full config
  per_question.jsonl   every question: gold chunks, retrieved chunks, metrics
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from retrieval import get_retriever, load_chunks

from .matching import GoldIndex
from .metrics import aggregate, question_metrics
from .questions import Question, load_questions

DEFAULT_KS = (1, 3, 5, 10, 20)
HEADLINE = ["hit@1", "hit@5", "hit@10", "recall@10", "mrr", "ndcg@10", "paper_hit@10"]
BREAKDOWN = ["hit@5", "lenient_hit@5", "mrr", "lenient_mrr"]
LENIENT = "lenient_"


def _git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5)
        dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _fmt(m: dict) -> str:
    return f"{m['mean']:.3f} [{m['lo']:.2f}, {m['hi']:.2f}]"


def groups_of(q: Question) -> list[str]:
    return ["all", f"type:{q.type}"] + [f"tag:{t}" for t in q.tags]


def run_eval(questions_path: Path, chunks_path: Path, retriever_name: str = "bm25",
             split: str | None = "dev", ks: tuple[int, ...] = DEFAULT_KS, out_root: Path | None = None,
             retriever_options: dict | None = None, threshold: float = 0.5, name: str | None = None) -> Path:
    t0 = time.perf_counter()
    if out_root is None:
        import paths
        out_root = paths.RUNS
    questions = load_questions(questions_path)
    if split:
        questions = [q for q in questions if q.split == split]
    chunks = load_chunks(chunks_path)
    chunk_paper = {c["chunk_id"]: c["paper_id"] for c in chunks}
    chunk_by_id = {c["chunk_id"]: c for c in chunks}
    gold = GoldIndex(chunks, threshold=threshold)

    retriever = get_retriever(retriever_name, **(retriever_options or {}))
    t_index = time.perf_counter()
    retriever.index(chunks)
    index_seconds = time.perf_counter() - t_index

    rows, excluded, query_times = [], [], []
    for q in questions:
        if not q.answerable:
            excluded.append({"id": q.id, "reason": "unanswerable (scored in the answer eval, not here)"})
            continue
        evidence = gold.resolve_question(q)
        if not any(e.resolved for e in evidence):
            excluded.append({"id": q.id, "reason": "no evidence quote matched any chunk; run `evaluate.py check`"})
            continue
        tq = time.perf_counter()
        hits = retriever.search(q.question, k=max(ks))
        query_times.append(time.perf_counter() - tq)
        strict = question_metrics(hits, chunk_paper, evidence, ks)
        lenient = question_metrics(hits, chunk_paper, evidence, ks, lenient=True)
        not_rel = gold.resolve_passages(q.not_relevant)
        judged = set().union(*(e.lenient_chunks for e in evidence)) | not_rel
        top10 = [h.chunk_id for h in hits[:10]]
        metrics = {**strict, **{LENIENT + k: v for k, v in lenient.items()},
                   "judged@10": sum(c in judged for c in top10) / len(top10) if top10 else 1.0}
        rows.append({
            "id": q.id, "question": q.question, "type": q.type, "tags": q.tags, "groups": groups_of(q),
            "evidence": [{"paper": e.paper, "quote": e.quote, "gold_chunks": sorted(e.gold_chunks),
                          "alt_chunks": sorted(e.alt_chunks), "unresolved_alternatives": e.unresolved_alternatives,
                          "resolved": e.resolved, "paper_source": e.paper_source} for e in evidence],
            "not_relevant_chunks": sorted(not_rel),
            "partially_resolved": not all(e.resolved for e in evidence),
            "retrieved": [{"chunk_id": h.chunk_id, "score": round(h.score, 4), "rank": h.rank} for h in hits],
            "metrics": metrics,
        })

    base_names = [f"{m}@{k}" for m in ("hit", "recall", "paper_hit") for k in ks] + ["mrr", "ndcg@10"]
    metric_names = base_names + [LENIENT + m for m in base_names] + ["judged@10"]
    group_names = sorted({g for r in rows for g in r["groups"]}, key=lambda g: (g != "all", g))
    by_group = {g: aggregate([r for r in rows if g in r["groups"]], metric_names) for g in group_names}

    chunks_dir = Path(chunks_path) if Path(chunks_path).is_dir() else Path(chunks_path).parent
    chunk_run = chunks_dir / "run.json"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = (out_root / (name or f"{stamp}_{retriever_name}_{chunks_dir.name}_{split or 'all'}")).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(),
        "questions_file": str(Path(questions_path).resolve()),
        "questions_sha1": hashlib.sha1(Path(questions_path).read_bytes()).hexdigest()[:12],
        "split": split,
        "chunks": str(chunks_dir.resolve()),
        "chunks_config": json.loads(chunk_run.read_text()) if chunk_run.exists() else None,
        "retriever": retriever.config(),
        "match_threshold": threshold,
        "ks": list(ks),
        "n_questions": len(questions),
        "n_scored": len(rows),
        "excluded": excluded,
        "results": by_group,
        "timing": {"index_seconds": round(index_seconds, 3),
                   "mean_query_ms": round(1000 * sum(query_times) / max(len(query_times), 1), 2),
                   "total_seconds": round(time.perf_counter() - t0, 2)},
    }
    summary["chunks_config"] = summary["chunks_config"] and {
        k: summary["chunks_config"].get(k) for k in ("parser", "chunking", "chunks", "papers_by_source")}

    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with open(run_dir / "per_question.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    report = render_report(summary, rows, chunk_by_id)
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    return run_dir


def render_report(summary: dict, rows: list[dict], chunk_by_id: dict[str, dict]) -> str:
    res = summary["results"]
    ret = summary["retriever"]
    cc = summary.get("chunks_config") or {}
    lines = [
        f"# Retrieval eval: {ret['name']}",
        "",
        f"- **Retriever:** `{json.dumps(ret)}`",
        f"- **Chunks:** {Path(summary['chunks']).name} (parser {cc.get('parser', '?')})",
        f"- **Questions:** {summary['n_scored']} scored of {summary['n_questions']} "
        f"(split: {summary['split']}, file sha1 {summary['questions_sha1']})",
        f"- **Commit:** {summary['git_commit'] or 'not a git repo'}   **Created:** {summary['created']}",
        f"- **Speed:** index {summary['timing']['index_seconds']}s, {summary['timing']['mean_query_ms']} ms/query",
        "",
    ]
    if "all" not in res:
        lines.append("_No questions could be scored. Run `python evaluate.py check` to see why._")
        return "\n".join(lines)

    a = res["all"]
    n_alt = sum(bool(e["alt_chunks"]) for r in rows for e in r["evidence"])
    lines += ["## Overall", "",
              "Mean with 95% bootstrap CI over questions. **Strict** counts only the original evidence; "
              "**lenient** also accepts the alternative passages you marked "
              f"({n_alt} evidence item{'s have' if n_alt != 1 else ' has'} alternatives).", "",
              "| metric | strict | lenient |", "|---|---|---|"]
    lines += [f"| {m} | {_fmt(a[m])} | {_fmt(a[LENIENT + m]) if LENIENT + m in a else '-'} |"
              for m in HEADLINE if m in a]  # only cutoffs that were computed (-k)
    j = a.get("judged@10")
    if j:
        lines += ["", f"**judged@10: {j['mean']:.2f}**, the share of each question's top 10 that you have judged "
                      "(evidence, alternative or not relevant). "
                  + ("Below ~0.5, unjudged passages may still answer questions, so even the lenient score can "
                     "undercount; review them in the app." if j["mean"] < 0.5 else
                     "High enough that the lenient score is a fair picture.")]

    breakdown = [m for m in BREAKDOWN if m in a] or [m for m in ("mrr", LENIENT + "mrr") if m in a]
    lines += ["", "## By question type and tag", "",
              "| group | n | " + " | ".join(breakdown) + " |", "|---|---|" + "---|" * len(breakdown)]
    for g, r in res.items():
        if g == "all":
            continue
        n = r[breakdown[0]]["n"]
        cells = " | ".join(f"{r[m]['mean']:.2f}" for m in breakdown)
        lines.append(f"| {g} | {n} | {cells} |")
    small = [g for g, r in res.items() if g != "all" and r[breakdown[0]]["n"] < 10]
    if small:
        lines += ["", f"_Groups with fewer than 10 questions ({', '.join(small)}) are anecdotal; "
                      "don't read much into differences there._"]

    rescued = [r["id"] for r in rows if r["metrics"]["hit@10"] == 0 and r["metrics"].get(LENIENT + "hit@10")]
    if rescued:
        lines += ["", f"**Found only through alternatives** (strict miss, lenient hit): {', '.join(rescued)}. "
                      "The retriever found a passage that answers the question, but not the original source."]

    misses = [r for r in rows if r["metrics"].get(LENIENT + "hit@10", r["metrics"]["hit@10"]) == 0]
    lines += ["", f"## Misses: nothing acceptable in the top 10 ({len(misses)})", "",
              "Unjudged passages listed here are worth reviewing in the app: they may answer the question.", ""]
    for r in misses:
        gold_where = "; ".join(
            f"{chunk_by_id[g].get('title', g)[:60]} › {chunk_by_id[g]['section'][:40]}"
            for e in r["evidence"] for g in e["gold_chunks"][:1])
        lines.append(f"**{r['id']}** ({r['type']}{', ' + ', '.join(r['tags']) if r['tags'] else ''}): {r['question']}")
        lines.append(f"- gold: {gold_where}")
        judged_nr = set(r.get("not_relevant_chunks", []))
        for h in r["retrieved"][:3]:
            c = chunk_by_id[h["chunk_id"]]
            mark = " (judged not relevant)" if h["chunk_id"] in judged_nr else " (unjudged)"
            lines.append(f"- got #{h['rank']}: {(c.get('title') or c['paper_id'])[:60]} › {c['section'][:40]}{mark}")
        lines.append("")

    partial = [r["id"] for r in rows if r["partially_resolved"]]
    bad_alts = [(r["id"], a) for r in rows for e in r["evidence"] for a in e.get("unresolved_alternatives", [])]
    if partial or summary["excluded"] or bad_alts:
        lines += ["## Data issues", ""]
        if partial:
            lines.append(f"- Some evidence quotes didn't match, scored on the rest: {', '.join(partial)}")
        for qid, a in bad_alts:
            lines.append(f"- {qid}: alternative didn't match any chunk, ignored: {a}")
        for e in summary["excluded"]:
            lines.append(f"- {e['id']} excluded: {e['reason']}")
    return "\n".join(lines) + "\n"


def compare_runs(run_dirs: list[Path], metrics: list[str] | None = None) -> str:
    summaries = [json.loads((Path(d) / "summary.json").read_text()) for d in run_dirs]
    if metrics is None:
        if all(s.get("kind") == "answer" for s in summaries):
            from .answer_runner import METRICS as ANSWER_METRICS
            metrics = ANSWER_METRICS
        else:
            metrics = HEADLINE + [LENIENT + m for m in ("hit@5", "hit@10", "mrr")] + ["judged@10"]
    names = [Path(d).name for d in run_dirs]
    hashes = {s["questions_sha1"] for s in summaries}
    out = ["| metric | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for m in metrics:
        out.append(f"| {m} | " + " | ".join(_fmt(s["results"]["all"][m]) if m in s["results"].get("all", {}) else "-"
                                           for s in summaries) + " |")
    if len(hashes) > 1:
        out.append("\n**Warning:** these runs used different question files; numbers are not comparable.")
    from .paired import format_paired, paired_compare
    for d, name in zip(run_dirs[1:], names[1:]):
        out += ["", format_paired(names[0], name, paired_compare(Path(run_dirs[0]), Path(d), metrics))]
    effort = [s.get("effort") for s in summaries]
    if any(effort):
        keys = ["turns", "searches", "passages_read", "input_tokens", "cost", "seconds"]
        out += ["", "Effort per question (mean):", "", "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
        for k in keys:
            out.append(f"| {k} | " + " | ".join(_effort_cell(e, k) for e in effort) + " |")
    return "\n".join(out)


def _effort_cell(effort: dict | None, key: str) -> str:
    if not effort or effort.get(key) is None:
        return "-"
    v = effort[key]
    return f"${v:.4f}" if key == "cost" else (f"{v:,.0f}" if key == "input_tokens" else f"{v:.1f}")
