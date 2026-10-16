import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDeleteEval, useEvals, useMeta, useQuestions, useStartEval } from "../api/hooks";
import { Empty, ErrorBanner, Seg } from "../components/ui";
import { useRun } from "../run";

const n2 = (v: number | null | undefined) => (v == null ? "" : v.toFixed(2));

export function when(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

function RunEvalPanel() {
  const meta = useMeta();
  const questions = useQuestions();
  const { run } = useRun();
  const start = useStartEval();
  const navigate = useNavigate();
  const [chunks, setChunks] = useState<string>("");
  const [retriever, setRetriever] = useState("bm25");
  const [split, setSplit] = useState<"dev" | "test" | "all">("dev");
  const chosen = chunks || run || "";
  const items = questions.data?.items ?? [];
  const n = items.filter((q) => split === "all" || (q.split ?? "dev") === split).length;
  const fileErrors = questions.data?.errors.length ?? 0;

  const go = () => {
    if (split === "test" && !window.confirm("The test split is for final numbers. Running it while you're still tuning inflates them. Run it anyway?")) return;
    start.mutate({ chunks: chosen, retriever, split }, { onSuccess: (r) => navigate(`/results/${r.name}`) });
  };

  return (
    <section className="run-panel" aria-label="Run the eval">
      <div className="row">
        <h2>Run the eval</h2>
        <span className="muted small">Same as python evaluate.py run</span>
      </div>
      <div className="row" style={{ marginTop: 10, gap: 14 }}>
        <label className="inline-field">
          <span>Chunks</span>
          <select className="select" value={chosen} onChange={(e) => setChunks(e.target.value)}>
            {(meta.data?.runs ?? []).map((r) => (
              <option key={r.name} value={r.name}>
                {r.name}
              </option>
            ))}
          </select>
        </label>
        <label className="inline-field">
          <span>Retriever</span>
          <select className="select" value={retriever} onChange={(e) => setRetriever(e.target.value)}>
            {(meta.data?.retrievers ?? ["bm25"]).map((r) => (
              <option key={r}>{r}</option>
            ))}
          </select>
        </label>
        <div className="inline-field">
          <span>Questions</span>
          <Seg
            label="Split"
            value={split}
            onChange={setSplit}
            options={[
              { value: "dev", label: "Dev" },
              { value: "test", label: "Test" },
              { value: "all", label: "All" },
            ]}
          />
        </div>
        <span className="spacer" />
        <button type="button" className="btn primary" onClick={go} disabled={start.isPending || !chosen || n === 0 || fileErrors > 0}>
          {start.isPending ? "Running…" : `Run eval on ${n} question${n === 1 ? "" : "s"}`}
        </button>
      </div>
      {fileErrors > 0 && <p className="small" style={{ color: "var(--warn)", marginTop: 8 }}>questions.yaml has problems; fix them on the Questions tab first.</p>}
      {start.error && <div style={{ marginTop: 10 }}><ErrorBanner error={start.error} /></div>}
    </section>
  );
}

export function ResultsPage() {
  const evals = useEvals();
  const del = useDeleteEval();
  const navigate = useNavigate();
  const [picked, setPicked] = useState<string[]>([]);
  const items = evals.data?.items ?? [];
  const toggle = (name: string) => setPicked((p) => (p.includes(name) ? p.filter((x) => x !== name) : [...p, name]));

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Results</h1>
          <p className="sub">Every eval run, from the app or the terminal. Each is a folder in corpus-builder/runs/.</p>
        </div>
      </div>
      <RunEvalPanel />
      {evals.error && <ErrorBanner error={evals.error} />}

      {evals.data && items.length === 0 && (
        <Empty title="No eval runs yet">
          <p>Run the eval above to score retrieval on your questions. Runs made with evaluate.py show up here too.</p>
        </Empty>
      )}

      {items.length > 0 && (
        <>
          <div className="toolbar" style={{ marginTop: 22 }}>
            <h2>Past runs</h2>
            <span className="spacer" />
            <button
              type="button"
              className="btn"
              disabled={picked.length < 2}
              onClick={() => navigate(`/results/compare?names=${picked.map(encodeURIComponent).join(",")}`)}
            >
              {picked.length < 2 ? "Select two runs to compare" : `Compare ${picked.length} runs`}
            </button>
          </div>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th aria-label="Select" />
                  <th>Run</th>
                  <th>Setup</th>
                  <th className="num">Questions</th>
                  <th className="num" title="Strict / lenient">Hit@5</th>
                  <th className="num" title="Strict / lenient">MRR</th>
                  <th className="num hide-sm" title="Share of each top 10 you have judged">Judged</th>
                  <th className="hide-sm" />
                </tr>
              </thead>
              <tbody>
                {items.map((r) => (
                  <tr key={r.name} onClick={() => navigate(`/results/${r.name}`)}>
                    <td onClick={(e) => e.stopPropagation()}>
                      <input type="checkbox" checked={picked.includes(r.name)} onChange={() => toggle(r.name)} aria-label={`Select ${r.name}`} />
                    </td>
                    <td>
                      <Link to={`/results/${r.name}`} className="paper-title" onClick={(e) => e.stopPropagation()}>
                        {when(r.created)}
                      </Link>
                      <div className="paper-meta xs">{r.split} split</div>
                    </td>
                    <td className="small">
                      {r.retriever?.name} on {r.chunks}
                      {r.git_commit && <div className="xs muted">commit {r.git_commit}</div>}
                    </td>
                    <td className="num">{r.n_scored}</td>
                    <td className="num">
                      {n2(r.headline["hit@5"]?.strict)} <span className="muted">/ {n2(r.headline["hit@5"]?.lenient)}</span>
                    </td>
                    <td className="num">
                      {n2(r.headline.mrr?.strict)} <span className="muted">/ {n2(r.headline.mrr?.lenient)}</span>
                    </td>
                    <td className="num hide-sm">{r.judged == null ? "" : `${Math.round(r.judged * 100)}%`}</td>
                    <td className="hide-sm" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        className="btn ghost small danger"
                        disabled={del.isPending}
                        onClick={() => {
                          if (window.confirm(`Delete this run's folder (${r.name})?`)) {
                            setPicked((p) => p.filter((x) => x !== r.name));
                            del.mutate(r.name);
                          }
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="xs muted" style={{ marginTop: 8 }}>Scores are strict / lenient.</p>
        </>
      )}
    </div>
  );
}
