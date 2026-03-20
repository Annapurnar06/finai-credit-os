"""Append-only audit log — PostgreSQL-backed (Kafka replacement for M1).

Every agent decision, tool call, HITL approval, and state transition is logged here.
Same interface contracts — Kafka producer slot in M4.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, Protocol

from sqlalchemy import text

from finai.core.models import AuditEvent


class AuditLogger(Protocol):
    async def append(self, event: AuditEvent) -> None: ...

    async def query(
        self,
        borrower_id: str | None = None,
        application_id: str | None = None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]: ...


class PostgresAuditLog:
    """Append-only audit log backed by PostgreSQL.

    Designed for RBI 7-year retention. Immutable — no UPDATE or DELETE operations.
    """

    def __init__(self, session_factory: Any) -> None:
        self._session_factory = session_factory

    async def append(self, event: AuditEvent) -> None:
        async with self._session_factory() as session:
            await session.execute(
                text("""
                    INSERT INTO audit_events
                    (event_type, agent_id, borrower_id, loan_id, application_id,
                     commit_class, input_hash, output_hash, policy_version,
                     model_id, latency_ms, trace_id, payload)
                    VALUES
                    (:event_type, :agent_id, :borrower_id, :loan_id, :application_id,
                     :commit_class, :input_hash, :output_hash, :policy_version,
                     :model_id, :latency_ms, :trace_id, :payload::jsonb)
                """),
                {
                    "event_type": event.event_type,
                    "agent_id": event.agent_id,
                    "borrower_id": event.borrower_id,
                    "loan_id": event.loan_id,
                    "application_id": event.application_id,
                    "commit_class": event.commit_class.value,
                    "input_hash": event.input_hash,
                    "output_hash": event.output_hash,
                    "policy_version": event.policy_version,
                    "model_id": event.model_id,
                    "latency_ms": event.latency_ms,
                    "trace_id": event.trace_id,
                    "payload": json.dumps(event.payload),
                },
            )
            await session.commit()

    async def query(
        self,
        borrower_id: str | None = None,
        application_id: str | None = None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": limit}

        if borrower_id:
            conditions.append("borrower_id = :borrower_id")
            params["borrower_id"] = borrower_id
        if application_id:
            conditions.append("application_id = :application_id")
            params["application_id"] = application_id
        if event_type:
            conditions.append("event_type = :event_type")
            params["event_type"] = event_type
        if since:
            conditions.append("created_at >= :since")
            params["since"] = since

        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM audit_events {where} ORDER BY created_at DESC LIMIT :limit"

        async with self._session_factory() as session:
            result = await session.execute(text(query), params)
            return [dict(row._mapping) for row in result.fetchall()]


def compute_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, default=str, sort_keys=True).encode()).hexdigest()[:16]
