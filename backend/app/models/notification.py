from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class NotificationType(str, Enum):
    """Enum for notification types."""
    SYSTEM = "system"           # General system announcements
    TASK_COMPLETE = "task_success" # AI task completed successfully
    TASK_FAILED = "task_failed"    # AI task failed
    NEW_LIKE = "like"           # Someone liked your work
    NEW_COMMENT = "comment"     # Someone commented on your work
    NEW_FOLLOW = "follow"       # Someone followed you
    FEATURED = "featured"       # Your work was featured by admin
    CREDIT_UPDATE = "credit"    # Credits added or expired
    ACCOUNT_STATUS_CHANGED = "account_status_changed"  # Account activated or deactivated by admin
    NSFW_APPROVED = "NSFW_APPROVED"  # NSFW content approved by admin
    NSFW_BLOCKED = "NSFW_BLOCKED"    # NSFW content blocked by admin


class Notification(Base):
    """Notification model for storing user alerts."""
    
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification content
    type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Action link (optional)
    link_url = Column(String(500), nullable=True)
    
    # Metadata
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", backref="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"
    
    def to_dict(self):
        """Convert notification to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value,
            "title": self.title,
            "content": self.content,
            "link_url": self.link_url,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
