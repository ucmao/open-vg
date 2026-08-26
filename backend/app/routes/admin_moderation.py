"""
Admin routes for NSFW moderation system.
"""
from fastapi import APIRouter, Depends, Query, status, Body, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func, cast
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
from typing import Optional, List
from pydantic import BaseModel, Field

from ..models.base import get_db
from ..models.admin import Admin
from ..models.work import Work, WorkStatus
from ..models.user import User
from ..models.moderation import (
    ModerationLog, 
    Lexicon, 
    ModerationType, 
    ModerationAction,
    NSFWStatus,
    LexiconCategory,
    LexiconSeverity,
    Report,
    ReportStatus,
    ReportType
)
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..services.moderation import get_moderation_service

router = APIRouter()


# ==================== Pydantic Schemas ====================

class NSFWApproveRequest(BaseModel):
    """NSFW"""
    pass


class NSFWRejectRequest(BaseModel):
    """NSFW"""
    reason: Optional[str] = Field(None, max_length=500, description="")


class CreateLexiconRequest(BaseModel):
    """Keywords"""
    word: str = Field(..., min_length=1, max_length=200, description="Keywords")
    category: str = Field(..., description="Category: violence, pornography, illegal, other")
    severity: str = Field("medium", description="Severity: low, medium, high")
    enabled: bool = Field(True, description="Is enabled")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes")


class UpdateLexiconRequest(BaseModel):
    """Keywords"""
    category: Optional[str] = Field(None, description="Category")
    severity: Optional[str] = Field(None, description="Severity")
    enabled: Optional[bool] = Field(None, description="Is enabled")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes")


# ==================== NSFW Moderation Routes ====================

@router.get("/moderation/nsfw/pending")
def get_pending_nsfw_works(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None, description="NSFW: violence, pornography, illegal"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    NSFW
    """
    try:
        #
        query = db.query(Work).filter(
            Work.nsfw_status == NSFWStatus.PENDING.value,
            Work.deleted_at == None  #
        )
        
        #
        if tag:
            # JSONB(PostgreSQL)- JSON
            # cast JSONB @> , SQLAlchemy
            query = query.filter(
                cast(Work.nsfw_tags, JSONB).op("@>")(cast([tag], JSONB))
            )
        
        #
        total = query.count()
        
        #
        works = query.order_by(
            Work.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Batch prefetch auxiliary data to avoid N+1 queries
        from ..models.work import batch_prefetch_work_data
        prefetched = batch_prefetch_work_data(works, db, None)
        
        items = [
            work.to_dict(
                include_user=True, 
                include_prompt=True,
                prefetched_counts=prefetched['counts'],
                prefetched_likes=prefetched['liked_work_ids'],
                prefetched_follows=prefetched['following_user_ids']
            ) for work in works
        ]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Pending NSFW works retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting pending NSFW works: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/moderation/nsfw/{work_id}/approve")
def approve_nsfw_work(
    work_id: int,
    request: NSFWApproveRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    NSFW
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if work.nsfw_status != NSFWStatus.PENDING.value:
            return error_response(
                message="Work is not pending NSFW review",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Status
        work.nsfw_status = NSFWStatus.APPROVED.value
        
        #
        log = ModerationLog(
            work_id=work_id,
            moderation_type=ModerationType.NSFW,
            action_type=ModerationAction.MANUAL_APPROVED,
            moderator_id=current_admin.id,
            reason="Manually approved by admin"
        )
        db.add(log)
        
        db.commit()
        
        # 🔔
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        #
        work_url = None
        if work.url_slug:
            work_url = f"/prompt/{work.url_slug}"
        elif work.short_code:
            work_url = f"/prompt/{work.short_code}"
        elif work.prompt_id:
            work_url = f"/prompt/{work.prompt_id}"
        
        work_title = work.share_name or work.title or 'Untitled'
        create_notification(
            db=db,
            user_id=work.user_id,
            type=NotificationType.NSFW_APPROVED,
            title="Work Approved ✅",
            content=f"Your work '{work_title}' has passed NSFW content moderation and is now visible to the public.",
            link_url=work_url
        )
        
        logger.info(f"Admin {current_admin.id} approved NSFW for work {work_id}")
        
        return success_response(
            data={"work_id": work_id, "nsfw_status": work.nsfw_status},
            message="Work NSFW approved successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving NSFW work: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/moderation/nsfw/{work_id}/reject")
def reject_nsfw_work(
    work_id: int,
    request: NSFWRejectRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    NSFW（）
    """
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if work.nsfw_status != NSFWStatus.PENDING.value:
            return error_response(
                message="Work is not pending NSFW review",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        reject_reason = request.reason or "Rejected by admin"
        from ..utils.validation import validate_reason_english
        valid, err = validate_reason_english(reject_reason)
        if not valid:
            return error_response(message=err or "Invalid reason", status_code=400)
        
        # Status
        work.nsfw_status = NSFWStatus.BLOCKED.value
        
        #
        log = ModerationLog(
            work_id=work_id,
            moderation_type=ModerationType.NSFW,
            action_type=ModerationAction.MANUAL_REJECTED,
            moderator_id=current_admin.id,
            nsfw_tags=work.nsfw_tags,
            reason=reject_reason
        )
        db.add(log)
        
        db.commit()
        
        # 🔔 Send notification to user
        from ..utils.notification import create_notification
        from ..models.notification import NotificationType
        
        # Build notification content in English
        tags_label = ""
        if work.nsfw_tags:
            tag_labels = {
                "VIOLENCE": "violence",
                "PORNOGRAPHY": "pornography",
                "ILLEGAL": "illegal activity",
                "OTHER": "other"
            }
            tags_list = [tag_labels.get(tag, tag.lower()) for tag in work.nsfw_tags]
            tags_label = ", detected tags: " + ", ".join(tags_list)
        
        work_title = work.share_name or work.title or 'Untitled'
        content = f"Your work '{work_title}' has been blocked due to content policy violation."
        if tags_label:
            content += tags_label
        if reject_reason and reject_reason != "Rejected by admin":
            content += f"\nReason: {reject_reason}"
        content += "\nThis work will not be publicly displayed."
        
        create_notification(
            db=db,
            user_id=work.user_id,
            type=NotificationType.NSFW_BLOCKED,
            title="Work Blocked ⚠️",
            content=content,
            link_url=None  # Blocked works don't provide links
        )
        
        logger.info(f"Admin {current_admin.id} rejected NSFW for work {work_id}")
        
        return success_response(
            data={"work_id": work_id, "nsfw_status": work.nsfw_status},
            message="Work NSFW rejected successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error rejecting NSFW work: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Moderation Logs Routes ====================

@router.get("/moderation/logs")
def get_moderation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    moderation_type: Optional[str] = Query(None, description=": nsfw, share_review"),
    action_type: Optional[str] = Query(None, description=": auto_blocked, manual_flagged, etc."),
    work_id: Optional[int] = Query(None, description="ID"),
    moderator_id: Optional[int] = Query(None, description="ID"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """

    """
    try:
        query = db.query(ModerationLog)
        
        #
        if moderation_type:
            query = query.filter(ModerationLog.moderation_type == moderation_type)
        
        if action_type:
            query = query.filter(ModerationLog.action_type == action_type)
        
        if work_id:
            query = query.filter(ModerationLog.work_id == work_id)
        
        if moderator_id:
            query = query.filter(ModerationLog.moderator_id == moderator_id)
        
        #
        total = query.count()
        
        logs = query.order_by(
            desc(ModerationLog.created_at)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [log.to_dict(include_work=True, include_moderator=True) for log in logs]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Moderation logs retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting moderation logs: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Lexicon Management Routes ====================

@router.get("/moderation/lexicons")
def get_lexicons(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    category: Optional[str] = Query(None, description="Category"),
    severity: Optional[str] = Query(None, description="Severity"),
    enabled: Optional[bool] = Query(None, description="EnableStatus"),
    search: Optional[str] = Query(None, description="Keywords"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Keywords
    """
    try:
        query = db.query(Lexicon)
        
        #
        if category:
            query = query.filter(Lexicon.category == category)
        
        if severity:
            query = query.filter(Lexicon.severity == severity)
        
        if enabled is not None:
            query = query.filter(Lexicon.enabled == enabled)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(Lexicon.word.ilike(search_term))
        
        #
        total = query.count()
        
        #
        lexicons = query.order_by(
            desc(Lexicon.created_at)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [lex.to_dict() for lex in lexicons]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Lexicons retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting lexicons: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _parse_period_to_utc_range(period: Optional[str]) -> Optional[tuple[datetime, datetime]]:
    """ period  (start_utc, end_utc)，None 。"""
    if not period or period == "all":
        return None
    now = datetime.now(timezone.utc)
    start = end = now
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "yesterday":
        start = (now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1))
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "last7":
        start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "last30":
        start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return None
    return (start, end)


def _collect_log_files(logs_dir: Path) -> list[Path]:
    """
    ：app.log + app.log.1, app.log.2, ...（）
     app.log, app.log.1, app.log.2 ... 。
    """
    result: list[Path] = []
    main_log = logs_dir / "app.log"
    if main_log.exists():
        result.append(main_log)
    n = 1
    while True:
        rotated = logs_dir / f"app.log.{n}"
        if not rotated.exists():
            break
        result.append(rotated)
        n += 1
    return result


def _analyze_lexicon_hits_from_log(
    logs_dir: Path, time_range: Optional[tuple[datetime, datetime]] = None
) -> dict:
    """
     event="lexicon_hit"  JSON ，。
    ： app.log, app.log.1, app.log.2, ...
    time_range: (start_utc, end_utc)  None 。
    """
    total = 0
    by_outcome: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    user_counts: dict[int, int] = {}  # user_id -> count
    word_counts: dict[str, int] = {}  # word -> count

    log_files = _collect_log_files(logs_dir)
    if not log_files:
        return {
            "total": 0,
            "by_outcome": {},
            "by_severity": {},
            "by_category": {},
            "top_by_user": [],
            "top_by_word": [],
            "error": "Log file not found",
        }

    for log_path in log_files:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or '"lexicon_hit"' not in line:
                    continue
                try:
                    #  JSON
                    start = line.find("{")
                    if start < 0:
                        continue
                    obj = json.loads(line[start:])
                    if obj.get("event") != "lexicon_hit":
                        continue

                    if time_range:
                        ts_str = obj.get("ts")
                        if ts_str:
                            try:
                                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                                if not time_range[0] <= ts <= time_range[1]:
                                    continue
                            except (ValueError, TypeError):
                                continue
                        else:
                            continue

                    total += 1

                    outcome = obj.get("outcome") or "unknown"
                    by_outcome[outcome] = by_outcome.get(outcome, 0) + 1

                    severity = obj.get("severity") or "unknown"
                    by_severity[severity] = by_severity.get(severity, 0) + 1

                    category = obj.get("category") or "unknown"
                    by_category[category] = by_category.get(category, 0) + 1

                    user_id = obj.get("user_id")
                    if user_id is not None:
                        user_counts[user_id] = user_counts.get(user_id, 0) + 1
                    word = obj.get("word") or ""
                    word_counts[word] = word_counts.get(word, 0) + 1
                except (json.JSONDecodeError, KeyError):
                    continue

    top_by_user = sorted(user_counts.items(), key=lambda x: -x[1])[:20]
    top_by_word = sorted(word_counts.items(), key=lambda x: -x[1])[:20]

    return {
        "total": total,
        "by_outcome": by_outcome,
        "by_severity": by_severity,
        "by_category": by_category,
        "top_by_user": [{"user_id": uid, "count": c} for uid, c in top_by_user],
        "top_by_word": [{"word": w, "count": c} for w, c in top_by_word],
        "error": None,
    }


@router.get("/moderation/lexicons/analyze-hits")
def analyze_lexicon_hits(
    period: Optional[str] = Query(
        "last7",
        description=": today, yesterday, last7, last30, all",
    ),
    current_admin: Admin = Depends(get_current_admin),
):
    """
     lexicon_hit ，。
    """
    try:
        backend_root = Path(__file__).resolve().parent.parent.parent
        logs_dir = backend_root / "logs"
        time_range = _parse_period_to_utc_range(period)
        data = _analyze_lexicon_hits_from_log(logs_dir, time_range)
        return success_response(data=data, message="Lexicon hit analysis completed")
    except Exception as e:
        logger.error(f"Error analyzing lexicon hits: {str(e)}", exc_info=True)
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/moderation/lexicons")
def create_lexicon(
    request: CreateLexiconRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Keywords
    """
    try:
        # Category
        try:
            category_enum = LexiconCategory(request.category.upper())
        except ValueError:
            return error_response(
                message=f"Invalid category. Must be one of: {[c.value for c in LexiconCategory]}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Severity
        try:
            severity_enum = LexiconSeverity(request.severity.upper())
        except ValueError:
            return error_response(
                message=f"Invalid severity. Must be one of: {[s.value for s in LexiconSeverity]}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # already exists()
        existing = db.query(Lexicon).filter(
            func.lower(Lexicon.word) == request.word.lower()
        ).first()
        
        if existing:
            return error_response(
                message="Lexicon word already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Keywords
        lexicon = Lexicon(
            word=request.word.lower(),  #
            category=category_enum,
            severity=severity_enum,
            enabled=request.enabled,
            notes=request.notes
        )
        
        db.add(lexicon)
        db.commit()
        db.refresh(lexicon)
        
        #
        moderation_service = get_moderation_service(db)
        moderation_service.invalidate_cache()
        
        logger.info(f"Admin {current_admin.id} created lexicon: {lexicon.word}")
        
        return success_response(
            data=lexicon.to_dict(),
            message="Lexicon created successfully",
            status_code=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating lexicon: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/moderation/lexicons/{lexicon_id}")
def update_lexicon(
    lexicon_id: int,
    request: UpdateLexiconRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Keywords
    """
    try:
        lexicon = db.query(Lexicon).filter(Lexicon.id == lexicon_id).first()
        
        if not lexicon:
            return error_response(
                message="Lexicon not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        #
        if request.category is not None:
            try:
                lexicon.category = LexiconCategory(request.category.upper())
            except ValueError:
                return error_response(
                    message=f"Invalid category. Must be one of: {[c.value for c in LexiconCategory]}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        if request.severity is not None:
            try:
                lexicon.severity = LexiconSeverity(request.severity.upper())
            except ValueError:
                return error_response(
                    message=f"Invalid severity. Must be one of: {[s.value for s in LexiconSeverity]}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        if request.enabled is not None:
            lexicon.enabled = request.enabled
        
        if request.notes is not None:
            lexicon.notes = request.notes
        
        db.commit()
        db.refresh(lexicon)
        
        #
        moderation_service = get_moderation_service(db)
        moderation_service.invalidate_cache()
        
        logger.info(f"Admin {current_admin.id} updated lexicon {lexicon_id}")
        
        return success_response(
            data=lexicon.to_dict(),
            message="Lexicon updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating lexicon: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/moderation/lexicons/{lexicon_id}")
def delete_lexicon(
    lexicon_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Keywords
    """
    try:
        lexicon = db.query(Lexicon).filter(Lexicon.id == lexicon_id).first()
        
        if not lexicon:
            return error_response(
                message="Lexicon not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        db.delete(lexicon)
        db.commit()
        
        #
        moderation_service = get_moderation_service(db)
        moderation_service.invalidate_cache()
        
        logger.info(f"Admin {current_admin.id} deleted lexicon {lexicon_id}")
        
        return success_response(
            message="Lexicon deleted successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting lexicon: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/moderation/lexicons/batch-import")
def batch_import_lexicons(
    words: List[CreateLexiconRequest] = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Keywords
    """
    try:
        created_count = 0
        skipped_count = 0
        errors = []
        
        for word_request in words:
            try:
                # already exists
                existing = db.query(Lexicon).filter(
                    func.lower(Lexicon.word) == word_request.word.lower()
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # CategorySeverity
                try:
                    category_enum = LexiconCategory(word_request.category.upper())
                    severity_enum = LexiconSeverity(word_request.severity.upper())
                except ValueError as e:
                    errors.append(f"Word '{word_request.word}': {str(e)}")
                    continue
                
                # Keywords
                lexicon = Lexicon(
                    word=word_request.word.lower(),
                    category=category_enum,
                    severity=severity_enum,
                    enabled=word_request.enabled,
                    notes=word_request.notes
                )
                
                db.add(lexicon)
                created_count += 1
                
            except Exception as e:
                errors.append(f"Word '{word_request.word}': {str(e)}")
                continue
        
        db.commit()
        
        #
        moderation_service = get_moderation_service(db)
        moderation_service.invalidate_cache()
        
        logger.info(f"Admin {current_admin.id} batch imported {created_count} lexicons")
        
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
        logger.error(f"Error batch importing lexicons: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class BatchUpdateLexiconRequest(BaseModel):
    """Keywords"""
    lexicon_ids: Optional[List[int]] = Field(None, description="KeywordsID（filters）")
    select_all: Optional[bool] = Field(False, description="")
    filters: Optional[dict] = Field(None, description="（select_alltrue）")
    category: Optional[str] = Field(None, description="Category")
    severity: Optional[str] = Field(None, description="Severity")
    enabled: Optional[bool] = Field(None, description="Is enabled")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes")


@router.post("/moderation/lexicons/batch-update")
def batch_update_lexicons(
    request: BatchUpdateLexiconRequest = Body(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Keywords
    """
    try:
        #
        update_data = {}
        if request.category is not None:
            try:
                update_data['category'] = LexiconCategory(request.category.upper())
            except ValueError:
                return error_response(
                    message=f"Invalid category. Must be one of: {[c.value for c in LexiconCategory]}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        if request.severity is not None:
            try:
                update_data['severity'] = LexiconSeverity(request.severity.upper())
            except ValueError:
                return error_response(
                    message=f"Invalid severity. Must be one of: {[s.value for s in LexiconSeverity]}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        if request.enabled is not None:
            update_data['enabled'] = request.enabled
        
        if request.notes is not None:
            update_data['notes'] = request.notes
        
        if not update_data:
            return error_response(
                message="No fields to update",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        #
        if request.select_all and request.filters:
            #
            query = db.query(Lexicon)
            
            filters = request.filters
            if filters.get('category'):
                query = query.filter(Lexicon.category == LexiconCategory(filters['category'].upper()))
            if filters.get('severity'):
                query = query.filter(Lexicon.severity == LexiconSeverity(filters['severity'].upper()))
            if 'enabled' in filters and filters['enabled'] is not None:
                query = query.filter(Lexicon.enabled == filters['enabled'])
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(Lexicon.word.ilike(search_term))
            
            #
            affected_count = query.update(update_data, synchronize_session=False)
        else:
            # ID
            if not request.lexicon_ids:
                return error_response(
                    message="Either lexicon_ids or select_all with filters must be provided",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            affected_count = db.query(Lexicon).filter(
                Lexicon.id.in_(request.lexicon_ids)
            ).update(update_data, synchronize_session=False)
        
        db.commit()
        
        #
        moderation_service = get_moderation_service(db)
        moderation_service.invalidate_cache()
        
        logger.info(f"Admin {current_admin.id} batch updated {affected_count} lexicons")
        
        return success_response(
            data={"affected_count": affected_count},
            message=f"Batch update completed: {affected_count} lexicons updated"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch updating lexicons: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Report Management Routes ====================

class ResolveReportRequest(BaseModel):
    pass


class DismissReportRequest(BaseModel):
    """Dismiss report request"""
    reason: Optional[str] = Field(None, max_length=500, description="Dismissal reason")


class BanReportRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500, description="")


@router.get("/moderation/reports")
def get_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status", description="Status: pending, resolved, dismissed"),
    keyword: Optional[str] = Query(None, description="：ID、Title/、、"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get reports list
    """
    try:
        #
        query = db.query(Report)
        
        # Status
        if status_filter:
            try:
                status_enum = ReportStatus(status_filter)
                query = query.filter(Report.status == status_enum)
            except ValueError:
                pass
        
        # Keywords
        if keyword and keyword.strip():
            kw = keyword.strip()
            keyword_like = f"%{kw}%"
            #  outerjoin
            query = query.outerjoin(Work, Report.work_id == Work.id).outerjoin(User, Report.reporter_id == User.id)
            
            conditions = [
                Report.reason.ilike(keyword_like),
            ]
            # Work User ( outerjoin , does not exist)
            conditions.extend([
                Work.title.ilike(keyword_like),
                Work.share_name.ilike(keyword_like),
                Work.prompt.ilike(keyword_like),
                User.handle.ilike(keyword_like),
                User.nickname.ilike(keyword_like),
            ])
            if kw.isdigit():
                conditions.append(Report.work_id == int(kw))
            query = query.filter(or_(*conditions))
        
        # join, distinct)
        if keyword and keyword.strip():
            total = query.distinct().count()
        else:
            total = query.count()
        
        if keyword and keyword.strip():
            reports = query.distinct().order_by(
                desc(Report.created_at)
            ).offset((page - 1) * page_size).limit(page_size).all()
        else:
            reports = query.order_by(
                desc(Report.created_at)
            ).offset((page - 1) * page_size).limit(page_size).all()
        
        #
        work_ids = [r.work_id for r in reports]
        reporter_ids = [r.reporter_id for r in reports]
        resolver_ids = [r.resolved_by for r in reports if r.resolved_by]
        
        works = db.query(Work).filter(Work.id.in_(work_ids)).all() if work_ids else []
        reporters = db.query(User).filter(User.id.in_(reporter_ids)).all() if reporter_ids else []
        resolvers = db.query(Admin).filter(Admin.id.in_(resolver_ids)).all() if resolver_ids else []
        
        works_dict = {w.id: w for w in works}
        reporters_dict = {u.id: u for u in reporters}
        resolvers_dict = {a.id: a for a in resolvers}
        
        #
        items = []
        for report in reports:
            work = works_dict.get(report.work_id)
            reporter = reporters_dict.get(report.reporter_id)
            resolver = resolvers_dict.get(report.resolved_by) if report.resolved_by else None
            
            item = report.to_dict(include_work=False, include_reporter=False, include_resolver=False)
            
            #  work
            if work:
                item["work"] = {
                    "id": work.id,
                    "title": work.title or work.share_name,
                    "share_name": work.share_name,
                    "type": work.type if work.type else None,
                    "model_name": work.model_name,
                    "prompt": work.prompt,
                    "url_slug": work.url_slug,
                    "short_code": work.short_code,
                    "file_url": work.file_url,
                    "thumbnail_url": work.thumbnail_url,
                    "user": {
                        "id": work.user.id if work.user else None,
                        "nickname": work.user.nickname if work.user else None,
                        "handle": work.user.handle if work.user else None,
                    } if work.user else None,
                }
            
            #  reporter
            if reporter:
                item["reporter"] = {
                    "id": reporter.id,
                    "nickname": reporter.nickname,
                    "handle": reporter.handle,
                }
            
            #  resolver
            if resolver:
                item["resolver"] = {
                    "id": resolver.id,
                    "nickname": resolver.nickname,
                    "username": resolver.username,
                }
            
            items.append(item)
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Reports retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting reports: {str(e)}", exc_info=True)
        # does not exist,
        error_str = str(e).lower()
        if 'does not exist' in error_str or 'no such table' in error_str or 'relation' in error_str:
            return paginated_response(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
                message="Reports table not found. Please run database migrations."
            )
        return error_response(
            message=f"An error occurred: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/moderation/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    request: ResolveReportRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Mark report as resolved
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            return error_response(
                message="Report not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if report.status != ReportStatus.PENDING:
            return error_response(
                message="Report is already processed",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        report.status = ReportStatus.RESOLVED
        report.resolved_at = datetime.now(timezone.utc)
        report.resolved_by = current_admin.id
        
        db.commit()
        
        logger.info(f"Report {report_id} resolved by admin {current_admin.id}")
        
        return success_response(
            data=report.to_dict(include_work=True, include_reporter=True, include_resolver=True),
            message="Report resolved successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error resolving report: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/moderation/reports/{report_id}/dismiss")
def dismiss_report(
    report_id: int,
    request: DismissReportRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Dismiss report
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            return error_response(
                message="Report not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if report.status != ReportStatus.PENDING:
            return error_response(
                message="Report is already processed",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        report.status = ReportStatus.DISMISSED
        report.resolved_at = datetime.now(timezone.utc)
        report.resolved_by = current_admin.id
        report.resolution_reason = request.reason
        
        db.commit()
        
        logger.info(f"Report {report_id} dismissed by admin {current_admin.id}")
        
        return success_response(
            data=report.to_dict(include_work=True, include_reporter=True, include_resolver=True),
            message="Report dismissed successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error dismissing report: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/moderation/reports/{report_id}/ban")
def ban_work_from_report(
    report_id: int,
    request: BanReportRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Ban work based on report
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            return error_response(
                message="Report not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        work = db.query(Work).filter(Work.id == report.work_id).first()
        if not work:
            return error_response(
                message="Work not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        #
        from ..models.moderation import NSFWStatus
        work.nsfw_status = NSFWStatus.BLOCKED.value
        work.is_shared = False
        work.share_status = None
        
        # Mark report as resolved
        report.status = ReportStatus.RESOLVED
        report.resolved_at = datetime.now(timezone.utc)
        report.resolved_by = current_admin.id
        report.resolution_reason = request.reason
        
        #
        moderation_log = ModerationLog(
            work_id=work.id,
            moderation_type=ModerationType.NSFW,
            action_type=ModerationAction.MANUAL_REJECTED,
            moderator_id=current_admin.id,
            reason=f"Banned due to user report: {request.reason}"
        )
        db.add(moderation_log)
        
        db.commit()
        
        logger.info(f"Work {work.id} banned due to report {report_id} by admin {current_admin.id}")
        
        return success_response(
            data={
                "report": report.to_dict(include_work=True, include_reporter=True, include_resolver=True),
                "work_id": work.id
            },
            message="Work banned successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error banning work from report: {str(e)}", exc_info=True)
        return error_response(
            message="An error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
