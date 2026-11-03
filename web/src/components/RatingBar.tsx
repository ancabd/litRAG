// Rate an answer on the Ask page: is it faithful to the passages it cites, and is it complete?
// For a decline: should it have answered? Ratings are saved as you click (data/feedback/ratings.jsonl).
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSaveFeedback } from "../api/hooks";
import type { AskResult, Level, Question, Rating } from "../api/types";

type Saved = { id?: string; rating: Rating; comment: string };

// ratings given in this browser session, so going back to an earlier answer shows yours
const remembered = new Map<string, Saved>();
const keyOf = (r: AskResult) =>
  JSON.stringify([r.question, r.generator.name, r.generator.model, r.retriever, r.run, r.answer]);

const LEVELS: { value: Level; label: string }[] = [
  { value: "yes", label: "Yes" },
  { value: "partly", label: "Partly" },
  { value: "no", label: "No" },
];

function Choice<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T | null | undefined;
  options: { value: T; label: string }[];
  onChange: (v: T | null) => void;
}) {
  return (
    <div className="seg rate-choice" role="group" aria-label={label}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          className={`${value === o.value ? "on" : ""} rate-${o.value}`}
          aria-pressed={value === o.value}
          onClick={() => onChange(value === o.value ? null : o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

/** The answer without its [W123#004] citations, as a starting point for a reference answer. */
const plain = (text: string) =>
  text.replace(/\s*\[[^[\]]*#\d{3,}[^[\]]*\]/g, "").replace(/\s+([.,;:])/g, "$1").trim();

function draftFrom(r: AskResult, saved: Saved): Partial<Question> {
  const decline = !r.answerable;
  const rightToDecline = decline && saved.rating.should_have_answered === "no";
  const papers = [...new Set(r.passages.filter((p) => p.cited_as).map((p) => p.paper_id))].slice(0, 4);
  const bits = Object.entries(saved.rating).filter(([, v]) => v).map(([k, v]) => `${k.replace(/_/g, " ")}: ${v}`);
  return {
    question: r.question,
    type: rightToDecline ? "unanswerable" : "lookup",
    answer: decline ? "" : plain(r.answer),
    evidence: rightToDecline ? [] : papers.length ? papers.map((paper) => ({ paper, quote: "" })) : [{ paper: "", quote: "" }],
    notes: [
      `From Ask (${r.generator.name === "agent" ? "agent" : r.generator.name === "extractive" ? "extractive" : "single shot"}` +
        `${r.generator.model ? `, ${r.generator.model}` : ""}, ${r.retriever}). Rated ${bits.join(", ")}.`,
      saved.comment ? `Comment: ${saved.comment}` : "",
      decline ? "" : "Answer and papers come from that answer: check the answer, and pick the quote in each paper.",
    ]
      .filter(Boolean)
      .join(" "),
  };
}

export function RatingBar({ result, k }: { result: AskResult; k: number }) {
  const navigate = useNavigate();
  const save = useSaveFeedback();
  const key = keyOf(result);
  const [s, setS] = useState<Saved>(() => remembered.get(key) ?? { rating: {}, comment: "" });
  const savedComment = useRef(s.comment);
  useEffect(() => {
    const prev = remembered.get(key) ?? { rating: {}, comment: "" };
    setS(prev);
    savedComment.current = prev.comment;
    save.reset();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const rated = Object.values(s.rating).some(Boolean);
  const persist = (next: Saved) => {
    setS(next);
    remembered.set(key, next);
    if (!Object.values(next.rating).some(Boolean)) return; // nothing to save yet (or you cleared it)
    save.mutate(
      { id: next.id, answer: { ...result, k }, rating: next.rating, comment: next.comment },
      {
        onSuccess: (rec) => {
          const withId = { ...next, id: rec.id };
          remembered.set(key, withId);
          setS((cur) => ({ ...cur, id: rec.id }));
          savedComment.current = next.comment;
        },
      },
    );
  };
  const setRating = (patch: Rating) => persist({ ...s, rating: { ...s.rating, ...patch } });

  return (
    <div className="rate" aria-label="Rate this answer">
      <div className="rate-head">
        <span className="rate-title">Rate this answer</span>
        <span className="rate-status xs" aria-live="polite">
          {save.isPending ? "Saving…" : save.isError ? <span className="danger-text">{save.error.message}</span> : s.id ? "Saved" : ""}
        </span>
      </div>
      <div className="rate-rows">
        {result.answerable ? (
          <>
            <div className="rate-row">
              <span className="rate-label" title="Every claim is backed by the passage it cites; nothing made up or cited wrongly">
                Faithful<span className="rate-help">every claim backed by the passage it cites</span>
              </span>
              <Choice label="Faithful" value={s.rating.faithful} options={LEVELS} onChange={(v) => setRating({ faithful: v })} />
            </div>
            <div className="rate-row">
              <span className="rate-label" title="Answers the question with everything relevant the corpus has (not the whole field)">
                Complete<span className="rate-help">answers it with all the corpus has on it</span>
              </span>
              <Choice label="Complete" value={s.rating.complete} options={LEVELS} onChange={(v) => setRating({ complete: v })} />
            </div>
          </>
        ) : (
          <div className="rate-row">
            <span className="rate-label">
              Should it have answered?<span className="rate-help">does the corpus answer this question?</span>
            </span>
            <Choice
              label="Should it have answered"
              value={s.rating.should_have_answered}
              options={[
                { value: "yes" as const, label: "Yes, the corpus has it" },
                { value: "no" as const, label: "No, declining was right" },
              ]}
              onChange={(v) => setRating({ should_have_answered: v })}
            />
          </div>
        )}
      </div>
      {rated && (
        <div className="rate-more">
          <input
            className="input"
            value={s.comment}
            maxLength={4000}
            placeholder={result.answerable ? "What was wrong or missing? (optional)" : "What should it have found? (optional)"}
            aria-label="Comment"
            onChange={(e) => setS({ ...s, comment: e.target.value })}
            onBlur={() => s.comment !== savedComment.current && persist(s)}
            onKeyDown={(e) => e.key === "Enter" && (e.target as HTMLInputElement).blur()}
          />
          <button type="button" className="btn small" onClick={() => navigate("/questions/new", { state: { draft: draftFrom(result, s) } })}>
            Add as eval question
          </button>
        </div>
      )}
    </div>
  );
}
