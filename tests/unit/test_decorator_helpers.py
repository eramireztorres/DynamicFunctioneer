
import pytest
import inspect
import ast
from dynamic_functioneer.utils.introspection import extract_class_code, is_class_method


class MyClassForTest:
    def my_method(self, a, b):
        return a + b

    @staticmethod
    def my_static_method(a, b):
        return a + b

class TestDecoratorHelpers:
    def test_extract_class_code(self):
        module = inspect.getmodule(MyClassForTest)
        class_code = extract_class_code(inspect.getmodule(self.__class__), "TestDecoratorHelpers")
        
        # Basic check to ensure it's a class definition
        assert 'class MyClassForTest:' in class_code
        assert 'def my_method(self, a, b):' in class_code

    def test_is_class_method(self):
        assert is_class_method(MyClassForTest.my_method) is True
        assert is_class_method(MyClassForTest.my_static_method) is False

    def test_is_class_method_with_nested_function(self):
        def outer_function():
            def nested_function(self):
                pass
            return nested_function
        
        assert is_class_method(outer_function()) is False
