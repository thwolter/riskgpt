import asyncio
import pytest

pytest.importorskip("langchain")
pytest.importorskip("langchain_openai")
pytest.importorskip("langchain_community")

from riskgpt.chains.get_categories import async_get_categories_chain
from riskgpt.models.schemas import CategoryRequest


def test_async_get_categories_chain():
    request = CategoryRequest(
        project_id="123",
        project_description="Ein neues IT-Projekt zur Einführung eines CRM-Systems.",
        domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
        language="de"
    )
    response = asyncio.run(async_get_categories_chain(request))
    assert isinstance(response.categories, list)

