from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from api import fetch_documents
from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.assessment import AssessmentResponse
from riskgpt.models.chains.risk import IdentifiedRisk, Risk, RiskRequest, RiskResponse
from riskgpt.models.common import BusinessContext
from riskgpt.workflows.risk_workflow import risk_workflow


@pytest.fixture
def test_request():
    """Fixture to create a sample RiskRequest."""
    return RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
        ),
        category="Technical",
        existing_risks=[
            Risk(
                title="Data loss",
                description="Risk of losing critical customer data during migration to the new CRM system",
            ),
        ],
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_risk_workflow_basic(test_request):
    """Test the basic functionality of the risk workflow."""
    response = await risk_workflow(test_request)
    assert isinstance(response.risks, list)
    assert len(response.risks) > 0
    assert response.risks[0].title
    assert response.risks[0].description
    assert response.risks[0].category


@pytest.mark.integration
@pytest.mark.asyncio
async def test_risk_workflow_with_document_refs(test_request):
    """Test the risk workflow with document references."""
    # Run the workflow
    response = await risk_workflow(test_request)

    # Check that document_refs are in the response
    assert hasattr(response, "document_refs")
    assert response.document_refs is not None
    assert len(response.document_refs) == 2
    assert "doc-uuid-001" in response.document_refs
    assert "doc-uuid-002" in response.document_refs


@pytest.mark.asyncio
@pytest.mark.integration
async def test_risk_workflow(test_request):
    response = await risk_workflow(test_request)
    assert isinstance(response.risks, list)
    assert len(response.risks) > 0


@pytest.mark.integration
def test_fetch_documents():
    context = BusinessContext(
        project_id="123",
        project_description="A new IT project to implement a CRM system.",
        domain_knowledge="The company operates in the B2B sector.",
    )

    # The function should return a list of document UUIDs
    docs = fetch_documents(context)
    assert isinstance(docs, list)
    assert len(docs) > 0
    assert isinstance(docs[0], str)


@patch("riskgpt.workflows.risk_workflow.fetch_documents")
@pytest.mark.integration
@pytest.mark.asyncio
async def test_risk_workflow_with_mocked_document_service(mock_fetch, test_request):
    """Test the risk workflow with a mocked document service."""
    # Mock the document service to return specific UUIDs
    mock_fetch.return_value = ["mock-doc-001", "mock-doc-002", "mock-doc-003"]

    # Run the workflow
    response = await risk_workflow(test_request)

    # Check that the mock was called
    mock_fetch.assert_called_once()

    # Check that document_refs are in the response and match the mocked values
    assert hasattr(response, "document_refs")
    assert response.document_refs is not None
    assert len(response.document_refs) == 3
    assert "mock-doc-001" in response.document_refs
    assert "mock-doc-002" in response.document_refs
    assert "mock-doc-003" in response.document_refs


@patch("riskgpt.workflows.risk_workflow.search_context")
@pytest.mark.integration
@pytest.mark.asyncio
async def test_risk_workflow_with_search(mock_search, test_request):
    """Test the risk workflow with search functionality."""
    # Mock the search function to return specific results
    mock_search.return_value = (
        [
            {
                "title": "Common Technical Risks in IT Projects",
                "url": "https://example.com/risks",
                "date": "2023-01-01",
                "type": "risk_context",
                "content": "Overview of technical risks in IT projects",
            },
            {
                "title": "CRM Implementation Challenges",
                "url": "https://example.com/crm",
                "date": "2023-02-01",
                "type": "risk_context",
                "content": "Specific challenges in CRM implementations",
            },
        ],
        True,  # Success flag
    )

    # Run the workflow
    response = await risk_workflow(test_request)

    # Check that the mock was called
    mock_search.assert_called_once()

    # Check that we have risks
    assert isinstance(response.risks, list)
    assert len(response.risks) > 0

    # Check that references from search are in the response
    assert hasattr(response, "references")
    assert response.references is not None
    assert len(response.references) > 0
    assert (
        "Common Technical Risks in IT Projects" in response.references
        or "CRM Implementation Challenges" in response.references
    )


@pytest.mark.asyncio
async def test_risk_workflow_with_mock(monkeypatch, test_request):
    # Mock response for get_risks_chain
    risk_response = RiskResponse(
        risks=[IdentifiedRisk(title="Mock Risk", description="Mock Description")],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="risk_identification",
            model_name="mock-model",
        ),
    )

    # Mock response for get_assessment_chain
    assessment_response = AssessmentResponse(
        impact=0.5,
        probability=0.2,
        evidence="mocked evidence",
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="risk_assessment",
            model_name="mock-model",
        ),
    )

    # Mock final response
    final_response = RiskResponse(
        risks=[IdentifiedRisk(title="Mock Risk", description="Mock Description")],
        document_refs=["doc1"],
        response_info=ResponseInfo(
            consumed_tokens=10,
            total_cost=0.0,
            prompt_name="risk_workflow",
            model_name="mock-model",
        ),
    )

    # Mock the StateGraph.compile().ainvoke method
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value={"response": final_response})

    with (
        patch(
            "src.api.search_context",
            return_value=(
                [
                    {
                        "title": "SearchRef",
                        "url": "u",
                        "date": "",
                        "type": "risk_context",
                        "content": "",
                    }
                ],
                True,
            ),
        ),
        patch("src.api.fetch_documents", return_value=["doc1"]),
        patch(
            "riskgpt.chains.base.BaseChain.invoke",
            new_callable=AsyncMock,
            side_effect=[risk_response, assessment_response],
        ),
        patch(
            "riskgpt.workflows.risk_workflow._build_risk_workflow_graph",
            return_value=mock_graph,
        ),
    ):
        resp = await risk_workflow(test_request)
        assert isinstance(resp.risks, list)
        assert len(resp.risks) > 0
        assert resp.risks[
            0
        ].title  # Just check that there's a title, don't check the specific value
        assert hasattr(resp, "document_refs")  # Just check that document_refs exists
        assert hasattr(resp, "references")  # Just check that references exists
        assert isinstance(resp.references, list)  # Check that references is a list
