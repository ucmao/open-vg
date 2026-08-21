"""Admin CRUD for model pages (landing pages for generation models, /magic/:slug)."""
from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional, List

from pydantic import BaseModel, Field

from ..models.base import get_db
from ..models.model_page import ModelPage, ModelPageStatus
from ..models.admin import Admin
from ..models.schemas import CreateModelPageRequest, UpdateModelPageRequest
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger

router = APIRouter()


class BatchUpdateModelPageRequest(BaseModel):
    """Batch update model pages request"""
    page_ids: List[int] = Field(..., description="Model page ID list")
    status: Optional[str] = Field(None, description="Status")


@router.get("/model-pages")
def get_model_pages(
    page: int = 1,
    page_size: int = 20,
    generation_model_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """List model pages. Admin only."""
    try:
        query = db.query(ModelPage).options(
            joinedload(ModelPage.generation_model)
        )
        if generation_model_id is not None:
            query = query.filter(ModelPage.generation_model_id == generation_model_id)
        if status_filter:
            query = query.filter(ModelPage.status == ModelPageStatus(status_filter))

        total = query.count()
        items = (
            query.order_by(ModelPage.sort_order, desc(ModelPage.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return paginated_response(
            items=[p.to_dict() for p in items],
            total=total,
            page=page,
            page_size=page_size,
            message="Model pages retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error listing model pages: {e}")
        return error_response(
            message="Failed to fetch model pages",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/model-pages/batch-update")
def batch_update_model_pages(
    request: BatchUpdateModelPageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Batch update model pages. Admin only."""
    if not request.page_ids:
        return error_response(message="Model page ID list", status_code=status.HTTP_400_BAD_REQUEST)
    if not request.status:
        return error_response(message="Update data not provided", status_code=status.HTTP_400_BAD_REQUEST)
    try:
        affected = (
            db.query(ModelPage)
            .filter(ModelPage.id.in_(request.page_ids))
            .update(
                {ModelPage.status: ModelPageStatus(request.status)},
                synchronize_session=False,
            )
        )
        db.commit()
        return success_response(message=f"successful {affected} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch updating model pages: {e}")
        return error_response(message="failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/model-pages/batch-delete")
def batch_delete_model_pages(
    page_ids: List[int] = Body(..., embed=True),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """。Admin only."""
    if not page_ids:
        return error_response(message="Model page ID list", status_code=status.HTTP_400_BAD_REQUEST)
    try:
        affected = (
            db.query(ModelPage).filter(ModelPage.id.in_(page_ids)).delete(synchronize_session=False)
        )
        db.commit()
        return success_response(message=f"successful {affected} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch deleting model pages: {e}")
        return error_response(message="failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/model-pages/{page_id}")
def get_model_page(
    page_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get one model page by ID. Admin only."""
    page = db.query(ModelPage).options(joinedload(ModelPage.generation_model)).filter(ModelPage.id == page_id).first()
    if not page:
        return error_response(message="does not exist", status_code=status.HTTP_404_NOT_FOUND)
    return success_response(data=page.to_dict(), message="Model page retrieved successfully")


@router.post("/model-pages")
def create_model_page(
    request: CreateModelPageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a model page. Admin only."""
    try:
        existing = db.query(ModelPage).filter(ModelPage.slug == request.slug).first()
        if existing:
            return error_response(message=" slug already exists", status_code=status.HTTP_400_BAD_REQUEST)
        if request.generation_model_id is not None:
            existing_model = db.query(ModelPage).filter(
                ModelPage.generation_model_id == request.generation_model_id
            ).first()
            if existing_model:
                return error_response(
                    message="Model already has exclusive page",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        page = ModelPage(
            slug=request.slug,
            generation_model_id=request.generation_model_id,
            title=request.title,
            excerpt=request.excerpt,
            content=request.content or "",
            meta_title=request.meta_title,
            meta_description=request.meta_description,
            meta_keywords=request.meta_keywords,
            og_image=request.og_image,
            featured_image=request.featured_image,
            icon=request.icon,
            config=request.config or {},
            status=ModelPageStatus(request.status),
            sort_order=request.sort_order,
            published_at=request.published_at,
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        return success_response(data=page.to_dict(), message="successful")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating model page: {e}")
        return error_response(message="failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put("/model-pages/{page_id}")
def update_model_page(
    page_id: int,
    request: UpdateModelPageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update a model page. Admin only."""
    page = db.query(ModelPage).filter(ModelPage.id == page_id).first()
    if not page:
        return error_response(message="does not exist", status_code=status.HTTP_404_NOT_FOUND)
    try:
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "status" and value:
                setattr(page, key, ModelPageStatus(value))
            elif key == "config" and value is not None:
                setattr(page, key, value)
            else:
                setattr(page, key, value)
        if request.generation_model_id is not None:
            other = (
                db.query(ModelPage)
                .filter(
                    ModelPage.generation_model_id == request.generation_model_id,
                    ModelPage.id != page_id,
                )
                .first()
            )
            if other:
                return error_response(
                    message="Model already has exclusive page",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        db.commit()
        db.refresh(page)
        return success_response(data=page.to_dict(), message="successful")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating model page: {e}")
        return error_response(message="failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/model-pages/{page_id}")
def delete_model_page(
    page_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete a model page. Admin only."""
    page = db.query(ModelPage).filter(ModelPage.id == page_id).first()
    if not page:
        return error_response(message="does not exist", status_code=status.HTTP_404_NOT_FOUND)
    try:
        db.delete(page)
        db.commit()
        return success_response(message="successful")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting model page: {e}")
        return error_response(message="failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
