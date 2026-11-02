// Making a corpus from the app: from seed papers (OpenAlex), or from your own documents.
// Both end in a background job that parses and chunks; CorpusJobView follows it.
import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  useBuildCorpus,
  useCorpus,
  useCorpusJob,
  useEverythingChanged,
  useReindex,
  useUploadDocument,
} from "../api/hooks";
import type { CorpusJob } from "../api/types";
import { ErrorBanner } from "./ui";

const SEED_EXAMPLE = `10.1103/PhysRevLett.98.146401
arxiv:2101.03164
W2963403868
Equivariant message passing for the prediction of tensorial properties`;

function size(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 2 ** 20) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / 2 ** 20).toFixed(1)} MB`;
}

// ------------------------------------------------------------------ job progress

export function CorpusJobView({ id, onDone, onClose }: { id: string; onDone?: (job: CorpusJob) => void; onClose?: () => void }) {
  const job = useCorpusJob(id);
  const changed = useEverythingChanged();
  const j = job.data;
  const [showLog, setShowLog] = useState(false);
  const reported = useRef(false);
  useEffect(() => {
    if (j && j.state !== "running" && !reported.current) {
      reported.current = true;
      changed();
      onDone?.(j);
    }
  }, [j, changed, onDone]);
  if (job.error) return <ErrorBanner error={job.error} />;
  if (!j) return null;
  const log = j.meta?.log ?? [];
  const frac = j.total ? j.done / j.total : 0;
  const collecting = j.meta?.phase === "collect";
  const what = collecting
    ? j.total
      ? `Fetching full texts: ${j.done} of ${j.total} papers`
      : "Finding the seeds and the papers around them in OpenAlex…"
    : j.total
      ? `Parsing and chunking: ${j.done} of ${j.total} files`
      : "Chunking…";

  return (
    <div className="corpus-job" role="status">
      {j.state === "running" && (
        <>
          <div className="corpus-job-head">
            <span className="spinner" aria-hidden />
            <strong>{what}</strong>
          </div>
          <div className="job-bar">
            <span style={{ width: `${Math.round(frac * 100)}%` }} />
          </div>
          <p className="xs muted">You can leave this page; the build keeps going on the server.</p>
        </>
      )}
      {j.state === "error" && <ErrorBanner error={new Error(j.error ?? "The build failed")} />}
      {j.state === "done" && j.result && <JobSummary job={j} />}
      {log.length > 0 && (
        <div className="corpus-log">
          <button type="button" className="btn small ghost" onClick={() => setShowLog((v) => !v)}>
            {showLog ? "Hide log" : j.state === "running" ? "Show log" : "Show full log"}
          </button>
          {(showLog || j.state === "running") && (
            <pre className="code">{(showLog ? log : log.slice(-6)).join("\n")}</pre>
          )}
        </div>
      )}
      {j.state !== "running" && onClose && (
        <button type="button" className="btn small ghost corpus-close" onClick={onClose} aria-label="Dismiss">
          ×
        </button>
      )}
    </div>
  );
}

function JobSummary({ job }: { job: CorpusJob }) {
  const r = job.result!;
  const run = r.runs[0];
  const failures = Object.keys(run?.failures ?? {});
  return (
    <div className="corpus-done">
      <p>
        <strong>Done.</strong>{" "}
        {r.papers != null && <>{r.papers} papers collected. </>}
        {run ? (
          <>
            {run.chunks?.toLocaleString()} chunk{run.chunks === 1 ? "" : "s"} in <code>{run.run}</code>, ready to search.
          </>
        ) : (
          "No chunk runs to update."
        )}
      </p>
      {r.by_status && (
        <p className="small muted">
          {Object.entries(r.by_status)
            .map(([k, v]) => `${v} ${k === "pdf" ? "with full text" : k.replace("_", " ")}`)
            .join(" · ")}
        </p>
      )}
      {failures.length > 0 && (
        <p className="small muted">
          {failures.length} file{failures.length === 1 ? "" : "s"} couldn't be parsed ({failures.slice(0, 4).join(", ")}
          {failures.length > 4 ? ", …" : ""}); open them from the list for details.
        </p>
      )}
      <div className="row">
        <Link className="btn small" to="/search">Search the corpus</Link>
        <Link className="btn small" to="/ask">Ask a question</Link>
        <Link className="btn small" to="/questions">Write eval questions</Link>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ from seeds

export function SeedForm({ disabledReason, onStarted }: { disabledReason?: string; onStarted: (id: string) => void }) {
  const corpus = useCorpus();
  const build = useBuildCorpus();
  const [seeds, setSeeds] = useState("");
  const [maxCiting, setMaxCiting] = useState(50);
  const [recent, setRecent] = useState(0);
  const [download, setDownload] = useState(true);
  const [key, setKey] = useState("");
  const n = seeds.split("\n").filter((l) => l.trim() && !l.trim().startsWith("#")).length;
  const busy = !!corpus.data?.job || build.isPending;

  return (
    <form
      className="corpus-card"
      onSubmit={(e) => {
        e.preventDefault();
        build.mutate(
          { seeds, max_citing: maxCiting, recent_citing: recent, download, openalex_key: key || undefined },
          { onSuccess: (job) => onStarted(job.id) },
        );
      }}
    >
      <h2>From seed papers</h2>
      <p className="small muted">
        Name a few papers your topic starts from. The builder adds every paper they cite and the most-cited papers
        citing them, from OpenAlex, and downloads the free full texts.
      </p>
      <div className="field">
        <label htmlFor="seeds">Seeds, one per line</label>
        <textarea
          id="seeds"
          className="textarea"
          rows={5}
          value={seeds}
          placeholder={SEED_EXAMPLE}
          onChange={(e) => setSeeds(e.target.value)}
        />
        <span className="hint">A DOI, an arXiv id (arxiv:…), an OpenAlex id (W…) or an exact title.</span>
      </div>
      <div className="fields-row">
        <div className="field">
          <label htmlFor="max-citing">Most-cited citing papers per seed</label>
          <input id="max-citing" className="input narrow" type="number" min={0} max={500} value={maxCiting}
                 onChange={(e) => setMaxCiting(Number(e.target.value))} />
        </div>
        <div className="field">
          <label htmlFor="recent">Most recent citing papers per seed</label>
          <input id="recent" className="input narrow" type="number" min={0} max={500} value={recent}
                 onChange={(e) => setRecent(Number(e.target.value))} />
        </div>
      </div>
      <label className="check">
        <input type="checkbox" checked={download} onChange={(e) => setDownload(e.target.checked)} />
        Download free full texts (otherwise abstracts only, much faster)
      </label>
      {!corpus.data?.openalex_key && (
        <div className="field" style={{ marginTop: 14 }}>
          <label htmlFor="oa-key">OpenAlex API key (optional)</label>
          <input id="oa-key" className="input" type="password" autoComplete="off" value={key}
                 placeholder="Without one, OpenAlex's small keyless daily allowance is used"
                 onChange={(e) => setKey(e.target.value)} />
          <span className="hint">
            Free at openalex.org/settings/api. Used for this build only, not saved; set OPENALEX_API_KEY to skip this.
          </span>
        </div>
      )}
      {build.error && <ErrorBanner error={build.error} />}
      <div className="row" style={{ marginTop: 12 }}>
        <button type="submit" className="btn primary" disabled={!n || busy || !!disabledReason}>
          {build.isPending ? "Starting…" : `Build from ${n || ""} seed${n === 1 ? "" : "s"}`}
        </button>
        <span className="xs muted">
          {disabledReason ?? "Each seed typically brings 50–150 papers; with downloads, expect a few minutes."}
        </span>
      </div>
    </form>
  );
}

// ------------------------------------------------------------------ your own documents

type Queued = { file: File; state: "waiting" | "uploading" | "added" | "failed"; note?: string };

export function DocumentUpload({ onStarted, title = "From your own documents" }: { onStarted: (id: string) => void; title?: string }) {
  const corpus = useCorpus();
  const upload = useUploadDocument();
  const reindex = useReindex();
  const [queue, setQueue] = useState<Queued[]>([]);
  const [over, setOver] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const input = useRef<HTMLInputElement>(null);
  const suffixes = corpus.data?.suffixes ?? [".pdf", ".txt", ".md", ".html", ".docx"];
  const busy = running || !!corpus.data?.job;

  const add = (files: FileList | null) => {
    if (!files) return;
    const fresh = Array.from(files).map((file): Queued => {
      const ok = suffixes.some((s) => file.name.toLowerCase().endsWith(s));
      return ok ? { file, state: "waiting" } : { file, state: "failed", note: "unsupported file type" };
    });
    setQueue((q) => [...q.filter((x) => x.state !== "added"), ...fresh]);
  };

  const start = async () => {
    setRunning(true);
    setError(null);
    let added = 0;
    for (let i = 0; i < queue.length; i++) {
      if (queue[i].state !== "waiting") continue;
      setQueue((q) => q.map((x, j) => (j === i ? { ...x, state: "uploading" } : x)));
      try {
        const row = await upload.mutateAsync({ file: queue[i].file });
        added++;
        setQueue((q) => q.map((x, j) => (j === i ? { ...x, state: "added", note: `${row.openalex_id}: ${row.title}` } : x)));
      } catch (e) {
        setQueue((q) => q.map((x, j) => (j === i ? { ...x, state: "failed", note: (e as Error).message } : x)));
      }
    }
    try {
      if (added) onStarted((await reindex.mutateAsync()).id);
    } catch (e) {
      setError(e);
    }
    setRunning(false);
  };

  const waiting = queue.filter((x) => x.state === "waiting").length;
  return (
    <div className="corpus-card">
      <h2>{title}</h2>
      <p className="small muted">
        Any text works, not only papers: notes, manuals, reports, saved web pages. Each file becomes one document
        (D0001, D0002, …), split into sections by its headings.
      </p>
      <div
        className={`dropzone ${over ? "over" : ""} ${busy ? "disabled" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          if (!busy) setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          if (!busy) add(e.dataTransfer.files);
        }}
      >
        <span>Drop files here, or</span>
        <button type="button" className="btn small" disabled={busy} onClick={() => input.current?.click()}>
          Choose files
        </button>
        <span className="xs muted">{suffixes.join(" ")}</span>
        <input ref={input} type="file" multiple hidden accept={suffixes.join(",")}
               onChange={(e) => {
                 add(e.target.files);
                 e.target.value = "";
               }} />
      </div>
      {queue.length > 0 && (
        <ul className="upload-list">
          {queue.map((x, i) => (
            <li key={`${x.file.name}-${i}`} className={`upload-${x.state}`}>
              <span className="upload-name">{x.file.name}</span>
              <span className="xs muted">{size(x.file.size)}</span>
              <span className="upload-note xs">
                {x.state === "uploading" ? "uploading…" : x.state === "waiting" ? "ready" : x.note}
              </span>
              {x.state !== "uploading" && !running && x.state !== "added" && (
                <button type="button" className="btn small ghost" aria-label={`Remove ${x.file.name}`}
                        onClick={() => setQueue((q) => q.filter((_, j) => j !== i))}>
                  ×
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
      {error != null && <ErrorBanner error={error} />}
      <div className="row" style={{ marginTop: 12 }}>
        <button type="button" className="btn primary" disabled={!waiting || busy} onClick={start}>
          {running ? "Adding…" : `Add ${waiting || ""} document${waiting === 1 ? "" : "s"}`}
        </button>
        <span className="xs muted">They're parsed and chunked right after, so they're searchable straight away.</span>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ the empty state

/** Shown on the Papers page while the corpus has nothing in it. */
export function CorpusStart({ corpusDir, onStarted }: { corpusDir?: string; onStarted: (id: string) => void }) {
  return (
    <>
      <div className="page-head">
        <div>
          <h1>Build a corpus</h1>
          <p className="sub">
            There's nothing to search yet. Start from a few seed papers, or upload your own documents. You can do both.
          </p>
        </div>
      </div>
      <div className="corpus-start">
        <SeedForm onStarted={onStarted} />
        <DocumentUpload onStarted={onStarted} />
      </div>
      {corpusDir && (
        <p className="xs muted" style={{ marginTop: 16 }}>
          Files go to <code>{corpusDir}</code>. The command line does the same: <code>python corpus_builder.py seeds.txt</code>{" "}
          then <code>python parse_corpus.py run</code>.
        </p>
      )}
    </>
  );
}

/** The running (or just finished) corpus job, resumed from the server if the page was reloaded. */
export function useCorpusJobId(): [string | null, (id: string | null) => void] {
  const corpus = useCorpus();
  const handed = (useLocation().state as { corpusJob?: string } | null)?.corpusJob ?? null; // e.g. after removing a document
  const [id, setId] = useState<string | null>(handed);
  const running = corpus.data?.job?.id ?? null;
  useEffect(() => {
    if (running && !id) setId(running);
  }, [running, id]);
  return [id, setId];
}
