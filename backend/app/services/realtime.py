"""Cross-process realtime event delivery through Redis Pub/Sub."""
from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Any, Optional

from ..utils.logger import logger
from ..utils.redis_cache import build_key, get_redis
from .websocket import get_connection_manager


REALTIME_CHANNEL = build_key(os.getenv("REALTIME_REDIS_CHANNEL", "realtime:user-events"))
_PROCESS_ID = uuid.uuid4().hex


def _event_envelope(user_id: int, message: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": uuid.uuid4().hex,
        "source": _PROCESS_ID,
        "user_id": int(user_id),
        "message": message,
    }


def _dispatch_local_fallback(user_id: int, message: dict[str, Any]) -> None:
    """Best-effort local delivery for development without Redis."""
    manager = get_connection_manager()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(manager.send_message(user_id, message))
    else:
        loop.create_task(manager.send_message(user_id, message))


def publish_user_event(user_id: int, message: dict[str, Any]) -> bool:
    """Publish an event for delivery by every API instance.

    Returns True when Redis accepted the event. Development falls back to the
    current process; production logs an error because polling remains the
    durable source of truth for job state.
    """
    envelope = _event_envelope(user_id, message)
    redis_client = get_redis()
    if redis_client is not None:
        try:
            redis_client.publish(
                REALTIME_CHANNEL,
                json.dumps(envelope, ensure_ascii=False, separators=(",", ":")),
            )
            return True
        except Exception as exc:
            logger.error("Failed to publish realtime event for user %s: %s", user_id, exc)

    if os.getenv("ENVIRONMENT", "development").strip().lower() != "production":
        _dispatch_local_fallback(user_id, message)
    return False


def _parse_event(raw: Any) -> Optional[tuple[int, dict[str, Any]]]:
    try:
        envelope = json.loads(raw)
        user_id = int(envelope["user_id"])
        message = envelope["message"]
        if not isinstance(message, dict):
            return None
        return user_id, message
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


class RedisRealtimeSubscriber:
    """Background subscriber owned by one FastAPI process."""

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task[None]] = None
        self._stopping = asyncio.Event()
        self._ready = asyncio.Event()

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stopping.clear()
        self._ready.clear()
        self._task = asyncio.create_task(self._run(), name="redis-realtime-subscriber")

    async def wait_until_ready(self, timeout: float = 5.0) -> None:
        """Wait until Redis confirms the channel subscription."""
        await asyncio.wait_for(self._ready.wait(), timeout=timeout)

    async def stop(self) -> None:
        self._stopping.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self._ready.clear()

    async def _run(self) -> None:
        while not self._stopping.is_set():
            redis_client = get_redis()
            if redis_client is None:
                await asyncio.sleep(2)
                continue

            pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
            try:
                await asyncio.to_thread(pubsub.subscribe, REALTIME_CHANNEL)
                self._ready.set()
                logger.info("Realtime subscriber listening on Redis channel %s", REALTIME_CHANNEL)
                while not self._stopping.is_set():
                    item = await asyncio.to_thread(
                        pubsub.get_message,
                        ignore_subscribe_messages=True,
                        timeout=1.0,
                    )
                    if not item or item.get("type") != "message":
                        continue
                    parsed = _parse_event(item.get("data"))
                    if parsed is None:
                        logger.warning("Discarded malformed realtime Redis event")
                        continue
                    user_id, message = parsed
                    await get_connection_manager().send_message(user_id, message)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("Realtime Redis subscriber failed: %s", exc)
                await asyncio.sleep(2)
            finally:
                self._ready.clear()
                try:
                    await asyncio.to_thread(pubsub.close)
                except Exception:
                    pass


realtime_subscriber = RedisRealtimeSubscriber()
