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
    yield
    logger.info("finai_shutting_down")


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
