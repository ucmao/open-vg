"""Sanitize production-specific values before they enter the demo dataset."""

import re
from typing import Any


# Product-site links point to the local app. External media is removed from safe
# seed profiles; the historical full profile requires an explicit opt-in.
SITE_ORIGIN_PATTERN = re.compile(
    r"https?://(?:vidgenerator\.ai|example\.com)(?::\d+)?",
    re.IGNORECASE,
)
BARE_SITE_DOMAIN_PATTERN = re.compile(
    r"(?<!cdn\.)(?<!@)\b(?:vidgenerator\.ai|example\.com)\b",
    re.IGNORECASE,
)
DEMO_ORIGIN = "http://localhost:3000"
DEMO_HOST = "localhost:3000"
LOCAL_MEDIA_PLACEHOLDER = "/demo/placeholder.svg"

MEDIA_URL_FIELDS = {
    "after_url",
    "avatar_url",
    "background_image_url",
    "before_url",
    "cover_url",
    "file_url",
    "icon_url",
    "image",
    "image_url",
    "og_image",
    "thumbnail_url",
    "trailing_image_url",
    "video_url",
}

TRACKING_CODE_REPLACEMENTS = (
    (re.compile(r"(?<![A-Z0-9])G-[A-Z0-9]{6,}(?![A-Z0-9])"), "G-XXXXXXXXXX"),
    (re.compile(r"(?<![A-Z0-9])AW-\d{6,}(?!\d)"), "AW-00000000000"),
    (re.compile(r"(?<![A-Z0-9])GTM-[A-Z0-9]{4,}(?![A-Z0-9])"), "GTM-XXXXXXX"),
    (
        re.compile(
            r"(google-site-verification[\"']?\s+content=[\"'])[^\"']+",
            re.IGNORECASE,
        ),
        r"\1YOUR_GOOGLE_SITE_VERIFICATION_TOKEN",
    ),
    (
        re.compile(r"(clarity\.ms/tag/)[A-Z0-9_-]+", re.IGNORECASE),
        r"\1YOUR_CLARITY_PROJECT_ID",
    ),
    (
        re.compile(
            r"([\"']clarity[\"']\s*,\s*[\"']script[\"']\s*,\s*[\"'])[^\"']+",
            re.IGNORECASE,
        ),
        r"\1YOUR_CLARITY_PROJECT_ID",
    ),
    (
        re.compile(r"(fbq\(\s*[\"']init[\"']\s*,\s*[\"'])\d+", re.IGNORECASE),
        r"\1YOUR_META_PIXEL_ID",
    ),
    (
        re.compile(r"(hjid\s*[:=]\s*)\d+", re.IGNORECASE),
        r"\1YOUR_HOTJAR_SITE_ID",
    ),
)


SECRET_PATTERNS = (
    re.compile(r"sk-[a-zA-Z0-9_-]{20,}"),
)


def sanitize_tracking_code(value: str) -> str:
    """Replace analytics, ads, and site-verification identifiers with placeholders."""
    sanitized = value
    for pattern, replacement in TRACKING_CODE_REPLACEMENTS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def _sanitize_external_media(value: str, field_name: str | None) -> str:
    if not re.match(r"^https?://", value, flags=re.IGNORECASE):
        return value
    is_media_field = bool(field_name and field_name.lower() in MEDIA_URL_FIELDS)
    has_media_extension = bool(
        re.search(r"\.(?:avif|gif|jpe?g|mp4|png|webm|webp)(?:\?.*)?$", value, re.IGNORECASE)
    )
    return LOCAL_MEDIA_PLACEHOLDER if is_media_field or has_media_extension else value


def sanitize_seed_data(
    value: Any,
    *,
    allow_external_media: bool = False,
    field_name: str | None = None,
) -> Any:
    """Recursively replace the production domain and sensitive keys in arbitrary JSON-compatible data."""
    if isinstance(value, str):
        for pattern in SECRET_PATTERNS:
            value = pattern.sub("REDACTED", value)
        value = SITE_ORIGIN_PATTERN.sub(DEMO_ORIGIN, value)
        value = BARE_SITE_DOMAIN_PATTERN.sub(DEMO_HOST, value)
        value = sanitize_tracking_code(value)
        return value if allow_external_media else _sanitize_external_media(value, field_name)
    if isinstance(value, list):
        return [
            sanitize_seed_data(
                item,
                allow_external_media=allow_external_media,
                field_name=field_name,
            )
            for item in value
        ]
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if key in ("openai_api_key", "api_secret", "secret_key", "access_token"):
                continue
            sanitized[key] = sanitize_seed_data(
                item,
                allow_external_media=allow_external_media,
                field_name=str(key),
            )
        # Exported custom code must never execute automatically in a new
        # installation. The placeholder remains visible as a setup template.
        if str(sanitized.get("config_key", "")).startswith("custom_code_"):
            sanitized["is_enabled"] = False
        return sanitized
    return value


def contains_production_domain(value: Any) -> bool:
    """Return whether nested seed data still contains a non-local product domain."""
    if isinstance(value, str):
        return bool(
            SITE_ORIGIN_PATTERN.search(value)
            or BARE_SITE_DOMAIN_PATTERN.search(value)
        )
    if isinstance(value, list):
        return any(contains_production_domain(item) for item in value)
    if isinstance(value, dict):
        return any(contains_production_domain(item) for item in value.values())
    return False
