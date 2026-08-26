import replicate
import os
import json
from typing import Optional, Dict, Any
from .base import BaseProvider
from ...models.generation_config import get_model_config
from ...utils.logger import logger
from ...utils.config import get_provider_api_key

class ReplicateProvider(BaseProvider):
    def __init__(self):
        self.api_key = get_provider_api_key("replicate") or os.getenv("REPLICATE_API_KEY", "test_mock_key")
        # Only create real client if not in mock mode
        if self.api_key and not self.api_key.startswith("test_"):
            self.client = replicate.Client(api_token=self.api_key)
        else:
            self.client = None
            logger.info("ReplicateProvider running in MOCK mode")

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
        # Check for mock mode
        if self.api_key.startswith("test_"):
            import asyncio
            import httpx
            
            async def simulate_replicate():
                await asyncio.sleep(3)
                async with httpx.AsyncClient() as client:
                    await client.post(webhook_url, json={
                        "status": "succeeded",
                        "output": "https://picsum.photos/1024/1024",
                        "id": f"mock_{work_id}"
                    })
            
            asyncio.create_task(simulate_replicate())
            return f"mock_{work_id}"

        # Initialize provider_model_id to avoid UnboundLocalError in exception handlers
        provider_model_id = None
        try:
            # Try to get config from generation_config (for legacy models)
            # If it fails, assume model_id is already a provider_model_id (for workflows)
            try:
                config = get_model_config(work_type, model_id)
                provider_model_id = config.get("provider_model_id") or config.get("replicate_model")
            except ValueError:
                # model_id is not in generation_config, assume it's already a provider_model_id
                # This happens when called from workflow executor
                provider_model_id = model_id
                logger.info(f"Using model_id as provider_model_id directly: {model_id}")
            
            if not provider_model_id:
                raise ValueError(f"Model '{model_id}' has no provider_model_id configured")
            
            # Prepare input
            input_data = {
                "prompt": prompt,
                **params
            }
            
            # Try to get model config to check for multiple parameters
            model_config = None
            try:
                model_config = get_model_config(work_type, model_id)
            except ValueError:
                # Model not in config, that's okay - we'll use heuristics
                pass
            
            # Convert concepts string to list for Luma models if present
            if "concepts" in input_data and isinstance(input_data["concepts"], str) and input_data["concepts"].strip():
                input_data["concepts"] = [c.strip() for c in input_data["concepts"].split(",") if c.strip()]
            elif "concepts" in input_data and not input_data["concepts"]:
                # If concepts is an empty string, Replicate might expect a list or nothing
                del input_data["concepts"]
            
            # Convert parameters from string to array if configured as multiple
            params_config = model_config.get("params", {}) if model_config else {}
            for param_key, param_value in list(input_data.items()):
                if param_value is None:
                    continue
                
                # Check if this parameter is configured as multiple in model config
                param_def = params_config.get(param_key, {})
                is_multiple = param_def.get("multiple", False)
                
                # Convert string to array if config says multiple=True
                if is_multiple and isinstance(param_value, str) and param_value.strip():
                    input_data[param_key] = [param_value]
                    logger.info(f"Converted {param_key} from string to array for model {provider_model_id}")

            if negative_prompt:
                input_data["negative_prompt"] = negative_prompt
            
            # Prepare prediction parameters (no webhook: completion is detected by polling only)
            prediction_params = {
                "input": input_data,
            }

            # Create prediction
            # If provider_model_id contains a colon, it's a version hash
            if ":" in provider_model_id:
                version_id = provider_model_id.split(":")[1]
                prediction = self.client.predictions.create(
                    version=version_id,
                    **prediction_params
                )
            else:
                # Use model name directly
                # Robust way: get model first, then use latest_version id
                model = self.client.models.get(provider_model_id)
                version_id = getattr(model.latest_version, 'id', str(model.latest_version))
                prediction = self.client.predictions.create(
                    version=version_id,
                    **prediction_params
                )
            
            logger.info(f"Replicate prediction created for work {work_id}: {prediction.id}")
            return prediction.id
            
        except replicate.exceptions.ReplicateError as e:
            # Log detailed error information for debugging
            import traceback
            error_details = {
                "work_id": work_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "model_id": model_id,
                "provider_model_id": provider_model_id,
            }
            logger.error(
                f"Failed to create Replicate prediction for work {work_id}. Details: {error_details}"
            )
            
            # Convert Replicate errors to more user-friendly messages
            error_msg = str(e).lower()
            if "internal server error" in error_msg:
                raise Exception("The generation service is temporarily unavailable. Please try again in a few moments.")
            elif "quota" in error_msg or "limit" in error_msg or "rate limit" in error_msg:
                raise Exception("Service quota exceeded. Please try again later.")
            elif "invalid" in error_msg or "not found" in error_msg:
                raise Exception(f"Model configuration error: {str(e)}")
            elif "timeout" in error_msg:
                raise Exception("Request timed out. Please try again.")
            else:
                # Re-raise with more context
                raise Exception(f"Generation service error: {str(e)}")
        except json.JSONDecodeError as e:
            # Handle case where Replicate API returns error status but empty response body
            # This often happens with rate limiting (429) or server errors (500)
            import traceback
            tb_str = traceback.format_exc()
            
            # Check if this JSONDecodeError is from Replicate client
            if "replicate" in tb_str.lower() or "prediction.py" in tb_str or "_raise_for_status" in tb_str:
                error_details = {
                    "work_id": work_id,
                    "error_type": "JSONDecodeError (likely Replicate API error)",
                    "error_message": str(e),
                    "traceback": tb_str,
                    "model_id": model_id,
                    "provider_model_id": provider_model_id,
                    "note": "Replicate API returned error status with empty response body. This often indicates rate limiting or server error."
                }
                logger.error(
                    f"Failed to create Replicate prediction for work {work_id}. Details: {error_details}"
                )
                
                # Check traceback for HTTP status codes
                if "429" in tb_str or "rate" in tb_str.lower() or "limit" in tb_str.lower():
                    raise Exception("Service quota exceeded. Please try again later.")
                elif "500" in tb_str or "502" in tb_str or "503" in tb_str:
                    raise Exception("The generation service is temporarily unavailable. Please try again in a few moments.")
                else:
                    # Generic error for empty response
                    raise Exception("Generation service error: API returned empty response. This may indicate rate limiting or service issues. Please try again later.")
            else:
                # Not a Replicate error, re-raise as-is
                raise
        except Exception as e:
            # Log detailed error information for debugging
            import traceback
            tb_str = traceback.format_exc()
            
            # Check if this might be a Replicate-related error
            error_msg = str(e).lower()
            is_replicate_error = (
                "replicate" in error_msg or 
                "replicate" in tb_str.lower() or
                "prediction" in error_msg
            )
            
            error_details = {
                "work_id": work_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": tb_str,
                "model_id": model_id,
                "provider_model_id": provider_model_id,
            }
            logger.error(
                f"Failed to create Replicate prediction for work {work_id}. Details: {error_details}"
            )
            
            # If it's a Replicate-related error, try to provide better error messages
            if is_replicate_error:
                if "429" in tb_str or "rate" in error_msg or "limit" in error_msg:
                    raise Exception("Service quota exceeded. Please try again later.")
                elif "500" in tb_str or "502" in tb_str or "503" in tb_str or "internal server" in error_msg:
                    raise Exception("The generation service is temporarily unavailable. Please try again in a few moments.")
                elif "timeout" in error_msg or "timed out" in error_msg:
                    raise Exception("Request timed out. Please try again.")
            
            # Re-raise to be handled by upper layer with user-friendly message
            raise

    def _output_to_file_url(self, output: Any) -> Optional[str]:
        """
        Normalize Replicate output to a single URL string.
        Replicate Python client may return file objects (with .url() method),
        list of URLs, dict like {"image": "url"}, or raw URL string.
        """
        if output is None:
            return None
        # List: take first element (image models return [url] or [file_obj])
        if isinstance(output, list) and len(output) > 0:
            output = output[0]
        # File object (newer Replicate SDK)
        if hasattr(output, "url") and callable(getattr(output, "url")):
            return output.url()
        # Already a string URL
        if isinstance(output, str) and (output.startswith("http://") or output.startswith("https://")):
            return output
        # Dict: common keys for image/video URL (value may still be file object)
        if isinstance(output, dict):
            val = (
                output.get("url")
                or output.get("image")
                or output.get("file_url")
                or output.get("output")
                or (list(output.values())[0] if output else None)
            )
            if val is not None and not isinstance(val, str):
                return self._output_to_file_url(val)
            return val
        return str(output) if output else None

    async def handle_webhook(self, work_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the Replicate webhook payload.
        Standard format for Replicate: status, output, error.
        """
        raw_status = payload.get("status")
        # Normalize: client may return str or enum (e.g. PredictionStatus.SUCCEEDED)
        status = str(getattr(raw_status, "value", raw_status)).lower() if raw_status is not None else ""
        output = payload.get("output")
        error = payload.get("error")

        if status == "succeeded":
            file_url = self._output_to_file_url(output)
            if not file_url:
                logger.warning(f"Replicate webhook succeeded but no file_url from output: type={type(output)!r}")
            return {
                "status": "success",
                "file_url": file_url
            }
        elif status in ("failed", "canceled"):
            return {
                "status": "failed",
                "error": error or "Generation failed"
            }
        else:
            return {
                "status": "processing"
            }

    async def get_status(self, provider_task_id: str) -> Dict[str, Any]:
        """
        Poll Replicate API for prediction status.
        """
        if self.api_key.startswith("test_"):
            return {"status": "processing"}

        try:
            prediction = self.client.predictions.get(provider_task_id)
            # Normalize status (client may return str or enum)
            raw_status = prediction.status
            status_str = str(getattr(raw_status, "value", raw_status)).lower() if raw_status is not None else ""
            payload = {
                "status": status_str or raw_status,
                "output": prediction.output,
                "error": prediction.error
            }
            return await self.handle_webhook(0, payload)  # work_id not used in handle_webhook
            
        except Exception as e:
            logger.error(f"Failed to get Replicate status: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
