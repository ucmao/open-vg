import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.models.user import UserSource
from app.routes import webhook as webhook_routes
from app.routes.auth import _should_return_verification_codes
from app.routes.webhook import _websocket_origin_allowed, _websocket_token
from scripts import create_first_admin
from app.utils import rate_limit
from app.utils.auth import create_access_token, get_current_user


def make_request(ip: str = "203.0.113.10") -> Request:
    return Request({"type": "http", "client": (ip, 1234), "headers": []})


def make_websocket(headers: list[tuple[bytes, bytes]]) -> WebSocket:
    return WebSocket(
        {
            "type": "websocket",
            "path": "/api/webhook/ws",
            "headers": headers,
            "client": ("203.0.113.10", 1234),
            "scheme": "ws",
            "query_string": b"",
        },
        receive=MagicMock(),
        send=MagicMock(),
    )


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        rate_limit._memory_windows.clear()

    @patch("app.utils.rate_limit.get_redis", return_value=None)
    def test_development_fallback_enforces_limit(self, _get_redis):
        request = make_request()
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            rate_limit.enforce_rate_limit(request, "test", 2, 60)
            rate_limit.enforce_rate_limit(request, "test", 2, 60)
            with self.assertRaises(HTTPException) as raised:
                rate_limit.enforce_rate_limit(request, "test", 2, 60)

        self.assertEqual(raised.exception.status_code, 429)
        self.assertIn("Retry-After", raised.exception.headers)

    @patch("app.utils.rate_limit.get_redis", return_value=None)
    def test_production_requires_redis(self, _get_redis):
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with self.assertRaises(HTTPException) as raised:
                rate_limit.enforce_rate_limit(make_request(), "test", 1, 60)
        self.assertEqual(raised.exception.status_code, 503)


class VerificationCodeSafetyTests(unittest.TestCase):
    def test_code_response_requires_explicit_non_production_opt_in(self):
        with patch.dict(
            os.environ,
            {"ENVIRONMENT": "development", "RETURN_VERIFICATION_CODES": "true"},
        ):
            self.assertTrue(_should_return_verification_codes())

        with patch.dict(
            os.environ,
            {"ENVIRONMENT": "production", "RETURN_VERIFICATION_CODES": "true"},
        ):
            self.assertFalse(_should_return_verification_codes())


class InitialAdminSafetyTests(unittest.TestCase):
    def test_production_rejects_existing_default_admin_password(self):
        existing_admin = MagicMock(
            username="admin",
            email="admin@example.com",
            password_hash=create_first_admin.hash_password("admin123"),
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [existing_admin]
        db.query.return_value.filter.return_value.first.return_value = existing_admin
        with (
            patch.object(create_first_admin, "SessionLocal", return_value=db),
            patch("builtins.print"),
            patch.dict(
                os.environ,
                {
                    "ENVIRONMENT": "production",
                    "INITIAL_ADMIN_EMAIL": "admin@example.com",
                    "INITIAL_ADMIN_PASSWORD": "a-new-strong-admin-password",
                },
            ),
            self.assertRaisesRegex(RuntimeError, "known default or invalid password"),
        ):
            create_first_admin.main()
        db.close.assert_called_once()


class VirtualUserAuthenticationTests(unittest.TestCase):
    def test_admin_created_user_is_rejected_even_with_valid_token(self):
        user = MagicMock(id=7, source=UserSource.ADMIN_CREATED)
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=create_access_token({"sub": 7}),
        )

        with self.assertRaises(HTTPException) as raised:
            asyncio.run(get_current_user(credentials=credentials, db=db))
        self.assertEqual(raised.exception.status_code, 401)


class WebSocketAuthenticationTests(unittest.TestCase):
    def test_user_id_is_not_part_of_websocket_route(self):
        websocket_paths = {
            route.path for route in webhook_routes.router.routes
            if getattr(route, "path", None)
        }
        self.assertIn("/ws", websocket_paths)
        self.assertNotIn("/ws/{user_id}", websocket_paths)

    def test_token_is_read_from_subprotocol_not_url(self):
        websocket = make_websocket(
            [(b"sec-websocket-protocol", b"bearer, signed.jwt.token")]
        )
        self.assertEqual(_websocket_token(websocket), "signed.jwt.token")

    def test_unapproved_browser_origin_is_rejected(self):
        websocket = make_websocket([(b"origin", b"https://evil.example")])
        with patch.dict(
            os.environ,
            {"WEBSOCKET_ALLOWED_ORIGINS": "https://app.example"},
        ):
            self.assertFalse(_websocket_origin_allowed(websocket))


if __name__ == "__main__":
    unittest.main()
