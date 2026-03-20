"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import StatsBar from "@/components/layout/StatsBar";
import RiskBadge from "@/components/cards/RiskBadge";
import SegmentBadge from "@/components/cards/SegmentBadge";
import { fetchApplications, fetchApplication } from "@/lib/api";
import { formatProductType, formatINR } from "@/lib/formatters";
import { STATUS_TO_COLUMN, KANBAN_COLUMNS } from "@/lib/constants";
import type { ApplicationListItem, ApplicationDetail, RiskLevel } from "@/lib/types";
import TimeInQueue from "@/components/shared/TimeInQueue";

interface EnrichedApp extends ApplicationListItem {
  detail?: ApplicationDetail;
}

export default function PipelinePage() {
  const [apps, setApps] = useState<EnrichedApp[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const list = await fetchApplications();
        const enriched: EnrichedApp[] = [];
        for (const app of list) {
          try {
            const detail = await fetchApplication(app.application_id);
            enriched.push({ ...app, detail });
          } catch {
            enriched.push(app);
          }
        }
        setApps(enriched);
      } catch {
        // API not available — use empty state
      } finally {
        setLoading(false);
      }
    }
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  const columns = KANBAN_COLUMNS.map((colName) => ({
    name: colName,
    apps: apps.filter((a) => STATUS_TO_COLUMN[a.status] === colName),
  }));

  const stats = [
    { label: "Documents Submitted", value: String(columns[0].apps.length) },
    { label: "Extracting", value: String(columns[1].apps.length) },
    { label: "Proposal Ready", value: String(columns[2].apps.length) },
    { label: "HITL Pending", value: String(columns[3].apps.length), deltaType: "negative" as const, delta: columns[3].apps.length > 0 ? "needs review" : "" },
    { label: "Approved Today", value: String(columns[4].apps.length), deltaType: "positive" as const },
    { label: "Rejected Today", value: String(columns[5].apps.length) },
  ];

  return (
    <AppShell title="Loan Pipeline">
      <StatsBar metrics={stats} />
      <div className="flex gap-3 p-4 h-[calc(100vh-112px-52px)] overflow-x-auto">
        {columns.map((col) => (
          <KanbanColumn key={col.name} name={col.name} apps={col.apps} loading={loading} />
        ))}
      </div>
    </AppShell>
  );
}

function KanbanColumn({
  name,
  apps,
  loading,
}: {
  name: string;
  apps: EnrichedApp[];
  loading: boolean;
}) {
  const isHITL = name === "HITL Pending";
  const isExtracting = name === "Extracting";

  return (
    <div className="flex-1 min-w-[220px] max-w-[280px] flex flex-col">
      <div className="flex items-center justify-between px-3 py-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-[12px] text-text-secondary font-medium">
            {name}
          </span>
          <span className="font-mono text-[10px] text-text-tertiary bg-bg-elevated rounded px-1.5 py-0.5">
            {apps.length}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 px-1">
        {loading ? (
          [...Array(2)].map((_, i) => (
            <div
              key={i}
              className="h-28 bg-bg-surface rounded border border-border-gold animate-[pulse-subtle_2s_ease-in-out_infinite]"
            />
          ))
        ) : apps.length === 0 ? (
          <p className="text-[12px] text-text-tertiary text-center py-8">
            No applications
          </p>
        ) : (
          apps.map((app) => (
            <ApplicationCard
              key={app.application_id}
              app={app}
              isHITL={isHITL}
              isExtracting={isExtracting}
            />
          ))
        )}
      </div>
    </div>
  );
}

function ApplicationCard({
  app,
  isHITL,
  isExtracting,
}: {
  app: EnrichedApp;
  isHITL: boolean;
  isExtracting: boolean;
}) {
  const result = app.detail?.result;
  const profile = result?.proposal?.borrower_profile;
  const riskFlags = result?.risk_flags || [];
  const highestRisk: RiskLevel = riskFlags.some((f) => f.level === "RED")
    ? "RED"
    : riskFlags.some((f) => f.level === "AMBER")
      ? "AMBER"
      : "GREEN";

  // Deterministic "time in queue" from application ID hash
  const hashCode = app.application_id.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  const hoursInQueue = (hashCode % 800) / 100 + 0.5;

  return (
    <Link href={`/applications/${app.application_id}`}>
      <div
        className={`bg-bg-surface border border-border-gold rounded p-3 hover:border-border-gold-hover hover:bg-bg-elevated transition-all duration-150 cursor-pointer ${
          isHITL ? "border-l-2 border-l-accent-gold" : ""
        }`}
        style={{ animation: "fade-in 0.2s ease-out" }}
      >
        <div className="flex items-center justify-between">
          <span className="text-[13px] text-text-primary font-medium truncate">
            {profile?.borrower_name || app.borrower_pan}
          </span>
          {profile?.segment && <SegmentBadge segment={profile.segment} />}
        </div>
        <div className="text-[12px] text-text-secondary mt-1">
          {formatProductType(app.product_type)}
          {result?.proposal?.eligibility?.max_loan_amount && (
            <span className="font-mono text-text-primary ml-1">
              {formatINR(result.proposal.eligibility.max_loan_amount)}
            </span>
          )}
        </div>
        <div className="flex items-center justify-between mt-2">
          <RiskBadge level={highestRisk} />
          <TimeInQueue hours={hoursInQueue} />
        </div>
        {isExtracting && (
          <div className="mt-2 h-1 bg-bg-elevated rounded-full overflow-hidden">
            <div
              className="h-full bg-accent-gold/60 rounded-full"
              style={{
                width: "60%",
                backgroundSize: "200% 100%",
                backgroundImage:
                  "linear-gradient(90deg, transparent, rgba(200,168,98,0.3), transparent)",
                animation: "shimmer 1.5s ease-in-out infinite",
              }}
            />
          </div>
        )}
        {isHITL && (
          <button className="w-full mt-2 py-1.5 text-[11px] text-accent-gold border border-accent-gold/30 rounded hover:bg-accent-gold/10 transition-colors">
            Review →
          </button>
        )}
      </div>
    </Link>
  );
}
