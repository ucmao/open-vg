"""Carousel (homepage_blocks type=carousel)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone

from ..models.base import get_db
from ..models.homepage_block import HomepageBlock
from ..utils.responses import success_response, error_response
from ..utils.logger import logger

router = APIRouter()


@router.get("/carousel/config")
def get_carousel_config_public(db: Session = Depends(get_db)):
    try:
        block = (
            db.query(HomepageBlock)
            .filter(HomepageBlock.type == "carousel", HomepageBlock.is_enabled == True)
            .order_by(HomepageBlock.sort_order)
            .first()
        )
        if not block or not block.config:
            return success_response(
                data={
                    "interval": 5000,
                    "autoplay": True,
                    "show_arrows": True,
                    "show_indicators": True,
                },
                message="Carousel config retrieved successfully",
            )
        c = block.config
        return success_response(
            data={
                "interval": c.get("interval", 5000),
                "autoplay": c.get("autoplay", True),
                "show_arrows": c.get("show_arrows", True),
                "show_indicators": c.get("show_indicators", True),
            },
            message="Carousel config retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error getting carousel config: {e}")
        return error_response(message="Failed to fetch carousel config")


def _filter_slide_by_time(slide, now):
    start_time = slide.get("start_time")
    end_time = slide.get("end_time")
    if start_time:
        try:
            st = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            if st.tzinfo is None:
                st = st.replace(tzinfo=timezone.utc)
            if st > now:
                return False
        except Exception:
            pass
    if end_time:
        try:
            et = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            if et.tzinfo is None:
                et = et.replace(tzinfo=timezone.utc)
            if et < now:
                return False
        except Exception:
            pass
    return True


@router.get("/carousel/active")
def get_active_carousel_slides(db: Session = Depends(get_db)):
    try:
        now = datetime.now(timezone.utc)
        block = (
            db.query(HomepageBlock)
            .filter(HomepageBlock.type == "carousel", HomepageBlock.is_enabled == True)
            .order_by(HomepageBlock.sort_order)
            .first()
        )
        if not block or not block.config:
            return success_response(
                data=[],
                message="Active carousel slides retrieved successfully",
            )
        slides = block.config.get("slides") or []
        out = []
        for s in slides:
            if not s.get("is_enabled", True):
                continue
            if not _filter_slide_by_time(s, now):
                continue
            out.append({
                "id": s.get("id"),
                "title": s.get("title"),
                "image_url": s.get("image_url") or "",
                "video_url": s.get("video_url"),
                "link_url": s.get("link_url"),
                "link_text": s.get("link_text") or "",
                "button_style": s.get("button_style") or "primary",
                "overlay_opacity": s.get("overlay_opacity", 50),
                "text_position": s.get("text_position") or "center",
                "text_align": s.get("text_align") or "center",
                "is_enabled": s.get("is_enabled", True),
                "sort_order": s.get("sort_order") if s.get("sort_order") is not None else 0,
                "start_time": s.get("start_time"),
                "end_time": s.get("end_time"),
            })
        out.sort(key=lambda x: (x.get("sort_order") if x.get("sort_order") is not None else 0, 0))
        return success_response(
            data=out,
            message="Active carousel slides retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error getting active carousel slides: {e}")
        return error_response(message="Failed to fetch active carousel slides")
