"use client";

import { useState } from "react";
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
      className={`border-t border-border/70 py-3 transition-colors ${
        highlighted ? "border-l-2 border-l-destructive pl-3" : "border-l-2 border-l-transparent"
      }`}
    >
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="text-[13px] font-medium">{chunk.doc_title}</span>
        <span className="font-mono text-[11px] text-muted-foreground">
          {chunk.chunk_id}
        </span>
        <span className="ml-auto flex items-baseline gap-3 font-mono text-[11px] text-muted-foreground">
          {typeof chunk.rrf_score === "number" && (
            <span>rrf {chunk.rrf_score.toFixed(4)}</span>
          )}
          {typeof chunk.bm25_rank === "number" && (
            <span>bm25 #{chunk.bm25_rank + 1}</span>
          )}
          {typeof chunk.vector_rank === "number" && (
            <span>vec #{chunk.vector_rank + 1}</span>
          )}
        </span>
      </div>
      <p className="mt-1.5 text-[13px] leading-relaxed text-muted-foreground">
        {shown}
      </p>
      {long && (
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="mt-1 text-[11px] text-muted-foreground underline decoration-border underline-offset-2 hover:text-foreground"
        >
          {expanded ? "Show less" : `Show more (${text.length} chars)`}
        </button>
      )}
    </div>
  );
}
