// Routes and the app shell. To add a page: add a route here, a nav link
// in Shell, and its API hooks in api/hooks.ts.
import { createBrowserRouter, Navigate, NavLink, Outlet, RouterProvider } from "react-router-dom";
import { useLlm, useMeta, useQuestions } from "./api/hooks";
import { ErrorBanner, Logo } from "./components/ui";
import { AskPage } from "./pages/AskPage";
import { PaperPage } from "./pages/PaperPage";
import { PapersPage } from "./pages/PapersPage";
import { QuestionEditor } from "./pages/QuestionEditor";
import { NoQuestionSelected, QuestionsPage } from "./pages/QuestionsPage";
import { SearchPage } from "./pages/SearchPage";
import { ComparePage } from "./pages/ComparePage";
import { ResultPage } from "./pages/ResultPage";
import { ResultsPage } from "./pages/ResultsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { useRun } from "./run";

function RunPicker() {
  const meta = useMeta();
  const { run, setRun } = useRun();
  const runs = meta.data?.runs ?? [];
  if (runs.length === 0) return <span>No chunk runs yet</span>;
  return (
    <>
      <label htmlFor="run">Chunks</label>
      <select id="run" className="select" value={run ?? ""} onChange={(e) => setRun(e.target.value)}>
        {runs.map((r) => (
          <option key={r.name} value={r.name}>
            {r.name}
          </option>
        ))}
      </select>
    </>
  );
}

function Shell() {
  const meta = useMeta();
  const questions = useQuestions();
  const llm = useLlm();
  const c = meta.data?.corpus;
  return (
    <div className="shell">
      <aside className="sidebar">
        <NavLink to="/questions" className="wordmark" aria-label="litrag home">
          <Logo />
          litrag
        </NavLink>
        <nav className="nav" aria-label="Main">
          <NavLink to="/ask">Ask</NavLink>
          <NavLink to="/questions">
            Questions <span className="count">{questions.data?.items.length ?? ""}</span>
          </NavLink>
          <NavLink to="/papers">
            Papers <span className="count">{c?.papers ?? ""}</span>
          </NavLink>
          <NavLink to="/search">Search</NavLink>
          <NavLink to="/results">Results</NavLink>
          <NavLink to="/settings">
            Settings
            {llm.data && !llm.data.configured && <span className="dot problem" title="No API key yet" aria-label="No API key yet" />}
          </NavLink>
        </nav>
        <div className="sidebar-foot">
          <RunPicker />
          {c && c.available && (
            <span className="corpus-stat">
              {c.status_counts.pdf ?? 0} full texts, {c.status_counts.abstract_only ?? 0} abstracts
            </span>
          )}
        </div>
      </aside>
      <main className="main">
        {meta.error && (
          <div className="page">
            <ErrorBanner error={meta.error} />
          </div>
        )}
        <Outlet />
      </main>
    </div>
  );
}

const router = createBrowserRouter([
  {
    element: <Shell />,
    children: [
      { index: true, element: <Navigate to="/questions" replace /> },
      {
        path: "questions",
        element: <QuestionsPage />,
        children: [
          { index: true, element: <NoQuestionSelected /> },
          { path: "new", element: <QuestionEditor key="new" isNew /> },
          { path: ":id", element: <QuestionEditor /> },
        ],
      },
      { path: "ask", element: <AskPage /> },
      { path: "papers", element: <PapersPage /> },
      { path: "papers/:id", element: <PaperPage /> },
      { path: "search", element: <SearchPage /> },
      { path: "results", element: <ResultsPage /> },
      { path: "results/compare", element: <ComparePage /> },
      { path: "results/:name", element: <ResultPage /> },
      { path: "settings", element: <SettingsPage /> },
      { path: "*", element: <Navigate to="/questions" replace /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
