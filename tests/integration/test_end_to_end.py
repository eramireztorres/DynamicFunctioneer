"""
Integration tests for end-to-end functionality.

These tests verify that different components work together correctly.
"""

import pytest
import tempfile
from pathlib import Path
from dynamic_functioneer.code_management.code_storage import CodeFileManager
from dynamic_functioneer.code_management.code_loader import DynamicModuleLoader
from dynamic_functioneer.code_management.dynamic_code_manager import DynamicCodeManager
from dynamic_functioneer.code_management.test_runner import SubprocessTestRunner


class TestCodeLifecycle:
    """Test the complete code lifecycle."""

    def test_save_load_execute_cycle(self, tmp_path):
        """Test saving, loading, and executing dynamic code."""
        # Create a simple function
        code = """
def add_numbers(a, b):
    '''Add two numbers.'''
    return a + b
"""

        # Save code
        code_file = tmp_path / "test_func.py"
        file_manager = CodeFileManager(str(code_file))
        file_manager.save_code(code)

        # Load code
        loader = DynamicModuleLoader(str(code_file))
        func = loader.load_function("add_numbers")

        # Execute
        result = func(2, 3)
        assert result == 5

    def test_dynamic_code_manager_integration(self, tmp_path):
        """Test DynamicCodeManager integrates all components."""
        code_file = tmp_path / "dynamic_func.py"
        manager = DynamicCodeManager(str(code_file))

        # Save code
        code = """
def multiply(x, y):
    return x * y
"""
        manager.save_code(code)

        # Verify existence
        assert manager.code_exists()

        # Load and execute
        func = manager.load_function("multiply")
        assert func(4, 5) == 20

        # Load code as string
        loaded_code = manager.load_code()
        assert "def multiply" in loaded_code


class TestTestingWorkflow:
    """Test the testing workflow integration."""

    def test_save_and_run_test(self, tmp_path):
        """Test saving and running a test file."""
        manager = DynamicCodeManager(str(tmp_path / "code.py"))

        # Create a test
        test_code = """
def test_simple():
    assert 1 + 1 == 2

if __name__ == '__main__':
    test_simple()
    print('Tests passed')
"""

        test_file = tmp_path / "test_integration.py"
        manager.save_test_file(str(test_file), test_code)

        # Run the test
        result = manager.run_test(str(test_file))
        assert result is True

    def test_custom_test_runner_integration(self, tmp_path):
        """Test using a custom test runner."""
        code_file = tmp_path / "code.py"

        # Create manager with custom test runner
        custom_runner = SubprocessTestRunner(timeout=5)
        manager = DynamicCodeManager(str(code_file), test_runner=custom_runner)

        # Verify test runner is set
        assert isinstance(manager.test_runner, SubprocessTestRunner)


class TestBackwardCompatibility:
    """Test backward compatibility with old import paths."""

    def test_old_imports_work(self):
        """Test that old import paths still work."""
        # Old import style
        from dynamic_functioneer.model_api_factory import ModelAPIFactory
        from dynamic_functioneer.dynamic_code_manager import DynamicCodeManager

        # Should be able to instantiate
        assert ModelAPIFactory is not None
        assert DynamicCodeManager is not None

    def test_old_and_new_imports_same(self):
        """Test that old and new imports reference same modules."""
        from dynamic_functioneer.model_api_factory import ModelAPIFactory as OldFactory
        from dynamic_functioneer.models import ModelAPIFactory as NewFactory

        # Should be the exact same class
        assert OldFactory is NewFactory
