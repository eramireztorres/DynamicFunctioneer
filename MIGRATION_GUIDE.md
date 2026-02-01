# Migration Guide - Using New Refactored Features

## Overview

The refactored DynamicFunctioneer maintains **100% backward compatibility**. Your existing code will continue to work without any changes. This guide shows you how to leverage the new features.

---

## What's Still the Same

Your existing code works exactly as before:

```python
from dynamic_functioneer.dynamic_decorator import dynamic_function

@dynamic_function()
def my_function():
    """My function docstring"""
    pass
```

**No changes required!**

---

## New Features You Can Use

### 1. Using Custom Configuration

Set default models and parameters globally:

```python
from dynamic_functioneer.config import get_config, set_config, DynamicFunctioneerConfig

# Get current configuration
config = get_config()

# Modify it
config.model.default_model = "claude-3-opus-20240229"
config.model.max_tokens = 2048
config.execution.error_retry_attempts = 5

# Set it globally
set_config(config)
```

Or use environment variables:

```bash
export DF_DEFAULT_MODEL="gpt-4"
export DF_ERROR_MODEL="gpt-4o"
export DF_MAX_TOKENS=2048
export DF_TEMPERATURE=0.7
export DF_ERROR_RETRIES=5
export DF_FIX_DYNAMICALLY=true
export DF_UNIT_TEST=true
```

---

### 2. Using Different Test Runners

#### Option 1: Pytest Runner

```python
from dynamic_functioneer.test_runner import PytestRunner
from dynamic_functioneer.dynamic_code_manager import DynamicCodeManager

# Create a DynamicCodeManager with pytest
manager = DynamicCodeManager(
    "d_my_function.py",
    test_runner=PytestRunner(pytest_args=["-v", "--tb=short"])
)

# Use it normally
manager.save_code(generated_code)
manager.run_test("test_my_function.py")  # Uses pytest
```

#### Option 2: Unittest Runner

```python
from dynamic_functioneer.test_runner import UnittestRunner
from dynamic_functioneer.dynamic_code_manager import DynamicCodeManager

manager = DynamicCodeManager(
    "d_my_function.py",
    test_runner=UnittestRunner(verbosity=2)
)
```

#### Option 3: Custom Test Runner

Implement your own test runner:

```python
from dynamic_functioneer.test_runner import TestExecutionStrategy

class MyCustomTestRunner(TestExecutionStrategy):
    def run_test(self, test_file_path: str) -> bool:
        # Your custom test execution logic
        print(f"Running custom tests on: {test_file_path}")
        return True

# Use it
manager = DynamicCodeManager("d_my_function.py", test_runner=MyCustomTestRunner())
```

---

### 3. Using Protocol Types for Type Checking

If you're building tools that work with DynamicFunctioneer:

```python
from dynamic_functioneer.protocols import ConversationalModelProtocol, ModelAPIProtocol

def process_with_conversational_model(model: ConversationalModelProtocol):
    """Only accepts models with conversation support"""
    response1 = model.get_response("Hello!")
    response2 = model.continue_conversation("How are you?")
    model.reset_conversation()

def process_with_any_model(model: ModelAPIProtocol):
    """Accepts any model"""
    response = model.get_response("Hello!")
```

---

### 4. Accessing Refactored Components

The refactored DynamicCodeManager now exposes its internal components:

```python
from dynamic_functioneer.dynamic_code_manager import DynamicCodeManager

manager = DynamicCodeManager("d_my_function.py")

# Access specific components
code_manager = manager.code_file_manager  # For file I/O
module_loader = manager.module_loader     # For imports
test_manager = manager.test_file_manager  # For test files
test_runner = manager.test_runner         # For running tests

# Use them directly if needed
code_manager.save_code("def foo(): pass")
function = module_loader.load_function("foo")
```

---

### 5. Registering Custom Model Patterns

Extend the model factory to support new providers:

```python
from dynamic_functioneer.model_api_factory import ModelAPIFactory

# Register a new pattern for automatic provider detection
ModelAPIFactory.register_model_pattern("mycompany/", "mycompany")

# Register a custom model class
from dynamic_functioneer.base_model_api import BaseModelAPI

class MyCompanyModelAPI(BaseModelAPI):
    def get_api_key_from_env(self):
        return os.getenv("MYCOMPANY_API_KEY")

    def get_response(self, prompt, **kwargs):
        # Your implementation
        pass

ModelAPIFactory.register_model("mycompany", MyCompanyModelAPI)

# Now use it
model = ModelAPIFactory.get_model_api(model="mycompany/my-model-v1")
```

---

### 6. Using the Code Storage Components Directly

For advanced use cases:

```python
from dynamic_functioneer.code_storage import CodeFileManager, TestFileManager

# Manage code files
code_file = CodeFileManager("/path/to/my_function.py")
code_file.save_code("def my_func(): return 42")
code = code_file.load_code()
exists = code_file.code_exists()
code_file.delete_code()

# Manage test files
test_manager = TestFileManager(test_dir="./tests")
test_path = test_manager.get_test_file_path("my_function")
test_manager.save_test_file(test_path, "import unittest...")
```

---

### 7. Using the Module Loader Directly

```python
from dynamic_functioneer.code_loader import DynamicModuleLoader

loader = DynamicModuleLoader("/path/to/dynamic_code.py")

# Load a function dynamically
my_function = loader.load_function("my_function")
result = my_function(arg1, arg2)

# Force reload if file changed
loader.reload_module()
```

---

## Type Checking with mypy

The refactored code now supports static type checking:

```bash
# Install mypy
pip install mypy

# Run type checking
mypy dynamic_functioneer/
```

Your IDE will also provide better autocomplete with the new type hints:

```python
from dynamic_functioneer.model_api_factory import ModelAPIFactory

# Your IDE now knows the return type is BaseModelAPI
model = ModelAPIFactory.get_model_api(model="gpt-4")
# Type hints work!
response = model.get_response("Hello")  # IDE knows this returns Optional[str]
```

---

## Logging Configuration

The new logging system allows you to configure log levels:

```python
import logging

# Set logging level for DynamicFunctioneer
logging.getLogger("dynamic_functioneer").setLevel(logging.DEBUG)

# Or configure specific modules
logging.getLogger("dynamic_functioneer.llama_model_api").setLevel(logging.WARNING)
```

Configure logging output:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dynamic_functioneer.log'),
        logging.StreamHandler()
    ]
)
```

---

## Examples: Before and After

### Before (Still Works)

```python
from dynamic_functioneer.dynamic_decorator import dynamic_function

@dynamic_function(model="gpt-4o-mini", error_trials=3)
def calculate_sum(numbers):
    """Calculate sum of numbers."""
    pass

result = calculate_sum([1, 2, 3, 4, 5])
```

### After (With New Features)

```python
from dynamic_functioneer.dynamic_decorator import dynamic_function
from dynamic_functioneer.config import get_config

# Configure globally
config = get_config()
config.model.default_model = "claude-3-opus-20240229"
config.execution.error_retry_attempts = 5

@dynamic_function()  # Uses configuration defaults
def calculate_sum(numbers):
    """Calculate sum of numbers."""
    pass

result = calculate_sum([1, 2, 3, 4, 5])
```

---

## Troubleshooting

### Import Errors

If you get import errors for new modules:

```python
# Make sure you're importing from the right location
from dynamic_functioneer.config import get_config  # ✓ Correct
from dynamic_functioneer import config  # ✗ Wrong
```

### Type Checking Issues

If mypy complains:

```bash
# Add type ignore comments if needed
model = get_model()  # type: ignore
```

Or install type stubs:

```bash
pip install types-requests  # For requests library
```

---

## Questions?

The refactoring maintains backward compatibility, so:

1. **Your existing code will continue to work** without any changes
2. **New features are opt-in** - use them when you need them
3. **No breaking changes** - all existing APIs remain the same

For questions or issues, please file an issue on GitHub.
