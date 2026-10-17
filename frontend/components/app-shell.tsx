"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  FileText,
  GitCompareArrows,
  History,
  MessageSquareText,
  ShieldCheck,
} from "lucide-react";
import { DarkModeToggle } from "@/components/dark-mode-toggle";
import { getHealth, getTraces } from "@/lib/api";
import type { Health, TraceSummary } from "@/lib/types";

const WORKSPACES = [
  { href: "/", label: "Ask", icon: MessageSquareText },
  { href: "/strategy", label: "Compare", icon: GitCompareArrows },
] as const;

const STATUS_DOT: Record<string, string> = {
  success: "bg-emerald-400",
  not_found: "bg-amber-400",
  error: "bg-red-400",
  cancelled: "bg-muted-foreground",
};

function time(iso: string) {
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
    window.addEventListener("sentinel:trace", refresh);
    const id = setInterval(refresh, 30000);
    return () => {
      active = false;
      clearInterval(id);
      window.removeEventListener("sentinel:trace", refresh);
    };
  }, [pathname]);

  const healthy = !down && !!health && health.status === "ok" && health.indexes_ok;
  const dot = down ? "bg-red-500" : healthy ? "bg-emerald-500" : "bg-amber-500";
  const docs = health?.corpus_size ?? null;

  const workspaceLinks = (compact = false) =>
    WORKSPACES.map((item) => {
      const active = pathname === item.href;
      const Icon = item.icon;
      return (
        <Link
          key={item.href}
          href={item.href}
          aria-current={active ? "page" : undefined}
          className={
            compact
              ? `shrink-0 rounded-md px-2.5 py-1.5 text-sm transition-colors ${
                  active
                    ? "bg-primary/10 text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`
              : `flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors ${
                  active
                    ? "bg-primary/10 text-foreground"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                }`
          }
        >
          {!compact && <Icon className="h-4 w-4" aria-hidden />}
          {item.label}
        </Link>
      );
    });

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[16rem_minmax(0,1fr)]">
      <aside className="sticky top-0 hidden h-screen flex-col gap-6 border-r border-border/60 bg-background/40 px-3 py-5 backdrop-blur-xl lg:flex">
        <Link href="/" className="flex items-center gap-2 px-2">
          <ShieldCheck className="h-5 w-5 text-emerald-500" aria-hidden />
          <span className="font-display text-lg tracking-tight">Sentinel RAG</span>
        </Link>

        <nav className="space-y-1" aria-label="Main">
          <p className="px-2 pb-1 text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground/70">
            Workspace
          </p>
          {workspaceLinks()}
          <Link
            href="/documents"
            aria-current={pathname === "/documents" ? "page" : undefined}
            className={`flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors ${
              pathname === "/documents"
                ? "bg-primary/10 text-foreground"
                : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
            }`}
          >
            <FileText className="h-4 w-4" aria-hidden />
            Documents
            <span
              className={`ml-auto rounded-full px-1.5 py-0.5 font-mono text-[10px] ${
                docs === 0
                  ? "bg-amber-500/15 text-amber-500"
                  : "bg-secondary text-muted-foreground"
              }`}
            >
              {docs ?? "—"}
            </span>
          </Link>
        </nav>

        <div className="flex min-h-0 flex-1 flex-col">
          <p className="flex items-center gap-1.5 px-2 pb-1 text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground/70">
            <History className="h-3 w-3" aria-hidden /> Recent
          </p>
          <div className="-mx-1 min-h-0 flex-1 overflow-y-auto px-1 [scrollbar-width:thin]">
            {traces === null && (
              <p className="px-2 py-1 text-xs text-muted-foreground">loading…</p>
            )}
            {traces?.length === 0 && (
              <p className="px-2 py-1 text-xs text-muted-foreground">
                Ask a question to start a trace.
              </p>
            )}
            {traces?.map((t) => (
              <Link
                key={t.id}
                href={`/?trace=${t.id}`}
                className="block rounded-md px-2 py-1.5 transition-colors hover:bg-muted/60"
              >
                <span className="flex items-center gap-2">
                  <span
                    aria-hidden
                    className={`h-1.5 w-1.5 shrink-0 rounded-full ${STATUS_DOT[t.final_status] ?? "bg-muted-foreground"}`}
                  />
                  <span className="min-w-0 flex-1 truncate text-xs">{t.query}</span>
                </span>
                <span className="mt-0.5 flex items-center gap-2 pl-3.5 text-[10px] text-muted-foreground">
                  <span>{t.strategy}</span>
                  <span className="font-mono">{t.latency_ms} ms</span>
                  <span className="ml-auto font-mono">{time(t.timestamp)}</span>
                </span>
              </Link>
            ))}
          </div>
        </div>

        <div className="mt-auto flex items-center justify-between border-t border-border/60 px-1 pt-4">
          <span className="flex items-center gap-2 text-xs text-muted-foreground">
            <span aria-hidden className={`h-2 w-2 rounded-full ${dot}`} />
            {down ? "backend down" : healthy ? "ok" : "degraded"}
            {docs !== null && (
              <span className="font-mono text-[10px] text-muted-foreground/70">
                · {docs} doc{docs === 1 ? "" : "s"}
              </span>
            )}
          </span>
          <DarkModeToggle />
        </div>
      </aside>

      <div className="flex min-w-0 flex-col">
        <header className="sticky top-0 z-20 border-b border-border/60 bg-background/70 backdrop-blur-xl lg:hidden">
          <div className="flex h-14 items-center gap-3 px-4">
            <Link href="/" className="flex shrink-0 items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-emerald-500" aria-hidden />
              <span className="hidden font-display text-lg tracking-tight sm:inline">
                Sentinel RAG
              </span>
            </Link>
            <nav className="ml-1 flex items-center gap-1 overflow-x-auto [scrollbar-width:none]">
              {workspaceLinks(true)}
              <Link
                href="/documents"
                aria-current={pathname === "/documents" ? "page" : undefined}
                className={`shrink-0 rounded-md px-2.5 py-1.5 text-sm transition-colors ${
                  pathname === "/documents"
                    ? "bg-primary/10 text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Documents
              </Link>
            </nav>
            <span
              aria-hidden
              className={`ml-auto h-2 w-2 shrink-0 rounded-full ${dot}`}
            />
          </div>
        </header>
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
