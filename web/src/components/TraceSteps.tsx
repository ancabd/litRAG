// What a generator did, step by step: each search or read, what came back, tokens and time,
// and Claude's own note on what it was doing. Used live on Ask and per question on answer runs.
import type { JudgmentKind, TraceStep } from "../api/types";

const VERB: Record<string, string> = {
  search: "Searched",
  read_around: "Read around",
  open_paper: "Opened paper",
  answer: "Answered",
  give_up: "Gave up",
  refused: "Over budget",
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

export interface PassageInfo {
  title?: string | null;
  section?: string | null;
  label?: JudgmentKind; // your evidence, an alternative, judged not relevant, or not reviewed
  cited?: number; // its number in the answer, if cited
}

const LABEL_TITLE: Record<string, string> = {
  evidence: "Your evidence",
  alternative: "An alternative you marked",
  not_relevant: "Judged not relevant",
};

function Passage({ id, info, anchorPrefix }: { id: string; info: PassageInfo; anchorPrefix?: string }) {
  const name = [info.title, info.section].filter(Boolean).join(" · ") || id;
  const body = (
    <>
      {info.cited != null && <span className="cite" title="Cited in the answer">{info.cited}</span>}
      <span className="tp-name">{name}</span>
    </>
  );
  const cls = `tp tp-${info.label ?? "unjudged"}`;
  const title = [LABEL_TITLE[info.label ?? ""], id].filter(Boolean).join(" · ");
  return anchorPrefix ? (
    <a className={cls} href={`#${anchorPrefix}${id}`} title={title}>{body}</a>
  ) : (
    <span className={cls} title={title}>{body}</span>
  );
}

export function TraceSteps({
  steps,
  passageInfo,
  anchorPrefix,
  working,
}: {
  steps: TraceStep[];
  /** Describe a passage by id; streamed steps carry their own titles, run pages pass labels and citations. */
  passageInfo?: (id: string) => PassageInfo;
  /** Link passages to `#${anchorPrefix}${id}` on the page. */
  anchorPrefix?: string;
  /** Still running: show a "working" row after the last step. */
  working?: string | null;
}) {
  if (!steps.length && !working) return null;
  return (
    <ol className="trace">
      {steps.map((s) => {
        const own = new Map((s.passages ?? []).map((p) => [p.chunk_id, p]));
        const ids = s.chunks ?? [];
        return (
          <li key={s.step} className={s.error ? "trace-error" : ""}>
            <span className="trace-n">{s.step}</span>
            <div style={{ minWidth: 0 }}>
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
              {ids.length > 0 && (
                <div className="tp-list">
                  {ids.map((id) => {
                    const p = own.get(id);
                    const info = { ...(p ? { title: p.title, section: p.section } : {}), ...(passageInfo?.(id) ?? {}) };
                    return <Passage key={id} id={id} info={info} anchorPrefix={anchorPrefix} />;
                  })}
                </div>
              )}
            </div>
          </li>
        );
      })}
      {working && (
        <li className="trace-working" role="status">
          <span className="trace-n">
            <span className="spinner" aria-hidden="true" />
          </span>
          <div className="muted">{working}</div>
        </li>
      )}
    </ol>
  );
}
