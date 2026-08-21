"""
Admin routes for managing comments.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import Optional

from ..models.base import get_db
from ..models.admin import Admin
from ..models.comment import Comment
from ..models.user import User
from ..models.work import Work
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger

router = APIRouter()

@router.get("/comments")
def get_all_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by comment content"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    work_id: Optional[int] = Query(None, description="Filter by work ID"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all comments with search and pagination.
    """
    try:
        query = db.query(Comment)
        
        filters = []
        if search:
            filters.append(Comment.content.ilike(f"%{search}%"))
            
        if user_id:
            filters.append(Comment.user_id == user_id)
            
        if work_id:
            filters.append(Comment.work_id == work_id)
            
        if filters:
            query = query.filter(and_(*filters))
            
        total = query.count()
        
        comments = query.order_by(Comment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # Format comment data with user and work info
        items = []
        for comment in comments:
            comment_dict = comment.to_dict(include_user=True)
            # Add work info for admin context
            work = db.query(Work).filter(Work.id == comment.work_id).first()
            if work:
                comment_dict["work"] = {
                    "id": work.id,
                    "title": work.title or work.share_name or "Untitled Work",
                    "short_code": work.short_code,
                    "url_slug": work.url_slug
                }
            items.append(comment_dict)
            
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Comments retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}")
        return error_response(message="Failed to retrieve comments", status_code=500)

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a comment by admin.
    """
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            return error_response(message="Comment not found", status_code=404)
            
        # Deleting a parent comment will trigger CASCADE delete for replies in DB
        db.delete(comment)
        db.commit()
        
        logger.info(f"Admin {current_admin.username} deleted comment {comment_id}")
        
        return success_response(message="Comment deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting comment: {str(e)}")
        return error_response(message="Failed to delete comment")
