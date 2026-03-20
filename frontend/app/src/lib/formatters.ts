const inrFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export function formatINR(amount: number): string {
  return inrFormatter.format(amount);
}

export function formatDuration(ms: number): string {
  const totalMinutes = Math.floor(ms / 60_000);
  if (totalMinutes < 60) return `${totalMinutes}m`;
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours < 24) return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;
  return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
}

export function formatDurationFromHours(hours: number): string {
  return formatDuration(hours * 3_600_000);
}

export function formatConfidence(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatProductType(type: string): string {
  return type
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function formatSegment(segment: string): string {
  const map: Record<string, string> = {
    salaried: "Salaried",
    self_employed: "Self-Employed",
    msme: "MSME",
    agriculture: "Agriculture",
    gig_worker: "Gig Worker",
  };
  return map[segment] || segment;
}

export function formatDocType(docType: string): string {
  const map: Record<string, string> = {
    pan: "PAN Card",
    aadhaar: "Aadhaar",
    bank_statement: "Bank Statement",
    salary_slip: "Salary Slip",
    itr: "ITR",
    gst_return: "GST Return",
    credit_bureau: "Credit Bureau",
    collateral: "Collateral",
    utility_bill: "Utility Bill",
    passbook: "Passbook",
  };
  return map[docType] || docType.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
