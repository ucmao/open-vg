from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProvider(ABC):
    @abstractmethod
    async def create_generation(
        self,
        work_id: int,
        work_type: str,
        model_id: str,
        prompt: str,
        negative_prompt: Optional[str],
        params: Dict[str, Any],
        webhook_url: str
    ) -> str:
        """
        Send generation request to the provider.
        Returns the provider's task ID or prediction ID.
        """
        pass

    @abstractmethod
    async def handle_webhook(self, work_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the webhook payload from the provider.
        Returns a standardized dictionary with status and result.
        """
        pass

    @abstractmethod
    async def get_status(self, provider_task_id: str) -> Dict[str, Any]:
        """
        Get the current status of a generation task from the provider.
        Returns a standardized dictionary with status and result.
        """
        pass

