"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import SegmentBadge from "@/components/cards/SegmentBadge";
import RiskBadge from "@/components/cards/RiskBadge";
import StatusBadge from "@/components/cards/StatusBadge";
import MetricCard from "@/components/cards/MetricCard";
import MonospaceAmount from "@/components/financial/MonospaceAmount";
import DBRGauge from "@/components/financial/DBRGauge";
import ProvenanceBadge from "@/components/shared/ProvenanceBadge";
import { fetchApplication } from "@/lib/api";
import { formatINR, formatDocType, formatConfidence } from "@/lib/formatters";
import type { ApplicationDetail, RiskLevel, ExtractionStatus } from "@/lib/types";

type Tab = "overview" | "financial" | "documents" | "applications" | "memory";

export default function BorrowerProfilePage() {
  const params = useParams();
  const id = params.id as string;
  const [app, setApp] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  useEffect(() => {
    fetchApplication(id)
      .then(setApp)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <AppShell title="Borrower 360">
        <div className="p-6 space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 bg-bg-surface rounded border border-border-gold animate-[pulse-subtle_2s_ease-in-out_infinite]" />
          ))}
        </div>
      </AppShell>
    );
  }

  if (!app?.result) {
    return (
      <AppShell title="Borrower 360">
        <div className="flex items-center justify-center h-64">
          <p className="text-text-tertiary text-[13px]">Borrower data not available</p>
        </div>
      </AppShell>
    );
  }

  const result = app.result;
  const profile = result.proposal.borrower_profile;
  const riskFlags = result.risk_flags || [];
  const extractions = result.extraction_results || {};
  const eligibility = result.proposal.eligibility;
  const dbr = result.proposal.dbr;
  const triangulation = result.proposal.triangulation;
  const docCheck = result.proposal.doc_check;

  const riskTier: RiskLevel = riskFlags.some((f) => f.level === "RED")
    ? "RED"
    : riskFlags.some((f) => f.level === "AMBER")
      ? "AMBER"
      : "GREEN";

  const tabs: { key: Tab; label: string }[] = [
    { key: "overview", label: "Overview" },
    { key: "financial", label: "Financial Profile" },
    { key: "documents", label: "Documents" },
    { key: "applications", label: "Applications" },
    { key: "memory", label: "Memory" },
  ];

  return (
    <AppShell title="Borrower 360">
      {/* Header */}
      <div className="bg-bg-surface border-b border-border-gold px-6 py-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-accent-gold bg-bg-elevated flex items-center justify-center font-serif text-lg text-accent-gold">
            {profile.borrower_name
              .split(" ")
              .map((w) => w[0])
              .slice(0, 2)
              .join("")}
          </div>
          <div className="flex-1">
            <h3 className="font-serif text-[28px] text-text-primary leading-tight">
              {profile.borrower_name}
            </h3>
            <div className="flex items-center gap-3 mt-1">
              <span className="font-mono text-[13px] text-text-secondary">
                {profile.pan}
              </span>
              <SegmentBadge segment={profile.segment} />
              <RiskBadge level={riskTier} />
              <span className="text-[11px] text-text-tertiary">
                Age {profile.age}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-0 border-b border-border-gold bg-bg-surface px-6">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2.5 text-[13px] border-b-2 transition-colors ${
              activeTab === tab.key
                ? "border-accent-gold text-accent-gold"
                : "border-transparent text-text-secondary hover:text-text-primary"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="p-6">
        {activeTab === "overview" && (
          <div className="flex gap-6">
            <div className="flex-[3] space-y-6">
              {/* Identity */}
              <div className="bg-bg-surface border border-border-gold rounded p-4">
                <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
                  Identity
                </h4>
                <div className="grid grid-cols-2 gap-x-6 gap-y-2">
                  {[
                    ["Name", profile.borrower_name],
                    ["PAN", profile.pan],
                    ["Age", String(profile.age)],
                    ["Segment", profile.segment],
                    ["Employer", profile.employer || "—"],
                  ].map(([label, value]) => (
                    <div key={label} className="flex items-baseline gap-3">
                      <span className="text-[11px] text-text-tertiary w-20 shrink-0">
                        {label}
                      </span>
                      <span className="font-mono text-[12px] text-text-primary">
                        {value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Financial snapshot */}
              <div className="grid grid-cols-4 gap-3">
                <MetricCard
                  label="Monthly Income"
                  value={formatINR(profile.monthly_income)}
                />
                <MetricCard
                  label="Bureau Score"
                  value={String(profile.liabilities?.bureau_score || "N/A")}
                  valueColor={
                    (profile.liabilities?.bureau_score || 0) >= 720
                      ? "text-risk-green"
                      : (profile.liabilities?.bureau_score || 0) >= 650
                        ? "text-risk-amber"
                        : "text-risk-red"
                  }
                />
                <div className="bg-bg-surface border border-border-gold rounded p-4 flex flex-col items-center">
                  <p className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
                    DBR
                  </p>
                  <DBRGauge ratio={dbr?.dbr_ratio || 0} size={70} />
                </div>
                <MetricCard
                  label="Max Eligible"
                  value={eligibility?.is_eligible ? formatINR(eligibility.max_loan_amount) : "N/A"}
                />
              </div>

              {/* Income Sources */}
              {profile.income_sources.length > 0 && (
                <div className="bg-bg-surface border border-border-gold rounded p-4">
                  <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
                    Income Sources
                  </h4>
                  {profile.income_sources.map((src, i) => (
                    <div key={i} className="flex items-center justify-between py-1.5 border-b border-border-gold last:border-0">
                      <span className="text-[12px] text-text-secondary">{src.source}</span>
                      <div className="flex items-center gap-3">
                        <MonospaceAmount amount={src.monthly || (src.annual ? src.annual / 12 : 0)} size="sm" />
                        <span className="font-mono text-[10px] text-text-tertiary">
                          {formatConfidence(src.confidence)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right column — entity graph + activity */}
            <div className="flex-[2] space-y-6">
              {/* Entity Graph (simplified SVG) */}
              <div className="bg-bg-surface border border-border-gold rounded p-4">
                <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
                  Entity Graph
                </h4>
                <EntityGraph
                  name={profile.borrower_name}
                  pan={profile.pan}
                  docTypes={Object.keys(extractions)}
                />
              </div>

              {/* Recent Activity */}
              <div className="bg-bg-surface border border-border-gold rounded p-4">
                <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
                  Pipeline Activity
                </h4>
                <div className="space-y-3">
                  {riskFlags.length > 0 && (
                    <ActivityItem
                      time="Pipeline"
                      text={`${riskFlags.length} risk flag(s) identified`}
                      color="text-risk-amber"
                    />
                  )}
                  {Object.entries(extractions).map(([dt, ext]) => (
                    <ActivityItem
                      key={dt}
                      time={ext.agent_name || dt}
                      text={`${formatDocType(dt)} extracted — ${ext.status}`}
                      color={ext.status === "success" ? "text-risk-green" : "text-risk-amber"}
                    />
                  ))}
                  <ActivityItem
                    time="System"
                    text={`Application status: ${app.status}`}
                    color="text-accent-gold"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "financial" && (
          <div className="space-y-6">
            {triangulation && (
              <div className="bg-bg-surface border border-border-gold rounded p-4">
                <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
                  Income Triangulation
                </h4>
                <div className="grid grid-cols-3 gap-4">
                  <MetricCard label="Declared" value={formatINR(triangulation.declared_income)} />
                  <MetricCard label="Verified" value={formatINR(triangulation.verified_income)} valueColor="text-accent-gold" />
                  <MetricCard label="Confidence" value={formatConfidence(triangulation.income_confidence)} />
                </div>
                <div className="mt-4 text-[12px] text-text-secondary">
                  Sources checked: {triangulation.sources_checked.join(", ")}
                </div>
              </div>
            )}
            {dbr && (
              <div className="bg-bg-surface border border-border-gold rounded p-4">
                <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
                  Debt Burden
                </h4>
                <div className="grid grid-cols-3 gap-4">
                  <MetricCard label="Net Income" value={formatINR(dbr.net_monthly_income)} />
                  <MetricCard label="Total EMI" value={formatINR(dbr.total_monthly_emi)} />
                  <MetricCard label="Max New EMI" value={formatINR(dbr.max_eligible_emi)} />
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "documents" && (
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(extractions).map(([dt, ext]) => (
              <div key={dt} className="bg-bg-surface border border-border-gold rounded p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[13px] text-text-primary">{formatDocType(dt)}</span>
                  <StatusBadge status={(ext.status || "failure") as ExtractionStatus} />
                </div>
                <div className="space-y-1">
                  {ext.data &&
                    Object.entries(ext.data)
                      .slice(0, 5)
                      .map(([k, v]) => (
                        <div key={k} className="flex items-baseline gap-2">
                          <span className="text-[10px] text-text-tertiary w-24 shrink-0 truncate">{k}</span>
                          <span className="font-mono text-[11px] text-text-primary truncate">{String(v)}</span>
                        </div>
                      ))}
                </div>
                <ProvenanceBadge agentName={ext.agent_name || dt} confidence={ext.confidence} />
              </div>
            ))}
            {docCheck?.missing?.map((doc) => (
              <div key={doc} className="border border-dashed border-risk-amber/30 rounded p-4">
                <span className="text-[13px] text-risk-amber">{formatDocType(doc)}</span>
                <p className="text-[11px] text-text-tertiary mt-1">Missing — required for this product</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === "applications" && (
          <div className="bg-bg-surface border border-border-gold rounded">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-gold">
                  <th className="text-left text-[11px] text-text-tertiary uppercase px-4 py-2 font-normal">ID</th>
                  <th className="text-left text-[11px] text-text-tertiary uppercase px-4 py-2 font-normal">Product</th>
                  <th className="text-left text-[11px] text-text-tertiary uppercase px-4 py-2 font-normal">Status</th>
                  <th className="text-left text-[11px] text-text-tertiary uppercase px-4 py-2 font-normal">Decision</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border-gold">
                  <td className="font-mono text-[12px] px-4 py-2 text-text-secondary">{app.application_id.slice(0, 8)}</td>
                  <td className="text-[12px] px-4 py-2 text-text-secondary">{app.product_type}</td>
                  <td className="text-[12px] px-4 py-2 text-text-secondary">{app.status}</td>
                  <td className="text-[12px] px-4 py-2 text-text-secondary">{result.final_decision || "—"}</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "memory" && (
          <div className="text-center py-16">
            <p className="font-serif text-xl text-text-tertiary">
              Memory search available via Mem0 integration
            </p>
            <p className="text-[12px] text-text-tertiary mt-1">
              Set MEM0_API_KEY for persistent borrower memory
            </p>
          </div>
        )}
      </div>
    </AppShell>
  );
}

function EntityGraph({ name, pan, docTypes }: { name: string; pan: string; docTypes: string[] }) {
  const nodes = [
    { label: pan, type: "PAN" },
    ...docTypes.filter((d) => d !== "pan").slice(0, 4).map((d) => ({ label: d.replace(/_/g, " "), type: d })),
  ];
  const cx = 120;
  const cy = 80;
  const r = 60;

  return (
    <svg width={240} height={160} className="mx-auto">
      {/* Center node */}
      <circle cx={cx} cy={cy} r={24} fill="none" stroke="var(--color-accent-gold)" strokeWidth={1.5} />
      <text x={cx} y={cy} textAnchor="middle" dominantBaseline="middle" fill="var(--color-accent-gold)" fontSize={9} fontFamily="DM Sans">
        {name.split(" ")[0]}
      </text>
      {/* Connected nodes */}
      {nodes.map((node, i) => {
        const angle = (Math.PI / (nodes.length + 1)) * (i + 1);
        const nx = cx + r * Math.cos(angle - Math.PI / 2);
        const ny = cy + r * Math.sin(angle - Math.PI / 2);
        return (
          <g key={i}>
            <line x1={cx} y1={cy} x2={nx} y2={ny} stroke="var(--color-accent-gold-muted)" strokeWidth={0.5} />
            <circle cx={nx} cy={ny} r={14} fill="var(--color-bg-elevated)" stroke="var(--color-border-gold-hover)" strokeWidth={1} />
            <text x={nx} y={ny} textAnchor="middle" dominantBaseline="middle" fill="var(--color-text-secondary)" fontSize={7} fontFamily="JetBrains Mono">
              {node.type.slice(0, 4).toUpperCase()}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function ActivityItem({ time, text, color }: { time: string; text: string; color: string }) {
  return (
    <div className="flex items-start gap-2">
      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${color.replace("text-", "bg-")}`} />
      <div>
        <p className="text-[12px] text-text-primary">{text}</p>
        <p className="text-[10px] text-text-tertiary font-mono">{time}</p>
      </div>
    </div>
  );
}
