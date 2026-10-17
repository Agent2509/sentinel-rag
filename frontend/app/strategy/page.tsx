"use client";

import { useEffect, useRef, useState } from "react";
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
import { STRATEGIES } from "@/components/strategy-selector";
import { streamQuery } from "@/lib/api";
import type { Strategy, Step, Trace } from "@/lib/types";

interface PanelState {
  steps: Step[];
  final: Trace | null;
  running: boolean;
  error: string | null;
  correction: boolean;
}

const EMPTY: PanelState = {
  steps: [],
  final: null,
  running: false,
  error: null,
  correction: true,
};

export default function StrategyLab() {
  const [query, setQuery] = useState("What is LoRA?");
  const [left, setLeft] = useState<Strategy>("fixed");
  const [right, setRight] = useState<Strategy>("semantic");
  const [panels, setPanels] = useState<Record<string, PanelState>>({
    left: EMPTY,
    right: EMPTY,
  });
  const abortRef = useRef<Record<string, AbortController>>({});
  const running = panels.left.running || panels.right.running;

  useEffect(
    () => () => Object.values(abortRef.current).forEach((c) => c.abort()),
    [],
  );

  function patch(key: string, update: Partial<PanelState>) {
    setPanels((prev) => ({ ...prev, [key]: { ...prev[key], ...update } }));
  }

  async function runSide(key: string, strategy: Strategy) {
    const controller = new AbortController();
    abortRef.current[key] = controller;
    patch(key, { steps: [], final: null, error: null, running: true });
    try {
      await streamQuery(
        { query, strategy, correction_enabled: panels[key].correction },
        (event) => {
          if (event.type === "step") {
            setPanels((prev) => ({
              ...prev,
              [key]: { ...prev[key], steps: [...prev[key].steps, event.step] },
            }));
          } else if (event.type === "final") {
            patch(key, { final: event.trace });
          }
        },
        controller.signal,
      );
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        patch(key, { error: (e as Error).message });
      }
    } finally {
      delete abortRef.current[key];
      patch(key, { running: false });
    }
  }

  async function runBoth() {
    await Promise.all([runSide("left", left), runSide("right", right)]);
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <Card className="mb-6">
        <CardContent className="flex flex-col gap-3 pt-6">
          <div className="flex gap-2">
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
          onChange={setLeft}
          state={panels.left}
          onCorrection={(c) => patch("left", { correction: c })}
          onCancel={() => abortRef.current.left?.abort()}
          disabled={running}
        />
        <Panel
          title="B"
          value={right}
          onChange={setRight}
          state={panels.right}
          onCorrection={(c) => patch("right", { correction: c })}
          onCancel={() => abortRef.current.right?.abort()}
          disabled={running}
        />
      </div>
    </div>
  );
}

function Panel({
  title,
  value,
  onChange,
  state,
  onCorrection,
  onCancel,
  disabled,
}: {
  title: string;
  value: Strategy;
  onChange: (s: Strategy) => void;
  state: PanelState;
  onCorrection: (c: boolean) => void;
  onCancel: () => void;
  disabled: boolean;
}) {
  const generation = state.steps.find((s) => s.action === "generation");
  const retrieval = state.steps.findLast((s) => s.action === "retrieval");
  const chunks = (retrieval?.chunks ?? state.final?.closest_chunks ?? []).slice(0, 3);

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between gap-2">
        <CardTitle className="flex items-center gap-2 text-sm">
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
            checked={state.correction}
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
        {state.error && <p className="text-destructive">{state.error}</p>}
        {state.running && (
          <p className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            {state.steps.at(-1)?.action ?? "starting"}…
          </p>
        )}
        {chunks.map((c) => (
          <ChunkCard key={c.chunk_id} chunk={c} />
        ))}
        {generation?.answer !== undefined && (
          <AnswerPanel answer={generation.answer} citations={generation.citations} />
        )}
        {!state.running && !generation && state.final && (
          <p className="text-muted-foreground">
            {state.final.fallback_message ?? "No confident answer."}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
