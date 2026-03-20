"""Context compiler + entity graph — Pandhi's 'stitched reality'.

Borrower identity resolution across fragmented DPI data sources.
M1: PostgreSQL JSONB. M3: Neo4j AuraDB (drop-in replacement via same interface).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from sqlalchemy import text

# Field priority hierarchy: AA > GSTN > ITR > bank_statement > self_declared
FIELD_PRIORITY = {
    "aa": 100,
    "gstn": 90,
    "itr": 80,
    "bureau": 75,
    "bank_statement": 70,
    "salary_slip": 65,
    "utility_bill": 50,
    "self_declared": 10,
}


@dataclass
class FieldValue:
    value: Any
    source: str
    timestamp: datetime
    confidence: float = 1.0
    priority: int = 0


@dataclass
class CompiledContext:
    """Minimum-sufficient context compiled for an agent task."""
    borrower_id: str
    fields: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    policy_version: str = ""
    compiled_at: datetime = field(default_factory=datetime.utcnow)


class EntityGraph(Protocol):
    async def upsert_borrower(self, borrower_data: dict[str, Any]) -> str: ...
    async def get_borrower(self, borrower_id: str) -> dict[str, Any] | None: ...
    async def resolve_identity(self, pan: str | None = None, mobile_hash: str | None = None, aadhaar_hash: str | None = None) -> str | None: ...
    async def update_fields(self, borrower_id: str, fields: dict[str, Any], source: str, confidence: float) -> None: ...


class PostgresEntityGraph:
    """PG JSONB-backed entity graph. Same interface for Neo4j migration in M3."""

    def __init__(self, session_factory: Any) -> None:
        self._session_factory = session_factory

    async def upsert_borrower(self, borrower_data: dict[str, Any]) -> str:
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    INSERT INTO borrower_entities (pan, aadhaar_hash, mobile_hash, fields, provenance)
                    VALUES (:pan, :aadhaar_hash, :mobile_hash, :fields::jsonb, :provenance::jsonb)
                    ON CONFLICT (pan) DO UPDATE SET
                        fields = borrower_entities.fields || EXCLUDED.fields,
                        provenance = borrower_entities.provenance || EXCLUDED.provenance,
                        updated_at = NOW()
                    RETURNING id
                """),
                {
                    "pan": borrower_data.get("pan"),
                    "aadhaar_hash": borrower_data.get("aadhaar_hash"),
                    "mobile_hash": borrower_data.get("mobile_hash"),
                    "fields": json.dumps(borrower_data.get("fields", {})),
                    "provenance": json.dumps(borrower_data.get("provenance", [])),
                },
            )
            await session.commit()
            row = result.fetchone()
            return str(row[0]) if row else ""

    async def get_borrower(self, borrower_id: str) -> dict[str, Any] | None:
        async with self._session_factory() as session:
            result = await session.execute(
                text("SELECT * FROM borrower_entities WHERE id = :id"),
                {"id": borrower_id},
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None

    async def resolve_identity(
        self,
        pan: str | None = None,
        mobile_hash: str | None = None,
        aadhaar_hash: str | None = None,
    ) -> str | None:
        conditions = []
        params: dict[str, Any] = {}
        if pan:
            conditions.append("pan = :pan")
            params["pan"] = pan
        if mobile_hash:
            conditions.append("mobile_hash = :mobile_hash")
            params["mobile_hash"] = mobile_hash
        if aadhaar_hash:
            conditions.append("aadhaar_hash = :aadhaar_hash")
            params["aadhaar_hash"] = aadhaar_hash

        if not conditions:
            return None

        where = " OR ".join(conditions)
        async with self._session_factory() as session:
            result = await session.execute(
                text(f"SELECT id FROM borrower_entities WHERE {where} LIMIT 1"),
                params,
            )
            row = result.fetchone()
            return str(row[0]) if row else None

    async def update_fields(
        self,
        borrower_id: str,
        fields: dict[str, Any],
        source: str,
        confidence: float = 1.0,
    ) -> None:
        provenance_entry = {
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": confidence,
            "fields_updated": list(fields.keys()),
        }
        async with self._session_factory() as session:
            await session.execute(
                text("""
                    UPDATE borrower_entities
                    SET fields = fields || :fields::jsonb,
                        provenance = provenance || :provenance::jsonb,
                        updated_at = NOW()
                    WHERE id = :id
                """),
                {
                    "id": borrower_id,
                    "fields": json.dumps(fields),
                    "provenance": json.dumps([provenance_entry]),
                },
            )
            await session.commit()


class ContextCompiler:
    """Compiles minimum-sufficient context for an agent task.

    Per Pandhi: 'Context is a build artifact, not a prompt dump.'
    """

    def __init__(self, entity_graph: EntityGraph) -> None:
        self._graph = entity_graph

    async def compile(
        self,
        borrower_id: str,
        required_fields: list[str] | None = None,
        policy_version: str = "",
    ) -> CompiledContext:
        borrower = await self._graph.get_borrower(borrower_id)
        if not borrower:
            return CompiledContext(borrower_id=borrower_id, policy_version=policy_version)

        fields = borrower.get("fields", {})
        provenance_log = borrower.get("provenance", [])

        if required_fields:
            fields = {k: v for k, v in fields.items() if k in required_fields}

        provenance_map: dict[str, list[dict[str, Any]]] = {}
        for entry in provenance_log:
            for f in entry.get("fields_updated", []):
                provenance_map.setdefault(f, []).append(entry)

        return CompiledContext(
            borrower_id=borrower_id,
            fields=fields,
            provenance=provenance_map,
            policy_version=policy_version,
        )

    def resolve_field_conflict(self, values: list[FieldValue]) -> FieldValue:
        """Resolves conflicting field values using priority hierarchy."""
        for v in values:
            v.priority = FIELD_PRIORITY.get(v.source, 0)
        return max(values, key=lambda v: (v.priority, v.confidence, v.timestamp))
