# 

import pytest

##############################
# Minimal stubs or real imports
##############################
# If you have these in the same package, you can do:
from dynamic_functioneer.llm_response_cleaner import LLMResponseCleaner
from dynamic_functioneer.llm_response_cleaner import CodeValidator
#
# For demonstration, we'll define a minimal version of LLMResponseCleaner
# that references the previously improved code in your snippet.


####################################
#           UNIT TESTS             #
####################################

def test_extract_valid_code_no_reconstruction():
    """
    If the code is already valid, it should pass through without needing reconstruction.
    """
    response = """```python
def add(a, b):
    return a + b
```"""
    cleaned = LLMResponseCleaner.clean_response(response)
    assert "def add(a, b)" in cleaned
    assert "return a + b" in cleaned


def test_invalid_code_triggers_reconstruction():
    """
    If the code is invalid, we try reconstruct_code. 
    Example: unclosed docstring or missing indentation
    """
    response = """```python
def foo():
    \"\"\"Unclosed docstring
print("some code")
```"""
    cleaned = LLMResponseCleaner.clean_response(response)
    # Because the docstring was unclosed, reconstruction should add '"""'
    # Also the second line might get indented
    assert "def foo()" in cleaned
    assert '"""' in cleaned  # appended docstring closer
    assert CodeValidator.validate_code(cleaned), "Reconstruction should yield valid code."

def test_reconstruction_fails_and_raises():
    """
    If code is so broken that reconstruction can't fix it, raise ValueError.
    E.g. missing colon on the def line.
    """
    response = """```python
def broken
    pass
```"""
    with pytest.raises(ValueError, match="reconstruction"):
        LLMResponseCleaner.clean_response(response)

def test_select_function_by_name():
    """
    Test that we can pass a function_name to pick only that function from the code.
    """
    response = """```python
def first():
    pass

def second():
    return 2
```"""
    # We only want 'second'
    cleaned = LLMResponseCleaner.clean_response(response, function_name="second")
    assert "def second()" in cleaned
    assert "def first()" not in cleaned

def test_select_function_not_found_raises():
    """
    If the user asks for a function name that doesn't exist, raise ValueError.
    """
    response = """```python
def first():
    pass
```"""
    with pytest.raises(ValueError, match="Function selection failed"):
        LLMResponseCleaner.clean_response(response, function_name="second")

