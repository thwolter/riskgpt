"""Integration tests for the extract_keywords chain."""

import pytest
from riskgpt.chains.extract_keywords import extract_keywords_chain
from riskgpt.models.chains.keywords import (
    ExtractKeywordsRequest,
    ExtractKeywordsResponse,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_extract_keywords_integration():
    """Integration test for extract_keywords_chain with a real LLM call."""
    # Create a test request with sample content
    request = ExtractKeywordsRequest(
        query=(
            "Recent developments in artificial intelligence have shown promising "
            "applications in risk management. Companies are increasingly using AI to identify "
            "potential risks in their operations and to automate risk assessment processes. "
            "However, there are concerns about the reliability and transparency of AI-based "
            "risk management systems. Regulators are starting to pay attention to these issues "
            "and are considering new guidelines for AI use in risk management."
        ),
        max_keywords=5,
    )

    # Call the function under test with a real LLM
    result = await extract_keywords_chain(request)

    # Verify the structure of the response
    assert isinstance(result, ExtractKeywordsResponse)
    assert isinstance(result.keywords, str)
    assert len(result.keywords) > 0

    # Check that we got keywords (at least one word)
    keywords = result.keywords.split()
    assert len(keywords) > 0

    # Verify that at least some expected keywords are present
    # Note: This is a fuzzy check since the exact keywords may vary
    expected_terms = ["risk", "management", "AI", "artificial", "intelligence"]
    found_terms = [
        term
        for term in expected_terms
        if any(term.lower() in keyword.lower() for keyword in keywords)
    ]
    assert (
        len(found_terms) > 0
    ), f"None of the expected terms {expected_terms} found in keywords: {keywords}"

    # Verify response info
    assert result.response_info is not None
    assert result.response_info.consumed_tokens > 0
    assert result.response_info.prompt_name == "extract_keywords"
