# DynamicFunctioneer Test Suite

This directory contains the comprehensive test suite for the DynamicFunctioneer project.

## Test Structure

```
tests/
├── unit/                   # Unit tests for individual components
│   ├── test_config.py     # Configuration system tests
│   ├── test_code_storage.py  # File I/O and storage tests
│   └── test_test_runner.py   # Test execution strategy tests
├── integration/            # Integration tests for component interactions
│   └── test_end_to_end.py # End-to-end workflow tests
└── fixtures/              # Shared test fixtures and data
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Run only unit tests
pytest tests/unit -v

# Run only integration tests
pytest tests/integration -v

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Slow tests only
pytest -m "not slow"    # Skip slow tests
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=dynamic_functioneer --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Test Files or Functions
```bash
# Run specific test file
pytest tests/unit/test_config.py -v

# Run specific test class
pytest tests/unit/test_config.py::TestModelConfig -v

# Run specific test function
pytest tests/unit/test_config.py::TestModelConfig::test_default_values -v
```

## Test Markers

Tests are organized using pytest markers defined in `pytest.ini`:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for component interactions
- `@pytest.mark.slow` - Tests that take significant time to run
- `@pytest.mark.requires_api_key` - Tests requiring API keys (typically skipped in CI)
- `@pytest.mark.network` - Tests requiring network access

Example usage:
```python
@pytest.mark.unit
def test_example():
    assert True

@pytest.mark.slow
@pytest.mark.network
def test_api_integration():
    # Test that calls external API
    pass
```

## Writing New Tests

### Unit Tests

Unit tests should test individual components in isolation. Place them in `tests/unit/`:

```python
"""
Unit tests for MyComponent.
"""
import pytest
from dynamic_functioneer.module import MyComponent


class TestMyComponent:
    """Test MyComponent functionality."""

    def test_basic_functionality(self):
        """Test that MyComponent works as expected."""
        component = MyComponent()
        result = component.do_something()
        assert result == expected_value

    def test_error_handling(self):
        """Test that MyComponent handles errors correctly."""
        component = MyComponent()
        with pytest.raises(ValueError):
            component.do_invalid_thing()
```

### Integration Tests

Integration tests verify that multiple components work together. Place them in `tests/integration/`:

```python
"""
Integration tests for workflow X.
"""
import pytest
from dynamic_functioneer.module_a import ComponentA
from dynamic_functioneer.module_b import ComponentB


class TestWorkflowX:
    """Test complete workflow X."""

    def test_complete_workflow(self, tmp_path):
        """Test that components A and B work together."""
        component_a = ComponentA()
        component_b = ComponentB()

        # Test interaction
        result_a = component_a.process()
        result_b = component_b.consume(result_a)

        assert result_b.is_valid()
```

### Using Fixtures

Use pytest fixtures for shared setup/teardown:

```python
@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary configuration for testing."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"key": "value"}')
    yield config_file
    # Cleanup happens automatically

def test_with_fixture(temp_config):
    """Test using the fixture."""
    assert temp_config.exists()
```

### Testing with Mock API Keys

For tests requiring API keys, use environment variables and skip if not available:

```python
import os
import pytest

@pytest.mark.requires_api_key
def test_api_call():
    """Test that requires an API key."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip("API key not available")

    # Test with real API
    result = make_api_call(api_key)
    assert result is not None
```

## Coverage Requirements

- Minimum coverage threshold: **70%**
- Coverage reports are generated automatically when running `pytest`
- CI/CD pipeline enforces coverage requirements
- View detailed coverage in `htmlcov/index.html` after running tests

## Continuous Integration

Tests run automatically on:
- Every push to `master`, `main`, or `develop` branches
- Every pull request to these branches
- Manual workflow dispatch

The CI pipeline:
1. Tests on Python 3.9, 3.10, 3.11, and 3.12
2. Runs unit tests with coverage
3. Runs integration tests
4. Performs linting and type checking
5. Tests package installation
6. Uploads coverage reports to Codecov

See `.github/workflows/tests.yml` for full CI configuration.

## Test Configuration

Test behavior is configured in `pytest.ini`:

- Test discovery patterns
- Coverage reporting options
- Test markers
- Timeout settings (5 minutes default)
- Warning filters
- Logging configuration

## Troubleshooting

### Tests Fail Locally But Pass in CI
- Check Python version (CI tests on 3.9-3.12)
- Ensure all dependencies are installed: `pip install -e .[dev]`
- Clear pytest cache: `pytest --cache-clear`

### Coverage Too Low
- Identify untested code: `pytest --cov --cov-report=term-missing`
- Focus on testing critical paths first
- Add unit tests for new features

### Import Errors
- Ensure package is installed in editable mode: `pip install -e .`
- Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
- Verify PYTHONPATH includes project root

### Slow Test Suite
- Run only fast tests: `pytest -m "not slow"`
- Use parallel execution: `pytest -n auto` (requires pytest-xdist)
- Profile slow tests: `pytest --durations=10`

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
   - Good: `test_config_loads_from_environment_variables`
   - Bad: `test_config1`

2. **Test Independence**: Each test should be independent and not rely on other tests

3. **Use Fixtures**: Share setup code using fixtures instead of duplicating in each test

4. **Test Edge Cases**: Don't just test the happy path, test error conditions too

5. **Keep Tests Fast**: Unit tests should run in milliseconds, not seconds

6. **Mock External Dependencies**: Use mocking for external APIs, databases, file systems in unit tests

7. **Documentation**: Add docstrings to test classes and complex test functions

8. **Arrange-Act-Assert**: Structure tests clearly:
   ```python
   def test_something():
       # Arrange: Set up test data
       component = MyComponent()

       # Act: Perform the action
       result = component.do_something()

       # Assert: Verify the result
       assert result == expected_value
   ```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- Project-specific testing guide: `../TESTING.md`
