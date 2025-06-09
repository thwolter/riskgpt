# RiskGPT


[![PyPI version](https://badge.fury.io/py/riskgpt.svg)](https://pypi.org/project/riskgpt/)
[![PyPI](https://img.shields.io/pypi/v/riskgpt)](https://pypi.org/project/riskgpt/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linted by Ruff](https://img.shields.io/badge/lint-ruff-green.svg)](https://docs.astral.sh/ruff/)
[![Checked with mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![License: MIT](https://img.shields.io/pypi/l/riskgpt.svg)](https://github.com/<USER_OR_ORG>/riskgpt/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/riskgpt)](https://pypi.org/project/riskgpt/)

RiskGPT provides utilities for analysing project risks and opportunities using LLM based chains. The package is available on PyPI.

```python
from riskgpt import configure_logging
configure_logging()
```

See the `docs/` directory for detailed documentation.

Validation helpers such as `validate_risk_request()` are available in `riskgpt.processors.input_validator` to convert dictionaries into request objects.

## Installation

Install the latest release from PyPI:

```bash
pip install riskgpt
```


For development this project uses [Poetry](https://python-poetry.org/) for dependency management. Install all dependencies including the development tools with:

```bash
poetry install --with dev
```

## Development

Install the pre-commit hooks once:

```bash
pre-commit install
```

The hooks run black, ruff and mypy on each commit. Tests are executed with `pytest` and coverage is measured via `pytest-cov`.

Run the full test suite locally with:

```bash
pytest --cov=riskgpt
```

## Circuit Breaker Pattern

RiskGPT implements a circuit breaker pattern for external API calls to handle service outages gracefully. The circuit breaker prevents sending requests to services that are likely to fail, reducing latency and conserving resources. It also allows the application to degrade gracefully when external services are unavailable.

The circuit breaker is implemented for:
- OpenAI API calls in the `BaseChain` class
- Search API calls (DuckDuckGo, Google Custom Search, Wikipedia) in the external context enrichment workflow

When the circuit is open (after multiple failures), the application will use fallback mechanisms:
- For OpenAI: Returns a minimal valid response with an error message
- For search providers: Returns empty results and continues with other data sources

The circuit breaker requires the `pybreaker` library. If not available, a fallback implementation is used that doesn't break the circuit.

## Environment Variables

RiskGPT loads configuration from environment variables using a `.env` file at the project root or the regular environment. The following variables are available:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | – | API key for the OpenAI service. Required to use the real model; otherwise a dummy model is used. |
| `OPENAI_MODEL_NAME` | `gpt-4.1-mini` | Name of the OpenAI chat model. |
| `MEMORY_TYPE` | `buffer` | Conversation memory backend. Choose `none`, `buffer` or `redis`. |
| `REDIS_URL` | – | Redis connection string. Needed when `MEMORY_TYPE` is set to `redis`. |
| `DEFAULT_PROMPT_VERSION` | `v1` | Version identifier for prompts under `riskgpt/prompts`. |
| `SEARCH_PROVIDER` | `duckduckgo` | Search provider for external context enrichment. Choose `duckduckgo`, `google`, or `wikipedia`. |
| `INCLUDE_WIKIPEDIA` | `False` | Whether to include Wikipedia results in addition to the primary search provider. |
| `GOOGLE_CSE_ID` | – | Google Custom Search Engine ID. Required when `SEARCH_PROVIDER` is set to `google`. |
| `GOOGLE_API_KEY` | – | Google API key. Required when `SEARCH_PROVIDER` is set to `google`. |

## License

RiskGPT is distributed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
