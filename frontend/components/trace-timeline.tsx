"use client";

import { STAGE_META } from "@/components/trace-step";
import type { Step } from "@/lib/types";

/** The signature element: one stacked bar of stage durations, drawn once. */
export function TraceTimeline({
  steps,
  running,
}: {
  steps: Step[];
  running: boolean;
}) {
  if (steps.length === 0) return null;
  const total = Math.max(
    1,
    steps.reduce((sum, s) => sum + s.duration_ms, 0),
  );

  return (
    <div className="border-b border-border py-4">
      <div className="flex h-2 w-full gap-px overflow-hidden">
        {steps.map((step) => {
          const retry = step.action === "hyde_rewrite";
          return (
            <div
              key={step.step_number}
              title={`${STAGE_META[step.action]?.label ?? step.action}: ${step.duration_ms} ms`}
              className={`trace-segment h-full ${
                retry ? "bg-destructive" : "bg-foreground/75"
              }`}
              style={{ width: `${(step.duration_ms / total) * 100}%` }}
            />
          );
        })}
        {running && (
          <div className="h-full flex-1 animate-pulse bg-foreground/15" />
        )}
      </div>
      <div className="mt-2.5 flex flex-wrap gap-x-5 gap-y-1 text-[11px] text-muted-foreground">
        {steps.map((step) => (
          <span key={step.step_number} className="flex items-center gap-1.5">
            <span
              aria-hidden
              className={`h-1.5 w-1.5 ${
                step.action === "hyde_rewrite"
                  ? "bg-destructive"
                  : "bg-foreground/60"
              }`}
            />
            {STAGE_META[step.action]?.label ?? step.action}
            <span className="font-mono">{step.duration_ms} ms</span>
          </span>
        ))}
        <span className="ml-auto font-mono">total {total} ms</span>
      </div>
    </div>
  );
}
