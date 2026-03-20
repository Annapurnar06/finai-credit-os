"""Policy engine — versioned, infrastructure-grade (not prompt-embedded).

Per Pandhi: 'Stop embedding decision logic in prompts. Surface it as enforcement infrastructure.'
Policies are loaded from YAML files in knowledge_garden/policies/.
Every evaluation returns (decision, policy_version, matched_rules).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PolicyRule:
    name: str
    condition: str
    threshold: Any
    action: str  # "allow", "deny", "flag", "escalate"
    severity: str = "info"  # "info", "warning", "hard_reject"


@dataclass
class PolicyDecision:
    allowed: bool
    policy_version: str
    matched_rules: list[PolicyRule] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)


@dataclass
class PolicyDocument:
    version: str
    product_type: str
    segment: str
    effective_date: str
    rules: dict[str, Any]
    raw: dict[str, Any]


class PolicyEngine:
    """Loads and evaluates versioned policy YAML from knowledge_garden/policies/."""

    def __init__(self, policy_dir: str | None = None) -> None:
        if policy_dir is None:
            policy_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "knowledge_garden",
                "policies",
            )
        self._policy_dir = Path(policy_dir)
        self._policies: dict[str, PolicyDocument] = {}
        self._load_policies()

    def _load_policies(self) -> None:
        if not self._policy_dir.exists():
            return
        for f in self._policy_dir.glob("*.yaml"):
            with open(f) as fh:
                data = yaml.safe_load(fh)
                if not data:
                    continue
                key = f"{data.get('product', '')}_{data.get('segment', '')}"
                self._policies[key] = PolicyDocument(
                    version=data.get("version", "0.0.0"),
                    product_type=data.get("product", ""),
                    segment=data.get("segment", ""),
                    effective_date=data.get("effective_date", ""),
                    rules=data.get("rules", {}),
                    raw=data,
                )

    def get_policy(self, product_type: str, segment: str) -> PolicyDocument | None:
        return self._policies.get(f"{product_type}_{segment}")

    def evaluate_eligibility(
        self,
        product_type: str,
        segment: str,
        borrower_data: dict[str, Any],
    ) -> PolicyDecision:
        policy = self.get_policy(product_type, segment)
        if not policy:
            return PolicyDecision(
                allowed=False,
                policy_version="none",
                rejection_reasons=[f"No policy found for {product_type}/{segment}"],
            )

        rules = policy.rules.get("eligibility", {})
        matched: list[PolicyRule] = []
        rejections: list[str] = []
        flags: list[str] = []

        age = borrower_data.get("age", 0)
        if rules.get("min_age") and age < rules["min_age"]:
            rejections.append(f"Age {age} below minimum {rules['min_age']}")
            matched.append(PolicyRule("min_age", "age >= threshold", rules["min_age"], "deny", "hard_reject"))

        if rules.get("max_age") and age > rules["max_age"]:
            rejections.append(f"Age {age} above maximum {rules['max_age']}")
            matched.append(PolicyRule("max_age", "age <= threshold", rules["max_age"], "deny", "hard_reject"))

        income = borrower_data.get("monthly_income", 0)
        if rules.get("min_monthly_income") and income < rules["min_monthly_income"]:
            rejections.append(f"Income {income} below minimum {rules['min_monthly_income']}")
            matched.append(PolicyRule("min_income", "income >= threshold", rules["min_monthly_income"], "deny", "hard_reject"))

        bureau_score = borrower_data.get("bureau_score", 0)
        if rules.get("min_bureau_score") and bureau_score < rules["min_bureau_score"]:
            rejections.append(f"Bureau score {bureau_score} below minimum {rules['min_bureau_score']}")
            matched.append(PolicyRule("min_bureau", "score >= threshold", rules["min_bureau_score"], "deny", "hard_reject"))

        dbr = borrower_data.get("dbr", 0)
        if rules.get("max_dbr") and dbr > rules["max_dbr"]:
            flags.append(f"DBR {dbr:.2%} exceeds threshold {rules['max_dbr']:.2%}")
            matched.append(PolicyRule("max_dbr", "dbr <= threshold", rules["max_dbr"], "flag", "warning"))

        return PolicyDecision(
            allowed=len(rejections) == 0,
            policy_version=policy.version,
            matched_rules=matched,
            flags=flags,
            rejection_reasons=rejections,
        )

    def check_auto_approval(
        self,
        product_type: str,
        segment: str,
        borrower_data: dict[str, Any],
        risk_flags: list[str],
    ) -> bool:
        policy = self.get_policy(product_type, segment)
        if not policy:
            return False

        auto_rules = policy.rules.get("auto_approval", {})
        if not auto_rules:
            return False

        bureau_min = auto_rules.get("bureau_score_min", 999)
        dbr_max = auto_rules.get("dbr_max", 0)
        require_green = auto_rules.get("all_risk_flags", "") == "GREEN"

        if borrower_data.get("bureau_score", 0) < bureau_min:
            return False
        if borrower_data.get("dbr", 1.0) > dbr_max:
            return False
        return not (require_green and len(risk_flags) > 0)
