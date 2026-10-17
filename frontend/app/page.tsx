"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, Play, Square, TriangleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { TraceStep } from "@/components/trace-step";
import { TraceTimeline } from "@/components/trace-timeline";
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
    <div className="mx-auto max-w-6xl px-6 py-10">
      <PageHeader
        title="Ask"
        description="Ask your corpus and watch the pipeline route, retrieve, grade and answer — every step is timed and every claim is footnoted."
      />

      {emptyCorpus ? (
        <div className="border-y border-border py-16 text-center">
          <p className="font-display text-2xl">No documents yet</p>
          <p className="mx-auto mt-2 max-w-md text-[15px] leading-relaxed text-muted-foreground">
            Add markdown, text or PDF files first. Then ask a question and watch
            retrieval, grading and self-correction step by step.
          </p>
          <Link
            href="/documents"
            className="mt-6 inline-flex h-9 items-center rounded-[2px] bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Add documents
          </Link>
        </div>
      ) : (
        <>
          <form
            className="border-y border-border py-4"
            onSubmit={(e) => {
              e.preventDefault();
              if (!running) runQuery();
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
              {running ? (
                <Button type="button" variant="secondary" onClick={cancel}>
                  <Square className="h-4 w-4" /> Cancel
                </Button>
              ) : (
                <Button
                  type="submit"
                  disabled={!query.trim()}
                  className="disabled:bg-transparent disabled:text-muted-foreground disabled:opacity-100 disabled:ring-1 disabled:ring-border"
                >
                  <Play className="h-4 w-4" /> Run
                </Button>
              )}
            </div>
            <div className="mt-3 border-t border-border/60 pt-3">
              <StrategySelector
                strategy={strategy}
                onStrategy={setStrategy}
                correction={correction}
                onCorrection={setCorrection}
                disabled={running}
              />
            </div>
          </form>

          <TraceTimeline steps={steps} running={running} />

          {error && (
            <div
              role="alert"
              className="mt-4 flex items-center gap-2 border-l-2 border-l-destructive py-2 pl-3 text-sm text-destructive"
            >
              <TriangleAlert className="h-4 w-4" aria-hidden />
              {error}
            </div>
          )}

          <div className="mt-8 grid gap-10 lg:grid-cols-[minmax(0,1fr)_26rem]">
            <section aria-label="Pipeline steps" className="min-w-0">
              <h2 className="font-serif text-xs italic text-muted-foreground">
                Pipeline
              </h2>
              <div className="mt-2" aria-live="polite">
                {pipelineSteps.map((step) => (
                  <TraceStep
                    key={step.step_number}
                    step={step}
                    threshold={threshold}
                    onCitation={highlightChunk}
                    highlightedChunk={highlight}
                  />
                ))}
                {running && (
                  <Skeleton className="mt-4 h-16 w-full rounded-none" />
                )}
                {!running && steps.length === 0 && !error && (
                  <div>
                    {IDLE_STAGES.map((stage) => (
                      <div
                        key={stage.key}
                        className="flex items-baseline gap-4 border-t border-border/70 py-2.5"
                      >
                        <span className="w-full text-[13px] font-medium">
                          {stage.title}
                        </span>
                        <span className="w-full text-[12px] leading-relaxed text-muted-foreground">
                          {stage.body}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

            <section
              aria-label="Answer"
              className="min-w-0 lg:sticky lg:top-8 lg:self-start"
            >
              <h2 className="font-serif text-xs italic text-muted-foreground">
                Answer
              </h2>
              <div className="mt-2 border-t border-border pt-4">
                {final && <StatusLine final={final} />}
                {generation?.answer ? (
                  <AnswerPanel
                    answer={generation.answer}
                    citations={generation.citations}
                    onCitation={highlightChunk}
                  />
                ) : final && final.final_status !== "success" ? (
                  <FallbackView final={final} highlight={highlight} />
                ) : running ? (
                  <p className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" /> working…
                  </p>
                ) : (
                  <div className="py-6">
                    <p className="font-serif text-[15px] italic leading-relaxed text-muted-foreground">
                      {corpusSize !== null && corpusSize <= 1
                        ? "One document is indexed. Ask about it, or add more on Documents."
                        : "Ask anything about your documents; the answer will cite the passages it used."}
                    </p>
                    {corpusSize !== null && corpusSize <= 1 && (
                      <Link
                        href="/documents"
                        className="mt-3 inline-block text-xs text-destructive underline underline-offset-2"
                      >
                        Manage documents
                      </Link>
                    )}
                  </div>
                )}
              </div>
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
        <div className="mx-auto max-w-6xl px-6 py-10 text-sm text-muted-foreground">
          Loading…
        </div>
      }
    >
      <AskView />
    </Suspense>
  );
}

function StatusLine({ final }: { final: Trace }) {
  return (
    <p className="mb-4 flex items-baseline gap-3 text-[11px]">
      <span
        className={
          final.final_status === "success"
            ? "text-foreground"
            : final.final_status === "not_found"
              ? "text-[#8a6a2f] dark:text-[#d9a441]"
              : "text-destructive"
        }
      >
        {final.final_status}
      </span>
      <span className="font-mono text-muted-foreground">
        {final.total_latency_ms} ms
      </span>
      <span className="text-muted-foreground">
        {final.retries === 0 ? "no retries" : `${final.retries} retries`}
      </span>
    </p>
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
      <p className="font-serif text-[15px] leading-relaxed text-muted-foreground">
        {final.fallback_message ?? final.error ?? "No confident answer found."}
      </p>
      {(reason || final.error) && (
        <p className="text-xs text-muted-foreground/80">
          <span className="font-medium text-foreground">Why: </span>
          {reason ?? final.error}
        </p>
      )}
      <div>
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
