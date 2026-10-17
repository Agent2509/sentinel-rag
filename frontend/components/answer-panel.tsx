import { Badge } from "@/components/ui/badge";
import type { Citation } from "@/lib/types";

export function AnswerPanel({
  answer,
  citations,
}: {
  answer: string;
  citations: Citation[] | undefined;
}) {
  return (
    <div className="space-y-3">
      <p className="whitespace-pre-wrap leading-relaxed">{answer}</p>
      {citations && citations.length > 0 && (
        <div>
          <p className="mb-1 text-xs font-medium text-muted-foreground">
            Citations
          </p>
          <ul className="space-y-1 text-sm">
            {citations.map((c) => (
              <li key={c.ref} className="flex items-center gap-2">
                <Badge variant="outline" className="font-mono text-[10px]">
                  [{c.ref}]
                </Badge>
                <span className="text-muted-foreground">{c.doc_title}</span>
                <span className="font-mono text-[11px] text-muted-foreground/70">
                  {c.chunk_id}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
