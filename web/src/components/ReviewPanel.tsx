// Review what retrieval returns for a question and judge each passage ("pooling").
// By default the top passages of every retriever (BM25, dense, hybrid) are merged, so judgments
// cover what any of them would rank; each passage shows which retrievers found it and where.
// Passages that answer it become alternatives (lenient scoring); the rest are recorded as
// not relevant, so they're never reviewed twice. Judgments are saved straight to the file.
import { useState } from "react";
import { Link } from "react-router-dom";
import { useJudge, useReview } from "../api/hooks";
import type { Question, ReviewHit } from "../api/types";
import { ChunkCard } from "./ChunkCard";
import { DenseNote, RetrieverSelect, shortRetriever } from "./RetrieverSelect";
import { ErrorBanner } from "./ui";

const LABEL = {
  evidence: "Your evidence",
  alternative: "Also answers it",
  not_relevant: "Doesn't answer it",
  unjudged: "Not reviewed",
} as const;

export function ReviewPanel({ question, dirty, version }: { question: Question; dirty: boolean; version: string }) {
  const [open, setOpen] = useState(false);
  const [retriever, setRetriever] = useState("pool");
  const [k, setK] = useState(10);
  const review = useReview(question.id, open, k, retriever);
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
          {open ? "Hide" : "Show what retrieval finds"}
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
          <div className="row" style={{ gap: 10, margin: "6px 0 4px" }}>
            <RetrieverSelect value={retriever} onChange={setRetriever}
              extra={[{ name: "pool", label: "All retrievers, merged" }]} />
            <select className="select" value={k} onChange={(e) => setK(Number(e.target.value))} aria-label="Passages per retriever">
              {[5, 10, 20].map((n) => (
                <option key={n} value={n}>
                  top {n}{retriever === "pool" ? " of each" : ""}
                </option>
              ))}
            </select>
            {review.isFetching && <span className="muted small">Searching…</span>}
          </div>
          {retriever !== "pool" && <DenseNote retriever={retriever} />}
          {review.error && <ErrorBanner error={review.error} />}
          {judge.error && <ErrorBanner error={judge.error} />}
          {data && (
            <p className="small muted" style={{ margin: "4px 0 10px" }}>
              {data.retriever === "pool"
                ? `${data.items.length} passages from the top ${data.k} of ${data.retrievers.map(shortRetriever).join(", ")} on ${data.run}, best rank first`
                : `Top ${data.items.length} from ${data.retriever} on ${data.run}`}
              : {data.judged} of {data.items.length} judged.
              {data.skipped.length > 0 && (
                <>
                  {" "}Not included: {data.skipped.map((s) => `${s.label} (${s.reason})`).join(", ")}.{" "}
                  <Link to="/settings">Build indexes</Link>
                </>
              )}
            </p>
          )}
          {data?.items.map((hit) => {
            const kind = hit.judgment.kind;
            const busy = judge.isPending && judge.variables?.chunk_id === hit.chunk_id;
            const off = dirty || judge.isPending;
            return (
              <div key={hit.chunk_id} className={`review-item j-${kind}`}>
                <div className="row review-head">
                  {data?.retriever === "pool" ? (
                    <span className="found-by" title="Rank of this passage in each retriever's results">
                      {Object.entries(hit.found_by).map(([name, rank]) => (
                        <span key={name} className="chip">
                          {shortRetriever(name)} #{rank}
                        </span>
                      ))}
                    </span>
                  ) : (
                    <span className="muted small">#{hit.rank}</span>
                  )}
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
