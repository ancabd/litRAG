import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { usePaper, usePaperChunks, useSearch } from "../api/hooks";
import { pdfUrl } from "../api/client";
import { ChunkCard } from "../components/ChunkCard";
import { ManualAdd } from "../components/ManualAdd";
import { CopyId, Empty, ErrorBanner, SearchIcon, StatusPill, useDebounced } from "../components/ui";
import { useRun } from "../run";

const ROLE: Record<string, string> = { seed: "Seed", reference: "Cited by a seed", citing: "Cites a seed" };

export function PaperPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { run } = useRun();
  const paper = usePaper(id);
  const chunks = usePaperChunks(id);
  const [q, setQ] = useState("");
  const query = useDebounced(q, 300);
  const within = useSearch(query, { paper: id, k: 20 });
  const p = paper.data;

  if (paper.error) {
    return (
      <div className="page">
        <ErrorBanner error={paper.error} />
        <Link to="/papers">Back to papers</Link>
      </div>
    );
  }
  if (!p) return null;
  const shown = query ? within.data?.items : chunks.data?.items;

  return (
    <div className="page">
      <a
        className="back"
        href="/papers"
        onClick={(e) => {
          e.preventDefault();
          if (window.history.length > 1) navigate(-1);
          else navigate("/papers");
        }}
      >
        Back to papers
      </a>
      <header className="paper-head">
        <h1>{p.title ?? "Untitled"}</h1>
        {p.authors && <p className="authors">{p.authors}</p>}
      </header>

      <dl className="facts">
        <dt>Id</dt>
        <dd>
          <span className="row">
            <span>{p.openalex_id}</span>
            <CopyId id={p.openalex_id} label="Copy" />
          </span>
        </dd>
        <dt>Published</dt>
        <dd>
          {p.year ?? "Year unknown"}
          {p.venue && `, ${p.venue}`}
        </dd>
        <dt>In the corpus</dt>
        <dd className="row">
          <StatusPill status={p.status} />
          {p.added_manually.length > 0 && (
            <span className="pill accent">{p.added_manually.includes("pdf") ? "PDF added by you" : "abstract added by you"}</span>
          )}
          {p.n_chunks !== undefined && <span className="muted">{p.n_chunks} chunk{p.n_chunks === 1 ? "" : "s"} in {p.run ?? run}</span>}
          {p.note && p.status !== "pdf" && <span className="muted xs">Download: {p.note}</span>}
        </dd>
        <dt>Why it's here</dt>
        <dd>
          {(p.roles ?? []).map((r) => ROLE[r] ?? r).join(", ")}
          {p.seeds.filter((s) => s.openalex_id !== p.openalex_id).length > 0 && (
            <>
              {" "}
              (
              {p.seeds
                .filter((s) => s.openalex_id !== p.openalex_id)
                .map((s, i) => (
                  <span key={s.openalex_id}>
                    {i > 0 && "; "}
                    <Link to={`/papers/${s.openalex_id}`}>{s.title}</Link>
                  </span>
                ))}
              )
            </>
          )}
        </dd>
        {p.cited_by_count != null && (
          <>
            <dt>Cited by</dt>
            <dd>{p.cited_by_count.toLocaleString()} papers</dd>
          </>
        )}
        <dt>Links</dt>
        <dd className="row">
          {p.pdf_available && (
            <a className="btn small primary" href={pdfUrl(p.openalex_id)} target="_blank" rel="noreferrer">
              Open PDF
            </a>
          )}
          {p.doi && (
            <a className="btn small" href={`https://doi.org/${p.doi}`} target="_blank" rel="noreferrer">
              DOI
            </a>
          )}
          <a className="btn small" href={`https://openalex.org/${p.openalex_id}`} target="_blank" rel="noreferrer">
            OpenAlex
          </a>
        </dd>
      </dl>

      <ManualAdd key={p.openalex_id} paper={p} />

      <section className="section-block">
        <h2>Abstract</h2>
        {p.abstract ? <p className="prose">{p.abstract}</p> : <p className="muted">No abstract available.</p>}
      </section>

      {p.questions.length > 0 && (
        <section className="section-block">
          <h2>Evidence for</h2>
          <ul className="stack" style={{ paddingLeft: 18, margin: 0 }}>
            {p.questions.map((q) => (
              <li key={q.id}>
                <Link to={`/questions/${q.id}`}>{q.question}</Link> <span className="id">{q.id}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="section-block">
        <div className="row" style={{ marginBottom: 10 }}>
          <h2>Chunks</h2>
          <span className="muted small">as the retriever sees this paper</span>
          <span className="spacer" />
          {(chunks.data?.items.length ?? 0) > 0 && (
            <div className="search-input" style={{ maxWidth: 320 }}>
              <SearchIcon />
              <input className="input" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search within this paper" aria-label="Search within this paper" />
            </div>
          )}
        </div>
        {chunks.data && chunks.data.items.length === 0 && (
          <Empty title="Nothing indexed for this paper">
            <p>
              {p.status === "metadata_only"
                ? "There was no free full text and no abstract, so there is nothing to search."
                : "This paper isn't in the selected chunk run. Re-run parse_corpus.py, or pick another run."}
            </p>
          </Empty>
        )}
        {shown?.map((c) => <ChunkCard key={c.chunk_id} chunk={c} />)}
        {query && within.data?.items.length === 0 && <p className="muted small">No chunks in this paper match.</p>}
      </section>
    </div>
  );
}
