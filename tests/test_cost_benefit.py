import asyncio
import os
from unittest.mock import patch

import pytest

from riskgpt.chains.cost_benefit import (
    async_cost_benefit_chain,
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


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_cost_benefit_chain():
    """Test the cost_benefit_chain function."""
    request = CostBenefitRequest(
        business_context=BusinessContext(
            project_id="test_cost_benefit", language=LanguageEnum.english
        ),
        risk_description="The project may fail due to lack of resources.",
        mitigations=["Allocate additional resources", "Prioritize critical tasks"],
    )
    response = cost_benefit_chain(request)

    # Check that the response has the expected fields
    assert isinstance(response.analyses, list)
    assert len(response.analyses) > 0

    # Check that each analysis has the expected structure
    for analysis in response.analyses:
        assert analysis.mitigation
        assert analysis.cost is not None
        assert analysis.benefit is not None


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_async_cost_benefit_chain():
    """Test the async_cost_benefit_chain function."""
    request = CostBenefitRequest(
        business_context=BusinessContext(
            project_id="test_async_cost_benefit", language=LanguageEnum.english
        ),
        risk_description="The project may fail due to lack of resources.",
        mitigations=["Allocate additional resources", "Prioritize critical tasks"],
    )
    response = asyncio.run(async_cost_benefit_chain(request))

    # Check that the response has the expected fields
    assert isinstance(response.analyses, list)
    assert len(response.analyses) > 0

    # Check that each analysis has the expected structure
    for analysis in response.analyses:
        assert analysis.mitigation
        assert analysis.cost is not None
        assert analysis.benefit is not None


def test_cost_benefit_chain_with_mock():
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

    # Mock the chain.invoke method to return our expected response
    with patch("riskgpt.chains.base.BaseChain.invoke", return_value=expected_response):
        response = cost_benefit_chain(request)

        # Check that the response matches our expectations
        assert len(response.analyses) == len(expected_response.analyses)
        assert (
            response.analyses[0].mitigation == expected_response.analyses[0].mitigation
        )
        assert response.analyses[0].cost == expected_response.analyses[0].cost
        assert response.analyses[0].benefit == expected_response.analyses[0].benefit
        assert response.references == expected_response.references


def test_async_cost_benefit_chain_with_mock():
    """Test the async_cost_benefit_chain function with a mock."""
    # Create a request
    request = CostBenefitRequest(
        business_context=BusinessContext(
            project_id="test_async_cost_benefit_mock", language=LanguageEnum.english
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

    # Define an async function to test
    async def run_test():
        # Create a mock coroutine that returns the expected response
        async def mock_invoke_async(*args, **kwargs):
            return expected_response

        # Mock the chain.invoke_async method to return our mock coroutine
        with patch("riskgpt.chains.base.BaseChain.invoke_async", mock_invoke_async):
            response = await async_cost_benefit_chain(request)

            # Check that the response matches our expectations
            assert len(response.analyses) == len(expected_response.analyses)
            assert (
                response.analyses[0].mitigation
                == expected_response.analyses[0].mitigation
            )
            assert response.analyses[0].cost == expected_response.analyses[0].cost
            assert response.analyses[0].benefit == expected_response.analyses[0].benefit
            assert response.references == expected_response.references

    # Run the async test
    asyncio.run(run_test())
