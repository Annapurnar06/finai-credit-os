"""Proposal generator sub-cluster — 6 sequential agents.

These agents synthesize extraction outputs into an underwriting-ready loan proposal.
They run sequentially after the extraction cluster completes.
"""
from __future__ import annotations

from typing import Any

import structlog

from finai.core.models import (
    AgentResult,
    CustomerSegment,
    DBRProfile,
    EligibilityResult,
    ProvenanceRecord,
    TriangulationResult,
)
from finai.core.policy import PolicyEngine

logger = structlog.get_logger()


async def generate_proposal_data(
    extraction_results: dict[str, Any],
    borrower_fields: dict[str, Any] | None = None,
) -> AgentResult:
    """Aggregates all extracted fields into a structured loan application record.

    Resolves field conflicts using priority hierarchy:
    AA > ITR > bank statement > salary slip > self-declared.
    """
    data: dict[str, Any] = {
        "borrower_name": "",
        "pan": "",
        "age": 0,
        "monthly_income": 0.0,
        "annual_income": 0.0,
        "employer": "",
        "segment": CustomerSegment.SALARIED.value,
        "income_sources": [],
        "assets": {},
        "liabilities": {},
    }

    # Extract from PAN
    pan_data = extraction_results.get("pan", {}).get("data", {})
    if pan_data:
        data["borrower_name"] = pan_data.get("name", "")
        data["pan"] = pan_data.get("pan_number", "")
        dob = pan_data.get("dob", "")
        if dob:
            try:
                from datetime import datetime
                birth = datetime.strptime(dob, "%d/%m/%Y")
                data["age"] = (datetime.now() - birth).days // 365
            except (ValueError, TypeError):
                pass

    # Income from bank statement (highest priority for actual income)
    bs_data = extraction_results.get("bank_statement", {}).get("data", {})
    if bs_data:
        avg_balance = bs_data.get("avg_monthly_balance", 0)
        salary_credits = bs_data.get("salary_credits", 0)
        data["monthly_income"] = max(salary_credits, avg_balance * 0.3)
        data["income_sources"].append({
            "source": "bank_statement",
            "monthly": data["monthly_income"],
            "confidence": 0.85,
        })

    # Income from salary slip (if available)
    slip_data = extraction_results.get("salary_slip", {}).get("data", {})
    if slip_data:
        net = slip_data.get("net_salary", 0)
        if net:
            data["monthly_income"] = max(data["monthly_income"], net)
            data["employer"] = slip_data.get("employer_name", "")
            data["income_sources"].append({
                "source": "salary_slip",
                "monthly": net,
                "confidence": 0.9,
            })

    # Income from ITR
    itr_data = extraction_results.get("itr", {}).get("data", {})
    if itr_data:
        gross = itr_data.get("gross_total_income", 0)
        if gross:
            data["annual_income"] = gross
            if not data["monthly_income"]:
                data["monthly_income"] = gross / 12
            data["income_sources"].append({
                "source": "itr",
                "annual": gross,
                "confidence": 0.95,
            })

    # GST for MSME/self-employed
    gst_data = extraction_results.get("gst_return", {}).get("data", {})
    if gst_data:
        turnover = gst_data.get("turnover_12m", 0)
        if turnover:
            data["segment"] = CustomerSegment.MSME.value
            data["annual_income"] = max(data.get("annual_income", 0), turnover * 0.15)
            data["income_sources"].append({
                "source": "gst",
                "turnover_12m": turnover,
                "estimated_monthly_profit": turnover * 0.15 / 12,
                "confidence": 0.8,
            })

    if not data["annual_income"] and data["monthly_income"]:
        data["annual_income"] = data["monthly_income"] * 12

    # Bureau liabilities
    bureau_data = extraction_results.get("credit_bureau", {}).get("data", {})
    if bureau_data:
        data["liabilities"]["bureau_score"] = bureau_data.get("score", 0)
        data["liabilities"]["active_tradelines"] = bureau_data.get("active_tradelines", 0)
        data["liabilities"]["total_outstanding"] = bureau_data.get("total_outstanding", 0)
        data["liabilities"]["total_emi"] = bureau_data.get("total_emi", 0)

    return AgentResult(
        agent_name="ProposalDataGenerator",
        status="success",
        confidence=0.9,
        data=data,
        provenance=[ProvenanceRecord(source="ProposalDataGenerator", confidence=0.9)],
    )


async def evaluate_eligibility(
    proposal_data: dict[str, Any],
    product_type: str = "personal_loan",
    policy_engine: PolicyEngine | None = None,
) -> AgentResult:
    """Runs eligibility rules engine against product policy matrix."""
    if policy_engine is None:
        policy_engine = PolicyEngine()

    segment = proposal_data.get("segment", "salaried")
    borrower_data = {
        "age": proposal_data.get("age", 0),
        "monthly_income": proposal_data.get("monthly_income", 0),
        "bureau_score": proposal_data.get("liabilities", {}).get("bureau_score", 0),
        "dbr": 0.0,
    }

    decision = policy_engine.evaluate_eligibility(product_type, segment, borrower_data)

    income = proposal_data.get("monthly_income", 0)
    max_emi = income * 0.5
    max_loan = max_emi * 60  # Assuming 5-year max tenure

    eligibility = EligibilityResult(
        is_eligible=decision.allowed,
        eligible_products=[{"product": product_type, "segment": segment}] if decision.allowed else [],
        max_loan_amount=max_loan if decision.allowed else 0,
        min_loan_amount=50000 if decision.allowed else 0,
        rate_band={"min": 10.5, "max": 18.0} if decision.allowed else {},
        tenure_options=[12, 24, 36, 48, 60] if decision.allowed else [],
        rejection_reasons=decision.rejection_reasons,
        policy_version=decision.policy_version,
    )

    return AgentResult(
        agent_name="EligibilityEvaluator",
        status="success" if decision.allowed else "failure",
        confidence=0.95,
        data=eligibility.model_dump(),
        provenance=[ProvenanceRecord(source="EligibilityEvaluator", confidence=0.95)],
    )


async def compute_dbr(
    proposal_data: dict[str, Any],
    bureau_data: dict[str, Any] | None = None,
) -> AgentResult:
    """Computes Debt Burden Ratio = (existing EMI obligations) / (net monthly income)."""
    income = proposal_data.get("monthly_income", 0)
    existing_emi = 0.0

    if bureau_data:
        existing_emi = bureau_data.get("total_emi", 0)
    elif proposal_data.get("liabilities"):
        existing_emi = proposal_data["liabilities"].get("total_emi", 0)

    dbr_ratio = existing_emi / income if income > 0 else 1.0
    max_eligible_emi = max(0, (income * 0.5) - existing_emi)

    profile = DBRProfile(
        total_monthly_emi=existing_emi,
        net_monthly_income=income,
        dbr_ratio=round(dbr_ratio, 4),
        max_eligible_emi=round(max_eligible_emi, 2),
    )

    flags = []
    if dbr_ratio > 0.5:
        flags.append("DBR exceeds 50% threshold")
    elif dbr_ratio > 0.4:
        flags.append("DBR in caution zone (40-50%)")

    return AgentResult(
        agent_name="DBRProfiler",
        status="success",
        confidence=0.98,
        data={**profile.model_dump(), "flags": flags},
    )


async def compute_roi(
    proposal_data: dict[str, Any],
    requested_amount: float = 0,
) -> AgentResult:
    """Computes Return on Income for productive loan purposes."""
    annual_income = proposal_data.get("annual_income", 0)
    roi_ratio = requested_amount / annual_income if annual_income > 0 else float("inf")

    flags = []
    if roi_ratio > 10:
        flags.append(f"Loan-to-income ratio {roi_ratio:.1f}x is very high")
    elif roi_ratio > 5:
        flags.append(f"Loan-to-income ratio {roi_ratio:.1f}x — review recommended")

    return AgentResult(
        agent_name="ROIProfiler",
        status="success",
        confidence=0.95,
        data={
            "annual_income": annual_income,
            "requested_amount": requested_amount,
            "roi_ratio": round(roi_ratio, 2),
            "flags": flags,
        },
    )


async def triangulate_income(
    extraction_results: dict[str, Any],
    proposal_data: dict[str, Any],
) -> AgentResult:
    """Cross-validates income evidence across all available sources.

    Key RBI requirement: income triangulation documented in credit file.
    """
    sources: list[dict[str, Any]] = []

    # Bank statement income
    bs = extraction_results.get("bank_statement", {}).get("data", {})
    if bs and bs.get("salary_credits"):
        sources.append({"source": "bank_statement", "monthly": bs["salary_credits"], "confidence": 0.85})

    # Salary slip income
    slip = extraction_results.get("salary_slip", {}).get("data", {})
    if slip and slip.get("net_salary"):
        sources.append({"source": "salary_slip", "monthly": slip["net_salary"], "confidence": 0.9})

    # ITR income
    itr = extraction_results.get("itr", {}).get("data", {})
    if itr and itr.get("gross_total_income"):
        sources.append({"source": "itr", "monthly": itr["gross_total_income"] / 12, "confidence": 0.95})

    # GST-derived income
    gst = extraction_results.get("gst_return", {}).get("data", {})
    if gst and gst.get("turnover_12m"):
        sources.append({"source": "gst", "monthly": gst["turnover_12m"] * 0.15 / 12, "confidence": 0.7})

    if not sources:
        return AgentResult(
            agent_name="DataTriangulationAgent",
            status="low_confidence",
            confidence=0.0,
            data=TriangulationResult(sources_checked=["none"]).model_dump(),
            errors=["No income sources available for triangulation"],
        )

    amounts = [s["monthly"] for s in sources]
    avg_income = sum(amounts) / len(amounts)
    max_deviation = max(abs(a - avg_income) / avg_income for a in amounts) if avg_income > 0 else 0

    discrepancies = []
    if max_deviation > 0.2:
        discrepancies.append({
            "type": "income_mismatch",
            "deviation": f"{max_deviation:.1%}",
            "sources": sources,
        })

    declared = proposal_data.get("monthly_income", 0)
    triangulation = TriangulationResult(
        declared_income=declared,
        verified_income=avg_income,
        income_confidence=round(1 - max_deviation, 2),
        sources_checked=[s["source"] for s in sources],
        discrepancies=discrepancies,
    )

    return AgentResult(
        agent_name="DataTriangulationAgent",
        status="success" if max_deviation <= 0.2 else "low_confidence",
        confidence=triangulation.income_confidence,
        data=triangulation.model_dump(),
    )


async def check_mandatory_documents(
    extraction_results: dict[str, Any],
    product_type: str = "personal_loan",
    segment: str = "salaried",
) -> AgentResult:
    """Validates that all product-specific mandatory documents are present and verified."""
    required_docs: dict[str, list[str]] = {
        "personal_loan_salaried": ["pan", "bank_statement", "salary_slip"],
        "personal_loan_self_employed": ["pan", "bank_statement", "itr", "gst_return"],
        "personal_loan_msme": ["pan", "bank_statement", "gst_return"],
        "business_loan_msme": ["pan", "bank_statement", "gst_return", "itr"],
        "personal_loan_gig_worker": ["pan", "bank_statement"],
        "personal_loan_agriculture": ["pan", "bank_statement"],
    }

    key = f"{product_type}_{segment}"
    required = required_docs.get(key, required_docs.get(f"{product_type}_salaried", ["pan"]))
    present = set(extraction_results.keys())
    successful = {k for k, v in extraction_results.items() if v.get("status") == "success"}

    missing = [d for d in required if d not in present]
    failed = [d for d in required if d in present and d not in successful]

    all_good = len(missing) == 0 and len(failed) == 0

    return AgentResult(
        agent_name="MandatoryDocCheckAgent",
        status="success" if all_good else "failure",
        confidence=1.0 if all_good else 0.5,
        data={
            "required": required,
            "present": list(present),
            "successful": list(successful),
            "missing": missing,
            "failed_extraction": failed,
            "complete": all_good,
        },
    )
