# External Context Enrichment

The `research` workflow collects recent external information about a project or sector and provides a short summary for workshop preparation.

**Note**: The workflow relies on live searches using the configured search provider (DuckDuckGo, Google Custom Search API, or Wikipedia). If network access is
restricted or the required API keys are missing, the search steps will fail and the response may be empty.

## Configuration

The search provider can be configured using environment variables:

- `SEARCH_PROVIDER`: The search provider to use. Options are `duckduckgo` (default), `google`, `wikipedia`, or `tavily`.
- `INCLUDE_WIKIPEDIA`: Whether to include Wikipedia results in addition to the primary search provider. Set to `true` or `false` (default).
- `GOOGLE_CSE_ID`: Google Custom Search Engine ID. Required when `SEARCH_PROVIDER` is set to `google`.
- `GOOGLE_API_KEY`: Google API key. Required when `SEARCH_PROVIDER` is set to `google`.
- `TAVILY_API_KEY`: Tavily API key. Required when `SEARCH_PROVIDER` is set to `tavily`.

## Input

`ResearchRequest`
- `business_context` (`BusinessContext`): object containing:
  - `project_id` (`str`): unique identifier for the project.
  - `project_description` (`str`, optional): detailed description of the project.
  - `domain_knowledge` (`str`, optional): specific domain knowledge relevant to the project.
  - `business_area` (`str`, optional): business area or department the project belongs to.
  - `industry_sector` (`str`, optional): industry sector the project operates in.
  - `document_refs` (`List[str]`, optional): references to document UUIDs.
- `focus_keywords` (`List[str]`, optional): keywords to refine the search.
- `time_horizon_months` (`int`, optional, default `12`): restrict search to the last months.
- `max_search_results` (`int`, default `3`): maximum number of search results to return per topic.
- `region` (`str`, default `"wt-wt"`): region for search results, default is worldwide.

## Output

`ResearchResponse`
- `sector_summary` (`str`): short overview of relevant developments.
- `workshop_recommendations` (`List[str]`): suggestions for the workshop.
- `full_report` (`str | None`, optional): optional long-form text.
- `response_info` (`ResponseInfo | None`, optional): token and cost meta information.

## Example

```python
from riskgpt.workflows import research
from riskgpt.models.workflows import ResearchRequest, ResearchResponse
from riskgpt.models.common import BusinessContext

request = ResearchRequest(
  business_context=BusinessContext(
    project_id="FiberOpticProject2023",
    project_description="Fiber optic infrastructure deployment for high-speed internet in rural areas",
    domain_knowledge="We have capabilities in telecommunications and network infrastructure.",
  ),
  focus_keywords=["ethics, sustainability, regulatory compliance"],
)

result: ResearchResponse = await research(request)
print("Sector Summary:")
print(result.summary)
print("\nFull Report Risks:")
print(result.full_report)
print("\nWorkshop Recommendations:")
for i, rec in enumerate(result.recommendations, 1):
  print(f"{i}. {rec}")
```
