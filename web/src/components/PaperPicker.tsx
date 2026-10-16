// Type a paper's title, author or OpenAlex id; pick it from the list.
import { useEffect, useId, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { PaperPage, PaperSummary } from "../api/types";
import { STATUS_LABEL, useDebounced } from "./ui";

export function PaperPicker({
  value,
  title,
  onChange,
  autoFocus,
}: {
  value: string;
  title?: string | null;
  onChange: (id: string, paper?: PaperSummary) => void;
  autoFocus?: boolean;
}) {
  const [text, setText] = useState(value);
  useEffect(() => setText(value), [value]); // follow changes made elsewhere (e.g. the passage finder)
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const listId = useId();
  const q = useDebounced(text, 200);
  const results = useQuery({
    queryKey: ["paperPick", q],
    queryFn: () => api.get<PaperPage>("/papers", { q, limit: 8 }),
    enabled: open && q.trim().length > 1,
  });
  const items = results.data?.items ?? [];

  const choose = (p: PaperSummary) => {
    setText(p.openalex_id);
    setOpen(false);
    onChange(p.openalex_id, p);
  };

  return (
    <div className="picker">
      <input
        className="input"
        value={text}
        autoFocus={autoFocus}
        placeholder="Paper: search by title, author or W… id"
        role="combobox"
        aria-expanded={open && items.length > 0}
        aria-controls={listId}
        aria-label="Paper"
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        onChange={(e) => {
          setText(e.target.value);
          setOpen(true);
          setActive(0);
          if (/^W\d+$/.test(e.target.value.trim())) onChange(e.target.value.trim());
        }}
        onKeyDown={(e) => {
          if (!open || items.length === 0) return;
          if (e.key === "ArrowDown") {
            e.preventDefault();
            setActive((a) => Math.min(a + 1, items.length - 1));
          } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setActive((a) => Math.max(a - 1, 0));
          } else if (e.key === "Enter") {
            e.preventDefault();
            choose(items[active]);
          } else if (e.key === "Escape") setOpen(false);
        }}
      />
      {open && items.length > 0 && (
        <ul className="picker-list" id={listId} role="listbox">
          {items.map((p, i) => (
            <li
              key={p.openalex_id}
              role="option"
              aria-selected={i === active}
              onMouseDown={(e) => {
                e.preventDefault();
                choose(p);
              }}
            >
              <div className="paper-title small">{p.title}</div>
              <div className="paper-meta xs">
                {p.openalex_id}, {p.year ?? "n.d."}, {STATUS_LABEL[p.status] ?? p.status}
              </div>
            </li>
          ))}
        </ul>
      )}
      {value && title && text === value && <div className="picker-resolved">{title}</div>}
    </div>
  );
}
