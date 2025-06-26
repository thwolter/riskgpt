from unittest.mock import AsyncMock, patch

import pytest

from src import (
    AudienceEnum,
    BusinessContext,
    ChallengeQuestionsRequest,
    ChallengeQuestionsResponse,
    challenge_questions_chain,
)


@pytest.fixture
def test_request():
    """Fixture to create a sample ChallengeQuestionsRequest."""
    return ChallengeQuestionsRequest(
        business_context=BusinessContext(
            project_id="CRM-2023",
            project_description="Implementation of a new CRM system",
            domain_knowledge="The company operates in the B2B sector",
            business_area="Sales",
            industry_sector="Technology",
        ),
        audience=AudienceEnum.risk_internal,
        focus_areas=["data security", "user adoption", "integration"],
        num_questions=3,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_challenge_questions_chain(test_request):
    """Test challenge_questions_chain with actual invocation."""

    response = await challenge_questions_chain(test_request)
    assert isinstance(response, ChallengeQuestionsResponse)
    assert isinstance(response.questions, list)
    assert len(response.questions) == test_request.num_questions

    # Check that each question is a non-empty string
    for question in response.questions:
        assert isinstance(question, str)
        assert len(question) > 0


@pytest.mark.asyncio
async def test_challenge_questions_chain_with_mock(test_request):
    """Test challenge_questions_chain with mocked BaseChain.invoke."""
    expected_questions = [
        "What are the potential data security risks when migrating customer data to the new CRM system?",
        "How might the implementation of the new CRM system affect existing sales processes?",
        "What integration challenges might arise with existing systems?",
    ]
    expected = ChallengeQuestionsResponse(
        questions=expected_questions,
    )
    with patch(
        "src.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_questions_chain(test_request)
        assert resp.questions == expected_questions
        assert len(resp.questions) == test_request.num_questions


@pytest.mark.asyncio
async def test_challenge_questions_chain_different_audience(test_request):
    """Test challenge_questions_chain with a different audience."""
    # Modify the request to use a different audience
    test_request.audience = AudienceEnum.executive

    # Mock the response
    expected_questions = [
        "What executive-level concerns exist regarding data security in the CRM implementation?",
        "How will the new CRM system impact executive decision-making processes?",
        "What are the strategic integration risks for the executive team to consider?",
    ]
    expected = ChallengeQuestionsResponse(
        questions=expected_questions,
    )

    with patch(
        "src.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_questions_chain(test_request)
        assert resp.questions == expected_questions
        assert len(resp.questions) == test_request.num_questions


@pytest.mark.asyncio
async def test_challenge_questions_chain_no_focus_areas(test_request):
    """Test challenge_questions_chain with no focus areas specified."""
    # Modify the request to have no focus areas
    test_request.focus_areas = None

    # Mock the response
    expected_questions = [
        "What are the key risks in implementing a new CRM system for a B2B company?",
        "How might the sales team's workflows be disrupted during the CRM transition?",
        "What data migration challenges should be anticipated in this implementation?",
    ]
    expected = ChallengeQuestionsResponse(
        questions=expected_questions,
    )

    with patch(
        "src.chains.base.BaseChain.invoke",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        resp = await challenge_questions_chain(test_request)
        assert resp.questions == expected_questions
        assert len(resp.questions) == test_request.num_questions
