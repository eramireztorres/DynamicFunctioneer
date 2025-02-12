import ast
from textwrap import dedent

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

        # ✅ Remove extra lines after the function using AST
        extracted_lines = selected_function.split("\n")
        cleaned_function = []
        
        for line in extracted_lines:
            if line.strip().startswith("#") or line.strip().startswith("library."):
                break  # Stop when encountering example calls
            cleaned_function.append(line)

        return "\n".join(cleaned_function).strip()  # Return only the function definition


# class CodeSelector:
#     """
#     Selects the most relevant function/method from multiple definitions and removes unrelated code.
#     """
#     @staticmethod
#     def select_relevant_function(code, function_name):
#         """
#         Selects the most relevant function definition from the code and removes unrelated code.

#         Args:
#             code (str): The Python code containing multiple functions.
#             function_name (str): The target function name.

#         Returns:
#             str: The selected function definition without extra code.

#         Raises:
#             ValueError: If the function is not found.
#         """
#         tree = ast.parse(code)
#         selected_function = None

#         for node in ast.walk(tree):
#             if isinstance(node, ast.FunctionDef) and node.name == function_name:
#                 selected_function = ast.unparse(node).strip()
#                 break  # Stop after finding the function

#         if not selected_function:
#             raise ValueError(f"Function '{function_name}' not found in the provided code.")

#         return selected_function  # Return only the function definition



def normalize_code_format(code):
    """
    Parses the code using AST and re-unparses it to normalize formatting.
    This ensures that different styles (like single vs. double quotes) don't cause test failures.
    
    Args:
        code (str): The original Python code.
    
    Returns:
        str: The normalized Python code.
    """
    return ast.unparse(ast.parse(code)).strip()

def run_test(test_name, input_code, function_name, expected_output=None, expect_error=False):
    print(f"\n--- {test_name} ---")
    print(f"Extracting function: {function_name}")
    print("Input Code:\n", input_code)

    try:
        result = CodeSelector.select_relevant_function(dedent(input_code), function_name)
        print("\nExtracted Function:\n", result)

        if expected_output:
            # Normalize both extracted and expected output
            normalized_result = normalize_code_format(result)
            normalized_expected = normalize_code_format(expected_output)
            
            print("\nExpected Output:\n", expected_output)
            assert normalized_result == normalized_expected, "❌ Test Failed"
            
        print("✅ Test Passed")
    except ValueError as e:
        if expect_error:
            print("✅ Expected Error:", e)
        else:
            print("❌ Unexpected Error:", e)


# ==== TEST 1: Simple Function ====
test_code_1 = """
def add(a, b):
    return a + b
"""

expected_output_1 = """
def add(a, b):
    return a + b
""".strip()

run_test("Simple Function Extraction", test_code_1, "add", expected_output_1)


# ==== TEST 2: Multiple Functions ====
test_code_2 = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""

expected_output_2 = """
def multiply(a, b):
    return a * b
""".strip()

run_test("Multiple Functions - Extract 'multiply'", test_code_2, "multiply", expected_output_2)


# ==== TEST 3: Function Inside a Class ====
test_code_3 = """
class MathOperations:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b
"""

expected_output_3 = """
def add(self, a, b):
    return a + b
""".strip()

run_test("Function Inside a Class - Extract 'add'", test_code_3, "add", expected_output_3)


# ==== TEST 4: Function with Decorators ====
test_code_4 = """
@staticmethod
def divide(a, b):
    return a / b
"""

expected_output_4 = """
@staticmethod
def divide(a, b):
    return a / b
""".strip()

run_test("Function with Decorators", test_code_4, "divide", expected_output_4)


# ==== TEST 5: Function Not Found ====
test_code_5 = """
def subtract(a, b):
    return a - b
"""

run_test("Function Not Found", test_code_5, "non_existent_function", expect_error=True)


# ==== TEST 6: Function with Docstrings ====
test_code_6 = """
def greet(name):
    \"\"\"Returns a greeting message.\"\"\"
    return f"Hello, {name}!"
"""

expected_output_6 = """
def greet(name):
    \"\"\"Returns a greeting message.\"\"\"
    return f"Hello, {name}!"
""".strip()

run_test("Function with Docstrings", test_code_6, "greet", expected_output_6)


# ==== TEST 7: Function with Indentation Issues ====
test_code_7 = """
def faulty_indent(a, b):
return a + b
"""

run_test("Function with Indentation Issues", test_code_7, "faulty_indent", expect_error=True)


# import ast
# from textwrap import dedent

# class CodeSelector:
#     """
#     Selects the most relevant function/method from multiple definitions and removes unrelated code.
#     """
#     @staticmethod
#     def select_relevant_function(code, function_name):
#         """
#         Selects the most relevant function definition from the code and removes unrelated code.

#         Args:
#             code (str): The Python code containing multiple functions.
#             function_name (str): The target function name.

#         Returns:
#             str: The selected function definition without extra code.

#         Raises:
#             ValueError: If the function is not found.
#         """
#         tree = ast.parse(code)
#         selected_function = None

#         for node in ast.walk(tree):
#             if isinstance(node, ast.FunctionDef) and node.name == function_name:
#                 selected_function = ast.unparse(node).strip()
#                 break  # Stop after finding the function

#         if not selected_function:
#             raise ValueError(f"Function '{function_name}' not found in the provided code.")

#         return selected_function  # Return only the function definition


# # ==== TEST CASES ====
# def run_test(test_name, input_code, function_name, expected_output=None, expect_error=False):
#     print(f"\n--- {test_name} ---")
#     print(f"Extracting function: {function_name}")
#     print("Input Code:\n", input_code)

#     try:
#         result = CodeSelector.select_relevant_function(dedent(input_code), function_name)
#         print("\nExtracted Function:\n", result)
#         if expected_output:
#             print("\nExpected Output:\n", expected_output)
#             assert result == expected_output, "❌ Test Failed"
#         print("✅ Test Passed")
#     except ValueError as e:
#         if expect_error:
#             print("✅ Expected Error:", e)
#         else:
#             print("❌ Unexpected Error:", e)


# # ==== TEST 1: Simple Function ====
# test_code_1 = """
# def add(a, b):
#     return a + b
# """

# expected_output_1 = """
# def add(a, b):
#     return a + b
# """.strip()

# run_test("Simple Function Extraction", test_code_1, "add", expected_output_1)


# # ==== TEST 2: Multiple Functions ====
# test_code_2 = """
# def add(a, b):
#     return a + b

# def multiply(a, b):
#     return a * b
# """

# expected_output_2 = """
# def multiply(a, b):
#     return a * b
# """.strip()

# run_test("Multiple Functions - Extract 'multiply'", test_code_2, "multiply", expected_output_2)


# # ==== TEST 3: Function Inside a Class ====
# test_code_3 = """
# class MathOperations:
#     def add(self, a, b):
#         return a + b

#     def multiply(self, a, b):
#         return a * b
# """

# expected_output_3 = """
# def add(self, a, b):
#     return a + b
# """.strip()

# run_test("Function Inside a Class - Extract 'add'", test_code_3, "add", expected_output_3)


# # ==== TEST 4: Function with Decorators ====
# test_code_4 = """
# @staticmethod
# def divide(a, b):
#     return a / b
# """

# expected_output_4 = """
# @staticmethod
# def divide(a, b):
#     return a / b
# """.strip()

# run_test("Function with Decorators", test_code_4, "divide", expected_output_4)


# # ==== TEST 5: Function Not Found ====
# test_code_5 = """
# def subtract(a, b):
#     return a - b
# """

# run_test("Function Not Found", test_code_5, "non_existent_function", expect_error=True)


# # ==== TEST 6: Function with Docstrings ====
# test_code_6 = """
# def greet(name):
#     \"\"\"Returns a greeting message.\"\"\"
#     return f"Hello, {name}!"
# """

# expected_output_6 = """
# def greet(name):
#     \"\"\"Returns a greeting message.\"\"\"
#     return f"Hello, {name}!"
# """.strip()

# run_test("Function with Docstrings", test_code_6, "greet", expected_output_6)


# # ==== TEST 7: Function with Indentation Issues ====
# test_code_7 = """
# def faulty_indent(a, b):
# return a + b
# """

# run_test("Function with Indentation Issues", test_code_7, "faulty_indent", expect_error=True)

