import inspect
import ast
from pathlib import Path
import textwrap

class CodeAnalyzer:
    """
    Analyzes Python code to determine whether a decorator is applied to a function or method
    and extracts relevant definitions for context.
    """

    @staticmethod
    def is_method(obj):
        """
        Checks whether the given object is a method of a class.

        Args:
            obj (object): The object to check.

        Returns:
            bool: True if the object is a method, False otherwise.
        """
        return inspect.ismethod(obj) or inspect.isfunction(obj) and '.' in obj.__qualname__

    @staticmethod
    def get_class_definition(obj):
        """
        Extracts the full class definition for a given method.

        Args:
            obj (object): The method for which the class definition is needed.

        Returns:
            str: The full class definition as a string.

        Raises:
            ValueError: If the object is not a method or its class cannot be found.
        """
        if not CodeAnalyzer.is_method(obj):
            raise ValueError("The provided object is not a method.")
        cls = obj.__qualname__.split('.')[0]
        module = inspect.getmodule(obj)
        if module is None:
            raise ValueError("Could not find the module for the provided object.")
        cls_obj = getattr(module, cls, None)
        if not inspect.isclass(cls_obj):
            raise ValueError("Could not find the class definition.")
        return inspect.getsource(cls_obj)

    @staticmethod
    def get_function_definition(obj):
        """
        Extracts the full function definition for a given function.

        Args:
            obj (object): The function to extract.

        Returns:
            str: The full function definition as a string.

        Raises:
            ValueError: If the object is not a function.
        """
        if not inspect.isfunction(obj):
            raise ValueError("The provided object is not a function.")
        return inspect.getsource(obj)

    @staticmethod
    def extract_definitions_from_script(script_path):
        """
        Extracts all function and class definitions from a script for context.

        Args:
            script_path (str or Path): Path to the script file.

        Returns:
            dict: A dictionary containing class and function definitions:
                {
                    "classes": {class_name: class_code, ...},
                    "functions": {function_name: function_code, ...}
                }

        Raises:
            FileNotFoundError: If the script file does not exist.
        """
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script file '{script_path}' not found.")
        
        with open(script_path, "r") as file:
            tree = ast.parse(file.read())

        classes = {}
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                class_code = ast.get_source_segment(file.read(), node)
                classes[class_name] = class_code
            elif isinstance(node, ast.FunctionDef):
                function_name = node.name
                function_code = ast.get_source_segment(file.read(), node)
                functions[function_name] = function_code

        return {"classes": classes, "functions": functions}

# # Example function
# def calculate_average(numbers):
#     """
#     Example function for testing.
#     """
#     pass

# # Example method in a class
# class ExampleClass:
#     def example_method(self):
#         """
#         Example method for testing.
#         """
#         pass

# # Analyze objects
# analyzer = CodeAnalyzer()
# print(analyzer.is_method(calculate_average))  # False
# print(analyzer.get_function_definition(calculate_average))  # Full function code

# print(analyzer.is_method(ExampleClass.example_method))  # True
# print(analyzer.get_class_definition(ExampleClass.example_method))  # Full class code


class ClassExtractor:
    """
    Extracts components from a class definition.
    """

    @staticmethod
    def extract_class_definition(cls):
        """
        Extracts the complete definition of a class, including its docstring and methods.

        Args:
            cls (type): The class object.

        Returns:
            str: The full class definition as a string.

        Raises:
            ValueError: If the provided object is not a class.
        """
        if not inspect.isclass(cls):
            raise ValueError("The provided object is not a class.")
        return inspect.getsource(cls)

    @staticmethod
    def extract_method_header(cls, method_name):
        """
        Extracts the method header and docstring for a specific method in the class.

        Args:
            cls (type): The class object.
            method_name (str): The name of the method to extract.

        Returns:
            str: The method header and its docstring as a string.

        Raises:
            ValueError: If the method is not found in the class.
        """
        if not inspect.isclass(cls):
            raise ValueError("The provided object is not a class.")
        method = getattr(cls, method_name, None)
        if not inspect.isfunction(method):
            raise ValueError(f"Method '{method_name}' not found in the class.")
        
        # Extract the source code and parse the AST
        method_source = inspect.getsource(method)
        method_ast = ast.parse(textwrap.dedent(method_source)).body[0]  # Dedent to avoid indent issues

        # Build the method header
        method_header = f"def {method_ast.name}({', '.join(arg.arg for arg in method_ast.args.args)}):"

        # Extract and format the docstring
        method_docstring = ast.get_docstring(method_ast)
        if method_docstring:
            method_docstring = textwrap.indent(f'"""{method_docstring}"""', "    ")

        # Combine header and docstring
        return f"{method_header}\n{method_docstring}" if method_docstring else method_header

    @staticmethod
    def extract_class_and_method(script_path, class_name, method_name):
        """
        Extracts the full class definition and a specific method's header from a script.

        Args:
            script_path (str): Path to the Python script file.
            class_name (str): The name of the class.
            method_name (str): The name of the method to extract.

        Returns:
            tuple: (class_definition, method_header)
        """
        with open(script_path, "r") as file:
            tree = ast.parse(file.read())

        class_node = next((node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name), None)
        if not class_node:
            raise ValueError(f"Class '{class_name}' not found in the script.")

        method_node = next((node for node in class_node.body if isinstance(node, ast.FunctionDef) and node.name == method_name), None)
        if not method_node:
            raise ValueError(f"Method '{method_name}' not found in the class '{class_name}'.")

        class_definition = ast.get_source_segment(file.read(), class_node)
        method_header = f"def {method_node.name}({', '.join(arg.arg for arg in method_node.args.args)}):"
        method_docstring = ast.get_docstring(method_node)
        return class_definition, f"{method_header}\n    \"\"\"{method_docstring}\"\"\""


class ShoppingCart:
    """
    A class to represent a shopping cart.

    Attributes:
        items (list): List of items in the cart.
    """

    def __init__(self):
        """
        Initializes the shopping cart with an empty list of items.
        """
        self.items = []

    def add_item(self, item):
        """
        Adds an item to the shopping cart.

        Args:
            item (str): The item to add.
        """
        self.items.append(item)


# # Example
# extractor = ClassExtractor()

# # Full class definition
# class_def = extractor.extract_class_definition(ShoppingCart)
# print("Class Definition:")
# print(class_def)

# # Method header for add_item
# method_header = extractor.extract_method_header(ShoppingCart, "add_item")
# print("\nMethod Header:")
# print(method_header)
