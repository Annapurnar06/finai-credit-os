import type { RiskLevel } from "@/lib/types";

const RISK_STYLES: Record<RiskLevel, string> = {
  RED: "bg-risk-red-bg text-risk-red border-risk-red/20",
  AMBER: "bg-risk-amber-bg text-risk-amber border-risk-amber/20",
  GREEN: "bg-risk-green-bg text-risk-green border-risk-green/20",
};

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
}

export default function RiskBadge({ level, className = "" }: RiskBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider border ${RISK_STYLES[level]} ${className}`}
    >
      {level}
    </span>
  );
}
