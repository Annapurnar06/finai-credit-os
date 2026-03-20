"""HITL gate primitives — Pandhi's 'Humans are the control plane'.

Wraps LangGraph interrupt() for clean HITL checkpoints.
Credit officer approval pauses the graph, resumes on confirmation.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import text

from finai.core.models import CommitClass, HITLDecision


class HITLGate:
    """Manages HITL review queue and decision tracking."""

    def __init__(self, session_factory: Any) -> None:
        self._session_factory = session_factory

    async def create_review(
        self,
        application_id: str,
        action_type: str,
        commit_class: CommitClass,
        decision_brief: dict[str, Any],
    ) -> str:
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    INSERT INTO hitl_queue
                    (application_id, action_type, commit_class, decision_brief)
                    VALUES (:app_id, :action_type, :commit_class, :brief::jsonb)
                    RETURNING id
                """),
                {
                    "app_id": application_id,
                    "action_type": action_type,
                    "commit_class": commit_class.value,
                    "brief": json.dumps(decision_brief),
                },
            )
            await session.commit()
            row = result.fetchone()
            return str(row[0]) if row else ""

    async def resolve_review(
        self,
        review_id: str,
        approved: bool,
        approver: str,
        rationale: str = "",
    ) -> HITLDecision:
        decision = {
            "approved": approved,
            "approver": approver,
            "rationale": rationale,
            "resolved_at": datetime.utcnow().isoformat(),
        }
        async with self._session_factory() as session:
            await session.execute(
                text("""
                    UPDATE hitl_queue
                    SET status = :status, assigned_to = :approver,
                        decision = :decision::jsonb, resolved_at = NOW()
                    WHERE id = :id
                """),
                {
                    "id": review_id,
                    "status": "approved" if approved else "rejected",
                    "approver": approver,
                    "decision": json.dumps(decision),
                },
            )
            await session.commit()

        return HITLDecision(
            id=review_id,
            action_type="review_resolution",
            commit_class=CommitClass.HARD_COMMIT,
            approver=approver,
            approved=approved,
            rationale=rationale,
            resolved_at=datetime.utcnow(),
        )

    async def get_pending_reviews(
        self, limit: int = 50
    ) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT hq.*, la.borrower_id, la.product_type, la.requested_amount
                    FROM hitl_queue hq
                    JOIN loan_applications la ON hq.application_id = la.id
                    WHERE hq.status = 'pending'
                    ORDER BY hq.created_at ASC
                    LIMIT :limit
                """),
                {"limit": limit},
            )
            return [dict(row._mapping) for row in result.fetchall()]

    async def get_review(self, review_id: str) -> dict[str, Any] | None:
        async with self._session_factory() as session:
            result = await session.execute(
                text("SELECT * FROM hitl_queue WHERE id = :id"),
                {"id": review_id},
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None


def compile_decision_brief(
    extraction_results: dict[str, Any],
    proposal: dict[str, Any] | None,
    risk_flags: list[dict[str, Any]],
    policy_version: str,
) -> dict[str, Any]:
    """Compile a 1-page decision brief for credit officer review."""
    red_flags = [f for f in risk_flags if f.get("level") == "RED"]
    amber_flags = [f for f in risk_flags if f.get("level") == "AMBER"]

    return {
        "summary": {
            "total_documents_processed": len(extraction_results),
            "risk_assessment": "HIGH" if red_flags else "MEDIUM" if amber_flags else "LOW",
            "red_flags_count": len(red_flags),
            "amber_flags_count": len(amber_flags),
        },
        "extraction_highlights": {
            k: {"status": v.get("status"), "confidence": v.get("confidence")}
            for k, v in extraction_results.items()
        },
        "proposal": proposal,
        "risk_flags": risk_flags,
        "policy_version": policy_version,
        "review_required_because": (
            [f["description"] for f in red_flags]
            + [f["description"] for f in amber_flags]
            + (["Manual review required per policy"] if not proposal else [])
        ),
    }
