"use client";

import { Badge } from "@/components/ui/badge";
import type { Citation } from "@/lib/types";

export function AnswerPanel({
  answer,
  citations,
  onCitation,
}: {
  answer: string;
  citations: Citation[] | undefined;
  onCitation?: (chunkId: string) => void;
}) {
  // Inline [n] markers become buttons that reveal the cited chunk.
  const parts = answer.split(/(\[\d+\])/g);

  return (
    <div className="space-y-3">
      <p className="whitespace-pre-wrap leading-relaxed">
        {parts.map((part, i) => {
          const match = /^\[(\d+)\]$/.exec(part);
          const cite = match
            ? citations?.find((c) => c.ref === Number(match[1]))
            : undefined;
          if (!cite || !onCitation) return <span key={i}>{part}</span>;
          return (
            <button
              key={i}
              type="button"
              onClick={() => onCitation(cite.chunk_id)}
              className="rounded px-0.5 font-mono text-xs text-primary underline decoration-dotted underline-offset-2 hover:bg-primary/10"
              aria-label={`Show chunk ${cite.chunk_id} from ${cite.doc_title}`}
            >
              [{cite.ref}]
            </button>
          );
        })}
      </p>
      {citations && citations.length > 0 && (
        <div>
          <p className="mb-1 text-xs font-medium text-muted-foreground">
            Citations
          </p>
          <ul className="space-y-0.5 text-sm">
            {citations.map((c) => (
              <li key={c.ref}>
                {onCitation ? (
                  <button
                    type="button"
                    onClick={() => onCitation(c.chunk_id)}
                    className="flex w-full items-center gap-2 rounded px-1 py-0.5 text-left hover:bg-muted/60"
                  >
                    <Badge variant="outline" className="font-mono text-[10px]">
                      [{c.ref}]
                    </Badge>
                    <span className="text-muted-foreground">{c.doc_title}</span>
                    <span className="font-mono text-[11px] text-muted-foreground/70">
                      {c.chunk_id}
                    </span>
                  </button>
                ) : (
                  <span className="flex w-full items-center gap-2 rounded px-1 py-0.5 text-left">
                    <Badge variant="outline" className="font-mono text-[10px]">
                      [{c.ref}]
                    </Badge>
                    <span className="text-muted-foreground">{c.doc_title}</span>
                    <span className="font-mono text-[11px] text-muted-foreground/70">
                      {c.chunk_id}
                    </span>
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
