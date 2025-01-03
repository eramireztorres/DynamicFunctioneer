import os
from pathlib import Path

class PromptManager:
    """
    Manages the loading and rendering of prompt templates.
    """

    def __init__(self, prompts_path="src/prompts"):
        """
        Initializes the PromptManager with the path to the prompt files.

        Args:
            prompts_path (str): Path to the folder containing prompt templates.
        """
        self.prompts_path = Path(prompts_path)

    def load_prompt(self, prompt_name):
        """
        Loads a prompt template from the prompts directory.

        Args:
            prompt_name (str): The name of the prompt file (e.g., "default_function_prompt.txt").

        Returns:
            str: The content of the prompt file.

        Raises:
            FileNotFoundError: If the specified prompt file does not exist.
        """
        prompt_file = self.prompts_path / prompt_name
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file '{prompt_name}' not found in {self.prompts_path}")
        with open(prompt_file, "r") as file:
            return file.read()

    def render_prompt(self, template, placeholders):
        """
        Renders a prompt by replacing placeholders in the template.

        Args:
            template (str): The prompt template as a string.
            placeholders (dict): A dictionary of placeholders to replace in the template.

        Returns:
            str: The rendered prompt.
        """
        for key, value in placeholders.items():
            template = template.replace(f"{{{key}}}", str(value))
        return template

