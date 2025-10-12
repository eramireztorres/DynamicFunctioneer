import os
import logging
from typing import Optional
import requests
from dynamic_functioneer.base_model_api import BaseModelAPI

logger = logging.getLogger(__name__)


class LlamaModelAPI(BaseModelAPI):
    """
    Llama model API client.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = 'meta-llama/llama-3.1-405b-instruct:free') -> None:
        super().__init__(api_key)
        self.model = model
        self.url = 'https://openrouter.ai/api/v1/chat/completions'

    def get_api_key_from_env(self) -> Optional[str]:
        """
        Retrieve the Llama API key from environment variables.
        """

        return os.getenv('LLAMA_API_KEY') or os.getenv('OPENROUTER_API_KEY')

    def get_response(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """
        Get a response from the Llama model.
        """

        logger.info(f'Using model: {self.model}')

        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            completion = response.json()
            if 'choices' in completion and len(completion['choices']) > 0:
                assistant_response = completion['choices'][0]['message']['content']
                return assistant_response.strip()
            else:
                logger.warning(f"Unexpected response structure: {completion}")
                return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response Body: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            return None
