"""L1 unit tests for proposal agents."""
from __future__ import annotations

import pytest

from finai.agents.proposal.agents import (
    check_mandatory_documents,
    compute_dbr,
    compute_roi,
    generate_proposal_data,
    triangulate_income,
)


@pytest.mark.asyncio
async def test_generate_proposal_data(sample_extraction_results):
    result = await generate_proposal_data(sample_extraction_results)
    assert result.status == "success"
    assert result.data["borrower_name"] == "RAJAN KRISHNAMURTHY"
    assert result.data["pan"] == "DEFPR5678B"
    assert result.data["monthly_income"] > 0


@pytest.mark.asyncio
async def test_compute_dbr():
    proposal = {"monthly_income": 85000}
    bureau = {"total_emi": 12000}
    result = await compute_dbr(proposal, bureau)
    assert result.status == "success"
    assert result.data["dbr_ratio"] == pytest.approx(12000 / 85000, abs=0.01)
    assert result.data["max_eligible_emi"] > 0


@pytest.mark.asyncio
async def test_compute_dbr_zero_income():
    result = await compute_dbr({"monthly_income": 0}, None)
    assert result.data["dbr_ratio"] == 1.0


@pytest.mark.asyncio
async def test_compute_roi():
    result = await compute_roi({"annual_income": 1000000}, requested_amount=500000)
    assert result.data["roi_ratio"] == 0.5


@pytest.mark.asyncio
async def test_triangulate_income(sample_extraction_results):
    proposal = {"monthly_income": 85000}
    result = await triangulate_income(sample_extraction_results, proposal)
    assert result.status in ("success", "low_confidence")
    assert result.data["sources_checked"]
    assert result.data["verified_income"] > 0


@pytest.mark.asyncio
async def test_mandatory_doc_check_pass(sample_extraction_results):
    result = await check_mandatory_documents(
        sample_extraction_results, "personal_loan", "salaried"
    )
    assert result.data["complete"] is True
    assert result.data["missing"] == []


@pytest.mark.asyncio
async def test_mandatory_doc_check_missing():
    result = await check_mandatory_documents(
        {"pan": {"status": "success"}},
        "personal_loan",
        "salaried",
    )
    assert result.data["complete"] is False
    assert "bank_statement" in result.data["missing"]
