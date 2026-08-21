"""Admin routes for recharge promos (): per-user extra credits % and promo URL."""
import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from sqlalchemy.exc import IntegrityError
from typing import Optional

from ..models.base import get_db
from ..models.admin import Admin
from ..models.user import User
from ..models.recharge_promo import RechargePromo
from ..models.schemas import CreateRechargePromoRequest, UpdateRechargePromoRequest
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..services.email import PROMO_EMAIL_PRESETS, build_recharge_promo_email_content, send_recharge_promo_email

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def _generate_promo_code() -> str:
    return uuid.uuid4().hex[:16]


def _promo_status(p: RechargePromo) -> str:
    now = datetime.now(timezone.utc)
    if p.valid_from and p.valid_from > now:
        return "pending"
    if p.valid_until < now:
        return "expired"
    return "active"


@router.get("/recharge-discount")
def list_recharge_promos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """List recharge promos with optional user filter and search (name, user email/nickname/handle, or )."""
    try:
        query = db.query(RechargePromo).outerjoin(User, RechargePromo.user_id == User.id)
        if user_id is not None:
            query = query.filter(RechargePromo.user_id == user_id)
        if search and search.strip():
            term = search.strip()
            term_like = f"%{term}%"
            or_conds = [
                RechargePromo.name.ilike(term_like),
                User.email.ilike(term_like),
                User.nickname.ilike(term_like),
                User.handle.ilike(term_like),
            ]
            if term in ("", "", "all", ""):
                or_conds.append(RechargePromo.user_id.is_(None))
            query = query.filter(or_(*or_conds))
        query = query.order_by(desc(RechargePromo.created_at))
        total = query.count()
        rows = query.offset((page - 1) * page_size).limit(page_size).all()
        items = []
        for p in rows:
            d = p.to_dict(user=p.user, frontend_url=FRONTEND_URL)
            d["status"] = _promo_status(p)
            items.append(d)
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Recharge promos retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error listing recharge promos: {str(e)}")
        return error_response(message="Failed to list recharge promos")


@router.get("/recharge-discount/email-presets")
def get_email_presets(current_admin: Admin = Depends(get_current_admin)):
    """Get preset options for promo email subject (admin selects when sending)."""
    items = [{"key": k, "label": v["label"]} for k, v in PROMO_EMAIL_PRESETS.items()]
    return success_response(data=items, message="Email presets retrieved successfully")


@router.post("/recharge-discount")
def create_recharge_promo(
    request: CreateRechargePromoRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a recharge promo and return the dedicated /recharge?promo= URL. user_id=None = ."""
    try:
        user = None
        if request.user_id is not None:
            user = db.query(User).filter(User.id == request.user_id).first()
            if not user:
                return error_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
        promo_code = _generate_promo_code()
        while db.query(RechargePromo).filter(RechargePromo.promo_code == promo_code).first():
            promo_code = _generate_promo_code()
        promo = RechargePromo(
            user_id=request.user_id,
            extra_credits_percent=request.extra_credits_percent,
            valid_from=request.valid_from,
            valid_until=request.valid_until,
            promo_code=promo_code,
            name=request.name,
            created_by=current_admin.id,
        )
        db.add(promo)
        db.commit()
        db.refresh(promo)
        d = promo.to_dict(user=promo.user, frontend_url=FRONTEND_URL)
        d["status"] = _promo_status(promo)
        logger.info(f"Recharge promo created: id={promo.id} user_id={request.user_id} by admin {current_admin.id}")
        return success_response(data=d, message="Recharge promo created successfully")
    except IntegrityError as e:
        db.rollback()
        err = str(e).lower()
        if "user_id" in err or "null" in err or "not-null" in err:
            logger.error(f"Recharge promo create IntegrityError (likely migration not run): {e}")
            return error_response(
                message="「」failed：。 backend : alembic upgrade head",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        logger.error(f"Error creating recharge promo: {e}")
        return error_response(message="Failed to create recharge promo")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating recharge promo: {str(e)}")
        return error_response(message="Failed to create recharge promo")


@router.get("/recharge-discount/{promo_id}")
def get_recharge_promo(
    promo_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get a single recharge promo by ID."""
    promo = db.query(RechargePromo).filter(RechargePromo.id == promo_id).first()
    if not promo:
        return error_response(message="Recharge promo not found", status_code=status.HTTP_404_NOT_FOUND)
    d = promo.to_dict(user=promo.user, frontend_url=FRONTEND_URL)
    d["status"] = _promo_status(promo)
    return success_response(data=d, message="Recharge promo retrieved successfully")


@router.put("/recharge-discount/{promo_id}")
def update_recharge_promo(
    promo_id: int,
    request: UpdateRechargePromoRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update a recharge promo (time range, extra %, name)."""
    promo = db.query(RechargePromo).filter(RechargePromo.id == promo_id).first()
    if not promo:
        return error_response(message="Recharge promo not found", status_code=status.HTTP_404_NOT_FOUND)
    if request.extra_credits_percent is not None:
        promo.extra_credits_percent = request.extra_credits_percent
    if request.valid_from is not None:
        promo.valid_from = request.valid_from
    if request.valid_until is not None:
        promo.valid_until = request.valid_until
    if request.name is not None:
        promo.name = request.name
    db.commit()
    db.refresh(promo)
    d = promo.to_dict(user=promo.user, frontend_url=FRONTEND_URL)
    d["status"] = _promo_status(promo)
    return success_response(data=d, message="Recharge promo updated successfully")


@router.delete("/recharge-discount/{promo_id}")
def delete_recharge_promo(
    promo_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete a recharge promo."""
    promo = db.query(RechargePromo).filter(RechargePromo.id == promo_id).first()
    if not promo:
        return error_response(message="Recharge promo not found", status_code=status.HTTP_404_NOT_FOUND)
    db.delete(promo)
    db.commit()
    return success_response(message="Recharge promo deleted successfully")


@router.get("/recharge-discount/{promo_id}/email-preview")
def get_email_preview(
    promo_id: int,
    reason_key: Optional[str] = Query("exclusive"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get email subject and body preview for confirmation before sending."""
    promo = db.query(RechargePromo).filter(RechargePromo.id == promo_id).first()
    if not promo:
        return error_response(message="Recharge promo not found", status_code=status.HTTP_404_NOT_FOUND)
    if promo.user_id is None:
        return error_response(message="Cannot send email for all-users promo ()", status_code=status.HTTP_400_BAD_REQUEST)
    user = db.query(User).filter(User.id == promo.user_id).first()
    if not user:
        return error_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
    base = FRONTEND_URL.rstrip("/")
    recharge_url = f"{base}/recharge?promo={promo.promo_code}"
    valid_until_str = promo.valid_until.strftime("%Y-%m-%d") if promo.valid_until else None
    subject, html_content = build_recharge_promo_email_content(
        nickname=user.nickname or user.handle or "there",
        recharge_url=recharge_url,
        extra_credits_percent=float(promo.extra_credits_percent),
        valid_until_str=valid_until_str,
        reason_key=reason_key or "exclusive",
    )
    return success_response(
        data={"subject": subject, "html_content": html_content},
        message="Email preview retrieved successfully",
    )


@router.post("/recharge-discount/{promo_id}/send-email")
async def send_promo_email(
    promo_id: int,
    reason_key: Optional[str] = Body("exclusive", embed=True),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Send promo email to the user with the dedicated recharge link."""
    promo = db.query(RechargePromo).filter(RechargePromo.id == promo_id).first()
    if not promo:
        return error_response(message="Recharge promo not found", status_code=status.HTTP_404_NOT_FOUND)
    if promo.user_id is None:
        return error_response(message="Cannot send email for all-users promo ()", status_code=status.HTTP_400_BAD_REQUEST)
    user = db.query(User).filter(User.id == promo.user_id).first()
    if not user:
        return error_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
    base = FRONTEND_URL.rstrip("/")
    recharge_url = f"{base}/recharge?promo={promo.promo_code}"
    valid_until_str = promo.valid_until.strftime("%Y-%m-%d") if promo.valid_until else None
    success, error_msg = await send_recharge_promo_email(
        email=user.email,
        nickname=user.nickname or user.handle or "there",
        recharge_url=recharge_url,
        extra_credits_percent=float(promo.extra_credits_percent),
        valid_until_str=valid_until_str,
        reason_key=reason_key or "exclusive",
    )
    if success:
        logger.info(f"Promo email sent: promo_id={promo_id} to {user.email} by admin {current_admin.id}")
        return success_response(message="Promo email sent successfully")
    return error_response(message=error_msg or "Failed to send email", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
