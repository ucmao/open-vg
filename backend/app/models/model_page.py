"""Model page (landing page for a generation model) - e.g. /magic/:slug."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from .base import Base


class ModelPageStatus(str, Enum):
    """Model page status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ModelPage(Base):
    """Landing page for a generation model (e.g. /magic/vhs). Same structure as Topic."""

    __tablename__ = "model_pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    generation_model_id = Column(Integer, ForeignKey("generation_models.id", ondelete="SET NULL"), nullable=True, unique=True, index=True)

    # Content
    title = Column(String(200), nullable=False, index=True)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=True)

    # SEO
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(String(500), nullable=True)
    og_image = Column(Text, nullable=True)

    # Visuals
    featured_image = Column(String(500), nullable=True)
    icon = Column(String(100), nullable=True)

    # Custom data (components, hero_button_*, etc.)
    config = Column(JSON, default={}, nullable=False)

    # Metadata
    status = Column(SQLEnum(ModelPageStatus), default=ModelPageStatus.DRAFT, nullable=False, index=True)
    view_count = Column(Integer, default=0, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    generation_model = relationship("GenerationModel", backref="model_page")

    def to_dict(self, include_model=True):
        d = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "excerpt": self.excerpt,
            "content": self.content,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "og_image": self.og_image,
            "featured_image": self.featured_image,
            "icon": self.icon,
            "config": self.config or {},
            "status": self.status.value,
            "view_count": self.view_count,
            "sort_order": self.sort_order,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_model and self.generation_model_id:
            d["generation_model_id"] = self.generation_model_id
            if self.generation_model:
                d["generation_model"] = {
                    "id": self.generation_model.id,
                    "model_key": self.generation_model.model_key,
                    "name": self.generation_model.name,
                    "work_type": self.generation_model.work_type,
                }
        return d
