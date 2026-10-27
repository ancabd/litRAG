// What a generator did, step by step: searches, passages read, tokens. Used on Ask and on answer runs.
import type { TraceStep } from "../api/types";

const VERB: Record<string, string> = {
  search: "Searched",
  read_around: "Read around",
  open_paper: "Opened paper",
  answer: "Answered",
  give_up: "Gave up",
};

function what(s: TraceStep): string {
  const i = s.input as Record<string, unknown>;
  if (s.action === "search") {
    const extra = [i.paper_id && `in ${i.paper_id}`, i.year_from && `from ${i.year_from}`, i.k && `k=${i.k}`].filter(Boolean);
    return `“${i.query ?? ""}”${extra.length ? ` (${extra.join(", ")})` : ""}`;
  }
  if (s.action === "read_around") return String(i.chunk_id ?? "");
  if (s.action === "open_paper") return String(i.paper_id ?? "");
  return "";
}

export function TraceSteps({ steps }: { steps: TraceStep[] }) {
  if (!steps.length) return null;
  return (
    <ol className="trace">
      {steps.map((s) => (
        <li key={s.step} className={s.error ? "trace-error" : ""}>
          <span className="trace-n">{s.step}</span>
          <div>
            <div>
              <strong>{VERB[s.action] ?? s.action}</strong> {what(s)}
              {s.note && <span className="muted"> → {s.note}</span>}
              {s.input_tokens > 0 && (
                <span className="xs muted">
                  {" "}
                  · {s.input_tokens.toLocaleString()} in / {s.output_tokens.toLocaleString()} out
                  {s.cache_read_tokens ? ` (${s.cache_read_tokens.toLocaleString()} cached)` : ""} · {s.seconds.toFixed(1)} s
                </span>
              )}
            </div>
            {s.thought && <div className="trace-thought">{s.thought}</div>}
          </div>
        </li>
      ))}
    </ol>
  );
}
