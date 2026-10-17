// 0..1 metric colour cutoffs
const GOOD = 0.8;
const FAIR = 0.5;

export function ScoreBar({
  label,
  value,
  suffix,
  max = 1,
}: {
  label: string;
  value: number | null;
  suffix?: string;
  max?: number;
}) {
  const has = value !== null && Number.isFinite(value);
  const pct = has ? Math.max(0, Math.min(1, value / max)) * 100 : 0;
  // Latency passes max>1; only 0..1 metrics get graded colour.
  const tone = !has
    ? "bg-secondary"
    : max === 1
      ? value >= GOOD
        ? "bg-emerald-500"
        : value >= FAIR
          ? "bg-amber-500"
          : "bg-red-500"
      : "bg-primary";
  return (
    <div className="space-y-1">
      <div className="flex items-baseline justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-mono">
          {has
            ? suffix
              ? `${Math.round(value)}${suffix}`
              : value.toFixed(3)
            : "—"}
        </span>
      </div>
      <div
        className="h-2 overflow-hidden rounded-full bg-secondary"
        role="img"
        aria-label={`${label}: ${has ? (suffix ? `${Math.round(value)}${suffix}` : value.toFixed(3)) : "no data"}`}
      >
        <div
          className={`h-full rounded-full transition-[width] duration-500 ${tone}${
            tone === "bg-emerald-500" ? " shadow-[0_0_10px] shadow-emerald-500/50" : ""
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
