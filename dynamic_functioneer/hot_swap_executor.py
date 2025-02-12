import logging
import os
from textwrap import dedent
from dynamic_functioneer.dynamic_code_manager import DynamicCodeManager
from dynamic_functioneer.llm_code_generator import LLMCodeGenerator
from dynamic_functioneer.boilerplate_manager import BoilerplateManager
from dynamic_functioneer.llm_response_cleaner import LLMResponseCleaner

class HotSwapExecutor:
    """
    Orchestrates the workflow for dynamically testing, validating, and applying new code.
    """

    def __init__(self, code_manager, llm_generator, retries=3, is_method=False, class_code=None):
        """
        Initializes the HotSwapExecutor.

        Args:
            code_manager (DynamicCodeManager): Manages dynamic code storage and retrieval.
            llm_generator (LLMCodeGenerator): Generates new or improved code using an LLM.
            retries (int): Number of retries for error correction.
            is_method (bool): Indicates if the target is a method.
            class_code (str): The full class definition (if applicable).
        """
        self.code_manager = code_manager
        self.llm_generator = llm_generator
        self.retries = retries
        self.is_method = is_method
        self.class_code = class_code
        logging.basicConfig(level=logging.INFO)
        
    def execute_workflow(self, function_name, test_code, condition_met=False, error_message=None, script_dir="."):
        """
        Executes the workflow for hot-swapping or fixing code dynamically.
        
        Args:
            function_name (str): The name of the function or method being managed.
            test_code (str or None): Test code for validating the function (None if unit_test=False).
            condition_met (bool): Indicates if a hot-swapping condition has been triggered.
            error_message (str): Runtime error message (if applicable).
            script_dir (str): Directory where the test file should be saved.
    
        Returns:
            bool: True if new code was successfully applied, False otherwise.
        """
        try:
            logging.info("Testing current function...")
    
            if test_code is not None:

                print(f'TEST CODE: {test_code}')

                test_result = self.run_test_workflow(function_name, test_code, script_dir)

                print(f'TEST RESULTS: {test_result}')
    
                if test_result:
                    logging.info("Test completed successfully.")  # ✅ Only print this if the test passed
                else:
                    logging.warning("Test failed.")  # ✅ Clearly indicate if the test failed
    
            else:
                logging.info(f"Skipping tests for {function_name} since unit_test is disabled.")
    
            return True
    
        except Exception as e:
            logging.error(f"Workflow execution failed: {e}")
            return False

        
    # def execute_workflow(self, function_name, test_code, condition_met=False, error_message=None, script_dir="."):
    #     """
    #     Executes the workflow for hot-swapping or fixing code dynamically.
    
    #     Args:
    #         function_name (str): The name of the function or method being managed.
    #         test_code (str or None): Test code for validating the function (None if unit_test=False).
    #         condition_met (bool): Indicates if a hot-swapping condition has been triggered.
    #         error_message (str): Runtime error message (if applicable).
    #         script_dir (str): Directory where the test file should be saved.
    
    #     Returns:
    #         bool: True if new code was successfully applied, False otherwise.
    #     """
    #     try:
    #         logging.info("Testing current function...")
    
    #         # ✅ ADD THIS CHECK TO AVOID TEST EXECUTION WHEN test_code IS NONE
    #         if test_code is not None:
    #             self.run_test_workflow(function_name, test_code, script_dir)
    #             logging.info("Test completed successfully.")
    #         else:
    #             logging.info(f"Skipping tests for {function_name} since unit_test is disabled.")
    
    #         return True
    
    #     except Exception as e:
    #         logging.error(f"Workflow execution failed: {e}")
    #         return False


    # def execute_workflow(self, function_name, test_code, condition_met=False, error_message=None, script_dir="."):
    #     """
    #     Executes the workflow for hot-swapping or fixing code dynamically.

    #     Args:
    #         function_name (str): The name of the function or method being managed.
    #         test_code (str): Test code for validating the function.
    #         condition_met (bool): Indicates if a hot-swapping condition has been triggered.
    #         error_message (str): Runtime error message (if applicable).
    #         script_dir (str): Directory where the test file should be saved.

    #     Returns:
    #         bool: True if new code was successfully applied, False otherwise.
    #     """
    #     try:
    #         logging.info("Testing current function...")
    #         self.run_test_workflow(function_name, test_code, script_dir)
    #         logging.info("Test completed successfully.")
    #         return True
    #     except Exception as e:
    #         logging.error(f"Workflow execution failed: {e}")
    #         return False

    def run_test_workflow(self, function_name, test_code, script_dir):
        """
        Handles the test workflow: saving and running test code.

        Args:
            function_name (str): The name of the function or method being tested.
            test_code (str): Test code for validation.
            script_dir (str): Directory where the test file should be saved.
        """
        test_file_path = self.save_test_code(function_name, test_code, script_dir)
        return self.run_test(test_file_path)  

    def save_test_code(self, function_name, test_code, script_dir):
        """
        Saves the test code to a file.

        Args:
            function_name (str): The name of the function or method being tested.
            test_code (str): Test code for validation.
            script_dir (str): Directory where the test file should be saved.

        Returns:
            str: The path to the saved test file.
        """
        logging.info("Saving test code...")
        test_file_path = os.path.join(script_dir, f"test_{function_name}.py")
        try:
            self.code_manager.save_test_file(test_file_path, dedent(test_code))
            logging.info(f"Test code saved successfully to {test_file_path}")
        except Exception as e:
            logging.warning(f"Failed to save test code for {function_name}: {e}")
        return test_file_path
    
    def run_test(self, test_file_path):
        logging.info(f"Running test file: {test_file_path}")
        try:
            success = self.code_manager.run_test(test_file_path)
            if not success:
                logging.warning("Test failed.")
            return success
        except Exception as e:
            logging.error(f"Error running test: {e}")
            return False


    # def run_test(self, test_file_path):
    #     """
    #     Runs the test file.

    #     Args:
    #         test_file_path (str): The path to the test file.

    #     Raises:
    #         Exception: If the test fails or encounters an error.
    #     """
    #     logging.info(f"Running test file: {test_file_path}")
    #     try:
    #         if not self.code_manager.run_test(test_file_path):
    #             logging.warning("Test failed.")
    #     except Exception as e:
    #         logging.error(f"Error running test: {e}")


    def _apply_error_correction(self, function_name, corrected_code, test_code, script_dir):
        """
        Applies corrected code and validates it through testing.
    
        Args:
            function_name (str): The name of the function or method.
            corrected_code (str): The corrected function or method code.
            test_code (str or None): The corresponding test code, if available.
            script_dir (str): Directory where the test file should be saved.
    
        Returns:
            bool: True if the corrected code passes validation or testing is skipped, False otherwise.
        """
        if not corrected_code:
            logging.error("No corrected code provided.")
            return False
    
        logging.info(f"Applying corrected code for {function_name}...")
        self.code_manager.save_code(corrected_code)
    
        if test_code:
            try:
                logging.info(f"Generating test file for {function_name}...")
                test_file_path = self.save_test_code(function_name, test_code, script_dir)
                logging.info(f"Testing corrected code for {function_name}...")
                return self.run_test(test_file_path)
            except Exception as e:
                logging.error(f"Error during testing of {function_name}: {e}")
                return False
    
        logging.warning(f"No test code provided for {function_name}. Skipping test execution.")
        return True


    # def _apply_error_correction(self, function_name, corrected_code, test_code, script_dir):
    #     """
    #     Applies corrected code and validates it through testing.

    #     Args:
    #         function_name (str): The name of the function or method.
    #         corrected_code (str): The corrected function or method code.
    #         test_code (str): The corresponding test code.
    #         script_dir (str): Directory where the test file should be saved.

    #     Returns:
    #         bool: True if the corrected code passes validation, False otherwise.
    #     """
    #     if not corrected_code:
    #         logging.error("No corrected code provided.")
    #         return False

    #     logging.info(f"Applying corrected code for {function_name}...")
    #     self.code_manager.save_code(corrected_code)

    #     if test_code:
    #         logging.info(f"Generating test file for {function_name}...")
    #         test_file_path = self.save_test_code(function_name, test_code, script_dir)
    #         logging.info(f"Testing corrected code for {function_name}...")
    #         return self.run_test(test_file_path)

    #     logging.warning(f"No test code provided for {function_name}. Skipping test execution.")
    #     return True


# class HotSwapExecutor:
#     """
#     Orchestrates the workflow for dynamically testing, validating, and applying new code.
#     """

#     def __init__(self, code_manager, llm_generator, retries=3, is_method=False, class_code=None):
#         """
#         Initializes the HotSwapExecutor.

#         Args:
#             code_manager (DynamicCodeManager): Manages dynamic code storage and retrieval.
#             llm_generator (LLMCodeGenerator): Generates new or improved code using an LLM.
#             retries (int): Number of retries for error correction.
#             is_method (bool): Indicates if the target is a method.
#             class_code (str): The full class definition (if applicable).
#         """
#         self.code_manager = code_manager
#         self.llm_generator = llm_generator
#         self.retries = retries
#         self.is_method = is_method
#         self.class_code = class_code
#         logging.basicConfig(level=logging.INFO)

#     def execute_workflow(self, function_name, test_code, condition_met=False, error_message=None, script_dir="."):
#         """
#         Executes the workflow for hot-swapping or fixing code dynamically.
    
#         Args:
#             function_name (str): The name of the function or method being managed.
#             test_code (str): Test code for validating the function.
#             condition_met (bool): Indicates if a hot-swapping condition has been triggered.
#             error_message (str): Runtime error message (if applicable).
#             script_dir (str): Directory where the test file should be saved.
    
#         Returns:
#             bool: True if new code was successfully applied, False otherwise.
#         """
#         try:
#             logging.info("Testing current function...")
#             # Gracefully handle test failures            
#             self._test_function(function_name, test_code, script_dir=script_dir)
#             logging.info("Test completed successfully (or skipped errors).")
#             return True
#         except Exception as e:
#             logging.error(f"Workflow execution failed: {e}")
#             return False

    
#     def _test_function(self, function_name, test_code, script_dir="."):
#         """
#         Tests the current function using the provided test code.
    
#         Args:
#             function_name (str): The name of the function or method being tested.
#             test_code (str): Test code for validation.
#             script_dir (str): Directory where the test file should be saved.
#         """
#         logging.info("Adding boilerplate to test code...")
        
#         # Create a BoilerplateManager instance
#         boilerplate_manager = BoilerplateManager(is_method=self.is_method, class_code=self.class_code)
        
#         # Generate complete test script
#         complete_test_code = boilerplate_manager.add_boilerplate(
#             test_code,
#             function_name,
#             import_path=self.code_manager.dynamic_file_path,
#             script_dir=script_dir  # Pass script directory
#         )
        
#         # Save the test file in the script directory
#         test_file_path = os.path.join(script_dir, f"test_{function_name}.py")
#         self.code_manager.save_test_file(test_file_path, dedent(complete_test_code))
        
#         # Run the test, handle any issues gracefully
#         try:
#             if not self.code_manager.run_test(test_file_path):
#                 logging.warning(f"Test for {function_name} failed. Execution will continue.")
#         except Exception as e:
#             logging.error(f"Error running test for {function_name}: {e}")

#     def _handle_failure(self, function_name, test_code, error_message, condition_met):
#         """
#         Handles failures by requesting new code from the LLM.

#         Args:
#             function_name (str): The name of the function or method being managed.
#             test_code (str): Test code for validating the function.
#             error_message (str): Runtime error message (if applicable).
#             condition_met (bool): Indicates if a hot-swapping condition has been triggered.

#         Returns:
#             bool: True if new code was successfully applied, False otherwise.
#         """
#         current_code = self.code_manager.load_code()
#         new_code = None

#         if error_message:
#             logging.info("Requesting error correction from LLM...")
#             for attempt in range(self.retries):
#                 new_code = self.llm_generator.fix_runtime_error(current_code, error_message)

#                 cleaned_code = LLMResponseCleaner.clean_response(new_code)

#                 if self._apply_new_code(function_name, cleaned_code, test_code):
#                     return True
#                 logging.warning(f"Retrying error correction ({attempt + 1}/{self.retries})...")
#         elif condition_met:
#             logging.info("Hot-swapping triggered by condition.")
#             new_code = self.llm_generator.hot_swap_improvement(
#                 current_code, {}, condition_met
#             )
#             return self._apply_new_code(function_name, new_code, test_code)

#         logging.error("Failed to apply new code after all retries.")
#         return False

#     def _apply_new_code(self, function_name, new_code, test_code):
#         """
#         Applies and validates new code dynamically.

#         Args:
#             function_name (str): The name of the function or method being updated.
#             new_code (str): The new function code to apply.
#             test_code (str): Test code for validating the updated function.

#         Returns:
#             bool: True if the new code passes validation, False otherwise.
#         """
#         if not new_code:
#             logging.error("No new code provided.")
#             return False

#         logging.info("Applying new code...")
#         self.code_manager.save_code(new_code)

#         logging.info("Testing new code...")
#         self._test_function(function_name, test_code)  # Do not raise errors here
#         return True


#     def _apply_error_correction(self, function_name, corrected_code, test_code, script_dir):
#         """
#         Applies corrected code and validates it through testing.

#         Args:
#             function_name (str): The name of the function or method.
#             corrected_code (str): The corrected function or method code.
#             test_code (str): The corresponding test code.
#             script_dir (str): Directory where the test file should be saved.

#         Returns:
#             bool: True if the corrected code passes validation, False otherwise.
#         """
#         if not corrected_code:
#             logging.error("No corrected code provided.")
#             return False

#         logging.info(f"Applying corrected code for {function_name}...")
#         self.code_manager.save_code(corrected_code)

#         logging.info(f"Generating test file for {function_name}...")
#         test_file_path = os.path.join(script_dir, f"test_{function_name}.py")
#         self.code_manager.save_test_file(test_file_path, dedent(test_code))

#         logging.info(f"Testing corrected code for {function_name}...")
#         try:
#             return self.code_manager.run_test(test_file_path)
#         except Exception as e:
#             logging.error(f"Error running test for {function_name}: {e}")
#             return False

# class HotSwapExecutor:
#     """
#     Orchestrates the workflow for dynamically testing, validating, and applying new code.
#     """

#     def __init__(self, code_manager, llm_generator, retries=3, is_method=False, class_code=None):
#         """
#         Initializes the HotSwapExecutor.

#         Args:
#             code_manager (DynamicCodeManager): Manages dynamic code storage and retrieval.
#             llm_generator (LLMCodeGenerator): Generates new or improved code using an LLM.
#             retries (int): Number of retries for error correction.
#             is_method (bool): Indicates if the target is a method.
#             class_code (str): The full class definition (if applicable).
#         """
#         self.code_manager = code_manager
#         self.llm_generator = llm_generator
#         self.retries = retries
#         self.is_method = is_method
#         self.class_code = class_code
#         logging.basicConfig(level=logging.INFO)

#     def execute_workflow(self, function_name, test_code, condition_met=False, error_message=None, script_dir="."):
#         """
#         Executes the workflow for hot-swapping or fixing code dynamically.
    
#         Args:
#             function_name (str): The name of the function or method being managed.
#             test_code (str): Test code for validating the function.
#             condition_met (bool): Indicates if a hot-swapping condition has been triggered.
#             error_message (str): Runtime error message (if applicable).
#             script_dir (str): Directory where the test file should be saved.
    
#         Returns:
#             bool: True if new code was successfully applied, False otherwise.
#         """
#         try:
#             logging.info("Testing current function...")
#             # Gracefully handle test failures            
#             self._test_function(function_name, test_code, script_dir=script_dir)
#             logging.info("Test completed successfully (or skipped errors).")
#             return True
#         except Exception as e:
#             logging.error(f"Workflow execution failed: {e}")
#             return False


#     # def execute_workflow(self, function_name, test_code, condition_met=False, error_message=None):
#     #     """
#     #     Executes the workflow for hot-swapping or fixing code dynamically.

#     #     Args:
#     #         function_name (str): The name of the function or method being managed.
#     #         test_code (str): Test code for validating the function.
#     #         condition_met (bool): Indicates if a hot-swapping condition has been triggered.
#     #         error_message (str): Runtime error message (if applicable).

#     #     Returns:
#     #         bool: True if new code was successfully applied, False otherwise.
#     #     """
#     #     try:
#     #         logging.info("Testing current function...")
#     #         # Gracefully handle test failures
#     #         self._test_function(function_name, test_code)
#     #         logging.info("Test completed successfully (or skipped errors).")
#     #         return True
#     #     except Exception as e:
#     #         logging.error(f"Workflow execution failed: {e}")
#     #         return False

    
#     def _test_function(self, function_name, test_code, script_dir="."):
#         """
#         Tests the current function using the provided test code.
    
#         Args:
#             function_name (str): The name of the function or method being tested.
#             test_code (str): Test code for validation.
#             script_dir (str): Directory where the test file should be saved.
#         """
#         logging.info("Adding boilerplate to test code...")
        
#         # Create a BoilerplateManager instance
#         boilerplate_manager = BoilerplateManager(is_method=self.is_method, class_code=self.class_code)
        
#         # Generate complete test script
#         complete_test_code = boilerplate_manager.add_boilerplate(
#             test_code,
#             function_name,
#             import_path=self.code_manager.dynamic_file_path,
#             script_dir=script_dir  # Pass script directory
#         )
        
#         # Save the test file in the script directory
#         test_file_path = os.path.join(script_dir, f"test_{function_name}.py")
#         self.code_manager.save_test_file(test_file_path, dedent(complete_test_code))
        
#         # Run the test, handle any issues gracefully
#         try:
#             if not self.code_manager.run_test(test_file_path):
#                 logging.warning(f"Test for {function_name} failed. Execution will continue.")
#         except Exception as e:
#             logging.error(f"Error running test for {function_name}: {e}")



#     # def _test_function(self, function_name, test_code, script_dir="."):
#     #     """
#     #     Tests the current function using the provided test code.
    
#     #     Args:
#     #         function_name (str): The name of the function or method being tested.
#     #         test_code (str): Test code for validation.
#     #         script_dir (str): Directory where the test file should be saved.
#     #     """
#     #     logging.info("Adding boilerplate to test code...")
        
#     #     # Create a BoilerplateManager instance
#     #     boilerplate_manager = BoilerplateManager(is_method=self.is_method, class_code=self.class_code)
        
#     #     # Generate complete test script
#     #     complete_test_code = boilerplate_manager.add_boilerplate(
#     #         test_code,
#     #         function_name,
#     #         import_path=self.code_manager.dynamic_file_path.replace(".py", "")
#     #     )
        
#     #     # Save the test file in the script directory
#     #     test_file_path = os.path.join(script_dir, f"test_{function_name}.py")
#     #     self.code_manager.save_test_file(test_file_path, dedent(complete_test_code))
        
#     #     # Run the test, handle any issues gracefully
#     #     try:
#     #         if not self.code_manager.run_test(test_file_path):
#     #             logging.warning(f"Test for {function_name} failed. Execution will continue.")
#     #     except Exception as e:
#     #         logging.error(f"Error running test for {function_name}: {e}")



#     # def _test_function(self, function_name, test_code):
#     #     """
#     #     Tests the current function using the provided test code.
    
#     #     Args:
#     #         function_name (str): The name of the function or method being tested.
#     #         test_code (str): Test code for validation.
#     #     """
#     #     logging.info("Adding boilerplate to test code...")
    
#     #     # Create a BoilerplateManager instance
#     #     boilerplate_manager = BoilerplateManager(is_method=self.is_method, class_code=self.class_code)
    
#     #     # Generate complete test script
#     #     complete_test_code = boilerplate_manager.add_boilerplate(
#     #         test_code,
#     #         function_name,
#     #         import_path=self.code_manager.dynamic_file_path.replace(".py", "")
#     #     )
    
#     #     # Save the test file
#     #     test_file_path = f"test_{function_name}.py"
#     #     self.code_manager.save_test_file(test_file_path, dedent(complete_test_code))
    
#     #     # Run the test, handle any issues gracefully
#     #     try:
#     #         if not self.code_manager.run_test(test_file_path):
#     #             logging.warning(f"Test for {function_name} failed. Execution will continue.")
#     #     except Exception as e:
#     #         logging.error(f"Error running test for {function_name}: {e}")

#     def _handle_failure(self, function_name, test_code, error_message, condition_met):
#         """
#         Handles failures by requesting new code from the LLM.

#         Args:
#             function_name (str): The name of the function or method being managed.
#             test_code (str): Test code for validating the function.
#             error_message (str): Runtime error message (if applicable).
#             condition_met (bool): Indicates if a hot-swapping condition has been triggered.

#         Returns:
#             bool: True if new code was successfully applied, False otherwise.
#         """
#         current_code = self.code_manager.load_code()
#         new_code = None

#         if error_message:
#             logging.info("Requesting error correction from LLM...")
#             for attempt in range(self.retries):
#                 new_code = self.llm_generator.fix_runtime_error(current_code, error_message)

#                 cleaned_code = LLMResponseCleaner.clean_response(new_code)

#                 if self._apply_new_code(function_name, cleaned_code, test_code):
#                     return True
#                 logging.warning(f"Retrying error correction ({attempt + 1}/{self.retries})...")
#         elif condition_met:
#             logging.info("Hot-swapping triggered by condition.")
#             new_code = self.llm_generator.hot_swap_improvement(
#                 current_code, {}, condition_met
#             )
#             return self._apply_new_code(function_name, new_code, test_code)

#         logging.error("Failed to apply new code after all retries.")
#         return False

#     def _apply_new_code(self, function_name, new_code, test_code):
#         """
#         Applies and validates new code dynamically.

#         Args:
#             function_name (str): The name of the function or method being updated.
#             new_code (str): The new function code to apply.
#             test_code (str): Test code for validating the updated function.

#         Returns:
#             bool: True if the new code passes validation, False otherwise.
#         """
#         if not new_code:
#             logging.error("No new code provided.")
#             return False

#         logging.info("Applying new code...")
#         self.code_manager.save_code(new_code)

#         logging.info("Testing new code...")
#         self._test_function(function_name, test_code)  # Do not raise errors here
#         return True


# class HotSwapExecutor:
#     """
#     Orchestrates the workflow for dynamically testing, validating, and applying new code.
#     """

#     def __init__(self, code_manager, llm_generator, retries=3, is_method=False, class_code=None):
#         """
#         Initializes the HotSwapExecutor.

#         Args:
#             code_manager (DynamicCodeManager): Manages dynamic code storage and retrieval.
#             llm_generator (LLMCodeGenerator): Generates new or improved code using an LLM.
#             retries (int): Number of retries for error correction.
#             is_method (bool): Indicates if the target is a method.
#             class_code (str): The full class definition (if applicable).
#         """
#         self.code_manager = code_manager
#         self.llm_generator = llm_generator
#         self.retries = retries
#         self.is_method = is_method
#         self.class_code = class_code
#         logging.basicConfig(level=logging.INFO)


#     def execute_workflow(self, function_name, test_code, condition_met=False, error_message=None):
#         """
#         Executes the workflow for hot-swapping or fixing code dynamically.

#         Args:
#             function_name (str): The name of the function or method being managed.
#             test_code (str): Test code for validating the function.
#             condition_met (bool): Indicates if a hot-swapping condition has been triggered.
#             error_message (str): Runtime error message (if applicable).

#         Returns:
#             bool: True if new code was successfully applied, False otherwise.
#         """
#         try:
#             # Step 1: Test the current function
#             logging.info("Testing current function...")
#             if not self._test_function(function_name, test_code):
#                 logging.warning("Current function failed validation.")
#                 return self._handle_failure(function_name, test_code, error_message, condition_met)
#             logging.info("Current function passed validation.")
#             return True

#         except Exception as e:
#             logging.error(f"Workflow execution failed: {e}")
#             return False


#     def _test_function(self, function_name, test_code):
#         """
#         Tests the current function using the provided test code.
    
#         Args:
#             function_name (str): The name of the function or method being tested.
#             test_code (str): Test code for validation.
    
#         Returns:
#             bool: True if the test passes, False otherwise.
#         """
#         logging.info("Adding boilerplate to test code...")
    
#         # Create a BoilerplateManager instance
#         boilerplate_manager = BoilerplateManager(is_method=self.is_method, class_code=self.class_code)
    
#         # Generate complete test script
#         complete_test_code = boilerplate_manager.add_boilerplate(
#             test_code,
#             function_name,
#             import_path=self.code_manager.dynamic_file_path.replace(".py", "")
#         )
    
#         # Save and run the test
#         test_file_path = f"test_{function_name}.py"
#         self.code_manager.save_test_file(test_file_path, dedent(complete_test_code))
#         return self.code_manager.run_test(test_file_path)

#     def _handle_failure(self, function_name, test_code, error_message, condition_met):
#         """
#         Handles failures by requesting new code from the LLM.

#         Args:
#             function_name (str): The name of the function or method being managed.
#             test_code (str): Test code for validating the function.
#             error_message (str): Runtime error message (if applicable).
#             condition_met (bool): Indicates if a hot-swapping condition has been triggered.

#         Returns:
#             bool: True if new code was successfully applied, False otherwise.
#         """
#         current_code = self.code_manager.load_code()
#         new_code = None

#         if error_message:
#             logging.info("Requesting error correction from LLM...")
#             for attempt in range(self.retries):
#                 new_code = self.llm_generator.fix_runtime_error(current_code, error_message)
                
#                 cleaned_code = LLMResponseCleaner.clean_response(new_code)
                
#                 if self._apply_new_code(function_name, cleaned_code, test_code):
#                     return True
#                 logging.warning(f"Retrying error correction ({attempt + 1}/{self.retries})...")
#         elif condition_met:
#             logging.info("Hot-swapping triggered by condition.")
#             new_code = self.llm_generator.hot_swap_improvement(
#                 current_code, {}, condition_met
#             )
#             return self._apply_new_code(function_name, new_code, test_code)

#         logging.error("Failed to apply new code after all retries.")
#         return False

#     def _apply_new_code(self, function_name, new_code, test_code):
#         """
#         Applies and validates new code dynamically.
    
#         Args:
#             function_name (str): The name of the function or method being updated.
#             new_code (str): The new function code to apply.
#             test_code (str): Test code for validating the updated function.
    
#         Returns:
#             bool: True if the new code passes validation, False otherwise.
#         """
#         if not new_code:
#             logging.error("No new code provided.")
#             return False
    
#         logging.info("Applying new code...")
#         self.code_manager.save_code(new_code)
    
#         logging.info("Testing new code...")
#         if self._test_function(function_name, test_code):
#             logging.info("New code passed validation and has been applied.")
#             return True
    
#         logging.error("New code failed validation.")
#         return False

# class HotSwapExecutor:
#     """
#     Orchestrates the workflow for dynamically testing, validating, and applying new code.
#     """

#     def __init__(self, code_manager, llm_generator, retries=3):
#         """
#         Initializes the HotSwapExecutor.

#         Args:
#             code_manager (DynamicCodeManager): Manages dynamic code storage and retrieval.
#             llm_generator (LLMCodeGenerator): Generates new or improved code using an LLM.
#             retries (int): Number of retries for error correction.
#         """
#         self.code_manager = code_manager
#         self.llm_generator = llm_generator
#         self.retries = retries
#         logging.basicConfig(level=logging.INFO)

#     def execute_workflow(self, function_name, test_code, condition_met=False, error_message=None):
#         """
#         Executes the workflow for hot-swapping or fixing code dynamically.

#         Args:
#             function_name (str): The name of the function or method being managed.
#             test_code (str): Test code for validating the function.
#             condition_met (bool): Indicates if a hot-swapping condition has been triggered.
#             error_message (str): Runtime error message (if applicable).

#         Returns:
#             bool: True if new code was successfully applied, False otherwise.
#         """
#         try:
#             # Step 1: Test the current function
#             logging.info("Testing current function...")
#             if not self._test_function(function_name, test_code):
#                 logging.warning("Current function failed validation.")
#                 return self._handle_failure(function_name, test_code, error_message, condition_met)
#             logging.info("Current function passed validation.")
#             return True

#         except Exception as e:
#             logging.error(f"Workflow execution failed: {e}")
#             return False

#     def _test_function(self, function_name, test_code):
#         """
#         Tests the current function using the provided test code.
    
#         Args:
#             function_name (str): The name of the function or method being tested.
#             test_code (str): Test code for validation.
    
#         Returns:
#             bool: True if the test passes, False otherwise.
#         """
#         logging.info("Adding boilerplate to test code...")
    
#         # Generate complete test script using BoilerplateManager
#         complete_test_code = BoilerplateManager.add_boilerplate(
#             test_code,
#             function_name,
#             import_path=self.code_manager.dynamic_file_path.replace(".py", "")
#         )
    
#         # Dedent the test code to fix any unintentional indentation issues
#         complete_test_code = dedent(complete_test_code)
    
#         # Save and run the test
#         test_file_path = f"test_{function_name}.py"
#         self.code_manager.save_test_file(test_file_path, complete_test_code)
#         return self.code_manager.run_test(test_file_path)

#     def _handle_failure(self, function_name, test_code, error_message, condition_met):
#         """
#         Handles failures by requesting new code from the LLM.

#         Args:
#             function_name (str): The name of the function or method being managed.
#             test_code (str): Test code for validating the function.
#             error_message (str): Runtime error message (if applicable).
#             condition_met (bool): Indicates if a hot-swapping condition has been triggered.

#         Returns:
#             bool: True if new code was successfully applied, False otherwise.
#         """
#         current_code = self.code_manager.load_code()
#         new_code = None

#         if error_message:
#             logging.info("Requesting error correction from LLM...")
#             for attempt in range(self.retries):
#                 new_code = self.llm_generator.fix_runtime_error(current_code, error_message)
                
#                 cleaned_code = LLMResponseCleaner.clean_response(new_code)
                
#                 if self._apply_new_code(function_name, cleaned_code, test_code):
#                     return True
#                 logging.warning(f"Retrying error correction ({attempt + 1}/{self.retries})...")
#         elif condition_met:
#             logging.info("Hot-swapping triggered by condition.")
#             new_code = self.llm_generator.hot_swap_improvement(
#                 current_code, {}, condition_met
#             )
#             return self._apply_new_code(function_name, new_code, test_code)

#         logging.error("Failed to apply new code after all retries.")
#         return False

#     def _apply_new_code(self, function_name, new_code, test_code):
#         """
#         Applies and validates new code dynamically.

#         Args:
#             function_name (str): The name of the function or method being updated.
#             new_code (str): The new function code to apply.
#             test_code (str): Test code for validating the updated function.

#         Returns:
#             bool: True if the new code passes validation, False otherwise.
#         """
#         if not new_code:
#             logging.error("No new code provided.")
#             return False

#         logging.info("Applying new code...")
#         self.code_manager.save_code(new_code)

#         logging.info("Testing new code...")
#         if self._test_function(function_name, test_code):
#             logging.info("New code passed validation and has been applied.")
#             return True

#         logging.error("New code failed validation.")
#         return False



# # Initialize components
# code_manager = DynamicCodeManager("dynamic_function.py")
# llm_generator = LLMCodeGenerator(model_provider="openai", model="gpt-4")

# # Initialize HotSwapExecutor
# executor = HotSwapExecutor(code_manager, llm_generator)


# executor.execute_workflow(
#     function_name="calculate_average",
#     test_code="""
# class TestCalculateAverage(unittest.TestCase):
#     def test_normal_cases(self):
#         self.assertEqual(calculate_average([1, 2, 3]), 2.0)

# if __name__ == "__main__":
#     unittest.main()
# """,
#     error_message="ZeroDivisionError: division by zero"
# )

