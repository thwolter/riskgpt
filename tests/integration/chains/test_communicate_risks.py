from unittest.mock import patch

import pytest

from src.chains.communicate_risks import communicate_risks_chain
from src.models.chains.communication import (
    CommunicationRequest,
    CommunicationResponse,
)
from src.models.chains.risk import Risk
from src.models.common import BusinessContext
from src.models.enums import AudienceEnum, LanguageEnum


@pytest.fixture
def test_request():
    """Fixture to create a sample CommunicationRequest."""
    return CommunicationRequest(
        business_context=BusinessContext(
            project_id="test_project",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        risks=[
            Risk(
                title="Data Security Risk",
                description="Potential data breaches due to inadequate security measures.",
            ),
            Risk(
                title="Compliance Risk",
                description="Failure to comply with industry regulations could lead to legal issues.",
            ),
        ],
        audience=AudienceEnum.regulator,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_communicate_risks_chain(test_request):
    """Test the communicate_risks_chain function with real API calls."""

    response: CommunicationResponse = await communicate_risks_chain(test_request)
    assert response.summary is not None
    assert response.technical_annex is not None


@pytest.mark.asyncio
async def test_communicate_risks_chain_with_mock(test_request):
    """Test communicate_risks_chain with mocked BaseChain.invoke."""

    expected = CommunicationResponse(
        summary="Mock summary",
        key_points=["Mock key point"],
        technical_annex="Mock technical annex",
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("src.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await communicate_risks_chain(test_request)
        assert resp.summary == expected.summary
        assert resp.key_points == expected.key_points
