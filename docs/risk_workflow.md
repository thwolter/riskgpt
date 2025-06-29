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
from src import BusinessContext, RiskRequest
from src import risk_workflow

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
from src import async_risk_workflow


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


The workflow includes integration with a document microservice that provides relevant documents based on the business context. This integration is currently implemented as a placeholder that will be replaced with actual API calls in the future. Set the `DOCUMENT_SERVICE_URL` environment variable to the base URL of this microservice.

```python
from src import fetch_documents

# Fetch relevant documents for a business context
document_refs = fetch_documents(business_context)
```
