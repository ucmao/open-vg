"""
Validation utilities.
"""
import re
from typing import Optional, Tuple


def is_english_only(text: str) -> bool:
    """
    Check if text contains only printable ASCII (English + common punctuation).
    Allows: letters, numbers, spaces, and common punctuation.
    Rejects: CJK, Cyrillic, Arabic, emoji, etc.
    """
    if not text or not text.strip():
        return True  # Empty is valid (optional fields)
    return bool(re.match(r"^[\x20-\x7E\r\n]+$", text))


def validate_reason_english(reason: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that reason (if provided) contains only English/ASCII.
    Returns (is_valid, error_message).
    """
    if not reason or not reason.strip():
        return True, None
    if not is_english_only(reason):
        return (
            False,
            "Reason must contain only English characters (letters, numbers, common punctuation). "
            "，。",
        )
    return True, None
