from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..models.base import get_db
from ..models.user import User
from ..models.recharge_package import RechargePackage
from ..models.recharge_promo import RechargePromo
from ..utils.auth import get_current_user_optional
from ..utils.responses import success_response

router = APIRouter()


def _validate_promo_for_user(db: Session, promo_code: str, user_id: Optional[int]) -> Optional[RechargePromo]:
    """Return promo if code exists, is valid for user (or global when user_id is None), and is currently valid."""
    promo = db.query(RechargePromo).filter(RechargePromo.promo_code == promo_code).first()
    if not promo:
        return None
    # Global promo (user_id is None) applies to everyone; otherwise must match user
    if promo.user_id is not None and (user_id is None or promo.user_id != user_id):
        return None
    now = datetime.now(timezone.utc)
    if promo.valid_from and promo.valid_from > now:
        return None
    if promo.valid_until < now:
        return None
    return promo


@router.get("/packages")
def get_active_recharge_packages(
    promo: Optional[str] = Query(None, description="Promo code for extra credits (e.g. from /recharge?promo=xxx)"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Get all active recharge packages. If promo query and user is logged in,
    validate promo and return promo_info (extra_credits_percent, valid_until) when valid.
    """
    packages = db.query(RechargePackage).filter(
        RechargePackage.is_active == True
    ).order_by(
        RechargePackage.order.asc(),
        RechargePackage.amount.asc()
    ).all()
    data = {"packages": [p.to_dict() for p in packages], "promo_info": None}
    if promo:
        user_id = current_user.id if current_user else None
        valid_promo = _validate_promo_for_user(db, promo.strip(), user_id)
        if valid_promo:
            data["promo_info"] = {
                "extra_credits_percent": float(valid_promo.extra_credits_percent),
                "valid_until": valid_promo.valid_until.isoformat() if valid_promo.valid_until else None,
            }
    return success_response(
        data=data,
        message="Active recharge packages retrieved successfully",
    )
