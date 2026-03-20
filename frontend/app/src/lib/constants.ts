import type { ApplicationStatus } from "./types";

export const STATUS_TO_COLUMN: Record<ApplicationStatus, string> = {
  draft: "Documents Submitted",
  documents_submitted: "Documents Submitted",
  extracting: "Extracting",
  extraction_complete: "Extracting",
  proposal_generated: "Proposal Ready",
  eligible: "Proposal Ready",
  ineligible: "Proposal Ready",
  hitl_pending: "HITL Pending",
  approved: "Approved",
  rejected: "Rejected",
};

export const KANBAN_COLUMNS = [
  "Documents Submitted",
  "Extracting",
  "Proposal Ready",
  "HITL Pending",
  "Approved",
  "Rejected",
] as const;

export const CHART_COLORS = {
  primary: "#C8A862",
  green: "#2D9D5E",
  amber: "#D4912E",
  red: "#C94444",
  surface: "#14161C",
  elevated: "#1C1F28",
  textSecondary: "#8B8680",
} as const;

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const NAV_ITEMS = [
  { label: "Pipeline", href: "/pipeline", icon: "Kanban" as const },
  { label: "HITL Queue", href: "/hitl-queue", icon: "UserCheck" as const },
  { label: "Borrowers", href: "/borrowers", icon: "Users" as const },
  { label: "Analytics", href: "/analytics", icon: "ChartLine" as const },
  { label: "Policies", href: "/policies", icon: "ShieldCheck" as const },
  { label: "Settings", href: "/settings", icon: "Gear" as const },
] as const;
