# Research Workflow

The Research Workflow orchestrates the process of gathering, extracting, and summarizing information from various external sources to provide enriched context for risk analysis and decision-making.

## Overview

The Research Workflow combines multiple steps into a single workflow:

1. Search for relevant information across multiple sources and scopes
2. Extract key points from search results
3. Deduplicate and summarize key points
4. Aggregate results into a comprehensive report

This workflow is designed to provide a comprehensive view of available information by leveraging multiple search providers specialized for different types of content.

## Usage

```python
from riskgpt.models.workflows.context import ResearchRequest
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import ScopeEnum
from riskgpt.workflows.research import get_research_graph

# Create a request
request = ResearchRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    focus_keywords=["security", "data migration", "integration"],
    scopes=[ScopeEnum.NEWS, ScopeEnum.ACADEMIC, ScopeEnum.REGULATORY]
)

# Get the research graph
graph = get_research_graph(request)

# Execute the graph
state = await graph.ainvoke({})

# Access the results
response = state["response"]
print(f"Summary: {response.summary}")
print(f"Recommendations: {response.recommendations}")
print(f"Full Report: {response.full_report}")
```

## Search Providers

The Research Workflow uses different search providers for different types of content:

| Provider | Purpose | When Used | Features |
|----------|---------|-----------|----------|
| **Tavily** | General-purpose search engine with AI-optimized results | Default provider and for News, Regulatory, Peer, and Document scopes | Supports different topics (general, news, finance), includes raw content |
| **Semantic Scholar** | Academic paper search | Academic scope | Specialized for academic papers, includes citation formatting, handles author lists |
| **Google** | Web search with high precision | LinkedIn scope | Requires API key and Custom Search Engine ID |
| **DuckDuckGo** | Privacy-focused web search | Fallback when other providers fail | No API key required, more privacy-focused |
| **Wikipedia** | Encyclopedia knowledge | Optional addition to any search | Context-aware inclusion based on query type |

The choice of search provider for each scope is configured in the settings:

```python
SCOPE_SEARCH_PROVIDERS = {
    "academic": "semantic_scholar",
    "news": "tavily",
    "regulatory": "tavily",
    "linkedin": "google",
    "peer": "tavily",
    "document": "tavily",
}
```

### Why These Providers?

- **Tavily**: Provides AI-optimized search results that are particularly useful for general information gathering and recent news.
- **Semantic Scholar**: Specialized for academic research, providing structured data about papers including citations and author information.
- **Google**: Offers high precision for specific queries, particularly useful for professional profiles and company information.
- **DuckDuckGo**: Serves as a reliable fallback option that doesn't require API keys.
- **Wikipedia**: Provides encyclopedic knowledge that can be useful for general background information.

## Workflow Description

The Research Workflow operates as a directed graph with the following nodes:

1. **Start Node**: Initializes the workflow state.

2. **Search Nodes**: For each scope specified in the request:
   - Creates a search request for that scope
   - Uses the appropriate search provider for that scope
   - Executes the search and stores results in the state

3. **Extract Key Points Nodes**: For each scope:
   - Processes the search results for that scope
   - Extracts key points relevant to the focus keywords
   - Attaches source information to each key point

4. **Summarize Key Points Node**:
   - Deduplicates key points to remove redundancy
   - Summarizes the key points into a coherent narrative
   - Organizes information in a structured format

5. **Aggregate Node**:
   - Combines all information into a final response
   - Creates recommendations based on the most relevant sources
   - Formats the full report with proper citations

## Visualization

The workflow can be visualized in Jupyter notebooks using the following code:

```python
from IPython.display import Image, display
from riskgpt.workflows.research import get_research_graph
from riskgpt.models.workflows.context import ResearchRequest
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import ScopeEnum

# Create a request
request = ResearchRequest(
    business_context=BusinessContext(
        project_id="Sample Project",
        project_description="A sample project for visualization",
        domain_knowledge="sample domain",
    ),
    focus_keywords=["sample", "keywords"],
    scopes=[ScopeEnum.NEWS, ScopeEnum.ACADEMIC]
)

# Get the graph
graph = get_research_graph(request)

# Visualize the graph
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Could not visualize graph: {e}")
    print("Make sure you have graphviz installed.")
```

## Error Handling

The Research Workflow includes robust error handling:

- Circuit breakers to prevent cascading failures when search providers are unavailable
- Fallback mechanisms to try alternative search providers when primary ones fail
- Graceful degradation to provide partial results when some components fail

If all search providers fail, the workflow will still complete but will indicate that no external data could be retrieved.