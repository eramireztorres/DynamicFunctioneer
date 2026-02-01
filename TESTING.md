# Testing Guide for DynamicFunctioneer

This guide provides comprehensive information about testing in the DynamicFunctioneer project.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Quick Start](#quick-start)
3. [Test Organization](#test-organization)
4. [Running Tests Locally](#running-tests-locally)
5. [CI/CD Workflow](#cicd-workflow)
6. [Coverage Requirements](#coverage-requirements)
7. [Writing Tests](#writing-tests)
8. [Pre-commit Hooks](#pre-commit-hooks)
9. [Troubleshooting](#troubleshooting)

## Testing Philosophy

DynamicFunctioneer follows these testing principles:

- **Comprehensive Coverage**: Maintain minimum 70% code coverage
- **Fast Feedback**: Unit tests run in milliseconds for quick feedback
- **Test Pyramid**: More unit tests, fewer integration tests, minimal E2E tests
- **Isolated Tests**: Each test is independent and can run in any order
- **Continuous Integration**: All tests run automatically on every push
- **Test-Driven Development**: Write tests before or alongside new features

## Quick Start

Install development dependencies:
```bash
pip install -e .[dev]
# or
pip install pytest pytest-cov pytest-timeout pytest-mock pytest-asyncio
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=dynamic_functioneer --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Organization

```
tests/
├── unit/                      # Unit tests (fast, isolated)
│   ├── test_config.py        # Configuration system
│   ├── test_code_storage.py  # File operations
│   └── test_test_runner.py   # Test execution
├── integration/               # Integration tests (slower, multiple components)
│   └── test_end_to_end.py    # Complete workflows
└── fixtures/                  # Shared test data and fixtures
```

### Test Types

**Unit Tests** (`tests/unit/`):
- Test individual components in isolation
- Fast execution (milliseconds)
- No external dependencies
- Use mocking for dependencies
- Mark with `@pytest.mark.unit`

**Integration Tests** (`tests/integration/`):
- Test component interactions
- Slower execution (seconds)
- May use temporary files/directories
- Test complete workflows
- Mark with `@pytest.mark.integration`

## Running Tests Locally

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test directory
pytest tests/unit
pytest tests/integration

# Run specific test file
pytest tests/unit/test_config.py

# Run specific test class
pytest tests/unit/test_config.py::TestModelConfig

# Run specific test function
pytest tests/unit/test_config.py::TestModelConfig::test_default_values
```

### Using Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests except slow ones
pytest -m "not slow"

# Run tests requiring API keys (usually skipped)
pytest -m requires_api_key

# Combine markers
pytest -m "unit and not slow"
```

### Coverage Options

```bash
# Generate all coverage reports
pytest --cov=dynamic_functioneer --cov-report=html --cov-report=xml --cov-report=term

# Show missing lines in terminal
pytest --cov=dynamic_functioneer --cov-report=term-missing

# Fail if coverage below 70%
pytest --cov=dynamic_functioneer --cov-fail-under=70

# Coverage for specific module
pytest --cov=dynamic_functioneer.models --cov-report=term-missing
```

### Advanced Options

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Stop at first failure
pytest -x

# Run last failed tests only
pytest --lf

# Run tests with specific keyword
pytest -k "test_config"

# Show test durations
pytest --durations=10

# Disable warnings
pytest --disable-warnings

# Show local variables on failure
pytest -l

# Increase verbosity for debugging
pytest -vv
```

## CI/CD Workflow

### Automated Testing

Tests run automatically on:
- **Push** to `master`, `main`, or `develop` branches
- **Pull Requests** to these branches
- **Manual trigger** via GitHub Actions

### Test Workflow (`.github/workflows/tests.yml`)

The CI pipeline includes three jobs:

#### 1. Test Job
- **Matrix Testing**: Python 3.9, 3.10, 3.11, 3.12 on Ubuntu
- **Steps**:
  1. Checkout code
  2. Set up Python with pip caching
  3. Install dependencies
  4. Run unit tests with coverage
  5. Run integration tests
  6. Upload coverage to Codecov

#### 2. Lint Job
- **Steps**:
  1. Check code formatting with `black`
  2. Check import sorting with `isort`
  3. Lint with `flake8` (syntax errors fail, style warnings don't)
  4. Type check with `mypy`

#### 3. Package Test Job
- **Steps**:
  1. Build package
  2. Install from wheel
  3. Test imports

### Coverage Workflow (`.github/workflows/coverage.yml`)

Runs on push/PR to `master`/`main`:
1. Generate HTML, XML, and Markdown coverage reports
2. Upload coverage artifacts
3. Comment coverage on pull requests

### Viewing CI Results

1. **GitHub Actions**: Go to the "Actions" tab in the repository
2. **Coverage Reports**: Check PR comments or download artifacts
3. **Codecov**: View detailed coverage at codecov.io (if configured)

### CI Best Practices

- **Don't skip CI**: Fix failing tests before merging
- **Review coverage**: Ensure new code has adequate test coverage
- **Check all Python versions**: Ensure compatibility across 3.9-3.12
- **Monitor test duration**: Keep test suite fast (< 5 minutes)

## Coverage Requirements

### Minimum Thresholds

- **Overall Coverage**: 70% minimum (enforced by pytest.ini)
- **New Code**: Should have > 80% coverage
- **Critical Paths**: Should have 100% coverage

### Checking Coverage

```bash
# Terminal report with missing lines
pytest --cov=dynamic_functioneer --cov-report=term-missing

# HTML report (interactive)
pytest --cov=dynamic_functioneer --cov-report=html
open htmlcov/index.html
```

### Coverage Reports

**HTML Report** (`htmlcov/index.html`):
- Interactive file browser
- Line-by-line coverage highlighting
- Branch coverage visualization
- Sortable by coverage percentage

**XML Report** (`coverage.xml`):
- Used by Codecov and other tools
- Machine-readable format

**Terminal Report**:
- Quick overview in console
- Shows missing lines
- Module-by-module breakdown

### Improving Coverage

1. **Identify gaps**: Run `pytest --cov-report=term-missing`
2. **Prioritize**: Focus on critical/complex code first
3. **Add unit tests**: Easier to write and maintain
4. **Test edge cases**: Don't just test happy paths
5. **Review regularly**: Make coverage part of code review

## Writing Tests

### Test Structure

```python
"""
Module-level docstring describing what's being tested.
"""
import pytest
from dynamic_functioneer.module import MyClass


class TestMyClass:
    """Test MyClass functionality."""

    def test_basic_behavior(self):
        """Test that MyClass behaves correctly in normal case."""
        # Arrange
        instance = MyClass()

        # Act
        result = instance.do_something()

        # Assert
        assert result == expected_value

    def test_error_handling(self):
        """Test that MyClass handles errors properly."""
        instance = MyClass()

        with pytest.raises(ValueError, match="expected error message"):
            instance.do_invalid_thing()

    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that requires significant time."""
        # Test implementation
        pass
```

### Using Fixtures

```python
import pytest
from pathlib import Path


@pytest.fixture
def temp_directory(tmp_path):
    """Create a temporary directory for testing."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    yield test_dir
    # Cleanup happens automatically


@pytest.fixture
def sample_config():
    """Provide a sample configuration."""
    return {
        "model": "gpt-4",
        "temperature": 0.7
    }


def test_with_fixtures(temp_directory, sample_config):
    """Test using multiple fixtures."""
    assert temp_directory.exists()
    assert sample_config["model"] == "gpt-4"
```

### Testing with Environment Variables

```python
def test_environment_variable(monkeypatch):
    """Test behavior with environment variables."""
    # Set environment variable
    monkeypatch.setenv('DF_DEFAULT_MODEL', 'gpt-4')

    # Test code that reads environment variable
    from dynamic_functioneer import get_config
    config = get_config()

    assert config.model.default_model == 'gpt-4'
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch


def test_with_mock():
    """Test using a mock object."""
    mock_api = Mock()
    mock_api.get_response.return_value = "mocked response"

    # Use the mock
    result = some_function(mock_api)

    # Verify mock was called correctly
    mock_api.get_response.assert_called_once_with("expected input")
    assert result == "mocked response"


@patch('dynamic_functioneer.models.openai_model_api.OpenAI')
def test_with_patch(mock_openai):
    """Test with patched import."""
    # Configure mock
    mock_openai.return_value.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="test response"))]
    )

    # Test code that uses OpenAI
    from dynamic_functioneer.models import OpenAIModelAPI
    api = OpenAIModelAPI("fake-key", "gpt-4")
    response = api.get_response("test prompt")

    assert response == "test response"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (-1, -2),
    (0, 0),
])
def test_double(input, expected):
    """Test that double function works for various inputs."""
    assert double(input) == expected
```

### Testing Async Code

```python
import pytest


@pytest.mark.asyncio
async def test_async_function():
    """Test asynchronous function."""
    result = await some_async_function()
    assert result is not None
```

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit to ensure code quality.

### Setup

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### What Hooks Run

The hooks will:
1. Run linting (black, isort, flake8)
2. Run type checking (mypy)
3. Run fast unit tests
4. Check for common issues (trailing whitespace, merge conflicts, etc.)

### Manual Execution

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for a commit (use sparingly)
git commit --no-verify -m "message"
```

## Troubleshooting

### Common Issues

#### Tests Pass Locally But Fail in CI

**Possible causes**:
- Different Python version
- Missing dependencies
- Environment-specific behavior
- Cached files

**Solutions**:
```bash
# Test with multiple Python versions locally
pyenv install 3.9 3.10 3.11 3.12
pyenv local 3.9
pytest

# Clear all caches
pytest --cache-clear
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reinstall in editable mode
pip install -e .
```

#### Import Errors

**Solutions**:
```bash
# Ensure package is installed
pip install -e .

# Verify PYTHONPATH
echo $PYTHONPATH

# Check sys.path in Python
python -c "import sys; print('\n'.join(sys.path))"
```

#### Coverage Too Low

**Solutions**:
1. Run with missing lines: `pytest --cov-report=term-missing`
2. Identify untested modules
3. Add unit tests for critical paths
4. Test edge cases and error handling
5. Don't test trivial code (getters/setters)

#### Slow Tests

**Solutions**:
```bash
# Identify slow tests
pytest --durations=10

# Mark slow tests
@pytest.mark.slow
def test_slow_operation():
    pass

# Skip slow tests during development
pytest -m "not slow"

# Run tests in parallel
pip install pytest-xdist
pytest -n auto
```

#### Flaky Tests

Tests that sometimes pass and sometimes fail are problematic.

**Common causes**:
- Race conditions
- Timing dependencies
- Shared state between tests
- External dependencies

**Solutions**:
- Use fixtures for clean state
- Add timeouts: `@pytest.mark.timeout(5)`
- Mock external dependencies
- Ensure test independence

#### API Key Tests

**Skip tests requiring API keys**:
```python
import os
import pytest

@pytest.mark.requires_api_key
def test_api_call():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip("API key not available")
    # Test implementation
```

**In CI**: Set secrets in GitHub repository settings

### Getting Help

1. Check test output for error messages
2. Run with `-vv` for detailed output
3. Review test documentation in `tests/README.md`
4. Check GitHub Actions logs for CI failures
5. Review pytest documentation: https://docs.pytest.org/

## Best Practices Summary

1. **Write tests early**: Don't wait until the end
2. **Keep tests simple**: One test should test one thing
3. **Use descriptive names**: Test names should explain what's being tested
4. **Test edge cases**: Don't just test happy paths
5. **Keep tests fast**: Use mocks for external dependencies
6. **Test publicly, not privately**: Test the public API, not implementation details
7. **Use fixtures**: Share setup code between tests
8. **Mark tests appropriately**: Use markers for organization
9. **Review coverage**: Make it part of code review
10. **Keep CI green**: Fix failing tests immediately

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test-Driven Development](https://testdriven.io/test-driven-development/)
- Tests README: `tests/README.md`
- Project Structure: `PROJECT_STRUCTURE.md`
