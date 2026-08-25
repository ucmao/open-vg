from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship, backref, Session
from sqlalchemy.sql import func
from enum import Enum
from typing import List, Dict, Set, Optional
from .base import Base


class WorkType(str, Enum):
    """Enum for work generation types."""
    TEXT2IMG = "text-to-image"
    TEXT2VIDEO = "text-to-video"
    IMG2IMG = "image-to-image"
    IMG2VIDEO = "image-to-video"
    IMG_EFFECTS = "image-effects"
    VIDEO_EFFECTS = "video-effects"


class WorkStatus(str, Enum):
    """Enum for work generation status."""
    GENERATING = "generating"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class ShareStatus(str, Enum):
    """Enum for work sharing status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def batch_prefetch_work_data(works: List['Work'], db: Session, current_user_id: Optional[int] = None) -> Dict:
    """
    Batch prefetch all auxiliary data needed for work.to_dict() to avoid N+1 queries.
    
    Args:
        works: List of Work objects to prefetch data for
        db: Database session
        current_user_id: Current user ID for checking likes/follows (optional)
    
    Returns:
        Dictionary with prefetched data:
        {
            'counts': {
                'comments': {work_id: count, ...},
                'forks': {work_id: count, ...}
            },
            'liked_work_ids': set of work_ids that current_user has liked,
            'following_user_ids': set of user_ids that current_user is following
        }
    """
    if not works:
        return {
            'counts': {'comments': {}, 'forks': {}},
            'liked_work_ids': set(),
            'following_user_ids': set()
        }
    
    from ..models.comment import Comment
    from ..models.like import Like
    from ..models.follow import Follow
    
    work_ids = [w.id for w in works]
    user_ids = list(set(w.user_id for w in works if w.user_id))
    
    # Batch query comment counts
    comment_counts = {}
    comment_results = db.query(
        Comment.work_id,
        func.count(Comment.id).label('count')
    ).filter(
        Comment.work_id.in_(work_ids)
    ).group_by(Comment.work_id).all()
    
    for work_id, count in comment_results:
        comment_counts[work_id] = count
    
    # Batch query fork counts
    fork_counts = {}
    fork_results = db.query(
        Work.parent_id,
        func.count(Work.id).label('count')
    ).filter(
        Work.parent_id.in_(work_ids),
        Work.is_shared == True,
        Work.share_status == ShareStatus.APPROVED
    ).group_by(Work.parent_id).all()
    
    for parent_id, count in fork_results:
        fork_counts[parent_id] = count
    
    # Batch query likes for current user
    liked_work_ids = set()
    if current_user_id:
        liked_results = db.query(Like.work_id).filter(
            Like.user_id == current_user_id,
            Like.work_id.in_(work_ids)
        ).all()
        liked_work_ids = {work_id for (work_id,) in liked_results}
    
    # Batch query follows for current user
    following_user_ids = set()
    if current_user_id and user_ids:
        follow_results = db.query(Follow.following_id).filter(
            Follow.follower_id == current_user_id,
            Follow.following_id.in_(user_ids)
        ).all()
        following_user_ids = {user_id for (user_id,) in follow_results}
    
    return {
        'counts': {
            'comments': comment_counts,
            'forks': fork_counts
        },
        'liked_work_ids': liked_work_ids,
        'following_user_ids': following_user_ids
    }


class Work(Base):
    """Work model for AI-generated content."""
    
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("works.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Generation information
    type = Column(String(50), nullable=False, index=True) # text-to-image, text-to-video, etc.
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    prompt_id = Column(String(36), nullable=True, index=True) # UUID
    source = Column(String(20), default="UGC", nullable=False) # UGC or PGC
    model_key = Column(String(100), nullable=False, index=True)  # GenerationModel.model_key
    model_name = Column(String(100), nullable=False, index=True)  # GenerationModel.name
    model_version = Column(String(50), nullable=True)
    params = Column(JSON, nullable=True)  # Store generation parameters as JSON
    tags = Column(JSON, default=[], nullable=False) # Store tags as JSON array
    
    # Files
    file_url = Column(Text, nullable=True)  # Main generated file
    thumbnail_url = Column(Text, nullable=True)  # Thumbnail
    storage_key = Column(String(50), nullable=True, index=True)  # Short storage key (e.g., 28-char NanoID)
    canonical_url = Column(Text, nullable=True)  # SEO-friendly URL (e.g., https://cdn.example.com/{storage_key}-{title}.jpg)
    short_code = Column(String(11), unique=True, nullable=True, index=True)  # 11-char NanoID for short URL (e.g., /prompt/8b3ed3aa3ef)
    url_slug = Column(String(250), unique=True, nullable=True, index=True)  # URL slug: short_code-title-slug (e.g., /prompt/5UWSKI183_s-ai-artwork)
    
    # Status
    status = Column(SQLEnum(WorkStatus), default=WorkStatus.GENERATING, nullable=False, index=True)
    error_message = Column(Text, nullable=True)  # Error details if failed
    
    # Replicate integration
    replicate_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Sharing
    is_shared = Column(Boolean, default=False, nullable=False, index=True)
    share_status = Column(SQLEnum(ShareStatus), nullable=True, index=True)
    share_name = Column(String(200), nullable=True)  # Display title for works (user-editable)
    title = Column(String(200), nullable=True)  # SEO title (auto-generated, for SEO purposes)
    description = Column(Text, nullable=True)  # Longer description (similar to title but more detailed)
    category = Column(String(100), nullable=True, index=True)  # Supports hierarchical categories: "Level1|Level2"
    reject_reason = Column(Text, nullable=True)
    is_banned = Column(Boolean, default=False, nullable=False, index=True)  # Admin banned flag
    ban_reason = Column(Text, nullable=True)  # Reason for ban
    is_featured = Column(Boolean, default=False, nullable=False, index=True)  # Featured on homepage
    hidden = Column(Boolean, default=False, nullable=False, index=True)  # Hidden from public view
    
    # NSFW Moderation
    nsfw_status = Column(String(20), nullable=True, index=True)  # 'pending', 'approved', 'blocked' - using String for flexibility
    nsfw_tags = Column(JSON, nullable=True)  # NSFW
    auto_moderated = Column(Boolean, default=False, nullable=False, index=True)  #
    
    # Engagement metrics
    like_count = Column(Integer, default=0, nullable=False)
    favorite_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)  # Soft delete timestamp
    
    # Relationships
    user = relationship("User", back_populates="works")
    favorites = relationship("Favorite", back_populates="work", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="work", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="work", cascade="all, delete-orphan")
    
    # Self-referential relationship for forks
    parent = relationship("Work", remote_side=[id], backref="forks")

    def __repr__(self):
        return f"<Work(id={self.id}, type={self.type}, status={self.status})>"
    
    def to_dict(self, include_user=False, include_prompt=True, current_user_id=None, db=None, 
                prefetched_counts=None, prefetched_likes=None, prefetched_follows=None):
        """Convert work to dictionary for API responses."""
        from ..services.storage import get_storage_service
        from ..models.comment import Comment
        storage = get_storage_service()
        
        # Calculate comment and fork counts efficiently
        comment_count = 0
        fork_count = 0
        
        # Use prefetched data if available (for batch operations)
        if prefetched_counts:
            comment_count = prefetched_counts.get('comments', {}).get(self.id, 0)
            fork_count = prefetched_counts.get('forks', {}).get(self.id, 0)
        elif db:
            comment_count = db.query(func.count(Comment.id)).filter(Comment.work_id == self.id).scalar() or 0
            fork_count = db.query(func.count(Work.id)).filter(
                Work.parent_id == self.id,
                Work.is_shared == True,
                Work.share_status == ShareStatus.APPROVED
            ).scalar() or 0
        elif hasattr(self, '_sa_instance_state'):
            try:
                if hasattr(self, 'comments'):
                    comment_count = len(self.comments)
                if hasattr(self, 'forks'):
                    # Using local import to avoid circular dependency if needed, but ShareStatus is already in scope
                    fork_count = len([f for f in self.forks if f.is_shared and f.share_status == ShareStatus.APPROVED])
            except:
                pass
        
        # Standard dict
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "parent_id": self.parent_id,
            "type": self.type,
            "prompt_id": self.prompt_id,
            "source": self.source,
            "model_key": self.model_key,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "params": self.params,
            "negative_prompt": self.negative_prompt,
            "tags": self.tags,
            "status": self.status.value,
            "error_message": self.error_message,
            "is_shared": self.is_shared,
            "is_featured": self.is_featured,
            "hidden": self.hidden,
            "share_status": self.share_status.value if self.share_status else None,
            "share_name": self.share_name,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "nsfw_status": self.nsfw_status,
            "nsfw_tags": self.nsfw_tags or [],
            "auto_moderated": self.auto_moderated,
            "storage_key": self.storage_key,
            "canonical_url": storage.get_public_url(self.canonical_url) if self.canonical_url else None,
            "short_code": self.short_code,
            "url_slug": self.url_slug,
            "like_count": self.like_count,
            "favorite_count": self.favorite_count,
            "view_count": self.view_count,
            "comment_count": comment_count,
            "fork_count": fork_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        
        # Handle URLs: use stored URLs
        if self.file_url:
            result["file_url"] = storage.get_public_url(self.file_url)
                
        # Thumbnail logic: use stored thumbnail_url or fallback to canonical_url/file_url
        if self.thumbnail_url:
            result["thumbnail_url"] = storage.get_public_url(self.thumbnail_url)
        else:
            result["thumbnail_url"] = self.canonical_url or result.get("file_url")
            
        if include_prompt:
            result["prompt"] = self.prompt
        
        if include_user and self.user:
            result["user"] = {
                "id": self.user.id,
                "handle": self.user.handle, # 🆔 Public identifier for linking
                "nickname": self.user.nickname,
                "email": self.user.email,
                "avatar_url": self.user.avatar_url,
                "bio": self.user.bio,
            }
        
        # Check if current user has liked this work
        if current_user_id:
            # Use prefetched data if available (for batch operations)
            if prefetched_likes is not None:
                result["is_liked"] = self.id in prefetched_likes
            elif db:
                from ..models.like import Like
                like = db.query(Like).filter(
                    Like.user_id == current_user_id,
                    Like.work_id == self.id
                ).first()
                result["is_liked"] = like is not None
            else:
                result["is_liked"] = False
            
            # Check if current user is following this author
            if prefetched_follows is not None:
                result["is_following_user"] = self.user_id in prefetched_follows
            elif db:
                from ..models.follow import Follow
                follow = db.query(Follow).filter(
                    Follow.follower_id == current_user_id,
                    Follow.following_id == self.user_id
                ).first()
                result["is_following_user"] = follow is not None
            else:
                result["is_following_user"] = False
        else:
            result["is_liked"] = False
            result["is_following_user"] = False
        
        return result
