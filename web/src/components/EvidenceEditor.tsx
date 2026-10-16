// One evidence item: paper + quote, checked live against the selected chunk run.
import { useEvidenceCheck } from "../api/hooks";
import type { Evidence } from "../api/types";
import { useRun } from "../run";
import { ChunkCard } from "./ChunkCard";
import { PaperPicker } from "./PaperPicker";
import { pages, useDebounced } from "./ui";

export function EvidenceEditor({
  value,
  index,
  onChange,
  onRemove,
}: {
  value: Evidence;
  index: number;
  onChange: (e: Evidence) => void;
  onRemove: () => void;
}) {
  const { run } = useRun();
  const quote = useDebounced(value.quote ?? "", 400);
  const check = useEvidenceCheck(value.paper ?? "", quote);
  const r = check.data;
  const stale = check.isFetching || quote !== (value.quote ?? "");

  return (
    <div className="evidence">
      <div className="evidence-grid">
        <PaperPicker
          value={value.paper}
          title={r?.paper === value.paper ? r.title : value.title}
          onChange={(paper, p) => onChange({ ...value, paper, title: p?.title ?? null })}
        />
        <button type="button" className="btn ghost small" onClick={onRemove} aria-label={`Remove evidence ${index + 1}`}>
          Remove
        </button>
      </div>
      <textarea
        className="textarea quote-input"
        style={{ marginTop: 8 }}
        rows={2}
        value={value.quote ?? ""}
        placeholder="Quote 10–30 words from the passage that answers the question"
        aria-label="Quote"
        onChange={(e) => onChange({ ...value, quote: e.target.value })}
      />

      {value.paper && r && (
        <div className="match" aria-live="polite" style={{ opacity: stale ? 0.6 : 1 }}>
          {r.status === "ok" && (
            <>
              <div className="match-status ok">
                <span className="dot ok" />
                Found in {r.gold.map((g) => g.chunk_id).join(", ")}
                <span className="muted">
                  {r.gold[0].section}
                  {pages(r.gold[0]) && `, ${pages(r.gold[0])}`}
                </span>
              </div>
              <ChunkCard chunk={r.gold[0]} />
            </>
          )}
          {r.status === "not_found" && (
            <>
              <div className="match-status warn">
                <span className="dot problem" />
                No chunk contains enough of this quote. Check for typos, or quote prose rather than an equation.
              </div>
              {r.closest.length > 0 && <p className="xs muted" style={{ marginTop: 6 }}>Closest passages:</p>}
              {r.closest.slice(0, 2).map((c) => (
                <ChunkCard key={c.chunk_id} chunk={c} />
              ))}
            </>
          )}
          {r.status === "no_quote" && (
            <div className="match-status muted">Add a quote so the right passage can be found.</div>
          )}
          {r.status === "paper_missing" && (
            <div className="match-status warn">
              <span className="dot problem" />
              {r.manifest_status
                ? `This paper has no chunks in ${run} (it's ${r.manifest_status.replace("_", " ")}), so it can't be evidence.`
                : "No paper with this id in the corpus."}
            </div>
          )}
        </div>
      )}

      {(value.alternatives ?? []).length > 0 && (
        <div className="alts">
          <span className="xs muted">
            Also accepted (lenient scoring): passages you marked in the review that answer this too
          </span>
          <ul>
            {(value.alternatives ?? []).map((a, i) => (
              <li key={`${a.paper}:${i}`}>
                <span className="alt-title">{a.title ?? a.paper}</span>
                <span className="alt-quote">“{a.quote.split(" ").slice(0, 14).join(" ")}…”</span>
                <button
                  type="button"
                  className="btn ghost small"
                  aria-label={`Remove alternative ${i + 1}`}
                  onClick={() => onChange({ ...value, alternatives: (value.alternatives ?? []).filter((_, j) => j !== i) })}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
