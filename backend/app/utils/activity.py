"""
User activity recording for DAU tracking.
Records first activity per user per day ().
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytz

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def record_user_activity(user_id: int, db: "Session") -> None:
    """
    。。
     heartbeat ；。
    activity_date ，「」「」。
    """
    now_utc = datetime.now(timezone.utc)
    activity_date = now_utc.date()

    from ..models.user_activity_log import UserActivityLog

    exists = (
        db.query(UserActivityLog)
        .filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.activity_date == activity_date,
        )
        .first()
    )
    if exists:
        return
    log = UserActivityLog(user_id=user_id, activity_date=activity_date)
    db.add(log)
    # commit, (login/heartbeat) commit
