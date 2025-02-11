import functools
import logging
import inspect
import importlib
import sys
import os
from functools import wraps
import ast
from dynamic_functioneer.dynamic_code_manager import DynamicCodeManager
from dynamic_functioneer.llm_code_generator import LLMCodeGenerator, extract_method_signature
from dynamic_functioneer.hot_swap_executor import HotSwapExecutor
from dynamic_functioneer.llm_response_cleaner import LLMResponseCleaner
from dynamic_functioneer.prompt_code_cleaner import DynamicFunctionCleaner


def _extract_class_code(module, class_name):
    """
    Extracts the full class code for the specified class.

    Args:
        module (module): The module containing the class.
        class_name (str): The name of the class.

    Returns:
        str: The full class code as a string.

    Raises:
        ValueError: If the class cannot be found or extracted.
    """
    # Get the source code of the module
    source = inspect.getsource(module)

    # Parse the source code into an AST
    tree = ast.parse(source)

    # Locate the target class
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return ast.unparse(node)

    raise ValueError(f"Class {class_name} not found in module {module.__name__}")



def dynamic_function(
    model="gpt-4o",
    prompt=None,
    dynamic_file=None,
    dynamic_test_file=None,
    extra_info=None,
    fix_dynamically=True,
    error_trials=3,
    error_model="gpt-4o",
    error_prompt=None,
    hs_condition=None,
    hs_model="gpt-4o",
    hs_prompt=None,
    execution_context=None,
    keep_ok_version=True,
    unit_test=False
):
    def decorator(func):
        
        # Determine the directory of the script containing the decorated function
        script_file_path = inspect.getfile(func)
        script_dir = os.path.dirname(os.path.abspath(script_file_path))
        module_name = os.path.splitext(os.path.basename(script_file_path))[0]  # Extract module name
        function_name = func.__name__

        is_method = "." in func.__qualname__

        if is_method:
            # Wrapper for methods           
            @wraps(func)
            def method_wrapper(self, *args, **kwargs):
                function_name = func.__name__
                class_name = self.__class__.__name__
                default_dynamic_file = os.path.join(script_dir, f"d_{class_name}_{function_name}.py")
                dynamic_file_path = dynamic_file or default_dynamic_file
            
                # Initialize components
                code_manager = DynamicCodeManager(dynamic_file_path)
                llm_generator = LLMCodeGenerator(model=model)
                try:
                    class_code = inspect.getsource(self.__class__)
                except OSError:
                    logging.warning(f"Source code for class {class_name} is not available. Using repr as fallback.")
                    class_code = repr(self.__class__)
                
                class_code = DynamicFunctionCleaner(class_code).clean_dynamic_function()
                
                hot_swap_executor = HotSwapExecutor(
                    code_manager=code_manager,
                    llm_generator=llm_generator,
                    retries=error_trials,
                    is_method=True,
                    class_code=class_code
                )
            
                if not code_manager.code_exists():
                    logging.info(f"Generating initial code for method {function_name}...")
                    
                    method_code = llm_generator.method_code_generation(
                            class_definition=class_code,
                            method_header=func.__name__,  # Pass only the method name
                            extra_info=extra_info
                        )
                   
                                        
                    cleaned_code = LLMResponseCleaner.clean_response(method_code)                    
                    cleaned_code = DynamicFunctionCleaner(cleaned_code).clean_dynamic_function()
                    
                    logging.info(f"Generated method code:\n{cleaned_code}")
                    code_manager.save_code(cleaned_code)
            
                    # Determine the test prompt dynamically
                    # test_prompt = "test_method_prompt.txt"
                    cleaned_test_code = None
                    if unit_test:
                        try:
                            test_code = llm_generator.generate_method_test_logic(
                                class_definition=class_code,
                                method_header=inspect.getsource(func),
                                extra_info=extra_info
                            )
                            
                            try:
                                cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
                                cleaned_test_code = DynamicFunctionCleaner(cleaned_test_code).clean_dynamic_function()
                                cleaned_test_code = TestImportInjector.ensure_imports(cleaned_test_code, module_name, function_name)
                                
                            except Exception as e:
                                logging.warning(f"Failed to clean test code for {function_name}: {e}")
                                cleaned_test_code = None
                                
                        except Exception as e:
                            logging.warning(f"Failed to generate test code for {function_name}: {e}")
                            cleaned_test_code = None
                        

            
                    hot_swap_executor.execute_workflow(
                        function_name=function_name,
                        test_code=cleaned_test_code if unit_test else None,
                        script_dir=script_dir
                    )

            
                importlib.invalidate_caches()
                dynamic_method = code_manager.load_function(function_name)
                dynamic_method = dynamic_method.__get__(self, type(self))  # Bind to instance
            
                try:
                    result = dynamic_method(*args, **kwargs)
                    logging.info(f"Dynamic method executed successfully with result: {result}")
                    return result
                except Exception as e:
                    logging.error(f"Runtime error in method {function_name}: {e}", exc_info=True)
                    if fix_dynamically:
                        for attempt in range(1, error_trials + 1):
                            logging.info(f"Attempting to fix {function_name} dynamically (attempt {attempt}/{error_trials})...")
                    
                            # Create a new LLMCodeGenerator with the error model
                            error_llm_generator = LLMCodeGenerator(model=error_model)
                    
                            try:
                                corrected_code = error_llm_generator.fix_runtime_error(
                                    code_manager.load_code(),
                                    error_message=str(e)
                                )
                                
                                corrected_code = LLMResponseCleaner.clean_response(corrected_code)
                                corrected_code = DynamicFunctionCleaner(corrected_code).clean_dynamic_function()
                    
                                cleaned_test_code = None
                                if unit_test:
                                    # Generate the corresponding test code
                                    try:
                                        test_code = error_llm_generator.generate_method_test_logic(
                                            class_definition=class_code,
                                            method_header=inspect.getsource(func),
                                            extra_info=extra_info
                                        )
                        
                                        try:
                                            cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
                                            cleaned_test_code = DynamicFunctionCleaner(cleaned_test_code).clean_dynamic_function()
                                            cleaned_test_code = TestImportInjector.ensure_imports(cleaned_test_code, module_name, function_name)
                                        except Exception as e:
                                            logging.warning(f"Failed to clean test code for {function_name}: {e}")
                                            cleaned_test_code = None
                                            
                                    except Exception as e:
                                        logging.warning(f"Failed to generate test code for {function_name}: {e}")
                                        cleaned_test_code = None
                    
                                # Apply the corrected code and validate
                                if hot_swap_executor._apply_error_correction(function_name, corrected_code, cleaned_test_code, script_dir):
                                    # Reload and execute the corrected function/method
                                    importlib.invalidate_caches()
                                    if is_method:
                                        dynamic_method = code_manager.load_function(function_name).__get__(self, type(self))
                                        result = dynamic_method(*args, **kwargs)
                                    else:
                                        dynamic_function = code_manager.load_function(function_name)
                                        result = dynamic_function(*args, **kwargs)
                    
                                    logging.info(f"Fixed {function_name} successfully on attempt {attempt} with result: {result}")
                                    return result
                                else:
                                    logging.warning(f"Fix attempt {attempt} for {function_name} failed.")
                            except Exception as retry_error:
                                logging.error(f"Fix attempt {attempt} for {function_name} encountered an error: {retry_error}")
                    
                        logging.error(f"All {error_trials} attempts to fix {function_name} failed.")
                        raise e
                    else:
                        raise e

            return method_wrapper

        else:
            # Wrapper for functions
            @wraps(func)
            def function_wrapper(*args, **kwargs):
                function_name = func.__name__
                default_dynamic_file = os.path.join(script_dir, f"d_{function_name}.py")
                dynamic_file_path = dynamic_file or default_dynamic_file

                # Initialize components
                code_manager = DynamicCodeManager(dynamic_file_path)
                llm_generator = LLMCodeGenerator(model=model)
                hot_swap_executor = HotSwapExecutor(
                    code_manager=code_manager,
                    llm_generator=llm_generator,
                    retries=error_trials,
                    is_method=False,
                    class_code=None
                )

                # Generate or load code
                if not code_manager.code_exists():
                    logging.info(f"Generating initial code for function {function_name}...")
                    function_code = llm_generator.initial_code_generation(
                        function_header=inspect.getsource(func),
                        docstring=func.__doc__,
                        extra_info=extra_info,
                    )
                    cleaned_code = LLMResponseCleaner.clean_response(function_code)                    
                    cleaned_code = DynamicFunctionCleaner(cleaned_code).clean_dynamic_function()
                    
                    logging.info(f"Generated function code:\n{cleaned_code}")
                    code_manager.save_code(cleaned_code)
                    
                    # Determine the test prompt dynamically
                    # test_prompt = "test_function_prompt.txt"
                    cleaned_test_code = None
                    
                               
                    if unit_test:
                        try:
                            
                            function_code = inspect.getsource(func)
                            function_code = DynamicFunctionCleaner(function_code).clean_dynamic_function()
                            
                            test_code = llm_generator.generate_function_test_logic(
                                function_code=function_code,
                                extra_info=extra_info
                            )
                            try:
                                cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
                                cleaned_test_code = DynamicFunctionCleaner(cleaned_test_code).clean_dynamic_function()
                                cleaned_test_code = TestImportInjector.ensure_imports(cleaned_test_code, module_name, function_name)
                            except Exception as e:
                                logging.warning(f"Failed to clean test code for {function_name}: {e}")
                                cleaned_test_code = None
                                
                        except Exception as e:
                            logging.warning(f"Failed to generate test code for {function_name}: {e}")
                            cleaned_test_code = None
            
                    hot_swap_executor.execute_workflow(
                        function_name=function_name,
                        test_code=cleaned_test_code if unit_test else None,
                        script_dir=script_dir
                    )
            

                # Load and execute the function
                importlib.invalidate_caches()
                dynamic_function = code_manager.load_function(function_name)
                try:
                    result = dynamic_function(*args, **kwargs)
                    logging.info(f"Dynamic function executed successfully with result: {result}")
                    return result
                except Exception as e:
                    logging.error(f"Runtime error in function {function_name}: {e}", exc_info=True)
                    if fix_dynamically:
                        for attempt in range(1, error_trials + 1):
                            logging.info(f"Attempting to fix {function_name} dynamically (attempt {attempt}/{error_trials})...")
                    
                            # Create a new LLMCodeGenerator with the error model
                            error_llm_generator = LLMCodeGenerator(model=error_model)
                    
                            try:
                                corrected_code = error_llm_generator.fix_runtime_error(
                                    code_manager.load_code(),
                                    error_message=str(e)
                                )
                                
                                corrected_code = LLMResponseCleaner.clean_response(corrected_code)
                                corrected_code = DynamicFunctionCleaner(corrected_code).clean_dynamic_function()
                                
                                cleaned_test_code = None
                                if unit_test:
                                    # Generate the corresponding test code
                                    try:
                                        
                                        function_code = inspect.getsource(func)
                                        function_code = DynamicFunctionCleaner(function_code).clean_dynamic_function()
                                        
                                        test_code = error_llm_generator.generate_function_test_logic(
                                            function_code=function_code,
                                            extra_info=extra_info
                                        )
                        
                                        try:
                                            cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
                                            cleaned_test_code = DynamicFunctionCleaner(cleaned_test_code).clean_dynamic_function()
                                            cleaned_test_code = TestImportInjector.ensure_imports(cleaned_test_code, module_name, function_name)
                                          
                                        except Exception as e:
                                            logging.warning(f"Failed to clean test code for {function_name}: {e}")
                                            cleaned_test_code = None
                                            
                                    except Exception as e:
                                        logging.warning(f"Failed to generate test code for {function_name}: {e}")
                                        cleaned_test_code = None
                                        
                                # Apply the corrected code and validate
                                if hot_swap_executor._apply_error_correction(function_name, corrected_code, cleaned_test_code, script_dir):
                                    # Reload and execute the corrected function/method
                                    importlib.invalidate_caches()
                                    dynamic_function = code_manager.load_function(function_name)
                                    result = dynamic_function(*args, **kwargs)
                    
                                    logging.info(f"Fixed {function_name} successfully on attempt {attempt} with result: {result}")
                                    return result
                                else:
                                    logging.warning(f"Fix attempt {attempt} for {function_name} failed.")
                            except Exception as retry_error:
                                logging.error(f"Fix attempt {attempt} for {function_name} encountered an error: {retry_error}")
                    
                        logging.error(f"All {error_trials} attempts to fix {function_name} failed.")
                        raise e
                    else:
                        raise e

                        
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





# def dynamic_function(
#     model="gpt-4o",
#     prompt=None,
#     dynamic_file=None,
#     dynamic_test_file=None,
#     extra_info=None,
#     fix_dynamically=True,
#     error_trials=3,
#     error_model="gpt-4o",
#     error_prompt=None,
#     hs_condition=None,
#     hs_model="gpt-4o",
#     hs_prompt=None,
#     execution_context=None,
#     keep_ok_version=True,
# ):
#     def decorator(func):
        
#         # Determine the directory of the script containing the decorated function
#         script_file_path = inspect.getfile(func)
#         script_dir = os.path.dirname(os.path.abspath(script_file_path))
        
#         is_method = "." in func.__qualname__

#         if is_method:
#             # Wrapper for methods           
#             @wraps(func)
#             def method_wrapper(self, *args, **kwargs):
#                 function_name = func.__name__
#                 class_name = self.__class__.__name__
#                 default_dynamic_file = os.path.join(script_dir, f"d_{class_name}_{function_name}.py")
#                 dynamic_file_path = dynamic_file or default_dynamic_file
            
#                 # Initialize components
#                 code_manager = DynamicCodeManager(dynamic_file_path)
#                 llm_generator = LLMCodeGenerator(model=model)
#                 try:
#                     class_code = inspect.getsource(self.__class__)
#                 except OSError:
#                     logging.warning(f"Source code for class {class_name} is not available. Using repr as fallback.")
#                     class_code = repr(self.__class__)
            
#                 hot_swap_executor = HotSwapExecutor(
#                     code_manager=code_manager,
#                     llm_generator=llm_generator,
#                     retries=error_trials,
#                     is_method=True,
#                     class_code=class_code
#                 )
            
#                 if not code_manager.code_exists():
#                     logging.info(f"Generating initial code for method {function_name}...")
                    
#                     method_code = llm_generator.method_code_generation(
#                             class_definition=class_code,
#                             method_header=func.__name__,  # Pass only the method name
#                             extra_info=extra_info
#                         )

                    
                    
#                     # method_code = llm_generator.method_code_generation(
#                     #     class_definition=class_code,
#                     #     method_header=inspect.getsource(func),
#                     #     extra_info=extra_info
#                     # )
                    
#                     # method_code = llm_generator.method_code_generation(
#                     #     class_definition=class_code,
#                     #     method_header=extract_method_signature(class_code, func.__name__),  # Pass only func.__name__
#                     #     extra_info=extra_info
#                     # )

                    
#                     cleaned_code = LLMResponseCleaner.clean_response(method_code)
#                     logging.info(f"Generated method code:\n{cleaned_code}")
#                     code_manager.save_code(cleaned_code)
            
#                     # Determine the test prompt dynamically
#                     test_prompt = "test_method_prompt.txt"
#                     test_code = llm_generator.generate_test_logic(
#                         cleaned_code,
#                         prompt=test_prompt
#                     )
#                     cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=cleaned_test_code,
#                         script_dir=script_dir
#                     )

            
#                 importlib.invalidate_caches()
#                 dynamic_method = code_manager.load_function(function_name)
#                 dynamic_method = dynamic_method.__get__(self, type(self))  # Bind to instance
            
#                 try:
#                     result = dynamic_method(*args, **kwargs)
#                     logging.info(f"Dynamic method executed successfully with result: {result}")
#                     return result
#                 except Exception as e:
#                     logging.error(f"Runtime error in method {function_name}: {e}", exc_info=True)
#                     if fix_dynamically:
#                         for attempt in range(1, error_trials + 1):
#                             logging.info(f"Attempting to fix method {function_name} dynamically (attempt {attempt}/{error_trials})...")
                            
#                             # Create a new LLMCodeGenerator with the error model
#                             error_llm_generator = LLMCodeGenerator(model=error_model)
                            
#                             try:
#                                 corrected_code = error_llm_generator.fix_runtime_error(
#                                     code_manager.load_code(),
#                                     error_message=str(e)
#                                 )
#                                 test_prompt = "test_method_prompt.txt"
#                                 test_code = error_llm_generator.generate_test_logic(
#                                     corrected_code,
#                                     prompt=test_prompt
#                                 )
#                                 cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
                    
#                                 hot_swap_executor.execute_workflow(
#                                     function_name=function_name,
#                                     test_code=cleaned_test_code,
#                                     script_dir=script_dir,
#                                     error_message=str(e)
#                                 )
                    
#                                 importlib.invalidate_caches()
#                                 dynamic_method = code_manager.load_function(function_name)
#                                 dynamic_method = dynamic_method.__get__(self, type(self))
#                                 result = dynamic_method(*args, **kwargs)
#                                 logging.info(f"Fixed method executed successfully on attempt {attempt} with result: {result}")
#                                 return result
#                             except Exception as retry_error:
#                                 logging.error(f"Fix attempt {attempt} for method {function_name} failed: {retry_error}")
                        
#                         logging.error(f"All {error_trials} attempts to fix method {function_name} failed.")
#                         raise e

#                     else:
#                         raise e


#             return method_wrapper

#         else:
#             # Wrapper for functions
#             @wraps(func)
#             def function_wrapper(*args, **kwargs):
#                 function_name = func.__name__
#                 default_dynamic_file = os.path.join(script_dir, f"d_{function_name}.py")
#                 dynamic_file_path = dynamic_file or default_dynamic_file

#                 # Initialize components
#                 code_manager = DynamicCodeManager(dynamic_file_path)
#                 llm_generator = LLMCodeGenerator(model=model)
#                 hot_swap_executor = HotSwapExecutor(
#                     code_manager=code_manager,
#                     llm_generator=llm_generator,
#                     retries=error_trials,
#                     is_method=False,
#                     class_code=None
#                 )

#                 # Generate or load code
#                 if not code_manager.code_exists():
#                     logging.info(f"Generating initial code for function {function_name}...")
#                     function_code = llm_generator.initial_code_generation(
#                         function_header=inspect.getsource(func),
#                         docstring=func.__doc__,
#                         extra_info=extra_info,
#                     )
#                     cleaned_code = LLMResponseCleaner.clean_response(function_code)
#                     logging.info(f"Generated function code:\n{cleaned_code}")
#                     code_manager.save_code(cleaned_code)
                    
#                     # Determine the test prompt dynamically
#                     test_prompt = "test_function_prompt.txt"
#                     test_code = llm_generator.generate_test_logic(
#                         cleaned_code,
#                         prompt=test_prompt
#                     )
#                     cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=cleaned_test_code,
#                         script_dir=script_dir
#                     )
            

#                 # Load and execute the function
#                 importlib.invalidate_caches()
#                 dynamic_function = code_manager.load_function(function_name)
#                 try:
#                     result = dynamic_function(*args, **kwargs)
#                     logging.info(f"Dynamic function executed successfully with result: {result}")
#                     return result
#                 except Exception as e:
#                     logging.error(f"Runtime error in function {function_name}: {e}", exc_info=True)
#                     if fix_dynamically:
#                         for attempt in range(1, error_trials + 1):
#                             logging.info(f"Attempting to fix function {function_name} dynamically (attempt {attempt}/{error_trials})...")
                            
#                             # Create a new LLMCodeGenerator with the error model
#                             error_llm_generator = LLMCodeGenerator(model=error_model)
                            
#                             try:
#                                 corrected_code = error_llm_generator.fix_runtime_error(
#                                     code_manager.load_code(),
#                                     error_message=str(e)
#                                 )
#                                 test_prompt = "test_function_prompt.txt"
#                                 test_code = error_llm_generator.generate_test_logic(
#                                     corrected_code,
#                                     prompt=test_prompt
#                                 )
#                                 cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
                    
#                                 hot_swap_executor.execute_workflow(
#                                     function_name=function_name,
#                                     test_code=cleaned_test_code,
#                                     script_dir=script_dir,
#                                     error_message=str(e)
#                                 )
                    
#                                 importlib.invalidate_caches()
#                                 dynamic_function = code_manager.load_function(function_name)
#                                 result = dynamic_function(*args, **kwargs)
#                                 logging.info(f"Fixed function executed successfully on attempt {attempt} with result: {result}")
#                                 return result
#                             except Exception as retry_error:
#                                 logging.error(f"Fix attempt {attempt} for function {function_name} failed: {retry_error}")
                        
#                         logging.error(f"All {error_trials} attempts to fix function {function_name} failed.")
#                         raise e

#                     else:
#                         raise e
#             return function_wrapper

#     return decorator


# def dynamic_function(
#     model="gpt-4o",
#     prompt=None,
#     dynamic_file=None,
#     dynamic_test_file=None,
#     extra_info=None,
#     fix_dynamically=True,
#     error_trials=3,
#     error_model="gpt-4o",
#     error_prompt=None,
#     hs_condition=None,
#     hs_model="gpt-4o",
#     hs_prompt=None,
#     execution_context=None,
#     keep_ok_version=True,
# ):
#     def decorator(func):
        
#         # Determine the directory of the script containing the decorated function
#         script_file_path = inspect.getfile(func)
#         script_dir = os.path.dirname(os.path.abspath(script_file_path))
        
#         is_method = "." in func.__qualname__

#         if is_method:
#             # Wrapper for methods           
#             @wraps(func)
#             def method_wrapper(self, *args, **kwargs):
#                 function_name = func.__name__
#                 class_name = self.__class__.__name__
#                 default_dynamic_file = os.path.join(script_dir, f"d_{class_name}_{function_name}.py")
#                 dynamic_file_path = dynamic_file or default_dynamic_file
            
#                 # Initialize components
#                 code_manager = DynamicCodeManager(dynamic_file_path)
#                 llm_generator = LLMCodeGenerator(model=model)
#                 try:
#                     class_code = inspect.getsource(self.__class__)
#                 except OSError:
#                     logging.warning(f"Source code for class {class_name} is not available. Using repr as fallback.")
#                     class_code = repr(self.__class__)
            
#                 hot_swap_executor = HotSwapExecutor(
#                     code_manager=code_manager,
#                     llm_generator=llm_generator,
#                     retries=error_trials,
#                     is_method=True,
#                     class_code=class_code
#                 )
            
#                 if not code_manager.code_exists():
#                     logging.info(f"Generating initial code for method {function_name}...")
                    
#                     method_code = llm_generator.method_code_generation(
#                             class_definition=class_code,
#                             method_header=func.__name__,  # Pass only the method name
#                             extra_info=extra_info
#                         )

                    
                    
#                     # method_code = llm_generator.method_code_generation(
#                     #     class_definition=class_code,
#                     #     method_header=inspect.getsource(func),
#                     #     extra_info=extra_info
#                     # )
                    
#                     # method_code = llm_generator.method_code_generation(
#                     #     class_definition=class_code,
#                     #     method_header=extract_method_signature(class_code, func.__name__),  # Pass only func.__name__
#                     #     extra_info=extra_info
#                     # )

                    
#                     cleaned_code = LLMResponseCleaner.clean_response(method_code)
#                     logging.info(f"Generated method code:\n{cleaned_code}")
#                     code_manager.save_code(cleaned_code)
            
#                     # Determine the test prompt dynamically
#                     test_prompt = "test_method_prompt.txt"
#                     test_code = llm_generator.generate_test_logic(
#                         cleaned_code,
#                         prompt=test_prompt
#                     )
#                     cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=cleaned_test_code,
#                         script_dir=script_dir
#                     )

            
#                 importlib.invalidate_caches()
#                 dynamic_method = code_manager.load_function(function_name)
#                 dynamic_method = dynamic_method.__get__(self, type(self))  # Bind to instance
            
#                 try:
#                     result = dynamic_method(*args, **kwargs)
#                     logging.info(f"Dynamic method executed successfully with result: {result}")
#                     return result
#                 except Exception as e:
#                     logging.error(f"Runtime error in method {function_name}: {e}", exc_info=True)
#                     if fix_dynamically:
#                         logging.info(f"Attempting to fix method {function_name} dynamically.")
#                         corrected_code = llm_generator.fix_runtime_error(
#                             code_manager.load_code(),
#                             error_message=str(e)
#                         )
#                         test_code = llm_generator.generate_test_logic(
#                             corrected_code,
#                             prompt="test_method_prompt.txt"
#                         )
#                         cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
#                         hot_swap_executor.execute_workflow(
#                             function_name=function_name,
#                             test_code=cleaned_test_code,
#                             script_dir=script_dir,
#                             error_message=str(e)
#                         )
                        
           
#                         importlib.invalidate_caches()
#                         dynamic_method = code_manager.load_function(function_name)
#                         dynamic_method = dynamic_method.__get__(self, type(self))
#                         result = dynamic_method(*args, **kwargs)
#                         logging.info(f"Fixed method executed successfully with result: {result}")
#                         return result
#                     else:
#                         raise e


#             return method_wrapper

#         else:
#             # Wrapper for functions
#             @wraps(func)
#             def function_wrapper(*args, **kwargs):
#                 function_name = func.__name__
#                 default_dynamic_file = os.path.join(script_dir, f"d_{function_name}.py")
#                 dynamic_file_path = dynamic_file or default_dynamic_file

#                 # Initialize components
#                 code_manager = DynamicCodeManager(dynamic_file_path)
#                 llm_generator = LLMCodeGenerator(model=model)
#                 hot_swap_executor = HotSwapExecutor(
#                     code_manager=code_manager,
#                     llm_generator=llm_generator,
#                     retries=error_trials,
#                     is_method=False,
#                     class_code=None
#                 )

#                 # Generate or load code
#                 if not code_manager.code_exists():
#                     logging.info(f"Generating initial code for function {function_name}...")
#                     function_code = llm_generator.initial_code_generation(
#                         function_header=inspect.getsource(func),
#                         docstring=func.__doc__,
#                         extra_info=extra_info,
#                     )
#                     cleaned_code = LLMResponseCleaner.clean_response(function_code)
#                     logging.info(f"Generated function code:\n{cleaned_code}")
#                     code_manager.save_code(cleaned_code)
                    
#                     # Determine the test prompt dynamically
#                     test_prompt = "test_function_prompt.txt"
#                     test_code = llm_generator.generate_test_logic(
#                         cleaned_code,
#                         prompt=test_prompt
#                     )
#                     cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=cleaned_test_code,
#                         script_dir=script_dir
#                     )
            

#                 # Load and execute the function
#                 importlib.invalidate_caches()
#                 dynamic_function = code_manager.load_function(function_name)
#                 try:
#                     result = dynamic_function(*args, **kwargs)
#                     logging.info(f"Dynamic function executed successfully with result: {result}")
#                     return result
#                 except Exception as e:
#                     logging.error(f"Runtime error in function {function_name}: {e}", exc_info=True)
#                     if fix_dynamically:
#                         logging.info(f"Attempting to fix function {function_name} dynamically.")
#                         corrected_code = llm_generator.fix_runtime_error(
#                             code_manager.load_code(),
#                             error_message=str(e)
#                         )
#                         test_prompt = "test_function_prompt.txt"
#                         test_code = llm_generator.generate_test_logic(
#                             corrected_code,
#                             prompt=test_prompt
#                         )
#                         cleaned_test_code = LLMResponseCleaner.clean_response(test_code)

#                         hot_swap_executor.execute_workflow(
#                             function_name=function_name,
#                             test_code=cleaned_test_code,
#                             script_dir=script_dir,
#                             error_message=str(e)
#                         )

#                         importlib.invalidate_caches()
#                         dynamic_function = code_manager.load_function(function_name)
#                         result = dynamic_function(*args, **kwargs)
#                         logging.info(f"Fixed function executed successfully with result: {result}")
#                         return result
#                     else:
#                         raise e
#             return function_wrapper

#     return decorator


# def dynamic_function(
#     model="gpt-4o",
#     prompt=None,
#     dynamic_file=None,
#     dynamic_test_file=None,
#     extra_info=None,
#     fix_dynamically=True,
#     error_trials=3,
#     error_model="gpt-4o",
#     error_prompt=None,
#     hs_condition=None,
#     hs_model="gpt-4o",
#     hs_prompt=None,
#     execution_context=None,
#     keep_ok_version=True,
# ):
#     def decorator(func):
#         is_method = "." in func.__qualname__

#         if is_method:
#             # Wrapper for methods
#             # @wraps(func)
#             # def method_wrapper(self, *args, **kwargs):
#             #     function_name = func.__name__
#             #     class_name = self.__class__.__name__
#             #     default_dynamic_file = f"d_{class_name}_{function_name}.py"
#             #     dynamic_file_path = dynamic_file or default_dynamic_file
            
#             #     # Initialize components
#             #     code_manager = DynamicCodeManager(dynamic_file_path)
#             #     llm_generator = LLMCodeGenerator(model=model)
#             #     hot_swap_executor = HotSwapExecutor(
#             #         code_manager=code_manager,
#             #         llm_generator=llm_generator,
#             #         retries=error_trials,
#             #         is_method=True,
#             #         class_code=inspect.getsource(self.__class__)
#             #     )
            
#             #     if not code_manager.code_exists():
#             #         logging.info(f"Generating initial code for method {function_name}...")
#             #         method_code = llm_generator.method_code_generation(
#             #             class_definition=inspect.getsource(self.__class__),
#             #             method_header=inspect.getsource(func),
#             #             extra_info=extra_info
#             #         )
#             #         cleaned_code = LLMResponseCleaner.clean_response(method_code)
#             #         logging.info(f"Generated method code:\n{cleaned_code}")
#             #         code_manager.save_code(cleaned_code)
            
#             #     importlib.invalidate_caches()
#             #     dynamic_method = code_manager.load_function(function_name)
#             #     dynamic_method = dynamic_method.__get__(self, type(self))  # Bind to instance
            
#             #     try:
#             #         result = dynamic_method(*args, **kwargs)
#             #         logging.info(f"Dynamic method executed successfully with result: {result}")
#             #         return result
#             #     except Exception as e:
#             #         logging.error(f"Runtime error in method {function_name}: {e}", exc_info=True)
#             #         if fix_dynamically:
#             #             logging.info(f"Attempting to fix method {function_name} dynamically.")
#             #             corrected_code = llm_generator.fix_runtime_error(
#             #                 code_manager.load_code(),
#             #                 error_message=str(e)
#             #             )
#             #             test_code = llm_generator.generate_test_logic(
#             #                 corrected_code,
#             #                 prompt="test_method_prompt.txt"
#             #             )
#             #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
#             #             hot_swap_executor.execute_workflow(
#             #                 function_name=function_name,
#             #                 test_code=cleaned_test_code,
#             #                 error_message=str(e),
#             #             )
            
#             #             importlib.invalidate_caches()
#             #             dynamic_method = code_manager.load_function(function_name)
#             #             dynamic_method = dynamic_method.__get__(self, type(self))
#             #             result = dynamic_method(*args, **kwargs)
#             #             logging.info(f"Fixed method executed successfully with result: {result}")
#             #             return result
#             #         else:
#             #             raise e
            
#             @wraps(func)
#             def method_wrapper(self, *args, **kwargs):
#                 function_name = func.__name__
#                 class_name = self.__class__.__name__
#                 default_dynamic_file = f"d_{class_name}_{function_name}.py"
#                 dynamic_file_path = dynamic_file or default_dynamic_file
            
#                 # Initialize components
#                 code_manager = DynamicCodeManager(dynamic_file_path)
#                 llm_generator = LLMCodeGenerator(model=model)
#                 try:
#                     class_code = inspect.getsource(self.__class__)
#                 except OSError:
#                     logging.warning(f"Source code for class {class_name} is not available. Using repr as fallback.")
#                     class_code = repr(self.__class__)
            
#                 hot_swap_executor = HotSwapExecutor(
#                     code_manager=code_manager,
#                     llm_generator=llm_generator,
#                     retries=error_trials,
#                     is_method=True,
#                     class_code=class_code
#                 )
            
#                 if not code_manager.code_exists():
#                     logging.info(f"Generating initial code for method {function_name}...")
#                     method_code = llm_generator.method_code_generation(
#                         class_definition=class_code,
#                         method_header=inspect.getsource(func),
#                         extra_info=extra_info
#                     )
#                     cleaned_code = LLMResponseCleaner.clean_response(method_code)
#                     logging.info(f"Generated method code:\n{cleaned_code}")
#                     code_manager.save_code(cleaned_code)
            
#                     # Determine the test prompt dynamically
#                     test_prompt = "test_method_prompt.txt"
#                     test_code = llm_generator.generate_test_logic(
#                         cleaned_code,
#                         prompt=test_prompt
#                     )
#                     cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=cleaned_test_code,
#                     )
            
#                 importlib.invalidate_caches()
#                 dynamic_method = code_manager.load_function(function_name)
#                 dynamic_method = dynamic_method.__get__(self, type(self))  # Bind to instance
            
#                 try:
#                     result = dynamic_method(*args, **kwargs)
#                     logging.info(f"Dynamic method executed successfully with result: {result}")
#                     return result
#                 except Exception as e:
#                     logging.error(f"Runtime error in method {function_name}: {e}", exc_info=True)
#                     if fix_dynamically:
#                         logging.info(f"Attempting to fix method {function_name} dynamically.")
#                         corrected_code = llm_generator.fix_runtime_error(
#                             code_manager.load_code(),
#                             error_message=str(e)
#                         )
#                         test_code = llm_generator.generate_test_logic(
#                             corrected_code,
#                             prompt="test_method_prompt.txt"
#                         )
#                         cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
#                         hot_swap_executor.execute_workflow(
#                             function_name=function_name,
#                             test_code=cleaned_test_code,
#                             error_message=str(e),
#                         )
            
#                         importlib.invalidate_caches()
#                         dynamic_method = code_manager.load_function(function_name)
#                         dynamic_method = dynamic_method.__get__(self, type(self))
#                         result = dynamic_method(*args, **kwargs)
#                         logging.info(f"Fixed method executed successfully with result: {result}")
#                         return result
#                     else:
#                         raise e


#             return method_wrapper

#         else:
#             # Wrapper for functions
#             @wraps(func)
#             def function_wrapper(*args, **kwargs):
#                 function_name = func.__name__
#                 default_dynamic_file = f"d_{function_name}.py"
#                 dynamic_file_path = dynamic_file or default_dynamic_file

#                 # Initialize components
#                 code_manager = DynamicCodeManager(dynamic_file_path)
#                 llm_generator = LLMCodeGenerator(model=model)
#                 hot_swap_executor = HotSwapExecutor(
#                     code_manager=code_manager,
#                     llm_generator=llm_generator,
#                     retries=error_trials,
#                     is_method=False,
#                     class_code=None
#                 )

#                 # Generate or load code
#                 if not code_manager.code_exists():
#                     logging.info(f"Generating initial code for function {function_name}...")
#                     function_code = llm_generator.initial_code_generation(
#                         function_header=inspect.getsource(func),
#                         docstring=func.__doc__,
#                         extra_info=extra_info,
#                     )
#                     cleaned_code = LLMResponseCleaner.clean_response(function_code)
#                     logging.info(f"Generated function code:\n{cleaned_code}")
#                     code_manager.save_code(cleaned_code)

#                 # Load and execute the function
#                 importlib.invalidate_caches()
#                 dynamic_function = code_manager.load_function(function_name)
#                 try:
#                     result = dynamic_function(*args, **kwargs)
#                     logging.info(f"Dynamic function executed successfully with result: {result}")
#                     return result
#                 except Exception as e:
#                     logging.error(f"Runtime error in function {function_name}: {e}", exc_info=True)
#                     if fix_dynamically:
#                         logging.info(f"Attempting to fix function {function_name} dynamically.")
#                         corrected_code = llm_generator.fix_runtime_error(
#                             code_manager.load_code(),
#                             error_message=str(e)
#                         )
#                         test_prompt = "test_function_prompt.txt"
#                         test_code = llm_generator.generate_test_logic(
#                             corrected_code,
#                             prompt=test_prompt
#                         )
#                         cleaned_test_code = LLMResponseCleaner.clean_response(test_code)

#                         hot_swap_executor.execute_workflow(
#                             function_name=function_name,
#                             test_code=cleaned_test_code,
#                             error_message=str(e),
#                         )

#                         importlib.invalidate_caches()
#                         dynamic_function = code_manager.load_function(function_name)
#                         result = dynamic_function(*args, **kwargs)
#                         logging.info(f"Fixed function executed successfully with result: {result}")
#                         return result
#                     else:
#                         raise e
#             return function_wrapper

#     return decorator


# # # @elapsedTimeDecorator()
# @dynamic_function(
#     model="meta-llama/llama-3.2-3b-instruct:free",
#     # prompt="custom_prompt.txt",
#     # hs_condition="len(numbers) > 1000",
#     # execution_context={"frequent_inputs": [[], [1, 2, 3]]},
#     # keep_ok_version=True
# )
# def calculate_average(numbers):
#     """
#     Calculates the average of a list of numbers.

#     Args:
#         numbers (list of float): A list of numeric values.

#     Returns:
#         float: The average of the list.
#     """
#     pass


# print(calculate_average([1, 3, 7]))

# print(calculate_average([3.3]*2000))

# @elapsedTimeDecorator()
# def d_calculate_average(numbers):
#     """
#     Calculates the average of a list of numbers.
#     Args:
#         numbers (list of float): A list of numeric values.
#     Returns:
#         float: The average of the list.
#     """
#     # Ensure the list is not empty to avoid division by zero
#     if not numbers:
#         return 0.0
#     # Calculate the sum of the numbers
#     total_sum = sum(numbers)
#     # Determine the number of elements in the list
#     count = len(numbers)
#     # Calculate and return the average
#     return total_sum / count

# print(d_calculate_average([1, 3, 7]))

# class Inventory:
#     def __init__(self):
#         """
#         Initializes the inventory with an empty stock dictionary.
#         """
#         self.stock = {}

#     @dynamic_function()
#     def update_stock(self, product, quantity):
#         """
#         Updates the stock for a product.

#         Args:
#             product (str): The name of the product.
#             quantity (int): The quantity to add (positive) or remove (negative).

#         Raises:
#             ValueError: If quantity is negative and results in stock below zero.
#         """
#         pass

# # Example Usage
# inventory = Inventory()

# # Add new product
# inventory.update_stock("apple", 50)

# # # # # Reduce stock
# # # # inventory.update_stock("apple", -20)

# # # # # Attempt invalid operation (should trigger dynamic fixing)
# # # # inventory.update_stock("apple", -40)


# # @elapsedTimeDecorator()
# @dynamic_function(
#     # model="meta-llama/llama-3.2-3b-instruct:free"
# )
# def calculate_average(numbers):
#     """
#     Calculates the average of a list of numbers.

#     Args:
#         numbers (list of float): A list of numeric values.

#     Returns:
#         float: The average of the list.
#     """
#     pass


# print(calculate_average([1, 3, 7]))