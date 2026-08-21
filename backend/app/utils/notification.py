from sqlalchemy.orm import Session
from ..models.notification import Notification, NotificationType
from ..utils.logger import logger

def create_notification(
    db: Session,
    user_id: int,
    type: NotificationType,
    title: str,
    content: str,
    link_url: str = None
):
    """
    Create a notification for a user.
    """
    try:
        # Pass the enum object - SQLAlchemy will use its value
        # Now that enum values are uppercase (NSFW_BLOCKED = "NSFW_BLOCKED"),
        # they match the database enum values
        notification = Notification(
            user_id=user_id,
            type=type,  # Pass enum object, SQLAlchemy uses type.value automatically
            title=title,
            content=content,
            link_url=link_url
        )
        db.add(notification)
        db.commit()
        
        # Here we could trigger a WebSocket broadcast in the future
        logger.info(f"Notification created successfully: user_id={user_id}, type={type.value}")
        return notification
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create notification: {str(e)}")
        logger.error(f"Notification details: user_id={user_id}, type={type}, type_value={type.value if hasattr(type, 'value') else type}")
        return None
