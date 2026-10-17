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
];

export function NavBar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 border-b border-border/60 bg-background/70 backdrop-blur-xl">
      <nav
        className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4"
        aria-label="Main"
      >
        <Link href="/" className="flex shrink-0 items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-emerald-500" aria-hidden />
          <span className="hidden font-display text-lg tracking-tight sm:inline">Sentinel RAG</span>
        </Link>

        <div className="ml-2 flex items-center gap-1 overflow-x-auto [scrollbar-width:none] max-sm:[mask-image:linear-gradient(to_right,black_85%,transparent)] max-sm:[-webkit-mask-image:linear-gradient(to_right,black_85%,transparent)]">
          {LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={`relative shrink-0 rounded-md px-3 py-1.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                  active
                    ? "bg-primary/10 text-foreground after:absolute after:inset-x-3 after:bottom-0 after:h-[2px] after:rounded-full after:bg-primary after:shadow-[0_0_8px] after:shadow-primary/70"
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
