"""Gemini provider for workflow: sync API adapted to async provider interface via result cache."""
import uuid
from typing import Optional, Dict, Any

from .base import BaseProvider
from ...utils.logger import logger
from ...services.gemini_service import get_gemini_service


class GeminiProvider(BaseProvider):
    """
    Adapts Google Gemini (sync generateContent) to workflow Provider contract.
    Calls Gemini in create_generation, caches result, returns synthetic task ID;
    get_status returns cached result so workflow/polling sees unified status.
    """

    def __init__(self):
        self._result_cache: Dict[str, Dict[str, Any]] = {}

    def _synthetic_id(self) -> str:
        return f"gemini_{uuid.uuid4().hex}"

    async def create_generation(
        self,
        work_id: int,
        work_type: str,
        model_id: str,
        prompt: str,
        negative_prompt: Optional[str],
        params: Dict[str, Any],
        webhook_url: str,
    ) -> str:
        synthetic_id = self._synthetic_id()
        try:
            gemini = get_gemini_service(db_session=None)
            p = dict(params)
            if model_id and not p.get("model") and not p.get("model_name"):
                p["model_name"] = model_id
            text = gemini.generate_content_for_workflow(prompt, p)
            
            result = {
                "status": "success",
                "file_url": None,
                "text": text,
            }
            self._result_cache[synthetic_id] = result
            
            # Trigger the webhook immediately but synchronously to ensure it happens
            if webhook_url:
                import httpx
                import asyncio
                # We stay in the loop to ensure this completes
                try:
                    # Very brief sleep to let other things breathe, 
                    # but we AWAIT the post so it's guaranteed to send.
                    await asyncio.sleep(0.1)
                    async with httpx.AsyncClient() as client:
                        logger.info(f"Gemini triggering direct webhook for work {work_id}")
                        await client.post(webhook_url, json={
                            "status": "succeeded",
                            "output": text,
                            "id": synthetic_id
                        }, timeout=5.0)
                except Exception as we:
                    logger.error(f"Failed to trigger Gemini webhook for {work_id}: {we}")

        except Exception as e:
            logger.exception(f"Gemini workflow generation failed for work {work_id}")
            result = {
                "status": "failed",
                "error": str(e),
                "file_url": None,
                "text": None,
            }
            self._result_cache[synthetic_id] = result
            
            if webhook_url:
                import httpx
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(webhook_url, json={
                            "status": "failed",
                            "error": str(e),
                            "id": synthetic_id
                        }, timeout=5.0)
                except: pass

        return synthetic_id

    async def handle_webhook(self, work_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini does not send webhooks; return processing so caller does not treat as completion."""
        return {"status": "processing"}

    async def get_status(self, provider_task_id: str) -> Dict[str, Any]:
        """Return cached result for synthetic task ID; normalize to provider contract."""
        if not provider_task_id.startswith("gemini_"):
            return {"status": "failed", "error": "Invalid Gemini task ID"}
        result = self._result_cache.pop(provider_task_id, None)
        if result is None:
            return {"status": "processing"}
        # Normalize: workflow expects status in ("success", "failed", "processing") and optional file_url, text
        status = result.get("status", "failed")
        out = {
            "status": status,
            "file_url": result.get("file_url"),
            "error": result.get("error"),
        }
        if result.get("text") is not None:
            out["text"] = result["text"]
        return out
