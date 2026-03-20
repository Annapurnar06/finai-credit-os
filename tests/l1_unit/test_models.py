"""L1 unit tests for domain models."""
from __future__ import annotations

from finai.core.models import (
    AgentResult,
    ApplicationStatus,
    AuditEvent,
    CommitClass,
    DocumentType,
    ExtractionResult,
    RiskFlag,
    RiskLevel,
)


def test_commit_class_values():
    assert CommitClass.READ_ONLY.value == "R"
    assert CommitClass.SOFT_COMMIT.value == "S"
    assert CommitClass.HARD_COMMIT.value == "H"
    assert CommitClass.IRREVERSIBLE.value == "I"


def test_document_types():
    assert DocumentType.PAN.value == "pan"
    assert DocumentType.BANK_STATEMENT.value == "bank_statement"
    assert DocumentType.UNKNOWN.value == "unknown"


def test_agent_result():
    result = AgentResult(
        agent_name="PanDataAgent",
        status="success",
        confidence=0.95,
        data={"pan_number": "ABCDE1234F"},
    )
    assert result.agent_name == "PanDataAgent"
    assert result.confidence == 0.95


def test_risk_flag():
    flag = RiskFlag(
        category="eligibility",
        level=RiskLevel.RED,
        description="Bureau score below threshold",
        source_agent="CreditBureauAgent",
    )
    assert flag.level == RiskLevel.RED


def test_audit_event():
    event = AuditEvent(
        event_type="extraction.pan",
        agent_id="PanDataAgent",
        commit_class=CommitClass.READ_ONLY,
    )
    assert event.commit_class == CommitClass.READ_ONLY


def test_extraction_result():
    result = ExtractionResult(
        agent_name="PanDataAgent",
        doc_type=DocumentType.PAN,
        status="success",
        confidence=0.98,
        data={"pan_number": "ABCPS1234A"},
    )
    assert result.doc_type == DocumentType.PAN
