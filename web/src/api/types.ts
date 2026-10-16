// Shapes of the server's JSON responses (server/app/routers). Keep in sync with the API.

export type PaperStatus = "pdf" | "abstract_only" | "metadata_only" | "not_downloaded" | string;
export type QuestionType = "lookup" | "multihop" | "comparison" | "unanswerable";
export type Split = "dev" | "test";
export type EvidenceStatus = "ok" | "paper_missing" | "no_quote" | "not_found";

export interface RunInfo {
  name: string;
  modified: number;
  parser: string | null;
  chunking: { size: number; overlap: number; min_words?: number } | null;
  chunks: number | null;
  papers_by_source: Record<string, number> | null;
}

export interface PaperSummary {
  openalex_id: string;
  title: string | null;
  authors: string | null;
  year: number | null;
  venue: string | null;
  doi: string | null;
  status: PaperStatus;
  roles: string[] | null;
  via_seeds: string[] | null;
  cited_by_count: number | null;
  n_chunks?: number;
  added_manually: string[]; // "pdf" and/or "abstract"
}

export interface Meta {
  corpus: { available: boolean; papers: number; status_counts: Record<string, number>; seeds: PaperSummary[] };
  runs: RunInfo[];
  default_run: string | null;
  retrievers: string[];
  questions: { types: QuestionType[]; splits: Split[]; tags: string[]; count: number };
  paths: Record<string, string>;
}

export interface PaperPage {
  total: number;
  offset: number;
  limit: number;
  status_counts: Record<string, number>;
  items: PaperSummary[];
}

export interface PaperDetail extends PaperSummary {
  abstract: string | null;
  abstract_source: string | null;
  is_oa: boolean | null;
  type: string | null;
  pdf_available: boolean;
  pdf_url: string | null;
  note: string | null;
  seeds: { openalex_id: string; title: string }[];
  questions: { id: string; question: string }[];
  run: string | null;
}

export interface Chunk {
  chunk_id: string;
  paper_id: string;
  section: string;
  page_start: number | null;
  page_end: number | null;
  source: string;
  n_words: number;
  text: string;
  highlights?: [number, number][];
  coverage?: number;
}

export interface SearchHit extends Chunk {
  rank: number;
  score: number;
  title: string | null;
  year: number | null;
  authors: string | null;
}

export interface SearchResult {
  query: string;
  run: string;
  retriever: Record<string, unknown>;
  items: SearchHit[];
}

export interface Passage {
  paper: string;
  quote: string;
  title?: string | null; // added by the server for display
}

export interface Evidence {
  paper: string;
  quote?: string | null;
  title?: string | null; // added by the server for display
  alternatives?: Passage[]; // other passages that answer this part too (lenient scoring)
}

export interface Question {
  id: string;
  question: string;
  type: QuestionType;
  tags?: string[];
  split?: Split;
  answer?: string | null;
  evidence?: Evidence[];
  notes?: string | null;
  not_relevant?: Passage[]; // reviewed passages that don't answer it
}

export interface QuestionWithStatus extends Question {
  evidence_status: {
    status: "ok" | "problem" | "unchecked" | "none";
    items: {
      paper: string;
      status: EvidenceStatus;
      gold: string[];
      alternatives: { paper: string; status: EvidenceStatus; gold: string[] }[];
    }[];
  };
}

export interface QuestionList {
  version: string;
  errors: string[];
  file: string;
  items: QuestionWithStatus[];
}

export interface EvidenceCheckResult {
  paper: string;
  quote: string | null;
  run: string;
  status: EvidenceStatus;
  paper_source: string | null;
  title: string | null;
  manifest_status: string | null;
  gold: Chunk[];
  closest: Chunk[];
}

export interface IngestResult {
  run: string;
  source: string | null; // pdf / abstract / abstract_fallback / skipped
  n_chunks: number;
  error: string | null;
  warnings: string | null;
}

export interface ManualResult {
  paper: PaperDetail;
  ingest: IngestResult[];
}

export type JudgmentKind = "evidence" | "alternative" | "not_relevant" | "unjudged";

export interface ReviewHit extends SearchHit {
  judgment: { kind: JudgmentKind; item: number | null };
}

export interface ReviewResult {
  version: string;
  run: string;
  retriever: string;
  items: ReviewHit[];
  judged: number;
  evidence: { paper: string; title: string | null }[];
}

// ------------------------------------------------------------------ eval runs (Results tab)

export interface Interval {
  mean: number;
  lo: number;
  hi: number;
  n: number;
}

export interface EvalBrief {
  name: string;
  created: string | null;
  retriever: Record<string, unknown> & { name: string };
  chunks: string | null;
  parser: string | null;
  split: string | null;
  n_scored: number;
  n_questions: number;
  questions_sha1: string;
  git_commit: string | null;
  headline: Record<string, { strict: number | null; lenient: number | null }>;
  judged: number | null;
}

export interface EvalHit {
  chunk_id: string;
  rank: number;
  score: number;
  label: { kind: JudgmentKind; item: number | null };
  paper_id?: string;
  title?: string | null;
  year?: number | null;
  section?: string;
  page_start?: number | null;
  page_end?: number | null;
  source?: string;
  text?: string;
  n_words?: number;
}

export interface EvalQuestion {
  id: string;
  question: string;
  type: string;
  tags: string[];
  strict_rank: number | null;
  lenient_rank: number | null;
  metrics: Record<string, number>;
  retrieved: EvalHit[];
}

export interface EvalDetail extends EvalBrief {
  summary: {
    results: Record<string, Record<string, Interval>>;
    excluded: { id: string; reason: string }[];
    timing: { index_seconds: number; mean_query_ms: number; total_seconds: number };
    ks: number[];
  };
  questions: EvalQuestion[];
  report: string | null;
  chunks_available: boolean;
}

export interface EvalCompare {
  runs: (EvalBrief & { results: Record<string, Interval> })[];
  same_questions: boolean;
  questions: { id: string; question: string; per_run: ({ strict_rank: number | null; lenient_rank: number | null } | null)[] }[];
}
