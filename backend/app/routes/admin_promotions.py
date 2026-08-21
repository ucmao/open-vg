"""Admin： Banner（ homepage_blocks type=banner， API ）"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import uuid

from ..models.base import get_db
from ..models.admin import Admin
from ..models.homepage_block import HomepageBlock
from ..models.schemas import CreatePromotionBannerRequest, UpdatePromotionBannerRequest
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger

router = APIRouter()


def _block_to_banner_dict(block):
    c = block.config or {}
    layout = c.get("layout_config") or {}
    countdown = layout.get("countdown") or {}
    return {
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
        "created_at": block.created_at.isoformat() if block.created_at else None,
        "updated_at": block.updated_at.isoformat() if block.updated_at else None,
    }


def _request_to_config(request, existing_config=None):
    """ Create/Update  config （ start_time/end_time ）"""
    base = existing_config.copy() if existing_config else {}
    d = request.model_dump(exclude_unset=True)
    #  config
    for k in ("is_enabled", "sort_order"):
        d.pop(k, None)
    if "start_time" in d and d["start_time"] is not None:
        if hasattr(d["start_time"], "isoformat"):
            d["start_time"] = d["start_time"].isoformat()
    if "end_time" in d and d["end_time"] is not None:
        if hasattr(d["end_time"], "isoformat"):
            d["end_time"] = d["end_time"].isoformat()
    base.update(d)
    if "layout_config" not in base and "show_countdown" in d:
        base.setdefault("layout_config", {})["countdown"] = {"visible": d.get("show_countdown", False)}
    return base


@router.get("/promotions")
def get_promotion_banners(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_enabled: Optional[bool] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(HomepageBlock).filter(HomepageBlock.type == "banner")
        if is_enabled is not None:
            query = query.filter(HomepageBlock.is_enabled == is_enabled)
        total = query.count()
        blocks = (
            query.order_by(HomepageBlock.sort_order, desc(HomepageBlock.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        items = [_block_to_banner_dict(b) for b in blocks]
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Promotion banners retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error getting promotion banners: {e}")
        return error_response(message="Failed to fetch promotion banners")


@router.get("/promotions/{banner_id}")
def get_promotion_banner(
    banner_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = db.query(HomepageBlock).filter(
            HomepageBlock.id == banner_id,
            HomepageBlock.type == "banner",
        ).first()
        if not block:
            return error_response(
                message="Promotion banner not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(
            data=_block_to_banner_dict(block),
            message="Promotion banner retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error getting promotion banner: {e}")
        return error_response(message="Failed to fetch promotion banner")


@router.post("/promotions")
def create_promotion_banner(
    request: CreatePromotionBannerRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        config = _request_to_config(request)
        if "layout_config" not in config:
            config["layout_config"] = {"countdown": {"visible": getattr(request, "show_countdown", False)}}
        block = HomepageBlock(
            type="banner",
            config=config,
            sort_order=getattr(request, "sort_order", 0) or 0,
            is_enabled=getattr(request, "is_enabled", True),
        )
        db.add(block)
        db.commit()
        db.refresh(block)
        logger.info(f"Promotion banner created: {block.id} by admin {current_admin.id}")
        return success_response(
            data=_block_to_banner_dict(block),
            message="Promotion banner created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating promotion banner: {e}")
        return error_response(message="Failed to create promotion banner")


@router.put("/promotions/{banner_id}")
def update_promotion_banner(
    banner_id: int,
    request: UpdatePromotionBannerRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = db.query(HomepageBlock).filter(
            HomepageBlock.id == banner_id,
            HomepageBlock.type == "banner",
        ).first()
        if not block:
            return error_response(
                message="Promotion banner not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        update_data = request.model_dump(exclude_unset=True)
        if "sort_order" in update_data:
            block.sort_order = update_data["sort_order"]
        if "is_enabled" in update_data:
            block.is_enabled = update_data["is_enabled"]
        config = dict(block.config or {})
        for k in ("title", "content", "image_url", "link_url", "link_text",
                  "background_color", "background_gradient", "background_image_url", "text_color",
                  "start_time", "end_time", "layout_config", "content_items"):
            if k in update_data:
                v = update_data[k]
                if k in ("start_time", "end_time") and v is not None and hasattr(v, "isoformat"):
                    v = v.isoformat()
                config[k] = v
        if "show_countdown" in update_data:
            config.setdefault("layout_config", {})["countdown"] = config.get("layout_config", {}).get("countdown") or {}
            config["layout_config"]["countdown"]["visible"] = update_data["show_countdown"]
        block.config = config
        db.commit()
        db.refresh(block)
        logger.info(f"Promotion banner updated: {banner_id} by admin {current_admin.id}")
        return success_response(
            data=_block_to_banner_dict(block),
            message="Promotion banner updated successfully",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating promotion banner: {e}")
        return error_response(message="Failed to update promotion banner")


@router.delete("/promotions/{banner_id}")
def delete_promotion_banner(
    banner_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = db.query(HomepageBlock).filter(
            HomepageBlock.id == banner_id,
            HomepageBlock.type == "banner",
        ).first()
        if not block:
            return error_response(
                message="Promotion banner not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        db.delete(block)
        db.commit()
        logger.info(f"Promotion banner deleted: {banner_id} by admin {current_admin.id}")
        return success_response(message="Promotion banner deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting promotion banner: {e}")
        return error_response(message="Failed to delete promotion banner")
