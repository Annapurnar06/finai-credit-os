"""FINAI Credit OS — FastAPI application."""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from finai.api.routes.applications import router as applications_router
from finai.api.routes.health import router as health_router
from finai.api.routes.hitl import router as hitl_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("finai_starting", version="0.1.0")
    await _seed_demo_data()
    yield
    logger.info("finai_shutting_down")


async def _seed_demo_data() -> None:
    """Auto-load 4 demo borrower profiles on startup."""
    import uuid

    from demo.scenarios.borrower_profiles import ALL_SCENARIOS

    from finai.api.routes.applications import _applications, _run_los_pipeline

    for scenario_key, scenario in ALL_SCENARIOS.items():
        app_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"finai-demo-{scenario_key}"))
        borrower_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"finai-borrower-{scenario['pan']}"))

        documents = [
            {
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"doc-{scenario_key}-{i}")),
                "filename": doc["filename"],
                "doc_type": doc.get("doc_type", "unknown"),
                "content_text": doc["content_text"],
            }
            for i, doc in enumerate(scenario["documents"])
        ]

        _applications[app_id] = {
            "application_id": app_id,
            "borrower_id": borrower_id,
            "borrower_pan": scenario["pan"],
            "product_type": scenario.get("product_type", "personal_loan"),
            "requested_amount": scenario.get("requested_amount", 0),
            "status": "documents_submitted",
            "documents": documents,
            "result": None,
        }

        await _run_los_pipeline(app_id)
        logger.info("demo_seed_complete", scenario=scenario_key, app_id=app_id[:8])


app = FastAPI(
    title="FINAI Credit OS",
    description="AI-Native Lending Operations Platform — GrāmCredit AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(applications_router, prefix="/api/v1", tags=["applications"])
app.include_router(hitl_router, prefix="/api/v1", tags=["hitl"])
