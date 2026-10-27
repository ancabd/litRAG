// Search the chunks with any retriever: BM25, dense or hybrid. The Ask page reuses the same results view.
import { useSearchParams } from "react-router-dom";
import { useMeta, useSearch } from "../api/hooks";
import { ChunkCard } from "../components/ChunkCard";
import { DenseNote, RetrieverSelect } from "../components/RetrieverSelect";
import { Empty, ErrorBanner, SearchIcon, useDebounced } from "../components/ui";
import { useRun } from "../run";

export function SearchPage() {
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const retriever = params.get("r") ?? "bm25";
  const query = useDebounced(q, 300);
  const search = useSearch(query, { k: 20, retriever });
  const update = (next: { q?: string; r?: string }) => {
    const p: Record<string, string> = {};
    const nq = next.q ?? q;
    const nr = next.r ?? retriever;
    if (nq) p.q = nq;
    if (nr !== "bm25") p.r = nr;
    setParams(p, { replace: true });
  };
  const meta = useMeta();
  const { run } = useRun();

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Search</h1>
          <p className="sub">Search every chunk in {run ?? "the selected run"}, by keywords (BM25), by meaning (dense), or both (hybrid).</p>
        </div>
      </div>
      <div className="toolbar">
        <div className="search-input" style={{ maxWidth: 720 }}>
          <SearchIcon />
          <input
            className="input"
            autoFocus
            style={{ height: 40, fontSize: 15 }}
            value={q}
            onChange={(e) => update({ q: e.target.value })}
            placeholder="e.g. radial symmetry function cutoff"
            aria-label="Search the corpus"
          />
        </div>
        <RetrieverSelect value={retriever} onChange={(r) => update({ r })} />
      </div>
      <DenseNote retriever={retriever} />
      {search.error && <ErrorBanner error={search.error} />}
      {!q && meta.data && meta.data.runs.length === 0 && (
        <Empty title="Nothing to search yet">
          <p>
            Parse the corpus first: <code>python parse_corpus.py run</code> in corpus-builder.
          </p>
        </Empty>
      )}
      {search.isFetching && !search.data && q && <p className="muted small">Searching…</p>}
      <div style={{ maxWidth: 820, opacity: search.isPlaceholderData ? 0.6 : 1 }}>
        {search.data?.items.map((hit) => (
          <ChunkCard key={hit.chunk_id} chunk={hit} showPaper />
        ))}
        {search.data && search.data.items.length === 0 && <p className="muted">No chunks match "{query}".</p>}
      </div>
    </div>
  );
}
