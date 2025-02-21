import ast
import logging
import textwrap
from typing import Optional

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

    Typical steps include:
      1. Removing bullet/prefix markers (e.g. '- ', '* ').
      2. Dedenting code blocks if they appear to have extra indentation.
      3. Removing trailing whitespace from each line.

    If code is already valid (as determined by CodeValidator.validate_code),
    the normalize_code method returns it unchanged.
    """

    @staticmethod
    def remove_prefixes(code: str, prefixes=None) -> str:
        """
        Removes specific prefixes at the start of each line (e.g. '- ', '* ').
        Lines that do not match any prefix are unchanged.

        Args:
            code (str): The Python code or text to clean.
            prefixes (List[str], optional): The list of prefixes to remove.
                                            Defaults to ['- ', '* '].

        Returns:
            str: Code with the specified prefixes removed from line beginnings.
        """
        if prefixes is None:
            prefixes = ["- ", "* "]

        cleaned_lines = []
        for line in code.splitlines():
            for prefix in prefixes:
                if line.startswith(prefix):
                    line = line[len(prefix):]
                    # Only remove the first matching prefix, then stop checking
                    break
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines)

    @staticmethod
    def remove_trailing_whitespace(code: str) -> str:
        """
        Removes trailing (right-side) whitespace from each line in the code.

        Args:
            code (str): The Python code.

        Returns:
            str: Same code, with trailing whitespace stripped on every line.
        """
        lines = code.splitlines()
        stripped = [line.rstrip() for line in lines]
        return "\n".join(stripped)

    @staticmethod
    def normalize_indentation(code: str) -> str:
        """
        Dedents code if it appears to have consistent leading indentation.

        This helps unify indentation style, especially if the code block
        was captured with extra indentation.

        Args:
            code (str): The code to dedent.

        Returns:
            str: Dedented code.
        """
        return textwrap.dedent(code)

    @staticmethod
    def normalize_code(code: str) -> str:
        """
        Performs a sequence of normalization steps on the code:
          1. If it's already valid Python (via CodeValidator), skip changes.
          2. Remove bullet/prefix lines (e.g. '- ', '* ').
          3. Dedent the code with textwrap.dedent().
          4. Remove trailing whitespace.

        Args:
            code (str): The Python code to normalize.

        Returns:
            str: Normalized Python code.
        """
        if CodeValidator.validate_code(code):
            # If it's already valid, do nothing
            return code

        # Remove bullet/prefix lines (commonly introduced in LLM responses)
        code = CodeNormalizer.remove_prefixes(code)

        # Dedent to handle extra indentation
        code = CodeNormalizer.normalize_indentation(code)

        # Remove trailing whitespace
        code = CodeNormalizer.remove_trailing_whitespace(code)

        return code


class CodeValidator:
    """
    Validates Python code by parsing it into an AST.
    """

    @staticmethod
    def validate_code(code: str) -> bool:
        """
        Tries to parse the code with ast.parse. If it succeeds, the code is valid.

        Args:
            code (str): The Python code to check.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False


class CodeSelector:
    """
    Selects the definition of a specific function (or method) from a larger code string.

    Typically used if multiple functions are present and you only want
    to keep or return one function's AST unparse.
    """

    @staticmethod
    def select_relevant_function(code: str, function_name: str) -> str:
        """
        Locates the given function_name within the provided code and returns
        just that function's definition as a string.

        Internally:
          1. Parses the code into an AST.
          2. Searches for an ast.FunctionDef that matches function_name.
          3. If found, unparse it to source code and return that snippet.
          4. If not found, raises ValueError.

        Args:
            code (str): The Python code containing multiple functions.
            function_name (str): The target function name.

        Returns:
            str: The source code of the function definition (including its docstring).

        Raises:
            ValueError: If the function is not found in the code or if ast.unparse is not available.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python code: {e.msg}") from e

        selected_function = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # Python 3.9+ has ast.unparse
                if hasattr(ast, "unparse"):
                    selected_function = ast.unparse(node).strip()
                else:
                    raise ValueError("ast.unparse is not available in this Python version.")
                break

        if not selected_function:
            raise ValueError(f"Function '{function_name}' not found in the provided code.")

        return selected_function



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



###################################
#        LLMResponseCleaner       #
###################################
class LLMResponseCleaner:
    """
    Cleans a Large Language Model (LLM) response to isolate valid Python code.

    Typical pipeline:
      1) Extract Python code block from the raw LLM text (```python ... ```).
      2) Normalize code (remove bullet prefixes, unify indentation).
      3) Validate. If invalid, attempt reconstruction (docstring closure, indentation fix).
      4) (Optionally) select a named function if multiple exist.
    """

    @staticmethod
    def clean_response(response: str, function_name: Optional[str] = None) -> str:
        """
        High-level method to clean the LLM's response.

        Steps:
          1. Extract code via CodeBlockExtractor.
          2. Normalize code with CodeNormalizer.
          3. Validate code with CodeValidator.
          4. If invalid, run CodeReconstructor. Re-validate.
          5. If function_name is provided, narrow down to that function with CodeSelector.

        Raises:
          ValueError: If the code cannot be made valid, or if function_name is not found (when provided).

        Returns:
          str: The final, cleaned Python code.
        """
        logging.info("Starting response cleaning process...")
        logging.debug(f"Raw LLM response:\n{response}")

        # Step 1: Extract potential python code block
        extracted_code = CodeBlockExtractor.extract_code_block(response)
        logging.debug(f"Extracted code block:\n{extracted_code}")

        # Step 2: Normalize
        normalized_code = CodeNormalizer.normalize_code(extracted_code)
        logging.debug(f"Normalized code:\n{normalized_code}")

        # Step 3: Validate
        if not CodeValidator.validate_code(normalized_code):
            # Step 4: Attempt reconstruction
            logging.warning("Initial validation failed. Attempting reconstruction.")
            try:
                reconstructed = CodeReconstructor.reconstruct_code(normalized_code)
                if not CodeValidator.validate_code(reconstructed):
                    raise ValueError("Reconstructed code is still invalid.")
                normalized_code = reconstructed
                logging.info("Reconstruction successful.")
            except ValueError as e:
                logging.error(f"Code reconstruction failed: {e}")
                raise ValueError(f"Code reconstruction failed: {e}")

        # Step 5: If we only want a single function, select it
        if function_name:
            try:
                final_code = CodeSelector.select_relevant_function(normalized_code, function_name)
                logging.debug(f"Final code after function selection:\n{final_code}")
                return final_code
            except ValueError as e:
                # The relevant function was not found
                logging.error(f"Function selection failed: {e}")
                raise ValueError(f"Function selection failed: {e}")

        return normalized_code
