// One answer-eval run: scores, how far the judge agrees with you, and every generated answer.
import { useState } from "react";
import { Link } from "react-router-dom";
import { useSetVerdict } from "../api/hooks";
import type { EvalDetail, EvalQuestion, Verdict } from "../api/types";
import { AnswerText } from "../components/AnswerText";
import { ScoreChart } from "../components/ScoreChart";
import { ErrorBanner, Seg, TYPE_LABEL } from "../components/ui";
import { Hit } from "./ResultPage";
import { when } from "./ResultsPage";

const METRICS = ["correct", "supported", "cites_gold", "retrieved_gold", "invalid_citations",
  "abstained_when_unanswerable", "abstained_when_answerable"];

const VERDICT_TONE: Record<string, string> = {
  correct: "ok", supported: "ok", partial: "accent", incorrect: "warn", unsupported: "warn",
};

type Filter = "all" | "wrong" | "abstained" | "unchecked" | "disagree";

const verdictOf = (q: EvalQuestion) => q.judgments?.correctness?.verdict ?? null;
const abstained = (q: EvalQuestion) => !!q.answer && !q.answer.answerable;

function Outcome({ q }: { q: EvalQuestion }) {
  const v = verdictOf(q);
  if (q.type === "unanswerable")
    return abstained(q) ? <span className="pill ok">Declined, as it should</span> : <span className="pill warn">Answered an unanswerable question</span>;
  if (abstained(q)) return <span className="pill warn">Declined</span>;
  if (v) return <span className={`pill ${VERDICT_TONE[v] ?? ""}`}>{v[0].toUpperCase() + v.slice(1)}</span>;
  return <span className="pill">Not judged</span>;
}

function YourVerdict({ run, q }: { run: string; q: EvalQuestion }) {
  const set = useSetVerdict(run);
  const mine = q.human?.correctness ?? null;
  const judge = verdictOf(q);
  return (
    <div className="your-verdict">
      <span className="small">Your verdict</span>
      <div className="seg" role="group" aria-label="Your verdict">
        {(["correct", "partial", "incorrect"] as Verdict[]).map((v) => (
          <button key={v} type="button" aria-pressed={mine === v} disabled={set.isPending}
            onClick={() => set.mutate({ qid: q.id, verdict: mine === v ? null : v })}>
            {v[0].toUpperCase() + v.slice(1)}
          </button>
        ))}
      </div>
      {mine && judge && (
        <span className={`xs ${mine === judge ? "muted" : "disagree"}`}>
          {mine === judge ? "Agrees with the judge" : `The judge said ${judge}`}
        </span>
      )}
      {set.error && <ErrorBanner error={set.error} />}
    </div>
  );
}

function Row({ run, q }: { run: string; q: EvalQuestion }) {
  const [open, setOpen] = useState(false);
  const a = q.answer;
  const cited = new Map((a?.citations ?? []).map((c, i) => [c, i + 1]));
  const c = q.judgments?.correctness;
  const s = q.judgments?.support;
  const prefix = `${q.id}-p-`;
  return (
    <li className="eval-q">
      <button type="button" className="eval-q-head" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        <span className="id">{q.id}</span>
        <span className="eval-q-text">{q.question}</span>
        <span className="row" style={{ gap: 6, flexWrap: "nowrap" }}>
          {q.human && <span className="pill" title="You graded this answer">Checked</span>}
          <Outcome q={q} />
        </span>
      </button>
      {open && a && (
        <div className="eval-q-detail">
          <div className="row small" style={{ marginBottom: 10 }}>
            <span className="muted">
              {TYPE_LABEL[q.type] ?? q.type}
              {q.tags.length > 0 && `, ${q.tags.join(", ")}`}
            </span>
            <span className="spacer" />
            <Link to={`/questions/${q.id}`} className="btn small">Open question</Link>
          </div>

          <div className="answer-pair">
            <div>
              <h3>Generated answer</h3>
              {a.answerable ? (
                <p className="prose"><AnswerText text={a.answer} citations={a.citations} anchorPrefix={prefix} /></p>
              ) : (
                <p className="prose not-found"><strong>Declined.</strong> {a.answer}</p>
              )}
              {a.invalid_citations.length > 0 && (
                <p className="xs disagree">Cites passages it wasn't given: {a.invalid_citations.join(", ")}</p>
              )}
            </div>
            <div>
              <h3>Your reference</h3>
              <p className="prose">{q.reference ?? <span className="muted">{q.type === "unanswerable" ? "Unanswerable: the right move is to decline." : "No reference answer, so correctness isn't judged."}</span>}</p>
            </div>
          </div>

          {(c || s) && (
            <div className="judge-notes">
              {c && (
                <p className="small">
                  <span className={`pill ${VERDICT_TONE[c.verdict ?? ""] ?? ""}`}>Judge: {c.verdict}</span> {c.reason}
                </p>
              )}
              {s && (
                <p className="small">
                  <span className={`pill ${VERDICT_TONE[s.verdict ?? ""] ?? ""}`}>Citations: {s.verdict}</span> {s.reason}
                </p>
              )}
            </div>
          )}
          {q.reference && a.answerable && <YourVerdict run={run} q={q} />}

          <h3 style={{ marginTop: 14 }}>Passages it was given</h3>
          <ol className="hits">
            {q.retrieved.map((h) => (
              <Hit key={h.chunk_id} h={h} anchor={prefix + h.chunk_id} citedAs={cited.get(h.chunk_id)} />
            ))}
          </ol>
        </div>
      )}
    </li>
  );
}

export function AnswerRun({ r }: { r: EvalDetail }) {
  const [filter, setFilter] = useState<Filter>("all");
  const [showReport, setShowReport] = useState(false);
  const results = r.summary.results;
  const all = results.all ?? {};
  const groups = Object.keys(results).filter((g) => g !== "all");
  const ag = r.agreement;
  const disagree = new Set(ag?.disagreements ?? []);
  const gradable = r.questions.filter((q) => q.reference && q.answer?.answerable && verdictOf(q));
  const test: Record<Filter, (q: EvalQuestion) => boolean> = {
    all: () => true,
    wrong: (q) => (q.type === "unanswerable" ? !abstained(q) : abstained(q) || ["incorrect", "partial"].includes(verdictOf(q) ?? "")),
    abstained,
    unchecked: (q) => gradable.includes(q) && !q.human,
    disagree: (q) => disagree.has(q.id),
  };
  const shown = r.questions.filter(test[filter]);
  const cost = (r.usage?.generator.cost ?? 0) + (r.usage?.judge?.cost ?? 0);
  const noRef = (r.summary as unknown as { no_reference_answer?: string[] }).no_reference_answer ?? [];

  return (
    <div className="page">
      <Link to="/results" className="back">Back to results</Link>
      <div className="page-head">
        <div>
          <h1>Answer eval, {when(r.created)}</h1>
          <p className="sub">
            {r.generator?.model ?? "Extractive baseline"} answering from the top {r.k} passages of {r.retriever?.name} on {r.chunks},{" "}
            {r.split ?? "all"} split, {r.n_scored} questions.{" "}
            {r.judge ? `Judged by ${r.judge.model}.` : "No judge, so only the citation metrics are scored."}
            {cost > 0 && ` Cost $${cost.toFixed(3)}.`}
          </p>
        </div>
      </div>

      <ScoreChart results={all} metrics={METRICS} strictLabel={null} />
      <p className="xs muted" style={{ marginTop: 6, maxWidth: "80ch" }}>
        Correct is the judge's grade against your reference (partial counts half). Supported asks whether the cited passages back the
        answer. Metrics marked ↓ are better low.
      </p>

      {r.judge && (
        <section className="section-block agreement">
          <h2>Can you trust the judge?</h2>
          {ag && ag.n > 0 ? (
            <p className="small" style={{ maxWidth: "80ch" }}>
              You graded {ag.n} answer{ag.n === 1 ? "" : "s"}; the judge gave the same verdict on{" "}
              <strong>{Math.round((ag.agreement ?? 0) * 100)}%</strong>
              {ag.kappa != null && <> (Cohen's κ {ag.kappa.toFixed(2)})</>}.{" "}
              {ag.n < 10
                ? "Grade a few more for a stable number; around 15–20 is enough at this size."
                : ag.kappa != null && ag.kappa >= 0.6
                ? "That is substantial agreement: the Correct score is usable."
                : "Agreement is weak, so read the Correct score with care and check the disagreements."}
            </p>
          ) : (
            <p className="small" style={{ maxWidth: "80ch" }}>
              Grade some answers yourself (open a question, then "Your verdict"). Agreement between you and the judge is what makes
              the Correct score worth reporting. {gradable.length} answers can be graded.
            </p>
          )}
        </section>
      )}

      {groups.length > 0 && (
        <section className="section-block">
          <h2>By question type and tag</h2>
          <div className="table-wrap" style={{ marginTop: 10 }}>
            <table className="data static">
              <thead>
                <tr>
                  <th>Group</th>
                  <th className="num">Questions</th>
                  <th className="num">Correct</th>
                  <th className="num">Supported</th>
                  <th className="num">Cites evidence</th>
                  <th className="num">Evidence retrieved</th>
                </tr>
              </thead>
              <tbody>
                {groups.map((g) => {
                  const row = results[g];
                  const v = (m: string) => (row[m] ? row[m].mean.toFixed(2) : "–");
                  const n = Math.max(0, ...Object.values(row).map((x) => x.n));
                  return (
                    <tr key={g}>
                      <td>{g.replace("type:", "Type: ").replace("tag:", "Tag: ").replace("retrieval:found", "Retrieval found the evidence").replace("retrieval:missed", "Retrieval missed the evidence")}</td>
                      <td className="num">{n}</td>
                      <td className="num">{v("correct")}</td>
                      <td className="num">{v("supported")}</td>
                      <td className="num">{v("cites_gold")}</td>
                      <td className="num">{v("retrieved_gold")}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="xs muted" style={{ marginTop: 6 }}>
            Compare "Retrieval found the evidence" with "Retrieval missed the evidence": it separates retrieval failures from generation failures.
          </p>
        </section>
      )}

      <section className="section-block">
        <div className="row" style={{ marginBottom: 10 }}>
          <h2>Answers</h2>
          <span className="spacer" />
          <Seg
            label="Filter answers"
            value={filter}
            onChange={setFilter}
            options={[
              { value: "all", label: "All", n: r.questions.length },
              { value: "wrong", label: "Wrong or partial", n: r.questions.filter(test.wrong).length },
              { value: "abstained", label: "Declined", n: r.questions.filter(abstained).length },
              ...(r.judge ? [
                { value: "unchecked" as Filter, label: "To grade", n: r.questions.filter(test.unchecked).length },
                { value: "disagree" as Filter, label: "Judge disagrees", n: disagree.size },
              ] : []),
            ]}
          />
        </div>
        {!r.chunks_available && (
          <p className="small muted">The chunks this run used ({r.chunks}) are no longer available, so passage text can't be shown.</p>
        )}
        {shown.length > 0 ? (
          <ul className="eval-qs">
            {shown.map((q) => <Row key={q.id} run={r.name} q={q} />)}
          </ul>
        ) : (
          <p className="small muted">No answers in this group.</p>
        )}
        {noRef.length > 0 && r.judge && (
          <p className="small muted" style={{ marginTop: 12 }}>
            No reference answer, so not graded for correctness:{" "}
            {noRef.map((id, i) => (
              <span key={id}>{i > 0 && ", "}<Link to={`/questions/${id}`}>{id}</Link></span>
            ))}
          </p>
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
