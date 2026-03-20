"""Domain models — Pydantic schemas for the entire lending lifecycle."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

# --- Enums ---

class CommitClass(str, Enum):
    READ_ONLY = "R"
    SOFT_COMMIT = "S"
    HARD_COMMIT = "H"
    IRREVERSIBLE = "I"


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    DOCUMENTS_SUBMITTED = "documents_submitted"
    EXTRACTING = "extracting"
    EXTRACTION_COMPLETE = "extraction_complete"
    PROPOSAL_GENERATED = "proposal_generated"
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    HITL_PENDING = "hitl_pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RiskLevel(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class DocumentType(str, Enum):
    PAN = "pan"
    AADHAAR = "aadhaar"
    BANK_STATEMENT = "bank_statement"
    SALARY_SLIP = "salary_slip"
    ITR = "itr"
    GST_RETURN = "gst_return"
    CREDIT_BUREAU = "credit_bureau"
    COLLATERAL = "collateral"
    UTILITY_BILL = "utility_bill"
    PASSBOOK = "passbook"
    COI = "coi"
    PASSPORT_DL = "passport_dl"
    PROPERTY_DOC = "property_doc"
    CASHFLOW_STATEMENT = "cashflow_statement"
    INSURANCE_POLICY = "insurance_policy"
    EMAIL_ATTACHMENT = "email_attachment"
    UNKNOWN = "unknown"


class CustomerSegment(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    MSME = "msme"
    AGRICULTURE = "agriculture"
    GIG_WORKER = "gig_worker"


class ProductType(str, Enum):
    PERSONAL_LOAN = "personal_loan"
    BUSINESS_LOAN = "business_loan"
    LAP = "lap"  # Loan Against Property
    GOLD_LOAN = "gold_loan"
    AGRICULTURE_LOAN = "agriculture_loan"
    VEHICLE_LOAN = "vehicle_loan"


# --- Core Data Models ---

class ProvenanceRecord(BaseModel):
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = 1.0
    raw_value: Any = None
    normalized_value: Any = None
    api_response_id: str | None = None


class DocumentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    doc_type: DocumentType = DocumentType.UNKNOWN
    content_base64: str | None = None
    content_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ExtractionResult(BaseModel):
    agent_name: str
    doc_type: DocumentType
    status: Literal["success", "failure", "low_confidence"]
    confidence: float
    data: dict[str, Any] = Field(default_factory=dict)
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class RiskFlag(BaseModel):
    flag_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    level: RiskLevel
    description: str
    source_agent: str
    details: dict[str, Any] = Field(default_factory=dict)


class DBRProfile(BaseModel):
    total_monthly_emi: float = 0.0
    net_monthly_income: float = 0.0
    dbr_ratio: float = 0.0
    max_eligible_emi: float = 0.0
    active_loans: list[dict[str, Any]] = Field(default_factory=list)


class EligibilityResult(BaseModel):
    is_eligible: bool
    eligible_products: list[dict[str, Any]] = Field(default_factory=list)
    max_loan_amount: float = 0.0
    min_loan_amount: float = 0.0
    rate_band: dict[str, float] = Field(default_factory=dict)
    tenure_options: list[int] = Field(default_factory=list)
    rejection_reasons: list[str] = Field(default_factory=list)
    policy_version: str = ""


class TriangulationResult(BaseModel):
    declared_income: float = 0.0
    verified_income: float = 0.0
    income_confidence: float = 0.0
    sources_checked: list[str] = Field(default_factory=list)
    discrepancies: list[dict[str, Any]] = Field(default_factory=list)


class LoanProposal(BaseModel):
    borrower_name: str = ""
    borrower_segment: CustomerSegment = CustomerSegment.SALARIED
    product_type: ProductType = ProductType.PERSONAL_LOAN
    requested_amount: float = 0.0
    recommended_amount: float = 0.0
    income_summary: dict[str, Any] = Field(default_factory=dict)
    asset_summary: dict[str, Any] = Field(default_factory=dict)
    liability_summary: dict[str, Any] = Field(default_factory=dict)
    dbr_profile: DBRProfile | None = None
    eligibility: EligibilityResult | None = None
    triangulation: TriangulationResult | None = None
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    missing_documents: list[str] = Field(default_factory=list)
    policy_version: str = ""


class HITLDecision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    commit_class: CommitClass
    approver: str = ""
    approved: bool | None = None
    rationale: str = ""
    decision_brief: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: datetime | None = None


class AuditEvent(BaseModel):
    event_type: str
    agent_id: str = ""
    borrower_id: str | None = None
    loan_id: str | None = None
    application_id: str | None = None
    commit_class: CommitClass = CommitClass.READ_ONLY
    input_hash: str = ""
    output_hash: str = ""
    policy_version: str = ""
    model_id: str = ""
    latency_ms: int = 0
    trace_id: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


# --- Agent Result Protocol ---

class AgentResult(BaseModel):
    agent_name: str
    status: Literal["success", "failure", "low_confidence"]
    confidence: float = 1.0
    data: dict[str, Any] = Field(default_factory=dict)
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    latency_ms: int = 0
