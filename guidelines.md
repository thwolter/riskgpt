
# RiskGPT Junie Guidelines

## What is Junie?
Junie is an AI assistant designed to help you navigate, understand, and develop the RiskGPT codebase. It can assist with code exploration, debugging, feature implementation, and understanding the project's architecture and patterns.

## Quick Start
1. Ask Junie about specific parts of the codebase: "How does the circuit breaker pattern work in RiskGPT?"
2. Get help with implementing new features: "How would I add a new search provider to the enrich_context workflow?"
3. Debug issues: "Why might my chain be failing when processing this input?"
4. Understand project structure: "Explain how the workflows are organized in RiskGPT"

## Code Style & Conventions
- **Python Version**: RiskGPT requires Python 3.12+
- **Formatting**: Code follows Ruff standards with 88 character line length
- **Type Annotations**: All code is type-annotated and checked with mypy
- **Imports**: Sorted using isort (via Ruff)
- **Pre-commit Hooks**: Ruff for linting/formatting and mypy for type checking

## RiskGPT-Specific Workflows
Junie can help with these common development scenarios:

### Exploring LangChain/LangGraph Implementations
- "Show me how RiskGPT implements LangGraph workflows"
- "Explain the BaseChain class and how it's used"
- "How does RiskGPT handle circuit breaking for external API calls?"

### Adding New Features
- "How do I add a new chain for risk analysis?"
- "What's the pattern for adding a new search provider?"
- "How should I structure a new workflow node?"

### Debugging Issues
- "Why might my circuit breaker be triggering too frequently?"
- "How can I debug this LangGraph workflow?"
- "What could cause this parsing error in my chain?"

### Testing
- "How should I write tests for a new chain?"
- "What's the pattern for mocking external services in tests?"
- "How do I run integration tests for my new feature?"

## Project Structure Overview
```
riskgpt/
├── src/riskgpt/           # Main package
│   ├── chains/            # LLM chain implementations
│   ├── config/            # Configuration settings
│   ├── helpers/           # Helper functions and utilities
│   ├── models/            # Data models and schemas
│   ├── processors/        # Input/output processors
│   ├── prompts/           # LLM prompts organized by function
│   ├── workflows/         # Risk assessment workflows using LangGraph
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── functional/        # Functional tests
│   ├── integration/       # Integration tests (require external services)
```

## Key Technologies
- **LangChain**: Framework for LLM applications
- **LangGraph**: For building complex, multi-step workflows
- **Pydantic**: For data validation and settings management
- **Circuit Breaker Pattern**: For resilient external API calls
- **Redis/Buffer Memory**: For conversation memory

## Effective Prompting Strategies

### DO:
- Specify the file or component you're asking about
- Include relevant error messages when debugging
- Mention which part of the codebase you're working with
- Ask about specific patterns or implementations

### DON'T:
- Ask overly broad questions ("How does RiskGPT work?")
- Paste large code blocks without context
- Ask Junie to write complete features without guidance

### Examples of Good Prompts:
- "How does the `BaseChain` class handle circuit breaking for OpenAI API calls?"
- "I'm getting a type error in my workflow node. Here's the error: [error]. How can I fix it?"
- "Show me the pattern for creating a new search provider in the `helpers/search` module"

## Tips and Best Practices
- **Provide Context**: Tell Junie which file or component you're working with
- **Be Specific**: Ask about particular patterns or implementations
- **Verify Responses**: Always test code suggestions in your development environment
- **Iterative Approach**: Start with high-level questions, then drill down into specifics

## When Not to Use Junie
- For running or executing code (use your local environment)
- For accessing external documentation (use the official docs)
- For sensitive information like API keys or credentials

## Troubleshooting
- If Junie doesn't understand your question, try rephrasing with more specific details
- If code suggestions don't work, ask Junie to explain the reasoning behind them
- For complex workflows, ask Junie to break down the explanation step by step

## Additional Resources
- [RiskGPT Documentation](https://thwolter.github.io/riskgpt/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Project README](./README.md) for installation and basic usage