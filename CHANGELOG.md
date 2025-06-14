# Changelog

All notable changes to this project will be documented in this file.

## [unreleased]

### 🚀 Features

- Extend category and risk chains
- Enhance chain registry with introspection capabilities and utility methods
- Add circuit breaker pattern for external API calls with fallbacks
- Unify and extend external search functionality with multiple providers
- Refactor schemas to adopt `BusinessContext` and simplify models
- Remove simple mode from risk workflow
- Add MAX_TOKENS setting and enhance error handling in circuit breaker

### 🐛 Bug Fixes

- Improve dummy responses for tests

### 💼 Other

- Introduce Risk Workflow and document microservice integration**
- Introduce Risk Workflow and document microservice integration**
- Add MkDocs deployment workflow and update PyPI workflow permissions**
- Improve `model_fields` validation logic and update MkDocs deploy workflow**
- Enhance GitHub Actions workflows for PyPI and MkDocs deploy**

### 🚜 Refactor

- Integrate `BusinessContext` usage in playground and external context enrichment
- Integrate `BusinessContext` across schemas, workflows, and tests
- Enhance schema and workflow consistency with language enum and improved domain knowledge handling
- Replace deprecated `Config` with `model_config` in schemas
- Remove legacy risk chain implementation and align workflows with `get_risks_chain`
- Centralize chain preparation logic and streamline sync/async implementations
- Centralize chain preparation logic and streamline sync/async implementations

### 📚 Documentation

- Document environment variables
- Add DOCUMENT_SERVICE_URL variable
- Remove simple mode

### 🧪 Testing

- Add unit tests for `cost_benefit_chain` and `async_cost_benefit_chain`, including mock-based scenarios

### ⚙️ Miscellaneous Tasks

- Release v0.1.3
- Remove playground notebook
- Update `langchain-google-community` to v2.0.7 and dependencies in `poetry.lock`
- Update GitHub Actions workflow for PyPI publishing
- Remove `deploy-docs.yml` GitHub Actions workflow
- Remove version increment step from PyPI publish workflow

<!-- generated by git-cliff -->
