"""
Credit service: add/consume credits with both credit_records (ledger) and users.total_credits updated in-app.
No database trigger is used; callers must use this service for all credit changes.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import update, select

from ..models.user import User
from ..models.credit_record import CreditRecord, CreditType


class InsufficientCreditsError(ValueError):
    """Raised when user has insufficient credits for a consume operation."""
    pass


def add_credits(
    db: Session,
    user_id: int,
    amount: int,
    credit_type: CreditType,
    description: str,
    *,
    order_id: Optional[int] = None,
    work_id: Optional[int] = None,
    expire_at: Optional[datetime] = None,
) -> int:
    """
    Add a credit record (ledger) and update users.total_credits.
    Does not commit; caller must commit.
    amount can be positive (grant) or negative (e.g. admin deduction).
    Returns the new total_credits for the user.
    """
    record = CreditRecord(
        user_id=user_id,
        amount=amount,
        type=credit_type,
        description=description,
        order_id=order_id,
        work_id=work_id,
        expire_at=expire_at,
    )
    db.add(record)
    db.flush()
    stmt = update(User).where(User.id == user_id).values(total_credits=User.total_credits + amount)
    db.execute(stmt)
    db.flush()
    new_balance = db.execute(select(User.total_credits).where(User.id == user_id)).scalar()
    return new_balance or 0


def consume_credits(
    db: Session,
    user_id: int,
    amount: int,
    description: str,
    *,
    work_id: Optional[int] = None,
) -> int:
    """
    Deduct credits: lock user row, check balance, insert consume record (negative amount), update total_credits.
    Does not commit; caller must commit.
    Raises InsufficientCreditsError if balance < amount.
    Returns the new total_credits for the user.
    """
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not user:
        raise InsufficientCreditsError("User not found")
    if user.total_credits < amount:
        raise InsufficientCreditsError(
            f"Insufficient credits. Required: {amount}, Available: {user.total_credits}"
        )
    record = CreditRecord(
        user_id=user_id,
        amount=-amount,
        type=CreditType.CONSUME,
        description=description,
        work_id=work_id,
    )
    db.add(record)
    db.flush()
    stmt = update(User).where(User.id == user_id).values(total_credits=User.total_credits - amount)
    db.execute(stmt)
    db.flush()
    return user.total_credits - amount
