"""
Unified handling for marking a work as failed and refunding credits.
All generation-failure paths should go through mark_work_failed so refund is never missed.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models.work import Work, WorkStatus
from ..models.credit_record import CreditRecord, CreditType
from ..models.generation_config import get_model_cost
from ..models.notification import NotificationType
from ..services.credit_service import add_credits as credit_service_add_credits
from ..utils.notification import create_notification
from ..utils.logger import logger


def mark_work_failed(
    db: Session,
    work: Work,
    error_message: str,
    *,
    refund_description: Optional[str] = None,
) -> None:
    """
    Mark work as failed, set completed_at, and perform idempotent refund.

    Caller is responsible for db.commit() and sending WebSocket if needed.
    Refund is skipped if this work_id already has a REFUND record (idempotent).
    """
    work.status = WorkStatus.FAILED
    work.error_message = error_message
    work.completed_at = datetime.now(timezone.utc)

    # Idempotent refund: skip if already refunded for this work
    existing = (
        db.query(CreditRecord)
        .filter(
            CreditRecord.work_id == work.id,
            CreditRecord.type == CreditType.REFUND,
        )
        .first()
    )
    if existing:
        logger.info(f"Work {work.id} already has refund record, skipping duplicate refund")
        return

    try:
        model_cost = get_model_cost(work.type, work.model_key, work.params or {})
    except Exception as e:
        logger.error(f"get_model_cost failed for work {work.id}, skipping refund: {e}")
        return

    # User-facing description: short and generic (shown in credit history)
    description = refund_description or "Refund: Generation failed"
    credit_service_add_credits(
        db,
        work.user_id,
        model_cost,
        CreditType.REFUND,
        description,
        work_id=work.id,
    )
    logger.info(f"Refunded {model_cost} credits for failed work {work.id}: {description}; reason: {error_message}")


def notify_generation_failed(db: Session, user_id: int) -> None:
    """
    Create a TASK_FAILED notification so it appears in the user's Notifications dropdown.
    Call after mark_work_failed + db.commit() so the user sees the failure and can check /billing for the refund.
    """
    create_notification(
        db,
        user_id,
        NotificationType.TASK_FAILED,
        title="Generation failed",
        content="Your generation did not complete. Credits have been refunded to your account. Check Billing for details.",
        link_url="/billing",
    )
