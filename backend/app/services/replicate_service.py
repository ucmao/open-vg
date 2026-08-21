"""Service for interacting with Replicate API."""
import replicate
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

from ..models.generation_config import get_model_config
from ..utils.logger import logger

load_dotenv()

REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")


class ReplicateService:
    """Service for managing Replicate API interactions."""
    
    def __init__(self):
        if not REPLICATE_API_KEY:
            raise ValueError("REPLICATE_API_KEY is not set")
        
        # Set API key for replicate library
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_KEY
        self.client = replicate.Client(api_token=REPLICATE_API_KEY)
    
    def create_generation(
        self,
        work_type: str,
        model_name: str,
        prompt: str,
        params: Dict[str, Any],
        webhook_url: str
    ) -> str:
        """
        Create a generation prediction on Replicate.
        
        Args:
            work_type: Type of generation (text-to-image, text-to-video, etc.)
            model_name: Name of the model
            prompt: Generation prompt
            params: Generation parameters
            webhook_url: Webhook URL for completion notification
            
        Returns:
            Prediction ID
        """
        try:
            # Get model configuration
            config = get_model_config(work_type, model_name)
            provider_model_id = config.get("provider_model_id") or config.get("replicate_model")
            
            # Prepare input
            input_data = {
                "prompt": prompt,
                **params
            }
            
            # Create prediction
            prediction = self.client.predictions.create(
                version=provider_model_id,
                input=input_data,
                webhook=webhook_url,
                webhook_events_filter=["completed"]
            )
            
            logger.info(f"Replicate prediction created: {prediction.id}")
            
            return prediction.id
            
        except Exception as e:
            # Log detailed error information for debugging
            import traceback
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "work_type": work_type,
                "model_name": model_name,
                "replicate_model": config.get("replicate_model") if 'config' in locals() else None,
            }
            logger.error(
                f"Failed to create Replicate prediction. Details: {error_details}"
            )
            
            # Raise user-friendly error message
            raise Exception(
                "The generation service is temporarily unavailable. "
                "Please contact support if this issue persists."
            )
    
    def get_prediction_status(self, prediction_id: str) -> Dict[str, Any]:
        """
        Get the status of a prediction.
        
        Args:
            prediction_id: Prediction ID
            
        Returns:
            Dictionary with prediction status and output
        """
        try:
            prediction = self.client.predictions.get(prediction_id)
            
            return {
                "id": prediction.id,
                "status": prediction.status,
                "output": prediction.output,
                "error": prediction.error if hasattr(prediction, "error") else None,
                "logs": prediction.logs if hasattr(prediction, "logs") else None,
            }
            
        except Exception as e:
            logger.error(f"Failed to get prediction status: {str(e)}")
            raise Exception(f"Failed to get prediction status: {str(e)}")
    
    def cancel_prediction(self, prediction_id: str) -> bool:
        """
        Cancel a running prediction.
        
        Args:
            prediction_id: Prediction ID
            
        Returns:
            True if cancelled successfully
        """
        try:
            self.client.predictions.cancel(prediction_id)
            logger.info(f"Prediction cancelled: {prediction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel prediction: {str(e)}")
            return False


# Singleton instance
_replicate_service: Optional[ReplicateService] = None


def get_replicate_service() -> ReplicateService:
    """
    Get or create ReplicateService singleton instance.
    
    Returns:
        ReplicateService instance
    """
    global _replicate_service
    if _replicate_service is None:
        _replicate_service = ReplicateService()
    return _replicate_service

