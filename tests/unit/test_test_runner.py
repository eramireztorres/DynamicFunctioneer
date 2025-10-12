"""
Unit tests for test execution strategies.
"""

import os
import tempfile
import pytest
from pathlib import Path
from dynamic_functioneer.code_management.test_runner import (
    TestExecutionStrategy,
    SubprocessTestRunner,
    PytestRunner,
    UnittestRunner,
)


class TestSubprocessTestRunner:
    """Test SubprocessTestRunner."""

    def test_run_passing_test(self, tmp_path):
        """Test running a passing test."""
        test_file = tmp_path / "test_pass.py"
        test_file.write_text("""
import sys
sys.exit(0)  # Success
""")

        runner = SubprocessTestRunner()
        result = runner.run_test(str(test_file))
        assert result is True

    def test_run_failing_test(self, tmp_path):
        """Test running a failing test."""
        test_file = tmp_path / "test_fail.py"
        test_file.write_text("""
import sys
sys.exit(1)  # Failure
""")

        runner = SubprocessTestRunner()
        result = runner.run_test(str(test_file))
        assert result is False

    def test_run_nonexistent_file(self):
        """Test running a nonexistent test file."""
        runner = SubprocessTestRunner()

        with pytest.raises(FileNotFoundError):
            runner.run_test("/nonexistent/test.py")

    def test_custom_python_executable(self, tmp_path):
        """Test using a custom Python executable."""
        test_file = tmp_path / "test_custom.py"
        test_file.write_text("import sys; sys.exit(0)")

        runner = SubprocessTestRunner(python_executable="python")
        result = runner.run_test(str(test_file))
        assert result is True

    def test_timeout(self, tmp_path):
        """Test timeout functionality."""
        test_file = tmp_path / "test_timeout.py"
        test_file.write_text("""
import time
time.sleep(10)  # Sleep longer than timeout
""")

        runner = SubprocessTestRunner(timeout=1)
        result = runner.run_test(str(test_file))
        assert result is False  # Should timeout


class TestPytestRunner:
    """Test PytestRunner."""

    def test_run_passing_pytest(self, tmp_path):
        """Test running a passing pytest test."""
        test_file = tmp_path / "test_pass.py"
        test_file.write_text("""
def test_example():
    assert True
""")

        try:
            import pytest as pytest_module
        except ImportError:
            pytest.skip("pytest not installed")

        runner = PytestRunner()
        result = runner.run_test(str(test_file))
        assert result is True

    def test_run_failing_pytest(self, tmp_path):
        """Test running a failing pytest test."""
        test_file = tmp_path / "test_fail.py"
        test_file.write_text("""
def test_example():
    assert False
""")

        try:
            import pytest as pytest_module
        except ImportError:
            pytest.skip("pytest not installed")

        runner = PytestRunner()
        result = runner.run_test(str(test_file))
        assert result is False

    def test_pytest_not_installed(self, tmp_path, monkeypatch):
        """Test error when pytest is not installed."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        # Mock pytest import to fail
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'pytest':
                raise ImportError("No module named 'pytest'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, '__import__', mock_import)

        runner = PytestRunner()
        with pytest.raises(ImportError, match="pytest is not installed"):
            runner.run_test(str(test_file))

    def test_custom_pytest_args(self, tmp_path):
        """Test using custom pytest arguments."""
        test_file = tmp_path / "test_custom.py"
        test_file.write_text("""
def test_example():
    assert True
""")

        try:
            import pytest as pytest_module
        except ImportError:
            pytest.skip("pytest not installed")

        runner = PytestRunner(pytest_args=["--tb=short"])
        result = runner.run_test(str(test_file))
        assert result is True


class TestAbstractTestExecutionStrategy:
    """Test that TestExecutionStrategy is abstract."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that TestExecutionStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TestExecutionStrategy()

    def test_must_implement_run_test(self):
        """Test that subclasses must implement run_test."""
        class IncompleteRunner(TestExecutionStrategy):
            pass

        with pytest.raises(TypeError):
            IncompleteRunner()

    def test_can_subclass_with_implementation(self, tmp_path):
        """Test that subclassing with run_test works."""
        class CustomRunner(TestExecutionStrategy):
            def run_test(self, test_file_path: str) -> bool:
                return True

        runner = CustomRunner()
        assert runner.run_test("any_path") is True
