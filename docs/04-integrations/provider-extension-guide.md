# AI Provider Extension Guide (3-Step Tutorial)

This guide walks developers through adding custom AI model provider adapters (SiliconFlow, Replicate, Gemini, HunyuanVideo, Wan 2.1, Midjourney, etc.) to VidGen.

---

## 🛠️ Step 1: Subclass `BaseProviderAdapter`

Create a new adapter file at `backend/app/services/ai_providers/custom_provider.py`:

```python
import httpx
from typing import Dict, Any
from app.services.ai_providers.base import BaseProviderAdapter, GenerationResult

class CustomProviderAdapter(BaseProviderAdapter):
    """Adapter for Custom AI Model Provider API."""

    def __init__(self, api_key: str, base_url: str = "https://api.customprovider.ai"):
        self.api_key = api_key
        self.base_url = base_url

    async def generate(self, prompt: str, params: Dict[str, Any]) -> GenerationResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "width": params.get("width", 1024),
            "height": params.get("height", 1024),
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self.base_url}/v1/generate", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return GenerationResult(
            image_url=data.get("output_url"),
            seed=data.get("seed"),
            raw_response=data
        )
```

---

## 🛠️ Step 2: Register in `ProviderFactory`

Register your adapter in `backend/app/services/ai_providers/factory.py`:

```python
from app.services.ai_providers.custom_provider import CustomProviderAdapter

class ProviderFactory:
    _adapters = {
        "siliconflow": SiliconFlowAdapter,
        "replicate": ReplicateAdapter,
        "gemini": GeminiAdapter,
        "custom_provider": CustomProviderAdapter,  # <-- Register your new adapter
    }

    @classmethod
    def get_adapter(cls, provider_name: str, **kwargs) -> BaseProviderAdapter:
        adapter_cls = cls._adapters.get(provider_name.lower())
        if not adapter_cls:
            raise ValueError(f"Unsupported AI Provider: {provider_name}")
        return adapter_cls(**kwargs)
```

---

## 🛠️ Step 3: Enable Model in Admin Panel or DB

Create a model entry in `generation_models` pointing to your new provider adapter:

```sql
INSERT INTO generation_models (model_key, name, work_type, provider_name, cost_credits)
VALUES ('custom-flux-v1', 'Custom Flux V1', 'text2img', 'custom_provider', 10);
```
