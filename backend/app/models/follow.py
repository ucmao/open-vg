from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Follow(Base):
    """Model to track user follows."""
    
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], backref="following_rels")
    following = relationship("User", foreign_keys=[following_id], backref="follower_rels")

    # Ensure a user cannot follow the same person twice
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='_follower_following_uc'),
    )

    def __repr__(self):
        return f"<Follow(follower_id={self.follower_id}, following_id={self.following_id})>"

