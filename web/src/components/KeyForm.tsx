// Enter, check and save the Anthropic API key. The key goes to the local server only; it is never shown again.
import { useState } from "react";
import { useLlm, useRemoveKey, useSetKey } from "../api/hooks";
import { ErrorBanner } from "./ui";

const SOURCE: Record<string, string> = {
  session: "entered here",
  environment: "from the ANTHROPIC_API_KEY environment variable",
  saved: "saved on this computer",
};

export function KeyStatusLine() {
  const llm = useLlm();
  const k = llm.data?.key;
  if (!k) return null;
  return k.configured ? (
    <p className="small">
      <span className="dot ok" aria-hidden="true" /> Using a key {SOURCE[k.source ?? ""] ?? ""}
      {k.hint && <span className="mono muted"> ({k.hint})</span>}.
    </p>
  ) : (
    <p className="small">
      <span className="dot problem" aria-hidden="true" /> No key yet. Claude answers, the agent and the judge need one.
    </p>
  );
}

export function KeyForm({ compact, onSaved }: { compact?: boolean; onSaved?: () => void }) {
  const llm = useLlm();
  const set = useSetKey();
  const remove = useRemoveKey();
  const [key, setKey] = useState("");
  const [remember, setRemember] = useState(true);
  const k = llm.data?.key;
  const save = () => {
    if (key.trim().length < 10 || set.isPending) return;
    set.mutate({ key: key.trim(), remember }, { onSuccess: () => { setKey(""); onSaved?.(); } });
  };

  return (
    <div className="key-form">
      {!compact && <KeyStatusLine />}
      <form
        className="row"
        style={{ gap: 8, flexWrap: "wrap" }}
        onSubmit={(e) => {
          e.preventDefault();
          save();
        }}
      >
        <input
          id="anthropic-key"
          className="input mono"
          type="password"
          autoComplete="off"
          spellCheck={false}
          placeholder={k?.configured ? "Paste a new key to replace it" : "sk-ant-..."}
          aria-label="Anthropic API key"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          style={{ flex: "1 1 280px", minWidth: 0 }}
        />
        <button type="submit" className="btn primary" disabled={key.trim().length < 10 || set.isPending}>
          {set.isPending ? "Checking…" : "Check and save"}
        </button>
      </form>
      <label className="small row" style={{ gap: 6, marginTop: 8 }}>
        <input id="remember-key" type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
        Remember on this computer (also used by <span className="mono">evaluate.py</span>)
      </label>
      {set.error && <div style={{ marginTop: 8 }}><ErrorBanner error={set.error} /></div>}
      {!compact && (
        <p className="xs muted" style={{ marginTop: 10, maxWidth: "70ch" }}>
          Create a key at platform.claude.com. "Check and save" asks Anthropic whether the key works (this costs nothing).
          The key stays on this computer: it is kept by the local server and, if you choose to remember it, saved to{" "}
          <span className="mono">{k?.key_file ?? "~/.config/litrag/credentials.json"}</span>, readable only by you and
          outside the repository, so it can't be committed. It is never shown again here.
        </p>
      )}
      {!compact && k && (k.saved || k.source === "session") && (
        <button type="button" className="btn small danger" style={{ marginTop: 10 }} disabled={remove.isPending}
          onClick={() => remove.mutate()}>
          {k.saved ? "Remove the saved key" : "Forget this key"}
        </button>
      )}
      {!compact && k?.environment && (
        <p className="xs muted" style={{ marginTop: 8 }}>
          ANTHROPIC_API_KEY is also set where the server runs. A key entered here takes priority until the server restarts;
          to remove that one, unset the variable and restart.
        </p>
      )}
    </div>
  );
}
