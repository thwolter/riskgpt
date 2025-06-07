# External Context Enrichment

The `external_context_enrichment` workflow collects recent external information about a project or sector and provides a short summary for workshop preparation.

## Input

`ExternalContextRequest`
- `project_name` (`str`): name of the project or company.
- `business_context` (`str`): brief description of the sector or business field.
- `focus_keywords` (`List[str]`, optional): keywords to refine the search.
- `time_horizon_months` (`int`, optional, default `12`): restrict search to the last months.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`ExternalContextResponse`
- `sector_summary` (`str`): short overview of relevant developments.
- `external_risks` (`List[str]`): bullet point risks or drivers.
- `source_table` (`List[Dict[str, str]]`): table of sources with `title`, `url`, `date`, `type`, and `comment`.
- `workshop_recommendations` (`List[str]`): suggestions for the workshop.
- `full_report` (`str | None`): optional long-form text.
- `response_info` (`ResponseInfo | None`): token and cost meta information.

## Example

```python
from riskgpt.workflows import external_context_enrichment
from riskgpt.models.schemas import ExternalContextRequest

req = ExternalContextRequest(
    project_name="SEFE Energy",
    business_context="fiber optic infrastructure",
    focus_keywords=["cyber", "supply chain"],
)
result = external_context_enrichment(req)
print(result.sector_summary)
```
