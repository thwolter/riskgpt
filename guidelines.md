# RiskGPT Project Guidelines

## Project Overview

RiskGPT is a Python package for analyzing project risks and opportunities using LLM-based chains. It leverages LangChain and LangGraph to create sophisticated workflows for risk assessment, analysis, and mitigation planning.

## Project Structure

```
riskgpt/
├── src/                    # Main source code
│   ├── riskgpt/           # Main package
│       ├── chains/        # LLM chain implementations
│       ├── config/        # Configuration settings
│       ├── helpers/       # Helper functions
│       ├── models/        # Data models and schemas
│       ├── processors/    # Input/output processors
│       ├── prompts/       # LLM prompts organized by function
│       ├── workflows/     # Risk assessment workflows
│       ├── api.py         # Public API functions
│       ├── logger.py      # Logging configuration
│       ├── py.typed       # Marker file for type checking
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── functional/        # Functional tests
│   ├── integration/       # Integration tests (require external services)
│   ├── utils/             # Test utilities
│   ├── conftest.py        # Pytest fixtures and configuration
├── docs/                   # Documentation
├── examples/               # Example notebooks and scripts
├── .env.example            # Environment variables template
├── .github/                # GitHub Actions workflows
├── CHANGELOG.md            # Release history and changes
├── LICENSE                 # Project license
├── mkdocs.yml              # MkDocs configuration
├── pyproject.toml          # Project configuration and dependencies
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── uv.lock                 # Dependency lock file
└── README.md               # Project overview and usage instructions
```

## Development Environment Setup

1. **Python Version**: This project requires Python 3.12 or higher.

2. **Environment Variables**: Copy `.env.example` to `.env` and configure the required variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Package Installation**: Use [Poetry](https://python-poetry.org/) for dependency management:
   ```bash
   poetry install
   ```

4. **Pre-commit Hooks**: Install pre-commit hooks to ensure code quality:
   ```bash
   pre-commit install
   ```

## Code Style Guidelines

RiskGPT follows these code style conventions:

1. **Formatting**: Code is formatted using both Ruff and Black with a line length of 88 characters.

2. **Linting**: Ruff is used for linting with import sorting enabled.

3. **Type Checking**: All code should be type-annotated and checked with mypy.

4. **Pre-commit Hooks**: The following checks run automatically on commit:
   - Ruff for linting
   - Ruff for formatting
   - Mypy for type checking

## Testing Guidelines

1. **Test Categories**:
   - **Unit Tests**: Test individual components in isolation
   - **Functional Tests**: Test interactions between components
   - **Integration Tests**: Test interactions with external services

2. **Running Tests**:
   - Run all unit and functional tests:
     ```bash
     poetry run pytest
     ```
   - Run with coverage:
     ```bash
     poetry run pytest --cov=src
     ```
   - Run integration tests (requires API keys):
     ```bash
     poetry run pytest -m integration
     ```

3. **Test Requirements**:
   - All new features should include appropriate tests
   - Integration tests should be marked with the `@pytest.mark.integration` decorator
   - Mock external dependencies in unit and functional tests

## Pull Request Process

1. Create a feature branch from `main`
2. Implement your changes with appropriate tests
3. Ensure all tests pass and code quality checks succeed
4. Submit a pull request with a clear description of the changes

## Dependency Management

1. Use `Poetry` for installing and managing dependencies
2. Add new dependencies to `pyproject.toml` in the appropriate section:
   - Runtime dependencies under `[project.dependencies]`
   - Development dependencies under `[tool.poetry.dev-dependencies]` or `[tool.uv.dev-dependencies]`
3. Update dependencies with:
   ```bash
   poetry update
   ```

## Documentation

1. Document all public functions, classes, and methods with docstrings
2. Update the README.md when adding new features or changing existing functionality
3. Documentation is built with MkDocs and deployed to GitHub Pages

## Troubleshooting

1. **Circuit Breaker Issues**: If external API calls are failing, check the circuit breaker status in logs
2. **Environment Variables**: Ensure all required environment variables are set correctly
3. **API Keys**: Verify that API keys for OpenAI and search providers are valid

## Continuous Integration

The project uses GitHub Actions for continuous integration:
1. Run tests on pull requests and pushes to main
2. Check code quality with Ruff, Black, and mypy
3. Build and publish package to PyPI on pushes to main that modify the src/ directory
4. Deploy documentation to GitHub Pages using MkDocs

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with the changes
3. Push changes to the main branch
4. The CI pipeline will automatically:
   - Build the package with Poetry
   - Publish to PyPI
   - Commit the version update back to the repository
