"""LangGraph state schemas — TypedDict per cluster.

Durable state persisted to PostgreSQL via LangGraph checkpoint store.
Per Pandhi: 'Work graph persists, runs are disposable.'
"""
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class ExtractionState(TypedDict, total=False):
    """State for a single document extraction sub-task (used with Send())."""
    document_id: str
    document_type: str
    content: str
    result: dict[str, Any]


class LOSState(TypedDict, total=False):
    """Main LOS pipeline state — shared across all nodes."""
    # Application identity
    application_id: str
    borrower_id: str

    # Document submission
    documents: list[dict[str, Any]]
    classification_results: dict[str, str]

    # Extraction (parallel agents write here, aggregated by reducer)
    extraction_results: Annotated[dict[str, Any], _merge_dicts]
    extraction_errors: Annotated[list[str], operator.add]

    # Proposal generation (sequential)
    proposal: dict[str, Any]
    eligibility: dict[str, Any]
    dbr_profile: dict[str, Any]
    triangulation: dict[str, Any]
    missing_documents: list[str]

    # Risk & policy
    risk_flags: Annotated[list[dict[str, Any]], operator.add]
    policy_version: str
    auto_approve_eligible: bool

    # HITL
    hitl_required: bool
    hitl_review_id: str
    hitl_decisions: list[dict[str, Any]]

    # Application status
    status: str
    final_decision: str
    decision_brief: dict[str, Any]


def _merge_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Merge extraction results from parallel agents."""
    merged = left.copy()
    merged.update(right)
    return merged
