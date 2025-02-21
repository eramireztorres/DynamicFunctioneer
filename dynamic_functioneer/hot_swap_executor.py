import logging
import os
from textwrap import dedent

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
            # logging.info("Testing current function...")
    
            if test_code is not None:

                print(f'TEST CODE: {test_code}')

                test_result = self.run_test_workflow(function_name, test_code, script_dir)

                print(f'TEST RESULTS: {test_result}')
    
                if test_result:
                    logging.info("Test completed successfully.")  # ✅ Only print this if the test passed
                else:
                    logging.warning("Test failed.")  # ✅ Clearly indicate if the test failed
    
            else:
                # logging.info(f"Skipping tests for {function_name} since unit_test is disabled.")
                pass
    
            return True
    
        except Exception as e:
            logging.error(f"Workflow execution failed: {e}")
            return False



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
                # logging.info(f"Generating test file for {function_name}...")
                test_file_path = self.save_test_code(function_name, test_code, script_dir)
                # logging.info(f"Testing corrected code for {function_name}...")
                return self.run_test(test_file_path)
            except Exception as e:
                logging.error(f"Error during testing of {function_name}: {e}")
                return False
    
        logging.warning(f"No test code provided for {function_name}. Skipping test execution.")
        return True



