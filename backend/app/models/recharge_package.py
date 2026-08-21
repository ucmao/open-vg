from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric
from sqlalchemy.sql import func
from .base import Base


class RechargePackage(Base):
    """Recharge package model for configuring credit purchase options."""
    
    __tablename__ = "recharge_packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)        # Package name, e.g., "Basic Plan"
    amount = Column(Numeric(10, 2), nullable=False)   # Payment amount in USD
    credits = Column(Integer, nullable=False)         # Number of credits awarded
    
    # UI related
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False)  # Highlight in UI
    tag_text = Column(String(50), nullable=True)      # e.g., "Best Value", "Hot"
    order = Column(Integer, default=0, nullable=False) # Sorting order
    description = Column(Text, nullable=True)          # Rich text description for recharge card (HTML)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<RechargePackage(id={self.id}, name={self.name}, amount={self.amount}, credits={self.credits})>"
    
    def to_dict(self):
        """Convert recharge package to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "amount": float(self.amount),
            "credits": self.credits,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "tag_text": self.tag_text,
            "order": self.order,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
