"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { FileText, Loader2, RefreshCw, Trash2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/page-header";
import { deleteDocument, getDocuments, triggerReindex, uploadDocument } from "@/lib/api";
import type { DocumentsPayload } from "@/lib/types";

const ACCEPT_EXT = [".md", ".txt", ".pdf"];

export default function Documents() {
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
    <div className="mx-auto max-w-4xl px-4 py-8">
      <PageHeader
        title="Documents"
        description="Upload markdown, text, or PDF files. Each upload re-embeds the corpus and rebuilds all three indexes."
      />

      <Card
        className={`mb-6 border-dashed transition-colors ${
          drag ? "border-primary/70 bg-primary/[0.06]" : "border-border/70"
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
        <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Upload className="h-5 w-5" aria-hidden />
          </span>
          <div>
            <p className="text-sm font-medium">Drop files to ingest</p>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {ACCEPT_EXT.join(" · ")} — the corpus re-embeds on upload
            </p>
          </div>
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
            variant="secondary"
            onClick={() => inputRef.current?.click()}
            disabled={busy}
          >
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Choose files
          </Button>
        </CardContent>
      </Card>

      {error && (
        <p role="alert" className="mb-4 text-sm text-destructive">
          {error}
        </p>
      )}

      <Card>
        <CardHeader className="grid-cols-[1fr_auto] items-center">
          <CardTitle className="flex items-center gap-2 text-sm">
            Corpus
            <Badge variant="secondary">{data ? data.documents.length : "—"}</Badge>
            {reindexing && (
              <span className="flex items-center gap-1 text-xs font-normal text-amber-500">
                <Loader2 className="h-3 w-3 animate-spin" /> reindexing…
              </span>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            <span
              className="max-w-[10rem] truncate font-mono text-[11px] text-muted-foreground"
              title={data?.corpus_version || undefined}
            >
              v{(data?.corpus_version ?? "—").slice(0, 12)}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() =>
                triggerReindex()
                  .then(refresh)
                  .catch((e) => setError((e as Error).message))
              }
              disabled={reindexing}
            >
              <RefreshCw className="h-3.5 w-3.5" /> Reindex
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <input
            aria-label="Filter documents"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by name…"
            className="mb-3 h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
          {data === null && !error && (
            <div className="space-y-2">
              <Skeleton className="h-8 rounded-md" />
              <Skeleton className="h-8 rounded-md" />
              <Skeleton className="h-8 rounded-md" />
            </div>
          )}
          {data !== null && (
            <ul className="divide-y divide-border/60">
            {docs.map((d) => (
              <li key={d.name} className="flex items-center gap-3 py-2 text-sm">
                <FileText className="h-4 w-4 text-muted-foreground" aria-hidden />
                <span className="flex-1 truncate">{d.name}</span>
                <span className="font-mono text-xs text-muted-foreground">
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
              <li className="py-6 text-center text-sm text-muted-foreground">
                {data.documents.length === 0
                  ? "No documents yet."
                  : "No documents match that filter."}
              </li>
            )}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
