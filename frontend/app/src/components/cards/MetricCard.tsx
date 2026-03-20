interface MetricCardProps {
  label: string;
  value: string;
  subtext?: string;
  valueColor?: string;
}

export default function MetricCard({
  label,
  value,
  subtext,
  valueColor = "text-text-primary",
}: MetricCardProps) {
  return (
    <div className="bg-bg-surface border border-border-gold rounded p-4">
      <p className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
        {label}
      </p>
      <p className={`font-mono text-xl mt-1 ${valueColor}`}>{value}</p>
      {subtext && (
        <p className="text-[11px] text-text-tertiary mt-1 font-mono">
          {subtext}
        </p>
      )}
    </div>
  );
}
