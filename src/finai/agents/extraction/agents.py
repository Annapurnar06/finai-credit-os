"""Document extraction agents for the FINAI Credit OS LOS pipeline.

Each agent processes a specific Indian financial document type and extracts
structured data using LLM calls via the shared ``run_extraction_agent`` runner.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

from finai.agents.base import run_extraction_agent
from finai.core.llm import get_llm_router
from finai.core.models import AgentResult, DocumentType

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# 1. Document classifier — uses LLM directly (no extraction schema)
# ---------------------------------------------------------------------------

_CLASSIFICATION_PROMPT = (
    "You are a document classification agent for an Indian lending platform.\n"
    "Classify the following document into exactly ONE of these categories:\n"
    "pan, aadhaar, bank_statement, salary_slip, itr, gst_return, credit_bureau, "
    "collateral, utility_bill, passbook, coi, passport_dl, property_doc, "
    "cashflow_statement, insurance_policy, email_attachment, unknown.\n\n"
    "Reply with ONLY the category string (e.g. 'pan'). No explanation."
)


async def classify_document(content: str) -> str:
    """Classify a document into a :class:`DocumentType` using the LLM.

    Returns the string value of the matching ``DocumentType`` enum member,
    falling back to ``'unknown'`` when the LLM response is not recognised.
    """
    llm = get_llm_router()
    result = await llm.complete(
        messages=[{"role": "user", "content": content[:3000]}],
        task="classification",
        system=_CLASSIFICATION_PROMPT,
        max_tokens=64,
        temperature=0.0,
    )
    raw = result.get("content", "").strip().lower().strip("'\"")
    # Validate against the enum
    valid_values = {dt.value for dt in DocumentType}
    return raw if raw in valid_values else DocumentType.UNKNOWN.value


# ---------------------------------------------------------------------------
# 2. PAN Card extraction
# ---------------------------------------------------------------------------

_PAN_SCHEMA = json.dumps({
    "pan_number": "string — 10-character alphanumeric PAN (e.g. ABCDE1234F)",
    "name": "string — full name as printed on the PAN card",
    "dob": "string — date of birth in YYYY-MM-DD format",
    "fathers_name": "string — father's name as printed, or null",
    "status": "string — 'active' or 'inactive' if determinable, else null",
})

_PAN_SYSTEM = (
    "You are a PAN card extraction agent for an Indian lending platform.\n"
    "Extract data from the provided PAN card text/OCR content.\n"
    "PAN follows the pattern: 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F).\n"
    "Dates should be normalised to YYYY-MM-DD. Names should be in title case."
)


async def extract_pan(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from a PAN card document."""
    return await run_extraction_agent(
        agent_name="extract_pan",
        doc_type=DocumentType.PAN.value,
        content=content,
        extraction_schema=_PAN_SCHEMA,
        system_prompt=_PAN_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# 3. Aadhaar extraction
# ---------------------------------------------------------------------------

_AADHAAR_SCHEMA = json.dumps({
    "uid_masked": "string — last 4 digits of Aadhaar shown as XXXX-XXXX-1234",
    "name": "string — full name as printed on Aadhaar",
    "dob": "string — date of birth in YYYY-MM-DD format, or year of birth",
    "gender": "string — 'Male', 'Female', or 'Other'",
    "address": "string — full address as printed on Aadhaar",
})

_AADHAAR_SYSTEM = (
    "You are an Aadhaar card extraction agent for an Indian lending platform.\n"
    "Extract data from the Aadhaar card text/OCR content.\n"
    "IMPORTANT: For privacy, always mask the UID — return only the last 4 digits "
    "in the format XXXX-XXXX-1234. Never return the full 12-digit UID.\n"
    "Normalise dates to YYYY-MM-DD. Preserve the full address as-is."
)


async def extract_aadhaar(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from an Aadhaar card document."""
    return await run_extraction_agent(
        agent_name="extract_aadhaar",
        doc_type=DocumentType.AADHAAR.value,
        content=content,
        extraction_schema=_AADHAAR_SCHEMA,
        system_prompt=_AADHAAR_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# 4. Bank statement extraction (most complex)
# ---------------------------------------------------------------------------

_BANK_STATEMENT_SCHEMA = json.dumps({
    "account_number": "string — bank account number",
    "bank_name": "string — name of the bank",
    "period": "string — statement period, e.g. '2024-01 to 2024-06'",
    "transactions_summary": {
        "total_credits": "number — total credits in INR",
        "total_debits": "number — total debits in INR",
        "transaction_count": "integer — number of transactions",
    },
    "avg_monthly_balance": "number — average monthly balance in INR",
    "salary_credits": [
        {
            "month": "string — YYYY-MM",
            "amount": "number — credited amount in INR",
            "source": "string — employer/source name if identifiable",
        }
    ],
    "emi_outflows": [
        {
            "description": "string — EMI description or beneficiary",
            "amount": "number — EMI amount in INR",
            "frequency": "string — 'monthly' or 'quarterly'",
        }
    ],
})

_BANK_STATEMENT_SYSTEM = (
    "You are a bank statement analysis agent for an Indian lending platform.\n"
    "Extract structured data from the bank statement text. Focus on:\n"
    "1. Identify salary credits — regular monthly credits from employers (look for "
    "NEFT/RTGS/IMPS credits with employer names or 'SALARY' narration).\n"
    "2. Identify EMI outflows — recurring debits labelled 'EMI', 'LOAN', or to "
    "known NBFC/bank loan accounts. Report amounts in INR.\n"
    "3. Compute average monthly balance from opening/closing balances across months.\n"
    "4. Summarise total credits and debits in INR.\n"
    "All monetary values must be in INR (Indian Rupees). Do not convert currencies."
)


async def extract_bank_statement(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from a bank statement."""
    return await run_extraction_agent(
        agent_name="extract_bank_statement",
        doc_type=DocumentType.BANK_STATEMENT.value,
        content=content,
        extraction_schema=_BANK_STATEMENT_SCHEMA,
        system_prompt=_BANK_STATEMENT_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# 5. Salary slip extraction
# ---------------------------------------------------------------------------

_SALARY_SLIP_SCHEMA = json.dumps({
    "gross_salary": "number — gross salary in INR",
    "net_salary": "number — net (take-home) salary in INR",
    "employer_name": "string — employer/company name",
    "epf_deduction": "number — EPF (Employee Provident Fund) deduction in INR",
    "esi_deduction": "number — ESI (Employee State Insurance) deduction in INR, or 0 if N/A",
    "hra": "number — House Rent Allowance component in INR",
})

_SALARY_SLIP_SYSTEM = (
    "You are a salary slip extraction agent for an Indian lending platform.\n"
    "Extract pay components from the salary slip / payslip text.\n"
    "Look for standard Indian payroll components:\n"
    "- Basic Salary, HRA (House Rent Allowance), DA (Dearness Allowance)\n"
    "- EPF (Employee Provident Fund), ESI (Employee State Insurance), PT (Professional Tax)\n"
    "- Gross salary = sum of all earnings; Net salary = gross minus all deductions.\n"
    "All amounts must be in INR. If a deduction is not present, return 0."
)


async def extract_salary_slip(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from a salary slip."""
    return await run_extraction_agent(
        agent_name="extract_salary_slip",
        doc_type=DocumentType.SALARY_SLIP.value,
        content=content,
        extraction_schema=_SALARY_SLIP_SCHEMA,
        system_prompt=_SALARY_SLIP_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# 6. ITR extraction
# ---------------------------------------------------------------------------

_ITR_SCHEMA = json.dumps({
    "gross_total_income": "number — gross total income in INR as filed",
    "tax_paid": "number — total tax paid in INR",
    "assessment_year": "string — e.g. '2024-25'",
    "itr_form_type": "string — ITR form number, e.g. 'ITR-1', 'ITR-3', 'ITR-4'",
    "business_income": "number — income from business/profession in INR, or 0 if salaried",
})

_ITR_SYSTEM = (
    "You are an ITR (Income Tax Return) extraction agent for an Indian lending platform.\n"
    "Extract fields from the ITR acknowledgement or filed return text.\n"
    "Key details to extract:\n"
    "- Gross Total Income (GTI) as declared under all heads.\n"
    "- Total tax paid including TDS, advance tax, and self-assessment tax.\n"
    "- Assessment Year in the format YYYY-YY (e.g. 2024-25).\n"
    "- ITR form type: ITR-1 (salaried), ITR-3 (business), ITR-4 (presumptive), etc.\n"
    "- Business income under Section 44AD/44ADA if applicable, else 0.\n"
    "All amounts in INR."
)


async def extract_itr(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from an ITR document."""
    return await run_extraction_agent(
        agent_name="extract_itr",
        doc_type=DocumentType.ITR.value,
        content=content,
        extraction_schema=_ITR_SCHEMA,
        system_prompt=_ITR_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# 7. GST return extraction
# ---------------------------------------------------------------------------

_GST_RETURN_SCHEMA = json.dumps({
    "gstin": "string — 15-character GSTIN (e.g. 27AABCU9603R1ZM)",
    "turnover_12m": "number — total turnover for last 12 months in INR",
    "itc_claimed": "number — Input Tax Credit claimed in INR",
    "filing_regularity_score": "number — 0.0 to 1.0 score (1.0 = all months filed on time)",
    "gstr_type": "string — e.g. 'GSTR-1', 'GSTR-3B', 'GSTR-9'",
})

_GST_RETURN_SYSTEM = (
    "You are a GST return extraction agent for an Indian lending platform.\n"
    "Extract fields from the GST return / GSTIN data.\n"
    "Key details:\n"
    "- GSTIN: 15-character alphanumeric identifier (state code + PAN + entity number + checksum).\n"
    "- Turnover: aggregate taxable turnover over the last 12 months in INR.\n"
    "- ITC (Input Tax Credit) claimed in the period.\n"
    "- Filing regularity: assess how consistently returns were filed on time; "
    "score 1.0 if all filed on time, 0.0 if none filed.\n"
    "- GSTR type: which return form (GSTR-1, GSTR-3B, GSTR-9, etc.).\n"
    "All amounts in INR."
)


async def extract_gst_return(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from a GST return."""
    return await run_extraction_agent(
        agent_name="extract_gst_return",
        doc_type=DocumentType.GST_RETURN.value,
        content=content,
        extraction_schema=_GST_RETURN_SCHEMA,
        system_prompt=_GST_RETURN_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# 8. Credit bureau report extraction
# ---------------------------------------------------------------------------

_CREDIT_BUREAU_SCHEMA = json.dumps({
    "score": "integer — credit score (CIBIL/Experian/CRIF, typically 300-900)",
    "dpd_history": "string — days-past-due summary, e.g. '000 000 000 030 000' for last 5 months",
    "active_tradelines": "integer — number of active/open loan accounts",
    "enquiry_count_6m": "integer — number of credit enquiries in last 6 months",
    "total_outstanding": "number — total outstanding balance across all tradelines in INR",
})

_CREDIT_BUREAU_SYSTEM = (
    "You are a credit bureau report extraction agent for an Indian lending platform.\n"
    "Extract data from CIBIL / Experian / CRIF / Equifax report text.\n"
    "Key details:\n"
    "- Credit score: 3-digit score (300-900 range).\n"
    "- DPD (Days Past Due) history: summarise the DPD codes across recent months.\n"
    "- Active tradelines: count of currently open loan/credit card accounts.\n"
    "- Enquiry count (last 6 months): how many hard enquiries were made.\n"
    "- Total outstanding: sum of all current outstanding balances in INR.\n"
    "All monetary values in INR."
)


async def extract_credit_bureau(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from a credit bureau report."""
    return await run_extraction_agent(
        agent_name="extract_credit_bureau",
        doc_type=DocumentType.CREDIT_BUREAU.value,
        content=content,
        extraction_schema=_CREDIT_BUREAU_SCHEMA,
        system_prompt=_CREDIT_BUREAU_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# 9. Utility bill extraction
# ---------------------------------------------------------------------------

_UTILITY_BILL_SCHEMA = json.dumps({
    "account_holder": "string — name of the account holder / consumer",
    "address": "string — service address as printed on the bill",
    "bill_amount": "number — billed amount in INR",
    "consumption_pattern": "string — summary of recent consumption (e.g. 'avg 250 units/month over 3 months')",
})

_UTILITY_BILL_SYSTEM = (
    "You are a utility bill extraction agent for an Indian lending platform.\n"
    "Extract data from electricity / water / gas / telecom bill text.\n"
    "Key details:\n"
    "- Account holder name as printed on the bill.\n"
    "- Full service address (used for address verification / KYC).\n"
    "- Bill amount in INR.\n"
    "- Consumption pattern: summarise recent usage to gauge lifestyle/address stability.\n"
    "All amounts in INR."
)


async def extract_utility_bill(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from a utility bill."""
    return await run_extraction_agent(
        agent_name="extract_utility_bill",
        doc_type=DocumentType.UTILITY_BILL.value,
        content=content,
        extraction_schema=_UTILITY_BILL_SCHEMA,
        system_prompt=_UTILITY_BILL_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# 10. Bank passbook extraction
# ---------------------------------------------------------------------------

_BANK_PASSBOOK_SCHEMA = json.dumps({
    "account_number": "string — bank account number",
    "branch_ifsc": "string — IFSC code of the branch (e.g. SBIN0001234)",
    "balance": "number — latest available balance in INR",
    "transaction_summary": "string — brief summary of recent transactions (credits, debits, frequency)",
})

_BANK_PASSBOOK_SYSTEM = (
    "You are a bank passbook extraction agent for an Indian lending platform.\n"
    "Extract data from the bank passbook text/OCR.\n"
    "Key details:\n"
    "- Account number as printed on the passbook.\n"
    "- Branch IFSC code (11-character alphanumeric, e.g. SBIN0001234).\n"
    "- Latest available balance in INR.\n"
    "- Transaction summary: summarise recent transaction patterns — "
    "e.g. 'Regular salary credits of ~INR 50,000/month, EMI debits of INR 12,000'.\n"
    "All amounts in INR."
)


async def extract_bank_passbook(
    content: str,
    audit_log: Any = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Extract structured fields from a bank passbook."""
    return await run_extraction_agent(
        agent_name="extract_bank_passbook",
        doc_type=DocumentType.PASSBOOK.value,
        content=content,
        extraction_schema=_BANK_PASSBOOK_SCHEMA,
        system_prompt=_BANK_PASSBOOK_SYSTEM,
        audit_log=audit_log,
        application_id=application_id,
        borrower_id=borrower_id,
    )


# ---------------------------------------------------------------------------
# Document type → extraction agent mapping
# ---------------------------------------------------------------------------

DOCUMENT_TYPE_TO_AGENT: dict[
    DocumentType,
    Callable[..., Coroutine[Any, Any, AgentResult]],
] = {
    DocumentType.PAN: extract_pan,
    DocumentType.AADHAAR: extract_aadhaar,
    DocumentType.BANK_STATEMENT: extract_bank_statement,
    DocumentType.SALARY_SLIP: extract_salary_slip,
    DocumentType.ITR: extract_itr,
    DocumentType.GST_RETURN: extract_gst_return,
    DocumentType.CREDIT_BUREAU: extract_credit_bureau,
    DocumentType.UTILITY_BILL: extract_utility_bill,
    DocumentType.PASSBOOK: extract_bank_passbook,
}
