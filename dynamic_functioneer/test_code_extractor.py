class CodeBlockExtractor:
    """
    Extracts Python code blocks from LLM responses.
    """
    @staticmethod
    def extract_code_block(response):
        """
        Extracts the first Python code block from the response.

        Args:
            response (str): The raw LLM response.

        Returns:
            str: Extracted Python code block, or the original response if no block is found.
        """
        lines = response.splitlines()
        code_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```python"):
                in_code_block = True
                continue  # Skip this line, don't include "```python"

            if in_code_block:
                if line.strip().startswith("```"):  # ✅ Stop at the first closing triple backtick
                    break
                code_lines.append(line)

        return "\n".join(code_lines).strip() if code_lines else response


# class CodeBlockExtractor:
#     """
#     Extracts Python code blocks from LLM responses.
#     """
#     @staticmethod
#     def extract_code_block(response):
#         """
#         Extracts the first Python code block from the response.

#         Args:
#             response (str): The raw LLM response.

#         Returns:
#             str: Extracted Python code block, or the original response if no block is found.
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


# ==== TEST CASES ====
def run_test(test_name, input_response, expected_output):
    print(f"\n--- {test_name} ---")
    print("Input Response:\n", input_response)

    extracted_code = CodeBlockExtractor.extract_code_block(input_response)

    print("\nExtracted Code:\n", extracted_code)
    print("\nExpected Output:\n", expected_output)
    
    assert extracted_code == expected_output, "❌ Test Failed"
    print("✅ Test Passed")


# ==== TEST 1: Single Code Block ====
test_response_1 = """
Here is your Python function:
```python
def add(a, b):
    return a + b
```
Hope this helps!
"""
expected_output_1 = """def add(a, b):\n    return a + b"""
run_test("Single Code Block Extraction", test_response_1, expected_output_1)


# ==== TEST 2: No Code Block in Response ====
test_response_2 = "There is no Python code in this response."
expected_output_2 = test_response_2  # Should return the original response
run_test("No Code Block Present", test_response_2, expected_output_2)


# ==== TEST 3: Multiple Code Blocks, Extract First One ====
test_response_3 = """
Here are two functions:
```python
def add(a, b):
    return a + b
```
Now, another one:
```python
def multiply(a, b):
    return a * b
```
"""
expected_output_3 = """def add(a, b):\n    return a + b"""  # Should extract only the first block
run_test("Multiple Code Blocks", test_response_3, expected_output_3)


# ==== TEST 4: Unclosed Code Block (Should Extract as-is) ====
test_response_4 = """
Here is your function:
```python
def divide(a, b):
    return a / b
"""
expected_output_4 = """def divide(a, b):\n    return a / b"""  # Should still extract despite missing closing ```
run_test("Unclosed Code Block", test_response_4, expected_output_4)


# ==== TEST 5: Code Block Without "python" Specifier ====
test_response_5 = """
Here is a function:
```
def subtract(a, b):
    return a - b
```
"""
expected_output_5 = test_response_5  # Should return original text (no valid Python block)
run_test("Code Block Without Language Specifier", test_response_5, expected_output_5)


