"""
Dynamic module loading for runtime code execution.

This module handles Python module import/reload operations for dynamically
generated functions.
"""

import os
import sys
import importlib
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class DynamicModuleLoader:
    """
    Manages dynamic loading of Python modules and functions.

    Responsibilities:
    - Import modules dynamically
    - Reload modified modules
    - Extract functions from modules
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the DynamicModuleLoader.

        Args:
            file_path: Path to the Python file containing the dynamic code.
        """
        self.file_path = file_path
        self.module_name = os.path.splitext(os.path.basename(file_path))[0]

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
        importlib.invalidate_caches()  # Clear cache

        try:
            # Remove module from cache to force reload
            if self.module_name in sys.modules:
                del sys.modules[self.module_name]

            # Add the directory to sys.path if not already there
            module_dir = os.path.dirname(os.path.abspath(self.file_path))
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)

            # Import the module
            module = importlib.import_module(self.module_name)

            # Get the function from the module
            if not hasattr(module, function_name):
                raise ImportError(
                    f"Function '{function_name}' not found in module '{self.module_name}'."
                )

            return getattr(module, function_name)

        except Exception as e:
            logger.error(f"Failed to load function '{function_name}' from '{self.module_name}': {e}")
            raise ImportError(f"Failed to load function '{function_name}': {e}") from e

    def reload_module(self) -> None:
        """
        Force reload of the module.

        This is useful when the file content has changed and needs to be reloaded.
        """
        if self.module_name in sys.modules:
            try:
                importlib.reload(sys.modules[self.module_name])
                logger.debug(f"Reloaded module: {self.module_name}")
            except Exception as e:
                logger.error(f"Failed to reload module {self.module_name}: {e}")
                raise
