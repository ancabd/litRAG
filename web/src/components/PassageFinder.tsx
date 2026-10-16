// Search the corpus from inside the question editor and turn a passage into evidence.
import { useState } from "react";
import { useSearch } from "../api/hooks";
import { ChunkCard } from "./ChunkCard";
import { ErrorBanner, SearchIcon, useDebounced } from "./ui";

function firstWords(text: string, n = 25): string {
  const sentence = text.split(/(?<=[.!?])\s+/)[0] ?? text;
  const words = sentence.split(/\s+/);
  return words.slice(0, n).join(" ");
}

export function PassageFinder({ onUse }: { onUse: (paper: string, quote: string) => void }) {
  const [q, setQ] = useState("");
  const query = useDebounced(q, 350);
  const search = useSearch(query, { k: 8 });

  return (
    <div className="finder">
      <div className="search-input">
        <SearchIcon />
        <input
          className="input"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search the corpus for the passage that answers this"
          aria-label="Search passages"
        />
      </div>
      <p className="xs muted" style={{ marginTop: 6 }}>
        Select words in a passage to quote just those, or use its first sentence. Searching with your question's
        own words makes keyword search look better than it is, so try other terms.
      </p>
      {search.error && <ErrorBanner error={search.error} />}
      <div className="results">
        {search.data?.items.map((hit) => (
          <ChunkCard
            key={hit.chunk_id}
            chunk={hit}
            showPaper
            actions={(selection) => (
              <>
                <button
                  type="button"
                  className="btn small primary"
                  disabled={!selection}
                  onClick={() => onUse(hit.paper_id, selection)}
                >
                  Quote selection
                </button>
                <button type="button" className="btn small" onClick={() => onUse(hit.paper_id, firstWords(hit.text))}>
                  Quote first sentence
                </button>
              </>
            )}
          />
        ))}
        {search.data && search.data.items.length === 0 && <p className="muted small">No passages match.</p>}
      </div>
    </div>
  );
}
