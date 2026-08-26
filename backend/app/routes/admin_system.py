from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models.base import get_db
from ..models.admin import Admin
from ..models.system_config import SystemConfig
from ..models.schemas import SystemConfigRequest, UpdateSystemConfigRequest
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response
from ..utils.logger import logger
from ..utils.crypto import encrypt_value, decrypt_value

router = APIRouter()

@router.get("/system/configs")
def get_system_configs(
    group: str = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get system configurations with sensitive data masked."""
    try:
        query = db.query(SystemConfig)
        if group:
            query = query.filter(SystemConfig.config_group == group)
        
        configs = query.all()
        result = []
        for config in configs:
            config_dict = config.to_dict()
            # Mask sensitive values: if encrypted or key implies secret
            is_sensitive = config.is_encrypted or any(s in config.config_key.lower() for s in ["api_key", "secret", "password", "token"])
            
            if is_sensitive and config.config_value:
                val = config.config_value
                if config.is_encrypted:
                    try:
                        val = decrypt_value(val)
                    except:
                        pass
                
                if val and len(val) > 8:
                    config_dict["config_value"] = f"{val[:4]}********{val[-4:]}"
                elif val:
                    config_dict["config_value"] = "********"
            
            result.append(config_dict)
            
        return success_response(data=result)
    except Exception as e:
        logger.error(f"Error fetching system configs: {e}")
        return error_response(message="Failed to fetch configurations")

@router.post("/system/configs")
def create_system_config(
    request: SystemConfigRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new system configuration."""
    try:
        existing = db.query(SystemConfig).filter(SystemConfig.config_key == request.config_key).first()
        if existing:
            return error_response(message="Configuration with this key already exists")
        
        value = request.config_value
        if request.is_encrypted and value:
            value = encrypt_value(value)
            
        new_config = SystemConfig(
            config_group=request.config_group,
            config_key=request.config_key,
            config_value=value,
            is_encrypted=request.is_encrypted,
            description=request.description
        )
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        
        return success_response(
            data=new_config.to_dict(),
            message="Configuration created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating system config: {e}")
        return error_response(message="Failed to create configuration")

@router.put("/system/configs/{config_key}")
def update_system_config(
    config_key: str,
    request: UpdateSystemConfigRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update an existing system configuration."""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
        if not config:
            return error_response(message="Configuration not found", status_code=status.HTTP_404_NOT_FOUND)
        
        if request.config_group is not None:
            config.config_group = request.config_group
        if request.description is not None:
            config.description = request.description
        if request.is_encrypted is not None:
            config.is_encrypted = request.is_encrypted
            
        if request.config_value is not None:
            value = request.config_value
            # If the value contains masking characters and hasn't changed from what we sent, skip update
            # Front-end should send the original value if it wants to update, 
            # or a new value that doesn't look like a mask.
            if "********" in value:
                # User likely didn't change the masked value
                pass
            else:
                if config.is_encrypted:
                    value = encrypt_value(value)
                config.config_value = value
        
        db.commit()
        db.refresh(config)
        return success_response(data=config.to_dict(), message="Configuration updated successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating system config: {e}")
        return error_response(message="Failed to update configuration")

@router.get("/system/configs/{config_key}/raw")
def get_system_config_raw(
    config_key: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get raw (unmasked) value of a system configuration."""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
        if not config:
            return error_response(message="Configuration not found", status_code=status.HTTP_404_NOT_FOUND)
        
        # Get raw value, decrypt if needed
        raw_value = config.config_value
        if config.is_encrypted and raw_value:
            try:
                raw_value = decrypt_value(raw_value)
            except Exception as e:
                logger.error(f"Error decrypting config value: {e}")
                raw_value = ""
        
        return success_response(data={"config_key": config_key, "config_value": raw_value or ""})
    except Exception as e:
        logger.error(f"Error fetching raw system config: {e}")
        return error_response(message="Failed to fetch raw configuration")

@router.delete("/system/configs/{config_key}")
def delete_system_config(
    config_key: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a system configuration."""
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
        if not config:
            return error_response(message="Configuration not found", status_code=status.HTTP_404_NOT_FOUND)
        
        db.delete(config)
        db.commit()
        return success_response(message="Configuration deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting system config: {e}")
        return error_response(message="Failed to delete configuration")

@router.post("/system/configs/init-providers")
def init_provider_configs(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Initialize default provider configurations (Replicate, Gemini)."""
    try:
        default_configs = [
            {
                "config_group": "providers",
                "config_key": "replicate_api_key",
                "config_value": "",
                "is_encrypted": True,
                "description": "Replicate API Token"
            },
            {
                "config_group": "providers",
                "config_key": "gemini_api_key",
                "config_value": "",
                "is_encrypted": True,
                "description": "Google Gemini API Key"
            },
            {
                "config_group": "providers",
                "config_key": "gemini_model",
                "config_value": "gemini-1.5-flash",
                "is_encrypted": False,
                "description": "Gemini model name (e.g., gemini-1.5-flash, gemini-1.5-pro)"
            },
            {
                "config_group": "providers",
                "config_key": "gemini_fallback_model",
                "config_value": "gemini-1.5-pro",
                "is_encrypted": False,
                "description": "Gemini fallback model (used when primary model is overloaded)"
            },
            {
                "config_group": "providers",
                "config_key": "a2e_api_key",
                "config_value": "",
                "is_encrypted": True,
                "description": "A2E AI API Key"
            },
            {
                "config_group": "providers",
                "config_key": "a2e_api_base_url",
                "config_value": "https://video.a2e.ai",
                "is_encrypted": False,
                "description": "A2E AI API Base URL"
            }
        ]
        
        created_count = 0
        for config_data in default_configs:
            existing = db.query(SystemConfig).filter(SystemConfig.config_key == config_data["config_key"]).first()
            if not existing:
                new_config = SystemConfig(**config_data)
                db.add(new_config)
                created_count += 1
        
        db.commit()
        return success_response(message=f"Initialized {created_count} provider configurations")
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing provider configs: {e}")
        return error_response(message="Failed to initialize provider configurations")
