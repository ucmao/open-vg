"""Invitation model for referral system."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Invitation(Base):
    """ - Invitation record model."""
    
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    
    #  - Inviter
    inviter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    #  - Invitee (nullable until someone registers with the code)
    invitee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Unique invite code
    invite_code = Column(String(20), unique=True, index=True, nullable=False)
    
    #  - Whether rewards have been granted
    reward_granted = Column(Boolean, default=False, nullable=False)
    
    # Statuses: pending, completed, expired
    # Status: pending (awaiting registration), completed (finished), expired (expired)
    status = Column(String(20), default="pending", nullable=False, index=True)
    
    #  - Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)  # When the invite code was used
    
    #  - Relationships
    inviter = relationship("User", foreign_keys=[inviter_id], backref="sent_invitations")
    invitee = relationship("User", foreign_keys=[invitee_id], backref="received_invitation")

    def __repr__(self):
        return f"<Invitation(id={self.id}, inviter_id={self.inviter_id}, invite_code={self.invite_code}, status={self.status})>"
    
    def to_dict(self):
        """Convert invitation to dictionary for API responses."""
        return {
            "id": self.id,
            "inviter_id": self.inviter_id,
            "invitee_id": self.invitee_id,
            "invite_code": self.invite_code,
            "reward_granted": self.reward_granted,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "used_at": self.used_at.isoformat() if self.used_at else None,
        }
