import { useLlm } from "../api/hooks";
import { KeyForm } from "../components/KeyForm";
import { ErrorBanner } from "../components/ui";

export function SettingsPage() {
  const llm = useLlm();
  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Settings</h1>
          <p className="sub">Things the app needs that don't belong in the repository.</p>
        </div>
      </div>
      {llm.error && <ErrorBanner error={llm.error} />}
      <section className="run-panel" aria-labelledby="key-h" style={{ maxWidth: 760 }}>
        <h2 id="key-h" style={{ marginBottom: 8 }}>Anthropic API key</h2>
        <KeyForm />
      </section>
    </div>
  );
}
