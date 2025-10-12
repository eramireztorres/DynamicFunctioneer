"""
Code management components for dynamic code storage, loading, and execution.

This package handles all aspects of managing dynamically generated code including
file storage, module loading, test execution, and hot-swapping.
"""

from dynamic_functioneer.code_management.code_storage import CodeFileManager, DynamicTestFileManager
from dynamic_functioneer.code_management.code_loader import DynamicModuleLoader
from dynamic_functioneer.code_management.dynamic_code_manager import DynamicCodeManager
from dynamic_functioneer.code_management.test_runner import (
    TestExecutionStrategy,
    SubprocessTestRunner,
    PytestRunner,
    UnittestRunner,
)
from dynamic_functioneer.code_management.hot_swap_executor import HotSwapExecutor

# Backward compatibility alias
TestFileManager = DynamicTestFileManager

__all__ = [
    'CodeFileManager',
    'TestFileManager',
    'DynamicTestFileManager',
    'DynamicModuleLoader',
    'DynamicCodeManager',
    'TestExecutionStrategy',
    'SubprocessTestRunner',
    'PytestRunner',
    'UnittestRunner',
    'HotSwapExecutor',
]
