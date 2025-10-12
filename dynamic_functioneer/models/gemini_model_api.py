import os
import logging
from typing import Optional, Any
from dynamic_functioneer.models.base_model_api import BaseModelAPI
from google import genai

logger = logging.getLogger(__name__)


class GeminiModelAPI(BaseModelAPI):
    """
    Gemini model API client that wraps the Google Gemini API,
    and is compatible with BaseModelAPI.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash") -> None:
        """
        Initialize the Gemini API client with the provided API key and model.
        """
        super().__init__(api_key)
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def get_api_key_from_env(self) -> Optional[str]:
        """
        Retrieve the Gemini API key from environment variables.
        Expects the key to be stored in 'GEMINI_API_KEY'.
        """
        return os.getenv("GEMINI_API_KEY")

    def get_response(self, prompt: str, **kwargs: Any) -> Optional[str]:
        """
        Get a response from the Gemini model based on the prompt.
        Additional keyword arguments are passed directly to the API call.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                **kwargs
            )
            if response and hasattr(response, "text"):
                return response.text.strip()
            else:
                logger.warning("No response text available from Gemini API.")
                return None
        except Exception as e:
            logger.error(f"An error occurred while fetching response: {e}", exc_info=True)
            return None



# import os
# import logging
# import google.generativeai as genai
# from base_model_api import BaseModelAPI

# class GeminiModelAPI(BaseModelAPI):
#     """
#     Gemini model API client.
#     """

#     def __init__(self, api_key=None, model='models/chat-bison-001'):
#         super().__init__(api_key)
#         self.model = model
#         genai.configure(api_key=self.api_key)
#         logging.basicConfig(level=logging.INFO)
#         logging.info("Gemini API configured successfully.")

#     def get_api_key_from_env(self):
#         """
#         Retrieve the Gemini API key from environment variables.
#         """
#         return os.getenv('GEMINI_API_KEY')

#     def get_response(self, prompt, **kwargs):
#         """
#         Get a response from the Gemini model.
#         """
#         try:
#             response = genai.generate_text(
#                 model=self.model,
#                 prompt=prompt,
#                 **kwargs
#             )
#             return self.format_response(response)
#         except Exception as e:
#             logging.error(f"Error in generate_text: {e}")
#             return None

#     @staticmethod
#     def format_response(response):
#         """
#         Format the API response for improved readability.
#         """
#         if hasattr(response, 'result'):
#             return response.result.strip()
#         elif isinstance(response, dict):
#             return "\n".join([f"{k}: {v}" for k, v in response.items()]).strip()
#         else:
#             return str(response).strip()
