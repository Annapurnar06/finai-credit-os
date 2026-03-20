"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ShieldWarning, Warning, CheckCircle, Lock } from "@phosphor-icons/react";
import AppShell from "@/components/layout/AppShell";
import RiskBadge from "@/components/cards/RiskBadge";
import SegmentBadge from "@/components/cards/SegmentBadge";
import StatusBadge from "@/components/cards/StatusBadge";
import MetricCard from "@/components/cards/MetricCard";
import MonospaceAmount from "@/components/financial/MonospaceAmount";
import DBRGauge from "@/components/financial/DBRGauge";
import IncomeTriangulationChart from "@/components/financial/IncomeTriangulationChart";
import ProvenanceBadge from "@/components/shared/ProvenanceBadge";
import { fetchApplication, resolveHITL } from "@/lib/api";
import { formatINR, formatConfidence, formatDocType, formatProductType } from "@/lib/formatters";
import type { ApplicationDetail, RiskFlag, ExtractionStatus } from "@/lib/types";

export default function DecisionBriefPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [app, setApp] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Decision form state
  const [decision, setDecision] = useState<"approve" | "reject" | null>(null);
  const [rationale, setRationale] = useState("");
  const [deviationType, setDeviationType] = useState("none");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    fetchApplication(id)
      .then(setApp)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async () => {
    if (!decision || rationale.length < 20) return;
    setSubmitting(true);
    try {
      await resolveHITL(id, {
        approved: decision === "approve",
        approver: "demo_officer",
        rationale,
      });
      setSubmitted(true);
      setTimeout(() => router.push("/hitl-queue"), 1500);
    } catch {
      setError("Failed to submit decision");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <AppShell title="Decision Brief">
        <div className="p-6 space-y-4">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-24 bg-bg-surface rounded border border-border-gold animate-[pulse-subtle_2s_ease-in-out_infinite]"
            />
          ))}
        </div>
      </AppShell>
    );
  }

  if (error || !app) {
    return (
      <AppShell title="Decision Brief">
        <div className="flex items-center justify-center h-64">
          <p className="text-risk-red text-[13px]">
            {error || "Application not found"}
          </p>
        </div>
      </AppShell>
    );
  }

  const result = app.result;
  const proposal = result?.proposal;
  const profile = proposal?.borrower_profile;
  const eligibility = proposal?.eligibility;
  const dbr = proposal?.dbr;
  const triangulation = proposal?.triangulation;
  const riskFlags = result?.risk_flags || [];
  const extractions = result?.extraction_results || {};
  const autoApprove = result?.auto_approve_eligible || false;

  const redFlags = riskFlags.filter((f) => f.level === "RED");
  const amberFlags = riskFlags.filter((f) => f.level === "AMBER");

  return (
    <AppShell title="Decision Brief" subtitle={`Application ${id.slice(0, 8)}`}>
      <div className="flex h-full">
        {/* Left column — The Evidence */}
        <div className="flex-[0_0_65%] overflow-y-auto p-6 space-y-6">
          {/* Borrower Header */}
          <div className="bg-bg-surface border border-border-gold rounded p-4 sticky top-0 z-10">
            <div className="flex items-baseline gap-3">
              <h3 className="font-serif text-2xl text-text-primary">
                {profile?.borrower_name || app.borrower_pan}
              </h3>
              <span className="font-mono text-[13px] text-text-secondary">
                {profile?.pan || app.borrower_pan}
              </span>
            </div>
            <div className="flex items-center gap-3 mt-2">
              {profile?.segment && <SegmentBadge segment={profile.segment} />}
              <span className="text-[13px] text-text-secondary">
                {formatProductType(app.product_type)}
              </span>
              {eligibility?.max_loan_amount ? (
                <MonospaceAmount amount={eligibility.max_loan_amount} className="text-accent-gold" />
              ) : null}
              {eligibility?.policy_version && (
                <span className="font-mono text-[10px] text-text-tertiary border border-border-gold-hover rounded px-1.5 py-0.5">
                  v{eligibility.policy_version}
                </span>
              )}
            </div>
          </div>

          {/* Risk Assessment */}
          <section>
            <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
              Risk Assessment
            </h4>
            {riskFlags.length === 0 ? (
              <div className="bg-risk-green-bg border border-risk-green/20 rounded p-4 flex items-center gap-3">
                <CheckCircle size={20} className="text-risk-green" weight="fill" />
                <span className="text-[13px] text-risk-green">
                  No risk flags — clean case
                </span>
              </div>
            ) : (
              <div className="space-y-2">
                {redFlags.length > 0 && (
                  <div className="bg-risk-red-bg border-l-2 border-risk-red rounded p-3 space-y-2">
                    {redFlags.map((flag) => (
                      <FlagItem key={flag.flag_id} flag={flag} />
                    ))}
                  </div>
                )}
                {amberFlags.length > 0 && (
                  <div className="bg-risk-amber-bg border-l-2 border-risk-amber rounded p-3 space-y-2">
                    {amberFlags.map((flag) => (
                      <FlagItem key={flag.flag_id} flag={flag} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Financial Summary */}
          {proposal && (
            <section>
              <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
                Financial Summary
              </h4>
              <div className="grid grid-cols-4 gap-3">
                <MetricCard
                  label="Monthly Income"
                  value={profile?.monthly_income ? formatINR(profile.monthly_income) : "N/A"}
                  subtext={profile?.income_sources?.[0]?.source || ""}
                />
                <MetricCard
                  label="Bureau Score"
                  value={
                    profile?.liabilities?.bureau_score
                      ? String(profile.liabilities.bureau_score)
                      : "N/A"
                  }
                  valueColor={
                    (profile?.liabilities?.bureau_score || 0) >= 720
                      ? "text-risk-green"
                      : (profile?.liabilities?.bureau_score || 0) >= 650
                        ? "text-risk-amber"
                        : "text-risk-red"
                  }
                  subtext="CIBIL"
                />
                <div className="bg-bg-surface border border-border-gold rounded p-4 flex flex-col items-center">
                  <p className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
                    DBR Ratio
                  </p>
                  <DBRGauge ratio={dbr?.dbr_ratio || 0} size={80} />
                </div>
                <MetricCard
                  label="Max Eligible Loan"
                  value={
                    eligibility?.is_eligible
                      ? formatINR(eligibility.max_loan_amount)
                      : "INELIGIBLE"
                  }
                  valueColor={
                    eligibility?.is_eligible ? "text-text-primary" : "text-risk-red"
                  }
                />
              </div>
            </section>
          )}

          {/* Income Triangulation */}
          {triangulation && profile?.income_sources && profile.income_sources.length > 0 && (
            <section>
              <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
                Income Triangulation
              </h4>
              <div className="bg-bg-surface border border-border-gold rounded p-4">
                <IncomeTriangulationChart
                  sources={profile.income_sources}
                  verifiedIncome={triangulation.verified_income}
                  confidence={triangulation.income_confidence}
                />
                {triangulation.discrepancies.length > 0 && (
                  <div className="mt-3 flex items-center gap-2 text-risk-amber text-[12px]">
                    <Warning size={14} />
                    Income mismatch detected — {triangulation.discrepancies[0]?.deviation} deviation across sources
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Document Extraction Results */}
          <section>
            <h4 className="text-[11px] text-text-tertiary uppercase tracking-[0.05em] mb-3">
              Document Extraction
            </h4>
            <div className="space-y-1">
              {Object.entries(extractions).map(([docType, ext]) => (
                <ExtractionRow key={docType} docType={docType} extraction={ext} />
              ))}
            </div>
          </section>
        </div>

        {/* Right column — The Decision */}
        <div className="flex-[0_0_35%] bg-bg-surface border-l border-border-gold p-6 flex flex-col">
          <div className="sticky top-0 space-y-6">
            {/* Recommendation */}
            <div
              className={`rounded p-4 border ${
                autoApprove
                  ? "bg-risk-green-bg border-risk-green/20"
                  : "bg-bg-elevated border-border-gold-hover"
              }`}
            >
              <p
                className={`text-[13px] font-medium ${
                  autoApprove ? "text-risk-green" : "text-text-secondary"
                }`}
              >
                {autoApprove
                  ? "AUTO-APPROVE ELIGIBLE"
                  : "MANUAL REVIEW REQUIRED"}
              </p>
              {!autoApprove && riskFlags.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {riskFlags.slice(0, 3).map((f) => (
                    <li
                      key={f.flag_id}
                      className="text-[11px] text-text-tertiary flex items-center gap-1.5"
                    >
                      <RiskBadge level={f.level} />
                      <span className="truncate">{f.description}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Decision Form */}
            {submitted ? (
              <div className="bg-risk-green-bg border border-risk-green/20 rounded p-4 text-center">
                <CheckCircle size={24} className="text-risk-green mx-auto" weight="fill" />
                <p className="text-[13px] text-risk-green mt-2">
                  Decision submitted. Redirecting...
                </p>
              </div>
            ) : (
              <>
                <div className="flex gap-2">
                  <button
                    onClick={() => setDecision("approve")}
                    className={`flex-1 py-2.5 rounded text-[13px] font-medium border transition-all duration-150 ${
                      decision === "approve"
                        ? "bg-accent-gold text-bg-primary border-accent-gold"
                        : "text-accent-gold border-accent-gold/30 hover:border-accent-gold/60"
                    }`}
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => setDecision("reject")}
                    className={`flex-1 py-2.5 rounded text-[13px] font-medium border transition-all duration-150 ${
                      decision === "reject"
                        ? "bg-risk-red text-text-primary border-risk-red"
                        : "text-risk-red border-risk-red/30 hover:border-risk-red/60"
                    }`}
                  >
                    Reject
                  </button>
                </div>

                <div>
                  <label className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
                    Decision Rationale
                  </label>
                  <textarea
                    value={rationale}
                    onChange={(e) => setRationale(e.target.value)}
                    placeholder="State your reasoning for this decision (mandatory per RBI Fair Practices Code)"
                    className="w-full mt-1 bg-bg-inset border border-border-gold rounded p-3 text-[13px] text-text-primary resize-none h-24 focus:outline-none focus:border-accent-gold-muted placeholder:text-text-tertiary"
                  />
                  <div className="flex justify-between mt-1">
                    <span
                      className={`text-[10px] font-mono ${
                        rationale.length >= 20
                          ? "text-text-tertiary"
                          : "text-risk-amber"
                      }`}
                    >
                      {rationale.length}/20 min characters
                    </span>
                  </div>
                </div>

                {decision === "approve" && amberFlags.length > 0 && (
                  <div>
                    <label className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
                      Deviation Type
                    </label>
                    <select
                      value={deviationType}
                      onChange={(e) => setDeviationType(e.target.value)}
                      className="w-full mt-1 bg-bg-inset border border-border-gold rounded p-2 text-[13px] text-text-primary focus:outline-none focus:border-accent-gold-muted"
                    >
                      <option value="none">None</option>
                      <option value="minor">Minor — within authority</option>
                      <option value="major">
                        Major — escalate to credit committee
                      </option>
                    </select>
                  </div>
                )}

                <button
                  onClick={handleSubmit}
                  disabled={
                    !decision || rationale.length < 20 || submitting
                  }
                  className="w-full py-2.5 rounded text-[13px] font-medium border border-accent-gold text-accent-gold hover:bg-accent-gold hover:text-bg-primary transition-all duration-150 disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  {submitting ? "Submitting..." : "Submit Decision"}
                </button>
              </>
            )}

            {/* Audit Trail */}
            <div className="flex items-start gap-2 text-[11px] text-text-tertiary border-t border-border-gold pt-4">
              <Lock size={14} className="shrink-0 mt-0.5" />
              <p>
                This decision will be logged with your ID, timestamp, policy
                version {eligibility?.policy_version || "—"}, and full
                rationale. Decision cannot be reversed after 24 hours.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function FlagItem({ flag }: { flag: RiskFlag }) {
  const Icon = flag.level === "RED" ? ShieldWarning : Warning;
  return (
    <div className="flex items-start gap-2">
      <Icon
        size={16}
        className={flag.level === "RED" ? "text-risk-red" : "text-risk-amber"}
        weight="fill"
      />
      <div className="flex-1 min-w-0">
        <p className="text-[13px] text-text-primary">{flag.description}</p>
        <ProvenanceBadge agentName={flag.source_agent} />
      </div>
    </div>
  );
}

function ExtractionRow({
  docType,
  extraction,
}: {
  docType: string;
  extraction: { agent_name?: string; status?: string; confidence?: number; data?: Record<string, unknown> };
}) {
  const [expanded, setExpanded] = useState(false);
  const status = (extraction.status || "failure") as ExtractionStatus;

  return (
    <div className="bg-bg-surface border border-border-gold rounded">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-left hover:bg-bg-elevated transition-colors"
      >
        <div className="flex items-center gap-3">
          <StatusBadge status={status} />
          <span className="text-[13px] text-text-primary">
            {formatDocType(docType)}
          </span>
        </div>
        <div className="flex items-center gap-3">
          {extraction.confidence !== undefined && (
            <span className="font-mono text-[11px] text-text-tertiary">
              {formatConfidence(extraction.confidence)}
            </span>
          )}
          <span className="text-text-tertiary text-[11px]">
            {expanded ? "▲" : "▼"}
          </span>
        </div>
      </button>
      {expanded && extraction.data && (
        <div className="px-4 pb-3 border-t border-border-gold">
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2">
            {Object.entries(extraction.data).map(([key, value]) => (
              <div key={key} className="flex items-baseline gap-2">
                <span className="text-[11px] text-text-tertiary w-32 shrink-0">
                  {key}
                </span>
                <span className="font-mono text-[12px] text-text-primary truncate">
                  {String(value)}
                </span>
              </div>
            ))}
          </div>
          {extraction.agent_name && (
            <div className="mt-2">
              <ProvenanceBadge
                agentName={extraction.agent_name}
                confidence={extraction.confidence}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
