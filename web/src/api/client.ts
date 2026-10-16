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
  if (!res.ok) {
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
    throw new ApiError(res.status, message, details);
  }
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
