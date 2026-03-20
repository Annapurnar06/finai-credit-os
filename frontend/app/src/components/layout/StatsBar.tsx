interface Metric {
  label: string;
  value: string;
  delta?: string;
  deltaType?: "positive" | "negative" | "neutral";
}

interface StatsBarProps {
  metrics: Metric[];
}

export default function StatsBar({ metrics }: StatsBarProps) {
  return (
    <div className="flex gap-4 px-6 py-3 bg-bg-surface border-b border-border-gold">
      {metrics.map((m) => (
        <div key={m.label} className="flex-1 min-w-0">
          <p className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] truncate">
            {m.label}
          </p>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="font-mono text-lg text-text-primary">
              {m.value}
            </span>
            {m.delta && (
              <span
                className={`text-[10px] font-mono ${
                  m.deltaType === "positive"
                    ? "text-risk-green"
                    : m.deltaType === "negative"
                      ? "text-risk-red"
                      : "text-text-tertiary"
                }`}
              >
                {m.delta}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
