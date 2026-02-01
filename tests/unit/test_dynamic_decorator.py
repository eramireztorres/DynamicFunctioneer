
import pytest
from unittest.mock import MagicMock, patch

from dynamic_functioneer.dynamic_decorator import dynamic_function


@pytest.fixture
def mock_dynamic_components():
    """Mocks all external dependencies of the dynamic_decorator."""
    with patch('dynamic_functioneer.dynamic_execution_handler.DynamicCodeManager') as mock_code_manager, \
         patch('dynamic_functioneer.dynamic_execution_handler.LLMCodeGenerator') as mock_llm_generator, \
         patch('dynamic_functioneer.dynamic_execution_handler.HotSwapExecutor') as mock_hot_swap_executor, \
         patch('dynamic_functioneer.dynamic_execution_handler.LLMResponseCleaner.clean_response') as mock_llm_cleaner, \
         patch('dynamic_functioneer.dynamic_execution_handler.DynamicFunctionCleaner') as mock_dynamic_cleaner, \
         patch('dynamic_functioneer.code_management.test_import_injector.TestImportInjector') as mock_import_injector, \
         patch('os.path.join', return_value='mock/path/to/file.py'), \
         patch('os.path.dirname', return_value='mock/path/to'), \
         patch('os.path.basename', return_value='file.py'), \
         patch('os.path.splitext', return_value=('file', '.py')):
        
        mock_code_manager.return_value.code_exists.return_value = True
        mock_code_manager.return_value.load_function.return_value = lambda *args, **kwargs: "mocked function"
        mock_llm_cleaner.side_effect = lambda x: x
        mock_dynamic_cleaner.return_value.clean_dynamic_function.side_effect = lambda: mock_dynamic_cleaner.call_args[0][0]

        yield {
            "code_manager": mock_code_manager,
            "llm_generator": mock_llm_generator,
            "hot_swap_executor": mock_hot_swap_executor,
            "llm_cleaner": mock_llm_cleaner,
            "dynamic_cleaner": mock_dynamic_cleaner,
            "import_injector": mock_import_injector,
        }

def test_decorator_applies_without_error(mock_dynamic_components):
    """Tests that the decorator can be applied to a function without crashing."""
    @dynamic_function()
    def example_function():
        """This is a docstring."""
        return "original"

    assert example_function is not None
    # The decorator replaces the original function with a wrapper
    assert example_function.__name__ == 'example_function'


def test_decorated_function_executes(mock_dynamic_components):
    """Tests that a decorated function can be called and returns the mocked value."""
    @dynamic_function()
    def example_function(a, b):
        """This is a docstring."""
        return a + b

    result = example_function(2, 3)
    assert result == "mocked function"
    
class MyClass:
    @dynamic_function()
    def example_method(self, a, b):
        """This is a docstring."""
        return a - b

def test_decorated_method_executes(mock_dynamic_components):
    """Tests that a decorated method can be called and returns the mocked value."""
    instance = MyClass()
    result = instance.example_method(5, 3)
    assert result == "mocked function"

def test_code_generation_when_file_does_not_exist(mock_dynamic_components):
    """Tests that code is generated when the dynamic file doesn't exist."""
    mock_code_manager = mock_dynamic_components["code_manager"].return_value
    mock_code_manager.code_exists.return_value = False
    mock_llm_generator = mock_dynamic_components["llm_generator"].return_value
    mock_llm_generator.initial_code_generation.return_value = "def example_function(a, b): return a * b"

    @dynamic_function()
    def example_function(a, b):
        """This is a docstring."""
        return a + b

    example_function(2, 3)

    mock_llm_generator.initial_code_generation.assert_called_once()
    mock_code_manager.save_code.assert_called_once_with('def example_function(a, b): return a * b')

def test_hot_swapping_is_triggered(mock_dynamic_components):
    """Tests that hot-swapping is triggered when hs_condition is True."""
    mock_hot_swap_executor = mock_dynamic_components["hot_swap_executor"].return_value

    @dynamic_function(hs_condition=True)
    def example_function(a, b):
        """This is a docstring."""
        return a + b

    example_function(2, 3)

    mock_hot_swap_executor.perform_hot_swap.assert_called_once()

def test_dynamic_error_fixing_is_triggered(mock_dynamic_components):
    """Tests that dynamic error fixing is triggered on runtime error."""
    mock_code_manager = mock_dynamic_components["code_manager"].return_value
    failing_function = MagicMock(side_effect=RuntimeError("mock error"))
    fixed_function = MagicMock(return_value="fixed")
    mock_code_manager.load_function.side_effect = [failing_function, fixed_function]
    mock_llm_generator = mock_dynamic_components["llm_generator"].return_value
    mock_llm_generator.fix_runtime_error.return_value = "def example_function(a, b): return a / b"

    mock_hot_swap_executor = mock_dynamic_components["hot_swap_executor"].return_value
    mock_hot_swap_executor._apply_error_correction.return_value = True

    @dynamic_function(fix_dynamically=True, error_trials=1)
    def example_function(a, b):
        """This is a docstring."""
        return a + b

    result = example_function(2, 3)

    assert result == "fixed"
    mock_llm_generator.fix_runtime_error.assert_called_once()

def test_unit_test_generation_is_triggered(mock_dynamic_components):
    """Tests that unit test generation is triggered when unit_test is True."""
    mock_code_manager = mock_dynamic_components["code_manager"].return_value
    mock_code_manager.code_exists.return_value = False
    mock_llm_generator = mock_dynamic_components["llm_generator"].return_value
    mock_llm_generator.initial_code_generation.return_value = "def example_function(a, b): return a * b"
    mock_llm_generator.generate_function_test_logic.return_value = "def test_example_function(): assert example_function(2, 3) == 6"

    @dynamic_function(unit_test=True)
    def example_function(a, b):
        """This is a docstring."""
        return a + b

    example_function(2, 3)

    mock_llm_generator.generate_function_test_logic.assert_called_once()

