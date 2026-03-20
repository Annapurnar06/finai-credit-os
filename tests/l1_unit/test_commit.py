"""L1 unit tests for commit discipline framework."""
from __future__ import annotations

from finai.core.commit import (
    CommitClass,
    get_cooling_off_seconds,
    register_tool,
    requires_dual_hitl,
    requires_hitl,
)


def test_requires_hitl():
    assert requires_hitl(CommitClass.HARD_COMMIT) is True
    assert requires_hitl(CommitClass.IRREVERSIBLE) is True
    assert requires_hitl(CommitClass.READ_ONLY) is False
    assert requires_hitl(CommitClass.SOFT_COMMIT) is False


def test_requires_dual_hitl():
    assert requires_dual_hitl(CommitClass.IRREVERSIBLE) is True
    assert requires_dual_hitl(CommitClass.HARD_COMMIT) is False


def test_cooling_off():
    assert get_cooling_off_seconds(CommitClass.IRREVERSIBLE) == 600
    assert get_cooling_off_seconds(CommitClass.HARD_COMMIT) == 0
    assert get_cooling_off_seconds(CommitClass.READ_ONLY) == 0
