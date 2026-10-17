"use client";

import { useRef, useState } from "react";
import { Loader2, Play, Square, TriangleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { TraceStep } from "@/components/trace-step";
import { AnswerPanel } from "@/components/answer-panel";
import { ChunkCard } from "@/components/chunk-card";
import { StrategySelector } from "@/components/strategy-selector";
import { streamQuery } from "@/lib/api";
import type { Strategy, Step, Trace } from "@/lib/types";

export default function TraceView() {
  const [query, setQuery] = useState(
    "How does attention differ from RNN sequence processing?",
  );
  const [strategy, setStrategy] = useState<Strategy>("semantic");
  const [correction, setCorrection] = useState(true);
  const [steps, setSteps] = useState<Step[]>([]);
  const [final, setFinal] = useState<Trace | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const generation = steps.find((s) => s.action === "generation");
  const pipelineSteps = steps.filter((s) => s.action !== "generation");

  async function run() {
    setRunning(true);
    setSteps([]);
    setFinal(null);
    setError(null);
    const controller = new AbortController();
    abortRef.current = controller;
    try {
      await streamQuery(
        { query, strategy, correction_enabled: correction },
        (event) => {
          if (event.type === "step") setSteps((prev) => [...prev, event.step]);
          else if (event.type === "final") setFinal(event.trace);
        },
        controller.signal,
      );
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        setError((e as Error).message);
      }
    } finally {
      setRunning(false);
      abortRef.current = null;
    }
  }

  function cancel() {
    abortRef.current?.abort();
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <Card className="mb-6">
        <CardContent className="pt-6">
          <form
            className="flex flex-col gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              if (!running) run();
            }}
          >
            <div className="flex gap-2">
              <input
                aria-label="Query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                maxLength={2000}
                placeholder="Ask something about the corpus…"
                className="h-10 flex-1 rounded-md border border-input bg-transparent px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
              {running ? (
                <Button type="button" variant="secondary" onClick={cancel}>
                  <Square className="h-4 w-4" /> Cancel
                </Button>
              ) : (
                <Button type="submit" disabled={!query.trim()}>
                  <Play className="h-4 w-4" /> Run
                </Button>
              )}
            </div>
            <StrategySelector
              strategy={strategy}
              onStrategy={setStrategy}
              correction={correction}
              onCorrection={setCorrection}
              disabled={running}
            />
          </form>
        </CardContent>
      </Card>

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm">
          <TriangleAlert className="h-4 w-4 text-destructive" aria-hidden />
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <section aria-label="Pipeline steps">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            Pipeline
          </h2>
          <div className="space-y-3" aria-live="polite">
            {pipelineSteps.map((step) => (
              <TraceStep key={step.step_number} step={step} />
            ))}
            {running && <Skeleton className="h-24 w-full rounded-lg" />}
            {!running && steps.length === 0 && !error && (
              <p className="text-sm text-muted-foreground">
                Run a query to watch the pipeline.
              </p>
            )}
          </div>
        </section>

        <section aria-label="Answer" className="lg:sticky lg:top-20 lg:self-start">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            Answer
          </h2>
          {final && <StatusBanner final={final} />}
          <Card>
            <CardContent className="pt-6">
              {generation?.answer !== undefined ? (
                <AnswerPanel
                  answer={generation.answer}
                  citations={generation.citations}
                />
              ) : final && final.final_status !== "success" ? (
                <FallbackView final={final} />
              ) : running ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" /> working…
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  The grounded answer and citations appear here.
                </p>
              )}
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  );
}

function StatusBanner({ final }: { final: Trace }) {
  const tone =
    final.final_status === "success"
      ? "default"
      : final.final_status === "not_found"
        ? "secondary"
        : "destructive";
  return (
    <div className="mb-2 flex items-center gap-2 text-xs">
      <Badge variant={tone}>{final.final_status}</Badge>
      <span className="font-mono text-muted-foreground">
        {final.total_latency_ms} ms · retries {final.retries}
      </span>
    </div>
  );
}

function FallbackView({ final }: { final: Trace }) {
  return (
    <div className="space-y-3">
      <p className="text-muted-foreground">
        {final.fallback_message ?? final.error ?? "No confident answer found."}
      </p>
      <div className="space-y-2">
        {final.closest_chunks?.map((chunk) => (
          <ChunkCard key={chunk.chunk_id} chunk={chunk} />
        ))}
      </div>
    </div>
  );
}
