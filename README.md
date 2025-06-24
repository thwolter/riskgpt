# RiskGPT

[![PyPI version](https://badge.fury.io/py/riskgpt.svg)](https://pypi.org/project/riskgpt/)
[![PyPI](https://img.shields.io/pypi/v/riskgpt)](https://pypi.org/project/riskgpt/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linted by Ruff](https://img.shields.io/badge/lint-ruff-green.svg)](https://docs.astral.sh/ruff/)
[![Checked with mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![License: MIT](https://img.shields.io/pypi/l/riskgpt.svg)](https://github.com/thwolter/riskgpt/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/riskgpt)](https://pypi.org/project/riskgpt/)

## 🎯 Overview

RiskGPT provides utilities for analyzing project risks and opportunities using LLM-based chains. The package leverages LangChain and LangGraph to create sophisticated workflows for risk assessment, analysis, and mitigation planning.

## 🚀 Features

- Risk and opportunity identification and analysis
- Cost-benefit analysis for risk mitigation strategies
- External context enrichment through web search
- Circuit breaker pattern for resilient external API calls
- Conversation memory with multiple backend options
- Programmatic API for direct access to search and document services

## 📁 Project Structure

```
riskgpt/
├── riskgpt/
│   ├── chains/            # LLM chain implementations
│   ├── config/            # Configuration settings
│   ├── models/            # Data models and schemas
│   ├── processors/        # Input/output processors
│   ├── prompts/           # LLM prompts organized by function
│   ├── registry/          # Component registry
│   ├── utils/             # Utility functions
│   ├── workflows/         # Risk assessment workflows
│   ├── api.py             # Public API functions
│   ├── logger.py          # Logging configuration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🛠️ Installation

Install dependencies using [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver:

```bash
uv sync
```

## 💡 Usage

Basic usage example:

```python
from src import configure_logging
from src.models.schemas import BusinessContext
from src.workflows.risk_workflow import run_risk_workflow

# Configure logging
configure_logging()

# Create a business context
context = BusinessContext(
    project_id="ACME-1",
    project_name="ACME Corp Security Upgrade",
    description="Implement new cybersecurity measures across all departments"
)

# Run the risk workflow
result = run_risk_workflow(context)
```

Validation helpers are available in `riskgpt.processors.input_validator` to convert dictionaries into request objects:

```python
from src.processors.input_validator import validate_risk_request
request_dict = {"project_id": "ACME-1", "project_name": "Security Upgrade", ...}
validated_request = validate_risk_request(request_dict)
```

## 🔧 Configuration

RiskGPT loads configuration from environment variables using a `.env` file at the project root or the regular environment.

Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Available environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | – | API key for the OpenAI service. Required to use the real model; otherwise a dummy model is used. |
| `OPENAI_MODEL_NAME` | `gpt-4.1-mini` | Name of the OpenAI chat model. |
| `MAX_TOKENS` | – | Maximum number of tokens in the model's response. This value might be adjusted depending on the model being used. |
| `MEMORY_TYPE` | `buffer` | Conversation memory backend. Choose `none`, `buffer` or `redis`. |
| `REDIS_URL` | – | Redis connection string. Needed when `MEMORY_TYPE` is set to `redis`. |
| `DEFAULT_PROMPT_VERSION` | `v1` | Version identifier for prompts under `riskgpt/prompts`. |
| `SEARCH_PROVIDER` | `duckduckgo` | Search provider for external context enrichment. Choose `duckduckgo`, `google`, or `wikipedia`. |
| `INCLUDE_WIKIPEDIA` | `False` | Whether to include Wikipedia results in addition to the primary search provider. |
| `GOOGLE_CSE_ID` | – | Google Custom Search Engine ID. Required when `SEARCH_PROVIDER` is set to `google`. |
| `GOOGLE_API_KEY` | – | Google API key. Required when `SEARCH_PROVIDER` is set to `google`. |
| `DOCUMENT_SERVICE_URL` | – | Base URL of the document microservice used to retrieve relevant documents in the risk workflow. |

## 🔄 Circuit Breaker Pattern

RiskGPT implements a circuit breaker pattern for external API calls to handle service outages gracefully. The circuit breaker prevents sending requests to services that are likely to fail, reducing latency and conserving resources.

The circuit breaker is implemented for:
- OpenAI API calls in the `BaseChain` class
- Search API calls (DuckDuckGo, Google Custom Search, Wikipedia) in the external context enrichment workflow

When the circuit is open (after multiple failures), the application will use fallback mechanisms:
- For OpenAI: Returns a minimal valid response with an error message
- For search providers: Returns empty results and continues with other data sources

## 🧪 Development

Install the pre-commit hooks once:

```bash
pre-commit install
```

The hooks run black, ruff and mypy on each commit. Tests are executed with `pytest` and coverage is measured via `pytest-cov`.

Run the full test suite locally with:

```bash
pytest --cov=src
```

Unit tests run by default when executing `pytest`:

```bash
pytest
```

Integration tests require real external services and valid API keys:

```bash
export OPENAI_API_KEY=sk-test-123
export DOCUMENT_SERVICE_URL=https://example.com
pytest -m integration
```

## 📚 Programmatic API

RiskGPT exposes helper functions to access search and document services directly:

```python
from src.api import search_context, fetch_documents
from src.models.schemas import BusinessContext

# Search recent news
results, ok = search_context("ACME Corp cybersecurity", "news")

# Retrieve project documents
docs = fetch_documents(BusinessContext(project_id="ACME-1"))
```

## 📄 License

RiskGPT is distributed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.