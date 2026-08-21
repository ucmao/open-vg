from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class PaymentStatus(str, Enum):
    """Enum for payment order status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentOrder(Base):
    """Payment order model for credit purchases."""
    
    __tablename__ = "payment_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Payment details
    amount_usd = Column(Numeric(10, 2), nullable=False)  # Amount in USD
    credits = Column(Integer, nullable=False)  # Number of credits purchased
    extra_credits_percent = Column(Numeric(5, 2), nullable=True)  # Promo: e.g. 10 = 10% extra credits
    
    # PayPal integration
    paypal_order_id = Column(String(255), unique=True, index=True, nullable=True)
    paypal_payment_id = Column(String(255), nullable=True)
    
    # Stripe integration
    stripe_session_id = Column(String(255), unique=True, index=True, nullable=True)
    stripe_payment_intent_id = Column(String(255), unique=True, index=True, nullable=True)
    

    
    # Provider
    payment_provider = Column(String(50), default="paypal", nullable=False)
    
    # Status
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    
    # Additional information
    error_message = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payment_orders")
    credit_records = relationship("CreditRecord", back_populates="order")

    def __repr__(self):
        return f"<PaymentOrder(id={self.id}, user_id={self.user_id}, amount_usd={self.amount_usd}, status={self.status})>"
    
    def to_dict(self):
        """Convert payment order to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount_usd": float(self.amount_usd),
            "credits": self.credits,
            "paypal_order_id": self.paypal_order_id,
            "stripe_session_id": self.stripe_session_id,
            "stripe_payment_intent_id": self.stripe_payment_intent_id,

            "payment_provider": self.payment_provider,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
