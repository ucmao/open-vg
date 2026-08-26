from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class ModerationType(str, Enum):
    NSFW = "NSFW"  # NSFW
    SHARE_REVIEW = "SHARE_REVIEW"  # Share review


class ModerationAction(str, Enum):
    AUTO_BLOCKED = "AUTO_BLOCKED"  # Auto blocked
    AUTO_FLAGGED = "AUTO_FLAGGED"  # Auto flagged
    MANUAL_FLAGGED = "MANUAL_FLAGGED"  #
    AUTO_APPROVED = "AUTO_APPROVED"  #
    MANUAL_APPROVED = "MANUAL_APPROVED"  #
    MANUAL_REJECTED = "MANUAL_REJECTED"  #


class NSFWStatus(str, Enum):
    """NSFW"""
    PENDING = "PENDING"  #
    APPROVED = "APPROVED"  #
    BLOCKED = "BLOCKED"  #


class LexiconCategory(str, Enum):
    VIOLENCE = "VIOLENCE"  #
    PORNOGRAPHY = "PORNOGRAPHY"  #
    ILLEGAL = "ILLEGAL"  #
    OTHER = "OTHER"  #


class LexiconSeverity(str, Enum):
    LOW = "LOW"  #
    MEDIUM = "MEDIUM"  #
    HIGH = "HIGH"  #


class ReportStatus(str, Enum):
    """（DB ；API  value ）"""
    PENDING = "pending"  #
    RESOLVED = "resolved"  #
    DISMISSED = "dismissed"  #


class ReportType(str, Enum):
    """（DB ；API  value ）"""
    PORNOGRAPHY = "pornography"  #
    VIOLENCE = "violence"  #
    GORE = "gore"  #
    HARASSMENT = "harassment"  #
    SPAM = "spam"  #
    COPYRIGHT = "copyright"  #
    OTHER = "other"  #


class ModerationLog(Base):
    
    __tablename__ = "moderation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    
    moderation_type = Column(SQLEnum(ModerationType), nullable=False, index=True)
    
    action_type = Column(SQLEnum(ModerationAction), nullable=False, index=True)
    
    # NSFW
    nsfw_tags = Column(JSON, nullable=True)  # NSFW, ['violence', 'pornography']
    flagged_keywords = Column(JSON, nullable=True)  #
    
    moderator_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # /
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    work = relationship("Work", backref="moderation_logs")
    moderator = relationship("Admin", backref="moderation_actions")
    
    __table_args__ = (
        Index('ix_moderation_logs_work_type', 'work_id', 'moderation_type'),
    )
    
    def to_dict(self, include_work=False, include_moderator=False):
        result = {
            "id": self.id,
            "work_id": self.work_id,
            "moderation_type": self.moderation_type.value,
            "action_type": self.action_type.value,
            "nsfw_tags": self.nsfw_tags or [],
            "flagged_keywords": self.flagged_keywords or [],
            "moderator_id": self.moderator_id,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_work and self.work:
            result["work"] = {
                "id": self.work.id,
                "title": self.work.title or self.work.share_name,
                "prompt": self.work.prompt[:100] if self.work.prompt else None,
            }
        
        if include_moderator and self.moderator:
            result["moderator"] = {
                "id": self.moderator.id,
                "nickname": self.moderator.nickname,
                "username": self.moderator.username,
            }
        
        return result


class Lexicon(Base):
    
    __tablename__ = "lexicons"
    
    id = Column(Integer, primary_key=True, index=True)
    
    word = Column(String(200), nullable=False, index=True, unique=True)
    
    category = Column(SQLEnum(LexiconCategory), nullable=False, index=True)
    
    severity = Column(SQLEnum(LexiconSeverity), default=LexiconSeverity.MEDIUM, nullable=False, index=True)
    
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "word": self.word,
            "category": self.category.value,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Report(Base):
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # DB , SQLAlchemy enum name)
    report_type = Column(SQLEnum(ReportType), nullable=False, index=True)
    
    reason = Column(Text, nullable=True)
    
    # DB , SQLAlchemy enum name)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False, index=True)
    
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True, index=True)
    resolution_reason = Column(Text, nullable=True)  # /
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    work = relationship("Work", backref="reports")
    reporter = relationship("User", foreign_keys=[reporter_id], backref="reports")
    resolver = relationship("Admin", foreign_keys=[resolved_by], backref="resolved_reports")
    
    __table_args__ = (
        Index('ix_reports_work_status', 'work_id', 'status'),
        Index('ix_reports_status_created', 'status', 'created_at'),
    )
    
    def to_dict(self, include_work=False, include_reporter=False, include_resolver=False):
        result = {
            "id": self.id,
            "work_id": self.work_id,
            "reporter_id": self.reporter_id,
            "report_type": self.report_type.value if self.report_type else "other",  # Default to "other" if missing
            "reason": self.reason,
            "status": self.status.value,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_reason": self.resolution_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_work and self.work:
            from ..models.work import batch_prefetch_work_data
            #  work
            result["work"] = {
                "id": self.work.id,
                "title": self.work.title or self.work.share_name,
                "share_name": self.work.share_name,
                "type": self.work.type if self.work.type else None,
                "model_name": self.work.model_name,
                "prompt": self.work.prompt,
                "url_slug": self.work.url_slug,
                "short_code": self.work.short_code,
                "file_url": self.work.file_url,
                "thumbnail_url": self.work.thumbnail_url,
                "user": {
                    "id": self.work.user.id if self.work.user else None,
                    "nickname": self.work.user.nickname if self.work.user else None,
                    "handle": self.work.user.handle if self.work.user else None,
                } if self.work.user else None,
            }
        
        if include_reporter and self.reporter:
            result["reporter"] = {
                "id": self.reporter.id,
                "nickname": self.reporter.nickname,
                "handle": self.reporter.handle,
            }
        
        if include_resolver and self.resolver:
            result["resolver"] = {
                "id": self.resolver.id,
                "nickname": self.resolver.nickname,
                "username": self.resolver.username,
            }
        
        return result
