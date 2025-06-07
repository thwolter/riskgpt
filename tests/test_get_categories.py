from riskgpt.chains.get_categories import get_categories_chain
from riskgpt.models.schemas import CategoryRequest

def test_get_categories_chain():
    request = CategoryRequest(
        project_id="123",
        project_description="Ein neues IT-Projekt zur Einführung eines CRM-Systems.",
        domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
        language="de"
    )
    response = get_categories_chain(request)
    print(f"\nTokens consumed: {response.response_info.consumed_tokens}, Cost: {response.response_info.total_cost:.4f} USD")
    print(response.categories)
    assert isinstance(response.categories, list)
