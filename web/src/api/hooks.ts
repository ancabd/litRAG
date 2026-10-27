// React Query hooks: caching, refetching and loading states for every API resource.
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type {
  AskResult,
  Chunk,
  EvalBrief,
  Job,
  LlmStatus,
  Verdict,
  EvalCompare,
  EvalDetail,
  EvidenceCheckResult,
  IndexStatus,
  ManualResult,
  Meta,
  PaperDetail,
  PaperPage,
  Question,
  QuestionList,
  QuestionWithStatus,
  ReviewResult,
  SearchResult,
} from "./types";
import { useRun } from "../run";

export const useMeta = () => useQuery({ queryKey: ["meta"], queryFn: () => api.get<Meta>("/meta") });

export interface PaperFilters {
  q: string;
  status: string;
  role: string;
  seed: string;
  sort: string;
  offset: number;
  limit: number;
}

export function usePapers(f: PaperFilters) {
  const { run } = useRun();
  return useQuery({
    queryKey: ["papers", f, run],
    queryFn: () => api.get<PaperPage>("/papers", { ...f, run }),
    placeholderData: keepPreviousData,
  });
}

export function usePaper(id: string | undefined) {
  const { run } = useRun();
  return useQuery({
    queryKey: ["paper", id, run],
    queryFn: () => api.get<PaperDetail>(`/papers/${id}`, { run }),
    enabled: !!id,
  });
}

export function usePaperChunks(id: string | undefined, enabled = true) {
  const { run } = useRun();
  return useQuery({
    queryKey: ["paperChunks", id, run],
    queryFn: () => api.get<{ run: string | null; items: Chunk[] }>(`/papers/${id}/chunks`, { run }),
    enabled: !!id && enabled,
  });
}

export function useSearch(q: string, opts: { k?: number; paper?: string; retriever?: string } = {}) {
  const { run } = useRun();
  return useQuery({
    queryKey: ["search", q, run, opts],
    queryFn: () =>
      api.get<SearchResult>("/search", { q, run, k: opts.k ?? 10, paper: opts.paper, retriever: opts.retriever ?? "bm25" }),
    enabled: q.trim().length > 0,
    placeholderData: keepPreviousData,
  });
}

export function useQuestions() {
  const { run } = useRun();
  return useQuery({ queryKey: ["questions", run], queryFn: () => api.get<QuestionList>("/questions", { run }) });
}

export function useEvidenceCheck(paper: string, quote: string) {
  const { run } = useRun();
  return useQuery({
    queryKey: ["evidence", paper, quote, run],
    queryFn: () => api.post<EvidenceCheckResult>("/evidence/check", { paper, quote, run }),
    enabled: paper.trim().length > 0,
    placeholderData: keepPreviousData,
    staleTime: 60_000,
  });
}

type WriteResult = { version: string; item: QuestionWithStatus };

export function useSaveQuestion() {
  const qc = useQueryClient();
  const { run } = useRun();
  return useMutation({
    mutationFn: ({ question, version, isNew }: { question: Question; version: string; isNew: boolean }) =>
      isNew
        ? api.post<WriteResult>("/questions", { question, version }, { run })
        : api.put<WriteResult>(`/questions/${encodeURIComponent(question.id)}`, { question, version }, { run }),
    onSuccess: (res) => {
      // put the saved question in the cache right away, so the UI never shows a stale list
      qc.setQueriesData<QuestionList>({ queryKey: ["questions"] }, (old) => {
        if (!old) return old;
        const exists = old.items.some((q) => q.id === res.item.id);
        const items = exists ? old.items.map((q) => (q.id === res.item.id ? res.item : q)) : [...old.items, res.item];
        return { ...old, version: res.version, items };
      });
      qc.invalidateQueries({ queryKey: ["questions"] });
      qc.invalidateQueries({ queryKey: ["meta"] });
      qc.invalidateQueries({ queryKey: ["paper"] });
      qc.invalidateQueries({ queryKey: ["review"] }); // judgments are part of the question
    },
  });
}

export function useDeleteQuestion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, version }: { id: string; version: string }) =>
      api.del<{ version: string }>(`/questions/${encodeURIComponent(id)}`, { version }),
    onSuccess: (res, vars) => {
      qc.setQueriesData<QuestionList>({ queryKey: ["questions"] }, (old) =>
        old ? { ...old, version: res.version, items: old.items.filter((q) => q.id !== vars.id) } : old,
      );
      qc.invalidateQueries({ queryKey: ["questions"] });
      qc.invalidateQueries({ queryKey: ["meta"] });
    },
  });
}

// ------------------------------------------------------------------ manual additions
// Each one changes the corpus and every chunk run, so everything derived from them is refetched.

function useCorpusChanged() {
  const qc = useQueryClient();
  return () => {
    for (const key of ["papers", "paper", "paperChunks", "search", "meta", "questions", "evidence", "paperPick"]) {
      qc.invalidateQueries({ queryKey: [key] });
    }
  };
}

export function useAddPdf() {
  const changed = useCorpusChanged();
  return useMutation({
    mutationFn: ({ paperId, file }: { paperId: string; file: File }) =>
      api.upload<ManualResult>(`/papers/${encodeURIComponent(paperId)}/pdf`, file),
    onSuccess: changed,
  });
}

export function useRemovePdf() {
  const changed = useCorpusChanged();
  return useMutation({
    mutationFn: (paperId: string) => api.del<ManualResult>(`/papers/${encodeURIComponent(paperId)}/pdf`),
    onSuccess: changed,
  });
}

export function useSetAbstract() {
  const changed = useCorpusChanged();
  return useMutation({
    mutationFn: ({ paperId, abstract }: { paperId: string; abstract: string }) =>
      api.put<ManualResult>(`/papers/${encodeURIComponent(paperId)}/abstract`, { abstract }),
    onSuccess: changed,
  });
}

// ------------------------------------------------------------------ reviewing retrieved passages

export function useReview(qid: string | undefined, enabled: boolean, k = 10, retriever = "pool") {
  const { run } = useRun();
  return useQuery({
    queryKey: ["review", qid, run, k, retriever],
    queryFn: () => api.get<ReviewResult>(`/questions/${encodeURIComponent(qid!)}/review`, { run, k, retriever }),
    placeholderData: keepPreviousData,
    enabled: !!qid && enabled,
  });
}

export function useJudge() {
  const qc = useQueryClient();
  const { run } = useRun();
  return useMutation({
    mutationFn: (b: { qid: string; chunk_id: string; kind: "alternative" | "not_relevant" | "clear"; item?: number; version: string }) =>
      api.post<{ version: string; item: QuestionWithStatus }>(`/questions/${encodeURIComponent(b.qid)}/judge`, {
        chunk_id: b.chunk_id,
        kind: b.kind,
        item: b.item ?? 0,
        version: b.version,
        run,
      }),
    onSuccess: (res) => {
      qc.setQueriesData<QuestionList>({ queryKey: ["questions"] }, (old) =>
        old ? { ...old, version: res.version, items: old.items.map((q) => (q.id === res.item.id ? res.item : q)) } : old,
      );
      qc.invalidateQueries({ queryKey: ["review"] });
      qc.invalidateQueries({ queryKey: ["questions"] });
    },
  });
}

// ------------------------------------------------------------------ eval runs

export const useEvals = () =>
  useQuery({ queryKey: ["evals"], queryFn: () => api.get<{ items: EvalBrief[]; runs_dir: string }>("/evals") });

export const useEval = (name: string | undefined) =>
  useQuery({ queryKey: ["eval", name], queryFn: () => api.get<EvalDetail>(`/evals/${encodeURIComponent(name!)}`), enabled: !!name });

export const useCompare = (names: string[]) =>
  useQuery({
    queryKey: ["evalCompare", names],
    queryFn: () => api.get<EvalCompare>("/evals/compare", { names: names.join(",") }),
    enabled: names.length >= 2,
  });

export interface StartEvalBody {
  kind: "retrieval" | "answer";
  chunks: string | null;
  retriever: string;
  split: string;
  generator?: string;
  model?: string;
  judge?: string;
  k?: number;
}

/** Retrieval evals finish in the request ({name}); answer evals start a job ({job}). */
export function useStartEval() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: StartEvalBody) => api.post<{ name?: string; job?: Job }>("/evals", b),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["evals"] }),
  });
}

export function useJob(id: string | null) {
  return useQuery({
    queryKey: ["job", id],
    queryFn: () => api.get<Job>(`/jobs/${id}`),
    enabled: !!id,
    refetchInterval: (q) => (q.state.data?.state === "running" || !q.state.data ? 1000 : false),
  });
}

export function useSetVerdict(name: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ qid, verdict }: { qid: string; verdict: Verdict | null }) =>
      api.put<{ human: { correctness: Verdict } | null }>(`/evals/${encodeURIComponent(name)}/verdicts/${encodeURIComponent(qid)}`, { verdict }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["eval", name] }),
  });
}

export const useLlm = () => useQuery({ queryKey: ["llm"], queryFn: () => api.get<LlmStatus>("/llm") });

export function useSetKey() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (b: { key: string; remember: boolean }) => api.put<LlmStatus>("/llm/key", b),
    onSuccess: (st) => qc.setQueryData(["llm"], st),
  });
}

export function useRemoveKey() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.del<LlmStatus>("/llm/key"),
    onSuccess: (st) => qc.setQueryData(["llm"], st),
  });
}

export function useAsk() {
  const { run } = useRun();
  return useMutation({
    mutationFn: (b: { question: string; generator: string; model?: string; k: number; retriever?: string }) =>
      api.post<AskResult>("/ask", { ...b, run }),
  });
}

export function useDeleteEval() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => api.del<{ deleted: string }>(`/evals/${encodeURIComponent(name)}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["evals"] }),
  });
}

// ------------------------------------------------------------------ embedding indexes

export function useIndexes() {
  const { run } = useRun();
  return useQuery({
    queryKey: ["indexes", run],
    queryFn: () => api.get<IndexStatus>("/indexes", { run }),
    enabled: !!run,
    refetchInterval: (q) => (q.state.data?.models.some((m) => m.job) ? 1000 : false), // while building
  });
}

export function useBuildIndex() {
  const qc = useQueryClient();
  const { run } = useRun();
  return useMutation({
    mutationFn: (model: string) => api.post<{ job: Job }>("/indexes", { model, run }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["indexes"] }),
  });
}
