// The selected chunk run (e.g. "pymupdf_w400_o60") is app-wide state: search, evidence
// checks and chunk counts all depend on it. Remembered per browser.
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "./api/client";
import type { Meta } from "./api/types";

const KEY = "litrag.run";
const RunContext = createContext<{ run: string | null; setRun: (r: string) => void }>({
  run: null,
  setRun: () => {},
});

function stored(): string | null {
  try {
    return localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function RunProvider({ children }: { children: ReactNode }) {
  const meta = useQuery({ queryKey: ["meta"], queryFn: () => api.get<Meta>("/meta") });
  const [run, setRunState] = useState<string | null>(stored());

  useEffect(() => {
    if (!meta.data) return;
    const names = meta.data.runs.map((r) => r.name);
    if (!run || !names.includes(run)) setRunState(meta.data.default_run);
  }, [meta.data, run]);

  const setRun = (r: string) => {
    setRunState(r);
    try {
      localStorage.setItem(KEY, r);
    } catch {
      /* storage unavailable: selection just isn't remembered */
    }
  };
  return <RunContext.Provider value={{ run, setRun }}>{children}</RunContext.Provider>;
}

export const useRun = () => useContext(RunContext);
