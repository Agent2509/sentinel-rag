"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { HealthDot } from "@/components/health-dot";
import { DarkModeToggle } from "@/components/dark-mode-toggle";

const LINKS = [
  { href: "/", label: "Trace View" },
  { href: "/strategy", label: "Strategy Lab" },
  { href: "/documents", label: "Documents" },
  { href: "/scoreboard", label: "Scoreboard" },
];

export function NavBar() {
  const pathname = usePathname();

  return (
    <header className="border-b border-border/60 backdrop-blur sticky top-0 z-20 bg-background/80">
      <nav
        className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4"
        aria-label="Main"
      >
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <ShieldCheck className="h-5 w-5 text-emerald-500" aria-hidden />
          <span>Sentinel RAG</span>
        </Link>

        <div className="ml-2 flex items-center gap-1">
          {LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={`rounded-md px-3 py-1.5 text-sm transition-colors ${
                  active
                    ? "bg-secondary text-secondary-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>

        <div className="ml-auto flex items-center gap-3">
          <HealthDot />
          <DarkModeToggle />
        </div>
      </nav>
    </header>
  );
}
