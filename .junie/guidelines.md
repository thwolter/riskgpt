# Project Guidelines


## Basic Considerations
- The package uses asynchronous programming

## Code Style & Conventions
- Follows Ruff standards with 88 character line length
- type-annotate the code and check with mypy
- sort imports using isort (via Ruff)

## Testing
- run mypy and ruff after making changes
- All new features must include tests in the `/tests` directory.
- Use `pytest` as the testing framework.
 
## Commit Messages
- Use the format: `<type>: <short description>`
- Example: `fix: correct login bug`
- Types can include:
  - `feat`: New feature
  - `fix`: Bug fix
  - `docs`: Documentation changes
  - `style`: Code style changes (formatting, etc.)
  - `refactor`: Code refactoring without changing functionality
  - `test`: Adding or updating tests

## Additional Notes
- For API documentation, use docstrings compatible with Sphinx.
- When in doubt, refer to the [project README](./README.md).
- After a doc string, leave a blank line before the next code line to maintain readability.