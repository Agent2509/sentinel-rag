"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import type { Chunk } from "@/lib/types";

const SNIPPET = 320;
const COMPACT_SNIPPET = 140;

export function ChunkCard({
  chunk,
  highlighted = false,
  compact = false,
}: {
  chunk: Chunk;
  highlighted?: boolean;
  compact?: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const text = chunk.context || chunk.text || "";
  const snippet = compact ? COMPACT_SNIPPET : SNIPPET;
  const long = text.length > snippet;
  const shown = expanded || !long ? text : `${text.slice(0, snippet)}…`;

  return (
    <div
      data-chunk-id={chunk.chunk_id}
      className={`rounded-md border bg-muted/30 p-3 text-sm transition-colors ${
        highlighted
          ? "border-primary/70 ring-2 ring-primary/30 shadow-[0_0_28px_-8px] shadow-primary/50"
          : "border-border/60 hover:border-border"
      }`}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-medium">{chunk.doc_title}</span>
        <span className="font-mono text-[11px] text-muted-foreground">
          {chunk.chunk_id}
        </span>
        {typeof chunk.rrf_score === "number" && (
          <Badge variant="outline" className="ml-auto font-mono text-[10px]">
            rrf {chunk.rrf_score.toFixed(4)}
          </Badge>
        )}
        {typeof chunk.bm25_rank === "number" && (
          <Badge variant="secondary" className="font-mono text-[10px]">
            bm25 #{chunk.bm25_rank + 1}
          </Badge>
        )}
        {typeof chunk.vector_rank === "number" && (
          <Badge variant="secondary" className="font-mono text-[10px]">
            vec #{chunk.vector_rank + 1}
          </Badge>
        )}
      </div>
      <p className="mt-2 whitespace-pre-wrap text-muted-foreground">{shown}</p>
      {long && (
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="mt-1 text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground"
        >
          {expanded ? "Show less" : `Show more (${text.length} chars)`}
        </button>
      )}
    </div>
  );
}
