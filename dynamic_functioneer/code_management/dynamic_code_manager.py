import os
import logging
from typing import Optional, Callable, Any
from dynamic_functioneer.code_management.code_storage import CodeFileManager, DynamicTestFileManager
from dynamic_functioneer.code_management.code_loader import DynamicModuleLoader
from dynamic_functioneer.code_management.test_runner import TestExecutionStrategy, SubprocessTestRunner

logger = logging.getLogger(__name__)


class DynamicCodeManager:
    """
    Manages dynamic generation, saving, and loading of function/method code and test files.

    This class now delegates responsibilities to focused components following SRP:
    - CodeFileManager: Handles file I/O for code
    - DynamicModuleLoader: Handles Python module loading
    - TestFileManager: Handles test file operations
    - TestExecutionStrategy: Handles test execution
    """

    def __init__(
        self,
        dynamic_file_path: str,
        test_runner: Optional[TestExecutionStrategy] = None
    ) -> None:
        """
        Initialize the DynamicCodeManager.

        Args:
            dynamic_file_path: Path to the file where dynamic code is stored.
            test_runner: Optional test execution strategy. Defaults to SubprocessTestRunner.
        """
        self.dynamic_file_path = dynamic_file_path
        self.test_file_dir = "."  # Default directory for test files

        # Delegate to focused components
        self._code_file_manager = CodeFileManager(dynamic_file_path)
        self._module_loader = DynamicModuleLoader(dynamic_file_path)
        self._test_file_manager = DynamicTestFileManager(self.test_file_dir)
        self._test_runner = test_runner or SubprocessTestRunner()

        os.makedirs(self.test_file_dir, exist_ok=True)

    def save_code(self, code: str) -> None:
        """
        Save the provided code to the dynamic file.

        Args:
            code: The code to save.
        """
        self._code_file_manager.save_code(code)

    def load_code(self) -> str:
        """
        Load and return the code from the dynamic file.

        Returns:
            The code stored in the dynamic file.

        Raises:
            FileNotFoundError: If the dynamic file does not exist.
        """
        return self._code_file_manager.load_code()

    def load_function(self, function_name: str) -> Callable[..., Any]:
        """
        Dynamically load and return a function by name from the dynamic file.

        Args:
            function_name: The name of the function to load.

        Returns:
            The loaded function.

        Raises:
            ImportError: If the module or function cannot be loaded.
        """
        return self._module_loader.load_function(function_name)

    def save_test_file(self, test_file_path: str, test_code: str) -> None:
        """
        Save test code to a specified file.

        Args:
            test_file_path: Full path to the test file.
            test_code: The test code to save.
        """
        self._test_file_manager.save_test_file(test_file_path, test_code)

    def run_test(self, test_file_path: str) -> bool:
        """
        Run a test file and check if it passes.

        Args:
            test_file_path: Path to the test file to run.

        Returns:
            True if the test passes, False otherwise.
        """
        return self._test_runner.run_test(test_file_path)

    def code_exists(self) -> bool:
        """
        Check if the dynamic file exists.

        Returns:
            True if the dynamic file exists, False otherwise.
        """
        return self._code_file_manager.code_exists()

    # Properties for accessing internal components if needed
    @property
    def code_file_manager(self) -> CodeFileManager:
        """Get the code file manager instance."""
        return self._code_file_manager

    @property
    def module_loader(self) -> DynamicModuleLoader:
        """Get the module loader instance."""
        return self._module_loader

    @property
    def test_file_manager(self) -> DynamicTestFileManager:
        """Get the test file manager instance."""
        return self._test_file_manager

    @property
    def test_runner(self) -> TestExecutionStrategy:
        """Get the test runner instance."""
        return self._test_runner


