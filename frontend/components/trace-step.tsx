"use client";

import {
  Gauge,
  MessageSquareText,
  RefreshCw,
  Route,
  Search,
  type LucideIcon,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AnswerPanel } from "@/components/answer-panel";
import { ChunkCard } from "@/components/chunk-card";
import type { Step } from "@/lib/types";

export const STAGE_META: Record<string, { icon: LucideIcon; label: string }> = {
  routing: { icon: Route, label: "Routing" },
  retrieval: { icon: Search, label: "Retrieval" },
  grading: { icon: Gauge, label: "Grading" },
  hyde_rewrite: { icon: RefreshCw, label: "HyDE rewrite" },
  generation: { icon: MessageSquareText, label: "Generation" },
};

export function TraceStep({
  step,
  index = 0,
  threshold = 0.6,
  onCitation,
  highlightedChunk,
}: {
  step: Step;
  index?: number;
  threshold?: number;
  onCitation?: (chunkId: string) => void;
  highlightedChunk?: string | null;
}) {
  const meta = STAGE_META[step.action] ?? {
    icon: Search,
    label: step.action,
  };
  const Icon = meta.icon;

  // Retry and success are carried by border + badge text + icon, not color alone.
  const tone =
    step.action === "hyde_rewrite"
      ? "retry"
      : step.action === "generation"
        ? "answer"
        : "idle";

  return (
    <Card
      style={{ animationDelay: `${index * 20}ms`, animationFillMode: "backwards" }}
      className={`animate-in fade-in slide-in-from-bottom-2 duration-300 motion-reduce:animate-none ${
        tone === "retry"
          ? "border-amber-500/40"
          : tone === "answer"
            ? "border-emerald-500/40"
            : ""
      }`}
    >
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-secondary text-xs">
            {step.step_number}
          </span>
          <Icon className="h-4 w-4 text-muted-foreground" aria-hidden />
          <span>{meta.label}</span>
          {tone === "retry" && (
            <Badge
              variant="outline"
              className="gap-1 border-amber-500/50 text-amber-500"
            >
              <span
                className="h-1.5 w-1.5 rounded-full bg-amber-500 motion-safe:animate-pulse"
                aria-hidden
              />
              retrying
            </Badge>
          )}
          {tone === "answer" && (
            <Badge variant="outline" className="border-emerald-500/50 text-emerald-500">
              answered
            </Badge>
          )}
          <span className="ml-auto font-mono text-xs font-normal text-muted-foreground">
            {step.duration_ms} ms
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        {step.action === "routing" && step.result && (
          <div className="flex items-center gap-2">
            <Badge variant={step.result.type === "simple" ? "secondary" : "default"}>
              {step.result.type}
            </Badge>
            <span className="text-muted-foreground">{step.result.reason}</span>
          </div>
        )}

        {step.action === "retrieval" && (
          <>
            {step.query_used && (
              <p className="font-mono text-xs text-muted-foreground">
                query: {step.query_used}
              </p>
            )}
            <div className="space-y-2">
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
          <p className="whitespace-pre-wrap text-muted-foreground">
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
      </CardContent>
    </Card>
  );
}

function GradeView({
  grade,
  threshold,
}: {
  grade: NonNullable<Step["grade"]>;
  threshold: number;
}) {
  if (grade.error) {
    return (
      <div className="space-y-2">
        <Badge variant="outline" className="border-destructive/50 text-destructive">
          grader failed
        </Badge>
        <p className="text-muted-foreground">{grade.reason}</p>
      </div>
    );
  }

  const relevant = grade.score !== null && grade.score >= threshold;
  const pct = Math.round((grade.score ?? 0) * 100);
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Badge variant={relevant ? "default" : "destructive"}>
          {relevant ? "✓ relevant" : "✗ low"}
        </Badge>
        <span className="font-mono text-xs text-muted-foreground">
          score {grade.score === null ? "n/a" : grade.score.toFixed(2)} · pass ≥{" "}
          {threshold}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-secondary">
        <div
          className={`h-full rounded-full ${relevant ? "bg-emerald-500" : "bg-amber-500"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {grade.reason && (
        <p className="text-muted-foreground">{grade.reason}</p>
      )}
    </div>
  );
}
