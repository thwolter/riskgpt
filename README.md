# RiskGPT

RiskGPT provides utilities for analysing project risks using LLM based chains.

```python
from riskgpt import configure_logging
configure_logging()
```

See the `docs/` directory for details.

An example Jupyter notebook is available in `notebooks/playground.ipynb` for an
interactive playground.


Validation helpers such as `validate_risk_request()` are available in
`riskgpt.processors.input_validator` to convert dictionaries into request
objects.

## Environment Variables

RiskGPT loads configuration from environment variables using a `.env` file at
the project root or the regular environment. The following variables are
available:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | – | API key for the OpenAI service. Required to use the real model; otherwise a dummy model is used. |
| `OPENAI_MODEL_NAME` | `gpt-4.1-mini` | Name of the OpenAI chat model. |
| `MEMORY_TYPE` | `buffer` | Conversation memory backend. Choose `none`, `buffer` or `redis`. |
| `REDIS_URL` | – | Redis connection string. Needed when `MEMORY_TYPE` is set to `redis`. |
| `DEFAULT_PROMPT_VERSION` | `v1` | Version identifier for prompts under `riskgpt/prompts`. |


