import os

import pytest

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
