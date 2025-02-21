import ast
import logging
import textwrap

class CodeBlockExtractor:
    """
    Extracts the first Python code block from LLM responses.
    Dedents and strips the contents so they match the indentation
    expected by tests.
    """

    @staticmethod
    def extract_code_block(response):
        """
        Extracts the first Python code block from the response,
        dedenting it to normalize indentation.

        Args:
            response (str): The raw LLM response.

        Returns:
            str: Dedented contents of the first Python code block,
                 or a stripped version of the original response if
                 no code block is found.
        """
        lines = response.splitlines()
        code_lines = []
        in_code_block = False

        for line in lines:
            # Detect the start of the code block
            if line.strip().startswith("```python"):
                in_code_block = True
                # Skip the line containing ```python
                continue

            # Detect the end of the code block
            if in_code_block and line.strip().startswith("```"):
                # Reached closing triple-backtick for the first code block
                in_code_block = False
                break

            # Collect lines while inside a code block
            if in_code_block:
                code_lines.append(line)

        if code_lines:
            # We found a code block; dedent to remove extra indentation
            extracted_code = "\n".join(code_lines)
            # dedent, then strip to remove leading/trailing newlines/spaces
            return textwrap.dedent(extracted_code).strip()
        else:
            # No code block was found, so return the original text, stripped
            return response.strip()


class CodeNormalizer:
    """
    Normalizes extracted Python code for validation and execution.
    """
    @staticmethod
    def normalize_indentation(code):
        """
        Fixes indentation issues in the code if needed.

        Args:
            code (str): The Python code to normalize.

        Returns:
            str: Code with consistent indentation.
        """
        # Only dedent if code appears to have excessive leading spaces
        if code.startswith("    "):
            return textwrap.dedent(code)
        return code

    @staticmethod
    def remove_prefixes(code):
        """
        Removes non-Python prefixes (e.g., markdown list prefixes like `- `).

        Args:
            code (str): The Python code with potential prefixes.

        Returns:
            str: Cleaned Python code.
        """
        return "\n".join(line.lstrip("- ") for line in code.splitlines())

    @staticmethod
    def normalize_code(code):
        """
        Applies normalization steps to clean the Python code.

        Args:
            code (str): The Python code to normalize.

        Returns:
            str: Fully normalized Python code.
        """
        # Skip normalization if already valid
        if CodeValidator.validate_code(code):
            print("Code appears valid. Skipping normalization.")
            return code

        code = CodeNormalizer.remove_prefixes(code)
        code = CodeNormalizer.normalize_indentation(code)
        return code



class CodeValidator:
    """
    Validates Python code using the AST module.
    """
    @staticmethod
    def validate_code(code):
        """
        Validates Python code using the `ast` module.

        Args:
            code (str): Python code to validate.

        Returns:
            bool: True if the code is valid, False otherwise.
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            print(f"SyntaxError during validation: {e.msg} at line {e.lineno}, offset {e.offset}")
            return False


class CodeSelector:
    """
    Selects the most relevant function/method from multiple definitions and removes unrelated code.
    """
    @staticmethod
    def select_relevant_function(code, function_name):
        """
        Selects the most relevant function definition from the code and removes unrelated code.

        Args:
            code (str): The Python code containing multiple functions.
            function_name (str): The target function name.

        Returns:
            str: The selected function definition without extra code.

        Raises:
            ValueError: If the function is not found.
        """
        tree = ast.parse(code)
        selected_function = None

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                selected_function = ast.unparse(node).strip()
                break  # Stop after finding the function

        if not selected_function:
            raise ValueError(f"Function '{function_name}' not found in the provided code.")

        return selected_function  # Return only the function definition



# class CodeSelector:
#     """
#     Selects the most relevant function/method from multiple definitions.
#     """
#     @staticmethod
#     def select_relevant_function(code, function_name):
#         """
#         Selects the most relevant function definition from the code.

#         Args:
#             code (str): The Python code containing multiple functions.
#             function_name (str): The target function name.

#         Returns:
#             str: The selected function definition.

#         Raises:
#             ValueError: If the function is not found.
#         """
#         tree = ast.parse(code)
#         for node in ast.walk(tree):
#             if isinstance(node, ast.FunctionDef) and node.name == function_name:
#                 return ast.unparse(node).strip()

#         raise ValueError(f"Function '{function_name}' not found in the provided code.")


# class CodeReconstructor:
#     """
#     Reconstructs incomplete or malformed Python code blocks.
#     """
#     @staticmethod
#     def reconstruct_code(code):
#         """
#         Attempts to fix incomplete code by checking for missing components (e.g., docstrings).

#         Args:
#             code (str): Malformed Python code.

#         Returns:
#             str: Reconstructed Python code.

#         Raises:
#             ValueError: If reconstruction is not possible.
#         """
#         if 'def ' not in code.splitlines()[0]:
#             raise ValueError("Cannot reconstruct code: Missing 'def' statement.")

#         # Attempt minimal adjustments
#         if '"""' not in code:
#             code = code.replace("def ", 'def ', 1)  # Minimal attempt to adjust
#         return code

class CodeReconstructor:
    """
    Reconstructs incomplete or malformed Python code blocks.
    """
    @staticmethod
    def reconstruct_code(code):
        """
        Attempts to fix incomplete code by checking for missing components (e.g., indentation, docstrings).

        Args:
            code (str): Malformed Python code.

        Returns:
            str: Reconstructed Python code.

        Raises:
            ValueError: If reconstruction is not possible.
        """
        lines = code.splitlines()
        
        # Ensure code starts with 'def ' or 'class '
        if not any(line.lstrip().startswith(("def ", "class ")) for line in lines):
            raise ValueError("Cannot reconstruct code: Missing 'def' or 'class' statement.")

        # Ensure docstrings are properly closed
        open_docstrings = sum(line.count('"""') for line in lines) % 2 != 0
        if open_docstrings:
            logging.warning("Detected unclosed docstring. Attempting to close it.")
            lines.append('"""')  # Append closing docstring

        # Ensure proper indentation for function definitions
        corrected_lines = []
        for line in lines:
            if line.lstrip().startswith("def ") or line.lstrip().startswith("class "):
                corrected_lines.append(line)
            else:
                corrected_lines.append("    " + line)  # Ensure minimum indentation
        
        reconstructed_code = "\n".join(corrected_lines)
        
        # Final validation
        if not CodeValidator.validate_code(reconstructed_code):
            raise ValueError("Reconstructed code is still invalid.")

        return reconstructed_code



class LLMResponseCleaner:
    """
    Cleans the LLM response to retain only valid Python code.
    """

    @staticmethod
    def extract_code_block(response):
        """
        Extracts the Python code block from the LLM response.

        Args:
            response (str): The raw response from the LLM.

        Returns:
            str: The extracted Python code block, or the original response if no block is found.
        """
        lines = response.splitlines()
        code_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```python"):
                in_code_block = True
                continue
            elif line.strip().startswith("```"):
                in_code_block = False
                continue

            if in_code_block:
                code_lines.append(line)

        if code_lines:
            print("Extracted Python code block successfully.")
            print(f"Extracted code block:\n{code_lines}")  # Print extracted lines
        else:
            print("No Python code block found. Returning the original response.")

        return "\n".join(code_lines) if code_lines else response

    @staticmethod
    def validate_code(response):
        """
        Validates the Python code using the `ast` module.

        Args:
            response (str): The cleaned Python code.

        Returns:
            str: The validated Python code.

        Raises:
            SyntaxError: If the code is invalid.
        """
        try:
            # Strip unintended prefixes before validation
            cleaned_response = "\n".join(line.lstrip("- ") for line in response.splitlines())
            print(f"Validating cleaned response:\n{cleaned_response}")  # Debug cleaned response
            ast.parse(cleaned_response)
            print("Python code validated successfully.")
            return cleaned_response
        except SyntaxError as e:
            print(f"SyntaxError encountered during validation: {e}")
            raise

    @staticmethod
    def clean_response(response, function_name=None):
        """
        Cleans the LLM response by extracting and validating Python code.
    
        Args:
            response (str): The raw response from the LLM.
            function_name (str, optional): The target function name for selection.
    
        Returns:
            str: The cleaned Python code.
    
        Raises:
            ValueError: If no valid code could be extracted.
        """
        logging.info("Starting response cleaning process.")
        logging.debug(f"Raw LLM response:\n{response}")  # Debugging raw LLM response
    
        # Step 1: Extract Python code block
        extracted_code = CodeBlockExtractor.extract_code_block(response)
        logging.debug(f"Extracted code block:\n{extracted_code}")  # Debug extracted code
    
        # Step 2: Normalize the code
        normalized_code = CodeNormalizer.normalize_code(extracted_code)
        logging.debug(f"Normalized code:\n{normalized_code}")  # Debug normalized code
    
        # Step 3: Validate the cleaned code
        if not CodeValidator.validate_code(normalized_code):
            logging.warning("Validation failed. Attempting reconstruction...")
            try:
                normalized_code = CodeReconstructor.reconstruct_code(normalized_code)
                logging.debug(f"Reconstructed code:\n{normalized_code}")  # Debug reconstructed code
    
                if not CodeValidator.validate_code(normalized_code):
                    raise ValueError("Reconstructed code is still invalid.")
            except ValueError as e:
                logging.error(f"Code reconstruction failed: {e}")
                raise ValueError(f"Code reconstruction failed: {e}")
    
        # Step 4: Select the relevant function if multiple exist
        # if function_name:
        #     try:
        #         normalized_code = CodeSelector.select_relevant_function(normalized_code, function_name)
        #     except ValueError as e:
        #         raise ValueError(f"Function selection failed: {e}")
        
        # Step 4: Select the relevant function if multiple exist
        if function_name:
            try:
                normalized_code = CodeSelector.select_relevant_function(normalized_code, function_name)
                logging.info(f"Final cleaned code:\n{normalized_code}")
            except ValueError as e:
                raise ValueError(f"Function selection failed: {e}")

    
        logging.info("Final cleaned code:")
        logging.info(f"\n{normalized_code}")
    
        return normalized_code



