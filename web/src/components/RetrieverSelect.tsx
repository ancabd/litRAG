// Pick a retriever: BM25, dense or hybrid, with the embedding model. Names are the ones evaluate.py takes.
import { useBuildIndex, useIndexes, useMeta } from "../api/hooks";
import type { EmbeddingIndex } from "../api/types";
import { ErrorBanner } from "./ui";

export const isDense = (name: string) => name.startsWith("dense") || name.startsWith("hybrid");

export function RetrieverSelect({ value, onChange, id }: { value: string; onChange: (v: string) => void; id?: string }) {
  const meta = useMeta();
  const options = meta.data?.retriever_choices ?? [{ name: "bm25", label: "BM25 (keywords)" }];
  return (
    <select id={id} className="select" value={value} onChange={(e) => onChange(e.target.value)} aria-label="Retriever">
      {options.map((o) => (
        <option key={o.name} value={o.name}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

/** The embedding model a retriever name uses: dense -> nomic, hybrid:bge-small -> bge-small, bm25 -> null. */
export function modelOf(name: string): string | null {
  if (!isDense(name)) return null;
  return name.split(":")[1] ?? "nomic";
}

function IndexLine({ index, installed }: { index: EmbeddingIndex; installed: boolean }) {
  const build = useBuildIndex();
  const job = index.job;
  if (index.ready)
    return (
      <span className="small">
        <span className="dot ok" aria-hidden="true" /> {index.model} embeddings ready ({index.chunks.toLocaleString()} chunks)
      </span>
    );
  if (job) {
    const frac = job.total ? job.done / job.total : 0;
    return (
      <span className="index-progress small" role="status">
        <span className="job-bar"><span style={{ width: `${Math.round(frac * 100)}%` }} /></span>
        Embedding with {index.model}: {job.done.toLocaleString()} of {(job.total ?? index.chunks).toLocaleString()} chunks
      </span>
    );
  }
  if (!installed)
    return (
      <span className="small">
        <span className="dot problem" aria-hidden="true" /> Needs the dense packages:{" "}
        <span className="mono">pip install -r corpus-builder/requirements-dense.txt</span>, then restart the server.
      </span>
    );
  return (
    <span className="row small" style={{ gap: 8 }}>
      <span>
        <span className="dot problem" aria-hidden="true" /> {index.model} embeddings not built
        {index.embedded > 0 && ` (${index.embedded} of ${index.chunks} chunks, the rest changed)`}
      </span>
      <button type="button" className="btn small" disabled={build.isPending} onClick={() => build.mutate(index.model)}>
        {build.isPending ? "Starting…" : index.embedded > 0 ? "Update" : "Build now"}
      </button>
      <span className="xs muted">a minute or two on a CPU; the first time also downloads the model</span>
      {build.error && <ErrorBanner error={build.error} />}
    </span>
  );
}

/** Next to a retriever menu: is the chosen model's index ready, and a button to build it. */
export function DenseNote({ retriever }: { retriever: string }) {
  const indexes = useIndexes();
  const model = modelOf(retriever);
  if (!model || !indexes.data) return null;
  const index = indexes.data.models.find((m) => m.model === model);
  if (!index) return null;
  return (
    <div className="dense-note">
      <IndexLine index={index} installed={indexes.data.installed} />
    </div>
  );
}

/** All embedding indexes of the current chunk run (Settings). */
export function IndexPanel() {
  const indexes = useIndexes();
  if (indexes.error) return <ErrorBanner error={indexes.error} />;
  if (!indexes.data) return null;
  return (
    <div className="index-panel">
      {indexes.data.models.map((m) => (
        <div key={m.model} className="index-row">
          <div>
            <b>{m.model}</b> <span className="mono xs muted">{m.model_id}</span>
            <div className="xs muted">{m.note}</div>
          </div>
          <IndexLine index={m} installed={indexes.data!.installed} />
        </div>
      ))}
      <p className="xs muted">
        For the chunk run <span className="mono">{indexes.data.run}</span> (pick another in the sidebar). Dense and hybrid with
        the same model share one index. Embeddings are kept in <span className="mono">data/chunks/{indexes.data.run}/embeddings/</span>;
        after you add a PDF, only the changed chunks need embedding again.
      </p>
    </div>
  );
}

/** "bm25", "dense (bge-small)", "hybrid (nomic)" from a run's stored retriever config. */
export function retrieverLabel(cfg: { name?: string; preset?: unknown; dense?: unknown } | null | undefined): string {
  if (!cfg?.name) return "";
  if (cfg.name === "dense") return `dense (${String(cfg.preset ?? "")})`;
  if (cfg.name === "hybrid") return `hybrid (${String((cfg.dense as { preset?: string } | undefined)?.preset ?? "")})`;
  return cfg.name;
}
