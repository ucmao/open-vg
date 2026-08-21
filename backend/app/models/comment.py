from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Comment(Base):
    """Comment model for works."""
    
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)  # For nested comments
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    work = relationship("Work", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<Comment(id={self.id}, work_id={self.work_id}, user_id={self.user_id})>"
    
    def to_dict(self, include_user=True, include_replies=False):
        """Convert comment to dictionary for API responses."""
        result = {
            "id": self.id,
            "work_id": self.work_id,
            "user_id": self.user_id,
            "parent_id": self.parent_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user and self.user:
            result["user"] = {
                "id": self.user.id,
                "handle": self.user.handle,
                "nickname": self.user.nickname,
                "avatar_url": self.user.avatar_url,
            }
        
        if include_replies and hasattr(self, 'replies'):
            result["replies"] = [reply.to_dict(include_user=include_user, include_replies=False) for reply in self.replies]
            result["reply_count"] = len(self.replies)
        else:
            result["reply_count"] = 0
        
        return result

