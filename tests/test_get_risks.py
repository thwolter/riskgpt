import os

import pytest

from riskgpt.chains.get_risks import get_risks_chain
from riskgpt.models.schemas import BusinessContext, LanguageEnum, RiskRequest


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_get_risks_chain():
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="Ein neues IT-Projekt zur Einführung eines CRM-Systems.",
            domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
            language=LanguageEnum.german,
        ),
        category="Technisch",
        existing_risks=["Datenverlust"],
    )
    response = get_risks_chain(request)
    assert isinstance(response.risks, list)
