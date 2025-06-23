from unittest.mock import patch

import pytest

from riskgpt.chains.get_risks import get_risks_chain
from riskgpt.models.schemas import (
    BusinessContext,
    LanguageEnum,
    ResponseInfo,
    Risk,
    RiskRequest,
    RiskResponse,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_risks_chain():
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


@pytest.mark.asyncio
async def test_get_risks_chain_with_mock():
    """Test get_risks_chain with mocked BaseChain.invoke."""
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="mock", language=LanguageEnum.english
        ),
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

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await get_risks_chain(request)
        assert resp.risks == expected.risks
