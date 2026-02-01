import os
import logging
import inspect
import importlib
from inspect import signature
from dynamic_functioneer.code_management.dynamic_code_manager import DynamicCodeManager
from dynamic_functioneer.code_generation.llm_code_generator import LLMCodeGenerator
from dynamic_functioneer.code_management.hot_swap_executor import HotSwapExecutor
from dynamic_functioneer.code_processing.llm_response_cleaner import LLMResponseCleaner
from dynamic_functioneer.code_processing.prompt_code_cleaner import DynamicFunctionCleaner

class DynamicExecutionHandler:
    """
    Handles the execution lifecycle of a dynamic function or method.
    Encapsulates initialization, hot-swapping, code generation, execution, and error recovery.
    """
    def __init__(self, func, script_dir, config, is_method=False, instance=None):
        self.func = func
        self.script_dir = script_dir
        self.config = config
        self.is_method = is_method
        self.instance = instance
        self.function_name = func.__name__
        self.module_name = os.path.splitext(os.path.basename(inspect.getfile(func)))[0]
        
        # Setup Class Context if method
        self.class_code = None
        if self.is_method and self.instance:
             try:
                # Optimized import to avoid circular dependency if placed at top level
                from dynamic_functioneer.utils.introspection import extract_class_code
                self.class_code = extract_class_code(inspect.getmodule(self.instance.__class__), self.instance.__class__.__name__)
             except Exception as e:
                logging.warning(f"Could not extract class code: {e}")
                self.class_code = repr(self.instance.__class__)

        if self.class_code:
             self.class_code = DynamicFunctionCleaner(self.class_code).clean_dynamic_function()

        # Determine Dynamic File Path
        if self.is_method and self.instance:
             class_name = self.instance.__class__.__name__
             default_file = os.path.join(self.script_dir, f"d_{class_name}_{self.function_name}.py")
        else:
             default_file = os.path.join(self.script_dir, f"d_{self.function_name}.py")
        
        self.dynamic_file_path = self.config.get('dynamic_file') or default_file

        # Initialize Managers
        self.code_manager = DynamicCodeManager(self.dynamic_file_path)
        self.llm_generator = LLMCodeGenerator(model=self.config.get('model'))
        self.hot_swap_executor = HotSwapExecutor(
            code_manager=self.code_manager,
            llm_generator=self.llm_generator,
            retries=self.config.get('error_trials', 3),
            is_method=self.is_method,
            class_code=self.class_code
        )

    def bind_args(self, args, kwargs):
        """Binds arguments to determining hot-swap condition."""
        try:
            sig = signature(self.func)
            if self.is_method and self.instance:
                 bound_args = sig.bind(self.instance, *args, **kwargs)
            else:
                 bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            return bound_args.arguments
        except Exception as e:
            logging.warning(f"Failed to bind arguments: {e}")
            return {}

    def check_hot_swap(self, args, kwargs):
        hs_condition = self.config.get('hs_condition')
        if not hs_condition:
            return False
            
        if isinstance(hs_condition, bool):
            return hs_condition
        
        if isinstance(hs_condition, str):
            local_args = self.bind_args(args, kwargs)
            try:
                return eval(hs_condition, {}, local_args)
            except Exception as e:
                logging.warning(f"Failed to evaluate hs_condition: {e}")
                return False
        return False

    def generate_initial_code(self):
        extra_info = self.config.get('extra_info')
        if self.is_method:
             code = self.llm_generator.method_code_generation(
                 class_definition=self.class_code,
                 method_header=self.function_name,
                 extra_info=extra_info
             )
        else:
             code = self.llm_generator.initial_code_generation(
                 function_header=inspect.getsource(self.func),
                 docstring=self.func.__doc__,
                 extra_info=extra_info
             )
        
        cleaned = LLMResponseCleaner.clean_response(code)
        return DynamicFunctionCleaner(cleaned).clean_dynamic_function()

    def generate_test_code(self):
        if not self.config.get('unit_test'):
            return None
            
        extra_info = self.config.get('extra_info')
        func_source = inspect.getsource(self.func)
        
        try:
            if self.is_method:
                test_code = self.llm_generator.generate_method_test_logic(
                    class_definition=self.class_code,
                    method_header=func_source,
                    extra_info=extra_info
                )
            else:
                func_code_clean = DynamicFunctionCleaner(func_source).clean_dynamic_function()
                test_code = self.llm_generator.generate_function_test_logic(
                    function_code=func_code_clean,
                    extra_info=extra_info
                )
            
            cleaned = LLMResponseCleaner.clean_response(test_code)
            cleaned = DynamicFunctionCleaner(cleaned).clean_dynamic_function()
            
            # Helper to inject imports
            from dynamic_functioneer.code_management.test_import_injector import TestImportInjector
            return TestImportInjector.ensure_imports(cleaned, self.module_name, self.function_name)
            
        except Exception as e:
            logging.warning(f"Failed to generate test code: {e}")
            return None

    def execute(self, *args, **kwargs):
        # Hot Swap
        if self.check_hot_swap(args, kwargs):
             logging.info(f"Triggering hot-swap for {self.function_name}...")
             self.hot_swap_executor.perform_hot_swap(
                 function_name=self.function_name,
                 hs_prompt=self.config.get('hs_prompt'),
                 hs_model=self.config.get('hs_model')
             )

        # Ensure Code Exists
        if not self.code_manager.code_exists():
            code = self.generate_initial_code()
            self.code_manager.save_code(code)
            test_code = self.generate_test_code()
            
            self.hot_swap_executor.execute_workflow(
                 function_name=self.function_name,
                 test_code=test_code,
                 script_dir=self.script_dir
            )

        # Execute
        importlib.invalidate_caches()
        dynamic_func = self.code_manager.load_function(self.function_name)
        
        if self.is_method and self.instance:
             dynamic_func = dynamic_func.__get__(self.instance, type(self.instance))

        try:
            return dynamic_func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Runtime error in {self.function_name}: {e}")
            if self.config.get('fix_dynamically'):
                return self.recover_from_error(e, *args, **kwargs)
            raise e

    def recover_from_error(self, error, *args, **kwargs):
        retries = self.config.get('error_trials', 3)
        error_model = self.config.get('error_model')
        
        for attempt in range(1, retries + 1):
             logging.info(f"Attempting to fix {self.function_name} (attempt {attempt}/{retries})...")
             try:
                 error_gen = LLMCodeGenerator(model=error_model)
                 corrected = error_gen.fix_runtime_error(
                     self.code_manager.load_code(),
                     str(error)
                 )
                 
                 cleaned = LLMResponseCleaner.clean_response(corrected)
                 cleaned = DynamicFunctionCleaner(cleaned).clean_dynamic_function()
                 
                 test_code = self.generate_test_code() # Regenerate test code for verification
                 
                 if self.hot_swap_executor._apply_error_correction(self.function_name, cleaned, test_code, self.script_dir):
                     importlib.invalidate_caches()
                     dynamic_func = self.code_manager.load_function(self.function_name)
                     if self.is_method and self.instance:
                         dynamic_func = dynamic_func.__get__(self.instance, type(self.instance))
                     
                     return dynamic_func(*args, **kwargs)
             except Exception as retry_err:
                 logging.error(f"Fix attempt {attempt} failed: {retry_err}")
        
        raise error
