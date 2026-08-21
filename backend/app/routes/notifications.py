from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional

from ..models.base import get_db
from ..models.user import User
from ..models.notification import Notification
from ..utils.auth import get_current_active_user
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger

router = APIRouter()


@router.get("")
def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    is_read: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's notifications.
    """
    try:
        query = db.query(Notification).filter(Notification.user_id == current_user.id)
        
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
            
        total = query.count()
        notifications = query.order_by(desc(Notification.created_at))\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()
            
        items = [n.to_dict() for n in notifications]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Notifications retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return error_response(message="Failed to retrieve notifications")


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the count of unread notifications.
    """
    try:
        count = db.query(func.count(Notification.id))\
            .filter(Notification.user_id == current_user.id, Notification.is_read == False)\
            .scalar() or 0
            
        return success_response(data={"count": count})
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        return error_response(message="Failed to get unread count")


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a specific notification as read.
    """
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            return error_response(message="Notification not found", status_code=404)
            
        notification.is_read = True
        db.commit()
        
        return success_response(message="Notification marked as read")
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking notification as read: {str(e)}")
        return error_response(message="Failed to update notification")


@router.post("/read-all")
def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark all user's notifications as read.
    """
    try:
        db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).update({Notification.is_read: True}, synchronize_session=False)
        
        db.commit()
        return success_response(message="All notifications marked as read")
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking all notifications as read: {str(e)}")
        return error_response(message="Failed to update notifications")


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification.
    """
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            return error_response(message="Notification not found", status_code=404)
            
        db.delete(notification)
        db.commit()
        
        return success_response(message="Notification deleted")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting notification: {str(e)}")
        return error_response(message="Failed to delete notification")
