import { formatSegment } from "@/lib/formatters";

interface SegmentBadgeProps {
  segment: string;
}

export default function SegmentBadge({ segment }: SegmentBadgeProps) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] text-text-secondary border border-border-gold-hover uppercase tracking-wider">
      {formatSegment(segment)}
    </span>
  );
}
