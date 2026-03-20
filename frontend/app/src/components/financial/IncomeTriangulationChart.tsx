"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { formatINR } from "@/lib/formatters";
import { CHART_COLORS } from "@/lib/constants";
import type { IncomeSource } from "@/lib/types";

interface Props {
  sources: IncomeSource[];
  verifiedIncome: number;
  confidence: number;
}

const SOURCE_LABELS: Record<string, string> = {
  bank_statement: "Bank Statement",
  salary_slip: "Salary Slip",
  itr: "ITR",
  gst: "GST-Derived",
};

export default function IncomeTriangulationChart({
  sources,
  verifiedIncome,
  confidence,
}: Props) {
  const data = sources.map((s) => ({
    name: SOURCE_LABELS[s.source] || s.source,
    amount: s.monthly || (s.annual ? s.annual / 12 : s.estimated_monthly_profit || 0),
    confidence: s.confidence,
  }));

  return (
    <div>
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 100, right: 20 }}>
            <XAxis
              type="number"
              tick={{ fill: CHART_COLORS.textSecondary, fontFamily: "JetBrains Mono", fontSize: 11 }}
              axisLine={{ stroke: CHART_COLORS.primary, strokeOpacity: 0.2 }}
              tickFormatter={(v: number) => `₹${(v / 1000).toFixed(0)}K`}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: CHART_COLORS.textSecondary, fontFamily: "DM Sans", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={100}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: CHART_COLORS.elevated,
                border: `1px solid rgba(200,168,98,0.15)`,
                borderRadius: 4,
                fontFamily: "JetBrains Mono",
                fontSize: 12,
              }}
              labelStyle={{ color: "#E8E4DF" }}
              formatter={(value) => [formatINR(Number(value)), "Monthly"]}
            />
            <Bar dataKey="amount" radius={[0, 2, 2, 0]} maxBarSize={24}>
              {data.map((_, i) => (
                <Cell key={i} fill={CHART_COLORS.primary} fillOpacity={0.7 + i * 0.1} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex items-center gap-4 mt-3 px-1">
        <span className="text-[11px] text-text-tertiary">Verified Income:</span>
        <span className="font-mono text-accent-gold text-[13px]">
          {formatINR(verifiedIncome)}
        </span>
        <span className="text-[11px] text-text-tertiary">Confidence:</span>
        <div className="flex items-center gap-1.5">
          <div className="w-16 h-1.5 bg-bg-elevated rounded-full overflow-hidden">
            <div
              className="h-full bg-accent-gold rounded-full transition-all"
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
          <span className="font-mono text-[11px] text-text-secondary">
            {(confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
}
