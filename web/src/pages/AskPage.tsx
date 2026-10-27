import { useState } from "react";
import { useAsk, useLlm } from "../api/hooks";
import type { AskResult } from "../api/types";
import { AnswerText } from "../components/AnswerText";
import { ChunkCard } from "../components/ChunkCard";
import { TraceSteps } from "../components/TraceSteps";
import { ErrorBanner, Seg } from "../components/ui";
import { useRun } from "../run";

function Meta({ r }: { r: AskResult }) {
  const bits = [
    r.generator.name === "agent" ? `agent (${r.generator.model})` : r.generator.model ?? "extractive baseline",
    r.generator.name === "agent"
      ? `${r.passages.length} passages read from ${r.run}`
      : `${r.passages.length} passages from ${r.retriever} on ${r.run}`,
    r.cached ? "cached" : `${r.seconds.toFixed(1)} s`,
  ];
  if (r.cost) bits.push(`$${r.cost.toFixed(4)}`);
  return <p className="xs muted answer-meta">{bits.join(", ")}</p>;
}

export function AskPage() {
  const llm = useLlm();
  const ask = useAsk();
  const { run } = useRun();
  const [question, setQuestion] = useState("");
  const [generator, setGenerator] = useState<"claude" | "agent" | "extractive">("claude");
  const [model, setModel] = useState("");
  const [k, setK] = useState(8);
  const [history, setHistory] = useState<AskResult[]>([]);
  const [shown, setShown] = useState<AskResult | null>(null);

  const usesModel = generator !== "extractive";
  const needsKey = usesModel && llm.data && !llm.data.configured;
  const submit = () => {
    if (question.trim().length < 3 || ask.isPending || needsKey) return;
    ask.mutate(
      { question: question.trim(), generator, model: usesModel ? model || undefined : undefined, k },
      {
        onSuccess: (r) => {
          setShown(r);
          setHistory((h) => [r, ...h.filter((x) => x.question !== r.question)].slice(0, 12));
        },
      },
    );
  };
  const r = shown;
  const cited = r ? r.passages.filter((p) => p.cited_as).sort((a, b) => a.cited_as! - b.cited_as!) : [];
  const others = r ? r.passages.filter((p) => !p.cited_as) : [];

  return (
    <div className="page ask">
      <div className="page-head">
        <div>
          <h1>Ask</h1>
          <p className="sub">Answers come only from the passages retrieved from your corpus, and cite them.</p>
        </div>
      </div>

      <div className="ask-box">
        <textarea
          className="textarea ask-input"
          rows={2}
          value={question}
          autoFocus
          aria-label="Your question"
          placeholder="e.g. How does NequIP's treatment of rotational symmetry differ from Behler-Parrinello symmetry functions?"
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <div className="row ask-controls">
          <Seg
            label="Answered by"
            value={generator}
            onChange={setGenerator}
            options={[
              { value: "claude", label: "Single shot" },
              { value: "agent", label: "Agent" },
              { value: "extractive", label: "Extractive baseline" },
            ]}
          />
          {usesModel && (
            <select className="select" value={model || llm.data?.default_model || ""} onChange={(e) => setModel(e.target.value)} aria-label="Model">
              {(llm.data?.models ?? []).map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          )}
          <select className="select" value={k} onChange={(e) => setK(Number(e.target.value))} aria-label="Passages">
            {[3, 5, 8, 12, 20].map((n) => (
              <option key={n} value={n}>
                {n} passages{generator === "agent" ? " per search" : ""}
              </option>
            ))}
          </select>
          <span className="spacer" />
          <button type="button" className="btn primary" onClick={submit} disabled={ask.isPending || question.trim().length < 3 || !!needsKey || !run}>
            {ask.isPending ? (generator === "agent" ? "Searching and reading…" : "Answering…") : "Ask"}
          </button>
        </div>
        <p className="xs muted" style={{ marginTop: 8 }}>
          {generator === "extractive" && "No model: returns the retrieved sentence that best overlaps your question. The floor an LLM should clearly beat."}
          {generator === "claude" && "One search with your question; Claude answers from the top passages."}
          {generator === "agent" && "Claude searches and reads with tools, as many times as it needs (up to 8 model calls), then answers. Slower, and its steps are shown below the answer."}
        </p>
      </div>

      {needsKey && (
        <div className="banner" style={{ marginTop: 14 }}>
          <div>
            Claude needs an API key. Create one at platform.claude.com, then start the server with it:
            <pre className="setup">export ANTHROPIC_API_KEY=sk-ant-...{"\n"}python -m app</pre>
            Until then you can try the extractive baseline.
          </div>
          <button type="button" className="btn small" onClick={() => setGenerator("extractive")}>
            Use the baseline
          </button>
        </div>
      )}
      {ask.error && <div style={{ marginTop: 14 }}><ErrorBanner error={ask.error} /></div>}

      {r && (
        <section className="answer" aria-live="polite" style={{ opacity: ask.isPending ? 0.5 : 1 }}>
          <p className="answer-q">{r.question}</p>
          {r.answerable ? (
            <div className="prose answer-text">
              <AnswerText text={r.answer} citations={r.citations} />
            </div>
          ) : (
            <div className="not-found">
              <strong>Not found in the corpus.</strong> <span className="prose">{r.answer}</span>
            </div>
          )}
          {r.warnings.length > 0 && (
            <ul className="answer-warnings">
              {r.warnings.map((w) => (
                <li key={w}>{w}</li>
              ))}
            </ul>
          )}
          <Meta r={r} />
          {r.generator.name === "agent" && r.trace && r.trace.length > 0 && (
            <details className="steps" open>
              <summary>How it got there ({r.trace.length} steps)</summary>
              <TraceSteps steps={r.trace} />
            </details>
          )}

          {cited.length > 0 && (
            <div className="sources">
              <h2>Sources</h2>
              {cited.map((p) => (
                <div key={p.chunk_id} id={`p-${p.chunk_id}`} className="source">
                  <span className="cite big">{p.cited_as}</span>
                  <ChunkCard chunk={p} showPaper />
                </div>
              ))}
            </div>
          )}
          {others.length > 0 && (
            <details className="others">
              <summary>
                {cited.length > 0 ? "Other retrieved passages" : "Retrieved passages"} ({others.length})
              </summary>
              {others.map((p) => (
                <div key={p.chunk_id} id={`p-${p.chunk_id}`}>
                  <ChunkCard chunk={p} showPaper />
                </div>
              ))}
            </details>
          )}
        </section>
      )}

      {history.length > 1 && (
        <section className="section-block">
          <h2>Earlier in this session</h2>
          <ul className="history">
            {history.map((h) => (
              <li key={h.question}>
                <button type="button" className={`linklike ${h === shown ? "current" : ""}`} onClick={() => { setShown(h); setQuestion(h.question); }}>
                  {h.question}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
