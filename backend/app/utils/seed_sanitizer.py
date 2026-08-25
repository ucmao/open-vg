"""Sanitize production-specific values before they enter the demo dataset."""

import re
from typing import Any


# Public CDN media is intentionally retained so the lightweight demo can show
# real content without committing binary assets. Only the production website
# hostname is replaced in links and copy.
PRODUCTION_DOMAIN_PATTERN = re.compile(r"(?<!cdn\.)vidgenerator\.ai", re.IGNORECASE)
DEMO_DOMAIN = "example.com"

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


def sanitize_tracking_code(value: str) -> str:
    """Replace analytics, ads, and site-verification identifiers with placeholders."""
    sanitized = value
    for pattern, replacement in TRACKING_CODE_REPLACEMENTS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def sanitize_seed_data(value: Any) -> Any:
    """Recursively replace the production domain in arbitrary JSON-compatible data."""
    if isinstance(value, str):
        value = PRODUCTION_DOMAIN_PATTERN.sub(DEMO_DOMAIN, value)
        return sanitize_tracking_code(value)
    if isinstance(value, list):
        return [sanitize_seed_data(item) for item in value]
    if isinstance(value, dict):
        sanitized = {key: sanitize_seed_data(item) for key, item in value.items()}
        # Exported custom code must never execute automatically in a new
        # installation. The placeholder remains visible as a setup template.
        if str(sanitized.get("config_key", "")).startswith("custom_code_"):
            sanitized["is_enabled"] = False
        return sanitized
    return value


def contains_production_domain(value: Any) -> bool:
    """Return whether a nested seed value still contains the production domain."""
    if isinstance(value, str):
        return bool(PRODUCTION_DOMAIN_PATTERN.search(value))
    if isinstance(value, list):
        return any(contains_production_domain(item) for item in value)
    if isinstance(value, dict):
        return any(contains_production_domain(item) for item in value.values())
    return False
