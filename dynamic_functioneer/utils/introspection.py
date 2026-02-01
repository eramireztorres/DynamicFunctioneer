import inspect
import ast
import logging

def extract_class_code(module, class_name):
    """
    Extracts the full class code for the specified class.

    Args:
        module (module): The module containing the class.
        class_name (str): The name of the class.

    Returns:
        str: The full class code as a string.

    Raises:
        ValueError: If the class cannot be found or extracted.
    """
    try:
        source = inspect.getsource(module)
    except (OSError, TypeError) as e:
         raise ValueError(f"Could not retrieve source for module {module}: {e}")

    # Parse the source code into an AST
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Failed to parse module source: {e}")

    # Locate the target class
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            if hasattr(ast, "unparse"):
                return ast.unparse(node)
            else:
                 # Fallback for older python versions if needed, but project requires >=3.11
                 raise ValueError("ast.unparse is not available")

    raise ValueError(f"Class {class_name} not found in module {module.__name__}")


def is_class_method(func):
    """
    Detects if the function is a class method defined at the top level of a class.
    This avoids mistaking nested functions for methods.
    """
    qualname = func.__qualname__
    if "<locals>" in qualname:
        return False  # It's a nested function

    # Check if there's a dot in the qualname (typical for methods: Class.method)
    # However, static methods also have dots but shouldn't be treated as instance methods
    # So we rely on the first argument being 'self' or 'cls'
    
    try:
        params = list(inspect.signature(func).parameters.keys())
        return len(params) > 0 and params[0] in {"self", "cls"}
    except (ValueError, TypeError):
        return False


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
