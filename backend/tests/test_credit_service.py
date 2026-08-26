import unittest
from unittest.mock import MagicMock

from app.models.credit_record import CreditType
from app.services.credit_service import (
    InsufficientCreditsError,
    add_credits,
    consume_credits,
)


class CreditServiceTests(unittest.TestCase):
    def test_consume_credits_uses_conditional_update_and_records_negative_amount(self):
        db = MagicMock()
        updated = MagicMock()
        updated.scalar_one_or_none.return_value = 50
        db.execute.return_value = updated

        balance = consume_credits(
            db,
            user_id=7,
            amount=30,
            description="Generate image",
            work_id=99,
        )

        self.assertEqual(balance, 50)
        record = db.add.call_args.args[0]
        self.assertEqual(record.user_id, 7)
        self.assertEqual(record.amount, -30)
        self.assertEqual(record.type, CreditType.CONSUME)
        self.assertEqual(record.work_id, 99)
        self.assertEqual(db.flush.call_count, 1)
        db.execute.assert_called_once()

    def test_consume_credits_rejects_insufficient_balance_without_writes(self):
        db = MagicMock()
        updated = MagicMock()
        updated.scalar_one_or_none.return_value = None
        selected = MagicMock()
        selected.scalar_one_or_none.return_value = 10
        db.execute.side_effect = [updated, selected]

        with self.assertRaisesRegex(InsufficientCreditsError, "Required: 20"):
            consume_credits(db, 7, 20, "Generate video")

        db.add.assert_not_called()
        self.assertEqual(db.execute.call_count, 2)

    def test_add_credits_records_ledger_and_returns_persisted_balance(self):
        db = MagicMock()
        updated = MagicMock()
        selected = MagicMock()
        selected.scalar.return_value = 125
        db.execute.side_effect = [updated, selected]

        balance = add_credits(
            db,
            user_id=7,
            amount=25,
            credit_type=CreditType.RECHARGE,
            description="Purchased 25 credits",
            order_id=12,
        )

        self.assertEqual(balance, 125)
        record = db.add.call_args.args[0]
        self.assertEqual(record.amount, 25)
        self.assertEqual(record.type, CreditType.RECHARGE)
        self.assertEqual(record.order_id, 12)
        self.assertEqual(db.flush.call_count, 2)
        self.assertEqual(db.execute.call_count, 2)


if __name__ == "__main__":
    unittest.main()
