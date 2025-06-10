import os

import pytest
from unittest.mock import patch
from riskgpt.models.schemas import CategoryResponse, ResponseInfo

from riskgpt.chains.get_categories import get_categories_chain
from riskgpt.models.schemas import BusinessContext, CategoryRequest


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_get_categories_chain():
    request = CategoryRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="Ein neues IT-Projekt zur Einführung eines CRM-Systems.",
            domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
            language="de",
        ),
        existing_categories=["Technisch"],
    )
    response = get_categories_chain(request)
    assert isinstance(response.categories, list)

from unittest.mock import patch
from riskgpt.models.schemas import CategoryResponse, ResponseInfo


def test_get_categories_chain_with_mock():
    """Test get_categories_chain with mocked BaseChain.invoke."""
    request = CategoryRequest(
        business_context=BusinessContext(project_id="mock", language="en"),
        existing_categories=["Tech"],
    )
    expected = CategoryResponse(
        categories=["Technical", "Operational"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_categories",
            model_name="mock-model",
        ),
    )
    with patch("riskgpt.chains.base.BaseChain.invoke", return_value=expected):
        resp = get_categories_chain(request)
        assert resp.categories == expected.categories
