import asyncio

from riskgpt.chains.get_categories import async_get_categories_chain
from riskgpt.models.schemas import BusinessContext, CategoryRequest


def test_async_get_categories_chain():
    request = CategoryRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="Ein neues IT-Projekt zur Einführung eines CRM-Systems.",
            domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
            language="de",
        ),
    )
    response = asyncio.run(async_get_categories_chain(request))
    assert isinstance(response.categories, list)
