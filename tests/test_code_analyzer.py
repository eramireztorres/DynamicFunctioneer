# test_code_analyzer.py

import pytest
import inspect
import ast
from dynamic_functioneer.code_analyzer import CodeAnalyzer

# Sample function and class for testing
def sample_function():
    pass

class SampleClass:
    def sample_method(self):
        pass

def test_is_method():
    assert not CodeAnalyzer.is_method(sample_function)
    assert CodeAnalyzer.is_method(SampleClass().sample_method)

def test_get_class_definition():
    method = SampleClass().sample_method
    class_def = CodeAnalyzer.get_class_definition(method)
    assert "class SampleClass" in class_def
    assert "def sample_method" in class_def

def test_extract_definitions_from_script(tmp_path):
    # Create a temporary Python script
    script_content = '''
def temp_function():
    pass

class TempClass:
    def temp_method(self):
        pass
'''
    script_file = tmp_path / "temp_script.py"
    script_file.write_text(script_content)

    definitions = CodeAnalyzer.extract_definitions_from_script(script_file)
    assert "TempClass" in definitions["classes"]
    assert "temp_function" in definitions["functions"]
