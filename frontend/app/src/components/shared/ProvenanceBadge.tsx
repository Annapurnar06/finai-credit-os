interface ProvenanceBadgeProps {
  agentName: string;
  confidence?: number;
}

export default function ProvenanceBadge({
  agentName,
  confidence,
}: ProvenanceBadgeProps) {
  return (
    <span className="inline-flex items-center gap-1.5 text-[10px] text-text-tertiary">
      <span className="font-mono">{agentName}</span>
      {confidence !== undefined && (
        <span className="font-mono text-text-tertiary/60">
          {(confidence * 100).toFixed(0)}%
        </span>
      )}
    </span>
  );
}
