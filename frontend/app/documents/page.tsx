"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { FileText, Loader2, RefreshCw, Trash2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { deleteDocument, getDocuments, triggerReindex, uploadDocument } from "@/lib/api";
import type { DocumentsPayload } from "@/lib/types";

export default function Documents() {
  const [data, setData] = useState<DocumentsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [drag, setDrag] = useState(false);
  const [filter, setFilter] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const refresh = useCallback(async () => {
    try {
      setData(await getDocuments());
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 3000); // picks up reindex completion
    return () => clearInterval(id);
  }, [refresh]);

  async function upload(files: FileList | null) {
    if (!files?.length) return;
    setBusy(true);
    setError(null);
    try {
      for (const file of Array.from(files)) await uploadDocument(file);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function remove(name: string) {
    setError(null);
    try {
      await deleteDocument(name);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const reindexing = data?.reindexing ?? false;
  const docs = (data?.documents ?? []).filter((d) =>
    d.name.toLowerCase().includes(filter.trim().toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <h1 className="mb-1 text-lg font-semibold">Documents</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Upload markdown, text, or PDF files. Each upload re-embeds the corpus and
        rebuilds all three indexes.
      </p>

      <Card
        className={`mb-6 border-dashed ${drag ? "border-primary" : ""}`}
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
        <CardContent className="flex flex-col items-center gap-3 py-8 text-center">
          <Upload className="h-6 w-6 text-muted-foreground" aria-hidden />
          <p className="text-sm text-muted-foreground">
            Drag files here, or
          </p>
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".md,.txt,.pdf"
            className="hidden"
            onChange={(e) => upload(e.target.files)}
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

      {error && <p className="mb-4 text-sm text-destructive">{error}</p>}

      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm">
            Corpus
            <Badge variant="secondary">{data?.documents.length ?? 0}</Badge>
            {reindexing && (
              <span className="flex items-center gap-1 text-xs font-normal text-amber-500">
                <Loader2 className="h-3 w-3 animate-spin" /> reindexing…
              </span>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] text-muted-foreground">
              v{data?.corpus_version ?? "—"}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => triggerReindex().then(refresh)}
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
        </CardContent>
      </Card>
    </div>
  );
}
