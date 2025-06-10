import asyncio
import os
from unittest.mock import patch

import pytest

from riskgpt.chains.get_categories import async_get_categories_chain
from riskgpt.models.schemas import (
    BusinessContext,
    CategoryRequest,
    CategoryResponse,
    LanguageEnum,
    ResponseInfo,
)


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_async_get_categories_chain():
    request = CategoryRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="Ein neues IT-Projekt zur Einführung eines CRM-Systems.",
            domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
            language=LanguageEnum.german,
        ),
    )
    response = asyncio.run(async_get_categories_chain(request))
    assert isinstance(response.categories, list)


@pytest.mark.asyncio
async def test_async_get_categories_chain_with_mock():
    """Async categories chain with mocked invoke_async."""
    request = CategoryRequest(
        business_context=BusinessContext(
            project_id="mock", language=LanguageEnum.english
        ),
    )
    expected = CategoryResponse(
        categories=["Technical"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_categories",
            model_name="mock-model",
        ),
    )

    async def mock_invoke_async(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke_async", mock_invoke_async):
        resp = await async_get_categories_chain(request)
        assert resp.categories == expected.categories
