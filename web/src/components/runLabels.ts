// Names for eval runs by their setup ("Agent (haiku-5-5) + Hybrid (bge-small)") instead of their timestamp.
import type { EvalBrief } from "../api/types";

const shortModel = (m?: string) => (m ?? "").replace(/^claude-/, "");

function retrieverPart(cfg: EvalBrief["retriever"] | null | undefined): string {
  const name = cfg?.name ?? "";
  if (name === "bm25") return "BM25";
  if (name === "dense") return `Dense (${String((cfg as { preset?: string }).preset ?? "")})`;
  if (name === "hybrid") return `Hybrid (${String((cfg as { dense?: { preset?: string } }).dense?.preset ?? "")})`;
  return name;
}

/** Method + retriever, e.g. "Single shot (haiku-5-5) + BM25", "Agent (sonnet-5-5) + Dense (bge-small)", "Hybrid (bge-small)". */
export function baseLabel(r: EvalBrief): string {
  const ret = retrieverPart(r.retriever);
  if (r.kind !== "answer") return ret;
  const g = r.generator;
  const method =
    g?.name === "agent" ? `Agent (${shortModel(g.model)})` : g?.name === "extractive" ? "Extractive" : `Single shot (${shortModel(g?.model)})`;
  return `${method} + ${ret}`;
}

/** Labels for a set of runs: the setup, plus whatever else differs between them, plus the time only if still ambiguous. */
export function runLabels(runs: EvalBrief[], when: (iso: string | null) => string): Record<string, string> {
  const differs = (f: (r: EvalBrief) => unknown) => new Set(runs.map((r) => JSON.stringify(f(r) ?? null))).size > 1;
  const extras: [boolean, (r: EvalBrief) => string][] = [
    [differs((r) => r.chunks), (r) => `on ${r.chunks}`],
    [differs((r) => r.split), (r) => `${r.split ?? "all"} split`],
    [differs((r) => r.k), (r) => `k=${r.k}`],
    [differs((r) => r.judge?.model), (r) => (r.judge?.model ? `judged by ${shortModel(r.judge.model)}` : "no judge")],
  ];
  const labels: Record<string, string> = {};
  for (const r of runs) {
    const bits = extras.filter(([on]) => on).map(([, f]) => f(r));
    labels[r.name] = [baseLabel(r), ...bits].join(", ");
  }
  const counts: Record<string, number> = {};
  Object.values(labels).forEach((l) => (counts[l] = (counts[l] ?? 0) + 1));
  for (const r of runs) if (counts[labels[r.name]] > 1) labels[r.name] += ` (${when(r.created)})`;
  return labels;
}
