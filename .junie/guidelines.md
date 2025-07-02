# Project Guidelines


## Basic Considerations
- The package uses asynchronous programming

## Code Style & Conventions
- Follows Ruff standards with 88 character line length
- Check that ruff formatting is correct by running `ruff check .` and ruff formatting with `ruff format .`
- type-annotate the code and check with mypy
- sort imports using isort (via Ruff)

## Testing
- run mypy and ruff after making changes
- All new features must include tests in the `/tests` directory.
- All changes must be tested by running the tests.
- Use `pytest` as the testing framework.
- Run only test not marketed as `integration` unless necessary.
- When running multiple tests marked with integration, use the '-n auto' option to run them in parallel.
 
## Testing Command Policy
- All automated test runs must use the `pytest` command directly (e.g., `pytest tests/`), not `python -m pytest` or any equivalent. 
- Command invoking pytest via the Python module interface (`python -m pytest ...`) is prohibited and will not be permitted for execution.
- Example of allowed command: `pytest tests/chains/test_summarize_keypoints.py tests/workflows/test_extraction_nodes.py -v`
- Example of prohibited command: `python -m pytest tests/chains/test_summarize_keypoints.py tests/workflows/test_extraction_nodes.py -v`

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
- Avoid implementing backwards compatibility to ensure the package remains modern and efficient.
- For API documentation, use docstrings compatible with Sphinx.
- When in doubt, refer to the [project README](./README.md).
- After a doc string, leave a blank line before the next code line to maintain readability.