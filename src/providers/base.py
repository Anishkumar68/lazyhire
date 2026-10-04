from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseLLMProvider(ABC):
    """Abstract Base Class for LLM Providers"""

    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text completion for a given prompt."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test health and credentials of provider."""
        pass
