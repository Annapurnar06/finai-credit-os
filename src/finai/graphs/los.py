"""LOS LangGraph orchestration — the main loan origination pipeline.

Architecture:
  Document Submission → Classification → Parallel Extraction (Send API)
  → Coordinator → Sequential Proposal → HITL Gate → Decision

Per Pandhi: 'Queue → run → checkpoint → reconcile → validate → commit'
"""
from __future__ import annotations

from typing import Any

import structlog
from langgraph.graph import END, StateGraph
from langgraph.types import Send

from finai.agents.extraction.agents import (
    DOCUMENT_TYPE_TO_AGENT,
    classify_document,
)
from finai.agents.proposal.agents import (
    check_mandatory_documents,
    compute_dbr,
    compute_roi,
    evaluate_eligibility,
    generate_proposal_data,
    triangulate_income,
)
from finai.core.hitl import compile_decision_brief
from finai.core.models import ApplicationStatus, RiskFlag, RiskLevel
from finai.core.policy import PolicyEngine
from finai.core.state import LOSState

logger = structlog.get_logger()


# --- Node functions ---

async def classify_documents(state: LOSState) -> dict[str, Any]:
    """Classify all submitted documents into types."""
    documents = state.get("documents", [])
    classifications: dict[str, str] = {}

    for doc in documents:
        doc_id = doc.get("id", "")
        content = doc.get("content_text", "") or doc.get("filename", "")
        doc_type = await classify_document(content[:3000])
        classifications[doc_id] = doc_type
        logger.info("document_classified", doc_id=doc_id, doc_type=doc_type)

    return {
        "classification_results": classifications,
        "status": ApplicationStatus.EXTRACTING.value,
    }


def route_to_extractors(state: LOSState) -> list[Send]:
    """Fire all relevant extraction agents in parallel via LangGraph Send()."""
    classifications = state.get("classification_results", {})
    documents = state.get("documents", [])
    sends: list[Send] = []

    doc_map = {d["id"]: d for d in documents}

    for doc_id, doc_type in classifications.items():
        if doc_type in DOCUMENT_TYPE_TO_AGENT and doc_id in doc_map:
            doc = doc_map[doc_id]
            sends.append(Send("extract_document", {
                "document_id": doc_id,
                "document_type": doc_type,
                "content": doc.get("content_text", ""),
                "application_id": state.get("application_id", ""),
                "borrower_id": state.get("borrower_id", ""),
            }))

    if not sends:
        sends.append(Send("extract_document", {
            "document_id": "none",
            "document_type": "unknown",
            "content": "",
        }))

    return sends


async def extract_document(state: dict[str, Any]) -> dict[str, Any]:
    """Single document extraction node — called in parallel via Send()."""
    doc_type = state.get("document_type", "unknown")
    content = state.get("content", "")
    agent_fn = DOCUMENT_TYPE_TO_AGENT.get(doc_type)
    if not agent_fn or not content:
        return {
            "extraction_results": {doc_type: {
                "status": "failure",
                "confidence": 0.0,
                "data": {},
                "errors": [f"No agent for document type: {doc_type}"],
            }},
        }

    result = await agent_fn(
        content=content,
        application_id=state.get("application_id"),
        borrower_id=state.get("borrower_id"),
    )

    return {
        "extraction_results": {doc_type: result.model_dump()},
    }


async def aggregate_extractions(state: LOSState) -> dict[str, Any]:
    """Coordinator node — aggregates parallel extraction results."""
    results = state.get("extraction_results", {})
    errors: list[str] = []
    risk_flags: list[dict[str, Any]] = []

    for doc_type, result in results.items():
        if result.get("status") == "failure":
            errors.append(f"Extraction failed for {doc_type}: {result.get('errors', [])}")
        elif result.get("status") == "low_confidence":
            risk_flags.append(RiskFlag(
                category="extraction",
                level=RiskLevel.AMBER,
                description=f"Low confidence extraction for {doc_type} ({result.get('confidence', 0):.0%})",
                source_agent=result.get("agent_name", doc_type),
            ).model_dump())

    return {
        "extraction_errors": errors,
        "risk_flags": risk_flags,
        "status": ApplicationStatus.EXTRACTION_COMPLETE.value,
    }


async def generate_proposal(state: LOSState) -> dict[str, Any]:
    """Run the 6-agent proposal generation pipeline sequentially."""
    extraction_results = state.get("extraction_results", {})

    # 1. Proposal data generation
    proposal_result = await generate_proposal_data(extraction_results)
    proposal_data = proposal_result.data

    # 2. Eligibility evaluation
    product_type = "personal_loan"  # Default, would come from application
    eligibility_result = await evaluate_eligibility(proposal_data, product_type)

    # 3. DBR computation
    bureau_data = extraction_results.get("credit_bureau", {}).get("data")
    dbr_result = await compute_dbr(proposal_data, bureau_data)

    # 4. ROI computation
    requested_amount = proposal_data.get("monthly_income", 0) * 24  # Default 2-year income
    roi_result = await compute_roi(proposal_data, requested_amount)

    # 5. Income triangulation
    triangulation_result = await triangulate_income(extraction_results, proposal_data)

    # 6. Mandatory document check
    segment = proposal_data.get("segment", "salaried")
    doc_check_result = await check_mandatory_documents(
        extraction_results, product_type, segment
    )

    # Compile risk flags from all agents
    risk_flags: list[dict[str, Any]] = list(state.get("risk_flags", []))
    for result in [dbr_result, roi_result, triangulation_result]:
        for flag_text in result.data.get("flags", []):
            risk_flags.append(RiskFlag(
                category="proposal",
                level=RiskLevel.AMBER,
                description=flag_text,
                source_agent=result.agent_name,
            ).model_dump())

    if not eligibility_result.data.get("is_eligible"):
        risk_flags.append(RiskFlag(
            category="eligibility",
            level=RiskLevel.RED,
            description="Borrower does not meet eligibility criteria",
            source_agent="EligibilityEvaluator",
            details={"reasons": eligibility_result.data.get("rejection_reasons", [])},
        ).model_dump())

    if not doc_check_result.data.get("complete"):
        risk_flags.append(RiskFlag(
            category="documentation",
            level=RiskLevel.AMBER,
            description=f"Missing documents: {doc_check_result.data.get('missing', [])}",
            source_agent="MandatoryDocCheckAgent",
        ).model_dump())

    # Check auto-approval eligibility
    policy_engine = PolicyEngine()
    red_flags = [f for f in risk_flags if f.get("level") == "RED"]
    auto_approve = policy_engine.check_auto_approval(
        product_type, segment,
        {
            "bureau_score": proposal_data.get("liabilities", {}).get("bureau_score", 0),
            "dbr": dbr_result.data.get("dbr_ratio", 1.0),
        },
        [f.get("description", "") for f in red_flags],
    )

    return {
        "proposal": {
            "borrower_profile": proposal_data,
            "eligibility": eligibility_result.data,
            "dbr": dbr_result.data,
            "roi": roi_result.data,
            "triangulation": triangulation_result.data,
            "doc_check": doc_check_result.data,
        },
        "eligibility": eligibility_result.data,
        "dbr_profile": dbr_result.data,
        "triangulation": triangulation_result.data,
        "missing_documents": doc_check_result.data.get("missing", []),
        "risk_flags": risk_flags,
        "auto_approve_eligible": auto_approve,
        "status": ApplicationStatus.PROPOSAL_GENERATED.value,
        "policy_version": eligibility_result.data.get("policy_version", ""),
    }


def route_after_proposal(state: LOSState) -> str:
    """Route to auto-approval or HITL review based on risk assessment."""
    if state.get("auto_approve_eligible", False):
        return "auto_approve"
    return "hitl_review"


async def auto_approve(state: LOSState) -> dict[str, Any]:
    """Auto-approve clean cases with full audit trail."""
    return {
        "status": ApplicationStatus.APPROVED.value,
        "final_decision": "approved",
        "hitl_required": False,
        "decision_brief": compile_decision_brief(
            state.get("extraction_results", {}),
            state.get("proposal"),
            state.get("risk_flags", []),
            state.get("policy_version", ""),
        ),
    }


async def hitl_review(state: LOSState) -> dict[str, Any]:
    """Flag for human-in-the-loop review."""
    brief = compile_decision_brief(
        state.get("extraction_results", {}),
        state.get("proposal"),
        state.get("risk_flags", []),
        state.get("policy_version", ""),
    )

    return {
        "status": ApplicationStatus.HITL_PENDING.value,
        "hitl_required": True,
        "decision_brief": brief,
    }


# --- Graph Construction ---

def build_los_graph() -> StateGraph:
    """Build the LOS LangGraph pipeline.

    Flow:
      classify_documents → route_to_extractors (parallel Send)
      → extract_document (N parallel) → aggregate_extractions
      → generate_proposal → route (auto_approve | hitl_review)
    """
    graph = StateGraph(LOSState)

    # Nodes
    graph.add_node("classify_documents", classify_documents)
    graph.add_node("extract_document", extract_document)
    graph.add_node("aggregate_extractions", aggregate_extractions)
    graph.add_node("generate_proposal", generate_proposal)
    graph.add_node("auto_approve", auto_approve)
    graph.add_node("hitl_review", hitl_review)

    # Edges
    graph.set_entry_point("classify_documents")
    graph.add_conditional_edges("classify_documents", route_to_extractors)
    graph.add_edge("extract_document", "aggregate_extractions")
    graph.add_edge("aggregate_extractions", "generate_proposal")
    graph.add_conditional_edges(
        "generate_proposal",
        route_after_proposal,
        {"auto_approve": "auto_approve", "hitl_review": "hitl_review"},
    )
    graph.add_edge("auto_approve", END)
    graph.add_edge("hitl_review", END)

    return graph


def get_los_app():
    """Get a compiled LOS application ready to invoke."""
    graph = build_los_graph()
    return graph.compile()
