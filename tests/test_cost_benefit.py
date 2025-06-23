from unittest.mock import patch

import pytest

from riskgpt.chains.cost_benefit import (
    cost_benefit_chain,
)
from riskgpt.models.schemas import (
    BusinessContext,
    CostBenefit,
    CostBenefitRequest,
    CostBenefitResponse,
    LanguageEnum,
    ResponseInfo,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cost_benefit_chain():
    """Test the cost_benefit_chain function."""
    request = CostBenefitRequest(
        business_context=BusinessContext(
            project_id="test_cost_benefit", language=LanguageEnum.english
        ),
        risk_description="The project may fail due to lack of resources.",
        mitigations=["Allocate additional resources", "Prioritize critical tasks"],
    )
    response = await cost_benefit_chain(request)

    # Check that the response has the expected fields
    assert isinstance(response.analyses, list)
    assert len(response.analyses) > 0

    # Check that each analysis has the expected structure
    for analysis in response.analyses:
        assert analysis.mitigation
        assert analysis.cost is not None
        assert analysis.benefit is not None


@pytest.mark.asyncio
async def test_cost_benefit_chain_with_mock():
    """Test the cost_benefit_chain function with a mock."""
    # Create a request
    request = CostBenefitRequest(
        business_context=BusinessContext(
            project_id="test_cost_benefit_mock", language=LanguageEnum.english
        ),
        risk_description="The project may fail due to lack of resources.",
        mitigations=["Allocate additional resources", "Prioritize critical tasks"],
    )

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
        response_info=ResponseInfo(
            consumed_tokens=100,
            total_cost=0.01,
            prompt_name="cost_benefit",
            model_name="mock-model",
        ),
    )

    async def mock_invoke(*args, **kwargs):
        """Mock the invoke method to return the expected response."""
        return expected_response

    # Mock the chain.invoke method to return our expected response
    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        response = await cost_benefit_chain(request)

        # Check that the response matches our expectations
        assert len(response.analyses) == len(expected_response.analyses)
        assert (
            response.analyses[0].mitigation == expected_response.analyses[0].mitigation
        )
        assert response.analyses[0].cost == expected_response.analyses[0].cost
        assert response.analyses[0].benefit == expected_response.analyses[0].benefit
        assert response.references == expected_response.references
