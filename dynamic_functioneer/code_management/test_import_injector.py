class TestImportInjector:
    """
    Ensures that the necessary imports (unittest or pytest) are included in test scripts
    and appends the necessary test execution block.
    """

    @staticmethod
    def ensure_imports(test_code, module_name, function_name):
        """
        Ensures that:
        1. Required testing framework imports (unittest or pytest) are present.
        2. The tested function is imported at the top of the script.
        3. A unittest main execution block is added.

        Args:
            test_code (str): The test script.
            module_name (str): The module name where the function is defined.
            function_name (str): The function being tested.

        Returns:
            str: The modified test script with necessary imports and execution.
        """
        # Ensure unittest or pytest is imported
        if "unittest" in test_code and "import unittest" not in test_code:
            test_code = "import unittest\n" + test_code

        if "pytest" in test_code and "import pytest" not in test_code:
            test_code = "import pytest\n" + test_code

        # Ensure the function is imported
        function_import = f"from {module_name} import {function_name}"
        if function_import not in test_code:
            test_code = function_import + "\n" + test_code

        # Ensure unittest main block is present
        if "unittest" in test_code and "__name__ == \"__main__\"" not in test_code:
            test_code += "\n\nif __name__ == \"__main__\":\n    unittest.main()\n"

        return test_code
