"""
Example script demonstrating how to use the analyse_risk workflow.

This script creates a sample risk and runs the analyse_risk workflow to analyze it.
"""

import asyncio
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from riskgpt.models.chains.risk import Risk
from riskgpt.models.common import BusinessContext
from riskgpt.models.workflows.risk_analysis import RiskAnalysisRequest
from riskgpt.workflows.risk_analysis import analyse_risk


async def main():
    """Run the analyse_risk workflow on a sample risk."""
    # Create a risk to analyze
    risk = Risk(
        title="Data Migration Failure",
        description="Risk of losing critical customer data during migration to the new CRM system",
        category="Technical",
        document_refs=["doc-123", "doc-456"],  # References to uploaded documents
    )

    # Create the request
    request = RiskAnalysisRequest(
        business_context=BusinessContext(
            project_id="CRM-2023",
            project_description="Implementation of a new CRM system",
            language="en",
        ),
        risk=risk,
        focus_keywords=["data loss", "migration", "backup"],
        time_horizon_months=6,
    )

    # Run the workflow
    print(f"Analyzing risk: {risk.title}")
    response = await analyse_risk(request)

    # Process the response
    print(f"\nRisk Summary: {response.risk_summary}")
    print("\nRisk Factors:")
    for factor in response.risk_factors:
        print(f"- {factor}")

    print("\nMitigation Strategies:")
    for strategy in response.mitigation_strategies:
        print(f"- {strategy}")

    print(f"\nImpact Assessment: {response.impact_assessment}")
    print(f"\nDocument References: {response.document_references}")

    if response.full_report:
        print(f"\nFull Report:\n{response.full_report}")

    if response.response_info:
        print("\nResponse Info:")
        print(f"- Consumed Tokens: {response.response_info.consumed_tokens}")
        print(f"- Total Cost: ${response.response_info.total_cost:.6f}")
        print(f"- Model Name: {response.response_info.model_name}")


if __name__ == "__main__":
    asyncio.run(main())
