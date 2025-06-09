# Publishing to PyPI

This project is configured to automatically publish new versions to PyPI when changes are made to the main package code in the `main` branch.

## Workflow Overview

The GitHub Actions workflow in `.github/workflows/publish-pypi.yml` handles the following steps:

1. Triggers when changes are pushed to the `main` branch that affect files in the `riskgpt/` directory
2. Automatically increments the patch version number in `pyproject.toml`
3. Builds the package using Poetry
4. Publishes the package to PyPI
5. Commits the updated version number back to the repository

## Required Setup

To enable automatic publishing to PyPI, you need to set up the following GitHub secret:

### PYPI_API_TOKEN

1. Create an API token on PyPI:
   - Log in to your PyPI account at https://pypi.org/
   - Go to Account Settings → API tokens
   - Create a new API token with the scope limited to the `riskgpt` project
   - Copy the token value (you won't be able to see it again)

2. Add the token as a GitHub repository secret:
   - Go to your GitHub repository
   - Navigate to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste the PyPI API token you copied
   - Click "Add secret"

## Manual Version Control

If you need to manually control the version number (for major or minor version bumps), you can:

1. Update the version in `pyproject.toml` directly
2. Push the change to the `main` branch
3. The workflow will still publish to PyPI but won't increment the version further

## Troubleshooting

If the workflow fails to publish, check:

1. The PyPI API token is correctly set up as a repository secret
2. The package version in `pyproject.toml` is higher than the latest version on PyPI
3. The GitHub Actions logs for specific error messages