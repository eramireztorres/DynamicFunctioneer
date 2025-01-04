import logging
import time
from pathlib import Path
from prompt_manager import PromptManager
from model_api_factory import ModelAPIFactory

class LLMCodeGenerator:
    """
    Manages interactions with the LLM to generate or improve function/method code.
    """

    def __init__(self, model_provider="openai", model="gpt-4", prompt_dir="prompts"):
        """
        Initialize the LLMCodeGenerator.

        Args:
            model_provider (str): The provider name for the LLM (e.g., "openai", "llama").
            model (str): The specific model to use (e.g., "gpt-4").
            prompt_dir (str): Directory containing prompt templates.
        """
        self.model_client = ModelAPIFactory.get_model_api(provider=model_provider, model=model)
        self.prompt_manager = PromptManager(prompt_dir)
        logging.basicConfig(level=logging.INFO)

    def generate_code(self, prompt_name, placeholders, retries=3, delay=5):
        """
        Generates or improves code using the LLM.

        Args:
            prompt_name (str): The name of the prompt template to use.
            placeholders (dict): A dictionary of placeholders for the prompt.
            retries (int): Number of retry attempts if the LLM call fails.
            delay (int): Delay in seconds between retries.

        Returns:
            str: The generated code from the LLM.

        Raises:
            RuntimeError: If the LLM call fails after the specified retries.
        """
        prompt = self.prompt_manager.load_prompt(prompt_name)
        rendered_prompt = self.prompt_manager.render_prompt(prompt, placeholders)

        for attempt in range(1, retries + 1):
            try:
                logging.info(f"Rendered Prompt Sent to LLM:\n{rendered_prompt}")
                logging.info(f"Sending prompt to LLM (attempt {attempt}/{retries})")
                response = self.model_client.get_response(rendered_prompt)
                if response:
                    logging.info("Code generated successfully.")
                    return response.strip()
            except Exception as e:
                logging.error(f"Error generating code (attempt {attempt}): {e}")
                if attempt < retries:
                    time.sleep(delay)

        raise RuntimeError(f"Failed to generate code after {retries} attempts.")

    def initial_code_generation(self, function_header, docstring, extra_info=""):
        """
        Generates initial code for a function/method.

        Args:
            function_header (str): The header of the function/method.
            docstring (str): The docstring describing the function/method.
            extra_info (str): Additional context for the LLM.

        Returns:
            str: The generated code.
        """
        placeholders = {
            "function_header": function_header,
            "extra_info": extra_info
        }
        return self.generate_code("default_function_prompt.txt", placeholders)

    def method_code_generation(self, class_definition, method_header, extra_info=""):
        """
        Generates initial code for a method.

        Args:
            class_definition (str): The full class definition with the `__init__` method.
            method_header (str): The header of the method to be generated.
            extra_info (str): Additional context for the LLM.

        Returns:
            str: The generated method code.
        """
        placeholders = {
            "class_definition": class_definition,
            "method_header": method_header,
            "extra_info": extra_info
        }
        return self.generate_code("default_method_prompt.txt", placeholders)

    def fix_runtime_error(self, current_code, error_message):
        """
        Requests a fix for a runtime error from the LLM.

        Args:
            current_code (str): The current version of the function/method code.
            error_message (str): The error message encountered during runtime.

        Returns:
            str: The fixed code.
        """
        placeholders = {
            "code": current_code,
            "error_message": error_message
        }
        return self.generate_code("error_correction_prompt.txt", placeholders)

    def hot_swap_improvement(self, current_code, execution_context, hot_swap_condition):
        """
        Requests a performance or functionality improvement for a function/method.

        Args:
            current_code (str): The current version of the function/method code.
            execution_context (dict): Context of the function's usage (e.g., input patterns, frequency).
            hot_swap_condition (str): The condition triggering the hot-swapping.

        Returns:
            str: The improved code.
        """
        placeholders = {
            "code": current_code,
            "execution_context": execution_context,
            "hot_swap_condition": hot_swap_condition
        }
        return self.generate_code("hot_swapping_prompt.txt", placeholders)

    def generate_test_logic(self, corrected_code, prompt="default_test_prompt.txt"):
        """
        Generates test logic for the corrected function using the LLM.

        Args:
            corrected_code (str): The corrected function code.
            prompt (str): The name of the test generation prompt template.

        Returns:
            str: The generated test logic.
        """
        placeholders = {
            "code": corrected_code
        }
        return self.generate_code(prompt, placeholders)


# class LLMCodeGenerator:
#     """
#     Manages interactions with the LLM to generate or improve function/method code.
#     """

#     def __init__(self, model_provider="openai", model="gpt-4", prompt_dir="prompts"):
#         """
#         Initialize the LLMCodeGenerator.

#         Args:
#             model_provider (str): The provider name for the LLM (e.g., "openai", "llama").
#             model (str): The specific model to use (e.g., "gpt-4").
#             prompt_dir (str): Directory containing prompt templates.
#         """
#         self.model_client = ModelAPIFactory.get_model_api(provider=model_provider, model=model)
#         self.prompt_manager = PromptManager(prompt_dir)
#         logging.basicConfig(level=logging.INFO)

#     def generate_code(self, prompt_name, placeholders, retries=3, delay=5):
#         """
#         Generates or improves code using the LLM.

#         Args:
#             prompt_name (str): The name of the prompt template to use.
#             placeholders (dict): A dictionary of placeholders for the prompt.
#             retries (int): Number of retry attempts if the LLM call fails.
#             delay (int): Delay in seconds between retries.

#         Returns:
#             str: The generated code from the LLM.

#         Raises:
#             RuntimeError: If the LLM call fails after the specified retries.
#         """
#         prompt = self.prompt_manager.load_prompt(prompt_name)
#         rendered_prompt = self.prompt_manager.render_prompt(prompt, placeholders)

#         for attempt in range(1, retries + 1):
#             try:
                
#                 # print(f'RENDERED_PROMPT: \n {rendered_prompt}: ')
                
#                 logging.info(f"Sending prompt to LLM (attempt {attempt}/{retries})")
#                 response = self.model_client.get_response(rendered_prompt)
#                 if response:
#                     logging.info("Code generated successfully.")
#                     return response.strip()
#             except Exception as e:
#                 logging.error(f"Error generating code (attempt {attempt}): {e}")
#                 if attempt < retries:
#                     time.sleep(delay)

#         raise RuntimeError(f"Failed to generate code after {retries} attempts.")

#     def initial_code_generation(self, function_header, docstring, extra_info=""):
#         """
#         Generates initial code for a function/method.

#         Args:
#             function_header (str): The header of the function/method.
#             docstring (str): The docstring describing the function/method.
#             extra_info (str): Additional context for the LLM.

#         Returns:
#             str: The generated code.
#         """
#         placeholders = {
#             "function_header": function_header,
#             "extra_info": extra_info
#         }
#         return self.generate_code("default_function_prompt.txt", placeholders)

#     def fix_runtime_error(self, current_code, error_message):
#         """
#         Requests a fix for a runtime error from the LLM.

#         Args:
#             current_code (str): The current version of the function/method code.
#             error_message (str): The error message encountered during runtime.

#         Returns:
#             str: The fixed code.
#         """
#         placeholders = {
#             "code": current_code,
#             "error_message": error_message
#         }
#         return self.generate_code("error_correction_prompt.txt", placeholders)

#     def hot_swap_improvement(self, current_code, execution_context, hot_swap_condition):
#         """
#         Requests a performance or functionality improvement for a function/method.

#         Args:
#             current_code (str): The current version of the function/method code.
#             execution_context (dict): Context of the function's usage (e.g., input patterns, frequency).
#             hot_swap_condition (str): The condition triggering the hot-swapping.

#         Returns:
#             str: The improved code.
#         """
#         placeholders = {
#             "code": current_code,
#             "execution_context": execution_context,
#             "hot_swap_condition": hot_swap_condition
#         }
#         return self.generate_code("hot_swapping_prompt.txt", placeholders)

#     def generate_test_logic(self, corrected_code, prompt="default_test_prompt.txt"):
#         """
#         Generates test logic for the corrected function using the LLM.

#         Args:
#             corrected_code (str): The corrected function code.
#             prompt_name (str): The name of the test generation prompt template.

#         Returns:
#             str: The generated test logic.
#         """
#         placeholders = {
#             "code": corrected_code
#         }
#         return self.generate_code(prompt, placeholders)


# llm_generator = LLMCodeGenerator()
# function_header = "def calculate_average(numbers):"
# docstring = """
#     Calculates the average of a list of numbers.

#     Args:
#         numbers (list of float): A list of numeric values.

#     Returns:
#         float: The average of the list.
# """
# generated_code = llm_generator.initial_code_generation(function_header, docstring)
# print("Generated Code:")
# print(generated_code)

# llm_generator = LLMCodeGenerator()
# current_code = """
# def calculate_average(numbers):
#     return sum(numbers) / len(numbers)
# """
# error_message = "ZeroDivisionError: division by zero"
# fixed_code = llm_generator.fix_runtime_error(current_code, error_message)
# print("Fixed Code:")
# print(fixed_code)

