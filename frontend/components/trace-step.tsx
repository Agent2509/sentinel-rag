"use client";

import {
  Gauge,
  MessageSquareText,
  RefreshCw,
  Route,
  Search,
  type LucideIcon,
} from "lucide-react";
import { AnswerPanel } from "@/components/answer-panel";
import { ChunkCard } from "@/components/chunk-card";
import type { Step } from "@/lib/types";

export const STAGE_META: Record<string, { icon: LucideIcon; label: string }> = {
  routing: { icon: Route, label: "Route" },
  retrieval: { icon: Search, label: "Retrieve" },
  grading: { icon: Gauge, label: "Grade" },
  hyde_rewrite: { icon: RefreshCw, label: "Retry" },
  generation: { icon: MessageSquareText, label: "Answer" },
};

export function TraceStep({
  step,
  threshold = null,
  onCitation,
  highlightedChunk,
}: {
  step: Step;
  index?: number;
  threshold?: number | null;
  onCitation?: (chunkId: string) => void;
  highlightedChunk?: string | null;
}) {
  const meta = STAGE_META[step.action] ?? {
    icon: Search,
    label: step.action,
  };
  const retry = step.action === "hyde_rewrite";
  const answered = step.action === "generation";

  return (
    <section className="border-t border-border py-5">
      <div className="flex items-baseline gap-3">
        <span className="w-4 shrink-0 text-right font-mono text-[11px] text-muted-foreground">
          {step.step_number}
        </span>
        <span className="text-[13px] font-medium">{meta.label}</span>
        {retry && (
          <span className="font-sans text-[10px] text-destructive">retry</span>
        )}
        {answered && (
          <span className="font-sans text-[10px] text-muted-foreground">
            answered
          </span>
        )}
        <span className="ml-auto font-mono text-[11px] text-muted-foreground">
          {step.duration_ms} ms
        </span>
      </div>

      <div className="mt-3 space-y-3 pl-7 text-[13px] leading-relaxed">
        {step.action === "routing" && step.result && (
          <p className="text-muted-foreground">
            <span className="text-foreground">{step.result.type}</span> — {step.result.reason}
          </p>
        )}

        {step.action === "retrieval" && (
          <>
            {step.query_used && (
              <p className="font-mono text-[11px] text-muted-foreground">
                {step.query_used}
              </p>
            )}
            <div>
              {step.chunks?.map((chunk) => (
                <ChunkCard
                  key={chunk.chunk_id}
                  chunk={chunk}
                  highlighted={highlightedChunk === chunk.chunk_id}
                />
              ))}
            </div>
          </>
        )}

        {step.action === "grading" && step.grade && (
          <GradeView grade={step.grade} threshold={threshold} />
        )}

        {step.action === "hyde_rewrite" && step.hypothetical_document && (
          <p className="whitespace-pre-wrap font-serif text-[15px] italic leading-relaxed text-muted-foreground">
            {step.hypothetical_document}
          </p>
        )}

        {step.action === "generation" && step.answer !== undefined && (
          <AnswerPanel
            answer={step.answer}
            citations={step.citations}
            onCitation={onCitation}
          />
        )}
      </div>
    </section>
  );
}

function GradeView({
  grade,
  threshold,
}: {
  grade: NonNullable<Step["grade"]>;
  threshold: number | null;
}) {
  if (grade.error) {
    return (
      <div className="space-y-1">
        <p className="text-destructive">The grader failed on this pass.</p>
        <p className="text-muted-foreground">{grade.reason}</p>
      </div>
    );
  }

  const relevant =
    threshold === null || grade.score === null
      ? null
      : grade.score >= threshold;
  const pct = Math.round((grade.score ?? 0) * 100);

  return (
    <div className="space-y-2">
      <div className="flex items-baseline gap-3">
        <span className="font-mono text-[12px]">{grade.score?.toFixed(2) ?? "n/a"}</span>
        <span className="text-[11px] text-muted-foreground">
          {relevant === null
            ? "no threshold"
            : relevant
              ? "pass"
              : "below threshold"}
          {threshold !== null && ` · pass ≥ ${threshold}`}
        </span>
      </div>
      <div className="h-1 w-full bg-secondary">
        <div
          className={`h-full ${relevant === false ? "bg-destructive" : "bg-foreground"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {grade.reason && <p className="text-muted-foreground">{grade.reason}</p>}
    </div>
  );
}
