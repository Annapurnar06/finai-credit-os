"""Loan application endpoints — document submission, status, pipeline execution."""
from __future__ import annotations

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from finai.core.models import ApplicationStatus
from finai.graphs.los import get_los_app

logger = structlog.get_logger()
router = APIRouter()

# In-memory store for M1 demo (PostgreSQL in production)
_applications: dict[str, dict[str, Any]] = {}


class DocumentInput(BaseModel):
    filename: str
    doc_type: str = "unknown"
    content_text: str


class ApplicationCreateRequest(BaseModel):
    borrower_pan: str
    product_type: str = "personal_loan"
    requested_amount: float = 0
    documents: list[DocumentInput] = Field(default_factory=list)


class ApplicationResponse(BaseModel):
    application_id: str
    status: str
    message: str


@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    request: ApplicationCreateRequest,
    background_tasks: BackgroundTasks,
) -> ApplicationResponse:
    """Create a new loan application and start the LOS pipeline."""
    app_id = str(uuid.uuid4())
    borrower_id = str(uuid.uuid4())

    documents = [
        {
            "id": str(uuid.uuid4()),
            "filename": doc.filename,
            "doc_type": doc.doc_type,
            "content_text": doc.content_text,
        }
        for doc in request.documents
    ]

    _applications[app_id] = {
        "application_id": app_id,
        "borrower_id": borrower_id,
        "borrower_pan": request.borrower_pan,
        "product_type": request.product_type,
        "requested_amount": request.requested_amount,
        "status": ApplicationStatus.DOCUMENTS_SUBMITTED.value,
        "documents": documents,
        "result": None,
    }

    background_tasks.add_task(_run_los_pipeline, app_id)

    return ApplicationResponse(
        application_id=app_id,
        status="documents_submitted",
        message=f"Application created with {len(documents)} documents. Pipeline started.",
    )


async def _run_los_pipeline(app_id: str) -> None:
    """Execute the LOS LangGraph pipeline."""
    app_data = _applications.get(app_id)
    if not app_data:
        return

    try:
        los_app = get_los_app()
        initial_state = {
            "application_id": app_id,
            "borrower_id": app_data["borrower_id"],
            "documents": app_data["documents"],
        }

        result = await los_app.ainvoke(initial_state)

        _applications[app_id]["status"] = result.get("status", "unknown")
        _applications[app_id]["result"] = {
            k: v for k, v in result.items()
            if k not in ("documents",)  # Don't store raw doc content
        }

        logger.info(
            "los_pipeline_complete",
            application_id=app_id,
            status=result.get("status"),
            auto_approve=result.get("auto_approve_eligible"),
        )

    except Exception as e:
        logger.error("los_pipeline_failed", application_id=app_id, error=str(e))
        _applications[app_id]["status"] = "error"
        _applications[app_id]["result"] = {"error": str(e)}


@router.get("/applications/{application_id}")
async def get_application(application_id: str) -> dict[str, Any]:
    """Get application status and results."""
    app = _applications.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return {
        "application_id": app["application_id"],
        "borrower_pan": app["borrower_pan"],
        "product_type": app["product_type"],
        "status": app["status"],
        "result": app.get("result"),
    }


@router.get("/applications")
async def list_applications() -> list[dict[str, Any]]:
    """List all applications."""
    return [
        {
            "application_id": app["application_id"],
            "borrower_pan": app["borrower_pan"],
            "status": app["status"],
            "product_type": app["product_type"],
        }
        for app in _applications.values()
    ]
