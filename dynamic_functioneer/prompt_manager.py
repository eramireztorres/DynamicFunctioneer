import importlib.resources

class PromptManager:
    """
    Manages the loading and rendering of prompt templates.
    """

    def load_prompt(self, prompt_name):
        """
        Loads a prompt template from within dynamic_functioneer's package data.
        """
        # 'dynamic_functioneer.prompts' must be a package or subpackage so that resources can be read.
        # If 'prompts' has no __init__.py, use importlib_resources.files(...) with the folder approach.
        return importlib.resources.read_text("dynamic_functioneer.prompts", prompt_name)

    def render_prompt(self, template, placeholders):
        """
        Renders a prompt by replacing placeholders in the template.
        """
        for key, value in placeholders.items():
            template = template.replace(f"{{{key}}}", str(value))
        return template



# import os
# from pathlib import Path

# class PromptManager:
#     """
#     Manages the loading and rendering of prompt templates.
#     """

#     def __init__(self, prompts_path=None):
#         """
#         Initializes the PromptManager with the path to the prompt files.
#         """
#         if prompts_path is None:
#             # Derive the absolute path of the 'prompts' folder inside dynamic_functioneer
#             prompts_path = os.path.join(os.path.dirname(__file__), "prompts")
#         self.prompts_path = Path(prompts_path)

#     def load_prompt(self, prompt_name):
#         """
#         Loads a prompt template from the prompts directory.

#         Args:
#             prompt_name (str): The name of the prompt file (e.g., "default_function_prompt.txt").

#         Returns:
#             str: The content of the prompt file.

#         Raises:
#             FileNotFoundError: If the specified prompt file does not exist.
#         """
#         prompt_file = os.path.join(self.prompts_path, prompt_name)
        
       
#         try:
#             with open(prompt_file, "r") as file:
#                 return file.read()
#         except Exception as e:
#             print(f"Prompt file '{prompt_name}' not found in {self.prompts_path}. Exception: {e}")
            

#     def render_prompt(self, template, placeholders):
#         """
#         Renders a prompt by replacing placeholders in the template.

#         Args:
#             template (str): The prompt template as a string.
#             placeholders (dict): A dictionary of placeholders to replace in the template.

#         Returns:
#             str: The rendered prompt.
#         """
#         for key, value in placeholders.items():
#             template = template.replace(f"{{{key}}}", str(value))
#         return template

