# RiskGPT

RiskGPT provides utilities for analysing project risks and opportunities using LLM based chains. The package is available on PyPI.

```python
from riskgpt import configure_logging
configure_logging()
```

See the `docs/` directory for detailed documentation. An example Jupyter notebook is available in `notebooks/playground.ipynb` for an interactive playground.

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

## Environment Variables

RiskGPT loads configuration from environment variables using a `.env` file at the project root or the regular environment. The following variables are available:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | – | API key for the OpenAI service. Required to use the real model; otherwise a dummy model is used. |
| `OPENAI_MODEL_NAME` | `gpt-4.1-mini` | Name of the OpenAI chat model. |
| `MEMORY_TYPE` | `buffer` | Conversation memory backend. Choose `none`, `buffer` or `redis`. |
| `REDIS_URL` | – | Redis connection string. Needed when `MEMORY_TYPE` is set to `redis`. |
| `DEFAULT_PROMPT_VERSION` | `v1` | Version identifier for prompts under `riskgpt/prompts`. |

## License

RiskGPT is distributed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
