import type { ExtractionStatus } from "@/lib/types";

const STATUS_STYLES: Record<ExtractionStatus, { bg: string; text: string; icon: string }> = {
  success: { bg: "bg-risk-green-bg", text: "text-risk-green", icon: "✓" },
  failure: { bg: "bg-risk-red-bg", text: "text-risk-red", icon: "✕" },
  low_confidence: { bg: "bg-risk-amber-bg", text: "text-risk-amber", icon: "~" },
};

interface StatusBadgeProps {
  status: ExtractionStatus;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const style = STATUS_STYLES[status];
  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono border ${style.bg} ${style.text} border-current/20`}
    >
      <span>{style.icon}</span>
      {status.replace("_", " ")}
    </span>
  );
}
