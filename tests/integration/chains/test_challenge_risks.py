from unittest.mock import AsyncMock, patch

import pytest

from src import challenge_risks_chain
from src import (
    ChallengeRisksRequest,
    ChallengeRisksResponse,
    RiskQuestions,
)
from src import Risk
from src import BusinessContext
from src import AudienceEnum


@pytest.fixture
def test_risks():
    """Fixture to create sample Risk objects."""
    return [
        Risk(
            title="Data Migration Failure",
            description="Risk of losing critical customer data during migration to the new CRM system",
            category="Technical",
        ),
        Risk(
            title="User Adoption Issues",
            description="Risk of low user adoption due to resistance to change",
            category="Organizational",
        ),
    ]


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
def test_request(test_risks, test_business_context):
    """Fixture to create a sample ChallengeRisksRequest."""
    return ChallengeRisksRequest(
        risks=test_risks,
        business_context=test_business_context,
        audience=AudienceEnum.risk_internal,
        focus_areas=["implementation strategy", "change management"],
        questions_per_risk=2,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_challenge_risks_chain(test_request):
    """Test challenge_risks_chain with actual invocation."""

    response = await challenge_risks_chain(test_request)
    assert isinstance(response, ChallengeRisksResponse)
    assert isinstance(response.risk_questions, list)
    assert len(response.risk_questions) == len(test_request.risks)

    # Check that each risk has the correct number of questions
    for risk_question in response.risk_questions:
        assert isinstance(risk_question, RiskQuestions)
        assert isinstance(risk_question.risk_title, str)
        assert isinstance(risk_question.questions, list)
        assert len(risk_question.questions) == test_request.questions_per_risk

        # Check that each question is a non-empty string
        for question in risk_question.questions:
            assert isinstance(question, str)
            assert len(question) > 0

    # Check that risk titles match
    risk_titles = [risk.title for risk in test_request.risks]
    response_titles = [rq.risk_title for rq in response.risk_questions]
    assert set(risk_titles) == set(response_titles)


@pytest.mark.asyncio
async def test_challenge_risks_chain_with_mock(test_request):
    """Test challenge_risks_chain with mocked BaseChain.invoke."""
    expected_risk_questions = [
        RiskQuestions(
            risk_title="Data Migration Failure",
            questions=[
                "What data validation procedures will be in place during the migration process?",
                "How will you ensure data integrity if the migration process is interrupted?",
            ],
        ),
        RiskQuestions(
            risk_title="User Adoption Issues",
            questions=[
                "What change management strategies will be implemented to address resistance?",
                "How will you measure and track user adoption rates?",
            ],
        ),
    ]
    expected = ChallengeRisksResponse(
        risk_questions=expected_risk_questions,
    )
    with patch(
        "src.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_risks_chain(test_request)
        assert resp.risk_questions == expected_risk_questions
        assert len(resp.risk_questions) == len(test_request.risks)
        for risk_question in resp.risk_questions:
            assert len(risk_question.questions) == test_request.questions_per_risk


@pytest.mark.asyncio
async def test_challenge_risks_chain_different_audience(test_request):
    """Test challenge_risks_chain with a different audience."""
    # Modify the request to use a different audience
    test_request.audience = AudienceEnum.executive

    # Mock the response
    expected_risk_questions = [
        RiskQuestions(
            risk_title="Data Migration Failure",
            questions=[
                "What is the potential financial impact if customer data is lost during migration?",
                "What contingency plans are in place to ensure business continuity if the migration fails?",
            ],
        ),
        RiskQuestions(
            risk_title="User Adoption Issues",
            questions=[
                "How will user adoption issues impact the ROI of the CRM implementation?",
                "What executive-level strategies can be employed to drive user adoption?",
            ],
        ),
    ]
    expected = ChallengeRisksResponse(
        risk_questions=expected_risk_questions,
    )

    with patch(
        "src.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_risks_chain(test_request)
        assert resp.risk_questions == expected_risk_questions
        assert len(resp.risk_questions) == len(test_request.risks)


@pytest.mark.asyncio
async def test_challenge_risks_chain_no_focus_areas(test_request):
    """Test challenge_risks_chain with no focus areas specified."""
    # Modify the request to have no focus areas
    test_request.focus_areas = None

    # Mock the response
    expected_risk_questions = [
        RiskQuestions(
            risk_title="Data Migration Failure",
            questions=[
                "What are the key vulnerabilities in the data migration process?",
                "How will you verify the integrity of migrated customer data?",
            ],
        ),
        RiskQuestions(
            risk_title="User Adoption Issues",
            questions=[
                "What are the main factors that could lead to user resistance?",
                "How will you identify and address early signs of adoption issues?",
            ],
        ),
    ]
    expected = ChallengeRisksResponse(
        risk_questions=expected_risk_questions,
    )

    with patch(
        "src.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_risks_chain(test_request)
        assert resp.risk_questions == expected_risk_questions
        assert len(resp.risk_questions) == len(test_request.risks)
