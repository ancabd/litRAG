// Search the chunks with the selected retriever. When answer generation exists,
// an "Ask" page will sit next to this one and reuse the same results view.
import { useSearchParams } from "react-router-dom";
import { useMeta, useSearch } from "../api/hooks";
import { ChunkCard } from "../components/ChunkCard";
import { Empty, ErrorBanner, SearchIcon, useDebounced } from "../components/ui";
import { useRun } from "../run";

export function SearchPage() {
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const query = useDebounced(q, 300);
  const search = useSearch(query, { k: 20 });
  const meta = useMeta();
  const { run } = useRun();

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Search</h1>
          <p className="sub">Keyword search (BM25) over every chunk in {run ?? "the selected run"}.</p>
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
            onChange={(e) => setParams(e.target.value ? { q: e.target.value } : {}, { replace: true })}
            placeholder="e.g. radial symmetry function cutoff"
            aria-label="Search the corpus"
          />
        </div>
      </div>
      {search.error && <ErrorBanner error={search.error} />}
      {!q && meta.data && meta.data.runs.length === 0 && (
        <Empty title="Nothing to search yet">
          <p>
            Parse the corpus first: <code>python parse_corpus.py run</code> in corpus-builder.
          </p>
        </Empty>
      )}
      <div style={{ maxWidth: 820, opacity: search.isPlaceholderData ? 0.6 : 1 }}>
        {search.data?.items.map((hit) => (
          <ChunkCard key={hit.chunk_id} chunk={hit} showPaper />
        ))}
        {search.data && search.data.items.length === 0 && <p className="muted">No chunks match "{query}".</p>}
      </div>
    </div>
  );
}
