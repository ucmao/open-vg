from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Like(Base):
    """Like model for user-work interactions."""
    
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User")
    work = relationship("Work")

    # Each user can like a work only once
    __table_args__ = (
        UniqueConstraint('user_id', 'work_id', name='uix_user_work_like'),
    )

    def __repr__(self):
        return f"<Like(user_id={self.user_id}, work_id={self.work_id})>"

