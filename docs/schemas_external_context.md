# External Context Schema Models

This page documents the schema models related to external context enrichment in the RiskGPT application.

## Overview

The external context schema models define the structure for collecting and summarizing external information about a project or sector. These models are used in the external_context_enrichment workflow.

## Models

### SourceEntry

```python
class SourceEntry(BaseModel):
    title: str
    url: str
    date: Optional[str] = None
    type: Optional[str] = None
    comment: Optional[str] = None
```

Structured reference to an external source.

**Fields:**
- `title` (str): Title of the source
- `url` (str): URL of the source
- `date` (Optional[str]): Date of the source
- `type` (Optional[str]): Type of the source (e.g., news, blog, academic)
- `comment` (Optional[str]): Additional comment about the source

**Example:**
```python
{
    "title": "CRM Implementation Challenges in Financial Services",
    "url": "https://example.com/crm-challenges",
    "date": "2023-05-15",
    "type": "industry_report",
    "comment": "Contains relevant case studies",
}
```

### ExternalContextRequest

```python
class ExternalContextRequest(BaseModel):
    business_context: BusinessContext
    focus_keywords: Optional[List[str]] = None
    time_horizon_months: Optional[int] = 12
```

Input model for external context enrichment.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `focus_keywords` (Optional[List[str]]): Specific keywords to focus on
- `time_horizon_months` (Optional[int]): Time horizon in months (default: 12)

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system in a financial services company",
        "language": "en",
    },
    "focus_keywords": ["cybersecurity", "data privacy", "compliance"],
    "time_horizon_months": 6,
}
```

### ExternalContextResponse

```python
class ExternalContextResponse(BaseModel):
    sector_summary: str
    external_risks: List[str]
    source_table: List[Dict[str, str]]
    workshop_recommendations: List[str]
    full_report: Optional[str] = None
    response_info: Optional[ResponseInfo] = None
```

Output model containing summarised external information.

**Fields:**
- `sector_summary` (str): Short overview of relevant developments
- `external_risks` (List[str]): Bullet point risks or drivers
- `source_table` (List[Dict[str, str]]): Table of sources with title, url, date, type, and comment
- `workshop_recommendations` (List[str]): Suggestions for the workshop
- `full_report` (Optional[str]): Optional long-form text
- `response_info` (Optional[ResponseInfo]): Information about the response processing

**Example:**
```python
{
    "sector_summary": "The financial services sector has seen increased regulatory scrutiny around CRM implementations in the past 6 months, with a focus on data privacy and security.",
    "external_risks": [
        "Potential issue: New GDPR compliance requirements for CRM systems",
        "Potential issue: Recent data breach at competitor using similar CRM system",
        "Potential issue: Industry-wide shortage of experienced CRM implementation specialists",
    ],
    "source_table": [
        {
            "title": "New GDPR Requirements for Financial CRM Systems",
            "url": "https://example.com/gdpr-crm",
            "date": "2023-04-10",
            "type": "regulatory_update",
            "comment": "Directly applicable to our implementation",
        },
        {
            "title": "Major Data Breach at FinCorp CRM System",
            "url": "https://example.com/fincorp-breach",
            "date": "2023-03-22",
            "type": "news",
            "comment": "Similar system architecture to our planned implementation",
        },
    ],
    "workshop_recommendations": [
        "Review source: New GDPR Requirements for Financial CRM Systems",
        "Review source: Major Data Breach at FinCorp CRM System",
    ],
    "response_info": {
        "consumed_tokens": 0,
        "total_cost": 0.0,
        "prompt_name": "external_context_enrichment",
        "model_name": "",
    },
}
```

## Usage

These models are used in the external_context_enrichment workflow to collect and summarize external information about a project or sector.

### External Context Enrichment

```python
from src.models.schemas import BusinessContext, ExternalContextRequest
from src.workflows import enrich_context

# Create a request
request = ExternalContextRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system in a financial services company",
        domain_knowledge="The company is subject to strict regulatory requirements",
    ),
    focus_keywords=["cybersecurity", "data privacy", "compliance"],
    time_horizon_months=6,
)

# Run the workflow
response = external_context_enrichment(request)

# Access the results
print(f"Sector Summary: {response.sector_summary}")

print("\nExternal Risks:")
for risk in response.external_risks:
    print(f"- {risk}")

print("\nSources:")
for source in response.source_table:
    print(f"- {source['title']} ({source['url']})")
    if 'date' in source and source['date']:
        print(f"  Date: {source['date']}")
    if 'type' in source and source['type']:
        print(f"  Type: {source['type']}")
    if 'comment' in source and source['comment']:
        print(f"  Comment: {source['comment']}")

print("\nWorkshop Recommendations:")
for recommendation in response.workshop_recommendations:
    print(f"- {recommendation}")
```

### Search Configuration

The external context enrichment workflow relies on search providers that can be configured using environment variables:

```python
# Example .env file configuration
SEARCH_PROVIDER=duckduckgo  # Options: duckduckgo, google, wikipedia
INCLUDE_WIKIPEDIA=true  # Whether to include Wikipedia results
GOOGLE_CSE_ID=your_cse_id  # Required for Google search
GOOGLE_API_KEY=your_api_key  # Required for Google search
```

The workflow performs searches in different categories:
- News search: For recent news articles
- Professional search: For professional content (LinkedIn)
- Regulatory search: For regulatory information
- Peer search: For competitor incidents

### Integration with Risk Workflow

The external context information can be used to enhance the risk workflow:

```python
from src.models.schemas import BusinessContext, ExternalContextRequest, RiskRequest
from src.workflows import enrich_context, risk_workflow

# First, get external context
context_request = ExternalContextRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system in a financial services company",
    ),
    focus_keywords=["cybersecurity", "data privacy"],
)
context_response = external_context_enrichment(context_request)

# Extract key insights from external context
external_insights = context_response.sector_summary
if context_response.external_risks:
    external_insights += "\n\nExternal risks:\n" + "\n".join(context_response.external_risks)

# Use the insights in the risk workflow
risk_request = RiskRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system in a financial services company",
        domain_knowledge=f"The company is subject to strict regulatory requirements. {external_insights}",
    ),
    category="Technical",
)
risk_response = risk_workflow(risk_request)
```