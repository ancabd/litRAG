import { Link, useSearchParams } from "react-router-dom";
import { useCompare } from "../api/hooks";
import { ErrorBanner } from "../components/ui";
import { outcome } from "./ResultPage";
import { when } from "./ResultsPage";

const METRICS: [string, string][] = [
  ["hit@1", "Hit@1"],
  ["hit@5", "Hit@5"],
  ["hit@10", "Hit@10"],
  ["mrr", "MRR"],
  ["ndcg@10", "nDCG@10"],
  ["lenient_hit@5", "Hit@5, lenient"],
  ["lenient_mrr", "MRR, lenient"],
  ["judged@10", "Judged"],
];

const rankText = (r: { strict_rank: number | null; lenient_rank: number | null } | null) => {
  if (!r) return "not in this run";
  const o = outcome(r);
  if (o === "found") return `#${r.strict_rank}`;
  if (o === "via-alternative") return `alt #${r.lenient_rank}`;
  return "miss";
};

export function ComparePage() {
  const [params] = useSearchParams();
  const names = (params.get("names") ?? "").split(",").filter(Boolean);
  const cmp = useCompare(names);
  const c = cmp.data;

  return (
    <div className="page">
      <Link to="/results" className="back">
        Back to results
      </Link>
      <div className="page-head">
        <div>
          <h1>Compare runs</h1>
          <p className="sub">Means with 95% intervals. Overlapping intervals mean the difference isn't established yet.</p>
        </div>
      </div>
      {cmp.error && <ErrorBanner error={cmp.error} />}
      {c && !c.same_questions && (
        <div className="banner">
          These runs used different versions of questions.yaml (new questions, edits, or passages judged in between), so
          their scores aren't directly comparable. To compare setups fairly, rerun them on the current questions.
        </div>
      )}
      {c && (
        <>
          <div className="table-wrap">
            <table className="data static">
              <thead>
                <tr>
                  <th>Metric</th>
                  {c.runs.map((r) => (
                    <th key={r.name}>
                      <Link to={`/results/${r.name}`}>{when(r.created)}</Link>
                      <div className="xs muted" style={{ fontWeight: 450 }}>
                        {r.retriever?.name} on {r.chunks}, {r.split}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {METRICS.filter(([m]) => c.runs.some((r) => r.results[m])).map(([m, label]) => (
                  <tr key={m}>
                    <td>{label}</td>
                    {c.runs.map((r) => {
                      const v = r.results[m];
                      return (
                        <td key={r.name} className="num-left">
                          {v ? (
                            <>
                              {v.mean.toFixed(2)} <span className="muted xs">[{v.lo.toFixed(2)}–{v.hi.toFixed(2)}]</span>
                            </>
                          ) : (
                            "–"
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <section className="section-block">
            <h2>Per question</h2>
            <p className="small muted" style={{ margin: "4px 0 10px" }}>
              Rank of your original evidence in each run; "alt" means only an alternative made the top 10. Rows where the runs disagree are highlighted.
            </p>
            <div className="table-wrap">
              <table className="data static">
                <thead>
                  <tr>
                    <th>Question</th>
                    {c.runs.map((r) => (
                      <th key={r.name}>{when(r.created)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {c.questions.map((q) => {
                    const texts = q.per_run.map(rankText);
                    const changed = new Set(texts).size > 1;
                    return (
                      <tr key={q.id} className={changed ? "changed" : ""}>
                        <td>
                          <Link to={`/questions/${q.id}`} className="id">
                            {q.id}
                          </Link>{" "}
                          <span className="small">{q.question}</span>
                        </td>
                        {texts.map((t, i) => (
                          <td key={i} className={`small ${t === "miss" ? "rank-miss" : ""}`}>
                            {t}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
