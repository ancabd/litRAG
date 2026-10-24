// An answer with its [chunk-id] citations turned into numbered links to the passages below it.
import type { ReactNode } from "react";

const CITE = /\[([^[\]]{3,200})\]/g;
const ID = /^[A-Za-z0-9]+#\d{3,}$/;

export function AnswerText({
  text,
  citations,
  anchorPrefix = "p-",
}: {
  text: string;
  citations: string[];
  anchorPrefix?: string;
}) {
  const number = new Map(citations.map((c, i) => [c, i + 1]));
  const out: ReactNode[] = [];
  let at = 0;
  for (const m of text.matchAll(CITE)) {
    const ids = m[1].split(/[;,\s]+/).filter((p) => ID.test(p));
    if (ids.length === 0) continue; // e.g. "[Fig. 2]": leave as text
    out.push(text.slice(at, m.index));
    ids.forEach((id) => {
      const n = number.get(id);
      out.push(
        n ? (
          <a key={`${m.index}-${id}`} href={`#${anchorPrefix}${id}`} className="cite" title={id}>
            {n}
          </a>
        ) : (
          <span key={`${m.index}-${id}`} className="cite bad" title={`${id} was not among the passages it was given`}>
            ?
          </span>
        ),
      );
    });
    at = (m.index ?? 0) + m[0].length;
  }
  out.push(text.slice(at));
  return <>{out}</>;
}
