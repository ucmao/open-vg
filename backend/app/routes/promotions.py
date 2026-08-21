"""： Banner（ homepage_blocks type=banner ，）"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timezone

from ..models.base import get_db
from ..models.homepage_block import HomepageBlock
from ..utils.responses import success_response, error_response
from ..utils.logger import logger

router = APIRouter()


def _block_to_banner_item(block):
    """Convert type=banner block to banner list item format"""
    c = block.config or {}
    layout = c.get("layout_config") or {}
    countdown = layout.get("countdown") or {}
    item = {
        "id": block.id,
        "title": c.get("title") or "",
        "content": c.get("content"),
        "image_url": c.get("image_url"),
        "content_items": c.get("content_items"),
        "link_url": c.get("link_url"),
        "link_text": c.get("link_text"),
        "background_color": c.get("background_color") or "#FF6B6B",
        "background_gradient": c.get("background_gradient"),
        "background_image_url": c.get("background_image_url"),
        "text_color": c.get("text_color") or "#FFFFFF",
        "is_enabled": block.is_enabled,
        "sort_order": block.sort_order,
        "start_time": c.get("start_time"),
        "end_time": c.get("end_time"),
        "show_countdown": countdown.get("visible", False),
        "layout_config": layout,
    }
    return item


@router.get("/promotions/active")
def get_active_promotion_banners(db: Session = Depends(get_db)):
    """Banner（）"""
    try:
        now = datetime.now(timezone.utc)
        blocks = (
            db.query(HomepageBlock)
            .filter(
                HomepageBlock.type == "banner",
                HomepageBlock.is_enabled == True,
            )
            .order_by(HomepageBlock.sort_order, desc(HomepageBlock.created_at))
            .all()
        )
        items = []
        for block in blocks:
            c = block.config or {}
            start_time = c.get("start_time")
            end_time = c.get("end_time")
            if start_time:
                try:
                    st = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    if st.tzinfo is None:
                        st = st.replace(tzinfo=timezone.utc)
                    if st > now:
                        continue
                except Exception:
                    pass
            if end_time:
                try:
                    et = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                    if et.tzinfo is None:
                        et = et.replace(tzinfo=timezone.utc)
                    if et < now:
                        continue
                except Exception:
                    pass
            items.append(_block_to_banner_item(block))
        return success_response(
            data=items,
            message="Active promotion banners retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error getting active promotion banners: {e}")
        return error_response(message="Failed to fetch active promotion banners")
