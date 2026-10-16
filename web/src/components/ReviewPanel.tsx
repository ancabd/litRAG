// Review what the retriever returns for a question and judge each passage ("pooling").
// Passages that answer it become alternatives (lenient scoring); the rest are recorded as
// not relevant, so they're never reviewed twice. Judgments are saved straight to the file.
import { useState } from "react";
import { useJudge, useReview } from "../api/hooks";
import type { Question, ReviewHit } from "../api/types";
import { ChunkCard } from "./ChunkCard";
import { ErrorBanner } from "./ui";

const LABEL = {
  evidence: "Your evidence",
  alternative: "Also answers it",
  not_relevant: "Doesn't answer it",
  unjudged: "Not reviewed",
} as const;

export function ReviewPanel({ question, dirty, version }: { question: Question; dirty: boolean; version: string }) {
  const [open, setOpen] = useState(false);
  const review = useReview(question.id, open);
  const judge = useJudge();
  const evidence = question.evidence ?? [];
  const multi = evidence.length > 1;
  if (question.type === "unanswerable") return null;

  const act = (hit: ReviewHit, kind: "alternative" | "not_relevant" | "clear", item = 0) =>
    // `version` comes from the questions list, which every save and judgment keeps current;
    // the review's own copy goes stale as soon as the editor saves.
    judge.mutate({ qid: question.id, chunk_id: hit.chunk_id, kind, item, version: version || review.data?.version || "" });

  const data = review.data;
  return (
    <div className="field">
      <div className="row">
        <span className="label">Review retrieved passages</span>
        <span className="spacer" />
        <button type="button" className="btn small" onClick={() => setOpen((v) => !v)}>
          {open ? "Hide" : "Show what the retriever finds"}
        </button>
      </div>
      <span className="hint">
        Other papers often restate the same result. Mark passages that answer the question too: strict scoring
        still wants your original source, lenient scoring also accepts these.
      </span>
      {open && (
        <div className="review">
          {dirty && (
            <div className="banner">Save your changes first. Judgments are written straight to questions.yaml.</div>
          )}
          {review.error && <ErrorBanner error={review.error} />}
          {judge.error && <ErrorBanner error={judge.error} />}
          {data && (
            <p className="small muted" style={{ margin: "4px 0 10px" }}>
              Top {data.items.length} from {data.retriever} on {data.run}: {data.judged} of {data.items.length} judged.
            </p>
          )}
          {data?.items.map((hit) => {
            const kind = hit.judgment.kind;
            const busy = judge.isPending && judge.variables?.chunk_id === hit.chunk_id;
            const off = dirty || judge.isPending;
            return (
              <div key={hit.chunk_id} className={`review-item j-${kind}`}>
                <div className="row review-head">
                  <span className="muted small">#{hit.rank}</span>
                  <span className={`pill ${kind === "evidence" || kind === "alternative" ? "ok" : kind === "not_relevant" ? "" : "warn"}`}>
                    {LABEL[kind]}
                    {multi && hit.judgment.item !== null && kind !== "not_relevant" ? `, part ${hit.judgment.item + 1}` : ""}
                  </span>
                  {busy && <span className="muted small">Saving…</span>}
                </div>
                <ChunkCard
                  chunk={hit}
                  showPaper
                  actions={() =>
                    kind === "evidence" ? null : (
                      <>
                        {kind !== "alternative" &&
                          (multi ? (
                            evidence.map((e, i) => (
                              <button key={i} type="button" className="btn small" disabled={off} onClick={() => act(hit, "alternative", i)}
                                title={e.title ?? e.paper}>
                                Answers part {i + 1}
                              </button>
                            ))
                          ) : (
                            <button type="button" className="btn small" disabled={off} onClick={() => act(hit, "alternative")}>
                              Answers it
                            </button>
                          ))}
                        {kind !== "not_relevant" && (
                          <button type="button" className="btn small" disabled={off} onClick={() => act(hit, "not_relevant")}>
                            Doesn't answer it
                          </button>
                        )}
                        {kind !== "unjudged" && (
                          <button type="button" className="btn small ghost" disabled={off} onClick={() => act(hit, "clear")}>
                            Undo
                          </button>
                        )}
                      </>
                    )
                  }
                />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
