from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class GeneratePage(Base):
    """
    Generate page configuration for managing /generate category pages with TDK.
    Supports hierarchical structure with parent-child relationships (level 1 and level 2).
    Each generate page can be used to host a dedicated SEO landing page under /generate.
    """

    __tablename__ = "generate_pages"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("generate_pages.id", ondelete="CASCADE"), nullable=True, index=True)
    category_name = Column(String(50), nullable=False, index=True)
    level = Column(Integer, default=1, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)
    page_path = Column(String(200), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    display_description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    parent = relationship("GeneratePage", remote_side=[id], backref="children")

    def to_dict(self, include_children: bool = False, include_parent: bool = True):
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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_parent and self.parent_id and self.parent:
            result["parent"] = {
                "id": self.parent.id,
                "category_name": self.parent.category_name,
                "page_path": self.parent.page_path,
            }

        if include_children and hasattr(self, "children"):
            result["children"] = [
                child.to_dict(include_children=False, include_parent=False)
                for child in sorted(self.children, key=lambda x: x.sort_order)
            ]

        return result

