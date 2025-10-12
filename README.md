# DynamicFunctioneer
Auto-generate and improve Python methods with decorators powered by LLMs.

## Prerequisites
A version of Python 3.11 or higher is required.

## Quick Installation
You can install DynamicFunctioneer directly from PyPI with a single command:

```bash
pip install dynamic-functioneer
```
This is the simplest way to get started with the package. You will also need to export the API key of your LLM models.

## Alternative Installation (from source)
If you prefer to work with the source code —for example, to develop or debug DynamicFunctioneer— you can install it from GitHub. To do this, you’ll need to use uv to manage your virtual environment and dependencies.

Before proceeding, install uv (if you haven’t already):

For macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing, ensure uv is accessible by verifying the version:

```bash
uv --version
```

If `uv` is not recognized, ensure the installation path (e.g., `~/.local/bin` on macOS/Linux or `%USERPROFILE%\.local\bin` on Windows) is added to your system's PATH environment variable.


## Installation

Clone the repository:

```bash
git clone https://github.com/eramireztorres/DynamicFunctioneer.git
```

Navigate to the directory:

```bash
cd DynamicFunctioneer
```

### Create virtual environment

You can create and manage the environment using `uv`:

```bash
uv venv
```

After creating the environment, activate it:

- **Linux/Mac**: `source .venv/bin/activate`
- **Windows**: `.venv\Scripts\activate`

Make sure to activate this environment whenever working with Gpt4CLI.

### Install the package:

```bash
uv sync
```

## Export the API keys of your models

### OpenAI Models

For OpenAI models, export your API key as an environment variable:

Linux or macOS:

```bash
export OPENAI_API_KEY='your_openai_api_key_here'
```

Or in windows:

```bash
setx OPENAI_API_KEY "your_openai_api_key_here"
```

You can export API keys for other model providers in a similar way by using the corresponding environment variable names:

- **Gemini**: Use GEMINI_API_KEY
- **Anthropic**: Use ANTHROPIC_API_KEY
- **OpenRouter**: Use OPENROUTER_API_KEY
     
### Overview

`@dynamic_function` is a Python decorator designed to enhance the flexibility and robustness of your functions and methods by dynamically generating, testing, and improving their implementation. Powered by large language models (LLMs), this decorator enables seamless integration of dynamic logic into your codebase, providing:

- **Automatic Implementation**: Generates function or method code dynamically based on provided descriptions and examples.
- **Error Handling**: Automatically detects and fixes runtime errors using iterative retries and LLM-based suggestions.
- **Unit Testing Integration**: Optionally generates and executes unit tests for the dynamic code to ensure reliability.
- **Customization**: Allows developers to configure models, retries, testing, and other parameters to suit their specific requirements.

By leveraging `@dynamic_function`, developers can prototype faster, maintain cleaner code, and handle edge cases with minimal manual intervention.

## `@dynamic_function` Decorator

The `@dynamic_function` decorator dynamically generates, tests, and improves the implementation of functions or methods using the power of large language models (LLMs). It integrates features like automatic code generation, runtime error fixing, and optional unit testing to provide a highly flexible and automated development workflow.

### Arguments

- **`model`** *(str, default="gpt-4o-mini")*  
  Specifies the LLM to use for generating the function or method code.

- **`dynamic_file`** *(str, optional)*  
  Path to the file where the dynamically generated function/method code will be stored. Defaults to a file in the same directory as the decorated function or method.

- **`dynamic_test_file`** *(str, optional)*  
  Path to the file where generated unit test code will be stored, if unit testing is enabled.

- **`extra_info`** *(str, optional)*  
  Additional information or examples to provide context to the LLM for code generation.

- **`fix_dynamically`** *(bool, default=True)*  
  If `True`, the decorator attempts to fix runtime errors dynamically by generating corrected code using the LLM.

- **`error_trials`** *(int, default=3)*  
  The number of attempts the LLM should make to fix runtime errors.

- **`error_model`** *(str, default="gpt-4o")*  
  The LLM model to use for generating fixes for runtime errors.

- **`error_prompt`** *(str, optional)*  
  A custom prompt to guide the LLM for fixing runtime errors. If `None`, a default error-fixing prompt is used.

- **`hs_condition`** *(callable, optional)*  
  A condition that, when met, triggers hot-swapping of the function or method with a new dynamically generated version.

- **`hs_model`** *(str, default="gpt-4o")*  
  The LLM model to use for hot-swapping logic when the `hs_condition` is met.

- **`hs_prompt`** *(str, optional)*  
  A custom prompt to guide the LLM for hot-swapping the function or method. Must include the {code} placeholder to get the current version of the function/method.

- **`execution_context`** *(dict, optional)*  
  A dictionary of additional context or variables required during code execution or testing.

- **`keep_ok_version`** *(bool, default=True)*  
  If `True`, retains the last known working version of the dynamically generated code before attempting any fixes or updates.

- **`unit_test`** *(bool, default=False)*  
  (Only for functions) If `True`, the decorator generates and executes unit tests for the dynamic code. Unit testing is skipped if set to `False`.

### Usage Example: Dynamic function

```python
@dynamic_function()
def calculate_average(numbers):
    """
    Calculates the average of a list of numbers.

    Args:
        numbers (list of float): A list of numeric values.

    Returns:
        float: The average of the list.

    Raises:
        ValueError: If the list is empty or contains invalid values.
    """
    pass
```

### Usage Example: Dynamic Methods in a Class 1

The `@dynamic_function` decorator can be applied to methods within a class to dynamically generate, test, and fix their implementation.

```python
from dynamic_functioneer.dynamic_decorator import dynamic_function

class TaskManager:
    """
    A class to represent a task management system.
    """

    def __init__(self):
        """
        Initializes the task manager with an empty task dictionary.
        """
        self.tasks = {}

    @dynamic_function(
        model="meta-llama/llama-3.2-3b-instruct:free",
        extra_info="Adds a new task with a given priority. Updates priority if the task already exists.",
        error_model="meta-llama/llama-3.2-3b-instruct:free"
    )
    def add_task(self, task_name, priority):
        """
        Adds or updates a task in the task list.

        Args:
            task_name (str): The name of the task.
            priority (int): The priority level of the task.

        Returns:
            str: Confirmation message about the added or updated task.
        """
        pass

    @dynamic_function(
        model="meta-llama/llama-3.2-3b-instruct:free",
        extra_info="Retrieves the priority of a given task. Raises an error if the task does not exist.",
        error_model="meta-llama/llama-3.2-3b-instruct:free"
    )
    def get_task_priority(self, task_name):
        """
        Retrieves the priority of a specified task.

        Args:
            task_name (str): The name of the task.

        Returns:
            int: The priority level of the task.

        Raises:
            KeyError: If the task does not exist.
        """
        pass


# Example Usage
if __name__ == "__main__":
    manager = TaskManager()

    # Add tasks
    print(manager.add_task("Finish report", 1))
    print(manager.add_task("Buy groceries", 2))

    # Update an existing task
    print(manager.add_task("Finish report", 3))

    # Retrieve task priorities
    print(manager.get_task_priority("Finish report"))  # Output: 3
    print(manager.get_task_priority("Buy groceries"))  # Output: 2
```

### Usage Example: Dynamic Methods in a Class 2

Example using different models for creating code and fix errors.

```python

from dynamic_functioneer.dynamic_decorator import dynamic_function

class StudentGrades:
    """
    A class to manage student grades in a course.
    """

    def __init__(self):
        """
        Initializes the StudentGrades class with an empty dictionary for student records.
        """
        self.grades = {}

    @dynamic_function(
        model="meta-llama/llama-3.2-1b-instruct:free",
        extra_info="Adds or updates a student's grade for a specific course.",
        error_model="chatgpt-4o-latest"
    )

    def add_grade(self, student_name, course_name, grade):
        """
        Adds or updates a student's grade for a specific course.

        Args:
            student_name (str): The name of the student.
            course_name (str): The name of the course.
            grade (float): The grade to assign to the student for the course.

        Returns:
            str: Confirmation message about the added or updated grade.

        Examples:
            >>> grades = StudentGrades()
            >>> grades.add_grade("Alice", "Math", 95.0)
            'Added grade for Alice in Math with grade 95.0'

            >>> grades.add_grade("Alice", "Math", 98.0)
            'Updated grade for Alice in Math to 98.0'

            >>> grades.grades
            {'Alice': {'Math': 98.0}}
        """

        pass


    @dynamic_function(
        model="gpt-4o-mini",
        extra_info="Retrieves the grade for a student in a specific course. Raises an error if the student or course is not found.",
        error_model="chatgpt-4o-latest"
    )

    def get_grade(self, student_name, course_name):
        """
        Retrieves the grade for a specific course.

        Args:
            student_name (str): The name of the student.
            course_name (str): The name of the course.

        Returns:
            float: The grade for the course.

        Raises:
            KeyError: If the student or course does not exist.

        Examples:
            >>> grades = StudentGrades()
            >>> grades.add_grade("Alice", "Math", 95.0)
            >>> grades.get_grade("Alice", "Math")
            95.0

            >>> grades.get_grade("Bob", "Math")
            Traceback (most recent call last):
                ...
            KeyError: "Student 'Bob' not found."

            >>> grades.get_grade("Alice", "Science")
            Traceback (most recent call last):
                ...
            KeyError: "Course 'Science' not found for student 'Alice'."
        """

        pass


# Example Usage
if __name__ == "__main__":
    grades = StudentGrades()

    # Add grades
    print(grades.add_grade("Alice", "Math", 95.0))
    print(grades.add_grade("Bob", "Math", 88.5))
    print(grades.add_grade("Alice", "Science", 89.0))

    # # Update a grade
    print(grades.add_grade("Alice", "Math", 98.0))  # Should update the Math grade for Alice

    # # Retrieve grades
    print(f"Alice's Math grade: {grades.get_grade('Alice', 'Math')}")  # Output: 98.0
    print(f"Bob's Math grade: {grades.get_grade('Bob', 'Math')}")      # Output: 88.5
    print(f"Alice's Science grade: {grades.get_grade('Alice', 'Science')}")  # Output: 89.0

```
