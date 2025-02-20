# test_class_extractor.py

import pytest
import inspect
from dynamic_functioneer.code_analyzer import ClassExtractor

# Sample class for testing
class SampleClass:
    """
    This is a sample class for testing purposes.
    """

    def sample_method(self):
        """
        This is a sample method.
        """
        pass

def test_extract_class_definition():
    class_def = ClassExtractor.extract_class_definition(SampleClass)
    assert "class SampleClass" in class_def
    assert "def sample_method" in class_def

def test_extract_method_header():
    method_header = ClassExtractor.extract_method_header(SampleClass, 'sample_method')
    assert "def sample_method" in method_header
    assert '"""This is a sample method."""' in method_header

def test_extract_class_and_method(tmp_path):
    # Create a temporary Python script
    script_content = '''
class TempClass:
    """
    Temporary class for testing.
    """
    def temp_method(self):
        """
        Temporary method.
        """
        pass
'''
    script_file = tmp_path / "temp_script.py"
    script_file.write_text(script_content)

    class_def, method_header = ClassExtractor.extract_class_and_method(script_file, 'TempClass', 'temp_method')
    assert "class TempClass" in class_def
    assert "def temp_method" in method_header
    assert '"""Temporary method."""' in method_header
