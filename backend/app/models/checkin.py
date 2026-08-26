"""CheckIn model for daily check-in rewards."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class CheckIn(Base):
    """ - Daily check-in record model."""
    
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Check-in date (used to prevent duplicate check-ins)
    check_date = Column(Date, nullable=False, index=True)
    
    # Consecutive check-in days
    consecutive_days = Column(Integer, default=1, nullable=False)
    
    #  - Credits earned from this check-in
    reward_credits = Column(Integer, nullable=False)
    
    #  - Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    #  - Relationships
    user = relationship("User", backref="checkins")
    
    # Unique constraint: one check-in per user per day
    __table_args__ = (
        UniqueConstraint('user_id', 'check_date', name='uq_user_check_date'),
    )

    def __repr__(self):
        return f"<CheckIn(id={self.id}, user_id={self.user_id}, check_date={self.check_date}, consecutive_days={self.consecutive_days})>"
    
    def to_dict(self):
        """Convert check-in record to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "check_date": self.check_date.isoformat(),
            "consecutive_days": self.consecutive_days,
            "reward_credits": self.reward_credits,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
