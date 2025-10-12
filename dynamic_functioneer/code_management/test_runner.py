"""
Test execution strategies for dynamic code validation.

This module provides pluggable test runner implementations following the
Strategy pattern, allowing flexibility in how tests are executed.
"""

import os
import subprocess
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class TestExecutionStrategy(ABC):
    """
    Abstract base class for test execution strategies.

    This allows different test frameworks (subprocess, pytest, unittest)
    to be plugged in without changing client code.
    """

    @abstractmethod
    def run_test(self, test_file_path: str) -> bool:
        """
        Run a test file and return success status.

        Args:
            test_file_path: Path to the test file to execute.

        Returns:
            True if all tests passed, False otherwise.
        """
        pass


class SubprocessTestRunner(TestExecutionStrategy):
    """
    Run tests using subprocess with the system Python interpreter.

    This is the default strategy, maintaining backward compatibility.
    """

    def __init__(self, python_executable: str = "python", timeout: Optional[int] = None) -> None:
        """
        Initialize the subprocess test runner.

        Args:
            python_executable: Path to the Python interpreter. Defaults to "python".
            timeout: Optional timeout in seconds for test execution.
        """
        self.python_executable = python_executable
        self.timeout = timeout

    def run_test(self, test_file_path: str) -> bool:
        """
        Run a test file using subprocess.

        Args:
            test_file_path: Path to the test file to execute.

        Returns:
            True if the test passed (returncode 0), False otherwise.

        Raises:
            FileNotFoundError: If the test file doesn't exist.
        """
        if not os.path.exists(test_file_path):
            raise FileNotFoundError(f"Test file '{test_file_path}' not found.")

        try:
            logger.info(f"Running test file: {test_file_path}")
            result = subprocess.run(
                [self.python_executable, test_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                logger.info(f"Test passed: {test_file_path}")
                logger.debug(f"Test output:\n{result.stdout}")
                return True
            else:
                logger.error(f"Test failed: {test_file_path}")
                logger.error(f"stdout:\n{result.stdout}")
                logger.error(f"stderr:\n{result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Test timed out after {self.timeout} seconds: {test_file_path}")
            return False
        except Exception as e:
            logger.error(f"Error running test file '{test_file_path}': {e}")
            return False


class PytestRunner(TestExecutionStrategy):
    """
    Run tests using pytest.

    This strategy provides more powerful test discovery and reporting.
    """

    def __init__(self, pytest_args: Optional[list] = None) -> None:
        """
        Initialize the pytest runner.

        Args:
            pytest_args: Optional list of additional pytest arguments.
        """
        self.pytest_args = pytest_args or []

    def run_test(self, test_file_path: str) -> bool:
        """
        Run a test file using pytest.

        Args:
            test_file_path: Path to the test file to execute.

        Returns:
            True if all tests passed, False otherwise.

        Raises:
            FileNotFoundError: If the test file doesn't exist.
            ImportError: If pytest is not installed.
        """
        if not os.path.exists(test_file_path):
            raise FileNotFoundError(f"Test file '{test_file_path}' not found.")

        try:
            import pytest
        except ImportError:
            raise ImportError(
                "pytest is not installed. Install it with: pip install pytest"
            )

        try:
            logger.info(f"Running test with pytest: {test_file_path}")
            # pytest.main returns 0 if all tests passed
            result = pytest.main([test_file_path, "-v"] + self.pytest_args)

            if result == 0:
                logger.info(f"All pytest tests passed: {test_file_path}")
                return True
            else:
                logger.error(f"Pytest tests failed: {test_file_path}")
                return False

        except Exception as e:
            logger.error(f"Error running pytest on '{test_file_path}': {e}")
            return False


class UnittestRunner(TestExecutionStrategy):
    """
    Run tests using unittest test discovery.

    This strategy uses Python's built-in unittest framework.
    """

    def __init__(self, verbosity: int = 2) -> None:
        """
        Initialize the unittest runner.

        Args:
            verbosity: Verbosity level for unittest output (0-2).
        """
        self.verbosity = verbosity

    def run_test(self, test_file_path: str) -> bool:
        """
        Run a test file using unittest.

        Args:
            test_file_path: Path to the test file to execute.

        Returns:
            True if all tests passed, False otherwise.

        Raises:
            FileNotFoundError: If the test file doesn't exist.
        """
        if not os.path.exists(test_file_path):
            raise FileNotFoundError(f"Test file '{test_file_path}' not found.")

        try:
            import unittest

            logger.info(f"Running test with unittest: {test_file_path}")

            # Load tests from the file
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(
                os.path.splitext(os.path.basename(test_file_path))[0]
            )

            # Run the tests
            runner = unittest.TextTestRunner(verbosity=self.verbosity)
            result = runner.run(suite)

            # Check if all tests passed
            success = result.wasSuccessful()

            if success:
                logger.info(f"All unittest tests passed: {test_file_path}")
            else:
                logger.error(f"Unittest tests failed: {test_file_path}")

            return success

        except Exception as e:
            logger.error(f"Error running unittest on '{test_file_path}': {e}")
            return False
