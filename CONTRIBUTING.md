# Contributing

Thank you for considering contributing to **RiskGPT**!

## Getting Started

1. Install dependencies including development tools:
   ```bash
   poetry install --with dev
   ```
2. Install the pre-commit hooks:
   ```bash
   pre-commit install
   ```
3. Create a feature branch and start hacking.

## Code Quality

All contributions must pass the automated checks:

- Formatting via **black**.
- Linting via **ruff**.
- Static type checking with **mypy**.
- Tests with **pytest** with at least 80% coverage.

Run the checks locally with:

```bash
pre-commit run --all-files
pytest --cov=riskgpt
```

Please include tests for new functionality.

## Pull Requests

Ensure the CI pipeline is green before requesting a review. A clear description of the change and the reasoning behind it is appreciated.
