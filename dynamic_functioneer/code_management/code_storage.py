"""
Code storage management for dynamic functions.

This module handles file I/O operations for dynamically generated code.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CodeFileManager:
    """
    Manages file I/O operations for dynamic code.

    Responsibilities:
    - Save code to files
    - Load code from files
    - Check file existence
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the CodeFileManager.

        Args:
            file_path: Path to the file where dynamic code is stored.
        """
        self.file_path = file_path

    def save_code(self, code: str) -> None:
        """
        Save code to the dynamic file.

        Args:
            code: The code to save.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path) or '.', exist_ok=True)

            with open(self.file_path, 'w') as file:
                file.write(code)
            logger.info(f"Dynamic code saved successfully to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save dynamic code to {self.file_path}: {e}")
            raise

    def load_code(self) -> str:
        """
        Load and return the code from the dynamic file.

        Returns:
            The code stored in the dynamic file.

        Raises:
            FileNotFoundError: If the dynamic file does not exist.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Dynamic file '{self.file_path}' not found.")

        with open(self.file_path, 'r') as file:
            return file.read()

    def code_exists(self) -> bool:
        """
        Check if the dynamic file exists.

        Returns:
            True if the dynamic file exists, False otherwise.
        """
        return os.path.exists(self.file_path)

    def delete_code(self) -> None:
        """
        Delete the dynamic code file if it exists.
        """
        if self.code_exists():
            try:
                os.remove(self.file_path)
                logger.info(f"Deleted dynamic code file: {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to delete code file {self.file_path}: {e}")
                raise


class DynamicTestFileManager:
    """
    Manages test file operations.

    Responsibilities:
    - Save test code to files
    - Manage test file paths

    Note: Renamed from TestFileManager to avoid pytest collection warnings.
    """

    def __init__(self, test_dir: str = ".") -> None:
        """
        Initialize the TestFileManager.

        Args:
            test_dir: Directory where test files should be saved.
        """
        self.test_dir = test_dir
        os.makedirs(self.test_dir, exist_ok=True)

    def save_test_file(self, test_file_path: str, test_code: str) -> None:
        """
        Save test code to a specified file.

        Args:
            test_file_path: Full path to the test file.
            test_code: The test code to save.
        """
        try:
            os.makedirs(os.path.dirname(test_file_path) or '.', exist_ok=True)
            with open(test_file_path, "w") as file:
                file.write(test_code)
            logger.info(f"Test code saved successfully to {test_file_path}")
        except Exception as e:
            logger.error(f"Failed to save test code to {test_file_path}: {e}")
            raise

    def get_test_file_path(self, function_name: str, script_dir: Optional[str] = None) -> str:
        """
        Generate test file path for a function.

        Args:
            function_name: Name of the function being tested.
            script_dir: Optional directory for the test file. Uses test_dir if None.

        Returns:
            The full path to the test file.
        """
        directory = script_dir if script_dir is not None else self.test_dir
        return os.path.join(directory, f"test_{function_name}.py")
