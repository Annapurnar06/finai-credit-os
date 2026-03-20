interface DBRGaugeProps {
  ratio: number;
  size?: number;
}

export default function DBRGauge({ ratio, size = 100 }: DBRGaugeProps) {
  const percent = Math.min(ratio * 100, 100);
  const r = size / 2 - 8;
  const cx = size / 2;
  const cy = size / 2 + 4;
  const circumference = Math.PI * r;
  const offset = circumference - (percent / 100) * circumference;

  const color =
    ratio > 0.5
      ? "var(--color-risk-red)"
      : ratio > 0.4
        ? "var(--color-risk-amber)"
        : "var(--color-risk-green)";

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 16} viewBox={`0 0 ${size} ${size / 2 + 16}`}>
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none"
          stroke="var(--color-bg-elevated)"
          strokeWidth={6}
          strokeLinecap="round"
        />
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth={6}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.5s ease-out" }}
        />
        {/* 40% threshold mark */}
        <line
          x1={cx + r * Math.cos(Math.PI * (1 - 0.4))}
          y1={cy - r * Math.sin(Math.PI * (1 - 0.4))}
          x2={cx + (r - 8) * Math.cos(Math.PI * (1 - 0.4))}
          y2={cy - (r - 8) * Math.sin(Math.PI * (1 - 0.4))}
          stroke="var(--color-risk-amber)"
          strokeWidth={1}
          opacity={0.5}
        />
        {/* 50% threshold mark */}
        <line
          x1={cx + r * Math.cos(Math.PI * (1 - 0.5))}
          y1={cy - r * Math.sin(Math.PI * (1 - 0.5))}
          x2={cx + (r - 8) * Math.cos(Math.PI * (1 - 0.5))}
          y2={cy - (r - 8) * Math.sin(Math.PI * (1 - 0.5))}
          stroke="var(--color-risk-red)"
          strokeWidth={1}
          opacity={0.5}
        />
      </svg>
      <span className="font-mono text-sm" style={{ color }}>
        {percent.toFixed(1)}%
      </span>
    </div>
  );
}
