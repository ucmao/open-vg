from sqlalchemy.orm import Session
from ..models.base import SessionLocal
from ..models.system_config import SystemConfig
from ..utils.crypto import decrypt_value
import os

def get_system_config(key: str, default: str = None) -> str:
    """
    Get a system configuration value from database.
    If not found in DB, falls back to environment variable.
    """
    db = SessionLocal()
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if config and config.config_value:
            val = config.config_value
            if config.is_encrypted:
                try:
                    val = decrypt_value(val)
                except:
                    pass
            return val
        
        # Fallback to environment variable (upper case)
        env_key = key.upper()
        return os.getenv(env_key, default)
    finally:
        db.close()

def get_provider_api_key(provider_name: str) -> str:
    """Helper to get provider API key specifically."""
    config_key = f"{provider_name.lower()}_api_key"
    return get_system_config(config_key)
