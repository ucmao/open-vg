"""Distributed fixed-window rate limiting helpers.

Production uses Redis so limits are shared by every API process. Development
can fall back to a small in-memory limiter to keep local setup convenient.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import ipaddress
import os
import threading
import time
from typing import Dict, Optional, Tuple

from fastapi import HTTPException, Request, status

from .logger import logger
from .redis_cache import build_key, get_redis


_FIXED_WINDOW_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


@dataclass
class _MemoryWindow:
    count: int
    expires_at: float


_memory_windows: Dict[str, _MemoryWindow] = {}
_memory_lock = threading.Lock()


def env_limit(name: str, default: int) -> int:
    """Read a non-negative integer rate-limit setting."""
    try:
        return max(0, int(os.getenv(name, str(default))))
    except ValueError:
        logger.warning("Invalid %s value; using %s", name, default)
        return default


def get_client_ip(request: Request) -> str:
    """Return the direct peer IP, or a validated proxy IP when explicitly trusted."""
    direct_ip = request.client.host if request.client else "unknown"
    if os.getenv("TRUST_PROXY_HEADERS", "false").lower() not in {"1", "true", "yes", "on"}:
        return direct_ip

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        try:
            return str(ipaddress.ip_address(real_ip.strip()))
        except ValueError:
            pass

    candidate = request.headers.get("cf-connecting-ip")
    if not candidate:
        forwarded = request.headers.get("x-forwarded-for", "")
        candidate = forwarded.split(",")[-1].strip() if forwarded else ""
    if not candidate:
        return direct_ip
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return direct_ip


def _identity_digest(identity: str) -> str:
    return hashlib.sha256(identity.strip().lower().encode("utf-8")).hexdigest()[:32]


def _memory_increment(key: str, window_seconds: int) -> Tuple[int, int]:
    now = time.time()
    with _memory_lock:
        entry = _memory_windows.get(key)
        if entry is None or entry.expires_at <= now:
            entry = _MemoryWindow(count=0, expires_at=now + window_seconds)
            _memory_windows[key] = entry
        entry.count += 1
        retry_after = max(1, int(entry.expires_at - now))

        # Prevent an unbounded development-process cache.
        if len(_memory_windows) > 10_000:
            expired = [item_key for item_key, item in _memory_windows.items() if item.expires_at <= now]
            for item_key in expired:
                _memory_windows.pop(item_key, None)
        return entry.count, retry_after


def enforce_rate_limit(
    request: Request,
    scope: str,
    limit: int,
    window_seconds: int,
    *,
    identity: Optional[str] = None,
) -> None:
    """Enforce a fixed-window limit for an IP, account, email, or user ID.

    A limit of zero disables that particular rule. Identity values are hashed
    before becoming Redis keys so email addresses are not stored in plaintext.
    """
    if limit <= 0:
        return

    raw_identity = identity or f"ip:{get_client_ip(request)}"
    key = build_key(f"rate-limit:{scope}:{_identity_digest(raw_identity)}")
    redis_client = get_redis()

    if redis_client is not None:
        try:
            count, retry_after = redis_client.eval(
                _FIXED_WINDOW_SCRIPT,
                1,
                key,
                max(1, window_seconds),
            )
            count = int(count)
            retry_after = max(1, int(retry_after))
        except Exception as exc:
            logger.error("Redis rate limiter failed for scope=%s: %s", scope, exc)
            if os.getenv("ENVIRONMENT", "development").strip().lower() == "production":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Request protection service is temporarily unavailable",
                ) from exc
            count, retry_after = _memory_increment(key, window_seconds)
    else:
        if os.getenv("ENVIRONMENT", "development").strip().lower() == "production":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Request protection service is not configured",
            )
        count, retry_after = _memory_increment(key, window_seconds)

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )
