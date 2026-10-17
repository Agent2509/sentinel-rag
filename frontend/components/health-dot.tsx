"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";
import type { Health } from "@/lib/types";

export function HealthDot() {
  const [health, setHealth] = useState<Health | null>(null);
  const [down, setDown] = useState(false);

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const h = await getHealth();
        if (active) {
          setHealth(h);
          setDown(false);
        }
      } catch {
        if (active) {
          setHealth(null);
          setDown(true);
        }
      }
    };
    poll();
    const id = setInterval(poll, 15000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, []);

  const ok = !down && !!health && health.indexes_ok;
  const label = down
    ? "backend unreachable"
    : health
      ? health.status
      : "checking";

  return (
    <span
      className="inline-flex items-center gap-1.5 text-xs text-muted-foreground"
      aria-live="polite"
    >
      <span
        aria-hidden
        className={`h-2 w-2 rounded-full ${ok ? "bg-emerald-500" : "bg-red-500"}`}
      />
      {label}
    </span>
  );
}
