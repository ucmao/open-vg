from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Favorite(Base):
    """Favorite model for users to save works they like."""
    
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint('user_id', 'work_id', name='unique_user_work_favorite'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    work = relationship("Work", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, work_id={self.work_id})>"
    
    def to_dict(self):
        """Convert favorite to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "work_id": self.work_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

