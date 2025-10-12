import abc
from typing import Optional, Any


class BaseModelAPI(abc.ABC):
    """
    Abstract base class for model APIs.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the API client with an API key.

        Args:
            api_key: Optional API key. If None, will attempt to get from environment.
        """
        self.api_key = api_key or self.get_api_key_from_env()

    @abc.abstractmethod
    def get_api_key_from_env(self) -> Optional[str]:
        """
        Retrieve the API key from environment variables.

        Returns:
            The API key from environment, or None if not found.
        """
        pass

    @abc.abstractmethod
    def get_response(self, prompt: str, **kwargs: Any) -> Optional[str]:
        """
        Get a response from the model based on the prompt.

        Args:
            prompt: The input prompt text.
            **kwargs: Additional model-specific parameters.

        Returns:
            The model's response text, or None if request failed.
        """
        pass
