# RiskGPT

RiskGPT is a Python package for analyzing project-related risks and opportunities using LLM-based chains.

## Features

- Extract risk categories from project descriptions
- Identify specific risks per category
- Assess impact using distributions or probability estimates with supporting evidence
- Support for domain-specific context and memory

## Chains

- [Get Categories](get_categories.md) – determine relevant risk categories for a project description
- [Get Risks](get_risks.md) – identify risks for a specific category
- [Get Assessment](get_assessment.md) – estimate impact and probability of a risk
- [Prioritize Risks](prioritize_risks.md) – rank risks by urgency or impact
- [Cost Benefit](cost_benefit.md) – estimate effort versus benefit of mitigations
- [Get Monitoring](get_monitoring.md) – derive indicators for ongoing monitoring
- [Get Opportunities](get_opportunities.md) – detect positive developments
- [Communicate Risks](communicate_risks.md) – create stakeholder summaries
- [Prepare Presentation Output](design/prepare_presentation_output.md) – combine chains for slides
- [Audience Output Matrix](design/audience_output.md) – target group specifics
- [External Context Enrichment](external_context_enrichment.md) – summarise recent external information

## Logging

Use `riskgpt.configure_logging()` to enable basic logging. Token usage is logged
at the INFO level whenever a chain is executed.


## Input Validation

The module `riskgpt.processors.input_validator` provides convenience functions
for validating dictionaries against the request models. These helpers raise a
`ValueError` if the input does not conform to the schema.

- `validate_category_request`
- `validate_risk_request`
- `validate_assessment_request`
- `validate_mitigation_request`

For information on environment variables and configuration see the
[Environment Variables](../README.md#environment-variables) section in the
README.


