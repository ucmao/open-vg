from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from .base import Base

class SystemConfig(Base):
    """
    General system configuration model for storing API keys, 
    third-party service settings, and other global parameters.
    """
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_group = Column(String(50), nullable=False, index=True, default="general")
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "config_group": self.config_group,
            "config_key": self.config_key,
            "config_value": self.config_value,
            "is_encrypted": self.is_encrypted,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
