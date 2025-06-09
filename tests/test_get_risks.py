from riskgpt.chains.get_risks import get_risks_chain
from riskgpt.models.schemas import BusinessContext, RiskRequest


def test_get_risks_chain():
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="Ein neues IT-Projekt zur Einführung eines CRM-Systems.",
            domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
            language="de",
        ),
        category="Technisch",
        existing_risks=["Datenverlust"],
    )
    response = get_risks_chain(request)
    assert isinstance(response.risks, list)
