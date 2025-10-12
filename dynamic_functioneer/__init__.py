"""
DynamicFunctioneer - Auto-generate and improve Python methods with decorators powered by LLMs.

This package provides a decorator-based approach to dynamically generate, test, and improve
Python functions and methods using Large Language Models.
"""

import sys

# Main public API - the dynamic_function decorator
from dynamic_functioneer.dynamic_decorator import dynamic_function

# Configuration
from dynamic_functioneer.config import (
    DynamicFunctioneerConfig,
    ModelConfig,
    ExecutionConfig,
    PathConfig,
    get_config,
    set_config,
    reset_config,
)

# Protocols
from dynamic_functioneer.protocols import (
    ModelAPIProtocol,
    ConversationalModelProtocol,
    TestRunnerProtocol,
    CodeLoaderProtocol,
    CodeStorageProtocol,
)

# Model APIs - for backward compatibility, expose all model classes
from dynamic_functioneer.models import (
    BaseModelAPI,
    ModelAPIFactory,
    OpenAIModelAPI,
    AnthropicModelAPI,
    GeminiModelAPI,
    LlamaModelAPI,
    LangGraphModelAPI,
)

# Code Management - for backward compatibility
from dynamic_functioneer.code_management import (
    CodeFileManager,
    TestFileManager,
    DynamicModuleLoader,
    DynamicCodeManager,
    TestExecutionStrategy,
    SubprocessTestRunner,
    PytestRunner,
    UnittestRunner,
    HotSwapExecutor,
)

# Code Generation - for backward compatibility
from dynamic_functioneer.code_generation import (
    LLMCodeGenerator,
    PromptManager,
    BoilerplateManager,
)

# Code Processing - for backward compatibility
from dynamic_functioneer.code_processing import (
    CodeAnalyzer,
    LLMResponseCleaner,
    DynamicFunctionCleaner,
)

# Utils - for backward compatibility
from dynamic_functioneer.utils import (
    DynamicFileManager,
)

__version__ = "0.2.0"  # Updated version with restructuring

__all__ = [
    # Main decorator
    'dynamic_function',

    # Configuration
    'DynamicFunctioneerConfig',
    'ModelConfig',
    'ExecutionConfig',
    'PathConfig',
    'get_config',
    'set_config',
    'reset_config',

    # Protocols
    'ModelAPIProtocol',
    'ConversationalModelProtocol',
    'TestRunnerProtocol',
    'CodeLoaderProtocol',
    'CodeStorageProtocol',

    # Models
    'BaseModelAPI',
    'ModelAPIFactory',
    'OpenAIModelAPI',
    'AnthropicModelAPI',
    'GeminiModelAPI',
    'LlamaModelAPI',
    'LangGraphModelAPI',

    # Code Management
    'CodeFileManager',
    'TestFileManager',
    'DynamicModuleLoader',
    'DynamicCodeManager',
    'TestExecutionStrategy',
    'SubprocessTestRunner',
    'PytestRunner',
    'UnittestRunner',
    'HotSwapExecutor',

    # Code Generation
    'LLMCodeGenerator',
    'PromptManager',
    'BoilerplateManager',

    # Code Processing
    'CodeAnalyzer',
    'LLMResponseCleaner',
    'DynamicFunctionCleaner',

    # Utils
    'DynamicFileManager',
]


# ============================================================================
# BACKWARD COMPATIBILITY: Create module aliases for old import paths
# ============================================================================
# This allows old code like "from dynamic_functioneer.model_api_factory import X"
# to continue working even though the file is now in dynamic_functioneer/models/

# Create module aliases
sys.modules['dynamic_functioneer.model_api_factory'] = sys.modules['dynamic_functioneer.models.model_api_factory']
sys.modules['dynamic_functioneer.base_model_api'] = sys.modules['dynamic_functioneer.models.base_model_api']
sys.modules['dynamic_functioneer.openai_model_api'] = sys.modules['dynamic_functioneer.models.openai_model_api']
sys.modules['dynamic_functioneer.anthropic_model_api'] = sys.modules['dynamic_functioneer.models.anthropic_model_api']
sys.modules['dynamic_functioneer.gemini_model_api'] = sys.modules['dynamic_functioneer.models.gemini_model_api']
sys.modules['dynamic_functioneer.llama_model_api'] = sys.modules['dynamic_functioneer.models.llama_model_api']
sys.modules['dynamic_functioneer.langgraph_model_api'] = sys.modules['dynamic_functioneer.models.langgraph_model_api']

sys.modules['dynamic_functioneer.dynamic_code_manager'] = sys.modules['dynamic_functioneer.code_management.dynamic_code_manager']
sys.modules['dynamic_functioneer.code_storage'] = sys.modules['dynamic_functioneer.code_management.code_storage']
sys.modules['dynamic_functioneer.code_loader'] = sys.modules['dynamic_functioneer.code_management.code_loader']
sys.modules['dynamic_functioneer.test_runner'] = sys.modules['dynamic_functioneer.code_management.test_runner']
sys.modules['dynamic_functioneer.hot_swap_executor'] = sys.modules['dynamic_functioneer.code_management.hot_swap_executor']

sys.modules['dynamic_functioneer.llm_code_generator'] = sys.modules['dynamic_functioneer.code_generation.llm_code_generator']
sys.modules['dynamic_functioneer.prompt_manager'] = sys.modules['dynamic_functioneer.code_generation.prompt_manager']
sys.modules['dynamic_functioneer.boilerplate_manager'] = sys.modules['dynamic_functioneer.code_generation.boilerplate_manager']

sys.modules['dynamic_functioneer.code_analyzer'] = sys.modules['dynamic_functioneer.code_processing.code_analyzer']
sys.modules['dynamic_functioneer.llm_response_cleaner'] = sys.modules['dynamic_functioneer.code_processing.llm_response_cleaner']
sys.modules['dynamic_functioneer.prompt_code_cleaner'] = sys.modules['dynamic_functioneer.code_processing.prompt_code_cleaner']

sys.modules['dynamic_functioneer.file_manager'] = sys.modules['dynamic_functioneer.utils.file_manager']
