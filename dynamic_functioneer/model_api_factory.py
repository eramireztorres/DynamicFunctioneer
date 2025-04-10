from dynamic_functioneer.openai_model_api import OpenAIModelAPI
from dynamic_functioneer.llama_model_api import LlamaModelAPI
from dynamic_functioneer.gemini_model_api import GeminiModelAPI
from dynamic_functioneer.anthropic_model_api import AnthropicModelAPI

class ModelAPIFactory:
    """
    Factory class to instantiate model API clients based on the provider name, model string, or alias.
    """

    _model_registry = {}
    _custom_models = {}

    _model_to_provider = {
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
    def register_model(cls, provider_name, model_class):
        cls._model_registry[provider_name.lower()] = model_class

    @classmethod
    def register_custom_model(cls, alias: str, factory_function):
        """
        Register a custom model alias (like 'crew-4-agent') mapped to a callable factory.
        """
        cls._custom_models[alias] = factory_function

    @classmethod
    def list_available_models(cls):
        """
        Return a list of all known provider models and custom aliases.
        """
        return list(cls._model_registry.keys()) + list(cls._custom_models.keys())

    @classmethod
    def get_provider_from_model(cls, model_name: str) -> str:
        for key, provider in cls._model_to_provider.items():
            if key in model_name:
                return provider
        return 'llama'  # fallback

    @classmethod
    def get_model_api(cls, provider='llama', model='meta-llama/llama-3.1-405b-instruct:free', **kwargs):
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
