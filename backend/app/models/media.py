from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class MediaType(str, Enum):
    """Media type enumeration."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class Media(Base):
    """Media model for storing uploaded file metadata."""
    
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)  # For images/videos
    file_size = Column(Integer, nullable=False)  # Bytes
    mime_type = Column(String(100), nullable=False)
    media_type = Column(SQLEnum(MediaType), nullable=False, index=True)
    
    # Storage metadata
    storage_key = Column(String(500), nullable=False)  # OSS key for deletion
    storage_type = Column(String(20), default="oss", nullable=False)  # oss, local
    
    # Optional metadata
    alt_text = Column(String(255), nullable=True)  # For images
    caption = Column(Text, nullable=True)
    
    # Purpose/Source: admin, user_upload, user_avatar, user_work
    source = Column(String(50), default="user_upload", nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="media")
    
    def __repr__(self):
        return f"<Media(id={self.id}, filename={self.filename}, type={self.media_type})>"
    
    def to_dict(self):
        """Convert media to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_url": self.file_url,
            "thumbnail_url": self.thumbnail_url,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "media_type": self.media_type.value,
            "storage_key": self.storage_key,
            "storage_type": self.storage_type,
            "source": self.source,
            "alt_text": self.alt_text,
            "caption": self.caption,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

