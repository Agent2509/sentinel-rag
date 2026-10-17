"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { DarkModeToggle } from "@/components/dark-mode-toggle";
import { getHealth, getTraces } from "@/lib/api";
import type { Health, TraceSummary } from "@/lib/types";

const WORKSPACES = [
  { href: "/", label: "Ask" },
  { href: "/strategy", label: "Compare" },
] as const;

const STATUS: Record<string, string> = {
  success: "bg-foreground",
  not_found: "bg-[#8a6a2f] dark:bg-[#d9a441]",
  error: "bg-destructive",
  cancelled: "bg-muted-foreground",
};

function clock(iso: string) {
  return new Date(iso).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [health, setHealth] = useState<Health | null>(null);
  const [down, setDown] = useState(false);
  const [traces, setTraces] = useState<TraceSummary[] | null>(null);
  const [activeTrace, setActiveTrace] = useState<string | null>(null);
  const [sheet, setSheet] = useState(false);

  useEffect(() => {
    let active = true;
    const poll = () =>
      getHealth()
        .then((h) => {
          if (active) {
            setHealth(h);
            setDown(false);
          }
        })
        .catch(() => {
          if (active) {
            setHealth(null);
            setDown(true);
          }
        });
    poll();
    const id = setInterval(poll, 15000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    let active = true;
    const load = () =>
      getTraces(10)
        .then((t) => {
          if (active) setTraces(t);
        })
        .catch(() => {});
    load();
    const refresh = () => load();
    const onActive = (e: Event) => {
      setActiveTrace((e as CustomEvent<string | null>).detail ?? null);
    };
    window.addEventListener("sentinel:trace", refresh);
    window.addEventListener("sentinel:active-trace", onActive);
    const id = setInterval(refresh, 30000);
    return () => {
      active = false;
      clearInterval(id);
      window.removeEventListener("sentinel:trace", refresh);
      window.removeEventListener("sentinel:active-trace", onActive);
    };
  }, [pathname]);

  const healthy = !down && !!health && health.status === "ok" && health.indexes_ok;
  const docs = health?.corpus_size ?? null;
  const currentTrace = pathname === "/" ? activeTrace : null;

  const linkClass = (active: boolean) =>
    `block border-l-2 py-1.5 pl-3 text-sm transition-colors ${
      active
        ? "border-l-destructive text-foreground"
        : "border-l-transparent text-muted-foreground hover:text-foreground"
    }`;

  const recentList = (onPick?: () => void) => (
    <>
      {traces === null && (
        <p className="px-4 py-1 text-xs text-muted-foreground">loading…</p>
      )}
      {traces?.length === 0 && (
        <p className="px-4 py-1 text-xs text-muted-foreground">
          A question starts a trace.
        </p>
      )}
      {traces?.map((t) => (
        <Link
          key={t.id}
          href={`/?trace=${t.id}`}
          onClick={() => {
            setActiveTrace(t.id);
            onPick?.();
          }}
          aria-current={currentTrace === t.id ? "true" : undefined}
          className={`block border-b border-border/60 px-4 py-2 transition-colors last:border-0 ${
            currentTrace === t.id ? "bg-secondary" : "hover:bg-secondary/60"
          }`}
        >
          <span className="flex items-center gap-2">
            <span
              aria-hidden
              className={`h-1.5 w-1.5 shrink-0 ${STATUS[t.final_status] ?? "bg-muted-foreground"}`}
            />
            <span className="min-w-0 flex-1 truncate text-xs leading-snug">
              {t.query}
            </span>
          </span>
          <span className="mt-1 flex items-center gap-3 pl-3.5 text-[11px] text-muted-foreground">
            <span>{t.strategy}</span>
            <span className="font-mono">{t.latency_ms} ms</span>
            <span className="ml-auto font-mono">{clock(t.timestamp)}</span>
          </span>
        </Link>
      ))}
    </>
  );

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[14rem_minmax(0,1fr)]">
      <aside className="sticky top-0 hidden h-screen flex-col border-r border-border bg-background px-4 py-6 lg:flex">
        <Link href="/" className="flex items-baseline gap-2 px-1">
          <span aria-hidden className="mb-[3px] h-2 w-2 bg-destructive" />
          <span className="font-display text-xl leading-none tracking-tight">
            Sentinel RAG
          </span>
        </Link>

        <nav className="mt-7 space-y-0.5" aria-label="Main">
          {WORKSPACES.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={pathname === item.href ? "page" : undefined}
              className={linkClass(pathname === item.href)}
            >
              {item.label}
            </Link>
          ))}
          <Link
            href="/documents"
            aria-current={pathname === "/documents" ? "page" : undefined}
            className={`${linkClass(pathname === "/documents")} flex items-center`}
          >
            Documents
            <span
              className={`ml-auto font-mono text-[11px] ${
                docs === 0 ? "text-destructive" : "text-muted-foreground"
              }`}
            >
              {docs ?? "—"}
            </span>
          </Link>
        </nav>

        <div className="mt-8 flex min-h-0 flex-1 flex-col">
          <p className="mb-2 px-1 font-serif text-xs italic text-muted-foreground">
            Recent
          </p>
          <div className="-mx-4 min-h-0 flex-1 overflow-y-auto [scrollbar-width:thin]">
            {recentList()}
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-border pt-4">
          <span className="flex items-center gap-2 text-xs text-muted-foreground">
            <span
              aria-hidden
              className={`h-1.5 w-1.5 ${
                down ? "bg-destructive" : healthy ? "bg-foreground" : "bg-[#8a6a2f]"
              }`}
            />
            {down ? "backend down" : healthy ? "ok" : "degraded"}
          </span>
          <span className="flex items-center gap-3">
            {docs !== null && (
              <span className="font-mono text-[11px] text-muted-foreground">
                {docs} doc{docs === 1 ? "" : "s"}
              </span>
            )}
            <DarkModeToggle />
          </span>
        </div>
      </aside>

      <div className="flex min-w-0 flex-col">
        <header className="sticky top-0 z-20 border-b border-border bg-background lg:hidden">
          <div className="flex h-14 items-center gap-4 px-4">
            <Link href="/" className="flex shrink-0 items-baseline gap-2">
              <span aria-hidden className="mb-[2px] h-2 w-2 bg-destructive" />
              <span className="font-display text-lg leading-none tracking-tight">
                Sentinel
              </span>
            </Link>
            <nav className="ml-1 flex items-center gap-4 overflow-x-auto [scrollbar-width:none]">
              {WORKSPACES.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={pathname === item.href ? "page" : undefined}
                  className={`shrink-0 py-1 text-sm ${
                    pathname === item.href
                      ? "text-foreground"
                      : "text-muted-foreground"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
              <Link
                href="/documents"
                className={`shrink-0 py-1 text-sm ${
                  pathname === "/documents"
                    ? "text-foreground"
                    : "text-muted-foreground"
                }`}
              >
                Documents
              </Link>
              <button
                type="button"
                onClick={() => setSheet(true)}
                className="shrink-0 py-1 text-sm text-muted-foreground"
              >
                Recent
              </button>
            </nav>
            <span
              aria-hidden
              className={`ml-auto h-1.5 w-1.5 shrink-0 ${
                down ? "bg-destructive" : healthy ? "bg-foreground" : "bg-[#8a6a2f]"
              }`}
            />
          </div>
        </header>
        <main className="flex-1">{children}</main>
      </div>

      {sheet && (
        <div className="fixed inset-0 z-50 flex flex-col bg-background lg:hidden">
          <div className="flex h-14 items-center justify-between border-b border-border px-4">
            <span className="font-display text-lg">Recent</span>
            <button
              type="button"
              onClick={() => setSheet(false)}
              aria-label="Close recent traces"
              className="p-1 text-muted-foreground"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto">{recentList(() => setSheet(false))}</div>
        </div>
      )}
    </div>
  );
}
