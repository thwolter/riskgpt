# Risk Workflow

The Risk Workflow orchestrates the risk identification and assessment process, integrating with web search and document microservice for enhanced context.

## Overview

The Risk Workflow combines multiple steps into a single workflow:

1. Web search for relevant context
2. Document retrieval from the document microservice
3. Risk identification (using direct implementation to avoid circular dependency)
4. Risk assessment


This workflow is designed to replace the individual chains with a more integrated approach that can leverage web search results and document references.

## Usage

```python
from riskgpt.models.schemas import BusinessContext, RiskRequest
from riskgpt.workflows import risk_workflow

# Create a request
request = RiskRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
        # Optional document references
        document_refs=["doc-uuid-001", "doc-uuid-002"],
    ),
    category="Technical",
    max_risks=5,
    existing_risks=["Data migration failure"],
)

# Run the workflow
response = risk_workflow(request)

# Access the results
for risk in response.risks:
    print(f"Risk: {risk.title}")
    print(f"Description: {risk.description}")
    print(f"Category: {risk.category}")
    if risk.document_refs:
        print(f"Document References: {risk.document_refs}")
    print("---")

# Access document references in the response
if response.document_refs:
    print(f"Document References: {response.document_refs}")

# Access search references in the response
if response.references:
    print(f"Search References: {response.references}")
```

## Asynchronous Usage

```python
import asyncio
from riskgpt.workflows import async_risk_workflow

async def main():
    # Create a request (same as above)
    # ...

    # Run the workflow asynchronously
    response = await async_risk_workflow(request)

    # Access the results (same as above)
    # ...

asyncio.run(main())
```

## Web Search Integration

The workflow includes integration with web search providers to find relevant context for risk identification. This uses the same search functionality as the external_context_enrichment workflow.

```python
# The search is performed automatically

response = risk_workflow(request)

# Access search references in the response
if response.references:
    print(f"Search References: {response.references}")
```

The search query is constructed from the business context and risk category, and the results are used to enhance the risk identification process.

## Document Microservice Integration

The workflow integrates with a document microservice that exposes a `/search` endpoint. The service URL is configured via the `DOCUMENT_SERVICE_URL` environment variable. When set, `fetch_relevant_documents` sends the business context to this endpoint and returns the list of document IDs. If the service is unavailable, the circuit breaker returns an empty list.

```python
from riskgpt.workflows import fetch_relevant_documents

# Fetch relevant documents for a business context
document_refs = fetch_relevant_documents(business_context)
```

## Schema Updates

The following schema models have been updated to include document references:

- `BusinessContext`: Added `document_refs` field to reference documents
- `Risk`: Added `document_refs` field to link risks to relevant documents
- `RiskRequest`: Added `document_refs` field for input document references
- `RiskResponse`: Added `document_refs` field for output document references
- `AssessmentRequest`: Added `document_refs` field for input document references
- `AssessmentResponse`: Added `document_refs` field for output document references

## Deprecation Notice

The following chains have been deprecated in favor of the Risk Workflow:

- `get_risks_chain` and `async_get_risks_chain`: Use `risk_workflow` and `async_risk_workflow` instead
- `get_assessment_chain` and `async_get_assessment_chain`: Use `risk_workflow` and `async_risk_workflow` instead

These chains will continue to work but will issue deprecation warnings.
