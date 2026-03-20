"""HITL review queue endpoints — credit officer workspace."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# In-memory HITL queue for M1 demo
_hitl_queue: dict[str, dict[str, Any]] = {}


class HITLResolveRequest(BaseModel):
    approved: bool
    approver: str
    rationale: str = ""


@router.get("/hitl/queue")
async def get_hitl_queue() -> list[dict[str, Any]]:
    """Get pending HITL reviews for credit officer."""
    return [
        item for item in _hitl_queue.values()
        if item.get("status") == "pending"
    ]


@router.get("/hitl/{review_id}")
async def get_hitl_review(review_id: str) -> dict[str, Any]:
    """Get a specific HITL review with decision brief."""
    review = _hitl_queue.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/hitl/{review_id}/resolve")
async def resolve_hitl_review(
    review_id: str,
    request: HITLResolveRequest,
) -> dict[str, Any]:
    """Credit officer resolves a HITL review."""
    review = _hitl_queue.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review["status"] != "pending":
        raise HTTPException(status_code=400, detail="Review already resolved")

    review["status"] = "approved" if request.approved else "rejected"
    review["approver"] = request.approver
    review["rationale"] = request.rationale

    return {"status": "resolved", "decision": review["status"]}
