"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import AppShell from "@/components/layout/AppShell";
import StatsBar from "@/components/layout/StatsBar";
import { CHART_COLORS } from "@/lib/constants";
import type { LLMHealthResponse } from "@/lib/types";
import { API_BASE } from "@/lib/constants";

const MOCK_AGENTS = [
  { name: "PanDataAgent", processed: 47, success_rate: 0.98, avg_confidence: 0.95, avg_latency: 120 },
  { name: "BankStatementAgent", processed: 42, success_rate: 0.96, avg_confidence: 0.87, avg_latency: 340 },
  { name: "SalarySlipAgent", processed: 28, success_rate: 0.97, avg_confidence: 0.91, avg_latency: 180 },
  { name: "ITReturnAgent", processed: 15, success_rate: 0.93, avg_confidence: 0.89, avg_latency: 250 },
  { name: "GSTReturnAgent", processed: 12, success_rate: 0.92, avg_confidence: 0.84, avg_latency: 280 },
  { name: "CreditBureauAgent", processed: 35, success_rate: 0.88, avg_confidence: 0.82, avg_latency: 410 },
  { name: "UtilityBillAgent", processed: 22, success_rate: 0.99, avg_confidence: 0.94, avg_latency: 90 },
  { name: "PassbookAgent", processed: 8, success_rate: 0.87, avg_confidence: 0.78, avg_latency: 320 },
];

const MOCK_THROUGHPUT = [
  { date: "Mar 14", submitted: 32, approved: 11, rejected: 4 },
  { date: "Mar 15", submitted: 45, approved: 16, rejected: 6 },
  { date: "Mar 16", submitted: 38, approved: 14, rejected: 3 },
  { date: "Mar 17", submitted: 52, approved: 19, rejected: 8 },
  { date: "Mar 18", submitted: 41, approved: 15, rejected: 5 },
  { date: "Mar 19", submitted: 47, approved: 18, rejected: 7 },
  { date: "Mar 20", submitted: 47, approved: 16, rejected: 5 },
];

const MOCK_FLAG_DIST = [
  { category: "eligibility", red: 12, amber: 8, green: 27 },
  { category: "documentation", red: 3, amber: 15, green: 29 },
  { category: "extraction", red: 1, amber: 7, green: 39 },
  { category: "proposal", red: 5, amber: 11, green: 31 },
];

export default function AnalyticsPage() {
  const [llmStats, setLlmStats] = useState<LLMHealthResponse | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/health/llm`)
      .then((r) => r.json())
      .then(setLlmStats)
      .catch(() => {});
  }, []);

  const stats = [
    { label: "Applications Today", value: "47" },
    { label: "Avg Pipeline Time", value: "2h 14m" },
    { label: "Auto-Approve Rate", value: "34%", delta: "+3%", deltaType: "positive" as const },
    { label: "HITL Override Rate", value: "8%" },
    { label: "Extraction Accuracy", value: "96.2%" },
    { label: "LLM Cost Today", value: "₹847" },
  ];

  return (
    <AppShell title="Agent Observability">
      <StatsBar metrics={stats} />
      <div className="flex gap-4 p-6">
        {/* Left column */}
        <div className="flex-1 space-y-6">
          {/* Agent Performance Table */}
          <div className="bg-bg-surface border border-border-gold rounded">
            <div className="px-4 py-3 border-b border-border-gold">
              <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
                Extraction Agent Performance
              </h4>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-gold">
                  <th className="text-left text-[11px] text-text-tertiary uppercase px-4 py-2 font-normal">Agent</th>
                  <th className="text-right text-[11px] text-text-tertiary uppercase px-3 py-2 font-normal">Processed</th>
                  <th className="text-right text-[11px] text-text-tertiary uppercase px-3 py-2 font-normal">Success</th>
                  <th className="text-right text-[11px] text-text-tertiary uppercase px-3 py-2 font-normal">Confidence</th>
                  <th className="text-right text-[11px] text-text-tertiary uppercase px-3 py-2 font-normal">Latency</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_AGENTS.sort((a, b) => a.success_rate - b.success_rate).map((agent) => (
                  <tr key={agent.name} className="border-b border-border-gold hover:bg-bg-elevated transition-colors">
                    <td className="px-4 py-2 font-mono text-[12px] text-text-primary">{agent.name}</td>
                    <td className="px-3 py-2 font-mono text-[12px] text-text-secondary text-right">{agent.processed}</td>
                    <td className={`px-3 py-2 font-mono text-[12px] text-right ${
                      agent.success_rate >= 0.95 ? "text-risk-green" : agent.success_rate >= 0.85 ? "text-risk-amber" : "text-risk-red"
                    }`}>
                      {(agent.success_rate * 100).toFixed(0)}%
                    </td>
                    <td className="px-3 py-2 font-mono text-[12px] text-text-secondary text-right">
                      {(agent.avg_confidence * 100).toFixed(0)}%
                    </td>
                    <td className="px-3 py-2 font-mono text-[12px] text-text-secondary text-right">
                      {agent.avg_latency}ms
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pipeline Throughput Chart */}
          <div className="bg-bg-surface border border-border-gold rounded p-4">
            <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-4">
              Pipeline Throughput (7 days)
            </h4>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={MOCK_THROUGHPUT}>
                  <XAxis
                    dataKey="date"
                    tick={{ fill: CHART_COLORS.textSecondary, fontFamily: "JetBrains Mono", fontSize: 11 }}
                    axisLine={{ stroke: CHART_COLORS.primary, strokeOpacity: 0.2 }}
                  />
                  <YAxis
                    tick={{ fill: CHART_COLORS.textSecondary, fontFamily: "JetBrains Mono", fontSize: 11 }}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: CHART_COLORS.elevated,
                      border: "1px solid rgba(200,168,98,0.15)",
                      borderRadius: 4,
                      fontFamily: "JetBrains Mono",
                      fontSize: 12,
                    }}
                  />
                  <Line type="monotone" dataKey="submitted" stroke={CHART_COLORS.primary} strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="approved" stroke={CHART_COLORS.green} strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="rejected" stroke={CHART_COLORS.red} strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center gap-6 mt-2">
              <LegendItem color={CHART_COLORS.primary} label="Submitted" />
              <LegendItem color={CHART_COLORS.green} label="Approved" />
              <LegendItem color={CHART_COLORS.red} label="Rejected" />
            </div>
          </div>
        </div>

        {/* Right column */}
        <div className="w-[380px] space-y-6">
          {/* Risk Flag Distribution */}
          <div className="bg-bg-surface border border-border-gold rounded p-4">
            <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-4">
              Risk Flag Distribution
            </h4>
            <div className="space-y-3">
              {MOCK_FLAG_DIST.map((cat) => {
                const total = cat.red + cat.amber + cat.green;
                return (
                  <div key={cat.category}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[11px] text-text-secondary capitalize">{cat.category}</span>
                      <span className="font-mono text-[10px] text-text-tertiary">{total}</span>
                    </div>
                    <div className="flex h-2 rounded-sm overflow-hidden">
                      <div style={{ width: `${(cat.red / total) * 100}%` }} className="bg-risk-red" />
                      <div style={{ width: `${(cat.amber / total) * 100}%` }} className="bg-risk-amber" />
                      <div style={{ width: `${(cat.green / total) * 100}%` }} className="bg-risk-green" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* LLM Usage */}
          <div className="bg-bg-surface border border-border-gold rounded">
            <div className="px-4 py-3 border-b border-border-gold">
              <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
                LLM Usage
              </h4>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-gold">
                  <th className="text-left text-[10px] text-text-tertiary uppercase px-4 py-2 font-normal">Model</th>
                  <th className="text-right text-[10px] text-text-tertiary uppercase px-3 py-2 font-normal">Calls</th>
                  <th className="text-right text-[10px] text-text-tertiary uppercase px-3 py-2 font-normal">Tokens</th>
                  <th className="text-right text-[10px] text-text-tertiary uppercase px-3 py-2 font-normal">Cost</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border-gold">
                  <td className="px-4 py-2 font-mono text-[11px] text-text-primary">mock-llm-v1</td>
                  <td className="px-3 py-2 font-mono text-[11px] text-text-secondary text-right">
                    {llmStats?.stats.total_calls || 0}
                  </td>
                  <td className="px-3 py-2 font-mono text-[11px] text-text-secondary text-right">
                    {llmStats?.stats.total_tokens || 0}
                  </td>
                  <td className="px-3 py-2 font-mono text-[11px] text-text-secondary text-right">₹0</td>
                </tr>
                <tr className="bg-bg-elevated">
                  <td className="px-4 py-2 text-[11px] text-text-primary font-medium">Total</td>
                  <td className="px-3 py-2 font-mono text-[11px] text-text-primary text-right">
                    {llmStats?.stats.total_calls || 0}
                  </td>
                  <td className="px-3 py-2 font-mono text-[11px] text-text-primary text-right">
                    {llmStats?.stats.total_tokens || 0}
                  </td>
                  <td className="px-3 py-2 font-mono text-[11px] text-accent-gold text-right">₹0</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Recent Incidents */}
          <div className="bg-bg-surface border border-border-gold rounded p-4">
            <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
              Recent Incidents
            </h4>
            <p className="text-[12px] text-text-tertiary text-center py-4">
              No incidents in the last 24 hours
            </p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className="w-3 h-0.5 rounded" style={{ backgroundColor: color }} />
      <span className="text-[10px] text-text-tertiary">{label}</span>
    </div>
  );
}
