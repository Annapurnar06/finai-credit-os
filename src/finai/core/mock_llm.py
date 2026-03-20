"""Mock LLM router — pre-computed extraction results for zero-API-key demo.

When ANTHROPIC_API_KEY is empty, this replaces the real LLM router.
Returns deterministic, realistic extraction results for the 4 demo
borrower profiles (Savitri, Rajan, Meera, Prakash) based on content matching.
Swap to real Claude by setting the API key — no other code changes needed.
"""
from __future__ import annotations

import json
import time
from typing import Any

import structlog

logger = structlog.get_logger()

# Pre-computed extraction results keyed by document content fingerprints
_MOCK_CLASSIFICATIONS: dict[str, str] = {
    "permanent account number": "pan",
    "pan:": "pan",
    "aadhaar": "aadhaar",
    "bank statement": "bank_statement",
    "account statement": "bank_statement",
    "salary slip": "salary_slip",
    "itr-1": "itr",
    "itr-2": "itr",
    "itr-3": "itr",
    "income tax return": "itr",
    "gstr": "gst_return",
    "gstin": "gst_return",
    "gst certificate": "gst_return",
    "utility": "utility_bill",
    "electricity": "utility_bill",
    "passbook": "passbook",
    "cibil": "credit_bureau",
    "credit information report": "credit_bureau",
    "experian": "credit_bureau",
    "equifax": "credit_bureau",
}

_MOCK_EXTRACTIONS: dict[str, dict[str, Any]] = {
    # --- Rajan (salaried_clean) ---
    "pan__DEFPR5678B": {
        "pan_number": "DEFPR5678B",
        "name": "RAJAN KRISHNAMURTHY",
        "dob": "15/03/1985",
        "fathers_name": "VENKATESH KRISHNAMURTHY",
        "status": "valid",
    },
    "bank_statement__50100248975631": {
        "account_number": "50100248975631",
        "bank_name": "HDFC BANK",
        "ifsc": "HDFC0001234",
        "period": "March 2025 - February 2026",
        "avg_monthly_balance": 203000,
        "salary_credits": 85000,
        "employer_detected": "TCS Ltd",
        "emi_outflows": 12000,
        "bounce_count": 0,
        "cash_deposit_ratio": 0.05,
        "transactions_summary": "12 months, regular salary credits",
    },
    "salary_slip__TCS": {
        "gross_salary": 85000,
        "net_salary": 72900,
        "employer_name": "TCS LIMITED",
        "employee_id": "TCS-CBE-45678",
        "epf_deduction": 5400,
        "esi_deduction": 0,
        "hra": 18000,
        "professional_tax": 200,
        "income_tax": 6500,
    },

    "credit_bureau__DEFPR5678B": {
        "score": 765,
        "dpd_history": [],
        "active_tradelines": 1,
        "enquiry_count_6m": 2,
        "total_outstanding": 180000,
        "total_emi": 12000,
        "oldest_tradeline_months": 48,
        "write_offs": 0,
        "settlements": 0,
    },

    # --- Savitri (msme_seasonal) ---
    "pan__ABCPS1234A": {
        "pan_number": "ABCPS1234A",
        "name": "SAVITRI BAI PATIL",
        "dob": "20/08/1978",
        "fathers_name": "RAMESH PATIL",
        "status": "valid",
    },
    "passbook__20198765432": {
        "account_number": "20198765432",
        "bank_name": "BANK OF MAHARASHTRA",
        "branch_ifsc": "MAHB0001456",
        "avg_monthly_balance": 15200,
        "cash_deposit_pattern": "seasonal_higher_oct_dec",
        "upi_transaction_count_monthly": 45,
        "salary_credits": 0,
        "emi_outflows": 0,
        "bounce_count": 0,
        "balance_trend": "growing",
    },
    "utility_bill__savitri": {
        "account_holder": "SAVITRI BAI PATIL",
        "address": "Plot 45, Itwari Market, Nagpur - 440002",
        "bill_amount": 1850,
        "units_consumed": 185,
        "bill_period": "January 2026",
        "payment_status": "PAID",
        "consumption_pattern": "residential_small_commercial",
    },

    # --- Meera (gig_worker) ---
    "pan__GHIMK9012C": {
        "pan_number": "GHIMK9012C",
        "name": "MEERA SRINIVASAN",
        "dob": "12/06/1992",
        "fathers_name": "KRISHNA SRINIVASAN",
        "status": "valid",
    },
    "bank_statement__98765432100": {
        "account_number": "98765432100",
        "bank_name": "KOTAK MAHINDRA BANK",
        "ifsc": "KKBK0005678",
        "period": "March 2025 - February 2026",
        "avg_monthly_balance": 100000,
        "salary_credits": 0,
        "employer_detected": None,
        "emi_outflows": 5000,
        "bounce_count": 1,
        "cash_deposit_ratio": 0.10,
        "income_pattern": "gig_multiple_sources",
        "credit_sources": ["Swiggy", "Urban Company", "Freelance UPI"],
        "avg_monthly_credits": 48200,
    },
    "credit_bureau__GHIMK9012C": {
        "score": 680,
        "dpd_history": [{"month": "Jun-2025", "dpd": 5}],
        "active_tradelines": 2,
        "enquiry_count_6m": 4,
        "total_outstanding": 45000,
        "total_emi": 5000,
        "oldest_tradeline_months": 18,
        "write_offs": 0,
        "settlements": 0,
    },
    "itr__GHIMK9012C": {
        "gross_total_income": 540000,
        "income_from_salary": 0,
        "income_from_other_sources": 540000,
        "deductions_80c": 50000,
        "total_income": 490000,
        "tax_paid": 12500,
        "assessment_year": "2025-26",
        "itr_form_type": "ITR-1",
        "filing_date": "28-Jul-2025",
    },

    # --- Prakash (first_time_borrower) ---
    "pan__JKLPN3456D": {
        "pan_number": "JKLPN3456D",
        "name": "PRAKASH KUMAR YADAV",
        "dob": "05/11/1988",
        "fathers_name": "SURESH YADAV",
        "status": "valid",
    },
    "bank_statement__38776543210": {
        "account_number": "38776543210",
        "bank_name": "STATE BANK OF INDIA",
        "ifsc": "SBIN0009876",
        "period": "September 2025 - February 2026",
        "avg_monthly_balance": 27000,
        "salary_credits": 0,
        "employer_detected": None,
        "emi_outflows": 0,
        "bounce_count": 0,
        "upi_merchant_credits": 18000,
        "cash_deposits": 10000,
        "mobile_recharge_regular": True,
        "avg_monthly_credits": 28700,
    },
    "gst_return__09JKLPN3456D1ZP": {
        "gstin": "09JKLPN3456D1ZP",
        "trade_name": "YADAV KIRANA STORE",
        "legal_name": "PRAKASH KUMAR YADAV",
        "registration_date": "01-Apr-2024",
        "composition_scheme": True,
        "turnover_12m": 1850000,
        "tax_payable": 18500,
        "tax_paid": 18500,
        "filing_regularity_score": 1.0,
        "quarterly_trend": {
            "Q1": 380000,
            "Q2": 420000,
            "Q3": 550000,
            "Q4": 500000,
        },
        "gstr_type": "GSTR-4",
    },
}


def _find_mock_classification(content: str) -> str:
    """Classify document using keyword matching with priority ordering.

    More specific keywords (e.g. 'credit information report') are checked
    before generic ones (e.g. 'pan:') to avoid false matches.
    """
    lower = content.lower()
    # Priority order: check specific/longer keywords first
    priority_keywords = sorted(_MOCK_CLASSIFICATIONS.keys(), key=len, reverse=True)
    for keyword in priority_keywords:
        if keyword in lower:
            return _MOCK_CLASSIFICATIONS[keyword]
    return "unknown"


def _find_mock_extraction(doc_type: str, content: str) -> dict[str, Any] | None:
    """Match content to a pre-computed extraction result."""
    for key, data in _MOCK_EXTRACTIONS.items():
        if not key.startswith(doc_type + "__"):
            continue
        identifier = key.split("__")[1]
        if identifier.lower() in content.lower():
            return data

    # Fallback: match by doc_type prefix if only one entry
    matches = [v for k, v in _MOCK_EXTRACTIONS.items() if k.startswith(doc_type + "__")]
    # Try to match by any PAN/account number in content
    for key, data in _MOCK_EXTRACTIONS.items():
        if not key.startswith(doc_type + "__"):
            continue
        # Check if any value from the data appears in the content
        for val in data.values():
            if isinstance(val, str) and len(val) > 5 and val.upper() in content.upper():
                return data

    return matches[0] if len(matches) == 1 else None


class MockLLMRouter:
    """Deterministic mock LLM for zero-API-key demo runs."""

    def __init__(self) -> None:
        self._call_count = 0
        self._total_tokens = 0

    async def complete(
        self,
        messages: list[dict[str, Any]],
        task: str = "default",
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.0,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        start = time.monotonic()
        self._call_count += 1

        content_text = ""
        for msg in messages:
            if isinstance(msg.get("content"), str):
                content_text += msg["content"]

        # Classification task
        if task == "classification" or "classify" in system.lower():
            result_text = _find_mock_classification(content_text)
        else:
            result_text = '{"mock": true, "note": "Mock LLM - set ANTHROPIC_API_KEY for real extraction"}'

        latency_ms = int((time.monotonic() - start) * 1000)
        self._total_tokens += len(content_text.split()) + len(result_text.split())

        logger.info("mock_llm_call", task=task, result_preview=result_text[:80])

        return {
            "content": result_text,
            "model": "mock-llm-v1",
            "input_tokens": len(content_text.split()),
            "output_tokens": len(result_text.split()),
            "latency_ms": latency_ms,
            "stop_reason": "end_turn",
        }

    async def extract_structured(
        self,
        content: str,
        schema_description: str,
        task: str = "extraction_fast",
        system: str = "",
    ) -> dict[str, Any]:
        start = time.monotonic()
        self._call_count += 1

        # Determine doc_type from system prompt or schema
        doc_type = _find_mock_classification(content)

        # Find matching pre-computed result
        mock_data = _find_mock_extraction(doc_type, content)
        if mock_data is None:
            mock_data = {"mock": True, "doc_type": doc_type, "note": "No mock data matched"}

        latency_ms = int((time.monotonic() - start) * 1000)
        self._total_tokens += len(content.split()) + 50

        logger.info("mock_extraction", doc_type=doc_type, fields=len(mock_data))

        return {
            "content": json.dumps(mock_data),
            "parsed": mock_data,
            "model": "mock-llm-v1",
            "input_tokens": len(content.split()),
            "output_tokens": 50,
            "latency_ms": latency_ms,
            "stop_reason": "end_turn",
        }

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "total_calls": self._call_count,
            "total_tokens": self._total_tokens,
            "mode": "mock",
        }
