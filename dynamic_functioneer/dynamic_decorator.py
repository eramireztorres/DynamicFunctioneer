import logging
import inspect
import importlib
import os
from functools import wraps
import ast
from inspect import signature
from dynamic_functioneer.code_management.dynamic_code_manager import DynamicCodeManager
from dynamic_functioneer.code_generation.llm_code_generator import LLMCodeGenerator
from dynamic_functioneer.code_management.hot_swap_executor import HotSwapExecutor
from dynamic_functioneer.code_processing.llm_response_cleaner import LLMResponseCleaner
from dynamic_functioneer.code_processing.prompt_code_cleaner import DynamicFunctionCleaner
from dynamic_functioneer.utils.introspection import extract_class_code, is_class_method
from dynamic_functioneer.dynamic_execution_handler import DynamicExecutionHandler






def dynamic_function(
    model="gpt-4.1-mini",
    prompt=None,
    dynamic_file=None,
    dynamic_test_file=None,
    extra_info=None,
    fix_dynamically=True,
    error_trials=3,
    error_model="gpt-4.1-mini",
    error_prompt=None,
    hs_condition=None,
    hs_model="gpt-4.1-mini",
    hs_prompt=None,
    execution_context=None,
    keep_ok_version=True,
    unit_test=False
):
    def decorator(func):
        
        # Determine the directory of the script containing the decorated function
        script_file_path = inspect.getfile(func)
        script_dir = os.path.dirname(os.path.abspath(script_file_path))
        
        is_method = is_class_method(func)

        config = {
            'model': model,
            'dynamic_file': dynamic_file,
            'dynamic_test_file': dynamic_test_file,
            'extra_info': extra_info,
            'fix_dynamically': fix_dynamically,
            'error_trials': error_trials,
            'error_model': error_model,
            'error_prompt': error_prompt,
            'hs_condition': hs_condition,
            'hs_model': hs_model,
            'hs_prompt': hs_prompt,
            'execution_context': execution_context,
            'keep_ok_version': keep_ok_version,
            'unit_test': unit_test
        }

        if is_method:
            # Wrapper for methods           
            @wraps(func)
            def method_wrapper(self, *args, **kwargs):
                handler = DynamicExecutionHandler(
                    func=func, 
                    script_dir=script_dir, 
                    config=config, 
                    is_method=True, 
                    instance=self
                )
                return handler.execute(*args, **kwargs)
            return method_wrapper

        else:
            # Wrapper for functions
            @wraps(func)
            def function_wrapper(*args, **kwargs):
                handler = DynamicExecutionHandler(
                    func=func, 
                    script_dir=script_dir, 
                    config=config, 
                    is_method=False, 
                    instance=None
                )
                return handler.execute(*args, **kwargs)

            return function_wrapper

    return decorator


class TestImportInjector:
    """
    Ensures that the necessary imports (unittest or pytest) are included in test scripts
    and appends the necessary test execution block.
    """

    @staticmethod
    def ensure_imports(test_code, module_name, function_name):
        """
        Ensures that:
        1. Required testing framework imports (unittest or pytest) are present.
        2. The tested function is imported at the top of the script.
        3. A unittest main execution block is added.

        Args:
            test_code (str): The test script.
            module_name (str): The module name where the function is defined.
            function_name (str): The function being tested.

        Returns:
            str: The modified test script with necessary imports and execution.
        """
        # Ensure unittest or pytest is imported
        if "unittest" in test_code and "import unittest" not in test_code:
            test_code = "import unittest\n" + test_code

        if "pytest" in test_code and "import pytest" not in test_code:
            test_code = "import pytest\n" + test_code

        # Ensure the function is imported
        function_import = f"from {module_name} import {function_name}"
        if function_import not in test_code:
            test_code = function_import + "\n" + test_code

        # Ensure unittest main block is present
        if "unittest" in test_code and "__name__ == \"__main__\"" not in test_code:
            test_code += "\n\nif __name__ == \"__main__\":\n    unittest.main()\n"

        return test_code