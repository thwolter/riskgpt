from unittest.mock import patch

import pytest
from riskgpt.chains.check_definition import check_definition_chain
from riskgpt.models.chains.definition_check import (
    DefinitionCheckRequest,
    DefinitionCheckResponse,
)


@pytest.fixture
def test_request():
    """Fixture to create a test DefinitionCheckRequest."""
    return DefinitionCheckRequest(
        risk_title="Resource Allocation Risk",
        risk_description="The project may fail due to lack of resources.",
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_check_definition_chain(test_request):
    """Test the check_definition_chain function."""

    response = await check_definition_chain(test_request)

    # Check that the response has the expected fields
    assert response.revised_description


@pytest.mark.asyncio
async def test_check_definition_chain_with_mock(test_request):
    """Test the check_definition_chain function with a mock."""

    # Define the expected response
    expected_response = DefinitionCheckResponse(
        revised_title="Resource Allocation Risk",
        revised_description="The project will fail by 20% due to insufficient allocation of critical resources.",
        rationale="The original description was too vague and lacked specific quantifiers.",
    )

    async def mock_invoke(*args, **kwargs):
        return expected_response

    # Mock the chain.invoke method to return our expected response
    with patch(
        "riskgpt.chains.base.BaseChain.invoke",
        return_value=expected_response,
        side_effect=mock_invoke,
    ):
        response = await check_definition_chain(test_request)

        # Check that the response matches our expectations
        assert response.revised_description == expected_response.revised_description
