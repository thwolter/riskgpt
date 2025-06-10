import os
from unittest.mock import patch

import pytest

from riskgpt.models.schemas import BusinessContext, LanguageEnum, RiskRequest
from riskgpt.workflows import (
    async_risk_workflow,
    fetch_relevant_documents,
    risk_workflow,
)


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_risk_workflow_basic():
    """Test the basic functionality of the risk workflow."""
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        category="Technical",
        existing_risks=["Data loss"],
    )
    response = risk_workflow(request)
    assert isinstance(response.risks, list)
    assert len(response.risks) > 0
    assert response.risks[0].title
    assert response.risks[0].description
    assert response.risks[0].category


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_risk_workflow_with_document_refs():
    """Test the risk workflow with document references."""
    # Create a request with document_refs
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
            document_refs=["doc-uuid-001", "doc-uuid-002"],
        ),
        category="Technical",
        existing_risks=["Data loss"],
    )

    # Run the workflow
    response = risk_workflow(request)

    # Check that document_refs are in the response
    assert hasattr(response, "document_refs")
    assert response.document_refs is not None
    assert len(response.document_refs) == 2
    assert "doc-uuid-001" in response.document_refs
    assert "doc-uuid-002" in response.document_refs


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.asyncio
async def test_async_risk_workflow():
    """Test the async version of the risk workflow."""
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        category="Technical",
        existing_risks=["Data loss"],
    )
    response = await async_risk_workflow(request)
    assert isinstance(response.risks, list)
    assert len(response.risks) > 0


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_fetch_relevant_documents():
    """Test the placeholder function for fetching relevant documents."""
    context = BusinessContext(
        project_id="123",
        project_description="A new IT project to implement a CRM system.",
        domain_knowledge="The company operates in the B2B sector.",
        language=LanguageEnum.english,
    )

    # The function should return a list of document UUIDs
    docs = fetch_relevant_documents(context)
    assert isinstance(docs, list)
    assert len(docs) > 0
    assert isinstance(docs[0], str)


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@patch("riskgpt.workflows.risk_workflow.fetch_relevant_documents")
def test_risk_workflow_with_mocked_document_service(mock_fetch):
    """Test the risk workflow with a mocked document service."""
    # Mock the document service to return specific UUIDs
    mock_fetch.return_value = ["mock-doc-001", "mock-doc-002", "mock-doc-003"]

    # Create a request
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        category="Technical",
        existing_risks=["Data loss"],
    )

    # Run the workflow
    response = risk_workflow(request)

    # Check that the mock was called
    mock_fetch.assert_called_once()

    # Check that document_refs are in the response and match the mocked values
    assert hasattr(response, "document_refs")
    assert response.document_refs is not None
    assert len(response.document_refs) == 3
    assert "mock-doc-001" in response.document_refs
    assert "mock-doc-002" in response.document_refs
    assert "mock-doc-003" in response.document_refs


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_risk_workflow_basic():
    """Test the risk workflow with additional features disabled."""
    # Create a request
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        category="Technical",
        existing_risks=["Data loss"],
    )

    # Run the workflow with features disabled
    response = risk_workflow(request, use_full_workflow=False)

    # Check that we have risks but no assessments
    assert isinstance(response.risks, list)
    assert len(response.risks) > 0
    assert response.risks[0].title
    assert response.risks[0].description
    assert response.risks[0].category

    # Document references should not be present when features are disabled
    assert not hasattr(response, "document_refs") or response.document_refs is None


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@patch("riskgpt.workflows.risk_workflow.perform_search")
def test_risk_workflow_with_search(mock_search):
    """Test the risk workflow with search functionality."""
    # Mock the search function to return specific results
    mock_search.return_value = (
        [
            {
                "title": "Common Technical Risks in IT Projects",
                "url": "https://example.com/risks",
                "date": "2023-01-01",
                "type": "risk_context",
                "comment": "Overview of technical risks in IT projects",
            },
            {
                "title": "CRM Implementation Challenges",
                "url": "https://example.com/crm",
                "date": "2023-02-01",
                "type": "risk_context",
                "comment": "Specific challenges in CRM implementations",
            },
        ],
        True,  # Success flag
    )

    # Create a request
    request = RiskRequest(
        business_context=BusinessContext(
            project_id="123",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        category="Technical",
        existing_risks=["Data loss"],
    )

    # Run the workflow
    response = risk_workflow(request)

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
