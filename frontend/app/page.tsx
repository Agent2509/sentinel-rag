"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  FileText,
  Loader2,
  MessageSquareText,
  Play,
  Square,
  TriangleAlert,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { STAGE_ACCENT, STAGE_META, TraceStep } from "@/components/trace-step";
import { PageHeader } from "@/components/page-header";
import { AnswerPanel } from "@/components/answer-panel";
import { ChunkCard } from "@/components/chunk-card";
import { StrategySelector } from "@/components/strategy-selector";
import { useQueryStream } from "@/hooks/use-query-stream";
import { getHealth, getTrace } from "@/lib/api";
import { fallbackLabel } from "@/lib/fallback";
import type { Strategy, Trace } from "@/lib/types";

const IDLE_STAGES = [
  { key: "routing", title: "Route", body: "an LLM labels the query simple or complex" },
  { key: "retrieval", title: "Retrieve", body: "BM25 + vector search, fused by RRF" },
  { key: "grading", title: "Grade", body: "an LLM scores whether the chunks can answer it" },
  { key: "hyde_rewrite", title: "Retry", body: "a low score triggers a HyDE rewrite" },
  { key: "generation", title: "Answer", body: "grounded generation with citations" },
];

function AskView() {
  const router = useRouter();
  const traceId = useSearchParams().get("trace");

  const [query, setQuery] = useState("");
  const [strategy, setStrategy] = useState<Strategy>("semantic");
  const [correction, setCorrection] = useState(true);
  const [threshold, setThreshold] = useState<number | null>(null);
  const [corpusSize, setCorpusSize] = useState<number | null>(null);
  const [highlight, setHighlight] = useState<string | null>(null);
  const { steps, final, running, error, run, cancel, load, setError } =
    useQueryStream();

  useEffect(() => {
    let active = true;
    getHealth()
      .then((h) => {
        if (!active) return;
        if (typeof h.grader_threshold === "number") setThreshold(h.grader_threshold);
        setCorpusSize(h.corpus_size);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  // A sidebar history link arrives as /?trace=<id>: load it into the same panel.
  useEffect(() => {
    if (!traceId) {
      window.dispatchEvent(
        new CustomEvent("sentinel:active-trace", { detail: null }),
      );
      return;
    }
    let active = true;
    getTrace(traceId)
      .then((trace) => {
        if (!active) return;
        load(trace);
        setQuery(trace.query);
        setStrategy(trace.strategy);
        setCorrection(trace.correction_enabled);
        setHighlight(null);
        window.dispatchEvent(
          new CustomEvent("sentinel:active-trace", { detail: traceId }),
        );
      })
      .catch((e) => {
        if (active) setError((e as Error).message);
      });
    return () => {
      active = false;
    };
  }, [traceId, load, setError]);

  const generation = steps.find((s) => s.action === "generation");
  const pipelineSteps = steps.filter((s) => s.action !== "generation");
  const emptyCorpus = corpusSize === 0;

  async function runQuery() {
    if (traceId) router.replace("/");
    window.dispatchEvent(new CustomEvent("sentinel:active-trace", { detail: null }));
    try {
      await run({ query, strategy, correction_enabled: correction });
    } finally {
      window.dispatchEvent(new Event("sentinel:trace"));
    }
  }

  function highlightChunk(chunkId: string | null) {
    setHighlight(chunkId);
    if (!chunkId) return;
    requestAnimationFrame(() => {
      // data-chunk-id is not unique in the DOM (retrieval + fallback render the
      // same chunk); the first match is the retrieval card, which is the target.
      document
        .querySelector(`[data-chunk-id="${CSS.escape(chunkId)}"]`)
        ?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <PageHeader
        title="Ask"
        description="Ask your corpus and watch the pipeline route, retrieve, grade and answer — with citations you can click."
      />

      {emptyCorpus ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-16 text-center">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
              <FileText className="h-5 w-5" aria-hidden />
            </span>
            <div>
              <p className="font-display text-xl">No documents yet</p>
              <p className="mx-auto mt-1 max-w-md text-sm text-muted-foreground">
                Add markdown, text or PDF files first, then ask questions and
                watch retrieval, grading and self-correction step by step.
              </p>
            </div>
            <Link
              href="/documents"
              className="mt-1 inline-flex h-9 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              <FileText className="h-4 w-4" aria-hidden /> Add documents
            </Link>
          </CardContent>
        </Card>
      ) : (
        <>
          <Card className="mb-6">
            <CardContent className="pt-5">
              <form
                className="flex flex-col gap-3"
                onSubmit={(e) => {
                  e.preventDefault();
                  if (!running) runQuery();
                }}
              >
                <div className="flex flex-col gap-2 sm:flex-row">
                  <input
                    aria-label="Query"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    maxLength={2000}
                    placeholder="Ask something about your documents…"
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
            <div
              role="alert"
              className="mb-4 flex items-center gap-2 rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm"
            >
              <TriangleAlert className="h-4 w-4 text-destructive" aria-hidden />
              {error}
            </div>
          )}

          <div className="grid gap-6 lg:grid-cols-2">
            <section aria-label="Pipeline steps" className="min-w-0">
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
                  // Same accent rails as the live steps: the preview and the run
                  // read as one design, not two.
                  <Card>
                    <CardContent className="space-y-1">
                      {IDLE_STAGES.map((stage, i) => {
                        const Icon = STAGE_META[stage.key].icon;
                        return (
                          <div
                            key={stage.key}
                            className={`flex items-start gap-3 rounded-md border-l-2 py-2 pl-3 ${
                              STAGE_ACCENT[stage.key] ?? "border-l-border"
                            }`}
                          >
                            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-secondary font-mono text-xs">
                              {i + 1}
                            </span>
                            <Icon
                              className="mt-1 h-4 w-4 shrink-0 text-muted-foreground"
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
                          </div>
                        );
                      })}
                    </CardContent>
                  </Card>
                )}
              </div>
            </section>

            <section
              aria-label="Answer"
              className="min-w-0 lg:sticky lg:top-8 lg:self-start"
            >
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">
                Answer
              </h2>
              {final && <StatusBanner final={final} />}
              <Card
                className={
                  final?.final_status === "success"
                    ? "shadow-[0_0_60px_-24px] shadow-primary/50"
                    : ""
                }
              >
                <CardContent className="pt-6">
                  {generation?.answer ? (
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
                    <div className="flex flex-col items-center gap-2 py-10 text-center">
                      <MessageSquareText
                        className="h-6 w-6 text-muted-foreground/60"
                        aria-hidden
                      />
                      <p className="max-w-xs text-sm text-muted-foreground">
                        {corpusSize !== null && corpusSize <= 1
                          ? "One document is indexed. Ask about it, or add more on Documents."
                          : "Ask anything about your documents to see the grounded answer and citations."}
                      </p>
                      {corpusSize !== null && corpusSize <= 1 && (
                        <Link
                          href="/documents"
                          className="text-xs text-primary underline underline-offset-2"
                        >
                          Manage documents
                        </Link>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </section>
          </div>
        </>
      )}
    </div>
  );
}

export default function AskPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-muted-foreground">
          Loading…
        </div>
      }
    >
      <AskView />
    </Suspense>
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

function FallbackView({
  final,
  highlight,
}: {
  final: Trace;
  highlight: string | null;
}) {
  const reason = fallbackLabel(final.fallback_reason);
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
