"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Loader2, RefreshCw, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/page-header";
import { deleteDocument, getDocuments, triggerReindex, uploadDocument } from "@/lib/api";
import type { DocumentsPayload } from "@/lib/types";

const ACCEPT_EXT = [".md", ".txt", ".pdf"];

export default function DocumentsPage() {
  const [data, setData] = useState<DocumentsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [drag, setDrag] = useState(false);
  const [filter, setFilter] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const reindexing = data?.reindexing ?? false;

  const refresh = useCallback(async () => {
    try {
      setData(await getDocuments());
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  useEffect(() => {
    // Initial load + poll. refresh()'s setState lands after its await, so this
    // is not a synchronous setState; the rule cannot see through the async call.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refresh();
    const id = setInterval(refresh, reindexing ? 3000 : 15000);
    return () => clearInterval(id);
  }, [refresh, reindexing]);

  async function upload(files: FileList | null) {
    if (!files?.length || busy) return;
    const all = Array.from(files);
    const accepted = all.filter((f) =>
      ACCEPT_EXT.some((ext) => f.name.toLowerCase().endsWith(ext)),
    );
    setBusy(true);
    setError(null);
    const failures: string[] = [];
    for (const file of accepted) {
      try {
        await uploadDocument(file);
      } catch (e) {
        failures.push(`${file.name}: ${(e as Error).message}`);
      }
    }
    if (accepted.length < all.length) {
      failures.push(
        `${all.length - accepted.length} file(s) skipped — only ${ACCEPT_EXT.join(", ")} accepted`,
      );
    }
    setError(failures.length ? failures.join("; ") : null);
    setBusy(false);
    await refresh();
  }

  async function remove(name: string) {
    if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return;
    setError(null);
    try {
      await deleteDocument(name);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const docs = (data?.documents ?? []).filter((d) =>
    d.name.toLowerCase().includes(filter.trim().toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <PageHeader
        title="Documents"
        description="The corpus is whatever sits in this list. Upload files and the indexes rebuild in the background."
      />

      <div
        className={`border p-8 text-center transition-colors ${
          drag ? "border-destructive" : "border-border"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          upload(e.dataTransfer.files);
        }}
      >
        <p className="font-display text-lg">Add documents</p>
        <p className="mt-1 text-[13px] text-muted-foreground">
          Markdown, plain text or PDF. Drop files here, or choose them.
        </p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".md,.txt,.pdf"
          className="hidden"
          onChange={(e) => {
            upload(e.target.files);
            e.target.value = "";
          }}
        />
        <Button
          className="mt-4"
          onClick={() => inputRef.current?.click()}
          disabled={busy}
        >
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          Choose files
        </Button>
      </div>

      {error && (
        <p
          role="alert"
          className="mt-4 border-l-2 border-l-destructive py-2 pl-3 text-sm text-destructive"
        >
          {error}
        </p>
      )}

      <section className="mt-10">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <h2 className="flex items-baseline gap-2 font-display text-xl">
            Corpus
            <span className="font-mono text-[13px] text-muted-foreground">
              {data ? data.documents.length : "—"}
            </span>
            {reindexing && (
              <span className="flex items-center gap-1.5 text-[11px] text-[#8a6a2f] dark:text-[#d9a441]">
                <Loader2 className="h-3 w-3 animate-spin" /> reindexing
              </span>
            )}
          </h2>
          <div className="flex items-baseline gap-4">
            <span
              className="max-w-[12rem] truncate font-mono text-[11px] text-muted-foreground"
              title={data?.corpus_version || undefined}
            >
              v{(data?.corpus_version ?? "—").slice(0, 12)}
            </span>
            <button
              type="button"
              onClick={() =>
                triggerReindex()
                  .then(refresh)
                  .catch((e) => setError((e as Error).message))
              }
              disabled={reindexing}
              className="flex items-center gap-1 text-[11px] text-muted-foreground underline underline-offset-2 hover:text-foreground disabled:opacity-50"
            >
              <RefreshCw className="h-3 w-3" /> Reindex
            </button>
          </div>
        </div>

        <input
          aria-label="Filter documents"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter by name…"
          className="mt-4 h-9 w-full border-0 border-b border-border bg-transparent px-0 text-[13px] outline-none placeholder:text-muted-foreground/70"
        />

        <div className="mt-4">
          {data === null && !error && (
            <div className="space-y-2">
              <Skeleton className="h-7 w-full rounded-none" />
              <Skeleton className="h-7 w-full rounded-none" />
              <Skeleton className="h-7 w-full rounded-none" />
            </div>
          )}
          {data !== null && (
            <ul>
              {docs.map((d) => (
                <li
                  key={d.name}
                  className="flex items-center gap-4 border-t border-border/70 py-2.5 text-[13px]"
                >
                  <span className="flex-1 truncate">{d.name}</span>
                  <span className="font-mono text-[11px] text-muted-foreground">
                    {d.tokens} tok
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Delete ${d.name}`}
                    onClick={() => remove(d.name)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </li>
              ))}
              {data && docs.length === 0 && (
                <li className="border-t border-border/70 py-8 text-center text-[13px] text-muted-foreground">
                  {data.documents.length === 0
                    ? "The corpus is empty. Add a document to begin."
                    : "No documents match that filter."}
                </li>
              )}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
