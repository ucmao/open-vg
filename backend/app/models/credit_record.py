from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class CreditType(str, Enum):
    """Enum for credit transaction types."""
    RECHARGE = "recharge"      # Purchase credits
    GIFT = "gift"              # Gift credits (e.g., new user bonus)
    CONSUME = "consume"        # Use credits for generation
    REFUND = "refund"          # Refund for failed generation


class CreditRecord(Base):
    """Credit transaction record model."""
    
    __tablename__ = "credit_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Integer, nullable=False)  # Positive for credit, negative for debit
    type = Column(SQLEnum(CreditType), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    
    # Expiration for gift credits
    expire_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Related records
    order_id = Column(Integer, ForeignKey("payment_orders.id", ondelete="SET NULL"), nullable=True)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="credit_records")
    order = relationship("PaymentOrder", back_populates="credit_records")

    def __repr__(self):
        return f"<CreditRecord(id={self.id}, user_id={self.user_id}, amount={self.amount}, type={self.type})>"
    
    def to_dict(self):
        """Convert credit record to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "type": self.type.value,
            "description": self.description,
            "expire_at": self.expire_at.isoformat() if self.expire_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

