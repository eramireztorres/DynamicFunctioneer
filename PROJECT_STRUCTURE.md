# DynamicFunctioneer Project Structure

## Overview

The project has been reorganized into a logical, modular structure that separates concerns and makes the codebase easier to navigate and maintain.

## New Directory Structure

```
dynamic_functioneer/
├── __init__.py                    # Main package exports + backward compatibility aliases
├── config.py                      # Configuration management system
├── protocols.py                   # Protocol interfaces (PEP 544)
├── dynamic_decorator.py           # Main @dynamic_function decorator
│
├── models/                        # LLM Model API implementations
│   ├── __init__.py
│   ├── base_model_api.py          # Abstract base class for all models
│   ├── model_api_factory.py      # Factory for creating model instances
│   ├── openai_model_api.py        # OpenAI/GPT models
│   ├── anthropic_model_api.py    # Anthropic/Claude models
│   ├── gemini_model_api.py        # Google Gemini models
│   ├── llama_model_api.py         # Meta Llama/OpenRouter models
│   └── langgraph_model_api.py     # LangGraph integration
│
├── code_management/               # Code storage, loading, and execution
│   ├── __init__.py
│   ├── code_storage.py            # File I/O for code (CodeFileManager, TestFileManager)
│   ├── code_loader.py             # Dynamic module loading (DynamicModuleLoader)
│   ├── dynamic_code_manager.py   # Main code manager (orchestrator)
│   ├── test_runner.py             # Test execution strategies
│   └── hot_swap_executor.py       # Hot-swapping logic
│
├── code_generation/               # LLM-based code generation
│   ├── __init__.py
│   ├── llm_code_generator.py      # Main code generator
│   ├── prompt_manager.py          # Prompt template management
│   └── boilerplate_manager.py     # Boilerplate code handling
│
├── code_processing/               # Code analysis and cleaning
│   ├── __init__.py
│   ├── code_analyzer.py           # Code analysis utilities
│   ├── llm_response_cleaner.py    # Clean LLM responses
│   └── prompt_code_cleaner.py     # Clean/format code blocks
│
└── utils/                         # General utilities
    ├── __init__.py
    └── file_manager.py            # File management utilities
```

---

## Package Descriptions

### 📦 `models/`
**Purpose:** LLM model API implementations

**Contains:**
- Base model API interface
- Factory pattern for creating model instances
- Implementations for different LLM providers (OpenAI, Anthropic, Google, Meta)

**Use when:** You need to add a new LLM provider or modify model interaction logic.

---

### 📦 `code_management/`
**Purpose:** Managing dynamic code lifecycle (storage, loading, execution, testing)

**Contains:**
- File I/O operations for code
- Python module dynamic import/reload
- Test execution strategies (subprocess, pytest, unittest)
- Hot-swapping functionality

**Use when:** You need to modify how code is stored, loaded, or tested.

**Key Classes:**
- `CodeFileManager` - Handles file I/O
- `DynamicModuleLoader` - Handles Python imports
- `TestExecutionStrategy` - Pluggable test runners
- `HotSwapExecutor` - Hot-swapping orchestration

---

### 📦 `code_generation/`
**Purpose:** Generating code using LLMs

**Contains:**
- Main LLM code generator
- Prompt template management
- Boilerplate code handling

**Use when:** You need to modify how code is generated from LLM responses.

**Key Classes:**
- `LLMCodeGenerator` - Main code generation logic
- `PromptManager` - Loads and manages prompt templates

---

### 📦 `code_processing/`
**Purpose:** Processing, analyzing, and cleaning code

**Contains:**
- Code analysis utilities
- LLM response cleaning
- Code formatting and cleanup

**Use when:** You need to modify how LLM responses are parsed or how code is cleaned.

**Key Classes:**
- `LLMResponseCleaner` - Extract code from LLM responses
- `DynamicFunctionCleaner` - Format and clean code blocks
- `CodeAnalyzer` - Analyze code structure

---

### 📦 `utils/`
**Purpose:** General utilities that don't fit other categories

**Contains:**
- File management utilities
- Helper functions

**Use when:** Adding general-purpose utilities.

---

## Import Patterns

### New Recommended Imports (Organized)

```python
# Import from organized packages
from dynamic_functioneer.models import ModelAPIFactory, OpenAIModelAPI
from dynamic_functioneer.code_management import DynamicCodeManager, PytestRunner
from dynamic_functioneer.code_generation import LLMCodeGenerator
from dynamic_functioneer.code_processing import LLMResponseCleaner
```

### Main Package Imports (Convenience)

```python
# Import from main package (recommended for end users)
from dynamic_functioneer import (
    dynamic_function,          # Main decorator
    get_config,                # Configuration
    ModelAPIFactory,           # Model factory
    DynamicCodeManager,        # Code manager
)
```

### Old Imports (Still Supported - Backward Compatible)

```python
# These still work! No need to change existing code
from dynamic_functioneer.model_api_factory import ModelAPIFactory
from dynamic_functioneer.dynamic_code_manager import DynamicCodeManager
from dynamic_functioneer.llm_code_generator import LLMCodeGenerator
```

**Note:** Old import paths are aliased in `__init__.py` using `sys.modules`, ensuring 100% backward compatibility.

---

## Benefits of New Structure

### ✅ Better Organization
- Related files grouped together
- Clear separation of concerns
- Easier to find specific functionality

### ✅ Improved Maintainability
- Each package has a focused responsibility
- Easier to understand what each module does
- Reduces cognitive load when navigating codebase

### ✅ Scalability
- Easy to add new models (add to `models/`)
- Easy to add new test runners (add to `code_management/`)
- Easy to add new code processors (add to `code_processing/`)

### ✅ Better Testing
- Each package can be tested independently
- Clearer test organization
- Easier to mock dependencies

### ✅ Backward Compatible
- All old imports still work
- No breaking changes
- Smooth migration path

---

## Migration Guide

### For Developers

**No changes required!** All old imports continue to work.

**Optional:** Update to new organized imports for better clarity:

```python
# Before (still works)
from dynamic_functioneer.model_api_factory import ModelAPIFactory

# After (recommended, but optional)
from dynamic_functioneer.models import ModelAPIFactory
```

### For New Code

Use the organized imports:

```python
from dynamic_functioneer.models import ModelAPIFactory, OpenAIModelAPI
from dynamic_functioneer.code_management import DynamicCodeManager
from dynamic_functioneer.code_generation import LLMCodeGenerator
```

---

## Adding New Components

### Adding a New Model Provider

1. Create new file in `models/`: `my_provider_model_api.py`
2. Implement `BaseModelAPI` interface
3. Register in `models/__init__.py`
4. Register in `ModelAPIFactory`

Example:
```python
# models/my_provider_model_api.py
from dynamic_functioneer.models.base_model_api import BaseModelAPI

class MyProviderModelAPI(BaseModelAPI):
    def get_api_key_from_env(self):
        return os.getenv('MY_PROVIDER_API_KEY')

    def get_response(self, prompt, **kwargs):
        # Implementation
        pass
```

### Adding a New Test Runner

1. Create class in `code_management/test_runner.py`
2. Inherit from `TestExecutionStrategy`
3. Implement `run_test()` method
4. Export in `code_management/__init__.py`

Example:
```python
# code_management/test_runner.py
class MyCustomRunner(TestExecutionStrategy):
    def run_test(self, test_file_path: str) -> bool:
        # Implementation
        pass
```

### Adding a New Code Processor

1. Create new file in `code_processing/`
2. Implement processing logic
3. Export in `code_processing/__init__.py`

---

## File Naming Conventions

- **Module files:** `snake_case.py` (e.g., `model_api_factory.py`)
- **Class names:** `PascalCase` (e.g., `ModelAPIFactory`)
- **Package names:** `snake_case` (e.g., `code_management/`)

---

## Version

- **Structure Version:** 2.0 (Reorganized)
- **Package Version:** 0.2.0
- **Backward Compatibility:** 100%

---

## Questions?

For questions about the structure or where to add new functionality, refer to the package descriptions above or check the README.md.
