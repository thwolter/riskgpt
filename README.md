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

