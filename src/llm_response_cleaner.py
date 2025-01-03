# import ast
# import logging

# class LLMResponseCleaner:
#     """
#     Cleans the LLM response to retain only valid Python code.
#     """

#     @staticmethod
#     def extract_valid_code(response):
#         """
#         Extracts valid Python code from the LLM response.

#         Args:
#             response (str): The raw response from the LLM.

#         Returns:
#             str: The cleaned Python code.

#         Raises:
#             SyntaxError: If the entire response is invalid Python code.
#         """
#         try:
#             # Attempt to parse the entire response as Python code
#             tree = ast.parse(response)
#             valid_code = response
#             logging.info("The response is valid Python code.")
#         except SyntaxError as e:
#             logging.warning(f"SyntaxError encountered: {e}. Attempting to filter valid code.")

#             # Filter line by line if the entire response is invalid
#             valid_lines = []
#             for line in response.splitlines():
#                 try:
#                     ast.parse(line)
#                     valid_lines.append(line)
#                 except SyntaxError:
#                     logging.warning(f"Invalid line removed: {line}")
#             valid_code = "\n".join(valid_lines)

#         return valid_code

#     @staticmethod
#     def clean_response(response):
#         """
#         Cleans the LLM response by removing extra comments and unrelated explanations.

#         Args:
#             response (str): The raw response from the LLM.

#         Returns:
#             str: The cleaned Python code.
#         """
#         # Split lines and filter out those starting with non-Python comment patterns
#         lines = response.splitlines()
#         cleaned_lines = [
#             line for line in lines if not line.strip().startswith(("#", "This implementation"))
#         ]
#         cleaned_code = "\n".join(cleaned_lines)

#         # Further validate cleaned code using AST
#         return LLMResponseCleaner.extract_valid_code(cleaned_code)

import ast
import logging

# class LLMResponseCleaner:
#     """
#     Cleans the LLM response to retain only valid Python code.
#     """

#     @staticmethod
#     def extract_code_block(response):
#         """
#         Extracts the Python code block from the LLM response.

#         Args:
#             response (str): The raw response from the LLM.

#         Returns:
#             str: The extracted Python code block, or the original response if no block is found.
#         """
#         lines = response.splitlines()
#         code_lines = []
#         in_code_block = False

#         for line in lines:
#             if line.strip().startswith("```python"):
#                 in_code_block = True
#                 continue
#             elif line.strip().startswith("```"):
#                 in_code_block = False
#                 continue

#             if in_code_block:
#                 code_lines.append(line)

#         return "\n".join(code_lines) if code_lines else response

#     @staticmethod
#     def validate_code(response):
#         """
#         Validates the Python code using the `ast` module.

#         Args:
#             response (str): The cleaned Python code.

#         Returns:
#             str: The validated Python code.

#         Raises:
#             SyntaxError: If the code is invalid.
#         """
#         try:
#             ast.parse(response)
#             return response
#         except SyntaxError as e:
#             logging.warning(f"SyntaxError encountered: {e}")
#             raise

#     @staticmethod
#     def clean_response(response):
#         """
#         Cleans the LLM response by extracting and validating Python code.

#         Args:
#             response (str): The raw response from the LLM.

#         Returns:
#             str: The cleaned Python code.

#         Raises:
#             ValueError: If no valid code could be extracted.
#         """
#         # Extract Python code block
#         extracted_code = LLMResponseCleaner.extract_code_block(response)

#         # Validate the extracted code
#         try:
#             return LLMResponseCleaner.validate_code(extracted_code)
#         except SyntaxError:
#             logging.error("No valid Python code could be extracted from the response.")
#             raise ValueError("Failed to clean the LLM response: No valid code found.")

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
            # Start of a code block
            if line.strip().startswith("```python"):
                in_code_block = True
                continue
            # End of a code block
            elif line.strip().startswith("```"):
                in_code_block = False
                continue

            # Collect lines inside the code block
            if in_code_block:
                code_lines.append(line)

        if code_lines:
            logging.info("Extracted Python code block successfully.")
        else:
            logging.warning("No Python code block found. Returning the original response.")

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
            ast.parse(response)
            logging.info("Python code validated successfully.")
            return response
        except SyntaxError as e:
            logging.warning(f"SyntaxError encountered during validation: {e}")
            raise

    @staticmethod
    def clean_response(response):
        """
        Cleans the LLM response by extracting and validating Python code.

        Args:
            response (str): The raw response from the LLM.

        Returns:
            str: The cleaned Python code.

        Raises:
            ValueError: If no valid code could be extracted.
        """
        logging.info("Starting response cleaning process.")

        # Step 1: Extract Python code block
        extracted_code = LLMResponseCleaner.extract_code_block(response)

        # Step 2: Remove empty lines or lines with only backticks
        cleaned_lines = [
            line for line in extracted_code.splitlines()
            if line.strip() and not line.strip().startswith("```")
        ]
        cleaned_code = "\n".join(cleaned_lines)

        # Step 3: Validate the cleaned code
        try:
            return LLMResponseCleaner.validate_code(cleaned_code)
        except SyntaxError:
            logging.error("No valid Python code could be extracted after cleaning.")
            raise ValueError("Failed to clean the LLM response: No valid code found.")
