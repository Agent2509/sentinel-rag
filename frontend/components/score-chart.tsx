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
          className="h-full rounded-full bg-emerald-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
