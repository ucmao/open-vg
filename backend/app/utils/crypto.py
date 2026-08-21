from cryptography.fernet import Fernet
import os
import base64
import hashlib
from ..utils.logger import logger

_env_mode = os.getenv("ENVIRONMENT", "development").strip().lower()
raw_key = os.getenv("CONFIG_ENCRYPTION_KEY", "").strip()

DEFAULT_CRYPTO_KEY = "aigc-platform-default-secret-key-change-it-in-prod"

if _env_mode == "production":
    if not raw_key or raw_key == DEFAULT_CRYPTO_KEY:
        raise RuntimeError(
            "CRITICAL SECURITY ERROR: Missing or default CONFIG_ENCRYPTION_KEY in PRODUCTION mode! "
            "Please set a custom CONFIG_ENCRYPTION_KEY in your environment variables to protect stored vendor API keys."
        )
else:
    if not raw_key or raw_key == DEFAULT_CRYPTO_KEY:
        logger.warning("CONFIG_ENCRYPTION_KEY not found or using default value in environment. Using default key for development.")
        raw_key = DEFAULT_CRYPTO_KEY

# Use SHA-256 to hash the raw key into a fixed 32-byte length
# This allows the user to use any simple string as a key
hashed_key = hashlib.sha256(raw_key.encode()).digest()

# Base64 encode the 32-byte hash to satisfy Fernet requirements
fernet_key = base64.urlsafe_b64encode(hashed_key)

cipher_suite = Fernet(fernet_key)

def encrypt_value(value: str) -> str:
    """Encrypt a string value."""
    if not value:
        return value
    try:
        return cipher_suite.encrypt(value.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        return value

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt an encrypted string value."""
    if not encrypted_value:
        return encrypted_value
    try:
        return cipher_suite.decrypt(encrypted_value.encode()).decode()
    except Exception as e:
        # If decryption fails, it might be because the value wasn't encrypted 
        # or the key has changed. We return the original value as a fallback.
        return encrypted_value
