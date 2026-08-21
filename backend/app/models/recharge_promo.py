"""Recharge promo: per-user extra credits % with validity and unique promo code for /recharge?promo=xxx."""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class RechargePromo(Base):
    """Per-user recharge promo: extra credits %, valid period, and unique code for marketing URL."""

    __tablename__ = "recharge_promos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # NULL =
    extra_credits_percent = Column(Numeric(5, 2), nullable=False)  # e.g. 10 = 10% extra
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    promo_code = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)

    user = relationship("User", backref="recharge_promos")

    def to_dict(self, *, user=None, frontend_url=None):
        out = {
            "id": self.id,
            "user_id": self.user_id,
            "extra_credits_percent": float(self.extra_credits_percent),
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "promo_code": self.promo_code,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if user is not None:
            out["user"] = {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "handle": user.handle,
            }
        else:
            out["user"] = None
        if frontend_url:
            base = frontend_url.rstrip("/")
            out["recharge_url"] = f"{base}/recharge?promo={self.promo_code}"
        return out
