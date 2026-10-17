"use client";

import { useEffect, useRef, useState } from "react";
import { FlaskConical, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/page-header";
import { ScoreBar } from "@/components/score-chart";
import { getEval, getEvalStatus, runEval } from "@/lib/api";
import type { EvalRow, EvalStatus } from "@/lib/types";

type MetricKey =
  | "faithfulness"
  | "answer_relevancy"
  | "context_precision"
  | "context_recall";

const METRICS: { key: MetricKey; label: string }[] = [
  { key: "faithfulness", label: "Faithfulness" },
  { key: "answer_relevancy", label: "Answer relevancy" },
  { key: "context_precision", label: "Context precision" },
  { key: "context_recall", label: "Context recall" },
];

interface Group {
  strategy: string;
  correction: boolean;
  n: number;
  metrics: Record<string, number | null>;
}

function mean(values: (number | null)[]): number | null {
  const nums = values.filter(
    (v): v is number => typeof v === "number" && Number.isFinite(v),
  );
  return nums.length ? nums.reduce((a, b) => a + b, 0) / nums.length : null;
}

function group(rows: EvalRow[]): Group[] {
  const map = new Map<string, EvalRow[]>();
  for (const row of rows) {
    const key = `${row.strategy}|${row.correction_enabled}`;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(row);
  }
  return [...map.values()].map((rs) => {
    const metrics: Record<string, number | null> = {
      latency_ms: mean(rs.map((r) => r.latency_ms)),
    };
    for (const m of METRICS) metrics[m.key] = mean(rs.map((r) => r[m.key]));
    return {
      strategy: rs[0].strategy,
      correction: rs[0].correction_enabled,
      n: rs.length,
      metrics,
    };
  });
}

/** Top combo per metric — only meaningful once a metric has more than one combo. */
function bestPerMetric(groups: Group[]) {
  return METRICS.flatMap((m) => {
    const ranked = groups
      .map((g) => ({ group: g, value: g.metrics[m.key] }))
      .filter((r): r is { group: Group; value: number } => typeof r.value === "number")
      .sort((x, y) => y.value - x.value);
    if (ranked.length < 2) return [];
    return [
      {
        label: m.label,
        ...ranked[0],
        tied: Math.abs(ranked[1].value - ranked[0].value) < 1e-9,
      },
    ];
  });
}

export default function Scoreboard() {
  const [rows, setRows] = useState<EvalRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<EvalStatus | null>(null);
  const [starting, setStarting] = useState(false);
  const [evalError, setEvalError] = useState<string | null>(null);
  const wasRunning = useRef(false);

  useEffect(() => {
    let active = true;
    getEval()
      .then((data) => active && setRows(data))
      .catch((e) => active && setError((e as Error).message));
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    const poll = () => {
      getEvalStatus()
        .then((s) => {
          if (!active) return;
          setStatus(s);
          if (wasRunning.current && !s.running) {
            getEval()
              .then((data) => active && setRows(data))
              .catch(() => {});
          }
          wasRunning.current = s.running;
        })
        .catch(() => {});
    };
    poll();
    const id = setInterval(poll, 3000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, []);

  async function startEval() {
    setStarting(true);
    setEvalError(null);
    try {
      await runEval();
      const s = await getEvalStatus();
      setStatus(s);
      wasRunning.current = s.running;
    } catch (e) {
      setEvalError((e as Error).message);
    } finally {
      setStarting(false);
    }
  }

  const groups = rows ? group(rows) : [];
  const best = bestPerMetric(groups);
  const maxLatency = Math.max(
    1,
    ...groups.map((g) => (g.metrics.latency_ms as number | null) ?? 0),
  );

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <PageHeader
        title="Scoreboard"
        description="RAGAS metrics per chunking strategy, averaged over the evaluation set."
      >
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            onClick={startEval}
            disabled={
              starting ||
              !status ||
              status.running ||
              status.corpus_size < status.min_docs
            }
          >
            {starting || status?.running ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FlaskConical className="h-4 w-4" />
            )}
            {status?.running ? "Evaluating…" : "Evaluate corpus"}
          </Button>
          {rows && rows.length > 0 && rows[0].corpus_version && (
            <span
              className="rounded-md border border-border/60 px-2 py-1 font-mono text-[11px] text-muted-foreground"
              title={rows[0].corpus_version}
            >
              corpus v{rows[0].corpus_version.slice(0, 10)}
            </span>
          )}
        </div>
      </PageHeader>

      {status && status.corpus_size < status.min_docs && !status.running && (
        <p className="mb-4 text-xs text-muted-foreground">
          Evaluation needs at least {status.min_docs} documents; you have{" "}
          {status.corpus_size}. Add more on the Documents page.
        </p>
      )}

      {(starting || status?.running) && (
        <p
          role="status"
          className="mb-4 flex items-center gap-2 text-xs text-muted-foreground"
        >
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          {status?.stage ?? "starting"}
          {status?.message ? ` — ${status.message}` : ""}
        </p>
      )}

      {status?.stage === "done" && !status.running && status.message && (
        <p className="mb-4 text-xs text-muted-foreground">{status.message}</p>
      )}

      {status?.stage === "error" && status.error && (
        <p role="alert" className="mb-4 text-sm text-destructive">
          Evaluation failed: {status.error}
        </p>
      )}

      {evalError && (
        <p role="alert" className="mb-4 text-sm text-destructive">
          {evalError}
        </p>
      )}

      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}

      {rows === null && !error && (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-52 rounded-lg" />
          <Skeleton className="h-52 rounded-lg" />
        </div>
      )}

      {rows !== null && rows.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-sm text-muted-foreground">
            No evaluation rows yet. Click <strong>Evaluate corpus</strong> to
            generate a test set from the current documents and run the matrix, or
            run it on the backend:
            <code className="ml-1 rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
              python -m eval.run_ragas
            </code>
          </CardContent>
        </Card>
      )}

      {groups.length > 0 && (
        <>
          {best.length > 1 && (
            <div className="mb-4 flex flex-wrap items-center gap-2 text-xs">
              <span className="text-muted-foreground">Best per metric:</span>
              {best.map((b) => (
                <Badge key={b.label} variant="outline" className="gap-1.5 font-normal">
                  {b.label}
                  <span
                    className={`font-mono ${
                      b.value >= 0.8 ? "text-emerald-400" : "text-amber-400"
                    }`}
                  >
                    {b.value.toFixed(3)}
                  </span>
                  <span className="text-muted-foreground">
                    {b.tied
                      ? "tie"
                      : `${b.group.strategy} · ${b.group.correction ? "on" : "off"}`}
                  </span>
                </Badge>
              ))}
            </div>
          )}
          {groups.length < 6 && (
            <p
              role="status"
              className="mb-4 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs text-muted-foreground"
            >
              Partial matrix: {groups.length} of 6 strategy × correction combos
              measured. Re-run the evaluation to fill the rest.
            </p>
          )}
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {groups.map((g) => (
            <Card key={`${g.strategy}-${g.correction}`}>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <span>{g.strategy}</span>
                  <Badge variant={g.correction ? "default" : "secondary"}>
                    {g.correction ? "correction on" : "correction off"}
                  </Badge>
                  <span className="ml-auto text-xs font-normal text-muted-foreground">
                    n={g.n}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {METRICS.map((m) => (
                  <ScoreBar
                    key={m.key}
                    label={m.label}
                    value={g.metrics[m.key]}
                  />
                ))}
                <ScoreBar
                  label="Latency"
                  value={g.metrics.latency_ms ?? null}
                  suffix=" ms"
                  max={maxLatency}
                />
              </CardContent>
            </Card>
          ))}
          </div>
        </>
      )}
    </div>
  );
}
