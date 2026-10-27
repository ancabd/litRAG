import { useLlm } from "../api/hooks";
import { KeyForm } from "../components/KeyForm";
import { IndexPanel } from "../components/RetrieverSelect";
import { ErrorBanner } from "../components/ui";

export function SettingsPage() {
  const llm = useLlm();
  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Settings</h1>
          <p className="sub">The API key, and the search indexes for dense and hybrid retrieval.</p>
        </div>
      </div>
      {llm.error && <ErrorBanner error={llm.error} />}
      <section className="run-panel" aria-labelledby="key-h" style={{ maxWidth: 760 }}>
        <h2 id="key-h" style={{ marginBottom: 8 }}>Anthropic API key</h2>
        <KeyForm />
      </section>
      <section className="run-panel" aria-labelledby="idx-h" style={{ maxWidth: 760, marginTop: 18 }}>
        <h2 id="idx-h" style={{ marginBottom: 4 }}>Search indexes</h2>
        <p className="small muted" style={{ marginBottom: 12 }}>Embeddings for dense and hybrid retrieval. BM25 needs none.</p>
        <IndexPanel />
      </section>
    </div>
  );
}
