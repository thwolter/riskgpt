from unittest.mock import patch

import pytest

from riskgpt.chains.get_categories import get_categories_chain
from riskgpt.models.schemas import (
    BusinessContext,
    CategoryRequest,
    CategoryResponse,
    LanguageEnum,
    ResponseInfo,
)


@pytest.mark.asyncio
async def test_get_categories_chain_with_mock():
    """Async categories chain with mocked invoke."""
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

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", mock_invoke):
        resp = await get_categories_chain(request)
        assert resp.categories == expected.categories
