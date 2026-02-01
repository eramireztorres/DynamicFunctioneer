import pytest
from unittest.mock import MagicMock, patch
from dynamic_functioneer.code_management.hot_swap_executor import HotSwapExecutor

@pytest.fixture
def mock_dependencies():
    code_manager = MagicMock()
    llm_generator = MagicMock()
    return code_manager, llm_generator

@pytest.fixture
def executor(mock_dependencies):
    code_manager, llm_generator = mock_dependencies
    return HotSwapExecutor(code_manager, llm_generator)

class TestHotSwapExecutor:

    def test_execute_workflow_success(self, executor, mock_dependencies):
        code_manager, _ = mock_dependencies
        code_manager.save_test_code.return_value = "test_file.py"
        code_manager.run_test.return_value = True

        result = executor.execute_workflow("test_func", "default test code", script_dir=".")
        
        assert result is True
        code_manager.run_test.assert_called_once()

    def test_execute_workflow_failure(self, executor, mock_dependencies):
        code_manager, _ = mock_dependencies
        code_manager.save_test_code.return_value = "test_file.py"
        code_manager.run_test.return_value = False # Test fails

        result = executor.execute_workflow("test_func", "default test code", script_dir=".")
        
        # According to implementation, it returns True even if test fails (just logs warning)
        assert result is True 
        code_manager.run_test.assert_called_once()

    def test_apply_error_correction_success(self, executor, mock_dependencies):
        code_manager, _ = mock_dependencies
        
        # Mock run_test to return True (correction verified)
        code_manager.run_test.return_value = True
        code_manager.save_test_code.return_value = "test_file.py"

        result = executor._apply_error_correction(
            function_name="func", 
            corrected_code="corrected", 
            test_code="test_code", 
            script_dir="."
        )
        
        assert result is True
        code_manager.save_code.assert_called_with("corrected")
        code_manager.run_test.assert_called_once()

    def test_apply_error_correction_failure(self, executor, mock_dependencies):
        code_manager, _ = mock_dependencies
        
        # Mock run_test to return False (correction failed verification)
        code_manager.run_test.return_value = False
        code_manager.save_test_code.return_value = "test_file.py"

        result = executor._apply_error_correction(
            function_name="func", 
            corrected_code="corrected", 
            test_code="test_code", 
            script_dir="."
        )
        
        assert result is False
        code_manager.save_code.assert_called_with("corrected")

    def test_perform_hot_swap(self, executor, mock_dependencies):
        code_manager, _ = mock_dependencies
        code_manager.code_exists.return_value = True
        code_manager.load_code.return_value = "current code"
        
        # Patch LLMCodeGenerator class because perform_hot_swap creates a new instance
        with patch('dynamic_functioneer.code_management.hot_swap_executor.LLMCodeGenerator') as MockLLMGenClass, \
             patch('dynamic_functioneer.code_management.hot_swap_executor.LLMResponseCleaner.clean_response', return_value="improved code"):
            
            mock_gen_instance = MockLLMGenClass.return_value
            mock_gen_instance.hot_swap_improvement.return_value = "improved code raw"
            
            result = executor.perform_hot_swap("test_func")
            
            assert result is True
            mock_gen_instance.hot_swap_improvement.assert_called_once()
            code_manager.save_code.assert_called_with("improved code")
