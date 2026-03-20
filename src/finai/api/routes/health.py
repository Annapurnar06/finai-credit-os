"""Health check endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from finai.core.llm import get_llm_router
from finai.core.memory import get_memory

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, Any]:
    llm = get_llm_router()
    memory = get_memory()
    return {
        "status": "healthy",
        "service": "finai-credit-os",
        "version": "0.1.0",
        "llm_mode": llm.stats.get("mode", "live"),
        "memory_mode": memory.stats.get("mode", "unknown"),
    }


@router.get("/health/llm")
async def llm_health() -> dict[str, Any]:
    llm = get_llm_router()
    return {
        "status": "configured",
        "stats": llm.stats,
    }


@router.get("/health/memory")
async def memory_health() -> dict[str, Any]:
    memory = get_memory()
    return {
        "status": "configured",
        "stats": memory.stats,
    }
