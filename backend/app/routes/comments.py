from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from ..models.base import get_db
from ..models.user import User
from ..models.work import Work
from ..models.comment import Comment
from ..models.schemas import CreateCommentRequest, CommentResponse
from ..utils.auth import get_current_active_user, get_current_user_optional
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger

router = APIRouter()


@router.get("/works/{work_id}/comments")
def get_comments(
    work_id: int,
    page: int = 1,
    page_size: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get comments for a work.
    """
    try:
        # Check if work exists
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Get top-level comments (parent_id is NULL) and their replies
        from sqlalchemy import or_
        
        # Get total count of top-level comments
        total = db.query(Comment).filter(
            Comment.work_id == work_id,
            Comment.parent_id == None
        ).count()
        
        # Get top-level comments with their replies
        top_level_comments = db.query(Comment).filter(
            Comment.work_id == work_id,
            Comment.parent_id == None
        ).order_by(
            desc(Comment.created_at)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Build nested structure
        items = []
        for comment in top_level_comments:
            # Get replies for this comment
            replies = db.query(Comment).filter(
                Comment.parent_id == comment.id
            ).order_by(Comment.created_at).all()
            
            comment_dict = comment.to_dict(include_user=True, include_replies=False)
            comment_dict["replies"] = [reply.to_dict(include_user=True, include_replies=False) for reply in replies]
            comment_dict["reply_count"] = len(replies)
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
        return error_response(
            message="An error occurred while retrieving comments",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/comments")
def create_comment(
    work_id: int,
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a comment on a work.
    """
    try:
        # Check if work exists
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # If parent_id is provided, validate it belongs to the same work
        if request.parent_id:
            parent_comment = db.query(Comment).filter(
                Comment.id == request.parent_id,
                Comment.work_id == work_id
            ).first()
            if not parent_comment:
                return error_response(
                    message="Parent comment not found or does not belong to this work",
                    status_code=status.HTTP_404_NOT_FOUND
                )

        # Create comment
        new_comment = Comment(
            work_id=work_id,
            user_id=current_user.id,
            content=request.content,
            parent_id=request.parent_id
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)

        # 🔔 Send notification to work owner or parent comment owner
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        # 1. Notify parent comment owner if it's a reply
        if request.parent_id:
            parent_comment = db.query(Comment).filter(Comment.id == request.parent_id).first()
            if parent_comment and parent_comment.user_id != current_user.id:
                create_notification(
                    db=db,
                    user_id=parent_comment.user_id,
                    type=NotificationType.NEW_COMMENT,
                    title="New Reply! 💬",
                    content=f"{current_user.nickname or current_user.handle} replied to your comment: '{new_comment.content[:50]}...'",
                    link_url=f"/prompt/{work.url_slug or work.short_code}"
                )
        # 2. Notify work owner if it's a top-level comment (and not their own work)
        elif work.user_id != current_user.id:
            create_notification(
                db=db,
                user_id=work.user_id,
                type=NotificationType.NEW_COMMENT,
                title="New Comment! 💬",
                content=f"{current_user.nickname or current_user.handle} commented on your work '{work.share_name or work.title}': '{new_comment.content[:50]}...'",
                link_url=f"/prompt/{work.url_slug or work.short_code}"
            )

        logger.info(f"Comment created: {new_comment.id} by user {current_user.id} on work {work_id}")

        return success_response(
            data=new_comment.to_dict(include_user=True),
            message="Comment created successfully",
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating comment: {str(e)}")
        return error_response(
            message="An error occurred while creating comment",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment (only by owner or work owner).
    """
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            return error_response(
                message="Comment not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Check if user is comment owner or work owner
        work = db.query(Work).filter(Work.id == comment.work_id).first()
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if comment.user_id != current_user.id and work.user_id != current_user.id:
            return error_response(
                message="Not authorized to delete this comment",
                status_code=status.HTTP_403_FORBIDDEN
            )

        db.delete(comment)
        db.commit()

        logger.info(f"Comment {comment_id} deleted by user {current_user.id}")

        return success_response(
            message="Comment deleted successfully"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting comment: {str(e)}")
        return error_response(
            message="An error occurred while deleting comment",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

