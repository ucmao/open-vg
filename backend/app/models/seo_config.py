from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from .base import Base


class SeoConfig(Base):
    """
    SEO configuration model for managing robots.txt and sitemap settings.
    """
    __tablename__ = "seo_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "config_key": self.config_key,
            "config_value": self.config_value,
            "is_enabled": self.is_enabled,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PageSeo(Base):
    """
    SEO configuration for specific pages (TDK).
    """
    __tablename__ = "page_seos"

    id = Column(Integer, primary_key=True, index=True)
    page_name = Column(String(50), unique=True, nullable=False, index=True)
    page_path = Column(String(200), nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "page_name": self.page_name,
            "page_path": self.page_path,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
