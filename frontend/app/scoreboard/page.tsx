"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ScoreBar } from "@/components/score-chart";
import { getEval } from "@/lib/api";
import type { EvalRow } from "@/lib/types";

const METRICS: { key: keyof EvalRow; label: string }[] = [
  { key: "faithfulness", label: "Faithfulness" },
  { key: "answer_relevancy", label: "Answer relevancy" },
  { key: "context_precision", label: "Context precision" },
  { key: "context_recall", label: "Context recall" },
];

interface Group {
  strategy: string;
  correction: number;
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
    (map.get(key) ?? map.set(key, []).get(key)!).push(row);
  }
  return [...map.values()].map((rs) => ({
    strategy: rs[0].strategy,
    correction: rs[0].correction_enabled,
    n: rs.length,
    metrics: Object.fromEntries([
      ...METRICS.map((m) => [
        m.key as string,
        mean(rs.map((r) => r[m.key] as number | null)),
      ]),
      ["latency_ms", mean(rs.map((r) => r.latency_ms))],
    ]),
  }));
}

export default function Scoreboard() {
  const [rows, setRows] = useState<EvalRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getEval()
      .then((data) => active && setRows(data))
      .catch((e) => active && setError((e as Error).message));
    return () => {
      active = false;
    };
  }, []);

  const groups = rows ? group(rows) : [];
  const maxLatency = Math.max(
    1,
    ...groups.map((g) => (g.metrics.latency_ms as number | null) ?? 0),
  );

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <h1 className="mb-1 text-lg font-semibold">Scoreboard</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        RAGAS metrics per chunking strategy (averaged over the evaluation set).
        {rows && rows.length > 0 && rows[0].corpus_version && (
          <span className="ml-1 font-mono text-xs">
            corpus v{rows[0].corpus_version}
          </span>
        )}
      </p>

      {error && <p className="text-sm text-destructive">{error}</p>}

      {rows === null && !error && (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-52 rounded-lg" />
          <Skeleton className="h-52 rounded-lg" />
        </div>
      )}

      {rows !== null && rows.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-sm text-muted-foreground">
            No evaluation rows yet. Run the eval on the backend:
            <code className="ml-1 rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
              .venv-eval/bin/python -m eval.run_ragas
            </code>
          </CardContent>
        </Card>
      )}

      {groups.length > 0 && (
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
                    key={m.key as string}
                    label={m.label}
                    value={g.metrics[m.key as string]}
                  />
                ))}
                <ScoreBar
                  label="Latency"
                  value={g.metrics.latency_ms as number | null}
                  suffix=" ms"
                  max={maxLatency}
                />
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
