"""
Redis cache helpers (sync).

This project uses FastAPI with both sync and async code paths.
To keep integration simple and avoid changing many call sites to async,
we use the synchronous redis-py client here.

Environment:
  - REDIS_URL=redis://localhost:6379/0
  - REDIS_PREFIX=vidgen:   (optional)
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

import redis

from .logger import logger

_redis_client: Optional[redis.Redis] = None


def _get_prefix() -> str:
    prefix = os.getenv("REDIS_PREFIX", "vidgen:")
    if prefix and not prefix.endswith(":"):
        prefix = prefix + ":"
    return prefix


def build_key(key: str) -> str:
    """Apply a global prefix to avoid key collisions."""
    if not key:
        return key
    prefix = _get_prefix()
    if not prefix:
        return key
    # Avoid double-prefixing
    return key if key.startswith(prefix) else f"{prefix}{key}"


def get_redis() -> Optional[redis.Redis]:
    """Get a singleton Redis client, or None if not configured."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    redis_url = os.getenv("REDIS_URL", "").strip()
    if not redis_url:
        return None

    try:
        _redis_client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,  # str <-> str
            socket_timeout=2,
            socket_connect_timeout=2,
            retry_on_timeout=True,
        )
        # Validate connectivity quickly; if it fails, keep None (degrade gracefully)
        _redis_client.ping()
        logger.info("Redis cache enabled")
        return _redis_client
    except Exception as e:
        _redis_client = None
        logger.warning(f"Redis cache disabled (connection failed): {e}")
        return None


def get_json(key: str) -> Optional[Any]:
    r = get_redis()
    if not r:
        return None
    try:
        raw = r.get(build_key(key))
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"Redis get_json failed for key={key}: {e}")
        return None


def set_json(key: str, value: Any, ttl_seconds: int) -> bool:
    r = get_redis()
    if not r:
        return False
    try:
        raw = json.dumps(value, ensure_ascii=False)
        r.setex(build_key(key), ttl_seconds, raw)
        return True
    except Exception as e:
        logger.warning(f"Redis set_json failed for key={key}: {e}")
        return False


def delete(key: str) -> bool:
    r = get_redis()
    if not r:
        return False
    try:
        r.delete(build_key(key))
        return True
    except Exception as e:
        logger.warning(f"Redis delete failed for key={key}: {e}")
        return False

