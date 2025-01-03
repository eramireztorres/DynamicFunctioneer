import functools
import logging
import inspect
from dynamic_code_manager import DynamicCodeManager
from llm_code_generator import LLMCodeGenerator
from hot_swap_executor import HotSwapExecutor
from llm_response_cleaner import LLMResponseCleaner
import importlib

from etimedecorator import elapsedTimeDecorator

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
#         # Resolve dynamic file and test file paths
#         function_name = func.__name__
#         default_dynamic_file = f"d_{function_name}.py"
#         default_test_file = f"d_{function_name}_test.py"
#         dynamic_file_path = dynamic_file or default_dynamic_file
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
#                 function_code = llm_generator.initial_code_generation(
#                     function_header=inspect.getsource(func),
#                     docstring=func.__doc__,
#                     extra_info=extra_info,
#                 )
#                 cleaned_code = LLMResponseCleaner.clean_response(function_code)
                
#                 print(f'function_code: \n {function_code} \n')
                
#                 print(f'cleaned_code: \n {cleaned_code} \n')
                
#                 code_manager.save_code(cleaned_code)

#             # Dynamically load the function
#             dynamic_func = code_manager.load_function(function_name)

#             # Handle runtime errors dynamically
#             try:
#                 # Execute the function
#                 result = dynamic_func(*args, **kwargs)

#                 # Check hot-swapping condition
#                 if hs_condition and eval(hs_condition, {}, kwargs):
#                     logging.info(f"Hot-swapping condition met for {function_name}.")
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=inspect.getsource(func),
#                         condition_met=True,
#                         error_message=None,
#                     )

#                 return result

#             except Exception as e:
#                 logging.error(f"Runtime error in {function_name}: {e}")
#                 if fix_dynamically:
#                     logging.info(f"Attempting to fix {function_name} dynamically.")
#                     hot_swap_executor.execute_workflow(
#                         function_name=function_name,
#                         test_code=inspect.getsource(func),
#                         error_message=str(e),
#                     )
#                 else:
#                     raise e

#         return wrapper

#     return decorator

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
    """
    Decorator for dynamically generating, managing, and hot-swapping Python functions or methods.

    Args:
        model (str): LLM model for code generation.
        prompt (str or Path): Custom prompt for initial code generation.
        dynamic_file (str or Path): Path to save dynamic code. Defaults to `d_<function_name>.py`.
        dynamic_test_file (str or Path): Path to save the test file.
        extra_info (str): Additional info for the LLM (e.g., input/output examples).
        fix_dynamically (bool): Automatically fix runtime errors using the LLM.
        error_trials (int): Maximum retries for fixing runtime errors.
        error_model (str): LLM model for error correction.
        error_prompt (str or Path): Custom prompt for error correction.
        hs_condition (str): Hot-swapping condition to trigger improvements.
        hs_model (str): LLM model for hot-swapping improvements.
        hs_prompt (str or Path): Custom prompt for hot-swapping improvements.
        execution_context (dict): Context describing runtime usage patterns or bottlenecks.
        keep_ok_version (bool): Roll back to last valid version if new code fails.
    """
    def decorator(func):
        # Resolve dynamic file and test file paths
        function_name = func.__name__
        default_dynamic_file = f"d_{function_name}.py"
        default_test_file = f"d_{function_name}_test.py"
        dynamic_file_path = dynamic_file or default_dynamic_file
        dynamic_test_file_path = dynamic_test_file or default_test_file

        # Initialize components
        code_manager = DynamicCodeManager(dynamic_file_path)
        llm_generator = LLMCodeGenerator(model=model)
        hot_swap_executor = HotSwapExecutor(code_manager, llm_generator, retries=error_trials)


        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if the function is already in the dynamic file
            if not code_manager.code_exists():
                logging.info(f"Generating initial code for {function_name}...")
                function_code = llm_generator.initial_code_generation(
                    function_header=inspect.getsource(func),
                    docstring=func.__doc__,
                    extra_info=extra_info,
                )
                cleaned_code = LLMResponseCleaner.clean_response(function_code)
                logging.info(f"Generated function code:\n{cleaned_code}")
                code_manager.save_code(cleaned_code)
        
            # Dynamically load the function
            importlib.invalidate_caches()
            dynamic_func = code_manager.load_function(function_name)
            logging.info(f"Dynamic function loaded: {dynamic_func}")
            logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")
        
            # Handle runtime errors dynamically
            try:
                # Create evaluation context for hs_condition
                context = kwargs.copy()  # Start with keyword arguments
                if args:  # Add positional arguments if available
                    arg_names = inspect.signature(func).parameters.keys()
                    context.update(dict(zip(arg_names, args)))
        
                # Execute the dynamically loaded function
                result = dynamic_func(*args, **kwargs)
                logging.info(f"Dynamic function executed successfully with result: {result}")
        
                # Check hot-swapping condition
                if hs_condition and eval(hs_condition, {}, context):
                    logging.info(f"Hot-swapping condition met for {function_name}.")
                    corrected_code = llm_generator.fix_runtime_error(
                        code_manager.load_code(),
                        error_message="Hot-swapping triggered condition met"
                    )
                    test_code = llm_generator.generate_test_logic(
                        corrected_code,
                        prompt="error_correction_prompt.txt"
                    )
                    cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
                    hot_swap_executor.execute_workflow(
                        function_name=function_name,
                        test_code=cleaned_test_code,
                        condition_met=True,
                        error_message=None,
                    )
        
                return result
        
            except Exception as e:
                logging.error(f"Runtime error in {function_name}: {e}", exc_info=True)
                if fix_dynamically:
                    logging.info(f"Attempting to fix {function_name} dynamically.")
                    corrected_code = llm_generator.fix_runtime_error(
                        code_manager.load_code(),
                        error_message=str(e)
                    )
                    test_code = llm_generator.generate_test_logic(
                        corrected_code,
                        prompt="error_correction_prompt.txt"
                    )
                    cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
                    hot_swap_executor.execute_workflow(
                        function_name=function_name,
                        test_code=cleaned_test_code,
                        error_message=str(e),
                    )
        
                    # Reload the dynamically fixed function
                    importlib.invalidate_caches()
                    dynamic_func = code_manager.load_function(function_name)
                    logging.info(f"Reloaded dynamic_func: {dynamic_func}")
        
                    # Execute the fixed function
                    result = dynamic_func(*args, **kwargs)
                    logging.info(f"Fixed function executed successfully with result: {result}")
                    return result
                else:
                    raise e


        # @functools.wraps(func)
        # def wrapper(*args, **kwargs):
        #     # Check if the function is already in the dynamic file
        #     if not code_manager.code_exists():
        #         logging.info(f"Generating initial code for {function_name}...")
        #         function_code = llm_generator.initial_code_generation(
        #             function_header=inspect.getsource(func),
        #             docstring=func.__doc__,
        #             extra_info=extra_info,
        #         )
        #         cleaned_code = LLMResponseCleaner.clean_response(function_code)
        #         logging.info(f"Generated function code:\n{cleaned_code}")
        #         code_manager.save_code(cleaned_code)
        
        #     # Dynamically load the function
        #     importlib.invalidate_caches()
        #     dynamic_func = code_manager.load_function(function_name)
        #     logging.info(f"Dynamic function loaded: {dynamic_func}")
        #     logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")
        
        #     # Handle runtime errors dynamically
        #     try:
        #         # Execute the dynamically loaded function
        #         logging.info(f"Executing dynamic_func: {dynamic_func}")
        #         result = dynamic_func(*args, **kwargs)
        #         logging.info(f"Dynamic function executed successfully with result: {result}")
        
        #         # Check hot-swapping condition
        #         if hs_condition and eval(hs_condition, {}, kwargs):
        #             logging.info(f"Hot-swapping condition met for {function_name}.")
        #             corrected_code = llm_generator.fix_runtime_error(
        #                 code_manager.load_code(),
        #                 error_message="Hot-swapping triggered condition met"
        #             )
        #             test_code = llm_generator.generate_test_logic(
        #                 corrected_code,
        #                 prompt="error_correction_prompt.txt"
        #             )
        #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
        #             hot_swap_executor.execute_workflow(
        #                 function_name=function_name,
        #                 test_code=cleaned_test_code,
        #                 condition_met=True,
        #                 error_message=None,
        #             )
        
        #         return result
        
        #     except Exception as e:
        #         logging.error(f"Runtime error in {function_name}: {e}", exc_info=True)
        #         if fix_dynamically:
        #             logging.info(f"Attempting to fix {function_name} dynamically.")
        #             corrected_code = llm_generator.fix_runtime_error(
        #                 code_manager.load_code(),
        #                 error_message=str(e)
        #             )
        #             test_code = llm_generator.generate_test_logic(
        #                 corrected_code,
        #                 prompt="error_correction_prompt.txt"
        #             )
        #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
        #             hot_swap_executor.execute_workflow(
        #                 function_name=function_name,
        #                 test_code=cleaned_test_code,
        #                 error_message=str(e),
        #             )
        
        #             # Reload the dynamically fixed function
        #             importlib.invalidate_caches()
        #             dynamic_func = code_manager.load_function(function_name)
        #             logging.info(f"Reloaded dynamic_func: {dynamic_func}")
        
        #             # Execute the fixed function
        #             result = dynamic_func(*args, **kwargs)
        #             logging.info(f"Fixed function executed successfully with result: {result}")
        #             return result
        #         else:
        #             raise e



        # @functools.wraps(func)
        # def wrapper(*args, **kwargs):
        #     # Check if the function is already in the dynamic file
        #     if not code_manager.code_exists():
        #         logging.info(f"Generating initial code for {function_name}...")
        #         function_code = llm_generator.initial_code_generation(
        #             function_header=inspect.getsource(func),
        #             docstring=func.__doc__,
        #             extra_info=extra_info,
        #         )
        #         cleaned_code = LLMResponseCleaner.clean_response(function_code)
        #         logging.info(f"Generated function code:\n{cleaned_code}")
        #         code_manager.save_code(cleaned_code)
        
        #     # Dynamically load the function
        #     importlib.invalidate_caches()
        #     dynamic_func = code_manager.load_function(function_name)
        #     logging.info(f"Dynamic function loaded: {dynamic_func}")
        
        #     # Log arguments being passed to the dynamic function
        #     logging.info(f"Arguments passed to {function_name}: args={args}, kwargs={kwargs}")
        
        #     # Handle runtime errors dynamically
        #     try:
        #         # Execute the dynamically loaded function
        #         result = dynamic_func(*args, **kwargs)
        #         logging.info(f"Dynamic function executed successfully with result: {result}")
        
        #         # Check hot-swapping condition
        #         if hs_condition and eval(hs_condition, {}, kwargs):
        #             logging.info(f"Hot-swapping condition met for {function_name}.")
        #             corrected_code = llm_generator.fix_runtime_error(
        #                 code_manager.load_code(),
        #                 error_message="Hot-swapping triggered condition met"
        #             )
        #             test_code = llm_generator.generate_test_logic(
        #                 corrected_code,
        #                 prompt="error_correction_prompt.txt"
        #             )
        #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
        #             hot_swap_executor.execute_workflow(
        #                 function_name=function_name,
        #                 test_code=cleaned_test_code,
        #                 condition_met=True,
        #                 error_message=None,
        #             )
        
        #         return result
        
        #     except Exception as e:
        #         logging.error(f"Runtime error in {function_name}: {e}")
        #         if fix_dynamically:
        #             logging.info(f"Attempting to fix {function_name} dynamically.")
        #             corrected_code = llm_generator.fix_runtime_error(
        #                 code_manager.load_code(),
        #                 error_message=str(e)
        #             )
        #             test_code = llm_generator.generate_test_logic(
        #                 corrected_code,
        #                 prompt="error_correction_prompt.txt"
        #             )
        #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
        #             hot_swap_executor.execute_workflow(
        #                 function_name=function_name,
        #                 test_code=cleaned_test_code,
        #                 error_message=str(e),
        #             )
        
        #             # Reload the dynamically fixed function
        #             importlib.invalidate_caches()
        #             dynamic_func = code_manager.load_function(function_name)
        #             logging.info(f"Reloaded dynamic function: {dynamic_func}")
        
        #             # Execute the fixed function
        #             result = dynamic_func(*args, **kwargs)
        #             logging.info(f"Fixed function executed successfully with result: {result}")
        #             return result
        #         else:
        #             raise e



        # @functools.wraps(func)
        # def wrapper(*args, **kwargs):
        #     # Check if the function is already in the dynamic file
        #     if not code_manager.code_exists():
        #         logging.info(f"Generating initial code for {function_name}...")
        #         function_code = llm_generator.initial_code_generation(
        #             function_header=inspect.getsource(func),
        #             docstring=func.__doc__,
        #             extra_info=extra_info,
        #         )
        #         cleaned_code = LLMResponseCleaner.clean_response(function_code)
        #         logging.info(f"Generated function code:\n{cleaned_code}")
        #         code_manager.save_code(cleaned_code)
        
        #     # Dynamically load the function
        #     importlib.invalidate_caches()
        #     dynamic_func = code_manager.load_function(function_name)
        #     logging.info(f"Dynamic function loaded: {dynamic_func}")
        
        #     # Handle runtime errors dynamically
        #     try:
        #         # Execute the dynamically loaded function
        #         result = dynamic_func(*args, **kwargs)
        #         logging.info(f"Dynamic function executed successfully with result: {result}")
        
        #         # Check hot-swapping condition
        #         if hs_condition and eval(hs_condition, {}, kwargs):
        #             logging.info(f"Hot-swapping condition met for {function_name}.")
        #             corrected_code = llm_generator.fix_runtime_error(
        #                 code_manager.load_code(),
        #                 error_message="Hot-swapping triggered condition met"
        #             )
        #             test_code = llm_generator.generate_test_logic(
        #                 corrected_code,
        #                 prompt="error_correction_prompt.txt"
        #             )
        #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
        #             hot_swap_executor.execute_workflow(
        #                 function_name=function_name,
        #                 test_code=cleaned_test_code,
        #                 condition_met=True,
        #                 error_message=None,
        #             )
        
        #         return result
        
        #     except Exception as e:
        #         logging.error(f"Runtime error in {function_name}: {e}")
        #         if fix_dynamically:
        #             logging.info(f"Attempting to fix {function_name} dynamically.")
        #             corrected_code = llm_generator.fix_runtime_error(
        #                 code_manager.load_code(),
        #                 error_message=str(e)
        #             )
        #             test_code = llm_generator.generate_test_logic(
        #                 corrected_code,
        #                 prompt="error_correction_prompt.txt"
        #             )
        #             cleaned_test_code = LLMResponseCleaner.clean_response(test_code)
        
        #             hot_swap_executor.execute_workflow(
        #                 function_name=function_name,
        #                 test_code=cleaned_test_code,
        #                 error_message=str(e),
        #             )
        
        #             # Reload the dynamically fixed function
        #             importlib.invalidate_caches()
        #             dynamic_func = code_manager.load_function(function_name)
        #             logging.info(f"Reloaded dynamic function: {dynamic_func}")
        
        #             # Execute the fixed function
        #             result = dynamic_func(*args, **kwargs)
        #             logging.info(f"Fixed function executed successfully with result: {result}")
        #             return result
        #         else:
        #             raise e


        return wrapper

    return decorator


@elapsedTimeDecorator()
@dynamic_function(
    model="gpt-4o",
    # prompt="custom_prompt.txt",
    hs_condition="len(numbers) > 1000",
    execution_context={"frequent_inputs": [[], [1, 2, 3]]},
    keep_ok_version=True
)
def calculate_average(numbers):
    """
    Calculates the average of a list of numbers.

    Args:
        numbers (list of float): A list of numeric values.

    Returns:
        float: The average of the list.
    """
    pass


print(calculate_average([1, 3, 7]))

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