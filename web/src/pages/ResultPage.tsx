import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useEval } from "../api/hooks";
import type { EvalHit, EvalQuestion, Interval } from "../api/types";
import { ScoreChart } from "../components/ScoreChart";
import { ErrorBanner, Highlighted, pages, Seg, TYPE_LABEL } from "../components/ui";
import { when } from "./ResultsPage";

const HEADLINE = ["hit@1", "hit@5", "hit@10", "recall@10", "mrr", "ndcg@10", "paper_hit@10"];

type Outcome = "found" | "via-alternative" | "missed";

export function outcome(q: { strict_rank: number | null; lenient_rank: number | null }, k = 10): Outcome {
  if (q.strict_rank != null && q.strict_rank <= k) return "found";
  if (q.lenient_rank != null && q.lenient_rank <= k) return "via-alternative";
  return "missed";
}

export function OutcomeLabel({ q }: { q: { strict_rank: number | null; lenient_rank: number | null } }) {
  const o = outcome(q);
  if (o === "found")
    return (
      <span className="pill ok">
        Found at #{q.strict_rank}
        {q.lenient_rank != null && q.lenient_rank < q.strict_rank! && `, alternative at #${q.lenient_rank}`}
      </span>
    );
  if (o === "via-alternative") return <span className="pill accent">Alternative at #{q.lenient_rank}</span>;
  return <span className="pill warn">Not in top 10</span>;
}

const KIND_LABEL: Record<string, string> = {
  evidence: "Your evidence",
  alternative: "Alternative",
  not_relevant: "Judged not relevant",
  unjudged: "Not reviewed",
};

function Hit({ h }: { h: EvalHit }) {
  const [open, setOpen] = useState(false);
  const k = h.label.kind;
  return (
    <li className={`hit hit-${k}`}>
      <span className="hit-rank">#{h.rank}</span>
      <div className="hit-body">
        <div className="row" style={{ gap: 6 }}>
          <span className={`pill ${k === "evidence" ? "ok" : k === "alternative" ? "accent" : ""}`}>{KIND_LABEL[k]}</span>
          {h.paper_id ? (
            <Link to={`/papers/${h.paper_id}`} className="small paper-title">
              {h.title ?? h.paper_id}
            </Link>
          ) : (
            <span className="id">{h.chunk_id}</span>
          )}
          {h.section && <span className="muted xs">{h.section}{pages(h as never) && `, ${pages(h as never)}`}</span>}
        </div>
        {h.text && (
          <p className={`prose hit-text ${open ? "" : "clamped"}`} onClick={() => setOpen((v) => !v)} title={open ? "" : "Click to read all"}>
            <Highlighted text={h.text} />
          </p>
        )}
      </div>
    </li>
  );
}

function QuestionRow({ q }: { q: EvalQuestion }) {
  const [open, setOpen] = useState(false);
  return (
    <li className="eval-q">
      <button type="button" className="eval-q-head" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        <span className="id">{q.id}</span>
        <span className="eval-q-text">{q.question}</span>
        <OutcomeLabel q={q} />
      </button>
      {open && (
        <div className="eval-q-detail">
          <div className="row small" style={{ marginBottom: 8 }}>
            <span className="muted">
              {TYPE_LABEL[q.type] ?? q.type}
              {q.tags.length > 0 && `, ${q.tags.join(", ")}`}
            </span>
            <span className="spacer" />
            <Link to={`/questions/${q.id}`} className="btn small">
              Open question
            </Link>
          </div>
          <ol className="hits">
            {q.retrieved.slice(0, 10).map((h) => (
              <Hit key={h.chunk_id} h={h} />
            ))}
          </ol>
          {q.retrieved.some((h) => h.label.kind === "unjudged") && (
            <p className="xs muted" style={{ marginTop: 8 }}>
              Passages marked "Not reviewed" may answer the question too. Review them from the question page, then rerun.
            </p>
          )}
        </div>
      )}
    </li>
  );
}

export function ResultPage() {
  const { name } = useParams();
  const run = useEval(name);
  const [filter, setFilter] = useState<"all" | "missed" | "via-alternative" | "found">("all");
  const [showReport, setShowReport] = useState(false);
  if (run.error)
    return (
      <div className="page">
        <ErrorBanner error={run.error} />
        <Link to="/results">Back to results</Link>
      </div>
    );
  const r = run.data;
  if (!r) return null;
  const results = r.summary.results;
  const all = results.all ?? {};
  const judged: Interval | undefined = all["judged@10"];
  const groups = Object.keys(results).filter((g) => g !== "all");
  const count = (o: Outcome) => r.questions.filter((q) => outcome(q) === o).length;
  const shown = r.questions.filter((q) => filter === "all" || outcome(q) === filter);

  return (
    <div className="page">
      <Link to="/results" className="back">
        Back to results
      </Link>
      <div className="page-head">
        <div>
          <h1>Eval run, {when(r.created)}</h1>
          <p className="sub">
            {r.retriever?.name} on {r.chunks} ({r.parser}), {r.split} split, {r.n_scored} of {r.n_questions} questions scored
            {r.git_commit && `, commit ${r.git_commit}`}
          </p>
        </div>
      </div>

      {r.n_scored === 0 ? (
        <div className="banner">No questions could be scored. Check them on the Questions tab: every answerable question needs evidence that matches a chunk.</div>
      ) : (
        <>
          <ScoreChart results={all} metrics={HEADLINE} />
          {judged && (
            <p className={`small ${judged.mean < 0.5 ? "judged-low" : "muted"}`} style={{ marginTop: 10, maxWidth: "80ch" }}>
              You have judged {Math.round(judged.mean * 100)}% of each question's top 10 on average.{" "}
              {judged.mean < 0.5
                ? "Unreviewed passages may still answer questions, so even the lenient score can undercount."
                : "That's enough for the lenient score to be a fair picture."}
            </p>
          )}
          {r.n_scored < 20 && (
            <p className="small muted" style={{ maxWidth: "80ch" }}>
              With {r.n_scored} question{r.n_scored === 1 ? "" : "s"} the intervals are wide; differences between runs need to be large to mean anything.
            </p>
          )}
        </>
      )}

      {groups.length > 0 && (
        <section className="section-block">
          <h2>By question type and tag</h2>
          <div className="table-wrap" style={{ marginTop: 10 }}>
            <table className="data static">
              <thead>
                <tr>
                  <th>Group</th>
                  <th className="num">n</th>
                  <th className="num">Hit@5 strict</th>
                  <th className="num">Hit@5 lenient</th>
                  <th className="num">MRR strict</th>
                  <th className="num">MRR lenient</th>
                </tr>
              </thead>
              <tbody>
                {groups.map((g) => {
                  const row = results[g];
                  const v = (m: string) => (row[m] ? row[m].mean.toFixed(2) : "");
                  return (
                    <tr key={g}>
                      <td>{g.replace("type:", "Type: ").replace("tag:", "Tag: ")}</td>
                      <td className="num">{row.mrr?.n ?? ""}</td>
                      <td className="num">{v("hit@5")}</td>
                      <td className="num">{v("lenient_hit@5")}</td>
                      <td className="num">{v("mrr")}</td>
                      <td className="num">{v("lenient_mrr")}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="section-block">
        <div className="row" style={{ marginBottom: 10 }}>
          <h2>Questions</h2>
          <span className="spacer" />
          <Seg
            label="Filter questions"
            value={filter}
            onChange={setFilter}
            options={[
              { value: "all", label: "All", n: r.questions.length },
              { value: "missed", label: "Missed", n: count("missed") },
              { value: "via-alternative", label: "Via alternative", n: count("via-alternative") },
              { value: "found", label: "Found", n: count("found") },
            ]}
          />
        </div>
        {!r.chunks_available && (
          <p className="small muted">The chunks this run used ({r.chunks}) are no longer available, so passage text can't be shown.</p>
        )}
        {shown.length > 0 ? (
          <ul className="eval-qs">
            {shown.map((q) => (
              <QuestionRow key={q.id} q={q} />
            ))}
          </ul>
        ) : (
          <p className="small muted">No questions in this group.</p>
        )}
        {r.summary.excluded.length > 0 && (
          <div className="small muted" style={{ marginTop: 12 }}>
            Not scored:{" "}
            {r.summary.excluded.map((e, i) => (
              <span key={e.id}>
                {i > 0 && "; "}
                <Link to={`/questions/${e.id}`}>{e.id}</Link> ({e.reason.split(";")[0].replace(" (scored in the answer eval, not here)", "")})
              </span>
            ))}
          </div>
        )}
      </section>

      {r.report && (
        <section className="section-block">
          <button type="button" className="btn small" onClick={() => setShowReport((v) => !v)}>
            {showReport ? "Hide report.md" : "Show report.md"}
          </button>
          {showReport && <pre className="report">{r.report}</pre>}
        </section>
      )}
    </div>
  );
}
