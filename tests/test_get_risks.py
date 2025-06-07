from riskgpt.chains.get_risks import get_risks_chain
from riskgpt.models.schemas import RiskRequest


def test_get_risks_chain():
    request = RiskRequest(
        project_id="123",
        project_description="Ein neues IT-Projekt zur Einführung eines CRM-Systems.",
        category="Technisch",
        domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
        language="de",
    )
    response = get_risks_chain(request)
    assert isinstance(response.risks, list)
