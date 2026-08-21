from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Optional

from ..models.base import get_db
from ..models.media import Media, MediaType
from ..models.admin import Admin
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..services.storage import get_storage_service

router = APIRouter()


@router.get("")
def get_media_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    media_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    source: Optional[str] = Query("admin"),  # Default to admin files only
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get media library list with pagination and filters.
    Only system admins can access.
    """
    try:
        # Build query
        query = db.query(Media)
        
        # Filter by source
        if source and source != "all":
            query = query.filter(Media.source == source)
            
        # Filter by media type
        if media_type:
            try:
                media_type_enum = MediaType(media_type)
                query = query.filter(Media.media_type == media_type_enum)
            except ValueError:
                return error_response(
                    message=f"Invalid media_type. Must be one of: {', '.join([e.value for e in MediaType])}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Search by filename
        if search:
            query = query.filter(
                or_(
                    Media.filename.ilike(f"%{search}%"),
                    Media.original_filename.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated results, ordered by created date (newest first)
        media_items = query.order_by(desc(Media.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        # Format results
        items = [item.to_dict() for item in media_items]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Media list retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting media list: {str(e)}")
        return error_response(
            message="An error occurred while retrieving media list",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{media_id}")
def get_media_detail(
    media_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get a single media item by ID.
    """
    try:
        media_item = db.query(Media).filter(Media.id == media_id).first()
        
        if not media_item:
            return error_response(
                message="Media not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return success_response(
            data=media_item.to_dict(),
            message="Media retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting media detail: {str(e)}")
        return error_response(
            message="An error occurred while retrieving media",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{media_id}")
def delete_media(
    media_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a media file from storage and database.
    """
    try:
        media_item = db.query(Media).filter(Media.id == media_id).first()
        
        if not media_item:
            return error_response(
                message="Media not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Delete from storage
        try:
            storage = get_storage_service()
            storage.delete_file(media_item.storage_key)
            logger.info(f"Deleted file from storage: {media_item.storage_key}")
        except Exception as e:
            logger.warning(f"Failed to delete file from storage: {str(e)}")
            # Continue with database deletion even if storage deletion fails
        
        # Delete from database
        db.delete(media_item)
        db.commit()
        
        logger.info(f"Media deleted: {media_id} by admin {current_admin.id}")
        
        return success_response(
            message="Media deleted successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting media: {str(e)}")
        return error_response(
            message="An error occurred while deleting media",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

