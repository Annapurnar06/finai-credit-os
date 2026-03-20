"""Base agent protocol — every agent follows this pattern.

Agents are stateless functions: read state → call tools → return typed result.
Per Anthropic best practices: Orchestrator-Worker pattern with tool use.

Memory integration: every extraction auto-stores results in Mem0 for
cross-agent knowledge sharing and borrower memory compounding.
"""
from __future__ import annotations

import time
from typing import Any

import structlog

from finai.core.audit import PostgresAuditLog, compute_hash
from finai.core.llm import get_llm_router
from finai.core.memory import get_memory
from finai.core.models import AgentResult, AuditEvent, CommitClass, ProvenanceRecord

logger = structlog.get_logger()


async def run_extraction_agent(
    agent_name: str,
    doc_type: str,
    content: str,
    extraction_schema: str,
    system_prompt: str,
    audit_log: PostgresAuditLog | None = None,
    application_id: str | None = None,
    borrower_id: str | None = None,
) -> AgentResult:
    """Generic extraction agent runner. All 17 extraction agents use this pattern."""
    start = time.monotonic()
    llm = get_llm_router()

    try:
        result = await llm.extract_structured(
            content=content,
            schema_description=extraction_schema,
            task="extraction_fast",
            system=system_prompt,
        )

        parsed = result.get("parsed", {})
        has_error = parsed.get("parse_error", False)
        confidence = 0.0 if has_error else _compute_confidence(parsed)

        agent_result = AgentResult(
            agent_name=agent_name,
            status="failure" if has_error else ("low_confidence" if confidence < 0.85 else "success"),
            confidence=confidence,
            data=parsed,
            provenance=[
                ProvenanceRecord(
                    source=agent_name,
                    confidence=confidence,
                    raw_value=content[:200],
                    normalized_value=parsed,
                )
            ],
            errors=["Failed to parse LLM response"] if has_error else [],
            latency_ms=result.get("latency_ms", 0),
        )

        # Store extraction result in borrower memory (Mem0 / fallback)
        if borrower_id and agent_result.status == "success":
            memory = get_memory()
            await memory.remember_fact(
                borrower_id=borrower_id,
                fact=f"{agent_name} extracted {doc_type}: {_summarize_extraction(parsed)}",
                source_agent=agent_name,
                category=f"extraction.{doc_type}",
            )

        if audit_log:
            await audit_log.append(AuditEvent(
                event_type=f"extraction.{doc_type}",
                agent_id=agent_name,
                borrower_id=borrower_id,
                application_id=application_id,
                commit_class=CommitClass.READ_ONLY,
                input_hash=compute_hash(content[:500]),
                output_hash=compute_hash(parsed),
                model_id=result.get("model", ""),
                latency_ms=result.get("latency_ms", 0),
                payload={"status": agent_result.status, "confidence": confidence},
            ))

        return agent_result

    except Exception as e:
        latency = int((time.monotonic() - start) * 1000)
        logger.error("agent_failed", agent=agent_name, error=str(e))
        return AgentResult(
            agent_name=agent_name,
            status="failure",
            confidence=0.0,
            errors=[str(e)],
            latency_ms=latency,
        )


def _summarize_extraction(parsed: dict[str, Any]) -> str:
    """Create a short summary of extraction for memory storage."""
    parts = []
    for key, val in parsed.items():
        if val is not None and val != "" and val != [] and not isinstance(val, dict):
            parts.append(f"{key}={val}")
        if len(parts) >= 5:
            break
    return ", ".join(parts) if parts else "no fields extracted"


def _compute_confidence(parsed: dict[str, Any]) -> float:
    """Compute extraction confidence based on field completeness."""
    if not parsed:
        return 0.0
    total = len(parsed)
    non_null = sum(1 for v in parsed.values() if v is not None and v != "" and v != [])
    return round(non_null / total, 2) if total > 0 else 0.0
