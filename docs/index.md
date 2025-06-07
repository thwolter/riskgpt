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

## Logging

Use `riskgpt.configure_logging()` to enable basic logging. Token usage is logged
at the INFO level whenever a chain is executed.

