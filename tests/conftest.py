"""Shared test fixtures for FINAI Credit OS."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_pan_content() -> str:
    return (
        "INCOME TAX DEPARTMENT\n"
        "PERMANENT ACCOUNT NUMBER CARD\n"
        "Name: RAJAN KRISHNAMURTHY\n"
        "Father's Name: VENKATESH KRISHNAMURTHY\n"
        "Date of Birth: 15/03/1985\n"
        "PAN: DEFPR5678B\n"
    )


@pytest.fixture
def sample_bank_statement_content() -> str:
    return (
        "HDFC BANK — ACCOUNT STATEMENT\n"
        "Account Holder: RAJAN KRISHNAMURTHY\n"
        "Account Number: 50100248975631\n"
        "IFSC: HDFC0001234\n"
        "Period: March 2025 — February 2026\n\n"
        "Average Monthly Balance: ₹2,03,000\n"
        "Salary Credits Detected: ₹85,000/month (Employer: TCS Ltd)\n"
        "EMI Outflows: ₹12,000/month\n"
        "Bounce Count: 0\n"
    )


@pytest.fixture
def sample_extraction_results() -> dict:
    return {
        "pan": {
            "agent_name": "PanDataAgent",
            "status": "success",
            "confidence": 1.0,
            "data": {
                "pan_number": "DEFPR5678B",
                "name": "RAJAN KRISHNAMURTHY",
                "dob": "15/03/1985",
                "fathers_name": "VENKATESH KRISHNAMURTHY",
                "status": "valid",
            },
        },
        "bank_statement": {
            "agent_name": "BankStatementAgent",
            "status": "success",
            "confidence": 0.92,
            "data": {
                "account_number": "50100248975631",
                "bank_name": "HDFC BANK",
                "avg_monthly_balance": 203000,
                "salary_credits": 85000,
                "emi_outflows": 12000,
                "bounce_count": 0,
            },
        },
        "salary_slip": {
            "agent_name": "SalarySlipAgent",
            "status": "success",
            "confidence": 0.95,
            "data": {
                "gross_salary": 85000,
                "net_salary": 72900,
                "employer_name": "TCS Ltd",
                "epf_deduction": 5400,
            },
        },
    }
