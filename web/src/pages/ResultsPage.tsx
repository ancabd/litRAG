import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDeleteEval, useEvals, useJob, useLlm, useMeta, useQuestions, useStartEval } from "../api/hooks";
import type { EvalBrief } from "../api/types";
import { DenseNote, RetrieverSelect, retrieverLabel } from "../components/RetrieverSelect";
import { Empty, ErrorBanner, Seg } from "../components/ui";
import { useRun } from "../run";

const n2 = (v: number | null | undefined) => (v == null ? "" : v.toFixed(2));

export function when(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

function Headline({ r, m }: { r: EvalBrief; m: string }) {
  const h = r.headline[m];
  if (!h || h.strict == null) return <td className="num muted">–</td>;
  return (
    <td className="num">
      {n2(h.strict)}
      {h.lenient != null && <span className="muted"> / {n2(h.lenient)}</span>}
    </td>
  );
}

function JobProgress({ id, onDone }: { id: string; onDone: (name: string) => void }) {
  const job = useJob(id);
  const j = job.data;
  useEffect(() => {
    if (j?.state === "done" && j.result) onDone(j.result.name);
  }, [j?.state, j?.result, onDone]);
  if (!j) return null;
  if (j.state === "error") return <div style={{ marginTop: 10 }}><ErrorBanner error={new Error(j.error ?? "The answer eval failed")} /></div>;
  const frac = j.total ? j.done / j.total : 0;
  return (
    <div className="job" role="status" style={{ marginTop: 12 }}>
      <div className="job-bar"><span style={{ width: `${Math.round(frac * 100)}%` }} /></div>
      <span className="small muted">
        Answering and judging: {j.done} of {j.total ?? "?"} questions. You can leave this page; the run keeps going.
      </span>
    </div>
  );
}

function RunEvalPanel() {
  const meta = useMeta();
  const questions = useQuestions();
  const llm = useLlm();
  const { run } = useRun();
  const start = useStartEval();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [kind, setKind] = useState<"retrieval" | "answer">("retrieval");
  const [chunks, setChunks] = useState<string>("");
  const [retriever, setRetriever] = useState("bm25");
  const [split, setSplit] = useState<"dev" | "test" | "all">("dev");
  const [generator, setGenerator] = useState<"claude" | "agent" | "extractive">("claude");
  const [model, setModel] = useState("");
  const [judge, setJudge] = useState("default");
  const [k, setK] = useState(5);
  const [jobId, setJobId] = useState<string | null>(null);
  const chosen = chunks || run || "";
  const items = questions.data?.items ?? [];
  const n = items.filter((q) => split === "all" || (q.split ?? "dev") === split).length;
  const fileErrors = questions.data?.errors.length ?? 0;
  const models = llm.data?.models ?? [];
  const genModel = model || llm.data?.default_model || "";
  const usesModel = generator !== "extractive";
  const judgeModel = judge === "default" ? llm.data?.judge_model ?? "claude-sonnet-5-5" : judge;
  const needsKey = kind === "answer" && !llm.data?.configured && (usesModel || judgeModel !== "none");

  const finished = useCallback(
    (name: string) => {
      setJobId(null);
      qc.invalidateQueries({ queryKey: ["evals"] });
      navigate(`/results/${name}`);
    },
    [navigate, qc],
  );

  const go = () => {
    if (split === "test" && !window.confirm("The test split is for final numbers. Running it while you're still tuning inflates them. Run it anyway?")) return;
    const body =
      kind === "retrieval"
        ? { kind, chunks: chosen, retriever, split }
        : { kind, chunks: chosen, retriever, split, generator, model: usesModel ? genModel : undefined, judge: judgeModel, k };
    start.mutate(body, {
      onSuccess: (r) => {
        if (r.job) setJobId(r.job.id);
        else if (r.name) navigate(`/results/${r.name}`);
      },
    });
  };
  const busy = start.isPending || !!jobId;

  return (
    <section className="run-panel" aria-label="Run the eval">
      <div className="row">
        <h2>Run an eval</h2>
        <Seg
          label="What to evaluate"
          value={kind}
          onChange={setKind}
          options={[
            { value: "retrieval", label: "Retrieval" },
            { value: "answer", label: "Answers" },
          ]}
        />
        <span className="muted small">Same as python evaluate.py {kind === "retrieval" ? "run" : "answer"}</span>
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
          <span>{kind === "answer" && generator === "agent" ? "Agent's search" : "Retriever"}</span>
          <RetrieverSelect value={retriever} onChange={setRetriever} />
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
      </div>
      <DenseNote retriever={retriever} />
      {kind === "answer" && (
        <div className="row" style={{ marginTop: 10, gap: 14 }}>
          <div className="inline-field">
            <span>Method</span>
            <Seg
              label="Method"
              value={generator}
              onChange={setGenerator}
              options={[
                { value: "claude", label: "Single shot" },
                { value: "agent", label: "Agent" },
                { value: "extractive", label: "Extractive baseline" },
              ]}
            />
          </div>
          {usesModel && (
            <label className="inline-field">
              <span>Model</span>
              <select className="select" value={genModel} onChange={(e) => setModel(e.target.value)}>
                {models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label className="inline-field">
            <span>Judge</span>
            <select className="select" value={judge} onChange={(e) => setJudge(e.target.value)}>
              <option value="default">{llm.data?.judge_model ?? "claude-sonnet-5-5"} (default, for every run)</option>
              {models.filter((m) => m !== llm.data?.judge_model).map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
              <option value="none">No judge (citation metrics only)</option>
            </select>
          </label>
          <label className="inline-field">
            <span>{generator === "agent" ? "Passages per search" : "Passages"}</span>
            <select className="select" value={k} onChange={(e) => setK(Number(e.target.value))}>
              {[3, 5, 8, 12, 20].map((x) => (
                <option key={x} value={x}>
                  {x}
                </option>
              ))}
            </select>
          </label>
        </div>
      )}
      <div className="row" style={{ marginTop: 12 }}>
        {kind === "answer" && (
          <span className="xs muted" style={{ maxWidth: "62ch" }}>
            {generator === "agent"
              ? "The agent makes several model calls per question (8 at most). Answers are cached, so rerunning the same setup is free."
              : "One generation and up to two judge calls per question. Answers are cached, so rerunning the same setup is free."}
          </span>
        )}
        <span className="spacer" />
        <button type="button" className="btn primary" onClick={go} disabled={busy || !chosen || n === 0 || fileErrors > 0 || needsKey}>
          {busy ? "Running…" : `Run ${kind === "answer" ? "answer eval" : "eval"} on ${n} question${n === 1 ? "" : "s"}`}
        </button>
      </div>
      {needsKey && (
        <p className="small" style={{ color: "var(--warn)", marginTop: 8 }}>
          Claude needs an API key: add one in <Link to="/settings">Settings</Link>. Without it, pick the extractive baseline with no judge.
        </p>
      )}
      {fileErrors > 0 && <p className="small" style={{ color: "var(--warn)", marginTop: 8 }}>questions.yaml has problems; fix them on the Questions tab first.</p>}
      {start.error && <div style={{ marginTop: 10 }}><ErrorBanner error={start.error} /></div>}
      {jobId && <JobProgress id={jobId} onDone={finished} />}
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
          <p className="sub">Every eval run, from the app or the terminal. Each is a folder in data/runs/.</p>
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
                  <th className="num" title="Retrieval: Hit@5 strict / lenient. Answers: share judged correct">Hit@5 / Correct</th>
                  <th className="num" title="Retrieval: MRR strict / lenient. Answers: share supported by its citations">MRR / Supported</th>
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
                      <span className={`pill ${r.kind === "answer" ? "accent" : ""}`}>{r.kind === "answer" ? "Answers" : "Retrieval"}</span>{" "}
                      {r.kind === "answer" && <>{r.generator?.name === "agent" ? `agent (${r.generator.model})` : r.generator?.model ?? "extractive"}, </>}
                      {retrieverLabel(r.retriever)} on {r.chunks}
                      {r.git_commit && <div className="xs muted">commit {r.git_commit}</div>}
                    </td>
                    <td className="num">{r.n_scored}</td>
                    <Headline r={r} m={r.kind === "answer" ? "correct" : "hit@5"} />
                    <Headline r={r} m={r.kind === "answer" ? "supported" : "mrr"} />
                    <td className="num hide-sm">{r.kind === "answer" || r.judged == null ? "" : `${Math.round(r.judged * 100)}%`}</td>
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
          <p className="xs muted" style={{ marginTop: 8 }}>Retrieval scores are strict / lenient. A dash means the run has no judge or no reference answers.</p>
        </>
      )}
    </div>
  );
}
