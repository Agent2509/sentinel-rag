import type {
  DocumentsPayload,
  EvalRow,
  EvalStatus,
  Health,
  SSEEvent,
  Strategy,
  TraceSummary,
  Trace,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export interface QueryBody {
  query: string;
  strategy: Strategy;
  correction_enabled: boolean;
}

/**
 * POST /api/query returns SSE. EventSource can't POST, so we read the fetch
 * body stream and split on the SSE frame separator. Handles frames that span
 * reader chunks and multi-line data payloads.
 */
export async function streamQuery(
  body: QueryBody,
  onEvent: (event: SSEEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok) {
    throw new Error(await errorDetail(res));
  }
  if (!res.body) throw new Error("Response has no body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const frames = buffer.split(/\r?\n\r?\n/);
    buffer = frames.pop() ?? ""; // last piece may be incomplete
    for (const frame of frames) {
      const payload = frame
        .split(/\r?\n/)
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trim())
        .join("\n")
        .trim();
      if (!payload) continue;
      try {
        const event = JSON.parse(payload) as SSEEvent | { type: "start" };
        if (event.type === "start") continue; // carries nothing consumers need
        onEvent(event);
      } catch {
        console.warn("[sse] malformed frame:", payload.slice(0, 200));
      }
    }
  }
}

async function errorDetail(res: Response): Promise<string> {
  const fallback = `${res.url} -> ${res.status}`;
  try {
    const data = (await res.json()) as { detail?: unknown };
    if (typeof data.detail === "string") return data.detail;
    if (data.detail) return JSON.stringify(data.detail);
    return fallback;
  } catch {
    return fallback;
  }
}

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(await errorDetail(res));
  return (await res.json()) as T;
}

// SQLite stores correction_enabled as 0/1; normalize to boolean at the boundary.
const bool01 = (v: number | boolean) => !!v;

export const getHealth = () => getJSON<Health>("/api/health");
export const getEval = async () =>
  (await getJSON<EvalRow[]>("/api/eval")).map((r) => ({
    ...r,
    correction_enabled: bool01(r.correction_enabled),
  }));
export const getEvalStatus = () => getJSON<EvalStatus>("/api/eval/status");

export async function runEval(): Promise<{ started: boolean }> {
  const res = await fetch(`${API_BASE}/api/eval/run`, { method: "POST" });
  if (!res.ok) throw new Error(await errorDetail(res));
  return (await res.json()) as { started: boolean };
}
export const getTraces = async (limit = 20) =>
  (await getJSON<TraceSummary[]>(`/api/traces?limit=${limit}`)).map((t) => ({
    ...t,
    correction_enabled: bool01(t.correction_enabled),
  }));
export const getTrace = (id: string) =>
  getJSON<Trace>(`/api/trace/${encodeURIComponent(id)}`);

export const getDocuments = () => getJSON<DocumentsPayload>("/api/documents");

async function send(path: string, init: RequestInit): Promise<Response> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) throw new Error(await errorDetail(res));
  return res;
}

export async function uploadDocument(file: File) {
  const body = new FormData();
  body.append("file", file);
  const res = await send("/api/documents", { method: "POST", body });
  return res.json() as Promise<{ name: string; reindex_started: boolean }>;
}

export async function deleteDocument(name: string): Promise<void> {
  await send(`/api/documents/${encodeURIComponent(name)}`, { method: "DELETE" });
}

export async function triggerReindex(): Promise<void> {
  const res = await fetch(`${API_BASE}/api/reindex`, { method: "POST" });
  if (!res.ok && res.status !== 409) throw new Error(await errorDetail(res));
}
