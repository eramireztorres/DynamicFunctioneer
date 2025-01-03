from pathlib import Path

class DynamicFileManager:
    """
    Manages dynamic files, including saving and loading generated code.
    """

    def __init__(self, base_path="src"):
        """
        Initializes the DynamicFileManager with a base directory for saving files.

        Args:
            base_path (str): Base directory for saving dynamic files.
        """
        self.base_path = Path(base_path)

    def save_file(self, file_name, content):
        """
        Saves content to a file.

        Args:
            file_name (str): The name of the file to save.
            content (str): The content to write to the file.
        """
        file_path = self.base_path / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            file.write(content)

    def load_file(self, file_name):
        """
        Loads content from a file.

        Args:
            file_name (str): The name of the file to load.

        Returns:
            str: The content of the file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        file_path = self.base_path / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"File '{file_name}' not found in {self.base_path}")
        with open(file_path, "r") as file:
            return file.read()
