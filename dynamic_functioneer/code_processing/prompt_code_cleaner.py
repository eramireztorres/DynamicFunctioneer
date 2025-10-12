import re

def remove_extra_final_lines(input_code):
    """
    Removes extra final lines from the code that have zero indentation.

    Args:
        input_code (str): The input Python code as a string.

    Returns:
        str: The cleaned Python code with unnecessary final lines removed.
    """
    lines = input_code.splitlines()

    while lines:
        last_line = lines[-1]  # Check the last line
        if last_line.strip() == "" or not last_line.startswith(" "):  # Line has zero indentation or is blank
            lines.pop()  # Remove the last line
        else:
            break  # Stop if the last line has non-zero indentation

    return "\n".join(lines)


class DynamicFunctionCleaner:
    """
    Cleans dynamically generated Python code by:
    1. Removing all occurrences of @dynamic_function with or without arguments.
    2. Preserving the integrity of function and method definitions, including docstrings and indentation.
    3. Removing unnecessary final lines with zero indentation.
    """

    def __init__(self, input_code):
        self.input_code = input_code

    def clean_dynamic_function(self):
        # Remove @dynamic_function decorators
        pattern = r'^\s*@dynamic_function\(.*?\)\s*$|^\s*@dynamic_function\s*$'
        lines = self.input_code.splitlines()
        cleaned_lines = []
        skip_next_blank_line = False

        for line in lines:
            if re.match(pattern, line):
                skip_next_blank_line = True
                continue
            if skip_next_blank_line and line.strip() == "":
                skip_next_blank_line = False
                continue
            cleaned_lines.append(line)

        # Remove extra final lines with zero indentation
        cleaned_code = "\n".join(cleaned_lines)
        return remove_extra_final_lines(cleaned_code)



# class DynamicFunctionCleaner:
#     """
#     Cleans dynamically generated Python code by:
#     1. Removing all occurrences of @dynamic_function with or without arguments.
#     2. Trimming extraneous non-method/function lines at the end of the string.
#     """

#     def __init__(self, input_code):
#         """
#         Initializes the cleaner with the input code.

#         Args:
#             input_code (str): The input code as a string.
#         """
#         self.input_code = input_code

#     def clean_dynamic_function(self):
#         """
#         Cleans the code by removing @dynamic_function and trimming non-function trailing lines.

#         Returns:
#             str: The cleaned code.
#         """
#         # Define the regular expression pattern to match @dynamic_function(...)
#         dynamic_function_pattern = r'^\s*@dynamic_function\(.*?\)\s*$|^\s*@dynamic_function\s*$'
#         cleaned_code = re.sub(dynamic_function_pattern, '', self.input_code, flags=re.MULTILINE)

#         # Define the pattern for valid function/method definitions
#         function_pattern = r'^\s*def\s+\w+\s*\(.*\):\s*$'

#         # Split the code into lines and process each line
#         lines = cleaned_code.splitlines()
#         trimmed_lines = []
#         found_valid_function = False

#         for line in reversed(lines):
#             if re.match(function_pattern, line):
#                 found_valid_function = True
#             if found_valid_function:
#                 trimmed_lines.append(line)

#         # Reverse back to preserve original order
#         trimmed_lines.reverse()

#         return '\n'.join(trimmed_lines)


# # Example usage
# if __name__ == "__main__":
#     input_code = """\
# class StudentGrades:
#     @dynamic_function(model="meta-llama/llama-3.2-1b-instruct:free", extra_info="Adds or updates a student's grade.")
#     def add_grade(self, student_name, course_name, grade):
#         pass

#     @dynamic_function()
#     def get_grade(self, student_name, course_name):
#         "Some docstring"
#         pass
# student_grades = StudentGrades()
# student_grades.add_grade("John Doe", "Math 101", 85.5)
# print(student_grades.get_grade("John Doe", "Math 101"))
# """
#     cleaner = DynamicFunctionCleaner(input_code)
#     cleaned_code = cleaner.clean_dynamic_function()
#     print("Cleaned Code:")
#     print(cleaned_code)
