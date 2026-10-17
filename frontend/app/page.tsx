"use client";

import { useEffect, useRef, useState } from "react";
import { Loader2, Play, Square, TriangleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { STAGE_META, TraceStep } from "@/components/trace-step";
import { AnswerPanel } from "@/components/answer-panel";
import { ChunkCard } from "@/components/chunk-card";
import { StrategySelector } from "@/components/strategy-selector";
import { TraceHistory } from "@/components/trace-history";
import { getHealth, getTrace, streamQuery } from "@/lib/api";
import type { Strategy, Step, Trace } from "@/lib/types";

const IDLE_STAGES = [
  { key: "routing", title: "Route", body: "an LLM labels the query simple or complex" },
  { key: "retrieval", title: "Retrieve", body: "BM25 + vector search, fused by RRF" },
  { key: "grading", title: "Grade", body: "an LLM scores whether the chunks can answer it" },
  { key: "hyde_rewrite", title: "Retry", body: "a low score triggers a HyDE rewrite" },
  { key: "generation", title: "Answer", body: "grounded generation with citations" },
];

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
  const [threshold, setThreshold] = useState(0.6);
  const [highlight, setHighlight] = useState<string | null>(null);
  const [runCount, setRunCount] = useState(0);
  const [activeTraceId, setActiveTraceId] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    let active = true;
    getHealth()
      .then((h) => {
        if (active && typeof h.grader_threshold === "number") {
          setThreshold(h.grader_threshold);
        }
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  const generation = steps.find((s) => s.action === "generation");
  const pipelineSteps = steps.filter((s) => s.action !== "generation");

  async function run() {
    setRunning(true);
    setSteps([]);
    setFinal(null);
    setError(null);
    setActiveTraceId(null);
    setRunCount((c) => c + 1);
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

  function highlightChunk(chunkId: string | null) {
    setHighlight(chunkId);
    if (!chunkId) return;
    requestAnimationFrame(() => {
      document
        .getElementById(`chunk-${CSS.escape(chunkId)}`)
        ?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
  }

  async function loadTrace(id: string) {
    setError(null);
    try {
      const trace = await getTrace(id);
      setActiveTraceId(id);
      setSteps(trace.steps);
      setFinal(trace);
      setQuery(trace.query);
      setStrategy(trace.strategy);
      setCorrection(trace.correction_enabled);
      setHighlight(null);
    } catch (e) {
      setError((e as Error).message);
    }
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
            {pipelineSteps.map((step, i) => (
              <TraceStep
                key={step.step_number}
                step={step}
                index={i}
                threshold={threshold}
                onCitation={highlightChunk}
                highlightedChunk={highlight}
              />
            ))}
            {running && <Skeleton className="h-24 w-full rounded-lg" />}
            {!running && steps.length === 0 && !error && (
              <ul className="space-y-2 rounded-lg border border-border/60 p-3">
                {IDLE_STAGES.map((stage, i) => {
                  const Icon = STAGE_META[stage.key].icon;
                  return (
                    <li key={stage.key} className="flex items-start gap-3">
                      <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-secondary text-xs">
                        {i + 1}
                      </span>
                      <span className="flex items-start gap-2">
                        <Icon
                          className="mt-0.5 h-4 w-4 text-muted-foreground"
                          aria-hidden
                        />
                        <span>
                          <span className="block text-sm font-medium">
                            {stage.title}
                          </span>
                          <span className="block text-xs text-muted-foreground">
                            {stage.body}
                          </span>
                        </span>
                      </span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
          <div className="mt-6">
            <TraceHistory
              onSelect={loadTrace}
              refreshKey={runCount}
              activeId={activeTraceId}
            />
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
                  onCitation={highlightChunk}
                />
              ) : final && final.final_status !== "success" ? (
                <FallbackView final={final} highlight={highlight} />
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
      <Badge
        variant={tone}
        className={
          final.final_status === "success"
            ? "shadow-[0_0_10px] shadow-emerald-500/30"
            : ""
        }
      >
        {final.final_status}
      </Badge>
      <span className="font-mono text-muted-foreground">
        {final.total_latency_ms} ms · retries {final.retries}
      </span>
    </div>
  );
}

const FALLBACK_LABELS: Record<string, string> = {
  grader_error: "the grader could not be reached",
  low_score: "the grader scored the retrieved chunks too low",
  simple_low_score: "a simple query graded too low to answer from",
  retries_exhausted: "retries were exhausted without a confident score",
  correction_disabled: "self-correction was off and the first grade was low",
  hyde_failed: "the HyDE rewrite could not be generated",
  no_citations: "the answer cited nothing in the retrieved chunks",
};

function FallbackView({
  final,
  highlight,
}: {
  final: Trace;
  highlight: string | null;
}) {
  const reason = final.fallback_reason ? FALLBACK_LABELS[final.fallback_reason] : null;
  return (
    <div className="space-y-3">
      <p className="text-muted-foreground">
        {final.fallback_message ?? final.error ?? "No confident answer found."}
      </p>
      {(reason || final.error) && (
        <p className="text-xs text-muted-foreground/80">
          <span className="font-medium text-foreground">Why: </span>
          {reason ?? final.error}
        </p>
      )}
      <div className="space-y-2">
        {final.closest_chunks?.map((chunk) => (
          <ChunkCard
            key={chunk.chunk_id}
            chunk={chunk}
            highlighted={highlight === chunk.chunk_id}
          />
        ))}
      </div>
    </div>
  );
}
