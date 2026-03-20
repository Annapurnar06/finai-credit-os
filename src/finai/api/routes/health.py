"""Health check endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from finai.core.llm import get_llm_router

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "finai-credit-os",
        "version": "0.1.0",
    }


@router.get("/health/llm")
async def llm_health() -> dict[str, Any]:
    llm = get_llm_router()
    return {
        "status": "configured",
        "stats": llm.stats,
    }
