import pytest
from unittest.mock import MagicMock, patch
from dynamic_functioneer.code_generation.llm_code_generator import LLMCodeGenerator

@pytest.fixture
def mock_dependencies():
    with patch('dynamic_functioneer.code_generation.llm_code_generator.ModelAPIFactory') as MockFactory, \
         patch('dynamic_functioneer.code_generation.llm_code_generator.PromptManager') as MockPromptManager, \
         patch('dynamic_functioneer.code_generation.llm_code_generator.DynamicFunctionCleaner') as MockCleaner:
        
        mock_model_client = MockFactory.get_model_api.return_value
        mock_prompt_manager = MockPromptManager.return_value
        
        yield mock_model_client, mock_prompt_manager, MockCleaner

class TestLLMCodeGenerator:

    def test_initial_code_generation_success(self, mock_dependencies):
        mock_model_client, mock_prompt_manager, MockCleaner = mock_dependencies
        
        # Setup mocks
        mock_prompt_manager.load_prompt.return_value = "prompt_template"
        mock_prompt_manager.render_prompt.return_value = "rendered_prompt"
        mock_model_client.get_response.return_value = "generated code"
        MockCleaner.return_value.clean_dynamic_function.return_value = "cleaned generated code"

        generator = LLMCodeGenerator()
        code = generator.initial_code_generation("def func(): pass", "docstring")

        assert code == "cleaned generated code"
        mock_model_client.get_response.assert_called_with("rendered_prompt")
        MockCleaner.assert_called_with("generated code")

    def test_generate_code_retry_success(self, mock_dependencies):
        mock_model_client, mock_prompt_manager, MockCleaner = mock_dependencies
        
        mock_prompt_manager.load_prompt.return_value = "prompt"
        mock_prompt_manager.render_prompt.return_value = "rendered"
        
        # Determine failure then success
        mock_model_client.get_response.side_effect = [None, "code"]
        MockCleaner.return_value.clean_dynamic_function.return_value = "cleaned"

        generator = LLMCodeGenerator()
        # Reduce delay for test
        code = generator.generate_code("prompt.txt", {}, retries=3, delay=0)

        assert code == "cleaned"
        assert mock_model_client.get_response.call_count == 2

    def test_generate_code_failure_exhausted_retries(self, mock_dependencies):
        mock_model_client, mock_prompt_manager, _ = mock_dependencies
        
        mock_prompt_manager.load_prompt.return_value = "prompt"
        mock_prompt_manager.render_prompt.return_value = "rendered"
        
        # Always fail (return None or raise Exception)
        mock_model_client.get_response.side_effect = Exception("API Error")

        generator = LLMCodeGenerator()
        
        with pytest.raises(RuntimeError, match="Failed to generate code after 2 attempts"):
            generator.generate_code("prompt.txt", {}, retries=2, delay=0)
    
    def test_method_code_generation(self, mock_dependencies):
        mock_model_client, mock_prompt_manager, MockCleaner = mock_dependencies
        
        mock_prompt_manager.load_prompt.return_value = "method_prompt"
        mock_prompt_manager.render_prompt.return_value = "rendered_method_prompt"
        mock_model_client.get_response.return_value = "method code"
        MockCleaner.return_value.clean_dynamic_function.return_value = "cleaned method code"

        generator = LLMCodeGenerator()
        code = generator.method_code_generation("class A:\n    def foo(self):\n        pass", "foo", "extra")

        assert code == "cleaned method code"
        mock_prompt_manager.render_prompt.assert_called()
        # Check if placeholders contain correct keys?
        # args bound to render_prompt: (prompt_content, placeholders)
        placeholders = mock_prompt_manager.render_prompt.call_args[0][1]
        assert "class_definition" in placeholders
        assert "method_header" in placeholders
