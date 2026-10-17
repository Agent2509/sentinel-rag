"use client";

import { useState } from "react";
import { ArrowLeftRight, Loader2, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AnswerPanel } from "@/components/answer-panel";
import { ChunkCard } from "@/components/chunk-card";
import { PageHeader } from "@/components/page-header";
import { TraceTimeline } from "@/components/trace-timeline";
import { STRATEGIES } from "@/components/strategy-selector";
import { useQueryStream } from "@/hooks/use-query-stream";
import { fallbackLabel } from "@/lib/fallback";
import type { Strategy, Step, Trace } from "@/lib/types";

interface PanelState {
  steps: Step[];
  final: Trace | null;
  running: boolean;
  error: string | null;
}

export default function ComparePage() {
  const [query, setQuery] = useState("");
  const [left, setLeft] = useState<Strategy>("fixed");
  const [right, setRight] = useState<Strategy>("semantic");
  const [leftCorrection, setLeftCorrection] = useState(true);
  const [rightCorrection, setRightCorrection] = useState(true);
  const leftStream = useQueryStream();
  const rightStream = useQueryStream();
  const running = leftStream.running || rightStream.running;
  const total = (steps: Step[]) =>
    steps.reduce((sum, step) => sum + step.duration_ms, 0);
  const sharedAxis = Math.max(
    total(leftStream.steps),
    total(rightStream.steps),
    1,
  );

  async function runBoth() {
    await Promise.all([
      leftStream.run({ query, strategy: left, correction_enabled: leftCorrection }),
      rightStream.run({
        query,
        strategy: right,
        correction_enabled: rightCorrection,
      }),
    ]);
  }

  function swap() {
    setLeft(right);
    setRight(left);
    setLeftCorrection(rightCorrection);
    setRightCorrection(leftCorrection);
    leftStream.reset();
    rightStream.reset();
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <PageHeader
        title="Compare"
        description="Run one question through two chunking strategies and read the same measures side by side."
      />

      <form
        className="border-y border-border py-4"
        onSubmit={(e) => {
          e.preventDefault();
          if (!running && query.trim()) runBoth();
        }}
      >
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <input
            aria-label="Query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            maxLength={2000}
            placeholder="Ask something about your documents…"
            className="h-10 flex-1 bg-transparent text-[15px] outline-none placeholder:text-muted-foreground/70"
          />
          <div className="flex gap-2">
            <Button
              type="button"
              variant="secondary"
              size="icon"
              onClick={swap}
              disabled={running}
              aria-label="Swap A and B"
              title="Swap A and B"
            >
              <ArrowLeftRight className="h-4 w-4" />
            </Button>
            <Button
              type="submit"
              disabled={running || !query.trim()}
              className="disabled:bg-transparent disabled:text-muted-foreground disabled:opacity-100 disabled:ring-1 disabled:ring-border"
            >
              {running ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              Compare
            </Button>
          </div>
        </div>
      </form>

      {(leftStream.final || rightStream.final) && (
        <DeltaStrip
          a={{ label: left, trace: leftStream.final }}
          b={{ label: right, trace: rightStream.final }}
        />
      )}

      <div className="mt-8 grid gap-10 lg:grid-cols-2">
        <Panel
          title="A"
          value={left}
          onChange={(v) => {
            setLeft(v);
            leftStream.reset();
          }}
          state={leftStream}
          scaleMax={sharedAxis}
          correction={leftCorrection}
          onCorrection={(c) => {
            setLeftCorrection(c);
            leftStream.reset();
          }}
          onCancel={leftStream.cancel}
          disabled={running}
        />
        <Panel
          title="B"
          value={right}
          onChange={(v) => {
            setRight(v);
            rightStream.reset();
          }}
          state={rightStream}
          scaleMax={sharedAxis}
          correction={rightCorrection}
          onCorrection={(c) => {
            setRightCorrection(c);
            rightStream.reset();
          }}
          onCancel={rightStream.cancel}
          disabled={running}
          className="lg:border-l lg:border-border lg:pl-10"
        />
      </div>
    </div>
  );
}

function DeltaStrip({
  a,
  b,
}: {
  a: { label: string; trace: Trace | null };
  b: { label: string; trace: Trace | null };
}) {
  const entries = [
    { key: "A", label: a.label, trace: a.trace },
    { key: "B", label: b.label, trace: b.trace },
  ];
  const fastest =
    a.trace && b.trace
      ? a.trace.total_latency_ms <= b.trace.total_latency_ms
        ? "A"
        : "B"
      : null;

  return (
    <div className="border-b border-border py-4">
      <div className="grid grid-cols-[6rem_1fr_1fr] items-baseline gap-x-6 gap-y-2 text-[13px]">
        <span className="font-serif text-xs italic text-muted-foreground">
          compare
        </span>
        {entries.map((e) => (
          <span key={e.key} className="text-[12px] text-muted-foreground">
            <span className="text-foreground">{e.key}</span> {e.label}
          </span>
        ))}

        <span className="text-[11px] text-muted-foreground">Latency</span>
        {entries.map((e) => (
          <span key={e.key} className="flex items-baseline gap-2">
            {fastest === e.key && (
              <span aria-hidden className="h-1.5 w-1.5 bg-foreground" />
            )}
            <span className="font-mono text-[12px]">
              {e.trace ? `${e.trace.total_latency_ms} ms` : "—"}
            </span>
            {fastest === e.key && <span className="sr-only">fastest</span>}
          </span>
        ))}

        <span className="text-[11px] text-muted-foreground">Retries</span>
        {entries.map((e) => (
          <span key={e.key} className="font-mono text-[12px]">
            {e.trace ? e.trace.retries : "—"}
          </span>
        ))}

        <span className="text-[11px] text-muted-foreground">Status</span>
        {entries.map((e) =>
          e.trace ? (
            <span
              key={e.key}
              className={`text-[12px] ${
                e.trace.final_status === "success"
                  ? "text-foreground"
                  : e.trace.final_status === "not_found"
                    ? "text-[#8a6a2f] dark:text-[#d9a441]"
                    : "text-destructive"
              }`}
            >
              {e.trace.final_status}
            </span>
          ) : (
            <span key={e.key} className="text-[12px] text-muted-foreground">
              running…
            </span>
          ),
        )}
      </div>
    </div>
  );
}

function Panel({
  title,
  value,
  onChange,
  state,
  scaleMax,
  correction,
  onCorrection,
  onCancel,
  disabled,
  className = "",
}: {
  title: string;
  value: Strategy;
  onChange: (s: Strategy) => void;
  state: PanelState;
  scaleMax: number;
  correction: boolean;
  onCorrection: (c: boolean) => void;
  onCancel: () => void;
  disabled: boolean;
  className?: string;
}) {
  const generation = state.steps.find((s) => s.action === "generation");
  const retrieval = state.steps.findLast((s) => s.action === "retrieval");
  const chunks = (retrieval?.chunks ?? state.final?.closest_chunks ?? []).slice(0, 3);

  return (
    <section className={`min-w-0 ${className}`}>
      <div className="flex flex-wrap items-baseline gap-3 border-t border-border pt-4">
        <span className="text-[13px] font-medium">{title}</span>
        <Select
          value={value}
          onValueChange={(v) => onChange(v as Strategy)}
          disabled={disabled}
        >
          <SelectTrigger className="h-7 w-[130px] border-0 px-2" aria-label={`Strategy ${title}`}>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STRATEGIES.map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <span className="ml-auto flex items-baseline gap-3 text-[11px] text-muted-foreground">
          {state.running && (
            <button type="button" onClick={onCancel} className="text-[11px] underline underline-offset-2">
              cancel
            </button>
          )}
          {state.final && (
            <>
              <span
                className={
                  state.final.final_status === "success"
                    ? "text-foreground"
                    : state.final.final_status === "not_found"
                      ? "text-[#8a6a2f] dark:text-[#d9a441]"
                      : "text-destructive"
                }
              >
                {state.final.final_status}
              </span>
              <span className="font-mono">{state.final.total_latency_ms} ms</span>
              <span className="font-mono">r{state.final.retries}</span>
            </>
          )}
        </span>
      </div>

      <div className="mt-3 flex items-center gap-2 border-t border-border/60 pt-3">
        <Switch
          id={`correction-${title}`}
          checked={correction}
          onCheckedChange={onCorrection}
          disabled={disabled}
        />
        <Label
          htmlFor={`correction-${title}`}
          className="text-[12px] text-muted-foreground"
        >
          Self-correction (HyDE)
        </Label>
      </div>

      {state.steps.length > 0 && (
        <TraceTimeline
          steps={state.steps}
          running={state.running}
          scaleMax={scaleMax}
        />
      )}

      <div className="mt-3 space-y-3 text-[13px]" aria-live="polite">
        {state.error && <p className="text-destructive">{state.error}</p>}
        {!state.running && !state.final && state.steps.length === 0 && (
          <p className="font-serif text-[15px] italic leading-relaxed text-muted-foreground">
            Pick a chunking strategy and run the comparison.
          </p>
        )}
        {state.running && (
          <p className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            {state.steps.at(-1)?.action ?? "starting"}…
          </p>
        )}
        {generation?.answer && (
          <AnswerPanel answer={generation.answer} citations={generation.citations} />
        )}
        {!state.running && !generation && state.final && (
          <div className="space-y-1">
            <p className="text-muted-foreground">
              {state.final.fallback_message ??
                state.final.error ??
                "No confident answer."}
            </p>
            {state.final.fallback_reason && (
              <p className="text-xs text-muted-foreground/80">
                <span className="font-medium text-foreground">Why: </span>
                {fallbackLabel(state.final.fallback_reason)}
              </p>
            )}
          </div>
        )}
        {chunks.length > 0 && (
          <div>
            <p className="font-serif text-xs italic text-muted-foreground">
              Retrieved passages
            </p>
            {chunks.map((c) => (
              <ChunkCard key={c.chunk_id} chunk={c} compact />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
