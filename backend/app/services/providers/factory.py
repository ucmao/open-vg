from typing import Dict
from .base import BaseProvider
from .replicate_provider import ReplicateProvider
from .gemini_provider import GeminiProvider
from .a2e_provider import A2EProvider

class ProviderFactory:
    _instances: Dict[str, BaseProvider] = {}

    @classmethod
    def get_provider(cls, provider_name: str) -> BaseProvider:
        if provider_name not in cls._instances:
            if provider_name == "replicate":
                cls._instances[provider_name] = ReplicateProvider()
            elif provider_name == "gemini":
                cls._instances[provider_name] = GeminiProvider()
            elif provider_name == "a2e":
                cls._instances[provider_name] = A2EProvider()
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        
        return cls._instances[provider_name]

