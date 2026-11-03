import { useEffect, useState, type ReactNode } from "react";
import { ApiError, pdfUrl } from "../api/client";

export const STATUS_LABEL: Record<string, string> = {
  pdf: "Full text",
  abstract_only: "Abstract only",
  metadata_only: "Metadata only",
  not_downloaded: "Not downloaded",
  document: "Document",
};

export const TYPE_LABEL: Record<string, string> = {
  lookup: "Lookup",
  multihop: "Multi-hop",
  comparison: "Comparison",
  unanswerable: "Unanswerable",
};

export function StatusPill({ status }: { status: string }) {
  const tone = status === "pdf" || status === "document" ? "ok" : status === "metadata_only" ? "warn" : "";
  return <span className={`pill ${tone}`}>{STATUS_LABEL[status] ?? status}</span>;
}

const DOT_TITLE: Record<string, string> = {
  ok: "All evidence found in the chunks",
  problem: "Some evidence can't be found in the chunks",
  none: "No evidence needed",
  unchecked: "No chunks to check against",
};

export function EvidenceDot({ status }: { status: string }) {
  return <span className={`dot ${status}`} title={DOT_TITLE[status]} aria-label={DOT_TITLE[status]} />;
}

/** Text with highlighted character spans (evidence matches). */
export function Highlighted({ text, spans }: { text: string; spans?: [number, number][] }) {
  if (!spans || spans.length === 0) return <>{text}</>;
  const parts: ReactNode[] = [];
  let at = 0;
  spans.forEach(([s, e], i) => {
    if (s > at) parts.push(text.slice(at, s));
    parts.push(<mark key={i}>{text.slice(s, e)}</mark>);
    at = e;
  });
  if (at < text.length) parts.push(text.slice(at));
  return <>{parts}</>;
}

export function CopyId({ id, label }: { id: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      className="copy id"
      title="Copy id"
      onClick={(e) => {
        e.stopPropagation();
        navigator.clipboard?.writeText(id).then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 1200);
        });
      }}
    >
      {copied ? "Copied" : label ?? id}
    </button>
  );
}

export function Seg<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: { value: T; label: string; n?: number }[];
  onChange: (v: T) => void;
  label: string;
}) {
  return (
    <div className="seg" role="group" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} type="button" aria-pressed={o.value === value} onClick={() => onChange(o.value)}>
          {o.label}
          {o.n !== undefined && <span className="n">{o.n}</span>}
        </button>
      ))}
    </div>
  );
}

export function ErrorBanner({ error, action }: { error: unknown; action?: ReactNode }) {
  const e = error instanceof ApiError ? error : null;
  const message = e?.message ?? (error instanceof Error ? error.message : String(error));
  return (
    <div className="banner danger" role="alert">
      <div>
        {message}
        {e && e.details.length > 0 && (
          <ul>
            {e.details.map((d) => (
              <li key={d}>{d.replace(/^[^,]+, /, "")}</li>
            ))}
          </ul>
        )}
      </div>
      {action}
    </div>
  );
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="empty">
      <h2>{title}</h2>
      {children}
    </div>
  );
}

export function useDebounced<T>(value: T, ms = 300): T {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return v;
}

type Paged = {
  page_start: number | null;
  page_end: number | null;
  page_label_start?: string | null;
  page_label_end?: string | null;
  source?: string;
};

/** "p. 12" or "pp. 12–13", with the page numbers printed in the document when it has its own (books). */
export function pages(c: Paged): string {
  if (c.page_start == null) return ""; // abstracts and text documents have no pages
  const start = c.page_label_start || String(c.page_start);
  const end = c.page_end != null ? c.page_label_end || String(c.page_end) : start;
  return c.page_end && c.page_end !== c.page_start ? `pp. ${start}–${end}` : `p. ${start}`;
}

/** A destructive button that asks for a second click instead of a dialog. */
export function ConfirmButton({
  label,
  confirm = "Click again to confirm",
  busy,
  busyLabel = "Removing…",
  disabled,
  onConfirm,
  className = "btn small",
}: {
  label: string;
  confirm?: string;
  busy?: boolean;
  busyLabel?: string;
  disabled?: boolean;
  onConfirm: () => void;
  className?: string;
}) {
  const [armed, setArmed] = useState(false);
  useEffect(() => {
    if (!armed) return;
    const t = setTimeout(() => setArmed(false), 4000);
    return () => clearTimeout(t);
  }, [armed]);
  return (
    <button
      type="button"
      className={`${className} ${armed ? "danger armed" : ""}`}
      disabled={disabled || busy}
      onBlur={() => setArmed(false)}
      onClick={(e) => {
        e.stopPropagation();
        if (!armed) return setArmed(true);
        setArmed(false);
        onConfirm();
      }}
    >
      {busy ? busyLabel : armed ? confirm : label}
    </button>
  );
}

/** The page reference, linked to the PDF opened at that page. */
export function PageRef({ chunk, className = "page-ref" }: { chunk: Paged & { paper_id: string }; className?: string }) {
  const label = pages(chunk);
  if (!label) return null;
  const printed = chunk.page_label_start && chunk.page_label_start !== String(chunk.page_start);
  return (
    <a
      className={className}
      href={`${pdfUrl(chunk.paper_id)}#page=${chunk.page_start}`}
      target="_blank"
      rel="noreferrer"
      title={`Open the PDF at this page${printed ? ` (page ${chunk.page_start} of the PDF file)` : ""}`}
      onClick={(e) => e.stopPropagation()}
    >
      {label}
    </a>
  );
}

export function SearchIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="7" cy="7" r="4.75" stroke="currentColor" strokeWidth="1.5" />
      <path d="M10.5 10.5 14 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

/** Logo: a potential-energy curve with a point in its well. */
export function Logo() {
  return (
    <svg width="22" height="22" viewBox="0 0 32 32" aria-hidden="true">
      <path d="M3 5 C6 26, 12 27, 16 24 S 24 15, 30 16" fill="none" stroke="var(--accent)" strokeWidth="2.6"
        strokeLinecap="round" />
      <circle cx="11.6" cy="24.6" r="3.1" fill="var(--mark)" stroke="var(--accent)" strokeWidth="1.2" />
    </svg>
  );
}

export function Toast({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div className="toast" role="status">
      {message}
    </div>
  );
}

export function useToast(): [string | null, (m: string) => void] {
  const [msg, setMsg] = useState<string | null>(null);
  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(() => setMsg(null), 2200);
    return () => clearTimeout(t);
  }, [msg]);
  return [msg, setMsg];
}
