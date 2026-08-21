"""
：Banner
type='banner' -> config  banner  JSON
type='carousel' -> config  { slides: [...], interval, autoplay, show_arrows, show_indicators }
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base


class HomepageBlock(Base):
    __tablename__ = "homepage_blocks"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True, comment="banner | carousel")
    config = Column(JSON, nullable=False, comment="Full configuration JSON")
    sort_order = Column(Integer, nullable=False, default=0)
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "config": self.config,
            "sort_order": self.sort_order,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
