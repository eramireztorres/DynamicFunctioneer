import functools
import logging
import inspect
from dynamic_code_manager import DynamicCodeManager
from llm_code_generator import LLMCodeGenerator
from hot_swap_executor import HotSwapExecutor
from llm_response_cleaner import LLMResponseCleaner
import importlib
import sys
from functools import wraps
from etimedecorator import elapsedTimeDecorator

import ast

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
):
    def decorator(func):
        is_method = "." in func.__qualname__

        if is_method:
            # Wrapper for methods
            # @wraps(func)
            # def method_wrapper(self, *args, **kwargs):
            #     function_name = func.__name__
            #     class_name = self.__class__.__name__
            #     default_dynamic_file = f"d_{class_name}_{function_name}.py"
            #     dynamic_file_path = dynamic_file or default_dynamic_file
            
            #     # Initialize components
            #     code_manager = DynamicCodeManager(dynamic_file_path)
            #     llm_generator = LLMCodeGenerator(model=model)
            #     hot_swap_executor = HotSwapExecutor(
            #         code_manager=code_manager,
            #         llm_generator=llm_generator,
            #         retries=error_trials,
            #         is_method=True,
            #         class_code=inspect.getsource(self.__class__)
            #     )
            
            #     if not code_manager.code_exists():
            #         logging.info(f"Generating initial code for method {function_name}...")
            #         method_code = llm_generator.method_code_generation(
            #             class_definition=inspect.getsource(self.__class__),
            #             method_header=inspect.getsource(func),
            #             extra_info=extra_info
            #         )
            #         cleaned_code = LLMResponseCleaner.clean_response(method_code)
            #         logging.info(f"Generated method code:\n{cleaned_code}")
            #         code_manager.save_code(cleaned_code)
            
            #     importlib.invalidate_caches()
            #     dynamic_method = code_manager.load_function(function_name)
            #     dynamic_method = dynamic_method.__get__(self, type(self))  # Bind to instance
            
            #     try:
            #         result = dynamic_method(*args, **kwargs)
            #         logging.info(f"Dynamic method executed successfully with result: {result}")
            #         return result
            #     except Exception as e:
            #         logging.error(f"Runtime error in method {function_name}: {e}", exc_info=True)
            #         if fix_dynamically:
            #             logging.info(f"Attempting to fix method {function_name} dynamically.")
            #             corrected_code = llm_generator.fix_runtime_error(
            #                 code_manager.load_code(),
            #                 error_message=str(e)
            #             )
            #             test_code = llm_generator.generate_test_logic(
            #                 corrected_code,
            #                 prompt="test_method_prompt.txt"
            #             )
            #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
            #             hot_swap_executor.execute_workflow(
            #                 function_name=function_name,
            #                 test_code=cleaned_test_code,
            #                 error_message=str(e),
            #             )
            
            #             importlib.invalidate_caches()
            #             dynamic_method = code_manager.load_function(function_name)
            #             dynamic_method = dynamic_method.__get__(self, type(self))
            #             result = dynamic_method(*args, **kwargs)
            #             logging.info(f"Fixed method executed successfully with result: {result}")
            #             return result
            #         else:
            #             raise e
            
            @wraps(func)
            def method_wrapper(self, *args, **kwargs):
                function_name = func.__name__
                class_name = self.__class__.__name__
                default_dynamic_file = f"d_{class_name}_{function_name}.py"
                dynamic_file_path = dynamic_file or default_dynamic_file
            
                # Initialize components
                code_manager = DynamicCodeManager(dynamic_file_path)
                llm_generator = LLMCodeGenerator(model=model)
                try:
                    class_code = inspect.getsource(self.__class__)
                except OSError:
                    logging.warning(f"Source code for class {class_name} is not available. Using repr as fallback.")
                    class_code = repr(self.__class__)
            
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
                        method_header=inspect.getsource(func),
                        extra_info=extra_info
                    )
                    cleaned_code = LLMResponseCleaner.clean_response(method_code)
                    logging.info(f"Generated method code:\n{cleaned_code}")
                    code_manager.save_code(cleaned_code)
            
                    # Determine the test prompt dynamically
                    test_prompt = "test_method_prompt.txt"
                    test_code = llm_generator.generate_test_logic(
                        cleaned_code,
                        prompt=test_prompt
                    )
                    cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
                    hot_swap_executor.execute_workflow(
                        function_name=function_name,
                        test_code=cleaned_test_code,
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
                        logging.info(f"Attempting to fix method {function_name} dynamically.")
                        corrected_code = llm_generator.fix_runtime_error(
                            code_manager.load_code(),
                            error_message=str(e)
                        )
                        test_code = llm_generator.generate_test_logic(
                            corrected_code,
                            prompt="test_method_prompt.txt"
                        )
                        cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
            
                        hot_swap_executor.execute_workflow(
                            function_name=function_name,
                            test_code=cleaned_test_code,
                            error_message=str(e),
                        )
            
                        importlib.invalidate_caches()
                        dynamic_method = code_manager.load_function(function_name)
                        dynamic_method = dynamic_method.__get__(self, type(self))
                        result = dynamic_method(*args, **kwargs)
                        logging.info(f"Fixed method executed successfully with result: {result}")
                        return result
                    else:
                        raise e


            return method_wrapper

        else:
            # Wrapper for functions
            @wraps(func)
            def function_wrapper(*args, **kwargs):
                function_name = func.__name__
                default_dynamic_file = f"d_{function_name}.py"
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
                    logging.info(f"Generated function code:\n{cleaned_code}")
                    code_manager.save_code(cleaned_code)

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
                        logging.info(f"Attempting to fix function {function_name} dynamically.")
                        corrected_code = llm_generator.fix_runtime_error(
                            code_manager.load_code(),
                            error_message=str(e)
                        )
                        test_prompt = "test_function_prompt.txt"
                        test_code = llm_generator.generate_test_logic(
                            corrected_code,
                            prompt=test_prompt
                        )
                        cleaned_test_code = LLMResponseCleaner.clean_response(test_code)

                        hot_swap_executor.execute_workflow(
                            function_name=function_name,
                            test_code=cleaned_test_code,
                            error_message=str(e),
                        )

                        importlib.invalidate_caches()
                        dynamic_function = code_manager.load_function(function_name)
                        result = dynamic_function(*args, **kwargs)
                        logging.info(f"Fixed function executed successfully with result: {result}")
                        return result
                    else:
                        raise e
            return function_wrapper

    return decorator


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
#         # Identify if the decorated entity is a method or function
#         is_method = "." in func.__qualname__

#         if is_method:
#             logging.info(f"Detected method: {func.__qualname__}")

#             # Extract class name and module
#             function_name = func.__name__
#             class_name = func.__qualname__.split(".")[0]
#             module = sys.modules[func.__module__]

#             # Retrieve the full class code
#             try:
#                 class_code = _extract_class_code(module, class_name)
#                 logging.info(f"Extracted class code for {class_name}:\n{class_code}")
#             except Exception as e:
#                 raise ValueError(f"Failed to extract class code for {class_name}: {e}")

#             # Generate dynamic file path
#             default_dynamic_file = f"d_{class_name}_{function_name}.py"
#         else:
#             logging.info(f"Detected standalone function: {func.__qualname__}")
#             function_name = func.__name__
#             default_dynamic_file = f"d_{function_name}.py"

#         # Set dynamic file paths
#         dynamic_file_path = dynamic_file or default_dynamic_file
#         default_test_file = f"d_{function_name}_test.py"
#         dynamic_test_file_path = dynamic_test_file or default_test_file

#         # Initialize components
#         code_manager = DynamicCodeManager(dynamic_file_path)
#         llm_generator = LLMCodeGenerator(model=model)
#         hot_swap_executor = HotSwapExecutor(
#             code_manager=code_manager,
#             llm_generator=llm_generator,
#             retries=error_trials,
#             is_method=is_method,
#             class_code=class_code if is_method else None
#         )
        
        
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             test_prompt = "test_method_prompt.txt" if is_method else "test_function_prompt.txt"
        
#             if not code_manager.code_exists():
#                 logging.info(f"Generating initial code for {function_name}...")
#                 function_code = llm_generator.initial_code_generation(
#                     function_header=inspect.getsource(func),
#                     docstring=func.__doc__,
#                     extra_info=extra_info,
#                 )
#                 cleaned_code = LLMResponseCleaner.clean_response(function_code)
#                 logging.info(f"Generated function code:\n{cleaned_code}")
#                 code_manager.save_code(cleaned_code)
        
#                 test_code = llm_generator.generate_test_logic(cleaned_code, prompt=test_prompt)
#                 cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
#                 hot_swap_executor.execute_workflow(
#                     function_name=function_name,
#                     test_code=cleaned_test_code,
#                 )
        
#             importlib.invalidate_caches()
#             dynamic_func = code_manager.load_function(function_name)
        
#             # Bind the dynamic function to self if it's a method
#             if is_method:
#                 dynamic_func = dynamic_func.__get__(args[0], type(args[0]))
#                 args = args[1:]  # Exclude self from args
        
#             logging.info(f"Dynamic function loaded: {dynamic_func}")
#             logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")
        
#             try:
#                 result = dynamic_func(*args, **kwargs)
#                 logging.info(f"Dynamic function executed successfully with result: {result}")
#                 return result
#             except Exception as e:
#                 logging.error(f"Runtime error in {function_name}: {e}", exc_info=True)
#                 if fix_dynamically:
#                     logging.info(f"Attempting to fix {function_name} dynamically.")
#                     corrected_code = llm_generator.fix_runtime_error(
#                         code_manager.load_code(),
#                         error_message=str(e)
#                     )
#                     test_code = llm_generator.generate_test_logic(corrected_code, prompt=test_prompt)
#                     cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=cleaned_test_code,
#                         error_message=str(e),
#                     )
        
#                     importlib.invalidate_caches()
#                     dynamic_func = code_manager.load_function(function_name)
        
#                     if is_method:
#                         dynamic_func = dynamic_func.__get__(args[0], type(args[0]))
#                         args = args[1:]
        
#                     logging.info(f"Reloaded dynamic function: {dynamic_func}")
#                     result = dynamic_func(*args, **kwargs)
#                     logging.info(f"Fixed function executed successfully with result: {result}")
#                     return result
#                 else:
#                     raise e
              


#         # @functools.wraps(func)
#         # def wrapper(*args, **kwargs):
#         #     test_prompt = "test_method_prompt.txt" if is_method else "test_function_prompt.txt"
        
#         #     if not code_manager.code_exists():
#         #         logging.info(f"Generating initial code for {function_name}...")
#         #         function_code = llm_generator.initial_code_generation(
#         #             function_header=inspect.getsource(func),
#         #             docstring=func.__doc__,
#         #             extra_info=extra_info,
#         #         )
#         #         cleaned_code = LLMResponseCleaner.clean_response(function_code)
#         #         logging.info(f"Generated function code:\n{cleaned_code}")
#         #         code_manager.save_code(cleaned_code)
        
#         #         test_code = llm_generator.generate_test_logic(cleaned_code, prompt=test_prompt)
#         #         cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
#         #         hot_swap_executor.execute_workflow(
#         #             function_name=function_name,
#         #             test_code=cleaned_test_code,
#         #         )
        
#         #     importlib.invalidate_caches()
#         #     dynamic_func = code_manager.load_function(function_name)
        
#         #     # Bind the dynamic function to self if it's a method
#         #     if is_method:
#         #         dynamic_func = dynamic_func.__get__(args[0], type(args[0]))
        
#         #     logging.info(f"Dynamic function loaded: {dynamic_func}")
#         #     logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")
        
#         #     try:
#         #         result = dynamic_func(*args, **kwargs)
#         #         logging.info(f"Dynamic function executed successfully with result: {result}")
#         #         return result
#         #     except Exception as e:
#         #         logging.error(f"Runtime error in {function_name}: {e}", exc_info=True)
#         #         if fix_dynamically:
#         #             logging.info(f"Attempting to fix {function_name} dynamically.")
#         #             corrected_code = llm_generator.fix_runtime_error(
#         #                 code_manager.load_code(),
#         #                 error_message=str(e)
#         #             )
#         #             test_code = llm_generator.generate_test_logic(corrected_code, prompt=test_prompt)
#         #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
#         #             hot_swap_executor.execute_workflow(
#         #                 function_name=function_name,
#         #                 test_code=cleaned_test_code,
#         #                 error_message=str(e),
#         #             )
        
#         #             importlib.invalidate_caches()
#         #             dynamic_func = code_manager.load_function(function_name)
        
#         #             if is_method:
#         #                 dynamic_func = dynamic_func.__get__(args[0], type(args[0]))
        
#         #             logging.info(f"Reloaded dynamic function: {dynamic_func}")
#         #             result = dynamic_func(*args, **kwargs)
#         #             logging.info(f"Fixed function executed successfully with result: {result}")
#         #             return result
#         #         else:
#         #             raise e



#         # @functools.wraps(func)
#         # def wrapper(*args, **kwargs):
#         #     # Always define test_prompt
#         #     test_prompt = "test_method_prompt.txt" if is_method else "test_function_prompt.txt"
        
#         #     if not code_manager.code_exists():
#         #         logging.info(f"Generating initial code for {function_name}...")
        
#         #         # Generate initial code for the function or method
#         #         function_code = llm_generator.initial_code_generation(
#         #             function_header=inspect.getsource(func),
#         #             docstring=func.__doc__,
#         #             extra_info=extra_info,
#         #         )
#         #         cleaned_code = LLMResponseCleaner.clean_response(function_code)
#         #         logging.info(f"Generated function code:\n{cleaned_code}")
#         #         code_manager.save_code(cleaned_code)
        
#         #         # Generate test logic for the initial code
#         #         test_code = llm_generator.generate_test_logic(
#         #             cleaned_code,
#         #             prompt=test_prompt
#         #         )
#         #         cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
#         #         # Save and test the initial code
#         #         hot_swap_executor.execute_workflow(
#         #             function_name=function_name,
#         #             test_code=cleaned_test_code,
#         #         )
        
#         #     # Dynamically load the function
#         #     importlib.invalidate_caches()
#         #     dynamic_func = code_manager.load_function(function_name)
#         #     logging.info(f"Dynamic function loaded: {dynamic_func}")
#         #     logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")
        
#         #     try:
#         #         result = dynamic_func(*args, **kwargs)
#         #         logging.info(f"Dynamic function executed successfully with result: {result}")
#         #         return result
#         #     except Exception as e:
#         #         logging.error(f"Runtime error in {function_name}: {e}", exc_info=True)
#         #         if fix_dynamically:
#         #             logging.info(f"Attempting to fix {function_name} dynamically.")
#         #             corrected_code = llm_generator.fix_runtime_error(
#         #                 code_manager.load_code(),
#         #                 error_message=str(e)
#         #             )
#         #             test_code = llm_generator.generate_test_logic(
#         #                 corrected_code,
#         #                 prompt=test_prompt  # Now test_prompt is always defined
#         #             )
#         #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
#         #             hot_swap_executor.execute_workflow(
#         #                 function_name=function_name,
#         #                 test_code=cleaned_test_code,
#         #                 error_message=str(e),
#         #             )
        
#         #             importlib.invalidate_caches()
#         #             dynamic_func = code_manager.load_function(function_name)
#         #             logging.info(f"Reloaded dynamic function: {dynamic_func}")
#         #             result = dynamic_func(*args, **kwargs)
#         #             logging.info(f"Fixed function executed successfully with result: {result}")
#         #             return result
#         #         else:
#         #             raise e


#         # @functools.wraps(func)
#         # def wrapper(*args, **kwargs):
#         #     if not code_manager.code_exists():
#         #         logging.info(f"Generating initial code for {function_name}...")

#         #         # Generate initial code for the function or method
#         #         function_code = llm_generator.initial_code_generation(
#         #             function_header=inspect.getsource(func),
#         #             docstring=func.__doc__,
#         #             extra_info=extra_info,
#         #         )
#         #         cleaned_code = LLMResponseCleaner.clean_response(function_code)
#         #         logging.info(f"Generated function code:\n{cleaned_code}")
#         #         code_manager.save_code(cleaned_code)

#         #         # Determine the test prompt dynamically
#         #         test_prompt = "test_method_prompt.txt" if is_method else "test_function_prompt.txt"

#         #         # Generate test logic for the initial code
#         #         test_code = llm_generator.generate_test_logic(
#         #             cleaned_code,
#         #             prompt=test_prompt
#         #         )
#         #         cleaned_test_code = LLMResponseCleaner.clean_response(test_code)

#         #         # Save and test the initial code
#         #         hot_swap_executor.execute_workflow(
#         #             function_name=function_name,
#         #             test_code=cleaned_test_code,
#         #         )

#         #     # Dynamically load the function
#         #     importlib.invalidate_caches()
#         #     dynamic_func = code_manager.load_function(function_name)
#         #     logging.info(f"Dynamic function loaded: {dynamic_func}")
#         #     logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")

#         #     try:
#         #         result = dynamic_func(*args, **kwargs)
#         #         logging.info(f"Dynamic function executed successfully with result: {result}")
#         #         return result
#         #     except Exception as e:
#         #         logging.error(f"Runtime error in {function_name}: {e}", exc_info=True)
#         #         if fix_dynamically:
#         #             logging.info(f"Attempting to fix {function_name} dynamically.")
#         #             corrected_code = llm_generator.fix_runtime_error(
#         #                 code_manager.load_code(),
#         #                 error_message=str(e)
#         #             )
#         #             test_code = llm_generator.generate_test_logic(
#         #                 corrected_code,
#         #                 prompt=test_prompt
#         #             )
#         #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)

#         #             hot_swap_executor.execute_workflow(
#         #                 function_name=function_name,
#         #                 test_code=cleaned_test_code,
#         #                 error_message=str(e),
#         #             )

#         #             importlib.invalidate_caches()
#         #             dynamic_func = code_manager.load_function(function_name)
#         #             logging.info(f"Reloaded dynamic function: {dynamic_func}")
#         #             result = dynamic_func(*args, **kwargs)
#         #             logging.info(f"Fixed function executed successfully with result: {result}")
#         #             return result
#         #         else:
#         #             raise e

#         return wrapper

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
#     """
#     Decorator for dynamically generating, managing, and hot-swapping Python functions or methods.

#     Args:
#         model (str): LLM model for code generation.
#         prompt (str or Path): Custom prompt for initial code generation.
#         dynamic_file (str or Path): Path to save dynamic code. Defaults to `d_<function_name>.py`.
#         dynamic_test_file (str or Path): Path to save the test file.
#         extra_info (str): Additional info for the LLM (e.g., input/output examples).
#         fix_dynamically (bool): Automatically fix runtime errors using the LLM.
#         error_trials (int): Maximum retries for fixing runtime errors.
#         error_model (str): LLM model for error correction.
#         error_prompt (str or Path): Custom prompt for error correction.
#         hs_condition (str): Hot-swapping condition to trigger improvements.
#         hs_model (str): LLM model for hot-swapping improvements.
#         hs_prompt (str or Path): Custom prompt for hot-swapping improvements.
#         execution_context (dict): Context describing runtime usage patterns or bottlenecks.
#         keep_ok_version (bool): Roll back to last valid version if new code fails.
#     """
#     def decorator(func):
#         # Identify if the decorated entity is a method or function
#         is_method = "." in func.__qualname__

#         if is_method:
#             logging.info(f"Detected method: {func.__qualname__}")
        
#             # Extract class name and module
#             function_name = func.__name__
#             class_name = func.__qualname__.split(".")[0]
#             module = sys.modules[func.__module__]
        
#             # Retrieve the full class code
#             try:
#                 class_code = _extract_class_code(module, class_name)
#                 logging.info(f"Extracted class code for {class_name}:\n{class_code}")
#             except Exception as e:
#                 raise ValueError(f"Failed to extract class code for {class_name}: {e}")
        
#             # Generate dynamic file path
#             default_dynamic_file = f"d_{class_name}_{function_name}.py"

#         else:
#             logging.info(f"Detected standalone function: {func.__qualname__}")
#             # Generate dynamic file path for standalone functions
#             function_name = func.__name__
#             default_dynamic_file = f"d_{function_name}.py"

#         # Set dynamic file paths
#         dynamic_file_path = dynamic_file or default_dynamic_file
#         default_test_file = f"d_{function_name}_test.py"
#         dynamic_test_file_path = dynamic_test_file or default_test_file

#         # Initialize components
#         code_manager = DynamicCodeManager(dynamic_file_path)
#         llm_generator = LLMCodeGenerator(model=model)
#         hot_swap_executor = HotSwapExecutor(code_manager, llm_generator, retries=error_trials)

#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             # Check if the function is already in the dynamic file
#             if not code_manager.code_exists():
#                 logging.info(f"Generating initial code for {function_name}...")
                
#                 # Generate initial code for the function or method
#                 function_code = llm_generator.initial_code_generation(
#                     function_header=inspect.getsource(func),
#                     docstring=func.__doc__,
#                     extra_info=extra_info,
#                 )
#                 cleaned_code = LLMResponseCleaner.clean_response(function_code)
#                 logging.info(f"Generated function code:\n{cleaned_code}")
#                 code_manager.save_code(cleaned_code)
        
#                 # Determine the test prompt dynamically
#                 test_prompt = "test_method_prompt.txt" if is_method else "test_function_prompt.txt"
                
#                 # Generate test logic for the initial code
#                 test_code = llm_generator.generate_test_logic(
#                     cleaned_code,
#                     prompt=test_prompt
#                 )
#                 cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
#                 # Save and test the initial code
#                 hot_swap_executor.execute_workflow(
#                     function_name=function_name,
#                     test_code=cleaned_test_code,
#                 )
        
#             # Dynamically load the function
#             importlib.invalidate_caches()
#             dynamic_func = code_manager.load_function(function_name)
#             logging.info(f"Dynamic function loaded: {dynamic_func}")
#             logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")
        
#             # Handle runtime errors dynamically
#             try:
#                 result = dynamic_func(*args, **kwargs)
#                 logging.info(f"Dynamic function executed successfully with result: {result}")
#                 return result
#             except Exception as e:
#                 logging.error(f"Runtime error in {function_name}: {e}", exc_info=True)
#                 if fix_dynamically:
#                     logging.info(f"Attempting to fix {function_name} dynamically.")
#                     corrected_code = llm_generator.fix_runtime_error(
#                         code_manager.load_code(),
#                         error_message=str(e)
#                     )
#                     test_code = llm_generator.generate_test_logic(
#                         corrected_code,
#                         prompt=test_prompt
#                     )
#                     cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=cleaned_test_code,
#                         error_message=str(e),
#                     )
        
#                     # Reload and execute fixed function
#                     importlib.invalidate_caches()
#                     dynamic_func = code_manager.load_function(function_name)
#                     logging.info(f"Reloaded dynamic function: {dynamic_func}")
#                     result = dynamic_func(*args, **kwargs)
#                     logging.info(f"Fixed function executed successfully with result: {result}")
#                     return result
#                 else:
#                     raise e


#         # @functools.wraps(func)
#         # def wrapper(*args, **kwargs):
#         #     # Common logic for both functions and methods
#         #     if not code_manager.code_exists():
#         #         logging.info(f"Generating initial code for {function_name}...")
#         #         function_code = llm_generator.initial_code_generation(
#         #             function_header=inspect.getsource(func),
#         #             docstring=func.__doc__,
#         #             extra_info=extra_info,
#         #         )
#         #         cleaned_code = LLMResponseCleaner.clean_response(function_code)
#         #         logging.info(f"Generated function code:\n{cleaned_code}")
#         #         code_manager.save_code(cleaned_code)

#         #     # Dynamically load the function
#         #     importlib.invalidate_caches()
#         #     dynamic_func = code_manager.load_function(function_name)
#         #     logging.info(f"Dynamic function loaded: {dynamic_func}")
#         #     logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")

#         #     # Handle runtime errors dynamically
#         #     try:
#         #         result = dynamic_func(*args, **kwargs)
#         #         logging.info(f"Dynamic function executed successfully with result: {result}")
#         #         return result
#         #     except Exception as e:
#         #         logging.error(f"Runtime error in {function_name}: {e}", exc_info=True)
#         #         if fix_dynamically:
#         #             logging.info(f"Attempting to fix {function_name} dynamically.")
#         #             corrected_code = llm_generator.fix_runtime_error(
#         #                 code_manager.load_code(),
#         #                 error_message=str(e)
#         #             )
#         #             cleaned_test_code = LLMResponseCleaner.clean_response(
#         #                 llm_generator.generate_test_logic(corrected_code, prompt="error_correction_prompt.txt")
#         #             )
#         #             hot_swap_executor.execute_workflow(
#         #                 function_name=function_name,
#         #                 test_code=cleaned_test_code,
#         #                 error_message=str(e),
#         #             )

#         #             # Reload and execute fixed function
#         #             importlib.invalidate_caches()
#         #             dynamic_func = code_manager.load_function(function_name)
#         #             logging.info(f"Reloaded dynamic function: {dynamic_func}")
#         #             result = dynamic_func(*args, **kwargs)
#         #             logging.info(f"Fixed function executed successfully with result: {result}")
#         #             return result
#         #         else:
#         #             raise e

#         return wrapper

#     return decorator



# @elapsedTimeDecorator()
# @dynamic_function(
#     model="gpt-4o",
#     # prompt="custom_prompt.txt",
#     hs_condition="len(numbers) > 1000",
#     execution_context={"frequent_inputs": [[], [1, 2, 3]]},
#     keep_ok_version=True
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

class Inventory:
    def __init__(self):
        """
        Initializes the inventory with an empty stock dictionary.
        """
        self.stock = {}

    @dynamic_function(
        # model="gpt-4o",
        # dynamic_file="dynamic_inventory.py",
        # error_trials=5,
        # extra_info="Manages inventory stock operations for a retail system."
    )
    def update_stock(self, product, quantity):
        """
        Updates the stock for a product.

        Args:
            product (str): The name of the product.
            quantity (int): The quantity to add (positive) or remove (negative).

        Raises:
            ValueError: If quantity is negative and results in stock below zero.
        """
        pass

# Example Usage
inventory = Inventory()

# Add new product
inventory.update_stock("apple", 50)

# # Reduce stock
# inventory.update_stock("apple", -20)

# # Attempt invalid operation (should trigger dynamic fixing)
# inventory.update_stock("apple", -40)


