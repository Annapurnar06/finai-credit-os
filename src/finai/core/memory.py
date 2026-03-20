"""Borrower memory layer — Mem0 integration.

Three memory types per Pandhi + ALOP spec:
- Episodic: per-borrower interaction history (calls, chats, document submissions)
- Semantic: extracted facts (income patterns, family context, preferences)
- Procedural: lender-specific rules discovered during operations

When MEM0_API_KEY is not set, falls back to an in-memory store for local dev.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog

from finai.config import get_settings

logger = structlog.get_logger()


class BorrowerMemory:
    """Persistent memory layer for borrower interactions and agent knowledge."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client: Any = None
        self._fallback: dict[str, list[dict[str, Any]]] = {}
        self._is_mock = True

        mem0_credential = settings.mem0_api_key
        if mem0_credential:
            try:
                self._client = _create_mem0_client(mem0_credential)
                self._is_mock = False
                logger.info("mem0_init", mode="live")
            except Exception as e:
                logger.warning("mem0_init_failed", error=str(e), fallback="in_memory")
        else:
            logger.info("mem0_init", mode="in_memory", note="Set MEM0_API_KEY for persistent memory")

    async def remember(
        self,
        borrower_id: str,
        messages: list[dict[str, str]],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store borrower interaction context.

        Args:
            borrower_id: Unique borrower identifier (PAN or UUID).
            messages: List of {"role": "user"|"assistant", "content": "..."} messages.
            metadata: Additional context (channel, agent_id, application_id).
        """
        meta = {
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }

        if self._client and not self._is_mock:
            try:
                self._client.add(messages, user_id=borrower_id, metadata=meta)
                logger.info("mem0_remember", borrower_id=borrower_id, messages=len(messages))
            except Exception as e:
                logger.error("mem0_remember_failed", error=str(e))
                self._store_fallback(borrower_id, messages, meta)
        else:
            self._store_fallback(borrower_id, messages, meta)

    async def recall(
        self,
        borrower_id: str,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant borrower memories for agent context compilation.

        Args:
            borrower_id: Unique borrower identifier.
            query: Semantic search query (e.g., "income history", "loan purpose").
            limit: Maximum number of memories to return.
        """
        if self._client and not self._is_mock:
            try:
                results = self._client.search(
                    query, filters={"user_id": borrower_id}, limit=limit
                )
                logger.info("mem0_recall", borrower_id=borrower_id, query=query[:50], results=len(results.get("results", [])))
                return results.get("results", [])
            except Exception as e:
                logger.error("mem0_recall_failed", error=str(e))
                return self._search_fallback(borrower_id, query, limit)
        else:
            return self._search_fallback(borrower_id, query, limit)

    async def remember_fact(
        self,
        borrower_id: str,
        fact: str,
        source_agent: str,
        category: str = "general",
    ) -> None:
        """Store a specific fact about a borrower (semantic memory).

        Used by agents to persist insights discovered during processing:
        - "Seasonal income pattern — higher Oct-Dec"
        - "Husband works at mandal office"
        - "Prefers Marathi communication"
        """
        await self.remember(
            borrower_id=borrower_id,
            messages=[
                {"role": "assistant", "content": f"[{category}] {fact}"},
            ],
            metadata={
                "source_agent": source_agent,
                "category": category,
                "memory_type": "semantic",
            },
        )

    async def remember_interaction(
        self,
        borrower_id: str,
        channel: str,
        summary: str,
        agent_id: str,
        application_id: str = "",
    ) -> None:
        """Store an interaction episode (episodic memory).

        Called after voice calls, chat sessions, document submissions.
        """
        await self.remember(
            borrower_id=borrower_id,
            messages=[
                {"role": "assistant", "content": f"[interaction:{channel}] {summary}"},
            ],
            metadata={
                "channel": channel,
                "agent_id": agent_id,
                "application_id": application_id,
                "memory_type": "episodic",
            },
        )

    async def get_borrower_context(
        self,
        borrower_id: str,
        task_description: str = "",
    ) -> dict[str, Any]:
        """Compile full memory context for an agent about to process a borrower.

        Returns a dict ready to inject into the agent's system prompt or context.
        """
        memories = await self.recall(borrower_id, task_description or "borrower history", limit=10)

        return {
            "borrower_id": borrower_id,
            "memory_count": len(memories),
            "memories": [
                {
                    "content": m.get("memory", m.get("content", "")),
                    "score": m.get("score", 0),
                    "created_at": m.get("created_at", ""),
                }
                for m in memories
            ],
            "has_prior_interactions": len(memories) > 0,
        }

    def _store_fallback(
        self,
        borrower_id: str,
        messages: list[dict[str, str]],
        metadata: dict[str, Any],
    ) -> None:
        if borrower_id not in self._fallback:
            self._fallback[borrower_id] = []
        self._fallback[borrower_id].append({
            "messages": messages,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def _search_fallback(
        self,
        borrower_id: str,
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        entries = self._fallback.get(borrower_id, [])
        query_lower = query.lower()
        scored = []
        for entry in entries:
            content = " ".join(m.get("content", "") for m in entry["messages"])
            # Simple keyword overlap scoring
            words = set(query_lower.split())
            overlap = sum(1 for w in words if w in content.lower())
            score = overlap / max(len(words), 1)
            scored.append({
                "memory": content,
                "score": score,
                "created_at": entry.get("timestamp", ""),
                "metadata": entry.get("metadata", {}),
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "mode": "mem0" if not self._is_mock else "in_memory",
            "fallback_borrowers": len(self._fallback),
            "fallback_total_memories": sum(len(v) for v in self._fallback.values()),
        }


def _create_mem0_client(credential: str) -> Any:
    """Initialize Mem0 client with the given credential."""
    from mem0 import MemoryClient
    return MemoryClient(**{"api_key": credential})


_memory: BorrowerMemory | None = None


def get_memory() -> BorrowerMemory:
    global _memory
    if _memory is None:
        _memory = BorrowerMemory()
    return _memory
