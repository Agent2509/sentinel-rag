import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Step, Trace } from "@/lib/types";

const api = vi.hoisted(() => ({ streamQuery: vi.fn() }));
vi.mock("@/lib/api", () => ({ streamQuery: api.streamQuery }));

import { useQueryStream } from "./use-query-stream";

const STEP: Step = { step_number: 1, action: "routing", duration_ms: 5 };
const TRACE: Trace = {
  trace_id: "t1",
  timestamp: "2026-01-01T00:00:00Z",
  query: "q",
  strategy: "fixed",
  correction_enabled: false,
  steps: [STEP],
  final_status: "success",
  total_latency_ms: 10,
  retries: 0,
};

const body = { query: "q", strategy: "fixed" as const, correction_enabled: false };

beforeEach(() => {
  api.streamQuery.mockReset();
});

describe("useQueryStream", () => {
  it("appends streamed steps and keeps the final trace", async () => {
    api.streamQuery.mockImplementation(async (_b, onEvent) => {
      onEvent({ type: "step", trace_id: "t1", step: STEP });
      onEvent({ type: "final", trace_id: "t1", trace: TRACE });
    });
    const { result } = renderHook(() => useQueryStream());

    await act(async () => {
      await result.current.run(body);
    });

    expect(result.current.steps).toEqual([STEP]);
    expect(result.current.final?.trace_id).toBe("t1");
    expect(result.current.running).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("aborts a running stream when a stored trace is loaded", () => {
    let signal: AbortSignal | undefined;
    api.streamQuery.mockImplementation(
      (_b, _o, s: AbortSignal) =>
        new Promise((_, reject) => {
          signal = s;
          s.addEventListener("abort", () =>
            reject(Object.assign(new Error("aborted"), { name: "AbortError" })),
          );
        }),
    );
    const { result } = renderHook(() => useQueryStream());

    act(() => {
      void result.current.run(body);
    });
    expect(result.current.running).toBe(true);

    act(() => result.current.load(TRACE));

    expect(signal?.aborted).toBe(true);
    expect(result.current.final?.trace_id).toBe("t1");
    expect(result.current.running).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("reset clears a loaded trace", () => {
    const { result } = renderHook(() => useQueryStream());
    act(() => result.current.load(TRACE));
    expect(result.current.steps).toHaveLength(1);

    act(() => result.current.reset());

    expect(result.current.steps).toEqual([]);
    expect(result.current.final).toBeNull();
    expect(result.current.running).toBe(false);
  });
});
