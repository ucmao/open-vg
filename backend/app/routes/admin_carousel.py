"""Admin：（ homepage_blocks type=carousel，config.slides ， API ）"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from ..models.base import get_db
from ..models.admin import Admin
from ..models.homepage_block import HomepageBlock
from ..models.schemas import CreateCarouselSlideRequest, UpdateCarouselSlideRequest
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger

router = APIRouter()


def _get_carousel_block(db: Session):
    return db.query(HomepageBlock).filter(HomepageBlock.type == "carousel").order_by(HomepageBlock.sort_order).first()


def _slide_to_dict(s: dict) -> dict:
    """ slide ，（）。"""
    return {
        "id": s.get("id"),
        "title": s.get("title"),
        "image_url": s.get("image_url"),
        "video_url": s.get("video_url"),
        "link_url": s.get("link_url"),
        "link_text": s.get("link_text"),
        "button_style": s.get("button_style"),
        "overlay_opacity": s.get("overlay_opacity"),
        "text_position": s.get("text_position"),
        "text_align": s.get("text_align"),
        "is_enabled": s.get("is_enabled"),
        "sort_order": s.get("sort_order"),
        "start_time": s.get("start_time"),
        "end_time": s.get("end_time"),
    }


@router.get("/carousel/config")
def get_carousel_config(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = _get_carousel_block(db)
        if not block or not block.config:
            return success_response(
                data={"interval": 5000, "autoplay": True, "show_arrows": True, "show_indicators": True},
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


@router.put("/carousel/config")
def update_carousel_config(
    request: dict,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = _get_carousel_block(db)
        if not block:
            block = HomepageBlock(
                type="carousel",
                config={"slides": [], "interval": 5000, "autoplay": True, "show_arrows": True, "show_indicators": True},
                sort_order=0,
                is_enabled=True,
            )
            db.add(block)
            db.commit()
            db.refresh(block)
        config = dict(block.config or {})
        if "interval" in request:
            config["interval"] = int(request["interval"])
        if "autoplay" in request:
            config["autoplay"] = bool(request["autoplay"])
        if "show_arrows" in request:
            config["show_arrows"] = bool(request["show_arrows"])
        if "show_indicators" in request:
            config["show_indicators"] = bool(request["show_indicators"])
        block.config = config
        db.commit()
        db.refresh(block)
        logger.info(f"Carousel config updated by admin {current_admin.id}")
        return success_response(
            data={
                "interval": config.get("interval", 5000),
                "autoplay": config.get("autoplay", True),
                "show_arrows": config.get("show_arrows", True),
                "show_indicators": config.get("show_indicators", True),
            },
            message="Carousel config updated successfully",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating carousel config: {e}")
        return error_response(message="Failed to update carousel config")


@router.get("/carousel")
def get_carousel_slides(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_enabled: Optional[bool] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = _get_carousel_block(db)
        slides: List[dict] = (block.config or {}).get("slides") or []
        if is_enabled is not None:
            slides = [s for s in slides if s.get("is_enabled", True) == is_enabled]
        slides = sorted(slides, key=lambda x: (x.get("sort_order", 0), 0))
        total = len(slides)
        start = (page - 1) * page_size
        items = [_slide_to_dict(s) for s in slides[start : start + page_size]]
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Carousel slides retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error getting carousel slides: {e}")
        return error_response(message="Failed to fetch carousel slides")


def _find_slide_by_id(block, slide_id):
    slides = (block.config or {}).get("slides") or []
    sid = str(slide_id)
    for i, s in enumerate(slides):
        if str(s.get("id")) == sid:
            return i, s
    return -1, None


@router.get("/carousel/{slide_id}")
def get_carousel_slide(
    slide_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = _get_carousel_block(db)
        if not block:
            return error_response(message="Carousel slide not found", status_code=status.HTTP_404_NOT_FOUND)
        _, slide = _find_slide_by_id(block, slide_id)
        if not slide:
            return error_response(message="Carousel slide not found", status_code=status.HTTP_404_NOT_FOUND)
        return success_response(data=_slide_to_dict(slide), message="Carousel slide retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting carousel slide: {e}")
        return error_response(message="Failed to fetch carousel slide")


@router.post("/carousel")
def create_carousel_slide(
    request: CreateCarouselSlideRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = _get_carousel_block(db)
        if not block:
            block = HomepageBlock(
                type="carousel",
                config={"slides": [], "interval": 5000, "autoplay": True, "show_arrows": True, "show_indicators": True},
                sort_order=0,
                is_enabled=True,
            )
            db.add(block)
            db.commit()
            db.refresh(block)
        config = dict(block.config or {})
        slides = list(config.get("slides") or [])
        new_id = str(uuid.uuid4())
        start_time = request.start_time.isoformat() if request.start_time else None
        end_time = request.end_time.isoformat() if request.end_time else None
        new_slide = {
            "id": new_id,
            "title": request.title,
            "image_url": request.image_url,
            "video_url": request.video_url,
            "link_url": request.link_url,
            "link_text": request.link_text or "",
            "button_style": request.button_style or "primary",
            "overlay_opacity": request.overlay_opacity or 50,
            "text_position": request.text_position or "center",
            "text_align": request.text_align or "center",
            "is_enabled": request.is_enabled,
            "sort_order": request.sort_order,
            "start_time": start_time,
            "end_time": end_time,
        }
        slides.append(new_slide)
        config["slides"] = slides
        block.config = config
        db.commit()
        db.refresh(block)
        logger.info(f"Carousel slide created: {new_id} by admin {current_admin.id}")
        return success_response(
            data=_slide_to_dict(new_slide),
            message="Carousel slide created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating carousel slide: {e}")
        return error_response(message="Failed to create carousel slide")


@router.put("/carousel/{slide_id}")
def update_carousel_slide(
    slide_id: str,
    request: UpdateCarouselSlideRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = _get_carousel_block(db)
        if not block:
            return error_response(message="Carousel slide not found", status_code=status.HTTP_404_NOT_FOUND)
        idx, _ = _find_slide_by_id(block, slide_id)
        if idx < 0:
            return error_response(message="Carousel slide not found", status_code=status.HTTP_404_NOT_FOUND)
        config = dict(block.config or {})
        slides = list(config.get("slides") or [])
        slide = dict(slides[idx])
        d = request.model_dump(exclude_unset=True)
        for k, v in d.items():
            if k in ("start_time", "end_time") and v is not None and hasattr(v, "isoformat"):
                v = v.isoformat()
            slide[k] = v
        for deprecated in ("subtitle", "description", "text_color"):
            slide.pop(deprecated, None)
        slides[idx] = slide
        config["slides"] = slides
        block.config = config
        db.commit()
        db.refresh(block)
        logger.info(f"Carousel slide updated: {slide_id} by admin {current_admin.id}")
        return success_response(data=_slide_to_dict(slide), message="Carousel slide updated successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating carousel slide: {e}")
        return error_response(message="Failed to update carousel slide")


@router.delete("/carousel/{slide_id}")
def delete_carousel_slide(
    slide_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        block = _get_carousel_block(db)
        if not block:
            return error_response(message="Carousel slide not found", status_code=status.HTTP_404_NOT_FOUND)
        idx, _ = _find_slide_by_id(block, slide_id)
        if idx < 0:
            return error_response(message="Carousel slide not found", status_code=status.HTTP_404_NOT_FOUND)
        config = dict(block.config or {})
        slides = list(config.get("slides") or [])
        slides.pop(idx)
        config["slides"] = slides
        block.config = config
        db.commit()
        logger.info(f"Carousel slide deleted: {slide_id} by admin {current_admin.id}")
        return success_response(message="Carousel slide deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting carousel slide: {e}")
        return error_response(message="Failed to delete carousel slide")
