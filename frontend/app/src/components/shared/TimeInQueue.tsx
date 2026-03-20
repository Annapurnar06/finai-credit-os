interface TimeInQueueProps {
  hours: number;
}

export default function TimeInQueue({ hours }: TimeInQueueProps) {
  const color =
    hours > 8
      ? "text-risk-red"
      : hours > 2
        ? "text-risk-amber"
        : "text-risk-green";

  let display: string;
  if (hours < 1) {
    display = `${Math.round(hours * 60)}m`;
  } else if (hours < 24) {
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    display = m > 0 ? `${h}h ${m}m` : `${h}h`;
  } else {
    const d = Math.floor(hours / 24);
    const h = Math.round(hours % 24);
    display = h > 0 ? `${d}d ${h}h` : `${d}d`;
  }

  return <span className={`font-mono text-[13px] ${color}`}>{display}</span>;
}
