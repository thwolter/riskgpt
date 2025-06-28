# RiskGPT

RiskGPT provides utilities for analyzing project risks and opportunities using LLM-based chains. The package leverages LangChain and LangGraph to create sophisticated workflows for risk assessment, analysis, and mitigation planning.

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
pip install riskgpt
```

You can also install directly from GitHub:
```bash
pip install git+https://github.com/thwolter/riskgpt.git
```



## Features

- Risk and opportunity identification and analysis
- Cost-benefit analysis for risk mitigation strategies
- External context enrichment through web search
- Circuit breaker pattern for resilient external API calls
- Conversation memory with multiple backend options
- Programmatic API for direct access to search and document services

## Helpers

- [Search](search.md) – unified interface for web search providers (DuckDuckGo, Google, Wikipedia, Tavily)

## Chains

- [Risk Categories](risk_categories.md) – determine relevant risk categories for a project description
- [Check Definition](check_definition.md) – validate risk definitions
- [Risk Drivers](risk_drivers.md) – identify underlying causes of risks
- [Risk Assessment](risk_assessment.md) – estimate impact and probability of a risk
- [Risk Mitigations](risk_mitigations.md) – develop strategies to address risks
- [Risk Indicators](risk_indicators.md) – derive indicators for ongoing monitoring
- [Opportunities](opportunities.md) – detect positive developments
- [Risk Identification](risk_identification.md) – identify risks for a specific category
- [Prioritize Risks](prioritize_risks.md) – rank risks by urgency or impact
- [Cost Benefit](cost_benefit.md) – estimate effort versus benefit of mitigations
- [Communicate Risks](communicate_risks.md) – create stakeholder summaries

## Workflows

- [Risk Workflow](risk_workflow.md) – orchestrate risk identification and assessment with document integration
- [Prepare Presentation Output](prepare_presentation_output.md) – combine chains for slides
- [External Context Enrichment](external_context_enrichment.md) – summarize recent external information
- [Check Context Quality](check_context_quality.md) – validate project background
- [Publishing](publishing.md) – publish risk assessment results

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

## Configuration

RiskGPT loads configuration from environment variables using a `.env` file at the project root or the regular environment.

Available environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | – | API key for the OpenAI service. Required to use the real model; otherwise a dummy model is used. |
| `OPENAI_MODEL_NAME` | `openai:gpt-4.1-nano` | Name of the OpenAI chat model. |
| `TEMPERATURE` | `0.7` | Temperature parameter for the model's response. Higher values make the output more random. |
| `MAX_TOKENS` | – | Maximum number of tokens in the model's response. This value might be adjusted depending on the model being used. |
| `MEMORY_TYPE` | `buffer` | Conversation memory backend. Choose `none`, `buffer` or `redis`. |
| `REDIS_URL` | – | Redis connection string. Needed when `MEMORY_TYPE` is set to `redis`. |
| `DEFAULT_PROMPT_VERSION` | `v1` | Version identifier for prompts under `riskgpt/prompts`. |
| `SEARCH_PROVIDER` | `duckduckgo` | Search provider for external context enrichment. Choose `duckduckgo`, `google`, `wikipedia`, or `tavily`. |
| `MAX_SEARCH_RESULTS` | `3` | Maximum number of search results to return. |
| `INCLUDE_WIKIPEDIA` | `False` | Whether to include Wikipedia results in addition to the primary search provider. |
| `GOOGLE_CSE_ID` | – | Google Custom Search Engine ID. Required when `SEARCH_PROVIDER` is set to `google`. |
| `GOOGLE_API_KEY` | – | Google API key. Required when `SEARCH_PROVIDER` is set to `google`. |
| `TAVILY_API_KEY` | – | Tavily API key. Required when `SEARCH_PROVIDER` is set to `tavily`. |
| `DOCUMENT_SERVICE_URL` | – | Base URL of the document microservice used to retrieve relevant documents in the risk workflow. |
