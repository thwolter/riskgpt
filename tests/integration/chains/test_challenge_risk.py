from unittest.mock import AsyncMock, patch

import pytest

from src.riskgpt.chains.challenge_risk import challenge_risk_chain
from src.riskgpt.models.chains.questions import (
    ChallengeRiskRequest,
    ChallengeRiskResponse,
)
from src.riskgpt.models.chains.risk import Risk
from src.riskgpt.models.common import BusinessContext
from src.riskgpt.models.enums import AudienceEnum


@pytest.fixture
def test_risk():
    """Fixture to create a sample Risk."""
    return Risk(
        title="Data Migration Failure",
        description="Risk of losing critical customer data during migration to the new CRM system",
        category="Technical",
    )


@pytest.fixture
def test_business_context():
    """Fixture to create a sample BusinessContext."""
    return BusinessContext(
        project_id="CRM-2023",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
        business_area="Sales",
        industry_sector="Technology",
    )


@pytest.fixture
def test_request(test_risk, test_business_context):
    """Fixture to create a sample ChallengeRiskRequest."""
    return ChallengeRiskRequest(
        risk=test_risk,
        business_context=test_business_context,
        audience=AudienceEnum.risk_internal,
        focus_areas=["data security", "contingency planning", "testing"],
        num_questions=3,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_challenge_risk_chain(test_request):
    """Test challenge_risk_chain with actual invocation."""

    response = await challenge_risk_chain(test_request)
    assert isinstance(response, ChallengeRiskResponse)
    assert isinstance(response.questions, list)
    assert len(response.questions) == test_request.num_questions

    # Check that each question is a non-empty string
    for question in response.questions:
        assert isinstance(question, str)
        assert len(question) > 0

    # Check that questions are related to the risk
    risk_keywords = ["data", "migration", "failure", "customer"]
    for question in response.questions:
        assert any(keyword.lower() in question.lower() for keyword in risk_keywords)


@pytest.mark.asyncio
async def test_challenge_risk_chain_with_mock(test_request):
    """Test challenge_risk_chain with mocked BaseChain.invoke."""
    expected_questions = [
        "What data validation procedures will be in place during the migration process?",
        "How will you ensure data integrity if the migration process is interrupted?",
        "What is the rollback strategy if critical data is corrupted during migration?",
    ]
    expected = ChallengeRiskResponse(
        questions=expected_questions,
    )
    with patch(
        "src.riskgpt.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_risk_chain(test_request)
        assert resp.questions == expected_questions
        assert len(resp.questions) == test_request.num_questions


@pytest.mark.asyncio
async def test_challenge_risk_chain_different_audience(test_request):
    """Test challenge_risk_chain with a different audience."""
    # Modify the request to use a different audience
    test_request.audience = AudienceEnum.executive

    # Mock the response
    expected_questions = [
        "What is the potential financial impact if customer data is lost during migration?",
        "How would data loss during migration affect our company's reputation and customer trust?",
        "What contingency plans are in place to ensure business continuity if the migration fails?",
    ]
    expected = ChallengeRiskResponse(
        questions=expected_questions,
    )

    with patch(
        "src.riskgpt.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_risk_chain(test_request)
        assert resp.questions == expected_questions
        assert len(resp.questions) == test_request.num_questions


@pytest.mark.asyncio
async def test_challenge_risk_chain_no_focus_areas(test_request):
    """Test challenge_risk_chain with no focus areas specified."""
    # Modify the request to have no focus areas
    test_request.focus_areas = None

    # Mock the response
    expected_questions = [
        "What are the key vulnerabilities in the data migration process?",
        "How will you verify the integrity of migrated customer data?",
        "What is your response plan if data corruption is detected after migration?",
    ]
    expected = ChallengeRiskResponse(
        questions=expected_questions,
    )

    with patch(
        "src.riskgpt.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_risk_chain(test_request)
        assert resp.questions == expected_questions
        assert len(resp.questions) == test_request.num_questions
