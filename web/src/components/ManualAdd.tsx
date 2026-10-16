// Adding what the corpus builder couldn't get: a PDF you have, or an abstract.
import { useEffect, useRef, useState, type ReactNode } from "react";
import { useAddPdf, useRemovePdf, useSetAbstract } from "../api/hooks";
import type { IngestResult, PaperDetail } from "../api/types";
import { ErrorBanner } from "./ui";

/** Plain-language outcome of re-chunking, per chunk run. */
export function IngestSummary({ results }: { results: IngestResult[] }) {
  if (results.length === 0) {
    return <p className="small muted">Saved. There are no chunk runs yet, so run parse_corpus.py to index it.</p>;
  }
  return (
    <ul className="ingest">
      {results.map((r) => (
        <li key={r.run} className={r.error ? "warn" : "ok"}>
          <span className={`dot ${r.error ? "problem" : "ok"}`} />
          <span>
            <strong>{r.run}</strong>:{" "}
            {r.source === "pdf" && `${r.n_chunks} chunks from the full text.`}
            {r.source === "abstract_fallback" &&
              `the PDF couldn't be parsed (${r.error}), so the abstract is used instead.`}
            {r.source === "abstract" && `${r.n_chunks} chunk${r.n_chunks === 1 ? "" : "s"} from the abstract.`}
            {(r.source === "skipped" || !r.source) && "nothing to index."}
            {r.warnings && <span className="muted"> Parser note: {r.warnings}</span>}
          </span>
        </li>
      ))}
    </ul>
  );
}

const isPdf = (f: File) => f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf");

/** A drop target + file picker for one PDF. */
export function PdfDrop({
  onFile,
  disabled,
  children,
}: {
  onFile: (f: File) => void;
  disabled?: boolean;
  children: ReactNode;
}) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const [wrong, setWrong] = useState(false);
  const take = (f: File | undefined) => {
    if (!f) return;
    if (!isPdf(f)) {
      setWrong(true);
      return;
    }
    setWrong(false);
    onFile(f);
  };
  return (
    <div
      className={`dropzone ${over ? "over" : ""} ${disabled ? "disabled" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setOver(false);
        if (!disabled) take(e.dataTransfer.files[0]);
      }}
    >
      {children}
      <button type="button" className="btn" disabled={disabled} onClick={() => input.current?.click()}>
        Choose PDF
      </button>
      <input
        ref={input}
        type="file"
        accept="application/pdf,.pdf"
        hidden
        onChange={(e) => {
          take(e.target.files?.[0]);
          e.target.value = "";
        }}
      />
      {wrong && <p className="small" style={{ color: "var(--danger)" }}>That isn't a PDF file.</p>}
    </div>
  );
}

export function ManualAdd({ paper }: { paper: PaperDetail }) {
  const add = useAddPdf();
  const remove = useRemovePdf();
  const setAbstract = useSetAbstract();
  const savedAbstract = paper.abstract_source === "manual" ? paper.abstract ?? "" : "";
  const [abstract, setText] = useState(savedAbstract);
  useEffect(() => setText(savedAbstract), [savedAbstract]); // follow the saved value after each change
  const manualPdf = paper.added_manually.includes("pdf");
  const canEditAbstract = !paper.abstract || paper.abstract_source === "manual";
  const busy = add.isPending || remove.isPending || setAbstract.isPending;
  const last = add.data ?? remove.data ?? setAbstract.data;
  const error = add.error ?? remove.error ?? setAbstract.error;

  if (paper.status === "pdf" && !manualPdf && !last) return null;

  return (
    <section className="section-block manual">
      <h2>{manualPdf ? "Full text you added" : "Add what's missing"}</h2>

      {!manualPdf && (
        <>
          <p className="small" style={{ color: "var(--ink-2)", maxWidth: "70ch", margin: "6px 0 10px" }}>
            No free full text was found for this paper. If you have the PDF, for example through your library, add it
            here. It's saved to <code className="code">corpus/pdfs/{paper.openalex_id}.pdf</code>, recorded in the
            manifest (and kept when the corpus builder runs again), and parsed into every chunk run.
          </p>
          <PdfDrop onFile={(file) => add.mutate({ paperId: paper.openalex_id, file })} disabled={busy}>
            <span className="small">{add.isPending ? "Adding the PDF and re-chunking…" : "Drop the PDF here, or"}</span>
          </PdfDrop>
        </>
      )}

      {manualPdf && (
        <div className="row" style={{ marginTop: 8 }}>
          <span className="small" style={{ color: "var(--ink-2)" }}>
            You added this paper's PDF by hand. Removing it deletes the file and goes back to the abstract.
          </span>
          <button
            type="button"
            className="btn small danger"
            disabled={busy}
            onClick={() => {
              if (window.confirm("Remove the PDF you added? The file is deleted from corpus/pdfs.")) remove.mutate(paper.openalex_id);
            }}
          >
            {remove.isPending ? "Removing…" : "Remove PDF"}
          </button>
        </div>
      )}

      {canEditAbstract && paper.status !== "pdf" && (
        <div className="field" style={{ marginTop: 18 }}>
          <label htmlFor="manual-abstract">{paper.abstract_source === "manual" ? "Abstract you added" : "Or add the abstract"}</label>
          <textarea
            id="manual-abstract"
            className="textarea"
            style={{ fontFamily: "var(--serif)", fontSize: 15 }}
            rows={5}
            value={abstract}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste the abstract from the publisher's page. It becomes searchable right away."
          />
          <div className="row">
            <button
              type="button"
              className="btn primary small"
              disabled={busy || !abstract.trim() || abstract.trim() === (paper.abstract ?? "")}
              onClick={() => setAbstract.mutate({ paperId: paper.openalex_id, abstract })}
            >
              {setAbstract.isPending ? "Saving…" : "Save abstract"}
            </button>
            {paper.abstract_source === "manual" && (
              <button
                type="button"
                className="btn small ghost danger"
                disabled={busy}
                onClick={() => {
                  setText("");
                  setAbstract.mutate({ paperId: paper.openalex_id, abstract: "" });
                }}
              >
                Remove abstract
              </button>
            )}
          </div>
        </div>
      )}

      {error && <ErrorBanner error={error} />}
      {last && !busy && <IngestSummary results={last.ingest} />}
    </section>
  );
}
