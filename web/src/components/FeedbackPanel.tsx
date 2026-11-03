// Your ratings of answers on the Ask page, per setup (Results page).
import { useDeleteFeedback, useFeedback } from "../api/hooks";
import type { FeedbackSummary, Rating } from "../api/types";
import { ErrorBanner } from "./ui";

function Score({ c }: { c: FeedbackSummary["faithful"] }) {
  if (!c.n) return <td className="num muted">–</td>;
  return (
    <td className="num" title={`${c.yes} yes, ${c.partly} partly, ${c.no} no`}>
      {Math.round((c.score ?? 0) * 100)}%
      <span className="xs muted">
        {c.yes}/{c.partly}/{c.no}
      </span>
    </td>
  );
}

const RATING_LABEL: Record<keyof Rating, string> = {
  faithful: "faithful",
  complete: "complete",
  should_have_answered: "should have answered",
};

export function FeedbackPanel() {
  const fb = useFeedback();
  const del = useDeleteFeedback();
  if (fb.error) return <ErrorBanner error={fb.error} />;
  const data = fb.data;
  if (!data || data.items.length === 0) return null;
  return (
    <section className="feedback-panel">
      <h2>Your ratings from Ask</h2>
      <p className="small muted" style={{ marginTop: 0 }}>
        Answers you rated on the Ask page, by setup. A score counts yes as 1, partly as ½ and no as 0; below it, the
        yes/partly/no counts. These are the questions you happened to ask, not a fixed set, so compare setups with an
        answer eval, and use these to find what to put in one.
      </p>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Setup</th>
              <th className="num">Rated</th>
              <th className="num" title="Every claim backed by the passage it cites">Faithful</th>
              <th className="num" title="Answers the question with everything relevant the corpus has">Complete</th>
              <th className="num" title="Declines you rated: declining was right / it should have answered">Declines right / wrong</th>
            </tr>
          </thead>
          <tbody>
            {data.summary.map((s) => (
              <tr key={s.label + (s.setup.prompt_version ?? "")}>
                <td>
                  {s.label}
                  {s.setup.prompt_version && <div className="xs muted">prompt {s.setup.prompt_version}</div>}
                </td>
                <td className="num">{s.n}</td>
                <Score c={s.faithful} />
                <Score c={s.complete} />
                <td className="num">
                  {s.declined ? `${s.should_have_answered.no} / ${s.should_have_answered.yes}` : <span className="muted">–</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <details className="others" style={{ marginTop: 10 }}>
        <summary>All {data.items.length} ratings</summary>
        <ul className="feedback-list">
          {data.items.map((f) => (
            <li key={f.id}>
              <div className="feedback-q">{f.answer.question}</div>
              <div className="xs muted">
                {Object.entries(f.rating)
                  .filter(([, v]) => v)
                  .map(([k, v]) => `${RATING_LABEL[k as keyof Rating]}: ${v}`)
                  .join(" · ")}
                {" · "}
                {f.answer.generator?.name === "agent" ? "agent" : f.answer.generator?.name === "extractive" ? "extractive" : "single shot"}
                {f.answer.generator?.model ? ` (${f.answer.generator.model})` : ""}, {f.answer.retriever} · {f.updated.slice(0, 10)}
              </div>
              {f.comment && <div className="small">“{f.comment}”</div>}
              <button type="button" className="btn ghost small danger" disabled={del.isPending} onClick={() => del.mutate(f.id)}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      </details>
      <p className="xs muted">Saved in {data.file}.</p>
    </section>
  );
}
