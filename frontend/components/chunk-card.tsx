"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import type { Chunk } from "@/lib/types";

const SNIPPET = 320;

export function ChunkCard({
  chunk,
  highlighted = false,
}: {
  chunk: Chunk;
  highlighted?: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const text = chunk.context || chunk.text || "";
  const long = text.length > SNIPPET;
  const shown = expanded || !long ? text : `${text.slice(0, SNIPPET)}…`;

  return (
    <div
      id={`chunk-${chunk.chunk_id}`}
      className={`rounded-md border bg-muted/30 p-3 text-sm transition-shadow ${
        highlighted
          ? "border-primary ring-2 ring-primary/40"
          : "border-border/60"
      }`}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-medium">{chunk.doc_title}</span>
        <span className="text-xs text-muted-foreground">{chunk.chunk_id}</span>
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
