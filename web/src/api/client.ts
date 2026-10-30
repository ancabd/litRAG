// One place for all HTTP calls. Errors come back as ApiError with the server's message.

export class ApiError extends Error {
  status: number;
  details: string[];
  constructor(status: number, message: string, details: string[] = []) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

type Params = Record<string, string | number | boolean | null | undefined>;

function url(path: string, params?: Params): string {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params ?? {})) {
    if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
  }
  const q = qs.toString();
  return `/api${path}${q ? `?${q}` : ""}`;
}

async function errorFrom(res: Response): Promise<ApiError> {
  let message = `${res.status} ${res.statusText}`;
  let details: string[] = [];
  try {
    const data = await res.json();
    const d = data.detail;
    if (typeof d === "string") message = d;
    else if (d && typeof d === "object") {
      message = d.message ?? message;
      details = d.errors ?? [];
    }
  } catch {
    /* not JSON */
  }
  return new ApiError(res.status, message, details);
}

/** POST, then read newline-delimited JSON events as they arrive (the agent's steps, then its result). */
export async function streamPost(path: string, body: unknown, onEvent: (e: unknown) => void, signal?: AbortSignal): Promise<void> {
  let res: Response;
  try {
    res = await fetch(url(path), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), signal });
  } catch (e) {
    if ((e as Error).name === "AbortError") throw e;
    throw new ApiError(0, "Can't reach the server. Is it running? Start it with `python -m app` in server/.");
  }
  if (!res.ok) throw await errorFrom(res);
  if (!res.body) throw new ApiError(0, "The server sent no data.");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (value) buf += decoder.decode(value, { stream: true });
    let nl: number;
    while ((nl = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, nl).trim();
      buf = buf.slice(nl + 1);
      if (line) onEvent(JSON.parse(line));
    }
    if (done) break;
  }
  if (buf.trim()) onEvent(JSON.parse(buf));
}

async function request<T>(method: string, path: string, params?: Params, body?: unknown): Promise<T> {
  let res: Response;
  try {
    const raw = body instanceof Blob; // file uploads are sent as-is
    res = await fetch(url(path, params), {
      method,
      headers: body === undefined ? undefined : { "Content-Type": raw ? body.type || "application/octet-stream" : "application/json" },
      body: body === undefined ? undefined : raw ? body : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "Can't reach the server. Is it running? Start it with `python -m app` in server/.");
  }
  if (!res.ok) throw await errorFrom(res);
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string, params?: Params) => request<T>("GET", path, params),
  post: <T>(path: string, body: unknown, params?: Params) => request<T>("POST", path, params, body),
  put: <T>(path: string, body: unknown, params?: Params) => request<T>("PUT", path, params, body),
  del: <T>(path: string, params?: Params) => request<T>("DELETE", path, params),
  upload: <T>(path: string, file: Blob) => request<T>("POST", path, undefined, file),
};

export const pdfUrl = (paperId: string) => `/api/papers/${encodeURIComponent(paperId)}/pdf`;
