"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { streamQuery, type QueryBody } from "@/lib/api";
import type { Step, Trace } from "@/lib/types";

/**
 * One query stream: run/cancel, live steps, final trace, error state.
 * Aborts the stream if the component unmounts mid-run.
 */
export function useQueryStream() {
  const [steps, setSteps] = useState<Step[]>([]);
  const [final, setFinal] = useState<Trace | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => () => abortRef.current?.abort(), []);

  const cancel = useCallback(() => abortRef.current?.abort(), []);

  /** Show a stored trace (from history) instead of streaming a new one. */
  const load = useCallback((trace: Trace) => {
    // a running stream would keep appending steps on top of the loaded trace
    abortRef.current?.abort();
    setSteps(trace.steps);
    setFinal(trace);
    setError(null);
    setRunning(false);
  }, []);

  /** Clear this panel so a changed selector never sits above an old result. */
  const reset = useCallback(() => {
    abortRef.current?.abort();
    setSteps([]);
    setFinal(null);
    setError(null);
    setRunning(false);
  }, []);

  const run = useCallback(async (body: QueryBody) => {
    const controller = new AbortController();
    abortRef.current = controller;
    setSteps([]);
    setFinal(null);
    setError(null);
    setRunning(true);
    try {
      await streamQuery(
        body,
        (event) => {
          if (event.type === "step") setSteps((prev) => [...prev, event.step]);
          else setFinal(event.trace);
        },
        controller.signal,
      );
    } catch (e) {
      if ((e as Error).name !== "AbortError") setError((e as Error).message);
    } finally {
      setRunning(false);
      abortRef.current = null;
    }
  }, []);

  return { steps, final, running, error, run, cancel, load, reset, setError };
}
