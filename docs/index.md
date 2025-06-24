# RiskGPT

RiskGPT is a Python package for analyzing project-related risks and opportunities using LLM-based chains.

[![PyPI](https://img.shields.io/pypi/v/riskgpt)](https://pypi.org/project/riskgpt/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linted by Ruff](https://img.shields.io/badge/lint-ruff-green.svg)](https://docs.astral.sh/ruff/)
[![Checked with mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![License: MIT](https://img.shields.io/pypi/l/riskgpt.svg)](https://github.com/thwolter/riskgpt/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/riskgpt)](https://pypi.org/project/riskgpt/)

---

## Installation

Install the latest release from [PyPI](https://pypi.org/project/riskgpt/):
```bash
pip install src
```



## Features

- Extract risk categories from project descriptions
- Identify specific risks per category
- Assess impact using distributions or probability estimates with supporting evidence
- Support for domain-specific context and memory

## Chains

- [Get Categories](get_categories.md) – determine relevant risk categories for a project description
- [Get Risks](get_risks.md) – identify risks for a specific category (deprecated)
- [Get Assessment](get_assessment.md) – estimate impact and probability of a risk (deprecated)
- [Risk Workflow](risk_workflow.md) – orchestrate risk identification and assessment with document integration
- [Prioritize Risks](prioritize_risks.md) – rank risks by urgency or impact
- [Cost Benefit](cost_benefit.md) – estimate effort versus benefit of mitigations
- [Get Monitoring](get_monitoring.md) – derive indicators for ongoing monitoring
- [Get Opportunities](get_opportunities.md) – detect positive developments
- [Communicate Risks](communicate_risks.md) – create stakeholder summaries
- [Prepare Presentation Output](design/prepare_presentation_output.md) – combine chains for slides
- [Audience Output Matrix](design/audience_output.md) – target group specifics
- [External Context Enrichment](external_context_enrichment.md) – summarise recent external information
- [Check Context Quality](check_context_quality.md) – validate project background

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
<!-- The following link was removed because README.md is not part of the documentation build -->
