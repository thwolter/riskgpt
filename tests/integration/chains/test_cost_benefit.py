from unittest.mock import patch

import pytest
from chains.cost_benefit import cost_benefit_chain
from models.chains.mitigation import (
    CostBenefit,
    CostBenefitRequest,
    CostBenefitResponse,
)
from models.common import BusinessContext


@pytest.fixture
def test_request():
    """Fixture to create a sample CostBenefitRequest."""
    return CostBenefitRequest(
        business_context=BusinessContext(
            project_id="test_project",
            project_description="Test project is a infrastructure project",
            domain_knowledge="Energy infrastructure is critical for modern economies.",
        ),
        risk_title="Project Delay Risk",
        risk_description="Risk of project delays due to resource constraints.",
        mitigations=["Allocate additional resources", "Prioritize critical tasks"],
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cost_benefit_chain(test_request):
    """Test the cost_benefit_chain function."""

    response = await cost_benefit_chain(test_request)

    # Check that the response has the expected fields
    assert isinstance(response.analyses, list)
    assert len(response.analyses) > 0

    # Check that each analysis has the expected structure
    for analysis in response.analyses:
        assert analysis.mitigation
        assert analysis.cost is not None
        assert analysis.benefit is not None


@pytest.mark.asyncio
async def test_cost_benefit_chain_with_mock(test_request):
    """Test the cost_benefit_chain function with a mock."""

    # Define the expected response
    expected_response = CostBenefitResponse(
        analyses=[
            CostBenefit(
                mitigation="Allocate additional resources",
                cost="High - Requires significant budget increase",
                benefit="High - Ensures project completion with quality",
            ),
            CostBenefit(
                mitigation="Prioritize critical tasks",
                cost="Low - Requires planning time",
                benefit="Medium - Ensures essential deliverables are completed",
            ),
        ],
        references=["Project management best practices"],
    )

    async def mock_invoke(*args, **kwargs):
        """Mock the invoke method to return the expected response."""
        return expected_response

    # Mock the chain.invoke method to return our expected response
    with patch("chains.base.BaseChain.invoke", side_effect=mock_invoke):
        response = await cost_benefit_chain(test_request)

        # Check that the response matches our expectations
        assert len(response.analyses) == len(expected_response.analyses)
        assert (
            response.analyses[0].mitigation == expected_response.analyses[0].mitigation
        )
        assert response.analyses[0].cost == expected_response.analyses[0].cost
        assert response.analyses[0].benefit == expected_response.analyses[0].benefit
        assert response.references == expected_response.references
