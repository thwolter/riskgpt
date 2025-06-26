from unittest.mock import AsyncMock, patch

import pytest
from chains.risk_categories import risk_categories_chain
from models.chains.categorization import CategoryRequest, CategoryResponse
from models.common import BusinessContext


@pytest.fixture
def test_request():
    """Fixture to create a sample CategoryRequest."""
    return CategoryRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="Implementierung eines neuen CRM-Systems",
            domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
        ),
        existing_categories=["Technisch"],
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_categories_chain(test_request):
    response = await risk_categories_chain(test_request)
    assert isinstance(response.categories, list)


@pytest.mark.asyncio
async def test_get_categories_chain_with_mock(test_request):
    """Test get_categories_chain with mocked BaseChain.invoke."""
    expected = CategoryResponse(
        categories=["Technical", "Operational"],
    )
    with patch(
        "chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await risk_categories_chain(test_request)
        assert resp.categories == expected.categories
