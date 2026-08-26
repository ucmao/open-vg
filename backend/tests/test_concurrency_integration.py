"""PostgreSQL and Redis concurrency integration tests.

These tests are skipped for a plain local unit-test run. CI supplies isolated
PostgreSQL and Redis services and runs Alembic before this module.
"""
from __future__ import annotations

import asyncio
import os
import threading
import time
import unittest
import uuid
from decimal import Decimal

from fastapi import BackgroundTasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

import app.models  # noqa: F401 - register every relationship mapper
from app.models.checkin import CheckIn
from app.models.credit_record import CreditRecord, CreditType
from app.models.payment_order import PaymentOrder, PaymentStatus
from app.models.user import User, UserSource
from app.routes.checkin import CHECKIN_BASE_REWARD, daily_checkin
from app.routes.payment import _complete_payment_order_and_notify
from app.services.credit_service import InsufficientCreditsError, consume_credits
from app.services.realtime import RedisRealtimeSubscriber, publish_user_event
from app.services.websocket import get_connection_manager


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "").strip()
TEST_REDIS_URL = os.getenv("REDIS_URL", "").strip()


@unittest.skipUnless(TEST_DATABASE_URL, "TEST_DATABASE_URL is not configured")
class PostgreSQLConcurrencyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool, pool_pre_ping=True)
        cls.Session = sessionmaker(bind=cls.engine, expire_on_commit=False)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        token = uuid.uuid4().hex[:10]
        with self.Session() as db:
            user = User(
                handle=f"it_{token}",
                email=f"{token}@integration.invalid",
                nickname="Concurrency Test",
                source=UserSource.IMPORT,
                total_credits=0,
                is_active=True,
                email_verified=True,
            )
            db.add(user)
            db.commit()
            self.user_id = user.id

    def tearDown(self):
        with self.Session() as db:
            db.query(User).filter(User.id == self.user_id).delete(
                synchronize_session=False
            )
            db.commit()

    def _run_concurrently(self, callbacks):
        barrier = threading.Barrier(len(callbacks))
        results = []
        guard = threading.Lock()

        def run(callback):
            try:
                value = callback(barrier)
            except Exception as exc:  # surfaced through the assertion below
                value = exc
            with guard:
                results.append(value)

        threads = [threading.Thread(target=run, args=(callback,)) for callback in callbacks]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertTrue(all(not thread.is_alive() for thread in threads), "concurrent operation hung")
        return results

    def test_credit_consumption_cannot_overdraw_under_concurrency(self):
        with self.Session() as db:
            user = db.get(User, self.user_id)
            user.total_credits = 100
            db.commit()

        def consume(barrier):
            with self.Session() as db:
                barrier.wait()
                try:
                    balance = consume_credits(db, self.user_id, 80, "Concurrent generation")
                    db.commit()
                    return balance
                except InsufficientCreditsError:
                    db.rollback()
                    return "insufficient"

        results = self._run_concurrently([consume, consume])
        self.assertCountEqual(results, [20, "insufficient"])
        with self.Session() as db:
            self.assertEqual(db.get(User, self.user_id).total_credits, 20)
            records = db.query(CreditRecord).filter(
                CreditRecord.user_id == self.user_id,
                CreditRecord.type == CreditType.CONSUME,
            ).all()
            self.assertEqual([record.amount for record in records], [-80])

    def test_payment_completion_grants_credits_exactly_once(self):
        with self.Session() as db:
            order = PaymentOrder(
                user_id=self.user_id,
                amount_usd=Decimal("9.99"),
                credits=100,
                payment_provider="stripe",
                status=PaymentStatus.PENDING,
            )
            db.add(order)
            db.commit()
            order_id = order.id

        def complete(barrier):
            with self.Session() as db:
                order = db.get(PaymentOrder, order_id)
                user = db.get(User, self.user_id)
                barrier.wait()
                _complete_payment_order_and_notify(db, order, user, BackgroundTasks())
                return "completed"

        results = self._run_concurrently([complete, complete])
        self.assertEqual(results, ["completed", "completed"])
        with self.Session() as db:
            self.assertEqual(db.get(User, self.user_id).total_credits, 100)
            self.assertEqual(db.get(PaymentOrder, order_id).status, PaymentStatus.COMPLETED)
            records = db.query(CreditRecord).filter(
                CreditRecord.user_id == self.user_id,
                CreditRecord.order_id == order_id,
                CreditRecord.type == CreditType.RECHARGE,
            ).all()
            self.assertEqual([record.amount for record in records], [100])

    def test_daily_checkin_grants_one_reward_under_concurrency(self):
        def checkin(barrier):
            with self.Session() as db:
                user = db.get(User, self.user_id)
                barrier.wait()
                return daily_checkin(current_user=user, db=db).status_code

        results = self._run_concurrently([checkin, checkin])
        self.assertCountEqual(results, [200, 400])
        with self.Session() as db:
            self.assertEqual(db.get(User, self.user_id).total_credits, CHECKIN_BASE_REWARD)
            self.assertEqual(
                db.query(CheckIn).filter(CheckIn.user_id == self.user_id).count(),
                1,
            )
            records = db.query(CreditRecord).filter(
                CreditRecord.user_id == self.user_id,
                CreditRecord.type == CreditType.GIFT,
            ).all()
            self.assertEqual([record.amount for record in records], [CHECKIN_BASE_REWARD])


class _RecordingWebSocket:
    def __init__(self):
        self.messages = []

    async def send_json(self, message):
        self.messages.append(message)


@unittest.skipUnless(TEST_REDIS_URL, "REDIS_URL is not configured")
class RedisWebSocketConcurrencyIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_publishers_reach_every_local_websocket(self):
        manager = get_connection_manager()
        user_id = int(time.time_ns() % 1_000_000_000)
        sockets = [_RecordingWebSocket(), _RecordingWebSocket()]
        manager.active_connections[user_id] = sockets
        subscriber = RedisRealtimeSubscriber()

        try:
            await subscriber.start()
            await subscriber.wait_until_ready()
            event_count = 20
            published = await asyncio.gather(*(
                asyncio.to_thread(
                    publish_user_event,
                    user_id,
                    {"type": "generation_complete", "work_id": index},
                )
                for index in range(event_count)
            ))
            self.assertTrue(all(published))

            async def all_delivered():
                deadline = asyncio.get_running_loop().time() + 5
                while asyncio.get_running_loop().time() < deadline:
                    if all(len(socket.messages) == event_count for socket in sockets):
                        return True
                    await asyncio.sleep(0.02)
                return False

            self.assertTrue(await all_delivered(), "Redis events were not fully delivered")
            for socket in sockets:
                self.assertEqual(
                    {message["work_id"] for message in socket.messages},
                    set(range(event_count)),
                )
        finally:
            await subscriber.stop()
            manager.active_connections.pop(user_id, None)


if __name__ == "__main__":
    unittest.main()
