import { Link, useSearchParams } from "react-router-dom";
import { useCompare } from "../api/hooks";
import type { Effort, EvalCompare, PairedDiff } from "../api/types";
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

const ANSWER_METRICS: [string, string][] = [
  ["correct", "Correct"],
  ["supported", "Supported by citations"],
  ["cites_gold", "Cites your evidence"],
  ["retrieved_gold", "Evidence retrieved"],
  ["invalid_citations", "Invalid citations (lower is better)"],
  ["abstained_when_unanswerable", "Declines unanswerable"],
  ["abstained_when_answerable", "Declines answerable (lower is better)"],
];

type PerRun = EvalCompare["questions"][number]["per_run"][number];

const answerText = (r: PerRun) => {
  if (!r) return "not in this run";
  if (r.unanswerable) return r.abstained ? "declined (right)" : "answered (wrong)";
  if (r.abstained) return "declined";
  return r.verdict ?? "not judged";
};
const isBad = (t: string) => ["incorrect", "declined", "answered (wrong)", "miss"].includes(t);

const rankText = (r: { strict_rank: number | null; lenient_rank: number | null } | null) => {
  if (!r) return "not in this run";
  const o = outcome(r);
  if (o === "found") return `#${r.strict_rank}`;
  if (o === "via-alternative") return `alt #${r.lenient_rank}`;
  return "miss";
};

const signed = (v: number) => `${v >= 0 ? "+" : "−"}${Math.abs(v).toFixed(2)}`;

function PairedTable({ pair, labels, runName }: {
  pair: EvalCompare["paired"][number];
  labels: [string, string][];
  runName: (name: string) => string;
}) {
  const rows = labels.filter(([m]) => pair.metrics[m]);
  const headline = pair.metrics[labels[0][0]] as PairedDiff | undefined;
  const qlinks = (ids: string[]) =>
    ids.map((id, i) => (
      <span key={id}>
        {i > 0 && ", "}
        <Link to={`/questions/${id}`}>{id}</Link>
      </span>
    ));
  return (
    <div style={{ marginTop: 10 }}>
      <p className="small" style={{ margin: "0 0 8px" }}>
        <strong>{runName(pair.run)}</strong> compared with <strong>{runName(pair.base)}</strong>, question by question
      </p>
      <div className="table-wrap">
        <table className="data static">
          <thead>
            <tr>
              <th>Metric</th>
              <th className="num">n</th>
              <th className="num">Before</th>
              <th className="num">After</th>
              <th>Difference [95% CI]</th>
              <th className="num" title="Questions where the second run did better / worse / the same">Better / worse / same</th>
              <th className="num" title="Two-sided exact sign test on better vs worse">p</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([m, label]) => {
              const r = pair.metrics[m];
              const improved = r.lower_is_better ? r.diff < 0 : r.diff > 0;
              const tone = r.clear ? (improved ? "diff-up" : "diff-down") : "";
              return (
                <tr key={m}>
                  <td>{label}</td>
                  <td className="num">{r.n}</td>
                  <td className="num">{r.mean_a.toFixed(2)}</td>
                  <td className="num">{r.mean_b.toFixed(2)}</td>
                  <td className={tone}>
                    {signed(r.diff)} <span className="muted xs">[{signed(r.lo)}, {signed(r.hi)}]</span>
                  </td>
                  <td className="num">
                    {r.better} / {r.worse} / {r.tied}
                  </td>
                  <td className="num">{r.p < 0.001 ? "<0.001" : r.p.toFixed(3)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {headline && (headline.better_ids.length > 0 || headline.worse_ids.length > 0) && (
        <p className="small" style={{ marginTop: 8 }}>
          {labels[0][1]}:{" "}
          {headline.better_ids.length > 0 && <>better on {qlinks(headline.better_ids)}</>}
          {headline.better_ids.length > 0 && headline.worse_ids.length > 0 && "; "}
          {headline.worse_ids.length > 0 && <>worse on {qlinks(headline.worse_ids)}</>}.
        </p>
      )}
    </div>
  );
}

const EFFORT_ROWS: [keyof Effort, string, (v: number) => string][] = [
  ["turns", "Model calls", (v) => v.toFixed(1)],
  ["searches", "Searches", (v) => v.toFixed(1)],
  ["passages_read", "Passages read", (v) => v.toFixed(1)],
  ["input_tokens", "Input tokens", (v) => Math.round(v).toLocaleString()],
  ["cost", "Cost per question", (v) => `$${v.toFixed(4)}`],
  ["seconds", "Seconds per question", (v) => v.toFixed(1)],
  ["gave_up", "Gave up", (v) => `${Math.round(v * 100)}%`],
  ["hit_budget", "Ran out of budget", (v) => `${Math.round(v * 100)}%`],
];

export function ComparePage() {
  const [params] = useSearchParams();
  const names = (params.get("names") ?? "").split(",").filter(Boolean);
  const cmp = useCompare(names);
  const c = cmp.data;
  const answers = !!c && c.kinds.length === 1 && c.kinds[0] === "answer";
  const mixed = !!c && c.kinds.length > 1;
  const metrics = answers ? ANSWER_METRICS : METRICS;
  const cellText = answers ? answerText : rankText;
  const setup = (r: EvalCompare["runs"][number]) =>
    r.kind === "answer"
      ? `${r.generator?.name === "agent" ? `agent (${r.generator.model})` : r.generator?.model ?? "extractive"}, ${r.retriever?.name} top ${r.k}, ${r.split}`
      : `${r.retriever?.name} on ${r.chunks}, ${r.split}`;

  return (
    <div className="page">
      <Link to="/results" className="back">
        Back to results
      </Link>
      <div className="page-head">
        <div>
          <h1>Compare runs</h1>
          <p className="sub">
            Each run's means with 95% intervals, then the paired comparison: the same questions, run by run. With a few dozen
            questions the paired comparison is the one that can show a real difference.
          </p>
        </div>
      </div>
      {cmp.error && <ErrorBanner error={cmp.error} />}
      {c && !c.same_questions && (
        <div className="banner">
          These runs used different versions of questions.yaml (new questions, edits, or passages judged in between), so
          their scores aren't directly comparable. To compare setups fairly, rerun them on the current questions.
        </div>
      )}
      {mixed && (
        <div className="banner">You picked both retrieval and answer runs. They measure different things; compare runs of one kind.</div>
      )}
      {c && !mixed && (
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
                        {setup(r)}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {metrics.filter(([m]) => c.runs.some((r) => r.results[m])).map(([m, label]) => (
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

          {c.paired.length > 0 && (
            <section className="section-block">
              <h2>Paired comparison</h2>
              <p className="small muted" style={{ margin: "4px 0 0", maxWidth: "86ch" }}>
                Per question, how much each run differs from the first one. A colored difference has a 95% interval that
                excludes zero; p is an exact sign test on the better/worse counts. Testing many metrics at once, about one in
                twenty comparisons shows p &lt; 0.05 by chance.
              </p>
              {c.paired.map((pair) => (
                <PairedTable key={pair.run} pair={pair} labels={metrics} runName={(n) => {
                  const r = c.runs.find((x) => x.name === n);
                  return r ? `${setup(r)} (${when(r.created)})` : n;
                }} />
              ))}
            </section>
          )}

          {answers && c.runs.some((r) => r.effort) && (
            <section className="section-block">
              <h2>Effort per question</h2>
              <div className="table-wrap" style={{ marginTop: 10 }}>
                <table className="data static">
                  <thead>
                    <tr>
                      <th />
                      {c.runs.map((r) => (
                        <th key={r.name} className="num">{setup(r).split(",")[0]}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {EFFORT_ROWS.map(([key, label, fmt]) => (
                      <tr key={key}>
                        <td>{label}</td>
                        {c.runs.map((r) => {
                          const v = r.effort?.[key];
                          return <td key={r.name} className="num">{v == null ? "–" : fmt(v as number)}</td>;
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <section className="section-block">
            <h2>Per question</h2>
            <p className="small muted" style={{ margin: "4px 0 10px" }}>
              {answers
                ? "The judge's verdict on each run's answer. Rows where the runs differ are highlighted."
                : 'Rank of your original evidence in each run; "alt" means only an alternative made the top 10. Rows where the runs disagree are highlighted.'}
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
                    const texts = q.per_run.map(cellText);
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
                          <td key={i} className={`small ${isBad(t) ? "rank-miss" : ""}`}>
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
