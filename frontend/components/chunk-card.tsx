import { Badge } from "@/components/ui/badge";
import type { Chunk } from "@/lib/types";

export function ChunkCard({ chunk }: { chunk: Chunk }) {
  const shown = chunk.context || chunk.text || "";
  const snippet = shown.length > 320 ? `${shown.slice(0, 320)}…` : shown;

  return (
    <div className="rounded-md border border-border/60 bg-muted/30 p-3 text-sm">
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
      <p className="mt-2 whitespace-pre-wrap text-muted-foreground">{snippet}</p>
    </div>
  );
}
