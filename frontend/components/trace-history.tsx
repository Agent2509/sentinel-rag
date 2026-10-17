"use client";

import { useEffect, useState } from "react";
import { History } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getTraces } from "@/lib/api";
import type { TraceSummary } from "@/lib/types";

function statusTone(status: string) {
  return status === "success"
    ? "default"
    : status === "not_found"
      ? "secondary"
      : "destructive";
}

export function TraceHistory({
  onSelect,
  refreshKey,
  activeId,
}: {
  onSelect: (id: string) => void;
  refreshKey: number;
  activeId?: string | null;
}) {
  const [traces, setTraces] = useState<TraceSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getTraces(20)
      .then((t) => {
        if (active) {
          setTraces(t);
          setError(null);
        }
      })
      .catch((e) => {
        if (active) setError((e as Error).message);
      });
    return () => {
      active = false;
    };
  }, [refreshKey]);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-sm">
          <History className="h-4 w-4 text-muted-foreground" aria-hidden />
          Recent traces
          {traces && <Badge variant="secondary">{traces.length}</Badge>}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && <p className="text-xs text-destructive">{error}</p>}
        {!traces && !error && (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        )}
        {traces && traces.length === 0 && (
          <p className="text-xs text-muted-foreground">
            Every run is stored here. Run a query, then come back to it later —
            no need to re-ask.
          </p>
        )}
        {traces && traces.length > 0 && (
          <ul className="-m-2 space-y-0.5">
            {traces.map((t) => (
              <li key={t.id}>
                <button
                  type="button"
                  onClick={() => onSelect(t.id)}
                  aria-current={activeId === t.id}
                  className={`w-full rounded-md px-2 py-1.5 text-left transition-colors hover:bg-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                    activeId === t.id ? "bg-muted" : ""
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <Badge
                      variant={statusTone(t.final_status)}
                      className="text-[10px]"
                    >
                      {t.final_status}
                    </Badge>
                    <span className="truncate text-sm">{t.query}</span>
                  </span>
                  <span className="mt-1 flex items-center gap-2 text-[11px] text-muted-foreground">
                    <span>{t.strategy}</span>
                    <span>{t.correction_enabled ? "correction" : "raw"}</span>
                    <span className="font-mono">{t.latency_ms} ms</span>
                    <span className="ml-auto font-mono">
                      {t.timestamp.slice(11, 19)}
                    </span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
