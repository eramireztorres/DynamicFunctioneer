import pytest
import ast
import re
import os
import textwrap
from dynamic_functioneer.boilerplate_manager import BoilerplateManager


@pytest.fixture
def sample_class_code():
    """
    Returns a sample class definition that includes two methods
    for demonstration purposes.
    """
    return textwrap.dedent("""\
    class SampleClass:
        def existing_method(self, x):
            return x * 2

        def target_method(self, y):
            return y + 10
    """)


@pytest.fixture
def sample_test_code():
    """
    Returns a minimal unittest-based test code snippet.
    """
    return textwrap.dedent("""\
    import unittest

    class TestSample(unittest.TestCase):
        def test_something(self):
            self.assertTrue(True)
    """)


def test_function_based_test(sample_test_code, tmp_path):
    """
    Ensures that add_boilerplate produces the correct output for a function-based test scenario.
    """
    manager = BoilerplateManager(is_method=False)
    script_dir = str(tmp_path)
    import_path = os.path.join(script_dir, "dynamic_function.py")  # Example dynamic file path

    result = manager.add_boilerplate(
        test_code=sample_test_code,
        function_name="dynamic_function",
        import_path=import_path,
        script_dir=script_dir
    )

    # Check that the final script includes a function import and a main block
    assert "from dynamic_function import dynamic_function" in result
    assert "unittest.main()" in result

    # It should preserve the test code lines
    assert "class TestSample(unittest.TestCase):" in result


def test_class_based_test(sample_class_code, sample_test_code, tmp_path):
    """
    Ensures that add_boilerplate produces the correct output for a class-based test scenario,
    replacing the specified method with an import statement in the AST.
    """
    manager = BoilerplateManager(is_method=True, class_code=sample_class_code)
    script_dir = str(tmp_path)
    import_path = os.path.join(script_dir, "dynamic_class_method.py")

    result = manager.add_boilerplate(
        test_code=sample_test_code,
        function_name="target_method",
        import_path=import_path,
        script_dir=script_dir
    )

    # Check that "target_method" was replaced by an import statement
    # We expect something like: from dynamic_class_method import target_method
    assert "from dynamic_class_method import target_method" in result
    # The old 'target_method' code should not remain in the final AST
    assert "def target_method(self, y):" not in result

    # Check that the test code and if-main block are appended
    assert "import unittest" in result
    assert "class TestSample(unittest.TestCase):" in result
    assert "unittest.main()" in result


def test_missing_test_code(tmp_path):
    """
    Ensures that passing empty or None test_code raises ValueError.
    """
    manager = BoilerplateManager(is_method=False)
    script_dir = str(tmp_path)
    import_path = os.path.join(script_dir, "dynamic_function.py")

    with pytest.raises(ValueError, match="Test code is missing or empty"):
        manager.add_boilerplate(
            test_code="",  # Empty code
            function_name="some_function",
            import_path=import_path,
            script_dir=script_dir
        )


def test_class_code_not_provided_for_method(tmp_path):
    """
    Ensures that if is_method=True but no class_code is given,
    the method-based test code generation raises ValueError.
    """
    manager = BoilerplateManager(is_method=True, class_code=None)
    script_dir = str(tmp_path)
    import_path = os.path.join(script_dir, "dynamic_class_method.py")

    with pytest.raises(ValueError, match="Class code must be provided"):
        manager.add_boilerplate(
            test_code="some test code",
            function_name="some_method",
            import_path=import_path,
            script_dir=script_dir
        )


def test_ast_unparse_compatibility(sample_class_code, sample_test_code, tmp_path, monkeypatch):
    """
    Demonstrates how to handle or test if ast.unparse isn't available.
    We artificially remove 'unparse' and verify we raise a ValueError.
    """
    manager = BoilerplateManager(is_method=True, class_code=sample_class_code)
    script_dir = str(tmp_path)
    import_path = os.path.join(script_dir, "dynamic_class_method.py")

    # Temporarily remove ast.unparse to simulate older Python versions
    original_unparse = getattr(ast, "unparse", None)
    monkeypatch.delattr(ast, "unparse", raising=False)

    # Now it should raise a ValueError about 'ast.unparse'
    with pytest.raises(ValueError, match="does not support 'ast.unparse'"):
        manager.add_boilerplate(
            test_code=sample_test_code,
            function_name="target_method",
            import_path=import_path,
            script_dir=script_dir
        )

    # Restore unparse for other tests
    if original_unparse:
        setattr(ast, "unparse", original_unparse)
