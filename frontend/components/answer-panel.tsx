"use client";

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
  // Models emit light markdown; render bold rather than showing asterisks.
  // Inline [n] markers become superscript footnote references.
  const blocks = answer.split(/(\*\*[^*]+\*\*)/g);

  const inline = (text: string, key: string) =>
    text.split(/(\[\d+\])/g).map((part, i) => {
      const match = /^\[(\d+)\]$/.exec(part);
      const cite = match
        ? citations?.find((c) => c.ref === Number(match[1]))
        : undefined;
      if (!cite) return <span key={`${key}-${i}`}>{part}</span>;
      if (!onCitation) {
        return (
          <sup
            key={`${key}-${i}`}
            className="mx-0.5 font-sans text-[10px] text-destructive"
          >
            {cite.ref}
          </sup>
        );
      }
      return (
        <button
          key={`${key}-${i}`}
          type="button"
          onClick={() => onCitation(cite.chunk_id)}
          className="mx-0.5 align-super font-sans text-[10px] font-medium leading-none text-destructive underline decoration-dotted underline-offset-2 hover:bg-secondary"
          aria-label={`Show chunk ${cite.chunk_id} from ${cite.doc_title}`}
        >
          {cite.ref}
        </button>
      );
    });

  return (
    <div className="space-y-5">
      <p className="whitespace-pre-wrap font-serif text-[17px] leading-[1.75] tracking-[0.004em]">
        {blocks.map((block, i) => {
          const bold = /^\*\*([^*]+)\*\*$/.exec(block);
          return bold ? (
            <strong key={i} className="font-semibold">
              {inline(bold[1], `b${i}`)}
            </strong>
          ) : (
            <span key={i}>{inline(block, `t${i}`)}</span>
          );
        })}
      </p>

      {citations && citations.length > 0 && (
        <div className="border-t border-border pt-3">
          <p className="font-serif text-xs italic text-muted-foreground">Notes</p>
          <ol className="mt-2 space-y-1">
            {citations.map((c) => (
              <li key={c.ref} className="flex items-baseline gap-3 text-[12px]">
                <span className="w-4 shrink-0 text-right font-mono text-[10px] text-muted-foreground">
                  {c.ref}.
                </span>
                {onCitation ? (
                  <button
                    type="button"
                    onClick={() => onCitation(c.chunk_id)}
                    className="flex min-w-0 items-baseline gap-2 text-left hover:text-foreground"
                  >
                    <span className="truncate underline decoration-border underline-offset-2">
                      {c.doc_title}
                    </span>
                    <span className="shrink-0 font-mono text-[10px] text-muted-foreground">
                      {c.chunk_id}
                    </span>
                  </button>
                ) : (
                  <span className="flex min-w-0 items-baseline gap-2">
                    <span className="truncate">{c.doc_title}</span>
                    <span className="shrink-0 font-mono text-[10px] text-muted-foreground">
                      {c.chunk_id}
                    </span>
                  </span>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
