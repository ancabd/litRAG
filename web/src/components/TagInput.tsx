import { useState } from "react";

const SUGGESTED = ["equation", "numeric", "definition"];

export function TagInput({
  value,
  onChange,
  known,
}: {
  value: string[];
  onChange: (tags: string[]) => void;
  known: string[];
}) {
  const [text, setText] = useState("");
  const add = (raw: string) => {
    const t = raw.trim().toLowerCase().replace(/\s+/g, "-");
    if (t && !value.includes(t)) onChange([...value, t]);
    setText("");
  };
  const suggestions = [...new Set([...SUGGESTED, ...known])].filter((t) => !value.includes(t)).slice(0, 10);

  return (
    <div className="stack">
      <div className="tags-input">
        {value.map((t) => (
          <span className="tag" key={t}>
            {t}
            <button type="button" aria-label={`Remove tag ${t}`} onClick={() => onChange(value.filter((x) => x !== t))}>
              ×
            </button>
          </span>
        ))}
        <input
          value={text}
          aria-label="Add tag"
          placeholder={value.length ? "" : "Add a tag and press Enter"}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === ",") {
              e.preventDefault();
              add(text);
            } else if (e.key === "Backspace" && !text && value.length) {
              onChange(value.slice(0, -1));
            }
          }}
          onBlur={() => text && add(text)}
        />
      </div>
      {suggestions.length > 0 && (
        <div className="tag-suggest">
          {suggestions.map((t) => (
            <button type="button" className="tag" key={t} onClick={() => add(t)}>
              + {t}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
