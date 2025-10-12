from typing import Dict, List, Callable, Type, Optional, Any
from dynamic_functioneer.models.openai_model_api import OpenAIModelAPI
from dynamic_functioneer.models.llama_model_api import LlamaModelAPI
from dynamic_functioneer.models.gemini_model_api import GeminiModelAPI
from dynamic_functioneer.models.anthropic_model_api import AnthropicModelAPI
from dynamic_functioneer.models.base_model_api import BaseModelAPI


class ModelAPIFactory:
    """
    Factory class to instantiate model API clients based on the provider name, model string, or alias.
    """

    _model_registry: Dict[str, Type[BaseModelAPI]] = {}
    _custom_models: Dict[str, Callable[..., BaseModelAPI]] = {}
    _model_patterns: Dict[str, str] = {}  # New: for pattern-based provider detection

    _model_to_provider: Dict[str, str] = {
        'gpt': 'openai',
        'gpt-4o': 'openai',
        'gpt-4o-mini': 'openai',
        'o1-': 'openai',
        'o3-': 'openai',
        'llama': 'meta',
        'gemini': 'google',
        'claude': 'anthropic',
        'deepseek': 'deepseek',
        'cognitivecomputations/': 'openrouter',
        'google/': 'openrouter',
        'mistralai/': 'openrouter',
        'qwen/': 'openrouter',
        'meta-llama/': 'openrouter',
        'deepseek/': 'openrouter',
        'nvidia/': 'openrouter',
        'microsoft/': 'openrouter'
    }

    @classmethod
    def register_model(cls, provider_name: str, model_class: Type[BaseModelAPI]) -> None:
        """
        Register a model provider class.

        Args:
            provider_name: The name of the provider (e.g., 'openai', 'anthropic').
            model_class: The model API class to register.
        """
        cls._model_registry[provider_name.lower()] = model_class

    @classmethod
    def register_model_pattern(cls, pattern: str, provider: str) -> None:
        """
        Register a model pattern for provider detection.

        Args:
            pattern: String pattern to match in model names.
            provider: The provider name to associate with this pattern.
        """
        cls._model_patterns[pattern] = provider
        cls._model_to_provider[pattern] = provider

    @classmethod
    def register_custom_model(cls, alias: str, factory_function: Callable[..., BaseModelAPI]) -> None:
        """
        Register a custom model alias (like 'crew-4-agent') mapped to a callable factory.

        Args:
            alias: The alias name for the custom model.
            factory_function: Callable that returns a BaseModelAPI instance.
        """
        cls._custom_models[alias] = factory_function

    @classmethod
    def list_available_models(cls) -> List[str]:
        """
        Return a list of all known provider models and custom aliases.

        Returns:
            List of available model names/aliases.
        """
        return list(cls._model_registry.keys()) + list(cls._custom_models.keys())

    @classmethod
    def get_provider_from_model(cls, model_name: str) -> str:
        """
        Detect provider from model name using pattern matching.

        Args:
            model_name: The model name to analyze.

        Returns:
            The detected provider name, or 'llama' as fallback.
        """
        for key, provider in cls._model_to_provider.items():
            if key in model_name:
                return provider
        return 'llama'  # fallback

    @classmethod
    def get_model_api(
        cls,
        provider: Optional[str] = 'llama',
        model: str = 'meta-llama/llama-3.1-405b-instruct:free',
        **kwargs: Any
    ) -> BaseModelAPI:
        """
        Get a model API instance based on provider or model name.

        Args:
            provider: Optional provider name. If None, detected from model name.
            model: The model name or alias.
            **kwargs: Additional arguments passed to the model constructor.

        Returns:
            An instance of a BaseModelAPI subclass.

        Raises:
            ValueError: If the provider or model cannot be found.
        """
        # Case 1: Handle custom aliases (e.g., 'sequential-4-agent-crew')
        if model in cls._custom_models:
            return cls._custom_models[model](**kwargs)

        # Case 2: Handle standard provider-based logic
        if not provider and model:
            provider = cls.get_provider_from_model(model)

        if provider and provider.lower() in cls._model_registry:
            model_class = cls._model_registry[provider.lower()]
            return model_class(model=model, **kwargs)

        raise ValueError(f"Unknown provider or model: {provider or model}")


# Register known providers
ModelAPIFactory.register_model('openai', OpenAIModelAPI)
ModelAPIFactory.register_model('meta', LlamaModelAPI)
ModelAPIFactory.register_model('google', GeminiModelAPI)
ModelAPIFactory.register_model('anthropic', AnthropicModelAPI)
ModelAPIFactory.register_model('deepseek', LlamaModelAPI)
ModelAPIFactory.register_model('openrouter', LlamaModelAPI)
