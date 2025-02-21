import os
import importlib
import logging
import sys
import subprocess



class DynamicCodeManager:
    """
    Manages dynamic generation, saving, and loading of function/method code and test files.
    """

    def __init__(self, dynamic_file_path):
        """
        Initialize the DynamicCodeManager.

        Args:
            dynamic_file_path (str): Path to the file where dynamic code is stored.
        """
        self.dynamic_file_path = dynamic_file_path
        self.test_file_dir = "."  # Default directory for test files
        os.makedirs(self.test_file_dir, exist_ok=True)
        logging.basicConfig(level=logging.INFO)

    def save_code(self, code):
        """
        Saves the provided code to the dynamic file.

        Args:
            code (str): The code to save.
        """
        try:
            with open(self.dynamic_file_path, 'w') as file:
                file.write(code)
            logging.info(f"Dynamic code saved successfully to {self.dynamic_file_path}")
        except Exception as e:
            logging.error(f"Failed to save dynamic code: {e}")

    def load_code(self):
        """
        Loads and returns the code from the dynamic file.

        Returns:
            str: The code stored in the dynamic file.

        Raises:
            FileNotFoundError: If the dynamic file does not exist.
        """
        if not os.path.exists(self.dynamic_file_path):
            raise FileNotFoundError(f"Dynamic file '{self.dynamic_file_path}' not found.")
        
        with open(self.dynamic_file_path, 'r') as file:
            return file.read()

    def load_function(self, function_name):
        """
        Dynamically loads and returns a function by name from the dynamic file.
    
        Args:
            function_name (str): The name of the function to load.
    
        Returns:
            Callable: The loaded function.
    
        Raises:
            ImportError: If the module or function cannot be loaded.
        """
        module_name = os.path.splitext(os.path.basename(self.dynamic_file_path))[0]
        importlib.invalidate_caches()  # Clear cache
        try:
            if module_name in sys.modules:
                del sys.modules[module_name]  # Remove module from cache
            module = importlib.import_module(module_name)
            return getattr(module, function_name)
        except AttributeError:
            raise ImportError(f"Function '{function_name}' not found in module '{module_name}'.")
        except Exception as e:
            raise ImportError(f"Failed to load function '{function_name}': {e}")


    def save_test_file(self, test_file_path, test_code):
        """
        Saves test code to a specified file.
    
        Args:
            test_file_path (str): Full path to the test file.
            test_code (str): The test code to save.
        """
        try:
            os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
            with open(test_file_path, "w") as file:
                file.write(test_code)
            logging.info(f"Test code saved successfully to {test_file_path}")            
        except Exception as e:
            logging.error(f"Failed to save test code: {e}")


    def run_test(self, test_file_name):
        """
        Runs a test file and checks if it passes.

        Args:
            test_file_name (str): The name of the test file to run.

        Returns:
            bool: True if the test passes, False otherwise.
        """
        test_file_path = os.path.join(self.test_file_dir, test_file_name)
        if not os.path.exists(test_file_path):
            raise FileNotFoundError(f"Test file '{test_file_path}' not found.")

        try:
            result = subprocess.run(
                ["python", test_file_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logging.info("Test passed successfully.")
                return True
            else:
                logging.error(f"Test failed:\n{result.stdout}\n{result.stderr}")
                return False
        except Exception as e:
            logging.error(f"Error running test file '{test_file_name}': {e}")
            return False

    def code_exists(self):
        """
        Checks if the dynamic file exists.

        Returns:
            bool: True if the dynamic file exists, False otherwise.
        """
        return os.path.exists(self.dynamic_file_path)


