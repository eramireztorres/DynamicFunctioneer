import pytest
import logging

##########################
# STUB for CodeValidator #
##########################
class CodeValidator:
    @staticmethod
    def validate_code(code: str) -> bool:
        """
        A stub version of CodeValidator. 
        Feel free to replace this with an actual implementation.
        """
        import ast
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

################################
# Class Under Test (unchanged) #
################################
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

########################
#       TESTS         #
########################

def test_missing_def_or_class():
    """
    If code has neither 'def' nor 'class', it should raise ValueError immediately.
    """
    input_code = """print("Hello, world!")"""
    with pytest.raises(ValueError, match="Missing 'def' or 'class'"):
        CodeReconstructor.reconstruct_code(input_code)

def test_unclosed_docstring(caplog):
    """
    Tests that unclosed triple-quote docstrings get closed automatically.
    """
    input_code = '''def foo():
    """
    A docstring that never ends
    pass
'''
    with caplog.at_level(logging.WARNING):
        output_code = CodeReconstructor.reconstruct_code(input_code)

    # We expect a warning about unclosed docstring
    assert any("Detected unclosed docstring" in rec.message for rec in caplog.records), \
        "No warning about unclosed docstring found in logs."

    # The result should now parse
    # Check that we appended a docstring closer:
    assert '"""' in output_code.splitlines()[-1], "Expected a closing triple quote on the last line."

def test_proper_indentation():
    """
    Tests that lines after the 'def' statement get indented by CodeReconstructor.
    """
    input_code = """def bar():
pass
"""
    output_code = CodeReconstructor.reconstruct_code(input_code)

    # Expect 'def bar():' on one line, then 4 spaces indentation for the next
    lines = output_code.splitlines()
    assert lines[0] == "def bar():"
    assert lines[1].startswith("    pass"), "The 'pass' line should be indented by 4 spaces."

def test_already_valid_code():
    """
    If code is already valid, it should pass reconstruction without errors and remain unchanged except for minimal indentation changes.
    """
    input_code = """def baz():
    print("I am valid!")
"""
    output_code = CodeReconstructor.reconstruct_code(input_code)
    # The code is valid, so no errors. Should remain basically the same,
    # though the indentation logic won't break anything here.
    assert "def baz()" in output_code
    assert "print(" in output_code

def test_invalid_code_after_reconstruction():
    """
    Forces the final code to remain invalid, expecting a ValueError.
    e.g., if code is missing a colon or has a random syntax error that can't be fixed with indentation or docstring closure.
    """
    # Missing colon for the def line
    input_code = """def bad_syntax
  some broken line
"""
    with pytest.raises(ValueError, match="still invalid"):
        CodeReconstructor.reconstruct_code(input_code)
