"""Demo runner — one command runs full LOS pipeline on all 4 borrower profiles.

Usage: python -m demo.run [scenario_name]
  scenario_name: salaried_clean, msme_seasonal, gig_worker, first_time_borrower, all
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from typing import Any

from demo.scenarios.borrower_profiles import ALL_SCENARIOS


async def run_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Run the LOS pipeline for a single borrower scenario."""
    from finai.graphs.los import get_los_app

    name = scenario["name"]
    print(f"\n{'='*70}")
    print(f"  FINAI Credit OS — LOS Pipeline Demo")
    print(f"  Borrower: {name}")
    print(f"  Scenario: {scenario['scenario']}")
    print(f"  {scenario['description']}")
    print(f"{'='*70}\n")

    app = get_los_app()
    initial_state = {
        "application_id": f"demo-{scenario['scenario']}",
        "borrower_id": f"borrower-{scenario['pan']}",
        "documents": [
            {
                "id": f"doc-{i}",
                "filename": doc["filename"],
                "doc_type": doc.get("doc_type", "unknown"),
                "content_text": doc["content_text"],
            }
            for i, doc in enumerate(scenario["documents"])
        ],
    }

    start = time.monotonic()
    print(f"[1/4] Submitting {len(scenario['documents'])} documents...")

    result = await app.ainvoke(initial_state)

    elapsed = time.monotonic() - start

    # Print results
    print(f"\n[2/4] Document Extraction Results:")
    extraction = result.get("extraction_results", {})
    for doc_type, ext_result in extraction.items():
        status = ext_result.get("status", "unknown")
        conf = ext_result.get("confidence", 0)
        icon = "+" if status == "success" else ("~" if status == "low_confidence" else "x")
        print(f"  [{icon}] {doc_type}: {status} (confidence: {conf:.0%})")

    print(f"\n[3/4] Proposal Summary:")
    proposal = result.get("proposal", {})
    if proposal:
        profile = proposal.get("borrower_profile", {})
        eligibility = proposal.get("eligibility", {})
        dbr = proposal.get("dbr", {})
        print(f"  Name: {profile.get('borrower_name', 'N/A')}")
        print(f"  Segment: {profile.get('segment', 'N/A')}")
        print(f"  Monthly Income: Rs.{profile.get('monthly_income', 0):,.0f}")
        print(f"  Eligible: {eligibility.get('is_eligible', False)}")
        if eligibility.get("is_eligible"):
            print(f"  Max Loan: Rs.{eligibility.get('max_loan_amount', 0):,.0f}")
        print(f"  DBR Ratio: {dbr.get('dbr_ratio', 0):.1%}")

    print(f"\n[4/4] Decision:")
    status = result.get("status", "unknown")
    flags = result.get("risk_flags", [])
    red = [f for f in flags if f.get("level") == "RED"]
    amber = [f for f in flags if f.get("level") == "AMBER"]
    print(f"  Status: {status}")
    print(f"  Auto-Approve Eligible: {result.get('auto_approve_eligible', False)}")
    print(f"  Risk Flags: {len(red)} RED, {len(amber)} AMBER")
    if red:
        for f in red:
            print(f"    [RED] {f.get('description', '')}")
    if amber:
        for f in amber:
            print(f"    [AMBER] {f.get('description', '')}")

    print(f"\n  Pipeline completed in {elapsed:.1f}s")
    print(f"{'='*70}\n")

    return result


async def main() -> None:
    scenario_name = sys.argv[1] if len(sys.argv) > 1 else "all"

    if scenario_name == "all":
        scenarios = list(ALL_SCENARIOS.values())
    elif scenario_name in ALL_SCENARIOS:
        scenarios = [ALL_SCENARIOS[scenario_name]]
    else:
        print(f"Unknown scenario: {scenario_name}")
        print(f"Available: {', '.join(ALL_SCENARIOS.keys())}, all")
        sys.exit(1)

    print("\n" + "="*70)
    print("  FINAI Credit OS — GramCredit AI Demo Runner")
    print(f"  Running {len(scenarios)} scenario(s)")
    print("="*70)

    results = {}
    for scenario in scenarios:
        try:
            result = await run_scenario(scenario)
            results[scenario["scenario"]] = {
                "status": result.get("status"),
                "auto_approve": result.get("auto_approve_eligible"),
                "risk_flags_count": len(result.get("risk_flags", [])),
            }
        except Exception as e:
            print(f"\n  ERROR running {scenario['scenario']}: {e}")
            results[scenario["scenario"]] = {"status": "error", "error": str(e)}

    # Summary
    print("\n" + "="*70)
    print("  DEMO SUMMARY")
    print("="*70)
    for name, r in results.items():
        status = r.get("status", "unknown")
        auto = r.get("auto_approve", False)
        flags = r.get("risk_flags_count", 0)
        print(f"  {name:25s} | Status: {status:20s} | Auto: {str(auto):5s} | Flags: {flags}")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
