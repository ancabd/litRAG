import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useBlocker, useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useDeleteQuestion, useMeta, useQuestions, useSaveQuestion } from "../api/hooks";
import { ApiError } from "../api/client";
import type { Evidence, Question, QuestionType, Split } from "../api/types";
import { EvidenceEditor } from "../components/EvidenceEditor";
import { PassageFinder } from "../components/PassageFinder";
import { ReviewPanel } from "../components/ReviewPanel";
import { TagInput } from "../components/TagInput";
import { Empty, ErrorBanner, Seg, Toast, TYPE_LABEL, useToast } from "../components/ui";

const TYPE_HINT: Record<QuestionType, string> = {
  lookup: "One fact from one passage.",
  multihop: "Needs two passages, where finding the second depends on the first.",
  comparison: "Needs two passages, compared side by side.",
  unanswerable: "The corpus doesn't contain the answer; checks that the system says so.",
};

const blank = (): Question => ({
  id: "",
  question: "",
  type: "lookup",
  tags: [],
  split: "dev",
  answer: "",
  evidence: [{ paper: "", quote: "" }],
  notes: "",
});

function normalize(q: Question): Question {
  return {
    id: q.id ?? "",
    question: q.question ?? "",
    type: q.type ?? "lookup",
    tags: q.tags ?? [],
    split: q.split ?? "dev",
    answer: q.answer ?? "",
    evidence: (q.evidence ?? []).map((e) => ({
      paper: e.paper ?? "",
      quote: e.quote ?? "",
      title: e.title ?? null,
      alternatives: (e.alternatives ?? []).map((a) => ({ paper: a.paper, quote: a.quote, title: a.title ?? null })),
    })),
    notes: q.notes ?? "",
    not_relevant: (q.not_relevant ?? []).map((p) => ({ paper: p.paper, quote: p.quote })),
  };
}

/** What gets saved: display-only fields (titles) stripped. */
function payload(q: Question): Question {
  return {
    ...q,
    evidence: q.evidence?.map(({ paper, quote, alternatives }) => ({
      paper,
      quote,
      alternatives: (alternatives ?? []).map(({ paper, quote }) => ({ paper, quote })),
    })),
    not_relevant: (q.not_relevant ?? []).map(({ paper, quote }) => ({ paper, quote })),
  };
}

const comparable = (q: Question) => JSON.stringify(payload(q));

export function QuestionEditor({ isNew = false }: { isNew?: boolean }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const list = useQuestions();
  const meta = useMeta();
  const save = useSaveQuestion();
  const del = useDeleteQuestion();
  const [toast, showToast] = useToast();

  const original = useMemo(() => {
    if (isNew) return blank();
    const found = list.data?.items.find((q) => q.id === id);
    return found ? normalize(found) : null;
  }, [isNew, id, list.data]);

  const [form, setForm] = useState<Question | null>(original);
  const [showFinder, setShowFinder] = useState(false);
  // reset the form when switching questions (not when the list refetches after a save)
  useEffect(() => {
    setForm(original);
    save.reset();
    setShowFinder(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isNew, id, original === null]);
  // when the file changes underneath a clean form (e.g. a judgment from the review panel), follow it
  const lastOriginal = useRef(original);
  useEffect(() => {
    const prev = lastOriginal.current;
    lastOriginal.current = original;
    if (original && prev && form && comparable(form) === comparable(prev) && comparable(prev) !== comparable(original)) {
      setForm(original);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [original]);

  const dirty = !!form && !!original && comparable(form) !== comparable(original);
  const skipBlock = useRef(false); // set right before navigating away after a save or delete
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      dirty && !skipBlock.current && currentLocation.pathname !== nextLocation.pathname,
  );
  useEffect(() => {
    skipBlock.current = false;
  }, [id, isNew]);
  useEffect(() => {
    if (blocker.state === "blocked") {
      if (window.confirm("Discard unsaved changes to this question?")) blocker.proceed();
      else blocker.reset();
    }
  }, [blocker]);
  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (dirty) e.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);

  const doSave = () => {
    if (!form || !list.data) return;
    const evidence = form.type === "unanswerable" ? [] : (form.evidence ?? []).filter((e) => e.paper.trim() || (e.quote ?? "").trim());
    save.mutate(
      { question: payload({ ...form, evidence }), version: list.data.version, isNew },
      {
        onSuccess: (res) => {
          setForm(normalize(res.item));
          showToast(isNew ? `Created ${res.item.id}` : `Saved ${res.item.id}`);
          if (isNew) {
            skipBlock.current = true;
            navigate(`/questions/${res.item.id}`, { replace: true });
          }
        },
      },
    );
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        if (dirty || isNew) doSave();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (list.isLoading) return null;
  if (!form) {
    return (
      <Empty title={`No question ${id}`}>
        <p>It may have been deleted or renamed in questions.yaml.</p>
        <Link to="/questions" className="btn">
          Back to questions
        </Link>
      </Empty>
    );
  }

  const set = <K extends keyof Question>(k: K, v: Question[K]) => setForm({ ...form, [k]: v });
  const evidence = form.evidence ?? [];
  const setEvidence = (ev: Evidence[]) => set("evidence", ev);
  const addPassage = (paper: string, quote: string) => {
    const i = evidence.findIndex((e) => !e.paper && !e.quote);
    const next = [...evidence];
    if (i >= 0) next[i] = { paper, quote };
    else next.push({ paper, quote });
    setEvidence(next);
  };
  const conflict = save.error instanceof ApiError && save.error.status === 409;
  const needsTwo = (form.type === "multihop" || form.type === "comparison") && evidence.filter((e) => e.paper).length < 2;

  return (
    <div className="editor">
      <div className="editor-head">
        {!isNew && <span className="id" style={{ fontSize: 13 }}>{form.id}</span>}
        <h2>{isNew ? "New question" : "Edit question"}</h2>
        <span className="spacer" />
        {dirty && <span className="muted small">Unsaved changes</span>}
        {!isNew && (
          <button
            type="button"
            className="btn ghost danger"
            disabled={del.isPending}
            onClick={() => {
              if (!list.data || !window.confirm(`Delete ${form.id}? Its id won't be reused.`)) return;
              del.mutate(
                { id: form.id, version: list.data.version },
                {
                  onSuccess: () => {
                    skipBlock.current = true;
                    navigate("/questions", { replace: true });
                  },
                },
              );
            }}
          >
            Delete
          </button>
        )}
        <button type="button" className="btn primary" onClick={doSave} disabled={save.isPending || (!dirty && !isNew)} title="Save (Ctrl/Cmd+S)">
          {save.isPending ? "Saving…" : isNew ? "Create question" : "Save"}
        </button>
      </div>

      {conflict ? (
        <ErrorBanner
          error={save.error}
          action={
            <button type="button" className="btn small" onClick={() => qc.invalidateQueries({ queryKey: ["questions"] })}>
              Reload file
            </button>
          }
        />
      ) : (
        save.error && <ErrorBanner error={save.error} />
      )}
      {del.error && <ErrorBanner error={del.error} />}

      <div className="field">
        <label htmlFor="q-text">Question</label>
        <textarea
          id="q-text"
          className="textarea question-input"
          rows={2}
          autoFocus={isNew}
          value={form.question}
          onChange={(e) => set("question", e.target.value)}
          placeholder="Ask it the way you would while reading, not in the paper's own words"
        />
      </div>

      <div className="field">
        <span className="label">Type</span>
        <Seg
          label="Question type"
          value={form.type}
          onChange={(t) => set("type", t)}
          options={(["lookup", "multihop", "comparison", "unanswerable"] as const).map((t) => ({ value: t, label: TYPE_LABEL[t] }))}
        />
        <span className="hint">{TYPE_HINT[form.type]}</span>
      </div>

      <div className="fields-row">
        <div className="field">
          <span className="label">Split</span>
          <Seg<Split>
            label="Split"
            value={form.split ?? "dev"}
            onChange={(s) => set("split", s)}
            options={[
              { value: "dev", label: "Dev" },
              { value: "test", label: "Test" },
            ]}
          />
          <span className="hint">{form.split === "test" ? "Held back: only run at the very end." : "Fine to look at and tune on."}</span>
        </div>
        <div className="field" style={{ flex: 1, minWidth: 260 }}>
          <span className="label">Tags</span>
          <TagInput value={form.tags ?? []} onChange={(t) => set("tags", t)} known={meta.data?.questions.tags ?? []} />
        </div>
      </div>

      {form.type !== "unanswerable" && (
        <div className="field">
          <div className="row">
            <span className="label">Evidence</span>
            <span className="spacer" />
            <button type="button" className="btn small" onClick={() => setShowFinder((v) => !v)}>
              {showFinder ? "Hide passage search" : "Find a passage"}
            </button>
            <button type="button" className="btn small" onClick={() => setEvidence([...evidence, { paper: "", quote: "" }])}>
              Add evidence
            </button>
          </div>
          {needsTwo && <span className="hint">{TYPE_LABEL[form.type]} questions need evidence from at least two places.</span>}
          {showFinder && <PassageFinder onUse={addPassage} />}
          {evidence.map((e, i) => (
            <EvidenceEditor
              key={i}
              index={i}
              value={e}
              onChange={(v) => setEvidence(evidence.map((x, j) => (j === i ? v : x)))}
              onRemove={() => setEvidence(evidence.filter((_, j) => j !== i))}
            />
          ))}
          {evidence.length === 0 && <p className="muted small">No evidence yet. Find a passage, or add one by hand.</p>}
        </div>
      )}

      {!isNew && <ReviewPanel question={form} dirty={dirty} version={list.data?.version ?? ""} />}

      <div className="field">
        <label htmlFor="q-answer">Reference answer</label>
        <textarea
          id="q-answer"
          className="textarea"
          rows={3}
          value={form.answer ?? ""}
          onChange={(e) => set("answer", e.target.value)}
          placeholder={form.type === "unanswerable" ? "Why it can't be answered from this corpus" : "In your own words; used later to grade generated answers"}
        />
      </div>

      <div className="field">
        <label htmlFor="q-notes">Notes</label>
        <textarea id="q-notes" className="textarea" rows={2} value={form.notes ?? ""} onChange={(e) => set("notes", e.target.value)} placeholder="For yourself" />
      </div>
      <Toast message={toast} />
    </div>
  );
}
