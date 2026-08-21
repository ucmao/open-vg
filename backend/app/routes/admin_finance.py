"""
Admin routes for managing finances (recharges and credits).
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func
from typing import Optional
from datetime import datetime, timedelta, timezone

from ..models.base import get_db
from ..models.admin import Admin
from ..models.user import User
from ..models.payment_order import PaymentOrder, PaymentStatus
from ..models.credit_record import CreditRecord, CreditType
from ..services.credit_service import add_credits as credit_service_add_credits
from ..models.recharge_package import RechargePackage
from ..models.schemas import CreateRechargePackageRequest, UpdateRechargePackageRequest, ManualAdjustCreditRequest
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..utils.validation import validate_reason_english

router = APIRouter()

@router.get("/finance/recharges")
def get_recharge_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by email, order ID, PayPal order ID, or Stripe ID"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all payment orders (recharges) with search and pagination.
    """
    try:
        query = db.query(PaymentOrder).join(User)
        
        filters = []
        if status:
            filters.append(PaymentOrder.status == status)
            
        if search:
            search_term = f"%{search}%"
            search_filters = [
                User.email.ilike(search_term),
                User.nickname.ilike(search_term),
                PaymentOrder.paypal_order_id.ilike(search_term),
                PaymentOrder.stripe_session_id.ilike(search_term),
                PaymentOrder.stripe_payment_intent_id.ilike(search_term),
            ]
            normalized_order_id = search.strip().lstrip("#")
            if normalized_order_id.isdigit():
                search_filters.append(PaymentOrder.id == int(normalized_order_id))
            filters.append(or_(*search_filters))
            
        if filters:
            query = query.filter(and_(*filters))
            
        total = query.count()
        records = query.order_by(PaymentOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        items = []
        for record in records:
            d = record.to_dict()
            d["user"] = {
                "id": record.user.id,
                "email": record.user.email,
                "nickname": record.user.nickname,
                "handle": record.user.handle
            }
            items.append(d)
            
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Recharge records retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting recharge records: {str(e)}")
        return error_response(message="Failed to retrieve recharge records")

@router.get("/finance/credits")
def get_credit_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Search by user email or description"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all credit consumption/acquisition records.
    """
    try:
        query = db.query(CreditRecord).join(User)
        
        filters = []
        if user_id:
            filters.append(CreditRecord.user_id == user_id)
            
        if type:
            filters.append(CreditRecord.type == type)
            
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    User.email.ilike(search_term),
                    User.nickname.ilike(search_term),
                    CreditRecord.description.ilike(search_term)
                )
            )
            
        if filters:
            query = query.filter(and_(*filters))
            
        total = query.count()
        records = query.order_by(CreditRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        items = []
        for record in records:
            d = record.to_dict()
            d["user"] = {
                "id": record.user.id,
                "email": record.user.email,
                "nickname": record.user.nickname,
                "handle": record.user.handle
            }
            items.append(d)
            
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Credit records retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting credit records: {str(e)}")
        return error_response(message="Failed to retrieve credit records")

@router.get("/finance/stats")
def get_finance_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get financial statistics.
    """
    try:
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day)
        
        # 1. Revenue
        total_revenue = db.query(func.sum(PaymentOrder.amount_usd)).filter(
            PaymentOrder.status == PaymentStatus.COMPLETED
        ).scalar() or 0
        
        today_revenue = db.query(func.sum(PaymentOrder.amount_usd)).filter(
            and_(
                PaymentOrder.status == PaymentStatus.COMPLETED,
                PaymentOrder.completed_at >= today_start
            )
        ).scalar() or 0
        
        # 2. Credits given vs consumed
        total_recharged_credits = db.query(func.sum(CreditRecord.amount)).filter(
            CreditRecord.type == CreditType.RECHARGE
        ).scalar() or 0
        
        total_consumed_credits = db.query(func.sum(CreditRecord.amount)).filter(
            CreditRecord.type == CreditType.CONSUME
        ).scalar() or 0
        
        today_consumed_credits = db.query(func.sum(CreditRecord.amount)).filter(
            and_(
                CreditRecord.type == CreditType.CONSUME,
                CreditRecord.created_at >= today_start
            )
        ).scalar() or 0
        
        # 3. User balance aggregate
        total_user_balance = db.query(func.sum(User.total_credits)).scalar() or 0
        
        return success_response(
            data={
                "total_revenue": float(total_revenue),
                "today_revenue": float(today_revenue),
                "total_recharged_credits": int(total_recharged_credits),
                "total_consumed_credits": abs(int(total_consumed_credits)),
                "today_consumed_credits": abs(int(today_consumed_credits)),
                "total_user_balance": int(total_user_balance)
            }
        )
    except Exception as e:
        logger.error(f"Error getting finance stats: {str(e)}")
        return error_response(message="Failed to retrieve finance stats")

@router.post("/finance/manual-credit")
def manual_adjust_credits(
    request: ManualAdjustCreditRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Manually adjust a user's credits (Admin only).
    """
    try:
        valid, err = validate_reason_english(request.description)
        if not valid:
            return error_response(message=err or "Invalid description", status_code=400)

        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            return error_response(message="User not found", status_code=404)
            
        new_balance = credit_service_add_credits(
            db,
            request.user_id,
            request.amount,
            CreditType.GIFT if request.amount > 0 else CreditType.CONSUME,
            f"[Admin Manual] {request.description}",
        )
        db.commit()
        
        # Ensure balance doesn't go negative (safety clamp)
        if new_balance < 0:
            user.total_credits = 0
            db.commit()
            new_balance = 0
        
        logger.info(f"Admin {current_admin.username} adjusted credits for user {user.email}: {request.amount}")
        return success_response(
            data={
                "user_id": user.id,
                "new_balance": new_balance,
                "amount": request.amount
            },
            message="Credits adjusted successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error adjusting credits: {str(e)}")
        return error_response(message="Failed to adjust credits")


# --- Recharge Package Management ---

@router.get("/finance/packages")
def get_all_recharge_packages(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all recharge packages (including inactive ones) for admin management.
    """
    try:
        packages = db.query(RechargePackage).order_by(
            RechargePackage.order.asc(),
            RechargePackage.amount.asc()
        ).all()
        return success_response(data=[p.to_dict() for p in packages])
    except Exception as e:
        logger.error(f"Error getting all recharge packages: {str(e)}")
        return error_response(message="Failed to retrieve packages")


@router.post("/finance/packages")
def create_recharge_package(
    req: CreateRechargePackageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new recharge package.
    """
    try:
        package = RechargePackage(**req.model_dump())
        db.add(package)
        db.commit()
        db.refresh(package)
        
        logger.info(f"Admin {current_admin.username} created recharge package: {package.name}")
        return success_response(data=package.to_dict(), message="Package created successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating recharge package: {str(e)}")
        return error_response(message="Failed to create package")


@router.put("/finance/packages/{package_id}")
def update_recharge_package(
    package_id: int,
    req: UpdateRechargePackageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update an existing recharge package.
    """
    try:
        package = db.query(RechargePackage).filter(RechargePackage.id == package_id).first()
        if not package:
            return error_response(message="Package not found", status_code=404)
            
        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(package, key, value)
            
        db.commit()
        db.refresh(package)
        
        logger.info(f"Admin {current_admin.username} updated recharge package: {package.id}")
        return success_response(data=package.to_dict(), message="Package updated successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating recharge package: {str(e)}")
        return error_response(message="Failed to update package")


@router.delete("/finance/packages/{package_id}")
def delete_recharge_package(
    package_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a recharge package.
    """
    try:
        package = db.query(RechargePackage).filter(RechargePackage.id == package_id).first()
        if not package:
            return error_response(message="Package not found", status_code=404)
            
        db.delete(package)
        db.commit()
        
        logger.info(f"Admin {current_admin.username} deleted recharge package: {package_id}")
        return success_response(message="Package deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting recharge package: {str(e)}")
        return error_response(message="Failed to delete package")
