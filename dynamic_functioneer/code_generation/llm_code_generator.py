import logging
import time
from pathlib import Path
import inspect
import ast
from dynamic_functioneer.code_generation.prompt_manager import PromptManager
from dynamic_functioneer.code_processing.prompt_code_cleaner import DynamicFunctionCleaner
from dynamic_functioneer.models.model_api_factory import ModelAPIFactory


def extract_function_signature(func_or_source):
    """
    Extracts the function signature and docstring from a function object or its source string.

    Args:
        func_or_source (function or str): The function object or its source as a string.

    Returns:
        str: The cleaned function signature with its docstring.

    Raises:
        ValueError: If the function signature cannot be extracted.
    """
    if isinstance(func_or_source, str):
        source = func_or_source
    else:
        try:
            source = inspect.getsource(func_or_source)
        except Exception as e:
            raise ValueError(f"Failed to retrieve source for the function: {e}")

    # Remove decorators while keeping the function header and docstring
    source_lines = source.splitlines()
    cleaned_lines = []
    in_function = False

    for line in source_lines:
        if line.strip().startswith("def "):  # Start of the function
            in_function = True
        if in_function:
            cleaned_lines.append(line)

    if not cleaned_lines:
        raise ValueError("No valid function definition found.")

    return "\n".join(cleaned_lines)


def extract_method_signature(class_definition, method_name):
    """
    Extracts the method signature from a class definition using AST,
    ensuring the result starts with `def` and includes the docstring.

    Args:
        class_definition (str): The full class source code as a string.
        method_name (str): The name of the method to extract.

    Returns:
        str: The cleaned method signature starting with `def` and including the docstring.

    Raises:
        ValueError: If the method cannot be extracted.
    """
    try:
        tree = ast.parse(class_definition)
    except SyntaxError as e:
        raise ValueError(f"Failed to parse class definition: {e}")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    # Use ast.unparse for full method extraction
                    try:
                        method_source = ast.unparse(item).strip()
                    except AttributeError:
                        raise ValueError("The `ast.unparse` function is unavailable in your Python version.")
                    return method_source

    raise ValueError(f"Could not extract method signature for '{method_name}'.")





class LLMCodeGenerator:
    """
    Manages interactions with the LLM to generate or improve function/method code.
    """

    def __init__(self, model_provider=None, model="gpt-4", prompt_dir="./dynamic_functioneer/prompts"):
        """
        Initialize the LLMCodeGenerator.

        Args:
            model_provider (str): The provider name for the LLM (e.g., "openai", "llama").
            model (str): The specific model to use (e.g., "gpt-4").
            prompt_dir (str): Directory containing prompt templates.
        """
        self.model_client = ModelAPIFactory.get_model_api(provider=model_provider, model=model)
        # self.prompt_manager = PromptManager(prompt_dir)
        self.prompt_manager = PromptManager()
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
                # logging.info(f"Rendered Prompt Sent to LLM:\n{rendered_prompt}")
                # logging.info(f"Sending prompt to LLM (attempt {attempt}/{retries})")
                response = self.model_client.get_response(rendered_prompt)
                if response:
                    logging.info("Code generated successfully.")
                    
                    # Clean the code using DynamicFunctionCleaner
                    cleaner = DynamicFunctionCleaner(response.strip())
                    cleaned_code = cleaner.clean_dynamic_function()
                    
                    return cleaned_code
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
        # Extract the function signature using AST
        cleaned_function_header = extract_function_signature(function_header)
    
        placeholders = {
            "function_header": cleaned_function_header,
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
        # Extract the method signature using AST
        cleaned_method_header = extract_method_signature(class_definition, method_header)
    
        placeholders = {
            "class_definition": class_definition,
            "method_header": cleaned_method_header,
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

    def hot_swap_improvement(self, current_code, execution_context, hot_swap_condition, 
                             hot_swapping_prompt="hot_swapping_prompt.txt"):
        """
        Requests a performance or functionality improvement for a function/method.

        Args:
            current_code (str): The current version of the function/method code.
        Returns:
            str: The improved code.
        """
        placeholders = {
            "code": current_code,
        }
        return self.generate_code(hot_swapping_prompt, placeholders)

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

    def generate_function_test_logic(self, function_code, extra_info="", 
                                     test_function_prompt="test_function_prompt.txt"):
        """
        Generates test logic for a function.
        """
        placeholders = {
            "function_code": function_code,
            "extra_info": extra_info
        }
        return self.generate_code(test_function_prompt, placeholders)

    def generate_method_test_logic(self, class_definition, method_header, extra_info="",
                                   test_method_prompt="test_method_prompt.txt"):
        """
        Generates test logic for a method in a class.
        """
        placeholders = {
            "class_definition": class_definition,
            "method_header": method_header,
            "extra_info": extra_info
        }
        return self.generate_code(test_method_prompt, placeholders)


