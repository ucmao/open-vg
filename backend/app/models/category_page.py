from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class CategoryPage(Base):
    """
    Category page configuration for managing work category pages with TDK.
    Supports hierarchical structure with parent-child relationships (level 1 and level 2).
    Each category page can display all works with that category.
    """
    __tablename__ = "category_pages"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("category_pages.id", ondelete="CASCADE"), nullable=True, index=True)  # Parent category ID
    category_name = Column(String(50), nullable=False, index=True)  # The category value used in Work.category (no longer unique)
    level = Column(Integer, default=1, nullable=False, index=True)  # Category level: 1 = first level, 2 = second level
    sort_order = Column(Integer, default=0, nullable=False)  # Sort order for display
    page_path = Column(String(200), nullable=False, index=True)  # URL path like /category/portraits or /category/3d-renders/characters
    title = Column(String(200), nullable=True)  # SEO Title
    description = Column(Text, nullable=True)  # SEO Description
    keywords = Column(Text, nullable=True)  # SEO Keywords
    display_description = Column(Text, nullable=True)  # Display description shown on the page (e.g., "Browse all portraits works")
    is_active = Column(Boolean, default=False, nullable=False, index=True)  # Whether the category is active (default False for imported categories)
    show_in_explore = Column(Boolean, default=False, nullable=False, index=True)  # Whether to show this category in explore page
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent = relationship("CategoryPage", remote_side=[id], backref="children")

    def to_dict(self, include_children=False):
        result = {
            "id": self.id,
            "parent_id": self.parent_id,
            "category_name": self.category_name,
            "level": self.level,
            "sort_order": self.sort_order,
            "page_path": self.page_path,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "display_description": self.display_description,
            "is_active": self.is_active,
            "show_in_explore": self.show_in_explore,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_children and hasattr(self, 'children'):
            result["children"] = [child.to_dict(include_children=False) for child in sorted(self.children, key=lambda x: x.sort_order)]
        
        return result