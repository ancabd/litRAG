import { useRef, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import type { Chunk, SearchHit } from "../api/types";
import { Highlighted, pages } from "./ui";

/** A passage from a paper. `showPaper` adds the paper title (search results). */
export function ChunkCard({
  chunk,
  showPaper,
  clamp = true,
  actions,
}: {
  chunk: Chunk | SearchHit;
  showPaper?: boolean;
  clamp?: boolean;
  actions?: (selection: string) => ReactNode;
}) {
  const [expanded, setExpanded] = useState(!clamp);
  const [selection, setSelection] = useState("");
  const ref = useRef<HTMLParagraphElement>(null);
  const hit = "title" in chunk ? (chunk as SearchHit) : null;

  const readSelection = () => {
    const sel = window.getSelection();
    if (sel && ref.current && sel.anchorNode && ref.current.contains(sel.anchorNode)) {
      setSelection(sel.toString().trim());
    } else setSelection("");
  };

  return (
    <article className="chunk">
      {showPaper && hit && (
        <div className="row" style={{ marginBottom: 4 }}>
          <Link to={`/papers/${chunk.paper_id}`} className="paper-title">
            {hit.title ?? chunk.paper_id}
          </Link>
          <span className="muted small">{hit.year}</span>
        </div>
      )}
      <div className="chunk-head">
        <span className="section">{chunk.section}</span>
        <span className="muted">{pages(chunk)}</span>
        <span className="id">{chunk.chunk_id}</span>
        {chunk.source !== "pdf" && <span className="pill">from abstract</span>}
        {chunk.coverage !== undefined && (
          <span className="muted xs">{Math.round(chunk.coverage * 100)}% of quote</span>
        )}
      </div>
      <p ref={ref} className={`prose ${expanded ? "" : "clamped"}`} onMouseUp={readSelection} onKeyUp={readSelection}>
        <Highlighted text={chunk.text} spans={chunk.highlights} />
      </p>
      <div className="chunk-actions">
        {clamp && chunk.n_words > 70 && (
          <button type="button" className="btn ghost small" onClick={() => setExpanded((e) => !e)}>
            {expanded ? "Show less" : "Show all"}
          </button>
        )}
        {actions?.(selection)}
      </div>
    </article>
  );
}
