import os

import pytest
from unittest.mock import patch
from riskgpt.models.schemas import RiskResponse, Risk, ResponseInfo

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

from unittest.mock import patch
from riskgpt.models.schemas import RiskResponse, Risk, ResponseInfo


def test_get_risks_chain_with_mock():
    """Test get_risks_chain with mocked BaseChain.invoke."""
    request = RiskRequest(
        business_context=BusinessContext(project_id="mock", language=LanguageEnum.english),
        category="Technical",
    )
    expected = RiskResponse(
        risks=[Risk(title="mock", description="desc", category="Technical")],
        references=["ref"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_risks",
            model_name="mock-model",
        ),
    )
    with patch("riskgpt.chains.base.BaseChain.invoke", return_value=expected):
        resp = get_risks_chain(request)
        assert resp.risks == expected.risks
