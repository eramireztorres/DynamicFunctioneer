from .model_api_factory import ModelAPIFactory
from .crewai_sequential2_model import CrewAISequential2ModelAPI

ModelAPIFactory.register_custom_model(
    "crewai-sequential2-gpt-4o-mini",
    lambda **kwargs: CrewAISequential2ModelAPI(model="crewai-sequential2-gpt-4o-mini", **kwargs)
)

ModelAPIFactory.register_custom_model(
    "crewai-sequential2-gemini-2.0-flash",
    lambda **kwargs: CrewAISequential2ModelAPI(model="crewai-sequential2-gemini-2.0-flash", **kwargs)
)


ModelAPIFactory.register_custom_model(
    "crewai-sequential2-google/gemini-2.0-flash",
    lambda **kwargs: CrewAISequential2ModelAPI(model="crewai-sequential2-google/gemini-2.0-flash", **kwargs)
)


