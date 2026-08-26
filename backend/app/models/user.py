from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class Gender(str, Enum):
    """Gender enumeration."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class UserSource(str, Enum):
    """User registration source enumeration."""
    REGISTER = "REGISTER"          # User registration
    GOOGLE = "GOOGLE"              # Google OAuth
    ADMIN_CREATED = "ADMIN_CREATED"  #
    IMPORT = "IMPORT"              # Data import


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String(15), unique=True, index=True, nullable=False) # Public identifier (6-15 chars, must start with letter, alphanumeric + underscore)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Profile information
    nickname = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)  # User bio/description
    
    # Social Media handles (optional)
    instagram_handle = Column(String(100), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    discord_handle = Column(String(100), nullable=True)
    
    # Location (optional)
    location = Column(String(80), nullable=True)  # User location/address
    
    # Gender (optional)
    gender = Column(SQLEnum(Gender), nullable=True)  # User gender
    
    # User registration source
    source = Column(SQLEnum(UserSource), nullable=False, server_default='REGISTER')
    
    # Handle change tracking
    handle_updated_at = Column(DateTime(timezone=True), nullable=True)  # Last time handle was changed
    
    # Credits
    total_credits = Column(Integer, default=0, nullable=False)
    
    # Admin permissions
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    works = relationship("Work", back_populates="user", cascade="all, delete-orphan")
    credit_records = relationship("CreditRecord", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    payment_orders = relationship("PaymentOrder", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    blog_posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="user", cascade="all, delete-orphan")
    
    # Follows relationships
    followers = relationship(
        "User",
        secondary="follows",
        primaryjoin="User.id==Follow.following_id",
        secondaryjoin="User.id==Follow.follower_id",
        backref=backref("following_users", viewonly=True),
        viewonly=True,
        overlaps="follower_users,following,followers,following_users"
    )
    following = relationship(
        "User",
        secondary="follows",
        primaryjoin="User.id==Follow.follower_id",
        secondaryjoin="User.id==Follow.following_id",
        backref=backref("follower_users", viewonly=True),
        viewonly=True,
        overlaps="follower_users,following,followers,following_users"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, nickname={self.nickname})>"
    
    def to_dict(self, db=None):
        """Convert user to dictionary for API responses."""
        data = {
            "id": self.id,
            "handle": self.handle,
            "email": self.email,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "instagram_handle": self.instagram_handle,
            "twitter_handle": self.twitter_handle,
            "discord_handle": self.discord_handle,
            "location": self.location,
            "gender": self.gender.value if self.gender else None,
            "source": self.source.value if self.source else None,
            "handle_updated_at": self.handle_updated_at.isoformat() if self.handle_updated_at else None,
            "total_credits": self.total_credits,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        # Add follow counts and aggregate stats if db session is provided
        if db:
            from .follow import Follow
            from .work import Work, WorkStatus, ShareStatus
            from sqlalchemy import func, and_
            
            data["followers_count"] = db.query(Follow).filter(Follow.following_id == self.id).count()
            data["following_count"] = db.query(Follow).filter(Follow.follower_id == self.id).count()
            
            # Aggregate stats for public works
            stats = db.query(
                func.sum(Work.view_count).label('total_views'),
                func.sum(Work.like_count).label('total_likes'),
                func.sum(Work.favorite_count).label('total_favorites'),
                func.count(Work.id).label('total_works')
            ).filter(
                and_(
                    Work.user_id == self.id,
                    Work.is_shared == True,
                    Work.status == WorkStatus.SUCCESS,
                    Work.share_status == ShareStatus.APPROVED,
                    Work.deleted_at == None  # Exclude soft-deleted works
                )
            ).first()
            
            # Count all successful works (for admin display, exclude soft-deleted)
            all_works_count = db.query(func.count(Work.id)).filter(
                and_(
                    Work.user_id == self.id,
                    Work.status == WorkStatus.SUCCESS,
                    Work.deleted_at == None  # Exclude soft-deleted works
                )
            ).scalar() or 0
            
            data["total_views"] = int(stats.total_views or 0)
            data["total_likes"] = int(stats.total_likes or 0)
            data["total_favorites"] = int(stats.total_favorites or 0)
            data["public_works_count"] = int(stats.total_works or 0)
            data["total_works_count"] = int(all_works_count)  # All successful works

            # Count total remixes of this user's works
            user_work_ids = db.query(Work.id).filter(
                and_(
                    Work.user_id == self.id,
                    Work.deleted_at == None  # Exclude soft-deleted works
                )
            ).subquery()
            data["total_remixes"] = db.query(func.count(Work.id)).filter(
                and_(
                    Work.parent_id.in_(user_work_ids),
                    Work.status == WorkStatus.SUCCESS,
                    Work.is_shared == True,
                    Work.share_status == ShareStatus.APPROVED,
                    Work.deleted_at == None  # Exclude soft-deleted works
                )
            ).scalar() or 0
            
        return data

