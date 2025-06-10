import asyncio
import os
from unittest.mock import patch

import pytest

from riskgpt.chains.check_definition import (
    async_check_definition_chain,
    check_definition_chain,
)
from riskgpt.models.schemas import (
    BusinessContext,
    DefinitionCheckRequest,
    DefinitionCheckResponse,
    LanguageEnum,
    ResponseInfo,
)


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_check_definition_chain():
    """Test the check_definition_chain function."""
    request = DefinitionCheckRequest(
        business_context=BusinessContext(
            project_id="test_check_definition", language=LanguageEnum.english
        ),
        risk_description="The project may fail due to lack of resources.",
    )
    response = check_definition_chain(request)

    # Check that the response has the expected fields
    assert response.revised_description
    assert isinstance(response.biases, list)

    # Check that the response contains improvements (the original had ambiguous wording)
    assert "ambiguous wording" in response.biases


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_async_check_definition_chain():
    """Test the async_check_definition_chain function."""
    request = DefinitionCheckRequest(
        business_context=BusinessContext(
            project_id="test_async_check_definition", language=LanguageEnum.english
        ),
        risk_description="The project may fail due to lack of resources.",
    )
    response = asyncio.run(async_check_definition_chain(request))

    # Check that the response has the expected fields
    assert response.revised_description
    assert isinstance(response.biases, list)

    # Check that the response contains improvements (the original had ambiguous wording)
    assert "ambiguous wording" in response.biases


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_check_definition_chain_with_passive_voice():
    """Test the check_definition_chain function with passive voice."""
    request = DefinitionCheckRequest(
        business_context=BusinessContext(
            project_id="test_check_definition_passive", language=LanguageEnum.english
        ),
        risk_description="The project is delayed by external factors.",
    )
    response = check_definition_chain(request)

    # Check that the response identifies passive voice
    assert "passive voice" in response.biases


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_check_definition_chain_missing_quantifiers():
    """Test the check_definition_chain function with missing quantifiers."""
    request = DefinitionCheckRequest(
        business_context=BusinessContext(
            project_id="test_check_definition_quantifiers",
            language=LanguageEnum.english,
        ),
        risk_description="The project will experience delays due to supply chain issues.",
    )
    response = check_definition_chain(request)

    # Check that the response identifies missing quantifiers
    assert "missing quantifiers" in response.biases


def test_check_definition_chain_with_mock():
    """Test the check_definition_chain function with a mock."""
    # Create a request
    request = DefinitionCheckRequest(
        business_context=BusinessContext(
            project_id="test_check_definition_mock", language=LanguageEnum.english
        ),
        risk_description="The project may fail due to lack of resources.",
    )

    # Define the expected response
    expected_response = DefinitionCheckResponse(
        revised_description="The project will fail by 20% due to insufficient allocation of critical resources.",
        biases=["ambiguous wording"],
        response_info=ResponseInfo(
            consumed_tokens=100,
            total_cost=0.01,
            prompt_name="check_definition",
            model_name="mock-model",
        ),
    )

    # Mock the chain.invoke method to return our expected response
    with patch("riskgpt.chains.base.BaseChain.invoke", return_value=expected_response):
        # Also mock the _process_response function to ensure biases are set correctly
        with patch(
            "riskgpt.chains.check_definition._process_response",
            return_value=expected_response,
        ):
            response = check_definition_chain(request)

            # Check that the response matches our expectations
            assert response.revised_description == expected_response.revised_description
            assert response.biases == expected_response.biases


def test_async_check_definition_chain_with_mock():
    """Test the async_check_definition_chain function with a mock."""
    # Create a request
    request = DefinitionCheckRequest(
        business_context=BusinessContext(
            project_id="test_async_check_definition_mock", language=LanguageEnum.english
        ),
        risk_description="The project may fail due to lack of resources.",
    )

    # Define the expected response
    expected_response = DefinitionCheckResponse(
        revised_description="The project will fail by 20% due to insufficient allocation of critical resources.",
        biases=["ambiguous wording"],
        response_info=ResponseInfo(
            consumed_tokens=100,
            total_cost=0.01,
            prompt_name="check_definition",
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
            # Also mock the _process_response function to ensure biases are set correctly
            with patch(
                "riskgpt.chains.check_definition._process_response",
                return_value=expected_response,
            ):
                response = await async_check_definition_chain(request)

                # Check that the response matches our expectations
                assert (
                    response.revised_description
                    == expected_response.revised_description
                )
                assert response.biases == expected_response.biases

    # Run the async test
    asyncio.run(run_test())
