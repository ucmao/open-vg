from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class TopicStatus(str, Enum):
    """Topic status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Topic(Base):
    """Topic model for templates, activity pages, and tool pages."""
    
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, index=True, nullable=False)  # SEO-friendly URL
    
    # Content
    title = Column(String(200), nullable=False, index=True)
    excerpt = Column(Text, nullable=True)  # Summary for meta description
    content = Column(Text, nullable=True)      # Detailed content/instructions
    
    # SEO
    meta_title = Column(String(200), nullable=True)  # SEO title
    meta_description = Column(Text, nullable=True)   # SEO description
    meta_keywords = Column(String(500), nullable=True)  # Keywords
    og_image = Column(Text, nullable=True)  # Open Graph image URL
    
    # Classification
    category = Column(String(100), nullable=True, index=True)  # Legacy category field
    category_id = Column(Integer, ForeignKey("blog_categories.id", ondelete="SET NULL"), nullable=True)
    tags = Column(JSON, default=[], nullable=False)  # Store tags as JSON array
    
    # Visuals
    featured_image = Column(String(500), nullable=True)  # Banner image
    icon = Column(String(100), nullable=True)            # Icon or emoji
    
    # Custom Data (JSON)
    # This can store lists of prompt_ids, recommended models, style presets, etc.
    config = Column(JSON, default={}, nullable=False)
    
    # Optional: when set, this topic is a model landing page (URL /magic/:slug)
    generation_model_id = Column(Integer, ForeignKey("generation_models.id", ondelete="SET NULL"), nullable=True, unique=True, index=True)
    
    # Metadata
    status = Column(SQLEnum(TopicStatus), default=TopicStatus.DRAFT, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False, index=True)
    view_count = Column(Integer, default=0, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)  # Display order
    
    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    blog_category = relationship("BlogCategory", back_populates="topics", foreign_keys=[category_id])
    generation_model = relationship("GenerationModel", backref="topic", foreign_keys=[generation_model_id])

    def to_dict(self):
        """Convert topic to dictionary for API responses."""
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "excerpt": self.excerpt,
            "content": self.content,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "og_image": self.og_image,
            "category": self.category,
            "category_id": self.category_id,
            "category_name": self.blog_category.name if self.blog_category else self.category,
            "tags": self.tags or [],
            "featured_image": self.featured_image,
            "icon": self.icon,
            "config": self.config or {},
            "generation_model_id": self.generation_model_id,
            "status": self.status.value,
            "is_featured": self.is_featured,
            "view_count": self.view_count,
            "sort_order": self.sort_order,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
