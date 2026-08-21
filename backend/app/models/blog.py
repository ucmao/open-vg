from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class PostStatus(str, Enum):
    """Blog post status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class BlogPost(Base):
    """Blog post model for SEO-optimized blog content."""
    
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, index=True, nullable=False)  # SEO-friendly URL
    
    # Content
    title = Column(String(200), nullable=False, index=True)
    excerpt = Column(Text, nullable=True)  # Summary for meta description
    content = Column(Text, nullable=False)  # Full content (HTML or Markdown)
    
    # SEO fields
    meta_title = Column(String(200), nullable=True)  # Custom meta title
    meta_description = Column(Text, nullable=True)  # Custom meta description
    meta_keywords = Column(String(500), nullable=True)  # Keywords
    og_image = Column(Text, nullable=True)  # Open Graph image URL
    
    # Classification
    category = Column(String(50), index=True, nullable=True)
    category_id = Column(Integer, ForeignKey("blog_categories.id", ondelete="SET NULL"), nullable=True)
    tags = Column(JSON, default=[], nullable=False)  # Array of tags (legacy)
    
    # Author and status
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(PostStatus), default=PostStatus.DRAFT, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Statistics
    view_count = Column(Integer, default=0, nullable=False)
    
    # Display order
    sort_order = Column(Integer, default=0, nullable=False)  # Display order
    
    # Relationships
    author = relationship("User", back_populates="blog_posts")
    blog_category = relationship("BlogCategory", back_populates="posts")

    def __repr__(self):
        return f"<BlogPost(id={self.id}, slug={self.slug}, title={self.title})>"
    
    def to_dict(self, include_content=False, include_author=True):
        """Convert blog post to dictionary for API responses."""
        result = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "excerpt": self.excerpt,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "og_image": self.og_image,
            "category": self.category,
            "category_id": self.category_id,
            "category_name": self.blog_category.name if self.blog_category else self.category,
            "tags": self.tags or [],
            "status": self.status.value,
            "is_featured": self.is_featured,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "view_count": self.view_count,
            "sort_order": self.sort_order,
            "author_id": self.author_id,  # Always include author_id
        }
        
        if include_content:
            result["content"] = self.content
        
        if include_author and self.author:
            result["author"] = {
                "id": self.author.id,
                "handle": self.author.handle,
                "nickname": self.author.nickname,
                "avatar_url": self.author.avatar_url,
                "bio": self.author.bio,
            }
        
        return result


class BlogCategory(Base):
    """Blog category model."""
    __tablename__ = "blog_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    posts = relationship("BlogPost", back_populates="blog_category")
    topics = relationship("Topic", back_populates="blog_category")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BlogTag(Base):
    """Blog tag model."""
    __tablename__ = "blog_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

