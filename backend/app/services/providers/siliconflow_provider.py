import os
import httpx
import asyncio
from typing import Optional, Dict, Any
from .base import BaseProvider
from ...models.generation_config import get_model_config
from ...utils.logger import logger
from ...utils.config import get_provider_api_key
from openai import OpenAI

class SiliconFlowProvider(BaseProvider):
    def __init__(self):
        self.api_key = get_provider_api_key("siliconflow") or os.getenv("SILICONFLOW_API_KEY", "test_mock_key")
        self.base_url = "https://api.siliconflow.cn/v1"
        
        # Only create real client if not in mock mode
        if not self.api_key.startswith("test_"):
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
            logger.info("SiliconFlowProvider running in MOCK mode")

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
        # Siliconflow API is synchronous. We'll run it in a thread to not block.
        # Then we'll simulate a webhook call to maintain the unified async architecture.
        
        # Try to get config from generation_config (for legacy models)
        # If it fails, assume model_id is already a provider_model_id (for workflows)
        try:
            config = get_model_config(work_type, model_id)
            provider_model_id = config.get("provider_model_id") or config.get("model_id")
        except ValueError:
            # model_id is not in generation_config, assume it's already a provider_model_id
            # This happens when called from workflow executor
            provider_model_id = model_id
            logger.info(f"Using model_id as provider_model_id directly: {model_id}")
        
        # Check if this is a Qwen model
        is_qwen_model = "Qwen" in provider_model_id
        # Qwen/Qwen-Image-Edit (image-to-image) doesn't support image_size, but Qwen/Qwen-Image (text-to-image) does
        is_qwen_edit_model = provider_model_id == "Qwen/Qwen-Image-Edit"
        
        # Check if this is a Wan model
        is_wan_model = "Wan" in provider_model_id
        
        steps = params.get("num_inference_steps")
        seed = params.get("seed")
        batch_size = params.get("batch_size", 1)
        
        extra_body = {}
        if steps is not None:
            extra_body["num_inference_steps"] = steps
        
        # Qwen models use cfg, Kolors uses guidance_scale
        if is_qwen_model:
            cfg = params.get("cfg")
            if cfg is not None:
                extra_body["cfg"] = cfg
            
            # Qwen/Qwen-Image (text-to-image) supports image_size, but Qwen/Qwen-Image-Edit doesn't
            if not is_qwen_edit_model:
                width = params.get("width", 1328)
                height = params.get("height", 1328)
                size = f"{width}x{height}"
                extra_body["image_size"] = size
        elif is_wan_model:
            # Wan models (T2V, I2V)
            # T2V requires image_size, I2V also lists it as required in some docs
            image_size = params.get("image_size")
            if image_size:
                extra_body["image_size"] = image_size
            else:
                # Default if not provided
                extra_body["image_size"] = "1280x720"
        else:
            # Kolors models
            width = params.get("width", 1024)
            height = params.get("height", 1024)
            size = f"{width}x{height}"
            extra_body["image_size"] = size
            extra_body["batch_size"] = batch_size
            
            guidance_scale = params.get("guidance_scale")
            if guidance_scale is not None:
                extra_body["guidance_scale"] = guidance_scale
        
        # Only include seed if it's >= 0 (SiliconFlow requires non-negative seed)
        if seed is not None and seed >= 0:
            extra_body["seed"] = seed
        
        if negative_prompt:
            extra_body["negative_prompt"] = negative_prompt
            
        # Add any other image parameters from params
        for key, value in params.items():
            if isinstance(value, str) and (value.startswith("http") or value.startswith("data:image")):
                # Avoid duplicate if it's already in extra_body
                if key not in extra_body:
                    extra_body[key] = value
        
        # Determine size parameter for API call
        size = None
        if is_qwen_edit_model:
            size = None
        elif is_qwen_model:
            width = params.get("width", 1328)
            height = params.get("height", 1328)
            size = f"{width}x{height}"
        elif is_wan_model:
            # Wan models don't use 'size' parameter in images.generate, they use extra_body
            size = None
        else:
            size = extra_body.get("image_size", "1024x1024")

        # Start background task to call the sync API and then hit our webhook
        asyncio.create_task(self._run_sync_generation(
            work_id, provider_model_id, prompt, size, extra_body, webhook_url
        ))

        return f"sf_{work_id}"

    async def _run_sync_generation(self, work_id, model_id, prompt, size, extra_body, webhook_url):
        try:
            # Check for mock key or no client
            if not self.client or self.api_key.startswith("test_"):
                logger.info(f"Running SiliconFlow generation in MOCK mode for work {work_id}")
                await asyncio.sleep(3)
                
                # Use a video URL if it's a video model
                is_video = "Wan" in model_id or "video" in model_id
                output_url = "https://siliconflow-api-oss.oss-cn-beijing.aliyuncs.com/community/wan2.1/T2V_1.mp4" if is_video else "https://picsum.photos/1024/1024"
                
                payload = {
                    "status": "succeeded",
                    "output": output_url,
                    "id": f"sf_mock_{work_id}"
                }
            else:
                # Actual API call (run in executor to avoid blocking)
                loop = asyncio.get_event_loop()
                
                # Determine which API endpoint to use
                is_video = "Wan" in model_id
                
                if is_video:
                    # Wan video models use a different endpoint than images.generate
                    # It's usually /v1/video/submit and it's ASYNCHRONOUS
                    logger.info(f"Calling SiliconFlow Video API for model {model_id}")
                    
                    async with httpx.AsyncClient() as client:
                        headers = {
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        }
                        data = {
                            "model": model_id,
                            "prompt": prompt,
                            **extra_body
                        }
                        
                        response = await client.post(
                            f"{self.base_url}/video/submit",
                            headers=headers,
                            json=data,
                            timeout=60.0
                        )
                        
                        if response.status_code != 200:
                            logger.error(f"SiliconFlow Video API submit failed ({response.status_code}): {response.text}")
                            raise Exception(f"SiliconFlow Video API submit failed: {response.text}")
                        
                        resp_json = response.json()
                        request_id = resp_json.get("requestId")
                        
                        if not request_id:
                            # Maybe it returned the URL directly?
                            output_url = resp_json.get("url") or (resp_json.get("data", [{}])[0].get("url") if resp_json.get("data") else None)
                            if not output_url:
                                raise Exception(f"SiliconFlow Video API response missing requestId and URL: {resp_json}")
                        else:
                            # It's async, we need to poll
                            logger.info(f"Polling SiliconFlow Video status for requestId: {request_id}")
                            output_url = await self._poll_video_status(request_id)
                else:
                    # Image models
                    # Prepare API call parameters
                    api_params = {
                        "model": model_id,
                        "prompt": prompt,
                        "n": 1,
                        "extra_body": extra_body
                    }
                    
                    # Only include size for non-Qwen/non-Wan models
                    if size is not None:
                        api_params["size"] = size
                    
                    response = await loop.run_in_executor(None, lambda: self.client.images.generate(**api_params))
                    output_url = response.data[0].url
                
                payload = {
                    "status": "succeeded",
                    "output": output_url,
                    "id": f"sf_{work_id}"
                }

            # Call our webhook
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json=payload)
                
        except Exception as e:
            # 🛡️ Only call failure webhook if we haven't succeeded yet
            # In a real sync task, this is implicit, but let's be safe
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"SiliconFlow generation failed for work {work_id}:\n{error_details}")
            
            # Avoid sending failure if we already know we succeeded (unlikely but safe)
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(webhook_url, json={
                        "status": "failed",
                        "error": str(e)
                    })
            except:
                pass

    async def handle_webhook(self, work_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Since we triggered the webhook ourselves in _run_sync_generation,
        we just follow the same standard format as Replicate for simplicity.
        """
        status = payload.get("status")
        if status == "succeeded":
            return {
                "status": "success",
                "file_url": payload.get("output")
            }
        else:
            return {
                "status": "failed",
                "error": payload.get("error", "Generation failed")
            }

    async def get_status(self, provider_task_id: str) -> Dict[str, Any]:
        """
        SiliconFlow is handled via internal polling in _run_sync_generation,
        so this method is mainly for architectural completeness.
        """
        return {"status": "processing"}

    async def _poll_video_status(self, request_id: str, max_attempts: int = 60, interval: int = 5) -> str:
        """
        Poll SiliconFlow Video API for status.
        """
        # SiliconFlow Video API endpoints can be tricky. We'll log the full URL.
        url = f"{self.base_url}/video/status"
        logger.info(f"Polling SiliconFlow Video status for requestId: {request_id} at {url}")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            for attempt in range(max_attempts):
                try:
                    # NOTE: Documentation says POST /video/status with requestId in JSON body
                    response = await client.post(
                        url,
                        headers=headers,
                        json={"requestId": request_id},
                        timeout=15.0
                    )
                    
                    # FALLBACK: If 404, try /v1/video/get-result which is used by some other Wan versions
                    if response.status_code == 404:
                        fallback_url = f"{self.base_url}/video/get-result"
                        logger.info(f"404 on /video/status, trying fallback: {fallback_url}")
                        # For get-result it's usually GET with query param
                        response = await client.get(
                            fallback_url,
                            headers={"Authorization": f"Bearer {self.api_key}"},
                            params={"requestId": request_id},
                            timeout=10.0
                        )
                    
                    resp_json = response.json()
                    # Expected status values: 'Succeed', 'InQueue', 'InProgress', 'Failed'
                    # We'll use case-insensitive check to be safe
                    status = str(resp_json.get("status", "")).lower()
                    
                    if status == "succeed":
                        results = resp_json.get("results", {})
                        # Results can contain 'videos' (list) or 'video' (object/string)
                        video_url = None
                        if "videos" in results and results["videos"]:
                            video_url = results["videos"][0].get("url")
                        elif "video" in results:
                            video_url = results["video"] if isinstance(results["video"], str) else results["video"].get("url")
                        
                        if video_url:
                            return video_url
                            
                        # Try to find any URL in the results
                        import json
                        logger.info(f"SF Video generation succeeded but no obvious URL found. Results: {json.dumps(results)}")
                        raise Exception("No video URL found in success response")
                    
                    elif status == "failed":
                        error_msg = resp_json.get("reason") or "Unknown error"
                        raise Exception(f"SiliconFlow Video generation failed: {error_msg}")
                    
                    # If still processing (InQueue, InProgress), wait and retry
                    current_status = resp_json.get("status", "Unknown")
                    logger.info(f"Video {request_id} status: {current_status}, retrying in {interval}s...")
                    
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error during SF poll: {str(e)}")
                except Exception as e:
                    logger.error(f"Error during SF poll: {str(e)}")
                    if "failed" in str(e).lower() or "timeout" in str(e).lower():
                        raise
                
                await asyncio.sleep(interval)
            
            raise Exception("SiliconFlow Video generation timed out")

