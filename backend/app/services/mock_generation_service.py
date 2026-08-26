"""
Mock AI Generation Service for Local Development & Open-Source Testing.
======================================================================
Allows developers to test generation workflows, UI progress bars, credit economics,
and WebSocket notifications without invoking external paid APIs (Replicate, Gemini).

To enable:
    Set MOCK_AI_GENERATION=true in backend/.env or docker-compose.yml
"""
import os
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..models.work import Work, WorkStatus
from ..services.storage import get_storage_service
from ..services.realtime import publish_user_event
from ..utils.logger import logger


def is_mock_generation_enabled() -> bool:
    """Check if MOCK_AI_GENERATION mode is enabled via environment variables."""
    val = os.getenv("MOCK_AI_GENERATION", "false").strip().lower()
    return val in ("true", "1", "yes", "y", "on")


def process_mock_generation(db: Session, work_id: int, delay_seconds: float = 3.0) -> dict:
    """
    Process mock generation for a work record.
    Simulates async API execution, sets mock media URLs, updates DB, and sends WS notification.
    """
    logger.info(f"🎨 [MOCK AI GENERATION] Simulating AI generation for work_id={work_id}...")
    
    # 1. Fetch work
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        logger.error(f"[MOCK AI GENERATION] Work {work_id} not found in database")
        return {"status": "error", "message": f"Work {work_id} not found"}

    # 2. Simulate processing delay
    if delay_seconds > 0:
        time.sleep(delay_seconds)

    # 3. Determine media type (video vs image)
    is_video = "video" in (work.type or "").lower()

    if is_video:
        # High quality sample video for text2video / img2video
        sample_file = "https://cdn.vidgenerator.ai/MOMh3WFh9u3MVFoyV1aiUe5KRq2t.mp4"
        sample_thumb = f"https://picsum.photos/seed/{work_id}/720/1280"
        ext = "mp4"
    else:
        # High quality sample image for text2img / img2img / img_effects
        sample_file = f"https://picsum.photos/seed/{work_id}/1024/1024"
        sample_thumb = f"https://picsum.photos/seed/{work_id}/512/512"
        ext = "jpg"

    storage = get_storage_service()
    canonical = storage.generate_canonical_url(
        storage_key=f"mock_{work_id}",
        title=work.prompt or "mock-generation",
        file_ext=ext
    )

    # 4. Update work record
    work.status = WorkStatus.COMPLETED
    work.file_url = sample_file
    work.thumbnail_url = sample_thumb
    work.canonical_url = canonical
    work.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(work)

    logger.info(f"✅ [MOCK AI GENERATION] Work {work_id} completed successfully (Mock Mode).")

    # 5. Publish completion for delivery by the API WebSocket subscriber.
    publish_user_event(work.user_id, {
        "type": "generation_complete",
        "work_id": work_id,
        "status": "success",
        "file_url": sample_file,
        "thumbnail_url": sample_thumb,
        "canonical_url": canonical,
        "is_mock": True,
    })

    return {
        "status": "completed",
        "work_id": work_id,
        "is_mock": True,
        "file_url": sample_file,
        "thumbnail_url": sample_thumb,
        "canonical_url": canonical
    }
