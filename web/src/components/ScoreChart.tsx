// Mean + 95% bootstrap CI per metric, strict vs lenient, on a fixed 0–1 scale.
// With a handful of questions the intervals are wide; showing them is the point.
import { useState } from "react";
import type { Interval } from "../api/types";

const LABELS: Record<string, string> = {
  "hit@1": "Hit@1",
  "hit@5": "Hit@5",
  "hit@10": "Hit@10",
  "recall@10": "Recall@10",
  mrr: "MRR",
  "ndcg@10": "nDCG@10",
  "paper_hit@10": "Right paper@10",
  correct: "Correct",
  supported: "Supported by citations",
  cites_gold: "Cites your evidence",
  retrieved_gold: "Evidence retrieved",
  invalid_citations: "Invalid citations ↓",
  abstained_when_unanswerable: "Declines unanswerable",
  abstained_when_answerable: "Declines answerable ↓",
};

const pct = (v: number) => `${(v * 100).toFixed(1)}%`;
const fmt = (i: Interval) => `${i.mean.toFixed(2)} [${i.lo.toFixed(2)}–${i.hi.toFixed(2)}]`;

export function ScoreChart({
  results,
  metrics,
  strictLabel = "Strict: only your original evidence",
}: {
  results: Record<string, Interval>;
  metrics: string[];
  /** Legend text for the main series; null hides the legend swatch (single-series charts). */
  strictLabel?: string | null;
}) {
  const [tip, setTip] = useState<{ x: number; y: number; text: string } | null>(null);
  const rows = metrics.filter((m) => results[m]);
  const hasLenient = rows.some((m) => results[`lenient_${m}`]);

  const mark = (m: string, i: Interval, which: "strict" | "lenient") => (
    <div
      className={`ci ci-${which}`}
      style={{ left: pct(i.lo), width: `max(2px, ${pct(i.hi - i.lo)})` }}
      onMouseMove={(e) => {
        const box = (e.currentTarget.closest(".scorechart") as HTMLElement).getBoundingClientRect();
        setTip({ x: e.clientX - box.left, y: e.clientY - box.top, text: `${LABELS[m] ?? m}${which === "strict" && !hasLenient ? "" : `, ${which}`}: ${fmt(i)} (n=${i.n})` });
      }}
      onMouseLeave={() => setTip(null)}
    >
      <span className="ci-dot" style={{ left: i.hi > i.lo ? pct((i.mean - i.lo) / (i.hi - i.lo)) : "50%" }} />
    </div>
  );

  return (
    <figure className="scorechart" aria-label="Scores with 95% confidence intervals">
      <div className="sc-legend">
        {(strictLabel || hasLenient) && (
          <span>
            <i className="sw sw-strict" /> {strictLabel ?? "Score"}
          </span>
        )}
        {hasLenient && (
          <span>
            <i className="sw sw-lenient" /> Lenient: alternatives count too
          </span>
        )}
        <span className="muted">Dot: mean. Line: 95% bootstrap interval.</span>
      </div>
      <div className="sc-grid">
        <div />
        <div className="sc-axis" aria-hidden="true">
          {[0, 0.25, 0.5, 0.75, 1].map((t) => (
            <span key={t} style={{ left: pct(t) }}>
              {t}
            </span>
          ))}
        </div>
        <div />
        {rows.map((m) => {
          const s = results[m];
          const l = results[`lenient_${m}`];
          return (
            <div className="sc-row" key={m} role="row">
              <div className="sc-label">{LABELS[m] ?? m}</div>
              <div className="sc-track">
                {[0.25, 0.5, 0.75].map((t) => (
                  <span key={t} className="sc-gridline" style={{ left: pct(t) }} />
                ))}
                <div className="sc-lane">{mark(m, s, "strict")}</div>
                {l && <div className="sc-lane">{mark(m, l, "lenient")}</div>}
              </div>
              <div className="sc-values">
                <span>{s.mean.toFixed(2)}</span>
                {l && <span>{l.mean.toFixed(2)}</span>}
              </div>
            </div>
          );
        })}
      </div>
      {tip && (
        <div className="sc-tip" style={{ left: tip.x + 12, top: tip.y - 30 }} role="tooltip">
          {tip.text}
        </div>
      )}
    </figure>
  );
}
