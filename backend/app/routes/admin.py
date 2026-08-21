from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func, or_
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
import pytz

from ..models.base import get_db
from ..models.user import User
from ..models.admin import Admin
from ..models.work import Work, ShareStatus, WorkStatus
from ..models.comment import Comment
from ..models.payment_order import PaymentOrder, PaymentStatus
from ..models.credit_record import CreditRecord, CreditType
from ..models.like import Like
from ..models.favorite import Favorite
from ..models.blog import BlogPost, PostStatus, BlogCategory, BlogTag
from ..models.generation_model import GenerationModel, APILibrary
from ..models.generate_page import GeneratePage
from ..models.generation_config import invalidate_cache
from ..models.schemas import (
    ReviewActionRequest,
    CreateBlogPostRequest,
    UpdateBlogPostRequest,
    CreateBlogCategoryRequest,
    UpdateBlogCategoryRequest,
    CreateBlogTagRequest,
    UpdateBlogTagRequest,
    CreateGenerationModelRequest,
    UpdateGenerationModelRequest,
    CreateAPILibraryRequest,
    UpdateAPILibraryRequest,
)
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..utils.url_slug import slugify
from ..services.generate_page_sync import upsert_generate_page_for_model, delete_generate_page_for_model

router = APIRouter()
def ensure_work_type_allowed(db: Session, work_type: str) -> None:
    """
    Ensure work_type exists as a level-1 generate page.
    This binds generation_models.work_type to /generate Category。
    """
    if not work_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_type is required",
        )

    exists = (
        db.query(GeneratePage)
        .filter(
            GeneratePage.level == 1,
            GeneratePage.category_name == work_type,
        )
        .first()
    )
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"work_type '{work_type}' must be one of level-1 generate pages (category_name)",
        )



@router.post("/works/{work_id}/approve")
def approve_work(
    work_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Approve a work for public sharing.
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if work.share_status != ShareStatus.PENDING:
            return error_response(
                message="Work is not pending review",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Approve work
        work.share_status = ShareStatus.APPROVED
        work.updated_at = datetime.now(timezone.utc)
        
        # Make files public in R2 (in production, update ACL)
        # This would require calling storage service to update file permissions
        
        db.commit()
        
        logger.info(f"Work {work_id} approved by admin {current_admin.id}")
        
        return success_response(
            message="Work approved successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving work: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/reject")
def reject_work(
    work_id: int,
    request: ReviewActionRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Reject a work with reason.
    """
    try:
        if request.action != "reject":
            return error_response(
                message="Invalid action",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.reject_reason:
            return error_response(
                message="Reject reason is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        from ..utils.validation import validate_reason_english
        valid, err = validate_reason_english(request.reject_reason)
        if not valid:
            return error_response(message=err or "Invalid reason", status_code=400)
        
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if work.share_status != ShareStatus.PENDING:
            return error_response(
                message="Work is not pending review",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Reject work
        work.share_status = ShareStatus.REJECTED
        work.reject_reason = request.reject_reason
        work.is_shared = False  # Reset shared flag
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"Work {work_id} rejected by admin {current_admin.id}")
        
        return success_response(
            message="Work rejected successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error rejecting work: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/works/{work_id}/takedown")
def takedown_work(
    work_id: int,
    request: ReviewActionRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Take down an approved work (for policy violations).
    """
    try:
        if not request.reject_reason:
            return error_response(
                message="Takedown reason is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        from ..utils.validation import validate_reason_english
        valid, err = validate_reason_english(request.reject_reason)
        if not valid:
            return error_response(message=err or "Invalid reason", status_code=400)
        
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if work.share_status != ShareStatus.APPROVED:
            return error_response(
                message="Work is not approved",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Take down work
        work.share_status = ShareStatus.REJECTED
        work.reject_reason = f"Takedown: {request.reject_reason}"
        work.is_shared = False
        work.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.warning(f"Work {work_id} taken down by admin {current_admin.id}: {request.reject_reason}")
        
        return success_response(
            message="Work taken down successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error taking down work: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/stats")
def get_admin_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get platform statistics for admin dashboard.
    "" / "" are calculated in Asia/Shanghai (Beijing time) for Chinese admins.
    """
    try:
        tz_beijing = pytz.timezone("Asia/Shanghai")
        now_utc = datetime.now(timezone.utc)
        now_beijing = now_utc.astimezone(tz_beijing)
        # Today 00:00 Beijing -> UTC for DB comparison
        today_start = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
        # First day of current month 00:00 Beijing -> UTC
        month_start = now_beijing.replace(day=1, hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
        seven_days_ago = now_utc - timedelta(days=7)
        
        # --- User Stats ---
        from ..models.user import UserSource
        from ..models.user_activity_log import UserActivityLog
        total_users = db.query(User).count()
        active_users = db.query(UserActivityLog.user_id).filter(
            UserActivityLog.created_at >= seven_days_ago
        ).distinct().count()
        today_new_users = db.query(User).filter(User.created_at >= today_start).count()
        # Real users: registered via email or Google OAuth
        real_users = db.query(User).filter(
            User.source.in_([UserSource.REGISTER, UserSource.GOOGLE])
        ).count()
        # Today's new real users
        today_new_real_users = db.query(User).filter(
            and_(
                User.source.in_([UserSource.REGISTER, UserSource.GOOGLE]),
                User.created_at >= today_start
            )
        ).count()
        
        # --- Work Stats ---
        #  /  （deleted_at）；「successful」， ≤100%
        total_works = db.query(Work).filter(
            Work.status == WorkStatus.SUCCESS,
            Work.deleted_at == None
        ).count()
        today_new_works = db.query(Work).filter(
            and_(
                Work.status == WorkStatus.SUCCESS,
                Work.deleted_at == None,
                Work.created_at >= today_start
            )
        ).count()
        approved_works = db.query(Work).filter(
            and_(
                Work.status == WorkStatus.SUCCESS,
                Work.deleted_at == None,
                Work.share_status == ShareStatus.APPROVED
            )
        ).count()
        
        # --- Revenue Stats (Monthly) ---
        from sqlalchemy import func
        # Monthly revenue (completed orders this month)
        monthly_revenue = db.query(func.sum(PaymentOrder.amount_usd)).filter(
            and_(
                PaymentOrder.status == PaymentStatus.COMPLETED,
                PaymentOrder.completed_at >= month_start
            )
        ).scalar() or 0
        
        today_revenue = db.query(func.sum(PaymentOrder.amount_usd)).filter(
            and_(
                PaymentOrder.status == PaymentStatus.COMPLETED,
                PaymentOrder.completed_at >= today_start
            )
        ).scalar() or 0

        # --- Recharge Stats (Monthly) ---
        # Monthly recharge count (completed orders this month)
        monthly_recharge_count = db.query(PaymentOrder).filter(
            and_(
                PaymentOrder.status == PaymentStatus.COMPLETED,
                PaymentOrder.completed_at >= month_start
            )
        ).count()
        
        total_paying_users = db.query(PaymentOrder.user_id).filter(
            PaymentOrder.status == PaymentStatus.COMPLETED
        ).distinct().count()
        
        today_recharge_count = db.query(PaymentOrder).filter(
            and_(
                PaymentOrder.status == PaymentStatus.COMPLETED,
                PaymentOrder.completed_at >= today_start
            )
        ).count()
        
        # Payment initiation count (all payment orders, regardless of status)
        payment_initiated_count = db.query(PaymentOrder).filter(
            PaymentOrder.created_at >= month_start
        ).count()
        
        today_payment_initiated_count = db.query(PaymentOrder).filter(
            PaymentOrder.created_at >= today_start
        ).count()
        
        # --- Engagement Stats ---
        total_comments = db.query(Comment).count()
        today_new_comments = db.query(Comment).filter(
            Comment.created_at >= today_start
        ).count()

        total_likes = db.query(Like).count()
        today_new_likes = db.query(Like).filter(
            Like.updated_at >= today_start
        ).count()

        total_favorites = db.query(Favorite).count()
        today_new_favorites = db.query(Favorite).filter(
            Favorite.updated_at >= today_start
        ).count()

        total_remixes = db.query(Work).filter(
            and_(Work.parent_id.isnot(None), Work.deleted_at == None)
        ).count()
        today_new_remixes = db.query(Work).filter(
            and_(
                Work.parent_id.isnot(None),
                Work.deleted_at == None,
                Work.created_at >= today_start
            )
        ).count()
        
        # Consumption Frequency (How many times users used the tools)
        total_consume_frequency = db.query(CreditRecord).filter(
            CreditRecord.type == CreditType.CONSUME
        ).count()
        
        today_consume_frequency = db.query(CreditRecord).filter(
            and_(
                CreditRecord.type == CreditType.CONSUME,
                CreditRecord.created_at >= today_start
            )
        ).count()
        
        # Successful works count from credit records (only successful generations)
        # Count CONSUME records where the associated work status is SUCCESS
        # Use inner join to only count records with valid work_id and successful work
        total_successful_works = db.query(CreditRecord).join(
            Work, CreditRecord.work_id == Work.id
        ).filter(
            and_(
                CreditRecord.type == CreditType.CONSUME,
                CreditRecord.work_id.isnot(None),
                Work.status == WorkStatus.SUCCESS
            )
        ).count()
        
        today_successful_works = db.query(CreditRecord).join(
            Work, CreditRecord.work_id == Work.id
        ).filter(
            and_(
                CreditRecord.type == CreditType.CONSUME,
                CreditRecord.work_id.isnot(None),
                Work.status == WorkStatus.SUCCESS,
                CreditRecord.created_at >= today_start
            )
        ).count()
        
        # --- NSFW Moderation Stats ---
        from ..models.moderation import NSFWStatus
        pending_nsfw_count = db.query(Work).filter(
            and_(
                Work.nsfw_status == NSFWStatus.PENDING.value,
                Work.deleted_at == None
            )
        ).count()
        
        stats = {
            "total_users": total_users,
            "real_users": real_users,
            "today_new_real_users": today_new_real_users,
            "active_users": active_users,
            "today_new_users": today_new_users,
            "total_works": total_works,
            "today_new_works": today_new_works,
            "approved_works": approved_works,
            "monthly_revenue": float(monthly_revenue),
            "today_revenue": float(today_revenue),
            "monthly_recharge_count": monthly_recharge_count,
            "total_paying_users": total_paying_users,
            "today_recharge_count": today_recharge_count,
            "payment_initiated_count": payment_initiated_count,
            "today_payment_initiated_count": today_payment_initiated_count,
            "total_comments": total_comments,
            "today_new_comments": today_new_comments,
            "total_likes": total_likes,
            "today_new_likes": today_new_likes,
            "total_favorites": total_favorites,
            "today_new_favorites": today_new_favorites,
            "total_remixes": total_remixes,
            "today_new_remixes": today_new_remixes,
            "total_consume_frequency": total_consume_frequency,
            "today_consume_frequency": today_consume_frequency,
            "total_successful_works": total_successful_works,
            "today_successful_works": today_successful_works,
            "pending_nsfw_count": pending_nsfw_count,
        }
        
        return success_response(
            data=stats,
            message="Statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/stats/snapshot")
def get_admin_stats_snapshot(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Real-time snapshot for dashboard top strip. Not affected by time picker.
    - : users with last_login in last 5 minutes (proxy for server load).
    - : revenue so far today (Beijing time). : credit records count today (Beijing time).
    - : pending NSFW count, pending reports (0 if no report model).
    - : total users, total works.
    """
    try:
        tz_beijing = pytz.timezone("Asia/Shanghai")
        now_utc = datetime.now(timezone.utc)
        now_beijing = now_utc.astimezone(tz_beijing)
        today_start = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
        five_min_ago = now_utc - timedelta(minutes=5)

        from ..models.user import UserSource
        from ..models.moderation import NSFWStatus, Report, ReportStatus

        online_count = db.query(User).filter(User.last_login >= five_min_ago).count()
        today_revenue = db.query(func.sum(PaymentOrder.amount_usd)).filter(
            and_(
                PaymentOrder.status == PaymentStatus.COMPLETED,
                PaymentOrder.completed_at >= today_start
            )
        ).scalar() or 0
        pending_nsfw_count = db.query(Work).filter(
            and_(
                Work.nsfw_status == NSFWStatus.PENDING.value,
                Work.deleted_at == None
            )
        ).count()
        
        # Query pending reports count
        try:
            pending_reports_count = db.query(Report).filter(
                Report.status == ReportStatus.PENDING
            ).count()
        except Exception:
            # If reports table doesn't exist yet, return 0
            pending_reports_count = 0
        
        total_users = db.query(User).count()
        total_works = db.query(Work).filter(
            Work.status == WorkStatus.SUCCESS,
            Work.deleted_at == None
        ).count()

        # （）
        today_credit_records_count = db.query(CreditRecord).filter(
            CreditRecord.created_at >= today_start
        ).count()

        return success_response(
            data={
                "online_count": online_count,
                "today_revenue": float(today_revenue),
                "today_credit_records_count": today_credit_records_count,
                "pending_nsfw_count": pending_nsfw_count,
                "pending_reports_count": pending_reports_count,
                "total_users": total_users,
                "total_works": total_works,
            },
            message="Snapshot retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting admin stats snapshot: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _period_stats(db: Session, start_dt: datetime, end_dt: datetime) -> dict:
    """Compute stats for a single time window [start_dt, end_dt)."""
    from ..models.user import UserSource
    from ..models.user_activity_log import UserActivityLog

    revenue = db.query(func.sum(PaymentOrder.amount_usd)).filter(
        and_(
            PaymentOrder.status == PaymentStatus.COMPLETED,
            PaymentOrder.completed_at >= start_dt,
            PaymentOrder.completed_at < end_dt
        )
    ).scalar() or 0

    recharge_count = db.query(PaymentOrder).filter(
        and_(
            PaymentOrder.status == PaymentStatus.COMPLETED,
            PaymentOrder.completed_at >= start_dt,
            PaymentOrder.completed_at < end_dt
        )
    ).count()

    new_users = db.query(User).filter(
        and_(
            User.source.in_([UserSource.REGISTER, UserSource.GOOGLE]),
            User.created_at >= start_dt,
            User.created_at < end_dt
        )
    ).count()

    # DAU:  user_activity_logs（）， last_login
    #  end_dt 「」（//7），end_date ，， <=；
    #  end_dt  00:00（「」），， <。
    tz_beijing = pytz.timezone("Asia/Shanghai")
    start_date = start_dt.astimezone(tz_beijing).date()
    end_dt_beijing = end_dt.astimezone(tz_beijing)
    end_date = end_dt_beijing.date()
    end_is_midnight = (
        end_dt_beijing.hour == 0
        and end_dt_beijing.minute == 0
        and end_dt_beijing.second == 0
        and end_dt_beijing.microsecond == 0
    )
    if end_is_midnight:
        active_users = db.query(UserActivityLog.user_id).filter(
            and_(
                UserActivityLog.activity_date >= start_date,
                UserActivityLog.activity_date < end_date
            )
        ).distinct().count()
    else:
        active_users = db.query(UserActivityLog.user_id).filter(
            and_(
                UserActivityLog.activity_date >= start_date,
                UserActivityLog.activity_date <= end_date
            )
        ).distinct().count()

    new_works = db.query(Work).filter(
        and_(
            Work.status == WorkStatus.SUCCESS,
            Work.deleted_at == None,
            Work.created_at >= start_dt,
            Work.created_at < end_dt
        )
    ).count()

    likes = db.query(Like).filter(
        and_(Like.created_at >= start_dt, Like.created_at < end_dt)
    ).count()

    comments = db.query(Comment).filter(
        and_(Comment.created_at >= start_dt, Comment.created_at < end_dt)
    ).count()

    favorites = db.query(Favorite).filter(
        and_(Favorite.created_at >= start_dt, Favorite.created_at < end_dt)
    ).count()

    remixes = db.query(Work).filter(
        and_(
            Work.parent_id.isnot(None),
            Work.deleted_at == None,
            Work.created_at >= start_dt,
            Work.created_at < end_dt
        )
    ).count()

    payment_initiated = db.query(PaymentOrder).filter(
        and_(
            PaymentOrder.created_at >= start_dt,
            PaymentOrder.created_at < end_dt
        )
    ).count()

    consume_frequency = db.query(CreditRecord).filter(
        and_(
            CreditRecord.type == CreditType.CONSUME,
            CreditRecord.created_at >= start_dt,
            CreditRecord.created_at < end_dt
        )
    ).count()

    successful_works = db.query(CreditRecord).join(
        Work, CreditRecord.work_id == Work.id
    ).filter(
        and_(
            CreditRecord.type == CreditType.CONSUME,
            CreditRecord.work_id.isnot(None),
            Work.status == WorkStatus.SUCCESS,
            CreditRecord.created_at >= start_dt,
            CreditRecord.created_at < end_dt
        )
    ).count()

    paying_users = db.query(PaymentOrder.user_id).filter(
        and_(
            PaymentOrder.status == PaymentStatus.COMPLETED,
            PaymentOrder.completed_at >= start_dt,
            PaymentOrder.completed_at < end_dt
        )
    ).distinct().count()

    return {
        "revenue": float(revenue),
        "recharge_count": recharge_count,
        "new_users": new_users,
        "active_users": active_users,
        "new_works": new_works,
        "likes": likes,
        "comments": comments,
        "favorites": favorites,
        "remixes": remixes,
        "payment_initiated": payment_initiated,
        "consume_frequency": consume_frequency,
        "successful_works": successful_works,
        "paying_users": paying_users,
    }


def _day1_retention(db: Session, start_dt: datetime, end_dt: datetime) -> dict:
    """
    Day-1 retention for real users: of users who registered in [start_dt, end_dt - 1 day),
    the share who have at least one activity on or after (registration date + 1 day) in Beijing.
    Uses user_activity_logs for accurate, stable retention (not last_login which gets overwritten).
    """
    from sqlalchemy import text

    end_dt_minus_1 = end_dt - timedelta(days=1)
    if start_dt >= end_dt_minus_1:
        return {"retention_cohort": 0, "retention_count": 0, "retention_rate": None}

    # Cohort = real users with created_at in [start_dt, end_dt - 1 day).
    # Retained = cohort members with at least one user_activity_logs row
    #   where activity_date >= (registration date in Beijing + 1 day).
    row = db.execute(
        text("""
        WITH cohort AS (
          SELECT
            u.id,
            (date(u.created_at AT TIME ZONE 'Asia/Shanghai') + interval '1 day')::date AS day1_min
          FROM users u
          WHERE u.source IN ('REGISTER', 'GOOGLE')
            AND u.created_at >= :start_dt AND u.created_at < :end_dt_minus_1
        )
        SELECT
          COUNT(*)::int AS cohort,
          COUNT(*) FILTER (WHERE EXISTS (
            SELECT 1 FROM user_activity_logs ual
            WHERE ual.user_id = cohort.id AND ual.activity_date >= cohort.day1_min
          ))::int AS retained
        FROM cohort
        """),
        {"start_dt": start_dt, "end_dt_minus_1": end_dt_minus_1},
    ).fetchone()

    cohort = row[0] or 0
    retained = row[1] or 0
    rate = (retained / cohort * 100) if cohort > 0 else None
    return {"retention_cohort": cohort, "retention_count": retained, "retention_rate": round(rate, 1) if rate is not None else None}


@router.get("/stats/period")
def get_admin_stats_period(
    range_type: str = Query("7d", description="today | yesterday | 7d | 14d | 30d"),
    start: Optional[str] = Query(None, description="ISO datetime for custom range start"),
    end: Optional[str] = Query(None, description="ISO datetime for custom range end"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Period stats for dashboard dynamic layer. Returns current period, previous period (same length),
    and totals. Frontend uses this to show "big number = period total" and "small number = %".
    """
    try:
        tz_beijing = pytz.timezone("Asia/Shanghai")
        now_utc = datetime.now(timezone.utc)
        now_beijing = now_utc.astimezone(tz_beijing)

        if range_type == "custom" and start and end:
            try:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                if start_dt.tzinfo is None:
                    start_dt = tz_beijing.localize(start_dt.replace(tzinfo=None)).astimezone(timezone.utc)
                if end_dt.tzinfo is None:
                    end_dt = tz_beijing.localize(end_dt.replace(tzinfo=None)).astimezone(timezone.utc)
            except ValueError:
                return error_response(message="Invalid start/end ISO format", status_code=400)
            period_length = end_dt - start_dt
            prev_end_dt = start_dt
            prev_start_dt = start_dt - period_length
            period_label = ""
        else:
            # today: from 00:00 Beijing today to now
            if range_type == "today":
                start_beijing = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0)
                end_dt = now_utc
                start_dt = start_beijing.astimezone(timezone.utc)
                prev_end_beijing = start_beijing
                prev_start_beijing = prev_end_beijing - timedelta(days=1)
                prev_start_dt = prev_start_beijing.astimezone(timezone.utc)
                prev_end_dt = prev_end_beijing.astimezone(timezone.utc)
                period_label = ""
            # yesterday: full calendar day Beijing
            elif range_type == "yesterday":
                yesterday = (now_beijing.date() - timedelta(days=1))
                start_beijing = tz_beijing.localize(datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0))
                end_beijing = start_beijing + timedelta(days=1)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = end_beijing.astimezone(timezone.utc)
                prev_start_beijing = start_beijing - timedelta(days=1)
                prev_end_beijing = start_beijing
                prev_start_dt = prev_start_beijing.astimezone(timezone.utc)
                prev_end_dt = prev_end_beijing.astimezone(timezone.utc)
                period_label = ""
            # 7： (-7) 00:00
            elif range_type == "7d":
                start_date_7d = now_beijing.date() - timedelta(days=7)
                start_beijing = tz_beijing.localize(datetime(start_date_7d.year, start_date_7d.month, start_date_7d.day, 0, 0, 0, 0))
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
                prev_start_date = start_date_7d - timedelta(days=7)
                prev_start_beijing = tz_beijing.localize(datetime(prev_start_date.year, prev_start_date.month, prev_start_date.day, 0, 0, 0, 0))
                prev_start_dt = prev_start_beijing.astimezone(timezone.utc)
                prev_end_dt = start_dt
                period_label = "7"
            # 14： (-14) 00:00
            elif range_type == "14d":
                start_date_14d = now_beijing.date() - timedelta(days=14)
                start_beijing = tz_beijing.localize(datetime(start_date_14d.year, start_date_14d.month, start_date_14d.day, 0, 0, 0, 0))
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
                prev_start_date = start_date_14d - timedelta(days=14)
                prev_start_beijing = tz_beijing.localize(datetime(prev_start_date.year, prev_start_date.month, prev_start_date.day, 0, 0, 0, 0))
                prev_start_dt = prev_start_beijing.astimezone(timezone.utc)
                prev_end_dt = start_dt
                period_label = "14"
            # 30： (-30) 00:00
            elif range_type == "30d":
                start_date_30d = now_beijing.date() - timedelta(days=30)
                start_beijing = tz_beijing.localize(datetime(start_date_30d.year, start_date_30d.month, start_date_30d.day, 0, 0, 0, 0))
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
                prev_start_date = start_date_30d - timedelta(days=30)
                prev_start_beijing = tz_beijing.localize(datetime(prev_start_date.year, prev_start_date.month, prev_start_date.day, 0, 0, 0, 0))
                prev_start_dt = prev_start_beijing.astimezone(timezone.utc)
                prev_end_dt = start_dt
                period_label = "30"
            # : from 1st 00:00 Beijing to now
            elif range_type == "month":
                start_beijing = now_beijing.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
                #
                prev_end_beijing = start_beijing
                prev_start_beijing = (start_beijing.replace(day=1) - timedelta(days=1)).replace(day=1)
                prev_start_dt = prev_start_beijing.astimezone(timezone.utc)
                prev_end_dt = prev_end_beijing.astimezone(timezone.utc)
                period_label = ""
            # : full last month Beijing; previous = month before last
            elif range_type == "last_month":
                first_this = now_beijing.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                last_month_end_beijing = first_this
                last_month_start_beijing = (first_this - timedelta(days=1)).replace(day=1)
                start_dt = last_month_start_beijing.astimezone(timezone.utc)
                end_dt = last_month_end_beijing.astimezone(timezone.utc)
                prev_month_start_beijing = (last_month_start_beijing - timedelta(days=1)).replace(day=1)
                prev_start_dt = prev_month_start_beijing.astimezone(timezone.utc)
                prev_end_dt = last_month_start_beijing.astimezone(timezone.utc)
                period_label = ""
            # : Q1 1-3, Q2 4-6, Q3 7-9, Q4 10-12; previous = full last quarter
            elif range_type == "quarter":
                q = (now_beijing.month - 1) // 3 + 1
                start_beijing = now_beijing.replace(month=(q - 1) * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
                if q == 1:
                    prev_start_beijing = tz_beijing.localize(datetime(now_beijing.year - 1, 10, 1, 0, 0, 0, 0))
                else:
                    prev_start_beijing = tz_beijing.localize(datetime(now_beijing.year, (q - 2) * 3 + 1, 1, 0, 0, 0, 0))
                prev_end_beijing = start_beijing
                prev_start_dt = prev_start_beijing.astimezone(timezone.utc)
                prev_end_dt = prev_end_beijing.astimezone(timezone.utc)
                period_label = ""
            # : full last quarter; previous = quarter before
            elif range_type == "last_quarter":
                q = (now_beijing.month - 1) // 3 + 1
                end_quarter_beijing = now_beijing.replace(month=(q - 1) * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                if q == 1:
                    start_quarter_beijing = tz_beijing.localize(datetime(now_beijing.year - 1, 10, 1, 0, 0, 0, 0))
                else:
                    start_quarter_beijing = tz_beijing.localize(datetime(now_beijing.year, (q - 2) * 3 + 1, 1, 0, 0, 0, 0))
                start_dt = start_quarter_beijing.astimezone(timezone.utc)
                end_dt = end_quarter_beijing.astimezone(timezone.utc)
                period_length = end_dt - start_dt
                prev_end_dt = start_dt
                prev_start_dt = prev_end_dt - period_length
                period_label = ""
            # : Jan 1 00:00 Beijing to now
            elif range_type == "year":
                start_beijing = now_beijing.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
                prev_start_beijing = start_beijing.replace(year=now_beijing.year - 1)
                prev_end_beijing = start_beijing
                prev_start_dt = prev_start_beijing.astimezone(timezone.utc)
                prev_end_dt = prev_end_beijing.astimezone(timezone.utc)
                period_label = ""
            else:
                end_dt = now_utc
                start_dt = end_dt - timedelta(days=7)
                prev_end_dt = start_dt
                prev_start_dt = prev_end_dt - timedelta(days=7)
                period_label = "7"

        current = _period_stats(db, start_dt, end_dt)
        previous = _period_stats(db, prev_start_dt, prev_end_dt)

        retention_current = _day1_retention(db, start_dt, end_dt)
        retention_previous = _day1_retention(db, prev_start_dt, prev_end_dt)
        current["retention_cohort"] = retention_current["retention_cohort"]
        current["retention_count"] = retention_current["retention_count"]
        current["retention_rate"] = retention_current["retention_rate"]
        previous["retention_cohort"] = retention_previous["retention_cohort"]
        previous["retention_count"] = retention_previous["retention_count"]
        previous["retention_rate"] = retention_previous["retention_rate"]

        total_users = db.query(User).count()
        total_works = db.query(Work).filter(
            Work.status == WorkStatus.SUCCESS,
            Work.deleted_at == None
        ).count()
        from ..models.user import UserSource
        total_real_users = db.query(User).filter(
            User.source.in_([UserSource.REGISTER, UserSource.GOOGLE])
        ).count()

        return success_response(
            data={
                "period_label": period_label,
                "period_start": start_dt.isoformat(),
                "period_end": end_dt.isoformat(),
                "current": current,
                "previous": previous,
                "totals": {"total_users": total_users, "total_works": total_works, "total_real_users": total_real_users},
            },
            message="Period stats retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting admin stats period: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/stats/history")
def get_admin_stats_history(
    range_type: str = Query("7d", description="today | yesterday | 7d | 14d | 30d | month | last_month | quarter | last_quarter | year | custom"),
    start: Optional[str] = Query(None, description="ISO datetime for custom range start"),
    end: Optional[str] = Query(None, description="ISO datetime for custom range end"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get historical statistics for charts (daily trend).
    Matches the range selection logic of /stats/period.
    """
    try:
        from sqlalchemy import func, and_
        from ..models.user import UserSource
        from ..models.user_activity_log import UserActivityLog
        
        tz_beijing = pytz.timezone("Asia/Shanghai")
        now_utc = datetime.now(timezone.utc)
        now_beijing = now_utc.astimezone(tz_beijing)
        
        # 1. Calculate the target date range (start_dt, end_dt) using the same logic as /stats/period
        if range_type == "custom" and start and end:
            try:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                if start_dt.tzinfo is None:
                    start_dt = tz_beijing.localize(start_dt.replace(tzinfo=None)).astimezone(timezone.utc)
                if end_dt.tzinfo is None:
                    end_dt = tz_beijing.localize(end_dt.replace(tzinfo=None)).astimezone(timezone.utc)
            except ValueError:
                return error_response(message="Invalid start/end ISO format", status_code=400)
        else:
            if range_type == "today":
                start_beijing = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
            elif range_type == "yesterday":
                yesterday = (now_beijing.date() - timedelta(days=1))
                start_beijing = tz_beijing.localize(datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0))
                end_beijing = start_beijing + timedelta(days=1)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = end_beijing.astimezone(timezone.utc)
            elif range_type == "7d":
                start_date_7d = now_beijing.date() - timedelta(days=7)
                start_beijing = tz_beijing.localize(datetime(start_date_7d.year, start_date_7d.month, start_date_7d.day, 0, 0, 0, 0))
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
            elif range_type == "14d":
                start_date_14d = now_beijing.date() - timedelta(days=14)
                start_beijing = tz_beijing.localize(datetime(start_date_14d.year, start_date_14d.month, start_date_14d.day, 0, 0, 0, 0))
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
            elif range_type == "30d":
                start_date_30d = now_beijing.date() - timedelta(days=30)
                start_beijing = tz_beijing.localize(datetime(start_date_30d.year, start_date_30d.month, start_date_30d.day, 0, 0, 0, 0))
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
            elif range_type == "month":
                start_beijing = now_beijing.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
            elif range_type == "last_month":
                first_this = now_beijing.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                last_month_start_beijing = (first_this - timedelta(days=1)).replace(day=1)
                start_dt = last_month_start_beijing.astimezone(timezone.utc)
                end_dt = first_this.astimezone(timezone.utc)
            elif range_type == "quarter":
                q = (now_beijing.month - 1) // 3 + 1
                start_beijing = now_beijing.replace(month=(q - 1) * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
            elif range_type == "last_quarter":
                q = (now_beijing.month - 1) // 3 + 1
                end_quarter_beijing = now_beijing.replace(month=(q - 1) * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                if q == 1:
                    start_quarter_beijing = tz_beijing.localize(datetime(now_beijing.year - 1, 10, 1, 0, 0, 0, 0))
                else:
                    start_quarter_beijing = tz_beijing.localize(datetime(now_beijing.year, (q - 2) * 3 + 1, 1, 0, 0, 0, 0))
                start_dt = start_quarter_beijing.astimezone(timezone.utc)
                end_dt = end_quarter_beijing.astimezone(timezone.utc)
            elif range_type == "year":
                start_beijing = now_beijing.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc
            else:
                start_date_7d = now_beijing.date() - timedelta(days=7)
                start_beijing = tz_beijing.localize(datetime(start_date_7d.year, start_date_7d.month, start_date_7d.day, 0, 0, 0, 0))
                start_dt = start_beijing.astimezone(timezone.utc)
                end_dt = now_utc

        # 2. Optimized Data Querying using GROUP BY
        # Use helper for date truncation in Beijing time
        def bj_date(column):
            return func.date(func.timezone('Asia/Shanghai', column))

        # 2.1 Get initial cumulative real users before start_dt
        initial_real_users_count = db.query(User).filter(
            and_(
                User.source.in_([UserSource.REGISTER, UserSource.GOOGLE]),
                User.created_at < start_dt
            )
        ).count()

        # 2.2 Get daily counts for all metrics
        # Real Users
        real_users_daily = db.query(bj_date(User.created_at), func.count(User.id)).filter(
            and_(
                User.source.in_([UserSource.REGISTER, UserSource.GOOGLE]),
                User.created_at >= start_dt,
                User.created_at < end_dt
            )
        ).group_by(bj_date(User.created_at)).all()
        real_users_map = {date: count for date, count in real_users_daily}

        # All Users
        new_users_daily = db.query(bj_date(User.created_at), func.count(User.id)).filter(
            and_(User.created_at >= start_dt, User.created_at < end_dt)
        ).group_by(bj_date(User.created_at)).all()
        new_users_map = {date: count for date, count in new_users_daily}

        # Active Users (DAU) - UserActivityLog.activity_date is already a Date
        active_users_daily = db.query(UserActivityLog.activity_date, func.count(func.distinct(UserActivityLog.user_id))).filter(
            and_(
                UserActivityLog.activity_date >= start_dt.astimezone(tz_beijing).date(),
                UserActivityLog.activity_date <= end_dt.astimezone(tz_beijing).date()
            )
        ).group_by(UserActivityLog.activity_date).all()
        active_users_map = {date: count for date, count in active_users_daily}

        # New Works
        new_works_daily = db.query(bj_date(Work.created_at), func.count(Work.id)).filter(
            and_(Work.status == WorkStatus.SUCCESS, Work.created_at >= start_dt, Work.created_at < end_dt)
        ).group_by(bj_date(Work.created_at)).all()
        works_map = {date: count for date, count in new_works_daily}

        # Revenue and Recharge Count
        payment_daily = db.query(
            bj_date(PaymentOrder.completed_at),
            func.sum(PaymentOrder.amount_usd),
            func.count(PaymentOrder.id)
        ).filter(
            and_(PaymentOrder.status == PaymentStatus.COMPLETED, PaymentOrder.completed_at >= start_dt, PaymentOrder.completed_at < end_dt)
        ).group_by(bj_date(PaymentOrder.completed_at)).all()
        revenue_map = {date: float(rev or 0) for date, rev, _ in payment_daily}
        recharge_map = {date: count for date, _, count in payment_daily}

        # Consumes
        consumes_daily = db.query(bj_date(CreditRecord.created_at), func.count(CreditRecord.id)).filter(
            and_(CreditRecord.type == CreditType.CONSUME, CreditRecord.created_at >= start_dt, CreditRecord.created_at < end_dt)
        ).group_by(bj_date(CreditRecord.created_at)).all()
        consumes_map = {date: count for date, count in consumes_daily}

        # Interaction (Comments, Likes, Favorites)
        comments_daily = db.query(bj_date(Comment.created_at), func.count(Comment.id)).filter(
            and_(Comment.created_at >= start_dt, Comment.created_at < end_dt)
        ).group_by(bj_date(Comment.created_at)).all()
        comments_map = {date: count for date, count in comments_daily}

        likes_daily = db.query(bj_date(Like.updated_at), func.count(Like.id)).filter(
            and_(Like.updated_at >= start_dt, Like.updated_at < end_dt)
        ).group_by(bj_date(Like.updated_at)).all()
        likes_map = {date: count for date, count in likes_daily}

        favorites_daily = db.query(bj_date(Favorite.updated_at), func.count(Favorite.id)).filter(
            and_(Favorite.updated_at >= start_dt, Favorite.updated_at < end_dt)
        ).group_by(bj_date(Favorite.updated_at)).all()
        favorites_map = {date: count for date, count in favorites_daily}

        # 3. Assemble History
        history = []
        iter_start_beijing = start_dt.astimezone(tz_beijing).replace(hour=0, minute=0, second=0, microsecond=0)
        iter_end_beijing = end_dt.astimezone(tz_beijing)
        
        current_day_beijing = iter_start_beijing
        cumulative_real_users = initial_real_users_count
        
        while current_day_beijing.date() <= iter_end_beijing.date():
            target_date = current_day_beijing.date()
            new_real = real_users_map.get(target_date, 0)
            cumulative_real_users += new_real
            
            history.append({
                "date": target_date.strftime("%m-%d"),
                "new_users": new_users_map.get(target_date, 0),
                "new_real_users": new_real,
                "cumulative_real_users": cumulative_real_users,
                "active_users": active_users_map.get(target_date, 0),
                "new_works": works_map.get(target_date, 0),
                "revenue": revenue_map.get(target_date, 0.0),
                "consumes": consumes_map.get(target_date, 0),
                "new_comments": comments_map.get(target_date, 0),
                "new_likes": likes_map.get(target_date, 0),
                "new_favorites": favorites_map.get(target_date, 0),
                "recharge_count": recharge_map.get(target_date, 0)
            })
            current_day_beijing += timedelta(days=1)
            
        return success_response(data=history)
        
    except Exception as e:
        logger.error(f"Error getting stats history: {str(e)}", exc_info=True)
        return error_response(message="An error occurred")



# NOTE: /users endpoint has been moved to admin_users.py for better organization
# and to support additional filters (is_active, source)


# Blog Management Routes
class BatchUpdateBlogPostRequest(BaseModel):
    """Batch update blog posts request"""
    post_ids: Optional[List[int]] = Field(None, description="Post ID list")
    status: Optional[str] = Field(None, description="Status")
    is_featured: Optional[bool] = Field(None, description="Is featured")
    category: Optional[str] = Field(None, description="Category")


@router.post("/blog/posts/batch-update")
def batch_update_blog_posts(
    request: BatchUpdateBlogPostRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ (Admin only)."""
    if not request.post_ids:
        return error_response(message="Post ID list", status_code=400)
    
    try:
        update_data = {}
        if request.status is not None:
            update_data[BlogPost.status] = PostStatus(request.status)
        if request.is_featured is not None:
            update_data[BlogPost.is_featured] = request.is_featured
        if request.category is not None:
            update_data[BlogPost.category] = request.category
            
        if not update_data:
            return error_response(message="Update data not provided", status_code=400)
            
        affected = db.query(BlogPost).filter(BlogPost.id.in_(request.post_ids)).update(
            update_data, synchronize_session=False
        )
        db.commit()
        return success_response(message=f"successful {affected} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch updating blog posts: {str(e)}")
        return error_response(message=f"failed: {str(e)}", status_code=500)


@router.post("/blog/posts/batch-delete")
def batch_delete_blog_posts(
    post_ids: List[int] = Body(..., embed=True),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Batch delete blog posts. Admin only."""
    if not post_ids:
        return error_response(message="Post ID list", status_code=400)
        
    try:
        affected = db.query(BlogPost).filter(BlogPost.id.in_(post_ids)).delete(synchronize_session=False)
        db.commit()
        return success_response(message=f"successful {affected} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch deleting blog posts: {str(e)}")
        return error_response(message=f"failed: {str(e)}", status_code=500)


@router.get("/blog/stats")
def get_blog_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Return blog stats: total, published_count, featured_count, total_views."""
    try:
        total = db.query(BlogPost).count()
        published_count = db.query(BlogPost).filter(BlogPost.status == PostStatus.PUBLISHED).count()
        featured_count = db.query(BlogPost).filter(BlogPost.is_featured == True).count()
        total_views = db.query(func.coalesce(func.sum(BlogPost.view_count), 0)).scalar() or 0
        return success_response(
            data={
                "total": total,
                "published_count": published_count,
                "featured_count": featured_count,
                "total_views": int(total_views),
            },
            message="OK"
        )
    except Exception as e:
        logger.error(f"Error getting blog stats: {str(e)}")
        return error_response(message="failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/blog/posts")
def get_blog_posts(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all blog posts for admin management.
    Includes drafts, published, and archived posts.
    """
    try:
        query = db.query(BlogPost)
        
        # Apply status filter if provided
        if status_filter:
            try:
                status_enum = PostStatus(status_filter)
                query = query.filter(BlogPost.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        total = query.count()
        # Try to order by sort_order if column exists, otherwise fallback to created_at
        try:
            posts = query.order_by(BlogPost.sort_order, desc(BlogPost.created_at))\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()
        except Exception:
            # Fallback if sort_order column doesn't exist yet
            posts = query.order_by(desc(BlogPost.created_at))\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()
        
        items = [post.to_dict() for post in posts]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Blog posts retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting blog posts: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/blog/posts/{post_id}")
def get_blog_post(
    post_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get a single blog post by ID for admin.
    """
    try:
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        
        if not post:
            return error_response(
                message="Post not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return success_response(
            data=post.to_dict(include_content=True),
            message="Blog post retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting blog post: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/blog/posts")
def create_blog_post(
    request: CreateBlogPostRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new blog post.
    """
    try:
        # Check if slug already exists
        existing = db.query(BlogPost).filter(BlogPost.slug == request.slug).first()
        if existing:
            return error_response(
                message="A post with this slug already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Set published_at based on status
        published_at = request.published_at
        if request.status == "published" and not published_at:
            published_at = datetime.now(timezone.utc)
        
        # Use provided author_id or default to current admin
        author_id = request.author_id if request.author_id else current_admin.id
        
        # Validate author_id if provided
        if request.author_id:
            from ..models.user import User
            author = db.query(User).filter(User.id == request.author_id).first()
            if not author:
                return error_response(
                    message="Author user not found",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        new_post = BlogPost(
            slug=request.slug,
            title=request.title,
            excerpt=request.excerpt,
            content=request.content,
            meta_title=request.meta_title,
            meta_description=request.meta_description,
            meta_keywords=request.meta_keywords,
            og_image=request.og_image,
            category=request.category,
            category_id=request.category_id,
            tags=request.tags or [],
            status=PostStatus(request.status),
            is_featured=request.is_featured,
            author_id=author_id,
            published_at=published_at
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        logger.info(f"Blog post created: {new_post.id} by admin {current_admin.id}")
        
        return success_response(
            data=new_post.to_dict(include_content=True),
            message="Blog post created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating blog post: {str(e)}")
        return error_response(
            message="An error occurred while creating blog post",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/blog/posts/{post_id}")
def update_blog_post(
    post_id: int,
    request: UpdateBlogPostRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update an existing blog post.
    """
    try:
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        
        if not post:
            return error_response(
                message="Post not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if slug is being changed and conflicts
        if request.slug and request.slug != post.slug:
            existing = db.query(BlogPost).filter(BlogPost.slug == request.slug).first()
            if existing:
                return error_response(
                    message="A post with this slug already exists",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            post.slug = request.slug
        
        # Update fields
        if request.title is not None:
            post.title = request.title
        if request.excerpt is not None:
            post.excerpt = request.excerpt
        if request.content is not None:
            post.content = request.content
        if request.meta_title is not None:
            post.meta_title = request.meta_title
        if request.meta_description is not None:
            post.meta_description = request.meta_description
        if request.meta_keywords is not None:
            post.meta_keywords = request.meta_keywords
        if request.og_image is not None:
            post.og_image = request.og_image
        if request.category is not None:
            post.category = request.category
        if request.category_id is not None:
            post.category_id = request.category_id
        if request.tags is not None:
            post.tags = request.tags
        if request.status is not None:
            post.status = PostStatus(request.status)
        if request.is_featured is not None:
            post.is_featured = request.is_featured
        if request.published_at is not None:
            post.published_at = request.published_at
        elif request.status == "published" and post.status != PostStatus.PUBLISHED and not post.published_at:
            post.published_at = datetime.now(timezone.utc)
        
        # Update author if provided
        if request.author_id is not None:
            from ..models.user import User
            author = db.query(User).filter(User.id == request.author_id).first()
            if not author:
                return error_response(
                    message="Author user not found",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            post.author_id = request.author_id
        
        post.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(post)
        
        logger.info(f"Blog post updated: {post_id} by admin {current_admin.id}")
        
        return success_response(
            data=post.to_dict(include_content=True),
            message="Blog post updated successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating blog post: {str(e)}")
        return error_response(
            message="An error occurred while updating blog post",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/blog/posts/{post_id}")
def delete_blog_post(
    post_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a blog post.
    """
    try:
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        
        if not post:
            return error_response(
                message="Post not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        db.delete(post)
        db.commit()
        
        logger.info(f"Blog post deleted: {post_id} by admin {current_admin.id}")
        
        return success_response(
            message="Blog post deleted successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting blog post: {str(e)}")
        return error_response(
            message="An error occurred while deleting blog post",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/blog/posts/generate-seo")
def generate_blog_seo_from_content(
    request: dict = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Generate SEO title, description, and tags for blog content using Gemini API.
    Can be used for new posts (before saving) or existing posts.
    """
    try:
        from ..services.gemini_service import get_gemini_service
        
        title = request.get("title", "")
        content = request.get("content", "")
        excerpt = request.get("excerpt")
        
        if not title:
            return error_response(
                message="Title is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not content:
            return error_response(
                message="Content is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate content using Gemini (pass db session)
        gemini_service = get_gemini_service(db_session=db)
        generated = gemini_service.generate_blog_seo(
            title=title,
            content=content,
            excerpt=excerpt
        )
        
        return success_response(
            data=generated,
            message="SEO content generated successfully"
        )
        
    except ValueError as e:
        # API key not configured
        return error_response(
            message=f"Gemini API : {str(e)}。。",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error generating blog SEO content: {error_message}")
        
        # Return appropriate status code based on error type
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if "" in error_message or "overloaded" in error_message.lower() or "unavailable" in error_message.lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif "quota" in error_message.lower() or "rate limit" in error_message.lower() or "429" in error_message:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        
        return error_response(
            message=error_message,
            status_code=status_code
        )


@router.post("/blog/posts/{post_id}/generate-seo")
def generate_blog_seo(
    post_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Generate SEO title, description, and tags for a blog post using Gemini API.
    """
    try:
        from ..services.gemini_service import get_gemini_service
        
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        
        if not post:
            return error_response(
                message="Post not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if not post.title:
            return error_response(
                message="Post has no title",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not post.content:
            return error_response(
                message="Post has no content",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate content using Gemini (pass db session)
        gemini_service = get_gemini_service(db_session=db)
        generated = gemini_service.generate_blog_seo(
            title=post.title,
            content=post.content,
            excerpt=post.excerpt
        )
        
        return success_response(
            data=generated,
            message="SEO content generated successfully"
        )
        
    except ValueError as e:
        # API key not configured
        return error_response(
            message=f"Gemini API : {str(e)}。。",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error generating blog SEO content: {error_message}")
        
        # Return appropriate status code based on error type
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if "" in error_message or "overloaded" in error_message.lower() or "unavailable" in error_message.lower():
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif "quota" in error_message.lower() or "rate limit" in error_message.lower() or "429" in error_message:
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        
        return error_response(
            message=error_message,
            status_code=status_code
        )


# Blog Category Management
@router.get("/blog/categories")
def get_blog_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all blog categories."""
    try:
        categories = db.query(BlogCategory).order_by(BlogCategory.name).all()
        return success_response(data=[c.to_dict() for c in categories])
    except Exception as e:
        logger.error(f"Error getting blog categories: {str(e)}")
        return error_response(message="An error occurred")


@router.post("/blog/categories")
def create_blog_category(
    request: CreateBlogCategoryRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new blog category."""
    try:
        # Check if name or slug already exists
        existing = db.query(BlogCategory).filter(
            (BlogCategory.name == request.name) | (BlogCategory.slug == request.slug)
        ).first()
        if existing:
            return error_response(message="Category name or slug already exists", status_code=400)
        
        new_category = BlogCategory(**request.model_dump())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return success_response(data=new_category.to_dict(), message="Category created successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating blog category: {str(e)}")
        return error_response(message="An error occurred")


@router.put("/blog/categories/{category_id}")
def update_blog_category(
    category_id: int,
    request: UpdateBlogCategoryRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a blog category."""
    try:
        category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()
        if not category:
            return error_response(message="Category not found", status_code=404)
        
        if request.name is not None:
            category.name = request.name
        if request.slug is not None:
            category.slug = request.slug
        if request.description is not None:
            category.description = request.description
            
        db.commit()
        db.refresh(category)
        return success_response(data=category.to_dict(), message="Category updated successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating blog category: {str(e)}")
        return error_response(message="An error occurred")


@router.delete("/blog/categories/{category_id}")
def delete_blog_category(
    category_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a blog category."""
    try:
        category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()
        if not category:
            return error_response(message="Category not found", status_code=404)
        
        db.delete(category)
        db.commit()
        return success_response(message="Category deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting blog category: {str(e)}")
        return error_response(message="An error occurred")


# Blog Tag Management
@router.get("/blog/tags")
def get_blog_tags(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all blog tags."""
    try:
        tags = db.query(BlogTag).order_by(BlogTag.name).all()
        return success_response(data=[t.to_dict() for t in tags])
    except Exception as e:
        logger.error(f"Error getting blog tags: {str(e)}")
        return error_response(message="An error occurred")


@router.post("/blog/tags")
def create_blog_tag(
    request: CreateBlogTagRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new blog tag."""
    try:
        existing = db.query(BlogTag).filter(
            (BlogTag.name == request.name) | (BlogTag.slug == request.slug)
        ).first()
        if existing:
            return error_response(message="Tag name or slug already exists", status_code=400)
        
        new_tag = BlogTag(**request.model_dump())
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return success_response(data=new_tag.to_dict(), message="Tag created successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating blog tag: {str(e)}")
        return error_response(message="An error occurred")


@router.put("/blog/tags/{tag_id}")
def update_blog_tag(
    tag_id: int,
    request: UpdateBlogTagRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a blog tag."""
    try:
        tag = db.query(BlogTag).filter(BlogTag.id == tag_id).first()
        if not tag:
            return error_response(message="Tag not found", status_code=404)
        
        if request.name is not None:
            tag.name = request.name
        if request.slug is not None:
            tag.slug = request.slug
            
        db.commit()
        db.refresh(tag)
        return success_response(data=tag.to_dict(), message="Tag updated successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating blog tag: {str(e)}")
        return error_response(message="An error occurred")


@router.delete("/blog/tags/{tag_id}")
def delete_blog_tag(
    tag_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a blog tag."""
    try:
        tag = db.query(BlogTag).filter(BlogTag.id == tag_id).first()
        if not tag:
            return error_response(message="Tag not found", status_code=404)
        
        db.delete(tag)
        db.commit()
        return success_response(message="Tag deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting blog tag: {str(e)}")
        return error_response(message="An error occurred")


@router.post("/blog/categories/batch-import")
def batch_import_blog_categories(
    categories: List[CreateBlogCategoryRequest] = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Batch import blog categories."""
    try:
        created_count = 0
        skipped_count = 0
        errors = []
        
        for cat_request in categories:
            try:
                # Check if name or slug already exists
                existing = db.query(BlogCategory).filter(
                    (BlogCategory.name == cat_request.name) | (BlogCategory.slug == cat_request.slug)
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new category
                new_category = BlogCategory(**cat_request.model_dump())
                db.add(new_category)
                created_count += 1
                
            except Exception as e:
                errors.append(f"Category '{cat_request.name}': {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Admin {current_admin.id} batch imported {created_count} blog categories")
        
        return success_response(
            data={
                "created": created_count,
                "skipped": skipped_count,
                "errors": errors
            },
            message=f"Batch import completed: {created_count} created, {skipped_count} skipped"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch importing blog categories: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/blog/tags/batch-import")
def batch_import_blog_tags(
    tags: List[CreateBlogTagRequest] = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Batch import blog tags."""
    try:
        created_count = 0
        skipped_count = 0
        errors = []
        
        for tag_request in tags:
            try:
                # Check if name or slug already exists
                existing = db.query(BlogTag).filter(
                    (BlogTag.name == tag_request.name) | (BlogTag.slug == tag_request.slug)
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new tag
                new_tag = BlogTag(**tag_request.model_dump())
                db.add(new_tag)
                created_count += 1
                
            except Exception as e:
                errors.append(f"Tag '{tag_request.name}': {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Admin {current_admin.id} batch imported {created_count} blog tags")
        
        return success_response(
            data={
                "created": created_count,
                "skipped": skipped_count,
                "errors": errors
            },
            message=f"Batch import completed: {created_count} created, {skipped_count} skipped"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch importing blog tags: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# API Library Management
# ============================================================================

@router.get("/api-library")
def get_api_library(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get API library entries with pagination."""
    try:
        query = db.query(APILibrary)
        
        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    APILibrary.name.ilike(search_filter),
                    APILibrary.provider.ilike(search_filter),
                    APILibrary.provider_model_id.ilike(search_filter)
                )
            )
        
        if is_active is not None:
            query = query.filter(APILibrary.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        apis = query.order_by(APILibrary.name).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [api.to_dict() for api in apis]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="API library retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting API library: {str(e)}")
        return error_response(message="An error occurred", status_code=500)


@router.get("/api-library/{api_id}")
def get_api_entry(
    api_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get a specific API entry."""
    api = db.query(APILibrary).filter(APILibrary.id == api_id).first()
    if not api:
        return error_response(message="API not found", status_code=404)
    return success_response(data=api.to_dict())


@router.post("/api-library")
def create_api_entry(
    request: CreateAPILibraryRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new API library entry."""
    try:
        existing = db.query(APILibrary).filter(APILibrary.api_key == request.api_key).first()
        if existing:
            return error_response(message=f"API key '{request.api_key}' already exists", status_code=400)
            
        new_api = APILibrary(**request.model_dump())
        db.add(new_api)
        db.commit()
        db.refresh(new_api)
        return success_response(data=new_api.to_dict(), message="API entry created", status_code=201)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating API entry: {str(e)}")
        return error_response(message=str(e), status_code=500)


@router.put("/api-library/{api_id}")
def update_api_entry(
    api_id: int,
    request: UpdateAPILibraryRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update an API library entry."""
    try:
        api = db.query(APILibrary).filter(APILibrary.id == api_id).first()
        if not api:
            return error_response(message="API not found", status_code=404)
            
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(api, key, value)
            
        db.commit()
        db.refresh(api)
        # Also invalidate generation models cache as API changes affect them
        invalidate_cache()
        return success_response(data=api.to_dict(), message="API entry updated")
    except Exception as e:
        db.rollback()
        return error_response(message=str(e), status_code=500)


@router.delete("/api-library/{api_id}")
def delete_api_entry(
    api_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete an API library entry."""
    try:
        api = db.query(APILibrary).filter(APILibrary.id == api_id).first()
        if not api:
            return error_response(message="API not found", status_code=404)
            
        # Check if used by any workflow node
        from ..models.workflow import Workflow
        workflows = db.query(Workflow).filter(Workflow.nodes.isnot(None)).all()
        ref_count = sum(1 for w in workflows if w.nodes and any(n.get("api_id") == api_id for n in w.nodes))
        if ref_count > 0:
            return error_response(message=f"Cannot delete API entry used by {ref_count} workflow(s)", status_code=400)
            
        db.delete(api)
        db.commit()
        return success_response(message="API entry deleted")
    except Exception as e:
        db.rollback()
        return error_response(message=str(e), status_code=500)


# ============================================================================
# Generation Model Management
# ============================================================================

@router.get("/models")
def get_generation_models(
    work_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all generation models, optionally filtered by work_type, is_active, and search.
    """
    try:
        from sqlalchemy.orm import joinedload
        from sqlalchemy import or_
        query = db.query(GenerationModel).options(
            joinedload(GenerationModel.workflow)
        )
        
        if work_type:
            query = query.filter(GenerationModel.work_type == work_type)
        
        if is_active is not None:
            # Ensure it's a boolean
            active_val = True if str(is_active).lower() in ['true', '1', 't', 'y', 'yes'] else False
            query = query.filter(GenerationModel.is_active == active_val)
            
        if search:
            search_filter = f"%{search}%"
            # Search in name, model_key, notes, and example_galleries (as string)
            from sqlalchemy import cast, String
            query = query.filter(
                or_(
                    GenerationModel.name.ilike(search_filter),
                    GenerationModel.model_key.ilike(search_filter),
                    GenerationModel.notes.ilike(search_filter),
                    cast(GenerationModel.example_galleries, String).ilike(search_filter)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated models
        models = query.order_by(
            GenerationModel.work_type,
            GenerationModel.sort_order,
            GenerationModel.id
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Convert models to dict, with error handling for each model
        items = []
        for model in models:
            try:
                item = model.to_full_dict()
            except Exception as e:
                logger.error(f"Error converting model {model.id} to dict: {str(e)}")
                try:
                    item = {
                        "id": model.id,
                        "name": model.name,
                        "model_key": model.model_key,
                        "work_type": model.work_type,
                        "workflow_id": model.workflow_id,
                        "is_active": model.is_active,
                        "error": f"Failed to load full details: {str(e)}"
                    }
                except Exception:
                    continue
            #  API （）
            workflow_api_names = []
            if getattr(model, "workflow", None) and model.workflow.nodes:
                api_ids = []
                seen_ids = set()
                for node in model.workflow.nodes:
                    if node.get("type") == "api_call" and node.get("api_id") and node["api_id"] not in seen_ids:
                        seen_ids.add(node["api_id"])
                        api_ids.append(node["api_id"])
                if api_ids:
                    apis = db.query(APILibrary).filter(APILibrary.id.in_(api_ids)).all()
                    id_to_name = {a.id: a.name for a in apis}
                    workflow_api_names = [id_to_name[i] for i in api_ids if i in id_to_name]
            item["workflow_api_names"] = workflow_api_names
            items.append(item)

        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Models retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting generation models: {str(e)}")
        return error_response(
            message="An error occurred while retrieving models",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/models/{model_id}")
def get_generation_model(
    model_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific generation model by ID.
    """
    try:
        model = db.query(GenerationModel).filter(GenerationModel.id == model_id).first()
        
        if not model:
            return error_response(
                message="Model not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return success_response(
            data=model.to_full_dict(),
            message="Model retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting generation model: {str(e)}")
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/models")
def create_generation_model(
    request: CreateGenerationModelRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new generation model.
    """
    try:
        # Validate workflow_id (required)
        from ..models.workflow import Workflow
        workflow = db.query(Workflow).filter(Workflow.id == request.workflow_id).first()
        if not workflow:
            return error_response(
                message=f"Workflow not found: {request.workflow_id}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        if not workflow.is_active:
            return error_response(
                message="Workflow is not active",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate work_type against generate_pages Category
        ensure_work_type_allowed(db, request.work_type)

        # Check if model_key already exists
        existing = db.query(GenerationModel).filter(
            GenerationModel.model_key == request.model_key
        ).first()
        
        if existing:
            return error_response(
                message=f"Model with key '{request.model_key}' already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # params_config is only for cost/credit additions (), not for visibility or defaults
        model_data = request.model_dump()
        model_data['created_by'] = current_admin.id
        model_data['params_config'] = request.params_config or {}
        
        new_model = GenerationModel(**model_data)
        
        db.add(new_model)
        db.flush()
        upsert_generate_page_for_model(
            db, new_model.work_type, new_model.model_key, new_model.name
        )
        db.commit()
        db.refresh(new_model)
        
        # Invalidate cache
        invalidate_cache()
        
        return success_response(
            data=new_model.to_full_dict(),
            message="Model created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating generation model: {str(e)}")
        return error_response(
            message="An error occurred while creating model",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/models/{model_id}")
def update_generation_model(
    model_id: int,
    request: UpdateGenerationModelRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update a generation model.
    """
    try:
        model = db.query(GenerationModel).filter(GenerationModel.id == model_id).first()
        
        if not model:
            return error_response(
                message="Model not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if model_key is being changed and if new key already exists
        if request.model_key and request.model_key != model.model_key:
            existing = db.query(GenerationModel).filter(
                GenerationModel.model_key == request.model_key,
                GenerationModel.id != model_id
            ).first()
            
            if existing:
                return error_response(
                    message=f"Model with key '{request.model_key}' already exists",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate workflow_id if provided
        workflow = None
        if request.workflow_id is not None:
            from ..models.workflow import Workflow
            if request.workflow_id:
                workflow = db.query(Workflow).filter(Workflow.id == request.workflow_id).first()
                if not workflow:
                    return error_response(
                        message=f"Workflow not found: {request.workflow_id}",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                if not workflow.is_active:
                    return error_response(
                        message="Workflow is not active",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # workflow_id cannot be None (must be provided)
                return error_response(
                    message="workflow_id is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # If work_type is being updated, validate against generate_pages Category
        if request.work_type is not None:
            ensure_work_type_allowed(db, request.work_type)

        # Determine target workflow: use new workflow if provided, otherwise use existing
        target_workflow = workflow
        if not target_workflow and model.workflow_id:
            from ..models.workflow import Workflow
            target_workflow = db.query(Workflow).filter(Workflow.id == model.workflow_id).first()
        
        # Update fields; params_config is only for cost/credit (), not for defaults
        update_data = request.model_dump(exclude_unset=True)
        old_work_type, old_model_key = model.work_type, model.model_key

        for key, value in update_data.items():
            if hasattr(model, key):
                setattr(model, key, value)

        db.commit()
        db.refresh(model)

        # Sync generate_pages: remove old path if work_type/model_key changed, then upsert current
        if (old_work_type, old_model_key) != (model.work_type, model.model_key):
            delete_generate_page_for_model(db, old_work_type, old_model_key)
        upsert_generate_page_for_model(
            db, model.work_type, model.model_key, model.name
        )
        db.commit()

        # Invalidate cache
        invalidate_cache()

        return success_response(
            data=model.to_full_dict(),
            message="Model updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating generation model: {str(e)}")
        return error_response(
            message="An error occurred while updating model",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/models/{model_id}")
def delete_generation_model(
    model_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a generation model.
    """
    try:
        model = db.query(GenerationModel).filter(GenerationModel.id == model_id).first()
        
        if not model:
            return error_response(
                message="Model not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        delete_generate_page_for_model(db, model.work_type, model.model_key)
        db.delete(model)
        db.commit()

        # Invalidate cache
        invalidate_cache()

        return success_response(message="Model deleted successfully")

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting generation model: {str(e)}")
        return error_response(
            message="An error occurred while deleting model",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class BatchUpdateModelRequest(BaseModel):
    """"""
    model_ids: Optional[List[int]] = Field(None, description="Model ID list")
    is_active: Optional[bool] = Field(None, description="Is enabled")
    is_featured: Optional[bool] = Field(None, description="Is featured")
    sort_order: Optional[int] = Field(None, description="Sort order")
    model_level: Optional[str] = Field(None, description="")
    category: Optional[str] = Field(None, description="")


class BatchUpdatePricingRequest(BaseModel):
    """Batch update model pricing request"""
    model_ids: List[int] = Field(..., description="Model ID list")
    cost: Optional[int] = Field(None, ge=0, description="Base cost (credits)")
    cost_additions: Optional[Dict[str, Dict[str, int]]] = Field(
        None,
        description="Cost additions: param_name -> { option_val -> credits }， {\"duration\": {\"5\": 0, \"8\": 10}}"
    )


@router.post("/models/batch-update-pricing")
def batch_update_models_pricing(
    request: BatchUpdatePricingRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """： (Admin only)."""
    if not request.model_ids:
        return error_response(message="Model ID list", status_code=400)
    if request.cost is None and not request.cost_additions:
        return error_response(message=" cost  cost_additions ", status_code=400)

    try:
        models = db.query(GenerationModel).filter(GenerationModel.id.in_(request.model_ids)).all()
        for model in models:
            if request.cost is not None:
                model.cost = request.cost
            if request.cost_additions:
                params_config = dict(model.params_config or {})
                for param_key, additions in request.cost_additions.items():
                    if not isinstance(additions, dict):
                        continue
                    entry = dict(params_config.get(param_key) or {})
                    existing = entry.get("cost_additions")
                    if isinstance(existing, dict):
                        merged = {**existing, **{str(k): int(v) for k, v in additions.items()}}
                    else:
                        merged = {str(k): int(v) for k, v in additions.items()}
                    entry["cost_additions"] = merged
                    params_config[param_key] = entry
                model.params_config = params_config
        db.commit()
        invalidate_cache()
        return success_response(message=f"successful {len(models)} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch updating model pricing: {str(e)}")
        return error_response(message=f"failed: {str(e)}", status_code=500)


@router.post("/models/batch-update")
def batch_update_models(
    request: BatchUpdateModelRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Batch update models. Admin only."""
    if not request.model_ids:
        return error_response(message="Model ID list", status_code=400)
    
    try:
        update_data = {}
        if request.is_active is not None:
            update_data[GenerationModel.is_active] = request.is_active
        if request.is_featured is not None:
            update_data[GenerationModel.is_featured] = request.is_featured
        if request.sort_order is not None:
            update_data[GenerationModel.sort_order] = request.sort_order
        if request.model_level is not None:
            update_data[GenerationModel.model_level] = request.model_level
        if request.category is not None:
            update_data[GenerationModel.category] = request.category
            
        if not update_data:
            return error_response(message="Update data not provided", status_code=400)
            
        affected = db.query(GenerationModel).filter(GenerationModel.id.in_(request.model_ids)).update(
            update_data, synchronize_session=False
        )
        db.commit()
        
        # Invalidate cache
        invalidate_cache()
        
        return success_response(message=f"successful {affected} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch updating models: {str(e)}")
        return error_response(message=f"failed: {str(e)}", status_code=500)


@router.post("/models/batch-delete")
def batch_delete_models(
    model_ids: List[int] = Body(..., embed=True),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ (Admin only)."""
    if not model_ids:
        return error_response(message="Model ID list", status_code=400)

    try:
        models = db.query(GenerationModel).filter(
            GenerationModel.id.in_(model_ids)
        ).all()
        for m in models:
            delete_generate_page_for_model(db, m.work_type, m.model_key)
        affected = db.query(GenerationModel).filter(
            GenerationModel.id.in_(model_ids)
        ).delete(synchronize_session=False)
        db.commit()

        # Invalidate cache
        invalidate_cache()

        return success_response(message=f"successful {affected} ")
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch deleting models: {str(e)}")
        return error_response(message=f"failed: {str(e)}", status_code=500)
