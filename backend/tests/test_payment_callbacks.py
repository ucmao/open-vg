import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi import BackgroundTasks

from app.models.payment_order import PaymentOrder, PaymentStatus
from app.models.user import User
from app.routes.payment import _complete_payment_order_and_notify
from app.routes.webhook import _complete_stripe_checkout_session


def make_order(**overrides):
    values = {
        "id": 21,
        "user_id": 7,
        "amount_usd": Decimal("9.99"),
        "credits": 100,
        "extra_credits_percent": Decimal("10"),
        "payment_provider": "stripe",
        "status": PaymentStatus.PENDING,
    }
    values.update(overrides)
    return PaymentOrder(**values)


def make_user():
    return User(id=7, email="buyer@example.test", nickname="Buyer", handle="buyer_7")


class PaymentCompletionTests(unittest.TestCase):
    @patch("app.routes.payment.send_recharge_success_email")
    @patch("app.routes.payment.log_payment")
    @patch("app.routes.payment.credit_service_add_credits")
    def test_completion_adds_bonus_once_and_queues_email(
        self, add_credits, log_payment, send_email
    ):
        db = MagicMock()
        order = make_order()
        user = make_user()
        db.query.return_value.filter.return_value.with_for_update.return_value.populate_existing.return_value.first.return_value = order
        background_tasks = BackgroundTasks()

        _complete_payment_order_and_notify(db, order, user, background_tasks)

        add_credits.assert_called_once()
        args = add_credits.call_args.args
        self.assertEqual(args[1:3], (7, 110))
        self.assertEqual(add_credits.call_args.kwargs["order_id"], 21)
        self.assertEqual(order.status, PaymentStatus.COMPLETED)
        self.assertIsNotNone(order.completed_at)
        db.commit.assert_called_once()
        log_payment.assert_called_once_with(7, 9.99, 110, "completed")
        self.assertEqual(len(background_tasks.tasks), 1)
        self.assertIs(background_tasks.tasks[0].func, send_email)

    @patch("app.routes.payment.credit_service_add_credits")
    def test_completion_is_idempotent_for_completed_order(self, add_credits):
        db = MagicMock()
        order = make_order(status=PaymentStatus.COMPLETED)
        db.query.return_value.filter.return_value.with_for_update.return_value.populate_existing.return_value.first.return_value = order

        _complete_payment_order_and_notify(db, order, make_user(), BackgroundTasks())

        add_credits.assert_not_called()
        db.commit.assert_not_called()


class StripeWebhookTests(unittest.TestCase):
    def test_unpaid_session_is_ignored_without_database_access(self):
        db = MagicMock()

        result = _complete_stripe_checkout_session(
            db,
            {"id": "cs_unpaid", "payment_status": "unpaid"},
            BackgroundTasks(),
        )

        self.assertIsNone(result)
        db.query.assert_not_called()

    @patch("app.routes.payment._complete_payment_order_and_notify")
    def test_paid_session_maps_order_and_records_provider_ids(self, complete):
        db = MagicMock()
        order = make_order()
        user = make_user()
        order_query = MagicMock()
        order_query.filter.return_value.first.return_value = order
        user_query = MagicMock()
        user_query.filter.return_value.first.return_value = user
        db.query.side_effect = [order_query, user_query]
        tasks = BackgroundTasks()

        result = _complete_stripe_checkout_session(
            db,
            {
                "id": "cs_paid",
                "payment_status": "paid",
                "client_reference_id": "21",
                "payment_intent": "pi_paid",
            },
            tasks,
        )

        self.assertIs(result, order)
        self.assertEqual(order.stripe_session_id, "cs_paid")
        self.assertEqual(order.stripe_payment_intent_id, "pi_paid")
        db.flush.assert_called_once()
        complete.assert_called_once_with(db, order, user, tasks)


if __name__ == "__main__":
    unittest.main()
