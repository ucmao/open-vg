"""CheckIn routes for daily check-in rewards system."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone
import os
from dotenv import load_dotenv

from ..models.base import get_db
from ..models.user import User
from ..models.checkin import CheckIn
from ..models.credit_record import CreditType
from ..services.credit_service import add_credits as credit_service_add_credits
from ..utils.auth import get_current_user
from ..utils.responses import success_response, error_response
from ..utils.logger import logger

load_dotenv()

router = APIRouter()

#  - Check-in reward configuration
CHECKIN_BASE_REWARD = int(os.getenv("CHECKIN_BASE_REWARD", "5"))
CHECKIN_CONSECUTIVE_BONUS = int(os.getenv("CHECKIN_CONSECUTIVE_BONUS", "2"))
CHECKIN_MAX_CONSECUTIVE = int(os.getenv("CHECKIN_MAX_CONSECUTIVE", "7"))
CHECKIN_REWARD_EXPIRY_DAYS = int(os.getenv("CHECKIN_REWARD_EXPIRY_DAYS", "60"))


def _count_consecutive_days_backward(db: Session, user_id: int, from_date: date) -> int:
    """
    Count consecutive check-in days backwards from from_date.
    Used for consecutive check-in logic.
    """
    count = 0
    d = from_date
    while True:
        exists = db.query(CheckIn).filter(
            CheckIn.user_id == user_id,
            CheckIn.check_date == d
        ).first()
        if not exists:
            break
        count += 1
        d = d - timedelta(days=1)
    return count


@router.post("/checkin")
def daily_checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Daily check-in endpoint.
    
    Users can check in once per day to earn credits.
    Consecutive check-ins grant bonus credits, up to 7 consecutive days.
    
    Returns:
        - consecutive_days: Consecutive check-in days
        - reward_credits: Credits earned from this check-in
        - total_credits: User current total credits
        - next_reward: Credits available for tomorrow check-in
    """
    try:
        # Use UTC date so one user can only check in once per calendar day globally (avoids timezone bugs)
        today = datetime.now(timezone.utc).date()

        # Serialize check-ins for one user. The unique constraint remains the
        # final guard, while this row lock also keeps the credit grant and the
        # check-in record in the same race-free transaction.
        locked_user = db.query(User).filter(
            User.id == current_user.id
        ).with_for_update().first()
        if not locked_user:
            return error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        #  - Check if already checked in today
        existing = db.query(CheckIn).filter(
            CheckIn.user_id == current_user.id,
            CheckIn.check_date == today
        ).first()
        
        if existing:
            return error_response(
                message="，！",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # ：，； 7  1
        yesterday = today - timedelta(days=1)
        consecutive_before_today = _count_consecutive_days_backward(db, current_user.id, yesterday)
        raw_today = consecutive_before_today + 1
        consecutive_days = ((raw_today - 1) % CHECKIN_MAX_CONSECUTIVE) + 1  # 1~7
        
        #  - Calculate reward credits
        #  + （）
        # Base reward + consecutive bonus (capped)
        bonus_days = min(consecutive_days - 1, CHECKIN_MAX_CONSECUTIVE - 1)
        reward_credits = CHECKIN_BASE_REWARD + (CHECKIN_CONSECUTIVE_BONUS * bonus_days)
        
        #  - Create check-in record
        checkin = CheckIn(
            user_id=current_user.id,
            check_date=today,
            consecutive_days=consecutive_days,
            reward_credits=reward_credits
        )
        db.add(checkin)
        
        #  - Grant credits
        expire_at = datetime.now(timezone.utc) + timedelta(days=CHECKIN_REWARD_EXPIRY_DAYS)
        total_credits = credit_service_add_credits(
            db,
            locked_user.id,
            reward_credits,
            CreditType.GIFT,
            f"Daily check-in reward (consecutive {consecutive_days} {'day' if consecutive_days == 1 else 'days'})",
            expire_at=expire_at,
        )
        
        db.commit()
        
        # （7  1 ）- Tomorrow's reward (day 1 after day 7)
        next_consecutive = (consecutive_days % CHECKIN_MAX_CONSECUTIVE) + 1
        next_bonus_days = min(next_consecutive - 1, CHECKIN_MAX_CONSECUTIVE - 1)
        next_reward = CHECKIN_BASE_REWARD + (CHECKIN_CONSECUTIVE_BONUS * next_bonus_days)
        
        logger.info(f"User {current_user.id} checked in: day {consecutive_days}, earned {reward_credits} credits")
        
        return success_response(
            data={
                "consecutive_days": consecutive_days,
                "reward_credits": reward_credits,
                "total_credits": total_credits,
                "next_reward": next_reward
            },
            message=f"Check-in successful！ {reward_credits} "
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during check-in: {str(e)}")
        return error_response(
            message="，",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/checkin/status")
def get_checkin_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get check-in status.
    
    ，Whether checked in today、Consecutive check-in days。
    
    Returns:
        - has_checked_today: Whether checked in today
        - consecutive_days: Consecutive check-in days
        - checkin_dates: List of check-in dates for the last 7 days
        - next_reward: Credits for next check-in (if not checked in today)
        - total_checkins: Total check-in count
        - config: Check-in configuration info
    """
    try:
        today = datetime.now(timezone.utc).date()
        
        #  - Check if checked in today
        today_checkin = db.query(CheckIn).filter(
            CheckIn.user_id == current_user.id,
            CheckIn.check_date == today
        ).first()
        
        has_checked_today = today_checkin is not None
        
        # ：，； 7  1~7
        if today_checkin:
            raw = _count_consecutive_days_backward(db, current_user.id, today)
        else:
            yesterday = today - timedelta(days=1)
            raw = _count_consecutive_days_backward(db, current_user.id, yesterday)
        consecutive_days = ((raw - 1) % CHECKIN_MAX_CONSECUTIVE) + 1 if raw else 0
        
        # 7 - Get last 7 days check-in records
        seven_days_ago = today - timedelta(days=6)
        recent_checkins = db.query(CheckIn).filter(
            CheckIn.user_id == current_user.id,
            CheckIn.check_date >= seven_days_ago,
            CheckIn.check_date <= today
        ).order_by(CheckIn.check_date.desc()).all()
        
        checkin_dates = [c.check_date.isoformat() for c in recent_checkins]
        
        # （7  1 ）- Next check-in reward (day 1 after day 7)
        next_reward = None
        if not has_checked_today:
            next_consecutive = (consecutive_days % CHECKIN_MAX_CONSECUTIVE) + 1
            next_bonus_days = min(next_consecutive - 1, CHECKIN_MAX_CONSECUTIVE - 1)
            next_reward = CHECKIN_BASE_REWARD + (CHECKIN_CONSECUTIVE_BONUS * next_bonus_days)
        
        #  - Total check-ins count
        total_checkins = db.query(func.count(CheckIn.id)).filter(
            CheckIn.user_id == current_user.id
        ).scalar() or 0
        
        return success_response(
            data={
                "has_checked_today": has_checked_today,
                "consecutive_days": consecutive_days,
                "checkin_dates": checkin_dates,
                "next_reward": next_reward,
                "total_checkins": total_checkins,
                "config": {
                    "base_reward": CHECKIN_BASE_REWARD,
                    "consecutive_bonus": CHECKIN_CONSECUTIVE_BONUS,
                    "max_consecutive": CHECKIN_MAX_CONSECUTIVE,
                    "reward_expiry_days": CHECKIN_REWARD_EXPIRY_DAYS
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting check-in status: {str(e)}")
        return error_response(
            message="",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/checkin/history")
def get_checkin_history(
    page: int = 1,
    page_size: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get check-in history (paginated).
    
    Args:
        page: Page number (starting from 1)
        page_size: Records per page (default 30)
    
    Returns:
        - items: Check-in records list
        - total: Total records count
        - page: Current page number
        - page_size: Page size
    """
    try:
        #  - Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 30
        
        #  - Query check-in history
        query = db.query(CheckIn).filter(
            CheckIn.user_id == current_user.id
        ).order_by(CheckIn.check_date.desc())
        
        total = query.count()
        checkins = query.offset((page - 1) * page_size).limit(page_size).all()
        
        #  - Convert to dict
        items = [{
            "check_date": c.check_date.isoformat(),
            "consecutive_days": c.consecutive_days,
            "reward_credits": c.reward_credits,
            "created_at": c.created_at.isoformat()
        } for c in checkins]
        
        return success_response(
            data={
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting check-in history: {str(e)}")
        return error_response(
            message="",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
