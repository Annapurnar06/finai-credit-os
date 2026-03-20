"""Commit discipline framework — Pandhi's 'Security = Commit Discipline'.

Every tool call is classified by reversibility BEFORE execution.
The gateway enforces gating based on commit class.
"""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from finai.core.models import CommitClass


@dataclass
class ToolSpec:
    name: str
    commit_class: CommitClass
    description: str
    handler: Callable[..., Coroutine[Any, Any, Any]]


# Registry of all tools with their commit classifications
_tool_registry: dict[str, ToolSpec] = {}


def register_tool(
    name: str,
    commit_class: CommitClass,
    description: str = "",
) -> Callable:
    """Decorator to register a tool with its commit class."""

    def decorator(func: Callable) -> Callable:
        _tool_registry[name] = ToolSpec(
            name=name,
            commit_class=commit_class,
            description=description,
            handler=func,
        )
        return func

    return decorator


def get_tool(name: str) -> ToolSpec | None:
    return _tool_registry.get(name)


def get_all_tools() -> dict[str, ToolSpec]:
    return _tool_registry.copy()


def requires_hitl(commit_class: CommitClass) -> bool:
    return commit_class in (CommitClass.HARD_COMMIT, CommitClass.IRREVERSIBLE)


def requires_dual_hitl(commit_class: CommitClass) -> bool:
    return commit_class == CommitClass.IRREVERSIBLE


def get_cooling_off_seconds(commit_class: CommitClass) -> int:
    if commit_class == CommitClass.IRREVERSIBLE:
        return 600  # 10 minutes
    return 0
