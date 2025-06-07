# RiskGPT

RiskGPT is a Python package for analyzing project-related risks and opportunities using LLM-based chains.

## Features

- Extract risk categories from project descriptions
- Identify specific risks per category
- Estimate impact using probabilistic methods
- Support for domain-specific context and memory

## Chains

- [Get Categories](get_categories.md) – determine relevant risk categories for a project description

## Logging

Use `riskgpt.configure_logging()` to enable basic logging. Token usage is logged
at the INFO level whenever a chain is executed.

