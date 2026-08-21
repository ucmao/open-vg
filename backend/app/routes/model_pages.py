"""Public API for model pages (by slug for /magic/:slug)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from ..models.base import get_db
from ..models.model_page import ModelPage, ModelPageStatus
from ..utils.responses import success_response, error_response
from ..utils.logger import logger

router = APIRouter()


@router.get("/slugs-by-model")
def get_model_page_slugs_by_model(
    db: Session = Depends(get_db),
):
    """Return { model_key: slug } for all published model pages linked to a generation model. Public."""
    try:
        pages = (
            db.query(ModelPage)
            .options(joinedload(ModelPage.generation_model))
            .filter(
                ModelPage.status == ModelPageStatus.PUBLISHED,
                ModelPage.generation_model_id.isnot(None),
            )
            .all()
        )
        result = {}
        for page in pages:
            if page.generation_model:
                result[page.generation_model.model_key] = page.slug
        return success_response(data=result, message="OK")
    except Exception as e:
        logger.error(f"Error fetching model page slugs by model: {e}")
        return error_response(
            message="Failed to fetch",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/by-slug/{slug}")
def get_model_page_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """Get published model page by slug. Public. Used by frontend /magic/:slug."""
    try:
        page = db.query(ModelPage).filter(ModelPage.slug == slug).first()
        if not page:
            return error_response(message="Page not found", status_code=status.HTTP_404_NOT_FOUND)
        if page.status != ModelPageStatus.PUBLISHED:
            return error_response(message="Page not found", status_code=status.HTTP_404_NOT_FOUND)
        page.view_count += 1
        db.commit()
        db.refresh(page)
        return success_response(data=page.to_dict(), message="OK")
    except Exception as e:
        logger.error(f"Error fetching model page by slug: {e}")
        return error_response(
            message="Failed to fetch page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
