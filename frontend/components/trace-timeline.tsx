"use client";

import { Fragment } from "react";
import { STAGE_META } from "@/components/trace-step";
import type { Step } from "@/lib/types";

function formatMs(ms: number) {
  return ms >= 1000 ? `${(ms / 1000).toFixed(2)} s` : `${ms} ms`;
}

/**
 * The signature element: one Gantt lane per stage on a shared time axis.
 * Pass `scaleMax` to compare two traces on the same axis.
 */
export function TraceTimeline({
  steps,
  running,
  scaleMax,
}: {
  steps: Step[];
  running: boolean;
  scaleMax?: number;
}) {
  if (steps.length === 0) return null;

  const ownTotal = steps.reduce((sum, s) => sum + s.duration_ms, 0);
  const axisTotal = Math.max(scaleMax ?? ownTotal, ownTotal, 1);
  const rows = steps.map((step, i) => {
    const start = steps
      .slice(0, i)
      .reduce((sum, s) => sum + s.duration_ms, 0);
    return {
      step,
      i,
      startPct: (start / axisTotal) * 100,
      widthPct: Math.max((step.duration_ms / axisTotal) * 100, 0.4),
      retry: step.action === "hyde_rewrite",
    };
  });

  return (
    <div className="border-b border-border py-5">
      <div className="flex items-baseline justify-between">
        <span className="font-serif text-xs italic text-muted-foreground">
          Trace
        </span>
        <span className="font-mono text-[11px] text-muted-foreground">
          total {formatMs(ownTotal)}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-[4.5rem_minmax(0,1fr)_4rem] gap-x-4 sm:grid-cols-[6rem_minmax(0,1fr)_4.5rem]">
        <span aria-hidden />
        <div className="relative h-4">
          <div className="absolute inset-x-0 bottom-0 h-px bg-border" />
          <span className="absolute bottom-1 left-0 font-mono text-[10px] text-muted-foreground">
            0
          </span>
          <span className="absolute bottom-1 right-0 font-mono text-[10px] text-muted-foreground">
            {formatMs(axisTotal)}
          </span>
        </div>
        <span aria-hidden />

        {rows.map(({ step, i, startPct, widthPct, retry }) => {
          const label = STAGE_META[step.action]?.label ?? step.action;
          return (
            <Fragment key={step.step_number}>
              <span className="py-1 text-[12px]">{label}</span>
              <div className="relative my-1 h-5">
                <div className="absolute inset-x-0 top-1/2 h-px bg-border/60" />
                <div
                  title={`${label}: ${formatMs(step.duration_ms)}`}
                  className={`trace-segment absolute top-1/2 h-2 -translate-y-1/2 ${
                    retry ? "bg-destructive" : "bg-foreground/80"
                  }`}
                  style={{
                    left: `${startPct}%`,
                    width: `${widthPct}%`,
                    animationDelay: `${i * 60}ms`,
                  }}
                />
                {running && i === rows.length - 1 && (
                  <span
                    aria-hidden
                    className="absolute top-1/2 h-2 w-1.5 -translate-y-1/2 animate-pulse bg-foreground/40"
                    style={{ left: `${startPct + widthPct}%` }}
                  />
                )}
              </div>
              <span className="py-1 text-right font-mono text-[11px] text-muted-foreground">
                {formatMs(step.duration_ms)}
              </span>
            </Fragment>
          );
        })}
      </div>
    </div>
  );
}
