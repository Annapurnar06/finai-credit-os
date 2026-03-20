import { formatINR } from "@/lib/formatters";

interface MonospaceAmountProps {
  amount: number;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export default function MonospaceAmount({
  amount,
  className = "",
  size = "md",
}: MonospaceAmountProps) {
  const formatted = formatINR(amount);
  const symbolEnd = formatted.indexOf("₹") + 1;
  const symbol = formatted.slice(0, symbolEnd);
  const number = formatted.slice(symbolEnd);

  const sizeClasses = {
    sm: "text-[13px]",
    md: "text-base",
    lg: "text-xl",
  };

  return (
    <span className={`font-mono ${sizeClasses[size]} ${className}`}>
      <span className="text-text-secondary">{symbol}</span>
      <span className="text-text-primary">{number}</span>
    </span>
  );
}
