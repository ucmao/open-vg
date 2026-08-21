"""
User activity log model for DAU (daily active users) tracking.
Records first activity per user per day (login or heartbeat).
"""
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base


class UserActivityLog(Base):
    """
    。。
     DAU， last_login 。
    """
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_date = Column(Date, nullable=False, index=True)  # Beijing date
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "activity_date", name="uq_user_activity_date"),
    )
