"""L1 unit tests for the policy engine."""
from __future__ import annotations

from finai.core.policy import PolicyEngine


def test_policy_loads_yaml():
    engine = PolicyEngine()
    policy = engine.get_policy("personal_loan", "salaried")
    assert policy is not None
    assert policy.version == "1.0.0"
    assert policy.rules.get("eligibility") is not None


def test_eligibility_pass():
    engine = PolicyEngine()
    decision = engine.evaluate_eligibility(
        "personal_loan",
        "salaried",
        {"age": 35, "monthly_income": 85000, "bureau_score": 720, "dbr": 0.15},
    )
    assert decision.allowed is True
    assert decision.policy_version == "1.0.0"


def test_eligibility_fail_low_income():
    engine = PolicyEngine()
    decision = engine.evaluate_eligibility(
        "personal_loan",
        "salaried",
        {"age": 35, "monthly_income": 10000, "bureau_score": 720, "dbr": 0.15},
    )
    assert decision.allowed is False
    assert any("Income" in r for r in decision.rejection_reasons)


def test_eligibility_fail_low_score():
    engine = PolicyEngine()
    decision = engine.evaluate_eligibility(
        "personal_loan",
        "salaried",
        {"age": 35, "monthly_income": 85000, "bureau_score": 500, "dbr": 0.15},
    )
    assert decision.allowed is False
    assert any("Bureau" in r or "score" in r for r in decision.rejection_reasons)


def test_auto_approval():
    engine = PolicyEngine()
    assert engine.check_auto_approval(
        "personal_loan",
        "salaried",
        {"bureau_score": 780, "dbr": 0.3},
        [],
    ) is True


def test_auto_approval_denied_with_flags():
    engine = PolicyEngine()
    assert engine.check_auto_approval(
        "personal_loan",
        "salaried",
        {"bureau_score": 780, "dbr": 0.3},
        ["Some risk flag"],
    ) is False


def test_msme_policy():
    engine = PolicyEngine()
    policy = engine.get_policy("personal_loan", "msme")
    assert policy is not None
    assert policy.rules.get("gram_score", {}).get("enabled") is True


def test_eligibility_msme_low_income_ok():
    """MSME policy allows lower income than salaried."""
    engine = PolicyEngine()
    decision = engine.evaluate_eligibility(
        "personal_loan",
        "msme",
        {"age": 40, "monthly_income": 20000, "bureau_score": 0, "dbr": 0.1},
    )
    assert decision.allowed is True
