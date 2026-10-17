import type {
  DocumentsPayload,
  EvalRow,
  Health,
  SSEEvent,
  Strategy,
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
 * reader chunks.
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
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail ?? detail;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  if (!res.body) throw new Error("Response has no body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? ""; // last piece may be incomplete
    for (const frame of frames) {
      const line = frame.split("\n").find((l) => l.startsWith("data:"));
      if (!line) continue;
      const payload = line.slice(5).trim();
      if (!payload) continue;
      try {
        onEvent(JSON.parse(payload) as SSEEvent);
      } catch {
        /* ignore malformed frame */
      }
    }
  }
}

async function getJSON<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { signal, cache: "no-store" });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return (await res.json()) as T;
}

export const getHealth = (signal?: AbortSignal) =>
  getJSON<Health>("/api/health", signal);
export const getEval = (signal?: AbortSignal) =>
  getJSON<EvalRow[]>("/api/eval", signal);

export const getDocuments = (signal?: AbortSignal) =>
  getJSON<DocumentsPayload>("/api/documents", signal);

async function send(path: string, init: RequestInit): Promise<Response> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* non-JSON */
    }
    throw new Error(detail);
  }
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
  if (!res.ok && res.status !== 409) throw new Error(`reindex ${res.status}`);
}
