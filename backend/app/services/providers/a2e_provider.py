import os
import httpx
import asyncio
import json
import uuid
import mimetypes
from typing import Optional, Dict, Any, List
from .base import BaseProvider
from ...utils.logger import logger
from ...utils.config import get_provider_api_key, get_system_config

class A2EProvider(BaseProvider):
    def __init__(self):
        self.api_key = get_provider_api_key("a2e") or os.getenv("A2E_API_KEY") or os.getenv("A2E_API_TOKEN", "test_mock_key")
        self.base_url = get_system_config("a2e_api_base_url", "https://video.a2e.ai")
        
        if self.api_key.startswith("test_"):
            logger.info("A2EProvider running in MOCK mode")

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
        Create a generation task on A2E platform.
        """
        # A2E doesn't support webhooks, so we'll start a background task to poll
        # and then call our own webhook to follow the unified architecture.
        
        # 1. Determine task type and parameters
        is_video = work_type in ["text-to-video", "image-to-video", "text2video", "img2video"]
        
        # 2. Extract and re-upload images if necessary
        # A2E requires images to be on their R2 storage
        reuploaded_params = params.copy()
        
        # Check for image inputs
        image_fields = ["image_url", "input_images"]
        for field in image_fields:
            if field in reuploaded_params:
                value = reuploaded_params[field]
                if isinstance(value, str) and value.startswith("http"):
                    # Single image URL
                    new_url = await self._ensure_image_on_a2e(value, "image2video" if is_video else "text2image")
                    reuploaded_params[field] = new_url
                elif isinstance(value, list):
                    # List of image URLs
                    new_urls = []
                    for url in value:
                        if isinstance(url, str) and url.startswith("http"):
                            new_urls.append(await self._ensure_image_on_a2e(url, "text2image"))
                        else:
                            new_urls.append(url)
                    reuploaded_params[field] = new_urls

        # 3. Execute the full flow (Submit -> Poll -> Webhook)
        # In Celery context, we should await this so the loop doesn't close prematurely
        await self._run_a2e_flow(
            work_id, work_type, model_id, prompt, negative_prompt, reuploaded_params, webhook_url
        )

        return f"a2e_{work_id}"

    async def _run_a2e_flow(self, work_id, work_type, model_id, prompt, negative_prompt, params, webhook_url):
        """
        Background flow: Submit -> Poll -> Webhook
        """
        try:
            if self.api_key.startswith("test_"):
                logger.info(f"Running A2E generation in MOCK mode for work {work_id}")
                await asyncio.sleep(3)
                is_video = "video" in work_type or "Wan" in model_id
                output_url = "https://3days-apac.generativeairesult.com/demo.mp4" if is_video else "https://picsum.photos/1024/1024"
                
                payload = {
                    "status": "succeeded",
                    "output": output_url,
                    "id": f"a2e_mock_{work_id}"
                }
                async with httpx.AsyncClient() as client:
                    await client.post(webhook_url, json=payload)
                return

            # 1. Submit task
            is_video = work_type in ["text-to-video", "image-to-video", "text2video", "img2video"]
            
            endpoint = "/api/v1/userWan25/start" if is_video else "/api/v1/userText2Image/start"
            
            # Map parameters
            a2e_payload = self._map_params(work_type, model_id, prompt, negative_prompt, params)
            
            logger.info(f"Submitting A2E task: {endpoint} for work {work_id}")
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    json=a2e_payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"A2E submission failed ({response.status_code}): {response.text}")
                    raise Exception(f"A2E submission failed: {response.text}")
                
                resp_data = response.json()
                if resp_data.get("code") != 0:
                    logger.error(f"A2E API error: {resp_data.get('message')}")
                    raise Exception(f"A2E API error: {resp_data.get('message')}")
                
                # Get external task ID
                data = resp_data.get("data")
                external_id = None
                if isinstance(data, list) and len(data) > 0:
                    external_id = data[0].get("_id")
                elif isinstance(data, dict):
                    external_id = data.get("_id")
                
                if not external_id:
                    raise Exception("A2E returned success but no task ID found")
                
                logger.info(f"A2E task submitted successfully: {external_id} for work {work_id}")
                
                # 2. Poll for status
                output_url = await self._poll_a2e_status(external_id, is_video)
                
                # 3. Success! Call webhook
                payload = {
                    "status": "succeeded",
                    "output": output_url,
                    "id": external_id
                }
                await client.post(webhook_url, json=payload)

        except Exception as e:
            logger.error(f"A2E flow failed for work {work_id}: {str(e)}")
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(webhook_url, json={
                        "status": "failed",
                        "error": str(e)
                    })
            except:
                pass

    def _map_params(self, work_type: str, model_id: str, prompt: str, negative_prompt: Optional[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map vidgen parameters to A2E parameters.
        """
        is_video = "video" in work_type
        
        if is_video:
            #  (I2V)
            # A2E : name, image_url, prompt, duration, resolution, enable_prompt_expansion, model, audio
            return {
                "name": params.get("name", f"task_{uuid.uuid4().hex[:8]}"),
                "image_url": params.get("image_url"),
                "prompt": prompt,
                "negative_prompt": negative_prompt or params.get("negative_prompt"),
                "duration": str(params.get("duration", "5")),
                "resolution": params.get("resolution", "720p").lower(),
                "enable_prompt_expansion": params.get("enable_prompt_expansion", False),
                "model": model_id if "wan" in model_id.lower() else "wan2.6-i2v-flash",
                "audio": params.get("audio", True),
                "seed": params.get("seed"),
                "multi_shots": params.get("multi_shots", False)
            }
        else:
            #  (T2I)
            # A2E : name, prompt, width, height, model_type, input_images, aspect_ratio, max_images, resolution
            aspect_ratio = params.get("aspect_ratio")
            width = params.get("width", 1024)
            height = params.get("height", 1024)
            
            # A2E resolution mapping: 1080p -> 1080P
            res = params.get("resolution", "1080p")
            if res.lower() == "1080p": res = "1080P"
            elif res.lower() == "2k": res = "2K"
            elif res.lower() == "4k": res = "4K"
            
            # Determine model_type
            model_type = params.get("model_type")
            if not model_type:
                model_id_lower = model_id.lower()
                if "seedream" in model_id_lower:
                    model_type = "seedream"
                else:
                    model_type = "a2e"
            
            payload = {
                "name": params.get("name", f"task_{uuid.uuid4().hex[:8]}"),
                "prompt": prompt,
                "width": width,
                "height": height,
                "model_type": model_type,
                "input_images": params.get("input_images", []),
                "max_images": 1,
                "resolution": res
            }
            if aspect_ratio:
                payload["aspect_ratio"] = aspect_ratio
                # If aspect_ratio is provided, A2E requires dimensions to match
                # Reference text2img.md mapping
                mapping = {
                    "1:1": (1024, 1024),
                    "16:9": (1344, 768),
                    "9:16": (768, 1344),
                    "4:3": (1024, 768),
                    "3:4": (768, 1024),
                    "2:3": (683, 1024),
                    "3:2": (1024, 683),
                }
                if aspect_ratio in mapping:
                    payload["width"], payload["height"] = mapping[aspect_ratio]
            
            return payload

    async def _ensure_image_on_a2e(self, image_url: str, task_type: str) -> str:
        """
        Check if the image is already on A2E domain, if not, re-upload it.
        """
        if "generativeairesult.com" in image_url:
            return image_url
            
        logger.info(f"Image {image_url} is not on A2E, re-uploading...")
        
        try:
            async with httpx.AsyncClient() as client:
                # 1. Download image
                resp = await client.get(image_url, timeout=30.0)
                resp.raise_for_status()
                img_data = resp.content
                content_type = resp.headers.get("content-type") or "image/jpeg"
                
                # 2. Get presigned URL from A2E
                # POST /api/v1/r2/upload-presigned-url
                # Body: { bucket: "3days-apac", content_type: "...", key: "...", type: "..." }
                
                date_str = asyncio.get_event_loop().time() # Not really a date, but we just need uniqueness
                import datetime
                now = datetime.datetime.now()
                date_str = now.strftime("%Y%m%d")
                
                ext = mimetypes.guess_extension(content_type) or ".jpg"
                uuid_str = uuid.uuid4().hex
                
                if task_type == "text2image":
                    base_key = f"user_text_to_image/{date_str}/{uuid_str}{ext}"
                else:
                    base_key = f"user_image_to_video_wan25/{date_str}/{uuid_str}{ext}"
                    
                presigned_payload = {
                    "bucket": "3days-apac",
                    "content_type": content_type,
                    "key": base_key,
                    "type": task_type
                }
                
                headers = {"Authorization": f"Bearer {self.api_key}"}
                p_resp = await client.post(
                    f"{self.base_url}/api/v1/r2/upload-presigned-url",
                    headers=headers,
                    json=presigned_payload,
                    timeout=10.0
                )
                
                if p_resp.status_code != 200:
                    raise Exception(f"Failed to get A2E presigned URL: {p_resp.text}")
                
                p_data = p_resp.json()
                if p_data.get("code") != 0:
                    raise Exception(f"A2E Presigned API error: {p_data.get('message')}")
                
                upload_url = p_data["data"]["uploadUrl"]
                full_key = p_data["data"]["key"]
                
                # 3. Upload to R2
                u_resp = await client.put(
                    upload_url,
                    content=img_data,
                    headers={"Content-Type": content_type},
                    timeout=60.0
                )
                
                if u_resp.status_code != 200:
                    raise Exception(f"Failed to upload image to A2E R2: {u_resp.status_code}")
                
                # 4. Return the new URL
                return f"https://3days-apac.generativeairesult.com/{full_key}"
                
        except Exception as e:
            logger.error(f"Failed to re-upload image to A2E: {str(e)}")
            # Fallback to original URL, though it might fail later
            return image_url

    async def _poll_a2e_status(self, external_id: str, is_video: bool, max_attempts: int = 120, interval: int = 5) -> str:
        """
        Poll A2E for task completion.
        """
        logger.info(f"Polling A2E status for task {external_id}")
        
        endpoint = f"/api/v1/userWan25/{external_id}" if is_video else f"/api/v1/userText2Image/{external_id}"
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            for attempt in range(max_attempts):
                try:
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=15.0
                    )
                    
                    if response.status_code != 200:
                        logger.warning(f"A2E poll failed ({response.status_code}), retrying...")
                        await asyncio.sleep(interval)
                        continue
                        
                    data = response.json()
                    task_data = data.get("data")
                    if task_data is None:
                        logger.warning(f"A2E poll returned empty data for task {external_id}, retrying...")
                        await asyncio.sleep(interval)
                        continue
                        
                    status = task_data.get("current_status")
                    
                    if status in ["completed", "success"]:
                        # Extract result URL
                        if is_video:
                            url = task_data.get("result_url") or task_data.get("video_url")
                            if url: return url
                        else:
                            urls = task_data.get("image_urls")
                            if urls and len(urls) > 0: return urls[0]
                            url = task_data.get("result_url") or task_data.get("image_url")
                            if url: return url
                        
                        raise Exception("A2E task completed but no output URL found")
                    
                    elif status in ["failed", "error"]:
                        msg = task_data.get("failed_message") or task_data.get("error_message") or "Platform error"
                        raise Exception(f"A2E generation failed: {msg}")
                    
                    # Still processing
                    logger.info(f"A2E task {external_id} status: {status}, attempt {attempt+1}/{max_attempts}")
                    
                except httpx.HTTPError:
                    pass # Ignore network errors and retry
                
                await asyncio.sleep(interval)
                
            raise Exception("A2E generation timed out")

    async def handle_webhook(self, work_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process internal webhook (triggered by _run_a2e_flow).
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
        Return processing since internal flow handles polling.
        """
        return {"status": "processing"}
