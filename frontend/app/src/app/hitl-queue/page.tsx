"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { X } from "@phosphor-icons/react";
import AppShell from "@/components/layout/AppShell";
import RiskBadge from "@/components/cards/RiskBadge";
import SegmentBadge from "@/components/cards/SegmentBadge";
import MetricCard from "@/components/cards/MetricCard";
import TimeInQueue from "@/components/shared/TimeInQueue";
import { fetchApplications, fetchApplication } from "@/lib/api";
import { formatINR, formatProductType } from "@/lib/formatters";
import type { ApplicationDetail, RiskLevel } from "@/lib/types";

interface QueueItem {
  application_id: string;
  borrower_name: string;
  borrower_pan: string;
  segment: string;
  product_type: string;
  amount: number;
  red_count: number;
  amber_count: number;
  highest_risk: RiskLevel;
  hours_in_queue: number;
  detail: ApplicationDetail;
}

export default function HITLQueuePage() {
  const [items, setItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "mine" | "unassigned">("all");

  useEffect(() => {
    async function load() {
      try {
        const list = await fetchApplications();
        const hitlApps = list.filter((a) => a.status === "hitl_pending");
        const queue: QueueItem[] = [];
        for (const app of hitlApps) {
          try {
            const detail = await fetchApplication(app.application_id);
            const result = detail.result;
            const flags = result?.risk_flags || [];
            queue.push({
              application_id: app.application_id,
              borrower_name: result?.proposal?.borrower_profile?.borrower_name || app.borrower_pan,
              borrower_pan: app.borrower_pan,
              segment: result?.proposal?.borrower_profile?.segment || "unknown",
              product_type: app.product_type,
              amount: result?.proposal?.eligibility?.max_loan_amount || 0,
              red_count: flags.filter((f) => f.level === "RED").length,
              amber_count: flags.filter((f) => f.level === "AMBER").length,
              highest_risk: flags.some((f) => f.level === "RED") ? "RED" : flags.some((f) => f.level === "AMBER") ? "AMBER" : "GREEN",
              hours_in_queue: (app.application_id.split("").reduce((a, c) => a + c.charCodeAt(0), 0) % 1200) / 100 + 0.5,
              detail,
            });
          } catch {
            // skip failed fetches
          }
        }
        setItems(queue);
      } catch {
        // API unavailable
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const selected = items.find((i) => i.application_id === selectedId);

  return (
    <AppShell title="HITL Review Queue">
      <div className="flex h-[calc(100vh-56px)]">
        {/* Main table */}
        <div className={`flex-1 flex flex-col ${selectedId ? "max-w-[calc(100%-480px)]" : ""}`}>
          {/* Filter bar */}
          <div className="flex items-center gap-3 px-6 py-3 border-b border-border-gold">
            {(["all", "mine", "unassigned"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 rounded text-[12px] border transition-colors ${
                  filter === f
                    ? "bg-bg-elevated border-border-gold-hover text-text-primary"
                    : "border-transparent text-text-secondary hover:text-text-primary"
                }`}
              >
                {f === "all" ? `All (${items.length})` : f === "mine" ? "Assigned to Me" : "Unassigned"}
              </button>
            ))}
          </div>

          {/* Table */}
          <div className="flex-1 overflow-auto">
            <table className="w-full">
              <thead className="sticky top-0 bg-bg-surface z-10">
                <tr className="border-b border-border-gold">
                  <th className="w-1 px-0" />
                  <th className="text-left text-[11px] text-text-tertiary uppercase tracking-[0.05em] px-4 py-2.5 font-normal">
                    Borrower
                  </th>
                  <th className="text-left text-[11px] text-text-tertiary uppercase tracking-[0.05em] px-3 py-2.5 font-normal">
                    Segment
                  </th>
                  <th className="text-left text-[11px] text-text-tertiary uppercase tracking-[0.05em] px-3 py-2.5 font-normal">
                    Product
                  </th>
                  <th className="text-right text-[11px] text-text-tertiary uppercase tracking-[0.05em] px-3 py-2.5 font-normal">
                    Amount
                  </th>
                  <th className="text-center text-[11px] text-text-tertiary uppercase tracking-[0.05em] px-3 py-2.5 font-normal">
                    Risk
                  </th>
                  <th className="text-right text-[11px] text-text-tertiary uppercase tracking-[0.05em] px-3 py-2.5 font-normal">
                    In Queue
                  </th>
                  <th className="text-left text-[11px] text-text-tertiary uppercase tracking-[0.05em] px-3 py-2.5 font-normal">
                    Assigned
                  </th>
                  <th className="px-3 py-2.5" />
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  [...Array(4)].map((_, i) => (
                    <tr key={i} className="border-b border-border-gold">
                      <td colSpan={9} className="px-4 py-4">
                        <div className="h-5 bg-bg-elevated rounded animate-[pulse-subtle_2s_ease-in-out_infinite]" />
                      </td>
                    </tr>
                  ))
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="text-center py-16">
                      <p className="font-serif text-xl text-text-tertiary">
                        No applications pending review
                      </p>
                      <p className="text-[12px] text-text-tertiary mt-1">
                        Applications auto-approved by policy are not shown here.
                      </p>
                    </td>
                  </tr>
                ) : (
                  items.map((item) => (
                    <tr
                      key={item.application_id}
                      onClick={() => setSelectedId(item.application_id)}
                      className={`border-b border-border-gold cursor-pointer transition-colors hover:bg-bg-elevated ${
                        selectedId === item.application_id
                          ? "bg-bg-elevated border-l-2 border-l-accent-gold"
                          : ""
                      }`}
                    >
                      <td className="w-1 px-0">
                        <div
                          className={`w-1 h-10 rounded-r ${
                            item.hours_in_queue > 8 || item.red_count > 0
                              ? "bg-risk-red"
                              : item.hours_in_queue > 2 || item.amber_count > 0
                                ? "bg-risk-amber"
                                : "bg-risk-green"
                          }`}
                        />
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-[13px] text-text-primary">{item.borrower_name}</p>
                        <p className="font-mono text-[11px] text-text-tertiary">{item.borrower_pan}</p>
                      </td>
                      <td className="px-3 py-3">
                        <SegmentBadge segment={item.segment} />
                      </td>
                      <td className="px-3 py-3 text-[13px] text-text-secondary">
                        {formatProductType(item.product_type)}
                      </td>
                      <td className="px-3 py-3 text-right font-mono text-[13px] text-text-primary">
                        {item.amount > 0 ? formatINR(item.amount) : "—"}
                      </td>
                      <td className="px-3 py-3 text-center">
                        <span className="font-mono text-[11px]">
                          {item.red_count > 0 && (
                            <span className="text-risk-red">{item.red_count}R</span>
                          )}
                          {item.red_count > 0 && item.amber_count > 0 && " "}
                          {item.amber_count > 0 && (
                            <span className="text-risk-amber">{item.amber_count}A</span>
                          )}
                          {item.red_count === 0 && item.amber_count === 0 && (
                            <span className="text-risk-green">0</span>
                          )}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <TimeInQueue hours={item.hours_in_queue} />
                      </td>
                      <td className="px-3 py-3 text-[12px] text-text-tertiary">
                        Unassigned
                      </td>
                      <td className="px-3 py-3">
                        <Link
                          href={`/applications/${item.application_id}`}
                          className="text-[11px] text-accent-gold border border-accent-gold/30 rounded px-2 py-1 hover:bg-accent-gold/10 transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Review →
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Side panel */}
        {selected && (
          <div className="w-[480px] bg-bg-surface border-l border-border-gold p-6 overflow-y-auto shrink-0">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-serif text-lg text-text-primary">
                  {selected.borrower_name}
                </h3>
                <p className="text-[11px] text-text-tertiary">Quick Preview</p>
              </div>
              <button
                onClick={() => setSelectedId(null)}
                className="text-text-tertiary hover:text-text-primary transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Risk flags */}
            <div className="space-y-1 mb-4">
              {selected.detail.result?.risk_flags?.slice(0, 5).map((f) => (
                <div key={f.flag_id} className="flex items-center gap-2">
                  <RiskBadge level={f.level} />
                  <span className="text-[12px] text-text-secondary truncate">
                    {f.description}
                  </span>
                </div>
              ))}
            </div>

            {/* Financial snapshot */}
            <div className="grid grid-cols-2 gap-2 mb-4">
              <MetricCard
                label="Income"
                value={
                  selected.detail.result?.proposal?.borrower_profile?.monthly_income
                    ? formatINR(selected.detail.result.proposal.borrower_profile.monthly_income)
                    : "N/A"
                }
              />
              <MetricCard
                label="Bureau Score"
                value={String(
                  selected.detail.result?.proposal?.borrower_profile?.liabilities?.bureau_score || "N/A"
                )}
              />
              <MetricCard
                label="DBR"
                value={
                  selected.detail.result?.proposal?.dbr?.dbr_ratio
                    ? `${(selected.detail.result.proposal.dbr.dbr_ratio * 100).toFixed(1)}%`
                    : "N/A"
                }
              />
              <MetricCard
                label="Max Eligible"
                value={
                  selected.detail.result?.proposal?.eligibility?.max_loan_amount
                    ? formatINR(selected.detail.result.proposal.eligibility.max_loan_amount)
                    : "N/A"
                }
              />
            </div>

            {/* Extraction status */}
            {selected.detail.result?.extraction_results && (
              <div className="mb-4">
                <p className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-2">
                  Extraction Status
                </p>
                {Object.entries(selected.detail.result.extraction_results).map(
                  ([docType, ext]) => (
                    <div key={docType} className="flex items-center justify-between py-1">
                      <span className="text-[12px] text-text-secondary">
                        {docType.replace(/_/g, " ")}
                      </span>
                      <span
                        className={`font-mono text-[10px] ${
                          ext.status === "success"
                            ? "text-risk-green"
                            : ext.status === "failure"
                              ? "text-risk-red"
                              : "text-risk-amber"
                        }`}
                      >
                        {ext.status}
                      </span>
                    </div>
                  ),
                )}
              </div>
            )}

            <Link
              href={`/applications/${selected.application_id}`}
              className="block w-full py-2.5 text-center text-[13px] text-accent-gold border border-accent-gold rounded hover:bg-accent-gold hover:text-bg-primary transition-all"
            >
              Open Full Brief →
            </Link>

            <div className="flex gap-2 mt-3">
              <button className="flex-1 py-1.5 text-[11px] text-text-secondary border border-border-gold rounded hover:bg-bg-elevated transition-colors">
                Assign to Me
              </button>
              <button className="flex-1 py-1.5 text-[11px] text-text-secondary border border-border-gold rounded hover:bg-bg-elevated transition-colors">
                Escalate
              </button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
