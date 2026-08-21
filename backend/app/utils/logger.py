import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

# Always write logs into backend/logs (independent of current working directory)
# logger.py is at backend/app/utils/logger.py
# parents[0] = backend/app/utils/
# parents[1] = backend/app/
# parents[2] = backend/  ← This is what we want
_BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
_DEFAULT_LOG_DIR = _BACKEND_DIR / "logs"
LOG_DIR = Path(os.getenv("LOG_DIR", str(_DEFAULT_LOG_DIR))).expanduser().resolve()
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Get log level from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Create logger
logger = logging.getLogger("vidgen")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Create formatters with standardized date-time format
# Format: YYYY-MM-DD HH:MM:SS (standard ISO-like format, using local time)
detailed_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

simple_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)-8s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(simple_formatter)

# File handler - all logs saved to app.log
file_handler = RotatingFileHandler(
    str(LOG_DIR / "app.log"),
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)

# Add handlers to logger (only if not already added to avoid duplicate logs)
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# Prevent logging from propagating to the root logger
logger.propagate = False


def log_request(method: str, path: str, status_code: int, duration: float):
    """
    Log HTTP request details with silencing for high-frequency/low-value paths.
    """
    # 1. Skip OPTIONS requests (too noisy)
    if method == "OPTIONS":
        return

    # 2. Skip high-frequency status/SEO/config paths
    silenced_prefixes = [
        "/api/seo/",
        "/api/admin/stats/",
        "/api/page-configs",
        "/api/category-pages/tree-active",
        "/api/generate/models",
        "/api/topic"
    ]
    
    if any(path.startswith(prefix) for prefix in silenced_prefixes):
        return

    logger.info(f"{method} {path} - {status_code} - {duration:.2f}ms")


def log_error(error: Exception, context: str = ""):
    """
    Log error with context and stack trace.
    
    Args:
        error: Exception object
        context: Context description (e.g., function name, operation)
    """
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)


def log_generation_start(user_id: int, work_type: str, model: str):
    """
    Log generation start event.
    
    Args:
        user_id: User ID who initiated the generation
        work_type: Type of generation (text2img, img2img, etc.)
        model: Model name used for generation
    """
    logger.info(f"Generation started - User: {user_id}, Type: {work_type}, Model: {model}")


def log_generation_complete(work_id: int, status: str, duration: float):
    """
    Log generation completion event.
    
    Args:
        work_id: Work ID
        status: Generation status (success, failed)
        duration: Generation duration in seconds
    """
    logger.info(f"Generation {status} - Work ID: {work_id}, Duration: {duration:.2f}s")


def log_payment(user_id: int, amount: float, credits: int, status: str):
    """
    Log payment transaction.
    
    Args:
        user_id: User ID
        amount: Payment amount
        credits: Credits purchased/used
        status: Transaction status (success, failed, refunded)
    """
    logger.info(f"Payment {status} - User: {user_id}, Amount: ${amount:.2f}, Credits: {credits}")

