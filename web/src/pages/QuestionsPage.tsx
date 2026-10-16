import { useMemo, useState } from "react";
import { Link, NavLink, Outlet, useParams } from "react-router-dom";
import { useQuestions } from "../api/hooks";
import type { QuestionWithStatus } from "../api/types";
import { Empty, ErrorBanner, EvidenceDot, SearchIcon, Seg, TYPE_LABEL } from "../components/ui";

const TYPES = ["lookup", "multihop", "comparison", "unanswerable"] as const;
const TARGET: Record<string, string> = { lookup: "~40%", multihop: "", comparison: "~30% with multi-hop", unanswerable: "~15%" };

function Mix({ items }: { items: QuestionWithStatus[] }) {
  const n = items.length || 1;
  const counts = Object.fromEntries(TYPES.map((t) => [t, items.filter((q) => q.type === t).length]));
  const eq = items.filter((q) => q.tags?.includes("equation")).length;
  return (
    <div className="mix" aria-label="Question mix by type">
      <div className="mix-bar">
        {TYPES.map((t) => (
          <span key={t} className={`t-${t}`} style={{ width: `${(100 * counts[t]) / n}%` }} title={`${TYPE_LABEL[t]}: ${counts[t]}`} />
        ))}
      </div>
      <div className="mix-legend">
        {TYPES.map((t) => (
          <span key={t} title={TARGET[t] ? `Target ${TARGET[t]}` : undefined}>
            <i className={`t-${t}`} />
            {TYPE_LABEL[t]} {counts[t]}
          </span>
        ))}
        <span title="Target 5–10 equation questions">equation {eq}</span>
      </div>
    </div>
  );
}

export function QuestionsPage() {
  const { id } = useParams();
  const list = useQuestions();
  const [q, setQ] = useState("");
  const [split, setSplit] = useState<"all" | "dev" | "test">("all");
  const [onlyProblems, setOnlyProblems] = useState(false);

  const items = list.data?.items ?? [];
  const shown = useMemo(() => {
    const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    return items.filter((x) => {
      if (split !== "all" && (x.split ?? "dev") !== split) return false;
      if (onlyProblems && x.evidence_status.status !== "problem") return false;
      const hay = `${x.id} ${x.question} ${(x.tags ?? []).join(" ")} ${x.type}`.toLowerCase();
      return terms.every((t) => hay.includes(t));
    });
  }, [items, q, split, onlyProblems]);
  const problems = items.filter((x) => x.evidence_status.status === "problem").length;
  const dev = items.filter((x) => (x.split ?? "dev") === "dev").length;

  return (
    <div className={`qlayout ${id ? "has-selection" : ""}`}>
      <section className="qlist-pane" aria-label="Questions">
        <div className="qlist-head">
          <div className="row">
            <div>
              <h1>Questions</h1>
              {list.data && (
                <p className="xs muted" style={{ marginTop: 2 }}>
                  {items.length} total, {dev} dev, {items.length - dev} test
                </p>
              )}
            </div>
            <span className="spacer" />
            <Link to="/questions/new" className="btn primary">
              New question
            </Link>
          </div>
          {items.length > 0 && <Mix items={items} />}
          <div className="search-input">
            <SearchIcon />
            <input className="input" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by text, id or tag" aria-label="Filter questions" />
          </div>
          <div className="row">
            <Seg
              label="Split"
              value={split}
              onChange={setSplit}
              options={[
                { value: "all", label: "All" },
                { value: "dev", label: "Dev" },
                { value: "test", label: "Test" },
              ]}
            />
            {problems > 0 && (
              <button type="button" className={`btn small ${onlyProblems ? "primary" : ""}`} onClick={() => setOnlyProblems((v) => !v)}>
                {problems} need fixing
              </button>
            )}
          </div>
        </div>

        {list.error && <div style={{ padding: 12 }}><ErrorBanner error={list.error} /></div>}
        {list.data && list.data.errors.length > 0 && (
          <div style={{ padding: "12px 12px 0" }}>
            <div className="banner" role="alert">
              <div>
                questions.yaml has problems. Saving is blocked until they're fixed; open the file in an editor, then reload.
                <ul>
                  {list.data.errors.slice(0, 5).map((e) => (
                    <li key={e}>{e.replace(/^[^,]+, /, "")}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        <ul className="qlist">
          {shown.map((x) => (
            <li key={x.id}>
              <NavLink to={`/questions/${x.id}`} className={({ isActive }) => (isActive ? "active" : "")}>
                <span className="qtext">{x.question || <em className="muted">Untitled</em>}</span>
                <EvidenceDot status={x.evidence_status.status} />
                <span className="qmeta">
                  <span className="id">{x.id}</span>
                  <span>{TYPE_LABEL[x.type] ?? x.type}</span>
                  {x.split === "test" && <span className="pill accent">test</span>}
                  {(() => {
                    const n = (x.evidence ?? []).reduce((a, e) => a + (e.alternatives?.length ?? 0), 0);
                    return n > 0 ? <span title="Alternative passages accepted in lenient scoring">+{n} alt</span> : null;
                  })()}
                  {(x.tags ?? []).map((t) => (
                    <span className="tag" key={t}>
                      {t}
                    </span>
                  ))}
                </span>
              </NavLink>
            </li>
          ))}
        </ul>
        {list.data && items.length === 0 && (
          <Empty title="No questions yet">
            <p>Write questions you'd genuinely ask while reading these papers, then point each one at the passage that answers it.</p>
            <Link to="/questions/new" className="btn primary">
              Write the first question
            </Link>
          </Empty>
        )}
        {items.length > 0 && shown.length === 0 && <p className="muted small" style={{ padding: 16 }}>No questions match these filters.</p>}
      </section>

      <section className="qeditor-pane" aria-label="Question editor">
        <Outlet />
      </section>
    </div>
  );
}

export function NoQuestionSelected() {
  return (
    <Empty title="Pick a question to edit">
      <p>
        A green dot means every evidence quote was found in the current chunks; amber means one wasn't, usually a typo
        or a quote taken from an equation.
      </p>
    </Empty>
  );
}
