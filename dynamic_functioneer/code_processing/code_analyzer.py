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
        return inspect.ismethod(obj) or (inspect.isfunction(obj) and '.' in obj.__qualname__)

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
        
        cls_name = obj.__qualname__.split('.')[0]
        module = inspect.getmodule(obj)
        if not module:
            raise ValueError("Could not find the module for the provided object.")
        
        cls_obj = getattr(module, cls_name, None)
        if not inspect.isclass(cls_obj):
            raise ValueError("Class definition could not be found.")
        
        return inspect.getsource(cls_obj)

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
        """
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script file '{script_path}' not found.")
        
        with open(script_path, "r") as file:
            source = file.read()
            tree = ast.parse(source)

        classes = {}
        functions = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_code = ast.get_source_segment(source, node)
                classes[node.name] = class_code
            elif isinstance(node, ast.FunctionDef):
                function_code = ast.get_source_segment(source, node)
                functions[node.name] = function_code

        return {"classes": classes, "functions": functions}



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
        if not method or not inspect.isfunction(method):
            raise ValueError(f"Method '{method_name}' not found in the class.")

        decorators = inspect.getclosurevars(method).nonlocals.get('decorators', [])
        decorators_str = "\n".join([f"@{d}" for d in decorators]) if decorators else ""

        method_source = inspect.getsource(method)
        method_ast = ast.parse(textwrap.dedent(method_source)).body[0]

        method_header = f"def {method_ast.name}({', '.join(arg.arg for arg in method_ast.args.args)}):"
        docstring = ast.get_docstring(method_ast)

        if docstring:
            docstring = textwrap.indent(f'"""{docstring}"""', "    ")

        return f"{decorators_str}\n{method_header}\n{docstring}" if docstring else method_header

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
            source = file.read()
            tree = ast.parse(source)

        class_node = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name), None)
        if not class_node:
            raise ValueError(f"Class '{class_name}' not found in the script.")

        method_node = next((n for n in class_node.body if isinstance(n, ast.FunctionDef) and n.name == method_name), None)
        if not method_node:
            raise ValueError(f"Method '{method_name}' not found in the class '{class_name}'.")

        class_definition = ast.get_source_segment(source, class_node)
        method_header = f"def {method_node.name}({', '.join(arg.arg for arg in method_node.args.args)}):"
        docstring = ast.get_docstring(method_node)

        return class_definition, f"{method_header}\n    \"\"\"{docstring}\"\"\"" if docstring else method_header


