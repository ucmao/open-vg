"""Reconcile paid Stripe Checkout Sessions for pending local payment orders.

Usage:
    python scripts/reconcile_stripe_payments.py --dry-run
    python scripts/reconcile_stripe_payments.py --execute
    python scripts/reconcile_stripe_payments.py --execute --order-id 120
"""
import argparse
import sys
from pathlib import Path

from fastapi import BackgroundTasks

# Add backend directory to path for imports
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import SessionLocal
from app.models.payment_order import PaymentOrder, PaymentStatus
from app.services.stripe_service import get_stripe_service
from app.routes.webhook import _complete_stripe_checkout_session


def reconcile_stripe_payments(execute: bool = False, order_id: int | None = None) -> None:
    db = SessionLocal()
    try:
        query = db.query(PaymentOrder).filter(
            PaymentOrder.payment_provider == "stripe",
            PaymentOrder.status == PaymentStatus.PENDING,
            PaymentOrder.stripe_session_id.isnot(None),
        )
        if order_id is not None:
            query = query.filter(PaymentOrder.id == order_id)

        orders = query.order_by(PaymentOrder.created_at.asc()).all()
        if not orders:
            print("No pending Stripe orders found.")
            return

        stripe_service = get_stripe_service()
        fixed_count = 0
        paid_count = 0

        for order in orders:
            session = stripe_service.retrieve_checkout_session(order.stripe_session_id)
            payment_status = session.get("payment_status")
            print(
                f"Order #{order.id}: session={order.stripe_session_id}, "
                f"payment_status={payment_status}, amount=${float(order.amount_usd):.2f}, credits={order.credits}"
            )

            if payment_status != "paid":
                continue

            paid_count += 1
            if not execute:
                print(f"  DRY RUN: would mark order #{order.id} completed and add credits.")
                continue

            _complete_stripe_checkout_session(db, session, BackgroundTasks())
            fixed_count += 1
            print(f"  Fixed order #{order.id}.")

        if execute:
            print(f"Done. Fixed {fixed_count} paid pending Stripe order(s).")
        else:
            print(f"Dry run done. {paid_count} paid pending Stripe order(s) need reconciliation.")
            print("Run again with --execute to update orders and add credits.")

    except Exception as exc:
        db.rollback()
        print(f"Error: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconcile pending Stripe payment orders.")
    parser.add_argument("--execute", action="store_true", help="Actually complete paid orders and add credits.")
    parser.add_argument("--dry-run", action="store_true", help="Only report what would be changed.")
    parser.add_argument("--order-id", type=int, default=None, help="Only reconcile a specific local order ID.")
    args = parser.parse_args()

    if not args.execute and not args.dry_run:
        parser.error("Choose --dry-run or --execute.")

    reconcile_stripe_payments(execute=args.execute, order_id=args.order_id)
