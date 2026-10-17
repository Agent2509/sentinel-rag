"use client";

import { useState } from "react";
import { Loader2, Play, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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

export default function StrategyLab() {
  const [query, setQuery] = useState("What is LoRA?");
  const [left, setLeft] = useState<Strategy>("fixed");
  const [right, setRight] = useState<Strategy>("semantic");
  const [leftCorrection, setLeftCorrection] = useState(true);
  const [rightCorrection, setRightCorrection] = useState(true);
  const leftStream = useQueryStream();
  const rightStream = useQueryStream();
  const running = leftStream.running || rightStream.running;

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

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <PageHeader
        title="Strategy Lab"
        description="Run one query through two chunking strategies side by side."
      />

      <Card className="mb-6">
        <CardContent className="flex flex-col gap-3 pt-6">
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              aria-label="Query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              maxLength={2000}
              placeholder="Ask something…"
              className="h-10 flex-1 rounded-md border border-input bg-transparent px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            <Button onClick={runBoth} disabled={running || !query.trim()}>
              {running ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              Compare
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel
          title="A"
          value={left}
          onChange={(v) => {
            setLeft(v);
            leftStream.reset();
          }}
          state={leftStream}
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
          correction={rightCorrection}
          onCorrection={(c) => {
            setRightCorrection(c);
            rightStream.reset();
          }}
          onCancel={rightStream.cancel}
          disabled={running}
        />
      </div>

      {leftStream.final && rightStream.final && (
        <DeltaStrip
          a={{ label: left, trace: leftStream.final }}
          b={{ label: right, trace: rightStream.final }}
        />
      )}
    </div>
  );
}

/** What the page exists for: the comparison that was never on screen. */
function DeltaStrip({
  a,
  b,
}: {
  a: { label: string; trace: Trace };
  b: { label: string; trace: Trace };
}) {
  const entries = [
    { key: "A", label: a.label, trace: a.trace },
    { key: "B", label: b.label, trace: b.trace },
  ];
  const fastest =
    a.trace.total_latency_ms <= b.trace.total_latency_ms ? "A" : "B";

  return (
    <Card className="mt-6">
      <CardContent className="grid grid-cols-[4.5rem_1fr_1fr] items-center gap-x-4 gap-y-2 pt-4 text-sm">
        <span className="text-xs text-muted-foreground">compare</span>
        {entries.map((e) => (
          <span key={e.key} className="font-mono text-xs text-muted-foreground">
            {e.key} · {e.label}
          </span>
        ))}

        <span className="text-xs text-muted-foreground">Latency</span>
        {entries.map((e) => (
          <span key={e.key} className="flex items-center gap-1.5 font-mono">
            <span
              aria-hidden
              className={`h-1.5 w-1.5 rounded-full ${
                fastest === e.key ? "bg-emerald-400" : "bg-transparent"
              }`}
            />
            {e.trace.total_latency_ms} ms
            {fastest === e.key && <span className="sr-only">fastest</span>}
          </span>
        ))}

        <span className="text-xs text-muted-foreground">Retries</span>
        {entries.map((e) => (
          <span key={e.key} className="font-mono">
            r{e.trace.retries}
          </span>
        ))}

        <span className="text-xs text-muted-foreground">Status</span>
        {entries.map((e) => (
          <Badge
            key={e.key}
            variant={
              e.trace.final_status === "success"
                ? "default"
                : e.trace.final_status === "not_found"
                  ? "secondary"
                  : "destructive"
            }
            className="w-fit"
          >
            {e.trace.final_status}
          </Badge>
        ))}
      </CardContent>
    </Card>
  );
}

function Panel({
  title,
  value,
  onChange,
  state,
  correction,
  onCorrection,
  onCancel,
  disabled,
}: {
  title: string;
  value: Strategy;
  onChange: (s: Strategy) => void;
  state: PanelState;
  correction: boolean;
  onCorrection: (c: boolean) => void;
  onCancel: () => void;
  disabled: boolean;
}) {
  const generation = state.steps.find((s) => s.action === "generation");
  const retrieval = state.steps.findLast((s) => s.action === "retrieval");
  const chunks = (retrieval?.chunks ?? state.final?.closest_chunks ?? []).slice(0, 3);

  return (
    <Card className="min-w-0">
      <CardHeader className="grid-cols-[1fr_auto] items-center gap-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          {/* A/B tint without plumbing a prop: emerald vs teal, same dot in the delta strip */}
          <span
            aria-hidden
            className={`h-2 w-2 shrink-0 rounded-full ${
              title === "A" ? "bg-emerald-400" : "bg-cyan-400"
            }`}
          />
          <span className="text-muted-foreground">{title}</span>{" "}
          <Select
            value={value}
            onValueChange={(v) => onChange(v as Strategy)}
            disabled={disabled}
          >
            <SelectTrigger className="h-8 w-[140px]" aria-label={`Strategy ${title}`}>
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
        </CardTitle>
        <div className="flex items-center gap-2">
          {state.running && (
            <Button type="button" variant="secondary" size="sm" onClick={onCancel}>
              <Square className="h-3.5 w-3.5" /> Cancel
            </Button>
          )}
          {state.final && (
            <div className="flex items-center gap-2 text-xs">
              <Badge
                variant={
                  state.final.final_status === "success"
                    ? "default"
                    : state.final.final_status === "not_found"
                      ? "secondary"
                      : "destructive"
                }
              >
                {state.final.final_status}
              </Badge>
              <span className="font-mono text-muted-foreground">
                {state.final.total_latency_ms}ms · r{state.final.retries}
              </span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3 text-sm" aria-live="polite">
        <div className="flex items-center gap-2">
          <Switch
            id={`correction-${title}`}
            checked={correction}
            onCheckedChange={onCorrection}
            disabled={disabled}
          />
          <Label
            htmlFor={`correction-${title}`}
            className="text-xs text-muted-foreground"
          >
            Self-correction (HyDE)
          </Label>
        </div>
        {state.error && (
          <p role="alert" className="text-destructive">
            {state.error}
          </p>
        )}
        {!state.running && !state.final && state.steps.length === 0 && (
          <p className="text-muted-foreground">
            Pick a chunking strategy above and hit Compare to see both pipelines
            run on the same query.
          </p>
        )}
        {state.running && (
          <p className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            {state.steps.at(-1)?.action ?? "starting"}…
          </p>
        )}
        {chunks.map((c) => (
          <ChunkCard key={c.chunk_id} chunk={c} />
        ))}
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
      </CardContent>
    </Card>
  );
}
